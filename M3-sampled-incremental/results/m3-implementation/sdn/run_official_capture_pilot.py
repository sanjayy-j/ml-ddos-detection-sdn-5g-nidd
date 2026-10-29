"""Collect genuine switch exports plus independent TX/RX evidence for prepared blocks.

This stage does not claim real-time detection accuracy. Collection is unlabelled;
validated recorded exports can subsequently be scored explicitly post hoc.
"""

import argparse
import hashlib
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
SPOOL_PREFIX = "m3_official_capture_"


def archive_truth_windows(source):
    """Zip oracle JSON locally and verify each member against its original bytes."""
    if not source.is_dir():
        return {}
    if source.is_symlink():
        raise ValueError("Native oracle evidence must not follow symlinks")
    paths = sorted(source.glob("*.json"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Native oracle evidence must not contain symlinks")
    if not paths:
        return {}
    archive = source / "truth_windows.zip"
    if archive.is_symlink():
        raise ValueError("Native oracle archive must not follow symlinks")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
        for path in paths:
            stream.write(path, path.name)
    verified = {}
    with zipfile.ZipFile(archive) as stream:
        if len(stream.namelist()) != len(paths):
            raise OSError("Oracle archive member count does not match source files")
        for path in paths:
            member = stream.read(path.name)
            if member != path.read_bytes():
                raise OSError(f"Oracle archive verification failed: {path}")
            verified[path] = hashlib.sha256(member).hexdigest()
    return verified


def preserve_native_spool(source, output, runs_root):
    """Verify every native file before rebasing durable collector summaries.

    The caller owns cleanup. Any failure leaves the complete native spool intact.
    Runtime config.output_root stays unchanged as execution provenance.
    """
    source = Path(source)
    if not source.is_dir() or source.is_symlink():
        raise ValueError("Native evidence spool must be a real directory")
    source, output, runs_root = (Path(path).resolve() for path in (source, output, runs_root))
    if any(path == source or source in path.parents for path in (output, runs_root)):
        raise ValueError("Durable evidence must be outside the native spool")
    archived_truth = archive_truth_windows(source / "truth")
    archived_windows = 0
    files = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError("Native evidence must not contain symlinks")
        if path.is_file():
            relative = path.relative_to(source)
            if (relative.parent == Path("truth") and re.fullmatch(r"\d+\.json", path.name)
                    and path in archived_truth):
                archived_windows += 1
                continue
            destination = (runs_root.joinpath(*relative.parts[1:])
                           if relative.parts[0] == "collector_runs" else output / relative)
            if destination.is_symlink() or any(p.is_symlink() for p in destination.parents):
                raise ValueError("Durable evidence must not follow symlinks")
            destination.parent.mkdir(parents=True, exist_ok=True)
            digest = sha256(path)
            shutil.copyfile(path, destination)
            if path.stat().st_size != destination.stat().st_size or sha256(destination) != digest:
                raise OSError(f"Evidence copy verification failed: {path}")
            files.append((path, destination, digest))
    # Recheck the source after copying: no active writer may race archival.
    if any(sha256(path) != digest for path, _, digest in files):
        raise OSError("Native evidence changed during preservation")
    if any(sha256(path) != digest for path, digest in archived_truth.items()):
        raise OSError("Native oracle evidence changed after archive verification")
    metadata = {"runtime_output_root": str(source / "collector_runs"),
                "durable_output_root": str(runs_root), "native_spool": str(source),
                "preservation": "byte_verified", "verified_files": len(files) + archived_windows,
                "archived_truth_windows": archived_windows}

    def rebase(value):
        if isinstance(value, dict):
            return {key: rebase(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rebase(item) for item in value]
        if isinstance(value, str):
            path = Path(value)
            if path.is_absolute():
                try:
                    return str(runs_root / path.relative_to(source / "collector_runs"))
                except ValueError:
                    pass
        return value

    for original, destination, digest in files:
        if original.name == "run_summary.json" and original.is_relative_to(source / "collector_runs"):
            summary = json.loads(destination.read_text(encoding="utf-8"))
            if "artifacts" in summary:
                summary["artifacts"] = rebase(summary["artifacts"])
            summary["storage"] = {**metadata, "runtime_summary_sha256": digest,
                                  "durable_run_directory": str(destination.parent)}
            atomic_json(destination, summary)
    return metadata


def cleanup_native_spool(source, temp_root=None):
    """Remove only an owned direct child of the configured temporary directory."""
    source = Path(source)
    root = Path(temp_root if temp_root is not None else tempfile.gettempdir()).resolve()
    resolved = source.resolve()
    if (source.is_symlink() or resolved.parent != root
            or not resolved.name.startswith(SPOOL_PREFIX)
            or resolved.name == SPOOL_PREFIX):
        raise ValueError("Refusing cleanup outside an owned native temporary spool")
    shutil.rmtree(resolved)


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


def run(blocks_path, manifest, sampling=1, output_root="output/sdn", *, research=None,
        runs_root=None):
    if sys.platform != "linux" or os.geteuid() != 0:
        raise ValueError("Run as root inside the configured isolated Linux/WSL lab")
    if sampling not in (1, 2, 5, 10, 20, 50):
        raise ValueError("Unsupported sampling setting")
    blocks_path, manifest = Path(blocks_path).resolve(), Path(manifest).resolve()
    runs_root = Path(runs_root).resolve() if runs_root is not None else ROOT / "output/runs"
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
    capture_dir = Path(tempfile.mkdtemp(prefix=SPOOL_PREFIX)).resolve()
    native_runs = capture_dir / "collector_runs"
    report = {"status": "running", "blocks_provenance": provenance, "sampling_rate": sampling,
              "collector_output_root": str(runs_root),
              "storage": {"native_spool": str(capture_dir),
                          "runtime_output_root": str(native_runs),
                          "durable_output_root": str(runs_root)}}
    if research:
        report["research"] = dict(research)
        report["implementation_sha256"] = {
            name: sha256(ROOT / name) for name in (
                "src/m3/model.py", "src/m3/naive_bayes.py", "src/m3/config.py",
                "src/m3/packets.py", "src/m3/engine.py", "src/m3/ingestion.py",
                "src/m3/causal_live.py", "src/m3/metrics.py", "sdn/live_ground_truth.py",
                "sdn/research_validation.py")}
        report["environment"] = {"kernel": platform.platform(), "python": sys.version,
                                 "logical_cpus": os.cpu_count(),
                                 "ovs": subprocess.check_output(["ovs-vsctl", "--version"], text=True).splitlines()[0]}
    controller = collector = teacher = net = None
    captures = []
    logs = []
    preserved = False
    preservation_attempted = False
    stopped = False
    binaries = Path(sys.executable).parent

    def stop_runtime():
        nonlocal stopped
        if stopped:
            return
        errors = []
        for process, capture in ([(process, True) for _, process in captures]
                                 + [(process, False) for process in (collector, teacher, controller)]):
            try:
                if process and process.poll() is None:
                    process.send_signal(signal.SIGINT) if capture else process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=10)
            except BaseException as error:  # noqa: BLE001 -- Finish stopping other evidence writers.
                errors.append(error)
        try:
            if net:
                net.stop()
        except BaseException as error:  # noqa: BLE001 -- Preserve files even if network cleanup fails.
            errors.append(error)
        for log in logs:
            log.close()
        stopped = not errors
        if errors:
            raise RuntimeError("Could not stop every measurement process") from errors[0]

    try:
        for port in (6653, 6343):
            with socket.socket(
                socket.AF_INET, socket.SOCK_STREAM if port == 6653 else socket.SOCK_DGRAM
            ) as probe:
                if port == 6653:
                    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                probe.bind(("127.0.0.1", port))
        log = (capture_dir / "controller.log").open("w")
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
            log = (capture_dir / f"{name}.log").open("w")
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
        # Independently retain every exporter UDP datagram, including packets the
        # collector has not read when its bounded measurement interval ends.
        log = (capture_dir / "sflow_rx.log").open("w")
        logs.append(log)
        process = subprocess.Popen(
            ["tcpdump", "--interface", "lo", "-B", "16384", "-n", "-U", "-s", "262144",
             "-w", str(capture_dir / "sflow_rx.pcap"), "udp dst port 6343"],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        captures.append(("sflow_rx", process))
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
            "output_root": str(native_runs),
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
                          trial_id=research["trial_id"], label_delay_seconds=0.5, replay_pps=100,
                          naive_bayes=research.get("naive_bayes", "log_space"),
                          telemetry_clock=research.get("telemetry_clock", "kernel_receive"))
            log = (capture_dir / "teacher.log").open("w")
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
        atomic_json(capture_dir / "collector_config.json", config)
        log = (capture_dir / "collector.log").open("w")
        logs.append(log)
        collector_command = (
            [str(binaries / "python"), "-m", "m3.causal_live", "--config",
             str(capture_dir / "collector_config.json"), "--truth", str(capture_dir / "truth")]
            if research else
            [str(binaries / "m3"), "live", "--config", str(capture_dir / "collector_config.json")]
        )
        collector = subprocess.Popen(
            collector_command,
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=ROOT,
        )
        deadline = origin - 0.5
        while "Collector ready" not in (capture_dir / "collector.log").read_text():
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
            (capture_dir / f"replay_{number}.log").write_text(text)
            stage.update(
                actual_start_epoch=started,
                actual_end_epoch=time.time(),
                exit_code=replay.returncode,
            )
            emitted = re.search(r"Actual:\s+(\d+) packets", text)
            if replay.returncode or not emitted or int(emitted[1]) != stage["packet_count"]:
                raise RuntimeError("Replay failed or emitted a different packet count")
            atomic_json(capture_dir / "execution.json", report)
        collector.wait(timeout=max(1, origin + total_duration - time.time()) + 20)
        if collector.returncode:
            raise RuntimeError("Live collector failed; raw evidence retained")
        if teacher:
            teacher.wait(timeout=10)
            if teacher.returncode:
                raise RuntimeError("Independent oracle failed")
        for _, process in captures:
            process.send_signal(signal.SIGINT)
            process.wait(timeout=10)
        for name, _ in captures:
            text = (capture_dir / f"{name}.log").read_text()
            dropped = re.search(r"(\d+) packets dropped by kernel", text)
            if dropped is None or int(dropped[1]) != 0:
                raise RuntimeError("Independent capture drop count is unavailable or nonzero")
        report["dataplane_validation"] = validate_dataplane(
            blocks, directory, capture_dir / "tx.pcap", capture_dir / "rx.pcap", origin
        )
        if report["dataplane_validation"]["status"] != "validated":
            raise RuntimeError("TX/RX packet evidence does not match prepared block multiplicities")
        match = re.search(r"run=([0-9a-f]{32})", (capture_dir / "collector.log").read_text())
        if not match:
            raise RuntimeError("Collector run identity missing")
        report.update(status="validated_collection", collector_run_id=match[1])
        if research:
            sampling_after = ovs("get", "sflow", ovs("get", "bridge", "m3s1", "sflow"), "sampling")
            if sampling_before != str(sampling) or sampling_after != str(sampling):
                raise RuntimeError("Actual switch sampling configuration changed")
            report["switch_sampling"] = {"before": int(sampling_before), "after": int(sampling_after)}
        stop_runtime()
        preservation_attempted = True
        report["storage"] = preserve_native_spool(capture_dir, output, runs_root)
        preserved = True
        if research:
            from research_validation import accept_realtime

            report["research"] = research
            accept_realtime(runs_root / match[1], output, report)
            report["status"] = "validated_realtime"
    except BaseException as error:
        report.update(status="failed", error=str(error))
        raise
    finally:
        try:
            stop_runtime()
        except BaseException as error:  # noqa: BLE001 -- Retain evidence after interrupted shutdown.
            report.update(status="failed", shutdown_error=str(error))
        # Never race a running collector while invalidating a failed trial.
        if report["status"] == "failed" and stopped:
            summary_paths = ([runs_root / report["collector_run_id"] / "run_summary.json"]
                             if preserved and report.get("collector_run_id")
                             else native_runs.glob("*/run_summary.json"))
            for summary_path in summary_paths:
                try:
                    failed = json.loads(summary_path.read_text(encoding="utf-8"))
                    failed.update(status="failed", error=report.get("error", report.get("shutdown_error")),
                                  validation={"accepted": False})
                    atomic_json(summary_path, failed)
                except (OSError, ValueError) as error:
                    report["storage"]["summary_update_error"] = str(error)
        try:
            if not preserved and not preservation_attempted:
                preservation_attempted = True
                report["storage"] = preserve_native_spool(capture_dir, output, runs_root)
                preserved = True
            if preserved and stopped:
                # Persist the final report before deleting its only native recovery copy.
                atomic_json(output / "execution.json", report)
                cleanup_native_spool(capture_dir)
            else:
                raise RuntimeError("Native preservation or measurement process shutdown is incomplete")
        except BaseException as error:  # noqa: BLE001 -- Never delete unpreserved evidence.
            report.update(status="failed")
            report["storage"].update(preservation_error=str(error), recovery_path=str(capture_dir))
            try:
                atomic_json(capture_dir / "execution.json", report)
            except OSError:
                pass
            try:
                atomic_json(output / "execution.json", report)
            except OSError:
                pass
        print(
            json.dumps(
                {"status": report["status"], "evidence": str(output), "error": report.get("error"),
                 "recovery_path": report.get("storage", {}).get("recovery_path")}
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
    parser.add_argument("--runs-output", help="Separate collector results directory for this study")
    parser.add_argument("--naive-bayes", choices=["river", "log_space"], default="log_space")
    parser.add_argument("--telemetry-clock", choices=["userspace", "kernel_receive"],
                        default="kernel_receive")
    parser.add_argument("--research-scenario", choices=["baseline", "drift", "unseen"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trial-id", type=int, default=1)
    args = parser.parse_args()
    research = ({"scenario": args.research_scenario, "seed": args.seed, "trial_id": args.trial_id,
                 "study_role": "validation_pilot", "naive_bayes": args.naive_bayes,
                 "telemetry_clock": args.telemetry_clock}
                if args.research_scenario else None)
    run(args.blocks, args.manifest, args.sampling, args.output_root, research=research,
        runs_root=args.runs_output)
