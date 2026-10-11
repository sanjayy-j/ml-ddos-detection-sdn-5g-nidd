"""Audit whether official session flow tuples have unambiguous labels.

TCP/UDP ports are normalized from Argus numbers, hexadecimal or known services.
ICMP is audited by endpoint pair only because Argus pseudo-port semantics must
be verified before packet matching. Unknown protocols/ports remain unjoined.
"""

import argparse
import csv
import json
import socket
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=10000)
def port_number(value, protocol):
    value = value.strip()
    if value.isdecimal():
        return int(value)
    if value.lower().startswith("0x"):
        return int(value, 16)
    try:
        return socket.getservbyname(value, protocol)
    except OSError:
        return None


def inspect(path):
    tuples = defaultdict(set)
    row_counts = Counter()
    unsupported = Counter()
    examples = {}
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        for row in reader:
            label = row["Label"].strip()
            family = row["Attack Type"].strip()
            row_counts[f"{label}/{family}"] += 1
            protocol = row["Proto"].strip().lower()
            src, dst = row["SrcAddr"].strip(), row["DstAddr"].strip()
            if protocol in ("tcp", "udp"):
                sport, dport = (
                    port_number(row["Sport"], protocol),
                    port_number(row["Dport"], protocol),
                )
                if sport is None or dport is None:
                    unsupported[f"{protocol}:unknown_port"] += 1
                    continue
                key = (protocol, *sorted([(src, sport), (dst, dport)]))
            elif protocol == "icmp":
                key = (protocol, *sorted([src, dst]))
            else:
                unsupported[protocol] += 1
                continue
            tuples[key].add((label, family))
            if family not in examples:
                examples[family] = {
                    field: row[field]
                    for field in (
                        "SrcAddr",
                        "DstAddr",
                        "Proto",
                        "Sport",
                        "Dport",
                        "StartTime",
                        "LastTime",
                        "Dur",
                        "Label",
                        "Attack Type",
                    )
                }
    ambiguous = [key for key, labels in tuples.items() if len(labels) > 1]
    by_protocol = Counter(key[0] for key in ambiguous)
    return {
        "path": str(path),
        "flow_rows": sum(row_counts.values()),
        "class_counts": dict(row_counts),
        "normalized_tuple_count": len(tuples),
        "ambiguous_tuple_count": len(ambiguous),
        "ambiguous_by_protocol": dict(by_protocol),
        "unjoined_rows_by_reason": dict(unsupported),
        "examples": examples,
        "notes": [
            "TCP/UDP tuple direction canonicalized; reverse packets share a key.",
            "ICMP audit uses endpoint pair, not validated ICMP type/code mapping.",
            "A conflict-free CSV tuple still requires capture tuple-coverage verification before packet labeling.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output/sdn/tuple_label_audit.json"))
    args = parser.parse_args()
    results = [inspect(path) for path in args.paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
