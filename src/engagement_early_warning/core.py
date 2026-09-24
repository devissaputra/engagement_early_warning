import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timedelta
from numbers import Real


DEFAULT_COEFFICIENTS = {
    "intercept": -1.6,
    "inactivity_ratio": 1.4,
    "overdue_task_rate": 1.8,
    "activity_drop_ratio": 1.2,
    "recent_activity_ratio": -0.8,
    "recent_score": -0.9,
}

RISK_FEATURES = (
    "inactivity_ratio",
    "overdue_task_rate",
    "activity_drop_ratio",
    "recent_activity_ratio",
    "recent_score",
)


def _finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _unit_interval(value, name):
    value = _finite_number(value, name)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def _positive_int(value, name, *, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    minimum = 0 if allow_zero else 1
    if value < minimum:
        comparator = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be {comparator}")
    return value


def _parse_date(value, name):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD format") from exc


def sigmoid(value: float) -> float:
    """Numerically stable logistic function."""
    value = _finite_number(value, "value")
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def validate_coefficients(coefficients=None):
    coefficients = dict(
        DEFAULT_COEFFICIENTS
        if coefficients is None
        else coefficients
    )
    expected = {"intercept", *RISK_FEATURES}
    if set(coefficients) != expected:
        raise ValueError(
            f"coefficients must contain exactly {sorted(expected)}"
        )
    return {
        name: _finite_number(value, f"{name} coefficient")
        for name, value in coefficients.items()
    }


def _normalize_event(event, *, cutoff=None):
    if not isinstance(event, Mapping):
        raise ValueError("activity events must be mappings")
    if "occurred_on" not in event:
        raise ValueError("activity event is missing occurred_on")
    occurred_on = _parse_date(event["occurred_on"], "occurred_on")
    if cutoff is not None and occurred_on > cutoff:
        raise ValueError("activity event occurs after prediction cutoff")
    event_type = event.get("event_type", "activity")
    if not isinstance(event_type, str) or not event_type.strip():
        raise ValueError("event_type must be a non-empty string")
    return {
        "occurred_on": occurred_on,
        "event_type": event_type.strip(),
    }


def _normalize_task(task, *, cutoff):
    if not isinstance(task, Mapping):
        raise ValueError("tasks must be mappings")
    if "due_on" not in task:
        raise ValueError("task is missing due_on")
    due_on = _parse_date(task["due_on"], "due_on")
    submitted_on = task.get("submitted_on")
    if submitted_on is not None:
        submitted_on = _parse_date(submitted_on, "submitted_on")
    return {
        "due_on": due_on,
        "submitted_on": submitted_on,
        "known_by_cutoff": due_on <= cutoff,
    }


def _normalize_assessment(assessment, *, cutoff):
    if not isinstance(assessment, Mapping):
        raise ValueError("assessments must be mappings")
    for field in ("available_on", "score"):
        if field not in assessment:
            raise ValueError(f"assessment is missing {field}")
    available_on = _parse_date(
        assessment["available_on"],
        "available_on",
    )
    score = _unit_interval(assessment["score"], "assessment score")
    return {
        "available_on": available_on,
        "score": score,
        "usable": available_on <= cutoff,
    }


def construct_time_safe_features(
    activity_events,
    tasks,
    assessments,
    prediction_cutoff,
    *,
    window_days=7,
    inactivity_cap_days=14,
):
    """Build features using only information available by the prediction cutoff."""
    cutoff = _parse_date(prediction_cutoff, "prediction_cutoff")
    window_days = _positive_int(window_days, "window_days")
    inactivity_cap_days = _positive_int(
        inactivity_cap_days,
        "inactivity_cap_days",
    )

    if not isinstance(activity_events, Sequence) or isinstance(
        activity_events, (str, bytes)
    ):
        raise ValueError("activity_events must be a sequence")
    if not isinstance(tasks, Sequence) or isinstance(tasks, (str, bytes)):
        raise ValueError("tasks must be a sequence")
    if not isinstance(assessments, Sequence) or isinstance(
        assessments, (str, bytes)
    ):
        raise ValueError("assessments must be a sequence")

    events = [
        _normalize_event(event, cutoff=cutoff)
        for event in activity_events
    ]
    normalized_tasks = [
        _normalize_task(task, cutoff=cutoff)
        for task in tasks
    ]
    normalized_assessments = [
        _normalize_assessment(assessment, cutoff=cutoff)
        for assessment in assessments
    ]

    current_start = cutoff - timedelta(days=window_days - 1)
    previous_end = current_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=window_days - 1)

    recent_events = [
        event
        for event in events
        if current_start <= event["occurred_on"] <= cutoff
    ]
    previous_events = [
        event
        for event in events
        if previous_start <= event["occurred_on"] <= previous_end
    ]

    if events:
        last_activity = max(event["occurred_on"] for event in events)
        inactive_days = max(0, (cutoff - last_activity).days)
    else:
        inactive_days = inactivity_cap_days

    due_tasks = [
        task
        for task in normalized_tasks
        if task["known_by_cutoff"]
    ]
    overdue_tasks = [
        task
        for task in due_tasks
        if task["submitted_on"] is None
        or task["submitted_on"] > cutoff
    ]

    recent_count = len(recent_events)
    previous_count = len(previous_events)
    activity_drop_ratio = (
        max(0.0, previous_count - recent_count) / previous_count
        if previous_count > 0
        else 0.0
    )

    available_assessments = [
        assessment
        for assessment in normalized_assessments
        if assessment["usable"]
    ]
    recent_score = (
        sorted(
            available_assessments,
            key=lambda row: row["available_on"],
        )[-1]["score"]
        if available_assessments
        else None
    )

    return {
        "prediction_cutoff": cutoff.isoformat(),
        "feature_window_start": previous_start.isoformat(),
        "feature_window_end": cutoff.isoformat(),
        "inactive_days": inactive_days,
        "inactivity_ratio": min(
            1.0,
            inactive_days / inactivity_cap_days,
        ),
        "overdue_tasks": len(overdue_tasks),
        "due_tasks": len(due_tasks),
        "overdue_task_rate": (
            len(overdue_tasks) / len(due_tasks)
            if due_tasks
            else 0.0
        ),
        "recent_activity_count": recent_count,
        "previous_activity_count": previous_count,
        "recent_activity_ratio": min(
            1.0,
            recent_count / window_days,
        ),
        "activity_drop_ratio": min(1.0, activity_drop_ratio),
        "recent_score": recent_score,
        "recent_score_available": recent_score is not None,
    }


def risk_from_features(features, *, coefficients=None):
    """Return a transparent synthetic risk probability and contributions."""
    if not isinstance(features, Mapping):
        raise ValueError("features must be a mapping")
    coefficients = validate_coefficients(coefficients)

    values = {}
    for name in RISK_FEATURES:
        value = features.get(name)
        if name == "recent_score" and value is None:
            values[name] = None
            continue
        values[name] = _unit_interval(value, name)

    linear_score = coefficients["intercept"]
    contributions = {"intercept": coefficients["intercept"]}

    for name in RISK_FEATURES:
        if values[name] is None:
            contributions[name] = None
            continue
        contribution = coefficients[name] * values[name]
        contributions[name] = contribution
        linear_score += contribution

    return {
        "probability": sigmoid(linear_score),
        "linear_score": linear_score,
        "features": values,
        "contributions": contributions,
        "coefficients": coefficients,
        "synthetic_coefficients": True,
    }


def risk_probability(
    inactive_days: float,
    missed_tasks: float,
    forum_posts: float,
    prior_score: float,
) -> float:
    """Backward-compatible synthetic score for the original four inputs."""
    inactive_days = _finite_number(inactive_days, "inactive_days")
    missed_tasks = _finite_number(missed_tasks, "missed_tasks")
    forum_posts = _finite_number(forum_posts, "forum_posts")
    if min(inactive_days, missed_tasks, forum_posts) < 0:
        raise ValueError("activity counts must be non-negative")
    prior_score = _unit_interval(prior_score, "prior_score")

    features = {
        "inactivity_ratio": min(1.0, inactive_days / 14.0),
        "overdue_task_rate": min(1.0, missed_tasks / 3.0),
        "activity_drop_ratio": 0.0,
        "recent_activity_ratio": min(1.0, forum_posts / 7.0),
        "recent_score": prior_score,
    }
    return risk_from_features(features)["probability"]


def validate_prediction_case(case):
    """Validate timing, prediction, outcome, and optional subgroup metadata."""
    if not isinstance(case, Mapping):
        raise ValueError("prediction case must be a mapping")

    required = {
        "learner_id",
        "course_id",
        "prediction_week",
        "prediction_cutoff",
        "outcome_window_start",
        "outcome_window_end",
        "risk",
        "future_disengagement",
    }
    missing = required - set(case)
    if missing:
        raise ValueError(
            f"prediction case is missing fields: {sorted(missing)}"
        )

    for field in ("learner_id", "course_id"):
        if not isinstance(case[field], str) or not case[field].strip():
            raise ValueError(f"{field} must be a non-empty string")

    prediction_week = _positive_int(
        case["prediction_week"],
        "prediction_week",
    )
    cutoff = _parse_date(
        case["prediction_cutoff"],
        "prediction_cutoff",
    )
    outcome_start = _parse_date(
        case["outcome_window_start"],
        "outcome_window_start",
    )
    outcome_end = _parse_date(
        case["outcome_window_end"],
        "outcome_window_end",
    )
    if outcome_start <= cutoff:
        raise ValueError(
            "outcome window must begin after prediction cutoff"
        )
    if outcome_end < outcome_start:
        raise ValueError(
            "outcome_window_end must not precede outcome_window_start"
        )

    risk = _unit_interval(case["risk"], "risk")
    outcome = case["future_disengagement"]
    if outcome not in (0, 1) or isinstance(outcome, bool):
        raise ValueError("future_disengagement must be integer 0 or 1")

    event_on = case.get("disengagement_event_on")
    if event_on is not None:
        event_on = _parse_date(
            event_on,
            "disengagement_event_on",
        )
        if outcome != 1:
            raise ValueError(
                "disengagement_event_on requires future_disengagement=1"
            )
        if not outcome_start <= event_on <= outcome_end:
            raise ValueError(
                "disengagement event must fall inside outcome window"
            )
    elif outcome == 1:
        raise ValueError(
            "positive outcomes require disengagement_event_on for lead-time analysis"
        )

    group = case.get("group", "all")
    if not isinstance(group, str) or not group.strip():
        raise ValueError("group must be a non-empty string")

    return {
        "learner_id": case["learner_id"].strip(),
        "course_id": case["course_id"].strip(),
        "prediction_week": prediction_week,
        "prediction_cutoff": cutoff,
        "outcome_window_start": outcome_start,
        "outcome_window_end": outcome_end,
        "risk": risk,
        "future_disengagement": int(outcome),
        "disengagement_event_on": event_on,
        "group": group.strip(),
    }


def calibration_bins(
    predictions: Sequence[float],
    outcomes: Sequence[int],
    bins: int = 5,
) -> list[dict]:
    """Group probabilities into reliability bins."""
    bins = _positive_int(bins, "bins")
    if not predictions or len(predictions) != len(outcomes):
        raise ValueError(
            "predictions and outcomes must be non-empty and have equal length"
        )

    predictions = [
        _unit_interval(value, "prediction")
        for value in predictions
    ]
    cleaned_outcomes = []
    for value in outcomes:
        if value not in (0, 1) or isinstance(value, bool):
            raise ValueError("outcomes must contain integer 0 or 1")
        cleaned_outcomes.append(int(value))

    rows = []
    for bin_index in range(bins):
        lower = bin_index / bins
        upper = (bin_index + 1) / bins
        members = [
            index
            for index, probability in enumerate(predictions)
            if (
                lower <= probability < upper
                or (bin_index == bins - 1 and probability == 1)
            )
        ]
        if members:
            mean_pred = (
                sum(predictions[i] for i in members) / len(members)
            )
            observed = (
                sum(cleaned_outcomes[i] for i in members)
                / len(members)
            )
            rows.append(
                {
                    "bin": bin_index,
                    "lower": lower,
                    "upper": upper,
                    "mean_pred": mean_pred,
                    "observed": observed,
                    "absolute_gap": abs(mean_pred - observed),
                    "n": len(members),
                }
            )
    return rows


def brier_score(predictions, outcomes):
    if not predictions or len(predictions) != len(outcomes):
        raise ValueError(
            "predictions and outcomes must be non-empty and have equal length"
        )
    predictions = [
        _unit_interval(value, "prediction")
        for value in predictions
    ]
    cleaned = []
    for value in outcomes:
        if value not in (0, 1) or isinstance(value, bool):
            raise ValueError("outcomes must contain integer 0 or 1")
        cleaned.append(int(value))
    return sum(
        (prediction - outcome) ** 2
        for prediction, outcome in zip(predictions, cleaned)
    ) / len(predictions)


def expected_calibration_error(predictions, outcomes, bins=5):
    rows = calibration_bins(predictions, outcomes, bins=bins)
    n = len(predictions)
    return sum(
        row["absolute_gap"] * row["n"] / n
        for row in rows
    )


def review_queue(
    cases,
    *,
    review_budget,
    alert_history=None,
    cooldown_days=14,
):
    """Select highest-risk cases within a human review budget and cooldown."""
    review_budget = _positive_int(
        review_budget,
        "review_budget",
    )
    cooldown_days = _positive_int(
        cooldown_days,
        "cooldown_days",
        allow_zero=True,
    )
    if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)):
        raise ValueError("cases must be a sequence")

    validated = [
        validate_prediction_case(case)
        for case in cases
    ]
    alert_history = {} if alert_history is None else dict(alert_history)

    eligible = []
    suppressed = []
    for case in validated:
        last_alert = alert_history.get(case["learner_id"])
        if last_alert is not None:
            last_alert = _parse_date(last_alert, "last_alert")
            days_since_alert = (
                case["prediction_cutoff"] - last_alert
            ).days
            if days_since_alert < 0:
                raise ValueError(
                    "alert history cannot occur after prediction cutoff"
                )
            if days_since_alert < cooldown_days:
                suppressed.append(
                    {
                        **case,
                        "suppression_reason": "cooldown",
                        "days_since_alert": days_since_alert,
                    }
                )
                continue
        eligible.append(case)

    eligible.sort(
        key=lambda row: (
            -row["risk"],
            row["learner_id"],
        )
    )
    selected = eligible[:review_budget]
    threshold = (
        selected[-1]["risk"]
        if selected
        else None
    )
    return {
        "selected": selected,
        "suppressed": suppressed,
        "review_budget": review_budget,
        "threshold": threshold,
        "eligible_count": len(eligible),
    }


def _classification_counts(selected_ids, cases):
    tp = fp = fn = tn = 0
    for case in cases:
        selected = case["learner_id"] in selected_ids
        outcome = case["future_disengagement"]
        if selected and outcome == 1:
            tp += 1
        elif selected and outcome == 0:
            fp += 1
        elif not selected and outcome == 1:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def evaluate_review_budget(
    cases,
    *,
    review_budget,
    alert_history=None,
    cooldown_days=14,
    calibration_bin_count=5,
):
    """Evaluate a capacity-constrained human review queue."""
    validated = [
        validate_prediction_case(case)
        for case in cases
    ]
    queue = review_queue(
        validated,
        review_budget=review_budget,
        alert_history=alert_history,
        cooldown_days=cooldown_days,
    )
    selected_ids = {
        case["learner_id"]
        for case in queue["selected"]
    }
    tp, fp, fn, tn = _classification_counts(
        selected_ids,
        validated,
    )

    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    false_positive_rate = (
        fp / (fp + tn)
        if fp + tn
        else None
    )
    false_negative_rate = (
        fn / (fn + tp)
        if fn + tp
        else None
    )

    lead_times = []
    for case in queue["selected"]:
        if (
            case["future_disengagement"] == 1
            and case["disengagement_event_on"] is not None
        ):
            lead_times.append(
                (
                    case["disengagement_event_on"]
                    - case["prediction_cutoff"]
                ).days
            )

    predictions = [case["risk"] for case in validated]
    outcomes = [
        case["future_disengagement"]
        for case in validated
    ]

    return {
        "n": len(validated),
        "review_budget": review_budget,
        "selected_count": len(queue["selected"]),
        "threshold": queue["threshold"],
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate,
        "mean_lead_time_days": (
            sum(lead_times) / len(lead_times)
            if lead_times
            else None
        ),
        "median_lead_time_days": (
            sorted(lead_times)[len(lead_times) // 2]
            if lead_times
            else None
        ),
        "brier_score": brier_score(predictions, outcomes),
        "expected_calibration_error": expected_calibration_error(
            predictions,
            outcomes,
            bins=calibration_bin_count,
        ),
        "calibration_bins": calibration_bins(
            predictions,
            outcomes,
            bins=calibration_bin_count,
        ),
        "selected": queue["selected"],
        "suppressed": queue["suppressed"],
    }


def subgroup_audit(
    cases,
    *,
    review_budget,
    group_field="group",
    calibration_bin_count=3,
):
    """Report descriptive group error and calibration diagnostics."""
    if group_field != "group":
        raise ValueError(
            "current baseline supports the normalized 'group' field only"
        )
    validated = [
        validate_prediction_case(case)
        for case in cases
    ]
    queue = review_queue(
        validated,
        review_budget=review_budget,
        cooldown_days=0,
    )
    selected_ids = {
        case["learner_id"]
        for case in queue["selected"]
    }

    grouped = defaultdict(list)
    for case in validated:
        grouped[case["group"]].append(case)

    rows = {}
    for group, members in sorted(grouped.items()):
        tp, fp, fn, tn = _classification_counts(
            selected_ids,
            members,
        )
        predictions = [row["risk"] for row in members]
        outcomes = [
            row["future_disengagement"]
            for row in members
        ]
        rows[group] = {
            "n": len(members),
            "prevalence": sum(outcomes) / len(outcomes),
            "selected_fraction": (
                sum(
                    row["learner_id"] in selected_ids
                    for row in members
                )
                / len(members)
            ),
            "precision": (
                tp / (tp + fp)
                if tp + fp
                else None
            ),
            "recall": (
                tp / (tp + fn)
                if tp + fn
                else None
            ),
            "false_positive_rate": (
                fp / (fp + tn)
                if fp + tn
                else None
            ),
            "false_negative_rate": (
                fn / (fn + tp)
                if fn + tp
                else None
            ),
            "brier_score": brier_score(
                predictions,
                outcomes,
            ),
            "expected_calibration_error": (
                expected_calibration_error(
                    predictions,
                    outcomes,
                    bins=min(
                        calibration_bin_count,
                        len(members),
                    ),
                )
            ),
        }
    return rows


def temporal_holdout(cases, holdout_start):
    """Split prediction cases by prediction date without random leakage."""
    holdout_start = _parse_date(
        holdout_start,
        "holdout_start",
    )
    validated = [
        validate_prediction_case(case)
        for case in cases
    ]
    development = [
        case
        for case in validated
        if case["prediction_cutoff"] < holdout_start
    ]
    holdout = [
        case
        for case in validated
        if case["prediction_cutoff"] >= holdout_start
    ]
    if not development or not holdout:
        raise ValueError(
            "temporal holdout requires records on both sides of holdout_start"
        )
    return {
        "development": development,
        "holdout": holdout,
        "holdout_start": holdout_start.isoformat(),
    }


def contribution_explanation(score_record):
    """Explain a synthetic score using only its actual component contributions."""
    if not isinstance(score_record, Mapping):
        raise ValueError("score_record must be a mapping")
    probability = _unit_interval(
        score_record.get("probability"),
        "probability",
    )
    contributions = score_record.get("contributions")
    if not isinstance(contributions, Mapping):
        raise ValueError("score_record is missing contributions")

    ranked = [
        (name, value)
        for name, value in contributions.items()
        if name != "intercept" and value is not None
    ]
    ranked.sort(
        key=lambda item: (
            -abs(item[1]),
            item[0],
        )
    )
    strongest = ", ".join(
        f"{name}={value:+.3f}"
        for name, value in ranked[:3]
    )
    return (
        f"Synthetic risk probability={probability:.3f}. "
        f"Strongest score contributions: {strongest}. "
        "This is a review signal, not a label of motivation, ability, or intent."
    )
