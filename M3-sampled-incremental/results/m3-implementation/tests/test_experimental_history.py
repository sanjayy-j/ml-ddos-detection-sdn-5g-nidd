import copy

import pytest

from m3.experimental_history import RecentHistory, replay_comparison


def features(count=1, size=100, udp=1):
    return {"packets_per_second": count * 10, "bytes_per_second": count * size * 10,
            "mean_packet_size": size if count else 0, "udp_fraction": udp if count else 0,
            "tcp_fraction": 1 - udp if count else 0, "icmp_fraction": 0,
            "syn_fraction": 0, "empty_window": int(count == 0)}


def test_history_is_packet_weighted_and_integrates_rates():
    h = RecentHistory()
    h.update(features=features(1, 100, 1), start=0, end=0.1, sampled_packets=1)
    result = h.update(features=features(3, 200, 0), start=0.1, end=0.2, sampled_packets=3)
    assert result["history_sampled_packets"] == 4
    assert result["history_mean_packet_size"] == 175
    assert result["history_udp_fraction"] == 0.25
    assert result["history_packets_per_second"] == pytest.approx(20)
    assert result["history_bytes_per_second"] == pytest.approx(3500)


def test_trailing_horizon_startup_empty_and_long_gap():
    h = RecentHistory()
    for i in range(6):
        result = h.update(features=features(0), start=i / 10, end=(i + 1) / 10,
                          sampled_packets=0)
    assert len(h.windows) == 5
    assert result["history_empty_streak"] == 6
    assert result["history_empty_fraction"] == pytest.approx(1)
    assert result["history_udp_fraction"] == 0
    result = h.update(features=features(2), start=1.0, end=1.1, sampled_packets=2)
    assert len(h.windows) == 1
    assert result["history_empty_streak"] == 0
    assert result["history_sampled_packets"] == 2


def test_nonchronological_or_invalid_input_rejected():
    h = RecentHistory()
    h.update(features=features(), start=0, end=0.1, sampled_packets=1)
    with pytest.raises(ValueError, match="chronological"):
        h.update(features=features(), start=0, end=0.1, sampled_packets=1)
    with pytest.raises(ValueError, match="nonnegative integer"):
        RecentHistory().update(features=features(), start=0, end=0.1, sampled_packets=-1)


def rows():
    return [{"index": i, "features": features(i % 3), "y_true": i % 2,
             "y_pred": 0, "score": 0, "warmup": i < 5, "attack_family": "UDPFlood",
             "window_start": i / 10, "window_end": (i + 1) / 10,
             "sampled_packets": i % 3, "observed_time": i / 10 + 1,
             "label_available_time": i / 10 + 1.01} for i in range(30)]


CONFIG = {"mode": "live_sflow", "window_seconds": 0.1, "grace_period": 5}


def test_future_rows_cannot_change_past_predictions_and_runs_reset():
    first = replay_comparison(rows()[:15], CONFIG)["predictions"]
    all_rows = replay_comparison(rows(), CONFIG)["predictions"]
    assert first == all_rows[:15]
    assert replay_comparison(rows()[:15], CONFIG)["predictions"] == first
    changed = copy.deepcopy(rows())
    changed[10]["y_true"] = 1 - changed[10]["y_true"]
    before_label = replay_comparison(changed, CONFIG)["predictions"]
    for i in range(11):
        assert before_label[i]["recent_history"] == all_rows[i]["recent_history"]


def test_recorded_delayed_label_is_not_used_early(monkeypatch):
    import m3.experimental_history as module

    class FakeDetector:
        def __init__(self, config):
            self.seen = 0
            self.model = self

        def predict(self, x):
            return int(self.seen > 0), float(self.seen > 0), 0

        def learn_one(self, x, y):
            self.seen += 1

    monkeypatch.setattr(module, "OnlineDetector", FakeDetector)
    data = rows()[:5]
    data[0]["label_available_time"] = data[0]["observed_time"] + 0.25
    for row in data[1:]:
        row["label_available_time"] = 10
    result = replay_comparison(data, CONFIG)["predictions"]
    assert [r["recent_history"]["prediction"] for r in result] == [0, 0, 0, 1, 1]


def test_unlabeled_windows_still_contribute_history_and_inputs_are_immutable(monkeypatch):
    import m3.experimental_history as module

    captured = []

    class FakeDetector:
        def __init__(self, config):
            self.model = self

        def predict(self, x):
            captured.append(dict(x))
            return 0, 0, 0

        def learn_one(self, x, y):
            pass

    monkeypatch.setattr(module, "OnlineDetector", FakeDetector)
    data = rows()[:4]
    original = copy.deepcopy(data)
    data[1]["y_true"] = None
    replay_comparison(data, CONFIG)
    transformed = [x for x in captured if "history_sampled_packets" in x]
    assert transformed[2]["history_sampled_packets"] == 3
    assert data[0] == original[0]
    assert all("y_true" not in x and "ground_truth_packets" not in x for x in captured)


@pytest.mark.parametrize('vote, expected', [(None, 'river'), ('log_space', 'log_space')])
def test_archived_history_replay_resolves_vote_explicitly(monkeypatch, vote, expected):
    import m3.experimental_history as module

    seen = []

    class FakeDetector:
        def __init__(self, config):
            seen.append(config.naive_bayes)
            self.model = self

        def predict(self, x):
            return 0, 0, 0

        def learn_one(self, x, y):
            pass

    monkeypatch.setattr(module, 'OnlineDetector', FakeDetector)
    config = dict(CONFIG)
    if vote is not None:
        config['naive_bayes'] = vote
    replay_comparison(rows()[:2], config)
    assert seen == [expected, expected]
