"""Phase 3.2 — repeated-seed stability of the three M1 classifiers.

Faculty correction item 1: every reported M1 result used the single seed 42.
This script retrains each model under several seeds and reports the spread.

It changes NOTHING about the methodology:

  * the hyperparameters are the ones the Stage F/G/H validation searches
    already selected (read from the committed run records), so no grid is
    re-run and no search space is reduced;
  * the operating point is the locked protocol from
    `evaluation.thresholds` — maximise validation recall subject to
    validation FPR <= 1%, ties toward the higher threshold — re-selected
    on validation for each seed, then applied to the test split once;
  * the preprocessed matrices are the committed primary representation,
    which is seed-independent (the split is deterministic by capture
    position and the transformers carry no RNG).

Only the model seeds vary: RandomForestClassifier.random_state, the
Nystroem component draw plus LinearSVC.random_state, and the CNN's
TensorFlow/NumPy/Python seeds and initialisers.

Results are written additively to `results/seed_sweep/`; no existing
artifact is touched. Rows are appended as each run finishes, so a long
sweep can be inspected while it is still going.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.metrics import compute_metrics  # noqa: E402
from evaluation.thresholds import (  # noqa: E402
    PRIMARY_FPR_CAP,
    select_threshold_at_fpr,
)
from models.random_forest import build_random_forest  # noqa: E402
from models.svm import build_svm, gamma_scale  # noqa: E402
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import load_processed, resolve_path  # noqa: E402

DEFAULT_SEEDS = (42, 43, 44, 45, 46)

# Metrics reported per seed (the Table 5 set plus the frozen threshold).
METRICS = ("accuracy", "precision", "recall", "f1", "fpr", "tnr",
           "roc_auc", "pr_auc")
COUNTS = ("TP", "TN", "FP", "FN")

ROW_FIELDS = ("model", "seed", "threshold", *METRICS, *COUNTS,
              "train_seconds", "notes")


def selected_hyperparameters(results_root: Path) -> dict[str, dict]:
    """Read the configurations the committed validation searches chose."""
    def record(name: str) -> dict:
        return json.loads(
            (results_root / name).read_text(encoding="utf-8"))

    rf = record("random_forest/rf_run_record.json")["chosen_hyperparameters"]
    svm = record("svm/svm_run_record.json")["chosen_hyperparameters"]
    cnn = record("cnn/cnn_run_record.json")["chosen_hyperparameters"]
    return {"RandomForest": rf, "SVM": svm, "CNN_1D": cnn}


def seeded_config(config: dict, seed: int) -> dict:
    """Copy of the config with every model seed set to `seed`."""
    out = json.loads(json.dumps(config))
    out["seed"] = seed
    models = out.setdefault("models", {})
    models.setdefault("random_forest", {})["random_state"] = seed
    models.setdefault("svm", {})["random_state"] = seed
    models.setdefault("cnn", {})["random_seed"] = seed
    return out


def evaluate(y_va, val_scores, y_te, test_scores) -> tuple[float, dict]:
    """Locked protocol: freeze on validation, then score test once."""
    operating = select_threshold_at_fpr(y_va, val_scores, PRIMARY_FPR_CAP)
    threshold = float(operating["threshold"])
    y_pred = (test_scores >= threshold).astype(np.int8)
    return threshold, compute_metrics(y_te, y_pred, test_scores)


def run_rf(config, chosen, data, seed):
    overrides = {k: v for k, v in chosen.items()
                 if k in ("max_depth", "min_samples_leaf", "max_features")}
    model = build_random_forest(seeded_config(config, seed), **overrides)
    t0 = time.perf_counter()
    model.fit(data["X"]["train"], data["y"]["train"])
    train_s = time.perf_counter() - t0
    val_scores = model.predict_proba(data["X"]["val"])[:, 1]
    test_scores = model.predict_proba(data["X"]["test"])[:, 1]
    return val_scores, test_scores, train_s


def run_svm(config, chosen, data, seed):
    X_tr = data["X"]["train"]
    # gamma is the sklearn 'scale' heuristic on TRAIN only; it does not
    # depend on the seed, so it is identical to the committed run.
    gamma = gamma_scale(X_tr)
    overrides = {k: v for k, v in chosen.items() if k in ("n_components", "C")}
    model = build_svm(seeded_config(config, seed), gamma, **overrides)
    t0 = time.perf_counter()
    model.fit(X_tr, data["y"]["train"])
    train_s = time.perf_counter() - t0
    val_scores = model.decision_function(data["X"]["val"])
    test_scores = model.decision_function(data["X"]["test"])
    return val_scores, test_scores, train_s


def run_cnn(config, chosen, data, seed):
    # Reuse the Stage H fit helper so early stopping, batch size, epoch
    # cap and class weighting are exactly those of the committed run.
    sys.path.insert(0, str(M1_ROOT / "experiments"))
    from train_cnn import PREDICT_BATCH, _fit_candidate  # noqa: E402

    from models.cnn import balanced_class_weight, reshape_for_conv1d

    Z_tr = reshape_for_conv1d(data["X"]["train"])
    Z_va = reshape_for_conv1d(data["X"]["val"])
    Z_te = reshape_for_conv1d(data["X"]["test"])
    y_tr = data["y"]["train"]
    params = {
        "filters": tuple(chosen["filters"]),
        "kernel_size": chosen["kernel_size"],
        "dropout": chosen["dropout"],
        "learning_rate": chosen["learning_rate"],
    }
    model, train_s, epochs_run, best_epoch = _fit_candidate(
        Z_tr, y_tr, Z_va, data["y"]["val"], params,
        balanced_class_weight(y_tr), seed)
    val_scores = model.predict(
        Z_va, batch_size=PREDICT_BATCH, verbose=0).ravel()
    test_scores = model.predict(
        Z_te, batch_size=PREDICT_BATCH, verbose=0).ravel()
    return val_scores, test_scores, train_s, f"epochs={epochs_run},best={best_epoch}"


RUNNERS = {"RandomForest": run_rf, "SVM": run_svm, "CNN_1D": run_cnn}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",
                        default=str(M1_ROOT / "config" / "m1_config.yaml"))
    parser.add_argument("--seeds", default=",".join(str(s) for s in DEFAULT_SEEDS),
                        help="comma-separated seeds (default: 42,43,44,45,46)")
    parser.add_argument("--models", default="RandomForest,SVM,CNN_1D",
                        help="comma-separated subset of the three models")
    args = parser.parse_args()

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    wanted = [m.strip() for m in args.models.split(",") if m.strip()]
    for name in wanted:
        if name not in RUNNERS:
            print(f"unknown model: {name}", file=sys.stderr)
            return 2

    config = load_config_file(args.config)
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"))
    out_dir = results_root / "seed_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)

    chosen = selected_hyperparameters(results_root)
    print("[1/3] selected configurations (from the committed run records)",
          flush=True)
    for name in wanted:
        print(f"      {name}: {chosen[name]}", flush=True)

    print("[2/3] loading the committed primary representation", flush=True)
    data = load_processed(config, REPO_ROOT)
    n_feat = data["X"]["train"].shape[1]
    print("      train={:,} val={:,} test={:,} features={}".format(
        len(data["y"]["train"]), len(data["y"]["val"]),
        len(data["y"]["test"]), n_feat), flush=True)

    rows_path = out_dir / "seed_sweep_runs.csv"
    fresh = not rows_path.is_file()
    handle = rows_path.open("a", newline="", encoding="utf-8")
    writer = csv.DictWriter(handle, fieldnames=ROW_FIELDS)
    if fresh:
        writer.writeheader()
        handle.flush()

    print("[3/3] training {} model(s) x {} seed(s)".format(
        len(wanted), len(seeds)), flush=True)
    for name in wanted:
        for seed in seeds:
            print(f"      --- {name} seed={seed} ---", flush=True)
            result = RUNNERS[name](config, chosen[name], data, seed)
            notes = ""
            if len(result) == 4:
                val_scores, test_scores, train_s, notes = result
            else:
                val_scores, test_scores, train_s = result
            threshold, metrics = evaluate(
                data["y"]["val"], val_scores, data["y"]["test"], test_scores)
            row = {"model": name, "seed": seed,
                   "threshold": round(threshold, 6),
                   "train_seconds": round(train_s, 2), "notes": notes}
            for key in METRICS:
                row[key] = round(float(metrics[key]), 6)
            for key in COUNTS:
                row[key] = int(metrics[key])
            writer.writerow(row)
            handle.flush()
            print("          threshold={:.6f} acc={:.6f} recall={:.6f} "
                  "f1={:.6f} fpr={:.6f} roc_auc={:.6f} ({:.0f}s)".format(
                      threshold, metrics["accuracy"], metrics["recall"],
                      metrics["f1"], metrics["fpr"], metrics["roc_auc"],
                      train_s), flush=True)
    handle.close()
    print("      wrote " + str(rows_path), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
