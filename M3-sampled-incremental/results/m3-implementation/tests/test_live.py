import socket
import threading
import time

import pytest
from test_core import sflow_datagram

from m3.config import RunConfig
from m3.live import run_live
from m3.store import RunRepository


@pytest.mark.parametrize("rate,expected", [(1, "completed"), (10, "failed")])
def test_udp_collector_health_and_raw_evidence(tmp_path, rate, expected):
    # Generated protocol fixtures test software only and stay in pytest's temporary directory.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    config = RunConfig(
        mode="live_sflow",
        output_root=str(tmp_path / "runs"),
        sampling_rate=1,
        port=port,
        duration_seconds=0.6,
        window_seconds=0.1,
        warmup_seconds=0.1,
    )

    def send():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            for _ in range(20):
                time.sleep(0.04)
                sender.sendto(sflow_datagram(rate), ("127.0.0.1", port))

    thread = threading.Thread(target=send)
    thread.start()
    try:
        if expected == "failed":
            with pytest.raises(RuntimeError, match="evidence retained"):
                run_live(config)
        else:
            run = run_live(config)
            assert run["counts"]["unlabeled"] > 0
            assert run["metrics"]["f1"]["value"] is None
            assert run["metrics"]["telemetry_bandwidth_kbps"]["status"] == "measured"
    finally:
        thread.join()
    run = RunRepository(config.output_root).list()[0]
    assert run["status"] == expected
    assert (tmp_path / "runs" / run["run_id"] / "sflow.datagrams").stat().st_size > 0
