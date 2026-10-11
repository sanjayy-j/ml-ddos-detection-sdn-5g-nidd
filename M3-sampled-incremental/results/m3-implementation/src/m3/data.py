import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

POSITIVE_FAMILIES = {"UDPFlood", "SYNFlood", "ICMPFlood"}
# Deliberate allowlist: labels, tools, addresses, row IDs, Seq and Offset never reach the model.
NUMERIC_COLUMNS = (
    "Dur",
    "TotPkts",
    "TotBytes",
    "SrcBytes",
    "DstBytes",
    "sMeanPktSz",
    "dMeanPktSz",
    "sTtl",
    "dTtl",
    "SrcPkts",
    "DstPkts",
    "Rate",
    "SrcRate",
    "DstRate",
)
CATEGORICAL_COLUMNS = ("Proto",)


@dataclass(frozen=True)
class Record:
    index: int
    time: float
    features: dict[str, float | str]
    label: int | None
    attack_family: str


def binary_label(family: str, label: str) -> int | None:
    family, label = family.strip(), label.strip()
    if family.startswith("SYNTH_") or label.startswith("SYNTH_"):
        raise ValueError("Synthetic placeholder labels are not valid official experiment data")
    if family in POSITIVE_FAMILIES:
        if label.lower() not in {"malicious", "1", "attack", family.lower()}:
            raise ValueError(f"Conflicting label for {family}: {label}")
        return 1
    if family.lower() == "benign" and label.lower() in {"benign", "0", "normal"}:
        return 0
    if family.lower() == "benign":
        raise ValueError(f"Conflicting benign label: {label}")
    return None


def extract_flow_features(row: dict[str, str]) -> dict[str, float | str]:
    features: dict[str, float | str] = {}
    for name in NUMERIC_COLUMNS:
        raw = (row.get(name) or "").strip()
        try:
            value = float(raw)
        except ValueError:
            if raw and raw.lower() not in {"nan", "null", "none"}:
                raise ValueError(f"Invalid numeric value in {name}: {raw!r}") from None
            value = math.nan
        features[f"missing_{name}"] = int(not math.isfinite(value))
        features[name] = value if math.isfinite(value) else 0.0
    for name in CATEGORICAL_COLUMNS:
        features[name] = (row.get(name) or "unknown").strip().lower()
    return features


def iter_csv(path: str | Path):
    with Path(path).open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(line for line in stream if not line.startswith("#"))
        required = {"Label", "Attack Type", "Proto", "Dur", "TotPkts", "TotBytes"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"Missing CSV columns: {sorted(required - set(reader.fieldnames or []))}"
            )
        for index, row in enumerate(reader):
            if None in row:
                raise ValueError(f"Malformed CSV row {index + 2}")
            family = row["Attack Type"].strip()
            yield Record(
                index,
                float(index),
                extract_flow_features(row),
                binary_label(family, row["Label"]),
                family,
            )


def audit_csv(path: str | Path) -> dict:
    counts: Counter = Counter()
    missing: Counter = Counter()
    seen: set[str] = set()
    duplicate_rows = 0
    rows = 0
    import hashlib

    with Path(path).open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(line for line in stream if not line.startswith("#"))
        columns = reader.fieldnames or []
        for row in reader:
            if None in row:
                raise ValueError(f"Malformed row {rows + 2}")
            rows += 1
            counts[row.get("Attack Type", "unknown")] += 1
            for key, value in row.items():
                if not value or value.strip().lower() in {"nan", "null", "none"}:
                    missing[key] += 1
            signature = hashlib.sha256(repr(tuple(row.values())).encode()).hexdigest()
            duplicate_rows += signature in seen
            seen.add(signature)
    return {
        "rows": rows,
        "columns": columns,
        "attack_counts": dict(counts),
        "missing_counts": dict(missing),
        "duplicate_rows": duplicate_rows,
        "ordering": "CSV row order only; chronological order is not established",
    }
