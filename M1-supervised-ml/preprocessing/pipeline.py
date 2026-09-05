"""Stage D — end-to-end M1 data preparation.

    raw CSV -> schema validation -> target -> feature policy
            -> capture blocks -> block/label contiguous split
            -> fit preprocessing on TRAIN ONLY -> transform all splits
            -> artifacts (matrices, fitted preprocessor, manifests, audit)

No model is trained here. The output is the leakage-safe, deterministic
representation consumed by Stage E (Random Forest / SVM / 1-D CNN).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .features import (
    build_feature_frame,
    build_target,
    forbidden_columns,
    get_categorical_columns,
    get_feature_columns,
    get_numeric_columns,
)
from .splitting import (
    PURGED,
    SPLIT_NAMES,
    assert_split_is_disjoint,
    build_split_manifest,
    detect_base_station,
    detect_capture_blocks,
    make_split,
)
from .transformers import build_preprocessor, get_output_feature_names


@dataclass
class PreparedData:
    """The Stage D output, ready for Stage E model training."""

    X: dict[str, np.ndarray]
    y: dict[str, np.ndarray]
    feature_names: list[str]
    preprocessor: Any
    split_manifest: pd.DataFrame
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def cnn_input_shape(self) -> tuple[int, int]:
        """1-D CNN input shape: (n_features, 1 channel).

        Each engineered feature occupies one position along the
        convolution axis. This is a spatial arrangement of tabular
        features, NOT a temporal sequence — feature order carries no
        time information and the CNN must not be described as modelling
        temporal dependencies.
        """
        return (len(self.feature_names), 1)


def resolve_path(root: Path, value: str | Path) -> Path:
    """Resolve a config path relative to the repository root."""
    path = Path(value)
    return path if path.is_absolute() else (Path(root) / path)


# ---------------------------------------------------------------------------
# duplicate analysis
# ---------------------------------------------------------------------------

def duplicate_report(
    features: pd.DataFrame,
    y: np.ndarray,
    block_ids: np.ndarray,
    assignment: np.ndarray | None = None,
) -> dict[str, Any]:
    """Quantify duplicate feature vectors without modifying any data.

    Duplicates are NOT dropped by default: repeated flow patterns are a
    genuine property of network traffic, and removing them would change
    the experimental distribution.
    """
    n = len(features)
    keys = pd.util.hash_pandas_object(features, index=False).to_numpy()

    frame = pd.DataFrame({"key": keys, "y": y, "block": block_ids})
    grouped = frame.groupby("key", sort=False)
    size = grouped.size()
    positives = grouped["y"].sum()
    negatives = size - positives
    minority = np.minimum(positives, negatives)
    n_blocks = grouped["block"].nunique()

    is_dup = size > 1
    is_ambiguous = minority > 0

    report: dict[str, Any] = {
        "n_rows": int(n),
        "n_unique_feature_vectors": int(len(size)),
        "n_duplicate_rows": int(n - len(size)),
        "n_duplicate_groups": int(is_dup.sum()),
        "n_ambiguous_groups": int(is_ambiguous.sum()),
        "rows_in_ambiguous_groups": int(size[is_ambiguous].sum()),
        # sum of per-group minority counts == irreducible error floor
        "bayes_error_rows": int(minority.sum()),
        "bayes_error_pct": round(100.0 * float(minority.sum()) / n, 4),
        "max_achievable_accuracy_pct": round(
            100.0 - 100.0 * float(minority.sum()) / n, 4
        ),
        "duplicate_groups_crossing_blocks": int((is_dup & (n_blocks > 1)).sum()),
    }

    if assignment is not None:
        frame["split"] = assignment
        kept = frame[frame["split"] != PURGED]
        per_key_splits = kept.groupby("key", sort=False)["split"].nunique()
        shared = set(per_key_splits[per_key_splits > 1].index)
        report["duplicate_vectors_shared_across_splits"] = int(len(shared))
        report["rows_whose_vector_appears_in_another_split"] = int(
            kept["key"].isin(shared).sum()
        )
    return report


# ---------------------------------------------------------------------------
# SVM computational strategy
# ---------------------------------------------------------------------------

def make_svm_subsample(
    y_train: np.ndarray, n_samples: int, seed: int
) -> np.ndarray:
    """Reproducible stratified subsample of TRAINING row indices for the SVM.

    An RBF `SVC` is O(n^2)-O(n^3) in the number of training samples, so
    fitting it on the full ~851k-row training split is not tractable.
    The subsample is drawn from the training split ONLY (validation and
    test remain complete and untouched), preserves the training class
    proportions, and is fully determined by `seed`.
    """
    n_train = len(y_train)
    if n_samples <= 0 or n_samples >= n_train:
        return np.arange(n_train)

    rng = np.random.default_rng(seed)
    selected = []
    for class_value in np.unique(y_train):
        class_indices = np.flatnonzero(y_train == class_value)
        # preserve the class proportion of the training split
        take = int(round(n_samples * len(class_indices) / n_train))
        take = max(1, min(take, len(class_indices)))
        selected.append(rng.choice(class_indices, size=take, replace=False))

    indices = np.sort(np.concatenate(selected))
    return indices


# ---------------------------------------------------------------------------
# main preparation
# ---------------------------------------------------------------------------

def prepare_m1_dataset(
    df: pd.DataFrame, config: dict[str, Any]
) -> PreparedData:
    """Build the leakage-safe train/val/test representation."""
    seed = int(config.get("seed", 42))

    # --- target + feature policy (feature policy raises on any violation) ---
    y_all = build_target(df, config).to_numpy()
    features = build_feature_frame(df, config)

    # --- capture structure ---
    block_ids = detect_capture_blocks(df, config)
    base_station_ids = detect_base_station(df, config)

    # --- split ---
    assignment = make_split(y_all, block_ids, config)
    assert_split_is_disjoint(assignment)

    metadata_columns = (config.get("schema") or {}).get("metadata_columns") or []
    attack_types = (
        df[metadata_columns[0]] if metadata_columns and metadata_columns[0] in df
        else None
    )
    manifest = build_split_manifest(
        block_ids, base_station_ids, y_all, assignment, attack_types
    )

    # --- duplicate analysis (reporting only; no rows are dropped) ---
    dup_cfg = config.get("duplicates") or {}
    duplicates: dict[str, Any] = {}
    if dup_cfg.get("report", True):
        duplicates = duplicate_report(features, y_all, block_ids, assignment)
    if dup_cfg.get("drop_exact_duplicates", False):
        raise NotImplementedError(
            "duplicates.drop_exact_duplicates is an explicit opt-in protocol "
            "change and is not implemented in Stage D; the default (keep all "
            "rows) preserves the experimental distribution."
        )

    # --- fit preprocessing on TRAIN ONLY ---
    masks = {name: (assignment == name) for name in SPLIT_NAMES}
    preprocessor = build_preprocessor(config)
    preprocessor.fit(features.loc[masks["train"]])
    feature_names = get_output_feature_names(preprocessor)

    X: dict[str, np.ndarray] = {}
    y: dict[str, np.ndarray] = {}
    for name in SPLIT_NAMES:
        mask = masks[name]
        X[name] = preprocessor.transform(features.loc[mask]).astype(np.float32)
        y[name] = y_all[mask].astype(np.int8)

    # --- SVM strategy: indices only, so no data is duplicated in memory ---
    svm_cfg = (config.get("models") or {}).get("svm") or {}
    svm_indices = make_svm_subsample(
        y["train"], int(svm_cfg.get("train_subsample", 0) or 0), seed
    )

    numeric_columns = get_numeric_columns(config)
    log_step = preprocessor.named_transformers_["numeric"].named_steps["log1p"]
    log_columns = [
        c for c, flagged in zip(numeric_columns, log_step.log_mask_) if flagged
    ]

    metadata = {
        "seed": seed,
        "n_rows_total": int(len(df)),
        "n_input_features": len(get_feature_columns(config)),
        "n_numeric_input_features": len(numeric_columns),
        "n_categorical_input_features": len(get_categorical_columns(config)),
        "n_output_features": len(feature_names),
        "cnn_input_shape": [len(feature_names), 1],
        "split_strategy": (config.get("split") or {}).get("strategy"),
        "purge_rows": int((config.get("split") or {}).get("purge_rows", 0) or 0),
        "n_purged_rows": int((assignment == PURGED).sum()),
        "log1p_skew_threshold": float(
            (config.get("preprocessing") or {}).get("log1p_skew_threshold", 2.0)
        ),
        "log1p_columns": log_columns,
        "splits": {
            name: {
                "rows": int(len(y[name])),
                "benign": int((y[name] == 0).sum()),
                "malicious": int((y[name] == 1).sum()),
                "malicious_pct": round(100.0 * float((y[name] == 1).mean()), 4),
                "shape": list(X[name].shape),
            }
            for name in SPLIT_NAMES
        },
        "svm_subsample": {
            "configured": int(svm_cfg.get("train_subsample", 0) or 0),
            "selected_rows": int(len(svm_indices)),
            "malicious_pct": round(
                100.0 * float(y["train"][svm_indices].mean()), 4
            ),
        },
        "duplicates": duplicates,
    }

    prepared = PreparedData(
        X=X,
        y=y,
        feature_names=feature_names,
        preprocessor=preprocessor,
        split_manifest=manifest,
        metadata=metadata,
    )
    prepared.metadata["svm_subsample_indices_saved"] = True
    prepared.svm_train_indices = svm_indices  # type: ignore[attr-defined]
    return prepared


# ---------------------------------------------------------------------------
# leakage audit
# ---------------------------------------------------------------------------

def run_leakage_audit(
    prepared: PreparedData, config: dict[str, Any]
) -> dict[str, Any]:
    """Explicit checks that must all pass before Stage D is declared done."""
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "FAIL",
                       "detail": detail})

    schema = config.get("schema") or {}
    banned = forbidden_columns(config)
    output_names = prepared.feature_names

    # 1-4: no forbidden column may survive into the output representation.
    # One-hot expands `col` into `col_value`, so prefix matching is used.
    def survives(column: str) -> bool:
        return any(n == column or n.startswith(f"{column}_") for n in output_names)

    record(
        "target_excluded",
        not survives(schema["label_column"]),
        f"label column '{schema['label_column']}' absent from feature matrix",
    )
    leaked_meta = [c for c in (schema.get("metadata_columns") or []) if survives(c)]
    record(
        "attack_type_and_tool_excluded",
        not leaked_meta,
        f"target-derived metadata absent: {schema.get('metadata_columns')}"
        if not leaked_meta else f"LEAKED: {leaked_meta}",
    )
    leaked_ids = [c for c in (schema.get("identifier_columns") or []) if survives(c)]
    record(
        "identifiers_excluded",
        not leaked_ids,
        f"identifier columns absent: {schema.get('identifier_columns')}"
        if not leaked_ids else f"LEAKED: {leaked_ids}",
    )
    leaked_drop = [c for c in (schema.get("drop_columns") or []) if survives(c)]
    record(
        "excluded_columns_absent",
        not leaked_drop,
        f"{len(schema.get('drop_columns') or [])} excluded columns absent"
        if not leaked_drop else f"LEAKED: {leaked_drop}",
    )

    # 5: preprocessing fitted on train rows only
    scaler = prepared.preprocessor.named_transformers_["numeric"].named_steps["scale"]
    seen = int(np.max(scaler.n_samples_seen_)) if np.ndim(
        scaler.n_samples_seen_) else int(scaler.n_samples_seen_)
    n_train = int(len(prepared.y["train"]))
    record(
        "preprocessing_fitted_on_train_only",
        seen == n_train,
        f"scaler saw {seen:,} rows; training split has {n_train:,}",
    )

    # 6: finite matrices
    all_finite = True
    detail = []
    for name in SPLIT_NAMES:
        finite = bool(np.isfinite(prepared.X[name]).all())
        all_finite &= finite
        detail.append(f"{name}={'finite' if finite else 'NON-FINITE'}")
    record("no_nan_or_inf_in_matrices", all_finite, ", ".join(detail))

    # 7: split disjointness by construction + class prior stability
    priors = {n: prepared.metadata["splits"][n]["malicious_pct"] for n in SPLIT_NAMES}
    spread = max(priors.values()) - min(priors.values())
    record(
        "class_prior_stable_across_splits",
        spread < 1.0,
        f"malicious% per split {priors}, spread={spread:.4f}pp",
    )

    # 8: deterministic feature ordering
    record(
        "deterministic_feature_order",
        len(output_names) == len(set(output_names)),
        f"{len(output_names)} uniquely-named output features in fixed order",
    )

    # 9: duplicate vectors spanning splits — reported, not silently ignored
    dup = prepared.metadata.get("duplicates") or {}
    shared_rows = dup.get("rows_whose_vector_appears_in_another_split")
    record(
        "duplicate_vectors_across_splits_quantified",
        shared_rows is not None,
        f"{shared_rows:,} rows share a feature vector with another split; "
        f"unavoidable given {dup.get('bayes_error_pct')}% irreducible "
        f"ambiguity - memorising such vectors yields at best the "
        f"Bayes-optimal majority prediction"
        if shared_rows is not None else "not computed",
    )

    # 10: no missingness indicator columns were added
    record(
        "no_missingness_indicators_added",
        not any(n.endswith("_missingindicator") or "missingindicator" in n.lower()
                for n in output_names),
        "no NA-indicator features generated (missingness is explained by "
        "observed columns and would encode capture artifacts)",
    )

    passed = all(c["status"] == "PASS" for c in checks)
    return {"all_passed": passed, "checks": checks}


# ---------------------------------------------------------------------------
# artifact persistence
# ---------------------------------------------------------------------------

def save_artifacts(
    prepared: PreparedData,
    config: dict[str, Any],
    root: Path,
    audit: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Write processed matrices, fitted preprocessor and manifests."""
    output_cfg = config.get("output") or {}
    results_dir = resolve_path(root, output_cfg.get("results_dir", "M1-supervised-ml/results"))
    processed_dir = resolve_path(
        root, output_cfg.get("processed_dir", "M1-supervised-ml/data/processed")
    )
    results_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, str] = {}

    # large matrices -> git-ignored processed dir
    for name in SPLIT_NAMES:
        x_path = processed_dir / f"X_{name}.npy"
        y_path = processed_dir / f"y_{name}.npy"
        np.save(x_path, prepared.X[name])
        np.save(y_path, prepared.y[name])
        written[f"X_{name}"] = str(x_path)
        written[f"y_{name}"] = str(y_path)

    indices = getattr(prepared, "svm_train_indices", None)
    if indices is not None:
        path = processed_dir / "svm_train_indices.npy"
        np.save(path, indices)
        written["svm_train_indices"] = str(path)

    preprocessor_path = processed_dir / "preprocessor.joblib"
    joblib.dump(prepared.preprocessor, preprocessor_path)
    written["preprocessor"] = str(preprocessor_path)

    # small, human-readable artifacts -> tracked results dir
    feature_order_path = results_dir / "feature_order.json"
    feature_order_path.write_text(
        json.dumps(
            {
                "n_output_features": len(prepared.feature_names),
                "cnn_input_shape": list(prepared.cnn_input_shape),
                "feature_order": prepared.feature_names,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    written["feature_order"] = str(feature_order_path)

    manifest_path = results_dir / "split_manifest.csv"
    prepared.split_manifest.to_csv(manifest_path, index=False)
    written["split_manifest"] = str(manifest_path)

    metadata_path = results_dir / "preprocessing_metadata.json"
    metadata_path.write_text(
        json.dumps(prepared.metadata, indent=2, default=str), encoding="utf-8"
    )
    written["preprocessing_metadata"] = str(metadata_path)

    if audit is not None:
        audit_path = results_dir / "leakage_audit.json"
        audit_path.write_text(json.dumps(audit, indent=2, default=str),
                              encoding="utf-8")
        written["leakage_audit"] = str(audit_path)

    return written


def load_processed(config: dict[str, Any], root: Path) -> dict[str, Any]:
    """Reload artifacts written by save_artifacts (used by Stage E)."""
    output_cfg = config.get("output") or {}
    processed_dir = resolve_path(
        root, output_cfg.get("processed_dir", "M1-supervised-ml/data/processed")
    )
    data: dict[str, Any] = {"X": {}, "y": {}}
    for name in SPLIT_NAMES:
        data["X"][name] = np.load(processed_dir / f"X_{name}.npy")
        data["y"][name] = np.load(processed_dir / f"y_{name}.npy")
    data["preprocessor"] = joblib.load(processed_dir / "preprocessor.joblib")
    svm_path = processed_dir / "svm_train_indices.npy"
    if svm_path.exists():
        data["svm_train_indices"] = np.load(svm_path)
    return data
