# M3: sampled telemetry and adaptive DDoS detection

This project implements **M3 only** using the **official 5G-NIDD release**. It combines an incremental Hoeffding Adaptive Tree with ADWIN, retains raw measurements, and separates offline model checks from genuine live SDN evidence.

**Status reviewed: 16 October 2026. Latest saved experimental checkpoint: 11 October 2026.**

The core software is implemented, an official-data flow-record pilot has completed, and real SDN forwarding and sampled-telemetry collection have been verified. **The complete official-packet live attack study is not finished.** This README distinguishes implemented features, measured evidence and planned work. Passing a software test is not the same as proving attack-detection performance.

## Project objective and scope

M3 asks: **How much monitoring overhead can we remove through sampling while retaining useful DDoS detection?** Instead of mirroring all packets to the controller, Open vSwitch exports sampled packet headers through sFlow. The collector builds one-second traffic windows, and an incremental Hoeffding Adaptive Tree predicts flooding activity. ADWIN supports adaptation to changing traffic and separately monitors prediction error.

The intended complete pipeline is:

```text
Verified official captures + independently verified labels
    -> documented trace preparation and isolated Mininet replay
    -> Open vSwitch sampling at 1/N -> sFlow collector
    -> one-second features -> HAT/ADWIN
    -> raw predictions, resource measurements and drift events
    -> FastAPI/React dashboard, final analysis and report
```

- Included: benign vs UDPFlood, SYNFlood and ICMPFlood; live SDN; reproducible experiments; accuracy-versus-overhead analysis and dashboard.
- Excluded: M1/M2 implementation, partner dependencies, scans, application-layer attacks, malware payload analysis and physical 5G/RAN deployment.
- This is detection and evaluation, **not automatic attack blocking or mitigation**.
- Official data is required; synthetic fixtures or unofficial data cannot become reported experimental evidence.
- Sampling values are **N = 1, 2, 5, 10, 20, 50**. N=1 is the unsampled reference. N=10 exports roughly one in ten eligible packets; switch sampling is probabilistic, not necessarily every tenth packet.

## Work implemented so far

| Area | What exists | Verification boundary |
|---|---|---|
| Official data acquisition | Official-release downloader, publisher checksums, extraction safeguards and provenance manifest | CSV and BS2 Argus inputs verified; required packet archive still incomplete |
| Data processing | Official label normalization, flood-family filtering, numeric feature allowlist and dataset audit | Labels, attack tools, addresses and identifiers are not model inputs |
| Online model | River HAT, internal ADWIN branch adaptation and a separate prediction-error ADWIN alarm monitor | Predict/score before learning; initial warm-up excluded from scoring |
| Offline evaluation | CSV flow replay, PCAP packet-window replay, sampling and three-trial offline sweeps | Packet matching/counting tested in software; official-capture coverage still needs validation |
| Ground truth | Checked CSV-to-Argus flow-label preparation and conservative packet-to-flow interval matching | Verified flow labels are not proof that every capture packet can be labelled |
| Live SDN | Isolated four-host Mininet/OVS topology, OS-Ken controller, sFlow exporter/decoder and live collector | Benign diagnostics verified; scored official-attack replay pending |
| Measurements | Quality metrics, inference timing, process CPU/memory, optional controller CPU, OpenFlow capture and OVS entry observations | Measured, estimated and unavailable values remain distinct |
| Evidence storage | Unique run IDs, settings, provenance, raw prediction/resource/drift logs and atomic summaries | Failed runs and logs retained instead of silently replaced |
| Backend/dashboard | Read-only FastAPI run API and React/TypeScript run selection, metrics, timelines, drift and comparison views | Dashboard displays saved evidence; it does not start training or collect traffic |
| Analysis | Comparable-run grouping, individual trial links, mean/sample standard deviation, charts and measured-cost Pareto analysis | Existing charts are preliminary, not the completed sampling study |
| Packaging | Python CLI, frontend build, setup scripts, tests and supporting documentation | A Git checkout does not include downloaded data or saved experiment outputs |

### Ground-truth safeguards

- CSV labels are joined to Argus records using unique file offsets, preserving full epoch intervals and numeric ports.
- TCP/UDP packets match bidirectional addresses, ports, protocol and time. ICMP matches endpoints, protocol and time, without invented pseudo-ports.
- Unmatched packets, invalid headers and contradictory overlapping labels remain unknown.
- An offline window is positive if it contains a verified flood packet; negative only when all original packets are known benign, or the window is empty. Otherwise it is unscored.
- Ground truth uses the original packet stream independently of N; only observed model features are sampled.
- Live scoring still requires verified replay timing and mappings. A capture filename alone is never ground truth.

## What has actually been verified

These are saved checkpoint results, not claims that tests or experiments were rerun on 16 October. The original record is in [verification-status.md](docs/verification-status.md).

### Official data and flow labels

- Combined official CSV: **1,215,890 records**, with per-session CSVs and BS2 Argus metadata available locally and provenance checked.
- Official labels joined to **314,757 flows**: ICMP session 14,452; SYN session 14,108; UDP session 286,197. These are session flow totals, not malicious-packet counts.
- Join checks found no missing rows or contradictions in offsets, endpoints, protocol, packet/byte counts, duration and displayed timestamps.
- At the 16 October review, the required GTP-removed capture archive remained a partial download. It cannot be accepted until complete and publisher-checksum verified. A partial file does not establish an active download process.

### Official UDPFlood2 CSV pilot

Run ID: `3b972edbde1a487a9fd5accd9f075b5a`.

| Item | Saved value |
|---|---:|
| Input flow records | 20,000 |
| Warm-up / evaluated records | 1,000 / 19,000 |
| Sampling N | 1 |
| Attack precision | 0.999943 |
| Attack recall | 0.986966 |
| Attack F1 | 0.993412 |
| ROC-AUC | 0.999534 |
| False-positive rate | 0.000739 |
| Mean inference latency | 0.112 ms |

**Interpretation:** this limited flow-record prefix validates the online learning/scoring pipeline. F1 is not overall accuracy. These are not live packet-detection results, a held-out batch test, complete-release performance or results across all sampling rates. Experimental learning receives the true label immediately after each prediction.

An initial official session-label parsing failure was retained, diagnosed and corrected. A separate benign-only prefix cannot establish attack recall or ROC-AUC; unavailable measurements were not invented.

### Real SDN diagnostics

| Diagnostic | N=1 | N=10 |
|---|---:|---:|
| Ping loss | 0% | 0% |
| Received sFlow UDP datagrams | 161 | 25 |
| Exported flow samples | 1,033 | 97 |

These verify real forwarding and sample export with benign probes. They are not repeated attack experiments or the final accuracy-versus-overhead comparison.

Live run `3506ba4c54344f20a1ee2bf4eeb533d4` received **1,051 decoded samples over 22 windows**, with actual controller CPU, OpenFlow traffic and OVS entry observations. Its windows were unlabelled, so detection quality was not scored. Received samples are not the total unsampled dataplane packet count.

### Software, interface and publication checks

- Recorded backend/model/protocol/API checks: **33 tests passed**.
- Recorded frontend checks: **13 tests passed**, including three using actual saved API data; production build passed.
- Recorded production-dependency audit: zero vulnerabilities. This is not a full security audit.
- Desktop/mobile connection-error layouts visually inspected. Populated panels have automated render checks, but populated desktop/mobile visual inspection remains pending.
- Core implementation milestones published inside the M3 results subfolder, preserving shared repository history and other methods.

## Remaining implementation and delivery plan

The remaining sequence is dependency-based. The original one-week target is historical, not a claim that the deadline was met; a revised submission date must be set separately.

| Order | Work to complete | Expected output / completion check |
|---|---|---|
| 1 | Finish the required official packet download, verify publisher checksum and extract | Verified archive/captures in the provenance manifest; partial files never used as final inputs |
| 2 | Validate packet-to-flow labels against actual captures | Coverage, unmatched/ambiguous packet counts, overlap and timestamp-alignment audit |
| 3 | Prepare official traces and validate offline packet-window scoring | Documented address/MAC/time transformations, parent/derived checksums, verified labels and a packet-path pilot |
| 4 | Complete scored live replay | Official traffic through the isolated switch, synchronized annotations and one reproducible labelled live run |
| 5 | Finalize baseline, drift and unseen-attack scenarios | Exact segments/order, source references, class mix, attack/drift boundaries and configuration files |
| 6 | Implement live sweep orchestration and execute trials | Actual OVS reconfiguration for every N, fresh model per trial, three trials per configuration, raw evidence and retained failures |
| 7 | Complete timeliness and robustness analysis | Detection delay, verified unsampled packets-to-detect, unseen-attack recall and an implemented/documented recovery criterion |
| 8 | Produce final analysis | Individual values, mean/sample standard deviation, quality/cost curves, Pareto front, justified sampling choice and limitations |
| 9 | Finish UI and deliverables | Populated desktop/mobile visual QA, regression checks, final report, slides, demo notes and rehearsed reproducible demo |

### Planned experiment matrix

- Six sampling values: `1, 2, 5, 10, 20, 50`.
- Three scenarios: baseline, documented drift and unseen attack.
- Three trials per configuration, with recorded seeds/run identifiers.
- Keep dataset segment, feature schema, replay rate, hardware, model settings, warm-up and decision threshold fixed when comparing N values.
- With one configuration per scenario: **18 trials per scenario, or 54 planned live trials**. This matrix has not been completed.
- The unseen scenario excludes SYNFlood from initial learning and introduces it later. Document subsequent labelled adaptation separately from first-exposure performance.
- Select the sampling rate using genuine quality and cost measurements, not the best individual run. No final best N has been established.

### Required metrics and remaining evidence

| Measurement | Current position | Remaining evidence |
|---|---|---|
| Precision, recall, F1, ROC-AUC, false-positive rate | Implemented; limited CSV pilot measured | Scored official live trials with appropriate class coverage |
| Inference latency | CSV pilot measured | Comparable scored live-window measurements |
| Detector/controller CPU and memory | Collection implemented; live resource diagnostics recorded | Sampling comparisons with monitored processes clearly identified |
| sFlow/OpenFlow bandwidth and OVS entries | Real lab measurement paths verified | Attack-trial comparisons, separately identifying channels and counted bytes |
| Detection time | Not established for official live attacks | Verified attack onset and first correct alarm; distinguish wall-clock from capture-time proxies |
| Packets-to-detect | Offline original-packet counting implemented/tested | Real-capture validation and trustworthy unsampled live packet counts |
| Unseen-attack recall | Metric path exists | Completed withheld-family scenario and trials |
| Post-drift recovery time | Unavailable; analysis still needs implementation | Annotated boundary, predefined recovery threshold/window and calculation |

## Evidence rules and limitations

1. Use the authors' official Fairdata release, not an unofficial mirror. The source DOI is [10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361](https://doi.org/10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361); attribution and license details are in [data-source.md](docs/data-source.md).
2. CSV flows (`flow-v1`) and PCAP/live packet windows (`packet-window-v1`) use different schemas and units. Do not mix their models or experimental conclusions.
3. Combined CSV row order alone does not prove natural chronological drift or physical detection delay.
4. Predict before learning. Immediate ground-truth labels are an experimental assumption, not an automatic production capability.
5. Do not double-sample live traffic: OVS samples; the collector processes the received samples.
6. Missing or undefined measurements are `null` with reasons, not zero. Known zero is a different result.
7. Estimated serialized CSV payload size is not measured live network overhead. sFlow and OpenFlow are separate channels. CPU percentages identify the monitored process and use 100% for one logical CPU.
8. Preserve every trial, failure, exclusion, configuration and raw measurement. Software-test fixtures never become experimental evidence.
9. Benign connectivity, drift alarms alone and a strong CSV pilot do not establish live attack detection, successful drift recovery or physical 5G deployment.

## Repository map

```text
configs/            Pilot and live-diagnostic settings
src/m3/             Model, evaluation, packet/sFlow handling, metrics, storage, API and CLI
scripts/            Official downloader and Linux setup
sdn/                Controller, topology, label preparation and diagnostics
frontend/           React/TypeScript dashboard and tests
tests/              Python/model/protocol/API checks
data/manifest.json  Official and prepared input provenance
docs/               Implementation contract, source notes and saved verification checkpoint
output/             Generated local evidence; run/analysis/SDN/PDF outputs excluded from Git
```

Supporting documents: [implementation contract](docs/implementation.md), [official data provenance](docs/data-source.md), [verification checkpoint](docs/verification-status.md) and [SDN setup/replay](sdn/README.md).

Supplementary local work: a line-by-line learning guide exists under `docs/code-guide/`, with a local packaged copy under `output/code-guide/`. These are currently untracked and are not included in this README-only publication.

## Quick start (Windows, project root)

Run these commands from the M3 implementation directory, not the shared repository's top level. Requirements: Python 3.12, Node.js/npm for the dashboard, and Ubuntu/WSL for live SDN. Downloads require internet access and sufficient disk space. A fresh checkout contains neither the dataset nor saved experiments.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe scripts/fetch_dataset.py
.\.venv\Scripts\m3.exe audit data/raw/Combined/Combined.csv
.\.venv\Scripts\m3.exe run --config configs/official_csv_pilot.json
```

Build the dashboard before starting `m3 serve`:

```powershell
Set-Location frontend
npm ci
npm run build
Set-Location ..
.\.venv\Scripts\m3.exe serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Starting the app does not create experimental results; a fresh checkout may show no runs. For development, start `npm run dev` from `frontend`; its API requests are forwarded to port 8000.

## Live SDN

See [SDN setup](sdn/README.md) and [data provenance](docs/data-source.md). Linux/WSL hosts Mininet, Open vSwitch and OS-Ken. The collector must run in the same network namespace as the sFlow target (normally inside WSL).

```bash
sudo bash scripts/setup_sdn.sh
sudo /opt/m3-sdn/bin/python sdn/validate_sflow.py
sudo /opt/m3-sdn/bin/python sdn/run_live_validation.py
```

The tested native Linux runtime is `/opt/m3-sdn`. The validation scripts start diagnostic components; they are not labelled flood experiments. For manual controller/collector/topology startup and bounded trace injection, follow [sdn/README.md](sdn/README.md). Replay must remain inside the isolated lab.

The supplied live config validates telemetry **without inventing attack labels**. It is not a scored attack experiment. Official capture replay additionally requires a verified trace manifest entry and independently justified ground-truth annotations; capture filenames are not labels.

## Evidence and experiments

- `output/runs/<run-id>/`: immutable run identity, config/provenance, prediction CSV, resource CSV, drift CSV, final summary; live runs also retain raw sFlow datagrams.
- `m3 sweep --config <csv-or-pcap-config>`: N=1,2,5,10,20,50, three recorded seeds per configuration. This is **offline**; live sweeps must also reconfigure OVS for each N.
- `m3 analyse`: comparable groups, individual-run links, mean/sample standard deviation, charts and measured-cost Pareto front. Fixtures are excluded.
- Metrics unavailable in a mode are `null` with a reason, never fabricated zero.
- CSV flow models and packet-window models use different feature schemas. They cannot be mixed as one experiment or used interchangeably.
- `Combined.csv` has no validated timestamps: row-order experiments are not evidence of natural chronological drift or physical detection delay.
- Binary target: Benign vs UDPFlood/SYNFlood/ICMPFlood. Scans and HTTP/app attacks are excluded. Labels/tools/addresses/IDs are not model features.
- Online evaluation predicts, logs and scores **before** learning. Learning uses immediate oracle ground truth for the experiment; deployment does not magically have these labels.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check src tests
```

Frontend: `npm test` and `npm run build` from `frontend`. Tests use explicitly isolated fixtures; fixture values must never be reported as experimental results. See [implementation contract](docs/implementation.md) for limitations and measurement definitions.

## Packet ground-truth preparation

After the default CSV download, fetch the BS2 Argus archive with `python scripts/fetch_dataset.py --file BS2_each_attack_argus.zip`. Inside Ubuntu with the Argus `ra` reader installed, run `/opt/m3-sdn/bin/python sdn/prepare_flow_labels.py`. This validates a one-to-one Offset join against official CSV labels and registers prepared numeric/time tables and their two-parent checksums. The code rejects inconsistencies instead of labeling an entire capture by its filename.

For offline packet evaluation, set `mode` to `pcap_replay`, `input_path` to a checksum-verified official capture and `flow_labels_path` to its matching `data/prepared/BS2_<family>_flow_labels.csv`. Full original packet labels determine window truth independently of the sampled feature stream. Packet-match coverage must be checked before using results. This path is not a substitute for scored live replay.

The downloader's `--list` option lists official files; `--file` selects one; `--captures` requests both GTP-removed archives (approximately 3.9 GB total). Requesting a download does not establish completion. There is no finished single end-to-end command for scored live attacks yet.

## Final completion checklist

- [x] Implement ingestion, online model, evidence storage, API and dashboard.
- [x] Verify a limited official CSV pilot and retain failed-run evidence.
- [x] Verify real forwarding/sampling at N=1 and N=10 with benign probes.
- [x] Prepare and verify official CSV-to-Argus flow-label joins.
- [ ] Complete and checksum-verify required official packet captures.
- [ ] Validate real-capture packet-label coverage, timing and conflicts.
- [ ] Complete prepared-trace provenance and one scored live attack pilot.
- [ ] Finalize reproducible baseline, drift and unseen-attack scenarios.
- [ ] Complete actual six-rate, three-trial live experiments per scenario.
- [ ] Validate detection delay/packet counts and implement recovery-time analysis.
- [ ] Produce final mean/variation tables, quality/cost curves and sampling choice.
- [ ] Visually check populated dashboard layouts and run final regression checks.
- [ ] Deliver report, slides, demo notes and a rehearsed reproducible demonstration.

## Publishing boundary

The approved remote is `sanjayy-j/ml-ddos-detection-sdn-5g-nidd`, branch `main`. Publish only under `M3-sampled-incremental/results/m3-implementation/`; preserve the rest of the shared repository. This local workspace has its own root history, so do not force-push it over the shared repository. The publication checkout is currently `tmp/publish-m3`; it contains the remote's original history. Copy committed milestones into the approved subfolder, inspect the scoped diff, and push normally. Downloads, environments, temporary files and generated experiment outputs stay excluded.
