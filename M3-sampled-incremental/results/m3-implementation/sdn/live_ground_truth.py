"""Linux victim-namespace oracle: kernel RX timestamps, full frames, no prediction access."""

import argparse
import csv
import hashlib
import json
import math
import socket
import struct
import time
from collections import defaultdict
from pathlib import Path

from m3.live_supervision import FrameLabels, restore_vlan, truth_payload
from m3.packets import iter_pcap
from m3.provenance import verify_input
from m3.store import atomic_json


def run(blocks_path, manifest, interface, output, origin, duration, window, control=None):
    blocks_path, output = Path(blocks_path), Path(output)
    verify_input(blocks_path, manifest)
    blocks = json.loads(blocks_path.read_text())["blocks"]
    pairs = []
    for block in blocks:
        path = Path(block["path"])
        if not path.is_absolute():
            path = blocks_path.parent / path
        verify_input(path, manifest)
        pairs.extend((frame, block["attack_family"]) for _, frame in iter_pcap(path))
    labels = FrameLabels(pairs)
    output.mkdir(parents=True, exist_ok=False)
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)
    timestamp_option = getattr(socket, "SO_TIMESTAMPNS", 35)
    sock.setsockopt(socket.SOL_SOCKET, timestamp_option, 1)
    sock.setsockopt(socket.SOL_SOCKET, 40, 1)  # Linux SO_RXQ_OVFL.
    sock.setsockopt(263, 8, 1)  # SOL_PACKET / PACKET_AUXDATA, including stripped VLANs.
    sock.bind((interface, 0))
    sock.settimeout(0.01)
    pending = defaultdict(list)
    next_window = 0
    count = unknown = drops = late = 0
    total = math.ceil(duration / window)
    atomic_json(output / "ready.json", {"ready_epoch": time.time()})
    if control:
        deadline = time.monotonic() + 90
        while not Path(control).is_file():
            if time.monotonic() > deadline:
                raise RuntimeError("Trial origin handshake unavailable")
            time.sleep(0.02)
        origin = json.loads(Path(control).read_text())["origin_epoch"]
        if origin <= time.time():
            raise RuntimeError("Trial origin must follow oracle readiness")
    try:
        with (output / "packet_events.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["epoch", "label", "attack_family", "frame_sha256"])
            writer.writeheader()
            while time.time() < origin + duration + 1:
                try:
                    frame, ancillary, _, address = sock.recvmsg(262144, 256)
                except TimeoutError:
                    frame = None
                if frame is not None and address[2] != 4:  # PACKET_OUTGOING excluded.
                    epoch = None
                    for level, kind, payload in ancillary:
                        if level == socket.SOL_SOCKET and kind == timestamp_option:
                            seconds, nanos = struct.unpack("@ll", payload[:struct.calcsize("@ll")])
                            epoch = seconds + nanos / 1e9
                        elif level == socket.SOL_SOCKET and kind == 40:
                            drops = max(drops, struct.unpack("I", payload[:4])[0])
                        elif level == 263 and kind == 8:
                            frame = restore_vlan(frame, payload)
                    if epoch is None:
                        raise RuntimeError("Independent kernel receive timestamp missing")
                    if origin <= epoch < origin + duration:
                        family = labels.match(frame)
                        label = None if family is None else int(family != "Benign")
                        index = math.floor((epoch - origin) / window)
                        late += index < next_window
                        pending[index].append(family)
                        writer.writerow({"epoch": epoch, "label": label, "attack_family": family,
                                         "frame_sha256": hashlib.sha256(frame).hexdigest()})
                        stream.flush()
                        count += 1
                        unknown += family is None
                # Publish after a fixed 150ms settling interval, independent of class/model.
                while next_window < total and time.time() >= origin + (next_window + 1) * window + 0.15:
                    truth = truth_payload(pending.pop(next_window, []),
                                          origin + next_window * window,
                                          origin + (next_window + 1) * window)
                    truth["available_epoch"] = time.time()
                    atomic_json(output / f"{next_window}.json", truth)
                    next_window += 1
    finally:
        sock.close()
        atomic_json(output / "health.json", {"packets": count, "unknown": unknown,
                    "kernel_drops": drops, "late_packets": late, "windows": next_window})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("blocks", "manifest", "interface", "output"):
        parser.add_argument("--" + key, required=True)
    for key in ("origin", "duration", "window"):
        parser.add_argument("--" + key, required=True, type=float)
    parser.add_argument("--control")
    args = parser.parse_args()
    run(args.blocks, args.manifest, args.interface, args.output, args.origin, args.duration, args.window, args.control)
