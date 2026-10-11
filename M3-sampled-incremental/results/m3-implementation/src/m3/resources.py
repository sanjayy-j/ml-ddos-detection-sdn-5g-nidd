import threading
import time
from statistics import mean

import numpy as np
import psutil

from m3.lab import LabMeasurements
from m3.metrics import measurement


class ResourceMonitor:
    def __init__(self, writer, controller_pid=None):
        self.writer = writer
        self.lab = LabMeasurements(writer)
        self.process = psutil.Process()
        try:
            self.controller = psutil.Process(controller_pid) if controller_pid else None
        except psutil.NoSuchProcess:
            self.controller = None
        self.rows = []
        self.telemetry_bytes = 0
        self.stop_event = threading.Event()
        self.started = time.perf_counter()
        self.thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self.started = time.perf_counter()
        self.lab.start()
        self.process.cpu_percent()
        if self.controller:
            self.controller.cpu_percent()
        self.thread.start()

    def sample(self):
        controller_cpu = None
        if self.controller:
            try:
                controller_cpu = self.controller.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.controller = None
        row = {
            "time": time.perf_counter() - self.started,
            "cpu_percent": self.process.cpu_percent(),
            "rss_mb": self.process.memory_info().rss / 1024**2,
            "telemetry_bytes": self.telemetry_bytes,
            "controller_cpu_percent": controller_cpu,
        }
        row["flow_table_entries"] = self.lab.sample()
        self.rows.append(row)
        self.writer.append("resources", row)

    def _loop(self):
        while not self.stop_event.wait(1):
            self.sample()

    def finish(self, live=False):
        self.stop_event.set()
        self.thread.join()
        self.sample()
        elapsed = max(time.perf_counter() - self.started, 1e-9)
        cpus = [r["cpu_percent"] for r in self.rows]
        controllers = [
            r["controller_cpu_percent"]
            for r in self.rows
            if r["controller_cpu_percent"] is not None
        ]
        return {
            **self.lab.finish(elapsed),
            "cpu_percent_mean": measurement(mean(cpus), "% of one logical CPU"),
            "cpu_percent_p95": measurement(np.percentile(cpus, 95), "% of one logical CPU"),
            "rss_mb_peak": measurement(max(r["rss_mb"] for r in self.rows), "MiB"),
            "telemetry_bandwidth_kbps": measurement(
                self.telemetry_bytes * 8 / elapsed / 1000,
                "kbit/s",
                status="measured" if live else "estimated",
                reason=None
                if live
                else "Serialized feature payload proxy, not an SDN channel measurement",
            ),
            "controller_cpu_percent_mean": measurement(
                mean(controllers) if controllers else None,
                "% of one logical CPU",
                reason="No live controller PID was monitored",
            ),
            "controller_cpu_percent_p95": measurement(
                np.percentile(controllers, 95) if controllers else None,
                "% of one logical CPU",
                reason="No live controller PID was monitored",
            ),
        }
