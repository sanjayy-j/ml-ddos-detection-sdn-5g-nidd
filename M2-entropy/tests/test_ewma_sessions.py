"""Tests for session-aware EWMA (state must never leak across session boundaries)."""

import sys
import unittest
from pathlib import Path

SYS_PATH_M2 = str(Path(__file__).resolve().parent.parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import numpy as np
import pandas as pd

from ewma import ewma, smooth_entropy_dataframe


def _manual(values, alpha):
    out, s = [], None
    for v in values:
        s = v if s is None else alpha * v + (1 - alpha) * s
        out.append(s)
    return out


class TestSessionAwareEwma(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "session_id": [1, 1, 1, 2, 2, 2],
            "X_entropy": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0],
        })

    def test_state_resets_at_session_boundary(self):
        out = smooth_entropy_dataframe(self.df, alpha=0.5)
        expected = _manual([1.0, 2.0, 3.0], 0.5) + _manual([10.0, 20.0, 30.0], 0.5)
        np.testing.assert_allclose(out["X_entropy_ewma"].to_numpy(), expected)
        # first window of session 2 equals its own raw value, not a blend with session 1
        self.assertEqual(out["X_entropy_ewma"].iloc[3], 10.0)

    def test_explicit_session_col(self):
        df = self.df.rename(columns={"session_id": "capture"})
        out = smooth_entropy_dataframe(df, alpha=0.5, session_col="capture")
        self.assertEqual(out["X_entropy_ewma"].iloc[3], 10.0)

    def test_missing_explicit_session_col_raises(self):
        with self.assertRaises(KeyError):
            smooth_entropy_dataframe(self.df, alpha=0.5, session_col="nope")

    def test_all_null_session_column_is_single_block(self):
        df = self.df.copy()
        df["session_id"] = None
        out = smooth_entropy_dataframe(df, alpha=0.5)
        np.testing.assert_allclose(out["X_entropy_ewma"].to_numpy(), _manual(df["X_entropy"].tolist(), 0.5))

    def test_initial_applies_to_each_session_start(self):
        out = smooth_entropy_dataframe(self.df, alpha=0.5, initial=0.0)
        self.assertEqual(out["X_entropy_ewma"].iloc[0], 0.0)
        self.assertEqual(out["X_entropy_ewma"].iloc[3], 0.0)

    def test_non_contiguous_repeat_of_session_value_is_new_block(self):
        df = pd.DataFrame({"session_id": [1, 1, 2, 2, 1, 1], "X_entropy": [1.0, 1.0, 9.0, 9.0, 5.0, 5.0]})
        out = smooth_entropy_dataframe(df, alpha=0.5)
        self.assertEqual(out["X_entropy_ewma"].iloc[4], 5.0)  # fresh state, not carried from block 2

    def test_row_order_and_index_preserved(self):
        df = self.df.copy()
        df.index = [10, 11, 12, 13, 14, 15]
        out = smooth_entropy_dataframe(df, alpha=0.3)
        self.assertEqual(list(out.index), [10, 11, 12, 13, 14, 15])

    def test_no_session_column_matches_plain_ewma(self):
        df = pd.DataFrame({"X_entropy": [1.0, 4.0, 2.0]})
        out = smooth_entropy_dataframe(df, alpha=0.4)
        self.assertEqual(out["X_entropy_ewma"].tolist(), ewma([1.0, 4.0, 2.0], 0.4))


class TestNanPolicy(unittest.TestCase):
    def test_default_still_raises_on_nan(self):
        with self.assertRaises(ValueError):
            smooth_entropy_dataframe(pd.DataFrame({"X_entropy": [1.0, np.nan, 2.0]}), alpha=0.5)

    def test_hold_keeps_nan_and_holds_state(self):
        df = pd.DataFrame({"X_entropy": [2.0, np.nan, 4.0]})
        out = smooth_entropy_dataframe(df, alpha=0.5, nan_policy="hold")["X_entropy_ewma"].tolist()
        self.assertEqual(out[0], 2.0)
        self.assertTrue(np.isnan(out[1]))
        self.assertEqual(out[2], 0.5 * 4.0 + 0.5 * 2.0)  # continues from held state

    def test_hold_leading_nan_initialises_on_first_valid(self):
        df = pd.DataFrame({"X_entropy": [np.nan, 3.0, 5.0]})
        out = smooth_entropy_dataframe(df, alpha=0.5, nan_policy="hold")["X_entropy_ewma"].tolist()
        self.assertTrue(np.isnan(out[0]))
        self.assertEqual(out[1], 3.0)
        self.assertEqual(out[2], 4.0)

    def test_hold_does_not_carry_state_over_session_boundary(self):
        df = pd.DataFrame({"session_id": [1, 1, 2, 2], "X_entropy": [2.0, 2.0, np.nan, 8.0]})
        out = smooth_entropy_dataframe(df, alpha=0.5, nan_policy="hold")["X_entropy_ewma"].tolist()
        self.assertEqual(out[3], 8.0)

    def test_invalid_policy(self):
        with self.assertRaises(ValueError):
            smooth_entropy_dataframe(pd.DataFrame({"X_entropy": [1.0]}), alpha=0.5, nan_policy="x")


if __name__ == "__main__":
    unittest.main()
