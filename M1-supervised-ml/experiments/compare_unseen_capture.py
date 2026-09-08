"""Stage L — primary (within-capture) vs secondary (unseen-capture) comparison.

    python M1-supervised-ml/experiments/compare_unseen_capture.py

Reads the frozen Stage I artifacts and the Stage L per-model records and
writes a report-ready comparison. It loads no model, runs no inference and
selects no threshold.

The two evaluations use DIFFERENT test populations and are therefore not
directly rankable against each other; the generated document states that
explicitly and always reports the representation-conflict difference
alongside any metric difference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402

MODELS = (("rf", "RandomForest", "Random Forest"),
          ("svm", "SVM", "SVM (Nystroem + LinearSVC)"),
          ("cnn", "CNN_1D", "1-D CNN"))

METRICS = ("accuracy", "precision", "recall", "f1", "fpr", "tnr",
           "roc_auc", "pr_auc")

PROTECTED = (
    "feature_order.json", "split_manifest.csv", "preprocessing_metadata.json",
    "random_forest/test_metrics.json", "random_forest/rf_run_record.json",
    "random_forest/rf_fpr_constrained_record.json",
    "svm/svm_run_record.json", "cnn/cnn_run_record.json",
    "evaluation/three_model_fpr1pct_summary.csv",
    "evaluation/three_model_per_attack_type.csv",
    "evaluation/model_comparison.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(results_root: Path, generated: str) -> tuple[str, pd.DataFrame]:
    ev = results_root / "evaluation"
    uc = results_root / "unseen_capture"
    primary = pd.read_csv(ev / "three_model_fpr1pct_summary.csv").set_index("model")
    prep = json.loads((uc / "unseen_capture_preparation.json").read_text(
        encoding="utf-8"))

    rows, available = [], []
    for short, key, label in MODELS:
        record_path = uc / short / "unseen_capture_record.json"
        if not record_path.is_file():
            continue
        available.append((short, key, label))
        rec = json.loads(record_path.read_text(encoding="utf-8"))
        held, prim = rec["held_out_metrics"], primary.loc[key]
        row = {"model": label, "evaluation": "secondary (unseen-capture)",
               "threshold": rec["operating_point"]["threshold"]}
        row.update({m: held[m] for m in METRICS})
        rows.append(row)
        row = {"model": label, "evaluation": "primary (within-capture)",
               "threshold": float(prim["threshold"])}
        row.update({m: float(prim[{"tnr": "test_specificity"}.get(
            m, f"test_{m}" if m in ("accuracy", "precision", "recall", "f1",
                                    "fpr") else m)]) for m in METRICS})
        rows.append(row)
    table = pd.DataFrame(rows)

    nl, np_ = prep["novelty_stage_l"], prep["novelty_primary"]
    out: list[str] = []
    w = out.append
    w("# Stage L — Secondary Unseen-Capture Generalisation Experiment")
    w("")
    w(f"_Generated {generated} by `experiments/compare_unseen_capture.py` "
      "from frozen Stage I and Stage L artifacts. No model was loaded, no "
      "inference run, no threshold selected._")
    w("")
    w("## 1. What this experiment is — and is not")
    w("")
    w("This is a **secondary** evaluation. It does **not** replace the "
      "primary Stage E within-capture protocol, whose results remain the "
      "project's primary results.")
    w("")
    w(f"Eight whole capture blocks — **{prep['held_out_blocks']}** — were "
      "held out entirely. Models were trained, selected and thresholded "
      f"using only the twelve development blocks "
      f"**{prep['development_blocks']}**.")
    w("")
    w("| Partition | Rows | Malicious % |")
    w("|---|---|---|")
    for name in ("dev_train", "dev_val", "held_out"):
        w(f"| {name} | {prep['rows'][name]:,} | "
          f"{prep['malicious_pct'][name]:.4f} |")
    w("")
    w("Preprocessing was fitted on **development-train only** "
      f"({prep['preprocessing_provenance']['fit_rows']:,} rows; scaler "
      f"confirmed to have seen exactly that many). No primary preprocessor, "
      "matrix or model was reused.")
    w("")
    w("## 2. The interpretation constraint — read before the numbers")
    w("")
    w("**UDPFlood is absent from the held-out blocks and is NOT evaluable "
      "under this holdout.** It could not be included: every feasible "
      "whole-block subset containing block 4 or 14 carries a 42.9-43.5 pp "
      "class-prior shift. No substitute attack type was used.")
    w("")
    w("This matters because the ambiguous mass that dominates the primary "
      "evaluation is almost entirely UDP flood:")
    w("")
    w("| Population | Rows in conflicting feature vectors |")
    w("|---|---|")
    w(f"| Primary Stage E test | **{np_['pct_rows_in_conflicting_vectors']}%** |")
    w(f"| Stage L held-out blocks | **{nl['pct_rows_in_conflicting_vectors']}%** |")
    w("")
    w("The two evaluations therefore score **different and unequally "
      "difficult populations**. Any metric difference between them must be "
      "interpreted jointly with this conflict disparity and with the "
      "differing class composition — **it must NOT be read as a pure "
      "improvement in generalisation.**")
    w("")
    w("## 3. Feature-vector novelty")
    w("")
    w("| Statistic | Stage L held-out | Primary test |")
    w("|---|---|---|")
    for key, label in (("pct_rows_vector_seen_in_reference",
                        "Rows whose vector occurs in development"),
                       ("pct_rows_vector_unseen_in_reference",
                        "Rows whose vector is unseen"),
                       ("pct_rows_in_conflicting_vectors",
                        "Rows in conflicting vectors"),
                       ("pct_unseen_vectors_that_are_conflicting",
                        "Unseen vectors that are conflicting")):
        w(f"| {label} | {nl[key]}% | {np_[key]}% |")
    w("")
    w("The held-out population is substantially more novel "
      f"({nl['pct_rows_vector_unseen_in_reference']}% of rows carry a "
      "feature vector never seen in development, versus "
      f"{np_['pct_rows_vector_unseen_in_reference']}% for the primary "
      "test). Novelty alone does not demonstrate generalisation; it "
      "characterises how different the evaluation population is.")
    w("")
    w("## 4. Held-out results vs primary results")
    w("")
    w("> The two rows per model are **not directly rankable** — different "
      "test populations, different difficulty (see §2).")
    w("")
    w("| Model | Evaluation | Accuracy | Precision | Recall | F1 | FPR | "
      "ROC-AUC | PR-AUC |")
    w("|---|---|---|---|---|---|---|---|---|")
    for row in table.itertuples():
        w(f"| {row.model} | {row.evaluation} | {row.accuracy:.6f} | "
          f"{row.precision:.6f} | {row.recall:.6f} | {row.f1:.6f} | "
          f"{row.fpr:.6f} | {row.roc_auc:.6f} | {row.pr_auc:.6f} |")
    w("")
    if len(available) < len(MODELS):
        missing = [m[2] for m in MODELS if m not in available]
        w(f"> **Incomplete:** results are not yet available for: "
          f"{', '.join(missing)}.")
        w("")

    w("## 5. Per-block held-out results")
    w("")
    for short, _, label in available:
        blocks = pd.read_csv(uc / short / "per_block_metrics.csv")
        w(f"**{label}**")
        w("")
        w("| Block | BS | Attack types | Rows | Malicious % | Accuracy | "
          "Precision | Recall | F1 | FPR | Specificity |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for b in blocks.itertuples():
            w(f"| {b.block} | {b.base_station} | {b.attack_types} | "
              f"{b.rows:,} | {b.malicious_pct:.3f} | {b.accuracy:.6f} | "
              f"{b.precision:.6f} | {b.recall:.6f} | {b.f1:.6f} | "
              f"{b.fpr:.6f} | {b.tnr:.6f} |")
        w("")
    w("Block 19 is benign-only, so recall and precision are undefined there "
      "and report as 0; its false-positive rate is the meaningful quantity.")
    w("")

    w("## 6. Per-attack-type held-out results")
    w("")
    w("| Attack type | " + " | ".join(l for _, _, l in available) + " |")
    w("|---" * (len(available) + 1) + "|")
    per = {s: pd.read_csv(uc / s / "per_attack_type.csv").set_index("group")
           for s, _, _ in available}
    groups = sorted(set().union(*(set(p.index) for p in per.values())) - {"Benign"})
    for g in groups:
        cells = []
        for s, _, _ in available:
            cells.append(f"{per[s].loc[g, 'recall']:.6f}"
                         if g in per[s].index else "-")
        w(f"| {g} | " + " | ".join(cells) + " |")
    w("| _Benign (FPR)_ | " + " | ".join(
        f"{per[s].loc['Benign', 'fpr']:.6f}" for s, _, _ in available) + " |")
    w("| **UDPFlood** | " + " | ".join(
        "**NOT PRESENT / NOT EVALUABLE**" for _ in available) + " |")
    w("")

    w("## 7. Limitations")
    w("")
    w("- **UDPFlood is not evaluable** under this holdout; Stage L cannot "
      "measure unseen-capture generalisation for the project's dominant "
      "failure mode.")
    w("- The held-out population is far less ambiguous than the primary "
      "test population, so held-out metrics are **not** comparable to "
      "primary metrics as a like-for-like improvement.")
    w("- Thresholds were fitted on development-validation, whose "
      "composition differs sharply from the held-out blocks; this alone can "
      "move the achieved operating point.")
    w("- This remains an offline flow-level evaluation. It does **not** "
      "establish real-world SDN/5G deployment performance, and does not "
      "cover controller integration, telemetry cost or mitigation.")
    w("- Results are specific to the evaluated 67-feature representation.")
    w("")
    return "\n".join(out) + "\n", table


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage L comparison.")
    parser.add_argument("--config", default=str(
        M1_ROOT / "config" / "m1_config_unseen_capture.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    results_root = resolve_path(REPO_ROOT, "M1-supervised-ml/results")
    uc = resolve_path(REPO_ROOT, config["output"]["results_dir"])

    before = {n: _sha256(results_root / n) for n in PROTECTED
              if (results_root / n).is_file()}

    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    markdown, table = build(results_root, generated)
    (uc / "unseen_capture_comparison.md").write_text(markdown, encoding="utf-8")
    table.to_csv(uc / "primary_vs_secondary.csv", index=False)

    after = {n: _sha256(results_root / n) for n in PROTECTED
             if (results_root / n).is_file()}
    changed = [n for n in before if before[n] != after.get(n)]
    if changed:
        raise SystemExit("ERROR: protected artifacts modified: " + str(changed))
    print("wrote {} ({} protected artifacts unchanged)".format(
        uc / "unseen_capture_comparison.md", len(before)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
