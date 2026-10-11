# M3: sampled telemetry and adaptive DDoS detection

This project implements **M3 only** using the **official 5G-NIDD release**. It combines an incremental Hoeffding Adaptive Tree with ADWIN, retains raw measurements, and separates offline model checks from genuine live SDN evidence.

## Quick start (Windows, project root)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe scripts/fetch_dataset.py
.\.venv\Scripts\m3.exe audit data/raw/Combined/Combined.csv
.\.venv\Scripts\m3.exe run --config configs/official_csv_pilot.json
.\.venv\Scripts\m3.exe serve
```

Open `http://127.0.0.1:8000` after building the frontend (`npm install` and `npm run build` from `frontend`). For development, start `npm run dev`; its API requests are forwarded to port 8000.

## Live SDN

See [SDN setup](sdn/README.md) and [data provenance](docs/data-source.md). Linux/WSL hosts Mininet, Open vSwitch and OS-Ken. The collector must run in the same network namespace as the sFlow target (normally inside WSL).

```bash
bash scripts/setup_sdn.sh
m3 live --config configs/live_telemetry_validation.json
```

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

## One-week delivery sequence

1. Verify official source/checksums and audit labels/features.
2. Pass model/API tests and an official CSV pilot (software validation only).
3. Verify real Mininet connectivity, controller, and sFlow export at N=1 and N=10.
4. Establish trustworthy packet labels and a shared window feature schema for trace replay.
5. Run all six sampling rates with three trials per approved baseline/drift/unseen scenario; preserve failures.
6. Analyse genuine quality-versus-cost measurements, document limitations, and rehearse the live demo.

No M1/M2 implementation or partner-owned tasks are included.

## Packet ground-truth preparation

After the default CSV download, fetch the BS2 Argus archive with `python scripts/fetch_dataset.py --file BS2_each_attack_argus.zip`. Inside Ubuntu with the Argus `ra` reader installed, run `/opt/m3-sdn/bin/python sdn/prepare_flow_labels.py`. This validates a one-to-one Offset join against official CSV labels and registers prepared numeric/time tables and their two-parent checksums. The code rejects inconsistencies instead of labeling an entire capture by its filename.

For offline packet evaluation, set `mode` to `pcap_replay`, `input_path` to a checksum-verified official capture and `flow_labels_path` to its matching `data/prepared/BS2_<family>_flow_labels.csv`. Full original packet labels determine window truth independently of the sampled feature stream. Packet-match coverage must be checked before using results. This path is not a substitute for scored live replay.

## Publishing boundary

The approved remote is `sanjayy-j/ml-ddos-detection-sdn-5g-nidd`, branch `main`. Publish only under `M3-sampled-incremental/results/m3-implementation/`; preserve the rest of the shared repository. This local workspace has its own root history, so do not force-push it over the shared repository. The publication checkout is currently `tmp/publish-m3`; it contains the remote's original history. Copy committed milestones into the approved subfolder, inspect the scoped diff, and push normally. Downloads, environments, temporary files and generated experiment outputs stay excluded.
