# M3: sampled telemetry and adaptive flood detection

Completed controlled M3 study using the official 5G-NIDD release. Status: 20 October 2026.

The implementation, 54-trial live matrix, analysis, research report and presentation are complete. All declared scientific evidence gates pass. This is a bounded SDN-emulator study ready for scientific review, not a claim of production readiness, a new learning algorithm, or guaranteed publication.

## Results and deliverables

- [Research report (PDF)](research/artifacts/M3_Research_Report.pdf)
- [Editable research presentation](research/artifacts/M3_Research_Presentation.pptx)
- [Manuscript source and figures](research/M3_Research_Report.md)
- [Complete mean/SD/95% interval tables](research/results/aggregated_metrics.csv)
- [Evidence-readiness checklist](research/results/research_readiness.json)
- [Reproduction instructions](docs/reproduce-study.md) and [demonstration script](docs/demo-script.md)

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
| Delivery | Report, editable slides/charts, derived evidence archives, dependency snapshot, instructions, tests and demo notes |

## Scope and pipeline

M3 asks how collecting fewer packet headers changes flood-detection quality and monitoring cost. It covers benign traffic and official UDPFlood, SYNFlood and ICMPFlood labels.

```text
Official captures + verified flow labels
  -> frozen selections -> isolated replay -> actual OVS sFlow sampling
  -> 0.1-second windows -> HAT prediction -> independent oracle label -> learning
  -> saved measurements -> analysis -> read-only API and dashboard
```

- N = 1, 2, 5, 10, 20, 50. OVS sampling is probabilistic.
- Scenarios: baseline, constructed family/cadence shift, and SYN excluded from warm-up.
- Every selected class replays at 100 packets/s. Natural attack intensity and chronology are not preserved.
- N=1 is an unsampled M3 reference, not M1. M1/M2, automatic blocking and physical 5G/RAN deployment are outside scope.
- Addresses, labels, identifiers and packet hashes never enter model features.
- The 0.5-second parameter holds a closed window before prediction. Its experimental label is read immediately afterward.

## Main findings

**Correction (second-level review).** The unsampled N=1 trials failed because of the learner, not
sampling: in 8 of 9 trials the tree never split (two redundant, near-perfect features tied below
the Hoeffding bound), and River 0.23's naive-Bayes leaf vote treats an underflowed density as
certainty, so it scored benign windows as attacks. Re-scoring the recorded features with a
log-space vote (`m3.naive_bayes`, now the default; nothing else changed) gives N=1 F1 0.985-0.997
at FPR 0.006-0.016 and N=2 F1 0.959-0.968 at FPR 6.3-8.4%; quality falls as N grows, and the
equal-weight rule still selects N=2 as the quality/cost trade-off. See
[`research/N1_Baseline_Reanalysis.md`](research/N1_Baseline_Reanalysis.md). The results below are
the study as run.

As run, N=2 had the strongest observed mean F1 and is selected by the predeclared equal-weight quality/cost rule in all three primary scenarios.

| Scenario | Selected N | Attack F1 mean +/- sample SD | False-positive rate | Combined IP bandwidth reduction vs N=1 |
|---|---|---|---|---|
| baseline | 2 | 0.956 +/- 0.013 | 8.96% | 46.94% |
| drift | 2 | 0.954 +/- 0.016 | 9.51% | 45.90% |
| unseen | 2 | 0.962 +/- 0.008 | 7.72% | 46.40% |

These are window-level results from three repeats on fixed traffic, not a population-wide optimum or significance claim. Across all 18 cells, mean F1 ranges from 0.595 to 0.962.

As run, the curve is non-monotonic because the N=1 learner failed (see the correction above); aggressive sampling also produces substantial false positives, and still does after the correction. One-second sensitivity changes the observation unit and learning opportunities, giving different quality results. At N=2, drift recovery meets the fixed criterion in 3/3 trials (mean 6.506 seconds from the scheduled shift boundary). External ADWIN alarms do not themselves establish attacks or prove internal HAT adaptation.

Even the selected cells misclassify about 8-10% of benign windows. The study does not establish production readiness or broad zero-day protection.

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
.venv/Scripts/python.exe -m zipfile -e research/results/derived_trial_evidence.zip output/published-study
.venv/Scripts/python.exe -m m3.cli serve --runs output/published-study --port 8000
```

Open http://127.0.0.1:8000/. Extract into a new, empty destination, not over existing experiments. This displays archived validated measurements; it does not replay traffic or freshly verify the omitted raw captures.

The dashboard defaults to measured combined sFlow + OpenFlow IP-layer bandwidth when available. Legacy payload/frame measurements have separate labels. Dashboard dots and rows are individual trials; the report's frontier uses three-trial cell means.

## Reproduce the live study

Follow [reproduce-study.md](docs/reproduce-study.md). Replay requires root privileges in a dedicated Linux/WSL2 Mininet/OVS environment without a physical uplink. Download official inputs, restore the exact annotation snapshots, prepare/hash-check scenarios, and run the matrix. Do not replace primary annotations or retry poor accuracy to select better results.

Core commands after preparation:

```sh
sudo /opt/m3-sdn/bin/python sdn/run_research_matrix.py
/opt/m3-sdn/bin/python scripts/compute_sensitivity.py
/opt/m3-sdn/bin/python scripts/analyse_research.py --output output/research/analysis
python scripts/build_research_report.py
```

The report builder refuses incomplete evidence and rechecks all 594 linked raw-artifact checksums. Original packet payloads, raw exports/captures and environments remain local. See [data attribution](research/results/DATA_ATTRIBUTION.md) and the [Linux package snapshot](requirements/research-linux.txt).

## Verification

- Windows: 139 Python tests passed; measured `m3` coverage is 81%.
- Linux study runtime: 138 passed, one optional PDF-rendering test skipped because reporting dependencies are absent there.
- Dashboard: 18 tests passed, including four real-API checks. Production TypeScript/Vite build passes.
- A primary-study real-API test also passes using only the unpacked published bundle.
- All 54 trials pass independent frame/timestamp, switch-configuration, chronology and raw-hash checks. Saved HAT quality reproduces exactly.
- All 80 prepared packet/mapping artifacts match frozen hashes. Both evidence archives pass CRC/member/path checks.
- Every page of the 11-page PDF and every slide of the 10-slide deck was rendered and inspected. Four slide charts have editable embedded data.
- Browser visual verification was explicitly waived. Automated tests are not a browser visual pass. PowerPoint itself was not opened.
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

Only `M3-sampled-incremental/results/m3-implementation/` is modified in the shared repository. Downloaded data, raw captures, environments, private render/validation files and unrelated local work are excluded.
