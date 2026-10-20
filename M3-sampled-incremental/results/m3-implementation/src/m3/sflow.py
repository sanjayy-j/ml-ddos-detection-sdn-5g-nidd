"""Bounded sFlow v5 decoding; unsupported record types are skipped by their lengths."""

import struct

from m3.packets import parse_header


class DecodeError(ValueError):
    pass


class Reader:
    def __init__(self, data):
        self.data, self.position = data, 0

    def take(self, size):
        if size < 0 or self.position + size > len(self.data):
            raise DecodeError("Truncated sFlow datagram")
        result = self.data[self.position : self.position + size]
        self.position += size
        return result

    def integer(self):
        return struct.unpack("!I", self.take(4))[0]

    def record(self):
        tag, length = self.integer(), self.integer()
        body = self.take(length)
        self.take((-length) % 4)
        return tag, body


def decode_datagram(data: bytes, timestamp: float, *, include_headers=False):
    reader = Reader(data)
    if reader.integer() != 5:
        raise DecodeError("Only sFlow version 5 is supported")
    address_type = reader.integer()
    if address_type not in (1, 2):
        raise DecodeError("Invalid agent address type")
    agent = reader.take(4 if address_type == 1 else 16).hex()
    subagent, sequence, uptime = reader.integer(), reader.integer(), reader.integer()
    samples = reader.integer()
    packets = []
    headers = []
    drops = 0
    for _ in range(samples):
        tag, body = reader.record()
        if tag not in (1, 3):
            continue
        sample = Reader(body)
        sample.integer()  # sample sequence
        sample.integer()  # compact source ID / expanded source type
        if tag == 3:
            sample.integer()  # expanded source index
        rate, _pool, sample_drops = sample.integer(), sample.integer(), sample.integer()
        if rate < 1:
            raise DecodeError("Invalid sampling rate")
        drops = max(drops, sample_drops)  # cumulative counter, not additive per sample
        for _ in range(4 if tag == 3 else 2):
            sample.integer()  # input/output interfaces and optional formats
        count = sample.integer()
        for _ in range(count):
            record_tag, record_body = sample.record()
            if record_tag != 1:
                continue
            header = Reader(record_body)
            protocol, length = header.integer(), header.integer()
            header.integer()  # stripped bytes
            header_length = header.integer()
            raw = header.take(header_length)
            packet = parse_header(raw, timestamp, length, rate, protocol)
            if packet is not None:
                packets.append(packet)
                if include_headers:
                    headers.append({"raw": raw, "protocol": protocol, "length": length})
    metadata = {
        "agent": agent,
        "subagent": subagent,
        "sequence": sequence,
        "uptime": uptime,
        "drops": drops,
    }
    if include_headers:
        metadata["headers"] = headers
    return packets, metadata
