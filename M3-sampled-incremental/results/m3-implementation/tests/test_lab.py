from types import SimpleNamespace

from m3.lab import LabMeasurements


def test_ovs_real_zero_vs_missing(monkeypatch, tmp_path):
    writer = SimpleNamespace(
        path=tmp_path,
        summary={"config": {"mode": "live_sflow", "ovs_bridge": "m3s1", "openflow_port": None}},
    )
    lab = LabMeasurements(writer)
    monkeypatch.setattr(
        "m3.lab.subprocess.run", lambda *a, **kw: SimpleNamespace(stdout="OFPST_FLOW reply:\n")
    )
    assert lab.sample() == 0
    assert lab.finish(1)["flow_table_entries"]["value"] == 0
    assert lab.finish(1)["openflow_bandwidth_kbps"]["value"] is None
    monkeypatch.setattr("m3.lab.subprocess.run", lambda *a, **kw: SimpleNamespace(stdout="invalid"))
    assert lab.sample() is None


def test_ovs_counts_and_safe_argv(monkeypatch, tmp_path):
    writer = SimpleNamespace(
        path=tmp_path, summary={"config": {"mode": "live_sflow", "ovs_bridge": "m3s1"}}
    )

    def run(args, **kwargs):
        assert args == ["ovs-ofctl", "-O", "OpenFlow13", "dump-flows", "m3s1"]
        assert kwargs["timeout"] == 1 and not kwargs.get("shell")
        return SimpleNamespace(
            stdout="OFPST_FLOW reply:\n cookie=0x0, priority=1\n cookie=0x1, priority=2\n"
        )

    monkeypatch.setattr("m3.lab.subprocess.run", run)
    lab = LabMeasurements(writer)
    assert lab.sample() == 2
    assert lab.finish(1)["flow_table_entries"]["value"] == 2
