"""Prepare bounded, source-labelled official-packet blocks for controlled replay.

Only Ethernet MAC addresses and packet timing change. This is constructed traffic,
not a natural chronological scenario. Reused source selections are disclosed.
"""

import argparse
import csv
import json
import math
from pathlib import Path

import dpkt

from m3.ground_truth import FlowLabels
from m3.packets import iter_pcap
from m3.provenance import sha256, verify_input
from m3.store import atomic_json

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {"Benign", "UDPFlood", "SYNFlood", "ICMPFlood"}
MAC_PREFIX = bytes.fromhex("000000000004000000000001")


def prepare_blocks(plan, output_dir, manifest_path="data/manifest.json"):
    segments = plan.get("segments", [])
    if not segments or len(segments) > 20:
        raise ValueError("Plan requires 1-20 bounded segments")
    output_dir, manifest_path = Path(output_dir).resolve(), Path(manifest_path).resolve()
    if output_dir.exists() or not output_dir.is_relative_to(ROOT / "data/prepared"):
        raise ValueError("Use a new output directory under data/prepared")
    for segment in segments:
        count, rate = segment["packet_count"], segment["pps"]
        if segment["family"] not in FAMILIES or type(count) is not int or not 1 <= count <= 100000:
            raise ValueError("Invalid block family or packet count")
        if isinstance(rate, bool) or not math.isfinite(rate) or not 0 < rate <= 10000:
            raise ValueError("Invalid bounded replay rate")
    parents = []
    for segment in segments:
        parents.append(
            (
                verify_input(segment["capture"], manifest_path),
                verify_input(segment["flow_labels"], manifest_path),
            )
        )
    output_dir.mkdir(parents=True, exist_ok=False)
    entries, blocks = [], []

    def register(path, sources):
        entries.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
                "verification_status": "verified",
                "parent_sha256s": sorted({source["sha256"] for source in sources}),
                "fixture": any(source.get("fixture") for source in sources),
                "transformations": [
                    "Select only exact original FlowLabels family matches; unknowns excluded",
                    "Rewrite Ethernet destination/source MAC only; bytes from offset14 unchanged",
                    "Construct packet timestamps as selection_index/pps; not natural chronology",
                    "Repeated blocks may reuse first eligible source packets; not independent data",
                ],
            }
        )

    try:
        for number, (segment, sources) in enumerate(zip(segments, parents, strict=True)):
            family = segment["family"]
            labels = FlowLabels(segment["flow_labels"])
            target = output_dir / f"block_{number:02d}.pcap"
            partial = target.with_suffix(".pcap.partial")
            mapping = output_dir / f"block_{number:02d}_mapping.csv"
            selected, examined = 0, 0
            with partial.open("xb") as output, mapping.open("x", newline="") as map_stream:
                writer = dpkt.pcap.Writer(output, snaplen=262144)
                map_writer = csv.writer(map_stream)
                map_writer.writerow(
                    [
                        "source_packet_index",
                        "source_epoch",
                        "label",
                        "attack_family",
                        "selection_index",
                        "original_sha256",
                        "rewritten_sha256",
                    ]
                )
                import hashlib

                for packet_index, (timestamp, frame) in enumerate(iter_pcap(segment["capture"])):
                    examined += 1
                    label, actual_family = labels.match(frame, timestamp)
                    if actual_family != family or label != int(family != "Benign"):
                        continue
                    rewritten = MAC_PREFIX + frame[12:]
                    writer.writepkt(rewritten, selected / segment["pps"])
                    map_writer.writerow(
                        [
                            packet_index,
                            repr(timestamp),
                            label,
                            family,
                            selected,
                            hashlib.sha256(frame).hexdigest(),
                            hashlib.sha256(rewritten).hexdigest(),
                        ]
                    )
                    selected += 1
                    if selected == segment["packet_count"]:
                        break
            if selected != segment["packet_count"]:
                raise ValueError(
                    f"Insufficient known {family} packets: {selected}/{segment['packet_count']}; partial retained"
                )
            partial.rename(target)
            register(target, sources)
            register(mapping, sources)
            blocks.append(
                {
                    "path": target.name,
                    "mapping": mapping.name,
                    "label": int(family != "Benign"),
                    "attack_family": family,
                    "packet_count": selected,
                    "pps": segment["pps"],
                    "source_packets_examined": examined,
                    "source_provenance": list(sources),
                }
            )
        document = {
            "schema": "controlled-official-replay-blocks-v1",
            "status": "prepared",
            "blocks": blocks,
            "plan": plan,
            "selection_policy": "First N exact-family original packets per block; repeated selections reuse source packets",
            "timing": "Constructed index/pps, not natural capture chronology",
            "fixture": any(source.get("fixture") for pair in parents for source in pair),
        }
        atomic_json(output_dir / "blocks.json", document)
        register(output_dir / "blocks.json", [source for pair in parents for source in pair])
        latest = json.loads(manifest_path.read_text())
        by_path = {entry["path"]: entry for entry in latest["files"]}
        by_path.update({entry["path"]: entry for entry in entries})
        latest["files"] = list(by_path.values())
        atomic_json(manifest_path, latest)
        return document
    except Exception as error:
        atomic_json(
            output_dir / "failed.json",
            {"status": "failed", "error": str(error), "registered": False},
        )
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", default="data/manifest.json")
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text())
    for segment in plan.get("segments", []):
        for key in ("capture", "flow_labels"):
            if verify_input(segment[key], args.manifest).get("fixture"):
                parser.error("Synthetic fixtures cannot become production replay blocks")
    result = prepare_blocks(plan, args.output_dir, args.manifest)
    print(
        json.dumps(
            {"status": result["status"], "blocks": len(result["blocks"]), "output": args.output_dir}
        )
    )
