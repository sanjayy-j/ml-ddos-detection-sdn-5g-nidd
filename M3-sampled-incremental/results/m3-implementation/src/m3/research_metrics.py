"""Predeclared, conservative estimators for the controlled M3 research study.

These helpers cannot turn a diagnostic, offline replay, or missing measurement
into a scored live experiment. Censored delays remain unavailable, never zero.
"""

import heapq
import json
import math
from collections import Counter, defaultdict
from statistics import mean, stdev

RATES = (1, 2, 5, 10, 20, 50)
SCENARIOS = ("baseline", "drift", "unseen")
VALIDATION_GATES = (
    "actual_switch_config_verified", "independent_tx_rx_match", "zero_capture_drops",
    "raw_hashes_verified", "chronological_prediction_before_label",
)


def _number(value):
    try:
        result = float(value)
    except (ValueError, TypeError):
        return None
    return result if math.isfinite(result) else None


def _boolean(value):
    return value is True or str(value).lower() in {"true", "1"}


def _label(row, key="label"):
    value = row.get(key, row.get("y_true" if key == "label" else "y_pred"))
    return int(value) if str(value) in {"0", "1"} else None


def _warmup(row):
    return _boolean(row.get("warmup", False)) or row.get("phase") == "warmup"


def _completion(row, origin=0):
    epoch = _number(row.get("completion_epoch"))
    relative = _number(row.get("observed_time"))
    return epoch if epoch is not None else origin + relative if relative is not None else None


def physical_detection_metrics(predictions, packet_events, origin_epoch, warmup_seconds,
                               episode_gap_seconds=0.5):
    """Measure physical detection using independent original-IP packet timestamps.

    ``observed_time`` is prediction *completion*, seconds since origin. Packet
    events contain kernel ``epoch``, binary ``label`` and optional ``is_ip``.
    A new episode begins after a benign interval of at least episode_gap_seconds.
    Optional relative window_start/window_end prevent alerts being assigned to
    an unrelated episode. Every original IP event, benign or attack, from onset
    through alert completion (inclusive) counts toward packets-to-detect.
    """
    origin, warmup = _number(origin_epoch), _number(warmup_seconds)
    if origin is None or warmup is None:
        return {"detection_time_seconds": None, "packets_to_detect": None, "episodes": [],
                "reason": "Missing physical origin or warm-up metadata"}
    if origin < 0 or warmup < 0 or episode_gap_seconds <= 0:
        raise ValueError("Warm-up must be nonnegative and episode gap positive")
    events = []
    for row in packet_events:
        epoch = _number(row.get("epoch"))
        if epoch is None or epoch < 0:
            raise ValueError("Every packet event requires a finite kernel epoch")
        if row.get("is_ip", True) and epoch >= origin + warmup:
            events.append({**row, "epoch": epoch})
    events.sort(key=lambda row: row["epoch"])
    episodes, current, benign_start = [], None, None
    for row in events:
        label, epoch = _label(row), row["epoch"]
        if label == 1:
            if current is None or (benign_start is not None
                                   and epoch - benign_start >= episode_gap_seconds):
                current = {"onset_epoch": epoch, "last_attack_epoch": epoch}
                episodes.append(current)
            current["last_attack_epoch"] = epoch
            benign_start = None
        elif label == 0 and benign_start is None:
            benign_start = epoch
    rows = []
    for row in predictions:
        completion = _completion(row, origin)
        if completion is not None and completion >= origin + warmup and not _warmup(row):
            rows.append((completion, row))
    rows.sort(key=lambda item: item[0])
    for index, episode in enumerate(episodes):
        onset = episode["onset_epoch"]
        next_onset = episodes[index + 1]["onset_epoch"] if index + 1 < len(episodes) else math.inf
        alert = None
        for completion, row in rows:
            if not (onset <= completion < next_onset
                    and _label(row) == 1 and _label(row, "predicted") == 1):
                continue
            start, end = _number(row.get("window_start")), _number(row.get("window_end"))
            if end is not None and origin + end <= onset:
                continue
            if start is not None and origin + start > episode["last_attack_epoch"]:
                continue
            alert = completion
            break
        episode.update({
            "alert_completion_epoch": alert,
            "detection_time_seconds": alert - onset if alert is not None else None,
            "packets_to_detect": sum(onset <= event["epoch"] <= alert for event in events)
            if alert is not None else None,
            "censored": alert is None,
            "reason": "No true-positive completed alert in this episode" if alert is None else None,
        })
    first = episodes[0] if episodes else {}
    return {
        "detection_time_seconds": first.get("detection_time_seconds"),
        "packets_to_detect": first.get("packets_to_detect"),
        "episodes": episodes,
        "false_positive_alerts": sum(_label(row) == 0 and _label(row, "predicted") == 1
                                     for _, row in rows),
        "count_definition": "All independent original IP packets, any class, onset through "
                            "alert completion inclusive; not sampled/exported packet counts",
        "episode_gap_seconds": episode_gap_seconds,
        "reason": "No post-warm-up labelled attack packets" if not episodes else first["reason"],
    }


def _balanced_accuracy(rows):
    totals = Counter(_label(row) for row in rows)
    if not totals[0] or not totals[1]:
        return None
    return sum(sum(_label(row) == label and _label(row, "predicted") == label
                   for row in rows) / totals[label] for label in (0, 1)) / 2


def post_drift_recovery(predictions, boundary_time, *, threshold=0.9, window=40,
                        consecutive=3, baseline_relative=None, baseline_accuracy=None):
    """First sustained qualifying rolling check, confirmed by later checks.

    Only observations completed at/after the predefined boundary are used. All
    rolling windows must contain both classes. Recovery time denotes the first
    qualifying check, while confirmation_time is the final sustaining check.
    Optional baseline-relative criterion must be declared before seeing results.
    """
    boundary = _number(boundary_time)
    if boundary is None or window < 2 or consecutive < 1 or not 0 <= threshold <= 1:
        raise ValueError("Invalid recovery criterion")
    if baseline_relative is not None:
        if baseline_accuracy is None or not 0 <= baseline_relative <= 1:
            raise ValueError("Baseline-relative recovery requires a declared baseline accuracy")
        threshold = baseline_relative * baseline_accuracy
    scored = [row for row in predictions
              if _number(row.get("observed_time")) is not None
              and float(row["observed_time"]) >= boundary
              and not _warmup(row)
              and _label(row) is not None and _label(row, "predicted") is not None]
    scored.sort(key=lambda row: float(row["observed_time"]))
    streak, first_time = 0, None
    for end in range(window, len(scored) + 1):
        accuracy = _balanced_accuracy(scored[end - window:end])
        time = float(scored[end - 1]["observed_time"])
        if accuracy is not None and accuracy >= threshold:
            if not streak:
                first_time = time
            streak += 1
            if streak == consecutive:
                return {"recovery_seconds": first_time - boundary, "confirmation_time": time,
                        "censored": False, "reason": None, "threshold": threshold,
                        "window": window, "consecutive": consecutive}
        else:
            streak, first_time = 0, None
    return {"recovery_seconds": None, "confirmation_time": None, "censored": True,
            "reason": "No sustained post-boundary recovery with both classes observed",
            "threshold": threshold, "window": window, "consecutive": consecutive}


def student_summary(values):
    """Unbounded two-sided Student-t mean CI; n=3 is explicitly a small study."""
    values = [float(v) for v in values if _number(v) is not None]
    n = len(values)
    average, sd = mean(values) if values else None, stdev(values) if n > 1 else None
    interval = None
    if n > 1:
        from scipy.stats import t

        half_width = float(t.ppf(0.975, n - 1)) * sd / math.sqrt(n)
        interval = [average - half_width, average + half_width]
    return {"n": n, "mean": average, "sample_sd": sd, "ci95": interval,
            "ci_method": "Student-t, two-sided, unbounded; repeatability not population proof",
            "small_sample_warning": n < 10}


def eligible(run):
    return (run.get("source") == "official_realtime_verified"
            and run.get("status") == "completed"
            and run.get("research", {}).get("study_role") != "validation_pilot"
            and run.get("validation", {}).get("accepted") is True)


def comparison_signature(run):
    config = run.get("config", {})
    settings = {key: value for key, value in config.items()
                if key not in {"trial_id", "seed", "sampling_rate", "sampling_n", "run_id",
                               "output", "output_root", "sampling_offset", "start_epoch",
                               "controller_pid", "bind", "port", "ovs_bridge", "openflow_port"}}
    return json.dumps({"scenario": run.get("scenario", config.get("scenario")),
                       "feature_schema": run.get("feature_schema"),
                       "provenance": run.get("provenance"),
                       "versions": run.get("versions", run.get("dependencies")),
                       "model_parameters": run.get("model_parameters"), "settings": settings},
                      sort_keys=True, default=str)


def _trial(run):
    return str(run.get("config", {}).get("trial_id", run.get("seed")))


def _rate(run):
    return run.get("sampling_rate", run.get("config", {}).get("sampling_n"))


def _metric(run, name):
    item = run.get("metrics", {}).get(name)
    if not isinstance(item, dict) or item.get("status") != "measured":
        return None
    value = _number(item.get("value"))
    return (value, item.get("unit")) if value is not None else None


def aggregate_trials(runs):
    groups, excluded = defaultdict(list), []
    for run in runs:
        if not eligible(run):
            excluded.append({"run_id": run.get("run_id"), "status": run.get("status"),
                             "reason": "Not a completed accepted official real-time trial",
                             "error": run.get("error")})
        else:
            groups[(comparison_signature(run), _rate(run))].append(run)
    output = []
    for (signature, rate), group in sorted(groups.items(), key=lambda item: str(item[0])):
        trials = [_trial(run) for run in group]
        duplicate = len(set(trials)) != len(trials) or "None" in trials
        metrics = {}
        for name in sorted({name for run in group for name in run.get("metrics", {})}):
            items = [_metric(run, name) for run in group]
            units = {item[1] for item in items if item is not None}
            usable = [item[0] for item in items if item is not None]
            summary = student_summary(usable if len(units) == 1 and not duplicate else [])
            summary.update({"missing_trials": len(group) - len(usable),
                            "unit": next(iter(units)) if len(units) == 1 else None,
                            "reason": "Duplicate trial IDs or incompatible units" if duplicate
                            or len(units) > 1 else None})
            metrics[name] = summary
        output.append({"comparison_group": signature, "sampling_rate": rate,
                       "scenario": group[0].get("scenario"), "trial_ids": trials,
                       "run_ids": [run.get("run_id") for run in group],
                       "complete_three_trials": len(set(trials)) == 3 and not duplicate,
                       "metrics": metrics})
    return {"groups": output, "excluded": excluded}


def paired_deltas(runs):
    groups = defaultdict(list)
    for run in runs:
        if eligible(run):
            groups[comparison_signature(run)].append(run)
    output = []
    for signature, group in groups.items():
        identities = [(_rate(run), _trial(run)) for run in group]
        if len(identities) != len(set(identities)) or any(t == "None" for _, t in identities):
            output.append({"comparison_group": signature, "metrics": {},
                           "reason": "Duplicate or missing trial IDs prevent exact pairing"})
            continue
        baseline = {_trial(run): run for run in group if _rate(run) == 1}
        for rate in sorted({_rate(run) for run in group if _rate(run) != 1}):
            candidate = {_trial(run): run for run in group if _rate(run) == rate}
            paired = sorted(set(baseline) & set(candidate))
            metrics = {}
            for name in sorted({name for run in group for name in run.get("metrics", {})}):
                deltas = []
                for trial in paired:
                    a, b = _metric(baseline[trial], name), _metric(candidate[trial], name)
                    if a is not None and b is not None and a[1] == b[1]:
                        deltas.append(b[0] - a[0])
                metrics[name] = student_summary(deltas)
            output.append({"comparison_group": signature, "sampling_rate": rate,
                           "reference_sampling_rate": 1, "paired_trial_ids": paired,
                           "delta_definition": "N minus N=1 within identical trial ID",
                           "metrics": metrics})
    return output


def select_pareto(points, quality_weight=0.5):
    """Descriptive ideal-point criterion using both measured channel costs.

    Inputs must already be comparable (same scenario, schema, replay and model
    settings). Each cost uses kbit/s; proxies and missing channels are excluded.
    Normalization uses all eligible points, and weights must be predeclared.
    """
    if not 0 <= quality_weight <= 1:
        raise ValueError("Quality weight must be between zero and one")
    valid, excluded = [], []
    for point in points:
        costs = [point.get(key, {}) for key in
                 ("sflow_bandwidth_kbit_s", "openflow_bandwidth_kbit_s")]
        quality = _number(point.get("f1"))
        if quality is None or not 0 <= quality <= 1 or any(
            not isinstance(cost, dict) or cost.get("status") != "measured"
            or cost.get("unit") != "kbit/s" or _number(cost.get("value")) is None
            or float(cost["value"]) < 0 for cost in costs
        ):
            excluded.append({"sampling_rate": point.get("sampling_rate"),
                             "reason": "Requires quality and both measured kbit/s channels"})
            continue
        valid.append({**point, "f1": quality, "combined_bandwidth_kbit_s":
                      sum(float(cost["value"]) for cost in costs)})
    front = [p for p in valid if not any(
        q["f1"] >= p["f1"] and q["combined_bandwidth_kbit_s"] <= p["combined_bandwidth_kbit_s"]
        and (q["f1"] > p["f1"] or q["combined_bandwidth_kbit_s"] < p["combined_bandwidth_kbit_s"])
        for q in valid)]
    if front:
        qualities = [p["f1"] for p in valid]
        costs = [p["combined_bandwidth_kbit_s"] for p in valid]
        for point in front:
            quality_gap = (max(qualities) - point["f1"]) / (max(qualities) - min(qualities)) \
                if max(qualities) != min(qualities) else 0
            cost_gap = (point["combined_bandwidth_kbit_s"] - min(costs)) / (max(costs) - min(costs)) \
                if max(costs) != min(costs) else 0
            point["ideal_distance"] = math.sqrt(quality_weight * quality_gap**2
                                                + (1 - quality_weight) * cost_gap**2)
    return {"front": front, "excluded": excluded,
            "recommendation": min(front, key=lambda p: (p["ideal_distance"],
                                                         p["combined_bandwidth_kbit_s"]))
            if front else None,
            "criterion": "Predeclared normalized weighted Euclidean distance to ideal",
            "quality_weight": quality_weight, "descriptive_only": True}


def evaluate_ablations(rows, *, seed=1, grace_period=50, drift_delta=0.002, threshold=0.5):
    """Offline quality-only ablations of the exact recorded feature sequence.

    Models predict before receiving each available label. The dummy is fixed to
    the warm-up majority (ties benign), never fitted on scored observations.
    These results do not claim equivalent measured live runtime costs.
    """
    from river import drift, tree

    from m3.metrics import QualityMetrics

    rows = list(rows)
    models = {
        "hat_adwin": tree.HoeffdingAdaptiveTreeClassifier(
            grace_period=grace_period, seed=seed, drift_detector=drift.ADWIN(delta=drift_delta),
            nominal_attributes=["Proto"], max_size=100),
        "hoeffding_tree": tree.HoeffdingTreeClassifier(
            grace_period=grace_period, nominal_attributes=["Proto"], max_size=100),
    }
    delayed = any("label_available_time" in row for row in rows)
    if delayed and any(_number(row.get("label_available_time")) is None
                       or _number(row.get("observed_time")) is None
                       for row in rows if _label(row) is not None):
        raise ValueError("Delayed-label ablations require every completion and availability time")
    times = [float(row["observed_time"]) for row in rows] if delayed else []
    if times != sorted(times):
        raise ValueError("Ablation completion times must preserve chronological feature order")
    first_scored = next((float(row["observed_time"]) for row in rows
                         if not _warmup(row)), math.inf) if delayed else math.inf
    warm_labels = [_label(row) for row in rows if _warmup(row)
                   and _label(row) is not None
                   and (not delayed or float(row["label_available_time"]) <= first_scored)]
    if not warm_labels:
        raise ValueError("Ablations require an explicit labelled warm-up segment")
    seen_scored = False
    for row in rows:
        if _warmup(row) and seen_scored:
            raise ValueError("Warm-up must be a chronological prefix")
        if not _warmup(row):
            seen_scored = True
    dummy = int(sum(warm_labels) > len(warm_labels) / 2)
    quality = {name: QualityMetrics() for name in (*models, "majority_warmup")}
    evaluated, pending = 0, []
    for index, row in enumerate(rows):
        label = _label(row)
        if label is None:
            continue
        features = row.get("features")
        if not isinstance(features, dict) or not features:
            raise ValueError("Every labelled observation requires its recorded features")
        warm = _warmup(row)
        if delayed:
            while pending and pending[0][0] <= float(row["observed_time"]):
                _, _, old_features, old_label = heapq.heappop(pending)
                for model in models.values():
                    model.learn_one(old_features, old_label)
        for name, model in models.items():
            score = float(model.predict_proba_one(features).get(1, 0))
            if not warm:
                quality[name].update(label, int(score >= threshold), score, 0,
                                     row.get("attack_family", row.get("family", "unknown")))
            if not delayed:
                model.learn_one(features, label)
        if delayed:
            heapq.heappush(pending, (float(row["label_available_time"]), index, features, label))
        if not warm:
            quality["majority_warmup"].update(label, dummy, float(dummy), 0,
                                              row.get("attack_family", row.get("family", "unknown")))
            evaluated += 1
    return {name: {"metrics": {key: value for key, value in metric.summary().items()
                               if not key.startswith("inference_latency")},
                   "evaluated": evaluated, "fixed_prediction": dummy
                   if name == "majority_warmup" else None,
                   "label_policy": "Recorded delayed availability; no early learning" if delayed
                   else "Immediate oracle label after prediction; availability timestamps absent",
                   "scope": "Offline quality-only; same exact recorded features and order"}
            for name, metric in quality.items()}


def research_readiness(runs):
    """Evidence checklist, not a journal acceptance or novelty guarantee."""
    accepted = [run for run in runs if eligible(run)]
    cells = defaultdict(list)
    for run in accepted:
        cells[(run.get("scenario"), _rate(run))].append(run)
    missing = []
    for scenario in SCENARIOS:
        for rate in RATES:
            group = cells[(scenario, rate)]
            ids = [_trial(run) for run in group]
            if len(ids) != 3 or len(set(ids)) != 3 or "None" in ids:
                missing.append({"scenario": scenario, "sampling_rate": rate,
                                "accepted_trial_ids": ids, "required_distinct_trials": 3})
    evidence = {
        gate: bool(accepted) and all(run.get("validation", {}).get(gate) is True for run in accepted)
        for gate in VALIDATION_GATES
    }
    evidence["raw_hash_links"] = bool(accepted) and all(run.get("raw_hashes") for run in accepted)
    evidence["exactly_54_planned_trials"] = len(accepted) == 54
    evidence["primary_window_0_1_seconds"] = bool(accepted) and all(
        run.get("config", {}).get("window_seconds") == 0.1 for run in accepted)
    evidence["both_classes_scored"] = bool(accepted) and all(
        run.get("validation", {}).get("both_classes_scored") is True for run in accepted)
    for key in ("ablations_completed", "sensitivity_completed"):
        evidence[key] = bool(accepted) and all(run.get("research", {}).get(key) is True
                                             for run in accepted)
    return {"ready": not missing and all(evidence.values()), "accepted_trials": len(accepted),
            "expected_trials": 54, "missing_cells": missing, "evidence_gates": evidence,
            "assessment": "Research evidence complete" if not missing and all(evidence.values())
            else "Research evidence incomplete; missing gates must not be described as completed",
            "caveat": "Passing gates does not establish novelty or guarantee paper acceptance. "
                      "Three repeats describe controlled repeatability with wide uncertainty."}
