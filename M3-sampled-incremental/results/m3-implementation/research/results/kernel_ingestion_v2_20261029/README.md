# Full study with the repaired collector

Completed 29 October 2026: **54 fresh primary trials accepted, zero failed
attempts**, with all evidence, ablation and sensitivity checks passing.
The dashboard serves exactly these 54 run IDs. The separate pilot and nine
targeted repair checks are excluded.

## Design and validation

- Sampling N = 1, 2, 5, 10, 20, 50; scenarios baseline, constructed drift and
  unseen attack; model seeds 42, 43, 44. All 18 cells have three fresh repeats.
- Official 5G-NIDD packet selections, 100 packets/s replay, model settings,
  0.1-second windows, 41-second warm-up and delayed-label order are unchanged.
- Linux kernel receive timestamps and independent bounded ingestion replace
  userspace receive timestamps. Collection uses verified native Linux storage.
- Every trial passed switch configuration, independent TX/RX, capture-drop,
  raw-hash, prediction-before-label, ingestion timing, drain/tail and independent
  sFlow reception checks. Maximum collector processing lag was **11.894 ms**,
  below the predeclared **100 ms** limit.
- No kernel drops, queue overflows or missing kernel timestamps were recorded.
- All 54 one-second sensitivity analyses completed. Ablations and aggregation
  passed. The analysis reports no missing cells or input read errors.
- Source and protocol hashes remained fixed during measurement. Source
  revision: `6cf8c036d12b387745afce40a0ac871ae36c625f`.
- Six protected document hashes were verified unchanged. The manuscript and
  presentation were not updated to include these results.

## Selected descriptive results

| Scenario | N=1 mean F1 | N=1 F1 range across seeds | N=2 mean F1 | N=1 mean IP bandwidth | N=2 mean IP bandwidth |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 99.44% | 98.62%-99.85% | 96.51% | 160.441 kbit/s | 85.961 kbit/s |
| Drift | 98.97% | 98.57%-99.59% | 96.44% | 141.798 kbit/s | 76.438 kbit/s |
| Unseen | 99.33% | 99.08%-99.53% | 96.90% | 159.749 kbit/s | 85.085 kbit/s |

The predeclared descriptive equal-weight quality/cost criterion selects N=2
in all three scenarios. Higher N still reduces bandwidth and loses information;
not every seed or metric is identical. The study describes controlled emulator
repeatability on fixed packet selections. It does not establish a population
optimum, natural 5G chronology, deployment readiness or publication acceptance.

## Evidence files

- `artifact_manifest.json`: file hashes for this results package.
- `protocol.json`, `matrix.json`, `source_sha256.json`: frozen settings,
  planned cells, completed run IDs and source hashes.
- `trial_index.json`, `study_status.json`, `research_readiness.json`: accepted
  primary run index, completion record and individual evidence gates.
- `aggregated_metrics.csv` / `.json`: mean, sample SD and Student-t intervals;
  individual values remain in the derived evidence archive.
- `derived_trial_evidence.zip`: all 54 summaries, predictions, feature vectors,
  resources, drift logs, ingestion logs and sensitivity results. Original packet
  payloads are omitted from the versioned archive.
- `ingestion_audit.json`: per-trial collector timing, counters and completion.
- Remaining JSON/PNG files: paired comparisons, Pareto results, ablations and
  descriptive replay-pacing audits. Empty failure records mean no measured
  attempt failed in this primary batch.

Raw datagrams, independent captures, oracle evidence and execution records
remain under `output/research/kernel_ingestion_v2_20261028/`. The earlier
dashboard dataset is retained under that study's `previous_dashboard/`.
Earlier result packages remain separate and unchanged, apart from dated
documentation pointing to this completed rerun.

The measured study completed before the subsequent dashboard layout changes;
the latter do not alter measured results. The dashboard API was checked against
all 54 run IDs, and its rendered values and dropdown ordering were inspected.
