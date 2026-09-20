"""
Unit tests for Exponentially Weighted Moving Average (EWMA) module in M2-entropy/ewma.py.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory (M2-entropy) to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ewma import ewma, smooth_entropy_dataframe

try:
    import numpy as np
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class TestEWMA(unittest.TestCase):
    """Test suite for ewma and smooth_entropy_dataframe."""

    def test_known_manual_ewma_sequence(self):
        """Test EWMA against a manually calculated reference sequence.

        Values: [1.0, 2.0, 3.0], alpha = 0.5, initial = None
        s[0] = 1.0
        s[1] = 0.5 * 2.0 + 0.5 * 1.0 = 1.5
        s[2] = 0.5 * 3.0 + 0.5 * 1.5 = 2.25
        """
        values = [1.0, 2.0, 3.0]
        res = ewma(values, alpha=0.5)
        self.assertEqual(res, [1.0, 1.5, 2.25])

    def test_alpha_one_exact_tracking(self):
        """Test alpha = 1.0 results in exact sequence tracking (no smoothing)."""
        values = [1.5, 2.8, 0.4, 3.1]
        res = ewma(values, alpha=1.0)
        self.assertEqual(res, values)

    def test_low_alpha_heavy_smoothing(self):
        """Test low alpha (e.g., 0.1) filters noise and heavily smooths sequence."""
        values = [10.0, 0.0, 10.0, 0.0]
        res = ewma(values, alpha=0.1)
        # s[0] = 10.0
        # s[1] = 0.1*0 + 0.9*10 = 9.0
        # s[2] = 0.1*10 + 0.9*9 = 9.1
        # s[3] = 0.1*0 + 0.9*9.1 = 8.19
        self.assertEqual(len(res), 4)
        self.assertAlmostEqual(res[1], 9.0, places=7)
        self.assertAlmostEqual(res[2], 9.1, places=7)
        self.assertAlmostEqual(res[3], 8.19, places=7)

    def test_invalid_alpha_values(self):
        """Test invalid alpha values raise ValueError or TypeError."""
        # alpha = 0
        with self.assertRaises(ValueError):
            ewma([1.0, 2.0], alpha=0.0)

        # negative alpha
        with self.assertRaises(ValueError):
            ewma([1.0, 2.0], alpha=-0.5)

        # alpha > 1.0
        with self.assertRaises(ValueError):
            ewma([1.0, 2.0], alpha=1.5)

        # non-numeric alpha
        with self.assertRaises(TypeError):
            ewma([1.0, 2.0], alpha="0.5")  # type: ignore

        with self.assertRaises(TypeError):
            ewma([1.0, 2.0], alpha=True)  # type: ignore

    def test_empty_input(self):
        """Test handling of empty sequence input."""
        res_list = ewma([], alpha=0.5)
        self.assertEqual(res_list, [])

        if HAS_PANDAS:
            res_arr = ewma(np.array([]), alpha=0.5)
            self.assertEqual(len(res_arr), 0)

            res_ser = ewma(pd.Series([]), alpha=0.5)
            self.assertEqual(len(res_ser), 0)

    def test_single_value_input(self):
        """Test single-value sequence input."""
        res = ewma([5.5], alpha=0.3)
        self.assertEqual(res, [5.5])

    def test_explicit_initial_value(self):
        """Test explicit initial value parameter.

        Values: [2.0, 4.0], alpha = 0.5, initial = 1.0
        s[0] = 1.0
        s[1] = 0.5 * 4.0 + 0.5 * 1.0 = 2.5
        """
        values = [2.0, 4.0]
        res = ewma(values, alpha=0.5, initial=1.0)
        self.assertEqual(res, [1.0, 2.5])

    def test_list_numpy_and_pandas_inputs(self):
        """Test input compatibility with list, NumPy array, and pandas Series."""
        values_list = [1.0, 2.0, 3.0]
        res_list = ewma(values_list, alpha=0.5)
        self.assertIsInstance(res_list, list)

        if HAS_PANDAS:
            arr = np.array([1.0, 2.0, 3.0])
            res_arr = ewma(arr, alpha=0.5)
            self.assertIsInstance(res_arr, np.ndarray)
            self.assertTrue(np.allclose(res_arr, np.array([1.0, 1.5, 2.25])))

            ser = pd.Series([1.0, 2.0, 3.0], index=[10, 20, 30], name="test_entropy")
            res_ser = ewma(ser, alpha=0.5)
            self.assertIsInstance(res_ser, pd.Series)
            self.assertEqual(list(res_ser.index), [10, 20, 30])
            self.assertEqual(res_ser.name, "test_entropy")

    def test_non_numeric_input_raises_type_error(self):
        """Test that non-numeric sequence elements raise TypeError."""
        with self.assertRaises(TypeError):
            ewma(["a", "b", "c"], alpha=0.5)

        with self.assertRaises(TypeError):
            ewma([1.0, "invalid", 3.0], alpha=0.5)

    def test_input_immutability(self):
        """Test that ewma does not mutate the original input list or array."""
        orig_list = [1.0, 2.0, 3.0]
        copy_list = list(orig_list)
        ewma(orig_list, alpha=0.5)
        self.assertEqual(orig_list, copy_list)

        if HAS_PANDAS:
            orig_arr = np.array([1.0, 2.0, 3.0])
            copy_arr = orig_arr.copy()
            ewma(orig_arr, alpha=0.5)
            self.assertTrue(np.array_equal(orig_arr, copy_arr))

    def test_smooth_entropy_dataframe_automatic_columns(self):
        """Test automatic selection of '_entropy' columns in smooth_entropy_dataframe."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")

        df = pd.DataFrame(
            {
                "window_id": [0, 1, 2],
                "start_idx": [0, 10, 20],
                "end_idx": [10, 20, 30],
                "flow_count": [10, 10, 10],
                "is_complete": [True, True, True],
                "session_id": [0, 0, 0],
                "Proto_entropy": [1.0, 2.0, 3.0],
                "State_entropy": [2.0, 4.0, 6.0],
            },
            index=[100, 101, 102],
        )

        res_df = smooth_entropy_dataframe(df, alpha=0.5)
        self.assertIn("Proto_entropy_ewma", res_df.columns)
        self.assertIn("State_entropy_ewma", res_df.columns)
        self.assertEqual(list(res_df.index), [100, 101, 102])
        self.assertEqual(list(res_df["Proto_entropy_ewma"]), [1.0, 1.5, 2.25])
        self.assertEqual(list(res_df["State_entropy_ewma"]), [2.0, 3.0, 4.5])

        # Verify metadata columns were preserved without accidental smoothing
        self.assertNotIn("window_id_ewma", res_df.columns)
        self.assertNotIn("flow_count_ewma", res_df.columns)

    def test_smooth_entropy_dataframe_explicit_columns(self):
        """Test smooth_entropy_dataframe with explicit entropy_columns selection."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")

        df = pd.DataFrame(
            {
                "window_id": [0, 1],
                "Proto_entropy": [1.0, 2.0],
                "State_entropy": [4.0, 8.0],
            }
        )

        res_df = smooth_entropy_dataframe(df, alpha=0.5, entropy_columns=["Proto_entropy"])
        self.assertIn("Proto_entropy_ewma", res_df.columns)
        self.assertNotIn("State_entropy_ewma", res_df.columns)

    def test_smooth_entropy_dataframe_missing_and_non_numeric_columns(self):
        """Test KeyError on missing requested column and TypeError on non-numeric column."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")

        df = pd.DataFrame(
            {
                "Proto_entropy": [1.0, 2.0],
                "Text_col": ["a", "b"],
            }
        )

        with self.assertRaises(KeyError):
            smooth_entropy_dataframe(df, alpha=0.5, entropy_columns=["NonExistent_entropy"])

        with self.assertRaises(TypeError):
            smooth_entropy_dataframe(df, alpha=0.5, entropy_columns=["Text_col"])

    def test_smooth_entropy_dataframe_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")

        df_empty = pd.DataFrame(columns=["window_id", "Proto_entropy"])
        res_df = smooth_entropy_dataframe(df_empty, alpha=0.5)

        self.assertEqual(len(res_df), 0)
        self.assertIn("Proto_entropy_ewma", res_df.columns)

    def test_smooth_entropy_dataframe_immutability(self):
        """Test that smooth_entropy_dataframe does not mutate the original DataFrame."""
        if not HAS_PANDAS:
            self.skipTest("pandas required")

        df = pd.DataFrame({"Proto_entropy": [1.0, 2.0, 3.0]})
        df_copy = df.copy()
        smooth_entropy_dataframe(df, alpha=0.5)
        pd.testing.assert_frame_equal(df, df_copy)


if __name__ == "__main__":
    unittest.main()
