"""Re-score the 54 live trials with the corrected naive-Bayes vote (second-level review, item 2).

Reads research/results/derived_trial_evidence.zip in place (nothing is extracted) and writes

  research/results/naive_bayes_reanalysis.json        checks, per-trial and per-cell results
  research/results/naive_bayes_reanalysis_cells.csv   per-cell summaries
  research/N1_Baseline_Reanalysis.md                  the same as a short report

Each check stops the script if it fails:
  1. Replaying every trial with River's vote ("river") reproduces the quality metrics of its
     live run summary to 1e-12, the gate analyse_research.py applies.
  2. aggregate_trials(), paired_deltas() and the quality-cost front over the archived run
     summaries reproduce the committed aggregated_metrics.json, paired_deltas.json and
     pareto_recommendations.json.
Then every trial is re-scored with the log-space vote (m3.naive_bayes), the only change, on the
same recorded features and label timing, and summarised with the same functions.

Diagnostics: final tree size, the root's best split merits and Hoeffding bound for N = 1,
empty-window shares and false-positive rates on empty and non-empty benign windows as run, and
the archived one-second sensitivity (River's vote). Channel bandwidth does not depend on the
learner and is carried over; detection delay, recovery, CPU and latency were measured live with
the original learner and are not re-scored.
"""

import argparse
import copy
import csv
import hashlib
import heapq
import json
import math
import platform
import zipfile
from collections import defaultdict
from pathlib import Path

import river
from river import drift, tree

from m3.research_metrics import (
    _label,
    _warmup,
    aggregate_trials,
    evaluate_ablations,
    paired_deltas,
    select_pareto,
    student_summary,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "research" / "results"
QUALITY = (
    "f1",
    "precision",
    "recall",
    "false_positive_rate",
    "roc_auc",
    "attack_f1",
    "attack_precision",
    "attack_recall",
    "benign_f1",
    "benign_precision",
    "benign_recall",
    "unseen_attack_recall",
)
CARRIED = ("sflow_bandwidth_kbit_s", "openflow_bandwidth_kbit_s")
REPORTED = ("f1", "false_positive_rate", "recall", "precision", "unseen_attack_recall")
SCENARIOS, RATES = ("baseline", "drift", "unseen"), (1, 2, 5, 10, 20, 50)
GATE = 1e-12


def value(metric):
    return None if metric is None else metric.get("value")


def mean_or_none(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def load(archive):
    with zipfile.ZipFile(archive) as z:
        runs = sorted({name.split("/")[0] for name in z.namelist()})
        return [
            {
                "summary": json.loads(z.read(f"{run}/run_summary.json")),
                "rows": [
                    json.loads(line)
                    for line in z.read(f"{run}/features.jsonl").decode().splitlines()
                ],
                "sensitivity": json.loads(z.read(f"{run}/sensitivity.json")),
            }
            for run in runs
        ]


def replay(trial, naive_bayes):
    c = trial["summary"]["config"]
    return evaluate_ablations(
        trial["rows"],
        seed=c["seed"],
        grace_period=c["grace_period"],
        drift_delta=c["drift_delta"],
        threshold=c["threshold"],
        naive_bayes=naive_bayes,
        unseen_enabled=trial["summary"]["scenario"] == "unseen",
    )


def root_split_state(trial):
    """Final root of the live learner (River's vote; splits do not depend on the vote)."""
    c = trial["summary"]["config"]
    model = tree.HoeffdingAdaptiveTreeClassifier(
        grace_period=c["grace_period"],
        seed=c["seed"],
        drift_detector=drift.ADWIN(delta=c["drift_delta"]),
        nominal_attributes=["Proto"],
        max_size=100,
    )
    pending = []
    for index, row in enumerate(trial["rows"]):
        label = _label(row)
        if label is None:
            continue
        while pending and pending[0][0] <= float(row["observed_time"]):
            _, _, features, old = heapq.heappop(pending)
            model.learn_one(features, old)
        heapq.heappush(pending, (float(row["label_available_time"]), index, row["features"], label))
    state = {"tree_nodes": model.n_nodes}
    if model.n_nodes == 1:
        criterion = model._new_split_criterion()
        root = model._root
        merits = sorted(
            (
                (s.merit, s.feature)
                for s in root.best_split_suggestions(criterion, model)
                if s.feature is not None
            ),
            reverse=True,
        )
        spread = criterion.range_of_merit(root.stats)
        state.update(
            {
                "labelled_windows_learned": root.total_weight,
                "best_split": {"feature": merits[0][1], "merit": merits[0][0]},
                "second_split": {"feature": merits[1][1], "merit": merits[1][0]},
                "hoeffding_bound": math.sqrt(
                    spread**2 * math.log(1 / model.delta) / (2 * root.total_weight)
                ),
                "tie_threshold": model.tau,
                "windows_needed_for_tie_split": math.ceil(
                    spread**2 * math.log(1 / model.delta) / (2 * model.tau**2)
                ),
            }
        )
    return state


def empty_windows(rows):
    scored = [r for r in rows if _label(r) is not None and not _warmup(r)]
    benign = [r for r in scored if _label(r) == 0]
    attack = [r for r in scored if _label(r) == 1]
    empty = lambda r: bool(r["features"]["empty_window"])
    alarm_rate = lambda rs: sum(int(r["y_pred"]) == 1 for r in rs) / len(rs) if rs else None
    return {
        "benign_empty_share": sum(map(empty, benign)) / len(benign),
        "attack_empty_share": sum(map(empty, attack)) / len(attack),
        "fpr_empty_benign": alarm_rate([r for r in benign if empty(r)]),
        "fpr_nonempty_benign": alarm_rate([r for r in benign if not empty(r)]),
    }


def corrected_summary(summary, metrics):
    run = copy.deepcopy(summary)
    run["metrics"] = {
        **{k: metrics[k] for k in QUALITY if k in metrics},
        **{k: summary["metrics"][k] for k in CARRIED if k in summary["metrics"]},
    }
    return run


def cells(aggregate, variant):
    out = []
    for group in aggregate["groups"]:
        for metric, s in group["metrics"].items():
            out.append(
                {
                    "variant": variant,
                    "scenario": group["scenario"],
                    "sampling_rate": group["sampling_rate"],
                    "metric": metric,
                    "n": s["n"],
                    "mean": s["mean"],
                    "sample_sd": s["sample_sd"],
                    "ci95": s["ci95"],
                }
            )
    return out


def paired(rows, scenarios, variant):
    out = []
    for item in rows:
        if "sampling_rate" not in item:
            continue
        for metric in REPORTED:
            s = item["metrics"].get(metric, {})
            out.append(
                {
                    "variant": variant,
                    "scenario": scenarios[item["comparison_group"]],
                    "sampling_rate": item["sampling_rate"],
                    "metric": metric,
                    "n": s.get("n"),
                    "mean": s.get("mean"),
                    "sample_sd": s.get("sample_sd"),
                    "ci95": s.get("ci95"),
                }
            )
    return out


def pareto(aggregate):
    """Equal-weight quality/cost front per scenario, built as in analyse_research.py."""
    fronts = {}
    for signature in sorted({g["comparison_group"] for g in aggregate["groups"]}):
        points = []
        for group in aggregate["groups"]:
            if group["comparison_group"] != signature:
                continue
            metric = group["metrics"]

            def cost(name, metric=metric):
                item = metric.get(name, {})
                return {
                    "value": item.get("mean"),
                    "unit": item.get("unit"),
                    "status": "measured" if item.get("n") == 3 else "unavailable",
                }

            points.append(
                {
                    "sampling_rate": group["sampling_rate"],
                    "f1": metric.get("f1", {}).get("mean")
                    if group["complete_three_trials"]
                    else None,
                    "sflow_bandwidth_kbit_s": cost("sflow_bandwidth_kbit_s"),
                    "openflow_bandwidth_kbit_s": cost("openflow_bandwidth_kbit_s"),
                }
            )
        fronts[signature] = select_pareto(points)
    return fronts


def check_pareto(fronts):
    worst = 0.0
    for item in json.loads((RESULTS / "pareto_recommendations.json").read_text()):
        mine = fronts[item["comparison_group"]]
        if (
            sorted(p["sampling_rate"] for p in mine["front"])
            != sorted(p["sampling_rate"] for p in item["front"])
            or mine["recommendation"]["sampling_rate"] != item["recommendation"]["sampling_rate"]
        ):
            raise ValueError(
                "Archived summaries do not reproduce the committed Pareto recommendation"
            )
        worst = max(
            worst,
            abs(
                mine["recommendation"]["ideal_distance"] - item["recommendation"]["ideal_distance"]
            ),
        )
    if worst > GATE:
        raise ValueError(f"Pareto ideal distances differ from the committed file ({worst})")
    return worst


def check_against_committed(aggregate, deltas):
    committed = json.loads((RESULTS / "aggregated_metrics.json").read_text())
    committed_deltas = json.loads((RESULTS / "paired_deltas.json").read_text())
    worst = 0.0
    index = {(g["comparison_group"], g["sampling_rate"]): g for g in aggregate["groups"]}
    for g in committed["groups"]:
        mine = index[(g["comparison_group"], g["sampling_rate"])]
        for metric in (*QUALITY, *CARRIED):
            a, b = (
                g["metrics"].get(metric, {}).get("mean"),
                mine["metrics"].get(metric, {}).get("mean"),
            )
            if (a is None) != (b is None):
                raise ValueError(f"Aggregate availability differs: {metric}")
            if a is not None:
                worst = max(worst, abs(a - b))
    dindex = {(d["comparison_group"], d.get("sampling_rate")): d for d in deltas}
    for d in committed_deltas:
        mine = dindex[(d["comparison_group"], d.get("sampling_rate"))]
        for metric in REPORTED:
            a, b = (
                d["metrics"].get(metric, {}).get("mean"),
                mine["metrics"].get(metric, {}).get("mean"),
            )
            if (a is None) != (b is None):
                raise ValueError(f"Paired-delta availability differs: {metric}")
            if a is not None:
                worst = max(worst, abs(a - b))
    if worst > GATE:
        raise ValueError(f"Archived summaries do not reproduce the committed aggregates ({worst})")
    return worst


def lookup(rows, variant, scenario, rate, metric, key="mean"):
    for row in rows:
        if (row["variant"], row["scenario"], row["sampling_rate"], row["metric"]) == (
            variant,
            scenario,
            rate,
            metric,
        ):
            return row[key]
    return None


def fmt(x, digits=3):
    return "–" if x is None else f"{x:.{digits}f}"


def report(result):
    c, p, t = result["cells"], result["paired_vs_n1"], result["trials"]
    n1 = [x["root_split"] for x in t if x["sampling_rate"] == 1]
    leaf = [x for x in n1 if "best_split" in x]
    rng = lambda key, sub=None: (
        min(x[key][sub] if sub else x[key] for x in leaf),
        max(x[key][sub] if sub else x[key] for x in leaf),
    )
    lines = [
        "# M3: re-analysis of the unsampled (N = 1) baseline",
        "",
        (f"Generated by `scripts/reanalyse_naive_bayes.py` from `research/results/derived_trial_evidence.zip` "
        f"(SHA-256 `{result['provenance']['archive_sha256'][:16]}…`) with River {result['provenance']['river']}. "
        "Every number below is recomputed from the recorded features of the 54 accepted live trials. "
        "The live study, its raw evidence and `M3_Research_Report.md` are unchanged; this note supersedes "
        "that report's interpretation of the non-monotonic sampling curve."),
        "",
        "## Checks (all passed)",
        "",
        (f"- Replaying each trial with River's vote reproduces its live quality metrics: largest difference "
         f"{result['checks']['max_replay_difference']:.1g} over {len(QUALITY)} metrics and 54 trials."),
        (f"- The archived run summaries reproduce the committed `aggregated_metrics.json`, `paired_deltas.json` and "
         f"`pareto_recommendations.json` (largest difference {result['checks']['max_committed_difference']:.1g})."),
        "",
        "## What went wrong at N = 1",
        "",
    ]
    split = [x for x in t if x["sampling_rate"] == 1 and "best_split" not in x["root_split"]]
    if leaf:
        lines.append(
            f"- **The tree did not split.** In {len(leaf)} of {len(n1)} N = 1 trials the Hoeffding Adaptive Tree ended "
            f"as a single leaf. Its two best splits were {leaf[0]['best_split']['feature']} and "
            f"{leaf[0]['second_split']['feature']} (merits {rng('best_split', 'merit')[0]:.3f}–"
            f"{rng('best_split', 'merit')[1]:.3f} and {rng('second_split', 'merit')[0]:.3f}–"
            f"{rng('second_split', 'merit')[1]:.3f}): two redundant features that separate the classes almost "
            f"perfectly. Their difference stayed below the Hoeffding bound ({rng('hoeffding_bound')[0]:.3f}–"
            f"{rng('hoeffding_bound')[1]:.3f}), which itself stayed above the tie threshold "
            f"τ = {leaf[0]['tie_threshold']}, so no split was allowed. A tie split needs "
            f"{leaf[0]['windows_needed_for_tie_split']:,} labelled windows; each trial provided "
            f"{rng('labelled_windows_learned')[0]:,.0f}–{rng('labelled_windows_learned')[1]:,.0f}."
        )
    for x in split:
        lines.append(
            f"- **Control: the one N = 1 trial whose tree split** ({x['scenario']}, trial {x['trial_id']}, "
            f"{x['root_split']['tree_nodes']} nodes) reached F1 {x['as_run']['f1']:.3f} at FPR "
            f"{x['as_run']['false_positive_rate']:.3f} as run, and {x['corrected']['hat_adwin']['f1']:.3f} at "
            f"{x['corrected']['hat_adwin']['false_positive_rate']:.3f} with the corrected vote."
        )
    lines += [
        ("- **The leaf's naive-Bayes vote was wrong.** River 0.23 adds `log(p) if p > 0 else 0.0` per feature, so a "
        "density that underflows to 0 counts as certainty. A benign window with ~1,200-byte packets has zero density "
        "under the flood class (~53-byte packets), so the flood class is never penalised and wins with probability "
        "~1. Hence recall ≈ 1 with most benign windows flagged."),
        ("- **Not sFlow batching.** N = 1 has almost no empty windows (table below), and the archived one-second "
        "re-scoring, made during the study with the original vote, keeps the high false-positive rate at N = 1. "
        "At one second the N = 2 advantage also disappears:"),
        "",
        "| Scenario | N = 1 FPR, 0.1 s | N = 1 FPR, 1 s | N = 2 F1, 0.1 s | N = 2 F1, 1 s |",
        "|---|---|---|---|---|",
    ]
    for scenario in SCENARIOS:
        lines.append(
            f"| {scenario} | {fmt(lookup(c, 'as_run', scenario, 1, 'false_positive_rate'))} | "
            f"{fmt(lookup(c, 'one_second_as_run', scenario, 1, 'false_positive_rate'))} | "
            f"{fmt(lookup(c, 'as_run', scenario, 2, 'f1'))} | "
            f"{fmt(lookup(c, 'one_second_as_run', scenario, 2, 'f1'))} |"
        )
    lines += [
        "",
        "Empty windows as run (scored windows; FPR on benign windows):",
        "",
        "| Scenario | N | Benign empty | Attack empty | FPR, empty | FPR, non-empty |",
        "|---|---|---|---|---|---|",
    ]
    diag = defaultdict(list)
    for x in t:
        diag[(x["scenario"], x["sampling_rate"])].append(x["empty_windows"])
    for scenario in SCENARIOS:
        for rate in RATES:
            d = diag[(scenario, rate)]
            avg = lambda k, d=d: mean_or_none([v[k] for v in d])
            lines.append(
                f"| {scenario} | {rate} | {fmt(avg('benign_empty_share'))} | {fmt(avg('attack_empty_share'))} "
                f"| {fmt(avg('fpr_empty_benign'))} | {fmt(avg('fpr_nonempty_benign'))} |"
            )
    lines += [
        "",
        "## Corrected results (log-space vote; nothing else changed)",
        "",
        "Mean over three trials. Bandwidth is the combined IP-layer sFlow and OpenFlow channel cost, unchanged.",
        "",
        "| Scenario | N | As run F1 / FPR | Corrected F1 / FPR | Corrected recall | Bandwidth (kbit/s) |",
        "|---|---|---|---|---|---|",
    ]
    for scenario in SCENARIOS:
        for rate in RATES:
            bw = sum(lookup(c, "as_run", scenario, rate, k) for k in CARRIED)
            lines.append(
                f"| {scenario} | {rate} | {fmt(lookup(c, 'as_run', scenario, rate, 'f1'))} / "
                f"{fmt(lookup(c, 'as_run', scenario, rate, 'false_positive_rate'))} | "
                f"{fmt(lookup(c, 'corrected', scenario, rate, 'f1'))} / "
                f"{fmt(lookup(c, 'corrected', scenario, rate, 'false_positive_rate'))} | "
                f"{fmt(lookup(c, 'corrected', scenario, rate, 'recall'))} | {bw:.1f} |"
            )
    lines += [
        "",
        ("From N = 5 a large share of windows is empty (table above) and empty windows are still flagged, so the "
        "corrected false-positive rate stays high: sparse sampling against 0.1-s windows, not the vote, now limits "
        "quality."),
    ]
    lines += [
        "",
        "Held-out SYN recall in the unseen scenario (SYN flood absent from warm-up), as run → corrected: "
        + "; ".join(
            f"N = {rate}: {fmt(lookup(c, 'as_run', 'unseen', rate, 'unseen_attack_recall'))} → "
            f"{fmt(lookup(c, 'corrected', 'unseen', rate, 'unseen_attack_recall'))}"
            for rate in RATES
        )
        + ".",
        "",
        "## Paired differences against N = 1 (corrected)",
        "",
        "N minus N = 1 within the same trial; mean and two-sided Student-t 95% interval (n = 3).",
        "",
        "| Scenario | N | ΔF1 | ΔFPR |",
        "|---|---|---|---|",
    ]
    for scenario in SCENARIOS:
        for rate in RATES[1:]:

            def cell(metric, scenario=scenario, rate=rate):
                mean = lookup(p, "corrected", scenario, rate, metric)
                ci = lookup(p, "corrected", scenario, rate, metric, "ci95")
                return f"{fmt(mean)} [{fmt(ci[0])}, {fmt(ci[1])}]" if ci else fmt(mean)

            lines.append(f"| {scenario} | {rate} | {cell('f1')} | {cell('false_positive_rate')} |")
    lines += [
        "",
        "## Quality–cost front (equal weights, descriptive)",
        "",
        "Built as for `pareto_recommendations.json`: mean F1 against combined channel bandwidth.",
        "",
        "| Scenario | As run: front → recommended N | Corrected: front → recommended N (F1, kbit/s) |",
        "|---|---|---|",
    ]
    fr = {(r["variant"], r["scenario"]): r for r in result["pareto"]}
    for scenario in SCENARIOS:
        a, b = fr[("as_run", scenario)], fr[("corrected", scenario)]
        lines.append(
            f"| {scenario} | {a['front']} → {a['recommended_sampling_rate']} | {b['front']} → "
            f"{b['recommended_sampling_rate']} ({b['recommended_f1']:.3f}, "
            f"{b['recommended_combined_bandwidth_kbit_s']:.1f}) |"
        )
    lines += [
        "",
        "## Scope",
        "",
        ("- Offline re-scoring of the exact recorded 0.1-s feature windows, in their recorded order and with their "
         "recorded label availability. The learner, its seed and every setting except the vote are unchanged."),
        ("- Channel bandwidth is learner-independent and carried over. Detection delay, post-drift recovery, CPU and "
         "inference latency are live measurements of the original learner and were not re-scored."),
        ("- The one-second figures are the archived post-hoc sensitivity (original vote, rebuilt from raw datagrams "
         "during the study); the raw datagrams are not in the repository, so they were not re-scored here."),
        "- Three repeats of fixed traffic describe repeatability, not population effects.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", default=str(RESULTS / "derived_trial_evidence.zip"))
    args = parser.parse_args()
    archive = Path(args.archive)
    trials = load(archive)
    if len(trials) != 54:
        raise ValueError(f"Expected 54 accepted trials, found {len(trials)}")

    worst, records, corrected = 0.0, [], []
    for trial in trials:
        s = trial["summary"]
        legacy, fixed = replay(trial, "river"), replay(trial, "log_space")
        for key in QUALITY:
            a, b = value(s["metrics"].get(key)), value(legacy["hat_adwin"]["metrics"].get(key))
            if (a is None) != (b is None) or (a is not None and abs(a - b) > GATE):
                raise ValueError(f"{s['run_id']}: replay does not reproduce the live {key}")
            if a is not None:
                worst = max(worst, abs(a - b))
        corrected.append(corrected_summary(s, fixed["hat_adwin"]["metrics"]))
        records.append(
            {
                "run_id": s["run_id"],
                "scenario": s["scenario"],
                "sampling_rate": s["sampling_rate"],
                "trial_id": s["config"].get("trial_id"),
                "seed": s["config"]["seed"],
                "as_run": {k: value(s["metrics"].get(k)) for k in REPORTED},
                "corrected": {
                    model: {k: value(fixed[model]["metrics"].get(k)) for k in REPORTED}
                    for model in ("hat_adwin", "hoeffding_tree", "majority_warmup")
                },
                "tree_nodes": {
                    "as_run": legacy["hat_adwin"]["tree_nodes"],
                    "corrected": fixed["hat_adwin"]["tree_nodes"],
                },
                "root_split": root_split_state(trial) if s["sampling_rate"] == 1 else None,
                "empty_windows": empty_windows(trial["rows"]),
                "one_second_as_run": {
                    k: value(trial["sensitivity"]["models"]["hat_adwin"]["metrics"].get(k))
                    for k in REPORTED
                },
            }
        )

    summaries = [t["summary"] for t in trials]
    as_run_agg, as_run_deltas = aggregate_trials(summaries), paired_deltas(summaries)
    committed_worst = check_against_committed(as_run_agg, as_run_deltas)
    corrected_agg, corrected_deltas = aggregate_trials(corrected), paired_deltas(corrected)
    scenarios = {g["comparison_group"]: g["scenario"] for g in as_run_agg["groups"]}
    fronts = {"as_run": pareto(as_run_agg), "corrected": pareto(corrected_agg)}
    committed_worst = max(committed_worst, check_pareto(fronts["as_run"]))
    pareto_rows = [
        {
            "variant": variant,
            "scenario": scenarios[signature],
            "front": sorted(p["sampling_rate"] for p in front["front"]),
            "recommended_sampling_rate": front["recommendation"]["sampling_rate"],
            "recommended_f1": front["recommendation"]["f1"],
            "recommended_combined_bandwidth_kbit_s": front["recommendation"][
                "combined_bandwidth_kbit_s"
            ],
            "criterion": front["criterion"],
            "quality_weight": front["quality_weight"],
        }
        for variant, by_signature in fronts.items()
        for signature, front in by_signature.items()
    ]

    one_second = []
    by_cell = defaultdict(list)
    for r in records:
        by_cell[(r["scenario"], r["sampling_rate"])].append(r["one_second_as_run"])
    for (scenario, rate), values in sorted(by_cell.items()):
        for metric in REPORTED:
            st = student_summary([v[metric] for v in values])
            one_second.append(
                {
                    "variant": "one_second_as_run",
                    "scenario": scenario,
                    "sampling_rate": rate,
                    "metric": metric,
                    "n": st["n"],
                    "mean": st["mean"],
                    "sample_sd": st["sample_sd"],
                    "ci95": st["ci95"],
                }
            )

    result = {
        "provenance": {
            "archive": "research/results/derived_trial_evidence.zip",
            "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "river": river.__version__,
            "python": platform.python_version(),
            "change": "naive_bayes='log_space' (m3.naive_bayes); every other setting as recorded",
        },
        "checks": {
            "trials": len(trials),
            "max_replay_difference": worst,
            "max_committed_difference": committed_worst,
            "gate": GATE,
        },
        "trials": records,
        "cells": cells(as_run_agg, "as_run") + cells(corrected_agg, "corrected") + one_second,
        "paired_vs_n1": paired(as_run_deltas, scenarios, "as_run")
        + paired(corrected_deltas, scenarios, "corrected"),
        "pareto": pareto_rows,
    }
    (RESULTS / "naive_bayes_reanalysis.json").write_text(
        json.dumps(result, indent=1) + "\n", encoding="utf-8"
    )
    with (RESULTS / "naive_bayes_reanalysis_cells.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            [
                "variant",
                "scenario",
                "sampling_rate",
                "metric",
                "n",
                "mean",
                "sample_sd",
                "ci95_lower",
                "ci95_upper",
            ]
        )
        for row in sorted(
            result["cells"],
            key=lambda r: (r["variant"], r["scenario"], r["sampling_rate"], r["metric"]),
        ):
            ci = row["ci95"] or [None, None]
            writer.writerow(
                [
                    row["variant"],
                    row["scenario"],
                    row["sampling_rate"],
                    row["metric"],
                    row["n"],
                    row["mean"],
                    row["sample_sd"],
                    ci[0],
                    ci[1],
                ]
            )
    (ROOT / "research" / "N1_Baseline_Reanalysis.md").write_text(
        report(result), encoding="utf-8", newline="\n"
    )
    print(json.dumps(result["checks"]))


if __name__ == "__main__":
    main()
