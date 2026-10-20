"""Audit every original capture packet against verified official flow intervals.

This measures label coverage, not model performance or a dataset quality pass.
Unknown packets remain unknown; filenames never supply labels.
"""

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import dpkt

from m3.ground_truth import FlowLabels, packet_key
from m3.packets import iter_pcap
from m3.provenance import verify_input
from m3.store import atomic_json

CATEGORIES = (
    "matched_benign",
    "matched_flood",
    "unmatched_key",
    "unmatched_time",
    "conflicting_label_overlap",
    "invalid_or_nonjoinable_header",
)


def audit_capture(capture, labels, manifest="data/manifest.json", max_packets=None):
    """Return a complete, diagnostic-capped, or failed coverage report.

    Provenance/schema errors raise before any capture is processed. Capture errors
    produce an explicitly failed partial report, never a successful full audit.
    """
    if max_packets is not None and (
        isinstance(max_packets, bool) or not isinstance(max_packets, int) or max_packets <= 0
    ):
        raise ValueError("max_packets must be a positive integer")
    provenance = {
        "capture": verify_input(capture, manifest),
        "labels": verify_input(labels, manifest),
    }
    flow_labels = FlowLabels(labels)
    label_families = Counter(
        row[3] for index in flow_labels.index.values() for row in index.intervals
    )
    counts = dict.fromkeys(CATEGORIES, 0)
    matched_families = Counter()
    mixed_family_sets = Counter()
    report = {
        "schema": "packet-label-coverage-v1",
        "purpose": "Full original-stream label coverage; not sampled/model accuracy evidence",
        "evidence_scope": (
            "synthetic_test_fixture_only_not_official_evidence"
            if any(entry.get("fixture") for entry in provenance.values())
            else "manifest_verified_inputs"
        ),
        "status": "complete",
        "complete": True,
        "max_packets": max_packets,
        "cap_reached": False,
        "counts": counts,
        "total_packets": 0,
        "min_timestamp_epoch": None,
        "max_timestamp_epoch": None,
        "timestamp_order_errors": 0,
        "error": None,
        "label_rows": flow_labels.rows,
        "unjoinable_label_rows": flow_labels.unjoinable_rows,
        "joinable_label_rows_by_family": dict(sorted(label_families.items())),
        "matching_rule": (
            "Existing FlowLabels bidirectional numeric tuple/protocol and interval match; "
            "unchanged IntervalIndex default 0.000001-second tolerance; ICMP uses "
            "endpoints/protocol/time, not guessed ports. Mixed benign/flood overlaps are "
            "unknown; overlapping positive families are matched as mixed_flood."
        ),
        "coverage_interpretation": (
            "Coverage is descriptive only: unknowns are not benign, and complete means "
            "the stream was scanned, not that label quality passed any threshold."
        ),
        "provenance": provenance,
    }
    previous = float("-inf")
    try:
        for timestamp, header in iter_pcap(capture):
            if not math.isfinite(timestamp):
                raise ValueError("Capture timestamp is not finite")
            if timestamp < previous:
                raise ValueError("Capture timestamps are not ordered")
            previous = timestamp
            report["total_packets"] += 1
            report["min_timestamp_epoch"] = (
                timestamp
                if report["min_timestamp_epoch"] is None
                else min(timestamp, report["min_timestamp_epoch"])
            )
            report["max_timestamp_epoch"] = (
                timestamp
                if report["max_timestamp_epoch"] is None
                else max(timestamp, report["max_timestamp_epoch"])
            )
            key = packet_key(header)
            index = flow_labels.index.get(key) if key is not None else None
            if key is None:
                counts["invalid_or_nonjoinable_header"] += 1
            elif index is None:
                counts["unmatched_key"] += 1
            else:
                candidates = index.at(timestamp)
                candidate_labels = {row[2] for row in candidates}
                if not candidates:
                    counts["unmatched_time"] += 1
                elif len(candidate_labels) != 1:
                    counts["conflicting_label_overlap"] += 1
                else:
                    label = next(iter(candidate_labels))
                    families = {row[3] for row in candidates}
                    family = next(iter(families)) if len(families) == 1 else "mixed_flood"
                    counts["matched_flood" if label else "matched_benign"] += 1
                    matched_families[family] += 1
                    if family == "mixed_flood":
                        mixed_family_sets[" + ".join(sorted(families))] += 1
            # Conservatively incomplete even if the cap happens to equal file length:
            # EOF has not been observed, so the full original stream is not proven.
            if max_packets is not None and report["total_packets"] >= max_packets:
                report.update(status="diagnostic_capped", complete=False, cap_reached=True)
                break
    except (ValueError, dpkt.UnpackError, OSError, EOFError) as error:
        report.update(status="failed", complete=False, error=str(error))
        report["timestamp_order_errors"] = int("timestamps are not ordered" in str(error))

    total = report["total_packets"]
    matched = counts["matched_benign"] + counts["matched_flood"]
    report.update(
        matched_packets=matched,
        unknown_packets=total - matched,
        match_coverage=matched / total if total else None,
        matched_packets_by_family=dict(sorted(matched_families.items())),
        mixed_flood_family_sets=dict(sorted(mixed_family_sets.items())),
        counts_reconcile=sum(counts.values()) == total,
    )
    if not report["counts_reconcile"]:
        raise AssertionError("Packet audit categories do not reconcile")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("data/manifest.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-packets", type=int, help="Diagnostic cap; never a full audit")
    args = parser.parse_args(argv)
    if args.output.resolve() in {
        args.capture.resolve(),
        args.labels.resolve(),
        args.manifest.resolve(),
    }:
        parser.error("Output must not overwrite capture, labels, or provenance manifest")
    try:
        report = audit_capture(args.capture, args.labels, args.manifest, args.max_packets)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"Packet audit rejected before scanning: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output, report)
    print(
        json.dumps(
            {
                key: report[key]
                for key in (
                    "status",
                    "complete",
                    "total_packets",
                    "matched_packets",
                    "unknown_packets",
                    "match_coverage",
                    "error",
                )
            }
        )
    )
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
