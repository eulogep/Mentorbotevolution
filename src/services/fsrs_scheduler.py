"""Adaptateur explicite autour de Py-FSRS pour Mentor Evolution.

Le service isole la dépendance externe, conserve un état JSON par carte et rend
les décisions de planification auditables. Il n'effectue aucune optimisation
personnalisée des poids sans historique suffisant et consentement explicite.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from fsrs import Card as FsrsCard
from fsrs import Rating, Scheduler


FSRS_VERSION = "fsrs-6.3.2"
DEFAULT_RETENTION = 0.90
MIN_RETENTION = 0.80
MAX_RETENTION = 0.97

RATING_BY_NAME = {
    "again": Rating.Again,
    "hard": Rating.Hard,
    "good": Rating.Good,
    "easy": Rating.Easy,
}


def normalize_desired_retention(value: Any) -> float:
    """Validate the explicit retention target chosen by the learner."""
    try:
        retention = float(value)
    except (TypeError, ValueError):
        return DEFAULT_RETENTION
    return min(MAX_RETENTION, max(MIN_RETENTION, retention))


def normalize_rating(data: dict[str, Any]) -> tuple[str, Rating]:
    """Normalize the modern rating or the legacy quality_response (0-5)."""
    raw_rating = data.get("rating")
    if isinstance(raw_rating, str):
        rating_name = raw_rating.strip().lower()
        if rating_name in RATING_BY_NAME:
            return rating_name, RATING_BY_NAME[rating_name]

    quality = data.get("quality_response")
    if quality is None:
        raise ValueError("rating or quality_response is required")
    try:
        quality = int(quality)
    except (TypeError, ValueError) as exc:
        raise ValueError("quality_response must be an integer between 0 and 5") from exc
    if not 0 <= quality <= 5:
        raise ValueError("quality_response must be between 0 and 5")

    if quality <= 1:
        return "again", Rating.Again
    if quality == 2:
        return "hard", Rating.Hard
    if quality <= 4:
        return "good", Rating.Good
    return "easy", Rating.Easy


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _to_naive_utc(value: datetime) -> datetime:
    return _to_utc(value).replace(tzinfo=None)


def _load_fsrs_card(scheduler_state: str | None) -> FsrsCard:
    if scheduler_state:
        try:
            return FsrsCard.from_json(scheduler_state)
        except (TypeError, ValueError, KeyError):
            # A malformed legacy state must not block learning. The next review
            # restarts safely in FSRS and the stored state is replaced.
            pass
    return FsrsCard()


def review_with_fsrs(
    scheduler_state: str | None,
    rating: Rating,
    desired_retention: Any,
) -> dict[str, Any]:
    """Schedule a review and expose auditable values for persistence/UI."""
    retention = normalize_desired_retention(desired_retention)
    # Fuzzing is disabled so that feedback, tests and audit trails remain
    # deterministic. It may be introduced later as an explicit product choice.
    scheduler = Scheduler(desired_retention=retention, enable_fuzzing=False)
    current_card = _load_fsrs_card(scheduler_state)
    previous_state = current_card.to_json()

    try:
        retrievability_before = round(scheduler.get_card_retrievability(current_card), 4)
    except (ValueError, ZeroDivisionError):
        retrievability_before = None

    updated_card, review_log = scheduler.review_card(current_card, rating)
    retrievability_after = round(scheduler.get_card_retrievability(updated_card), 4)
    due_at = _to_utc(updated_card.due)
    reviewed_at = _to_utc(review_log.review_datetime)
    delta_seconds = max(0.0, (due_at - reviewed_at).total_seconds())
    # FSRS peut planifier des pas d’apprentissage de quelques minutes. La durée
    # en minutes est donc la source de vérité ; le nombre de jours complets est
    # uniquement conservé pour les anciens consommateurs du champ `interval`.
    scheduled_minutes = math.ceil(delta_seconds / 60)
    scheduled_days = math.floor(scheduled_minutes / 1440)

    return {
        "card_state": updated_card.to_json(),
        "review_log": review_log.to_json(),
        "previous_state": previous_state,
        "retrievability_before": retrievability_before,
        "retrievability_after": retrievability_after,
        "due_at": _to_naive_utc(due_at),
        "reviewed_at": _to_naive_utc(reviewed_at),
        "scheduled_days": scheduled_days,
        "scheduled_minutes": scheduled_minutes,
        "scheduled_days_exact": round(delta_seconds / 86400, 4),
        "retention_target": retention,
        "memory_state": {
            "state": updated_card.state.name.lower(),
            "stability_days": round(updated_card.stability, 2),
            "difficulty": round(updated_card.difficulty, 2),
        },
    }


def describe_rating(rating_name: str, scheduled_minutes: int) -> dict[str, Any]:
    """Return concise, non-deceptive pedagogical feedback for one review."""
    descriptions = {
        "again": {
            "message": "Réponse oubliée : la carte revient rapidement pour consolider le rappel.",
            "tip": "Relisez la correction, puis reformulez-la avant de réessayer.",
        },
        "hard": {
            "message": "Réponse retrouvée avec difficulté : l’intervalle reste prudent.",
            "tip": "Cherchez un indice ou un exemple qui relie cette notion à un contexte TOEIC.",
        },
        "good": {
            "message": "Rappel réussi : la prochaine récupération est espacée.",
            "tip": "Variez le contexte de pratique pour favoriser le transfert.",
        },
        "easy": {
            "message": "Rappel fluide : la carte peut être revue plus loin dans le temps.",
            "tip": "Conservez une formulation précise : une carte simple reste plus facile à récupérer.",
        },
    }
    feedback = descriptions[rating_name].copy()
    if scheduled_minutes < 1:
        delay_label = "moins d’une minute"
    elif scheduled_minutes < 1440:
        delay_label = f"environ {scheduled_minutes} minute(s)"
    else:
        delay_label = f"environ {round(scheduled_minutes / 1440, 1)} jour(s)"
    feedback["next_action"] = f"Prochaine récupération prévue dans {delay_label}."
    return feedback
