"""Aggregate only comparable trials; never conflate offline proxies with live cost."""

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from m3.store import RunRepository, atomic_json

SIGNATURE_KEYS = (
    "threshold",
    "grace_period",
    "drift_delta",
    "window_seconds",
    "warmup_records",
    "warmup_seconds",
    "max_records",
)


def comparison_key(run):
    return json.dumps(
        {
            "source": run["source"],
            "mode": run["mode"],
            "unit": run["unit"],
            "scenario": run["scenario"],
            "feature_schema": run.get("feature_schema"),
            "checksum": (run.get("provenance") or {}).get("sha256"),
            "settings": {k: run["config"].get(k) for k in SIGNATURE_KEYS},
        },
        sort_keys=True,
    )


def pareto(points):
    """Maximise F1 and minimise measured bandwidth. Equality preserves ties."""
    return [
        point
        for point in points
        if not any(
            other["f1"] >= point["f1"]
            and other["cost"] <= point["cost"]
            and (other["f1"] > point["f1"] or other["cost"] < point["cost"])
            for other in points
        )
    ]


def aggregate(runs):
    grouped = defaultdict(list)
    for run in runs:
        if run["status"] == "completed" and run["source"] != "fixture":
            grouped[(comparison_key(run), run["sampling_rate"])].append(run)
    rows = []
    for (key, rate), group in sorted(grouped.items()):
        row = {
            "comparison_group": key,
            "sampling_rate": rate,
            "run_ids": [r["run_id"] for r in group],
            "trials": len(group),
            "distinct_seeds": len({r["seed"] for r in group}),
            "metrics": {},
        }
        names = sorted({name for r in group for name in r["metrics"]})
        for name in names:
            metrics = [r["metrics"].get(name, {}) for r in group]
            values = [m["value"] for m in metrics if m.get("value") is not None]
            signatures = {
                (m.get("unit"), m.get("status")) for m in metrics if m.get("value") is not None
            }
            compatible = len(signatures) == 1
            row["metrics"][name] = {
                "mean": mean(values) if values and compatible else None,
                "std": stdev(values) if len(values) > 1 and compatible else None,
                "min": min(values) if values and compatible else None,
                "max": max(values) if values and compatible else None,
                "n": len(values),
                "unit": next(iter(signatures))[0] if compatible else None,
                "status": next(iter(signatures))[1] if compatible else "unavailable",
                "reasons": sorted({m.get("reason") for m in metrics if m.get("reason")}),
            }
        rows.append(row)
    return rows


def analyse(root, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    runs = RunRepository(root).list()
    rows = aggregate(runs)
    atomic_json(
        output / "aggregated_metrics.json",
        {
            "groups": rows,
            "failed_runs": [
                {"run_id": r["run_id"], "error": r["error"]}
                for r in runs
                if r["status"] == "failed"
            ],
            "notes": [
                "Standard deviation uses ddof=1; n<2 yields null.",
                "Three distinct seeds are required per N; incomplete groups remain visible.",
            ],
        },
    )
    with (output / "aggregated_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "comparison_group",
                "N",
                "trials",
                "distinct_seeds",
                "metric",
                "mean",
                "std",
                "n",
                "unit",
                "status",
            ]
        )
        for row in rows:
            for name, metric in row["metrics"].items():
                writer.writerow(
                    [
                        row["comparison_group"],
                        row["sampling_rate"],
                        row["trials"],
                        row["distinct_seeds"],
                        name,
                        metric["mean"],
                        metric["std"],
                        metric["n"],
                        metric["unit"],
                        metric["status"],
                    ]
                )
    charts = []
    by_group = defaultdict(list)
    for row in rows:
        by_group[row["comparison_group"]].append(row)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fronts = []
    for index, (key, group) in enumerate(by_group.items()):
        for name in ("f1", "recall", "cpu_percent_mean", "telemetry_bandwidth_kbps"):
            values = [(r["sampling_rate"], r["metrics"].get(name, {})) for r in group]
            values = [(n, m) for n, m in values if m.get("mean") is not None]
            if not values:
                continue
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.errorbar(
                [n for n, _ in values],
                [m["mean"] for _, m in values],
                yerr=[m["std"] or 0 for _, m in values],
                marker="o",
                capsize=3,
            )
            ax.set(
                xlabel="Sampling N",
                ylabel=f"{name} ({values[0][1]['unit']})",
                title=f"M3 {name} - {values[0][1]['status']} / group {index + 1}",
            )
            ax.grid(alpha=0.2)
            fig.tight_layout()
            path = output / f"group_{index + 1}_{name}.png"
            fig.savefig(path, dpi=160)
            plt.close(fig)
            charts.append(str(path))
        points = []
        for row in group:
            quality, cost = (
                row["metrics"].get("f1", {}),
                row["metrics"].get("telemetry_bandwidth_kbps", {}),
            )
            if (
                quality.get("mean") is not None
                and cost.get("mean") is not None
                and cost.get("status") == "measured"
            ):
                points.append(
                    {"N": row["sampling_rate"], "f1": quality["mean"], "cost": cost["mean"]}
                )
        fronts.append(
            {
                "comparison_group": key,
                "front": pareto(points),
                "reason": None if points else "No comparable measured quality and live bandwidth",
            }
        )
        if points:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.scatter(
                [p["cost"] for p in points], [p["f1"] for p in points], label="Configurations"
            )
            efficient = sorted(pareto(points), key=lambda p: p["cost"])
            ax.plot(
                [p["cost"] for p in efficient],
                [p["f1"] for p in efficient],
                color="#21618C",
                linestyle="--",
                label="Pareto-efficient",
            )
            for point in points:
                ax.annotate(
                    f"N={point['N']}",
                    (point["cost"], point["f1"]),
                    xytext=(4, 4),
                    textcoords="offset points",
                )
            ax.set(
                xlabel="Measured received sFlow payload (kbit/s)",
                ylabel="F1",
                title=f"Accuracy versus measured overhead - group {index + 1}",
            )
            ax.legend()
            fig.tight_layout()
            path = output / f"group_{index + 1}_pareto.png"
            fig.savefig(path, dpi=160)
            plt.close(fig)
            charts.append(str(path))
    atomic_json(output / "pareto_fronts.json", {"groups": fronts})
    return {
        "groups": len(by_group),
        "configurations": len(rows),
        "charts": charts,
        "output": str(output),
        "excluded_fixture_runs": sum(r["source"] == "fixture" for r in runs),
    }
