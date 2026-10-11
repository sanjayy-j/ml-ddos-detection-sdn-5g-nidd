"""Run the genuine M3 collector against an isolated benign sFlow probe.

The resulting run is telemetry validation with no attack-quality labels.
"""
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "output" / "sdn"
    output.mkdir(parents=True, exist_ok=True)
    binaries = Path(sys.executable).parent
    with (output / "live_controller.log").open("w") as controller_log, \
         (output / "live_collector.log").open("w") as collector_log, \
         (output / "live_topology.log").open("w") as topology_log:
        controller = subprocess.Popen([str(binaries / "osken-manager"), "--ofp-tcp-listen-port", "6653",
                                       str(ROOT / "sdn" / "controller.py")],
                                      stdout=controller_log, stderr=subprocess.STDOUT)
        collector = None
        try:
            deadline = time.monotonic() + 60
            while True:
                if controller.poll() is not None:
                    raise RuntimeError("Controller failed; inspect live_controller.log")
                try:
                    with socket.create_connection(("127.0.0.1", 6653), timeout=0.5):
                        break
                except OSError:
                    if time.monotonic() > deadline:
                        raise RuntimeError("Controller startup timed out")
                    time.sleep(0.25)
            config = {"mode": "live_sflow", "sampling_rate": 1, "seed": 42, "scenario": "baseline",
                      "output_root": str(ROOT / "output" / "runs"), "bind": "127.0.0.1", "port": 6343,
                      "duration_seconds": 22, "warmup_seconds": 2, "window_seconds": 1,
                      "threshold": 0.5, "labels_path": None, "controller_pid": controller.pid,
                      "ovs_bridge": "m3s1", "openflow_port": 6653}
            config_path = output / "live_validation_config.json"
            config_path.write_text(json.dumps(config, indent=2) + "\n")
            collector = subprocess.Popen([str(binaries / "m3"), "live", "--config", str(config_path)],
                                         stdout=collector_log, stderr=subprocess.STDOUT, cwd=ROOT)
            time.sleep(4)
            if collector.poll() is not None:
                raise RuntimeError("Collector failed; inspect live_collector.log")
            topology = subprocess.run([sys.executable, str(ROOT / "sdn" / "topology.py"),
                                       "--sampling", "1", "--probe", "--duration", "8",
                                       "--evidence", str(output / "live_topology.json")],
                                      stdout=topology_log, stderr=subprocess.STDOUT, cwd=ROOT, timeout=45)
            collector.wait(timeout=40)
            if topology.returncode or collector.returncode:
                raise RuntimeError("Live validation failed; inspect saved logs")
            print("Genuine M3 collector run saved in output/runs; source=live_sflow, labels unavailable.")
        finally:
            if collector and collector.poll() is None:
                collector.terminate()
                collector.wait(timeout=10)
            controller.terminate()
            controller.wait(timeout=10)


if __name__ == "__main__":
    main()
