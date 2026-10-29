# Collector backlog diagnosis and repair

Engineering investigation begun 2026-10-28; repeated verification continued 2026-10-29.
This document records an implementation defect and its verification. It does not
update the manuscript or replace the complete primary experiment matrix.

## Problem

The corrected log-space study completed 54 controlled trials, but some repeated
N=1 and N=2 configurations had large F1 swings. Passing the original evidence
checks did not establish that telemetry had been processed promptly or completely.
The earlier study and all failures are retained as recorded.

The causal collector read UDP telemetry, ran the model, wrote logs and saved
checkpoints in the same loop. Its timestamps were Python receive times. Disk or
model work could delay socket reads, so an older batch of sampled packets was
assigned to a newer 0.1-second feature window. Independent truth described the
newer window, producing mismatched observations. Some runs also left a tail of
telemetry unread when collection ended. Frequent writes to the mounted OneDrive
directory were a plausible contributing source of stalls; the evidence does not
attribute every stall to a particular filesystem operation.

## Evidence from retained runs

The exact prefix of each sampled Ethernet header was matched to the independently
captured victim RX frame. The seven diagnostic runs had unambiguous matches.
RX timestamps are used only for diagnosis and evidence checking, never as input
to the deployed detector.

| Run / condition | Attack F1 | RX-to-Python read delay p95 / maximum |
| --- | ---: | ---: |
| `50a9cfabd3c948409ba967f444f3081b`, baseline N=1 seed43 | 0.4489 | 4.460 / 5.728 s |
| `ef6b6262c44e4f88aeb14797f1607467`, baseline N=1 seed42 | 0.9923 | 0.090 / 0.170 s |
| `4580fd2c59ef4fc0ac76377793004752`, drift N=1 seed44 | 0.6017 | 28.712 / 30.603 s |
| `7314798c3ae5416ca0d8032764b318f3`, drift N=1 seed42 | 0.7868 | 3.292 / 10.895 s |
| `92011ddcf7514e47a341679170bcc388`, drift N=2 seed43 | 0.6339 | 4.265 / 7.191 s |

The bad baseline had 346 empty windows among 679 evaluated windows. The bad
drift seed44 run was missing 1,188 distinct RX frames from retained raw sample
headers, including an unread tail. These are observation defects, not a reason
to choose a favorable model seed or hide low-scoring runs.

`scripts/audit_collector_backlog.py` reproduces the timing/coverage diagnosis from
the saved raw study. It records source/evidence hashes, matching ambiguities,
window mismatches, RX coverage, exporter uptime and stage pacing. Exporter uptime
is quantized to one second and cannot reconstruct precise original packet times.

## Repair

1. `src/m3/ingestion.py` receives datagrams in an independent bounded reader
   thread and preserves Linux kernel UDP arrival timestamps. Overflow, missing
   timestamps, kernel drops, excessive lag or an incomplete drain fail the run.
2. `src/m3/causal_live.py` uses these timestamps for feature windows and saves
   a one-to-one datagram processing log. Timeout watermarks avoid closing a
   window ahead of unread packets. Per-event forced disk flushes are removed.
3. `sdn/run_official_capture_pilot.py` collects into native Linux temporary
   storage. After measurement, it verifies durable copies before cleanup.
   Individual truth-window files are retained byte-identically in a verified
   ZIP. A separate loopback UDP capture independently checks sFlow reception.
4. `sdn/research_validation.py` independently recomputes lag, bin counts,
   datagram agreement and N=1 RX-frame coverage. Kernel-to-read and
   kernel-to-processing maximum lag must be no greater than the declared
   0.1-second primary window. Scores are not acceptance criteria.
5. Protocol signatures separate `kernel_receive` runs from historical userspace
   timestamps. Historical signatures remain unchanged. The dashboard warns
   that earlier collector scores are under review.

Model vote, model parameters, seed list, feature definitions, threshold, window
size, warm-up, delayed-label order and frozen replay selections are unchanged.
The corrected collector still uses deployable sFlow datagram arrival times;
natural exporter batching is not equivalent to precise packet event time.

## Verification and limits

The first repaired pilot reproduced baseline N=1 seed43 with F1 0.993827,
precision 0.987730 and recall 1.0. Maximum kernel-to-processing lag was
0.001922 s; maximum kernel-to-read lag was 0.001700 s. All new gates passed,
including independent UDP capture and complete N=1 tail coverage.

That pilot is a diagnostic validation run, excluded from the primary matrix.
`scripts/validate_collector_repair.py` declares a further targeted check of
baseline N=1, drift N=1 and drift N=2 across seeds42/43/44. The initial repaired
baseline seed43 pilot is reused transparently; eight new runs are planned.
No low-score rejection or automatic outcome-based retry is permitted. The
retained state and results live in
`output/research/kernel_ingestion_v2_20261028/repair_validation/`.

The targeted batch completed on 2026-10-29: all nine runs passed every required
gate, with no failed measured attempts. All raw evidence hashes and six protected
document hashes were verified. Maximum kernel-to-processing lag across the nine
runs was 16.348 ms, below the declared 100 ms limit. There were no recorded kernel
drops, queue overflows or missing timestamps.

| Targeted configuration | Repeats | F1 mean +/- sample SD | F1 range |
| --- | ---: | ---: | ---: |
| Baseline N=1 | 3 | 0.993832 +/- 0.001515 | 0.992320-0.995349 |
| Drift N=1 | 3 | 0.983567 +/- 0.007394 | 0.977413-0.991770 |
| Drift N=2 | 3 | 0.955439 +/- 0.001100 | 0.954635-0.956693 |

The formerly poor drift N=1 seed44 case improved from F1 0.601660 to 0.977413;
drift N=2 seed43 improved from 0.633929 to 0.954635. These are engineering
comparisons between fresh physical repetitions, not a controlled estimate of
the contribution of each individual storage/thread/timestamp change.

The [versioned validation package](../../research/results/collector_repair_20261029/README.md)
contains the seven-run historical audit, nine repaired-run results, derived
evidence and checksums. Raw packet captures and oracle evidence remain in the
local study. The package does not claim to complete the 54-trial primary rerun.

At the time of the initial repair commit, 218 Python tests passed with one
skip; 18 frontend tests passed with four optional integration skips. The
frontend production build and Ruff checks passed. Six protected paper/document
files were verified unchanged against saved hashes.
After the targeted batch, the full Python suite again passed: 218 passed,
one skipped, one existing Starlette/httpx deprecation warning (17.85 seconds).
Graphify reused its saved graph and refreshed the code index to 1,645 nodes;
cached semantic document extraction was not rebuilt. Two focused diagnostic
agents independently investigated model numerics and telemetry timing; the
benchmark workflow preserved the baseline and evaluated the repaired collector
without retuning the detector.

A successful targeted check establishes engineering regression evidence for
these configurations. A separate full 54-trial study was required before
replacing the full sampling comparison or reporting corrected study-wide
means. That [full rerun](../../research/results/kernel_ingestion_v2_20261029/README.md)
subsequently completed on 2026-10-29 with all 54 primary trials accepted,
zero failed attempts and a maximum collector processing lag of 11.894 ms.
All 54 sensitivity analyses and all declared evidence gates passed. The
dashboard now serves the new primary matrix, with the prior dashboard data
preserved separately. The six protected document hashes remain unchanged.
Ordinary differences from live scheduling, OVS sampling and model
randomness remain possible; the fix does not promise identical runs or
monotonic quality as N changes.

## Reproduction

Run live commands sequentially in the existing isolated Linux environment with
the pinned `/opt/m3-sdn/bin/python`. Do not run expensive unrelated workloads
while measuring.

```sh
# Read-only historical diagnosis, after live collection has stopped.
python scripts/audit_collector_backlog.py

# Resume the explicitly separate nine-run engineering check.
/opt/m3-sdn/bin/python scripts/validate_collector_repair.py \
  --study output/research/kernel_ingestion_v2_20261028

# Complete the separate full primary study only after inspecting the pilot.
/opt/m3-sdn/bin/python scripts/finish_corrected_study.py \
  --protocol configs/research_protocol_kernel_ingestion.json \
  --output output/research/kernel_ingestion_v2_20261028
```

The full-study launcher pins source hashes, requires exactly one accepted
separate N=1 pilot, retains failures and verifies paper hashes. Full-study
publication requires an explicit new results directory so earlier evidence
cannot be overwritten accidentally.
