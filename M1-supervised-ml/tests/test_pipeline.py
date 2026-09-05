"""Stage D tests — end-to-end preparation, artifacts and leakage audit."""

import numpy as np
import pytest

from fixtures import make_synthetic_5gnidd, synthetic_config
from preprocessing.pipeline import (
    load_processed,
    make_svm_subsample,
    prepare_m1_dataset,
    run_leakage_audit,
    save_artifacts,
)
from preprocessing.splitting import SPLIT_NAMES


@pytest.fixture(scope="module")
def prepared():
    df = make_synthetic_5gnidd(n_blocks=4, rows_per_block=400, seed=0)
    config = synthetic_config()
    return prepare_m1_dataset(df, config), config


# --- end-to-end -------------------------------------------------------------

def test_pipeline_produces_all_three_splits(prepared):
    data, _ = prepared
    for name in SPLIT_NAMES:
        assert data.X[name].shape[0] == data.y[name].shape[0]
        assert data.X[name].shape[0] > 0
        assert data.X[name].shape[1] == len(data.feature_names)


def test_all_matrices_are_finite(prepared):
    data, _ = prepared
    for name in SPLIT_NAMES:
        assert np.isfinite(data.X[name]).all()
        assert not np.isnan(data.X[name]).any()


def test_matrices_are_float32_and_targets_binary(prepared):
    data, _ = prepared
    for name in SPLIT_NAMES:
        assert data.X[name].dtype == np.float32
        assert set(np.unique(data.y[name])) <= {0, 1}


def test_cnn_input_shape_is_fixed_and_matches_feature_count(prepared):
    data, _ = prepared
    assert data.cnn_input_shape == (len(data.feature_names), 1)
    # the CNN reshape must be consistent with the produced matrices
    n_features = data.X["train"].shape[1]
    reshaped = data.X["train"].reshape(-1, *data.cnn_input_shape)
    assert reshaped.shape == (len(data.X["train"]), n_features, 1)


def test_svm_representation_is_finite_and_scaled(prepared):
    data, _ = prepared
    train = data.X["train"]
    assert np.isfinite(train).all()
    # standardised numeric block keeps magnitudes bounded for the RBF kernel
    assert np.abs(train).max() < 1e6


def test_preparation_is_reproducible():
    df = make_synthetic_5gnidd(n_blocks=3, rows_per_block=300, seed=1)
    first = prepare_m1_dataset(df, synthetic_config())
    second = prepare_m1_dataset(df, synthetic_config())

    assert first.feature_names == second.feature_names
    for name in SPLIT_NAMES:
        np.testing.assert_array_equal(first.X[name], second.X[name])
        np.testing.assert_array_equal(first.y[name], second.y[name])


# --- SVM strategy -----------------------------------------------------------

def test_svm_subsample_is_stratified_and_reproducible():
    rng = np.random.default_rng(0)
    y = (rng.random(10000) < 0.6).astype(np.int8)

    first = make_svm_subsample(y, 1000, seed=42)
    second = make_svm_subsample(y, 1000, seed=42)

    np.testing.assert_array_equal(first, second)
    assert len(first) == pytest.approx(1000, abs=2)
    # class proportion preserved
    assert abs(y[first].mean() - y.mean()) < 0.02
    # indices are unique and within range
    assert len(set(first.tolist())) == len(first)
    assert first.max() < len(y)


def test_svm_subsample_returns_all_rows_when_not_limiting():
    y = np.array([0, 1, 0, 1], dtype=np.int8)
    np.testing.assert_array_equal(make_svm_subsample(y, 0, 42), np.arange(4))
    np.testing.assert_array_equal(make_svm_subsample(y, 99, 42), np.arange(4))


def test_svm_subsample_drawn_from_training_only(prepared):
    data, _ = prepared
    indices = data.svm_train_indices
    assert indices.max() < len(data.y["train"])


# --- duplicates -------------------------------------------------------------

def test_duplicate_report_present_and_does_not_drop_rows(prepared):
    data, config = prepared
    duplicates = data.metadata["duplicates"]

    assert duplicates["n_rows"] == sum(
        len(data.y[name]) for name in SPLIT_NAMES
    ) + data.metadata["n_purged_rows"]
    assert "bayes_error_pct" in duplicates
    assert "rows_whose_vector_appears_in_another_split" in duplicates


def test_dropping_duplicates_is_explicit_opt_in():
    df = make_synthetic_5gnidd(n_blocks=2, rows_per_block=100)
    config = synthetic_config()
    config["duplicates"]["drop_exact_duplicates"] = True
    with pytest.raises(NotImplementedError):
        prepare_m1_dataset(df, config)


# --- leakage audit ----------------------------------------------------------

def test_leakage_audit_passes(prepared):
    data, config = prepared
    audit = run_leakage_audit(data, config)
    failures = [c for c in audit["checks"] if c["status"] != "PASS"]
    assert audit["all_passed"], f"failed checks: {failures}"


def test_no_forbidden_column_survives_into_output_features(prepared):
    data, config = prepared
    schema = config["schema"]
    banned = (
        [schema["label_column"]]
        + schema["metadata_columns"]
        + schema["identifier_columns"]
        + schema["drop_columns"]
    )
    for column in banned:
        assert not any(
            name == column or name.startswith(f"{column}_")
            for name in data.feature_names
        ), f"{column} leaked into the feature matrix"


def test_class_prior_stable_across_splits(prepared):
    data, _ = prepared
    priors = [data.metadata["splits"][n]["malicious_pct"] for n in SPLIT_NAMES]
    assert max(priors) - min(priors) < 1.0


# --- artifacts --------------------------------------------------------------

def test_artifacts_roundtrip(tmp_path, prepared):
    data, config = prepared
    config = dict(config)
    config["output"] = {
        "results_dir": "results",
        "processed_dir": "processed",
    }
    audit = run_leakage_audit(data, config)
    written = save_artifacts(data, config, tmp_path, audit=audit)

    for key in ("X_train", "y_train", "preprocessor", "split_manifest",
                "feature_order", "preprocessing_metadata", "leakage_audit"):
        assert key in written

    reloaded = load_processed(config, tmp_path)
    for name in SPLIT_NAMES:
        np.testing.assert_array_equal(reloaded["X"][name], data.X[name])
        np.testing.assert_array_equal(reloaded["y"][name], data.y[name])

    # the reloaded preprocessor must reproduce the same transformation
    assert reloaded["preprocessor"] is not None
    np.testing.assert_array_equal(
        reloaded["svm_train_indices"], data.svm_train_indices
    )


def test_reloaded_preprocessor_transforms_identically(tmp_path):
    df = make_synthetic_5gnidd(n_blocks=2, rows_per_block=200, seed=3)
    config = synthetic_config()
    config["output"] = {"results_dir": "results", "processed_dir": "processed"}
    data = prepare_m1_dataset(df, config)
    save_artifacts(data, config, tmp_path)

    from preprocessing.features import build_feature_frame

    reloaded = load_processed(config, tmp_path)["preprocessor"]
    features = build_feature_frame(df, config)
    np.testing.assert_allclose(
        reloaded.transform(features).astype(np.float32),
        data.preprocessor.transform(features).astype(np.float32),
    )
