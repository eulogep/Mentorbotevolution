import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from src.services.learning_pipeline import build_learning_pipeline
from src.services.concept_extraction import extract_concepts_from_text
from src.services.flashcard_generation import generate_flashcards_from_concepts
from tests.test_backend_flask import client, auth_headers


def test_concept_extraction_service():
    """Vérifie que le service d'extraction extrait des concepts d'un texte simple."""
    text = "The TOEIC exam evaluates listening and reading skills. Grammar is important."
    concepts = extract_concepts_from_text(text, max_concepts=3)
    
    assert isinstance(concepts, list)
    assert len(concepts) > 0
    for concept in concepts:
        assert "title" in concept
        assert "description" in concept
        assert "confidence" in concept
        assert concept["source"] == "heuristic"


def test_flashcard_generation_service():
    """Vérifie que les flashcards sont bien générées à partir des concepts."""
    concepts = [
        {"title": "Listening Skills", "description": "Practice listening", "confidence": 0.8, "source": "heuristic"},
        {"title": "Reading Comprehension", "description": "Practice reading", "confidence": 0.95, "source": "heuristic"}
    ]
    flashcards = generate_flashcards_from_concepts(concepts)
    
    assert isinstance(flashcards, list)
    assert len(flashcards) == 2
    for card in flashcards:
        assert "concept_name" in card
        assert "question" in card
        assert "answer" in card
        assert card["difficulty"] == "medium"
        assert card["source"] == "heuristic"


def test_learning_pipeline_service():
    """Vérifie que le pipeline d'apprentissage produit le dictionnaire complet attendu."""
    text = "This is a simple document about TOEIC and spaced repetition techniques."
    pipeline = build_learning_pipeline(user_id=1, subject_id=1, document_text=text)
    
    assert isinstance(pipeline, dict)
    assert "document_summary" in pipeline
    assert "concepts" in pipeline
    assert "flashcards" in pipeline
    assert "revision_plan" in pipeline
    assert pipeline["is_simulated"] is True
    assert pipeline["pipeline_version"] == "0.1"
    
    # Vérifie que la planification de révision est générée
    assert len(pipeline["revision_plan"]) > 0
    for plan in pipeline["revision_plan"]:
        assert "concept_name" in plan
        assert "schedule" in plan
        assert len(plan["schedule"]) == 5  # 5 étapes de révision par défaut


def test_analyze_document_route_returns_pipeline(client, auth_headers):
    """Vérifie que la route /api/analysis/analyze-document intègre bien le bloc pipeline dans sa réponse."""
    import io
    data = {
        "file": (
            io.BytesIO(
                b"Grammar rules and business communication vocabulary are critical for TOEIC preparation."
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
    res_data = response.get_json()
    
    # Compatibilité ancienne route préservée
    assert "status" in res_data
    assert "analysis" in res_data
    assert "generated_content" in res_data
    
    # Nouveau bloc pipeline présent
    assert "pipeline" in res_data
    pipeline = res_data["pipeline"]
    assert "document_summary" in pipeline
    assert "concepts" in pipeline
    assert "flashcards" in pipeline
    assert "revision_plan" in pipeline
    assert pipeline["is_simulated"] is True
