"""
Service d'importation des flashcards depuis le pipeline d'apprentissage
========================================================================
"""

from datetime import datetime
from src.models.user import db, Subject, Concept, Card


def import_pipeline_flashcards(user_id: int, payload: dict) -> dict:
    """
    Importe les flashcards du pipeline en base de données.
    
    Args:
        user_id (int): ID de l'utilisateur connecté
        payload (dict): Données d'import contenant les flashcards et métadonnées
        
    Returns:
        dict: Rapport d'importation
    """
    if not payload or not isinstance(payload.get("flashcards"), list):
        return {
            "status": "error",
            "message": "Le format du payload est invalide. 'flashcards' doit être une liste."
        }

    flashcards_list = payload["flashcards"]
    source_doc = payload.get("source_document", "Inconnu")
    subject_id = payload.get("subject_id")

    # 1. Récupération ou création du Subject
    if not subject_id:
        subject_name = payload.get("subject_name", "Pipeline imports")
        subject = Subject.query.filter_by(user_id=user_id, name=subject_name).first()
        if not subject:
            subject = Subject(
                user_id=user_id,
                name=subject_name,
                description=f"Matière créée automatiquement pour stocker les imports du document '{source_doc}'.",
                status="in_progress"
            )
            db.session.add(subject)
            db.session.flush()  # Pour obtenir subject.id
        subject_id = subject.id
    else:
        subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()
        if not subject:
            return {
                "status": "error",
                "message": f"Matière avec l'ID {subject_id} introuvable."
            }

    saved_count = 0
    skipped_count = 0
    created_card_ids = []

    # 2. Traitement de chaque flashcard
    for card_data in flashcards_list:
        concept_name = card_data.get("concept_name")
        question = card_data.get("question")
        answer = card_data.get("answer")
        difficulty = card_data.get("difficulty", "medium")

        # Ignorer si question ou réponse vide
        if not question or not answer or not concept_name:
            skipped_count += 1
            continue

        concept_name = concept_name.strip()
        question = question.strip()
        answer = answer.strip()

        # Éviter les doublons simples (même question, même réponse pour ce user)
        existing_card = Card.query.filter_by(
            user_id=user_id,
            subject_id=subject_id,
            front_content=question,
            back_content=answer
        ).first()

        if existing_card:
            skipped_count += 1
            continue

        # Récupération ou création du Concept associé
        concept = Concept.query.filter_by(subject_id=subject_id, name=concept_name).first()
        if not concept:
            concept = Concept(
                subject_id=subject_id,
                name=concept_name,
                status="not-started",
                mastery=0
            )
            db.session.add(concept)
            db.session.flush()

        # Création de la carte
        card = Card(
            user_id=user_id,
            subject_id=subject_id,
            concept_name=concept_name,
            front_content=question,
            back_content=answer,
            difficulty=difficulty,
            priority="normal",
            next_review=datetime.utcnow()
        )
        db.session.add(card)
        db.session.flush()
        created_card_ids.append(card.id)
        saved_count += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Erreur lors de la sauvegarde en base : {str(e)}"
        }

    return {
        "status": "success",
        "saved_count": saved_count,
        "skipped_count": skipped_count,
        "subject_id": subject_id,
        "created_card_ids": created_card_ids,
        "source": "pipeline_import"
    }
