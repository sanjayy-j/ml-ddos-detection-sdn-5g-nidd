"""Stage H tests — 1-D CNN.

Deliberately cheap: tiny synthetic tensors and 1-2 epoch fits, so the
suite never depends on the expensive full CNN training run.
"""

import os

import numpy as np
import pytest

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from models.cnn import (  # noqa: E402
    CNN_INPUT_CHANNELS,
    balanced_class_weight,
    build_cnn,
    describe_cnn,
    reshape_for_conv1d,
    set_seeds,
)

N_FEATURES = 67


# --- input representation ---------------------------------------------------

def test_reshape_produces_the_expected_conv1d_shape():
    X = np.arange(20 * N_FEATURES, dtype=np.float32).reshape(20, N_FEATURES)
    Z = reshape_for_conv1d(X)
    assert Z.shape == (20, N_FEATURES, CNN_INPUT_CHANNELS)


def test_reshape_preserves_stage_d_feature_order_exactly():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(50, N_FEATURES)).astype(np.float32)
    Z = reshape_for_conv1d(X)
    # dropping the channel axis must return the original matrix untouched
    np.testing.assert_array_equal(Z[:, :, 0], X)
    for row in range(5):
        np.testing.assert_array_equal(Z[row, :, 0], X[row])


def test_reshape_rejects_non_2d_input():
    with pytest.raises(ValueError, match="2-D"):
        reshape_for_conv1d(np.zeros((4, 5, 6)))


# --- class weighting --------------------------------------------------------

def test_balanced_class_weight_matches_sklearn():
    from sklearn.utils.class_weight import compute_class_weight

    y = np.array([0] * 30 + [1] * 70)
    got = balanced_class_weight(y)
    expected = compute_class_weight("balanced", classes=np.array([0, 1]), y=y)
    assert got[0] == pytest.approx(expected[0])
    assert got[1] == pytest.approx(expected[1])
    # the majority class receives the smaller weight
    assert got[1] < got[0]


# --- construction -----------------------------------------------------------

def test_model_input_and_output_shapes():
    model = build_cnn(N_FEATURES, seed=42)
    assert model.input_shape == (None, N_FEATURES, CNN_INPUT_CHANNELS)
    assert model.output_shape == (None, 1)


def test_architecture_is_a_genuine_1d_cnn():
    model = build_cnn(N_FEATURES, filters=(32, 64), kernel_size=3, seed=42)
    names = [layer.__class__.__name__ for layer in model.layers]
    assert names.count("Conv1D") == 2
    assert "GlobalAveragePooling1D" in names
    assert "Dropout" in names
    assert model.get_layer("conv1").filters == 32
    assert model.get_layer("conv2").filters == 64
    assert model.get_layer("conv1").kernel_size == (3,)
    assert model.get_layer("output").activation.__name__ == "sigmoid"


def test_same_padding_keeps_the_feature_axis_intact():
    """kernel_size=5 must remain valid on a short 67-position axis."""
    model = build_cnn(N_FEATURES, kernel_size=5, seed=42)
    assert model.get_layer("conv2").output.shape[1] == N_FEATURES


def test_hyperparameters_are_applied():
    model = build_cnn(N_FEATURES, filters=(64, 128), kernel_size=5,
                      dropout=0.2, learning_rate=3e-4, seed=42)
    assert model.get_layer("conv1").filters == 64
    assert model.get_layer("conv2").filters == 128
    assert model.get_layer("dropout").rate == pytest.approx(0.2)
    assert float(model.optimizer.learning_rate.numpy()) == pytest.approx(3e-4)


def test_model_is_compact():
    """A deliberately small architecture, not an over-deep network."""
    assert build_cnn(N_FEATURES, seed=42).count_params() < 100_000


# --- training / inference on a small fixture --------------------------------

@pytest.fixture(scope="module")
def tiny_data():
    rng = np.random.default_rng(0)
    n = 400
    y = (rng.random(n) < 0.6).astype(np.int8)
    X = rng.normal(size=(n, N_FEATURES)).astype(np.float32)
    X[y == 1] += 0.7  # a learnable signal
    return reshape_for_conv1d(X), y


def test_trains_and_produces_valid_probabilities(tiny_data):
    Z, y = tiny_data
    model = build_cnn(N_FEATURES, seed=42)
    model.fit(Z, y, epochs=1, batch_size=64, verbose=0,
              class_weight=balanced_class_weight(y))
    scores = model.predict(Z, batch_size=128, verbose=0).ravel()

    assert scores.shape == (len(y),)
    assert np.isfinite(scores).all()
    assert (scores >= 0).all() and (scores <= 1).all()  # sigmoid output


def test_training_is_deterministic_with_the_configured_seed(tiny_data):
    Z, y = tiny_data
    weights = balanced_class_weight(y)

    def run():
        set_seeds(42)
        m = build_cnn(N_FEATURES, seed=42)
        m.fit(Z, y, epochs=1, batch_size=64, verbose=0, shuffle=False,
              class_weight=weights)
        return m.predict(Z, batch_size=128, verbose=0).ravel()

    np.testing.assert_allclose(run(), run(), rtol=1e-5, atol=1e-6)


def test_describe_cnn_records_reproducibility_fields():
    model = build_cnn(N_FEATURES, filters=(32, 64), kernel_size=3,
                      dropout=0.3, learning_rate=1e-3, seed=42)
    info = describe_cnn(model, {})

    assert info["input_shape"] == [N_FEATURES, CNN_INPUT_CHANNELS]
    assert info["filters"] == [32, 64]
    assert info["kernel_size"] == 3
    assert info["loss"] == "binary_crossentropy"
    assert info["optimizer"] == "Adam"
    assert info["tensorflow_version"]
    assert info["keras_version"]
    assert info["total_parameters"] > 0


# --- the locked operating-point protocol applies to CNN scores --------------

def test_fpr_constrained_threshold_works_on_sigmoid_scores(tiny_data):
    from evaluation.metrics import compute_metrics
    from evaluation.thresholds import select_threshold_at_fpr

    Z, y = tiny_data
    model = build_cnn(N_FEATURES, seed=42)
    model.fit(Z, y, epochs=2, batch_size=64, verbose=0,
              class_weight=balanced_class_weight(y))
    scores = model.predict(Z, batch_size=128, verbose=0).ravel()

    result = select_threshold_at_fpr(y, scores, 0.01)
    assert 0.0 <= result["threshold"] <= 1.0        # a probability
    pred = (scores >= result["threshold"]).astype(np.int8)
    assert compute_metrics(y, pred)["fpr"] <= 0.01 + 1e-9


def test_declared_input_width_is_the_canonical_feature_count():
    """The CNN is built for exactly the Stage D 67-feature vector."""
    model = build_cnn(N_FEATURES, seed=42)
    assert model.input_shape == (None, N_FEATURES, CNN_INPUT_CHANNELS)


def test_conv1d_stack_is_length_agnostic_at_inference():
    """Pins a real robustness difference vs RF/SVM.

    `Conv1D(padding="same")` preserves the axis length and
    `GlobalAveragePooling1D` collapses it, so the network accepts ANY
    feature-axis width at inference instead of raising the way RF and SVM
    do on a wrong-width matrix. Shape discipline for the CNN therefore
    has to come from the caller, which is why `train_cnn.py` asserts the
    reshape against the Stage D matrix. Recorded so the behaviour cannot
    change silently.
    """
    model = build_cnn(N_FEATURES, seed=42)
    rng = np.random.default_rng(1)
    for width in (N_FEATURES, N_FEATURES + 1):
        Z = reshape_for_conv1d(rng.normal(size=(4, width)).astype(np.float32))
        assert model.predict(Z, verbose=0).shape == (4, 1)


def test_metadata_columns_are_absent_from_the_canonical_feature_list():
    """The real leakage guard: metadata never reaches the feature vector."""
    from fixtures import synthetic_config
    from preprocessing.features import get_feature_columns

    features = get_feature_columns(synthetic_config())
    for column in ("Attack Type", "Attack Tool", "Label", "Unnamed: 0",
                   "Seq", "Offset"):
        assert column not in features
