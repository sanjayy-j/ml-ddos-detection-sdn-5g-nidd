"""Opt-in offline experiment; the live detector and feature schema are unchanged.

History uses closed sampled-telemetry windows only. Labels, packet identities,
oracle packet counts, absolute time and future observations are not features.
"""

import heapq
import math
from collections import deque

from m3.config import RunConfig
from m3.metrics import QualityMetrics
from m3.model import OnlineDetector
from m3.naive_bayes import likelihood


class RecentHistory:
    """Append a fixed trailing 0.5 s context, including the current closed bin.

    Protocol/size means are weighted by observed packet counts. Exported rates
    already include sampling weights; integrate them before dividing by the
    observed history duration. Startup uses the available partial history.
    """

    def __init__(self, horizon=0.5):
        if not math.isfinite(horizon) or horizon <= 0:
            raise ValueError("History horizon must be positive and finite")
        self.horizon = horizon
        self.windows = deque()
        self.previous_end = None
        self.empty_streak = 0

    def update(self, *, features, start, end, sampled_packets):
        start, end = float(start), float(end)
        if not all(math.isfinite(t) for t in (start, end)) or end <= start:
            raise ValueError("Window bounds must be finite and increasing")
        if end - start > self.horizon + 1e-8:
            raise ValueError("History must cover at least one complete window")
        if self.previous_end is not None and start < self.previous_end - 1e-8:
            raise ValueError("Windows must be chronological and non-overlapping")
        if type(sampled_packets) is not int or sampled_packets < 0:
            raise ValueError("Sampled packet count must be a nonnegative integer")
        if any(not math.isfinite(float(v)) for v in features.values()):
            raise ValueError("Features must be finite numbers")
        if self.previous_end is None or start > self.previous_end + 1e-8:
            self.empty_streak = 0
        self.empty_streak = self.empty_streak + 1 if sampled_packets == 0 else 0
        self.previous_end = end
        self.windows.append((start, end, dict(features), sampled_packets))
        while self.windows and self.windows[0][1] <= end - self.horizon + 1e-8:
            self.windows.popleft()
        # Fixed 0.1 s bins align exactly with 0.5 s. Proportional overlap also
        # defines behavior for arbitrary valid bins, without consulting packets.
        pieces = [(max(s, end - self.horizon), e, f, n,
                   (e - max(s, end - self.horizon)) / (e - s))
                  for s, e, f, n in self.windows]
        span = end - pieces[0][0]
        count = sum(n * weight for _, _, _, n, weight in pieces)
        result = dict(features)
        result["history_sampled_packets"] = count
        for key in ("packets_per_second", "bytes_per_second"):
            result[f"history_{key}"] = sum(f[key] * (e - s) for s, e, f, _, _ in pieces) / span
        for key in ("mean_packet_size", "udp_fraction", "tcp_fraction", "icmp_fraction",
                    "syn_fraction"):
            result[f"history_{key}"] = (
                sum(f[key] * n * weight for _, _, f, n, weight in pieces) / count
                if count else 0.0)
        result["history_empty_fraction"] = sum(
            (e - s) * int(n == 0) for s, e, _, n, _ in pieces) / span
        result["history_empty_streak"] = self.empty_streak
        return result


def replay_comparison(rows, config, horizon=0.5):
    """Paired prequential replay using recorded completion/label availability.

    Both models get identical observations, labels, seeds and hyperparameters.
    Only the experimental feature transform differs. Pending examples retain
    their original feature snapshot. No model timing measurements are claimed.
    """
    config = RunConfig(**{**config, "naive_bayes": config.get("naive_bayes", "river")})
    models = {name: OnlineDetector(config) for name in ("current", "recent_history")}
    history = RecentHistory(horizon)
    quality = {name: QualityMetrics() for name in models}
    pending = []
    predictions = []
    last_time = -math.inf
    baseline_prediction_mismatches = 0
    max_baseline_score_error = 0.0
    seen_scored = False
    for index, row in enumerate(rows):
        observed = float(row["observed_time"])
        available = float(row["label_available_time"])
        if not math.isfinite(observed) or observed < last_time:
            raise ValueError("Completion times must be finite and chronological")
        if not math.isfinite(available) or available < observed:
            raise ValueError("Labels must be available only after prediction")
        last_time = observed
        warm = row["warmup"]
        if type(warm) is not bool or (warm and seen_scored):
            raise ValueError("Explicit warm-up must be a chronological prefix")
        seen_scored |= not warm
        features = dict(row["features"])
        transformed = history.update(features=features, start=row["window_start"],
                                     end=row["window_end"], sampled_packets=row["sampled_packets"])
        inputs = {"current": features, "recent_history": transformed}
        while pending and pending[0][0] <= observed:
            _, _, old_inputs, label = heapq.heappop(pending)
            for name, detector in models.items():
                with likelihood(config.naive_bayes):
                    detector.model.learn_one(old_inputs[name], label)
        results = {name: detector.predict(inputs[name])[:2] for name, detector in models.items()}
        label = row["y_true"]
        if label is not None and (type(label) is not int or label not in (0, 1)):
            raise ValueError("Labels must be binary integers or null")
        scored = label is not None and not warm
        prediction_row = {"index": row["index"], "warmup": warm, "scored": scored,
                          "label": label, "sampled_packets": row["sampled_packets"]}
        for name, (predicted, score) in results.items():
            prediction_row[name] = {"prediction": predicted, "score": score}
            if scored:
                quality[name].update(label, predicted, score, 0, row["attack_family"])
        predictions.append(prediction_row)
        if scored:
            baseline_prediction_mismatches += results["current"][0] != row["y_pred"]
            max_baseline_score_error = max(max_baseline_score_error,
                                           abs(results["current"][1] - row["score"]))
        if label is not None:
            heapq.heappush(pending, (available, index, inputs, label))
    return {
        "models": {name: {
            "metrics": {k: v["value"] for k, v in metric.summary(
                unseen_enabled=config.scenario == "unseen").items()
                        if not k.startswith("inference_latency")},
            "confusion": {"tp": metric.confusion[(1, 1)], "fp": metric.confusion[(0, 1)],
                          "tn": metric.confusion[(0, 0)], "fn": metric.confusion[(1, 0)]},
        } for name, metric in quality.items()},
        "baseline_prediction_mismatches": baseline_prediction_mismatches,
        "max_baseline_score_error": max_baseline_score_error,
        "predictions": predictions,
    }
