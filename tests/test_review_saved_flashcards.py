import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from src.models.user import db, Card, Subject
from tests.test_backend_flask import client, auth_headers


def test_get_review_cards_unauthorized(client):
    """Vérifie que la récupération sans JWT renvoie 401."""
    response = client.get("/api/spaced-repetition/review-cards")
    assert response.status_code == 401


def test_get_review_cards_authorized(client, auth_headers):
    """Vérifie la récupération de cartes pour l'utilisateur connecté avec fallback démo."""
    ctx = app.app_context()
    ctx.push()
    try:
        # Nettoyage et création d'une carte
        Card.query.filter_by(user_id=1).delete()
        card = Card(
            user_id=1,
            concept_name="Grammaire",
            front_content="Question de test",
            back_content="Réponse de test",
            next_review=datetime.utcnow() + timedelta(days=1)
        )
        db.session.add(card)
        db.session.commit()
    finally:
        ctx.pop()

    response = client.get("/api/spaced-repetition/review-cards", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["cards"]) > 0
    assert data["cards"][0]["front_content"] == "Question de test"


def test_post_card_answer_unauthorized(client):
    """Vérifie que la réponse à une carte sans JWT renvoie 401."""
    response = client.post("/api/spaced-repetition/review-cards/1/answer", json={"quality": 4})
    assert response.status_code == 401


def test_post_card_answer_invalid_quality(client, auth_headers):
    """Vérifie qu'une note invalide renvoie 400."""
    response = client.post(
        "/api/spaced-repetition/review-cards/1/answer",
        headers=auth_headers,
        json={"quality": 6}  # Invalide (>5)
    )
    assert response.status_code == 400


def test_post_card_answer_not_found(client, auth_headers):
    """Vérifie qu'une carte inexistante renvoie 404."""
    response = client.post(
        "/api/spaced-repetition/review-cards/9999/answer",
        headers=auth_headers,
        json={"quality": 3}
    )
    assert response.status_code == 404


def test_post_card_answer_success(client, auth_headers):
    """Vérifie la mise à jour correcte de next_review après soumission d'une réponse valide."""
    ctx = app.app_context()
    ctx.push()
    try:
        # Création d'une carte spécifique
        Card.query.filter_by(user_id=1).delete()
        card = Card(
            user_id=1,
            concept_name="Vocabulary",
            front_content="What is CEO?",
            back_content="Chief Executive Officer",
            interval=1,
            easiness_factor=2.5,
            next_review=datetime.utcnow()
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id
    finally:
        ctx.pop()

    # Rendre une réponse
    response = client.post(
        f"/api/spaced-repetition/review-cards/{card_id}/answer",
        headers=auth_headers,
        json={"quality": 4}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["card_id"] == card_id

    # Vérification en base
    ctx = app.app_context()
    ctx.push()
    try:
        updated_card = Card.query.get(card_id)
        assert updated_card.review_count == 1
        assert updated_card.success_count == 1
        assert updated_card.interval == 6  # SM-2 logic (first interval is 6 days for quality >= 3)
        assert updated_card.next_review > datetime.utcnow() + timedelta(days=5)
    finally:
        ctx.pop()
