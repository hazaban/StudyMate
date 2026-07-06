"""Ebbinghaus memory curve algorithm for spaced repetition.
Each mastery level has its own independent review count.
When a card upgrades (unmastered→familiar→mastered) or downgrades,
its count resets so the new level starts from its first interval.
"""
from datetime import date, timedelta

# Intervals keyed by mastery_level, indexed by review_count within that level.
# review_count: 0 = just entered this level, 1 = reviewed once at this level, ...
CARD_INTERVALS = {
    "unmastered": [1, 1, 2, 3, 5, 8, 14, 21, 30],
    "familiar":   [3, 5, 8, 14, 21, 30],
    "mastered":   [7, 14, 30],
}
MASTERED_LONG_TERM = 30


def calculate_next_review_date(
    last_review_date: date,
    mastery_level: str,
    review_count: int = 0,
    created_at: date = None
) -> date:
    today = date.today()
    base_date = max(last_review_date, today)

    levels = CARD_INTERVALS.get(mastery_level, CARD_INTERVALS["unmastered"])
    idx = min(review_count, len(levels) - 1)
    interval_days = levels[idx]

    if mastery_level == "mastered" and review_count >= len(levels):
        interval_days = MASTERED_LONG_TERM

    next_date = base_date + timedelta(days=interval_days)
    if next_date < today:
        next_date = today + timedelta(days=1)
    if created_at and next_date < created_at:
        next_date = created_at + timedelta(days=1)
    return next_date


def update_mastery_level(current_level: str, is_correct: bool) -> str:
    if is_correct:
        if current_level == "unmastered": return "familiar"
        elif current_level == "familiar": return "mastered"
        return "mastered"
    else:
        if current_level == "mastered": return "familiar"
        elif current_level == "familiar": return "unmastered"
        return "unmastered"


def get_today_review_cards(cards: list) -> list:
    today = date.today()
    return [c for c in cards if c.next_review_date <= today]
