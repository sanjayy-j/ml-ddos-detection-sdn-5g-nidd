"""Regenerate the manuscript's Figures 2 and 3 from committed artifacts.

Faculty correction item 5 asks for the figure sources to be archived. The
originals were produced outside version control and are not recoverable,
so this script rebuilds them from the artifacts that ARE committed:

  Figure 2  results/{random_forest,svm,cnn}/test_roc_curve.csv
            plus the frozen thresholds and the achieved operating points
            in results/evaluation/three_model_fpr1pct_summary.csv
  Figure 3  results/random_forest/per_attack_type_fpr_constrained.csv
            and the SVM/CNN per-attack tables, plus the UDP-flood
            ambiguity split in results/split_composition/

It reads no raw data, trains nothing and selects no threshold, so it is
deterministic and cannot change any reported number. Style, model order
and colours follow `evaluation/plots.py` so the paper figures match the
repository's existing figures.

Figures 4 and 5 are NOT produced here. They show the M2 entropy decision
rule and the M3 flow-record mode on synthetic streams, and the
diagnostic outputs behind them were never committed (the manuscript's
data-availability statement says so). Regenerating them requires their
owners to re-run those diagnostics and archive the outputs; see
docs/revision_findings.md.

Usage, from the repository root:

    python M1-supervised-ml/experiments/generate_paper_figures.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.plots import (  # noqa: E402
    ATTACK_ORDER,
    MODEL_COLOURS,
    MODEL_DIRS,
    MODEL_LABELS,
    MODEL_ORDER,
    _style,
)
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402

FIGURE_DPI = 300
MARKERS = {"RandomForest": "o", "SVM": "s", "CNN_1D": "^"}


def load_summary(results: Path) -> pd.DataFrame:
    frame = pd.read_csv(results / "evaluation" / "three_model_fpr1pct_summary.csv")
    return frame.set_index("model")


def figure_2(plt, results: Path, out_dir: Path) -> Path:
    """Test ROC curves on linear (a) and logarithmic (b) FPR axes."""
    summary = load_summary(results)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))

    for panel, (ax, logx) in enumerate(zip(axes, (False, True))):
        for model in MODEL_ORDER:
            curve = pd.read_csv(results / MODEL_DIRS[model] / "test_roc_curve.csv")
            ax.plot(curve["fpr"], curve["tpr"],
                    color=MODEL_COLOURS[model], linewidth=1.6,
                    label="{} (AUC {:.4f})".format(
                        MODEL_LABELS[model], float(summary.loc[model, "roc_auc"])))
            # the frozen operating point, as achieved on test
            ax.plot(float(summary.loc[model, "test_fpr"]),
                    float(summary.loc[model, "test_recall"]),
                    marker=MARKERS[model], color=MODEL_COLOURS[model],
                    markersize=7, markeredgecolor="white", linestyle="none",
                    zorder=5)
        ax.plot([0, 1], [0, 1], color="0.6", linewidth=0.8, linestyle=":")
        ax.axvline(0.01, color="0.4", linewidth=0.8, linestyle="--")
        ax.set_xlabel("False-positive rate")
        ax.set_ylabel("True-positive rate (recall)")
        ax.set_ylim(0, 1.02)
        if logx:
            ax.set_xscale("log")
            ax.set_xlim(1e-5, 1)
            ax.set_title("(b) logarithmic FPR axis")
        else:
            ax.set_xlim(0, 1)
            ax.set_title("(a) linear FPR axis")
        ax.legend(loc="lower right", frameon=False)

    path = out_dir / "figure2_test_roc_curves.png"
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def figure_3(plt, results: Path, out_dir: Path) -> Path:
    """(a) recall by attack type; (b) where the UDP-flood misses sit."""
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))

    # --- (a) per-attack recall at the frozen operating points -------------
    ax = axes[0]
    width = 0.26
    for offset, model in zip((-width, 0.0, width), MODEL_ORDER):
        folder = results / MODEL_DIRS[model]
        name = "per_attack_type_fpr_constrained.csv"
        if not (folder / name).is_file():
            name = "per_attack_type.csv"
        frame = pd.read_csv(folder / name)
        frame = frame[frame["group"] != "Benign"].set_index("group")
        xs, ys = [], []
        for i, attack in enumerate(ATTACK_ORDER):
            if attack in frame.index:
                xs.append(i + offset)
                ys.append(float(frame.loc[attack, "recall"]))
        ax.bar(xs, ys, width=width, color=MODEL_COLOURS[model],
               label=MODEL_LABELS[model])
    supports = pd.read_csv(
        results / MODEL_DIRS["RandomForest"] / "per_attack_type_fpr_constrained.csv")
    supports = supports.set_index("group")["support"]
    ax.set_xticks(range(len(ATTACK_ORDER)))
    ax.set_xticklabels(
        ["{}\nn={:,}".format(a, int(supports[a])) for a in ATTACK_ORDER],
        rotation=45, ha="right", fontsize=7.5)
    ax.set_ylabel("Test recall at the frozen operating point")
    ax.set_ylim(0, 1.05)
    ax.set_title("(a) recall by attack type")
    ax.legend(loc="lower left", frameon=False)

    # --- (b) UDP-flood records split by label ambiguity -------------------
    ax = axes[1]
    amb = pd.read_csv(results / "split_composition"
                      / "udpflood_by_ambiguity_published.csv")
    amb = amb.set_index("subset")
    carrier_n = int(amb.loc["carrier", "support"])
    carrier_hit = int(amb.loc["carrier", "detected"])
    non_n = int(amb.loc["non_carrier", "support"])
    non_hit = int(amb.loc["non_carrier", "detected"])

    labels = ["Carries the dominant\nconflicting vector",
              "Any other\nfeature vector"]
    detected = [carrier_hit, non_hit]
    missed = [carrier_n - carrier_hit, non_n - non_hit]
    ax.bar(labels, detected, color="#009E73", label="detected")
    ax.bar(labels, missed, bottom=detected, color="#D55E00", label="missed")
    for i, (d, m) in enumerate(zip(detected, missed)):
        ax.text(i, d + m, "n={:,}\nrecall {:.6f}".format(d + m, d / (d + m)),
                ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("UDP-flood test records (Random Forest)")
    ax.set_ylim(0, max(carrier_n, non_n) * 1.25)
    ax.set_title("(b) where the UDP-flood misses sit")
    ax.legend(loc="upper right", frameon=False)

    path = out_dir / "figure3_per_attack_and_ambiguity.png"
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",
                        default=str(M1_ROOT / "config" / "m1_config.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    results = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"))
    out_dir = results / "paper_figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    plt = _style()
    written = [figure_2(plt, results, out_dir), figure_3(plt, results, out_dir)]

    manifest = {
        "purpose": "manuscript Figures 2 and 3, rebuilt from committed artifacts",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generation_script":
            "M1-supervised-ml/experiments/generate_paper_figures.py",
        "figures": [p.name for p in written],
        "inputs": [
            "results/{random_forest,svm,cnn}/test_roc_curve.csv",
            "results/evaluation/three_model_fpr1pct_summary.csv",
            "results/{random_forest,svm,cnn}/per_attack_type_fpr_constrained.csv",
            "results/split_composition/udpflood_by_ambiguity_published.csv",
        ],
        "operating_point":
            "validation FPR <= 1%, thresholds frozen before test",
        "evaluation_scope":
            "within-capture (within-session) generalisation; these figures do "
            "NOT establish unseen-capture, unseen-session, "
            "unseen-base-station or unseen-attack generalisation",
        "figures_4_and_5":
            "not reproducible here: the M2 and M3 synthetic diagnostics behind "
            "them were never committed, as the manuscript's data-availability "
            "statement records. Their owners must re-run and archive those "
            "outputs.",
    }
    (out_dir / "paper_figure_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    for path in written:
        print("      wrote " + str(path), flush=True)
    print("      wrote " + str(out_dir / "paper_figure_manifest.json"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
