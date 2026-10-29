# Targeted collector repair verification

Completed 29 October 2026. **Nine engineering validation runs passed.** This
package is separate from the full 54-trial primary study. The subsequent
[full rerun](../kernel_ingestion_v2_20261029/README.md) is now complete; none of
these nine diagnostic runs was reused as a primary trial.

The selected configurations were baseline N=1, drift N=1 and drift N=2, each
with model seeds42/43/44. The initial repaired baseline seed43 pilot is included
transparently; the other eight runs were collected afterward. Configuration
selection followed the historical timing diagnosis. No F1 cutoff or outcome-based
replacement was used. All nine are marked `validation_pilot` so primary-study
analysis excludes them. No measured attempt failed in this targeted batch.

| Configuration | F1 mean +/- sample SD | Minimum-maximum |
| --- | ---: | ---: |
| Baseline N=1 | 0.993832 +/- 0.001515 | 0.992320-0.995349 |
| Drift N=1 | 0.983567 +/- 0.007394 | 0.977413-0.991770 |
| Drift N=2 | 0.955439 +/- 0.001100 | 0.954635-0.956693 |

The independent kernel clock, ingestion lag, complete-drain/tail and UDP-capture
checks passed for every run. Maximum collector processing lag was 16.348 ms;
the declared limit was 100 ms. No kernel drops, queue overflows or missing
timestamps were recorded. Model settings and frozen traffic selections were
unchanged. Live scheduling, source/exporter batching and OVS randomness still
prevent an expectation of bit-identical repeated scores.

- `validation_results.json`: individual metrics, ingestion statistics, gate
  outcomes, source hashes, historical matching configurations and three-run
  summaries. These are descriptive engineering comparisons.
- `historical_timing_audit.json`: reproducible, read-only diagnosis of seven
  retained old runs. Independent RX times are diagnostic only, never detector
  input. N>1 unsampled RX frames are expected and are not automatically losses.
- `derived_validation_evidence.zip`: all nine saved summaries, feature vectors,
  predictions, resource readings, drift logs and ingestion logs. Member hashes
  are recorded in the results JSON.
- `manifest.json`: hashes and sizes of this package's files.

Raw sFlow datagrams, independent TX/RX/UDP packet captures, oracle records and
complete execution logs remain under
`output/research/kernel_ingestion_v2_20261028/`. The initial pilot is under
`pilot/`; the other eight runs are under `repair_validation/`. Reproducing
independent capture validation requires these retained raw files. This archive
contains derived evidence, not the complete raw capture set.

The earlier studies and failure records are preserved. The dashboard subsequently
switched to the new full kernel-clock study, retaining its earlier study in a
separate backup. The manuscript and presentation
remain unchanged. See [the full engineering note](../../../docs/experiments/collector-backlog-repair.md)
and [the validation runner](../../../scripts/validate_collector_repair.py).
