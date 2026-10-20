"""Build the paper and portable derived evidence only after all study gates pass.

No raw packet payloads are placed in the publication archive. Raw local evidence
remains linked by checksum; the official release must be downloaded separately.
"""

import argparse
import hashlib
import html
import json
import re
import shutil
import zipfile
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ("baseline", "drift", "unseen")
RATES = (1, 2, 5, 10, 20, 50)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def local_path(path):
    value = str(path)
    if re.match(r"^/mnt/[a-z]/", value) and ROOT.drive:
        value = value[5].upper() + ":/" + value[7:]
    return Path(value)


def load_complete(analysis, runs_root):
    readiness = json.loads((Path(analysis) / "research_readiness.json").read_text())
    if readiness.get("ready") is not True or readiness.get("accepted_trials") != 54:
        raise ValueError("Completed research report requires all 54 trials and analysis gates")
    runs = []
    for path in Path(runs_root).glob("*/run_summary.json"):
        run = json.loads(path.read_text())
        if (run.get("source") == "official_realtime_verified"
                and run.get("validation", {}).get("accepted") is True
                and run.get("status") == "completed"
                and run.get("research", {}).get("study_role") != "validation_pilot"):
            for key, expected in run["raw_hashes"].items():
                if digest(local_path(run["artifacts"][key])) != expected:
                    raise ValueError(f"Accepted raw evidence changed: {run['run_id']} {key}")
            runs.append((path.parent, run))
    if len(runs) != 54:
        raise ValueError("Readiness and actual accepted run count disagree")
    return readiness, runs


def number(value, digits=3):
    return "NA" if value is None else f"{value:.{digits}f}"


def metric(group, key):
    return group["metrics"].get(key, {})


def mean_sd(group, key):
    item = metric(group, key)
    return f"{number(item.get('mean'))} +/- {number(item.get('sample_sd'))}"


def plot_results(groups, destination):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"baseline": "#17446B", "drift": "#AD5823", "unseen": "#287755"}
    destination.mkdir(parents=True, exist_ok=True)
    for key, label, filename, logarithmic in (
        ("f1", "Attack F1", "f1_vs_sampling.png", False),
        ("false_positive_rate", "False-positive rate", "fpr_vs_sampling.png", False),
        ("sflow_bandwidth_kbit_s", "sFlow IP-layer bandwidth (kbit/s)", "bandwidth_vs_sampling.png", True),
        ("cpu_percent_mean", "Detector CPU (% of one logical CPU)", "cpu_vs_sampling.png", False),
    ):
        figure, axis = plt.subplots(figsize=(7, 4.1))
        for scenario in SCENARIOS:
            selected = [groups[(scenario, rate)] for rate in RATES]
            values = [metric(group, key).get("mean") for group in selected]
            errors = [metric(group, key).get("sample_sd") for group in selected]
            axis.errorbar(RATES, values, yerr=errors, marker="o", capsize=3,
                          label=scenario.title(), color=colors[scenario], linewidth=1.5)
        axis.set(xlabel="Switch sampling denominator N", ylabel=label)
        axis.set_xscale("log")
        axis.set_xticks(RATES, labels=[str(n) for n in RATES])
        if logarithmic:
            axis.set_yscale("log")
        axis.grid(alpha=0.22)
        axis.legend(frameon=False)
        figure.tight_layout()
        figure.savefig(destination / filename, dpi=200)
        plt.close(figure)


def write_publication(analysis, runs, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for filename in ("aggregated_metrics.json", "aggregated_metrics.csv", "paired_deltas.json",
                     "quality_ablations.json", "pareto_recommendations.json", "research_readiness.json"):
        shutil.copyfile(Path(analysis) / filename, destination / filename)
    matrix = ROOT / "output/research/equalrate_v1/matrix.json"
    if matrix.is_file():
        shutil.copyfile(matrix, destination / "experiment_matrix.json")
    failures = []
    for folder in (ROOT / "output/research/equalrate_v1", ROOT / "output/research/causal_validation"):
        for path in sorted(folder.glob("*/execution.json")):
            report = json.loads(path.read_text())
            if report.get("status") == "failed":
                failures.append({"evidence_directory": path.parent.name, "report": report})
    (destination / "failed_attempts.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")
    for name in ("official_SYNFlood_packet_audit.json", "official_ICMPFlood_packet_audit.json",
                 "official_UDPFlood_packet_audit_corrected.json"):
        shutil.copyfile(ROOT / "output/sdn" / name, destination / name)
    # Freeze the exact conservative label snapshots used by this study. Regenerating
    # them with later zero-port handling can legitimately produce a different input.
    prepared = ROOT / "data/prepared"
    with zipfile.ZipFile(destination / "frozen_preparation_annotations.zip", "w",
                         compression=zipfile.ZIP_DEFLATED) as archive:
        for family in ("SYNFlood", "ICMPFlood", "UDPFlood"):
            name = f"BS2_{family}_flow_labels.csv"
            archive.write(prepared / name, name)
        selected = prepared / "research_20261019_equalrate_v1"
        expected = {}
        for scenario in SCENARIOS:
            for source in sorted((selected / scenario).glob("block_*_mapping.csv")):
                archive.write(source, f"expected_mappings/{scenario}/{source.name}")
                expected[f"{scenario}/{source.name}"] = digest(source)
            for source in sorted((selected / scenario).glob("block_*.pcap")):
                expected[f"{scenario}/{source.name}"] = digest(source)
        archive.writestr("expected_prepared_sha256.json", json.dumps(expected, indent=2))
    index = []
    archive_path = destination / "derived_trial_evidence.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for directory, run in runs:
            names = ["run_summary.json", "features.jsonl", "predictions.csv", "resources.csv",
                     "drift.csv", "sensitivity.json"]
            for name in names:
                archive.write(directory / name, f"{run['run_id']}/{name}")
            events = local_path(run["artifacts"]["packet_events"])
            archive.write(events, f"{run['run_id']}/packet_events.csv")
            index.append({"run_id": run["run_id"], "scenario": run["scenario"],
                          "sampling_rate": run["sampling_rate"], "trial_id": run["config"]["trial_id"],
                          "raw_hashes": run["raw_hashes"], "config": run["config"]})
    (destination / "trial_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    (destination / "DATA_ATTRIBUTION.md").write_text(
        "# Data attribution\n\nDerived from the official 5G-NIDD release by Samarakoon et al.\n"
        "Release DOI: https://doi.org/10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361\n"
        "Upstream licence: Creative Commons Attribution 4.0.\n"
        "Licence terms: https://creativecommons.org/licenses/by/4.0/\n"
        "Changes: exact packet selection, Ethernet MAC rewriting, constructed equal-rate timing,\n"
        "live switch sampling, window feature extraction and derived measurements.\n"
        "This archive contains derived window evidence and hashes, not original packet payloads.\n"
        "The separate frozen annotation archive contains derived flow labels, packet mappings and hashes.\n"
        "No endorsement by the dataset authors is implied.\n", encoding="utf-8")
    # Match the repository's LF checkout policy so release checksums remain valid
    # on Windows and Linux. This changes formatting, not measurement values.
    for path in destination.iterdir():
        if path.suffix.lower() in {".json", ".csv", ".md"}:
            path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")


def manuscript(groups, runs, analysis, figures):
    all_f1 = [metric(group, "f1")["mean"] for group in groups.values()]
    text = [
        "# Sampling and Adaptive Flood Detection in an SDN Emulator",
        "## A controlled, independently validated 5G-NIDD replay study",
        "Research manuscript and reproducibility report. 20 October 2026.",
        "## Abstract",
        ("Packet sampling reduces telemetry volume, but the resulting observation and export timing "
        "can change online intrusion-detection quality. We evaluate an existing Hoeffding Adaptive "
        "Tree with ADWIN using official 5G-NIDD-derived packets in an isolated Mininet/OVS/OS-Ken "
        "testbed. A fixed study contains 54 accepted live trials: three scenarios, six switch "
        "sampling denominators and three repeats. Every class replays at 100 packets/s. Full sender "
        "and receiver captures, kernel packet timestamps and prediction-before-label records "
        "independently validate the experimental evidence. Across the 18 cells, mean attack F1 "
        f"ranges from {min(all_f1):.3f} to {max(all_f1):.3f}. We report channel costs, paired differences, "
        "censored physical detection/recovery, quality ablations and a window-size sensitivity check. "
        "The contribution is an auditable measurement pipeline and a bounded empirical study, "
        "not a new learning algorithm. Constructed traffic timing, oracle supervision and fixed "
        "source captures limit deployment and generalization claims."),
        "## 1. Introduction and research questions",
        ("SDN monitoring places detection logic near control-plane observations. A useful detector "
        "must account for what telemetry it can collect and what collecting it costs. This study "
        "asks how actual switch sampling changes prequential flood-detection quality and measured "
        "control-channel cost, and how the observed trade-off changes under held-out SYN introduction "
        "and a constructed distribution shift. N=1 is an internal unsampled M3 reference. No M1/M2 "
        "implementation or cross-method superiority claim is included."),
        "## 2. Related work and contribution boundary",
        ("5G-NIDD supplies labelled traffic from a functional 5G test network [1]. ADWIN and adaptive "
        "Hoeffding trees are established stream-learning methods [2,3]. Sampling-based SDN DDoS "
        "detection and resource trade-offs already appear in Ujjan et al. [4]. HAT/ADWIN stream traffic "
        "classification in SDN [5] and incremental 5G malicious-traffic detection [6] further limit any "
        "generic novelty claim. Our candidate contribution is instead the reproducible combination of "
        "source-to-packet provenance, actual switch exports, independent original-packet truth, causal "
        "label revelation and uncertainty-aware repeated measurement. Published classifier scores on "
        "different features/splits are not comparable baselines. Detailed source and access notes are "
        "in docs/research-related-work.md. Sufficient originality for a specific venue remains a "
        "scientific judgement beyond this artifact-completeness assessment."),
        "## 3. Methods",
    ]
    methods = (ROOT / "docs/research-methods.md").read_text(encoding="utf-8")
    # Keep the detailed protocol but avoid duplicating introductory questions here.
    methods = methods[methods.index("## Fixed protocol"):]
    text.append(re.sub(r"^## ", "### ", methods, flags=re.MULTILINE))
    text += ["## 4. Results", "### 4.1 Detection quality"]
    for scenario in SCENARIOS:
        best = max(RATES, key=lambda rate: metric(groups[(scenario, rate)], "f1")["mean"])
        group = groups[(scenario, best)]
        base = groups[(scenario, 1)]
        cost = lambda item: sum(metric(item, key)["mean"] for key in (
            "sflow_bandwidth_kbit_s", "openflow_bandwidth_kbit_s"))
        reduction = 100 * (1 - cost(group) / cost(base))
        text.append(f"{scenario.title()}: the highest cell-mean attack F1 occurs at N={best} "
                    f"({metric(group, 'f1')['mean']:.3f}), with false-positive rate "
                    f"{metric(group, 'false_positive_rate')['mean']:.3f} and "
                    f"{reduction:.2f}% lower combined channel bandwidth than N=1. "
                    "This is an observed cell ranking, not an independent optimum or significance test.")
    for scenario in SCENARIOS:
        text += [f"#### {scenario.title()}",
                 "| N | Precision | Recall | F1 mean +/- SD | ROC-AUC | FPR |",
                 "|---|---|---|---|---|---|"]
        for rate in RATES:
            group = groups[(scenario, rate)]
            text.append(f"| {rate} | {number(metric(group, 'precision').get('mean'))} | "
                        f"{number(metric(group, 'recall').get('mean'))} | {mean_sd(group, 'f1')} | "
                        f"{number(metric(group, 'roc_auc').get('mean'))} | "
                        f"{number(metric(group, 'false_positive_rate').get('mean'))} |")
    text += ["#### Held-out SYN family",
             "| N | SYN recall mean +/- SD | Correct first SYN-window predictions |",
             "|---|---|---|"]
    for rate in RATES:
        first_hits = 0
        for directory, run in runs:
            if run["scenario"] != "unseen" or run["sampling_rate"] != rate:
                continue
            rows = [json.loads(line) for line in (directory / "features.jsonl").read_text().splitlines()]
            first = next(row for row in rows if row.get("attack_family") == "SYNFlood"
                         and row.get("phase") == "evaluation" and row.get("y_true") == 1)
            first_hits += first["y_pred"] == 1
        text.append(f"| {rate} | {mean_sd(groups[('unseen', rate)], 'unseen_attack_recall')} | {first_hits}/3 |")
    text.append("SYN is excluded from warm-up, but the detector subsequently learns from oracle SYN "
                "labels. Overall SYN recall therefore mixes first encounter with later adaptation. "
                "The first-window count is shown separately and is based on only three encounters.")
    text += [("Every cell contains three accepted trials. Error bars in the following figures are "
             "sample standard deviations, not confidence intervals. Exact unbounded Student-t "
             "intervals and all per-class metrics are retained in the machine-readable tables."),
             "![Attack F1 by actual switch sampling denominator](figures/f1_vs_sampling.png)",
             "![False-positive rate by sampling denominator](figures/fpr_vs_sampling.png)",
             "### 4.2 Measured cost"]
    for scenario in SCENARIOS:
        text += [f"#### {scenario.title()}",
                 "| N | sFlow IP kbit/s | OpenFlow IP kbit/s | Detector CPU % | Controller CPU % |",
                 "|---|---|---|---|---|"]
        for rate in RATES:
            group = groups[(scenario, rate)]
            keys = ("sflow_bandwidth_kbit_s", "openflow_bandwidth_kbit_s",
                    "cpu_percent_mean", "controller_cpu_percent_mean")
            text.append("| " + str(rate) + " | " + " | ".join(number(metric(group, key).get("mean"))
                                                             for key in keys) + " |")
        base, sparse = groups[(scenario, 1)], groups[(scenario, 50)]
        cost = lambda group: sum(metric(group, key)["mean"]
                                 for key in ("sflow_bandwidth_kbit_s", "openflow_bandwidth_kbit_s"))
        reduction = 100 * (1 - cost(sparse) / cost(base))
        text.append(f"At N=50 versus N=1 in {scenario}, mean combined channel cost changes by "
                    f"{-reduction:.2f}% and mean F1 changes by "
                    f"{metric(sparse, 'f1')['mean'] - metric(base, 'f1')['mean']:+.3f}. "
                    "These are descriptive controlled-study differences, not population effect estimates.")
    text += ["![Measured sFlow IP-layer bandwidth](figures/bandwidth_vs_sampling.png)",
             "![Detector CPU across the whole measurement interval](figures/cpu_vs_sampling.png)",
             "### 4.3 Physical alerts and constructed shift recovery",
             "| Scenario | N | First-episode delay (s) | Detected /3 | Original packets to alert | Recovery mean (s) | Recovered /3 |",
             "|---|---|---|---|---|---|---|"]
    for scenario in SCENARIOS:
        for rate in RATES:
            group = groups[(scenario, rate)]
            delay, recovery = metric(group, "detection_time_seconds"), metric(group, "post_drift_recovery_seconds")
            text.append(f"| {scenario} | {rate} | {number(delay.get('mean'))} | {delay.get('n', 0)}/3 | "
                        f"{number(metric(group, 'packets_to_detect').get('mean'), 1)} | "
                        f"{number(recovery.get('mean'))} | {recovery.get('n', 0)}/3 |")
    text += [("Delay and packets-to-alert summarize the first post-warm-up attack episode per trial. "
             "NA retains censored or inapplicable outcomes. Delay means condition on observed detection "
             "and must be read together with the detected count; they are not average delays with "
             "misses assigned zero. Recovery applies only to the declared drift scenario. Per-episode "
             "packet counts, misses and false alarms remain in each run's research_metrics."),
             ("The following counts are external ADWIN prediction-error alarms during evaluation "
              "in the constructed drift scenario. An alarm does not itself establish an attack or "
              "a HAT internal branch replacement; internal adaptation events were not instrumented."),
             "| N | External alarms in trials 1, 2, 3 | Mean count |",
             "|---|---|---|"]
    for rate in RATES:
        selected = sorted((run for _, run in runs
                           if run["scenario"] == "drift" and run["sampling_rate"] == rate),
                          key=lambda run: run["config"]["trial_id"])
        alarms = [run["drift_count"] for run in selected]
        text.append(f"| {rate} | {', '.join(str(value) for value in alarms)} | {mean(alarms):.2f} |")
    text.append("### 4.4 Paired uncertainty, ablations and window sensitivity")
    paired = json.loads((Path(analysis) / "paired_deltas.json").read_text())
    for result in paired:
        if result.get("sampling_rate") != 50:
            continue
        signature = json.loads(result["comparison_group"])
        value = result["metrics"]["f1"]
        interval = value.get("ci95") or [None, None]
        text.append(f"{signature['scenario'].title()} paired N=50 minus N=1 attack-F1 change: "
                    f"mean {number(value['mean'])}, 95% Student-t interval "
                    f"[{number(interval[0])}, {number(interval[1])}], n={value['n']}. "
                    "The three fixed-traffic repeats cannot establish broad statistical superiority.")
    ablations = {item["run_id"]: item["models"] for item in json.loads(
        (Path(analysis) / "quality_ablations.json").read_text())}
    text += ["| Scenario | N | HAT F1 | HT F1 | Warm-up majority F1 | One-second HAT F1 |",
             "|---|---|---|---|---|---|"]
    for scenario in SCENARIOS:
        for rate in (1, 2, 50):
            selected = [(directory, run) for directory, run in runs
                        if run["scenario"] == scenario and run["sampling_rate"] == rate]
            values = []
            for model in ("hat_adwin", "hoeffding_tree", "majority_warmup"):
                measured = [ablations[run["run_id"]][model]["metrics"]["f1"]["value"]
                            for _, run in selected]
                values.append(mean(value for value in measured if value is not None)
                              if any(value is not None for value in measured) else None)
            sensitivity = [json.loads((directory / "sensitivity.json").read_text())["models"]
                           ["hat_adwin"]["metrics"]["f1"]["value"] for directory, _ in selected]
            values.append(mean(value for value in sensitivity if value is not None)
                          if any(value is not None for value in sensitivity) else None)
            text.append(f"| {scenario} | {rate} | " + " | ".join(number(v) for v in values) + " |")
    text += [("All six N values' ablations are included in the derived archive. These are offline "
             "quality-only comparisons. The one-second study changes the observation unit, available "
             "warm-up observations and eligible pure-class support; it does not compare equivalent "
             "live runtime or isolate only a statistical aggregation effect."),
             "### 4.5 Descriptive frontier",
             ("The saved pareto_recommendations.json identifies nondominated points and the fixed "
             "equal-weight normalized ideal-point recommendation separately by scenario. All individual "
             "trials and uncertainty remain available. A selected N is an in-study operational suggestion "
             "under this cost definition, not an externally validated optimum."),
             "## 5. Discussion and threats to validity",
             ("Sampling affects more than feature volume. Sparse exports and batching can produce empty "
             "arrival windows even when original attack packets arrive. Retaining those windows is "
             "necessary to measure the deployed observation path. Independent truth makes these misses "
             "visible instead of scoring only selected packets. High recall accompanied by a high "
             "false-positive rate remains a poor operating point, and an overhead reduction alone does "
             "not establish a useful detector. The reported ablations and uncertainty should guide the "
             "interpretation rather than an isolated best run."),
             ("The study uses selected sessions from one release and one isolated shared-host testbed. "
             "Source-flow identity correlations are not removed by disjoint packet indices. Equal-rate "
             "retiming deliberately removes natural volume and burst structure. Drift changes family "
             "and cadence together. Oracle labels enable supervised adaptation that production cannot "
             "assume. N=1 is not full PacketIn mirroring, and M1/M2 are outside scope. CPU and latency "
             "reflect this instrumented software testbed, not physical switch or 5G capacity. Human "
             "review must assess whether the bounded findings provide sufficient novelty for a venue."),
             ("The primary sampling curve is non-monotonic: observing every eligible header does "
             "not yield the strongest classifier here. Export batching, feature timing and the "
             "online learner's state are plausible explanations, but this design does not isolate "
             "their causal effects. The nonadaptive-tree ablation and one-second sensitivity show "
             "that conclusions depend on the learner and observation schedule. No general HAT "
             "adaptation advantage follows from the primary F1 ranking. Even the strongest cells "
             "retain material false positives, so the study does not establish production readiness."),
             "## 6. Reproducibility and completion evidence",
             ("The repository includes the frozen protocol, preparation code, provenance manifest, "
             "resumable trial runner, analysis, tests and this report generator. The derived evidence "
             "archive contains per-window features/predictions, packet event hashes, resource/drift logs, "
             "trial summaries and sensitivity outputs for all 54 accepted trials. It excludes original "
             "packet payloads. Raw local captures and exports remain linked by SHA256. Technical failures "
             "and retry explanations remain in the matrix/evidence index and are not silently replaced. "
             "A clean checkout requires the official dataset download before rerunning the live study."),
             "## 7. Conclusion",
             ("This controlled study produces independently validated evidence for the accuracy-cost "
             "trade-off of sampled adaptive flood detection. Its results support conclusions limited "
             "to the reported constructed scenarios, instrumentation and supervision policy. The "
             "software and evidence package support research review; they do not establish a new "
             "learning algorithm, universal sampling optimum, physical 5G deployment performance, "
             "or guaranteed publication acceptance."),
             "## References",
             ("[1] S. Samarakoon et al. 5G-NIDD: A Comprehensive Network Intrusion Detection Dataset "
             "Generated over 5G Wireless Network. arXiv:2212.01298, 2022. https://arxiv.org/abs/2212.01298"),
             ("[2] A. Bifet and R. Gavalda. Learning from Time-Changing Data with Adaptive Windowing. "
             "SDM 2007, 443-448. https://doi.org/10.1137/1.9781611972771.42"),
             ("[3] A. Bifet and R. Gavalda. Adaptive Learning from Evolving Data Streams. IDA 2009. "
             "https://doi.org/10.1007/978-3-642-03915-7_22"),
             ("[4] R. M. A. Ujjan et al. Towards sFlow and adaptive polling sampling for deep learning "
             "based DDoS detection in SDN. FGCS 111, 763-779, 2020. https://doi.org/10.1016/j.future.2019.10.015"),
             ("[5] A. M. Eldhai et al. Improved Feature Selection and Stream Traffic Classification "
             "Based on Machine Learning in Software-Defined Networks. IEEE Access 12, 34141-34159, 2024. "
             "https://doi.org/10.1109/ACCESS.2024.3370435"),
             ("[6] Z. Wang, K. W. Fok and V. L. L. Thing. Exploring Emerging Trends in 5G Malicious "
             "Traffic Analysis and Incremental Learning Intrusion Detection Strategies. "
             "arXiv:2402.14353, 2024. https://arxiv.org/abs/2402.14353"),
             "[7] P. Phaal and M. Lavine. sFlow Version 5. 2004. https://sflow.org/sflow_version_5.txt"]
    fronts = json.loads((Path(analysis) / "pareto_recommendations.json").read_text())
    recommendations = ["| Scenario | Suggested N | Mean F1 | Combined IP kbit/s |",
                       "|---|---|---|---|"]
    for front in fronts:
        candidate = front.get("recommendation")
        if candidate:
            scenario = json.loads(front["comparison_group"])["scenario"]
            recommendations.append(f"| {scenario} | {candidate['sampling_rate']} | "
                                   f"{number(candidate['f1'])} | "
                                   f"{number(candidate['combined_bandwidth_kbit_s'])} |")
    position = text.index("## 5. Discussion and threats to validity")
    text[position:position] = recommendations
    return re.sub(r"(?m)^(\|[^\n]*\|)\n\n(?=\|)", r"\1\n", "\n\n".join(text)) + "\n"


def render_pdf(markdown, root, output):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import (
        Image,
        KeepTogether,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Paper", fontName="Times-Roman", fontSize=10.5,
                              leading=14.3, spaceAfter=7, allowWidows=0, allowOrphans=0))
    styles.add(ParagraphStyle(name="PaperCell", fontName="Helvetica", fontSize=8.1, leading=10.4))
    styles.add(ParagraphStyle(name="PaperTitle", fontName="Times-Bold", fontSize=21, leading=25,
                              spaceAfter=12, textColor=colors.HexColor("#17324D")))
    for key in ("Heading1", "Heading2", "Heading3", "Heading4"):
        styles[key].fontName = "Times-Bold"
        styles[key].textColor = colors.HexColor("#17324D")
        styles[key].keepWithNext = 1
    width = A4[0] - 92
    story, lines, index = [], markdown.splitlines(), 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line:
            continue
        image = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line)
        if image:
            story.append(Image(str(root / image[2]), width=width, height=width * 4.1 / 7))
            story.append(Paragraph(html.escape(image[1]) + ". Error bars: sample SD, three trials.", styles["Caption"] if "Caption" in styles else styles["PaperCell"]))
            story.append(Spacer(1, 9))
            continue
        if line.startswith("|"):
            data = []
            while True:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                    data.append([Paragraph(html.escape(cell), styles["PaperCell"]) for cell in cells])
                while index < len(lines) and not lines[index].strip():
                    index += 1
                if index >= len(lines) or not lines[index].strip().startswith("|"):
                    break
                line = lines[index].strip()
                index += 1
            table = Table(data, colWidths=[width / len(data[0])] * len(data[0]), repeatRows=1)
            table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF4")),
                ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#B9C5D0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
            captions = []
            while (story and isinstance(story[-1], Paragraph)
                   and story[-1].style.name in ("Heading1", "Heading2", "Heading3", "Heading4")):
                captions.insert(0, story.pop())
            story.append(KeepTogether([*captions, table, Spacer(1, 10)]))
            continue
        heading = re.match(r"^(#{1,4}) (.*)", line)
        if heading:
            style = "PaperTitle" if len(heading[1]) == 1 else f"Heading{len(heading[1]) - 1}"
            story.append(Paragraph(html.escape(heading[2]), styles[style]))
        else:
            while index < len(lines) and lines[index].strip():
                if lines[index].lstrip().startswith(("#", "|", "![")):
                    break
                line += " " + lines[index].strip()
                index += 1
            text = html.escape(line)
            text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
            text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
            story.append(Paragraph(text, styles["Paper"]))

    def page(canvas, document):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#596875"))
        canvas.drawString(46, 26, "Controlled 5G-NIDD replay study - M3")
        canvas.drawRightString(A4[0] - 46, 26, str(document.page))

    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=46, rightMargin=46,
                                 topMargin=43, bottomMargin=43,
                                 title="Sampling and Adaptive Flood Detection in an SDN Emulator")
    document.build(story, onFirstPage=page, onLaterPages=page)


def build(analysis, runs_root, destination, pdf):
    readiness, runs = load_complete(analysis, runs_root)
    aggregated = json.loads((Path(analysis) / "aggregated_metrics.json").read_text())
    groups = {(group["scenario"], group["sampling_rate"]): group for group in aggregated["groups"]}
    if len(groups) != 18 or not all(group["complete_three_trials"] for group in groups.values()):
        raise ValueError("Incompatible or incomplete comparison groups")
    destination = Path(destination)
    write_publication(analysis, runs, destination / "results")
    plot_results(groups, destination / "figures")
    fronts = json.loads((Path(analysis) / "pareto_recommendations.json").read_text())
    for index, front in enumerate(fronts, 1):
        scenario = json.loads(front["comparison_group"])["scenario"]
        shutil.copyfile(Path(analysis) / f"pareto_{index}.png",
                        destination / "figures" / f"pareto_{scenario}.png")
    paper = manuscript(groups, runs, analysis, destination / "figures")
    (destination / "M3_Research_Report.md").write_text(paper, encoding="utf-8", newline="\n")
    render_pdf(paper, destination, Path(pdf))
    print(json.dumps({"accepted_trials": len(runs), "ready": readiness["ready"], "pdf": str(pdf)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", default="output/research/analysis")
    parser.add_argument("--runs", default="output/runs")
    parser.add_argument("--output", default="research")
    parser.add_argument("--pdf", default="output/pdf/M3_Research_Report.pdf")
    args = parser.parse_args()
    build(args.analysis, args.runs, args.output, args.pdf)
