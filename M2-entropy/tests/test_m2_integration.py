"""Integration tests: SrcAddr/Dport pipeline, session isolation, label isolation, CLI."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SYS_PATH_M2 = str(Path(__file__).resolve().parent.parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import numpy as np
import pandas as pd

from features import FeatureConfig
from pipeline import PipelineConfig, run_entropy_pipeline
from thresholds import ThresholdConfig
import run_m2


def make_flows(n_per_session=300, sessions=3, seed=0):
    rng = np.random.default_rng(seed)
    parts = []
    for s in range(1, sessions + 1):
        src = rng.choice([f"10.0.0.{i}" for i in range(1, 9)], n_per_session)
        dport = rng.choice(["http", "https", "853", "0x0800"], n_per_session).astype(object)
        dport[rng.random(n_per_session) < 0.2] = np.nan
        label = np.where(rng.random(n_per_session) < 0.3, "Malicious", "Benign")
        parts.append(pd.DataFrame({
            "SrcAddr": src, "Dport": dport, "Rank": np.arange(1, n_per_session + 1),
            "Label": label, "Attack Type": np.where(label == "Malicious", "UDPFlood", "Benign"),
            "session_id": s,
        }))
    return pd.concat(parts, ignore_index=True)


def cfgs(**kw):
    fc = FeatureConfig(categorical_cols=["SrcAddr", "Dport"], numerical_cols=[],
                       unobserved_missing_cols=["Dport"], min_observed=10)
    tc = ThresholdConfig(min_history=5, min_valid_history=5, voting_threshold=1)
    return PipelineConfig(df=kw.pop("df"), window_size=50, step_size=25, alpha=0.3,
                          feature_config=fc, threshold_config=tc, session_col="session_id", **kw)


class TestPipelineSessions(unittest.TestCase):
    def setUp(self):
        self.df = make_flows()
        self.out = run_entropy_pipeline(cfgs(df=self.df)).output_df

    def test_two_separate_entropy_features(self):
        for c in ("SrcAddr_entropy", "Dport_entropy", "SrcAddr_entropy_ewma", "Dport_entropy_ewma"):
            self.assertIn(c, self.out.columns)
        self.assertFalse(np.allclose(self.out["SrcAddr_entropy"], self.out["Dport_entropy"], equal_nan=True))

    def test_windows_never_cross_sessions(self):
        sess = self.df["session_id"].to_numpy()
        for r in self.out.itertuples():
            self.assertEqual(sess[r.start_idx], sess[r.end_idx - 1])
            self.assertEqual(sess[r.start_idx], r.session_id)

    def test_ewma_resets_at_each_session_start(self):
        firsts = self.out.groupby("session_id").head(1)
        np.testing.assert_allclose(firsts["SrcAddr_entropy_ewma"], firsts["SrcAddr_entropy"])
        self.assertEqual(len(firsts), 3)

    def test_ewma_matches_independent_per_session_recompute(self):
        for _, g in self.out.groupby("session_id"):
            v = g["SrcAddr_entropy"].to_numpy()
            exp, s = [], None
            for x in v:
                s = x if s is None else 0.3 * x + 0.7 * s
                exp.append(s)
            np.testing.assert_allclose(g["SrcAddr_entropy_ewma"], exp)

    def test_threshold_warmup_restarts_per_session(self):
        for _, g in self.out.groupby("session_id"):
            self.assertTrue(g["threshold_is_warmup"].iloc[:5].all())
            self.assertFalse(g["window_anomaly"].iloc[:5].any())

    def test_session_result_independent_of_other_sessions(self):
        only_s2 = self.df[self.df["session_id"] == 2].reset_index(drop=True)
        alone = run_entropy_pipeline(cfgs(df=only_s2)).output_df
        together = self.out[self.out["session_id"] == 2].reset_index(drop=True)
        np.testing.assert_allclose(alone["SrcAddr_entropy_ewma"], together["SrcAddr_entropy_ewma"])
        np.testing.assert_allclose(alone["Dport_entropy_ewma"], together["Dport_entropy_ewma"], equal_nan=True)
        self.assertEqual(alone["window_anomaly"].tolist(), together["window_anomaly"].tolist())

    def test_labels_do_not_influence_detection(self):
        flipped = self.df.copy()
        flipped["Label"] = np.where(flipped["Label"] == "Benign", "Malicious", "Benign")
        flipped["Attack Type"] = "Other"
        out2 = run_entropy_pipeline(cfgs(df=flipped)).output_df
        self.assertEqual(self.out["window_anomaly"].tolist(), out2["window_anomaly"].tolist())
        np.testing.assert_allclose(self.out["SrcAddr_entropy_ewma"], out2["SrcAddr_entropy_ewma"])

    def test_deterministic(self):
        again = run_entropy_pipeline(cfgs(df=self.df)).output_df
        pd.testing.assert_frame_equal(self.out, again)

    def test_unobserved_dport_windows_cannot_alarm(self):
        df = self.df.copy()
        df.loc[df["session_id"] == 3, "Dport"] = np.nan          # nothing observed in session 3
        out = run_entropy_pipeline(cfgs(df=df)).output_df
        s3 = out[out["session_id"] == 3]
        self.assertTrue(s3["Dport_entropy"].isna().all())
        self.assertFalse(s3["window_anomaly"].any())             # invalid -> no alarm, not a crash


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        df = make_flows(n_per_session=200, sessions=2).drop(columns=["session_id"])
        df.insert(0, "", range(len(df)))
        df["Dport"] = df["Dport"].fillna("")
        self.csv = os.path.join(self.tmp.name, "flows.csv")
        df.to_csv(self.csv, index=False)
        self.out_dir = os.path.join(self.tmp.name, "out")

    def tearDown(self):
        self.tmp.cleanup()

    def test_main_writes_outputs(self):
        run_m2.main(["--input", self.csv, "--output-dir", self.out_dir, "--window-size", "50",
                     "--step-size", "25", "--min-history", "5", "--voting-threshold", "1"])
        w = pd.read_csv(os.path.join(self.out_dir, "windows.csv"))
        with open(os.path.join(self.out_dir, "metrics.json")) as fh:
            m = json.load(fh)
        self.assertEqual(m["data_quality"]["n_sessions"], 2)
        self.assertEqual(m["pipeline"]["entropy_columns"], ["SrcAddr_entropy", "Dport_entropy"])
        self.assertIn("y_true", w.columns)
        self.assertIn("all_windows", m["evaluation"])
        half, anymal = m["evaluation"]["all_windows"], m["evaluation_any_malicious_flow"]["all_windows"]
        self.assertEqual(half["tp"] + half["fp"], anymal["tp"] + anymal["fp"])      # same predictions
        self.assertGreaterEqual(anymal["n_attack_windows"], half["n_attack_windows"])
        self.assertEqual(anymal["n_attack_windows"], int((w["malicious_fraction"] > 0).sum()))

    def test_subprocess_entry_point(self):
        script = os.path.join(SYS_PATH_M2, "run_m2.py")
        r = subprocess.run([sys.executable, script, "--input", self.csv, "--output-dir", self.out_dir,
                            "--window-size", "50", "--step-size", "25", "--min-history", "5"],
                           capture_output=True, text=True, cwd=self.tmp.name)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.out_dir, "metrics.json")))

    def test_missing_input_file_message(self):
        with self.assertRaises(FileNotFoundError):
            run_m2.main(["--input", os.path.join(self.tmp.name, "nope.csv"), "--output-dir", self.out_dir])

    def test_no_eval_skips_label_columns(self):
        run_m2.main(["--input", self.csv, "--output-dir", self.out_dir, "--no-eval", "--min-history", "5",
                     "--window-size", "50", "--step-size", "25"])
        w = pd.read_csv(os.path.join(self.out_dir, "windows.csv"))
        self.assertNotIn("y_true", w.columns)


if __name__ == "__main__":
    unittest.main()
