"""Run a fixed three-candidate experiment; never change the production detector."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from m3.experimental_variants import (
    CANDIDATES,
    EXPECTED_CELLS,
    METRICS,
    assess_candidate,
    compare,
    replay_variants,
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percent(value, digits=4):
    return f"{100*value:.{digits}f}%" if value is not None else "unavailable"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path,
                        default=ROOT / "research/results/derived_trial_evidence.zip")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/experiments/detector_variants_v1")
    parser.add_argument("--finalize-existing", action="store_true",
                        help="Finish reporting from complete saved trials without retraining")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if not args.finalize_existing and any(args.output.iterdir()):
        raise SystemExit("Choose a new, empty output directory; existing evidence is not overwritten")
    if args.finalize_existing:
        for name in ("comparison.json", "REPORT.md", "per_trial.csv"):
            if (args.output / name).exists():
                raise SystemExit("Refusing to overwrite completed results")
        protocol = json.loads((args.output / "protocol.json").read_text(encoding="utf-8"))
        trials = json.loads((args.output / "trials.partial.json").read_text(encoding="utf-8"))
        if protocol["candidates"] != CANDIDATES or protocol["archive_sha256"] != sha256(args.archive):
            raise ValueError("Saved training protocol or input archive changed")
        cells = [(t["scenario"], t["sampling_rate"], t["trial_id"]) for t in trials]
        if len(cells) != 54 or set(cells) != EXPECTED_CELLS or any(
                t.get("baseline_metrics_reproduced") is not True
                or t.get("baseline_prediction_mismatches") != 0
                or t.get("max_baseline_score_error", 1) > 1e-10
                or set(t["models"]) != {"current", *CANDIDATES} for t in trials):
            raise ValueError("Incomplete or unverified saved trials")
        finish_report(args.output, protocol, trials, reused_training=True)
        return
    protocol = {
        "created_utc": datetime.now(UTC).isoformat(), "candidates": CANDIDATES,
        "threshold": "Unchanged per saved trial; no threshold search",
        "features": "Exact recorded baseline telemetry; no additional inputs",
        "scope": "Exploratory offline quality; all 54 previously inspected archived trials",
        "primary_operating_point": "N=2; all scenarios and repeats",
        "baseline_gate": "All scored predictions identical, scores within 1e-10; "
                         "all five required quality metrics within 1e-12 of saved live results",
        "quality_gate": "N=2 mean FPR strictly lower and F1 strictly higher; recall no lower in "
                        "any N=2 repeat; N=2 precision/ROC-AUC no lower; FPR, recall and F1 "
                        "no worse in any of 18 scenario/rate cell means",
        "deployment_gate": "Reused offline data cannot authorize default promotion; require "
                           "fresh-data confirmation and paired live cost/latency evidence",
        "selection": "Three fixed single-setting hypotheses; report every result, no post-hoc tuning",
        "label_policy": "Prediction before current label; prior training only after recorded availability",
        "aggregation": "Unweighted mean of per-trial metrics; pooled confusion counts separate",
        "caveats": ["Existing data were used for diagnosis; not untouched held-out validation",
                    "Repeated scenarios reuse traffic; repeats are not independent captures",
                    "Label timing is recorded oracle supervision, not operational human labels",
                    "No new live timing, CPU, bandwidth or knee measurements"],
        "archive_sha256": sha256(args.archive),
        "implementation_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in (
            Path(__file__), ROOT / "src/m3/experimental_variants.py", ROOT / "src/m3/model.py")},
        "python": platform.python_version(),
        "dependencies": {k: importlib.metadata.version(k) for k in ("river", "numpy", "scipy")},
    }
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2), encoding="utf-8")
    trials, cells = [], set()
    with zipfile.ZipFile(args.archive) as archive:
        entries = sorted(n for n in archive.namelist() if n.endswith("/run_summary.json"))
        if len(entries) != 54:
            raise ValueError("Expected the complete 54-trial archive")
        for i, entry in enumerate(entries, 1):
            saved = json.loads(archive.read(entry))
            config = saved["config"]
            cell = (saved["scenario"], saved["sampling_rate"], config["trial_id"])
            if (saved["validation"].get("accepted") is not True
                    or saved["source"] != "official_realtime_verified"
                    or config["window_seconds"] != 0.1 or cell in cells
                    or cell not in EXPECTED_CELLS):
                raise ValueError(f"Unaccepted, unexpected or duplicate primary trial: {cell}")
            cells.add(cell)
            rows = [json.loads(line) for line in archive.read(
                entry.replace("run_summary.json", "features.jsonl")).splitlines()]
            trial = replay_variants(rows, config)
            if trial["baseline_prediction_mismatches"] or trial["max_baseline_score_error"] > 1e-10:
                raise ValueError(f"Baseline predictions did not reproduce: {cell}")
            for key in METRICS:
                if abs(trial["models"]["current"]["metrics"][key]
                       - saved["metrics"][key]["value"]) > 1e-12:
                    raise ValueError(f"Baseline {key} did not reproduce: {cell}")
            trial.update(run_id=saved["run_id"], scenario=cell[0], sampling_rate=cell[1],
                         trial_id=cell[2], seed=config["seed"], baseline_metrics_reproduced=True)
            predictions = trial.pop("predictions")
            (args.output / f"{saved['run_id']}_predictions.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in predictions), encoding="utf-8")
            trials.append(trial)
            (args.output / "trials.partial.json").write_text(json.dumps(trials, indent=2),
                                                            encoding="utf-8")
            print(f"{i}/54 {cell}: baseline exact; " + "; ".join(
                f"{name} FPR={trial['models'][name]['metrics']['false_positive_rate']:.4f}"
                for name in CANDIDATES), flush=True)
    if cells != EXPECTED_CELLS:
        raise ValueError("Incomplete primary matrix")
    finish_report(args.output, protocol, trials)


def finish_report(output, protocol, trials, reused_training=False):
    n2 = [t for t in trials if t["sampling_rate"] == 2]
    candidates = {name: {
        "n2": compare(n2, name), "all_rates": compare(trials, name),
        "gate": assess_candidate(trials, name),
        "groups": [{"scenario": s, "sampling_rate": n, **compare([
            t for t in trials if t["scenario"] == s and t["sampling_rate"] == n], name)}
                   for s, n in sorted({(s, n) for s, n, _ in EXPECTED_CELLS})],
    } for name in CANDIDATES}
    report = {"protocol": protocol, "baseline_reproduced_all_trials": True,
              "candidates": candidates, "trials": trials,
              "production_changed": False}
    report["report_generation"] = {
        "created_utc": datetime.now(UTC).isoformat(), "reused_training": reused_training,
        "trials_sha256": sha256(output / "trials.partial.json"),
        "implementation_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in (
            Path(__file__), ROOT / "src/m3/experimental_variants.py")},
        "note": "Undefined precision retained as null; original training protocol retained",
    }
    (output / "comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Detector variants: baseline-gated comparison", "",
             "Three fixed single-setting candidates. All 54 scored baseline trials reproduced.",
             "No production code or original results changed. Means are per-trial percentages.",
             "", "## Primary setting: N=2 (nine trials)", "",
             "| Detector | False-positive rate | Recall | F1 | Precision | ROC-AUC |",
             "|---|---:|---:|---:|---:|---:|"]
    baseline = next(iter(candidates.values()))["n2"]["current"]["mean_metrics"]
    lines.append("| current | " + " | ".join(percent(baseline[k]) for k in METRICS) + " |")
    for name, result in candidates.items():
        values = result["n2"]["candidate"]["mean_metrics"]
        lines.append(f"| {name} | " + " | ".join(percent(values[k]) for k in METRICS) + " |")
    lines += ["", "## Changes and gate decisions", ""]
    for name, result in candidates.items():
        lines += [f"### {name}", "", f"Only override: `{CANDIDATES[name]}`", ""]
        for scope in ("n2", "all_rates"):
            lines.append(f"{scope} (new minus current):")
            for key, delta in result[scope]["changes"].items():
                rel = delta["relative_percent"]
                rel_text = f"{rel:+.4f}%" if rel is not None else "undefined"
                points = delta["percentage_points"]
                pp_text = f"{points:+.4f}" if points is not None else "unavailable"
                lines.append(f"- {key}: {pp_text} percentage points; "
                             f"relative {rel_text}")
            lines.append("")
        gate = result["gate"]
        lines += [f"Offline quality gate passed: {gate['offline_quality_pass']}", ""]
        lines += [f"- {failure}" for failure in gate["quality_failures"]]
        lines += ["", ("Deployment ready: False; independent fresh-data and paired live "
                  "latency/resource evidence are absent."), ""]
    lines += ["## All scenario/rate means", "",
              ("| Candidate | Scenario | N | FPR current -> new | Recall current -> new | "
              "F1 current -> new |"), "|---|---|---:|---:|---:|---:|"]
    for name, result in candidates.items():
        for group in result["groups"]:
            a, b = group["current"]["mean_metrics"], group["candidate"]["mean_metrics"]
            lines.append(f"| {name} | {group['scenario']} | {group['sampling_rate']} | " +
                         " | ".join(f"{percent(a[k], 2)} -> {percent(b[k], 2)}"
                                    for k in ("false_positive_rate", "recall", "f1")) + " |")
    lines += ["", "## Limits", ""] + [f"- {c}" for c in protocol["caveats"]]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (output / "per_trial.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id", "scenario", "N", "trial_id", "model", *METRICS,
                         "tp", "fp", "tn", "fn"])
        for t in trials:
            for name, result in t["models"].items():
                writer.writerow([t["run_id"], t["scenario"], t["sampling_rate"], t["trial_id"], name,
                                 *[result["metrics"][k] for k in METRICS],
                                 *[result["confusion"][k] for k in ("tp", "fp", "tn", "fn")]])
    print(f"Completed: {output / 'REPORT.md'}", flush=True)


if __name__ == "__main__":
    main()
