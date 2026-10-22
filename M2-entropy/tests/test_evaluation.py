"""Tests for window-level evaluation against dataset labels."""

import sys
import unittest
from pathlib import Path

SYS_PATH_M2 = str(Path(__file__).resolve().parent.parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import numpy as np
import pandas as pd

from evaluation import compute_metrics, evaluate_windows, label_windows


class TestLabelWindows(unittest.TestCase):
    def setUp(self):
        self.flows = pd.DataFrame({
            "Label": ["Benign"] * 4 + ["Malicious"] * 4 + ["Benign"] * 2,
            "Attack Type": ["Benign"] * 4 + ["UDPFlood", "UDPFlood", "SYNFlood", "UDPFlood"] + ["Benign"] * 2,
        })
        self.windows = pd.DataFrame({"start_idx": [0, 2, 4, 6, 8], "end_idx": [4, 6, 8, 10, 10]})

    def test_fraction_and_y_true_with_default_half_rule(self):
        out = label_windows(self.windows, self.flows)
        self.assertEqual(out["malicious_fraction"].tolist(), [0.0, 0.5, 1.0, 0.5, 0.0])
        self.assertEqual(out["y_true"].tolist(), [0, 1, 1, 1, 0])

    def test_custom_attack_fraction(self):
        out = label_windows(self.windows, self.flows, attack_fraction=1.0)
        self.assertEqual(out["y_true"].tolist(), [0, 0, 1, 0, 0])

    def test_dominant_attack_type(self):
        out = label_windows(self.windows, self.flows)
        self.assertEqual(out["dominant_attack_type"].tolist(), ["", "UDPFlood", "UDPFlood", "UDPFlood", ""])

    def test_missing_label_column(self):
        with self.assertRaises(KeyError):
            label_windows(self.windows, self.flows.drop(columns=["Label"]))

    def test_invalid_attack_fraction(self):
        with self.assertRaises(ValueError):
            label_windows(self.windows, self.flows, attack_fraction=0.0)


class TestMetrics(unittest.TestCase):
    def test_known_confusion_matrix(self):
        y_true = np.array([1, 1, 1, 0, 0, 0, 0, 1])
        y_pred = np.array([1, 1, 0, 1, 0, 0, 0, 0])
        m = compute_metrics(y_true, y_pred)
        self.assertEqual((m["tp"], m["fp"], m["fn"], m["tn"]), (2, 1, 2, 3))
        self.assertAlmostEqual(m["precision"], 2 / 3)
        self.assertAlmostEqual(m["recall"], 0.5)
        self.assertAlmostEqual(m["f1"], 2 * (2 / 3) * 0.5 / ((2 / 3) + 0.5))
        self.assertAlmostEqual(m["false_positive_rate"], 0.25)

    def test_undefined_ratios_are_none_not_zero(self):
        m = compute_metrics(np.array([0, 0]), np.array([0, 0]))
        self.assertIsNone(m["precision"])
        self.assertIsNone(m["recall"])
        self.assertIsNone(m["f1"])

    def test_evaluable_scope_excludes_warmup_and_invalid(self):
        lab = pd.DataFrame({
            "y_true": [1, 1, 0, 0],
            "window_anomaly": [False, True, False, True],
            "threshold_is_warmup": [True, False, False, False],
            "threshold_is_valid": [True, True, False, True],
            "dominant_attack_type": ["UDPFlood", "UDPFlood", "", ""],
        })
        r = evaluate_windows(lab)
        self.assertEqual(r["all_windows"]["n_windows"], 4)
        self.assertEqual(r["evaluable_windows"]["n_windows"], 2)       # rows 1 and 3
        self.assertEqual(r["n_warmup_or_unevaluable_windows"], 2)
        self.assertEqual(r["per_attack_type_recall"]["UDPFlood"]["alarmed"], 1)


if __name__ == "__main__":
    unittest.main()
