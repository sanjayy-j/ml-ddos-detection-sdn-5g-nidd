# Controlled M3 study: methods and interpretation

## Research questions

1. How does actual OVS sampling N change binary flood-detection quality when
   benign and attack packets replay at the same rate?
2. What is the measured quality-versus-control-channel-cost frontier in this
   isolated implementation?
3. How do held-out SYN introduction and a constructed family/cadence shift
   affect missed attacks, false positives and predeclared recovery?
4. How sensitive are quality conclusions to a one-second rather than0.1-second
   window, and to adaptive versus nonadaptive tree or majority prediction?

This M3-only study does not answer the original overview's M1-versus-M2-versus-M3
questions. N=1 is an internal unsampled M3 reference. It is not an implemented M1.

## Fixed protocol and source selection

The frozen protocol is `configs/research_protocol.json`, SHA256
`f8196653b1a0dfe6da652fa75d1aba720a6bd243842292d5a017b8cc2f8cc36d`.
Three scenarios, six N values(1,2,5,10,20,50), and three model seeds(42,43,44)
yield 54 planned primary trials. Trial order uses seed 20261019. No threshold or
hyperparameter tuning uses primary evaluation outcomes. Technical pilots and
failed attempts remain separate from the randomized matrix.

Exact authoritative flow-family matches supply 27,200 original packet selections
in 40 prepared blocks. Mapping audits found no reused source packet indices or
identical original frame hashes across these selected scenarios. This does not
establish independence of source flows, sessions or capture conditions. Training
and evaluation can still share traffic-generation and flow identities. Raw
addresses, tools, labels and frame hashes never enter the model's feature vector.

A packet inherits a label only through a compatible original bidirectional
endpoint/protocol/time interval, including numeric transport ports for TCP/UDP.
ICMP uses endpoints, protocol and time, without guessed pseudo-ports. The interval
tolerance is 1 microsecond. A SYN flag or an attack-session filename alone is not
evidence that a packet is malicious. Unknown and conflicting matches are excluded
from prepared blocks, rather than relabelled benign.

Full original-stream audits, before selection, gave the following coverage.
These are label-join coverage figures, not classifier scores:

| BS2 session | Original packets | Known benign | Known flood | Unknown |
|---|---:|---:|---:|---:|
| SYN | 93,312 | 64,648 | 14,691 | 13,973 |
| ICMP | 313,667 | 294,232 | 1,079 | 18,356 |
| UDP | 656,389 | 230,118 | 417,404 | 8,867 |

Argus suppresses some numeric zero ports in text output. UDP reconstruction used
binary-flow port-zero filters and exact original record offsets, not blanket
replacement of missing values. Conservative unresolved values remain unknown.
Selection from confidently labelled packets limits representativeness.

Only Ethernet destination/source MAC addresses change. Network-layer headers and
payloads remain original. Packet timestamps become selection_index/100 for replay.
All selected classes use 100 pps. The original dataset's attack intensity, burst
structure and natural chronology are not preserved. This design removes selected
rate-label confounding but cannot estimate line-rate attack performance.

Baseline and unseen scenarios each have 12 eight-second blocks, alternating
benign/attack conditions. Drift has eight eight-second blocks followed by eight
two-second blocks. Two-second gaps separate blocks. The drift post-stage uses
800 confidently matched ICMP packets from the available 1,079. Family and cadence
change together, so this is a joint covariate/cadence-shift scenario. It does not
isolate a causal benefit of ADWIN or demonstrate a natural concept change.

The first four blocks form warm-up. Baseline exposes UDP and SYN during warm-up.
Unseen exposes UDP but excludes SYN from its entire warm-up. Actual run metadata,
not these approximate schedule offsets, defines physical origin and boundaries.

## Isolated live testbed

An OS-Ken OpenFlow 1.3 learning controller drives a four-host Mininet topology and
OVS userspace datapath. The testbed has no physical-network uplink. Bounded
tcpreplay injects verified blocks through the sender interface. The victim's full
received packets and sender's transmitted packets are captured independently.
Expected versus observed whole-frame multiplicities must agree, and capture
kernel drops must be zero. Sampling configuration is read before and after each
trial. OVS sampling randomness is uncontrolled; recorded model seeds do not seed
the switch. Repeats reuse frozen input traffic and measure controlled repeatability.

## Independent supervision and causal order

A separate process in the victim namespace reads full frames using AF_PACKET and
kernel receive timestamps. Full-frame source matching supplies packet truth,
independently of which packets OVS samples. PACKET_AUXDATA restores kernel-stripped
VLAN headers before matching. Unknown or conflicting frames remain unknown.

The observer publishes pure-class window snapshots after a fixed settling
interval. Empty, mixed and unknown windows are unscored; they are never assumed
benign. For every completed feature window, the detector waits a declared0.5s,
predicts, records completion time, then opens the independent truth snapshot.
It logs/scores the observation before learning its newly revealed oracle label.
Labels for gaps do not train the classifier. A zero-sample window with known
original-packet truth remains scored and can be a false negative or false positive.

This is delayed **experimental oracle supervision**. A production system does
not know packet truth automatically. The 0.5 s delay contributes to physical alarm
latency and is not presented as pure inference cost.

Precisely, `label_delay_seconds` names a **window-closure holdback**, not a
0.5-second delay after prediction. Once prediction completes, that window's
experimental label is read and learned immediately. This study does not model
asynchronous human annotation or an operational labelling service.

## Features and model

Primary windows are 0.1 s, indexed by collector receipt time. Features are estimated
packets/s and bytes/s(weighted by N), sampled mean packet size, UDP/TCP/ICMP/SYN
fractions, and an empty-window indicator. sFlow export batching, queueing and host
scheduling can delay features relative to packet onset. Error near boundaries is
part of the measured observation pipeline, not removed based on model outcomes.

River HAT uses grace_period 200, threshold 0.5, internal ADWIN delta 0.002, and a
separate external ADWIN prediction-error monitor. The external monitor does not
reset the classifier. Internal branch changes are not inferred from its alarms.
Warm-up observations train but do not contribute to reported quality.

## Measurements

Per-class precision, recall and F1, rank-based tie-aware ROC-AUC, false-positive
rate, and held-out SYN recall use independently labelled evaluation windows.
Physical detection delay uses prediction completion minus original received attack
onset. Packets-to-detect counts all original IP packets from onset through alert
completion, not selected samples. Undetected episodes remain censored. Inference
latency measures only the model's predict call, not export/window/label delay.

CPU values represent percentages of one logical CPU, not the whole machine.
Detector and controller CPU are separate. Flow entries are periodic snapshots.
Resource aggregation excludes pre-origin idle time. Legacy telemetry bandwidth
counts sFlow UDP payload; legacy OpenFlow bandwidth counts captured frame bytes.
The scientific Pareto aliases use a consistent **IP-layer** basis: IPv4/UDP/payload
for sFlow, captured IP packet bytes for OpenFlow. Report both channel components
and their sum, including periodic counter/control traffic. These virtual-link
costs do not measure physical wire overhead or production switch CPU.

Recovery requires rolling balanced accuracy >= 0.90 across 40 scored post-boundary
observations, sustained for three consecutive checks with both classes in each
window. Missing recovery is censored, not zero. Block cadence affects whether this
criterion can be observed and must accompany interpretation.

## Comparisons and uncertainty

Report all three trial values, mean, sample SD, and an unbounded two-sided 95%
Student-t mean interval. N=3 gives a wide interval with critical value 4.30265.
Pair each N with N=1 using the same scenario/trial identity. This pairing controls
the fixed input/model seed, not OVS sampling RNG. Do not claim independent new
traffic populations or statistical superiority from overlapping/limited repeats.

Quality-only offline ablations consume the exact saved features and causal label
order: HAT, nonadaptive Hoeffding Tree, and a fixed warm-up-majority dummy. These
do not compare equivalent live CPU/latency costs. One-second sensitivity rebuilds
features from the actual raw datagrams and original RX events, not averages of
nonlinear0.1s feature vectors. It remains explicitly post-hoc quality sensitivity.

Pareto candidates maximize F1 and minimize measured combined IP-layer channel
bandwidth. A descriptive recommendation minimizes normalized ideal-point distance
with predeclared equal quality/cost weighting. It is not a universal best N.

## Reproducibility and limitations

Retain the manifest, protocol, exact configuration, software revision, dependency
versions, raw datagrams, TX/RX captures, original-packet events, per-window causal
records, resource logs, failed attempts and SHA256 links. A clean checkout excludes
large raw data, prepared captures and local results. Reproduce by downloading the
official release and applying the documented preparation and lab commands.

The selected release/session, constructed timing, flow identity correlations,
oracle labels, low fixed replay rate, short shifts, shared-host scheduling and
uncontrolled sampling limit external validity. No physical5G/RAN or MEC experiment,
automatic mitigation, broad zero-day guarantee, or causal adaptation advantage is
established by this design. Paper acceptance and sufficient novelty require human
review beyond automated artifact-completeness gates.
