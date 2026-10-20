"""Read-only OVS observation and loopback-only OpenFlow capture for the isolated lab."""

import signal
import subprocess
import sys

import dpkt

from m3.metrics import measurement


class LabMeasurements:
    def __init__(self, writer):
        self.writer = writer
        config = writer.summary["config"]
        self.origin = config.get("start_epoch")
        self.duration = config.get("duration_seconds")
        self.bridge = config.get("ovs_bridge") if config["mode"] == "live_sflow" else None
        self.port = config.get("openflow_port") if config["mode"] == "live_sflow" else None
        self.capture = None
        self.log = None
        self.flow_counts = []
        self.flow_error = "OVS observation was not configured"
        self.capture_error = "Independent OpenFlow capture was not configured"

    def start(self):
        if self.port is None:
            return
        if sys.platform != "linux":
            self.capture_error = "OpenFlow capture must run inside the Linux SDN namespace"
            return
        try:
            self.log = (self.writer.path / "openflow_capture.log").open("wb")
            self.capture = subprocess.Popen(
                [
                    "tcpdump",
                    "-i",
                    "lo",
                    "-U",
                    "-w",
                    str(self.writer.path / "openflow.pcap"),
                    "tcp",
                    "port",
                    str(self.port),
                ],
                stdout=self.log,
                stderr=subprocess.STDOUT,
            )
        except OSError as exc:
            self.capture_error = f"OpenFlow capture could not start: {exc}"
            if self.log:
                self.log.close()
                self.log = None

    def sample(self):
        if not self.bridge:
            return None
        try:
            result = subprocess.run(
                ["ovs-ofctl", "-O", "OpenFlow13", "dump-flows", self.bridge],
                capture_output=True,
                text=True,
                timeout=1,
                check=True,
            )
            if "OFPST_FLOW" not in result.stdout and "OFPMP_FLOW" not in result.stdout:
                raise ValueError("OVS did not return a flow-statistics reply")
            count = sum("cookie=" in line for line in result.stdout.splitlines())
            self.flow_counts.append(count)
            return count
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            self.flow_error = f"OVS flow observation unavailable: {exc}"
            return None

    def finish(self, elapsed):
        byte_count = None
        if self.capture:
            try:
                if self.capture.poll() is None:
                    self.capture.send_signal(signal.SIGINT)
                self.capture.wait(timeout=3)
                if self.capture.returncode != 0:
                    raise ValueError("tcpdump failed; inspect openflow_capture.log")
                with (self.writer.path / "openflow.pcap").open("rb") as stream:
                    byte_count = sum(len(packet) for epoch, packet in dpkt.pcap.Reader(stream)
                                     if self.origin is None or self.origin <= float(epoch)
                                     < self.origin + self.duration)
            except (OSError, ValueError, dpkt.UnpackError, subprocess.SubprocessError) as exc:
                self.capture_error = f"OpenFlow capture unavailable: {exc}"
            finally:
                if self.capture.poll() is None:
                    self.capture.kill()
                    self.capture.wait(timeout=3)
                if self.log:
                    self.log.close()
        return {
            "openflow_bandwidth_kbps": measurement(
                byte_count * 8 / elapsed / 1000 if byte_count is not None else None,
                "kbit/s",
                self.capture_error,
            ),
            "flow_table_entries": measurement(
                sum(self.flow_counts) / len(self.flow_counts) if self.flow_counts else None,
                "entries (snapshot mean)",
                self.flow_error,
            ),
        }
