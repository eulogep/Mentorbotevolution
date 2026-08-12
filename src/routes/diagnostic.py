"""Authenticated formative diagnostic routes with server-enforced review boundaries."""

from collections import defaultdict
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, send_file, url_for
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.content.toeic_listening_conversations_talks import (
    TOEIC_LISTENING_CONVERSATIONS_TALKS_ID,
    get_toeic_listening_conversations_talks_audio_path,
    get_toeic_listening_conversations_talks_diagnostic as load_toeic_listening_conversations_talks,
    get_toeic_listening_conversations_talks_item,
    get_toeic_listening_conversations_talks_stimulus,
)
from src.content.toeic_listening_question_response import (
    TOEIC_LISTENING_QUESTION_RESPONSE_ID,
    get_toeic_listening_question_response_diagnostic as load_toeic_listening_question_response,
    get_toeic_listening_question_response_item,
)
from src.content.toeic_reading_diagnostic import (
    TOEIC_READING_DIAGNOSTIC_ID,
    get_diagnostic_item as get_toeic_reading_item,
    get_toeic_reading_diagnostic as load_toeic_reading_diagnostic,
)
from src.models.user import (
    Card,
    DiagnosticAttempt,
    DiagnosticResponse,
    DiagnosticStimulusPlayback,
    Subject,
    db,
)


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


def _no_store(payload, status=200):
    """Return a JSON response that user agents and intermediaries must not cache."""
    response = jsonify(payload)
    response.status_code = status
    response.headers["Cache-Control"] = "no-store"
    return response


def _reading_catalog():
    return load_toeic_reading_diagnostic(), get_toeic_reading_item


def _listening_catalog():
    return load_toeic_listening_question_response(), get_toeic_listening_question_response_item


def _shared_listening_catalog():
    return load_toeic_listening_conversations_talks(), get_toeic_listening_conversations_talks_item


def _catalog_for_diagnostic_id(diagnostic_id):
    if diagnostic_id == TOEIC_READING_DIAGNOSTIC_ID:
        return _reading_catalog()
    if diagnostic_id == TOEIC_LISTENING_QUESTION_RESPONSE_ID:
        return _listening_catalog()
    if diagnostic_id == TOEIC_LISTENING_CONVERSATIONS_TALKS_ID:
        return _shared_listening_catalog()
    raise ValueError("Unknown diagnostic")


def _stimulus_loader_for_diagnostic_id(diagnostic_id):
    if diagnostic_id == TOEIC_LISTENING_CONVERSATIONS_TALKS_ID:
        return get_toeic_listening_conversations_talks_stimulus
    return None


def _public_item(item):
    """Expose a reading item without answer, explanation or remediation metadata."""
    return {
        key: value
        for key, value in item.items()
        if key not in {"correct_index", "explanation", "remediation"}
    }


def _public_listening_item(item):
    """Expose question-response metadata without scripts, options, or correction data."""
    return {
        key: value
        for key, value in item.items()
        if key not in {"choices", "transcript", "correct_index", "explanation", "remediation"}
    }


def _public_shared_listening_item(item):
    """Whitelist only non-sensitive fields required to render one shared-stimulus question."""
    permitted = {"id", "stimulus_id", "task_type", "target", "scenario", "choice_labels"}
    return {key: item[key] for key in permitted if key in item}


def _public_shared_listening_stimulus(stimulus, attempt_id=None):
    """Whitelist media metadata while keeping every transcript and speaker label private."""
    permitted = {
        "id",
        "task_type",
        "scenario",
        "audio_id",
        "audio_status",
        "script_version",
        "audio_duration_seconds",
        "max_plays",
    }
    public_stimulus = {key: stimulus[key] for key in permitted if key in stimulus}
    if attempt_id is not None:
        public_stimulus["audio_url"] = url_for(
            "diagnostic.get_shared_listening_audio",
            attempt_id=attempt_id,
            stimulus_id=stimulus["id"],
        )
    return public_stimulus


def _public_diagnostic_metadata(diagnostic):
    """Whitelist diagnostic-level metadata that contains no private editorial content."""
    permitted = {
        "id",
        "content_version",
        "title",
        "description",
        "learning_domain",
        "source",
        "disclaimer",
        "max_plays_per_item",
        "max_plays_per_stimulus",
    }
    return {key: diagnostic[key] for key in permitted if key in diagnostic}


def _listening_review_items(responses, item_loader):
    """Return question-response transcript and correction only after a completed attempt."""
    by_item_id = {response.item_id: response for response in responses}
    review_items = []
    for item_id, response in by_item_id.items():
        item = item_loader(item_id)
        if not item:
            continue
        review_items.append({
            "item_id": item_id,
            "transcript": item["transcript"],
            "choices": item["choices"],
            "correct_index": item["correct_index"],
            "selected_index": response.selected_index,
            "is_correct": response.is_correct,
            "explanation": item["explanation"],
        })
    return review_items


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
        raise ValueError("This diagnostic is available only for a language learning path")
    return subject


def _analysis_from_responses(responses, item_loader):
    grouped = defaultdict(list)
    for response in responses:
        grouped[response.target].append(response)

    items_by_id = {response.item_id: item_loader(response.item_id) or {} for response in responses}
    breakdown = []
    recommendations = []
    available_remediation_targets = []
    for target, target_responses in sorted(grouped.items()):
        total = len(target_responses)
        correct = sum(response.is_correct for response in target_responses)
        incorrect = total - correct
        accuracy = round(correct / total, 3) if total else None
        remediation_available = any(
            not response.is_correct and items_by_id[response.item_id].get("remediation")
            for response in target_responses
        )
        if remediation_available:
            available_remediation_targets.append(target)
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
                "message": "Reprenez des contenus analogues avec une justification des indices entendus ou lus ; cette cible relève d’abord de la compréhension.",
            })
        else:
            recommendations.append({
                "target": target,
                "code": "continue_sampling",
                "message": "Résultats observés sur un petit lot : continuez la pratique pour obtenir une mesure plus stable.",
            })

    return {
        "breakdown": breakdown,
        "recommendations": recommendations,
        # This marks an optional atomic card, not a performance conclusion.
        "available_remediation_targets": available_remediation_targets,
    }


def _start_attempt(diagnostic_id, loader, public_item_loader, public_stimulus_loader=None):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    subject = _subject_for_user(user_id, data.get("subject_id"))
    diagnostic = loader()
    attempt = DiagnosticAttempt(
        user_id=user_id,
        subject_id=subject.id if subject else None,
        diagnostic_id=diagnostic_id,
        content_version=diagnostic.get("content_version"),
        total_items=len(diagnostic["items"]),
        started_at=_utcnow_naive(),
    )
    db.session.add(attempt)
    db.session.commit()
    payload = {
        "status": "success",
        "attempt": attempt.to_dict(),
        "diagnostic": _public_diagnostic_metadata(diagnostic),
        "items": [public_item_loader(item) for item in diagnostic["items"]],
    }
    if public_stimulus_loader:
        payload["stimuli"] = [
            public_stimulus_loader(stimulus, attempt.id)
            for stimulus in diagnostic["stimuli"]
        ]
    return payload


def _owned_attempt_or_404(attempt_id):
    user_id = int(get_jwt_identity())
    attempt = DiagnosticAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
    if not attempt:
        return None
    return attempt


@diagnostic_bp.route("/toeic-reading", methods=["GET"])
@jwt_required()
def get_toeic_reading_diagnostic():
    """Expose original reading metadata, never answers or corrections."""
    diagnostic = load_toeic_reading_diagnostic()
    return jsonify({
        "status": "success",
        "diagnostic": _public_diagnostic_metadata(diagnostic),
        "items": [_public_item(item) for item in diagnostic["items"]],
    })


@diagnostic_bp.route("/toeic-reading/start", methods=["POST"])
@jwt_required()
def start_toeic_reading_diagnostic():
    """Create one fresh formative reading attempt for an explicit language path."""
    try:
        return jsonify(_start_attempt(TOEIC_READING_DIAGNOSTIC_ID, load_toeic_reading_diagnostic, _public_item)), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to start the reading diagnostic."}), 500


@diagnostic_bp.route("/toeic-listening-question-response", methods=["GET"])
@jwt_required()
def get_toeic_listening_question_response():
    """Expose Listening metadata and audio URLs without transcripts or corrections."""
    diagnostic = load_toeic_listening_question_response()
    return jsonify({
        "status": "success",
        "diagnostic": _public_diagnostic_metadata(diagnostic),
        "items": [_public_listening_item(item) for item in diagnostic["items"]],
    })


@diagnostic_bp.route("/toeic-listening-question-response/start", methods=["POST"])
@jwt_required()
def start_toeic_listening_question_response():
    """Create a Listening attempt with one permitted client-declared play per item."""
    try:
        return jsonify(_start_attempt(
            TOEIC_LISTENING_QUESTION_RESPONSE_ID,
            load_toeic_listening_question_response,
            _public_listening_item,
        )), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to start the listening diagnostic."}), 500


@diagnostic_bp.route("/toeic-listening-conversations-talks", methods=["GET"])
@jwt_required()
def get_toeic_listening_conversations_talks():
    """Expose shared-stimulus Listening metadata with a strict public whitelist."""
    diagnostic = load_toeic_listening_conversations_talks()
    return _no_store({
        "status": "success",
        "diagnostic": _public_diagnostic_metadata(diagnostic),
        "stimuli": [_public_shared_listening_stimulus(stimulus) for stimulus in diagnostic["stimuli"]],
        "items": [_public_shared_listening_item(item) for item in diagnostic["items"]],
    })


@diagnostic_bp.route("/toeic-listening-conversations-talks/start", methods=["POST"])
@jwt_required()
def start_toeic_listening_conversations_talks():
    """Create a shared-stimulus Listening attempt for one language learning path."""
    try:
        payload = _start_attempt(
            TOEIC_LISTENING_CONVERSATIONS_TALKS_ID,
            load_toeic_listening_conversations_talks,
            _public_shared_listening_item,
            _public_shared_listening_stimulus,
        )
        return _no_store(payload, 201)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to start the shared Listening diagnostic."}), 500


@diagnostic_bp.route("/attempts/<int:attempt_id>/stimuli/<string:stimulus_id>/playback", methods=["POST"])
@jwt_required()
def register_listening_stimulus_playback(attempt_id, stimulus_id):
    """Register the single server-authorized play for a shared Listening stimulus."""
    try:
        attempt = _owned_attempt_or_404(attempt_id)
        if not attempt:
            return jsonify({"status": "error", "message": "Diagnostic attempt not found"}), 404
        if attempt.diagnostic_id != TOEIC_LISTENING_CONVERSATIONS_TALKS_ID:
            return jsonify({"status": "error", "message": "This attempt has no shared Listening stimuli"}), 404
        if attempt.status != "in_progress":
            return jsonify({"status": "error", "message": "This diagnostic attempt has already been submitted"}), 409
        stimulus = get_toeic_listening_conversations_talks_stimulus(stimulus_id)
        if not stimulus:
            raise ValueError("Unknown listening stimulus")
        if stimulus.get("audio_status") != "available":
            return jsonify({"status": "error", "message": "This audio stimulus is not available"}), 409
        existing = DiagnosticStimulusPlayback.query.filter_by(
            attempt_id=attempt.id,
            stimulus_id=stimulus_id,
        ).first()
        if existing:
            return jsonify({"status": "error", "message": "The listening play limit was already used"}), 409

        now = _utcnow_naive()
        playback = DiagnosticStimulusPlayback(
            attempt_id=attempt.id,
            stimulus_id=stimulus_id,
            audio_id=stimulus["audio_id"],
            script_version=stimulus["script_version"],
            audio_duration_seconds=stimulus.get("audio_duration_seconds"),
            play_count=1,
            first_played_at=now,
            last_played_at=now,
        )
        db.session.add(playback)
        db.session.commit()
        public_playback = playback.to_dict()
        public_playback["audio_url"] = url_for(
            "diagnostic.get_shared_listening_audio",
            attempt_id=attempt.id,
            stimulus_id=stimulus_id,
        )
        return _no_store({"status": "success", "playback": public_playback}, 201)
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "The listening play limit was already used"}), 409
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to register Listening playback."}), 500


@diagnostic_bp.route("/attempts/<int:attempt_id>/stimuli/<string:stimulus_id>/audio", methods=["GET"])
@jwt_required()
def get_shared_listening_audio(attempt_id, stimulus_id):
    """Serve one private WAV only to its attempt owner after server-authorized playback."""
    attempt = _owned_attempt_or_404(attempt_id)
    if not attempt or attempt.diagnostic_id != TOEIC_LISTENING_CONVERSATIONS_TALKS_ID:
        return jsonify({"status": "error", "message": "Diagnostic attempt not found"}), 404
    playback = DiagnosticStimulusPlayback.query.filter_by(
        attempt_id=attempt.id,
        stimulus_id=stimulus_id,
    ).first()
    if not playback:
        return jsonify({"status": "error", "message": "Authorize the single listening playback before requesting audio"}), 409
    audio_path = get_toeic_listening_conversations_talks_audio_path(stimulus_id)
    if not audio_path:
        return jsonify({"status": "error", "message": "This audio stimulus is not available"}), 404
    response = send_file(audio_path, mimetype="audio/wav", conditional=False, max_age=0)
    response.headers["Cache-Control"] = "no-store"
    return response


@diagnostic_bp.route("/attempts/<int:attempt_id>/submit", methods=["POST"])
@jwt_required()
def submit_diagnostic_attempt(attempt_id):
    """Store answers and return descriptive feedback, never a TOEIC score estimate."""
    try:
        attempt = _owned_attempt_or_404(attempt_id)
        if not attempt:
            return jsonify({"status": "error", "message": "Diagnostic attempt not found"}), 404
        if attempt.status != "in_progress":
            return jsonify({"status": "error", "message": "This diagnostic attempt has already been submitted"}), 409

        diagnostic, item_loader = _catalog_for_diagnostic_id(attempt.diagnostic_id)
        shared_stimulus_loader = _stimulus_loader_for_diagnostic_id(attempt.diagnostic_id)
        data = request.get_json(silent=True) or {}
        raw_responses = data.get("responses")
        if not isinstance(raw_responses, list):
            raise ValueError("responses must be a list")
        expected_ids = {item["id"] for item in diagnostic["items"]}
        supplied_ids = [str(response.get("item_id", "")) for response in raw_responses if isinstance(response, dict)]
        if len(raw_responses) != len(expected_ids) or set(supplied_ids) != expected_ids or len(set(supplied_ids)) != len(supplied_ids):
            raise ValueError("All diagnostic items must be answered exactly once")

        playback_by_stimulus = {}
        if shared_stimulus_loader:
            playback_by_stimulus = {
                playback.stimulus_id: playback
                for playback in DiagnosticStimulusPlayback.query.filter_by(attempt_id=attempt.id).all()
            }

        created_responses = []
        for raw_response in raw_responses:
            if not isinstance(raw_response, dict):
                raise ValueError("Each response must be an object")
            item = item_loader(str(raw_response.get("item_id", "")))
            if not item:
                raise ValueError("Unknown diagnostic item")
            try:
                selected_index = int(raw_response.get("selected_index"))
            except (TypeError, ValueError) as exc:
                raise ValueError("selected_index must identify one proposed answer") from exc
            if not 0 <= selected_index < len(item["choices"]):
                raise ValueError("selected_index is outside the available choices")

            stimulus_id = None
            audio_id = None
            script_version = None
            audio_duration_seconds = None
            play_count = None
            if shared_stimulus_loader:
                forbidden_client_fields = {"play_count", "audio_id", "script_version", "transcript", "choices", "correct_index"}
                if forbidden_client_fields.intersection(raw_response):
                    raise ValueError("Shared Listening playback and correction fields are server-managed")
                stimulus_id = item["stimulus_id"]
                playback = playback_by_stimulus.get(stimulus_id)
                if not playback or playback.play_count != 1:
                    raise ValueError("Listen to each audio stimulus before responding")
                stimulus = shared_stimulus_loader(stimulus_id)
                if not stimulus or stimulus.get("audio_status") != "available":
                    raise ValueError("The required audio stimulus is unavailable")
                audio_id = playback.audio_id
                script_version = playback.script_version
                audio_duration_seconds = playback.audio_duration_seconds
                play_count = playback.play_count
            elif item.get("task_type", "").startswith("listening_"):
                try:
                    play_count = int(raw_response.get("play_count", 0))
                except (TypeError, ValueError) as exc:
                    raise ValueError("play_count must be a whole number for a listening item") from exc
                if play_count < 1:
                    raise ValueError("Listen to each audio item before responding")
                if play_count > item.get("max_plays", diagnostic.get("max_plays_per_item", 1)):
                    raise ValueError("The listening play limit was exceeded")
                audio_id = item["audio_id"]
                script_version = item.get("script_version")

            response = DiagnosticResponse(
                attempt_id=attempt.id,
                item_id=item["id"],
                task_type=item["task_type"],
                target=item["target"],
                scenario=item["scenario"],
                stimulus_id=stimulus_id,
                audio_id=audio_id,
                script_version=script_version,
                audio_duration_seconds=audio_duration_seconds,
                play_count=play_count,
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
        analysis = _analysis_from_responses(created_responses, item_loader)
        result = {
            "status": "success",
            "attempt": attempt.to_dict(),
            "analysis": analysis,
            "disclaimer": "Résultats descriptifs issus de ce diagnostic original ; aucune estimation de score TOEIC n’est fournie.",
        }
        if attempt.diagnostic_id == TOEIC_LISTENING_QUESTION_RESPONSE_ID:
            result["review_items"] = _listening_review_items(created_responses, item_loader)
        if attempt.diagnostic_id == TOEIC_LISTENING_CONVERSATIONS_TALKS_ID:
            return _no_store(result)
        return jsonify(result)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Unable to submit the diagnostic attempt."}), 500


@diagnostic_bp.route("/attempts/<int:attempt_id>/listening-review", methods=["GET"])
@jwt_required()
def get_shared_listening_review(attempt_id):
    """Expose transcript and corrections only after the owner has completed the attempt."""
    attempt = _owned_attempt_or_404(attempt_id)
    if not attempt or attempt.diagnostic_id != TOEIC_LISTENING_CONVERSATIONS_TALKS_ID:
        return jsonify({"status": "error", "message": "Diagnostic attempt not found"}), 404
    if attempt.status != "completed":
        return jsonify({"status": "error", "message": "Submit the diagnostic before the post-submission review"}), 409

    diagnostic = load_toeic_listening_conversations_talks()
    responses_by_item = {response.item_id: response for response in attempt.responses}
    items_by_stimulus = defaultdict(list)
    for item in diagnostic["items"]:
        response = responses_by_item.get(item["id"])
        if not response:
            continue
        items_by_stimulus[item["stimulus_id"]].append({
            "item_id": item["id"],
            "choices": item["choices"],
            "correct_index": item["correct_index"],
            "selected_index": response.selected_index,
            "is_correct": response.is_correct,
            "explanation": item["explanation"],
        })

    review_stimuli = []
    for stimulus in diagnostic["stimuli"]:
        review_stimuli.append({
            "stimulus_id": stimulus["id"],
            "audio_url": url_for(
                "diagnostic.get_shared_listening_audio",
                attempt_id=attempt.id,
                stimulus_id=stimulus["id"],
            ),
            "speaker_transcript": stimulus["speaker_transcript"],
            "items": items_by_stimulus[stimulus["id"]],
        })
    return _no_store({
        "status": "success",
        "attempt": attempt.to_dict(),
        "review_stimuli": review_stimuli,
    })


@diagnostic_bp.route("/attempts/<int:attempt_id>/create-remediation", methods=["POST"])
@jwt_required()
def create_diagnostic_remediation(attempt_id):
    """Create optional FSRS cards only for reusable errors selected by the learner."""
    try:
        attempt = _owned_attempt_or_404(attempt_id)
        if not attempt:
            return jsonify({"status": "error", "message": "Diagnostic attempt not found"}), 404
        if attempt.status != "completed":
            return jsonify({"status": "error", "message": "Submit the diagnostic before creating remediation cards"}), 409

        _, item_loader = _catalog_for_diagnostic_id(attempt.diagnostic_id)
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
            item = item_loader(response.item_id)
            remediation = item.get("remediation") if item else None
            if not remediation:
                skipped_count += 1
                continue
            front = remediation["front"]
            back = remediation["back"]
            existing = Card.query.filter_by(
                user_id=attempt.user_id,
                subject_id=attempt.subject_id,
                front_content=front,
                back_content=back,
            ).first()
            if existing:
                skipped_count += 1
                continue
            card = Card(
                user_id=attempt.user_id,
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
