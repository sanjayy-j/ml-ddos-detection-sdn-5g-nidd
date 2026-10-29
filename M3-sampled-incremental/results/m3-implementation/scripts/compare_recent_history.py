"""Reproduce the baseline and evaluate ONE fixed, exploratory history candidate."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import sys
import zipfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from m3.experimental_history import replay_comparison


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate(trials):
    result = {"trials": len(trials), "models": {}, "changes": {}}
    for name in ("current", "recent_history"):
        metrics = trials[0]["models"][name]["metrics"]
        means = {}
        for key in metrics:
            values = [t["models"][name]["metrics"][key] for t in trials
                      if t["models"][name]["metrics"][key] is not None]
            means[key] = mean(values) if values else None
        result["models"][name] = {
            "mean_metrics": means,
            "pooled_confusion": {key: sum(t["models"][name]["confusion"][key] for t in trials)
                                 for key in ("tp", "fp", "tn", "fn")},
        }
    for key, old in result["models"]["current"]["mean_metrics"].items():
        new = result["models"]["recent_history"]["mean_metrics"][key]
        result["changes"][key] = {
            "percentage_points": 100 * (new - old) if old is not None and new is not None else None,
            "relative_percent": 100 * (new - old) / old if old and new is not None else None,
        }
    result["trials_with_lower_fpr"] = sum(t["models"]["recent_history"]["metrics"][
        "false_positive_rate"] < t["models"]["current"]["metrics"]["false_positive_rate"]
        for t in trials)
    result["trials_with_lower_recall"] = sum(t["models"]["recent_history"]["metrics"][
        "recall"] < t["models"]["current"]["metrics"]["recall"] for t in trials)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path,
                        default=ROOT / "research/results/derived_trial_evidence.zip")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/experiments/recent_history_v1")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output / "protocol.json").exists():
        raise SystemExit("Output already has a protocol; choose a fresh --output directory")
    protocol = {
        "created_utc": datetime.now(UTC).isoformat(),
        "experiment": "recent_history_v1", "scope": "Exploratory offline quality comparison",
        "candidate_count": 1, "history_seconds": 0.5, "current_window_included": True,
        "selection": "All 54 archived primary trials, no outcome-based exclusions",
        "baseline_gate": "Every scored prediction identical; maximum score error <= 1e-10; "
                         "F1, recall and FPR reproduce archived metrics within 1e-12",
        "labels": "Recorded availability timestamps, predict before current label, "
                  "train on prior labels only when available; same seeds/settings",
        "aggregation": "Arithmetic mean of per-trial metrics; paired trial deltas; "
                       "pooled confusion counts also provided",
        "caveats": ["Existing trials were inspected during diagnosis: no untouched test set",
                    "Repeated scenarios reuse traffic; repeats are not independent captures",
                    "Not a live candidate run; no new latency, CPU, bandwidth or knee claims",
                    "Oracle-supervised adaptation is retained, not autonomous labeling"],
        "archive_sha256": sha256(args.archive),
        "implementation_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in (
            Path(__file__), ROOT / "src/m3/experimental_history.py", ROOT / "src/m3/model.py")},
        "python": platform.python_version(),
        "dependencies": {k: importlib.metadata.version(k) for k in ("river", "numpy", "scipy")},
    }
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2), encoding="utf-8")
    trials = []
    with zipfile.ZipFile(args.archive) as archive:
        summaries = sorted(n for n in archive.namelist() if n.endswith("/run_summary.json"))
        if len(summaries) != 54:
            raise ValueError("Expected the complete 54-trial archive")
        cells = set()
        for i, entry in enumerate(summaries, 1):
            saved = json.loads(archive.read(entry))
            if saved["validation"].get("accepted") is not True:
                raise ValueError(f"Trial not accepted: {entry}")
            config = saved["config"]
            if config["window_seconds"] != 0.1:
                raise ValueError("Only the original 0.1-second primary windows are allowed")
            cell = (saved["scenario"], saved["sampling_rate"], config["trial_id"])
            if cell in cells:
                raise ValueError(f"Duplicate trial cell {cell}")
            cells.add(cell)
            rows = [json.loads(line) for line in archive.read(
                entry.replace("run_summary.json", "features.jsonl")).splitlines()]
            comparison = replay_comparison(rows, config)
            if comparison["baseline_prediction_mismatches"] or comparison[
                    "max_baseline_score_error"] > 1e-10:
                raise ValueError(f"Baseline predictions did not reproduce: {entry}")
            for key in ("f1", "recall", "false_positive_rate"):
                if abs(comparison["models"]["current"]["metrics"][key]
                       - saved["metrics"][key]["value"]) > 1e-12:
                    raise ValueError(f"Baseline metric {key} did not reproduce: {entry}")
            predictions = comparison.pop("predictions")
            (args.output / f"{saved['run_id']}_predictions.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in predictions), encoding="utf-8")
            comparison.update(run_id=saved["run_id"], scenario=saved["scenario"],
                              sampling_rate=saved["sampling_rate"], trial_id=config["trial_id"],
                              seed=config["seed"], recorded_dependencies=saved.get("dependencies"))
            trials.append(comparison)
            (args.output / "trials.partial.json").write_text(json.dumps(trials, indent=2),
                                                            encoding="utf-8")
            print(f"{i}/54 {cell}: baseline reproduced; "
                  f"FPR {comparison['models']['current']['metrics']['false_positive_rate']:.4f} -> "
                  f"{comparison['models']['recent_history']['metrics']['false_positive_rate']:.4f}",
                  flush=True)
    expected = {(s, n, t) for s in ("baseline", "drift", "unseen")
                for n in (1, 2, 5, 10, 20, 50) for t in (1, 2, 3)}
    if cells != expected:
        raise ValueError("Archive cells do not match the declared experiment matrix")
    grouped = defaultdict(list)
    for trial in trials:
        grouped[(trial["scenario"], trial["sampling_rate"])].append(trial)
    report = {"protocol": protocol, "baseline_reproduced_all_trials": True,
              "all_trials": aggregate(trials),
              "n2": aggregate([t for t in trials if t["sampling_rate"] == 2]),
              "groups": [{"scenario": s, "sampling_rate": n, **aggregate(group)}
                         for (s, n), group in sorted(grouped.items())], "trials": trials}
    (args.output / "comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Recent-history detector comparison", "", ("Exploratory offline quality only. "
             "One fixed 0.5-second candidate; original live detector/results unchanged."), "",
             "All 54 baseline trials reproduced their saved scored predictions and quality metrics.",
             "", ("Values are mean percentages across trials. Delta is new minus current, "
             "in percentage points. Negative FPR is better; negative recall/F1 is worse."), "",
             ("| Scope | Trials | FPR current -> new | FPR delta | Recall current -> new | "
             "F1 current -> new |"), "|---|---:|---:|---:|---:|---:|"]
    scopes = [("All rates", report["all_trials"]), ("N=2 overall", report["n2"])]
    scopes += [(f"{g['scenario']}, N={g['sampling_rate']}", g) for g in report["groups"]]
    for title, group in scopes:
        a, b = [group["models"][name]["mean_metrics"] for name in ("current", "recent_history")]
        lines.append(f"| {title} | {group['trials']} | "
                     f"{100*a['false_positive_rate']:.2f} -> {100*b['false_positive_rate']:.2f} | "
                     f"{group['changes']['false_positive_rate']['percentage_points']:+.2f} | "
                     f"{100*a['recall']:.2f} -> {100*b['recall']:.2f} | "
                     f"{100*a['f1']:.2f} -> {100*b['f1']:.2f} |")
    lines += ["", "## Limits", ""] + [f"- {c}" for c in protocol["caveats"]]
    lines += ["", ("The JSON includes relative percentage changes, pooled confusion counts, "
              "per-trial outcomes and implementation/data hashes. This is not confirmatory evidence "
              "on fresh traffic. Candidate deployment and a new Pareto knee require live evaluation.")]
    (args.output / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (args.output / "per_trial.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id", "scenario", "sampling_rate", "trial_id", "model",
                         "fpr_percent", "recall_percent", "f1_percent", "tp", "fp", "tn", "fn"])
        for t in trials:
            for name, result in t["models"].items():
                writer.writerow([t["run_id"], t["scenario"], t["sampling_rate"], t["trial_id"],
                                 name, *[100 * result["metrics"][k] for k in
                                         ("false_positive_rate", "recall", "f1")],
                                 *[result["confusion"][k] for k in ("tp", "fp", "tn", "fn")]])
    print(f"Completed: {args.output / 'REPORT.md'}", flush=True)


if __name__ == "__main__":
    main()
