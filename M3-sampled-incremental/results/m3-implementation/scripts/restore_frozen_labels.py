"""Restore only the three checksum-pinned study annotation CSVs, never overwrite."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def restore(archive_path, manifest_path="data/manifest.json", prepared="data/prepared"):
    manifest = json.loads(Path(manifest_path).read_text())
    prepared = Path(prepared)
    names = [f"BS2_{family}_flow_labels.csv" for family in ("SYNFlood", "ICMPFlood", "UDPFlood")]
    entries = {Path(item["path"]).name: item for item in manifest["files"]
               if item["path"].endswith("_flow_labels.csv")}
    with zipfile.ZipFile(archive_path) as archive:
        payloads = {name: archive.read(name) for name in names}
        for name, value in payloads.items():
            if hashlib.sha256(value).hexdigest() != entries[name]["sha256"]:
                raise ValueError(f"Frozen annotation checksum mismatch: {name}")
            target = prepared / name
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != entries[name]["sha256"]:
                raise ValueError(f"Different existing annotations retained: {target}")
        prepared.mkdir(parents=True, exist_ok=True)
        for name, value in payloads.items():
            target = prepared / name
            if not target.exists():
                with target.open("xb") as stream:
                    stream.write(value)
    return names


def verify_prepared(archive_path, prepared):
    with zipfile.ZipFile(archive_path) as archive:
        expected = json.loads(archive.read("expected_prepared_sha256.json"))
    root = Path(prepared).resolve()
    for relative, checksum in expected.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Missing or unsafe prepared artifact: {relative}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Prepared selection differs: {relative}")
    return len(expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", default="research/results/frozen_preparation_annotations.zip")
    parser.add_argument("--manifest", default="data/manifest.json")
    parser.add_argument("--prepared", default="data/prepared")
    parser.add_argument("--verify-prepared", help="Verify generated PCAP/mapping bytes against the frozen study")
    args = parser.parse_args()
    if args.verify_prepared:
        print(json.dumps({"verified_prepared_artifacts": verify_prepared(args.archive, args.verify_prepared)}))
    else:
        print(json.dumps({"restored_or_verified": restore(args.archive, args.manifest, args.prepared)}))
