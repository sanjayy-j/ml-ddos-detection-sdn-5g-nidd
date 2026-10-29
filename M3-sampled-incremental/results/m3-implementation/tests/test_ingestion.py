"""Synthetic queue/timestamp fixtures; no experiment traffic or performance claims."""

import socket
import struct
from itertools import pairwise
from types import SimpleNamespace

import pytest

from m3 import ingestion
from m3.ingestion import IngestionEvent, KernelDatagramReceiver


class FakeSocket:
    def setsockopt(self, *_):
        pass

    def settimeout(self, *_):
        pass

    def recvmsg(self, *_):
        return b"missing-clock", [], 0, ("127.0.0.1", 1)


def test_queue_cannot_be_accidentally_unbounded():
    with pytest.raises(ValueError, match="queue capacity"):
        KernelDatagramReceiver(FakeSocket(), 200, lag_limit_seconds=0.1, capacity=0)


def test_missing_kernel_timestamp_fails_instead_of_using_read_time():
    receiver = KernelDatagramReceiver(FakeSocket(), 200, lag_limit_seconds=0.1)
    receiver.start()
    with pytest.raises(RuntimeError, match="timestamp missing"):
        list(receiver.events())
    receiver.stop()
    assert receiver.stats["missing_timestamps"] == 1
    assert not receiver.stats["drain_complete"]


def test_bounded_queue_failure_is_visible_and_preserves_overflow_event():
    receiver = KernelDatagramReceiver(FakeSocket(), 200, lag_limit_seconds=0.1, capacity=1)
    first, second = IngestionEvent(100, 100, b"first"), IngestionEvent(101, 101, b"second")
    receiver._enqueue(first)
    with pytest.raises(RuntimeError, match="queue overflowed"):
        receiver._enqueue(second)
    assert receiver.queue.get_nowait() == first
    assert receiver.overflow_event == second
    assert receiver.stats["queue_overflows"] == 1


def test_timeout_watermark_precedes_next_arrival_and_pending_events_drain(monkeypatch):
    clock = SimpleNamespace(now=100.0)
    calls = 0

    class Socket(FakeSocket):
        def recvmsg(self, *_):
            nonlocal calls
            calls += 1
            clock.now += 0.02
            if calls == 2:
                ancillary = [(socket.SOL_SOCKET, getattr(socket, "SO_TIMESTAMPNS", 35),
                              struct.pack("@ll", 100, 30_000_000))]
                return b"queued", ancillary, 0, ("127.0.0.1", 1)
            raise TimeoutError

    monkeypatch.setattr(ingestion, "time", SimpleNamespace(time=lambda: clock.now))
    receiver = KernelDatagramReceiver(Socket(), 100.05, lag_limit_seconds=0.1)
    receiver.start()
    receiver.thread.join(timeout=1)
    events = list(receiver.events())
    assert events[0].payload is None and events[0].kernel_epoch == 100
    assert events[1].payload == b"queued" and events[1].kernel_epoch == 100.03
    assert all(a.kernel_epoch <= b.kernel_epoch for a, b in pairwise(events))
    assert receiver.stats["drain_complete"]
    receiver.validate()
