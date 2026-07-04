"""Ebbinghaus memory curve algorithm for spaced repetition.

Cards: next_review_date computed as today + interval based on mastery + review_count.
Mistakes: independent 1/3/7/14/30 day intervals based on consecutive correct_count.

Key invariant: next_review_date is always >= today (never in the past),
and >= created_at (never before creation).
"""

from datetime import date, timedelta


# ─── Flash Cards: Ebbinghaus intervals ────────────────────────────────────
# Intervals are in days, keyed by mastery_level.
# Each review_count tier picks a progressively longer interval.
# After 5 reviews, intervals cap at 30 days (monthly review).

CARD_INTERVALS = {
    "unmastered": [1, 1, 2, 3, 5, 8, 14, 21, 30],
    "familiar":   [3, 5, 8, 14, 21, 30],
    "mastered":   [7, 14, 30],
}

MASTERED_LONG_TERM = 30  # days between reviews for long-term mastered cards


def calculate_next_review_date(
    last_review_date: date,
    mastery_level: str,
    review_count: int = 0,
    created_at: date = None
) -> date:
    """Calculate the next review date using modified Ebbinghaus curve.

    Args:
        last_review_date: The date of last review (or today for new cards)
        mastery_level: unmastered / familiar / mastered
        review_count: Total number of reviews so far
        created_at: Original creation date (to prevent next_review < creation)

    Returns:
        The next review date (always >= today, always >= created_at if provided)
    """
    today = date.today()

    # For first review of a new card, last_review_date is meaningless.
    # Base from today.
    base_date = max(last_review_date, today)

    levels = CARD_INTERVALS.get(mastery_level, CARD_INTERVALS["unmastered"])
    idx = min(review_count, len(levels) - 1)
    interval_days = levels[idx]

    # For mastered cards reviewed many times, use fixed long-term interval
    if mastery_level == "mastered" and review_count >= len(levels):
        interval_days = MASTERED_LONG_TERM

    next_date = base_date + timedelta(days=interval_days)

    # Never allow next_review_date to be in the past
    if next_date < today:
        next_date = today + timedelta(days=1)

    # Never allow next_review_date to be before creation date
    if created_at and next_date < created_at:
        next_date = created_at + timedelta(days=1)

    return next_date


def update_mastery_level(current_level: str, is_correct: bool) -> str:
    """Update mastery level after a single review answer.

    Correct: unmastered→familiar→mastered
    Incorrect: mastered→familiar→unmastered
    """
    if is_correct:
        if current_level == "unmastered":
            return "familiar"
        elif current_level == "familiar":
            return "mastered"
        return "mastered"
    else:
        if current_level == "mastered":
            return "familiar"
        elif current_level == "familiar":
            return "unmastered"
        return "unmastered"


def get_today_review_cards(cards: list) -> list:
    """Filter cards whose next_review_date is today or earlier."""
    today = date.today()
    return [c for c in cards if c.next_review_date <= today]
