"""Freeze controlled scenarios with disjoint source indices and rate-matched classes.

The scenarios are constructed packet selections, not natural capture chronology.
Identical frozen traffic is repeated across trials, not independent datasets.
"""

import argparse
import importlib.util
import json
from pathlib import Path

from m3.provenance import sha256, verify_input
from m3.store import atomic_json

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_ROOT = "data/raw/BS2 GTP removed/BS2 GTP removed"
SOURCES = {
    "Benign": ("SYNflood_BS2_nogtp.pcapng", "BS2_SYNFlood_flow_labels.csv"),
    "SYNFlood": ("SYNflood_BS2_nogtp.pcapng", "BS2_SYNFlood_flow_labels.csv"),
    "UDPFlood": ("UDPflood_BS2_nogtp.pcapng", "BS2_UDPFlood_flow_labels.csv"),
    "ICMPFlood": ("ICMPflood_BS2_nogtp.pcapng", "BS2_ICMPFlood_flow_labels.csv"),
}


def build_plans(protocol):
    """Allocate nonoverlapping eligible-packet intervals before examining outcomes."""
    positions, plans = {}, {}
    for scenario in ("baseline", "drift", "unseen"):
        definition = protocol["scenarios"][scenario]
        segments = []
        for block in definition["blocks"]:
            family, count = block["family"], block["packet_count"]
            rate = block.get("pps", protocol["primary_pps"])
            if rate != protocol["primary_pps"]:
                raise ValueError("Every family must use the same primary rate")
            if family not in SOURCES or type(count) is not int or count <= 0:
                raise ValueError("Invalid declared family/count")
            capture, labels = SOURCES[family]
            key = (capture, family)
            skip = positions.get(key, 0)
            segments.append(
                {
                    "capture": f"{CAPTURE_ROOT}/{capture}",
                    "flow_labels": f"data/prepared/{labels}",
                    "family": family,
                    "packet_count": count,
                    "pps": rate,
                    "skip_matching": skip,
                }
            )
            positions[key] = skip + count
        warmup = definition["warmup_blocks"]
        if type(warmup) is not int or not 0 < warmup < len(segments):
            raise ValueError("Invalid warm-up block boundary")
        if scenario == "unseen" and any(
            segment["family"] == "SYNFlood" for segment in segments[:warmup]
        ):
            raise ValueError("Unseen SYN attack must be absent throughout warm-up")
        plans[scenario] = {
            "purpose": definition["purpose"],
            "scenario": scenario,
            "require_disjoint_source_packets": True,
            "warmup_blocks": warmup,
            "gap_seconds": protocol["gap_seconds"],
            "drift_before_block": definition.get("drift_before_block"),
            "reuse": "No source-index reuse within/across scenarios; same frozen inputs across trials",
            "chronology": "Constructed segments, not natural original chronology",
            "segments": segments,
        }
    return plans


def prepare_scenarios(protocol_path, output_dir, manifest_path):
    """Prepare once, or verify an existing identical frozen preparation."""
    protocol_path, output_dir = Path(protocol_path), Path(output_dir).resolve()
    manifest_path = Path(manifest_path)
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    plans = build_plans(protocol)
    verified = set()
    for plan in plans.values():
        for segment in plan["segments"]:
            for field in ("capture", "flow_labels"):
                path = segment[field]
                if path in verified:
                    continue
                if verify_input(path, manifest_path).get("fixture"):
                    raise ValueError("Synthetic fixtures cannot become research evidence")
                verified.add(path)
    if not output_dir.is_relative_to(ROOT / "data/prepared"):
        raise ValueError("Research preparation must stay under data/prepared")
    protocol_hash = sha256(protocol_path)
    index_path = output_dir / "scenarios.json"
    if output_dir.exists():
        saved = json.loads(index_path.read_text(encoding="utf-8"))
        if saved["protocol_sha256"] != protocol_hash:
            raise ValueError("Existing preparation uses a different protocol; never overwrite it")
        for name, item in saved["scenarios"].items():
            blocks_path = output_dir / item["blocks"]
            verify_input(blocks_path, manifest_path)
            blocks = json.loads(blocks_path.read_text())
            if blocks["plan"] != plans[name]:
                raise ValueError("Existing frozen blocks do not match declared protocol")
            for block in blocks["blocks"]:
                for field in ("path", "mapping"):
                    verify_input(blocks_path.parent / block[field], manifest_path)
        return saved
    output_dir.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location(
        "research_prepare_blocks", ROOT / "sdn/prepare_replay_blocks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prepared = {}
    for scenario, plan in plans.items():
        result = module.prepare_blocks(plan, output_dir / scenario, manifest_path)
        prepared[scenario] = {
            "blocks": f"{scenario}/blocks.json",
            "warmup_blocks": plan["warmup_blocks"],
            "drift_before_block": plan["drift_before_block"],
            "packet_count": sum(block["packet_count"] for block in result["blocks"]),
            "active_seconds": sum(
                block["packet_count"] / block["pps"] for block in result["blocks"]
            ),
        }
    document = {
        "schema": "controlled-research-scenarios-v1",
        "status": "prepared",
        "protocol_sha256": protocol_hash,
        "scenarios": prepared,
        "source_index_reuse": "None within or across scenarios; repeated trials reuse frozen inputs",
        "limitations": "Matched subset, constructed chronology, equal replay rates; natural duplicate payloads remain possible",
    }
    atomic_json(index_path, document)
    return document


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default="configs/research_protocol.json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", default="data/manifest.json")
    args = parser.parse_args()
    print(json.dumps(prepare_scenarios(args.protocol, args.output_dir, args.manifest), indent=2))
