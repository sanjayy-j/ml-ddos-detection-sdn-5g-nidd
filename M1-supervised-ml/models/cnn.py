"""Stage H — 1-D CNN for M1 (TensorFlow/Keras).

INPUT REPRESENTATION — read this before interpreting any result.

The Stage D canonical representation is a **tabular** 67-feature vector,
not a temporal signal. It is reshaped to `(67, 1)` purely so a `Conv1D`
stack can be applied along the feature axis:

    (samples, 67)  ->  (samples, 67, 1)

The reshape is a pure `np.reshape`, so the Stage D feature ordering is
preserved exactly and no feature is reordered. Consequences that must be
stated whenever this model is discussed:

  * `Conv1D` here does **not** perform temporal convolution and does not
    model packet or flow sequences over time.
  * Convolution assumes neighbouring positions are related; for a tabular
    vector that adjacency is an artifact of the column order, so feature
    ordering can influence what the kernels can combine.
  * This experiment evaluates a convolutional architecture over a fixed
    feature vector. It says nothing about CNNs for genuine temporal
    network-sequence modelling.

Class weighting matches RF and SVM: sklearn's "balanced" formula, so all
three model families share one imbalance strategy.
"""

from __future__ import annotations

from typing import Any

import numpy as np

CNN_INPUT_CHANNELS = 1


def reshape_for_conv1d(X: np.ndarray) -> np.ndarray:
    """(samples, n_features) -> (samples, n_features, 1), order preserved."""
    X = np.asarray(X)
    if X.ndim != 2:
        raise ValueError(f"expected a 2-D matrix, got shape {X.shape}")
    return X.reshape(X.shape[0], X.shape[1], CNN_INPUT_CHANNELS)


def balanced_class_weight(y: np.ndarray) -> dict[int, float]:
    """sklearn's 'balanced' weights as a Keras class_weight dict.

    n_samples / (n_classes * count(class)) — identical to the
    `class_weight='balanced'` used by the RF and the SVM.
    """
    y = np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    total = len(y)
    return {
        int(c): float(total / (len(classes) * n)) for c, n in zip(classes, counts)
    }


def set_seeds(seed: int) -> None:
    """Seed Python, NumPy and TensorFlow RNGs."""
    import keras

    keras.utils.set_random_seed(seed)


def build_cnn(
    n_features: int,
    filters: tuple[int, int] = (32, 64),
    kernel_size: int = 3,
    dropout: float = 0.3,
    learning_rate: float = 1e-3,
    dense_units: int = 64,
    seed: int = 42,
) -> Any:
    """Compact 1-D CNN over the ordered canonical feature vector.

    Input (n_features, 1)
      -> Conv1D(filters[0], kernel_size, ReLU, same padding)
      -> Conv1D(filters[1], kernel_size, ReLU, same padding)
      -> GlobalAveragePooling1D
      -> Dense(dense_units, ReLU) -> Dropout -> Dense(1, sigmoid)

    'same' padding keeps the 67-position axis intact through both
    convolutions, so a kernel_size of 5 remains valid without shrinking
    the short feature axis.
    """
    import keras
    from keras import layers

    set_seeds(seed)
    model = keras.Sequential(
        [
            layers.Input(shape=(n_features, CNN_INPUT_CHANNELS)),
            layers.Conv1D(filters[0], kernel_size, activation="relu",
                          padding="same", name="conv1"),
            layers.Conv1D(filters[1], kernel_size, activation="relu",
                          padding="same", name="conv2"),
            layers.GlobalAveragePooling1D(name="gap"),
            layers.Dense(dense_units, activation="relu", name="dense"),
            layers.Dropout(dropout, seed=seed, name="dropout"),
            layers.Dense(1, activation="sigmoid", name="output"),
        ],
        name="m1_cnn_1d",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        # PR-AUC is the project's primary validation selection metric
        metrics=[
            keras.metrics.AUC(curve="PR", name="pr_auc"),
            keras.metrics.AUC(curve="ROC", name="roc_auc"),
        ],
    )
    return model


def describe_cnn(model: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Architecture/reproducibility summary for the run record."""
    import keras
    import tensorflow as tf

    conv1, conv2 = model.get_layer("conv1"), model.get_layer("conv2")
    return {
        "architecture": "Conv1D -> Conv1D -> GlobalAvgPool1D -> Dense -> "
                        "Dropout -> Dense(sigmoid)",
        "input_shape": list(model.input_shape[1:]),
        "filters": [int(conv1.filters), int(conv2.filters)],
        "kernel_size": int(conv1.kernel_size[0]),
        "padding": conv1.padding,
        "dense_units": int(model.get_layer("dense").units),
        "dropout": float(model.get_layer("dropout").rate),
        "loss": "binary_crossentropy",
        "optimizer": "Adam",
        "learning_rate": float(model.optimizer.learning_rate.numpy()),
        "total_parameters": int(model.count_params()),
        "tensorflow_version": tf.__version__,
        "keras_version": keras.__version__,
    }
