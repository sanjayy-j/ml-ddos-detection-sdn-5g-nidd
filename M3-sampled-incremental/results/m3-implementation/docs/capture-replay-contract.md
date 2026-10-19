# Official-packet evaluation increment - 19 October 2026

## Iteration compact

- Goal: move from CSV/benign diagnostics to source-verified official packets and independently validated switch-export evidence.
- User/system action: evaluate binary benign versus UDP/SYN/ICMP flooding; do not add automatic mitigation.
- Data: official Fairdata BS2 GTP-removed archive, publisher SHA256 `a155cefbe18ec565ac447e5bc1f9faf1b9dc65d565e077c6263a3055a72638d3`; official session CSV and Argus parents for labels.
- Primary gate: trustworthy packet labels and exact source-to-transmit-to-receive multiplicities, before accepting quality scores.
- Unacceptable mistakes: filename-derived labels, fabricated missing ports, using partial downloads, silently dropping capture loss, or calling post-hoc inference real-time detection.
- Baseline: saved CSV pilot and benign live diagnostics; neither is a live attack accuracy baseline.
- Model/threshold: keep HAT/ADWIN and threshold 0.5 unchanged; no tuning against the new pilot.
- Evaluation: original SYN packet-window replay first, then a bounded controlled SYN/benign live collection at N=1. The six-rate/three-scenario study remains separate pending work.
- Fallback: retain failed/unlabelled runs and unknown labels; do not promote unvalidated evidence.

## Data preparation and UDP port-zero correction

`scripts/fetch_dataset.py --resume` appends only after an exact HTTP 206 Content-Range response. The official server ignored ranges in the observed probe, so `--restart` preserved the old partial and started afresh. Final size and publisher SHA256 are required before extraction/registration. A failed prefix is never official input.

`sdn/audit_packet_labels.py` verifies both inputs and audits the full original packet stream. Counts distinguish known benign/flood, unmatched key/time, conflicting overlaps, and invalid/nonjoinable headers. `complete` means EOF was scanned, not perfect coverage. A cap produces an explicitly incomplete diagnostic.

The first UDP audit matched no flood packets because Argus 5.0.2 suppressed numeric zero ports in its display. The capture's port-zero values were not used to fill blanks by assumption. Instead, native Argus filters `(tcp or udp) and src port 0` and `(tcp or udp) and dst port 0` independently identified exact source-record offsets. Only blanks confirmed at the same offset and protocol become `0`; other missing values remain unknown. Commands, counts and contradictions are recorded in the preparation audit. The previous prepared input is retained under its SHA256 filename, with its original ancestry in the manifest.

## Controlled block contract

`sdn/prepare_replay_blocks.py` takes explicit source capture, flow-label path, family, count and replay rate per segment. It selects only exact original family matches, retaining source order within each block and saving source indices, original epochs and frame hashes.

Only destination/source Ethernet MAC bytes are rewritten to the isolated victim/sender. Original IP/transport/payload bytes and checksums remain unchanged. Output timestamps are constructed as packet index divided by the chosen rate. Repeated blocks deliberately reuse source selections; the pilot changes class/rate distribution and is not natural chronology, an independent holdout, or a generalization benchmark. Partial/insufficient preparation is not registered as verified.

The supplied six-block SYN pilot alternates 800 benign packets at 100 packets/s and 8,000 verified SYN packets at 1,000 packets/s. These are predeclared controlled rates, not inferred original attack rates. Source blocks are replayed only on private Mininet links without an uplink.

## Independent live-evidence gates

`sdn/run_official_capture_pilot.py` checks connectivity before measurement, bounds replay, records actual commands/counts/times, collects switch exports, and independently captures sender TX and victim RX. Both observed whole-frame multisets must equal the prepared multiset, and both kernel capture-drop counts must be zero. A mismatch or missing evidence leaves the experiment failed. Testbed-only IPv6 is disabled to prevent unrelated router solicitations; host external interfaces are not altered.

Capture files are written on Linux's native temporary storage with a large capture buffer, then copied into the retained experiment directory. The first Windows-mounted capture attempt lost packets and remains failed with logs retained. No missing packets are imputed.

The live collector in this pilot is unlabelled: it does not pretend that independently checked labels were available in real time. Source run identity, raw datagrams, measured controller/channel costs and failed attempts remain saved.

## Recorded-export scoring boundary

`sdn/score_recorded_sflow.py` is explicitly **post-hoc scoring of genuine live switch exports**, not real-time detection accuracy. It revalidates TX/RX data and official block provenance, checks datagram bounds/order/sequence and sampling settings, and builds arrival-clock features from recorded exports. Labels come from the independently observed complete receiver stream, not the sampled subset.

Only nonempty, pure-class receive windows whose sampled headers are compatible with that class are scored. Mixed, empty, ambiguous or unmatched windows remain unlabelled. The model still predicts before its label is revealed and learned. First 24 seconds are warm-up by default. The distinct result source `official_5g_nidd_recorded_sflow` prevents aggregation with live inference or offline source-capture pilots.

Post-hoc classifier latency is not live detector CPU cost. Live collection costs are retained separately. Exact onset delay, live packets-to-detect, drift recovery, unseen-attack success, and the full repeated sampling trade-off are not established by this pilot.

## Reproduce the next stages

From the project directory, after installing the documented environments:

```powershell
.\.venv\Scripts\python.exe scripts/fetch_dataset.py --file 'BS2 GTP removed.zip' --restart
.\.venv\Scripts\python.exe sdn/audit_packet_labels.py --capture 'data/raw/BS2 GTP removed/BS2 GTP removed/SYNflood_BS2_nogtp.pcapng' --labels data/prepared/BS2_SYNFlood_flow_labels.csv --output output/sdn/syn_packet_audit.json
.\.venv\Scripts\m3.exe run --config configs/official_syn_packet_pilot.json
```

Do not use `--restart` unless intentionally preserving/restarting an incomplete transfer; already verified archives are reused. In Ubuntu, from the same project directory:

```sh
/opt/m3-sdn/bin/python sdn/prepare_flow_labels.py --family UDPFlood
/opt/m3-sdn/bin/python sdn/prepare_replay_blocks.py --plan configs/official_syn_controlled_blocks.json --output-dir data/prepared/NEW_UNIQUE_BLOCK_DIRECTORY
sudo /opt/m3-sdn/bin/python sdn/run_official_capture_pilot.py --blocks data/prepared/NEW_UNIQUE_BLOCK_DIRECTORY/blocks.json --sampling 1
/opt/m3-sdn/bin/python sdn/score_recorded_sflow.py --execution output/sdn/ACTUAL_VALIDATED_EXPERIMENT/execution.json
```

Use newly created block directories and the actual validated experiment path printed by the runner. Placeholders above are not existing result directories. Downloaded archives, prepared packets and generated measurements remain excluded from Git; provenance and reproducible code are versioned.
