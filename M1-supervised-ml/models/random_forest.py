"""Stage F — Random Forest model factory.

NOTE ON LOCATION: the Stage-A skeleton directory is `models/random-forest/`,
which is not a valid Python identifier and therefore cannot be imported.
The importable module lives here as `models/random_forest.py`; the
hyphenated directory is left untouched as a skeleton placeholder.

The factory reads every hyperparameter from the M1 configuration so that
nothing is hard-coded at the call site and runs stay reproducible.
"""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import RandomForestClassifier


def build_random_forest(
    config: dict[str, Any], **overrides: Any
) -> RandomForestClassifier:
    """Build an unfitted RandomForestClassifier from config.

    `overrides` is used by the validation-set hyperparameter search to
    vary one candidate at a time; the configured seed and class weighting
    are never overridden silently by the search grid.
    """
    rf_cfg = dict(((config.get("models") or {}).get("random_forest") or {}))
    seed = rf_cfg.pop("random_state", config.get("seed", 42))

    params: dict[str, Any] = {
        "n_estimators": rf_cfg.pop("n_estimators", 200),
        "max_depth": rf_cfg.pop("max_depth", None),
        "min_samples_leaf": rf_cfg.pop("min_samples_leaf", 1),
        "min_samples_split": rf_cfg.pop("min_samples_split", 2),
        "max_features": rf_cfg.pop("max_features", "sqrt"),
        # Stage D chose class weighting over any resampling scheme; the
        # imbalance is mild (60.7/39.3) so no SMOTE/oversampling is used.
        "class_weight": rf_cfg.pop("class_weight", "balanced"),
        "n_jobs": rf_cfg.pop("n_jobs", -1),
        "random_state": seed,
    }
    params.update(overrides)
    return RandomForestClassifier(**params)


def describe_forest(model: RandomForestClassifier) -> dict[str, Any]:
    """Structural summary of a fitted forest (for the run record)."""
    depths = [est.get_depth() for est in model.estimators_]
    leaves = [est.get_n_leaves() for est in model.estimators_]
    return {
        "n_estimators": len(model.estimators_),
        "mean_depth": round(float(sum(depths) / len(depths)), 3),
        "max_depth_reached": int(max(depths)),
        "mean_leaves": round(float(sum(leaves) / len(leaves)), 1),
        "total_nodes": int(sum(e.tree_.node_count for e in model.estimators_)),
    }
