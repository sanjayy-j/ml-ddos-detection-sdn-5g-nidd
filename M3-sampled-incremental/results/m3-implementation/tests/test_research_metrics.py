"""Research estimators must preserve censoring, pairing, and evidence boundaries."""

import pytest

from m3.research_metrics import (
    aggregate_trials,
    comparison_signature,
    evaluate_ablations,
    paired_deltas,
    physical_detection_metrics,
    post_drift_recovery,
    research_readiness,
    select_pareto,
    student_summary,
)


def test_comparison_ignores_runtime_identity_not_scientific_settings():
    first = {"scenario": "baseline", "config": {"start_epoch": 100, "controller_pid": 12,
             "sampling_rate": 1, "trial_id": 1, "window_seconds": 0.1}}
    second = {"scenario": "baseline", "config": {"start_epoch": 200, "controller_pid": 34,
              "sampling_rate": 50, "trial_id": 3, "window_seconds": 0.1}}
    assert comparison_signature(first) == comparison_signature(second)
    second["config"]["window_seconds"] = 1
    assert comparison_signature(first) != comparison_signature(second)


def test_physical_delay_uses_completion_and_all_original_ip_packets():
    events = [
        {"epoch": 101, "label": 1},
        {"epoch": 101.2, "label": 0},
        {"epoch": 101.3, "label": 1},
        {"epoch": 101.4, "label": 0, "is_ip": False},
    ]
    predictions = [{"observed_time": 1.5, "label": 1, "predicted": 1}]
    result = physical_detection_metrics(predictions, events, 100, 0)
    assert result["detection_time_seconds"] == pytest.approx(0.5)
    assert result["packets_to_detect"] == 3
    assert result["episodes"][0]["censored"] is False


def test_warmup_and_undetected_episodes_are_not_zero():
    events = [{"epoch": 100.1, "label": 1}, {"epoch": 102, "label": 1}]
    result = physical_detection_metrics([], events, 100, 1)
    assert result["detection_time_seconds"] is None
    assert result["episodes"][0]["onset_epoch"] == 102
    assert result["episodes"][0]["censored"] is True
    assert physical_detection_metrics([], events, None, 1)["reason"]


def test_distinct_attack_episodes_and_false_alarms_retained():
    events = [
        {"epoch": 100.1, "label": 0},
        {"epoch": 101, "label": 1},
        {"epoch": 101.1, "label": 0},
        {"epoch": 102, "label": 0},
        {"epoch": 103, "label": 1},
    ]
    predictions = [
        {"observed_time": 0.5, "label": 0, "predicted": 1},
        {"observed_time": 1.1, "label": 1, "predicted": 1},
    ]
    result = physical_detection_metrics(predictions, events, 100, 0, episode_gap_seconds=0.5)
    assert len(result["episodes"]) == 2
    assert result["episodes"][1]["censored"] is True
    assert result["false_positive_alerts"] == 1


def test_invalid_physical_metadata_rejected():
    with pytest.raises(ValueError):
        physical_detection_metrics([], [], 100, -1)
    with pytest.raises(ValueError):
        physical_detection_metrics([], [{"epoch": float("nan"), "label": 1}], 100, 0)


def test_recovery_requires_both_classes_and_sustained_checks():
    rows = [{"observed_time": i, "label": i % 2, "predicted": i % 2} for i in range(50)]
    result = post_drift_recovery(rows, 0)
    assert result["recovery_seconds"] == 39
    assert result["confirmation_time"] == 41
    assert result["censored"] is False
    single = [{"observed_time": i, "label": 0, "predicted": 0} for i in range(60)]
    assert post_drift_recovery(single, 0)["recovery_seconds"] is None


def test_recovery_is_post_boundary_and_resets_streak():
    rows = [{"observed_time": i, "label": i % 2, "predicted": i % 2} for i in range(100)]
    result = post_drift_recovery(rows, 50, window=4, consecutive=3)
    assert result["recovery_seconds"] == 3
    assert result["confirmation_time"] == 55
    with pytest.raises(ValueError):
        post_drift_recovery(rows, 0, baseline_relative=0.95)


def test_three_trial_ci_uses_student_t_and_singleton_is_unavailable():
    result = student_summary([1, 2, 3])
    assert result["mean"] == 2
    assert result["sample_sd"] == 1
    assert result["ci95"][1] == pytest.approx(4.4841377, rel=1e-6)
    assert student_summary([2])["ci95"] is None
    assert student_summary([])["mean"] is None


def run(n=1, trial=1, value=0.9, **overrides):
    result = {
        "run_id": f"{n}-{trial}", "source": "official_realtime_verified", "status": "completed",
        "scenario": "baseline", "sampling_rate": n, "seed": trial,
        "config": {"trial_id": trial, "window_seconds": 0.1},
        "validation": {"accepted": True},
        "metrics": {"f1": {"value": value, "unit": "ratio", "status": "measured"}},
    }
    result.update(overrides)
    return result


def test_aggregate_preserves_missing_and_failed_trials():
    result = aggregate_trials([run(trial=1), run(trial=2), run(trial=3, status="failed")])
    assert result["groups"][0]["metrics"]["f1"]["n"] == 2
    assert result["excluded"][0]["run_id"] == "1-3"
    assert result["groups"][0]["complete_three_trials"] is False


def test_paired_delta_requires_matching_trial_not_unpaired_means():
    rows = [run(1, 1, 0.8), run(1, 2, 0.9), run(10, 1, 0.7), run(10, 3, 0.99)]
    result = paired_deltas(rows)
    assert result[0]["metrics"]["f1"]["mean"] == pytest.approx(-0.1)
    assert result[0]["metrics"]["f1"]["n"] == 1
    assert result[0]["paired_trial_ids"] == ["1"]


def test_pareto_requires_both_measured_channel_costs():
    def point(n, f1, a, b, status="measured"):
        return {"sampling_rate": n, "f1": f1,
                "sflow_bandwidth_kbit_s": {"value": a, "status": status, "unit": "kbit/s"},
                "openflow_bandwidth_kbit_s": {"value": b, "status": "measured", "unit": "kbit/s"}}
    result = select_pareto([point(1, 0.9, 10, 2), point(2, 0.8, 20, 2),
                            point(5, 0.85, 3, 2), point(10, 1, 1, 1, "estimated")])
    assert {p["sampling_rate"] for p in result["front"]} == {1, 5}
    assert result["recommendation"]["sampling_rate"] in {1, 5}
    assert len(result["excluded"]) == 1


def test_ablation_same_sequence_and_no_evaluation_label_leakage():
    rows = [{"features": {"packets_per_second": i}, "label": i % 2, "warmup": i < 10}
            for i in range(30)]
    result = evaluate_ablations(rows, seed=1, grace_period=5)
    assert set(result) == {"hat_adwin", "hoeffding_tree", "majority_warmup"}
    assert all(v["evaluated"] == 20 for v in result.values())
    assert result["majority_warmup"]["fixed_prediction"] == 0


def test_readiness_empty_never_claims_research_complete():
    result = research_readiness([])
    assert result["ready"] is False
    assert result["accepted_trials"] == 0
    assert len(result["missing_cells"]) == 18


def test_csv_prediction_aliases_and_completion_epoch():
    result = physical_detection_metrics(
        [{"completion_epoch": 101.5, "y_true": "1", "y_pred": "1", "phase": "scored"}],
        [{"epoch": 101, "label": 1}], 100, 0)
    assert result["detection_time_seconds"] == 0.5
    assert result["packets_to_detect"] == 1


def test_window_bounds_prevent_previous_episode_alert_assignment():
    events = [{"epoch": 101, "label": 1}, {"epoch": 101.1, "label": 0},
              {"epoch": 103, "label": 1}]
    rows = [{"observed_time": 3.2, "label": 1, "predicted": 1,
             "window_start": 1, "window_end": 1.1}]
    result = physical_detection_metrics(rows, events, 100, 0)
    assert all(episode["censored"] for episode in result["episodes"])


def test_missing_cost_channel_and_duplicate_trials_do_not_pass():
    result = select_pareto([{"sampling_rate": 1, "f1": 0.9}])
    assert result["recommendation"] is None
    assert paired_deltas([run(), run(), run(10)])[0]["reason"]
    assert aggregate_trials([run(), run()])["groups"][0]["metrics"]["f1"]["n"] == 0


def test_incompatible_units_do_not_aggregate():
    first, second = run(trial=1), run(trial=2)
    second["metrics"]["f1"]["unit"] = "percent"
    assert aggregate_trials([first, second])["groups"][0]["metrics"]["f1"]["mean"] is None


def test_ablation_rejects_noncausal_warmup_and_missing_features():
    with pytest.raises(ValueError, match="prefix"):
        evaluate_ablations([{"label": 0}, {"label": 1, "warmup": True}])
    with pytest.raises(ValueError, match="recorded features"):
        evaluate_ablations([{"label": 0, "warmup": True}])


def test_ablation_delayed_labels_require_complete_timing_and_avoid_early_warmup_labels():
    rows = [{"features": {"rate": i}, "label": i % 2, "warmup": i < 3,
             "observed_time": i, "label_available_time": i + 0.5} for i in range(8)]
    result = evaluate_ablations(rows)
    assert result["majority_warmup"]["fixed_prediction"] == 0
    assert "delayed" in result["hat_adwin"]["label_policy"]
    rows[0].pop("label_available_time")
    with pytest.raises(ValueError, match="every completion"):
        evaluate_ablations(rows)


def test_full_matrix_needs_all_evidence_and_no_performance_threshold():
    from m3.research_metrics import VALIDATION_GATES

    runs = []
    for scenario in ("baseline", "drift", "unseen"):
        for rate in (1, 2, 5, 10, 20, 50):
            for trial in (1, 2, 3):
                item = run(rate, trial, value=0.3, scenario=scenario)
                item["validation"].update({gate: True for gate in VALIDATION_GATES})
                item["validation"]["both_classes_scored"] = True
                item["raw_hashes"] = {"rx.pcap": "a" * 64}
                item["research"] = {"ablations_completed": True, "sensitivity_completed": True}
                for key in ("recall", "roc_auc", "false_positive_rate", "cpu_percent_mean",
                            "cpu_percent_p95", "controller_cpu_percent_mean", "controller_cpu_percent_p95",
                            "sflow_bandwidth_kbit_s", "openflow_bandwidth_kbit_s", "inference_latency_ms",
                            "inference_latency_p95_ms", "flow_table_entries"):
                    item["metrics"][key] = {"value": 0.3, "status": "measured",
                                            "unit": "kbit/s" if "bandwidth" in key else "ratio"}
                runs.append(item)
    assert research_readiness(runs)["ready"] is True
    runs[0]["metrics"]["openflow_bandwidth_kbit_s"]["value"] = None
    assert research_readiness(runs)["ready"] is False
    runs[0]["metrics"]["openflow_bandwidth_kbit_s"]["value"] = 0.3
    runs[0]["validation"]["zero_capture_drops"] = False
    assert research_readiness(runs)["ready"] is False


def test_analysis_empty_directory_writes_no_fabricated_results(tmp_path):
    import importlib.util
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "scripts" / "analyse_research.py"
    spec = importlib.util.spec_from_file_location("analyse_research", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.analyse(tmp_path / "missing", tmp_path / "analysis")
    assert result["accepted_trials"] == 0
    assert result["ready"] is False
    aggregate = json.loads((tmp_path / "analysis" / "aggregated_metrics.json").read_text())
    assert aggregate["groups"] == []
    assert not list((tmp_path / "analysis").glob("*.png"))
