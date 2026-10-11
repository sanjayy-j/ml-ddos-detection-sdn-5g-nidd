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
