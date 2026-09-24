import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from engagement_early_warning import core


class CoreTests(unittest.TestCase):
    def test_risk_orders_clear_examples(self):
        high = core.risk_probability(10, 2, 0, 0.4)
        low = core.risk_probability(1, 0, 2, 0.8)
        self.assertGreater(high, low)

    def test_calibration_bins_validate_inputs(self):
        rows = core.calibration_bins([0.1, 0.8], [0, 1])
        self.assertEqual(sum(row["n"] for row in rows), 2)
        with self.assertRaises(ValueError):
            core.calibration_bins([], [])


if __name__ == "__main__":
    unittest.main()
