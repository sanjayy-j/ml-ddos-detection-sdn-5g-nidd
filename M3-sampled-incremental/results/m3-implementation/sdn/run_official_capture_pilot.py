"""Collect genuine switch exports plus independent TX/RX evidence for prepared blocks.

This stage does not claim real-time detection accuracy. Collection is unlabelled;
validated recorded exports can subsequently be scored explicitly post hoc.
"""

import argparse
import json
import math
import os
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from m3.packets import iter_pcap
from m3.provenance import sha256, verify_input
from m3.store import atomic_json

ROOT = Path(__file__).resolve().parents[1]


def preserve_truth(source, destination):
    """Retain all oracle evidence without thousands of slow cross-filesystem copies."""
    if not source.is_dir() or destination.exists():
        return
    destination.mkdir()
    for name in ("packet_events.csv", "health.json", "ready.json"):
        if (source / name).is_file():
            shutil.copyfile(source / name, destination / name)
    archive = source.parent / "truth_windows.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
        for path in source.glob("*.json"):
            stream.write(path, path.name)
    shutil.copyfile(archive, destination / archive.name)


def block_path(block, directory):
    path = Path(block["path"])
    return path if path.is_absolute() else directory / path


def validate_dataplane(blocks, directory, tx, rx, origin):
    """Match whole-frame multiplicities; never infer correctness from a filename."""
    expected = Counter()
    family_by_frame = {}
    for block in blocks:
        for _, frame in iter_pcap(block_path(block, directory)):
            expected[frame] += 1
            family = block["attack_family"]
            if frame in family_by_frame and family_by_frame[frame] != family:
                raise ValueError("Prepared frame has conflicting class assignments")
            family_by_frame[frame] = family
    observed = {}
    windows = defaultdict(Counter)
    for name, path in (("tx", tx), ("rx", rx)):
        frames = Counter()
        unknown = 0
        for epoch, frame in iter_pcap(path):
            frames[frame] += 1
            family = family_by_frame.get(frame)
            unknown += family is None
            if name == "rx":
                windows[math.floor(epoch - origin)][family or "unknown"] += 1
        observed[name] = {
            "packets": sum(frames.values()),
            "unknown_packets": unknown,
            "matches_expected_multiplicity": frames == expected,
            "sha256": sha256(path),
        }
    valid = all(v["matches_expected_multiplicity"] for v in observed.values())
    return {
        "status": "validated" if valid else "failed",
        "expected_packets": sum(expected.values()),
        "captures": observed,
        "receive_windows": {str(k): dict(v) for k, v in sorted(windows.items())},
        "interpretation": "Actual forwarded full-packet evidence; not model accuracy",
    }


def wait_until(epoch):
    while (remaining := epoch - time.time()) > 0:
        time.sleep(min(remaining, 0.1))


def run(blocks_path, manifest, sampling=1, output_root="output/sdn", *, research=None):
    if sys.platform != "linux" or os.geteuid() != 0:
        raise ValueError("Run as root inside the configured isolated Linux/WSL lab")
    if sampling not in (1, 2, 5, 10, 20, 50):
        raise ValueError("Unsupported sampling setting")
    blocks_path, manifest = Path(blocks_path).resolve(), Path(manifest).resolve()
    provenance = verify_input(blocks_path, manifest)
    if provenance.get("fixture"):
        raise ValueError("Synthetic block fixtures cannot become official live evidence")
    document = json.loads(blocks_path.read_text())
    blocks = document["blocks"]
    if not blocks or len(blocks) > 20:
        raise ValueError("Pilot requires 1-20 bounded prepared blocks")
    directory = blocks_path.parent
    for block in blocks:
        record = verify_input(block_path(block, directory), manifest)
        if record.get("fixture") or not 0 < block["pps"] <= 10000:
            raise ValueError("Unverified fixture or unsafe replay rate")
        if not 1 <= block["packet_count"] <= 100000:
            raise ValueError("Unbounded replay block")

    # Network tools are imported only inside Linux execution, not fixture tests.
    from mininet.net import Mininet
    from mininet.node import OVSSwitch, RemoteController
    from topology import ovs, set_sampling

    output = Path(output_root).resolve() / ("official_pilot_" + uuid.uuid4().hex)
    output.mkdir(parents=True, exist_ok=False)
    native_capture = tempfile.TemporaryDirectory(prefix="m3_official_capture_")
    capture_dir = Path(native_capture.name)
    report = {"status": "running", "blocks_provenance": provenance, "sampling_rate": sampling}
    if research:
        report["research"] = dict(research)
        report["implementation_sha256"] = {
            name: sha256(ROOT / name) for name in (
                "src/m3/model.py", "src/m3/packets.py", "src/m3/engine.py",
                "src/m3/causal_live.py", "src/m3/metrics.py", "sdn/live_ground_truth.py",
                "sdn/research_validation.py")}
        report["environment"] = {"kernel": platform.platform(), "python": sys.version,
                                 "logical_cpus": os.cpu_count(),
                                 "ovs": subprocess.check_output(["ovs-vsctl", "--version"], text=True).splitlines()[0]}
    controller = collector = teacher = net = None
    captures = []
    logs = []
    binaries = Path(sys.executable).parent
    try:
        for port in (6653, 6343):
            with socket.socket(
                socket.AF_INET, socket.SOCK_STREAM if port == 6653 else socket.SOCK_DGRAM
            ) as probe:
                if port == 6653:
                    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                probe.bind(("127.0.0.1", port))
        log = (output / "controller.log").open("w")
        logs.append(log)
        controller = subprocess.Popen(
            [
                str(binaries / "osken-manager"),
                "--ofp-tcp-listen-port",
                "6653",
                str(ROOT / "sdn/controller.py"),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        deadline = time.monotonic() + 60
        while True:
            if controller.poll() is not None:
                raise RuntimeError("Controller startup failed")
            try:
                with socket.create_connection(("127.0.0.1", 6653), timeout=0.3):
                    break
            except OSError:
                if time.monotonic() > deadline:
                    raise RuntimeError("Controller startup timeout")
                time.sleep(0.2)
        ovs("--timeout=5", "--if-exists", "del-br", "m3s1")
        net = Mininet(controller=None, switch=OVSSwitch, autoSetMacs=True, autoStaticArp=True)
        net.addController("m3c0", controller=RemoteController, ip="127.0.0.1", port=6653)
        switch = net.addSwitch("m3s1", protocols="OpenFlow13", datapath="user", failMode="secure")
        hosts = []
        for number, name in enumerate(("m3a1", "m3a2", "m3benign", "m3victim"), 1):
            host = net.addHost(name, ip=f"10.77.0.{number}/24")
            net.addLink(host, switch)
            hosts.append(host)
        net.start()
        for host in hosts:
            host.cmd("sysctl -q -w net.ipv6.conf.all.disable_ipv6=1")
        # Disable only this isolated testbed's root-namespace interfaces. Otherwise
        # Linux router solicitations contaminate the independently captured stream.
        for interface in ["m3s1", *switch.intfNames()]:
            if interface.startswith("m3s1"):
                subprocess.run(
                    ["sysctl", "-q", "-w", f"net.ipv6.conf.{interface}.disable_ipv6=1"],
                    check=True,
                )
        time.sleep(2)
        report["ping_loss_percent"] = net.pingAll(timeout="2")
        if report["ping_loss_percent"]:
            raise RuntimeError("Connectivity failed before measurement")
        time.sleep(1)
        for name, host, interface, direction in (
            ("tx", hosts[0], "m3a1-eth0", "out"),
            ("rx", hosts[3], "m3victim-eth0", "in"),
        ):
            log = (output / f"{name}.log").open("w")
            logs.append(log)
            process = host.popen(
                [
                    "tcpdump",
                    "-B",
                    "16384",
                    "-n",
                    "-s",
                    "0",
                    "-Q",
                    direction,
                    "-i",
                    interface,
                    "-w",
                    str(capture_dir / f"{name}.pcap"),
                ],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            captures.append((name, process))
        time.sleep(1)
        if any(process.poll() is not None for _, process in captures):
            raise RuntimeError("Independent capture startup failed")
        origin = math.ceil(time.time()) + (30 if research else 15)
        offset = 1.0
        stages = []
        for block in blocks:
            duration = block["packet_count"] / block["pps"]
            stages.append({"start": offset, "duration": duration, **block})
            offset += math.ceil(duration) + (2 if research else 4)
        total_duration = math.ceil(offset + 4)
        config = {
            "mode": "live_sflow",
            "sampling_rate": sampling,
            "seed": research["seed"] if research else 42,
            "scenario": research["scenario"] if research else "baseline",
            "output_root": str(ROOT / "output/runs"),
            "bind": "127.0.0.1",
            "port": 6343,
            "start_epoch": origin,
            "duration_seconds": total_duration,
            "warmup_seconds": stages[4]["start"] if research else 0,
            "window_seconds": 0.1 if research else 1,
            "controller_pid": controller.pid,
            "ovs_bridge": "m3s1",
            "openflow_port": 6653,
        }
        if research:
            config.update(input_path=str(blocks_path), manifest_path=str(manifest),
                          trial_id=research["trial_id"], label_delay_seconds=0.5, replay_pps=100)
            log = (output / "teacher.log").open("w")
            logs.append(log)
            teacher = hosts[3].popen(
                [str(binaries / "python"), str(ROOT / "sdn/live_ground_truth.py"),
                 "--blocks", str(blocks_path), "--manifest", str(manifest),
                 "--interface", "m3victim-eth0", "--output", str(capture_dir / "truth"),
                 "--origin", str(origin), "--duration", str(total_duration), "--window", "0.1",
                 "--control", str(capture_dir / "origin.json")],
                stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
            ready_deadline = time.monotonic() + 90
            while not (capture_dir / "truth/ready.json").is_file():
                if teacher.poll() is not None or time.monotonic() > ready_deadline:
                    raise RuntimeError("Independent oracle did not become ready")
                time.sleep(0.1)
            origin = math.ceil(time.time()) + 30
            config["start_epoch"] = origin
            atomic_json(capture_dir / "origin.json", {"origin_epoch": origin})
        atomic_json(output / "collector_config.json", config)
        log = (output / "collector.log").open("w")
        logs.append(log)
        collector_command = (
            [str(binaries / "python"), "-m", "m3.causal_live", "--config",
             str(output / "collector_config.json"), "--truth", str(capture_dir / "truth")]
            if research else
            [str(binaries / "m3"), "live", "--config", str(output / "collector_config.json")]
        )
        collector = subprocess.Popen(
            collector_command,
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=ROOT,
        )
        deadline = origin - 0.5
        while "Collector ready" not in (output / "collector.log").read_text():
            if collector.poll() is not None or time.time() > deadline:
                raise RuntimeError("Collector did not become ready before measurement")
            time.sleep(0.1)
        set_sampling(sampling, "127.0.0.1:6343")
        sampling_before = ovs("get", "sflow", ovs("get", "bridge", "m3s1", "sflow"), "sampling")
        report.update(
            origin_epoch=origin,
            duration_seconds=total_duration,
            stages=stages,
            capture_scope="isolated sender TX and victim RX; no physical uplink",
            evaluation_timing=("real-time prediction followed by independent oracle revelation"
                               if research else "unlabelled live collection; any subsequent scoring is post hoc"),
        )
        for number, stage in enumerate(stages):
            wait_until(origin + stage["start"])
            started = time.time()
            replay = hosts[0].popen(
                [
                    "tcpreplay",
                    "--intf1=m3a1-eth0",
                    f"--pps={stage['pps']}",
                    "--loop=1",
                    str(block_path(stage, directory)),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            try:
                stdout, _ = replay.communicate(timeout=stage["duration"] + 15)
            except subprocess.TimeoutExpired:
                replay.kill()
                replay.communicate()
                raise RuntimeError("Replay exceeded bounded stage duration") from None
            text = stdout.decode(errors="replace")
            (output / f"replay_{number}.log").write_text(text)
            stage.update(
                actual_start_epoch=started,
                actual_end_epoch=time.time(),
                exit_code=replay.returncode,
            )
            emitted = re.search(r"Actual:\s+(\d+) packets", text)
            if replay.returncode or not emitted or int(emitted[1]) != stage["packet_count"]:
                raise RuntimeError("Replay failed or emitted a different packet count")
            atomic_json(output / "execution.json", report)
        collector.wait(timeout=max(1, origin + total_duration - time.time()) + 20)
        if collector.returncode:
            raise RuntimeError("Live collector failed; raw evidence retained")
        if teacher:
            teacher.wait(timeout=10)
            if teacher.returncode:
                raise RuntimeError("Independent oracle failed")
            preserve_truth(capture_dir / "truth", output / "truth")
        for _, process in captures:
            process.send_signal(signal.SIGINT)
            process.wait(timeout=10)
        for name, _ in captures:
            shutil.copyfile(capture_dir / f"{name}.pcap", output / f"{name}.pcap")
        for name, _ in captures:
            text = (output / f"{name}.log").read_text()
            dropped = re.search(r"(\d+) packets dropped by kernel", text)
            if dropped is None or int(dropped[1]) != 0:
                raise RuntimeError("Independent capture drop count is unavailable or nonzero")
        report["dataplane_validation"] = validate_dataplane(
            blocks, directory, output / "tx.pcap", output / "rx.pcap", origin
        )
        if report["dataplane_validation"]["status"] != "validated":
            raise RuntimeError("TX/RX packet evidence does not match prepared block multiplicities")
        match = re.search(r"run=([0-9a-f]{32})", (output / "collector.log").read_text())
        if not match:
            raise RuntimeError("Collector run identity missing")
        report.update(status="validated_collection", collector_run_id=match[1])
        if research:
            sampling_after = ovs("get", "sflow", ovs("get", "bridge", "m3s1", "sflow"), "sampling")
            if sampling_before != str(sampling) or sampling_after != str(sampling):
                raise RuntimeError("Actual switch sampling configuration changed")
            report["switch_sampling"] = {"before": int(sampling_before), "after": int(sampling_after)}
            from research_validation import accept_realtime

            report["research"] = research
            accept_realtime(ROOT / "output/runs" / match[1], output, report)
            report["status"] = "validated_realtime"
    except BaseException as error:
        report.update(status="failed", error=str(error))
        collector_log = output / "collector.log"
        identity = re.search(r"run=([0-9a-f]{32})", collector_log.read_text()) if collector_log.is_file() else None
        if identity:
            summary_path = ROOT / "output/runs" / identity[1] / "run_summary.json"
            if summary_path.is_file():
                failed = json.loads(summary_path.read_text())
                failed.update(status="failed", error=str(error), validation={"accepted": False})
                atomic_json(summary_path, failed)
        raise
    finally:
        for _, process in captures:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                process.wait(timeout=10)
        for process in (collector, teacher, controller):
            if process and process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
        if net:
            net.stop()
        for log in logs:
            log.close()
        for source in capture_dir.glob("*.pcap"):
            destination = output / source.name
            if not destination.exists():
                shutil.copyfile(source, destination)
        if (capture_dir / "truth").is_dir() and not (output / "truth").exists():
            preserve_truth(capture_dir / "truth", output / "truth")
        native_capture.cleanup()
        atomic_json(output / "execution.json", report)
        print(
            json.dumps(
                {"status": report["status"], "evidence": str(output), "error": report.get("error")}
            ),
            flush=True,
        )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blocks", required=True)
    parser.add_argument("--manifest", default="data/manifest.json")
    parser.add_argument("--sampling", type=int, default=1)
    parser.add_argument("--output-root", default="output/sdn")
    parser.add_argument("--research-scenario", choices=["baseline", "drift", "unseen"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trial-id", type=int, default=1)
    args = parser.parse_args()
    research = ({"scenario": args.research_scenario, "seed": args.seed, "trial_id": args.trial_id,
                 "study_role": "validation_pilot"}
                if args.research_scenario else None)
    run(args.blocks, args.manifest, args.sampling, args.output_root, research=research)
