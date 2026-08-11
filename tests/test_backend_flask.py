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
from src.models.user import Card, Concept, StudySession, Subject, db  # noqa: E402
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
