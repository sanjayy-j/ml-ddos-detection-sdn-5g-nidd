# M3: sampled telemetry and adaptive flood detection

Controlled M3 implementation using the official 5G-NIDD release. Status: 29 October 2026.

**The repaired collector's full 54-trial rerun is complete.** All primary trials,
raw-evidence checks, ingestion checks, ablations and sensitivity analyses passed,
with no failed attempts. The dashboard now serves this new study. Results are
saved separately in [the kernel-clock study](research/results/kernel_ingestion_v2_20261029/README.md).
The earlier studies remain under review after an audit found telemetry backlog,
incorrect time-window assignment and incomplete collection. They are preserved.
The initial pilot and nine [targeted repair checks](research/results/collector_repair_20261029/README.md)
are excluded from the primary matrix. See [the diagnosis and repair](docs/experiments/collector-backlog-repair.md).
The existing manuscript and presentation have not been updated to incorporate
the new study. Passing the experiment gates does not establish novelty,
production readiness or publication acceptance.

**Preparing the report:** use [the current findings and writing checklist below](#preparing-the-report).
The existing report/PDF, slides and root `research/results/` tables describe earlier
studies. Their numbers must be replaced before a new manuscript is submitted.

## Results and deliverables

- [Latest 54-trial results and validation record](research/results/kernel_ingestion_v2_20261029/README.md)
- [Latest mean/SD/95% interval tables](research/results/kernel_ingestion_v2_20261029/aggregated_metrics.csv)
- [Latest evidence-readiness checklist](research/results/kernel_ingestion_v2_20261029/research_readiness.json)
- [Existing report PDF — awaiting revision](research/artifacts/M3_Research_Report.pdf)
- [Existing editable presentation — awaiting revision](research/artifacts/M3_Research_Presentation.pptx)
- [Existing manuscript — use its structure, replace old findings](research/M3_Research_Report.md)
- [Historical mean/SD/95% interval tables](research/results/aggregated_metrics.csv)
- [Historical evidence-readiness checklist](research/results/research_readiness.json)
- [Reproduction instructions](docs/reproduce-study.md) and [demonstration script](docs/demo-script.md)
- [Complete GitHub backup and restore instructions](docs/github-backup.md)

## What was completed

| Area | Completed work |
|---|---|
| Official data | Publisher-verified BS2 captures, checked CSV/Argus flow labels, packet-coverage audits and frozen annotations |
| Ground truth | Exact endpoint/protocol/port/time matches, unknown-label preservation, independent kernel packet timestamps and VLAN restoration |
| Online detector | Packet-window features, River HAT with internal ADWIN adaptation, external error monitoring, prediction before reading the current oracle label |
| Live lab | Isolated four-host Mininet/OVS/OS-Ken lab, actual switch sampling, bounded official-packet replay, full TX/RX verification and zero capture drops |
| Primary study | Six sampling values, three scenarios and three repeats: 54 accepted trials; failures and technical retry history retained |
| Analysis | Quality/resource/timing metrics, censored recovery, mean/sample SD/Student-t intervals, paired comparisons, HT/dummy ablations and one-second sensitivity |
| Application | Read-only FastAPI API and React dashboard with provenance, prediction timelines, drift logs and compatible-run comparisons |
| Delivery | Latest derived evidence and dashboard complete; existing report and editable slides await revision to the new study |

## Scope and pipeline

M3 asks how collecting fewer packet headers changes flood-detection quality and monitoring cost. It covers benign traffic and official UDPFlood, SYNFlood and ICMPFlood labels.

```text
Official captures + verified flow labels
  -> frozen selections -> isolated replay -> actual OVS sFlow sampling
  -> Linux kernel arrival timestamps -> 0.1-second windows
  -> HAT prediction -> independent oracle label -> learning
  -> saved measurements -> analysis -> read-only API and dashboard
```

- N = 1, 2, 5, 10, 20, 50. OVS sampling is probabilistic.
- Scenarios: baseline, constructed family/cadence shift, and SYN excluded from warm-up.
- Every selected class replays at 100 packets/s. Natural attack intensity and chronology are not preserved.
- N=1 is an unsampled M3 reference, not M1. M1/M2, automatic blocking and physical 5G/RAN deployment are outside scope.
- Addresses, labels, identifiers and packet hashes never enter model features.
- The 0.5-second parameter holds a closed window before prediction. Its experimental label is read immediately afterward.

## Preparing the report

### Use one current evidence package

Use **`research/results/kernel_ingestion_v2_20261029/`** for the new report's
experimental findings. Its [manifest](research/results/kernel_ingestion_v2_20261029/artifact_manifest.json)
records the package hashes. The full study contains **54 fresh primary trials**:
six N values, three scenarios and seeds 42/43/44, with three repeats per cell.
The separate pilot and nine repair-validation runs are excluded. No primary
attempt failed, and no low-score run was discarded.

| Material needed by the author | Current source |
|---|---|
| Primary design, fixed model settings and chronology | [Protocol](research/results/kernel_ingestion_v2_20261029/protocol.json) and [kernel-clock configuration](configs/research_protocol_kernel_ingestion.json) |
| All 54 run identities and completed cells | [Matrix](research/results/kernel_ingestion_v2_20261029/matrix.json) and [trial index](research/results/kernel_ingestion_v2_20261029/trial_index.json) |
| Metric means, sample SD, support and 95% intervals | [Aggregated CSV](research/results/kernel_ingestion_v2_20261029/aggregated_metrics.csv) and [JSON](research/results/kernel_ingestion_v2_20261029/aggregated_metrics.json) |
| Individual predictions, features, resource readings and drift events | [Derived evidence archive](research/results/kernel_ingestion_v2_20261029/derived_trial_evidence.zip), containing all 54 runs |
| Collector timing, drops, drain completion and validation | [Ingestion audit](research/results/kernel_ingestion_v2_20261029/ingestion_audit.json) and [readiness gates](research/results/kernel_ingestion_v2_20261029/research_readiness.json) |
| Sampling frontier and the fixed quality/cost selection rule | [Pareto recommendations](research/results/kernel_ingestion_v2_20261029/pareto_recommendations.json); use each entry's scenario metadata to identify its PNG |
| Model ablations and sampling differences | [Quality ablations](research/results/kernel_ingestion_v2_20261029/quality_ablations.json) and [paired deltas](research/results/kernel_ingestion_v2_20261029/paired_deltas.json) |
| One-second sensitivity | Each primary run's `sensitivity.json` inside the derived archive |
| Source/version provenance and pacing limitations | [Source hashes](research/results/kernel_ingestion_v2_20261029/source_sha256.json), per-run summaries and [replay timing audit](research/results/kernel_ingestion_v2_20261029/replay_timing_audit.json) |
| Official input attribution and selection provenance | [Data manifest](data/manifest.json), [data source notes](docs/data-source.md) and per-run provenance |

Raw datagrams, independent TX/RX/sFlow captures, oracle records and full execution
logs remain locally under `output/research/kernel_ingestion_v2_20261028/`.
They are not included in the Git archive of derived results. Do not claim that
extracting the derived archive independently revalidates omitted raw captures.

### Current results to describe

Each row summarizes three primary repeats. F1 and false-positive rate (FPR) are
percentages; the F1 sample SD is expressed in percentage points. Bandwidth is
the mean of measured **sFlow + OpenFlow IP-layer kbit/s**, not telemetry payload
bytes or Ethernet frame bandwidth. Underlying CSV ratio values remain on 0-1.

| N | Scenario | Attack F1 mean +/- sample SD (%) | Mean FPR (%) | Mean combined IP bandwidth (kbit/s) |
|---:|---|---:|---:|---:|
| 1 | Baseline | 99.44 +/- 0.71 | 1.04 | 160.441 |
| 1 | Drift | 98.97 +/- 0.54 | 0.55 | 141.798 |
| 1 | Unseen | 99.33 +/- 0.23 | 1.13 | 159.749 |
| 2 | Baseline | 96.51 +/- 1.71 | 6.75 | 85.961 |
| 2 | Drift | 96.44 +/- 0.52 | 7.24 | 76.438 |
| 2 | Unseen | 96.90 +/- 0.59 | 6.19 | 85.085 |
| 5 | Baseline | 81.62 +/- 1.28 | 42.24 | 40.362 |
| 5 | Drift | 77.88 +/- 3.42 | 47.89 | 36.457 |
| 5 | Unseen | 81.88 +/- 0.58 | 41.55 | 40.439 |
| 10 | Baseline | 71.98 +/- 2.23 | 67.12 | 25.882 |
| 10 | Drift | 71.60 +/- 0.17 | 68.89 | 23.723 |
| 10 | Unseen | 73.58 +/- 0.39 | 68.08 | 25.265 |
| 20 | Baseline | 67.37 +/- 1.46 | 82.48 | 18.032 |
| 20 | Drift | 65.71 +/- 0.11 | 84.45 | 17.177 |
| 20 | Unseen | 69.35 +/- 0.90 | 81.56 | 17.967 |
| 50 | Baseline | 64.18 +/- 1.70 | 88.97 | 13.280 |
| 50 | Drift | 64.96 +/- 0.37 | 89.67 | 13.380 |
| 50 | Unseen | 65.09 +/- 3.61 | 87.01 | 13.294 |

The main finding changes from the older manuscript: **N=1 has the highest mean
F1 in all three scenarios.** The predeclared equal-weight quality/cost criterion
selects **N=2 as a descriptive compromise**, not as the most accurate detector.
Increasing N reduces measured telemetry bandwidth but also increases information
loss; report the substantial false-positive rates at aggressive sampling.
Do not describe F1 as accuracy or label three fixed-traffic repeats as proof of
a population-wide optimum or statistical superiority.

### Section-by-section revision checklist

- [ ] **Abstract and conclusions:** replace the old numerical findings with the
  current study, distinguishing highest detection quality from the N=2 cost trade-off.
- [ ] **Methods:** describe official packet/label provenance, exact frozen
  selections, 100 pps replay, all 18 cells, seeds, 41-second warm-up, 0.1-second
  windows and the 0.5-second holdback. State that timestamps were constructed
  for replay rather than preserving natural 5G chronology.
- [ ] **Collector and model:** explain kernel timestamps, independent bounded
  UDP ingestion, native Linux collection storage and verified durable copying.
  Record log-space naive-Bayes voting, HAT's internal ADWIN adaptation and the
  separate external error-monitor alarms. Preserve prediction-before-label order.
- [ ] **Repair history:** distinguish the earlier numerical-vote correction
  from the later collector-backlog defect. Explain why earlier results were
  superseded, referencing the [engineering diagnosis](docs/experiments/collector-backlog-repair.md).
- [ ] **Validation:** report 54 accepted primary trials, zero failed attempts,
  all declared gates passing and maximum collector processing lag **11.894 ms**
  against a **100 ms** limit. This lag is a separate measure from inference
  latency, detection time and the declared label holdback.
- [ ] **Results and figures:** replace every old table/chart using this package.
  Include precision, recall, F1, ROC-AUC, FPR, class/window support, timing,
  packets-to-detect, CPU, bandwidth, unseen recall and censored recovery.
  Keep unavailable metrics unavailable; never turn them into zeros. Show
  individual repeats, sample SD/intervals, ablations and one-second sensitivity.
- [ ] **Interpretation:** describe remaining seed variation and sparse sampling
  without selecting only favorable runs. An ADWIN alarm is not an attack label,
  and no alarm does not prove absence of a shift. Distinguish individual-trial
  dashboard dots from the report's frontier of three-trial cell means.
- [ ] **Limitations and contribution:** retain fixed source captures, uncontrolled
  OVS randomness/scheduling, oracle supervision, short constructed shifts,
  equal-rate retiming and shared-host emulator limits. The contribution is an
  auditable measurement pipeline and bounded empirical study, not a new learner.
- [ ] **Scope:** this evidence covers M3 only. Any M1/M2 comparison in a combined
  paper needs their independently validated results and compatible metric definitions.
- [ ] **Reproducibility and availability:** verify cited code/data links before
  submission. The [backup guide](docs/github-backup.md) explains source snapshots,
  raw-evidence release assets and fresh restoration. Check the generated backup
  verification receipt before claiming a complete public snapshot. Cloning code
  alone does not download the large raw-evidence archives.
- [ ] **Final review:** check related-work citations, novelty, authorship, venue
  requirements, figure captions and consistency across text, tables and final PDF.

The current [report builder](scripts/build_research_report.py) defaults to older
analysis/run paths and has historical publication-copy metadata in its code.
Do not run its defaults for the new report. Adapt and review that generator
before automated regeneration, or author the revised manuscript directly from
the current evidence package. This README update does not regenerate the report,
PDF, figures or presentation.

## Historical findings under review

<details>
<summary>Earlier studies only — exclude these numbers from the new report</summary>

The values below are retained historical results. They are not current validated
recommendations after the collector defect was discovered. Do not combine their
quality values with measurements from repaired runs.

**Earlier numerical correction (second-level review).** The original N=1 investigation found
that in 8 of 9 trials the tree never split (two redundant, near-perfect features tied below
the Hoeffding bound), and River 0.23's naive-Bayes leaf vote treats an underflowed density as
certainty, so it scored benign windows as attacks. Re-scoring the recorded features with a
log-space vote (`m3.naive_bayes`, now the default; nothing else changed) gives N=1 F1 0.985-0.997
at FPR 0.006-0.016 and N=2 F1 0.959-0.968 at FPR 6.3-8.4%; quality falls as N grows, and the
equal-weight rule selected N=2 in that offline analysis. See
[`research/N1_Baseline_Reanalysis.md`](research/N1_Baseline_Reanalysis.md). The results below are
the original study as run. Correcting the numerical vote did not fix the separate
collector timing defect subsequently identified in fresh live repeats.

As run, N=2 had the strongest observed mean F1 and is selected by the predeclared equal-weight quality/cost rule in all three primary scenarios.

| Scenario | Selected N | Attack F1 mean +/- sample SD | False-positive rate | Combined IP bandwidth reduction vs N=1 |
|---|---|---|---|---|
| baseline | 2 | 0.956 +/- 0.013 | 8.96% | 46.94% |
| drift | 2 | 0.954 +/- 0.016 | 9.51% | 45.90% |
| unseen | 2 | 0.962 +/- 0.008 | 7.72% | 46.40% |

These are window-level results from three repeats on fixed traffic, not a population-wide optimum or significance claim. Across all 18 cells, mean F1 ranges from 0.595 to 0.962.

As run, the curve is non-monotonic because the N=1 learner failed (see the correction above); aggressive sampling also produces substantial false positives, and still does after the correction. One-second sensitivity changes the observation unit and learning opportunities, giving different quality results. At N=2, drift recovery meets the fixed criterion in 3/3 trials (mean 6.506 seconds from the scheduled shift boundary). External ADWIN alarms do not themselves establish attacks or prove internal HAT adaptation.

Even the selected cells misclassify about 8-10% of benign windows. The study does not establish production readiness or broad zero-day protection.

</details>

## Review the published study locally

Use a fresh checkout with Python 3.12 and Node/npm. Run commands from this
implementation directory (in the shared repository:
`M3-sampled-incremental/results/m3-implementation/`), not its repository root.
In PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev,report]"
cd frontend
npm ci
npm run build
cd ..
.venv/Scripts/python.exe -m zipfile -e research/results/kernel_ingestion_v2_20261029/derived_trial_evidence.zip output/published-study
.venv/Scripts/python.exe -m m3.cli serve --runs output/published-study --port 8000
```

Open http://127.0.0.1:8000/. Extract into a new, empty destination, not over existing experiments. This displays archived validated measurements; it does not replay traffic or freshly verify the omitted raw captures.

The dashboard defaults to measured combined sFlow + OpenFlow IP-layer bandwidth when available. Legacy payload/frame measurements have separate labels. Dashboard dots and rows are individual trials; the report's frontier uses three-trial cell means.

## Reproduce the live study

Use the dataset installation and frozen preparation instructions in
[reproduce-study.md](docs/reproduce-study.md). Its default matrix/report examples
describe the historical study; use the explicit kernel-clock commands below for
a new run. Replay requires root privileges in a dedicated Linux/WSL2 Mininet/OVS
environment without a physical uplink. Do not replace primary annotations or
retry poor accuracy to select better results.

Core commands after preparation:

```sh
sudo /opt/m3-sdn/bin/python sdn/preflight.py
sudo /opt/m3-sdn/bin/python sdn/run_official_capture_pilot.py \
  --blocks data/prepared/research_20261019_equalrate_v1/baseline/blocks.json \
  --sampling 1 --research-scenario baseline --seed 43 --trial-id 2 \
  --naive-bayes log_space --telemetry-clock kernel_receive \
  --output-root output/research/kernel_reproduction/pilot/evidence \
  --runs-output output/research/kernel_reproduction/pilot/runs
sudo /opt/m3-sdn/bin/python scripts/finish_corrected_study.py \
  --protocol configs/research_protocol_kernel_ingestion.json \
  --output output/research/kernel_reproduction
```

Use a new, empty study directory. The finish script requires an accepted separate
N=1 pilot, runs the 54-cell matrix, computes sensitivity/analysis, checks source
and raw-artifact hashes and protects existing document hashes. It does not write
a manuscript. Original packet payloads, raw exports/captures and environments
remain local. See the [Linux package snapshot](requirements/research-linux.txt).

## Verification

- Full Linux source including the diagnostic and backup/restore checks:
  247 Python tests passed, one optional report-rendering test skipped. The
  diagnostic modules referenced by historical source fingerprints are included.
- An earlier isolated committed-source audit, using the existing Linux
  dependencies, passed 189 tests with one skipped and restored all 54 current
  runs through its API. That count predates versioning the diagnostic/backup
  tests. See the backup verification receipt for the final remote restore audit.
  A complete fresh-machine dependency installation has not been tested.
- Dashboard: 18 frontend tests passed; four optional integration tests were
  skipped in the latest run. Production TypeScript/Vite build passed.
- Direct API checks matched all 54 served run IDs to the new primary matrix.
  Browser inspection confirmed current values, numeric N/scenario/seed ordering,
  separate selector labels and the revised panel order. Narrow layout was checked.
- All 54 primary trials, raw hashes and collector gates passed; all 54 sensitivity
  analyses completed. Maximum collector processing lag was 11.894 ms.
- All 80 frozen prepared packet/mapping files and six protected document hashes
  were verified. The existing report and slides still describe historical work;
  earlier rendering checks do not validate a revised manuscript that is not written.
- One upstream Starlette/httpx deprecation warning remains; no project test failure is hidden.

Software checks:

```powershell
.venv/Scripts/python.exe -m pytest --cov=m3
.venv/Scripts/python.exe -m ruff check src/m3 sdn scripts tests
cd frontend
npm test
npm run build
```

Real-API frontend checks are opt-in. The full four-check suite uses the local historical evidence store, including CSV and benign diagnostic modes. To check the published primary-study bundle on port 8000:

```powershell
$env:M3_API_URL='http://127.0.0.1:8000'
npm test -- --run src/integration.test.tsx -t 'accepted official realtime'
```

## Repository map

```text
configs/                    Frozen protocol and examples
data/manifest.json          Official/derived provenance and checksums
src/m3/                     Model, telemetry, metrics, evidence store and API
sdn/                        Preparation, observation and live orchestration
frontend/                   Read-only React/TypeScript dashboard
scripts/                    Acquisition, analysis and artifact builders
tests/                      Python regression tests
requirements/               Linux package-version snapshot
research/                   Manuscript, figures, final artifacts and derived results
docs/                       Methods, sources, reproduction, demo and verification
```

## Interpretation and future research

The implemented study is complete within its declared scope. Extensions need a new protocol: flow/session-disjoint held-out captures, natural or varied traffic rates, more independent repeats, operational label delays, and physical-switch/5G validation. These are future research directions, not claims established here.

Read [methods and limitations](docs/research-methods.md), [related work](docs/research-related-work.md), [readiness criteria](docs/research-readiness-gates.md), and the dated [verification record](docs/verification-status.md). Human review must assess novelty, venue fit and scientific claims before submission.

## Publishing boundary

Only `M3-sampled-incremental/results/m3-implementation/` is modified in the shared
repository's source tree. Large original/derived data, raw captures and project
artifacts are stored in the separate backup release described in
[the restoration guide](docs/github-backup.md). Reinstallable environments,
dependencies, credentials and backup transfer caches are excluded.
