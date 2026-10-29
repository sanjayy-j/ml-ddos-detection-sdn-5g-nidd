# Recent-history detector: experimental comparison

## Decision

Keep the current live detector. The fixed recent-history candidate improves the
average across the complete sampling matrix, but worsens every N=2 trial's
false-positive rate. N=2 is the existing recommended operating point.

## What was tested

One experimental feature transform adds the current closed window plus preceding
windows covering 0.5 seconds. It adds observed sampled-packet count, integrated
estimated packet/byte rates, packet-weighted size/protocol statistics, empty-window
fraction and consecutive-empty count. Predictions still occur every 0.1 seconds.
No threshold or hyperparameter search was performed.

Both models use the same HAT/ADWIN configuration, seed, recorded observations,
warm-up, evaluation labels and label-availability order. Current and future labels,
ground-truth packet counts, packet identities and absolute time are not features.
Unknown-label windows contribute telemetry context but do not train either model.

All 54 archived baseline trials reproduced their saved scored predictions, scores
(tolerance 1e-10) and F1/recall/FPR (tolerance 1e-12). No trials were excluded based
on performance. Experimental outputs are separate from the original live study.

## Results

These are arithmetic means of per-trial percentages, not pooled metrics.
Percentage-point changes are new minus current. Relative changes divide that
difference by the current value.

| Scope / metric | Current | Experimental | Change in percentage points | Relative change |
|---|---:|---:|---:|---:|
| All 54: false-positive rate | 63.69% | 39.07% | -24.62 | -38.66% |
| All 54: attack recall | 91.92% | 98.40% | +6.48 | +7.05% |
| All 54: F1 | 72.93% | 84.06% | +11.13 | +15.26% |
| Nine N=2 trials: false-positive rate | 8.73% | 12.17% | +3.44 | +39.42% |
| Nine N=2 trials: attack recall | 99.82% | 99.38% | -0.44 | -0.44% |
| Nine N=2 trials: F1 | 95.74% | 93.96% | -1.77 | -1.85% |

False-positive rate improved in 42 of 54 trials, but in zero of nine N=2 trials.
At N=2, pooled false alarms increased from 232 to 322, and missed attack windows
increased from 5 to 14. Counts and mean-rate percentage changes have different
weighting and should not be substituted for one another.

The candidate also regressed strongly in one drift/N=1 repeat; the all-rate average
must not be used to claim universal improvement. Full scenario/rate results,
including regressions, are in the generated report.

## Evidence, reproduction and boundaries

- Runner: `scripts/compare_recent_history.py`.
- Opt-in feature/replay module: `src/m3/experimental_history.py`.
- Tests: `tests/test_experimental_history.py`.
- Results: `output/experiments/recent_history_v1/REPORT.md`, `comparison.json`,
  `per_trial.csv`, `protocol.json`, and per-run prediction logs.
- Verification: 145 Python tests passed; one existing FastAPI/Starlette test-client
  deprecation warning. Lint passed for all three experimental Python files.

From the repository root, run a fresh output directory (existing experiment
directories are intentionally not overwritten):

```powershell
.venv/Scripts/python.exe scripts/compare_recent_history.py --output output/experiments/recent_history_v1_reproduction
```

The protocol records archive and implementation SHA256 hashes, dependency versions,
the single fixed candidate, reproduction tolerances and all evaluation caveats.

This is exploratory offline evidence, not a new live trial or an untouched test
set. Existing traces were inspected during diagnosis, repeats reuse traffic, and
the original oracle-supervised adaptation is retained. There is no new measured
latency, CPU, bandwidth or Pareto-knee evidence. No significance or publication
claim follows from these percentages.

Before promoting a revised candidate: freeze its design, evaluate independent
chronological captures with realistic label timing, compare paired live runs, and
recompute the quality/cost trade-off. The current detector remains unchanged.
