import csv
import json
import re
import threading
import uuid
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

RUN_ID = re.compile(r"^[0-9a-f]{32}$")


def utc_now():
    return datetime.now(UTC).isoformat()


def dependency_versions():
    result = {}
    for name in ("m3-sdn", "river", "numpy", "psutil", "dpkt"):
        try:
            result[name] = version(name)
        except PackageNotFoundError:
            result[name] = "not installed"
    return result


def atomic_json(path: Path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


class RunWriter:
    def __init__(self, config, source, provenance=None):
        self.run_id = uuid.uuid4().hex
        self.path = Path(config.output_root) / self.run_id
        self.path.mkdir(parents=True, exist_ok=False)
        self.lock = threading.Lock()
        self.streams = {}
        self.writers = {}
        fields = {
            "predictions": [
                "index",
                "time",
                "y_true",
                "y_pred",
                "score",
                "latency_ms",
                "phase",
                "attack_family",
                "sampled_packets",
                "observed_time",
            ],
            "resources": [
                "time",
                "cpu_percent",
                "rss_mb",
                "telemetry_bytes",
                "controller_cpu_percent",
                "flow_table_entries",
            ],
            "drift": ["time", "index", "event", "detector"],
        }
        for name, columns in fields.items():
            stream = (self.path / f"{name}.csv").open("w", newline="", encoding="utf-8")
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            stream.flush()
            self.streams[name], self.writers[name] = stream, writer
        self.summary = {
            "schema_version": 1,
            "run_id": self.run_id,
            "source": source,
            "mode": config.mode,
            "status": "running",
            "sampling_rate": config.sampling_rate,
            "seed": config.seed,
            "scenario": config.scenario,
            "unit": "flow" if config.mode == "csv_replay" else "window",
            "feature_schema": "flow-v1" if config.mode == "csv_replay" else "packet-window-v1",
            "created_at": utc_now(),
            "ended_at": None,
            "counts": {
                key: 0
                for key in ["input", "sampled", "evaluated", "warmup", "excluded", "unlabeled"]
            },
            "metrics": {},
            "drift_count": 0,
            "error": None,
            "config": config.to_dict(),
            "provenance": provenance,
            "model": {
                "implementation": "river.HoeffdingAdaptiveTreeClassifier",
                "version": "0.1.0",
                "learning_policy": "predict-log-score-learn; oracle labels after prediction",
            },
            "dependencies": dependency_versions(),
        }
        self.save()

    def append(self, kind, row):
        with self.lock:
            self.writers[kind].writerow(row)
            self.streams[kind].flush()

    def save(self):
        with self.lock:
            atomic_json(self.path / "run_summary.json", self.summary)

    def finish(self, metrics, error=None):
        self.summary.update(
            status="failed" if error else "completed",
            metrics=metrics,
            error=str(error) if error else None,
            ended_at=utc_now(),
        )
        self.save()
        with self.lock:
            for stream in self.streams.values():
                stream.close()


class RunRepository:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def directory(self, run_id):
        if not RUN_ID.fullmatch(run_id):
            raise FileNotFoundError("Invalid run ID")
        path = self.root / run_id
        if path.is_symlink() or not path.is_dir():
            raise FileNotFoundError("Run not found")
        return path

    def get(self, run_id):
        return json.loads((self.directory(run_id) / "run_summary.json").read_text(encoding="utf-8"))

    def list(self):
        if not self.root.is_dir():
            return []
        result = []
        for path in self.root.iterdir():
            if RUN_ID.fullmatch(path.name):
                try:
                    result.append(self.get(path.name))
                except (FileNotFoundError, json.JSONDecodeError):
                    continue
        return sorted(result, key=lambda run: run["created_at"], reverse=True)

    def series(self, run_id, limit=1000):
        if limit < 2:
            raise ValueError("Series limit must be at least two")
        result = {}
        for name in ["predictions", "resources", "drift"]:
            rows = []
            path = self.directory(run_id) / f"{name}.csv"
            # Count first, then parse only selected rows: bounded memory even for million-flow runs.
            with path.open(newline="", encoding="utf-8") as stream:
                total = sum(1 for _ in csv.DictReader(stream))
            selected = (
                {round(i * (total - 1) / (limit - 1)) for i in range(limit)}
                if total > limit
                else None
            )
            with path.open(newline="", encoding="utf-8") as stream:
                for index, row in enumerate(csv.DictReader(stream)):
                    if index >= total or (selected is not None and index not in selected):
                        continue
                    if None in row or any(value is None for value in row.values()):
                        continue  # A live writer may be between writes; retry on the next poll.
                    for key, value in row.items():
                        if value == "":
                            row[key] = None
                        elif key not in {"phase", "attack_family", "event", "detector"}:
                            try:
                                row[key] = float(value)
                            except ValueError:
                                pass
                    rows.append(row)
            result[name] = rows
        return result
