"""Routes du diagnostic TOEIC original et de ses remédiations formatives."""

from collections import defaultdict
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.content.toeic_reading_diagnostic import (
    TOEIC_READING_DIAGNOSTIC_ID,
    get_diagnostic_item,
    get_toeic_reading_diagnostic as load_toeic_reading_diagnostic,
)
from src.models.user import Card, DiagnosticAttempt, DiagnosticResponse, Subject, db


diagnostic_bp = Blueprint("diagnostic", __name__)


def _utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _safe_seconds(value, maximum=7200):
    try:
        return max(0.0, min(maximum, float(value)))
    except (TypeError, ValueError):
        return None


def _safe_confidence(value):
    if value in (None, ""):
        return None
    try:
        confidence = int(value)
    except (TypeError, ValueError):
        return None
    return confidence if 1 <= confidence <= 4 else None


def _public_item(item):
    """Expose an item without answer, explanation or remediation metadata."""
    return {
        key: value
        for key, value in item.items()
        if key not in {"correct_index", "explanation", "remediation"}
    }


def _subject_for_user(user_id, subject_id):
    if subject_id in (None, ""):
        return None
    try:
        subject_id = int(subject_id)
    except (TypeError, ValueError):
        raise ValueError("subject_id must be an integer")
    subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()
    if not subject:
        raise ValueError("Subject not found")
    if subject.domain != "language":
        raise ValueError("The reading diagnostic is available only for a language learning path")
    return subject


def _analysis_from_responses(responses):
    grouped = defaultdict(list)
    for response in responses:
        grouped[response.target].append(response)

    breakdown = []
    recommendations = []
    for target, target_responses in sorted(grouped.items()):
        total = len(target_responses)
        correct = sum(response.is_correct for response in target_responses)
        incorrect = total - correct
        accuracy = round(correct / total, 3) if total else None
        remediation_available = any(
            (get_diagnostic_item(response.item_id) or {}).get("remediation")
            for response in target_responses
        )
        breakdown.append({
            "target": target,
            "items": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": accuracy,
            "remediation_available": remediation_available,
        })

        if total < 4:
            recommendations.append({
                "target": target,
                "code": "insufficient_data",
                "message": "Échantillon trop petit pour conclure : poursuivez avec de nouveaux items avant de cibler cette compétence.",
            })
        elif incorrect >= 2 and remediation_available:
            recommendations.append({
                "target": target,
                "code": "create_remediation",
                "message": "Plusieurs réponses ont été fragiles. Vous pouvez créer des cartes de remédiation ciblées, puis les revoir avec FSRS.",
            })
        elif incorrect >= 2:
            recommendations.append({
                "target": target,
                "code": "guided_practice",
                "message": "Reprenez des textes analogues avec une justification des indices : cette cible relève d’abord de la compréhension de document.",
            })
        else:
            recommendations.append({
                "target": target,
                "code": "continue_sampling",
                "message": "Résultats observés sur un petit lot : continuez la pratique pour obtenir une mesure plus stable.",
            })

    return {"breakdown": breakdown, "recommendations": recommendations}


@diagnostic_bp.route("/toeic-reading", methods=["GET"])
@jwt_required()
def get_toeic_reading_diagnostic():
    """Expose the original item metadata, never the answers or corrections."""
    diagnostic = load_toeic_reading_diagnostic()
    return jsonify({
        "status": "success",
        "diagnostic": {
            key: value for key, value in diagnostic.items() if key != "items"
        },
        "items": [_public_item(item) for item in diagnostic["items"]],
    })


@diagnostic_bp.route("/toeic-reading/start", methods=["POST"])
@jwt_required()
def start_toeic_reading_diagnostic():
    """Create one fresh formative attempt for an explicit language path."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True) or {}
        subject = _subject_for_user(user_id, data.get("subject_id"))
        diagnostic = load_toeic_reading_diagnostic()
        attempt = DiagnosticAttempt(
            user_id=user_id,
            subject_id=subject.id if subject else None,
            diagnostic_id=TOEIC_READING_DIAGNOSTIC_ID,
            total_items=len(diagnostic["items"]),
            started_at=_utcnow_naive(),
        )
        db.session.add(attempt)
        db.session.commit()
        return jsonify({
            "status": "success",
            "attempt": attempt.to_dict(),
            "diagnostic": {
                key: value for key, value in diagnostic.items() if key != "items"
            },
            "items": [_public_item(item) for item in diagnostic["items"]],
        }), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to start the reading diagnostic."}), 500


@diagnostic_bp.route("/attempts/<int:attempt_id>/submit", methods=["POST"])
@jwt_required()
def submit_diagnostic_attempt(attempt_id):
    """Store answers, return feedback and never infer a TOEIC score."""
    try:
        user_id = int(get_jwt_identity())
        attempt = DiagnosticAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
        if not attempt:
            return jsonify({"status": "error", "message": "Diagnostic attempt not found"}), 404
        if attempt.status != "in_progress":
            return jsonify({"status": "error", "message": "This diagnostic attempt has already been submitted"}), 409

        data = request.get_json(silent=True) or {}
        raw_responses = data.get("responses")
        if not isinstance(raw_responses, list):
            raise ValueError("responses must be a list")
        diagnostic = load_toeic_reading_diagnostic()
        expected_ids = {item["id"] for item in diagnostic["items"]}
        supplied_ids = [str(response.get("item_id", "")) for response in raw_responses if isinstance(response, dict)]
        if len(raw_responses) != len(expected_ids) or set(supplied_ids) != expected_ids or len(set(supplied_ids)) != len(supplied_ids):
            raise ValueError("All diagnostic items must be answered exactly once")

        created_responses = []
        for raw_response in raw_responses:
            if not isinstance(raw_response, dict):
                raise ValueError("Each response must be an object")
            item = get_diagnostic_item(str(raw_response.get("item_id", "")))
            if not item:
                raise ValueError("Unknown diagnostic item")
            try:
                selected_index = int(raw_response.get("selected_index"))
            except (TypeError, ValueError) as exc:
                raise ValueError("selected_index must identify one proposed answer") from exc
            if not 0 <= selected_index < len(item["choices"]):
                raise ValueError("selected_index is outside the available choices")
            response = DiagnosticResponse(
                attempt_id=attempt.id,
                item_id=item["id"],
                task_type=item["task_type"],
                target=item["target"],
                scenario=item["scenario"],
                selected_index=selected_index,
                is_correct=selected_index == item["correct_index"],
                response_time_seconds=_safe_seconds(raw_response.get("response_time_seconds")),
                confidence=_safe_confidence(raw_response.get("confidence")),
                created_at=_utcnow_naive(),
            )
            db.session.add(response)
            created_responses.append(response)

        db.session.flush()
        attempt.correct_count = sum(response.is_correct for response in created_responses)
        attempt.status = "completed"
        attempt.completed_at = _utcnow_naive()
        attempt.duration_seconds = _safe_seconds(data.get("duration_seconds"))
        if attempt.duration_seconds is None and attempt.started_at:
            attempt.duration_seconds = max(0.0, (attempt.completed_at - attempt.started_at).total_seconds())
        db.session.commit()
        analysis = _analysis_from_responses(created_responses)
        return jsonify({
            "status": "success",
            "attempt": attempt.to_dict(),
            "analysis": analysis,
            "disclaimer": "Résultats descriptifs issus de ce diagnostic original ; aucune estimation de score TOEIC n’est fournie.",
        })
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to submit the diagnostic attempt."}), 500


@diagnostic_bp.route("/attempts/<int:attempt_id>/create-remediation", methods=["POST"])
@jwt_required()
def create_diagnostic_remediation(attempt_id):
    """Create optional FSRS cards only for reusable errors selected by the learner."""
    try:
        user_id = int(get_jwt_identity())
        attempt = DiagnosticAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
        if not attempt:
            return jsonify({"status": "error", "message": "Diagnostic attempt not found"}), 404
        if attempt.status != "completed":
            return jsonify({"status": "error", "message": "Submit the diagnostic before creating remediation cards"}), 409

        data = request.get_json(silent=True) or {}
        requested_targets = data.get("targets")
        if requested_targets is not None and (
            not isinstance(requested_targets, list) or not all(isinstance(target, str) for target in requested_targets)
        ):
            raise ValueError("targets must be a list of target names")
        requested_targets = set(requested_targets or [])

        created_cards = []
        skipped_count = 0
        for response in attempt.responses:
            if response.is_correct or (requested_targets and response.target not in requested_targets):
                continue
            item = get_diagnostic_item(response.item_id)
            remediation = item.get("remediation") if item else None
            if not remediation:
                skipped_count += 1
                continue
            front = remediation["front"]
            back = remediation["back"]
            existing = Card.query.filter_by(
                user_id=user_id,
                subject_id=attempt.subject_id,
                front_content=front,
                back_content=back,
            ).first()
            if existing:
                skipped_count += 1
                continue
            card = Card(
                user_id=user_id,
                subject_id=attempt.subject_id,
                learning_domain="language",
                concept_name=remediation["concept_name"],
                front_content=front,
                back_content=back,
                difficulty="medium",
                priority="normal",
                tags=",".join(remediation["tags"]),
                next_review=_utcnow_naive(),
            )
            db.session.add(card)
            db.session.flush()
            created_cards.append(card)

        db.session.commit()
        return jsonify({
            "status": "success",
            "created_count": len(created_cards),
            "skipped_count": skipped_count,
            "cards": [card.to_dict() for card in created_cards],
            "message": "Les cartes créées sont des remédiations optionnelles et rejoignent les revues FSRS du domaine langue.",
        }), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to create remediation cards."}), 500
