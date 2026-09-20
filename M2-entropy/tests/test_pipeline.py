"""
Unit tests for Step 6A: End-to-End Offline Pipeline Integration (M2-entropy/pipeline.py).

Covers:
- Successful end-to-end execution on synthetic flow datasets
- Metadata and feature column presence in output DataFrame
- Raw entropy and EWMA column generation and naming
- Adaptive threshold output columns and boolean anomaly decisions
- Strict label isolation (detector does not consume Label or Attack Type)
- Input DataFrame immutability
- Configurable window_size, step_size, alpha, and threshold settings
- Graceful handling of insufficient data (DataFrame smaller than window size)
- Completely self-contained execution (no external CSV required)
"""

import sys
import unittest
from pathlib import Path

# Add parent directory (M2-entropy) to sys.path
SYS_PATH_M2 = str(Path(__file__).resolve().parent.parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import numpy as np
import pandas as pd

from pipeline import PipelineConfig, PipelineResult, run_entropy_pipeline
from thresholds import ThresholdConfig


class TestPipelineIntegration(unittest.TestCase):
    """Test suite for end-to-end M2 offline entropy detection pipeline."""

    def setUp(self):
        """Generate a small synthetic flow dataset for testing."""
        np.random.seed(42)
        n_rows = 500
        self.synthetic_df = pd.DataFrame({
            "Proto": np.random.choice(["tcp", "udp", "icmp"], size=n_rows),
            "State": np.random.choice(["CON", "FIN", "INT", "REQ"], size=n_rows),
            "sTtl": np.random.choice([64, 128, 255], size=n_rows),
            "sDSb": np.random.choice([0, 8, 16], size=n_rows),
            "TotPkts": np.random.randint(1, 100, size=n_rows),
            "TotBytes": np.random.randint(64, 10000, size=n_rows),
            "Rate": np.random.uniform(1.0, 500.0, size=n_rows),
            "Dur": np.random.uniform(0.01, 2.0, size=n_rows),
            "Label": np.random.choice([0, 1], size=n_rows, p=[0.9, 0.1]),
            "Attack Type": np.random.choice(["Benign", "UDP-Flood"], size=n_rows, p=[0.9, 0.1]),
            "Attack Tool": np.random.choice(["None", "hping3"], size=n_rows, p=[0.9, 0.1]),
        })

    def test_pipeline_execution_synthetic_data(self):
        cfg = PipelineConfig(
            df=self.synthetic_df,
            window_size=100,
            step_size=50,
            alpha=0.2,
            threshold_config=ThresholdConfig(min_history=5, min_valid_history=5, voting_threshold=2),
        )
        res = run_entropy_pipeline(cfg)

        self.assertIsInstance(res, PipelineResult)
        self.assertEqual(res.input_row_count, 500)
        self.assertGreater(res.number_of_windows, 0)
        self.assertIsInstance(res.output_df, pd.DataFrame)
        self.assertGreater(len(res.output_df), 0)

    def test_expected_metadata_and_column_structure(self):
        cfg = PipelineConfig(
            df=self.synthetic_df,
            window_size=100,
            step_size=50,
            threshold_config=ThresholdConfig(min_history=5, min_valid_history=5, voting_threshold=2),
        )
        res = run_entropy_pipeline(cfg)
        out = res.output_df

        # Verify metadata columns
        expected_meta = ["window_id", "start_idx", "end_idx", "flow_count", "is_complete"]
        for col in expected_meta:
            self.assertIn(col, out.columns)

        # Verify overall threshold columns
        expected_thresh_meta = ["threshold_is_warmup", "threshold_is_valid", "threshold_alarm_count", "window_anomaly"]
        for col in expected_thresh_meta:
            self.assertIn(col, out.columns)

        # Verify raw entropy and EWMA columns exist
        self.assertGreater(len(res.entropy_columns), 0)
        self.assertGreater(len(res.ewma_columns), 0)
        for c in res.entropy_columns:
            self.assertIn(c, out.columns)
        for c in res.ewma_columns:
            self.assertIn(c, out.columns)

        # Verify per-feature threshold output columns exist
        for ewma_col in res.ewma_columns:
            self.assertIn(f"{ewma_col}_baseline", out.columns)
            self.assertIn(f"{ewma_col}_mad", out.columns)
            self.assertIn(f"{ewma_col}_threshold_lower", out.columns)
            self.assertIn(f"{ewma_col}_threshold_upper", out.columns)
            self.assertIn(f"{ewma_col}_alarm", out.columns)
            self.assertIn(f"{ewma_col}_valid", out.columns)

    def test_anomaly_output_is_boolean(self):
        cfg = PipelineConfig(
            df=self.synthetic_df,
            window_size=100,
            step_size=50,
            threshold_config=ThresholdConfig(min_history=2, min_valid_history=2, voting_threshold=1),
        )
        res = run_entropy_pipeline(cfg)
        out = res.output_df

        self.assertIn(out["window_anomaly"].dtype, [bool, np.dtype("bool")])
        self.assertIn(out["threshold_is_warmup"].dtype, [bool, np.dtype("bool")])
        self.assertIn(out["threshold_is_valid"].dtype, [bool, np.dtype("bool")])

    def test_strict_label_isolation(self):
        """Verify ground-truth labels (Label, Attack Type, Attack Tool) are NEVER used in detector."""
        cfg = PipelineConfig(
            df=self.synthetic_df,
            window_size=100,
            step_size=50,
            threshold_config=ThresholdConfig(min_history=2, min_valid_history=2, voting_threshold=1),
        )
        res = run_entropy_pipeline(cfg)
        out = res.output_df

        # Label, Attack Type, Attack Tool must never enter entropy features or alarms
        for label_col in ["Label", "Attack Type", "Attack Tool"]:
            self.assertNotIn(f"{label_col}_entropy", out.columns)
            self.assertNotIn(f"{label_col}_entropy_ewma", out.columns)
            self.assertNotIn(f"{label_col}_alarm", out.columns)
            self.assertNotIn(f"{label_col}_entropy_ewma_alarm", out.columns)

    def test_input_dataframe_immutability(self):
        df_copy = self.synthetic_df.copy()
        cfg = PipelineConfig(
            df=self.synthetic_df,
            window_size=100,
            step_size=50,
            threshold_config=ThresholdConfig(min_history=2, min_valid_history=2, voting_threshold=1),
        )
        run_entropy_pipeline(cfg)

        # Original DataFrame must remain unmutated
        pd.testing.assert_frame_equal(self.synthetic_df, df_copy)

    def test_configurable_window_and_step_size(self):
        cfg1 = PipelineConfig(
            df=self.synthetic_df,
            window_size=100,
            step_size=50,
            drop_incomplete=True,
            threshold_config=ThresholdConfig(min_history=2, min_valid_history=2, voting_threshold=1),
        )
        res1 = run_entropy_pipeline(cfg1)
        # 500 rows, W=100, S=50 -> complete windows at pos 0, 50, 100, 150, 200, 250, 300, 350, 400 -> 9 windows
        self.assertEqual(res1.number_of_windows, 9)

        cfg2 = PipelineConfig(
            df=self.synthetic_df,
            window_size=200,
            step_size=100,
            drop_incomplete=True,
            threshold_config=ThresholdConfig(min_history=2, min_valid_history=2, voting_threshold=1),
        )
        res2 = run_entropy_pipeline(cfg2)
        # 500 rows, W=200, S=100 -> complete windows at pos 0, 100, 200, 300 -> 4 windows
        self.assertEqual(res2.number_of_windows, 4)

    def test_insufficient_data_handling(self):
        small_df = self.synthetic_df.iloc[:20].copy()
        cfg = PipelineConfig(
            df=small_df,
            window_size=100,
            step_size=50,
            drop_incomplete=True,
            threshold_config=ThresholdConfig(min_history=2, min_valid_history=2, voting_threshold=1),
        )
        res = run_entropy_pipeline(cfg)

        self.assertEqual(res.input_row_count, 20)
        self.assertEqual(res.number_of_windows, 0)
        self.assertEqual(len(res.output_df), 0)


if __name__ == "__main__":
    unittest.main()
