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

    def test_session_aware_ewma_resets_at_boundaries(self):
        """EWMA must reset at session boundaries when session_col is active.

        Strategy
        --------
        Build a DataFrame with **two sessions × two windows each** (400 rows
        total, W=100, S=100, drop_incomplete=True → 4 complete windows).

        Window layout
        ~~~~~~~~~~~~~
        Rows 0-99   : session A, window A0 — Proto = all 'tcp'       → H_Proto = 0.0
        Rows 100-199: session A, window A1 — Proto = 50 'tcp'+50 'udp' → H_Proto = 1.0
        Rows 200-299: session B, window B0 — Proto = all 'udp'       → H_Proto = 0.0
        Rows 300-399: session B, window B1 — Proto = 50 'udp'+50 'icmp'→ H_Proto = 1.0

        With alpha=0.5 the expected EWMA values are:

          A0: ewma[A0] = 0.0          (first observation = raw value)
          A1: ewma[A1] = 0.5×1.0 + 0.5×0.0 = 0.5  (EWMA carry-over from A0)
          B0: ewma[B0] = 0.0          (RESET: first observation of session B)
          B1: ewma[B1] = 0.5×1.0 + 0.5×0.0 = 0.5  (EWMA carry-over from B0)

        Without a session reset, B0 would instead be:
          ewma[B0] = 0.5×0.0 + 0.5×0.5 = 0.25  ← distinguishably wrong.

        This also exercises the "session" source-column name (not 'session_id')
        to verify the column-name resolution path introduced by the bug fix.
        """
        n = 100  # rows per window

        proto_a0 = ["tcp"] * n                           # all same  → H = 0.0
        proto_a1 = ["tcp"] * (n // 2) + ["udp"] * (n // 2)  # 50/50  → H = 1.0
        proto_b0 = ["udp"] * n                           # all same  → H = 0.0
        proto_b1 = ["udp"] * (n // 2) + ["icmp"] * (n // 2)  # 50/50 → H = 1.0

        df = pd.DataFrame({
            # Proto column drives the analytically known entropy values.
            "Proto":   proto_a0 + proto_a1 + proto_b0 + proto_b1,
            # All other default categorical and numerical columns held constant
            # so that Proto_entropy is the only feature whose value changes.
            "State":   ["CON"] * (4 * n),
            "sTtl":    [64]    * (4 * n),
            "sDSb":    [0]     * (4 * n),
            "TotPkts": [10]    * (4 * n),
            "TotBytes":[1000]  * (4 * n),
            "Rate":    [100.0] * (4 * n),
            "Dur":     [0.1]   * (4 * n),
            # Use "session" (not "session_id") to exercise the name-resolution path.
            "session": ["A"] * (2 * n) + ["B"] * (2 * n),
        })

        alpha = 0.5
        cfg = PipelineConfig(
            df=df,
            window_size=n,
            step_size=n,
            drop_incomplete=True,
            alpha=alpha,
            session_col="session",
            threshold_config=ThresholdConfig(
                min_history=1, min_valid_history=1, voting_threshold=1
            ),
        )
        res = run_entropy_pipeline(cfg)

        self.assertEqual(res.number_of_windows, 4)
        self.assertEqual(res.number_of_complete_windows, 4)

        out = res.output_df

        # session_id must be present and carry the right labels.
        self.assertIn("session_id", out.columns)
        self.assertEqual(list(out["session_id"]), ["A", "A", "B", "B"])

        # --- Verify Proto_entropy_ewma specifically ---
        self.assertIn("Proto_entropy", out.columns, "Proto_entropy must be a raw entropy column")
        self.assertIn("Proto_entropy_ewma", out.columns, "Proto_entropy_ewma must exist")

        raw = list(out["Proto_entropy"])
        ewma_col = list(out["Proto_entropy_ewma"])

        # Raw entropy sanity check (H=0 for constant, H=1 for 50/50 binary).
        self.assertAlmostEqual(raw[0], 0.0, places=10, msg="A0 raw: constant proto → H=0")
        self.assertAlmostEqual(raw[1], 1.0, places=10, msg="A1 raw: 50/50 proto → H=1")
        self.assertAlmostEqual(raw[2], 0.0, places=10, msg="B0 raw: constant proto → H=0")
        self.assertAlmostEqual(raw[3], 1.0, places=10, msg="B1 raw: 50/50 proto → H=1")

        # EWMA assertions derived independently from the recurrence.
        # Session A -------------------------------------------------------
        expected_ewma_A0 = 0.0                                  # first value = raw
        expected_ewma_A1 = alpha * raw[1] + (1 - alpha) * expected_ewma_A0  # = 0.5
        # Session B (reset) -----------------------------------------------
        expected_ewma_B0 = 0.0                                  # RESET: first value of new session
        expected_ewma_B1 = alpha * raw[3] + (1 - alpha) * expected_ewma_B0  # = 0.5

        self.assertAlmostEqual(ewma_col[0], expected_ewma_A0, places=10,
                               msg="A0: EWMA must equal first raw value")
        self.assertAlmostEqual(ewma_col[1], expected_ewma_A1, places=10,
                               msg="A1: EWMA must follow recurrence from A0")
        self.assertAlmostEqual(ewma_col[2], expected_ewma_B0, places=10,
                               msg="B0: EWMA must RESET (not carry over from session A)")
        self.assertAlmostEqual(ewma_col[3], expected_ewma_B1, places=10,
                               msg="B1: EWMA must follow recurrence from B0")

        # The reset discriminant: without reset B0 would be
        #   0.5 * raw[2] + 0.5 * ewma_col[1] = 0.5*0.0 + 0.5*0.5 = 0.25 ≠ 0.0
        wrong_b0 = alpha * raw[2] + (1 - alpha) * ewma_col[1]
        self.assertNotAlmostEqual(
            wrong_b0, expected_ewma_B0, places=5,
            msg="Discriminant: without reset, B0 would differ from the asserted value",
        )

    def test_session_unaware_behavior_unchanged(self):
        """Omitting session_col must produce EWMA values matching an independently
        computed expected sequence (alpha=0.5, Proto_entropy).

        Strategy
        --------
        Build a DataFrame whose windows yield analytically known Proto_entropy
        values: constant-proto windows give H=0, alternating-proto windows give
        H=1.  With no session boundaries and alpha=0.5 the EWMA recurrence is:

            ewma[0] = raw[0]
            ewma[t] = 0.5 * raw[t] + 0.5 * ewma[t-1]    for t >= 1

        We compute the expected sequence in the test and assert element-wise equality,
        proving that the session-unaware code path is correct and unchanged.
        """
        n = 100  # rows per window
        # 4 windows, no session column:
        #   window 0: Proto = all 'tcp'          → H_Proto = 0.0
        #   window 1: Proto = 50 'tcp' + 50 'udp'→ H_Proto = 1.0
        #   window 2: Proto = all 'tcp'          → H_Proto = 0.0
        #   window 3: Proto = 50 'tcp' + 50 'udp'→ H_Proto = 1.0
        proto = (
            ["tcp"] * n
            + ["tcp"] * (n // 2) + ["udp"] * (n // 2)
            + ["tcp"] * n
            + ["tcp"] * (n // 2) + ["udp"] * (n // 2)
        )
        df = pd.DataFrame({
            "Proto":   proto,
            "State":   ["CON"] * (4 * n),
            "sTtl":    [64]    * (4 * n),
            "sDSb":    [0]     * (4 * n),
            "TotPkts": [10]    * (4 * n),
            "TotBytes":[1000]  * (4 * n),
            "Rate":    [100.0] * (4 * n),
            "Dur":     [0.1]   * (4 * n),
        })

        alpha = 0.5
        cfg = PipelineConfig(
            df=df,
            window_size=n,
            step_size=n,
            drop_incomplete=True,
            alpha=alpha,
            session_col=None,          # explicit: no session awareness
            threshold_config=ThresholdConfig(
                min_history=1, min_valid_history=1, voting_threshold=1
            ),
        )
        res = run_entropy_pipeline(cfg)

        self.assertEqual(res.number_of_windows, 4)
        self.assertIn("Proto_entropy",      res.output_df.columns)
        self.assertIn("Proto_entropy_ewma", res.output_df.columns)

        raw   = list(res.output_df["Proto_entropy"])
        ewma_actual = list(res.output_df["Proto_entropy_ewma"])

        # Independently compute the expected EWMA from the recurrence.
        expected: list = [float(raw[0])]
        for t in range(1, len(raw)):
            expected.append(alpha * raw[t] + (1 - alpha) * expected[t - 1])

        for t, (exp, act) in enumerate(zip(expected, ewma_actual)):
            self.assertAlmostEqual(
                act, exp, places=10,
                msg=f"Window {t}: session-unaware EWMA mismatch (expected {exp}, got {act})",
            )


if __name__ == "__main__":
    unittest.main()
