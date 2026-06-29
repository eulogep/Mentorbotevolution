"""
Service central du pipeline d'apprentissage
===========================================
"""

from datetime import datetime, timedelta
from src.services.concept_extraction import extract_concepts_from_text
from src.services.flashcard_generation import generate_flashcards_from_concepts


def build_learning_pipeline(user_id: int, subject_id: int, document_text: str) -> dict:
    """
    Construit le pipeline d'apprentissage complet à partir d'un texte de document.
    
    Args:
        user_id (int): ID de l'utilisateur
        subject_id (int): ID de la matière / sujet
        document_text (str): Texte extrait du document
        
    Returns:
        dict: Bloc de données du pipeline d'apprentissage
    """
    if not document_text:
        return {
            "document_summary": "Aucun contenu à résumer.",
            "concepts": [],
            "flashcards": [],
            "revision_plan": [],
            "is_simulated": True,
            "pipeline_version": "0.1"
        }

    # 1. Extraction de concepts (Heuristique)
    concepts = extract_concepts_from_text(document_text)

    # 2. Génération de flashcards (Heuristique)
    flashcards = generate_flashcards_from_concepts(concepts)

    # 3. Planning de révision (Courbe d'oubli espacée)
    revision_plan = []
    now = datetime.utcnow()
    intervals = [1, 3, 7, 14, 30]  # Jours d'intervalle typiques

    for c in concepts:
        concept_schedule = []
        for i, interval in enumerate(intervals):
            scheduled_date = now + timedelta(days=interval)
            concept_schedule.append({
                "review_step": i + 1,
                "interval_days": interval,
                "scheduled_date": scheduled_date.isoformat() + "Z",
                "target_confidence": round(0.7 + (i * 0.05), 2)
            })
        
        revision_plan.append({
            "concept_name": c["title"],
            "schedule": concept_schedule
        })

    # 4. Résumé simplifié du document (Heuristique)
    word_count = len(document_text.split())
    summary = (
        f"Document contenant {word_count} mots. "
        f"L'analyse a identifié {len(concepts)} concepts clés à étudier en priorité."
    )

    return {
        "document_summary": summary,
        "concepts": concepts,
        "flashcards": flashcards,
        "revision_plan": revision_plan,
        "is_simulated": True,  # Clé obligatoire pour signifier le mode local/heuristique sans IA externe
        "pipeline_version": "0.1"
    }
