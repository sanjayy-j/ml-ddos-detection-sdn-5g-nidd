"""
Shannon Entropy Module for M2 — Entropy-Based Statistical Detection.

Provides functions to compute Shannon entropy H(X) over categorical distributions
for label-free DDoS detection components.
"""

import math
from collections import Counter
from typing import Any, Dict, Iterable, Union


def calculate_shannon_entropy(
    data: Union[Iterable[Any], Dict[Any, int], Counter],
    base: float = 2.0,
) -> float:
    """
    Calculate the Shannon entropy H(X) of a categorical sequence or frequency distribution.

    Mathematical Definition:
        H(X) = - sum_{i} p_i * log_{base}(p_i)
    where p_i is the empirical probability of category i.

    Edge Cases & Behavior:
        - Empty input (sequence length 0 or total frequency 0): Returns 0.0.
        - Single unique category (p_1 = 1.0): Returns 0.0 (log_2(1.0) = 0).
        - Zero-probability terms (p_i = 0): Safely ignored since lim_{p->0} p * log(p) = 0.
        - Logarithm base: Default is 2.0 (measuring entropy in bits).

    Parameters:
        data: Sequence of categorical values (list, tuple, np.ndarray, pd.Series)
              OR a frequency mapping (dict, Counter).
        base: Logarithm base for entropy calculation (default 2.0).

    Returns:
        float: Calculated Shannon entropy value >= 0.0.
    """
    if base <= 0 or base == 1.0:
        raise ValueError(f"Logarithm base must be positive and != 1.0, got {base}")

    if isinstance(data, (dict, Counter)):
        counts = data
        total_count = sum(counts.values())
    else:
        # Convert iterable to frequency counts
        counts = Counter(data)
        total_count = sum(counts.values())

    if total_count == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p_i = count / total_count
            entropy -= p_i * math.log(p_i, base)

    return float(entropy)
