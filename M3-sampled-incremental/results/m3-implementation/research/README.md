# Controlled M3 study artifacts

The completed primary study contains 54 accepted live trials: three scenarios,
six actual OVS sampling denominators and three repeats. The machine-readable
readiness result reports evidence completeness, not publication acceptance.

## Read and review

- `artifacts/M3_Research_Report.pdf`: 11-page manuscript/report.
- `artifacts/M3_Research_Presentation.pptx`: 10 editable slides, four native charts.
- `M3_Research_Report.md` and `figures/`: manuscript source and mean/SD figures.
- `figures/pareto_baseline.png`, `pareto_drift.png`, `pareto_unseen.png`:
  F1-versus-combined-IP-cost frontiers. These show nondominated three-trial means,
  not confidence regions; all candidates and uncertainty remain in the tables.
- `results/aggregated_metrics.csv` / `.json`: actual metric sample counts, means,
  sample SD, unbounded 95% Student-t intervals and units for all 18 cells.
- `results/paired_deltas.json`: trial-paired changes versus N=1.
- `results/quality_ablations.json`: exact-feature HAT, HT and warm-up-majority scores.
- `results/pareto_recommendations.json`: descriptive mean-quality/cost frontiers.
- `results/experiment_matrix.json`, `trial_index.json`, `failed_attempts.json`:
  run identities, frozen order, raw hashes and retained technical failures.
- `N1_Baseline_Reanalysis.md`, `results/naive_bayes_reanalysis.json` and
  `results/naive_bayes_reanalysis_cells.csv`: why the unsampled N=1 trials failed and
  all 54 trials re-scored with the corrected naive-Bayes vote (second-level review).
  They supersede the manuscript's interpretation of the non-monotonic curve.

## Derived archives

`results/derived_trial_evidence.zip` contains 378 files: summary, per-window
features, predictions, resource/drift logs, sensitivity and original-packet event
hashes for every run. It contains no original packet payloads or raw sFlow exports.

`results/frozen_preparation_annotations.zip` preserves the exact three flow-label
CSVs, 40 mapping CSVs and expected hashes for all 80 prepared packet/mapping files.
Use these snapshots for this study rather than silently regenerating annotations
with later preprocessing logic. Original captures must be downloaded separately.

See `results/DATA_ATTRIBUTION.md` for the official DOI, CC BY 4.0 licence and
transformations. See `SHA256SUMS.txt` for published file checksums.

## Reproduce and interpret

Follow [the reproduction guide](../docs/reproduce-study.md). The derived bundle
can populate the read-only dashboard without replay; this is archived evidence
display, not a new experiment or fresh local verification of omitted raw captures.

The primary window is 0.1 seconds. One-second sensitivity and model ablations are
offline quality checks, not equivalent live resource/latency comparisons. Missing
recovery remains censored. Repeats share fixed traffic and do not establish new
capture/flow independence. N=1 is an unsampled M3 reference, not M1.

All result claims must retain the controlled timing, oracle-label, shared-host and
selected-capture limitations described in the manuscript. Novelty and venue fit
still require human scientific review.
