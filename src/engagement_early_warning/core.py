import math
from collections.abc import Sequence


def sigmoid(value: float) -> float:
    """Numerically stable logistic function."""
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def risk_probability(
    inactive_days: float,
    missed_tasks: float,
    forum_posts: float,
    prior_score: float,
) -> float:
    """Return an interpretable synthetic disengagement risk score."""
    if min(inactive_days, missed_tasks, forum_posts) < 0:
        raise ValueError("activity counts must be non-negative")
    if not 0.0 <= prior_score <= 1.0:
        raise ValueError("prior_score must be between 0 and 1")
    linear_score = (
        -1.8
        + 0.18 * inactive_days
        + 0.75 * missed_tasks
        - 0.12 * forum_posts
        - 1.2 * prior_score
    )
    return sigmoid(linear_score)


def calibration_bins(
    predictions: Sequence[float], outcomes: Sequence[int], bins: int = 5
) -> list[dict]:
    """Group probabilities into bins for a simple calibration review."""
    if not predictions or len(predictions) != len(outcomes):
        raise ValueError("predictions and outcomes must be non-empty and have equal length")
    if bins <= 0:
        raise ValueError("bins must be positive")
    if any(not 0.0 <= value <= 1.0 for value in predictions):
        raise ValueError("predictions must be between 0 and 1")
    if any(value not in (0, 1) for value in outcomes):
        raise ValueError("outcomes must contain only 0 and 1")

    rows = []
    for bin_index in range(bins):
        lower = bin_index / bins
        upper = (bin_index + 1) / bins
        members = [
            index
            for index, probability in enumerate(predictions)
            if lower <= probability < upper
            or (bin_index == bins - 1 and probability == 1)
        ]
        if members:
            rows.append(
                {
                    "bin": bin_index,
                    "mean_pred": sum(predictions[i] for i in members) / len(members),
                    "observed": sum(outcomes[i] for i in members) / len(members),
                    "n": len(members),
                }
            )
    return rows
