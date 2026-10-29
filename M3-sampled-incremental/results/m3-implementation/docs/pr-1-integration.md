# PR #1 integration and verification - 26 October 2026

Reviewed PR: https://github.com/sanjayy-j/ml-ddos-detection-sdn-5g-nidd/pull/1

Head reviewed: `4c97a649c54ae206e20e6443c9f3e46c0e7321a4`, based on `10fc7de`.
All 33 changed files were included in the full local review branch. M3 files were
also integrated into this M3 workspace. Existing local experimental work and all
original live measurements were preserved. This does not merge GitHub main.

## M3 changes from the PR

- Added log-space Gaussian Naive Bayes leaf voting to avoid underflow being
  interpreted as an unpenalised class likelihood.
- Added `RunConfig.naive_bayes`: `log_space` for new standalone runs, or `river`
  for exact historical replay. HAT and the external ADWIN remain separate.
- Updated ablation and sensitivity replay to respect each recorded voting mode;
  absent historical fields mean `river`.
- Added 54-trial offline quality reanalysis, cell CSV, correction report, updated
  documentation and a 29-file artifact checksum manifest.
- Preserved the original 54 live runs, report/PDF/slides and measured timing,
  recovery and CPU evidence rather than relabelling them as corrected live runs.

## M2 changes from the PR

The full repository's `M2-entropy/` contains these changes; it is not another M3
Python package. The local full-repository checkout is `tmp/publish-m3`.

- Added base rate, alarm rate, precision lift, balanced accuracy and MCC.
- Reported both majority-malicious and any-malicious-flow window labelling rules.
- Included full-file results for 1,215,890 flow rows, 24,311 default windows and
  four sensitivity settings, a 23-row summary and a 20-session breakdown.
- Preserved and labelled the superseded 50,000-row legacy experiment.
- Reported weak/chance-level performance and missing-port limitations honestly.

## Additional integration safeguards

1. Correctly restore nested `river`/`log_space` contexts, including exceptions.
   Temporary River rebinding remains single-thread scoped.
2. Include vote mode in generic backend and dashboard comparison signatures;
   absent historical mode equals explicit `river`, not `log_space`.
3. Resolve the unchanged frozen protocol to `river` explicitly in the live
   matrix. A revised protocol may select `model.naive_bayes="log_space"`, but a
   matrix cannot resume under a different vote.
4. Preserve historical voting in the opt-in local history/variant comparison
   modules while respecting explicit corrected modes. These local experiments
   are not automatically promoted or published.
5. Fix lint issues in the new report script without changing its rendered report.

Each behavioural safeguard received a failing regression before its fix.

## Verification performed here

- Original M3 baseline: 164 Python tests passed, one existing warning.
- Integrated M3 workspace: 179 Python tests passed, 82% coverage, same existing
  Starlette/httpx deprecation warning; includes local experimental tests.
- M2: all 159 tests passed using the existing environment.
- Dashboard: 15 unit/component tests passed; four opt-in real-API tests skipped.
  Production TypeScript/Vite build passed. No browser visual pass is claimed.
- All 54 original live quality replays and committed aggregation/frontier checks
  reproduced with maximum difference zero.
- Corrected scientific reanalysis values reproduced within 1e-12. Only two
  diagnostic split merits differed, by at most 8.9e-16. Local Python-runtime
  provenance was retained separately rather than rewriting PR artifacts.
- Both default M2 metric sets recomputed from all 24,311 saved windows matched
  exactly; summary/session tables matched committed Git bytes.
- All 29 research-artifact checksums verified. Original raw captures, reports,
  PDFs and slides were not overwritten. The formatted report renderer reproduced
  the committed correction report exactly.
- Ruff passed for maintained M3 Python source, SDN, scripts and tests.

An initial sandbox-only baseline attempt encountered Windows file-replace and
local-socket access restrictions. Baseline and final suites then passed with
normal local-file/loopback access; these initial environment failures were not
treated as application defects or hidden as passing tests.

## Interpretation

Corrected offline N=1 mean F1 ranges 0.985-0.997 and FPR 0.62%-1.63% across
scenarios. N=2 mean F1 ranges 0.959-0.968, with the original measured bandwidth
roughly 46%-47% lower than N=1. N=2 remains the descriptive equal-weight trade-off,
not the highest-quality corrected detector or a universal operating optimum.

This is offline quality reanalysis, not a new corrected live study. Fresh corrected
live timing/resource/recovery validation and manuscript changes outside this PR
are not silently claimed complete. GitHub merge is separate.
