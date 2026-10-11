import math
from collections import Counter

import numpy as np


def measurement(value, unit="ratio", reason=None, status="measured"):
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return {
            "value": None,
            "unit": unit,
            "status": "unavailable",
            "reason": reason or "Insufficient observations",
        }
    return {
        "value": float(value),
        "unit": unit,
        "status": status,
        "reason": reason if status == "estimated" else None,
    }


def roc_auc(labels: list[int], scores: list[float]) -> float | None:
    positive, negative = sum(labels), len(labels) - sum(labels)
    if not positive or not negative:
        return None
    ordered = sorted(zip(scores, labels))
    rank_sum = 0.0
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][0] == ordered[i][0]:
            j += 1
        average_rank = ((i + 1) + j) / 2
        rank_sum += average_rank * sum(label for _, label in ordered[i:j])
        i = j
    return (rank_sum - positive * (positive + 1) / 2) / (positive * negative)


class QualityMetrics:
    def __init__(self):
        self.confusion = Counter()
        self.labels: list[int] = []
        self.scores: list[float] = []
        self.latencies: list[float] = []
        self.unseen_true = 0
        self.unseen_detected = 0

    def update(self, label, predicted, score, latency_ms, family, unseen_family="SYNFlood"):
        self.confusion[(label, predicted)] += 1
        self.labels.append(label)
        self.scores.append(score)
        self.latencies.append(latency_ms)
        if label == 1 and family == unseen_family:
            self.unseen_true += 1
            self.unseen_detected += int(predicted == 1)

    def summary(self, unseen_enabled=False):
        tp, fp = self.confusion[(1, 1)], self.confusion[(0, 1)]
        tn, fn = self.confusion[(0, 0)], self.confusion[(1, 0)]
        divide = lambda a, b: a / b if b else None
        result = {
            "precision": measurement(divide(tp, tp + fp), reason="No positive predictions"),
            "recall": measurement(divide(tp, tp + fn), reason="No positive labels"),
            "f1": measurement(
                divide(2 * tp, 2 * tp + fp + fn), reason="No positive labels or predictions"
            ),
            "roc_auc": measurement(
                roc_auc(self.labels, self.scores), reason="ROC-AUC requires both classes"
            ),
            "false_positive_rate": measurement(divide(fp, fp + tn), reason="No negative labels"),
            "inference_latency_ms": measurement(
                np.mean(self.latencies) if self.latencies else None, "ms"
            ),
            "inference_latency_p95_ms": measurement(
                np.percentile(self.latencies, 95) if self.latencies else None, "ms"
            ),
            "unseen_attack_recall": measurement(
                divide(self.unseen_detected, self.unseen_true) if unseen_enabled else None,
                reason="No held-out SYN attack observations"
                if unseen_enabled
                else "Not an unseen-attack scenario",
            ),
        }
        for label, prefix in [(1, "attack"), (0, "benign")]:
            true = self.confusion[(label, label)]
            false = self.confusion[(1 - label, label)]
            missed = self.confusion[(label, 1 - label)]
            result[f"{prefix}_precision"] = measurement(divide(true, true + false))
            result[f"{prefix}_recall"] = measurement(divide(true, true + missed))
            result[f"{prefix}_f1"] = measurement(divide(2 * true, 2 * true + false + missed))
        return result
