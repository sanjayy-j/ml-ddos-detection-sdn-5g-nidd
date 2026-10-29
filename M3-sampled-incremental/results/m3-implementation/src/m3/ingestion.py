"""Bounded, independent UDP capture with Linux kernel arrival timestamps.

The reader never runs the model or writes experiment files. A timeout watermark
uses the time BEFORE recvmsg, so a packet arriving after that timeout cannot be
silently assigned to an already closed window.
"""

import math
import queue
import socket
import struct
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionEvent:
    kernel_epoch: float
    read_epoch: float
    payload: bytes | None = None


class KernelDatagramReceiver:
    def __init__(self, sock, stop_epoch, *, lag_limit_seconds, capacity=4096):
        if type(capacity) is not int or capacity < 1:
            raise ValueError("Telemetry queue capacity must be a positive integer")
        if (not math.isfinite(stop_epoch) or not math.isfinite(lag_limit_seconds)
                or lag_limit_seconds <= 0):
            raise ValueError("Telemetry drain deadline and lag limit must be finite")
        if not hasattr(sock, "recvmsg"):
            raise RuntimeError("Kernel timestamp collection requires Linux recvmsg")
        self.sock, self.stop_epoch = sock, stop_epoch
        self.timestamp_option = getattr(socket, "SO_TIMESTAMPNS", 35)
        sock.setsockopt(socket.SOL_SOCKET, self.timestamp_option, 1)
        sock.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_RXQ_OVFL", 40), 1)
        sock.settimeout(0.01)
        self.queue = queue.Queue(maxsize=capacity)
        self.done, self.stopping = threading.Event(), threading.Event()
        self.error, self.overflow_event = None, None
        self.stats = {
            "timestamp_source": "kernel_receive_ns", "queue_capacity": capacity,
            "max_queue_depth": 0, "queue_overflows": 0, "kernel_drops": 0,
            "missing_timestamps": 0, "datagrams_received": 0,
            "max_receive_lag_seconds": 0.0, "max_processing_lag_seconds": 0.0,
            "lag_limit_seconds": lag_limit_seconds,
            "receiver_finished": False, "drain_complete": False,
        }
        self.thread = threading.Thread(target=self._read, name="m3-kernel-udp-reader", daemon=True)

    def start(self):
        self.thread.start()

    def _enqueue(self, event):
        try:
            self.queue.put_nowait(event)
            self.stats["max_queue_depth"] = max(self.stats["max_queue_depth"], self.queue.qsize())
        except queue.Full as exc:
            self.stats["queue_overflows"] += 1
            self.overflow_event = event
            raise RuntimeError("Bounded telemetry ingestion queue overflowed") from exc

    def _read(self):
        try:
            while not self.stopping.is_set():
                before = time.time()
                try:
                    payload, ancillary, flags, _ = self.sock.recvmsg(65535, 256)
                except TimeoutError:
                    self._enqueue(IngestionEvent(before, time.time()))
                    if before >= self.stop_epoch:
                        self.stats["drain_complete"] = True
                        break
                    continue
                read = time.time()
                if flags & (getattr(socket, "MSG_TRUNC", 32) | getattr(socket, "MSG_CTRUNC", 8)):
                    raise RuntimeError("Truncated telemetry datagram or timestamp ancillary data")
                epoch = None
                for level, kind, value in ancillary:
                    if level == socket.SOL_SOCKET and kind == self.timestamp_option:
                        size = struct.calcsize("@ll")
                        seconds, nanos = struct.unpack("@ll", value[:size])
                        epoch = seconds + nanos / 1e9
                    elif level == socket.SOL_SOCKET and kind == getattr(socket, "SO_RXQ_OVFL", 40):
                        self.stats["kernel_drops"] = max(self.stats["kernel_drops"],
                                                         struct.unpack("I", value[:4])[0])
                if epoch is None:
                    self.stats["missing_timestamps"] += 1
                    raise RuntimeError("UDP kernel receive timestamp missing")
                if epoch > read:
                    raise RuntimeError("Kernel and reader timestamps moved backwards")
                self.stats["datagrams_received"] += 1
                self.stats["max_receive_lag_seconds"] = max(
                    self.stats["max_receive_lag_seconds"], read - epoch)
                self._enqueue(IngestionEvent(epoch, read, payload))
                # FIFO reception of an event beyond the drain deadline proves
                # earlier queued datagrams have already been read.
                if epoch >= self.stop_epoch:
                    self.stats["drain_complete"] = True
                    break
        except BaseException as error:  # noqa: BLE001 - report every reader failure to its owner
            self.error = error
        finally:
            self.stats["receiver_finished"] = True
            self.done.set()

    def events(self):
        while not self.done.is_set() or not self.queue.empty():
            try:
                yield self.queue.get(timeout=0.05)
            except queue.Empty:
                continue
        if self.overflow_event is not None:
            yield self.overflow_event
        if self.error is not None:
            raise RuntimeError(f"Telemetry receiver failed: {self.error}") from self.error

    def processed(self, event, epoch):
        lag = epoch - event.kernel_epoch
        if lag < 0 or epoch < event.read_epoch:
            raise RuntimeError("Telemetry processing chronology moved backwards")
        self.stats["max_processing_lag_seconds"] = max(
            self.stats["max_processing_lag_seconds"], lag)

    def stop(self):
        self.stopping.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=1)
        if self.thread.is_alive():
            raise RuntimeError("Telemetry receiver did not stop")

    def validate(self):
        if (not self.stats["receiver_finished"] or not self.stats["drain_complete"]
                or self.stats["queue_overflows"] or self.stats["kernel_drops"]
                or self.stats["missing_timestamps"]
                or self.stats["max_receive_lag_seconds"] > self.stats["lag_limit_seconds"]
                or self.stats["max_processing_lag_seconds"] > self.stats["lag_limit_seconds"]):
            raise RuntimeError(f"Telemetry ingestion timing/integrity failed: {self.stats}")
