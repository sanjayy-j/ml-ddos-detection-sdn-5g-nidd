# Further detector improvements: baseline-gated comparison

## Decision

Keep the original live detector and configuration. None of the three fixed
candidates passed the no-regression checks. The previous recent-history candidate
also remains experimental and is not enabled.

## Fixed candidates

Each variant changes exactly one baseline HAT parameter, with identical telemetry,
ADWIN delta, seed, threshold, warm-up and recorded label-availability order:

1. `majority_leaf`: `leaf_prediction="mc"`, instead of adaptive Naive Bayes.
2. `no_bootstrap`: `bootstrap_sampling=False`.
3. `faster_splits`: `grace_period=50`, instead of 200 examples between split attempts.

All three candidates were declared before evaluation, and all were evaluated on
all 54 archived primary runs. Baseline scored predictions reproduced exactly;
scores matched within 1e-10 and all five required baseline quality metrics within
1e-12. No outcomes, repeats or scenarios were discarded. No parameters were tuned
after inspecting these results.

## N=2 results

These are means across the nine N=2 trials, covering all three scenarios and
three repeats. They are not pooled metrics.

| Detector | False-positive rate | Attack recall | F1 |
|---|---:|---:|---:|
| Unchanged baseline | 8.7316% | 99.8174% | 95.7355% |
| Majority-class leaves | 8.8606% | 90.8150% | 90.6012% |
| No bootstrap | 9.8475% | 99.5894% | 95.1096% |
| Faster split attempts | 8.1051% | 99.4743% | 95.8450% |

The closest candidate, faster split attempts, reduced mean false-positive rate by
0.6265 percentage points (7.1754% relative) and increased F1 by 0.1095 percentage
points (0.1143% relative). However, recall fell by 0.3430 percentage points; pooled
missed attack windows rose from 5 to 15. This does **not** satisfy the requirement
that the new detector must be better without sacrificing attack detection.

The other two candidates worsened all three N=2 headline quality metrics. Across
all rates, majority-class leaves produced apparently attractive false-alarm
reductions but much lower recall, including runs with no positive predictions.
Undefined precision is retained as null/unavailable, never replaced by a favorable
number or omitted from an average without notice.

## Automated checks for future experiments

The isolated comparison module rejects a candidate if:

- The 54-trial matrix is incomplete, duplicated or baseline reproduction is unverified.
- N=2 mean false-positive rate and F1 do not strictly improve.
- Recall decreases in any N=2 repeat, even if the average improves.
- N=2 precision or ROC-AUC decreases.
- FPR, recall or F1 worsens in any of the 18 scenario/rate cell means.
- Required quality metrics are unavailable or invalid.

Even a passing offline quality gate does not authorize deployment: independent
fresh-data confirmation and paired live latency/resource evidence are still
required. These checks govern the experimental comparison runner; the live
pipeline is not silently reconfigured and no automatic promotion is implemented.

## Files and reproduction

- `src/m3/experimental_variants.py`: fixed variants, causal replay, metric aggregation
  and conservative eligibility checks.
- `scripts/compare_detector_variants.py`: full matrix runner and evidence report.
- `tests/test_experimental_variants.py`: causal timing, future-label isolation,
  cloning, missing evidence, hidden regressions and null-metric reporting tests.
- `output/experiments/detector_variants_v1/REPORT.md`: full results and rejection reasons.
- The same output folder contains `comparison.json`, `protocol.json`, `per_trial.csv`,
  complete intermediate trial summaries and per-run prediction traces.

JSON/CSV quality metrics are ratios in [0, 1]; Markdown tables display percentages.
Verification: 164 Python tests passed, with one existing FastAPI/Starlette
test-client deprecation warning. Lint passed for the three new Python files.
Whitespace checks passed, and production `model.py`/`config.py` have no changes.
The work used bounded experiment design, ML evaluation and final self-review;
no subagents were used. The existing Graphify index was left unchanged because
these targeted changes were verified directly against the known model/evaluation sources.

Use a fresh directory to reproduce from the repository root:

```powershell
.venv/Scripts/python.exe scripts/compare_detector_variants.py --output output/experiments/detector_variants_v1_reproduction
```

Reporting initially stopped on undefined precision after all 54 training/replay
comparisons had completed. A reporting-only repair preserved those model outputs
and the original frozen protocol. `--finalize-existing` finished the report without
retraining or changing candidate settings. Original training hashes and separate
report-generation hashes are retained for auditability.

This is exploratory reuse of previously inspected traffic, not untouched held-out
evaluation. Repeats share traffic traces and use recorded oracle labels. The study's
original results, production detector, configuration and knee recommendation are
unchanged. No new live CPU, latency, bandwidth, knee or publication claim is made.
