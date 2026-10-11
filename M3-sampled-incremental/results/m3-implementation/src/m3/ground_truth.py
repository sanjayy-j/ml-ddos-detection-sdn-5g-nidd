"""Conservative packet-to-official-flow joins; unknown/conflicting matches stay unknown."""

import csv
import ipaddress
import math
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path

import dpkt

from m3.data import POSITIVE_FAMILIES


def flow_key(source, destination, protocol, sport=None, dport=None):
    source, destination = str(ipaddress.ip_address(source)), str(ipaddress.ip_address(destination))
    if protocol in (6, 17):
        if sport is None or dport is None:
            return None
        endpoints = sorted(((source, int(sport)), (destination, int(dport))))
    else:
        # ICMP direction/type identifiers are not Argus TCP/UDP ports. Time+endpoints only.
        endpoints = sorted(((source, None), (destination, None)))
    return protocol, tuple(endpoints)


def packet_key(header):
    try:
        ip = dpkt.ethernet.Ethernet(header).data
        if isinstance(ip, dpkt.ip.IP):
            if ip.offset:
                return None
            protocol = ip.p
        elif isinstance(ip, dpkt.ip6.IP6):
            protocol = ip.nxt
        else:
            return None
        source, destination = ipaddress.ip_address(ip.src), ipaddress.ip_address(ip.dst)
        if protocol in (6, 17):
            if not isinstance(ip.data, (dpkt.tcp.TCP, dpkt.udp.UDP)):
                return None
            return flow_key(source, destination, protocol, ip.data.sport, ip.data.dport)
        if protocol in (1, 58):
            return flow_key(source, destination, protocol)
        return None
    except (ValueError, dpkt.UnpackError, AttributeError):
        return None


class IntervalIndex:
    """Balanced max-end index: avoid scanning all historical flows on each packet."""

    def __init__(self, intervals):
        self.intervals = sorted(intervals)
        self.starts = [row[0] for row in self.intervals]
        self.size = 1
        while self.size < len(intervals):
            self.size *= 2
        self.ends = [float("-inf")] * (self.size * 2)
        for index, row in enumerate(self.intervals):
            self.ends[self.size + index] = row[1]
        for node in range(self.size - 1, 0, -1):
            self.ends[node] = max(self.ends[node * 2], self.ends[node * 2 + 1])

    def at(self, timestamp, tolerance=0.000001):
        bound = bisect_right(self.starts, timestamp + tolerance)
        stack = [(1, 0, self.size)]
        result = []
        while stack:
            node, low, high = stack.pop()
            if low >= bound or self.ends[node] < timestamp - tolerance:
                continue
            if high - low == 1:
                result.append(self.intervals[low])
            else:
                middle = (low + high) // 2
                stack.extend([(node * 2, low, middle), (node * 2 + 1, middle, high)])
        return result


class FlowLabels:
    def __init__(self, path):
        grouped = defaultdict(list)
        self.rows = 0
        self.unjoinable_rows = 0
        with Path(path).open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            required = {
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
            }
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("Flow label table lacks the verified numeric/time schema")
            for row in reader:
                self.rows += 1
                start, end = float(row["start_epoch"]), float(row["end_epoch"])
                if not math.isfinite(start) or not math.isfinite(end) or end < start:
                    raise ValueError("Invalid official flow interval")
                label = int(row["label"])
                family = row["attack_family"]
                if (
                    (label == 0 and family != "Benign")
                    or (label == 1 and family not in POSITIVE_FAMILIES)
                    or label not in (0, 1)
                ):
                    raise ValueError("Conflicting flow label/family")
                protocol = {"tcp": 6, "udp": 17, "icmp": 1, "ipv6-icmp": 58}.get(
                    row["protocol"].strip().lower()
                )
                if protocol is None:
                    self.unjoinable_rows += 1
                    continue
                ports = []
                for key in ("src_port", "dst_port"):
                    text = row[key].strip()
                    if text and (not text.isdecimal() or not 0 <= int(text) <= 65535):
                        raise ValueError(
                            "Flow ports must be numeric; service-name guesses are forbidden"
                        )
                    ports.append(int(text) if text else None)
                key = flow_key(row["src_ip"], row["dst_ip"], protocol, *ports)
                if key is None:
                    self.unjoinable_rows += 1
                else:
                    grouped[key].append((start, end, label, family))
        self.index = {key: IntervalIndex(rows) for key, rows in grouped.items()}

    def match(self, header, timestamp):
        key = packet_key(header)
        index = self.index.get(key)
        if index is None:
            return None, "unknown"
        candidates = index.at(timestamp)
        labels = {row[2] for row in candidates}
        if len(labels) != 1:
            return None, "unknown"
        label = next(iter(labels))
        families = {row[3] for row in candidates}
        return label, next(iter(families)) if len(families) == 1 else "mixed_flood"


class WindowTruth:
    def __init__(self):
        self.packets = 0
        self.unknown = 0
        self.positive_families = set()

    def add(self, label, family):
        self.packets += 1
        self.unknown += label is None
        if label == 1:
            self.positive_families.add(family)

    def label(self):
        if self.positive_families:
            family = (
                next(iter(self.positive_families))
                if len(self.positive_families) == 1
                else "mixed_flood"
            )
            return 1, family
        if self.unknown:
            return None, "unknown"
        return 0, "Benign"
