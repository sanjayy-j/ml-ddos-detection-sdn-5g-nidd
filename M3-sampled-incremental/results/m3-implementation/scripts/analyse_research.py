"""Analyse accepted official real-time trials without creating numeric evidence.

Run with the project's environment: python scripts/analyse_research.py
--runs output/runs --output output/research. No live traffic is started here.
"""

import argparse
import csv
import json
from pathlib import Path

from m3.research_metrics import (
    aggregate_trials,
    comparison_signature,
    eligible,
    evaluate_ablations,
    paired_deltas,
    research_readiness,
    select_pareto,
)
from m3.store import atomic_json


def _features(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def analyse(runs_root, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    runs, read_errors, ablations = [], [], []
    for path in sorted(Path(runs_root).rglob("run_summary.json")):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            read_errors.append({"path": str(path), "error": str(exc)})
            continue
        runs.append(run)
        if not eligible(run):
            continue
        sensitivity_path = path.parent / "sensitivity.json"
        if sensitivity_path.is_file():
            sensitivity = json.loads(sensitivity_path.read_text())
            if (sensitivity.get("primary_run_id") == run["run_id"]
                    and sensitivity.get("window_seconds") == 1
                    and sensitivity.get("raw_hashes") == run.get("raw_hashes")
                    and sensitivity.get("models")):
                run.setdefault("research", {})["sensitivity_completed"] = True
        feature_path = path.parent / "features.jsonl"
        if feature_path.is_file():
            try:
                config = run.get("config", {})
                result = evaluate_ablations(
                    _features(feature_path), seed=run.get("seed", 1),
                    grace_period=config.get("grace_period", 50),
                    drift_delta=config.get("drift_delta", 0.002),
                    threshold=config.get("threshold", 0.5),
                )
                for key in ("f1", "precision", "recall", "roc_auc", "false_positive_rate"):
                    observed = run["metrics"].get(key, {}).get("value")
                    replayed = result["hat_adwin"]["metrics"][key]["value"]
                    if (observed is None) != (replayed is None) or (
                            observed is not None and abs(observed - replayed) > 1e-12):
                        raise ValueError(f"Recorded HAT quality does not reproduce: {key}")
                ablations.append({"run_id": run["run_id"], "models": result})
                run.setdefault("research", {})["ablations_completed"] = True
            except (OSError, ValueError, KeyError, TypeError) as exc:
                read_errors.append({"path": str(feature_path), "error": str(exc)})
    aggregate = aggregate_trials(runs)
    paired = paired_deltas(runs)
    fronts = []
    for signature in sorted({comparison_signature(run) for run in runs if eligible(run)}):
        points = []
        for group in aggregate["groups"]:
            if group["comparison_group"] != signature:
                continue
            metric = group["metrics"]
            def cost(name, metric=metric):
                item = metric.get(name, {})
                return {"value": item.get("mean"), "unit": item.get("unit"),
                        "status": "measured" if item.get("n") == 3 else "unavailable"}
            points.append({"sampling_rate": group["sampling_rate"],
                           "f1": metric.get("f1", {}).get("mean")
                           if group["complete_three_trials"] else None,
                           "sflow_bandwidth_kbit_s": cost("sflow_bandwidth_kbit_s"),
                           "openflow_bandwidth_kbit_s": cost("openflow_bandwidth_kbit_s")})
        fronts.append({"comparison_group": signature, **select_pareto(points)})
    readiness = research_readiness(runs)
    readiness["input_read_errors"] = read_errors
    if read_errors:
        readiness["ready"] = False
    atomic_json(output / "research_readiness.json", readiness)
    atomic_json(output / "aggregated_metrics.json", aggregate)
    atomic_json(output / "paired_deltas.json", paired)
    atomic_json(output / "quality_ablations.json", ablations)
    atomic_json(output / "pareto_recommendations.json", fronts)
    with (output / "aggregated_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["comparison_group", "scenario", "sampling_rate", "metric", "n", "mean",
                         "sample_sd", "ci95_lower", "ci95_upper", "unit", "missing_trials"])
        for group in aggregate["groups"]:
            for name, item in group["metrics"].items():
                interval = item["ci95"] or [None, None]
                writer.writerow([group["comparison_group"], group["scenario"], group["sampling_rate"],
                                 name, item["n"], item["mean"], item["sample_sd"], *interval,
                                 item["unit"], item["missing_trials"]])
    for index, front in enumerate(fronts):
        points = front["front"]
        if not points:
            continue
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with plt.style.context("seaborn-v0_8-whitegrid"):
            figure, axis = plt.subplots(figsize=(7, 4.5))
            for point in points:
                axis.scatter(point["combined_bandwidth_kbit_s"], point["f1"])
                axis.annotate(f"N={point['sampling_rate']}",
                              (point["combined_bandwidth_kbit_s"], point["f1"]),
                              xytext=(4, 4), textcoords="offset points")
            axis.set(xlabel="Measured sFlow + OpenFlow bandwidth (kbit/s)", ylabel="F1",
                     title="Descriptive Pareto candidates: three accepted trials per point")
            figure.tight_layout()
            figure.savefig(output / f"pareto_{index + 1}.png", dpi=180)
            plt.close(figure)
    return readiness


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=Path("output/runs"))
    parser.add_argument("--output", type=Path, default=Path("output/research"))
    args = parser.parse_args()
    readiness = analyse(args.runs, args.output)
    print(json.dumps({"accepted_trials": readiness["accepted_trials"],
                      "ready": readiness["ready"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
