import hashlib
import json
import os
from pathlib import Path

OFFICIAL_DOI = "10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361"


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_input(path: str | Path, manifest_path: str | Path) -> dict:
    source = Path(path).resolve()
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("dataset") != "5G-NIDD" or manifest.get("doi") != OFFICIAL_DOI:
        raise ValueError("Input requires the official 5G-NIDD provenance manifest")
    entries = manifest.get("files", [])
    # Most records use the exact canonical path. Resolve only a matching entry;
    # traversing every unrelated path is exceptionally slow on WSL's 9p/DrvFS.
    direct = [entry for entry in entries if Path(os.path.abspath(entry["path"])) == source]
    candidates = direct or entries  # Preserve resolved/symlink alias compatibility.
    for entry in candidates:
        if Path(entry["path"]).resolve() == source:
            if (
                manifest.get("status") != "verified"
                and entry.get("verification_status") != "verified"
                and entry.get("verified") is not True
            ):
                raise ValueError("Selected official file is not yet verified")
            actual = sha256(source)
            if actual != entry.get("sha256"):
                raise ValueError("Dataset checksum mismatch: preserve the verified original")
            return {"dataset": "5G-NIDD", "doi": OFFICIAL_DOI, **entry}
    raise ValueError("Input is not registered in the official dataset manifest")
