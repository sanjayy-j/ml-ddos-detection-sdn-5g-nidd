import random

import pytest
from river import tree
from river.tree.nodes import hatc_nodes, htc_nodes, last_nodes

from m3.config import RunConfig
from m3.naive_bayes import likelihood, log_space_naive_bayes
from m3.research_metrics import evaluate_ablations


def separable(rng, label):
    """Windows like the N = 1 trials: two redundant, perfectly separating features."""
    size = rng.gauss(1200, 350) if label == 0 else rng.gauss(52, 10)
    return {"mean_packet_size": size, "bytes_per_second": size * 100,
            "packets_per_second": rng.gauss(100, 15)}


def nb_tree(rows):
    model = tree.HoeffdingTreeClassifier(leaf_prediction="nb", grace_period=10_000)
    for features, label in rows:
        model.learn_one(features, label)
    return model


def test_matches_river_when_no_density_underflows():
    rng = random.Random(3)
    rows = [({"a": rng.gauss(label, 1.0), "b": rng.gauss(2 * label, 1.5)}, label)
            for label in (0, 1) * 200]
    model = nb_tree(rows)
    for x in ({"a": 0.2, "b": 0.5}, {"a": 0.8, "b": 1.7}, {"a": 1.4, "b": 3.0}):
        river_vote = model.predict_proba_one(x)
        with likelihood("log_space"):
            fixed_vote = model.predict_proba_one(x)
        assert fixed_vote == pytest.approx(river_vote, abs=1e-9)


def test_underflowed_density_no_longer_counts_as_certainty():
    rng = random.Random(7)
    model = nb_tree([(separable(rng, label), label) for label in (0, 1) * 300])
    benign = {"mean_packet_size": 1200.0, "bytes_per_second": 120_000.0, "packets_per_second": 100.0}
    attack = {"mean_packet_size": 52.0, "bytes_per_second": 5_200.0, "packets_per_second": 100.0}
    assert model.predict_proba_one(benign)[1] > 0.99          # River: benign window scored as attack
    with likelihood("log_space"):
        assert model.predict_proba_one(benign)[1] < 1e-6
        assert model.predict_proba_one(attack)[1] > 0.99


def test_context_restores_river_function_even_after_an_error():
    originals = [site.do_naive_bayes_prediction for site in (htc_nodes, hatc_nodes, last_nodes)]
    with pytest.raises(RuntimeError):
        with likelihood("log_space"):
            assert htc_nodes.do_naive_bayes_prediction is log_space_naive_bayes
            raise RuntimeError
    assert [site.do_naive_bayes_prediction
            for site in (htc_nodes, hatc_nodes, last_nodes)] == originals
    with pytest.raises(ValueError):
        with likelihood("gaussian"):
            pass


def test_config_default_and_validation():
    assert RunConfig(input_path="fixture").naive_bayes == "log_space"
    assert RunConfig(input_path="fixture", naive_bayes="river").naive_bayes == "river"
    with pytest.raises(ValueError, match="naive_bayes"):
        RunConfig(input_path="fixture", naive_bayes="gaussian")


def test_ablation_replay_reproduces_the_unsampled_failure_only_with_river_vote():
    rng = random.Random(11)
    labels = [i % 2 for i in range(600)]
    rows = [{"features": separable(rng, label), "label": label, "warmup": i < 200}
            for i, label in enumerate(labels)]
    legacy = evaluate_ablations(rows, seed=42, grace_period=200, naive_bayes="river")["hat_adwin"]
    fixed = evaluate_ablations(rows, seed=42, grace_period=200, naive_bayes="log_space")["hat_adwin"]
    assert legacy["tree_nodes"] == fixed["tree_nodes"] == 1      # tied features: no split yet
    assert legacy["metrics"]["false_positive_rate"]["value"] > 0.9
    assert fixed["metrics"]["false_positive_rate"]["value"] < 0.02
    assert fixed["metrics"]["recall"]["value"] > 0.98
