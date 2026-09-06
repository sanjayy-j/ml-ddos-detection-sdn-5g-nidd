"""Stage F tests — Random Forest model.

Uses the synthetic 5G-NIDD-shaped fixture and the real Stage D pipeline, so
no part of this requires the 263 MB Combined.csv.
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier

from fixtures import make_synthetic_5gnidd, synthetic_config
from models.random_forest import build_random_forest, describe_forest
from preprocessing.features import build_feature_frame, get_feature_columns
from preprocessing.pipeline import prepare_m1_dataset


@pytest.fixture(scope="module")
def prepared():
    df = make_synthetic_5gnidd(n_blocks=4, rows_per_block=400, seed=0)
    config = synthetic_config()
    return prepare_m1_dataset(df, config), config, df


# --- construction -----------------------------------------------------------

def test_model_initialises_from_config():
    config = synthetic_config()
    config["models"]["random_forest"] = {
        "n_estimators": 25, "max_depth": 7, "class_weight": "balanced",
        "random_state": 42, "n_jobs": 1,
    }
    model = build_random_forest(config)

    assert isinstance(model, RandomForestClassifier)
    assert model.n_estimators == 25
    assert model.max_depth == 7
    assert model.class_weight == "balanced"
    assert model.random_state == 42


def test_overrides_apply_without_touching_seed_or_class_weight():
    config = synthetic_config()
    config["models"]["random_forest"] = {
        "n_estimators": 10, "class_weight": "balanced",
        "random_state": 42, "n_jobs": 1,
    }
    model = build_random_forest(config, max_depth=5, min_samples_leaf=9)

    assert model.max_depth == 5
    assert model.min_samples_leaf == 9
    assert model.class_weight == "balanced"   # not overridden by the grid
    assert model.random_state == 42


def test_class_weight_balanced_is_the_default_strategy():
    config = synthetic_config()
    config["models"]["random_forest"] = {"n_estimators": 5, "n_jobs": 1}
    assert build_random_forest(config).class_weight == "balanced"


# --- training on the Stage D representation ---------------------------------

def test_accepts_stage_d_feature_matrix_and_dimensions(prepared):
    data, _, _ = prepared
    model = build_random_forest(
        {"models": {"random_forest": {"n_estimators": 15, "n_jobs": 1}}, "seed": 42})
    model.fit(data.X["train"], data.y["train"])

    assert model.n_features_in_ == data.X["train"].shape[1]
    assert model.n_features_in_ == len(data.feature_names)
    assert list(model.classes_) == [0, 1]


def test_prediction_shapes_and_valid_probabilities(prepared):
    data, _, _ = prepared
    model = build_random_forest(
        {"models": {"random_forest": {"n_estimators": 15, "n_jobs": 1}}, "seed": 42})
    model.fit(data.X["train"], data.y["train"])

    X_test = data.X["test"]
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)

    assert pred.shape == (len(X_test),)
    assert set(np.unique(pred)) <= {0, 1}
    assert proba.shape == (len(X_test), 2)
    assert np.isfinite(proba).all()
    assert (proba >= 0).all() and (proba <= 1).all()
    np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-9)


def test_no_nan_or_inf_in_predictions(prepared):
    data, _, _ = prepared
    model = build_random_forest(
        {"models": {"random_forest": {"n_estimators": 10, "n_jobs": 1}}, "seed": 42})
    model.fit(data.X["train"], data.y["train"])
    scores = model.predict_proba(data.X["test"])[:, 1]
    assert np.isfinite(scores).all()
    assert not np.isnan(scores).any()


def test_training_is_deterministic_with_the_configured_seed(prepared):
    data, _, _ = prepared
    cfg = {"models": {"random_forest": {"n_estimators": 20, "n_jobs": 1}}, "seed": 42}
    a = build_random_forest(cfg).fit(data.X["train"], data.y["train"])
    b = build_random_forest(cfg).fit(data.X["train"], data.y["train"])

    np.testing.assert_array_equal(
        a.predict_proba(data.X["test"]), b.predict_proba(data.X["test"]))
    np.testing.assert_array_equal(a.feature_importances_, b.feature_importances_)


def test_different_seeds_give_different_forests(prepared):
    data, _, _ = prepared
    a = build_random_forest(
        {"models": {"random_forest": {"n_estimators": 20, "n_jobs": 1,
                                      "random_state": 1}}}).fit(
        data.X["train"], data.y["train"])
    b = build_random_forest(
        {"models": {"random_forest": {"n_estimators": 20, "n_jobs": 1,
                                      "random_state": 2}}}).fit(
        data.X["train"], data.y["train"])
    assert not np.array_equal(a.feature_importances_, b.feature_importances_)


def test_describe_forest_reports_structure(prepared):
    data, _, _ = prepared
    model = build_random_forest(
        {"models": {"random_forest": {"n_estimators": 12, "max_depth": 6,
                                      "n_jobs": 1}}, "seed": 42})
    model.fit(data.X["train"], data.y["train"])
    info = describe_forest(model)

    assert info["n_estimators"] == 12
    assert info["max_depth_reached"] <= 6
    assert info["total_nodes"] > 0


# --- the metadata columns must never reach the model ------------------------

@pytest.mark.parametrize("column", ["Attack Type", "Attack Tool"])
def test_attack_metadata_never_enters_training_matrix(prepared, column):
    data, config, df = prepared

    # not in the configured feature list
    assert column not in get_feature_columns(config)
    # not in the frame handed to the preprocessor
    assert column not in build_feature_frame(df, config).columns
    # not in any encoded output feature name
    assert not any(name == column or name.startswith(column + "_")
                   for name in data.feature_names)


def test_identifier_columns_never_enter_training_matrix(prepared):
    data, config, df = prepared
    for column in ("Unnamed: 0", "Seq", "Offset", "Label"):
        assert column not in build_feature_frame(df, config).columns
        assert not any(name == column or name.startswith(column + "_")
                       for name in data.feature_names)


def test_model_input_width_equals_locked_feature_count(prepared):
    """Training must consume exactly the Stage D representation."""
    data, _, _ = prepared
    model = build_random_forest(
        {"models": {"random_forest": {"n_estimators": 5, "n_jobs": 1}}, "seed": 42})
    model.fit(data.X["train"], data.y["train"])
    assert model.n_features_in_ == data.X["train"].shape[1]

    # a matrix with an extra column must be rejected at predict time
    wrong = np.hstack([data.X["test"], np.ones((len(data.X["test"]), 1),
                                               dtype=np.float32)])
    with pytest.raises(ValueError):
        model.predict(wrong)


# --- regression: grid values that survive a DataFrame round-trip -----------

def test_is_unlimited_handles_nan_from_dataframe_roundtrip():
    """max_depth=None becomes float NaN once the search table is built.

    The column mixes None with ints, so pandas casts it to float64 and
    `NaN in (None, ...)` is False. Guarding on NaN explicitly prevents an
    `int(NaN)` crash during tie-breaking.
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
    from train_random_forest import _is_unlimited

    import numpy as np
    import pandas as pd

    assert _is_unlimited(None)
    assert _is_unlimited(float("nan"))
    assert _is_unlimited(np.nan)
    assert _is_unlimited("config")
    assert not _is_unlimited(20)
    assert not _is_unlimited(0.5)

    # the actual failure mode: None + ints in one column -> float64 NaN
    frame = pd.DataFrame({"max_depth": [None, 20, 30]})
    assert frame["max_depth"].dtype == "float64"
    ranks = frame["max_depth"].apply(
        lambda d: 10 ** 6 if _is_unlimited(d) else int(d))
    assert list(ranks) == [10 ** 6, 20, 30]
