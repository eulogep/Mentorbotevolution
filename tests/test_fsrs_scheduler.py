import json

import pytest

from src.services.fsrs_scheduler import (
    DEFAULT_RETENTION,
    normalize_desired_retention,
    normalize_rating,
    review_with_fsrs,
)


def test_normalize_legacy_quality_and_explicit_rating():
    assert normalize_rating({"rating": "easy"})[0] == "easy"
    assert normalize_rating({"quality_response": 0})[0] == "again"
    assert normalize_rating({"quality_response": 2})[0] == "hard"
    assert normalize_rating({"quality_response": 4})[0] == "good"
    assert normalize_rating({"quality_response": 5})[0] == "easy"


def test_normalize_rating_rejects_invalid_input():
    with pytest.raises(ValueError):
        normalize_rating({})
    with pytest.raises(ValueError):
        normalize_rating({"quality_response": 8})


def test_desired_retention_is_bounded():
    assert normalize_desired_retention(None) == DEFAULT_RETENTION
    assert normalize_desired_retention(0.1) == 0.80
    assert normalize_desired_retention(2) == 0.97


def test_fsrs_review_generates_serializable_state_and_a_future_due_date():
    rating_name, rating = normalize_rating({"rating": "good"})
    assert rating_name == "good"

    result = review_with_fsrs("", rating, 0.90)

    state = json.loads(result["card_state"])
    log = json.loads(result["review_log"])
    assert state["state"] in {1, 2, 3}
    assert log["rating"] == 3
    assert result["scheduled_days"] >= 1
    assert result["due_at"] > result["reviewed_at"]
    assert 0 <= result["retrievability_after"] <= 1
