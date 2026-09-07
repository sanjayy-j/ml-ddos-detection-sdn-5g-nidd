"""Stage J — figures for the frozen RF/SVM/CNN evaluation.

Consumes saved evaluation artifacts only. Nothing here trains a model,
loads a model file, generates a prediction, or selects a threshold: the
data path is

    saved evaluation artifacts -> plotting -> deterministic figures

Data-preparation helpers are kept separate from rendering so they can be
tested without producing images.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

MODEL_ORDER = ("RandomForest", "SVM", "CNN_1D")
MODEL_LABELS = {
    "RandomForest": "Random Forest",
    "SVM": "SVM (Nystroem + LinearSVC)",
    "CNN_1D": "1-D CNN",
}
MODEL_DIRS = {"RandomForest": "random_forest", "SVM": "svm", "CNN_1D": "cnn"}
MODEL_COLOURS = {
    "RandomForest": "#0072B2",   # blue
    "SVM": "#D55E00",            # vermillion
    "CNN_1D": "#009E73",         # green
}

# Ordered smallest-support first, with UDPFlood last so the one divergent
# class is not buried mid-axis.
ATTACK_ORDER = (
    "ICMPFlood", "SYNFlood", "UDPScan", "SYNScan", "TCPConnectScan",
    "SlowrateDoS", "HTTPFlood", "UDPFlood",
)

FPR_BUDGETS = (0.001, 0.01, 0.05, 0.10)
PRIMARY_FPR_CAP = 0.01

# Test-set malicious prevalence: the PR no-skill reference (NOT 0.5).
TEST_MALICIOUS_PREVALENCE = 0.607077

# PNG metadata carrying a timestamp would break byte-determinism.
DETERMINISTIC_PNG_METADATA = {"Software": None, "Creation Time": None}
FIGURE_DPI = 200


class PlotDataError(Exception):
    """Raised when a required plotting input is missing or malformed."""


def _require(path: Path) -> Path:
    if not path.is_file():
        raise PlotDataError(f"required plotting input not found: {path}")
    return path


def _read_csv(path: Path) -> pd.DataFrame:
    _require(path)
    try:
        frame = pd.read_csv(path)
    except Exception as exc:  # malformed CSV
        raise PlotDataError(f"could not read {path}: {exc}") from exc
    if frame.empty:
        raise PlotDataError(f"plotting input is empty: {path}")
    return frame


def load_curves(results_root: Path) -> dict[str, dict[str, pd.DataFrame]]:
    """Per-model test ROC and PR curve points."""
    results_root = Path(results_root)
    curves: dict[str, dict[str, pd.DataFrame]] = {}
    for model in MODEL_ORDER:
        folder = results_root / MODEL_DIRS[model]
        roc = _read_csv(folder / "test_roc_curve.csv")
        pr = _read_csv(folder / "test_pr_curve.csv")
        for frame, cols, name in ((roc, {"fpr", "tpr"}, "ROC"),
                                  (pr, {"recall", "precision"}, "PR")):
            missing = cols - set(frame.columns)
            if missing:
                raise PlotDataError(
                    f"{model} {name} curve missing columns: {sorted(missing)}")
        curves[model] = {"roc": roc, "pr": pr}
    return curves


def load_summary(results_root: Path) -> pd.DataFrame:
    """Stage I canonical summary, ordered canonically."""
    frame = _read_csv(Path(results_root) / "evaluation"
                      / "three_model_fpr1pct_summary.csv")
    missing = set(MODEL_ORDER) - set(frame["model"])
    if missing:
        raise PlotDataError(f"summary missing models: {sorted(missing)}")
    frame["model"] = pd.Categorical(frame["model"], MODEL_ORDER, ordered=True)
    return frame.sort_values("model").reset_index(drop=True)


def load_budgets(results_root: Path) -> pd.DataFrame:
    """Stage I validation FPR-budget table, ordered by model then budget."""
    frame = _read_csv(Path(results_root) / "evaluation"
                      / "three_model_fpr_budget.csv")
    for column in ("model", "max_fpr", "recall", "fpr"):
        if column not in frame.columns:
            raise PlotDataError(f"budget table missing column: {column}")
    frame["model"] = pd.Categorical(frame["model"], MODEL_ORDER, ordered=True)
    return frame.sort_values(["model", "max_fpr"]).reset_index(drop=True)


def load_per_attack(results_root: Path) -> pd.DataFrame:
    """Stage I per-attack recall, ordered by ATTACK_ORDER (Benign excluded)."""
    frame = _read_csv(Path(results_root) / "evaluation"
                      / "three_model_per_attack_type.csv")
    attacks = frame[frame["group"] != "Benign"].copy()
    missing = set(ATTACK_ORDER) - set(attacks["group"])
    if missing:
        raise PlotDataError(f"per-attack table missing: {sorted(missing)}")
    attacks["group"] = pd.Categorical(attacks["group"], ATTACK_ORDER,
                                      ordered=True)
    return attacks.sort_values("group").reset_index(drop=True)


def load_confusion(results_root: Path) -> pd.DataFrame:
    """Stage I confusion counts, ordered canonically."""
    frame = _read_csv(Path(results_root) / "evaluation"
                      / "three_model_confusion_matrices.csv")
    for column in ("model", "TN", "FP", "FN", "TP"):
        if column not in frame.columns:
            raise PlotDataError(f"confusion table missing column: {column}")
    frame["model"] = pd.Categorical(frame["model"], MODEL_ORDER, ordered=True)
    return frame.sort_values("model").reset_index(drop=True)


def build_manifest(figures: list[dict[str, Any]], script: str,
                   generated_utc: str) -> dict[str, Any]:
    """Provenance record describing every figure produced."""
    return {
        "stage": "J",
        "generated_utc": generated_utc,
        "generation_script": script,
        "operating_point": "validation FPR <= 1%, thresholds frozen before test",
        "frozen_thresholds": {
            "RandomForest": 0.478734, "SVM": -0.062874, "CNN_1D": 0.471731,
        },
        "pr_no_skill_reference": TEST_MALICIOUS_PREVALENCE,
        "evaluation_scope": (
            "within-capture (within-session) generalisation; the figures do "
            "NOT establish unseen-capture, unseen-session, "
            "unseen-base-station or unseen-attack generalisation"
        ),
        "timing_caveat": (
            "Inference time = amortised batch throughput over the test set, "
            "not single-flow latency; single wall-clock runs on a "
            "load-variable machine, so values are approximate."
        ),
        "models_retrained": False,
        "predictions_generated_during_plotting": False,
        "thresholds_selected_during_plotting": False,
        "figures": figures,
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": FIGURE_DPI,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.autolayout": True,
    })
    return plt


def _save(fig, path: Path) -> None:
    fig.savefig(path, metadata=DETERMINISTIC_PNG_METADATA)
    import matplotlib.pyplot as plt
    plt.close(fig)


def plot_roc(curves, summary, path: Path) -> None:
    plt = _style()
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    aucs = summary.set_index("model")["roc_auc"]
    for model in MODEL_ORDER:
        roc = curves[model]["roc"]
        ax.plot(roc["fpr"], roc["tpr"], color=MODEL_COLOURS[model], lw=1.8,
                label=f"{MODEL_LABELS[model]} (AUC = {aucs[model]:.4f})")
    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.6, label="No skill (AUC = 0.5)")
    ax.set_xlabel("False Positive Rate  (FP / (FP + TN))")
    ax.set_ylabel("True Positive Rate / Recall  (TP / (TP + FN))")
    ax.set_title("Test-set ROC — M1 supervised models\n"
                 "positive class = Malicious; 182,402 test flows")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", frameon=False)
    _save(fig, path)


def plot_pr(curves, summary, path: Path) -> None:
    plt = _style()
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    aucs = summary.set_index("model")["pr_auc"]
    for model in MODEL_ORDER:
        pr = curves[model]["pr"]
        ax.plot(pr["recall"], pr["precision"], color=MODEL_COLOURS[model],
                lw=1.8, label=f"{MODEL_LABELS[model]} (PR-AUC = {aucs[model]:.4f})")
    ax.axhline(TEST_MALICIOUS_PREVALENCE, ls="--", color="k", lw=1, alpha=0.6,
               label=f"No skill = malicious prevalence "
                     f"({TEST_MALICIOUS_PREVALENCE:.3f})")
    ax.set_xlabel("Recall  (TP / (TP + FN))")
    ax.set_ylabel("Precision  (TP / (TP + FP))")
    ax.set_title("Test-set Precision-Recall — M1 supervised models\n"
                 "positive class = Malicious; no-skill baseline is 0.607, not 0.5")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.legend(loc="lower left", frameon=False)
    _save(fig, path)


def plot_fpr_budget(budgets, path: Path) -> None:
    plt = _style()
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    for model in MODEL_ORDER:
        sub = budgets[budgets["model"] == model]
        ax.plot(sub["fpr"], sub["recall"], "o-", color=MODEL_COLOURS[model],
                lw=1.6, ms=6, label=MODEL_LABELS[model])
        primary = sub[sub["max_fpr"] == PRIMARY_FPR_CAP]
        if len(primary):
            ax.plot(primary["fpr"], primary["recall"], "*",
                    color=MODEL_COLOURS[model], ms=18, mec="k", mew=0.6,
                    zorder=5)
    ax.axvline(PRIMARY_FPR_CAP, ls=":", color="k", lw=1.2, alpha=0.7)
    ax.set_xscale("log")
    # label the 1% line against the axis top, clear of the data and legend
    ax.annotate("primary operating point\n(validation FPR <= 1%)",
                xy=(PRIMARY_FPR_CAP, 1.0), xycoords=("data", "axes fraction"),
                xytext=(-6, -10), textcoords="offset points",
                ha="right", va="top", fontsize=8, color="0.25")
    ax.set_xlabel("Achieved validation FPR (log scale)")
    ax.set_ylabel("Validation recall")
    ax.set_title("Validation FPR budget vs recall  (stars = primary 1% point)\n"
                 "RF and CNN collapse to a single point (discrete scores); "
                 "only the SVM moves", fontsize=10)
    ax.legend(loc="lower right", frameon=False, bbox_to_anchor=(1.0, 0.02))
    _save(fig, path)


def plot_metric_comparison(summary, path: Path) -> None:
    plt = _style()
    import numpy as np

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(9.5, 4.6), gridspec_kw={"width_ratios": [3, 1]})
    metrics = [("test_recall", "Recall"), ("test_precision", "Precision"),
               ("test_f1", "F1")]
    x = np.arange(len(metrics))
    width = 0.26
    for i, model in enumerate(MODEL_ORDER):
        row = summary[summary["model"] == model].iloc[0]
        values = [row[key] for key, _ in metrics]
        bars = ax_left.bar(x + (i - 1) * width, values, width,
                           color=MODEL_COLOURS[model], label=MODEL_LABELS[model])
        ax_left.bar_label(bars, fmt="%.3f", fontsize=7, padding=2)
    ax_left.set_xticks(x, [label for _, label in metrics])
    ax_left.set_ylim(0, 1.12)
    ax_left.set_ylabel("Score")
    ax_left.legend(loc="upper left", frameon=False, fontsize=8)
    ax_left.set_title("Detection quality")

    # FPR is 2 orders of magnitude smaller; a shared axis would hide it
    for i, model in enumerate(MODEL_ORDER):
        row = summary[summary["model"] == model].iloc[0]
        bars = ax_right.bar([i], [row["test_fpr"]], 0.6,
                            color=MODEL_COLOURS[model])
        ax_right.bar_label(bars, fmt="%.4f", fontsize=7, padding=2)
    ax_right.set_xticks(range(len(MODEL_ORDER)), ["RF", "SVM", "CNN"])
    ax_right.set_ylabel("False Positive Rate")
    ax_right.set_title("False alarms (own scale)")
    ax_right.set_ylim(0, 0.016)

    fig.suptitle("Test metrics at thresholds selected on VALIDATION "
                 "(FPR <= 1%), frozen before test evaluation", fontsize=10.5)
    _save(fig, path)


def plot_per_attack(per_attack, path: Path) -> None:
    plt = _style()
    import numpy as np

    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    x = np.arange(len(ATTACK_ORDER))
    width = 0.26
    for i, model in enumerate(MODEL_ORDER):
        values = [float(per_attack[per_attack["group"] == a][model].iloc[0])
                  for a in ATTACK_ORDER]
        bars = ax.bar(x + (i - 1) * width, values, width,
                      color=MODEL_COLOURS[model], label=MODEL_LABELS[model])
        ax.bar_label(bars, fmt="%.2f", fontsize=6.5, padding=2, rotation=90)
    labels = [f"{a}\n(n={int(per_attack[per_attack['group'] == a]['support'].iloc[0]):,})"
              for a in ATTACK_ORDER]
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Test recall (detection rate)")
    ax.set_title("Per-attack-type test recall at the frozen FPR <= 1% "
                 "operating point\nUDP flood is the sole divergent class "
                 "(7-10% across all three models)")
    ax.legend(loc="lower left", frameon=False, fontsize=8)
    _save(fig, path)


def plot_confusion(row, path: Path, normalised: bool = False) -> None:
    plt = _style()
    import numpy as np

    model = str(row["model"])
    counts = np.array([[int(row["TN"]), int(row["FP"])],
                       [int(row["FN"]), int(row["TP"])]])
    display = (counts / counts.sum(axis=1, keepdims=True)) if normalised else counts

    fig, ax = plt.subplots(figsize=(5.0, 4.4))
    ax.imshow(counts / counts.sum(axis=1, keepdims=True), cmap="Blues",
              vmin=0, vmax=1)
    ax.grid(False)
    for r in range(2):
        for c in range(2):
            share = counts[r, c] / counts[r].sum()
            text = (f"{display[r, c]:.4f}" if normalised
                    else f"{counts[r, c]:,}\n({share:.1%} of row)")
            ax.text(c, r, text, ha="center", va="center", fontsize=11,
                    color="white" if share > 0.5 else "black")
    ax.set_xticks([0, 1], ["Predicted\nBenign", "Predicted\nMalicious"])
    ax.set_yticks([0, 1], ["Actual\nBenign", "Actual\nMalicious"])
    kind = "row-normalised" if normalised else "absolute counts"
    ax.set_title(f"{MODEL_LABELS[model]} — test confusion matrix ({kind})\n"
                 f"frozen FPR <= 1% operating point; N = {counts.sum():,}")
    _save(fig, path)


def plot_cost(summary, path: Path) -> None:
    plt = _style()
    import numpy as np

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(9.0, 4.2))
    x = np.arange(len(MODEL_ORDER))
    labels = ["RF", "SVM", "CNN"]
    colours = [MODEL_COLOURS[m] for m in MODEL_ORDER]

    train = [float(summary[summary["model"] == m]["train_seconds"].iloc[0])
             for m in MODEL_ORDER]
    bars = ax_left.bar(x, train, 0.6, color=colours)
    ax_left.bar_label(bars, labels=[f"{v:,.0f} s" for v in train], fontsize=8,
                      padding=2)
    ax_left.set_yscale("log")
    ax_left.set_xticks(x, labels)
    ax_left.set_ylabel("Training time (s, log scale)")
    ax_left.set_title("Training cost")

    thr = [float(summary[summary["model"] == m]
                 ["batch_throughput_ms_per_flow"].iloc[0]) for m in MODEL_ORDER]
    bars = ax_right.bar(x, thr, 0.6, color=colours)
    # approximate measurements: 3 decimal places, no false precision
    ax_right.bar_label(bars, labels=[f"~{v:.3f}" for v in thr], fontsize=8,
                       padding=2)
    ax_right.set_xticks(x, labels)
    ax_right.set_ylabel("ms per flow (approx.)")
    ax_right.set_title("Amortised batch throughput")
    ax_right.set_ylim(0, max(thr) * 1.35)

    fig.suptitle("Approximate computational cost — inference time is amortised "
                 "batch throughput\nover the test set, NOT single-flow latency "
                 "(single timed runs; treat as approximate)", fontsize=9.5)
    _save(fig, path)
