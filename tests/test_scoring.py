"""scoring.py の簡易テスト。"""
from backend.schemas.search import Budget, TimeSlot
from backend.services.scoring import score_place


def test_score_place_prefers_higher_rating():
    high_rating = {"rating": 4.8, "user_ratings_total": 500, "price_level": 2}
    low_rating = {"rating": 3.0, "user_ratings_total": 500, "price_level": 2}

    high_score = score_place(high_rating, TimeSlot.DAY, Budget.UNDER_3000)
    low_score = score_place(low_rating, TimeSlot.DAY, Budget.UNDER_3000)

    assert high_score > low_score


def test_score_place_handles_missing_fields():
    place: dict = {}
    score = score_place(place, TimeSlot.MORNING, Budget.UNDER_2000)
    assert score >= 0


def test_score_place_rewards_budget_match():
    matching = {"rating": 4.0, "user_ratings_total": 100, "price_level": 2}
    non_matching = {"rating": 4.0, "user_ratings_total": 100, "price_level": 4}

    matching_score = score_place(matching, TimeSlot.DAY, Budget.UNDER_3000)
    non_matching_score = score_place(non_matching, TimeSlot.DAY, Budget.UNDER_3000)

    assert matching_score > non_matching_score
