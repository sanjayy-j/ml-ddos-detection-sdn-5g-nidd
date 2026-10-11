import math
import struct
from dataclasses import dataclass
from pathlib import Path

import dpkt

from m3.data import Record


@dataclass(frozen=True)
class Packet:
    time: float
    length: int
    protocol: int
    syn: bool
    sample_rate: int = 1


def parse_header(header: bytes, time: float, length: int, sample_rate=1, protocol=1):
    offset = 0
    if protocol == 1:  # sFlow raw header protocol: Ethernet ISO88023
        if len(header) < 14:
            return None
        ethertype = struct.unpack_from("!H", header, 12)[0]
        offset = 14
        while ethertype in (0x8100, 0x88A8):
            if len(header) < offset + 4:
                return None
            ethertype = struct.unpack_from("!H", header, offset + 2)[0]
            offset += 4
    elif protocol == 11:
        ethertype = 0x0800
    elif protocol == 12:
        ethertype = 0x86DD
    else:
        return None
    if ethertype == 0x0800:
        if len(header) < offset + 20 or header[offset] >> 4 != 4:
            return None
        ihl = (header[offset] & 15) * 4
        if ihl < 20 or len(header) < offset + ihl:
            return None
        ipproto = header[offset + 9]
        fragmented = struct.unpack_from("!H", header, offset + 6)[0] & 0x1FFF
        transport = offset + ihl
    elif ethertype == 0x86DD:
        if len(header) < offset + 40:
            return None
        ipproto, fragmented, transport = header[offset + 6], False, offset + 40
        if ipproto not in (6, 17, 58):
            return None  # IPv6 extension headers require additional decoding; do not guess.
    else:
        return None
    syn = (
        ipproto == 6
        and not fragmented
        and len(header) >= transport + 14
        and bool(header[transport + 13] & 2)
    )
    return Packet(time, length, ipproto, syn, sample_rate)


def iter_pcap(path: str | Path):
    with Path(path).open("rb") as stream:
        magic = stream.read(4)
        stream.seek(0)
        reader = (
            dpkt.pcapng.Reader(stream) if magic == b"\x0a\x0d\x0d\x0a" else dpkt.pcap.Reader(stream)
        )
        if reader.datalink() != dpkt.pcap.DLT_EN10MB:
            raise ValueError(
                "Packet input requires Ethernet captures; use the official GTP-removed trace"
            )
        previous = float("-inf")
        for timestamp, header in reader:
            timestamp = float(timestamp)
            if timestamp < previous:
                raise ValueError("Capture timestamps are not ordered")
            previous = timestamp
            yield timestamp, header


class WindowAccumulator:
    def __init__(self, seconds=1):
        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("Window duration must be positive and finite")
        self.seconds = seconds
        self.index = None
        self.packets = []

    def _record(self):
        count = len(self.packets)
        weighted_packets = sum(p.sample_rate for p in self.packets)
        weighted_bytes = sum(p.length * p.sample_rate for p in self.packets)
        total_bytes = sum(p.length for p in self.packets)
        features = {
            "packets_per_second": weighted_packets / self.seconds,
            "bytes_per_second": weighted_bytes / self.seconds,
            "mean_packet_size": total_bytes / count if count else 0.0,
            "udp_fraction": sum(p.protocol == 17 for p in self.packets) / count if count else 0.0,
            "tcp_fraction": sum(p.protocol == 6 for p in self.packets) / count if count else 0.0,
            "icmp_fraction": sum(p.protocol in (1, 58) for p in self.packets) / count
            if count
            else 0.0,
            "syn_fraction": sum(p.syn for p in self.packets) / count if count else 0.0,
            "empty_window": int(not count),
        }
        return Record(self.index, self.index * self.seconds, features, None, "unknown"), count

    def advance(self, relative_time):
        index = math.floor(relative_time / self.seconds)
        if index < 0:
            return
        if self.index is None:
            self.index = 0
        if index < self.index:
            raise ValueError("Window observations moved backwards")
        if index - self.index > 100000:
            raise ValueError("Capture gap is too large; prepare a documented trace segment")
        while self.index < index:
            yield self._record()
            self.index += 1
            self.packets = []

    def add(self, packet, origin):
        yield from self.advance(packet.time - origin)
        self.packets.append(packet)

    def finish(self):
        if self.index is not None:
            yield self._record()
