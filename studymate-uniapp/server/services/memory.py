"""Ebbinghaus memory curve algorithm for spaced repetition."""

from datetime import date, timedelta

# Review intervals in days based on mastery level
REVIEW_INTERVALS = {
    "unmastered": 1,       # Review again tomorrow
    "familiar": 3,          # Review in 3 days
    "mastered": 7           # Review in 7 days
}

# Extended intervals for long-term stable review
LONG_TERM_INTERVALS = {
    "unmastered": 1,
    "familiar": 2,
    "mastered": 14
}


def calculate_next_review_date(
    last_review_date: date,
    mastery_level: str,
    review_count: int = 0
) -> date:
    """Calculate the next review date based on Ebbinghaus curve.

    Args:
        last_review_date: The date of last review
        mastery_level: Current mastery level (unmastered/familiar/mastered)
        review_count: Total number of reviews so far

    Returns:
        The next review date
    """
    # If reviewed many times (>5), extend the interval
    if review_count > 5:
        intervals = LONG_TERM_INTERVALS
    else:
        intervals = REVIEW_INTERVALS

    interval_days = intervals.get(mastery_level, 1)

    # Gradually extend intervals for high-frequency review
    if mastery_level == "mastered" and review_count > 3:
        interval_days = min(30, 7 * (review_count - 2))

    return last_review_date + timedelta(days=interval_days)


def update_mastery_level(current_level: str, is_correct: bool) -> str:
    """Update mastery level based on review result.

    Args:
        current_level: Current mastery level
        is_correct: Whether the user answered correctly

    Returns:
        New mastery level
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
    """Filter cards that need review today."""
    today = date.today()
    return [c for c in cards if c.next_review_date <= today]