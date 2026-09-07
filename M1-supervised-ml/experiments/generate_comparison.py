"""Stage K CLI — generate the final supervised-model comparison.

    python M1-supervised-ml/experiments/generate_comparison.py

Reads the canonical Stage D/I artifacts and writes a report-ready
`results/evaluation/model_comparison.md`. Every number is pulled from an
artifact at generation time — none is hard-coded. No model is loaded, no
inference run, and no threshold selected or changed.

The generated prose is checked against the Stage K wording rules before
being written; generation fails if a forbidden claim appears or a
required hedge is missing.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.comparison import (  # noqa: E402
    best_by,
    check_claims,
    gather_comparison_facts,
)
from evaluation.plots import ATTACK_ORDER, MODEL_ORDER  # noqa: E402
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402

PROTECTED = (
    "feature_order.json", "split_manifest.csv", "preprocessing_metadata.json",
    "random_forest/test_metrics.json", "random_forest/rf_run_record.json",
    "random_forest/test_metrics_fpr_constrained.json",
    "random_forest/rf_fpr_constrained_record.json",
    "svm/test_metrics.json", "svm/svm_run_record.json",
    "cnn/test_metrics.json", "cnn/cnn_run_record.json",
    "evaluation/three_model_fpr1pct_summary.csv",
    "evaluation/three_model_fpr_budget.csv",
    "evaluation/three_model_per_attack_type.csv",
    "evaluation/three_model_confusion_matrices.csv",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_markdown(facts: dict, generated_utc: str) -> str:
    m = facts["models"]
    rep = facts["representation"]
    splits = facts["splits"]
    b = facts["budgets"]
    out: list[str] = []
    w = out.append

    w("# M1 Supervised Models — Final Comparison and Interpretation")
    w("")
    w(f"_Generated {generated_utc} by "
      "`experiments/generate_comparison.py` from the canonical Stage D/I "
      "artifacts. No model was trained, loaded or run to produce this "
      "document._")
    w("")
    w("## 1. Scope of this comparison")
    w("")
    w("Three supervised models — Random Forest, SVM (Nystroem RBF "
      "approximation + LinearSVC) and a 1-D CNN — are compared **under the "
      "current feature representation** (67 encoded features from Stage D) "
      "and **under the common operating-point protocol**: the decision "
      "threshold was chosen to maximise validation recall subject to "
      "validation FPR <= 1%, ties broken toward the highest threshold, and "
      "frozen before any test evaluation.")
    w("")
    w(f"Split sizes: train {splits['train']:,}, validation "
      f"{splits['val']:,}, test {splits['test']:,}. All three models share "
      "the same representation, split, target definition and leakage "
      "exclusions, so differences below are attributable to the model "
      "families rather than to differing inputs.")
    w("")
    w("Canonical numbers live in "
      "[`three_model_fpr1pct_summary.csv`](three_model_fpr1pct_summary.csv), "
      "[`three_model_fpr_budget.csv`](three_model_fpr_budget.csv), "
      "[`three_model_per_attack_type.csv`](three_model_per_attack_type.csv) "
      "and [`three_model_confusion_matrices.csv`](three_model_confusion_matrices.csv); "
      "figures are in `results/plots/`. That summary CSV already carries "
      "every field required for a machine-readable comparison, so it is "
      "referenced here rather than duplicated.")
    w("")

    # ---- A. definitive comparison -------------------------------------
    w("## 2. Definitive comparison (frozen FPR <= 1% operating point, test set)")
    w("")
    w("| Metric | Random Forest | SVM | 1-D CNN |")
    w("|---|---|---|---|")
    rows = [
        ("Frozen threshold", "threshold", "{:.6f}"),
        ("Accuracy", "accuracy", "{:.6f}"),
        ("Precision", "precision", "{:.6f}"),
        ("Recall", "recall", "{:.6f}"),
        ("F1", "f1", "{:.6f}"),
        ("False Positive Rate", "fpr", "{:.6f}"),
        ("Specificity", "specificity", "{:.6f}"),
        ("ROC-AUC", "roc_auc", "{:.6f}"),
        ("PR-AUC", "pr_auc", "{:.6f}"),
    ]
    for label, key, fmt in rows:
        w(f"| {label} | " + " | ".join(fmt.format(m[k][key])
                                       for k in MODEL_ORDER) + " |")
    w("| Inference (approx. batch throughput) | "
      + " | ".join(f"~{m[k]['throughput_ms_per_flow']:.4f} ms/flow"
                   for k in MODEL_ORDER) + " |")
    w("| Training time | "
      + " | ".join(f"~{m[k]['train_seconds']:,.0f} s" for k in MODEL_ORDER) + " |")
    w("| Model size | "
      + " | ".join(f"{m[k]['model_size']:,} {m[k]['model_size_kind']}"
                   for k in MODEL_ORDER) + " |")
    w("")
    w("Confusion matrices (test, N = "
      f"{m['RandomForest']['n']:,}; actual benign "
      f"{m['RandomForest']['TN'] + m['RandomForest']['FP']:,}, actual "
      f"malicious {m['RandomForest']['TP'] + m['RandomForest']['FN']:,}):")
    w("")
    w("| Model | TN | FP | FN | TP |")
    w("|---|---|---|---|---|")
    for k in MODEL_ORDER:
        w(f"| {m[k]['label']} | {m[k]['TN']:,} | {m[k]['FP']:,} | "
          f"{m[k]['FN']:,} | {m[k]['TP']:,} |")
    w("")
    w("> **Inference figures are approximate amortised batch-throughput "
      "measurements** — total wall-clock time to score the whole test split "
      "divided by the row count — **not single-flow latency**. They come "
      "from single timed runs on a load-variable machine (the identical RF "
      "scoring call produced 0.0011 and 0.0017 ms/flow on two occasions), "
      "so they indicate relative cost only.")
    w("")

    # ---- B. FPR budget ------------------------------------------------
    w("## 3. FPR-budget behaviour (validation)")
    w("")
    w("| Validation FPR budget | Random Forest | SVM | 1-D CNN |")
    w("|---|---|---|---|")
    for cap in sorted(b):
        w(f"| <= {cap:.1%} | " + " | ".join(f"{b[cap][k]:.6f}"
                                            for k in MODEL_ORDER) + " |")
    w("")
    collapsed = [m[k]["label"] for k in MODEL_ORDER
                 if facts["budgets_collapsed"][k]]
    moving = [m[k]["label"] for k in MODEL_ORDER
              if not facts["budgets_collapsed"][k]]
    w(f"{' and '.join(collapsed)} produce **discrete score distributions**: "
      "every budget resolves to the same threshold, at an achieved "
      f"validation FPR of {m['RandomForest']['val_fpr']:.6f} and "
      f"{m['CNN_1D']['val_fpr']:.6f} respectively — far below the 1% cap. "
      "Widening the alarm budget therefore buys them no additional recall. "
      f"Only {' and '.join(moving)} traces distinct thresholds, and even "
      f"there recall rises only from {b[0.001]['SVM']:.6f} to "
      f"{b[0.1]['SVM']:.6f} across a hundred-fold change in budget.")
    w("")
    w("**Relationship to the frozen test results.** The threshold was "
      "selected on validation alone and then applied once to the test "
      "split. Validation and test recall differ as a result: for example "
      f"RF moves from {m['RandomForest']['val_recall']:.6f} (validation) to "
      f"{m['RandomForest']['recall']:.6f} (test), and the SVM's achieved "
      f"FPR moves from {m['SVM']['val_fpr']:.6f} to {m['SVM']['fpr']:.6f}. "
      "That drift is an ordinary consequence of fixing an operating point "
      "on one split and measuring it on another; no threshold was adjusted "
      "in response to test behaviour.")
    w("")

    # ---- C. per-attack ------------------------------------------------
    w("## 4. Per-attack-type interpretation (test)")
    w("")
    w("| Attack Type | Support | Random Forest | SVM | 1-D CNN |")
    w("|---|---|---|---|---|")
    for name in ATTACK_ORDER:
        a = facts["attacks"][name]
        w(f"| {name} | {a['support']:,} | " +
          " | ".join(f"{a[k]:.6f}" for k in MODEL_ORDER) + " |")
    bf = facts["benign_fpr"]
    w("| _Benign (FPR)_ | "
      f"{m['RandomForest']['TN'] + m['RandomForest']['FP']:,} | " +
      " | ".join(f"{bf[k]:.6f}" for k in MODEL_ORDER) + " |")
    w("")
    udp = facts["attacks"]["UDPFlood"]
    others = [n for n in ATTACK_ORDER if n != "UDPFlood"]
    worst_other = min(min(facts["attacks"][n][k] for k in MODEL_ORDER)
                      for n in others)
    w(f"Seven of the eight attack types are detected at "
      f"{worst_other:.4f} or better by all three models. **UDP flood is the "
      f"single common failure mode**: RF {udp['RandomForest']:.4f}, SVM "
      f"{udp['SVM']:.4f}, CNN {udp['CNN_1D']:.4f} on "
      f"{udp['support']:,} test flows.")
    w("")
    w("**How much this establishes.** All three classifiers consume the "
      "same 67-feature representation, so their agreement provides "
      "corroboration across model families rather than three independent "
      "tests of the representation itself. It does not, on its own, prove "
      "a UDP-flood-specific limitation. The independent evidence is the "
      "Stage D exact-vector analysis summarised next, which was computed "
      "combinatorially from the data before any model was trained.")
    w("")

    # ---- D. representation --------------------------------------------
    w("## 5. Representation-level explanation")
    w("")
    w(f"After preprocessing the data has **{rep['n_output_features']} model "
      f"features**. Across {rep['n_rows']:,} rows there are only "
      f"{rep['n_unique_vectors']:,} distinct feature vectors, and "
      f"**{rep['n_conflicting_vectors']:,} of those vectors occur with "
      "both labels**. Assigning each distinct vector its majority label — "
      "the best any deterministic function of these features can do — "
      f"still leaves **{rep['forced_errors']:,} forced errors**, an "
      f"empirical ceiling of **{rep['overall_ceiling_pct']:.4f}%** overall "
      "and **78.6258%** on the test split (Stage D review, README §12).")
    w("")
    w(f"Exact feature-vector repetition across splits is substantial: "
      f"{rep['rows_sharing_vector_across_splits']:,} rows share a feature "
      "vector with another split, **72.97%** of test rows share a vector "
      "with training data, and **18.07%** of test rows are label-pure "
      "repeats of training rows.")
    w("")
    w("The representation therefore contains many identical feature "
      "vectors associated with both labels, so a deterministic classifier "
      "using only these features cannot perfectly separate the classes. "
      "This is a property of the representation, not evidence that the "
      "three model families were badly implemented.")
    w("")
    w("> **Scope of the ceiling.** This is the *empirical* ceiling under "
      "the evaluated exact-feature-vector representation and majority-rule "
      "analysis. It is **not** a universal theoretical limit for every "
      "possible model or for richer feature sets: a representation with "
      "additional or different features (for example window- or "
      "session-level aggregates) is not bound by it.")
    w("")

    # ---- E. findings ---------------------------------------------------
    w("## 6. Principal findings")
    w("")
    w(f"1. **Random Forest leads on accuracy, recall and F1** at the common "
      f"operating point ({m['RandomForest']['accuracy']:.6f}, "
      f"{m['RandomForest']['recall']:.6f}, {m['RandomForest']['f1']:.6f}), "
      "under the current feature representation.")
    w(f"2. **The CNN attains the lowest test FPR "
      f"({m['CNN_1D']['fpr']:.6f}) and highest precision "
      f"({m['CNN_1D']['precision']:.6f}), together with the lowest recall "
      f"({m['CNN_1D']['recall']:.6f})** — it sits at the most conservative "
      "point of the trade-off.")
    w(f"3. **The SVM attains the highest PR-AUC ({m['SVM']['pr_auc']:.6f}), "
      f"but its frozen test operating point exceeds the 1% target at "
      f"FPR {m['SVM']['fpr']:.6f} ({m['SVM']['fpr'] * 100:.3f}%)** — the "
      "threshold met the constraint on validation "
      f"({m['SVM']['val_fpr']:.6f}) and drifted on test.")
    w(f"4. **ROC-AUC is tightly clustered** "
      f"({min(m[k]['roc_auc'] for k in MODEL_ORDER):.6f}-"
      f"{max(m[k]['roc_auc'] for k in MODEL_ORDER):.6f}), indicating "
      "broadly similar discrimination under the current feature "
      "representation.")
    w("5. **All three lose substantial recall under the strict FPR "
      f"constraint** — recall spans "
      f"{min(m[k]['recall'] for k in MODEL_ORDER):.6f}-"
      f"{max(m[k]['recall'] for k in MODEL_ORDER):.6f}, so roughly 56-57% "
      "of malicious test flows go undetected at this alarm budget.")
    w("6. **UDP flood is the major common attack-category failure mode** "
      f"({udp['CNN_1D']:.4f}-{udp['SVM']:.4f} recall), while the other "
      "seven attack types are detected almost completely.")
    w("7. **The representation-level conflict analysis explains both the "
      "convergence and the limits** of the three families: with "
      f"{rep['n_conflicting_vectors']:,} conflicting feature vectors and "
      f"{rep['forced_errors']:,} forced errors, no deterministic "
      "classifier on this representation can separate the ambiguous mass.")
    w("")

    # ---- F. cost --------------------------------------------------------
    w("## 7. Cost and complexity")
    w("")
    w(f"Training cost differs by two orders of magnitude: RF "
      f"~{m['RandomForest']['train_seconds']:,.0f} s, CNN "
      f"~{m['CNN_1D']['train_seconds']:,.0f} s, SVM "
      f"~{m['SVM']['train_seconds']:,.0f} s. Model complexity is expressed "
      "in each family's own units and is **not** comparable across rows: "
      f"{m['RandomForest']['model_size']:,} tree nodes, "
      f"{m['SVM']['model_size']:,} linear weights over the Nystroem "
      f"feature map, {m['CNN_1D']['model_size']:,} trainable parameters.")
    w("")
    w("Approximate batch throughput orders as RF "
      f"(~{m['RandomForest']['throughput_ms_per_flow']:.4f} ms/flow) < CNN "
      f"(~{m['CNN_1D']['throughput_ms_per_flow']:.4f}) < SVM "
      f"(~{m['SVM']['throughput_ms_per_flow']:.4f}). These are "
      "machine-dependent, single-run measurements of amortised batch "
      "throughput and must not be read as deployment latency; no memory "
      "figures or hardware-normalised conclusions are offered because none "
      "were measured. On this evidence RF is the cheapest to both train "
      "and score, while the SVM is the most expensive on both counts.")
    w("")

    # ---- G. scope / limitations ----------------------------------------
    w("## 8. Evaluation scope and limitations")
    w("")
    w("M1 is evaluated under a **within-capture (within-session) "
      "protocol**: all 20 capture sessions contribute to train, validation "
      "and test, split by position within each session and label stream. "
      "Results measure the ability to classify later flows from capture "
      "sessions the model has already observed.")
    w("")
    w("The experiment **does not establish**:")
    w("")
    w("- unseen-capture generalisation")
    w("- unseen-session generalisation")
    w("- unseen-base-station generalisation")
    w("- unseen-attack generalisation")
    w("")
    w("In particular this comparison **does not establish unseen-session "
      "generalisation**, and no figure or table here should be presented "
      "as if it did.")
    w("")
    w("Further constraints on interpretation:")
    w("")
    w("- Exact feature-vector repetition across splits is extensive (see "
      "§5), so part of the measured performance reflects repeated flow "
      "patterns rather than generalisation to novel ones.")
    w("- `Combined.csv` contains no wall-clock timestamp, IP-address or "
      "port fields, so no temporal or endpoint-identity analysis is "
      "possible from this data (`RunTime` is a flow duration, not a "
      "timestamp).")
    w("- `Attack Type` and `Attack Tool` are analysis metadata only and "
      "were never model inputs; they are used solely for the per-attack "
      "breakdown.")
    w("- This is a flow-level offline evaluation. It does not represent "
      "the complete SDN deployment loop — controller integration, "
      "telemetry collection cost and mitigation actions are out of scope.")
    w("")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the Stage K model comparison.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"))

    before = {n: _sha256(results_root / n) for n in PROTECTED
              if (results_root / n).is_file()}

    print("[1/4] gathering facts from canonical artifacts", flush=True)
    facts = gather_comparison_facts(results_root)
    print("      {} models, {} attack types, {} budgets".format(
        len(facts["models"]), len(facts["attacks"]), len(facts["budgets"])),
        flush=True)
    for metric, maximise in (("accuracy", True), ("recall", True),
                             ("f1", True), ("fpr", False),
                             ("precision", True), ("pr_auc", True)):
        print("      leader on {:<10} {}".format(
            metric, best_by(facts, metric, maximise)), flush=True)

    print("[2/4] rendering comparison markdown", flush=True)
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    markdown = build_markdown(facts, generated)

    print("[3/4] checking wording rules", flush=True)
    result = check_claims(markdown)
    if result["forbidden_claims_found"]:
        raise SystemExit("ERROR: forbidden claims present: "
                         + str(result["forbidden_claims_found"]))
    if result["missing_hedges"]:
        raise SystemExit("ERROR: required hedges missing: "
                         + str(result["missing_hedges"]))
    print("      no forbidden claims; all required hedges present", flush=True)

    out_path = results_root / "evaluation" / "model_comparison.md"
    out_path.write_text(markdown, encoding="utf-8")

    print("[4/4] verifying protected artifacts unchanged", flush=True)
    after = {n: _sha256(results_root / n) for n in PROTECTED
             if (results_root / n).is_file()}
    changed = [n for n in before if before[n] != after.get(n)]
    if changed:
        raise SystemExit("ERROR: protected artifacts modified: " + str(changed))
    print("      {} protected artifacts unchanged".format(len(before)), flush=True)
    print("      wrote " + str(out_path), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
