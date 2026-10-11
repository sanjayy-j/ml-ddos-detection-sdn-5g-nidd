import json
import math
from pathlib import Path


class LabelTimeline:
    def __init__(self, path=None):
        self.intervals = []
        self.source = None
        self.verified = False
        self.time_basis = "relative_seconds"
        if path:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if data.get("verified") is not True or not data.get("source"):
                raise ValueError("Packet labels require a verified, documented ground-truth source")
            self.source, self.verified = data["source"], True
            self.time_basis = data.get("time_basis", "relative_seconds")
            if self.time_basis not in {"relative_seconds", "epoch_seconds"}:
                raise ValueError("Unknown label time basis")
            self.intervals = sorted(data.get("intervals", []), key=lambda x: x["start"])
            previous = float("-inf")
            for item in self.intervals:
                if (
                    not all(math.isfinite(item[k]) for k in ("start", "end"))
                    or item["start"] < previous
                    or item["end"] <= item["start"]
                ):
                    raise ValueError("Labels overlap or have invalid bounds")
                if item["label"] not in (0, 1, None):
                    raise ValueError("Labels must be 0, 1 or null")
                previous = item["end"]

    def label(self, start, end, origin):
        if self.time_basis == "epoch_seconds":
            start, end = start + origin, end + origin
        for item in self.intervals:
            if item["start"] <= start and item["end"] >= end:
                return item["label"], item.get("attack_family", "unknown")
        return None, "unknown"
