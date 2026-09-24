import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from engagement_early_warning import core


def case(
    learner_id,
    risk,
    outcome,
    *,
    cutoff="2026-09-14",
    event_on=None,
    group="A",
    week=3,
):
    return {
        "learner_id": learner_id,
        "course_id": "C01",
        "prediction_week": week,
        "prediction_cutoff": cutoff,
        "outcome_window_start": "2026-09-15",
        "outcome_window_end": "2026-10-05",
        "risk": risk,
        "future_disengagement": outcome,
        "disengagement_event_on": event_on,
        "group": group,
    }


class CoreTests(unittest.TestCase):
    def test_sigmoid_is_stable(self):
        self.assertGreater(core.sigmoid(1000), 0.99)
        self.assertLess(core.sigmoid(-1000), 0.01)

    def test_sigmoid_rejects_nan(self):
        with self.assertRaises(ValueError):
            core.sigmoid(math.nan)

    def test_risk_orders_clear_legacy_examples(self):
        high = core.risk_probability(10, 2, 0, 0.4)
        low = core.risk_probability(1, 0, 2, 0.8)
        self.assertGreater(high, low)

    def test_risk_rejects_boolean_counts(self):
        with self.assertRaises(ValueError):
            core.risk_probability(True, 1, 1, 0.5)

    def test_time_safe_features_reject_future_activity(self):
        with self.assertRaises(ValueError):
            core.construct_time_safe_features(
                [{"occurred_on": "2026-09-15"}],
                [],
                [],
                "2026-09-14",
            )

    def test_future_task_due_date_is_not_overdue(self):
        features = core.construct_time_safe_features(
            [],
            [{"due_on": "2026-09-20", "submitted_on": None}],
            [],
            "2026-09-14",
        )
        self.assertEqual(features["due_tasks"], 0)
        self.assertEqual(features["overdue_tasks"], 0)

    def test_submission_after_cutoff_counts_as_overdue_at_cutoff(self):
        features = core.construct_time_safe_features(
            [],
            [
                {
                    "due_on": "2026-09-10",
                    "submitted_on": "2026-09-16",
                }
            ],
            [],
            "2026-09-14",
        )
        self.assertEqual(features["overdue_tasks"], 1)

    def test_future_assessment_is_not_used(self):
        features = core.construct_time_safe_features(
            [],
            [],
            [
                {
                    "available_on": "2026-09-20",
                    "score": 0.9,
                }
            ],
            "2026-09-14",
        )
        self.assertIsNone(features["recent_score"])

    def test_latest_available_assessment_is_used(self):
        features = core.construct_time_safe_features(
            [],
            [],
            [
                {
                    "available_on": "2026-09-01",
                    "score": 0.6,
                },
                {
                    "available_on": "2026-09-12",
                    "score": 0.8,
                },
            ],
            "2026-09-14",
        )
        self.assertEqual(features["recent_score"], 0.8)

    def test_activity_drop_is_computed_from_prior_window(self):
        events = [
            {"occurred_on": "2026-09-03"},
            {"occurred_on": "2026-09-04"},
            {"occurred_on": "2026-09-05"},
            {"occurred_on": "2026-09-12"},
        ]
        features = core.construct_time_safe_features(
            events,
            [],
            [],
            "2026-09-14",
            window_days=7,
        )
        self.assertGreater(features["activity_drop_ratio"], 0)

    def test_risk_score_returns_components(self):
        record = core.risk_from_features(
            {
                "inactivity_ratio": 0.5,
                "overdue_task_rate": 0.5,
                "activity_drop_ratio": 0.5,
                "recent_activity_ratio": 0.2,
                "recent_score": 0.7,
            }
        )
        self.assertIn("contributions", record)
        self.assertTrue(record["synthetic_coefficients"])

    def test_missing_recent_score_is_supported(self):
        record = core.risk_from_features(
            {
                "inactivity_ratio": 0.5,
                "overdue_task_rate": 0.5,
                "activity_drop_ratio": 0.5,
                "recent_activity_ratio": 0.2,
                "recent_score": None,
            }
        )
        self.assertIsNone(record["contributions"]["recent_score"])

    def test_prediction_case_requires_future_outcome_window(self):
        bad = case(
            "L1",
            0.8,
            1,
            event_on="2026-09-16",
        )
        bad["outcome_window_start"] = "2026-09-14"
        with self.assertRaises(ValueError):
            core.validate_prediction_case(bad)

    def test_positive_outcome_requires_event_date(self):
        with self.assertRaises(ValueError):
            core.validate_prediction_case(case("L1", 0.8, 1))

    def test_event_must_fall_inside_outcome_window(self):
        with self.assertRaises(ValueError):
            core.validate_prediction_case(
                case(
                    "L1",
                    0.8,
                    1,
                    event_on="2026-10-20",
                )
            )

    def test_calibration_bins_validate_inputs(self):
        rows = core.calibration_bins([0.1, 0.8], [0, 1])
        self.assertEqual(sum(row["n"] for row in rows), 2)
        with self.assertRaises(ValueError):
            core.calibration_bins([], [])

    def test_calibration_bins_reject_boolean_bins(self):
        with self.assertRaises(ValueError):
            core.calibration_bins([0.1], [0], bins=True)

    def test_brier_score_known_example(self):
        self.assertAlmostEqual(
            core.brier_score([0.0, 1.0], [0, 1]),
            0.0,
        )

    def test_expected_calibration_error_is_non_negative(self):
        value = core.expected_calibration_error(
            [0.1, 0.2, 0.8, 0.9],
            [0, 0, 1, 1],
            bins=2,
        )
        self.assertGreaterEqual(value, 0)

    def test_review_queue_respects_budget(self):
        cases = [
            case("L1", 0.9, 1, event_on="2026-09-20"),
            case("L2", 0.8, 0),
            case("L3", 0.7, 0),
        ]
        queue = core.review_queue(cases, review_budget=2)
        self.assertEqual(len(queue["selected"]), 2)
        self.assertEqual(queue["selected"][0]["learner_id"], "L1")

    def test_review_queue_cooldown_suppresses_repeat_alert(self):
        cases = [
            case("L1", 0.9, 1, event_on="2026-09-20"),
            case("L2", 0.8, 0),
        ]
        queue = core.review_queue(
            cases,
            review_budget=2,
            alert_history={"L1": "2026-09-10"},
            cooldown_days=7,
        )
        self.assertEqual(
            queue["suppressed"][0]["learner_id"],
            "L1",
        )

    def test_future_alert_history_is_rejected(self):
        with self.assertRaises(ValueError):
            core.review_queue(
                [
                    case(
                        "L1",
                        0.9,
                        1,
                        event_on="2026-09-20",
                    )
                ],
                review_budget=1,
                alert_history={"L1": "2026-09-20"},
            )

    def test_evaluation_computes_precision_recall_and_lead_time(self):
        cases = [
            case("L1", 0.9, 1, event_on="2026-09-20"),
            case("L2", 0.8, 0),
            case("L3", 0.7, 1, event_on="2026-09-28"),
            case("L4", 0.1, 0),
        ]
        result = core.evaluate_review_budget(
            cases,
            review_budget=2,
        )
        self.assertEqual(result["true_positive"], 1)
        self.assertEqual(result["false_positive"], 1)
        self.assertAlmostEqual(result["precision"], 0.5)
        self.assertAlmostEqual(result["recall"], 0.5)
        self.assertEqual(result["mean_lead_time_days"], 6)

    def test_evaluation_computes_brier_and_ece(self):
        cases = [
            case("L1", 0.9, 1, event_on="2026-09-20"),
            case("L2", 0.2, 0),
        ]
        result = core.evaluate_review_budget(
            cases,
            review_budget=1,
            calibration_bin_count=2,
        )
        self.assertIn("brier_score", result)
        self.assertIn("expected_calibration_error", result)

    def test_subgroup_audit_returns_each_group(self):
        cases = [
            case(
                "L1",
                0.9,
                1,
                event_on="2026-09-20",
                group="A",
            ),
            case("L2", 0.8, 0, group="A"),
            case(
                "L3",
                0.7,
                1,
                event_on="2026-09-28",
                group="B",
            ),
            case("L4", 0.1, 0, group="B"),
        ]
        audit = core.subgroup_audit(
            cases,
            review_budget=2,
        )
        self.assertEqual(set(audit), {"A", "B"})

    def test_subgroup_audit_reports_group_brier(self):
        cases = [
            case(
                "L1",
                0.9,
                1,
                event_on="2026-09-20",
                group="A",
            ),
            case("L2", 0.2, 0, group="A"),
        ]
        audit = core.subgroup_audit(
            cases,
            review_budget=1,
        )
        self.assertIn("brier_score", audit["A"])

    def test_temporal_holdout_splits_by_prediction_date(self):
        early = case(
            "L1",
            0.8,
            1,
            cutoff="2026-09-07",
            event_on="2026-09-16",
        )
        early["outcome_window_start"] = "2026-09-08"
        early["outcome_window_end"] = "2026-09-28"
        late = case(
            "L2",
            0.7,
            0,
            cutoff="2026-09-21",
        )
        late["outcome_window_start"] = "2026-09-22"
        late["outcome_window_end"] = "2026-10-12"
        split = core.temporal_holdout(
            [early, late],
            "2026-09-14",
        )
        self.assertEqual(len(split["development"]), 1)
        self.assertEqual(len(split["holdout"]), 1)

    def test_temporal_holdout_requires_both_sides(self):
        with self.assertRaises(ValueError):
            core.temporal_holdout(
                [
                    case(
                        "L1",
                        0.8,
                        1,
                        event_on="2026-09-20",
                    )
                ],
                "2026-09-01",
            )

    def test_explanation_uses_actual_contributions(self):
        score = core.risk_from_features(
            {
                "inactivity_ratio": 0.8,
                "overdue_task_rate": 0.7,
                "activity_drop_ratio": 0.6,
                "recent_activity_ratio": 0.1,
                "recent_score": 0.4,
            }
        )
        text = core.contribution_explanation(score)
        self.assertIn("Synthetic risk probability=", text)
        self.assertIn("review signal", text)


if __name__ == "__main__":
    unittest.main()
