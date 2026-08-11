"""Transparent per-domain helpers for the shared FSRS learning module."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from src.models.user import AdaptiveLearningProfile, Card, ReviewLog
from src.services.domain_catalog import DOMAIN_OPTIONS
from src.services.fsrs_scheduler import DEFAULT_RETENTION, normalize_desired_retention


ADAPTIVE_DOMAINS = tuple(DOMAIN_OPTIONS.keys())


def resolve_card_domain(card: Card) -> str:
    """Return the persisted card domain, then its subject domain, then general."""
    if card.learning_domain in ADAPTIVE_DOMAINS:
        return card.learning_domain
    if card.subject and card.subject.domain in ADAPTIVE_DOMAINS:
        return card.subject.domain
    return "general"


def get_effective_retention(user, domain: str) -> tuple[float, str]:
    """Return the explicit domain preference or the learner's global fallback."""
    profile = AdaptiveLearningProfile.query.filter_by(user_id=user.id, domain=domain).first()
    if profile:
        return normalize_desired_retention(profile.desired_retention), "domain_profile"
    return normalize_desired_retention(user.desired_retention or DEFAULT_RETENTION), "global_profile"


def recommendation_for_domain(cards_total: int, cards_due: int, review_count: int, recall_rate: float | None) -> dict:
    """Offer only data-based next actions; never predict achievement or ability."""
    if cards_total == 0:
        return {
            "code": "add_cards",
            "message": "Ajoutez des cartes si vous souhaitez pratiquer ce domaine par rappel espacé.",
        }
    if cards_due:
        return {
            "code": "review_due",
            "message": "Des cartes sont dues : une courte session de rappel est prioritaire.",
        }
    if review_count >= 5 and recall_rate is not None and recall_rate < 0.70:
        return {
            "code": "reinforce",
            "message": "Les rappels récents sont fragiles : réduisez l’ajout de nouvelles cartes et reformulez les notions difficiles.",
        }
    return {
        "code": "continue",
        "message": "Aucune carte n’est due actuellement ; poursuivez les exercices pratiques et revenez à l’échéance calculée.",
    }


def build_adaptive_overview(user, now: datetime) -> list[dict]:
    """Build descriptive domain metrics from persisted cards and review logs."""
    cards = Card.query.filter_by(user_id=user.id).all()
    cards_by_domain: dict[str, list[Card]] = defaultdict(list)
    card_domains: dict[int, str] = {}
    for card in cards:
        domain = resolve_card_domain(card)
        cards_by_domain[domain].append(card)
        card_domains[card.id] = domain

    recent_logs = ReviewLog.query.filter(
        ReviewLog.user_id == user.id,
        ReviewLog.reviewed_at >= now - timedelta(days=30),
    ).all()
    logs_by_domain: dict[str, list[ReviewLog]] = defaultdict(list)
    for log in recent_logs:
        logs_by_domain[card_domains.get(log.card_id, "general")].append(log)

    profile_domains = {profile.domain for profile in user.adaptive_profiles}
    # Les deux parcours initiaux doivent être configurables même avant la
    # première carte : le module sert aussi de point d’entrée pour TOEIC et informatique.
    represented_domains = set(cards_by_domain) | profile_domains | {"language", "computing"}
    overview = []
    for domain in sorted(represented_domains):
        domain_cards = cards_by_domain[domain]
        domain_logs = logs_by_domain[domain]
        reviewed_count = len(domain_logs)
        successful_count = sum(log.rating != "again" for log in domain_logs)
        recall_rate = round(successful_count / reviewed_count, 3) if reviewed_count else None
        average_response_seconds = (
            round(sum(log.response_time for log in domain_logs) / reviewed_count, 1)
            if reviewed_count else None
        )
        due_count = sum(card.is_due for card in domain_cards)
        retention, retention_source = get_effective_retention(user, domain)
        overview.append({
            "domain": domain,
            "label": DOMAIN_OPTIONS[domain],
            "cards_total": len(domain_cards),
            "cards_due": due_count,
            "reviews_last_30_days": reviewed_count,
            "recall_rate": recall_rate,
            "average_response_seconds": average_response_seconds,
            "desired_retention": retention,
            "retention_source": retention_source,
            "recommendation": recommendation_for_domain(
                len(domain_cards), due_count, reviewed_count, recall_rate,
            ),
        })
    return overview
