"""Log-space naive-Bayes leaf votes for River's Hoeffding trees.

River 0.23 builds the naive-Bayes vote of a tree leaf from Gaussian densities and adds
``log(p) if p > 0 else 0.0`` per feature (``river.tree.utils.do_naive_bayes_prediction``).
A density that underflows to exactly 0 therefore counts as log 1 = 0, the most favourable
value: a feature value that rules a class out leaves that class unpenalised. With well
separated classes (benign packets of ~1,200 bytes, flood packets of ~53 bytes) a leaf then
scores benign windows as attacks with probability ~1, which is what happened to the
unsampled (N = 1) trials, whose tree never split.

``log_space_naive_bayes`` computes the Gaussian log density directly, so the vote equals
River's whenever no density underflows and stays correct when one would. Zero-variance
features and non-Gaussian attribute observers keep River's behaviour.

``likelihood(mode)`` selects the vote for the duration of a ``with`` block by rebinding the
function in River's tree-node modules. It is not thread-safe; the detector is single-threaded.
"""

import math
from contextlib import contextmanager

from river.tree.nodes import hatc_nodes, htc_nodes, last_nodes
from river.tree.splitter import GaussianSplitter

MODES = ("river", "log_space")
_SITES = (htc_nodes, hatc_nodes, last_nodes)


def _log_likelihood(splitter, value, cls):
    if isinstance(splitter, GaussianSplitter):
        estimator = splitter._att_dist_per_class.get(cls)
        if estimator is None:
            return 0.0
        var = estimator.sigma ** 2
        if not var:
            return 0.0
        return -((value - estimator.mu) ** 2) / (2 * var) - 0.5 * math.log(math.tau * var)
    probability = splitter.cond_proba(value, cls)
    return math.log(probability) if probability > 0 else 0.0


def log_space_naive_bayes(x, observed_class_distribution, splitters):
    """Drop-in replacement for ``river.tree.utils.do_naive_bayes_prediction``."""
    total = sum(observed_class_distribution.values())
    if not observed_class_distribution or total == 0:
        return {}
    votes = {}
    for cls, weight in observed_class_distribution.items():
        if weight <= 0:
            votes[cls] = -math.inf
            continue
        vote = math.log(weight / total)
        for attribute, splitter in (splitters or {}).items():
            if attribute in x:
                vote += _log_likelihood(splitter, x[attribute], cls)
        votes[cls] = vote
    best = max(votes.values())
    lse = best + math.log(sum(math.exp(v - best) for v in votes.values()))
    return {cls: math.exp(v - lse) for cls, v in votes.items()}


@contextmanager
def likelihood(mode):
    """Use River's naive-Bayes vote ("river") or the log-space one ("log_space")."""
    if mode not in MODES:
        raise ValueError(f"naive_bayes must be one of {MODES}")
    if mode == "river":
        yield
        return
    saved = [site.do_naive_bayes_prediction for site in _SITES]
    for site in _SITES:
        site.do_naive_bayes_prediction = log_space_naive_bayes
    try:
        yield
    finally:
        for site, original in zip(_SITES, saved):
            site.do_naive_bayes_prediction = original
