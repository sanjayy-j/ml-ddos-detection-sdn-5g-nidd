import json
import random
import time
from dataclasses import replace

from m3.data import iter_csv
from m3.labels import LabelTimeline
from m3.metrics import QualityMetrics, measurement
from m3.model import OnlineDetector
from m3.packets import WindowAccumulator, iter_pcap, parse_header
from m3.provenance import verify_input
from m3.resources import ResourceMonitor
from m3.store import RunWriter


class Evaluation:
    def __init__(self, config, writer, model=None):
        self.config, self.writer = config, writer
        self.detector = model or OnlineDetector(config)
        self.quality = QualityMetrics()
        self.first_attack = None
        self.first_alarm = None
        self.processed = 0
        self.last_save = time.perf_counter()

    def observe(self, record, warmup=False, sampled_packets=None, observed_time=None):
        counts = self.writer.summary["counts"]
        label = record.label
        if warmup and self.config.scenario == "unseen" and record.attack_family == "SYNFlood":
            counts["excluded"] += 1
            return
        predicted, score, latency = self.detector.predict(record.features)
        observed_time = (
            observed_time
            if observed_time is not None
            else record.time
            + (0 if self.config.mode == "csv_replay" else self.config.window_seconds)
        )
        phase = "unlabeled" if label is None else "warmup" if warmup else "evaluation"
        self.writer.append(
            "predictions",
            {
                "index": record.index,
                "time": record.time,
                "y_true": label,
                "y_pred": predicted,
                "score": score,
                "latency_ms": latency,
                "phase": phase,
                "attack_family": record.attack_family,
                "sampled_packets": sampled_packets,
                "observed_time": observed_time,
            },
        )
        if label is None:
            counts["unlabeled"] += 1
        elif warmup:
            counts["warmup"] += 1
            self.detector.learn(record.features, label, predicted, monitor=False)
        else:
            # Evaluation order is deliberately visible: log/score before learning.
            self.quality.update(label, predicted, score, latency, record.attack_family)
            counts["evaluated"] += 1
            if label == 1 and self.first_attack is None:
                self.first_attack = record.time
            if label == 1 and predicted == 1 and self.first_alarm is None:
                self.first_alarm = observed_time
            if self.detector.learn(record.features, label, predicted):
                self.writer.append(
                    "drift",
                    {
                        "time": record.time,
                        "index": record.index,
                        "event": "error_distribution_change",
                        "detector": "external_ADWIN",
                    },
                )
                self.writer.summary["drift_count"] += 1
        self.processed += 1
        if time.perf_counter() - self.last_save > 1:
            self.writer.summary["metrics"] = self.summary()
            self.writer.save()
            self.last_save = time.perf_counter()

    def summary(self):
        result = self.quality.summary(self.config.scenario == "unseen")
        physical = self.config.mode != "csv_replay"
        delay = (
            self.first_alarm - self.first_attack
            if physical and self.first_alarm is not None
            else None
        )
        result.update(
            {
                "detection_time_seconds": measurement(
                    delay,
                    "seconds",
                    "No detected, labeled attack"
                    if physical
                    else "CSV row indices are not physical timestamps",
                    status="measured" if self.config.mode == "live_sflow" else "estimated",
                ),
                "packets_to_detect": measurement(
                    None, "packets", "Requires unsampled ground-truth packet counts"
                ),
                "post_drift_recovery_seconds": measurement(
                    None, "seconds", "Requires an annotated drift boundary and recovery analysis"
                ),
            }
        )
        return result


def run_replay(config, *, fixture=False, model=None):
    provenance = None if fixture else verify_input(config.input_path, config.manifest_path)
    writer = RunWriter(config, "fixture" if fixture else "official_5g_nidd", provenance)
    evaluator = Evaluation(config, writer, model)
    resources = ResourceMonitor(writer)
    resources.start()
    rng = random.Random(config.seed)
    error = None
    try:
        if config.mode == "csv_replay":
            eligible = 0
            for record in iter_csv(config.input_path):
                counts = writer.summary["counts"]
                counts["input"] += 1
                if config.max_records is not None and counts["input"] > config.max_records:
                    counts["input"] -= 1
                    break
                if record.label is None:
                    counts["excluded"] += 1
                    continue
                warmup = eligible < config.warmup_records
                eligible += 1
                if rng.random() >= 1 / config.sampling_rate:
                    continue
                counts["sampled"] += 1
                resources.telemetry_bytes += len(json.dumps(record.features).encode())
                evaluator.observe(record, warmup)
            writer.summary["notes"] = [
                "Flow-record subsampling; scored quality is conditional on selection",
                "CSV row order does not establish natural chronology",
            ]
        elif config.mode == "pcap_replay":
            labels = LabelTimeline(config.labels_path)
            accumulator = WindowAccumulator(config.window_seconds)
            origin = None

            def observe_window(item):
                record, count = item
                label, family = labels.label(
                    record.time, record.time + config.window_seconds, origin
                )
                evaluator.observe(
                    replace(record, label=label, attack_family=family),
                    record.time < config.warmup_seconds,
                    count,
                )

            for timestamp, header in iter_pcap(config.input_path):
                if origin is None:
                    origin = timestamp
                writer.summary["counts"]["input"] += 1
                if config.max_records and writer.summary["counts"]["input"] > config.max_records:
                    writer.summary["counts"]["input"] -= 1
                    break
                for item in accumulator.advance(timestamp - origin):
                    observe_window(item)
                packet = parse_header(header, timestamp, len(header), config.sampling_rate)
                if packet and rng.random() < 1 / config.sampling_rate:
                    writer.summary["counts"]["sampled"] += 1
                    resources.telemetry_bytes += min(len(header), 128)
                    for item in accumulator.add(packet, origin):
                        observe_window(item)
            # The final incomplete capture window is intentionally not scored.
            writer.summary["notes"] = [
                "Seeded offline packet selection, not measured switch export",
                "Final partial capture window excluded",
            ]
        else:
            raise ValueError("Use the live collector for live_sflow mode")
    except Exception as exc:  # noqa: BLE001 - preserve failures from third-party models in the run log
        error = exc
    metrics = {**evaluator.summary(), **resources.finish()}
    writer.finish(metrics, error)
    if error:
        raise RuntimeError(f"Run {writer.run_id} failed; raw logs preserved: {error}") from error
    return writer.summary
