import io
import os
import sys
import uuid

import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-with-enough-length-for-hs256"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-with-enough-length-for-hs256"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app, get_database_uri  # noqa: E402
from src.models.user import Concept, StudySession, Subject, db  # noqa: E402
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
    assert body["next_review_in_days"] >= 1
    assert body["updated_card"]["review_count"] == 1
    assert body["updated_card"]["interval"] == body["next_review_in_days"]


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
