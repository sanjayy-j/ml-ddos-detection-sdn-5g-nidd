"""Tests for transparent handling of missing values (never invent a destination port)."""

import sys
import unittest
from pathlib import Path

SYS_PATH_M2 = str(Path(__file__).resolve().parent.parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import numpy as np
import pandas as pd

from features import FeatureConfig, FeatureExtractor
from window_entropy import compute_window_entropy
from windowing import FlowWindow


def _window(src, dport):
    df = pd.DataFrame({"SrcAddr": src, "Dport": dport})
    return FlowWindow(window_id=0, start_idx=0, end_idx=len(df), data=df)


class TestUnobservedMissing(unittest.TestCase):
    def cfg(self, **kw):
        return FeatureConfig(categorical_cols=["SrcAddr", "Dport"], numerical_cols=[], **kw)

    def test_default_behaviour_unchanged_missing_becomes_sentinel_category(self):
        w = _window(["a"] * 4, ["80", np.nan, "80", np.nan])
        feats = FeatureExtractor(self.cfg()).extract_features(w.data)
        self.assertIn("__missing__", set(feats["Dport"]))

    def test_unobserved_missing_stays_nan_and_is_not_invented(self):
        w = _window(["a"] * 4, ["80", np.nan, "443", np.nan])
        feats = FeatureExtractor(self.cfg(unobserved_missing_cols=["Dport"])).extract_features(w.data)
        self.assertEqual(int(feats["Dport"].isna().sum()), 2)
        self.assertEqual(set(feats["Dport"].dropna()), {"80", "443"})

    def test_entropy_over_observed_only_with_counts(self):
        dports = ["80", "443"] * 6 + [np.nan] * 8   # 12 observed (H=1 bit), 8 missing
        w = _window(["a"] * 20, dports)
        res = compute_window_entropy(w, self.cfg(unobserved_missing_cols=["Dport"], min_observed=10))
        self.assertAlmostEqual(res.entropy_scores["Dport_entropy"], 1.0)
        self.assertEqual(res.entropy_scores["Dport_observed_count"], 12.0)
        self.assertEqual(res.entropy_scores["Dport_missing_count"], 8.0)

    def test_too_few_observed_gives_nan_not_zero(self):
        w = _window(["a"] * 20, ["80"] * 3 + [np.nan] * 17)
        res = compute_window_entropy(w, self.cfg(unobserved_missing_cols=["Dport"], min_observed=10))
        self.assertTrue(np.isnan(res.entropy_scores["Dport_entropy"]))
        self.assertEqual(res.entropy_scores["Dport_missing_count"], 17.0)

    def test_srcaddr_and_dport_entropy_are_separate_features(self):
        src = ["a", "b", "c", "d"] * 5           # 2 bits
        dport = ["80"] * 20                      # 0 bits
        res = compute_window_entropy(_window(src, dport), self.cfg())
        self.assertAlmostEqual(res.entropy_scores["SrcAddr_entropy"], 2.0)
        self.assertAlmostEqual(res.entropy_scores["Dport_entropy"], 0.0)

    def test_port_tokens_kept_verbatim(self):
        # service names, hex and decimals are different categories exactly as in the file
        w = _window(["a"] * 4, ["http", "0x0800", "853", "http"])
        feats = FeatureExtractor(self.cfg()).extract_features(w.data)
        self.assertEqual(feats["Dport"].tolist(), ["http", "0x0800", "853", "http"])


if __name__ == "__main__":
    unittest.main()
