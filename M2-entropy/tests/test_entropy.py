"""
Unit tests for Shannon Entropy implementation in M2-entropy/entropy.py.
"""

import math
import os
import sys
import unittest
from collections import Counter
from pathlib import Path

import numpy as np

# Add parent directory (M2-entropy) to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent) if "__file__" in globals() else "..")

from entropy import calculate_shannon_entropy

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class TestShannonEntropy(unittest.TestCase):
    """Test suite for calculate_shannon_entropy function."""

    def test_a_single_unique_category(self):
        """Test A: [A, A, A, A] -> entropy = 0.0 bits."""
        data = ["A", "A", "A", "A"]
        result = calculate_shannon_entropy(data)
        self.assertEqual(result, 0.0)

    def test_b_four_equally_likely_categories(self):
        """Test B: [A, B, C, D] -> entropy = 2.0 bits (log2(4))."""
        data = ["A", "B", "C", "D"]
        result = calculate_shannon_entropy(data)
        self.assertAlmostEqual(result, 2.0, places=7)

    def test_c_two_equally_likely_categories(self):
        """Test C: [A, A, B, B] -> entropy = 1.0 bit (log2(2))."""
        data = ["A", "A", "B", "B"]
        result = calculate_shannon_entropy(data)
        self.assertAlmostEqual(result, 1.0, places=7)

    def test_d_empty_input(self):
        """Test D: Empty input -> defined and documented behavior = 0.0 bits."""
        data = []
        result = calculate_shannon_entropy(data)
        self.assertEqual(result, 0.0)

    def test_frequency_dictionary_and_counter_input(self):
        """Test passing frequency dictionary or Counter directly."""
        counts = {"A": 2, "B": 2}
        result = calculate_shannon_entropy(counts)
        self.assertAlmostEqual(result, 1.0, places=7)

        counter = Counter(["A", "B", "C", "D"])
        result_counter = calculate_shannon_entropy(counter)
        self.assertAlmostEqual(result_counter, 2.0, places=7)

    def test_numpy_array_input(self):
        """Test compatibility with numpy ndarray input."""
        arr = np.array(["A", "B", "C", "D"])
        self.assertAlmostEqual(calculate_shannon_entropy(arr), 2.0, places=7)

        numeric_arr = np.array([10, 10, 20, 20])
        self.assertAlmostEqual(calculate_shannon_entropy(numeric_arr), 1.0, places=7)

    def test_pandas_series_input_if_available(self):
        """Test compatibility with pandas Series if pandas is installed."""
        if HAS_PANDAS:
            s = pd.Series(["A", "A", "B", "B"])
            self.assertAlmostEqual(calculate_shannon_entropy(s), 1.0, places=7)

    def test_unequal_probabilities(self):
        """Test sequence with unequal category distribution."""
        # 3 A's (p=0.75), 1 B (p=0.25)
        # H = - (0.75 * log2(0.75) + 0.25 * log2(0.25)) = 0.8112781...
        data = ["A", "A", "A", "B"]
        expected = - (0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
        self.assertAlmostEqual(calculate_shannon_entropy(data), expected, places=7)

    def test_custom_log_base(self):
        """Test entropy calculation with custom logarithm bases (nats and hartleys)."""
        data = ["A", "B", "C", "D"]
        # Base e (nat)
        result_nat = calculate_shannon_entropy(data, base=math.e)
        self.assertAlmostEqual(result_nat, math.log(4), places=7)

        # Base 10 (hartley)
        result_10 = calculate_shannon_entropy(data, base=10.0)
        self.assertAlmostEqual(result_10, math.log10(4), places=7)

    def test_invalid_base_raises_value_error(self):
        """Test that invalid log bases raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_shannon_entropy(["A", "B"], base=0)
        with self.assertRaises(ValueError):
            calculate_shannon_entropy(["A", "B"], base=1.0)
        with self.assertRaises(ValueError):
            calculate_shannon_entropy(["A", "B"], base=-2.0)


if __name__ == "__main__":
    unittest.main()
