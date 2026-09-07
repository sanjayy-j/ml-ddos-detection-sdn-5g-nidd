"""Stage I tests — evaluation consolidation.

Uses synthetic artifact fixtures written to tmp_path, so nothing here
depends on model training or on the real result files.
"""

import json

import pandas as pd
import pytest

from evaluation.consolidate import (
    ATTACK_TYPES,
    METRIC_TOLERANCE,
    MODEL_ORDER,
    ArtifactError,
    build_confusion_table,
    build_fpr_budget_table,
    build_per_attack_table,
    build_summary_table,
    load_model_results,
    verify_metric_consistency,
)


def _metrics(tp, tn, fp, fn, **overrides):
    """Build a metrics dict with internally consistent rate values."""
    n = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    out = {
        "n": n, "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "accuracy": (tp + tn) / n,
        "precision": precision,
        "recall": recall,
        "f1": (2 * precision * recall / (precision + recall)
               if precision + recall else 0.0),
        "fpr": fp / (fp + tn) if fp + tn else 0.0,
        "tnr": tn / (tn + fp) if tn + fp else 0.0,
        "roc_auc": 0.85, "pr_auc": 0.86, "per_flow_inference_ms": 0.001,
    }
    out.update(overrides)
    return out


# --- metric consistency -----------------------------------------------------

def test_consistent_metrics_pass():
    rows = verify_metric_consistency(_metrics(48505, 71109, 561, 62227))
    assert all(r["consistent"] for r in rows)
    assert max(r["abs_deviation"] for r in rows) <= METRIC_TOLERANCE


def test_inconsistent_metric_is_detected_not_corrected():
    metrics = _metrics(100, 100, 10, 10, accuracy=0.99)   # deliberately wrong
    rows = {r["metric"]: r for r in verify_metric_consistency(metrics)}

    assert rows["accuracy"]["consistent"] is False
    assert rows["accuracy"]["stored"] == 0.99
    assert rows["accuracy"]["recomputed"] == pytest.approx(200 / 220)
    # the caller's dict must be left untouched
    assert metrics["accuracy"] == 0.99
    # other metrics still pass
    assert rows["precision"]["consistent"] is True


def test_n_mismatch_is_detected():
    metrics = _metrics(10, 10, 5, 5)
    metrics["n"] = 999
    rows = {r["metric"]: r for r in verify_metric_consistency(metrics)}
    assert rows["n"]["consistent"] is False


def test_missing_confusion_count_raises():
    metrics = _metrics(10, 10, 5, 5)
    del metrics["TP"]
    with pytest.raises(ArtifactError, match="TP"):
        verify_metric_consistency(metrics)


def test_zero_division_is_handled():
    rows = {r["metric"]: r for r in
            verify_metric_consistency(_metrics(0, 100, 0, 0))}
    assert rows["precision"]["recomputed"] == 0.0
    assert rows["f1"]["recomputed"] == 0.0
    assert rows["fpr"]["recomputed"] == 0.0


# --- artifact fixture -------------------------------------------------------

@pytest.fixture
def results_root(tmp_path):
    """A minimal but complete set of the artifacts Stage I consumes."""
    specs = {
        "RandomForest": ("random_forest", "rf_fpr_constrained_record.json",
                         "test_metrics_fpr_constrained", 0.478734,
                         "per_attack_type_fpr_constrained.csv",
                         (48505, 71109, 561, 62227), True),
        "SVM": ("svm", "svm_run_record.json", "test_metrics", -0.062874,
                "per_attack_type.csv", (48466, 70802, 868, 62266), False),
        "CNN_1D": ("cnn", "cnn_run_record.json", "test_metrics", 0.471731,
                   "per_attack_type.csv", (47192, 71549, 121, 63540), True),
    }
    for model, (folder, record_name, key, thr, attack_csv,
                (tp, tn, fp, fn), collapsed) in specs.items():
        d = tmp_path / folder
        d.mkdir(parents=True, exist_ok=True)
        record = {
            key: _metrics(tp, tn, fp, fn),
            "operating_point": {"threshold": thr, "recall": 0.53,
                                "fpr": 0.005, "primary_fpr_cap": 0.01},
            "validation_metrics_at_frozen_threshold": {"precision": 0.99},
            "timings_seconds": {"train": 31.0},
            "model_structure": {"n_components": 512, "total_parameters": 10561},
            "forest_structure": {"total_nodes": 172630},
        }
        (d / record_name).write_text(json.dumps(record), encoding="utf-8")

        thresholds = [thr] * 4 if collapsed else [thr, thr - 0.01,
                                                  thr - 0.02, thr - 0.02]
        pd.DataFrame({
            "max_fpr": [0.001, 0.01, 0.05, 0.1],
            "threshold": thresholds,
            "recall": [0.52, 0.53, 0.54, 0.54],
            "fpr": [0.0009, 0.009, 0.019, 0.019],
            "satisfiable": [True] * 4,
        }).to_csv(d / "validation_fpr_budgets.csv", index=False)

        rows = [{"group": a, "support": 100, "recall": 0.99, "fpr": None}
                for a in ATTACK_TYPES]
        rows.append({"group": "Benign", "support": 71670, "recall": None,
                     "fpr": fp / (fp + tn)})
        pd.DataFrame(rows).to_csv(d / attack_csv, index=False)
    return tmp_path


# --- loading / error handling ----------------------------------------------

def test_load_model_results_returns_all_three(results_root):
    loaded = load_model_results(results_root)
    assert list(loaded) == list(MODEL_ORDER)
    assert loaded["RandomForest"]["operating_point"]["threshold"] == 0.478734


def test_missing_artifact_raises_artifact_error(tmp_path):
    with pytest.raises(ArtifactError, match="not found"):
        load_model_results(tmp_path)


def test_malformed_json_raises_artifact_error(results_root):
    (results_root / "svm" / "svm_run_record.json").write_text(
        "{not json", encoding="utf-8")
    with pytest.raises(ArtifactError, match="not valid JSON"):
        load_model_results(results_root)


def test_missing_metrics_key_raises(results_root):
    path = results_root / "cnn" / "cnn_run_record.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    del record["test_metrics"]
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ArtifactError, match="test_metrics"):
        load_model_results(results_root)


# --- table construction -----------------------------------------------------

def test_summary_table_ordering_and_columns(results_root):
    table = build_summary_table(load_model_results(results_root))
    assert list(table["model"]) == list(MODEL_ORDER)
    for column in ("threshold", "val_recall", "val_fpr", "test_accuracy",
                   "test_precision", "test_recall", "test_f1", "test_fpr",
                   "test_specificity", "roc_auc", "pr_auc",
                   "batch_throughput_ms_per_flow", "train_seconds",
                   "model_size"):
        assert column in table.columns
    assert (table["operating_point"] == "validation FPR <= 1%").all()


def test_confusion_table_reconciles(results_root):
    table = build_confusion_table(load_model_results(results_root))
    for row in table.itertuples():
        assert row.n == row.TN + row.FP + row.FN + row.TP
        assert row.actual_benign == row.TN + row.FP
        assert row.actual_malicious == row.TP + row.FN
    # every model evaluated the same test split
    assert table["n"].nunique() == 1


def test_fpr_budget_table_flags_collapsed_budgets(results_root):
    loaded = load_model_results(results_root)
    table = build_fpr_budget_table(loaded, results_root)

    assert len(table) == 12                       # 3 models x 4 budgets
    assert list(table["model"].unique()) == list(MODEL_ORDER)
    collapsed = table.groupby("model")["budgets_collapsed"].first()
    assert bool(collapsed["RandomForest"]) is True   # discrete scores
    assert bool(collapsed["SVM"]) is False           # smooth scores


def test_per_attack_table_covers_all_types_and_benign(results_root):
    loaded = load_model_results(results_root)
    table = build_per_attack_table(loaded, results_root)

    assert set(ATTACK_TYPES) <= set(table["group"])
    assert "Benign" in set(table["group"])
    benign = table[table["group"] == "Benign"].iloc[0]
    assert benign["metric"] == "fpr"
    for model in MODEL_ORDER:
        assert model in table.columns
        assert benign[model] is not None


def test_missing_budget_artifact_raises(results_root):
    (results_root / "cnn" / "validation_fpr_budgets.csv").unlink()
    with pytest.raises(ArtifactError, match="not found"):
        build_fpr_budget_table(load_model_results(results_root), results_root)


# --- determinism ------------------------------------------------------------

def test_tables_are_deterministic(results_root):
    loaded = load_model_results(results_root)
    for builder in (build_summary_table, build_confusion_table):
        pd.testing.assert_frame_equal(builder(loaded), builder(loaded))
    pd.testing.assert_frame_equal(
        build_fpr_budget_table(loaded, results_root),
        build_fpr_budget_table(loaded, results_root))
    pd.testing.assert_frame_equal(
        build_per_attack_table(loaded, results_root),
        build_per_attack_table(loaded, results_root))
