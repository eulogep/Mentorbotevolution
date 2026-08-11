"""Routes des parcours de maîtrise multi-domaines."""

from datetime import date, datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.content.toeic_foundations import get_starter_pack
from src.models.user import Card, Concept, Subject, db
from src.services.domain_catalog import DOMAIN_OPTIONS, find_template, public_catalog

mastery_bp = Blueprint("mastery", __name__)


def _parse_target_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError("target_date must use the YYYY-MM-DD format") from exc


def _parse_weekly_hours(value):
    if value in (None, ""):
        return None
    try:
        hours = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("weekly_hours must be a number") from exc
    if not 0.25 <= hours <= 80:
        raise ValueError("weekly_hours must be between 0.25 and 80")
    return hours


def _create_path(user_id: int, data: dict) -> tuple[Subject, dict | None]:
    """Create a user-selected path and its optional transparent starter pack."""
    template_id = data.get("template_id")
    template = find_template(template_id) if template_id else None
    if template_id and not template:
        raise ValueError("Unknown learning path template")
    starter_pack = get_starter_pack(template_id) if template else None

    if template:
        name = template["title"]
        domain = template["domain"]
        description = template["description"]
        objective_type = template["objective_type"]
        objective_label = template["objective_label"]
        source = template["source"]
        concepts = template["concepts"]
    else:
        name = str(data.get("name", "")).strip()
        domain = str(data.get("domain", "general")).strip()
        description = str(data.get("description", "")).strip()
        objective_type = str(data.get("objective_type", "competency")).strip()
        objective_label = str(data.get("objective_label", "Compétence visée")).strip()
        source = "user_created"
        concepts = data.get("concepts", [])

    if not name:
        raise ValueError("A learning path name is required")
    if domain not in DOMAIN_OPTIONS:
        raise ValueError("Unknown learning domain")
    if objective_type not in {"competency", "exam_score", "project", "certification"}:
        raise ValueError("Unknown objective type")

    target_score = None
    if objective_type == "exam_score" and data.get("target_score") not in (None, ""):
        try:
            target_score = int(data["target_score"])
        except (TypeError, ValueError) as exc:
            raise ValueError("target_score must be an integer") from exc

    subject = Subject(
        user_id=user_id,
        name=name,
        description=description,
        domain=domain,
        objective_type=objective_type,
        objective_label=objective_label or "Compétence visée",
        target_score=target_score,
        target_date=_parse_target_date(data.get("target_date")),
        weekly_hours=_parse_weekly_hours(data.get("weekly_hours")),
        source=source,
        status="in_progress",
    )
    db.session.add(subject)
    db.session.flush()

    for concept in concepts:
        if isinstance(concept, str):
            concept = {"name": concept}
        concept_name = str(concept.get("name", "")).strip()
        if not concept_name:
            continue
        db.session.add(Concept(
            subject_id=subject.id,
            name=concept_name,
            status="not-started",
            mastery=0,
            competency_type=concept.get("competency_type", "knowledge"),
            evidence_criterion=concept.get("evidence_criterion", ""),
        ))

    if starter_pack:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for card_data in starter_pack["cards"]:
            db.session.add(Card(
                user_id=user_id,
                subject_id=subject.id,
                learning_domain=starter_pack["learning_domain"],
                concept_name=card_data["concept_name"],
                front_content=card_data["question"],
                back_content=card_data["answer"],
                difficulty=card_data.get("difficulty", "medium"),
                priority="normal",
                tags=",".join(card_data.get("tags", [])),
                next_review=now,
            ))

    db.session.commit()
    return subject, starter_pack


@mastery_bp.route("/subjects", methods=["GET"])
@jwt_required()
def get_subjects():
    """Return only the learner’s existing paths; never invent a default path."""
    try:
        user_id = int(get_jwt_identity())
        subjects = Subject.query.filter_by(user_id=user_id).order_by(Subject.created_at.desc()).all()
        return jsonify([subject.to_dict() for subject in subjects])
    except Exception:
        return jsonify({"status": "error", "message": "Unable to retrieve learning paths."}), 500


@mastery_bp.route("/get-subjects", methods=["GET"])
@jwt_required()
def get_subjects_enhanced():
    """Frontend-compatible wrapper around the explicit-path list."""
    try:
        user_id = int(get_jwt_identity())
        subjects = Subject.query.filter_by(user_id=user_id).order_by(Subject.created_at.desc()).all()
        return jsonify({"status": "success", "subjects": [subject.to_dict() for subject in subjects]})
    except Exception:
        return jsonify({"status": "error", "message": "Unable to retrieve learning paths."}), 500


@mastery_bp.route("/catalog", methods=["GET"])
@jwt_required()
def get_learning_path_catalog():
    """Expose the editorial template catalogue without creating any data."""
    return jsonify({
        "status": "success",
        "domains": [{"id": key, "label": label} for key, label in DOMAIN_OPTIONS.items()],
        "templates": public_catalog(),
        "disclaimer": "Les modèles sont des structures de départ. Ils ne constituent ni un diagnostic ni une certification.",
    })


@mastery_bp.route("/create-path", methods=["POST"])
@jwt_required()
def create_learning_path():
    """Create a free path or a user-selected editorial template."""
    try:
        user_id = int(get_jwt_identity())
        subject, starter_pack = _create_path(user_id, request.get_json(silent=True) or {})
        response = {"status": "success", "subject": subject.to_dict()}
        if starter_pack:
            response["starter_pack"] = {
                "id": starter_pack["id"],
                "title": starter_pack["title"],
                "cards_created": len(starter_pack["cards"]),
                "learning_domain": starter_pack["learning_domain"],
                "disclaimer": "Jeu de départ éditorial : complétez-le avec vos propres contenus et une pratique variée.",
            }
        return jsonify(response), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to create the learning path."}), 500


@mastery_bp.route("/plan", methods=["POST"])
@jwt_required()
def create_plan():
    """Legacy alias retained for existing clients; now creates a generic free path."""
    try:
        user_id = int(get_jwt_identity())
        payload = request.get_json(silent=True) or {}
        subject, _ = _create_path(user_id, {
            "name": payload.get("subject", payload.get("name", "")),
            "description": payload.get("description", ""),
            "domain": payload.get("domain", "general"),
            "objective_type": payload.get("objective_type", "competency"),
            "objective_label": payload.get("objective_label", "Compétence visée"),
            "target_date": payload.get("target_date"),
            "weekly_hours": payload.get("weekly_hours"),
            "concepts": payload.get("concepts", []),
        })
        return jsonify(subject.to_dict()), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to create the learning path."}), 500
