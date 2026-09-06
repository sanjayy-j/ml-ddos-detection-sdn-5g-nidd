"""Stage G tests — SVM model (Nystroem RBF approximation + LinearSVC)."""

import numpy as np
import pytest
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from fixtures import make_synthetic_5gnidd, synthetic_config
from models.svm import ChunkedNystroem, build_svm, describe_svm, gamma_scale
from preprocessing.features import build_feature_frame, get_feature_columns
from preprocessing.pipeline import prepare_m1_dataset


@pytest.fixture(scope="module")
def prepared():
    df = make_synthetic_5gnidd(n_blocks=4, rows_per_block=400, seed=0)
    config = synthetic_config()
    return prepare_m1_dataset(df, config), config, df


def _cfg(**svm):
    base = {"seed": 42, "models": {"svm": {"max_iter": 500, **svm}}}
    return base


# --- gamma ------------------------------------------------------------------

def test_gamma_scale_matches_sklearn_heuristic():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(500, 8))
    assert gamma_scale(X) == pytest.approx(1.0 / (8 * X.var()))


def test_gamma_scale_handles_constant_matrix():
    X = np.ones((10, 4))
    assert gamma_scale(X) == pytest.approx(1.0 / 4)


# --- construction -----------------------------------------------------------

def test_model_is_an_svm_pipeline():
    model = build_svm(_cfg(), gamma=0.05)
    assert isinstance(model, Pipeline)
    assert isinstance(model.named_steps["nystroem"], ChunkedNystroem)
    assert isinstance(model.named_steps["linearsvc"], LinearSVC)
    # a genuine maximum-margin hinge-loss classifier
    assert model.named_steps["linearsvc"].loss == "squared_hinge"


def test_config_and_overrides_are_applied():
    model = build_svm(_cfg(C=0.5, n_components=64), gamma=0.05)
    assert model.named_steps["linearsvc"].C == 0.5
    assert model.named_steps["nystroem"].n_components == 64

    override = build_svm(_cfg(C=0.5, n_components=64), gamma=0.05,
                         C=2.0, n_components=32)
    assert override.named_steps["linearsvc"].C == 2.0
    assert override.named_steps["nystroem"].n_components == 32


def test_class_weight_defaults_to_stage_d_choice():
    assert build_svm(_cfg(), gamma=0.05).named_steps[
        "linearsvc"].class_weight == "balanced"


def test_seed_is_propagated_to_both_stages():
    model = build_svm(_cfg(), gamma=0.05)
    assert model.named_steps["nystroem"].random_state == 42
    assert model.named_steps["linearsvc"].random_state == 42


# --- chunked feature map ----------------------------------------------------

def test_chunked_nystroem_matches_unchunked_output():
    from sklearn.kernel_approximation import Nystroem

    rng = np.random.default_rng(1)
    X = rng.normal(size=(500, 10))
    chunked = ChunkedNystroem(n_components=32, gamma=0.1, random_state=42,
                              chunk_rows=64).fit(X)
    plain = Nystroem(kernel="rbf", gamma=0.1, n_components=32,
                     random_state=42).fit(X)

    np.testing.assert_allclose(chunked.transform(X), plain.transform(X),
                               rtol=1e-5, atol=1e-5)


def test_chunked_nystroem_output_shape_dtype_and_finiteness():
    rng = np.random.default_rng(2)
    X = rng.normal(size=(300, 6))
    Z = ChunkedNystroem(n_components=16, gamma=0.2, random_state=42,
                        chunk_rows=100).fit(X).transform(X)
    assert Z.shape == (300, 16)
    assert Z.dtype == np.float32           # memory cap, not float64
    assert np.isfinite(Z).all()


def test_chunk_size_does_not_change_the_result():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(250, 5))
    a = ChunkedNystroem(n_components=16, gamma=0.1, random_state=42,
                        chunk_rows=1000).fit(X).transform(X)
    b = ChunkedNystroem(n_components=16, gamma=0.1, random_state=42,
                        chunk_rows=7).fit(X).transform(X)
    np.testing.assert_array_equal(a, b)


# --- training on the Stage D representation ---------------------------------

def test_trains_and_scores_on_stage_d_matrix(prepared):
    data, _, _ = prepared
    gamma = gamma_scale(data.X["train"])
    model = build_svm(_cfg(n_components=32), gamma=gamma)
    model.fit(data.X["train"], data.y["train"])

    scores = model.decision_function(data.X["test"])
    pred = model.predict(data.X["test"])

    assert scores.shape == (len(data.X["test"]),)
    assert np.isfinite(scores).all()
    assert set(np.unique(pred)) <= {0, 1}
    assert list(model.named_steps["linearsvc"].classes_) == [0, 1]


def test_decision_scores_are_margins_not_probabilities(prepared):
    data, _, _ = prepared
    model = build_svm(_cfg(n_components=32), gamma=gamma_scale(data.X["train"]))
    model.fit(data.X["train"], data.y["train"])
    scores = model.decision_function(data.X["val"])
    # margins are unbounded; the sign is the default decision
    assert scores.min() < 0 < scores.max()
    np.testing.assert_array_equal(
        (scores >= 0).astype(np.int8), model.predict(data.X["val"]))


def test_training_is_deterministic(prepared):
    data, _, _ = prepared
    gamma = gamma_scale(data.X["train"])
    a = build_svm(_cfg(n_components=32), gamma=gamma).fit(
        data.X["train"], data.y["train"])
    b = build_svm(_cfg(n_components=32), gamma=gamma).fit(
        data.X["train"], data.y["train"])
    np.testing.assert_allclose(a.decision_function(data.X["test"]),
                               b.decision_function(data.X["test"]),
                               rtol=1e-9, atol=1e-9)


def test_describe_svm_records_reproducibility_fields(prepared):
    data, _, _ = prepared
    model = build_svm(_cfg(n_components=32, C=0.25),
                      gamma=gamma_scale(data.X["train"]))
    model.fit(data.X["train"], data.y["train"])
    info = describe_svm(model)

    assert info["approximation"] == "Nystroem(rbf)"
    assert info["classifier"] == "LinearSVC"
    assert info["n_components"] == 32
    assert info["C"] == 0.25
    assert info["class_weight"] == "balanced"
    assert np.isfinite(info["coef_l2_norm"])


# --- leakage guards ---------------------------------------------------------

@pytest.mark.parametrize("column", ["Attack Type", "Attack Tool"])
def test_attack_metadata_never_reaches_the_svm(prepared, column):
    data, config, df = prepared
    assert column not in get_feature_columns(config)
    assert column not in build_feature_frame(df, config).columns
    assert not any(name == column or name.startswith(column + "_")
                   for name in data.feature_names)


def test_svm_consumes_exactly_the_locked_feature_width(prepared):
    data, _, _ = prepared
    model = build_svm(_cfg(n_components=32), gamma=gamma_scale(data.X["train"]))
    model.fit(data.X["train"], data.y["train"])
    assert model.named_steps["nystroem"].n_features_in_ == \
        data.X["train"].shape[1]

    wrong = np.hstack([data.X["test"],
                       np.ones((len(data.X["test"]), 1), dtype=np.float32)])
    with pytest.raises(ValueError):
        model.decision_function(wrong)
