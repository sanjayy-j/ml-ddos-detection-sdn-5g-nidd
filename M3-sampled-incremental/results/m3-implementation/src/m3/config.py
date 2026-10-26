import json
import math
import re
from dataclasses import asdict, dataclass, fields
from pathlib import Path

SAMPLING_RATES = (1, 2, 5, 10, 20, 50)


@dataclass(frozen=True)
class RunConfig:
    mode: str = "csv_replay"
    input_path: str | None = None
    manifest_path: str = "data/manifest.json"
    labels_path: str | None = None
    flow_labels_path: str | None = None
    output_root: str = "output/runs"
    sampling_rate: int = 1
    seed: int = 42
    scenario: str = "baseline"
    threshold: float = 0.5
    warmup_records: int = 1000
    max_records: int | None = None
    warmup_seconds: float = 20.0
    window_seconds: float = 1.0
    duration_seconds: float = 80.0
    bind: str = "127.0.0.1"
    port: int = 6343
    start_epoch: float | None = None
    controller_pid: int | None = None
    ovs_bridge: str | None = None
    openflow_port: int | None = None
    grace_period: int = 200
    drift_delta: float = 0.002
    naive_bayes: str = "log_space"
    trial_id: int = 1
    label_delay_seconds: float = 0.5
    replay_pps: float = 100.0

    def __post_init__(self):
        if self.mode not in {"csv_replay", "pcap_replay", "live_sflow"}:
            raise ValueError("Unknown input mode")
        if self.flow_labels_path and (self.mode != "pcap_replay" or self.labels_path):
            raise ValueError(
                "flow_labels_path is for offline packet replay only; use either flow labels or timeline labels"
            )
        if type(self.sampling_rate) is not int or self.sampling_rate not in SAMPLING_RATES:
            raise ValueError(f"sampling_rate must be one of {SAMPLING_RATES}")
        if type(self.seed) is not int:
            raise ValueError("seed must be an integer")
        if type(self.trial_id) is not int or self.trial_id < 1:
            raise ValueError("trial_id must be a positive integer")
        if not math.isfinite(self.label_delay_seconds) or self.label_delay_seconds < 0:
            raise ValueError("label_delay_seconds must be nonnegative and finite")
        if not math.isfinite(self.replay_pps) or not 0 < self.replay_pps <= 10000:
            raise ValueError("replay_pps must be positive and bounded")
        for name in ("warmup_records", "grace_period", "port"):
            if type(getattr(self, name)) is not int:
                raise ValueError(f"{name} must be an integer")
        if self.max_records is not None and type(self.max_records) is not int:
            raise ValueError("max_records must be an integer or null")
        if self.scenario not in {"baseline", "drift", "unseen"}:
            raise ValueError("scenario must be baseline, drift or unseen")
        if self.start_epoch is not None and not math.isfinite(self.start_epoch):
            raise ValueError("start_epoch must be finite")
        if self.ovs_bridge is not None and not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]{0,31}", self.ovs_bridge
        ):
            raise ValueError("Invalid OVS bridge name")
        if self.openflow_port is not None and (
            type(self.openflow_port) is not int or not 1 <= self.openflow_port <= 65535
        ):
            raise ValueError("Invalid OpenFlow port")
        if not math.isfinite(self.threshold) or not 0 < self.threshold < 1:
            raise ValueError("threshold must be strictly between 0 and 1")
        if self.warmup_records < 0 or (self.max_records is not None and self.max_records < 1):
            raise ValueError("Invalid record limit")
        for value in (self.window_seconds, self.duration_seconds):
            if not math.isfinite(value) or value <= 0:
                raise ValueError("Window and duration must be positive and finite")
        if not math.isfinite(self.warmup_seconds) or self.warmup_seconds < 0:
            raise ValueError("Warm-up duration must be nonnegative")
        if not 1 <= self.port <= 65535:
            raise ValueError("Invalid UDP port")
        if (
            not math.isfinite(self.drift_delta)
            or not 0 < self.drift_delta < 1
            or self.grace_period < 1
        ):
            raise ValueError("Invalid model configuration")
        # "river" reproduces runs made before this option existed (River 0.23's vote, which
        # treats an underflowed density as certainty); see m3.naive_bayes.
        if self.naive_bayes not in ("river", "log_space"):
            raise ValueError("naive_bayes must be river or log_space")
        if self.mode != "live_sflow" and not self.input_path:
            raise ValueError("Replay modes require input_path")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def load(cls, path: str | Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        unknown = set(data) - {f.name for f in fields(cls)}
        if unknown:
            raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
        return cls(**data)
