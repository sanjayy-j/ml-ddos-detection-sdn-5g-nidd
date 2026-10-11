"""Verify controller connectivity and real OVS sFlow export at N=1 and N=10.

This diagnostic uses benign ICMP only, receives actual UDP datagrams, and saves
evidence. It is not the M3 learning collector or an attack-quality experiment.
"""
import json
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def flow_sample_count(payload):
    if len(payload) < 28 or struct.unpack_from("!I", payload)[0] != 5:
        return 0
    kind = struct.unpack_from("!I", payload, 4)[0]
    if kind not in (1, 2):
        return 0
    offset = 12 if kind == 1 else 24
    if len(payload) < offset + 16:
        return 0
    count = struct.unpack_from("!I", payload, offset + 12)[0]
    offset += 16
    flows = 0
    for _ in range(count):
        if len(payload) < offset + 8:
            break
        tag, length = struct.unpack_from("!II", payload, offset)
        flows += int(tag in (1, 3))
        offset += 8 + length
    return flows


def main():
    output = ROOT / "output" / "sdn"
    output.mkdir(parents=True, exist_ok=True)
    manager = Path(sys.executable).parent / "osken-manager"
    controller_log = (output / "controller.log").open("w")
    controller = subprocess.Popen([str(manager), "--ofp-tcp-listen-port", "6653",
                                   str(ROOT / "sdn" / "controller.py")],
                                  stdout=controller_log, stderr=subprocess.STDOUT)
    evidence = []
    try:
        deadline = time.monotonic() + 60
        ready = False
        while time.monotonic() < deadline:
            if controller.poll() is not None:
                raise RuntimeError("Controller exited; inspect output/sdn/controller.log")
            try:
                with socket.create_connection(("127.0.0.1", 6653), timeout=0.5):
                    ready = True
                    break
            except OSError:
                time.sleep(0.25)
        if not ready:
            raise RuntimeError("Controller did not listen within 60 seconds")
        for rate in (1, 10):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
                listener.bind(("127.0.0.1", 6343))
                listener.settimeout(0.5)
                topology_log = (output / f"topology_N{rate}.log").open("w")
                topology = subprocess.Popen([sys.executable, str(ROOT / "sdn" / "topology.py"),
                                             "--sampling", str(rate), "--probe", "--duration", "8",
                                             "--evidence", str(output / f"topology_N{rate}.json")],
                                            stdout=topology_log, stderr=subprocess.STDOUT, cwd=ROOT)
                deadline = time.monotonic() + 60
                packets = []
                while time.monotonic() < deadline:
                    try:
                        payload, source = listener.recvfrom(65535)
                        packets.append(payload)
                    except socket.timeout:
                        pass
                    if topology.poll() is not None:
                        break
                if topology.poll() is None:
                    topology.terminate()
                    topology.wait(timeout=10)
                    raise RuntimeError("Topology timed out; inspect its log")
                topology_log.close()
                topology_data = json.loads((output / f"topology_N{rate}.json").read_text()) if (output / f"topology_N{rate}.json").exists() else {}
                flows = sum(flow_sample_count(packet) for packet in packets)
                (output / f"sflow_N{rate}.hex").write_text("\n".join(packet.hex() for packet in packets) + "\n")
                row = {"sampling_rate": rate, "controller_pid": controller.pid,
                       "topology_exit_code": topology.returncode,
                       "ping_loss_percent": topology_data.get("ping_loss_percent"),
                       "datagrams": len(packets), "received_bytes": sum(map(len, packets)),
                       "flow_samples": flows, "traffic": "benign ICMP diagnostic"}
                row["passed"] = topology.returncode == 0 and row["ping_loss_percent"] == 0 and flows > 0
                evidence.append(row)
                print(json.dumps(row), flush=True)
    finally:
        controller.terminate()
        controller.wait(timeout=10)
        controller_log.close()
        (output / "validation.json").write_text(json.dumps(evidence, indent=2) + "\n")
    return 0 if len(evidence) == 2 and all(row["passed"] for row in evidence) else 1


if __name__ == "__main__":
    raise SystemExit(main())
