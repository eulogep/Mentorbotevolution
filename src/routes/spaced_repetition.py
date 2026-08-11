"""API de répétition espacée et de pratique de récupération.

La planification s’appuie sur FSRS et conserve les champs SM-2 historiques pour
une migration progressive des cartes existantes. Les réponses sont journalisées
pour rendre les décisions explicables et permettre une optimisation future.
"""

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.models.user import Card, ReviewLog, StudySession, User, db
from src.services.fsrs_scheduler import (
    DEFAULT_RETENTION,
    MAX_RETENTION,
    MIN_RETENTION,
    FSRS_VERSION,
    describe_rating,
    normalize_desired_retention,
    normalize_rating,
    review_with_fsrs,
)
from src.services.pipeline_flashcard_import import import_pipeline_flashcards

spaced_repetition_bp = Blueprint("spaced_repetition", __name__)


def _utcnow_naive() -> datetime:
    """Return a UTC timestamp compatible with the project’s current schema."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _safe_limit(raw_limit, default=20, maximum=100):
    try:
        return max(1, min(maximum, int(raw_limit)))
    except (TypeError, ValueError):
        return default


def _safe_response_time(value) -> float:
    try:
        return max(0.0, min(3600.0, float(value or 0)))
    except (TypeError, ValueError):
        return 0.0


@spaced_repetition_bp.route("/create-card", methods=["POST"])
@jwt_required()
def create_spaced_repetition_card():
    """Create a card that is immediately eligible for active recall."""
    try:
        data = request.get_json(silent=True) or {}
        user_id = int(get_jwt_identity())

        concept_name = str(data.get("concept_name", "")).strip()
        if not concept_name:
            return jsonify({"status": "error", "message": "concept_name is required"}), 400

        tags = data.get("tags", [])
        card = Card(
            user_id=user_id,
            subject_id=data.get("subject_id"),
            concept_name=concept_name,
            front_content=str(data.get("content", data.get("front_content", ""))).strip(),
            back_content=str(data.get("back_content", "")).strip(),
            difficulty=data.get("difficulty", "medium"),
            priority=data.get("priority", "normal"),
            tags=",".join(tags) if isinstance(tags, list) else "",
            next_review=_utcnow_naive(),
        )
        db.session.add(card)
        db.session.commit()

        return jsonify({
            "status": "success",
            "card": card.to_dict(),
            "message": "Carte créée : elle est disponible pour une première récupération active.",
        })
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Impossible de créer la carte."}), 500


@spaced_repetition_bp.route("/review-card", methods=["POST"])
@jwt_required()
def review_card():
    """Record one recall attempt and schedule its next retrieval with FSRS."""
    try:
        data = request.get_json(silent=True) or {}
        user_id = int(get_jwt_identity())
        card_id = data.get("card_id")
        if card_id is None:
            return jsonify({"status": "error", "message": "card_id is required"}), 400

        rating_name, rating = normalize_rating(data)
        card = Card.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return jsonify({"status": "error", "message": "Card not found"}), 404

        user = db.session.get(User, user_id)
        retention_target = normalize_desired_retention(
            user.desired_retention if user else DEFAULT_RETENTION
        )
        result = review_with_fsrs(card.scheduler_state, rating, retention_target)
        response_time = _safe_response_time(data.get("response_time"))

        # FSRS becomes the source of truth. Legacy aggregates are maintained so
        # existing endpoints and historical cards remain usable during migration.
        card.scheduler_type = "fsrs"
        card.scheduler_state = result["card_state"]
        card.scheduler_version = FSRS_VERSION
        card.interval = result["scheduled_days"]
        card.review_count += 1
        if rating_name != "again":
            card.success_count += 1
        card.total_response_time += response_time
        card.last_reviewed = result["reviewed_at"]
        card.next_review = result["due_at"]

        db.session.add(ReviewLog(
            user_id=user_id,
            card_id=card.id,
            rating=rating_name,
            response_time=response_time,
            retrievability_before=result["retrievability_before"],
            scheduled_days=result["scheduled_days"],
            scheduler_version=FSRS_VERSION,
            previous_state=result["previous_state"],
            review_log=result["review_log"],
            next_state=result["card_state"],
            reviewed_at=result["reviewed_at"],
        ))
        db.session.commit()

        feedback = describe_rating(rating_name, result["scheduled_days"])
        return jsonify({
            "status": "success",
            "updated_card": card.to_dict(),
            "feedback": feedback,
            "rating": rating_name,
            "next_review_in_days": result["scheduled_days"],
            "next_review_at": card.next_review.isoformat(),
            "retention_target": result["retention_target"],
            "memory_state": result["memory_state"],
            "retrievability_before": result["retrievability_before"],
            # Legacy alias preserved for clients that previously expected it.
            "retention_probability": result["retrievability_after"],
        })
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Impossible d’enregistrer cette révision."}), 500


@spaced_repetition_bp.route("/get-due-cards", methods=["GET"])
@jwt_required()
def get_due_cards():
    """Return due cards ordered by their actual next review timestamp."""
    try:
        user_id = int(get_jwt_identity())
        limit = _safe_limit(request.args.get("limit"), default=20)
        due_cards = (
            Card.query
            .filter(Card.user_id == user_id, Card.next_review <= _utcnow_naive())
            .order_by(Card.next_review.asc())
            .limit(limit)
            .all()
        )
        cards_data = [card.to_dict() for card in due_cards]
        average_seconds = (
            sum(card.average_response_time for card in due_cards if card.review_count > 0)
            / max(1, sum(1 for card in due_cards if card.review_count > 0))
        )
        estimated_minutes = max(1, round((average_seconds or 90) * len(due_cards) / 60)) if due_cards else 0

        return jsonify({
            "status": "success",
            "due_cards": cards_data,
            "total_due": len(cards_data),
            "estimated_time_minutes": estimated_minutes,
            "scheduling_method": "FSRS pour les cartes déjà migrées ; état initial pour les nouvelles cartes.",
        })
    except Exception:
        return jsonify({"status": "error", "message": "Impossible de récupérer les cartes dues."}), 500


@spaced_repetition_bp.route("/settings", methods=["GET"])
@jwt_required()
def get_spaced_repetition_settings():
    """Expose the learner’s explicit retention target and its trade-off."""
    user = db.session.get(User, int(get_jwt_identity()))
    retention = normalize_desired_retention(user.desired_retention if user else DEFAULT_RETENTION)
    return jsonify({
        "status": "success",
        "desired_retention": retention,
        "bounds": {"min": MIN_RETENTION, "max": MAX_RETENTION},
        "explanation": "Une rétention cible plus élevée augmente le nombre de révisions quotidiennes prévues.",
    })


@spaced_repetition_bp.route("/settings", methods=["PUT"])
@jwt_required()
def update_spaced_repetition_settings():
    """Persist an informed retention preference instead of hidden tuning."""
    data = request.get_json(silent=True) or {}
    try:
        requested_retention = float(data.get("desired_retention"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "desired_retention must be a number"}), 400
    if not MIN_RETENTION <= requested_retention <= MAX_RETENTION:
        return jsonify({
            "status": "error",
            "message": f"desired_retention must be between {MIN_RETENTION} and {MAX_RETENTION}",
        }), 400

    try:
        user = db.session.get(User, int(get_jwt_identity()))
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        user.desired_retention = requested_retention
        db.session.commit()
        return jsonify({"status": "success", "desired_retention": user.desired_retention})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Impossible de mettre à jour la rétention cible."}), 500


@spaced_repetition_bp.route("/get-schedule", methods=["GET"])
@jwt_required()
def get_review_schedule():
    """Summarize the real workload generated by scheduled cards."""
    try:
        user_id = int(get_jwt_identity())
        days_ahead = _safe_limit(request.args.get("days_ahead"), default=7, maximum=60)
        schedule = {}
        base_date = _utcnow_naive().date()

        for day_offset in range(days_ahead):
            current_date = base_date + timedelta(days=day_offset)
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())
            day_cards = (
                Card.query.filter(
                    Card.user_id == user_id,
                    Card.next_review >= day_start,
                    Card.next_review <= day_end,
                ).all()
            )
            cards_count = len(day_cards)
            date_str = current_date.isoformat()
            estimated_minutes = max(1, round(cards_count * 1.5)) if cards_count else 0
            schedule[date_str] = {
                "date": date_str,
                "cards_due": cards_count,
                "estimated_time_minutes": estimated_minutes,
                "difficulty_distribution": {
                    "easy": sum(card.difficulty == "easy" for card in day_cards),
                    "medium": sum(card.difficulty == "medium" for card in day_cards),
                    "hard": sum(card.difficulty == "hard" for card in day_cards),
                },
                "workload": "light" if cards_count < 10 else "moderate" if cards_count < 20 else "heavy",
            }

        total_minutes = sum(day["estimated_time_minutes"] for day in schedule.values())
        peak_day = max(schedule, key=lambda date: schedule[date]["cards_due"]) if schedule else None
        return jsonify({
            "status": "success",
            "schedule": schedule,
            "summary": {
                "total_cards": sum(day["cards_due"] for day in schedule.values()),
                "total_time_hours": round(total_minutes / 60, 1),
                "peak_day": peak_day,
                "light_days": sum(day["workload"] == "light" for day in schedule.values()),
            },
        })
    except Exception:
        return jsonify({"status": "error", "message": "Impossible de générer le calendrier."}), 500


@spaced_repetition_bp.route("/performance-analytics", methods=["GET"])
@jwt_required()
def get_performance_analytics():
    """Return descriptive analytics, never fabricated score predictions."""
    try:
        user_id = int(get_jwt_identity())
        period_days = _safe_limit(request.args.get("period_days"), default=30, maximum=365)
        cutoff = _utcnow_naive() - timedelta(days=period_days)
        all_cards = Card.query.filter_by(user_id=user_id).all()
        review_logs = (
            ReviewLog.query.filter(
                ReviewLog.user_id == user_id,
                ReviewLog.reviewed_at >= cutoff,
            ).order_by(ReviewLog.reviewed_at.desc()).all()
        )
        sessions = (
            StudySession.query.filter(
                StudySession.user_id == user_id,
                StudySession.started_at >= cutoff,
            ).order_by(StudySession.started_at.desc()).all()
        )
        ratings = {name: sum(log.rating == name for log in review_logs) for name in ("again", "hard", "good", "easy")}
        successful_reviews = ratings["hard"] + ratings["good"] + ratings["easy"]
        success_rate = round(successful_reviews / len(review_logs), 3) if review_logs else 0.0
        avg_response_time = round(
            sum(log.response_time for log in review_logs) / len(review_logs), 1
        ) if review_logs else 0.0
        fragile_cards = [
            card.to_dict() for card in all_cards
            if card.review_count >= 2 and card.success_rate < 0.60
        ][:5]

        insights = []
        if not review_logs:
            insights.append("Aucune revue enregistrée sur la période : effectuez une session pour obtenir des données personnelles.")
        elif ratings["again"]:
            insights.append("Les cartes notées « À revoir » sont prioritaires : reliez-les à un exemple avant la prochaine tentative.")
        if review_logs and success_rate >= 0.8:
            insights.append("Vos rappels récents sont solides. Conservez un rythme régulier plutôt que de masser les révisions.")
        if fragile_cards:
            insights.append("Certaines cartes restent fragiles ; réduisez leur périmètre ou ajoutez un exemple concret.")

        return jsonify({
            "status": "success",
            "analytics": {
                "period_days": period_days,
                "total_cards": len(all_cards),
                "total_reviews": len(review_logs),
                "average_success_rate": success_rate,
                "average_response_time": avg_response_time,
                "ratings": ratings,
                "fragile_cards": fragile_cards,
                "recent_sessions": [session.to_dict() for session in sessions[:10]],
            },
            "insights": insights,
        })
    except Exception:
        return jsonify({"status": "error", "message": "Impossible de calculer les analyses."}), 500


@spaced_repetition_bp.route("/import-pipeline-flashcards", methods=["POST"])
@jwt_required()
def import_pipeline_cards():
    """Persist pipeline cards for the authenticated user."""
    try:
        user_id = int(get_jwt_identity())
        result = import_pipeline_flashcards(user_id, request.get_json(silent=True) or {})
        if result.get("status") == "error":
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception:
        return jsonify({"status": "error", "message": "Impossible d’importer les cartes du pipeline."}), 500
