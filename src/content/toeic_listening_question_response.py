"""Premier incrément Listening : quatre exercices Question–réponse éditoriaux.

Les scripts, réponses, corrections et remédiations sont originaux. Ils ne
reproduisent aucun item, enregistrement, script ni corrigé ETS. Les transcriptions
et indices de correction ne doivent jamais être exposés avant la soumission.
"""

from copy import deepcopy


TOEIC_LISTENING_QUESTION_RESPONSE_ID = "toeic-listening-question-response-v1"

TOEIC_LISTENING_QUESTION_RESPONSE = {
    "id": TOEIC_LISTENING_QUESTION_RESPONSE_ID,
    "title": "Diagnostic écoute — questions et réponses",
    "description": (
        "Quatre exercices audio originaux d’anglais professionnel. Écoutez une fois, "
        "puis choisissez la réponse la plus adaptée."
    ),
    "learning_domain": "language",
    "source": "editorial_original",
    "disclaimer": (
        "Cette activité formative originale ne constitue pas un test TOEIC officiel "
        "et ne fournit aucune estimation de score."
    ),
    "max_plays_per_item": 1,
    "items": [
        {
            "id": "lqr-01",
            "task_type": "listening_question_response",
            "target": "listening_function",
            "scenario": "budget-meeting",
            "audio_id": "lqr-01",
            "audio_url": "/listening/lqr-01.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "max_plays": 1,
            "choices": [
                "Thursday afternoon works for me.",
                "The budget was approved last quarter.",
                "It is on the third floor.",
            ],
            "choice_labels": ["A", "B", "C"],
            "transcript": (
                "Can we move the budget meeting to Thursday afternoon? "
                "A. Thursday afternoon works for me. "
                "B. The budget was approved last quarter. "
                "C. It is on the third floor."
            ),
            "correct_index": 0,
            "explanation": "La réponse A accepte directement le changement d’horaire proposé.",
            "remediation": {
                "front": "Comment accepter simplement un changement d’horaire en anglais professionnel ?",
                "back": "Thursday afternoon works for me. — Cette formule accepte le créneau proposé.",
                "concept_name": "Accepter un changement d’horaire",
                "tags": ["toeic", "diagnostic", "listening", "communication", "meeting"],
            },
        },
        {
            "id": "lqr-02",
            "task_type": "listening_question_response",
            "target": "listening_function",
            "scenario": "delivery-follow-up",
            "audio_id": "lqr-02",
            "audio_url": "/listening/lqr-02.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "max_plays": 1,
            "choices": [
                "The warehouse closes at six.",
                "Yes, I will send it this afternoon.",
                "The order has three items.",
            ],
            "choice_labels": ["A", "B", "C"],
            "transcript": (
                "Could you email the delivery reference for my order? "
                "A. The warehouse closes at six. "
                "B. Yes, I will send it this afternoon. "
                "C. The order has three items."
            ),
            "correct_index": 1,
            "explanation": "La réponse B répond à la demande d’envoi de la référence par courriel.",
            "remediation": {
                "front": "Quelle formule annonce l’envoi d’une information par courriel ?",
                "back": "Yes, I will send it this afternoon. — La formule confirme un envoi ultérieur dans la journée.",
                "concept_name": "Confirmer un envoi par courriel",
                "tags": ["toeic", "diagnostic", "listening", "communication", "customer-service"],
            },
        },
        {
            "id": "lqr-03",
            "task_type": "listening_question_response",
            "target": "listening_detail",
            "scenario": "safety-briefing",
            "audio_id": "lqr-03",
            "audio_url": "/listening/lqr-03.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "max_plays": 1,
            "choices": [
                "It begins at ten o’clock.",
                "In the training room upstairs.",
                "Ms. Patel from operations will.",
            ],
            "choice_labels": ["A", "B", "C"],
            "transcript": (
                "Who will lead the safety briefing this morning? "
                "A. It begins at ten o’clock. "
                "B. In the training room upstairs. "
                "C. Ms. Patel from operations will."
            ),
            "correct_index": 2,
            "explanation": "La réponse C identifie la personne responsable du briefing.",
            "remediation": None,
        },
        {
            "id": "lqr-04",
            "task_type": "listening_question_response",
            "target": "listening_cause",
            "scenario": "it-support",
            "audio_id": "lqr-04",
            "audio_url": "/listening/lqr-04.wav",
            "audio_status": "available",
            "script_version": "1.0.0",
            "max_plays": 1,
            "choices": [
                "It is being updated by the IT team.",
                "The printer is beside the reception desk.",
                "We ordered more paper yesterday.",
            ],
            "choice_labels": ["A", "B", "C"],
            "transcript": (
                "Why is the printer offline at the moment? "
                "A. It is being updated by the IT team. "
                "B. The printer is beside the reception desk. "
                "C. We ordered more paper yesterday."
            ),
            "correct_index": 0,
            "explanation": "La réponse A donne la cause demandée : une mise à jour est en cours.",
            "remediation": {
                "front": "Comment expliquer qu’un équipement est temporairement indisponible ?",
                "back": "It is being updated by the IT team. — La formulation indique une mise à jour en cours.",
                "concept_name": "Expliquer une indisponibilité technique",
                "tags": ["toeic", "diagnostic", "listening", "it-support", "passive-voice"],
            },
        },
    ],
}


def get_toeic_listening_question_response_diagnostic() -> dict:
    """Return a defensive copy of the original Listening package."""
    return deepcopy(TOEIC_LISTENING_QUESTION_RESPONSE)


def get_toeic_listening_question_response_item(item_id: str) -> dict | None:
    """Return one Listening item without sharing mutable content."""
    for item in TOEIC_LISTENING_QUESTION_RESPONSE["items"]:
        if item["id"] == item_id:
            return deepcopy(item)
    return None
