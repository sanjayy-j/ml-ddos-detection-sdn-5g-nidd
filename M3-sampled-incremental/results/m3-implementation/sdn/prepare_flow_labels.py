"""Strictly join official per-session labels to Argus numeric/time exports.

Run inside Ubuntu with argus-client installed. Any mismatch prevents a verified
manifest entry; raw `ra` output is retained for investigation.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    "start_epoch",
    "end_epoch",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "protocol",
    "label",
    "attack_family",
    "offset",
]
EXPORT = [
    "stime",
    "ltime",
    "saddr",
    "daddr",
    "sport",
    "dport",
    "proto",
    "seq",
    "dur",
    "offset",
    "pkts",
    "bytes",
]
FLOODS = {"UDPFlood", "SYNFlood", "ICMPFlood"}


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verify_source(path, manifest):
    relative = path.resolve().relative_to(ROOT).as_posix()
    matches = [
        item
        for item in manifest["files"]
        if item["path"] == relative and item["sha256"] == sha(path)
    ]
    if len(matches) != 1:
        raise ValueError(f"Official source checksum not verified: {path}")
    return matches[0]["sha256"]


def time_match(display, epoch):
    try:
        minute, second = display.strip().split(":")
        expected = int(minute) * 60 + float(second)
        observed = float(epoch) % 3600
        distance = abs(expected - observed)
        return min(distance, 3600 - distance) <= 0.11
    except ValueError:
        return False


def prepare(family, manifest):
    csv_path = ROOT / "data/raw/BS2_each_attack_csv/BS2_each_attack_csv" / f"{family}2.csv"
    argus_path = ROOT / "data/raw/BS2_each_attack_argus/BS2_each_attack_argus" / f"{family}2.argus"
    parents = [verify_source(csv_path, manifest), verify_source(argus_path, manifest)]
    prepared = ROOT / "data/prepared"
    prepared.mkdir(parents=True, exist_ok=True)
    raw_output = prepared / f"BS2_{family}_ra_numeric.csv"
    command = ["ra", "-n", "-u", "-r", str(argus_path), "-c", ",", "-s", *EXPORT]
    # Argus performs small per-record reads/writes. Native temporary files avoid
    # hundreds of thousands of slow DrvFS operations on a Windows project mount.
    with tempfile.TemporaryDirectory(prefix="m3_argus_") as temporary:
        native_input = Path(temporary) / argus_path.name
        native_output = Path(temporary) / "numeric.csv"
        shutil.copyfile(argus_path, native_input)
        runtime_command = [*command]
        runtime_command[runtime_command.index("-r") + 1] = str(native_input)
        with native_output.open("w") as output:
            subprocess.run(runtime_command, stdout=output, check=True)
        shutil.copyfile(native_output, raw_output)
    labels = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            offset = int(row["Offset"])
            if offset in labels:
                raise ValueError(f"Repeated CSV Offset {offset}")
            labels[offset] = row
    result_path = prepared / f"BS2_{family}_flow_labels.csv"
    partial = result_path.with_suffix(f".csv.partial.{os.getpid()}")
    seen = set()
    management_records = 0
    contradictions = []
    with raw_output.open(newline="") as source, partial.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        for row in csv.DictReader(source):
            if row["Proto"].strip() == "man":
                management_records += 1
                continue
            offset = int(row["Offset"])
            if offset in seen or offset not in labels:
                raise ValueError(f"Repeated or absent Argus Offset {offset}")
            seen.add(offset)
            label_row = labels[offset]
            for field in ("SrcAddr", "DstAddr", "Proto", "TotPkts", "TotBytes"):
                if row[field].strip() != label_row[field].strip():
                    contradictions.append(
                        f"Offset {offset}: {field}: Argus {row[field]} != CSV {label_row[field]}"
                    )
            if abs(float(row["Dur"]) - float(label_row["Dur"])) > 0.00001:
                contradictions.append(f"Offset {offset}: Dur mismatch")
            if not time_match(label_row["StartTime"], row["StartTime"]) or not time_match(
                label_row["LastTime"], row["LastTime"]
            ):
                contradictions.append(f"Offset {offset}: displayed timestamp mismatch")
            attack = label_row["Attack Type"].strip()
            original = label_row["Label"].strip()
            if attack == "Benign" and original == "Benign":
                label = 0
            elif attack in FLOODS and original in ("Malicious", attack):
                label = 1
            else:
                raise ValueError(f"Unexpected label pair {original}/{attack} in session {family}")
            proto = row["Proto"].strip()
            src_port, dst_port = row["Sport"].strip(), row["Dport"].strip()
            if proto not in ("tcp", "udp"):
                src_port = dst_port = ""
            elif (src_port and not src_port.isdecimal()) or (dst_port and not dst_port.isdecimal()):
                raise ValueError("Non-numeric TCP/UDP port in ra -n output")
            start, end = float(row["StartTime"]), float(row["LastTime"])
            if not math.isfinite(start) or not math.isfinite(end) or end < start:
                raise ValueError("Invalid epoch interval")
            writer.writerow(
                dict(
                    zip(
                        FIELDS,
                        [
                            start,
                            end,
                            row["SrcAddr"],
                            row["DstAddr"],
                            src_port,
                            dst_port,
                            proto,
                            label,
                            attack,
                            offset,
                        ],
                    )
                )
            )
    audit = {
        "session": family,
        "csv_rows": len(labels),
        "argus_flow_rows": len(seen),
        "argus_management_records_excluded": management_records,
        "missing_offsets": len(labels.keys() - seen),
        "contradiction_count": len(contradictions),
        "contradiction_examples": contradictions[:10],
        "parent_sha256s": parents,
        "ra_command": command,
        "ra_version": subprocess.run(
            ["ra", "-h"], check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        ).stdout.splitlines()[:2],
    }
    audit_path = prepared / f"BS2_{family}_join_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n")
    if contradictions or seen != labels.keys():
        raise ValueError(
            f"Official label join failed for {family}; inspect {audit_path}; unverified partial retained"
        )
    partial.replace(result_path)
    entries = []
    for path in (raw_output, result_path, audit_path):
        entries.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha(path),
                "size_bytes": path.stat().st_size,
                "verification_status": "verified",
                "download_url": manifest["source_url"],
                "parent_sha256s": parents,
                "transformations": [
                    "ra -n -u numeric/time export",
                    "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks",
                ],
                "label_scope": "Flow intervals only; packet coverage and overlap conflicts still require validation",
            }
        )
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=sorted(FLOODS), action="append")
    parser.add_argument(
        "--restore-checkpoint",
        action="store_true",
        help="Merge verified prepared provenance after an older concurrent fetch completed",
    )
    args = parser.parse_args()
    manifest_path = ROOT / "data/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if args.restore_checkpoint:
        checkpoint = json.loads((ROOT / "data/prepared/provenance_checkpoint.json").read_text())
        by_path = {item["path"]: item for item in manifest["files"]}
        for item in checkpoint["files"]:
            target = (ROOT / item["path"]).resolve()
            if not target.is_relative_to(ROOT) or sha(target) != item["sha256"]:
                raise ValueError(f"Checkpoint checksum mismatch: {item['path']}")
            by_path[item["path"]] = item
        manifest["files"] = list(by_path.values())
        temporary = manifest_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(manifest, indent=2) + "\n")
        temporary.replace(manifest_path)
        print("Restored verified checkpoint provenance without removing current capture entries.")
        return
    entries = []
    for family in args.family or sorted(FLOODS):
        entries.extend(prepare(family, manifest))
    # Merge current manifest again in case a concurrent official capture completed.
    latest = json.loads(manifest_path.read_text())
    paths = {item["path"] for item in entries}
    latest["files"] = [item for item in latest["files"] if item["path"] not in paths] + entries
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(latest, indent=2) + "\n")
    temporary.replace(manifest_path)
    (ROOT / "data/prepared/provenance_checkpoint.json").write_text(
        json.dumps(latest, indent=2) + "\n"
    )
    print(json.dumps(entries, indent=2))


if __name__ == "__main__":
    main()
