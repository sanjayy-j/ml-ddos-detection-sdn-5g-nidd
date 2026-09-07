"""Stage J tests — plotting data-preparation layer.

Tests the loaders, ordering and manifest only; no pixel comparison and
no dependency on model training.
"""

import json

import pandas as pd
import pytest

from evaluation.plots import (
    ATTACK_ORDER,
    FPR_BUDGETS,
    MODEL_DIRS,
    MODEL_LABELS,
    MODEL_ORDER,
    PRIMARY_FPR_CAP,
    TEST_MALICIOUS_PREVALENCE,
    PlotDataError,
    build_manifest,
    load_budgets,
    load_confusion,
    load_curves,
    load_per_attack,
    load_summary,
)


@pytest.fixture
def results_root(tmp_path):
    """A minimal set of the artifacts the plotting layer consumes."""
    # per-model curve files, deliberately written out of canonical order
    for model in reversed(MODEL_ORDER):
        d = tmp_path / MODEL_DIRS[model]
        d.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"fpr": [0.0, 0.5, 1.0],
                      "tpr": [0.0, 0.9, 1.0]}).to_csv(
            d / "test_roc_curve.csv", index=False)
        pd.DataFrame({"recall": [1.0, 0.5, 0.0],
                      "precision": [0.6, 0.9, 1.0]}).to_csv(
            d / "test_pr_curve.csv", index=False)

    ev = tmp_path / "evaluation"
    ev.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({
        "model": list(reversed(MODEL_ORDER)),
        "threshold": [0.471731, -0.062874, 0.478734],
        "test_recall": [0.426182, 0.437687, 0.438040],
        "test_precision": [0.997443, 0.982406, 0.988566],
        "test_f1": [0.597197, 0.605575, 0.607079],
        "test_fpr": [0.001688, 0.012111, 0.007828],
        "roc_auc": [0.850978, 0.850177, 0.852824],
        "pr_auc": [0.864283, 0.879445, 0.867387],
        "train_seconds": [159.63, 3093.58, 31.11],
        "batch_throughput_ms_per_flow": [0.003808, 0.006808, 0.001703],
    }).to_csv(ev / "three_model_fpr1pct_summary.csv", index=False)

    budget_rows = []
    for model in reversed(MODEL_ORDER):
        for cap in reversed(FPR_BUDGETS):
            budget_rows.append({"model": model, "max_fpr": cap,
                                "threshold": 0.5, "recall": 0.53,
                                "fpr": cap / 10, "satisfiable": True})
    pd.DataFrame(budget_rows).to_csv(ev / "three_model_fpr_budget.csv",
                                     index=False)

    attack_rows = [{"group": a, "metric": "recall", "support": 100,
                    **{m: 0.99 for m in MODEL_ORDER}}
                   for a in reversed(ATTACK_ORDER)]
    attack_rows.append({"group": "Benign", "metric": "fpr", "support": None,
                        **{m: 0.005 for m in MODEL_ORDER}})
    pd.DataFrame(attack_rows).to_csv(ev / "three_model_per_attack_type.csv",
                                     index=False)

    pd.DataFrame({
        "model": list(reversed(MODEL_ORDER)),
        "TN": [71549, 70802, 71109], "FP": [121, 868, 561],
        "FN": [63540, 62266, 62227], "TP": [47192, 48466, 48505],
        "n": [182402] * 3,
    }).to_csv(ev / "three_model_confusion_matrices.csv", index=False)
    return tmp_path


# --- constants --------------------------------------------------------------

def test_model_and_attack_constants():
    assert MODEL_ORDER == ("RandomForest", "SVM", "CNN_1D")
    assert set(MODEL_LABELS) == set(MODEL_ORDER)
    assert set(MODEL_DIRS) == set(MODEL_ORDER)
    assert len(ATTACK_ORDER) == 8
    assert ATTACK_ORDER[-1] == "UDPFlood"      # divergent class plotted last


def test_pr_no_skill_reference_is_prevalence_not_half():
    assert TEST_MALICIOUS_PREVALENCE == pytest.approx(0.607077)
    assert TEST_MALICIOUS_PREVALENCE != 0.5


def test_primary_cap_and_budgets():
    assert PRIMARY_FPR_CAP == 0.01
    assert FPR_BUDGETS == (0.001, 0.01, 0.05, 0.10)


# --- loading ----------------------------------------------------------------

def test_load_curves_returns_all_models(results_root):
    curves = load_curves(results_root)
    assert set(curves) == set(MODEL_ORDER)
    for model in MODEL_ORDER:
        assert list(curves[model]["roc"].columns) == ["fpr", "tpr"]
        assert list(curves[model]["pr"].columns) == ["recall", "precision"]


def test_loaders_impose_canonical_model_order(results_root):
    """Artifacts are written reversed; loaders must reorder."""
    assert list(load_summary(results_root)["model"]) == list(MODEL_ORDER)
    assert list(load_confusion(results_root)["model"]) == list(MODEL_ORDER)
    assert list(load_budgets(results_root)["model"].unique()) == list(MODEL_ORDER)


def test_budget_rows_ordered_by_model_then_budget(results_root):
    budgets = load_budgets(results_root)
    for model in MODEL_ORDER:
        caps = list(budgets[budgets["model"] == model]["max_fpr"])
        assert caps == sorted(caps)
        assert tuple(caps) == FPR_BUDGETS


def test_per_attack_ordered_and_excludes_benign(results_root):
    attacks = load_per_attack(results_root)
    assert list(attacks["group"]) == list(ATTACK_ORDER)
    assert "Benign" not in set(attacks["group"])


def test_confusion_rows_reconcile(results_root):
    confusion = load_confusion(results_root)
    for row in confusion.itertuples():
        assert row.TN + row.FP + row.FN + row.TP == row.n


# --- error handling ---------------------------------------------------------

def test_missing_curve_file_raises(results_root):
    (results_root / MODEL_DIRS["SVM"] / "test_roc_curve.csv").unlink()
    with pytest.raises(PlotDataError, match="not found"):
        load_curves(results_root)


def test_curve_with_wrong_columns_raises(results_root):
    pd.DataFrame({"x": [1], "y": [2]}).to_csv(
        results_root / MODEL_DIRS["CNN_1D"] / "test_pr_curve.csv", index=False)
    with pytest.raises(PlotDataError, match="missing columns"):
        load_curves(results_root)


def test_empty_artifact_raises(results_root):
    (results_root / "evaluation" / "three_model_fpr_budget.csv").write_text(
        "model,max_fpr,recall,fpr\n", encoding="utf-8")
    with pytest.raises(PlotDataError, match="empty"):
        load_budgets(results_root)


def test_summary_missing_a_model_raises(results_root):
    path = results_root / "evaluation" / "three_model_fpr1pct_summary.csv"
    frame = pd.read_csv(path)
    frame[frame["model"] != "SVM"].to_csv(path, index=False)
    with pytest.raises(PlotDataError, match="missing models"):
        load_summary(results_root)


def test_per_attack_missing_type_raises(results_root):
    path = results_root / "evaluation" / "three_model_per_attack_type.csv"
    frame = pd.read_csv(path)
    frame[frame["group"] != "UDPFlood"].to_csv(path, index=False)
    with pytest.raises(PlotDataError, match="missing"):
        load_per_attack(results_root)


def test_missing_required_column_raises(results_root):
    path = results_root / "evaluation" / "three_model_confusion_matrices.csv"
    pd.read_csv(path).drop(columns=["FP"]).to_csv(path, index=False)
    with pytest.raises(PlotDataError, match="FP"):
        load_confusion(results_root)


# --- manifest ---------------------------------------------------------------

def test_manifest_records_provenance_and_caveats():
    figures = [{"filename": "roc_curves_test.png", "title": "ROC",
                "data_source": ["cnn/test_roc_curve.csv"], "split": "test",
                "operating_point": "threshold-independent"}]
    manifest = build_manifest(figures, "generate_plots.py", "2026-01-01T00:00:00")

    assert manifest["stage"] == "J"
    assert manifest["generation_script"] == "generate_plots.py"
    assert manifest["figures"] == figures
    assert manifest["models_retrained"] is False
    assert manifest["predictions_generated_during_plotting"] is False
    assert manifest["thresholds_selected_during_plotting"] is False
    assert manifest["pr_no_skill_reference"] == TEST_MALICIOUS_PREVALENCE
    assert set(manifest["frozen_thresholds"]) == set(MODEL_ORDER)
    assert "not single-flow latency" in manifest["timing_caveat"]
    assert "within-capture" in manifest["evaluation_scope"]
    # manifest must be JSON-serialisable
    assert json.loads(json.dumps(manifest, default=str))["stage"] == "J"


def test_manifest_figure_entries_have_required_fields():
    figures = [{"filename": "f.png", "title": "t", "data_source": ["a.csv"],
                "split": "test", "operating_point": "validation FPR <= 1%"}]
    manifest = build_manifest(figures, "s.py", "2026-01-01T00:00:00")
    for figure in manifest["figures"]:
        for field in ("filename", "title", "data_source", "split",
                      "operating_point"):
            assert field in figure
