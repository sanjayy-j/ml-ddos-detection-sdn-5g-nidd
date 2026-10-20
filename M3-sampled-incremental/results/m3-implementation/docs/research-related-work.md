# Research context and verified sources

Sources checked on 20 October 2026. These establish context, not a claim that
the present implementation is the first use of sampled adaptive learning.

## Dataset and evaluation setting

Samarakoon, Siriwardhana, Porambage, Liyanage, Chang, Kim, Kim and Ylianttila,
**5G-NIDD: A Comprehensive Network Intrusion Detection Dataset Generated over
5G Wireless Network**, arXiv:2212.01298 (2022), describe labelled traffic from a
functional 5G test network. The present study selects verified packet records
from that release and replays them in an SDN emulator. Rewriting Ethernet MACs
and constructing replay times changes the evaluation distribution. Results from
the original dataset paper cannot be compared numerically with these window
predictions as if their tasks and splits were identical.

- Paper: <https://arxiv.org/abs/2212.01298>
- Author repository: <https://github.com/yushan1986/5g-nidd>
- Release DOI: <https://doi.org/10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361>

## Established adaptive-learning methods

Bifet and Gavalda, **Learning from Time-Changing Data with Adaptive Windowing**,
SDM 2007, pp.443-448, DOI10.1137/1.9781611972771.42, introduce adaptive window
management for changing streams. ADWIN's guarantees concern its assumptions and
change statistic. They do not guarantee flood detection or recovery in this lab.

- Publisher: <https://doi.org/10.1137/1.9781611972771.42>
- Author manuscript: <https://www.cs.upc.edu/~gavalda/papers/adwin06.pdf>

Bifet and Gavalda, **Adaptive Learning from Evolving Data Streams**, IDA2009,
DOI10.1007/978-3-642-03915-7_22, develop adaptive tree methods. The authors'
extended manuscript is titled *Adaptive Parameter-free Learning from Evolving
Data Streams*. It is relevant prior art, not a new algorithm contributed here.

- Author manuscript: <https://www.cs.upc.edu/~gavalda/papers/ida09-extended.pdf>
- Implementation studied: [River0.23 source](https://raw.githubusercontent.com/online-ml/river/0.23.0/river/tree/hoeffding_adaptive_tree_classifier.py)

The implementation uses HAT's internal drift adaptation and a separate ADWIN
monitor of prequential prediction errors. An external alarm is not proof that an
alternate branch was created or promoted. The monitor does not reset HAT.

## Sampling and SDN intrusion detection

Phaal and Lavine, **sFlow Version5** (sFlow.org, July2004), specify sampled packet
records and periodic counters. N denotes the average original-packet-to-sample
ratio, not a guarantee of exactly every Nth packet. The format does not provide
an original per-packet event timestamp in each raw-header record. This study
therefore names collector-arrival windows explicitly and measures physical alarm
delay separately with independently timestamped received originals.

- Specification: <https://sflow.org/sflow_version_5.txt>

**Towards sFlow and adaptive polling sampling for deep learning based DDoS
detection in SDN**, publisher article S0167739X19318333, already studies sampling,
SDN intrusion detection and accuracy-resource trade-offs. Its publisher abstract
was retrievable through search, but the full page returned403 during this review.
No detailed implementation or numerical comparison is inferred from inaccessible
sections. The generic accuracy-overhead question must not be claimed as new.

- Publisher: <https://www.sciencedirect.com/science/article/pii/S0167739X19318333>

Ilias et al., **Convolutional Neural Networks and Mixture of Experts for Intrusion
Detection in5G Networks and beyond**, arXiv:2412.03483 (2024), provide a later
5G-NIDD model study. Its feature-array classification setting differs from live
switch-exported windows. Its reported scores are context, not a same-protocol
baseline against which this implementation can claim superiority.

- Paper: <https://arxiv.org/abs/2412.03483>

## Appropriate contribution and claim limits

The candidate contribution is a reproducible **measurement and evidence
pipeline**: official packet-to-flow provenance, actual OVS sampling, independent
TX/RX validation, kernel receive timestamps, prediction-before-oracle-revelation
records, repeated equal-rate trials, and uncertainty-aware quality/cost analysis.
Whether this constitutes sufficient novelty for a particular venue requires a
broader literature review and human scientific judgement. Automated readiness
checks establish artifact completeness, not originality or acceptance.

Do not claim a new HAT/ADWIN algorithm, natural concept-drift discovery, a
physical5G deployment, zero-day protection in general, or automatic mitigation.
The unseen experiment excludes SYN during warm-up but subsequently learns from
oracle SYN labels. Report first-encounter and later adaptation separately.

## Packet-observer implementation reference

Linux may remove a VLAN header from the raw receive buffer and expose it as
PACKET_AUXDATA instead. The observer reconstructs a tag only when the kernel marks
the VLAN metadata valid, then checks whole-frame hashes against independent RX
PCAP evidence. It does not infer missing packet bytes from their expected label.

- [Linux packet socket manual](https://man7.org/linux/man-pages/man7/packet.7.html)
- [Kernel UAPI definitions](https://github.com/torvalds/linux/blob/master/include/uapi/linux/if_packet.h)
