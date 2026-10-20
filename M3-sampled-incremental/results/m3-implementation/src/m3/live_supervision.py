"""Independent packet truth and strictly ordered experimental label revelation.

This is an oracle for an isolated experiment, not a production labelling service.
No sampled packet, schedule name, or model prediction supplies the truth label.
"""

import json
import math
import struct
from pathlib import Path


def restore_vlan(frame, auxiliary):
    """Reconstruct a stripped VLAN tag only when Linux marks its metadata valid.

    Linux PACKET_AUXDATA / tpacket_auxdata: see packet(7) and if_packet.h.
    This also handles stacked VLAN tags by restoring the stripped outer tag.
    """
    if len(auxiliary) < 20 or len(frame) < 14:
        raise ValueError("Truncated packet auxdata or Ethernet frame")
    status, _, _, _, _, tci, tpid = struct.unpack("=IIIHHHH", auxiliary[:20])
    if status & (1 << 4):
        return frame[:12] + struct.pack("!HH", tpid if status & (1 << 6) else 0x8100, tci) + frame[12:]
    return frame


class FrameLabels:
    def __init__(self, pairs):
        self.frames = {}
        for frame, family in pairs:
            previous = self.frames.setdefault(frame, family)
            if previous != family:
                raise ValueError("Full frame has conflicting authoritative labels")

    def match(self, frame):
        return self.frames.get(frame)


def truth_payload(families, start_epoch, end_epoch):
    known = set(families)
    pure = len(known) == 1 and None not in known
    family = next(iter(known)) if pure else "unknown"
    return {
        "label": int(family != "Benign") if pure else None,
        "attack_family": family,
        "packets": len(families),
        "start_epoch": start_epoch,
        "end_epoch": end_epoch,
        "mixed_or_unknown": bool(families) and not pure,
    }


def reveal_truth(path, *, prediction_epoch, read_epoch):
    if not all(math.isfinite(x) for x in (prediction_epoch, read_epoch)):
        raise ValueError("Nonfinite chronology clock")
    if read_epoch < prediction_epoch:
        raise ValueError("Label clock precedes prediction completion")
    payload = json.loads(Path(path).read_text())
    if prediction_epoch < payload["end_epoch"]:
        raise ValueError("Window was not closed before prediction")
    if payload["available_epoch"] > read_epoch:
        raise ValueError("Label availability clock is in the future")
    return payload
