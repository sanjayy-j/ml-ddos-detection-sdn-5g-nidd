"""Unit tests for M2 evaluation utilities."""

import sys
import unittest
from pathlib import Path

import numpy as np

SYS_PATH_M2 = str(Path(__file__).resolve().parent.parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

from evaluate import evaluate_predictions, assign_window_ground_truth


class TestEvaluatePredictions(unittest.TestCase):

    def test_confusion_matrix_and_metrics(self):
        result = evaluate_predictions(
            y_true=[1, 1, 0, 0],
            y_pred=[1, 0, 1, 0],
        )

        self.assertEqual(result["tp"], 1)
        self.assertEqual(result["tn"], 1)
        self.assertEqual(result["fp"], 1)
        self.assertEqual(result["fn"], 1)
        self.assertAlmostEqual(result["accuracy"], 0.5)
        self.assertAlmostEqual(result["precision"], 0.5)
        self.assertAlmostEqual(result["recall"], 0.5)
        self.assertAlmostEqual(result["f1_score"], 0.5)
        self.assertAlmostEqual(result["false_positive_rate"], 0.5)

    def test_perfect_predictions(self):
        result = evaluate_predictions([1, 1, 0, 0], [1, 1, 0, 0])

        self.assertEqual(result["tp"], 2)
        self.assertEqual(result["tn"], 2)
        self.assertEqual(result["fp"], 0)
        self.assertEqual(result["fn"], 0)
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["precision"], 1.0)
        self.assertEqual(result["recall"], 1.0)
        self.assertEqual(result["f1_score"], 1.0)
        self.assertEqual(result["false_positive_rate"], 0.0)

    def test_zero_division_is_handled(self):
        result = evaluate_predictions([0, 0], [0, 0])

        self.assertEqual(result["precision"], 0.0)
        self.assertEqual(result["recall"], 0.0)
        self.assertEqual(result["f1_score"], 0.0)
        self.assertEqual(result["false_positive_rate"], 0.0)

    def test_rejects_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            evaluate_predictions([1, 0], [1])

    def test_rejects_empty_inputs(self):
        with self.assertRaises(ValueError):
            evaluate_predictions([], [])

    def test_rejects_non_binary_values(self):
        with self.assertRaises(ValueError):
            evaluate_predictions([0, 2], [0, 1])

    def test_rejects_missing_values(self):
        with self.assertRaises(ValueError):
            evaluate_predictions([1, np.nan], [1, 0])


class TestAssignWindowGroundTruth(unittest.TestCase):

    def test_mixed_window_is_malicious(self):
        labels = np.array(["Benign", "Malicious", "Benign", "Malicious"])

        result = assign_window_ground_truth(labels, 0, 3)

        self.assertTrue(result["ground_truth_malicious"])
        self.assertEqual(result["malicious_flow_count"], 1)
        self.assertEqual(result["flow_count"], 3)
        self.assertAlmostEqual(result["malicious_fraction"], 1 / 3)

    def test_benign_window(self):
        labels = np.array(["Benign", "Benign", "Benign"])

        result = assign_window_ground_truth(labels, 0, 3)

        self.assertFalse(result["ground_truth_malicious"])
        self.assertEqual(result["malicious_flow_count"], 0)
        self.assertEqual(result["malicious_fraction"], 0.0)

    def test_uses_positional_window_range(self):
        labels = np.array(["Benign", "Benign", "Malicious", "Benign"])

        result = assign_window_ground_truth(labels, 2, 4)

        self.assertTrue(result["ground_truth_malicious"])
        self.assertEqual(result["malicious_flow_count"], 1)
        self.assertAlmostEqual(result["malicious_fraction"], 0.5)

    def test_rejects_invalid_window_range(self):
        labels = np.array(["Benign", "Malicious"])

        with self.assertRaises(ValueError):
            assign_window_ground_truth(labels, 0, 3)

    def test_rejects_missing_labels(self):
        labels = np.array(["Benign", None], dtype=object)

        with self.assertRaises(ValueError):
            assign_window_ground_truth(labels, 0, 2)


if __name__ == "__main__":
    unittest.main()
