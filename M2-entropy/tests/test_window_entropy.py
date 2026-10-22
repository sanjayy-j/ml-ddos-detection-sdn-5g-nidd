"""
Unit tests for Window-Level Entropy Computation Module in M2-entropy/window_entropy.py.
"""

import math
import sys
import unittest
from pathlib import Path

# Add parent directory (M2-entropy) to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from window_entropy import (
    WindowEntropyResult,
    compute_entropy_over_windows,
    compute_window_entropy,
)
from windowing import FlowWindow, slice_flow_windows

try:
    import numpy as np
    import pandas as pd
    from features import FeatureConfig
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class TestWindowEntropy(unittest.TestCase):
    """Test suite for compute_window_entropy and compute_entropy_over_windows."""

    def setUp(self):
        """Create sample DataFrame and FlowWindow fixtures for testing."""
        if HAS_PANDAS:
            self.df_sample = pd.DataFrame(
                {
                    "Proto": ["tcp", "udp", "tcp", "icmp", "udp", "tcp", "udp", "tcp"],
                    "State": ["REQ", "INT", "CON", "FIN", "REQ", "REQ", "REQ", "REQ"],
                    "sTtl": [64, 64, 64, 64, 64, 64, 64, 64],  # Constant -> entropy 0
                    "sDSb": ["CS0", "CS0", "EF", "CS0", "CS0", "CS0", "CS0", "CS0"],
                    "TotPkts": [1, 5, 20, 100, 1, 2, 1, 1],
                    "TotBytes": [42, 500, 1500, 60000, 42, 84, 42, 42],
                    "Rate": [0.0, 12.5, 400.0, 15000.0, 1.2, 2.5, 1.0, 0.5],
                    "Dur": [0.0, 0.5, 2.3, 10.1, 0.1, 0.2, 0.1, 0.1],
                    "Label": ["Benign", "Malicious", "Benign", "Malicious", "Benign", "Malicious", "Benign", "Malicious"],
                    "Attack Type": ["Benign", "UDPFlood", "Benign", "SYNFlood", "Benign", "UDPFlood", "Benign", "UDPFlood"],
                },
                index=range(10, 18),
            )
            self.windows = slice_flow_windows(self.df_sample, window_size=4, step_size=4)

    def test_single_window_categorical_features(self):
        """Test entropy calculation on a single FlowWindow with categorical features."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        config = FeatureConfig(categorical_cols=["Proto", "State"], numerical_cols=[])
        win_res = compute_window_entropy(self.windows[0], feature_config=config)

        self.assertIsInstance(win_res, WindowEntropyResult)
        self.assertEqual(win_res.window_id, 0)
        self.assertEqual((win_res.start_idx, win_res.end_idx), (0, 4))
        self.assertEqual(win_res.flow_count, 4)
        self.assertTrue(win_res.is_complete)

        # Window 0 Proto: ["tcp", "udp", "tcp", "icmp"] -> 4 items, 3 categories: tcp (2), udp (1), icmp (1)
        # H = - (0.5 * log2(0.5) + 0.25 * log2(0.25) + 0.25 * log2(0.25)) = 1.5 bits
        self.assertIn("Proto_entropy", win_res.entropy_scores)
        self.assertAlmostEqual(win_res.entropy_scores["Proto_entropy"], 1.5, places=7)

    def test_single_unique_category_results_in_zero_entropy(self):
        """Test that constant value in window produces exactly 0.0 entropy."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        config = FeatureConfig(categorical_cols=["sTtl"], numerical_cols=[])
        win_res = compute_window_entropy(self.windows[0], feature_config=config)
        self.assertEqual(win_res.entropy_scores["sTtl_entropy"], 0.0)

    def test_numerical_binned_features(self):
        """Test entropy calculation on discretized numerical features."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        config = FeatureConfig(categorical_cols=[], numerical_cols=["TotPkts"], n_bins=3)
        win_res = compute_window_entropy(self.windows[0], feature_config=config)

        self.assertIn("TotPkts_bin_entropy", win_res.entropy_scores)
        self.assertGreaterEqual(win_res.entropy_scores["TotPkts_bin_entropy"], 0.0)

    def test_multiple_windows_computation(self):
        """Test computing entropy across multiple windows."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        config = FeatureConfig(categorical_cols=["Proto", "State"], numerical_cols=[])
        results = compute_entropy_over_windows(self.windows, feature_config=config)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].window_id, 0)
        self.assertEqual(results[1].window_id, 1)

        # Window 1 State: ["REQ", "REQ", "REQ", "REQ"] -> constant -> entropy 0.0
        self.assertEqual(results[1].entropy_scores["State_entropy"], 0.0)

    def test_as_dataframe_option(self):
        """Test returning results as a pandas DataFrame."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        config = FeatureConfig(categorical_cols=["Proto"], numerical_cols=[])
        df_res = compute_entropy_over_windows(self.windows, feature_config=config, as_dataframe=True)

        self.assertIsInstance(df_res, pd.DataFrame)
        self.assertEqual(len(df_res), 2)
        self.assertIn("window_id", df_res.columns)
        self.assertIn("Proto_entropy", df_res.columns)
        self.assertEqual(list(df_res["window_id"]), [0, 1])

    def test_empty_window_collection(self):
        """Test behavior when passing an empty collection of windows."""
        results = compute_entropy_over_windows([], as_dataframe=False)
        self.assertEqual(len(results), 0)

        if HAS_PANDAS:
            df_empty = compute_entropy_over_windows([], as_dataframe=True)
            self.assertEqual(len(df_empty), 0)
            self.assertIn("window_id", df_empty.columns)

    def test_preservation_of_window_metadata_and_order(self):
        """Test that window metadata and sequence order are preserved exactly."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        results = compute_entropy_over_windows(self.windows)
        for idx, res in enumerate(results):
            self.assertEqual(res.window_id, self.windows[idx].window_id)
            self.assertEqual(res.start_idx, self.windows[idx].start_idx)
            self.assertEqual(res.end_idx, self.windows[idx].end_idx)
            self.assertEqual(res.flow_count, self.windows[idx].flow_count)

    def test_different_logarithm_bases(self):
        """Test entropy calculation with custom logarithm bases (e.g., base e for nats)."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        config = FeatureConfig(categorical_cols=["Proto"], numerical_cols=[])
        res_nat = compute_window_entropy(self.windows[0], feature_config=config, base=math.e)
        res_bit = compute_window_entropy(self.windows[0], feature_config=config, base=2.0)

        # H_nat = H_bit * ln(2)
        self.assertAlmostEqual(res_nat.entropy_scores["Proto_entropy"], res_bit.entropy_scores["Proto_entropy"] * math.log(2), places=7)

    def test_excluded_columns_not_in_entropy_output(self):
        """Test that Label and Attack Type never appear in entropy output."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        config = FeatureConfig()
        win_res = compute_window_entropy(self.windows[0], feature_config=config)

        self.assertNotIn("Label_entropy", win_res.entropy_scores)
        self.assertNotIn("Attack Type_entropy", win_res.entropy_scores)

    def test_no_mutation_of_original_window_data(self):
        """Test that computing entropy does not alter original window.data."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        orig_data_copy = self.windows[0].data.copy()
        compute_window_entropy(self.windows[0])
        pd.testing.assert_frame_equal(self.windows[0].data, orig_data_copy)

    def test_empty_dataframe_window(self):
        """Test handling of a window with 0 rows."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")
        df_empty_cols = pd.DataFrame(columns=self.df_sample.columns)
        empty_win = FlowWindow(window_id=99, start_idx=0, end_idx=0, data=df_empty_cols, is_complete=False)
        res = compute_window_entropy(empty_win)

        self.assertEqual(res.window_id, 99)
        self.assertEqual(res.flow_count, 0)
        self.assertIn("Proto_entropy", res.entropy_scores)
        self.assertEqual(res.entropy_scores["Proto_entropy"], 0.0)

    def test_invalid_input_behavior(self):
        """Test TypeError raised when non-FlowWindow is passed."""
        with self.assertRaises(TypeError):
            compute_window_entropy("not_a_window")  # type: ignore


if __name__ == "__main__":
    unittest.main()
