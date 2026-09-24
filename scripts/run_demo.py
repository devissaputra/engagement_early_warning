import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from engagement_early_warning.core import (
    construct_time_safe_features,
    contribution_explanation,
    evaluate_review_budget,
    risk_from_features,
    subgroup_audit,
    temporal_holdout,
)


def load_cases():
    rows = []
    with (ROOT / "data" / "sample.csv").open(
        encoding="utf-8",
        newline="",
    ) as handle:
        for row in csv.DictReader(handle):
            features = {
                "inactivity_ratio": float(row["inactivity_ratio"]),
                "overdue_task_rate": float(row["overdue_task_rate"]),
                "activity_drop_ratio": float(row["activity_drop_ratio"]),
                "recent_activity_ratio": float(row["recent_activity_ratio"]),
                "recent_score": (
                    None
                    if row["recent_score"] == ""
                    else float(row["recent_score"])
                ),
            }
            score = risk_from_features(features)
            rows.append(
                {
                    "learner_id": row["learner_id"],
                    "course_id": row["course_id"],
                    "group": row["group"],
                    "prediction_week": int(row["prediction_week"]),
                    "prediction_cutoff": row["prediction_cutoff"],
                    "outcome_window_start": row["outcome_window_start"],
                    "outcome_window_end": row["outcome_window_end"],
                    "risk": score["probability"],
                    "future_disengagement": int(
                        row["future_disengagement"]
                    ),
                    "disengagement_event_on": (
                        row["disengagement_event_on"] or None
                    ),
                    "score_record": score,
                }
            )
    return rows


with (ROOT / "data" / "history_example.json").open(
    encoding="utf-8"
) as handle:
    history = json.load(handle)

features = construct_time_safe_features(
    history["activity_events"],
    history["tasks"],
    history["assessments"],
    history["prediction_cutoff"],
)

history_score = risk_from_features(features)

print("Engagement Early-Warning System synthetic demo")
print()
print("Cutoff-safe feature example:")
print(
    {
        "prediction_cutoff": features["prediction_cutoff"],
        "inactive_days": features["inactive_days"],
        "overdue_tasks": features["overdue_tasks"],
        "due_tasks": features["due_tasks"],
        "recent_activity_count": features["recent_activity_count"],
        "previous_activity_count": features["previous_activity_count"],
        "recent_score": features["recent_score"],
        "risk": round(history_score["probability"], 3),
    }
)
print(contribution_explanation(history_score))

cases = load_cases()
evaluation = evaluate_review_budget(
    cases,
    review_budget=6,
    calibration_bin_count=4,
)

print("\nReview-budget evaluation:")
for key in (
    "n",
    "review_budget",
    "selected_count",
    "threshold",
    "precision",
    "recall",
    "false_positive_rate",
    "false_negative_rate",
    "mean_lead_time_days",
    "brier_score",
    "expected_calibration_error",
):
    value = evaluation[key]
    if isinstance(value, float):
        value = round(value, 3)
    print(key, value)

print("\nSelected learners:")
for row in evaluation["selected"]:
    original = next(
        case
        for case in cases
        if case["learner_id"] == row["learner_id"]
    )
    print(
        row["learner_id"],
        {
            "risk": round(row["risk"], 3),
            "future_disengagement": row["future_disengagement"],
            "lead_time_days": (
                None
                if row["disengagement_event_on"] is None
                else (
                    row["disengagement_event_on"]
                    - row["prediction_cutoff"]
                ).days
            ),
            "explanation": contribution_explanation(
                original["score_record"]
            ),
        },
    )

print("\nCalibration bins:")
for row in evaluation["calibration_bins"]:
    print(
        {
            key: round(value, 3)
            if isinstance(value, float)
            else value
            for key, value in row.items()
        }
    )

print("\nSubgroup audit:")
audit = subgroup_audit(
    cases,
    review_budget=6,
    calibration_bin_count=3,
)
for group, row in audit.items():
    print(
        group,
        {
            key: round(value, 3)
            if isinstance(value, float)
            else value
            for key, value in row.items()
        },
    )

split = temporal_holdout(cases, "2026-09-14")
print(
    "\nTemporal holdout:",
    {
        "development_n": len(split["development"]),
        "holdout_n": len(split["holdout"]),
        "holdout_start": split["holdout_start"],
    },
)

print(
    "\nNote: coefficients, learner histories, outcomes, groups, and metrics "
    "are synthetic. The demo tests time safety, review-capacity evaluation, "
    "calibration diagnostics, lead time, and subgroup auditing; it does not "
    "establish validity for a real course or learner population."
)
