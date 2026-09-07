"""Stage H CLI — M1 1-D CNN (TensorFlow/Keras).

    python M1-supervised-ml/experiments/train_cnn.py

Protocol, in enforced order:
  1. load the Stage D processed artifacts, verify, reshape to (n, 67, 1)
  2. architecture/hyperparameter search on TRAIN, scored on VALIDATION
  3. freeze the operating threshold on VALIDATION at FPR <= 1%
  4. evaluate TEST exactly once at the frozen threshold
  5. per-attack breakdown, curve data, additive 3-model comparison

The test split is not read until step 4. Early stopping uses validation
PR-AUC only. RF and SVM artifacts are read but never modified.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.metrics import compute_metrics, group_breakdown  # noqa: E402
from evaluation.thresholds import (  # noqa: E402
    FPR_BUDGETS,
    PRIMARY_FPR_CAP,
    recall_at_fpr_budgets,
    select_threshold_at_fpr,
)
from models.cnn import (  # noqa: E402
    balanced_class_weight,
    build_cnn,
    describe_cnn,
    reshape_for_conv1d,
    set_seeds,
)
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import load_processed, resolve_path  # noqa: E402
from training.metadata import (  # noqa: E402
    load_split_metadata,
    verify_metadata_alignment,
)

# Full factorial over the candidates named in the Stage H brief. Kept
# affordable by a small model (~10.5k parameters, ~8 s/epoch) plus early
# stopping on validation PR-AUC.
SEARCH_GRID = {
    "filters": [(32, 64), (64, 128)],
    "kernel_size": [3, 5],
    "dropout": [0.2, 0.3],
    "learning_rate": [1e-3, 3e-4],
}
SELECTION_METRIC = "pr_auc"
TIE_TOLERANCE = 1e-3
MAX_EPOCHS = 30
PATIENCE = 5
BATCH_SIZE = 512
PREDICT_BATCH = 4096

BASELINES = {
    "always_malicious_accuracy": 0.607077,
    "exact_vector_memorisation_accuracy": 0.735129,
    "empirical_feature_space_ceiling": 0.786258,
}


def verify_inputs(data: dict) -> dict:
    report = {}
    n_features = data["X"]["train"].shape[1]
    for split in ("train", "val", "test"):
        X, y = data["X"][split], data["y"][split]
        assert X.shape[0] == y.shape[0], f"{split}: X/y row mismatch"
        assert X.shape[1] == n_features, f"{split}: feature-count mismatch"
        assert np.isfinite(X).all(), f"{split}: non-finite values present"
        assert set(np.unique(y)) <= {0, 1}, f"{split}: target not binary"
        report[split] = {
            "rows": int(X.shape[0]),
            "features": int(X.shape[1]),
            "malicious_pct": round(100 * float(y.mean()), 4),
        }
    report["n_features"] = int(n_features)
    return report


def _fit_candidate(Z_tr, y_tr, Z_va, y_va, params, class_weight, seed):
    """Train one candidate with early stopping on validation PR-AUC."""
    import keras

    set_seeds(seed)
    model = build_cnn(
        n_features=Z_tr.shape[1],
        filters=tuple(params["filters"]),
        kernel_size=params["kernel_size"],
        dropout=params["dropout"],
        learning_rate=params["learning_rate"],
        seed=seed,
    )
    stopper = keras.callbacks.EarlyStopping(
        monitor="val_pr_auc", mode="max", patience=PATIENCE,
        restore_best_weights=True, verbose=0,
    )
    t0 = time.perf_counter()
    history = model.fit(
        Z_tr, y_tr,
        validation_data=(Z_va, y_va),
        epochs=MAX_EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weight,
        callbacks=[stopper],
        verbose=0,
        shuffle=True,
    )
    fit_seconds = time.perf_counter() - t0
    val_pr = history.history["val_pr_auc"]
    best_epoch = int(np.argmax(val_pr)) + 1
    return model, fit_seconds, len(val_pr), best_epoch


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the M1 1-D CNN.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    seed = int(config.get("seed", 42))
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"),
    )
    results_dir = results_root / "cnn"
    results_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("processed_dir",
                                         "M1-supervised-ml/data/processed"),
    )

    # ---------------- 1. load / verify / reshape ----------------
    print("[1/6] loading Stage D artifacts", flush=True)
    data = load_processed(config, REPO_ROOT)
    integrity = verify_inputs(data)
    feature_names = json.loads(
        (results_root / "feature_order.json").read_text(encoding="utf-8")
    )["feature_order"]
    assert len(feature_names) == integrity["n_features"], "feature-name mismatch"

    Z_tr = reshape_for_conv1d(data["X"]["train"])
    Z_va = reshape_for_conv1d(data["X"]["val"])
    y_tr, y_va = data["y"]["train"], data["y"]["val"]
    # the reshape must not perturb the Stage D ordering
    assert np.array_equal(Z_tr[:, :, 0], data["X"]["train"]), "reshape altered data"
    class_weight = balanced_class_weight(y_tr)
    print("      input shape {} (Stage D order preserved); class_weight={}".format(
        Z_tr.shape[1:], {k: round(v, 6) for k, v in class_weight.items()}), flush=True)

    # ---------------- 2. search (validation only) ----------------
    print("[2/6] architecture search ({} candidates, criterion: validation {})"
          .format(int(np.prod([len(v) for v in SEARCH_GRID.values()])),
                  SELECTION_METRIC), flush=True)
    keys = list(SEARCH_GRID)
    candidates = [dict(zip(keys, combo))
                  for combo in itertools.product(*(SEARCH_GRID[k] for k in keys))]

    rows = []
    for i, params in enumerate(candidates, 1):
        model, fit_s, epochs_run, best_epoch = _fit_candidate(
            Z_tr, y_tr, Z_va, y_va, params, class_weight, seed)
        scores = model.predict(Z_va, batch_size=PREDICT_BATCH,
                               verbose=0).ravel()
        row = compute_metrics(y_va, (scores >= 0.5).astype(np.int8), scores)
        row["candidate"] = i
        row["filters"] = "x".join(str(f) for f in params["filters"])
        row["kernel_size"] = params["kernel_size"]
        row["dropout"] = params["dropout"]
        row["learning_rate"] = params["learning_rate"]
        row["params"] = int(model.count_params())
        row["epochs_run"] = epochs_run
        row["best_epoch"] = best_epoch
        row["fit_seconds"] = round(fit_s, 1)
        rows.append(row)
        print("      [{:>2}/{}] filters={:<7} k={} drop={} lr={:<7} PR-AUC={:.5f} "
              "ROC-AUC={:.5f} epochs={:>2}(best {:>2}) fit={:.0f}s".format(
                  i, len(candidates), row["filters"], params["kernel_size"],
                  params["dropout"], params["learning_rate"], row["pr_auc"],
                  row["roc_auc"], epochs_run, best_epoch, fit_s), flush=True)
        del model
        import keras
        keras.backend.clear_session()

    search = pd.DataFrame(rows)
    search.to_csv(results_dir / "validation_search.csv", index=False)

    best_score = search[SELECTION_METRIC].max()
    close = search[search[SELECTION_METRIC] >= best_score - TIE_TOLERANCE].copy()
    # tie-break toward the simpler/cheaper model: fewer params, then
    # smaller kernel, then fewer epochs
    chosen = close.sort_values(["params", "kernel_size", "fit_seconds"]).iloc[0]
    best = {
        "filters": tuple(int(f) for f in str(chosen["filters"]).split("x")),
        "kernel_size": int(chosen["kernel_size"]),
        "dropout": float(chosen["dropout"]),
        "learning_rate": float(chosen["learning_rate"]),
    }
    print("      best {}={:.5f}; {} within {}; chosen -> {}".format(
        SELECTION_METRIC, best_score, len(close), TIE_TOLERANCE, best), flush=True)

    # ---------------- 3. refit + freeze threshold on VALIDATION ----------
    print("[3/6] refitting chosen configuration", flush=True)
    model, train_seconds, epochs_run, best_epoch = _fit_candidate(
        Z_tr, y_tr, Z_va, y_va, best, class_weight, seed)
    t0 = time.perf_counter()
    val_scores = model.predict(Z_va, batch_size=PREDICT_BATCH, verbose=0).ravel()
    val_seconds = time.perf_counter() - t0
    print("      trained {} epochs (best {}) in {:.0f}s; val scored in {:.2f}s"
          .format(epochs_run, best_epoch, train_seconds, val_seconds), flush=True)

    budget_rows = recall_at_fpr_budgets(y_va, val_scores, FPR_BUDGETS)
    pd.DataFrame(budget_rows).to_csv(
        results_dir / "validation_fpr_budgets.csv", index=False)
    for row in budget_rows:
        print("        FPR<={:<7.2%} threshold={:>10.6f} recall={:.6f} "
              "achieved_FPR={:.6f} satisfiable={}".format(
                  row["max_fpr"], row["threshold"], row["recall"],
                  row["fpr"], row["satisfiable"]), flush=True)

    operating = select_threshold_at_fpr(y_va, val_scores, PRIMARY_FPR_CAP)
    threshold = operating["threshold"]
    print("      FROZEN threshold (validation FPR<=1%) = {:.6f}".format(threshold),
          flush=True)
    if not operating["satisfiable"]:
        print("      WARNING: {}".format(operating["reason"]), flush=True)
    val_metrics = compute_metrics(
        y_va, (val_scores >= threshold).astype(np.int8), val_scores)
    val_at_half = compute_metrics(
        y_va, (val_scores >= 0.5).astype(np.int8), val_scores)

    # ---------------- 4. TEST: exactly once ----------------
    print("[4/6] final test evaluation (single pass, frozen threshold)", flush=True)
    Z_te, y_te = reshape_for_conv1d(data["X"]["test"]), data["y"]["test"]
    t0 = time.perf_counter()
    test_scores = model.predict(Z_te, batch_size=PREDICT_BATCH, verbose=0).ravel()
    test_seconds = time.perf_counter() - t0
    y_pred = (test_scores >= threshold).astype(np.int8)
    test_metrics = compute_metrics(y_te, y_pred, test_scores)
    test_metrics["per_flow_inference_ms"] = round(
        1000 * test_seconds / len(y_te), 6)
    for key in ("accuracy", "precision", "recall", "f1", "fpr", "tnr",
                "roc_auc", "pr_auc"):
        print("      {:<10} {:.6f}".format(key, test_metrics[key]), flush=True)
    print("      TP={:,} TN={:,} FP={:,} FN={:,}".format(
        test_metrics["TP"], test_metrics["TN"],
        test_metrics["FP"], test_metrics["FN"]), flush=True)

    # ---------------- 5. per-attack + curve data ----------------
    print("[5/6] per-attack analysis and curve data", flush=True)
    meta = load_split_metadata(config, REPO_ROOT, "test")
    verify_metadata_alignment(meta, y_te)
    by_type = pd.DataFrame(group_breakdown(
        y_te, y_pred, meta["attack_type"].to_numpy()))
    by_tool = pd.DataFrame(group_breakdown(
        y_te, y_pred, meta["attack_tool"].to_numpy()))
    by_type.to_csv(results_dir / "per_attack_type.csv", index=False)
    by_tool.to_csv(results_dir / "per_attack_tool.csv", index=False)
    print(by_type.to_string(index=False), flush=True)

    from sklearn.metrics import precision_recall_curve, roc_curve
    fpr_c, tpr_c, _ = roc_curve(y_te, test_scores)
    prec_c, rec_c, _ = precision_recall_curve(y_te, test_scores)
    step = max(1, len(fpr_c) // 2000)
    pd.DataFrame({"fpr": fpr_c[::step], "tpr": tpr_c[::step]}).to_csv(
        results_dir / "test_roc_curve.csv", index=False)
    step = max(1, len(prec_c) // 2000)
    pd.DataFrame({"recall": rec_c[::step], "precision": prec_c[::step]}).to_csv(
        results_dir / "test_pr_curve.csv", index=False)

    # ---------------- 6. persist + additive 3-model comparison ----------
    print("[6/6] writing artifacts", flush=True)
    model_path = processed_dir / "cnn_model.keras"
    model.save(model_path)

    record = {
        "stage": "H",
        "model": "1-D CNN (TensorFlow/Keras)",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "seed": seed,
        "split_protocol": (config.get("split") or {}).get("strategy"),
        "evaluation_scope": (
            "within-capture (within-session) generalisation; NOT unseen-capture, "
            "unseen-session, unseen-base-station or unseen-attack generalisation"
        ),
        "input_representation": {
            "shape": list(Z_tr.shape[1:]),
            "source": "Stage D canonical 67-feature matrix, reshaped (n,67)->(n,67,1)",
            "feature_order_preserved": True,
            "caveat": (
                "Tabular feature vector, NOT a temporal signal. Conv1D does not "
                "perform temporal convolution and does not model packet/flow "
                "sequences; adjacency along the 67-axis is an artifact of column "
                "order."
            ),
        },
        "integrity": integrity,
        "class_weight": {str(k): v for k, v in class_weight.items()},
        "class_weight_note": (
            "sklearn 'balanced' formula, identical to the RF and SVM strategy"
        ),
        "selection_metric": SELECTION_METRIC,
        "search_grid": {k: [str(x) for x in v] for k, v in SEARCH_GRID.items()},
        "n_candidates": len(candidates),
        "training_controls": {
            "max_epochs": MAX_EPOCHS, "patience": PATIENCE,
            "batch_size": BATCH_SIZE,
            "early_stopping_monitor": "val_pr_auc (max), restore_best_weights=True",
        },
        "chosen_hyperparameters": {
            "filters": list(best["filters"]), "kernel_size": best["kernel_size"],
            "dropout": best["dropout"], "learning_rate": best["learning_rate"],
        },
        "model_structure": describe_cnn(model, config),
        "epochs_run": epochs_run,
        "best_epoch": best_epoch,
        "operating_point": {
            "rule": ("max validation recall subject to validation FPR <= 1%; "
                     "ties broken toward the highest threshold; frozen before test"),
            "primary_fpr_cap": PRIMARY_FPR_CAP,
            **operating,
        },
        "validation_fpr_budgets": budget_rows,
        "timings_seconds": {
            "train": round(train_seconds, 2),
            "val_inference": round(val_seconds, 3),
            "test_inference": round(test_seconds, 3),
            "search_total": round(float(search["fit_seconds"].sum()), 1),
        },
        "validation_metrics_at_frozen_threshold": val_metrics,
        "validation_metrics_at_0_5": val_at_half,
        "test_metrics": test_metrics,
        "baselines_test": BASELINES,
        "comparison_test": {
            "beats_always_malicious": bool(
                test_metrics["accuracy"] > BASELINES["always_malicious_accuracy"]),
            "beats_memorisation_baseline": bool(
                test_metrics["accuracy"]
                > BASELINES["exact_vector_memorisation_accuracy"]),
            "gap_to_ceiling_pp": round(
                100 * (BASELINES["empirical_feature_space_ceiling"]
                       - test_metrics["accuracy"]), 4),
        },
    }
    (results_dir / "cnn_run_record.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8")
    (results_dir / "test_metrics.json").write_text(
        json.dumps(test_metrics, indent=2), encoding="utf-8")

    # additive three-model comparison; RF/SVM records are READ ONLY
    rf = json.loads((results_root / "random_forest"
                     / "rf_fpr_constrained_record.json").read_text(encoding="utf-8"))
    svm = json.loads((results_root / "svm"
                      / "svm_run_record.json").read_text(encoding="utf-8"))
    rows_cmp = []
    for name, tm, thr, infer in (
        ("RandomForest", rf["test_metrics_fpr_constrained"],
         rf["operating_point"]["threshold"], rf["test_metrics_fpr_constrained"]
         .get("per_flow_inference_ms")),
        ("SVM", svm["test_metrics"], svm["operating_point"]["threshold"],
         svm["test_metrics"].get("per_flow_inference_ms")),
        ("CNN_1D", test_metrics, threshold,
         test_metrics["per_flow_inference_ms"]),
    ):
        rows_cmp.append({
            "model": name, "operating_point": "validation FPR <= 1%",
            "threshold": thr,
            **{k: tm[k] for k in ("accuracy", "precision", "recall", "f1",
                                  "fpr", "tnr", "roc_auc", "pr_auc",
                                  "TP", "TN", "FP", "FN")},
            "per_flow_inference_ms": infer,
        })
    comparison = pd.DataFrame(rows_cmp)
    comparison.to_csv(results_root / "model_comparison_fpr1pct.csv", index=False)
    print("\n=== three-model comparison at validation FPR <= 1% ===", flush=True)
    print(comparison[["model", "accuracy", "precision", "recall", "f1", "fpr",
                      "roc_auc", "pr_auc", "per_flow_inference_ms"]]
          .to_string(index=False), flush=True)
    print("      wrote " + str(results_dir), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
