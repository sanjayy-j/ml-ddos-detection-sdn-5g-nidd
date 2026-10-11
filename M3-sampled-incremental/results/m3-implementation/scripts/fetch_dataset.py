"""Fetch only the authors' public Fairdata release, checking publisher SHA256.

Usage: python scripts/fetch_dataset.py [--captures] [--list]
Requires no third-party packages. ZIP members are preserved byte-for-byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = "9d13ef28-2ca7-44b0-9950-225359afac65"
DOI = "10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361"
PAGE = f"https://etsin.fairdata.fi/dataset/{DATASET_ID}"
LIST_URL = "https://metax.fairdata.fi/v3/directories?" + urllib.parse.urlencode(
    {
        "path": "/",
        "storage_service": "ida",
        "csc_project": "2006938",
        "dataset": DATASET_ID,
        "pagination": "false",
    }
)
AUTHORIZE = "https://etsin.fairdata.fi/api/download/authorize"
DEFAULT = ["README.pdf", "Combined.zip", "BS1_each_attack_csv.zip", "BS2_each_attack_csv.zip"]


def request_json(url: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "M3-5G-NIDD-research/1.0",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def save_manifest(path: Path, manifest: dict) -> None:
    if path.exists():
        current = json.loads(path.read_text(encoding="utf-8"))
        by_path = {item["path"]: item for item in current.get("files", [])}
        by_path.update({item["path"]: item for item in manifest.get("files", [])})
        manifest["files"] = list(by_path.values())
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def fetch(record: dict, target: Path) -> None:
    expected = record["checksum"].removeprefix("sha256:")
    if target.exists():
        if target.stat().st_size == record["size"] and digest(target) == expected:
            print(f"Verified existing {target.name}", flush=True)
            return
        raise ValueError(
            f"Existing {target} does not match the official checksum; preserve it and investigate."
        )
    # This is the public authorization API used by Etsin's download button.
    # Its signed URL is transient and is deliberately not saved to the manifest.
    transient_url = request_json(AUTHORIZE, {"cr_id": DATASET_ID, "file": record["pathname"]})[
        "url"
    ]
    if urllib.parse.urlparse(transient_url).hostname != "download.fairdata.fi":
        raise ValueError("Portal returned an unexpected download host")
    partial = target.with_suffix(target.suffix + ".partial")
    if partial.exists():
        raise ValueError(
            f"Partial download exists at {partial}; preserve or remove it before retrying."
        )
    print(f"Downloading {target.name} ({record['size']:,} bytes)", flush=True)
    with (
        urllib.request.urlopen(transient_url, timeout=120) as response,
        partial.open("xb") as output,
    ):
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    if partial.stat().st_size != record["size"] or digest(partial) != expected:
        raise ValueError(f"Publisher checksum verification failed for {partial}")
    partial.rename(target)


def entry(path: Path, record: dict, parent: str | None = None) -> dict:
    item = {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
        "verification_status": "verified",
        "size_bytes": path.stat().st_size,
        "download_url": AUTHORIZE,
        "official_filename": record["filename"],
        "official_file_id": record["id"],
        "official_path": record["pathname"],
    }
    if parent:
        item.update(
            parent_sha256=parent, transformations=["ZIP extraction only; member bytes unchanged"]
        )
    else:
        item["publisher_sha256"] = record["checksum"].removeprefix("sha256:")
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--captures",
        action="store_true",
        help="Also obtain both GTP-removed capture archives (~3.9 GB)",
    )
    parser.add_argument(
        "--file",
        action="append",
        dest="files",
        help="Download a selected official filename instead of defaults (repeatable)",
    )
    parser.add_argument(
        "--list", action="store_true", help="Print official filenames and sizes only"
    )
    args = parser.parse_args()
    raw = ROOT / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "data" / "manifest.json"
    manifest = {
        "dataset": "5G-NIDD",
        "doi": DOI,
        "source_url": PAGE,
        "license": "CC-BY-4.0",
        "files": [],
        "status": "blocked",
        "notes": [],
    }
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = previous.get("files", [])
    try:
        listing = request_json(LIST_URL)
        records = {record["filename"]: record for record in listing["files"]}
        if args.list:
            print(
                json.dumps(
                    [
                        {
                            "filename": r["filename"],
                            "size_bytes": r["size"],
                            "sha256": r["checksum"],
                        }
                        for r in records.values()
                    ],
                    indent=2,
                )
            )
            return 0
        manifest["metadata_url"] = LIST_URL
        manifest["retrieved_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        names = (args.files or DEFAULT) + (
            ["BS1_GTP_removed.zip", "BS2 GTP removed.zip"] if args.captures else []
        )
        for name in names:
            record = records[name]
            target = raw / name
            fetch(record, target)
            new_entries = [entry(target, record)]
            if target.suffix == ".zip":
                parent = digest(target)
                destination = raw / target.stem
                with zipfile.ZipFile(target) as archive:
                    members = [member for member in archive.infolist() if not member.is_dir()]
                    if sum(member.file_size for member in members) > 8 * 1024**3:
                        members = [
                            member
                            for member in members
                            if any(
                                name in member.filename.lower()
                                for name in ("icmp", "udp", "synflood")
                            )
                        ]
                        manifest["notes"].append(
                            "Large capture archive: extraction limited to network-flood members."
                        )
                    required = sum(
                        member.file_size
                        for member in members
                        if not (destination / member.filename).exists()
                    )
                    if required + 1024**3 > shutil.disk_usage(raw).free:
                        raise ValueError(
                            "Insufficient disk space to extract safely with a 1GB reserve; verified archive retained."
                        )
                    for member in members:
                        if member.is_dir():
                            continue
                        member_path = destination / member.filename
                        if not member_path.resolve().is_relative_to(destination.resolve()):
                            raise ValueError("Archive contains an unsafe path")
                        member_path.parent.mkdir(parents=True, exist_ok=True)
                        with archive.open(member) as source:
                            checksum = hashlib.sha256()
                            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                                checksum.update(chunk)
                        if member_path.exists() and digest(member_path) != checksum.hexdigest():
                            raise ValueError(f"Existing extracted member differs: {member_path}")
                        if not member_path.exists():
                            with archive.open(member) as source, member_path.open("xb") as output:
                                shutil.copyfileobj(source, output, 1024 * 1024)
                        new_entries.append(entry(member_path, record, parent))
            replaced = {item["path"] for item in new_entries}
            manifest["files"] = [
                item for item in manifest["files"] if item["path"] not in replaced
            ] + new_entries
            save_manifest(manifest_path, manifest)
        manifest["status"] = "verified"
        manifest["notes"] += [
            "Publisher SHA256 checked for each downloaded archive. Extracted files have local SHA256 and parent archive provenance.",
            "Combined.csv order must not be claimed chronological without further evidence.",
            "Capture filenames alone do not provide packet-level attack ground truth.",
        ]
        if not any("GTP" in name for name in names):
            manifest["notes"].append(
                "Packet capture archives have not been downloaded. Use --captures when needed."
            )
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        manifest["notes"].append(f"Download blocked: {type(error).__name__}: {error}")
        print(manifest["notes"][-1], file=sys.stderr)
    save_manifest(manifest_path, manifest)
    print(f"Saved {manifest_path}")
    return 0 if manifest["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
