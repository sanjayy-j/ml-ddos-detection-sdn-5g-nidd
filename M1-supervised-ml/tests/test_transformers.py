"""Stage D tests — preprocessing transformations."""

import numpy as np
import pytest

from fixtures import make_synthetic_5gnidd, synthetic_config
from preprocessing.features import build_feature_frame, build_target
from preprocessing.splitting import detect_capture_blocks, make_split
from preprocessing.transformers import (
    SkewedLog1pTransformer,
    build_preprocessor,
    get_output_feature_names,
)


def _train_val(seed=0):
    df = make_synthetic_5gnidd(seed=seed)
    config = synthetic_config()
    y = build_target(df, config).to_numpy()
    blocks = detect_capture_blocks(df, config)
    assignment = make_split(y, blocks, config)
    features = build_feature_frame(df, config)
    return config, features[assignment == "train"], features[assignment == "val"]


# --- skew-gated log1p -------------------------------------------------------

def test_log1p_applied_only_to_skewed_non_negative_columns():
    rng = np.random.default_rng(0)
    heavy = rng.lognormal(3, 3, size=2000)      # very skewed, non-negative
    gaussian = rng.normal(10, 2, size=2000)     # low skew
    negative = -np.abs(rng.lognormal(3, 3, size=2000))  # skewed but negative
    X = np.column_stack([heavy, gaussian, negative])

    transformer = SkewedLog1pTransformer(skew_threshold=2.0).fit(X)

    assert transformer.log_mask_[0]        # heavy-tailed, non-negative
    assert not transformer.log_mask_[1]    # not skewed enough
    assert not transformer.log_mask_[2]    # negative => log1p unsafe

    out = transformer.transform(X)
    np.testing.assert_allclose(out[:, 0], np.log1p(heavy))
    np.testing.assert_allclose(out[:, 1], gaussian)
    np.testing.assert_allclose(out[:, 2], negative)


def test_log1p_constant_column_is_not_transformed():
    X = np.column_stack([np.full(100, 5.0), np.arange(100.0)])
    transformer = SkewedLog1pTransformer().fit(X)
    assert not transformer.log_mask_[0]


def test_log1p_rejects_wrong_width():
    transformer = SkewedLog1pTransformer().fit(np.ones((10, 3)))
    with pytest.raises(ValueError, match="Expected 3 columns"):
        transformer.transform(np.ones((10, 2)))


# --- fitted preprocessor ----------------------------------------------------

def test_preprocessing_is_fitted_on_training_data_only():
    config, train, val = _train_val()
    preprocessor = build_preprocessor(config)
    preprocessor.fit(train)

    scaler = preprocessor.named_transformers_["numeric"].named_steps["scale"]
    seen = scaler.n_samples_seen_
    seen = int(np.max(seen)) if np.ndim(seen) else int(seen)
    assert seen == len(train)

    # transforming validation data must not change the fitted statistics
    before = scaler.mean_.copy()
    preprocessor.transform(val)
    np.testing.assert_array_equal(scaler.mean_, before)


def test_transform_is_deterministic():
    config, train, val = _train_val()
    preprocessor = build_preprocessor(config).fit(train)

    first = preprocessor.transform(val)
    second = preprocessor.transform(val)
    np.testing.assert_array_equal(first, second)


def test_output_contains_no_nan_or_infinite_values():
    config, train, val = _train_val()
    preprocessor = build_preprocessor(config).fit(train)

    for matrix in (preprocessor.transform(train), preprocessor.transform(val)):
        assert np.isfinite(matrix).all()


def test_feature_names_are_deterministic_and_unique():
    config, train, _ = _train_val()
    preprocessor = build_preprocessor(config).fit(train)
    names = get_output_feature_names(preprocessor)

    assert len(names) == len(set(names))
    assert len(names) == preprocessor.transform(train).shape[1]

    again = build_preprocessor(config).fit(train)
    assert get_output_feature_names(again) == names


def test_categorical_encoding_is_one_hot_and_not_ordinal():
    config, train, _ = _train_val()
    preprocessor = build_preprocessor(config).fit(train)
    names = get_output_feature_names(preprocessor)
    matrix = preprocessor.transform(train)

    proto_columns = [i for i, n in enumerate(names) if n.startswith("Proto_")]
    assert len(proto_columns) > 1, "Proto must expand into one-hot columns"
    block = matrix[:, proto_columns]
    assert set(np.unique(block)) <= {0.0, 1.0}
    # exactly one active level per row
    np.testing.assert_array_equal(block.sum(axis=1), np.ones(len(block)))


def test_unseen_category_is_handled_without_error():
    config, train, val = _train_val()
    preprocessor = build_preprocessor(config).fit(train)

    modified = val.copy()
    modified.loc[modified.index[0], "Proto"] = "totally-new-protocol"
    matrix = preprocessor.transform(modified)

    assert np.isfinite(matrix).all()
    names = get_output_feature_names(preprocessor)
    proto_columns = [i for i, n in enumerate(names) if n.startswith("Proto_")]
    # unknown category => all-zero one-hot block, never a new column
    assert matrix[0, proto_columns].sum() == 0.0


def test_missing_categorical_becomes_explicit_category_not_indicator():
    config, train, _ = _train_val()
    preprocessor = build_preprocessor(config).fit(train)
    names = get_output_feature_names(preprocessor)

    # dDSb is missing whenever no reverse traffic was observed
    assert any(n.startswith("dDSb_") for n in names)
    # no generic missingness-indicator columns were added
    assert not any("missingindicator" in n.lower() for n in names)


def test_numeric_columns_are_standardised():
    config, train, _ = _train_val()
    preprocessor = build_preprocessor(config).fit(train)
    names = get_output_feature_names(preprocessor)
    matrix = preprocessor.transform(train)

    numeric_columns = [
        i for i, n in enumerate(names)
        if not any(n.startswith(f"{c}_") for c in
                   config["schema"]["categorical_columns"])
    ]
    block = matrix[:, numeric_columns]
    np.testing.assert_allclose(block.mean(axis=0), 0, atol=1e-4)
