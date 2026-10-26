"""
Tabulate the committed M2 results with chance-level references.

    python M2-entropy/summarize_results.py

Reads every results/<run>/metrics.json written by run_m2.py (full-file runs) and the legacy
prefix run results/sensitivity_summary.csv (run_sensitivity.py, first 50,000 rows), and writes:

  results/m2_results_summary.csv          one row per run x window-labelling rule x scope
  results/5gnidd_default/per_session.csv  per-session counts for the default full-file run

Every rate, including the chance references (base rate, precision lift, balanced accuracy,
MCC), is computed by evaluation.metrics_from_counts, the function run_m2.py uses, so the
legacy and current rows share one definition. A detector whose alarms are independent of
the labels has precision equal to the base rate, so precision_lift < 1 means worse than chance.
"""

import json
import sys
from pathlib import Path

M2_DIR = Path(__file__).resolve().parent
if str(M2_DIR) not in sys.path:
    sys.path.insert(0, str(M2_DIR))

import pandas as pd

from evaluation import metrics_from_counts

RESULTS = M2_DIR / "results"
LEGACY_CSV = RESULTS / "sensitivity_summary.csv"
LEGACY_CONFIG = {  # run_sensitivity.py experiments: (k, voting threshold)
    "baseline_k3_vote2": (3.0, 2),
    "sensitive_k2_vote2": (2.0, 2),
    "vote1_k3": (3.0, 1),
}
METRIC_COLS = ["n_windows", "n_attack_windows", "base_rate", "alarm_rate", "tp", "fp", "fn", "tn",
               "precision", "precision_lift", "recall", "f1", "false_positive_rate",
               "balanced_accuracy", "mcc"]


def _row(run, rows, features, k, vote, dport_missing, rule, scope, counts):
    m = metrics_from_counts(counts["tp"], counts["fp"], counts["fn"], counts["tn"])
    return {"run": run, "input_rows": rows, "features": features, "k_sensitivity": k,
            "voting_threshold": vote, "dport_missing": dport_missing, "label_rule": rule,
            "scope": scope, **{c: m[c] for c in METRIC_COLS}}


def full_file_rows():
    out = []
    for path in sorted(RESULTS.glob("*/metrics.json")):
        s = json.loads(path.read_text())
        a = s["arguments"]
        if a.get("max_rows") is not None:
            raise ValueError(f"{path} is not a full-file run (max_rows={a['max_rows']})")
        rules = [(f"malicious fraction >= {a['attack_fraction']}", s["evaluation"]),
                 ("any malicious flow", s["evaluation_any_malicious_flow"])]
        for rule, ev in rules:
            for scope in ("all_windows", "evaluable_windows"):
                out.append(_row(path.parent.name, s["data_quality"]["n_rows"], "SrcAddr, Dport",
                                a["k_sensitivity"], a["voting_threshold"], a["dport_missing"],
                                rule, scope.replace("_", " "), ev[scope]))
    return out


def legacy_rows():
    out = []
    for r in pd.read_csv(LEGACY_CSV).to_dict("records"):
        k, vote = LEGACY_CONFIG[r["experiment"]]
        out.append(_row(f"legacy_prefix_{r['experiment']}", 50_000,
                        "10 attributes (Proto, State, sTtl, sDSb, SrcAddr, Dport, TotPkts, TotBytes, Rate, Dur)",
                        k, vote, "n/a", "any malicious flow", "all windows", r))
    return out


def per_session(run_dir):
    path = run_dir / "windows.csv.gz"
    w = pd.read_csv(path if path.exists() else run_dir / "windows.csv")
    evaluable = ~w["threshold_is_warmup"].astype(bool) & w["threshold_is_valid"].astype(bool)
    alarm = w["window_anomaly"].astype(bool)
    rows = []
    for sid, g in w.groupby("session_id"):
        ev, al = evaluable.loc[g.index], alarm.loc[g.index]
        types = g.loc[g["dominant_attack_type"].fillna("") != "", "dominant_attack_type"]
        half, anymal = g["y_true"] == 1, g["malicious_fraction"] > 0
        m = metrics_from_counts(int((half & al).sum()), int((~half & al).sum()),
                                int((half & ~al).sum()), int((~half & ~al).sum()))
        rows.append({
            "session_id": sid,
            "attack_type": types.mode().iloc[0] if len(types) else "Benign only",
            "windows": len(g),
            "evaluable_windows": int(ev.sum()),
            "dport_unevaluable_windows": int(g["Dport_entropy"].isna().sum()),
            "attack_windows_half_rule": int(half.sum()),
            "attack_windows_any_rule": int(anymal.sum()),
            "alarms": int(al.sum()),
            **{f"{c}_half_rule": m[c] for c in ("tp", "fp", "precision", "recall", "false_positive_rate")},
        })
    return pd.DataFrame(rows)


def main():
    summary = pd.DataFrame(legacy_rows() + full_file_rows())
    summary.to_csv(RESULTS / "m2_results_summary.csv", index=False)
    print(f"wrote {RESULTS / 'm2_results_summary.csv'} ({len(summary)} rows)")
    default = RESULTS / "5gnidd_default"
    if default.is_dir():
        sessions = per_session(default)
        sessions.to_csv(default / "per_session.csv", index=False)
        print(f"wrote {default / 'per_session.csv'} ({len(sessions)} sessions)")
    cols = ["run", "label_rule", "scope", "n_windows", "base_rate", "precision", "precision_lift",
            "recall", "false_positive_rate", "balanced_accuracy", "mcc"]
    with pd.option_context("display.width", 220, "display.max_columns", 20, "display.precision", 3):
        print(summary[cols].to_string(index=False))


if __name__ == "__main__":
    main()
