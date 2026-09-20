"""
Unit tests for Step 5: Adaptive Baseline and Threshold Engine (M2-entropy/thresholds.py).

Covers:
- Configuration validation (ThresholdConfig)
- ThresholdResult serialization
- Mathematics: rolling median, MAD, scaled MAD, lower/upper/both thresholds, MAD floor
- Causality: temporal separation, evaluation before buffer insertion
- Warm-up behavior: suppress vs expanding policies
- Invalid values: NaN, Infinite, constant values, empty inputs
- DataFrame API: auto & explicit column selection, index preservation, immutability, voting, sessions
"""

import math
import sys
import unittest
from pathlib import Path

# Add parent directory (M2-entropy) to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from thresholds import (
    AdaptiveThresholdEngine,
    ThresholdConfig,
    ThresholdResult,
)


class TestThresholdConfig(unittest.TestCase):
    """Test suite for ThresholdConfig validation."""

    def test_default_config_valid(self):
        config = ThresholdConfig()
        self.assertEqual(config.history_len, 50)
        self.assertEqual(config.min_history, 10)
        self.assertEqual(config.k_sensitivity, 3.0)
        self.assertEqual(config.mad_floor, 1e-4)
        self.assertEqual(config.direction, "both")
        self.assertEqual(config.voting_threshold, 2)
        self.assertEqual(config.warmup_policy, "suppress")
        self.assertEqual(config.min_valid_history, 10)

    def test_custom_valid_config(self):
        config = ThresholdConfig(
            history_len=100,
            min_history=20,
            k_sensitivity=2.5,
            mad_floor=1e-3,
            direction="upper",
            voting_threshold=1,
            warmup_policy="expanding",
            min_valid_history=15,
        )
        self.assertEqual(config.history_len, 100)
        self.assertEqual(config.direction, "upper")

    def test_invalid_history_len(self):
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(history_len=0)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(history_len=-5)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(history_len="50")
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(history_len=True)

    def test_invalid_min_history(self):
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(min_history=0)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(history_len=20, min_history=25)

    def test_invalid_min_valid_history(self):
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(min_valid_history=0)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(history_len=20, min_valid_history=25)

    def test_invalid_k_sensitivity(self):
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(k_sensitivity=0.0)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(k_sensitivity=-1.5)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(k_sensitivity=float("nan"))

    def test_invalid_mad_floor(self):
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(mad_floor=0.0)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(mad_floor=-1e-4)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(mad_floor=float("nan"))

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            ThresholdConfig(direction="invalid_dir")
        with self.assertRaises(ValueError):
            ThresholdConfig(direction="UPPER")

    def test_invalid_warmup_policy(self):
        with self.assertRaises(ValueError):
            ThresholdConfig(warmup_policy="invalid_policy")

    def test_invalid_voting_threshold(self):
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(voting_threshold=0)
        with self.assertRaises((ValueError, TypeError)):
            ThresholdConfig(voting_threshold=-1)


class TestThresholdResult(unittest.TestCase):
    """Test suite for ThresholdResult serialization."""

    def test_threshold_result_defaults_and_to_dict(self):
        res = ThresholdResult(
            window_id=1,
            start_idx=0,
            end_idx=100,
            flow_count=100,
            is_warmup=False,
            is_valid=True,
            feature_alarms={"Proto_entropy_ewma": True},
            baselines={"Proto_entropy_ewma": 1.5},
            thresholds_lower={"Proto_entropy_ewma": 1.0},
            thresholds_upper={"Proto_entropy_ewma": 2.0},
            mads={"Proto_entropy_ewma": 0.1},
            feature_valid={"Proto_entropy_ewma": True},
            window_anomaly=True,
        )
        d = res.to_dict()
        self.assertEqual(d["window_id"], 1)
        self.assertEqual(d["Proto_entropy_ewma_baseline"], 1.5)
        self.assertEqual(d["Proto_entropy_ewma_threshold_lower"], 1.0)
        self.assertEqual(d["Proto_entropy_ewma_threshold_upper"], 2.0)
        self.assertEqual(d["Proto_entropy_ewma_alarm"], True)
        self.assertEqual(d["threshold_alarm_count"], 1)
        self.assertTrue(d["window_anomaly"])


class TestThresholdMath(unittest.TestCase):
    """Test suite for rolling median, MAD, scaled MAD, and thresholds."""

    def test_manual_median_and_mad_calculation(self):
        # Sequence: [10.0, 12.0, 11.0, 13.0, 14.0] -> median = 12.0
        # residual abs(val - 12) = [2.0, 0.0, 1.0, 1.0, 2.0] -> sorted = [0, 1, 1, 2, 2] -> median residual (MAD) = 1.0
        # scaled_mad = 1.4826 * 1.0 = 1.4826
        # k=3.0 -> lower = 12 - 3*1.4826 = 7.5522, upper = 12 + 3*1.4826 = 16.4478
        history = [10.0, 12.0, 11.0, 13.0, 14.0]
        config = ThresholdConfig(history_len=10, min_history=5, min_valid_history=5, k_sensitivity=3.0, voting_threshold=1)
        engine = AdaptiveThresholdEngine(config)

        # Create DataFrame with history followed by test point 17.0 (should trigger upper alarm)
        df = pd.DataFrame({"feat_ewma": history + [17.0, 5.0, 12.0]})
        out = engine.process_series(df)

        # Index 5 (6th row, value 17.0) evaluated against history [10, 12, 11, 13, 14]
        b5 = out.loc[5, "feat_ewma_baseline"]
        mad5 = out.loc[5, "feat_ewma_mad"]
        low5 = out.loc[5, "feat_ewma_threshold_lower"]
        up5 = out.loc[5, "feat_ewma_threshold_upper"]
        alarm5 = out.loc[5, "feat_ewma_alarm"]

        self.assertAlmostEqual(b5, 12.0, places=5)
        self.assertAlmostEqual(mad5, 1.0, places=5)
        self.assertAlmostEqual(low5, 12.0 - 3.0 * 1.4826 * 1.0, places=4)
        self.assertAlmostEqual(up5, 12.0 + 3.0 * 1.4826 * 1.0, places=4)
        self.assertTrue(alarm5)  # 17.0 > 16.4478 -> upper alarm

        # Index 6 (value 5.0): evaluated against history [10, 12, 11, 13, 14, 17]
        # history = [10, 11, 12, 13, 14, 17] -> median = 12.5, MAD = 1.5 -> lower_thresh = 5.8283
        alarm6 = out.loc[6, "feat_ewma_alarm"]
        self.assertTrue(alarm6)  # 5.0 < 5.8283 -> lower threshold alarm

        # Index 7 (value 12.0): normal value -> no alarm
        alarm7 = out.loc[7, "feat_ewma_alarm"]
        self.assertFalse(alarm7)

    def test_directional_detection(self):
        history = [10.0] * 10
        # Lower only
        cfg_lower = ThresholdConfig(min_history=10, direction="lower", voting_threshold=1)
        eng_lower = AdaptiveThresholdEngine(cfg_lower)
        df = pd.DataFrame({"f_ewma": history + [100.0, 0.0]})  # 100 is high, 0 is low
        out_lower = eng_lower.process_series(df)
        self.assertFalse(out_lower.loc[10, "f_ewma_alarm"])  # 100 > upper, but direction is lower -> no alarm
        self.assertTrue(out_lower.loc[11, "f_ewma_alarm"])   # 0 < lower -> alarm

        # Upper only
        cfg_upper = ThresholdConfig(min_history=10, direction="upper", voting_threshold=1)
        eng_upper = AdaptiveThresholdEngine(cfg_upper)
        out_upper = eng_upper.process_series(df)
        self.assertTrue(out_upper.loc[10, "f_ewma_alarm"])   # 100 > upper -> alarm
        self.assertFalse(out_upper.loc[11, "f_ewma_alarm"])  # 0 < lower, but direction is upper -> no alarm

    def test_strict_inequality(self):
        history = [10.0] * 10
        cfg = ThresholdConfig(min_history=10, mad_floor=1.0, k_sensitivity=2.0, direction="both", voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        # baseline = 10, mad = 0 -> scaled_mad = 1.4826 * 1.0 = 1.4826 -> upper = 10 + 2*1.4826 = 12.9652
        df = pd.DataFrame({"f_ewma": history + [12.9652]})
        out = eng.process_series(df)
        # 12.9652 is equal to upper_thresh -> strict inequality (val > upper_thresh) must evaluate to False
        self.assertFalse(out.loc[10, "f_ewma_alarm"])

    def test_mad_floor_zero_variability(self):
        # Constant history of 5.0 -> raw MAD = 0.0
        history = [5.0] * 15
        cfg = ThresholdConfig(min_history=10, mad_floor=1e-3, k_sensitivity=3.0, voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        df = pd.DataFrame({"f_ewma": history + [5.001, 6.0]})
        out = eng.process_series(df)
        
        # Raw MAD at row 10 should be 0.0, but scaled MAD uses max(0.0, 1e-3) = 1e-3
        self.assertEqual(out.loc[10, "f_ewma_mad"], 0.0)
        expected_upper = 5.0 + 3.0 * (1.4826 * 1e-3)
        self.assertAlmostEqual(out.loc[10, "f_ewma_threshold_upper"], expected_upper, places=6)
        self.assertFalse(out.loc[10, "f_ewma_alarm"])  # 5.001 is within threshold
        self.assertTrue(out.loc[16, "f_ewma_alarm"])   # 6.0 at row 16 triggers alarm


class TestThresholdCausality(unittest.TestCase):
    """Test suite ensuring strict temporal causality."""

    def test_current_value_not_in_own_baseline(self):
        # 10 rows of 1.0
        history = [1.0] * 10
        cfg = ThresholdConfig(min_history=10, voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        # Row 10 has a massive spike 1000.0
        df = pd.DataFrame({"f_ewma": history + [1000.0, 1.0]})
        out = eng.process_series(df)

        # Baseline at row 10 must be 1.0 (from rows 0..9), NOT influenced by 1000.0
        self.assertEqual(out.loc[10, "f_ewma_baseline"], 1.0)
        self.assertTrue(out.loc[10, "f_ewma_alarm"])

        # Row 11 has history containing 1000.0 -> baseline median of [1.0*10, 1000.0] is still 1.0
        self.assertEqual(out.loc[11, "f_ewma_baseline"], 1.0)
        self.assertFalse(out.loc[11, "f_ewma_alarm"])


class TestThresholdWarmup(unittest.TestCase):
    """Test suite for warm-up policies."""

    def test_suppress_warmup_policy(self):
        cfg = ThresholdConfig(history_len=20, min_history=10, min_valid_history=10, warmup_policy="suppress", voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        df = pd.DataFrame({"f_ewma": [5.0] * 15})
        out = eng.process_series(df)

        # Rows 0..9 are in warm-up phase
        for i in range(10):
            self.assertTrue(out.loc[i, "threshold_is_warmup"])
            self.assertTrue(np.isnan(out.loc[i, "f_ewma_baseline"]))
            self.assertFalse(out.loc[i, "f_ewma_alarm"])
            self.assertFalse(out.loc[i, "window_anomaly"])

        # Row 10 onwards is out of warm-up phase
        for i in range(10, 15):
            self.assertFalse(out.loc[i, "threshold_is_warmup"])
            self.assertEqual(out.loc[i, "f_ewma_baseline"], 5.0)

    def test_expanding_warmup_policy(self):
        cfg = ThresholdConfig(
            history_len=20,
            min_history=10,
            min_valid_history=5,
            warmup_policy="expanding",
            voting_threshold=1,
        )
        eng = AdaptiveThresholdEngine(cfg)
        df = pd.DataFrame({"f_ewma": [5.0] * 15})
        out = eng.process_series(df)

        # Rows 0..4 have < 5 valid observations -> warm-up, NaN baselines
        for i in range(5):
            self.assertTrue(np.isnan(out.loc[i, "f_ewma_baseline"]))

        # Rows 5..9 have >= 5 valid observations -> expanding baselines computed
        for i in range(5, 15):
            self.assertEqual(out.loc[i, "f_ewma_baseline"], 5.0)


class TestThresholdInvalidValues(unittest.TestCase):
    """Test suite for invalid (NaN, Infinite) value handling."""

    def test_nan_and_inf_in_current_and_history(self):
        cfg = ThresholdConfig(min_history=5, min_valid_history=5, voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)

        # History with valid values plus NaN and Inf interspersed
        data = [10.0, np.nan, 10.0, np.inf, 10.0, -np.inf, 10.0, 10.0, np.nan, 100.0]
        df = pd.DataFrame({"f_ewma": data})
        out = eng.process_series(df)

        # Invalid rows should be marked threshold_is_valid = False
        self.assertFalse(out.loc[1, "threshold_is_valid"])
        self.assertFalse(out.loc[3, "threshold_is_valid"])
        self.assertFalse(out.loc[5, "threshold_is_valid"])
        self.assertFalse(out.loc[8, "threshold_is_valid"])

        # Row 9 (value 100.0): should have 5 valid historical observations (rows 0, 2, 4, 6, 7)
        self.assertTrue(out.loc[9, "threshold_is_valid"])
        self.assertFalse(out.loc[9, "threshold_is_warmup"])
        self.assertEqual(out.loc[9, "f_ewma_baseline"], 10.0)
        self.assertTrue(out.loc[9, "f_ewma_alarm"])

    def test_empty_dataframe(self):
        cfg = ThresholdConfig(voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        df = pd.DataFrame({"f_ewma": pd.Series(dtype=float), "window_id": pd.Series(dtype=int)})
        out = eng.process_series(df)

        self.assertEqual(len(out), 0)
        self.assertIn("f_ewma_baseline", out.columns)
        self.assertIn("window_anomaly", out.columns)


class TestAdaptiveThresholdEngineDataFrame(unittest.TestCase):
    """Test suite for DataFrame processing, column selection, consensus, and session boundary resets."""

    def test_auto_column_selection(self):
        df = pd.DataFrame({
            "window_id": [0, 1],
            "Proto_entropy_ewma": [1.0, 2.0],
            "State_entropy": [0.5, 0.6],
            "ignored_col": [10, 20],
        })
        cfg = ThresholdConfig(min_history=1, min_valid_history=1, voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        out = eng.process_series(df)

        self.assertIn("Proto_entropy_ewma_baseline", out.columns)
        self.assertIn("State_entropy_baseline", out.columns)
        self.assertNotIn("ignored_col_baseline", out.columns)

    def test_explicit_column_selection(self):
        df = pd.DataFrame({
            "col_a": [1.0, 2.0, 3.0],
            "col_b": [4.0, 5.0, 6.0],
        })
        cfg = ThresholdConfig(min_history=1, min_valid_history=1, voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        out = eng.process_series(df, entropy_columns=["col_a"])

        self.assertIn("col_a_baseline", out.columns)
        self.assertNotIn("col_b_baseline", out.columns)

    def test_missing_and_non_numeric_columns(self):
        df = pd.DataFrame({"col_a": ["str1", "str2"]})
        cfg = ThresholdConfig(voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)

        with self.assertRaises(KeyError):
            eng.process_series(df, entropy_columns=["missing_col"])

        with self.assertRaises(TypeError):
            eng.process_series(df, entropy_columns=["col_a"])

    def test_input_immutability_and_index_preservation(self):
        df = pd.DataFrame(
            {"f_ewma": [1.0, 2.0, 3.0]},
            index=["row_a", "row_b", "row_c"],
        )
        df_copy = df.copy()
        cfg = ThresholdConfig(min_history=1, min_valid_history=1, voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        out = eng.process_series(df)

        # Original DataFrame must not be mutated
        pd.testing.assert_frame_equal(df, df_copy)
        # Output DataFrame index must match input index
        self.assertListEqual(list(out.index), ["row_a", "row_b", "row_c"])

    def test_multi_feature_consensus_voting(self):
        df = pd.DataFrame({
            "f1_ewma": [10.0] * 10 + [100.0],
            "f2_ewma": [10.0] * 10 + [100.0],
            "f3_ewma": [10.0] * 10 + [10.0],  # f3 normal
        })
        # Requires 2 alarms for window anomaly
        cfg = ThresholdConfig(min_history=10, voting_threshold=2)
        eng = AdaptiveThresholdEngine(cfg)
        out = eng.process_series(df)

        self.assertTrue(out.loc[10, "f1_ewma_alarm"])
        self.assertTrue(out.loc[10, "f2_ewma_alarm"])
        self.assertFalse(out.loc[10, "f3_ewma_alarm"])
        self.assertEqual(out.loc[10, "threshold_alarm_count"], 2)
        self.assertTrue(out.loc[10, "window_anomaly"])

    def test_insufficient_features_for_voting_threshold_error(self):
        df = pd.DataFrame({"f1_ewma": [1.0, 2.0]})
        cfg = ThresholdConfig(voting_threshold=3)
        eng = AdaptiveThresholdEngine(cfg)

        with self.assertRaises(ValueError):
            eng.process_series(df)

    def test_session_boundary_history_reset(self):
        df = pd.DataFrame({
            "session_id": [1] * 12 + [2] * 10,
            "f_ewma": [10.0] * 22,
        })
        cfg = ThresholdConfig(min_history=10, voting_threshold=1)
        eng = AdaptiveThresholdEngine(cfg)
        out = eng.process_series(df)

        # In session 1, row 10 is out of warm-up
        self.assertFalse(out.loc[10, "threshold_is_warmup"])

        # Row 12 is the start of session 2 -> history buffer resets!
        # Rows 12..21 in session 2 are back in warm-up phase (0..9 valid items in new session)
        self.assertTrue(out.loc[12, "threshold_is_warmup"])
        self.assertTrue(out.loc[21, "threshold_is_warmup"])


if __name__ == "__main__":
    unittest.main()
