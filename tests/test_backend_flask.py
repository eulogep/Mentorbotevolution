import io
import os
import sys
import uuid

import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-with-enough-length-for-hs256"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-with-enough-length-for-hs256"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app, get_database_uri, should_auto_create_tables  # noqa: E402
from src.content.toeic_listening_conversations_talks import (  # noqa: E402
    get_toeic_listening_conversations_talks_item,
)
from src.content.toeic_listening_question_response import get_toeic_listening_question_response_item  # noqa: E402
from src.content.toeic_listening_multi_speaker import get_toeic_listening_multi_speaker_item  # noqa: E402
from src.content.toeic_reading_diagnostic import get_diagnostic_item  # noqa: E402
from src.models.user import (  # noqa: E402
    Card,
    Concept,
    DiagnosticResponse,
    DiagnosticStimulusPlayback,
    StudySession,
    Subject,
    db,
)
from src.utils import document_extraction  # noqa: E402


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def auth_headers(client):
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"user_{suffix}",
        "email": f"user_{suffix}@example.com",
        "password": "password123",
    }
    register_response = client.post("/api/user/register", json=payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/user/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_flask_routes_start(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_database_url_postgres_scheme_is_normalized(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/app")
    assert get_database_uri() == "postgresql://user:pass@localhost:5432/app"


def test_flask_migrate_extension_is_registered():
    assert "migrate" in app.extensions


def test_database_auto_create_policy_prefers_migrations_for_postgres(monkeypatch):
    monkeypatch.delenv("AUTO_CREATE_DB", raising=False)
    assert should_auto_create_tables("sqlite:///:memory:") is True
    assert should_auto_create_tables("postgresql://user:pass@localhost:5432/app") is False

    monkeypatch.setenv("AUTO_CREATE_DB", "true")
    assert should_auto_create_tables("postgresql://user:pass@localhost:5432/app") is True

    monkeypatch.setenv("AUTO_CREATE_DB", "false")
    assert should_auto_create_tables("sqlite:///:memory:") is False


def test_register_and_login(client):
    email = "learner@example.com"
    register_response = client.post(
        "/api/user/register",
        json={"username": "learner", "email": email, "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/user/login",
        json={"email": email, "password": "password123"},
    )
    assert login_response.status_code == 200
    body = login_response.get_json()
    assert body["access_token"]
    assert body["user_id"]


def test_analyze_plain_text_upload(client, auth_headers):
    data = {
        "file": (
            io.BytesIO(
                b"Business vocabulary and conditional sentences improve TOEIC reading comprehension."
            ),
            "lesson.txt",
        )
    }
    response = client.post(
        "/api/analysis/analyze-document",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    analysis = response.get_json()["analysis"]
    assert analysis["extraction_method"] == "plain_text"
    assert analysis["is_simulated"] is False
    assert analysis["word_count"] > 0


def test_analyze_pdf_upload_when_pymupdf_available(client, auth_headers):
    fitz = pytest.importorskip("fitz")

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "PDF grammar lesson for TOEIC conditional sentences.")
    pdf_bytes = document.tobytes()
    document.close()

    response = client.post(
        "/api/analysis/analyze-document",
        headers=auth_headers,
        data={"file": (io.BytesIO(pdf_bytes), "lesson.pdf")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    analysis = response.get_json()["analysis"]
    assert analysis["extraction_method"] == "pdf_text"
    assert analysis["is_simulated"] is False
    assert "PDF grammar lesson" in analysis["extracted_text"]


def test_pdf_extraction_error_uses_stable_public_reason():
    result = document_extraction.extract_text_from_pdf(io.BytesIO(b"not a real pdf"))
    assert result.text == ""
    assert result.method == "pdf_error"
    assert result.fallback_reason == "PDF text extraction failed"
    assert "not a real pdf" not in result.fallback_reason


def test_image_ocr_failure_sentinel_is_not_treated_as_text(monkeypatch):
    class FakeUpload(io.BytesIO):
        content_type = "image/png"
        filename = "scan.png"

    monkeypatch.setattr(
        document_extraction,
        "extract_text_from_image",
        lambda _file: "[OCR Failed: tesseract missing]",
    )

    result = document_extraction.extract_text_from_document(FakeUpload(b"image"))
    assert result.text == ""
    assert result.method == "image_ocr_failed"
    assert result.fallback_reason == "Image OCR failed"


def test_create_and_review_spaced_repetition_card(client, auth_headers):
    create_response = client.post(
        "/api/spaced-repetition/create-card",
        headers=auth_headers,
        json={
            "concept_name": "Conditional Sentences",
            "content": "Explain if clauses",
        },
    )
    assert create_response.status_code == 200
    card = create_response.get_json()["card"]

    review_response = client.post(
        "/api/spaced-repetition/review-card",
        headers=auth_headers,
        json={"card_id": card["id"], "quality_response": 4, "response_time": 12.5},
    )
    assert review_response.status_code == 200
    body = review_response.get_json()
    assert body["next_review_in_days"] > 0
    assert body["next_review_in_minutes"] > 0
    assert body["updated_card"]["review_count"] == 1
    assert body["updated_card"]["interval_minutes"] == body["next_review_in_minutes"]
    assert body["updated_card"]["interval"] == body["next_review_in_minutes"] // 1440
    assert body["updated_card"]["scheduler_type"] == "fsrs"
    assert body["rating"] == "good"

    with app.app_context():
        from src.models.user import ReviewLog
        review_log = ReviewLog.query.one()
        assert review_log.rating == "good"
        assert review_log.scheduled_minutes == body["next_review_in_minutes"]
        assert review_log.scheduled_days == body["updated_card"]["interval"]


def test_update_progress_creates_study_session(client, auth_headers):
    with app.app_context():
        subject = Subject(user_id=1, name="TOEIC", status="in_progress")
        db.session.add(subject)
        db.session.flush()
        concept = Concept(subject_id=subject.id, name="Reading Speed")
        db.session.add(concept)
        db.session.commit()
        concept_id = concept.id

    response = client.post(
        "/api/analysis/update-progress",
        headers=auth_headers,
        json={
            "concept_id": concept_id,
            "mastery_level": 0.8,
            "retention_rate": 0.75,
            "time_spent": 25,
        },
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"

    with app.app_context():
        session = StudySession.query.filter_by(session_type="validation").one()
        assert session.duration_minutes == 25
        assert session.cards_reviewed == 1
        assert session.cards_correct == 1


def test_multidomain_catalog_and_explicit_computing_path(client, auth_headers):
    empty_response = client.get("/api/mastery/get-subjects", headers=auth_headers)
    assert empty_response.status_code == 200
    assert empty_response.get_json()["subjects"] == []

    catalog_response = client.get("/api/mastery/catalog", headers=auth_headers)
    assert catalog_response.status_code == 200
    catalog = catalog_response.get_json()
    template_ids = {template["id"] for template in catalog["templates"]}
    assert "computing-foundations" in template_ids
    assert "toeic-foundations" in template_ids

    create_response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={"template_id": "computing-foundations", "weekly_hours": 4},
    )
    assert create_response.status_code == 201
    subject = create_response.get_json()["subject"]
    assert subject["name"] == "Fondamentaux de l’informatique"
    assert subject["domain"] == "computing"
    assert subject["objective_type"] == "competency"
    assert subject["target_score"] is None
    assert subject["weekly_hours"] == 4
    assert len(subject["concepts"]) == 5
    assert subject["concepts"][0]["evidence_criterion"]


def test_custom_learning_path_supports_goal_and_deadline(client, auth_headers):
    response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={
            "name": "Automatiser mes rapports Excel",
            "domain": "productivity",
            "description": "Construire des tableaux mensuels reproductibles.",
            "objective_type": "competency",
            "objective_label": "Automatiser un rapport mensuel",
            "target_date": "2026-12-31",
            "weekly_hours": 2.5,
            "concepts": [
                {
                    "name": "Références structurées",
                    "competency_type": "procedure",
                    "evidence_criterion": "Construire une formule qui reste correcte après ajout de lignes.",
                }
            ],
        },
    )
    assert response.status_code == 201
    subject = response.get_json()["subject"]
    assert subject["domain"] == "productivity"
    assert subject["objective_label"] == "Automatiser un rapport mensuel"
    assert subject["target_date"] == "2026-12-31"
    assert subject["concepts"][0]["competency_type"] == "procedure"


def test_toeic_template_creates_original_starter_cards(client, auth_headers):
    response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={"template_id": "toeic-foundations"},
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["starter_pack"]["id"] == "toeic-business-vocabulary-foundations-v1"
    assert payload["starter_pack"]["cards_created"] == 36
    assert payload["starter_pack"]["learning_domain"] == "language"

    subject_id = payload["subject"]["id"]
    cards = Card.query.filter_by(subject_id=subject_id).all()
    assert len(cards) == 36
    assert {card.learning_domain for card in cards} == {"language"}
    assert all("toeic" in card.tags.split(",") for card in cards)
    assert all(card.next_review is not None for card in cards)


def test_adaptive_profiles_filter_sessions_and_apply_domain_retention(client, auth_headers):
    language_path_response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={
            "name": "Anglais professionnel de contrôle",
            "domain": "language",
            "description": "Parcours isolé pour vérifier le filtrage adaptatif.",
            "objective_type": "competency",
            "objective_label": "Réviser une carte de vocabulaire.",
        },
    )
    computing_path_response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={"template_id": "computing-foundations"},
    )
    assert language_path_response.status_code == 201
    assert computing_path_response.status_code == 201
    language_subject_id = language_path_response.get_json()["subject"]["id"]
    computing_subject_id = computing_path_response.get_json()["subject"]["id"]

    profile_response = client.put(
        "/api/spaced-repetition/adaptive-profiles/language",
        headers=auth_headers,
        json={"desired_retention": 0.93},
    )
    assert profile_response.status_code == 200
    assert profile_response.get_json()["profile"]["desired_retention"] == 0.93

    language_card_response = client.post(
        "/api/spaced-repetition/create-card",
        headers=auth_headers,
        json={
            "subject_id": language_subject_id,
            "concept_name": "Board meeting",
            "front_content": "Que signifie board meeting ?",
            "back_content": "Réunion du conseil d’administration.",
        },
    )
    computing_card_response = client.post(
        "/api/spaced-repetition/create-card",
        headers=auth_headers,
        json={
            "subject_id": computing_subject_id,
            "concept_name": "DNS",
            "front_content": "Quel service associe un nom de domaine à une adresse IP ?",
            "back_content": "Le DNS.",
        },
    )
    assert language_card_response.status_code == 200
    assert computing_card_response.status_code == 200
    language_card = language_card_response.get_json()["card"]

    language_due_response = client.get(
        "/api/spaced-repetition/get-due-cards?domain=language",
        headers=auth_headers,
    )
    assert language_due_response.status_code == 200
    language_due = language_due_response.get_json()
    assert language_due["domain"] == "language"
    assert language_due["total_due"] == 1
    assert language_due["due_cards"][0]["learning_domain"] == "language"

    review_response = client.post(
        "/api/spaced-repetition/review-card",
        headers=auth_headers,
        json={"card_id": language_card["id"], "rating": "good", "response_time": 8},
    )
    assert review_response.status_code == 200
    review = review_response.get_json()
    assert review["learning_domain"] == "language"
    assert review["retention_target"] == 0.93
    assert review["retention_source"] == "domain_profile"

    overview_response = client.get(
        "/api/spaced-repetition/adaptive-overview",
        headers=auth_headers,
    )
    assert overview_response.status_code == 200
    language_overview = next(
        item for item in overview_response.get_json()["domains"] if item["domain"] == "language"
    )
    assert language_overview["cards_total"] == 1
    assert language_overview["desired_retention"] == 0.93
    assert language_overview["retention_source"] == "domain_profile"


def test_toeic_reading_diagnostic_records_results_and_creates_remediation(client, auth_headers):
    path_response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={
            "name": "Diagnostic lecture TOEIC",
            "domain": "language",
            "description": "Parcours de contrôle du diagnostic original.",
            "objective_type": "competency",
            "objective_label": "Lire des documents professionnels.",
        },
    )
    assert path_response.status_code == 201
    subject_id = path_response.get_json()["subject"]["id"]

    start_response = client.post(
        "/api/diagnostic/toeic-reading/start",
        headers=auth_headers,
        json={"subject_id": subject_id},
    )
    assert start_response.status_code == 201
    start_payload = start_response.get_json()
    assert start_payload["diagnostic"]["id"] == "toeic-reading-diagnostic-v1"
    assert len(start_payload["items"]) == 19
    assert "correct_index" not in start_payload["items"][0]
    assert "explanation" not in start_payload["items"][0]

    responses = []
    for public_item in start_payload["items"]:
        item = get_diagnostic_item(public_item["id"])
        selected_index = item["correct_index"]
        if item["target"] == "grammar":
            selected_index = (selected_index + 1) % len(item["choices"])
        responses.append({
            "item_id": item["id"],
            "selected_index": selected_index,
            "response_time_seconds": 5,
            "confidence": 2,
        })

    submit_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/submit",
        headers=auth_headers,
        json={"responses": responses, "duration_seconds": 180},
    )
    assert submit_response.status_code == 200
    submitted = submit_response.get_json()
    assert submitted["attempt"]["status"] == "completed"
    assert submitted["attempt"]["total_items"] == 19
    assert submitted["attempt"]["correct_count"] == 14
    grammar_recommendation = next(
        item for item in submitted["analysis"]["recommendations"] if item["target"] == "grammar"
    )
    assert grammar_recommendation["code"] == "create_remediation"
    assert "score TOEIC" in submitted["disclaimer"]

    remediation_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/create-remediation",
        headers=auth_headers,
        json={"targets": ["grammar"]},
    )
    assert remediation_response.status_code == 201
    remediation = remediation_response.get_json()
    assert remediation["created_count"] == 5
    assert {card["learning_domain"] for card in remediation["cards"]} == {"language"}
    assert all("diagnostic" in card["tags"] for card in remediation["cards"])
    assert Card.query.filter_by(subject_id=subject_id).count() == 5

    duplicate_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/create-remediation",
        headers=auth_headers,
        json={"targets": ["grammar"]},
    )
    assert duplicate_response.status_code == 201
    assert duplicate_response.get_json()["created_count"] == 0
    assert duplicate_response.get_json()["skipped_count"] == 5


def test_toeic_listening_question_response_hides_scripts_requires_play_and_creates_remediation(client, auth_headers):
    path_response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={
            "name": "Diagnostic écoute TOEIC",
            "domain": "language",
            "description": "Parcours de contrôle du diagnostic d’écoute original.",
            "objective_type": "competency",
            "objective_label": "Comprendre de courts échanges professionnels.",
        },
    )
    assert path_response.status_code == 201
    subject_id = path_response.get_json()["subject"]["id"]

    public_response = client.get(
        "/api/diagnostic/toeic-listening-question-response",
        headers=auth_headers,
    )
    assert public_response.status_code == 200
    public_items = public_response.get_json()["items"]
    assert len(public_items) == 4
    assert public_items[0]["audio_id"] == "lqr-01"
    assert public_items[0]["audio_status"] == "available"
    for public_item in public_items:
        assert "choices" not in public_item
        assert "transcript" not in public_item
        assert "correct_index" not in public_item
        assert "explanation" not in public_item
        assert "remediation" not in public_item

    start_response = client.post(
        "/api/diagnostic/toeic-listening-question-response/start",
        headers=auth_headers,
        json={"subject_id": subject_id},
    )
    assert start_response.status_code == 201
    start_payload = start_response.get_json()
    assert start_payload["diagnostic"]["id"] == "toeic-listening-question-response-v1"
    assert len(start_payload["items"]) == 4
    assert "transcript" not in start_payload["items"][0]
    assert "choices" not in start_payload["items"][0]

    missing_play_responses = []
    for public_item in start_payload["items"]:
        item = get_toeic_listening_question_response_item(public_item["id"])
        missing_play_responses.append({
            "item_id": item["id"],
            "selected_index": item["correct_index"],
            "response_time_seconds": 4,
        })
    missing_play_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/submit",
        headers=auth_headers,
        json={"responses": missing_play_responses, "duration_seconds": 60},
    )
    assert missing_play_response.status_code == 400
    assert "Listen to each audio item" in missing_play_response.get_json()["message"]

    too_many_play_responses = [
        {**response, "play_count": 2}
        for response in missing_play_responses
    ]
    too_many_play_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/submit",
        headers=auth_headers,
        json={"responses": too_many_play_responses, "duration_seconds": 60},
    )
    assert too_many_play_response.status_code == 400
    assert "play limit" in too_many_play_response.get_json()["message"]

    responses = []
    for public_item in start_payload["items"]:
        item = get_toeic_listening_question_response_item(public_item["id"])
        selected_index = item["correct_index"]
        if item["id"] in {"lqr-01", "lqr-02", "lqr-04"}:
            selected_index = (selected_index + 1) % len(item["choices"])
        responses.append({
            "item_id": item["id"],
            "selected_index": selected_index,
            "response_time_seconds": 4,
            "confidence": 2,
            "play_count": 1,
        })

    submit_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/submit",
        headers=auth_headers,
        json={"responses": responses, "duration_seconds": 90},
    )
    assert submit_response.status_code == 200
    submitted = submit_response.get_json()
    assert submitted["attempt"]["status"] == "completed"
    assert submitted["attempt"]["total_items"] == 4
    assert submitted["attempt"]["correct_count"] == 1
    assert len(submitted["review_items"]) == 4
    assert submitted["review_items"][0]["transcript"]
    assert "correct_index" in submitted["review_items"][0]
    assert set(submitted["analysis"]["available_remediation_targets"]) == {"listening_function", "listening_cause"}
    saved_responses = DiagnosticResponse.query.filter_by(attempt_id=start_payload["attempt"]["id"]).all()
    assert {response.audio_id for response in saved_responses} == {"lqr-01", "lqr-02", "lqr-03", "lqr-04"}
    assert {response.play_count for response in saved_responses} == {1}

    remediation_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/create-remediation",
        headers=auth_headers,
        json={"targets": submitted["analysis"]["available_remediation_targets"]},
    )
    assert remediation_response.status_code == 201
    remediation = remediation_response.get_json()
    assert remediation["created_count"] == 3
    assert {card["learning_domain"] for card in remediation["cards"]} == {"language"}
    assert all("listening" in card["tags"] for card in remediation["cards"])

    duplicate_response = client.post(
        f"/api/diagnostic/attempts/{start_payload['attempt']['id']}/create-remediation",
        headers=auth_headers,
        json={"targets": submitted["analysis"]["available_remediation_targets"]},
    )
    assert duplicate_response.status_code == 201
    assert duplicate_response.get_json()["created_count"] == 0
    assert Card.query.filter_by(subject_id=subject_id).count() == 3


def test_shared_listening_stimuli_require_server_playback_and_delay_review(client, auth_headers):
    path_response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={
            "name": "Listening partagé TOEIC",
            "domain": "language",
            "description": "Parcours de test pour conversations et présentations originales.",
            "objective_type": "competency",
            "objective_label": "Comprendre des échanges professionnels courts.",
        },
    )
    assert path_response.status_code == 201
    subject_id = path_response.get_json()["subject"]["id"]

    catalog_response = client.get(
        "/api/diagnostic/toeic-listening-conversations-talks",
        headers=auth_headers,
    )
    assert catalog_response.status_code == 200
    assert catalog_response.headers["Cache-Control"] == "no-store"
    catalog = catalog_response.get_json()
    assert catalog["diagnostic"]["id"] == "toeic-listening-conversations-talks-v1"
    assert len(catalog["stimuli"]) == 4
    assert len(catalog["items"]) == 8
    for stimulus in catalog["stimuli"]:
        assert stimulus["audio_status"] == "available"
        assert stimulus["audio_duration_seconds"] > 0
        assert "audio_url" not in stimulus
        assert "asset_filename" not in stimulus
        assert "speaker_transcript" not in stimulus
    for item in catalog["items"]:
        assert "choices" not in item
        assert "correct_index" not in item
        assert "explanation" not in item
        assert "remediation" not in item

    start_response = client.post(
        "/api/diagnostic/toeic-listening-conversations-talks/start",
        headers=auth_headers,
        json={"subject_id": subject_id},
    )
    assert start_response.status_code == 201
    assert start_response.headers["Cache-Control"] == "no-store"
    started = start_response.get_json()
    attempt_id = started["attempt"]["id"]
    assert started["attempt"]["content_version"] == "1.0.0"
    assert all("speaker_transcript" not in stimulus for stimulus in started["stimuli"])
    assert all("asset_filename" not in stimulus for stimulus in started["stimuli"])
    assert all(stimulus["audio_url"].startswith(f"/api/diagnostic/attempts/{attempt_id}/stimuli/") for stimulus in started["stimuli"])
    assert all("choices" not in item for item in started["items"])

    blocked_audio = client.get(started["stimuli"][0]["audio_url"], headers=auth_headers)
    assert blocked_audio.status_code == 409

    other_suffix = uuid.uuid4().hex[:8]
    other_payload = {
        "username": f"other_{other_suffix}",
        "email": f"other_{other_suffix}@example.com",
        "password": "password123",
    }
    assert client.post("/api/user/register", json=other_payload).status_code == 201
    other_login = client.post(
        "/api/user/login",
        json={"email": other_payload["email"], "password": other_payload["password"]},
    )
    assert other_login.status_code == 200
    other_headers = {"Authorization": f"Bearer {other_login.get_json()['access_token']}"}
    assert client.post(
        f"/api/diagnostic/attempts/{attempt_id}/stimuli/conversation-01/playback",
        headers=other_headers,
        json={},
    ).status_code == 404
    assert client.get(
        f"/api/diagnostic/attempts/{attempt_id}/listening-review",
        headers=other_headers,
    ).status_code == 404
    assert client.get(started["stimuli"][0]["audio_url"], headers=other_headers).status_code == 404

    premature_review = client.get(
        f"/api/diagnostic/attempts/{attempt_id}/listening-review",
        headers=auth_headers,
    )
    assert premature_review.status_code == 409
    assert "transcript" not in premature_review.get_data(as_text=True).lower()

    responses = []
    for public_item in started["items"]:
        private_item = get_toeic_listening_conversations_talks_item(public_item["id"])
        responses.append({
            "item_id": private_item["id"],
            "selected_index": (private_item["correct_index"] + 1) % len(private_item["choices"]),
            "response_time_seconds": 5,
            "confidence": 2,
        })

    client_managed_playback = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={
            "responses": [{**response, "play_count": 1} for response in responses],
            "duration_seconds": 90,
        },
    )
    assert client_managed_playback.status_code == 400
    assert "server-managed" in client_managed_playback.get_json()["message"]

    missing_playback = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"responses": responses, "duration_seconds": 90},
    )
    assert missing_playback.status_code == 400
    assert "Listen to each audio stimulus" in missing_playback.get_json()["message"]

    for stimulus in started["stimuli"]:
        playback_response = client.post(
            f"/api/diagnostic/attempts/{attempt_id}/stimuli/{stimulus['id']}/playback",
            headers=auth_headers,
            json={},
        )
        assert playback_response.status_code == 201
        assert playback_response.headers["Cache-Control"] == "no-store"
        playback_payload = playback_response.get_json()["playback"]
        assert playback_payload["play_count"] == 1
        audio_response = client.get(playback_payload["audio_url"], headers=auth_headers)
        assert audio_response.status_code == 200
        assert audio_response.headers["Cache-Control"] == "no-store"
        assert audio_response.mimetype == "audio/wav"
        assert audio_response.data.startswith(b"RIFF")

    duplicate_playback = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/stimuli/conversation-01/playback",
        headers=auth_headers,
        json={},
    )
    assert duplicate_playback.status_code == 409

    submit_response = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"responses": responses, "duration_seconds": 90},
    )
    assert submit_response.status_code == 200
    assert submit_response.headers["Cache-Control"] == "no-store"
    submitted = submit_response.get_json()
    assert submitted["attempt"]["status"] == "completed"
    assert submitted["attempt"]["correct_count"] == 0
    assert "review_stimuli" not in submitted
    assert "speaker_transcript" not in submit_response.get_data(as_text=True)

    playbacks = DiagnosticStimulusPlayback.query.filter_by(attempt_id=attempt_id).all()
    assert len(playbacks) == 4
    assert {playback.play_count for playback in playbacks} == {1}
    saved_responses = DiagnosticResponse.query.filter_by(attempt_id=attempt_id).all()
    assert len(saved_responses) == 8
    assert {response.stimulus_id for response in saved_responses} == {
        "conversation-01", "conversation-02", "talk-01", "talk-02"
    }
    assert {response.play_count for response in saved_responses} == {1}
    assert all(response.script_version == "1.0.0" for response in saved_responses)
    assert all(response.audio_duration_seconds > 0 for response in saved_responses)

    review_response = client.get(
        f"/api/diagnostic/attempts/{attempt_id}/listening-review",
        headers=auth_headers,
    )
    assert review_response.status_code == 200
    assert review_response.headers["Cache-Control"] == "no-store"
    review = review_response.get_json()
    assert len(review["review_stimuli"]) == 4
    assert all(len(stimulus["items"]) == 2 for stimulus in review["review_stimuli"])
    assert all(stimulus["speaker_transcript"] for stimulus in review["review_stimuli"])
    assert all(stimulus["audio_url"].startswith(f"/api/diagnostic/attempts/{attempt_id}/stimuli/") for stimulus in review["review_stimuli"])
    assert client.get(review["review_stimuli"][0]["audio_url"], headers=other_headers).status_code == 404

    remediation_response = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/create-remediation",
        headers=auth_headers,
        json={"targets": ["listening_detail"]},
    )
    assert remediation_response.status_code == 201
    assert remediation_response.get_json()["created_count"] == 2
    assert Card.query.filter_by(subject_id=subject_id).count() == 2


def test_multi_speaker_listening_uses_three_questions_per_private_stimulus(client, auth_headers):
    path_response = client.post(
        "/api/mastery/create-path",
        headers=auth_headers,
        json={
            "name": "Listening approfondi TOEIC",
            "domain": "language",
            "description": "Parcours de test pour stimuli professionnels originaux à trois questions.",
            "objective_type": "competency",
            "objective_label": "Comprendre des échanges professionnels continus.",
        },
    )
    assert path_response.status_code == 201
    subject_id = path_response.get_json()["subject"]["id"]

    catalog_response = client.get(
        "/api/diagnostic/toeic-listening-multi-speaker",
        headers=auth_headers,
    )
    assert catalog_response.status_code == 200
    assert catalog_response.headers["Cache-Control"] == "no-store"
    catalog = catalog_response.get_json()
    assert catalog["diagnostic"]["id"] == "toeic-listening-multi-speaker-v1"
    assert len(catalog["stimuli"]) == 4
    assert len(catalog["items"]) == 12
    assert {item["target"] for item in catalog["items"]} == {
        "listening_detail", "listening_main_idea", "listening_inference"
    }
    assert all("audio_url" not in stimulus for stimulus in catalog["stimuli"])
    assert all("speaker_transcript" not in stimulus for stimulus in catalog["stimuli"])
    assert all("choices" not in item and "correct_index" not in item for item in catalog["items"])

    start_response = client.post(
        "/api/diagnostic/toeic-listening-multi-speaker/start",
        headers=auth_headers,
        json={"subject_id": subject_id},
    )
    assert start_response.status_code == 201
    started = start_response.get_json()
    attempt_id = started["attempt"]["id"]
    assert started["attempt"]["content_version"] == "1.0.0"
    assert {stimulus["id"] for stimulus in started["stimuli"]} == {
        "conversation-01", "conversation-02", "talk-01", "talk-02"
    }
    assert all(stimulus["audio_url"].startswith(f"/api/diagnostic/attempts/{attempt_id}/stimuli/") for stimulus in started["stimuli"])
    assert all(sum(item["stimulus_id"] == stimulus["id"] for item in started["items"]) == 3 for stimulus in started["stimuli"])

    assert client.get(started["stimuli"][0]["audio_url"], headers=auth_headers).status_code == 409
    premature_review = client.get(
        f"/api/diagnostic/attempts/{attempt_id}/listening-review",
        headers=auth_headers,
    )
    assert premature_review.status_code == 409

    responses = []
    for public_item in started["items"]:
        private_item = get_toeic_listening_multi_speaker_item(public_item["id"])
        responses.append({
            "item_id": private_item["id"],
            "selected_index": (private_item["correct_index"] + 1) % len(private_item["choices"]),
            "response_time_seconds": 8,
            "confidence": 2,
        })

    missing_playback = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"responses": responses, "duration_seconds": 180},
    )
    assert missing_playback.status_code == 400
    assert "Listen to each audio stimulus" in missing_playback.get_json()["message"]

    for stimulus in started["stimuli"]:
        playback_response = client.post(
            f"/api/diagnostic/attempts/{attempt_id}/stimuli/{stimulus['id']}/playback",
            headers=auth_headers,
            json={},
        )
        assert playback_response.status_code == 201
        playback = playback_response.get_json()["playback"]
        assert playback["play_count"] == 1
        audio_response = client.get(playback["audio_url"], headers=auth_headers)
        assert audio_response.status_code == 200
        assert audio_response.headers["Cache-Control"] == "no-store"
        assert audio_response.mimetype == "audio/wav"
        assert audio_response.data.startswith(b"RIFF")

    submitted = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"responses": responses, "duration_seconds": 180},
    )
    assert submitted.status_code == 200
    assert submitted.headers["Cache-Control"] == "no-store"
    assert submitted.get_json()["attempt"]["total_items"] == 12
    assert submitted.get_json()["attempt"]["correct_count"] == 0
    assert "speaker_transcript" not in submitted.get_data(as_text=True)

    review_response = client.get(
        f"/api/diagnostic/attempts/{attempt_id}/listening-review",
        headers=auth_headers,
    )
    assert review_response.status_code == 200
    review = review_response.get_json()
    assert len(review["review_stimuli"]) == 4
    assert all(len(stimulus["items"]) == 3 for stimulus in review["review_stimuli"])
    assert all(stimulus["speaker_transcript"] for stimulus in review["review_stimuli"])

    remediation_response = client.post(
        f"/api/diagnostic/attempts/{attempt_id}/create-remediation",
        headers=auth_headers,
        json={"targets": ["listening_inference"]},
    )
    assert remediation_response.status_code == 201
    assert remediation_response.get_json()["created_count"] == 2
    assert Card.query.filter_by(subject_id=subject_id).count() == 2
