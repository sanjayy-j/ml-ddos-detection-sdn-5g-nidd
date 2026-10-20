# M3 isolated SDN testbed

Use Ubuntu/WSL2 as root, from the repository directory. Installation:

```sh
bash scripts/setup_sdn.sh
```

The tested runtime lives at `/opt/m3-sdn` on Ubuntu's native filesystem to avoid
slow imports from the Windows mount. Set `M3_SDN_ENV` when installing if a different
location is needed and substitute that path in the commands below. Validate both
rates with `/opt/m3-sdn/bin/python sdn/validate_sflow.py`; output is saved under
`output/sdn/`, including the actual raw sFlow datagrams as hex.
Run `/opt/m3-sdn/bin/python sdn/run_live_validation.py` to exercise the real M3
collector with independent controller CPU, OpenFlow traffic capture, and OVS
flow-table observations. The saved run remains `live_sflow` with quality metrics
unavailable because connectivity-probe traffic has no academic attack labels.

Start the OS-Ken learning switch controller in one terminal:

```sh
/opt/m3-sdn/bin/osken-manager --ofp-tcp-listen-port 6653 sdn/controller.py
```

Start `m3 live --config CONFIG.json` in a second terminal. Configure `bind` as
`127.0.0.1`, `port` as `6343`, and `sampling_rate` to match the topology.
Run collector, controller, and Mininet in the same Ubuntu network namespace.
Use `controller_pid` to measure the actual controller process CPU.

Start the topology in a third terminal:

```sh
/opt/m3-sdn/bin/python sdn/topology.py --sampling 1 --probe --duration 15
/opt/m3-sdn/bin/python sdn/topology.py --sampling 10 --probe --duration 15
```

These probes create benign ICMP traffic and validate forwarding and real switch
sampling. They do not supply attack evaluation results. Exported sFlow comes
from `m3s1` via OVS, rather than full PacketIn mirroring. Polling interval is one
second; packet header snapshots are 256 bytes. All hosts are private Mininet
namespaces with no physical/uplink interface.

`output/sdn/topology.json` records ping loss, sampling configuration, forwarding
rules, datapath, and replay metadata. Forwarding must achieve zero ping loss.
Default userspace OVS uses `/dev/net/tun`; `--datapath kernel` can be selected on
a host with an available OVS kernel module.

## Official trace replay

Obtain capture archives through `python scripts/fetch_dataset.py --captures`.
Original archives are checksum-verified and preserved. Captures must be prepared
as Ethernet PCAP with documented source/destination IP and MAC rewrites into
`10.77.0.0/24`. Each transformed file needs a manifest entry containing its
checksum, parent checksum, and transformations. The topology does not rewrite
traffic or manufacture labels:

```sh
/opt/m3-sdn/bin/python sdn/topology.py --sampling 10 --duration 80 \
  --pcap data/prepared/verified_trace.pcap --pps 1000
```

Replay is limited to at most 10,000 packets/s and the isolated `m3a1-eth0` link.
The runner's separate label schedule must use verified official capture metadata,
not the filename alone. Use a common `start_epoch` in runner configuration and
replay scheduling when producing scored results. No labels means telemetry-only
validation; the runner should mark detection-quality metrics unavailable.

Current implementation provides a topology and optional trace injection. Exact
timestamp/address ground truth and transformed official captures must be verified
before scoring live replay.

## Verified flow supervision

The small official `BS2_each_attack_argus.zip` archive supplies exact epoch times
and numeric ports omitted or abbreviated in its corresponding session CSVs.
Install `argus-client`, fetch that archive, then run:

```sh
python scripts/fetch_dataset.py --file BS2_each_attack_argus.zip
/opt/m3-sdn/bin/python sdn/prepare_flow_labels.py
```

This exports full `ra -n -u` records and joins each to its official CSV label via
a unique file Offset. It checks exact endpoint/protocol/packet/byte fields, duration
precision, and the CSV's abbreviated displayed timestamps. Argus management
records are excluded explicitly. Mismatches retain an unverified partial file
and prevent provenance registration. Prepared flow intervals, audits, and both
official parent SHA256 values are recorded under `data/prepared/` and the manifest.
Packet matching still needs timestamp/tuple coverage and overlap validation;
missing TCP/UDP ports remain blank rather than fabricated as zero.
