# Reproduce the controlled M3 study

Run from this implementation directory, not the shared repository root. The
experiment requires an isolated Linux/WSL2 Mininet/OVS lab with root privileges.
It creates no physical uplink. Do not run other experiments on its named bridge,
controller port 6653 or sFlow port 6343 while a trial is active.

## 0. Review published results without replaying traffic

After the completed study package is published, its derived archive can populate
the dashboard without downloading the original packet captures. First install
the Python app and build the frontend as described in the README. Choose a new,
empty results destination; do not extract over an existing experiment folder.

```sh
python -m zipfile -e research/results/derived_trial_evidence.zip output/published-study
m3 serve --runs output/published-study --port 8000
```

Open `http://127.0.0.1:8000/`. These are archived validated measurements, not a new
live collection or a fresh local verification of the omitted raw packet files.
The manuscript, per-window records and aggregate CSV are available for inspection.
Full experiment reproduction still requires the official inputs and Linux lab below.

## 1. Install and obtain official inputs

Use the repository setup instructions and inspect scripts before running them:

```sh
sudo bash scripts/setup_sdn.sh
/opt/m3-sdn/bin/python scripts/fetch_dataset.py --file BS2_each_attack_csv.zip --file BS2_each_attack_argus.zip --file 'BS2 GTP removed.zip'
```

The downloader verifies publisher checksums, preserves existing partials, and
extracts verified members. It does not silently accept an incomplete archive.
The complete BS2 packet archive checksum is
`a155cefbe18ec565ac447e5bc1f9faf1b9dc65d565e077c6263a3055a72638d3`.
Keep enough free disk space for archives, extraction and trial evidence.

The live-study reference runtime was CPython 3.12.15 on Linux. For a fresh lab,
`requirements/research-linux.txt` records its installed package versions (without
the original editable checkout path). After setup, apply the snapshot and install
this checkout without changing those dependency pins:

```sh
sudo .tools/uv pip install --python /opt/m3-sdn/bin/python -r requirements/research-linux.txt
sudo .tools/uv pip install --python /opt/m3-sdn/bin/python -e . --no-deps
```

Do not change an environment while a matrix is running. These are version pins,
not a distribution-hash or kernel/OVS image lock. Native tool/kernel versions and
per-trial dependency information remain part of the measurement evidence.

## 2. Restore the exact study label snapshots

For a byte-identical selection recipe, use the published derived annotations:

```sh
/opt/m3-sdn/bin/python scripts/restore_frozen_labels.py
```

This verifies each annotation against the pinned manifest before writing and
refuses to overwrite different existing files. The archive contains derived flow
labels and source-packet mapping annotations, **not original packet payloads**.
Original data and upstream attribution remain required.

Important data-version distinction: the primary study used conservative SYN/ICMP
label snapshots and the binary-confirmed-zero-port UDP snapshot. Re-running the
current general `sdn/prepare_flow_labels.py` can improve other snapshots' port
coverage. That is a different preprocessing version, not an exact replication of
this frozen selection. Do not silently replace the primary annotations.

## 3. Prepare and verify the three frozen scenarios

```sh
/opt/m3-sdn/bin/python sdn/prepare_research_scenarios.py --output-dir data/prepared/research_20261019_equalrate_v1
/opt/m3-sdn/bin/python scripts/restore_frozen_labels.py --verify-prepared data/prepared/research_20261019_equalrate_v1
```

The second command compares generated packet files and mapping CSV bytes with
the published study hashes. Metadata paths can differ between machines; input
packet content and selected source indices must not. The preparer verifies an
existing complete output; it does not overwrite different or incomplete outputs.

## 4. Run the actual switch matrix

```sh
sudo /opt/m3-sdn/bin/python sdn/run_research_matrix.py
```

This executes the locally frozen randomized 54-trial matrix sequentially. It
skips accepted completed cells, retains all raw files, and stops on an integrity
failure. Model settings are fixed, and all selected classes replay at 100 pps.
Expect a multi-hour instrumented study on this software testbed, not a quick
classifier benchmark. No quality threshold selects or rejects trials.

For a diagnosed **technical** failure only, retain its evidence and explain a
retry explicitly:

```sh
sudo /opt/m3-sdn/bin/python sdn/run_research_matrix.py --retry-failed 'Describe the verified technical fix here'
```

Do not retry poor accuracy to select a better outcome. A running/interrupted
cell is not automatically accepted or silently reset. Inspect its saved evidence
and preserve the reason for any recovery action.

## 5. Compute sensitivity, ablations and uncertainty

```sh
/opt/m3-sdn/bin/python scripts/compute_sensitivity.py
/opt/m3-sdn/bin/python scripts/analyse_research.py --output output/research/analysis
```

Analysis recomputes HAT quality from the exact stored sequence and checks it
against primary live scores. It also evaluates nonadaptive HT and a fixed
warm-up-majority dummy. One-second sensitivity reconstructs features from actual
raw exports, rather than averaging 0.1-second ratios. Neither is a live resource
comparison. The final readiness JSON must say 54 accepted trials and `ready=true`.

## 6. Generate the manuscript and derived evidence

Install the optional report dependencies into a suitable project environment:

```sh
python -m pip install -e '.[report]'
python scripts/build_research_report.py
```

The builder refuses incomplete studies and rechecks every linked raw checksum.
The reference PDF build used Windows CPython 3.12.2, ReportLab 4.5.1, pypdf 6.21.1
and Matplotlib 3.11.2. These reporting packages are separate from the frozen Linux
live-study package snapshot.
It creates the manuscript, figures, statistical tables and portable derived
evidence under `research/`, plus the PDF under `output/pdf/`. It never substitutes
illustrative results. Original packets and large raw captures remain local.

Presentation regeneration uses the Codex bundled Artifact Tool runtime. The
editable final PPTX can be reviewed without that runtime. Browser visual checks
were waived by the project user; automated frontend and real-API tests are separate.

## What repeatability means

The frozen inputs and model seeds are reproducible. OVS sampling randomness and
host scheduling are not seeded. Therefore repeated measurements need not match
bit-for-bit. Compare uncertainty, class support and per-trial results. The study
does not establish generalization to new captures, line-rate floods or physical 5G.
