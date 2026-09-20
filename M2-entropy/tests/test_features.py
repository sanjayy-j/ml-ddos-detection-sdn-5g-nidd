"""
Unit tests for Feature Extractor and Discretization module in M2-entropy/features.py.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory (M2-entropy) to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import numpy as np
    import pandas as pd
    from features import (
        DEFAULT_EXCLUDE_COLS,
        FeatureConfig,
        FeatureExtractor,
        extract_categorical_and_binned_features,
    )
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class TestFeatureExtractor(unittest.TestCase):
    """Test suite for FeatureExtractor and extract_categorical_and_binned_features."""

    def setUp(self):
        """Create sample DataFrame fixtures for testing."""
        if HAS_PANDAS:
            self.df_sample = pd.DataFrame(
                {
                    "Proto": ["tcp", "udp", "tcp", "icmp", "udp"],
                    "State": ["REQ", "INT", "CON", "FIN", "REQ"],
                    "sTtl": [64, 128, 64, 255, 64],
                    "sDSb": ["CS0", "CS0", "EF", "CS0", "CS0"],
                    "TotPkts": [1, 5, 20, 100, 2],
                    "TotBytes": [42, 500, 1500, 60000, 84],
                    "Rate": [0.0, 12.5, 400.0, 15000.0, 1.2],
                    "Dur": [0.0, 0.5, 2.3, 10.1, 0.1],
                    "Label": ["Benign", "Malicious", "Benign", "Malicious", "Benign"],
                    "Attack Type": ["Benign", "UDPFlood", "Benign", "SYNFlood", "Benign"],
                    "Offset": [100, 200, 300, 400, 500],
                },
                index=[10, 20, 30, 40, 50],  # Non-default index
            )

    def test_categorical_feature_extraction(self):
        """Test extraction of categorical features without modification."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        config = FeatureConfig(
            categorical_cols=["Proto", "State"],
            numerical_cols=[],
        )
        extractor = FeatureExtractor(config)
        res = extractor.extract_features(self.df_sample)

        self.assertIn("Proto", res.columns)
        self.assertIn("State", res.columns)
        self.assertEqual(len(res.columns), 2)
        self.assertEqual(list(res["Proto"]), ["tcp", "udp", "tcp", "icmp", "udp"])
        self.assertEqual(list(res["State"]), ["REQ", "INT", "CON", "FIN", "REQ"])

    def test_numerical_binning_strategies(self):
        """Test discretization of numerical features into bins using different strategies."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        # Quantile strategy
        cfg_q = FeatureConfig(categorical_cols=[], numerical_cols=["TotPkts"], n_bins=3, binning_strategy="quantile")
        res_q = extract_categorical_and_binned_features(self.df_sample, cfg_q)
        self.assertIn("TotPkts_bin", res_q.columns)
        self.assertEqual(len(res_q), 5)
        self.assertTrue(all(val.startswith("bin_") for val in res_q["TotPkts_bin"]))

        # Uniform strategy
        cfg_u = FeatureConfig(categorical_cols=[], numerical_cols=["Rate"], n_bins=3, binning_strategy="uniform")
        res_u = extract_categorical_and_binned_features(self.df_sample, cfg_u)
        self.assertIn("Rate_bin", res_u.columns)
        self.assertEqual(len(res_u), 5)

        # Log-quantile strategy
        cfg_l = FeatureConfig(categorical_cols=[], numerical_cols=["TotBytes"], n_bins=3, binning_strategy="log_quantile")
        res_l = extract_categorical_and_binned_features(self.df_sample, cfg_l)
        self.assertIn("TotBytes_bin", res_l.columns)
        self.assertEqual(len(res_l), 5)

        # Custom bin strategy
        cfg_c = FeatureConfig(
            categorical_cols=[],
            numerical_cols=["TotPkts"],
            binning_strategy="custom",
            custom_bins={"TotPkts": [0, 3, 50, 1000]},
        )
        res_c = extract_categorical_and_binned_features(self.df_sample, cfg_c)
        self.assertIn("TotPkts_bin", res_c.columns)
        self.assertEqual(list(res_c["TotPkts_bin"]), ["bin_0", "bin_1", "bin_1", "bin_2", "bin_0"])

    def test_missing_value_handling(self):
        """Test categorical fill token and numerical imputation strategies for missing values."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        df_missing = self.df_sample.copy()
        df_missing.loc[20, "Proto"] = np.nan
        df_missing.loc[30, "TotPkts"] = np.nan

        config = FeatureConfig(
            categorical_cols=["Proto"],
            numerical_cols=["TotPkts"],
            categorical_missing_fill="__missing__",
            numeric_missing_fill="median",
        )
        extractor = FeatureExtractor(config)
        res = extractor.extract_features(df_missing)

        # Categorical missing replaced with token
        self.assertEqual(res.loc[20, "Proto"], "__missing__")
        # Numerical missing filled with median before binning
        self.assertEqual(len(res), 5)

    def test_invalid_or_missing_requested_columns(self):
        """Test KeyError when non-existent column is requested."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        config = FeatureConfig(categorical_cols=["NonExistentCol"])
        extractor = FeatureExtractor(config)
        with self.assertRaises(KeyError):
            extractor.extract_features(self.df_sample)

    def test_exclusion_of_target_and_metadata_columns(self):
        """Test ValueError when excluded columns (Label, Attack Type, Offset) are requested as entropy features."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        for bad_col in ["Label", "Attack Type", "Offset"]:
            config = FeatureConfig(categorical_cols=[bad_col])
            extractor = FeatureExtractor(config)
            with self.assertRaises(ValueError):
                extractor.extract_features(self.df_sample)

    def test_allow_excluded_override(self):
        """Test that allow_excluded=True permits extracting excluded columns for evaluation tracking."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        config = FeatureConfig(categorical_cols=["Label"], numerical_cols=[])
        extractor = FeatureExtractor(config)
        res = extractor.extract_features(self.df_sample, allow_excluded=True)
        self.assertIn("Label", res.columns)
        self.assertEqual(list(res["Label"]), ["Benign", "Malicious", "Benign", "Malicious", "Benign"])

    def test_preservation_of_row_count_order_and_index(self):
        """Test that output DataFrame preserves exact row count, row order, and original index."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        config = FeatureConfig(categorical_cols=["Proto"], numerical_cols=["Dur"])
        extractor = FeatureExtractor(config)
        res = extractor.extract_features(self.df_sample)

        self.assertEqual(len(res), len(self.df_sample))
        self.assertEqual(list(res.index), [10, 20, 30, 40, 50])
        self.assertEqual(list(res["Proto"]), list(self.df_sample["Proto"]))

    def test_richer_dataframe_with_src_ip_and_dst_port(self):
        """Test feature extraction with hypothetical richer dataset containing SrcIP and DstPort."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        df_rich = self.df_sample.copy()
        df_rich["SrcIP"] = ["192.168.1.10", "10.0.0.5", "192.168.1.10", "172.16.0.2", "10.0.0.5"]
        df_rich["DstPort"] = [80, 443, 80, 22, 443]

        config = FeatureConfig(
            categorical_cols=["SrcIP", "DstPort", "Proto"],
            numerical_cols=["TotPkts"],
        )
        res = extract_categorical_and_binned_features(df_rich, config)

        self.assertIn("SrcIP", res.columns)
        self.assertIn("DstPort", res.columns)
        self.assertIn("Proto", res.columns)
        self.assertIn("TotPkts_bin", res.columns)
        self.assertEqual(list(res["SrcIP"]), ["192.168.1.10", "10.0.0.5", "192.168.1.10", "172.16.0.2", "10.0.0.5"])
        self.assertEqual(list(res["DstPort"]), ["80", "443", "80", "22", "443"])

    def test_empty_input_dataframe(self):
        """Test behavior when input DataFrame is empty."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        df_empty = pd.DataFrame(columns=["Proto", "TotPkts"])
        config = FeatureConfig(categorical_cols=["Proto"], numerical_cols=["TotPkts"])
        extractor = FeatureExtractor(config)
        res = extractor.extract_features(df_empty)

        self.assertEqual(len(res), 0)
        self.assertIn("Proto", res.columns)
        self.assertIn("TotPkts_bin", res.columns)

    def test_invalid_bin_configuration(self):
        """Test error handling for invalid bin configurations."""
        if not HAS_PANDAS:
            self.skipTest("pandas is required for this test")
        # n_bins < 2
        with self.assertRaises(ValueError):
            FeatureExtractor(FeatureConfig(n_bins=1))

        # invalid strategy
        with self.assertRaises(ValueError):
            FeatureExtractor(FeatureConfig(binning_strategy="invalid_strategy"))

        # custom strategy missing bin edges for column
        with self.assertRaises(ValueError):
            FeatureExtractor(FeatureConfig(binning_strategy="custom", numerical_cols=["TotPkts"], custom_bins={}))


if __name__ == "__main__":
    unittest.main()
