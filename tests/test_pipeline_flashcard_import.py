import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from src.models.user import db, Card, Subject, Concept
from src.services.pipeline_flashcard_import import import_pipeline_flashcards
from tests.test_backend_flask import client, auth_headers


def test_import_pipeline_flashcards_valid(client):
    """Vérifie l'importation de flashcards valides avec création de Subject et Concept."""
    with app.app_context():
        # Nettoyage
        Card.query.filter_by(user_id=1).delete()
        subjects = Subject.query.filter_by(user_id=1).all()
        subject_ids = [s.id for s in subjects]
        if subject_ids:
            Concept.query.filter(Concept.subject_id.in_(subject_ids)).delete(synchronize_session=False)
        Subject.query.filter_by(user_id=1).delete()
        db.session.commit()

        payload = {
            "source_document": "test_doc.txt",
            "subject_name": "TOEIC Grammaire",
            "flashcards": [
                {
                    "concept_name": "Conditionals",
                    "question": "What is type 1 conditional?",
                    "answer": "If + present simple, will + infinitive",
                    "difficulty": "medium"
                },
                {
                    "concept_name": "Vocabulary",
                    "question": "What does stakeholder mean?",
                    "answer": "A person with an interest or concern in something",
                    "difficulty": "easy"
                }
            ]
        }

        result = import_pipeline_flashcards(user_id=1, payload=payload)
        
        assert result["status"] == "success"
        assert result["saved_count"] == 2
        assert result["skipped_count"] == 0
        assert len(result["created_card_ids"]) == 2

        # Vérification en base
        subject = Subject.query.filter_by(user_id=1, name="TOEIC Grammaire").first()
        assert subject is not None
        
        cards = Card.query.filter_by(user_id=1, subject_id=subject.id).all()
        assert len(cards) == 2
        assert cards[0].concept_name == "Conditionals"
        assert cards[1].concept_name == "Vocabulary"


def test_import_pipeline_flashcards_empty_or_invalid(client):
    """Vérifie la robustesse avec des données vides ou invalides."""
    with app.app_context():
        # 1. Payload vide
        result = import_pipeline_flashcards(user_id=1, payload={})
        assert result["status"] == "error"

        # 2. Flashcards vides
        payload = {
            "source_document": "test_doc.txt",
            "flashcards": []
        }
        result = import_pipeline_flashcards(user_id=1, payload=payload)
        assert result["status"] == "success"
        assert result["saved_count"] == 0
        assert result["skipped_count"] == 0

        # 3. Flashcards avec des éléments invalides (manque question ou réponse ou concept_name)
        payload = {
            "source_document": "test_doc.txt",
            "flashcards": [
                {
                    "concept_name": "Grammar",
                    "question": "Only question"
                },
                {
                    "concept_name": "Vocabulary",
                    "answer": "Only answer"
                },
                {
                    "question": "No concept",
                    "answer": "No concept answer"
                },
                {
                    "concept_name": "Grammar",
                    "question": "Valid?",
                    "answer": "Valid!"
                }
            ]
        }
        result = import_pipeline_flashcards(user_id=1, payload=payload)
        assert result["status"] == "success"
        assert result["saved_count"] == 1
        assert result["skipped_count"] == 3


def test_import_route_jwt_protected(client):
    """Vérifie que la route d'import exige le token JWT."""
    response = client.post(
        "/api/spaced-repetition/import-pipeline-flashcards",
        json={"flashcards": []}
    )
    assert response.status_code == 401


def test_import_route_success(client, auth_headers):
    """Vérifie l'intégration de la route avec token JWT valide."""
    payload = {
        "source_document": "route_test.txt",
        "subject_name": "Route Subject",
        "flashcards": [
            {
                "concept_name": "Route Concept",
                "question": "Q1",
                "answer": "A1"
            }
        ]
    }
    response = client.post(
        "/api/spaced-repetition/import-pipeline-flashcards",
        headers=auth_headers,
        json=payload
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["saved_count"] == 1
