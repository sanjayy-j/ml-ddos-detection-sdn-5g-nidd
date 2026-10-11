# M3 implementation contract

Approved scope: M3 only, official 5G-NIDD data, live Mininet/OVS sampling, River HAT and
ADWIN, reproducible evaluation and a FastAPI/React results application. No partner dependencies.

The prediction is a binary DDoS/flooding alarm. False positives and missed attacks are
both reported; there is no automatic mitigation. UDPFlood, SYNFlood and ICMPFlood are
positive, Benign negative, and other families excluded. Labels, source identities, row
indices and attack tools are never model inputs. Threshold is fixed at 0.5 before evaluation.

Original files require an official-source manifest and matching SHA256. Prepared data
must retain original references and transformation records. Test fixtures are never official
evidence. Unknown packet labels exclude a window from quality scoring instead of guessing.

Offline packet replay supports `flow_labels_path`: checksum-verified numeric Argus flow
intervals joined one-to-one to official per-session labels. Packets match full TCP/UDP
bidirectional endpoint/port/protocol tuples and epoch intervals (1 microsecond tolerance).
ICMP matches endpoint/protocol/time, not guessed service or ICMP pseudo-port identifiers.
Overlapping contradictory labels, unparseable headers and unmatched tuples stay unknown.
A window is positive if it contains at least one authoritative matched flood packet; negative
only if all original packets are known benign (or it is empty). Otherwise it is unscored.
Coverage is reported. Ground truth is obtained from all original packets, independent of N;
only feature extraction is sampled. Offline packets-to-detect counts original packets through
the first correctly alarmed window; capture-time delay is an estimated window-end proxy.

CSV replay predicts on sampled flow records and is a flow-subsampling benchmark. Its row
indices are not physical timestamps and do not prove packet sampling or chronological drift.
Packet replay and the live collector share a one-second packet-window feature definition.
Live sampling occurs in OVS once; the collector must not sample the received stream again.

HAT adapts branches using internal ADWIN detectors. A separate ADWIN monitor observes
prediction error and records alarms; it does not reset the HAT. Evaluation order is
predict, save prediction/update metrics, reveal label, learn. Warm-up is not scored.
SYNFlood is excluded from warm-up in the unseen scenario. Ground-truth labels becoming
available immediately is an experimental assumption, not a production availability claim.

Each configuration gets a new model and unique directory. A JSON summary identifies source,
unit, mode, configuration, provenance, status and nullable metrics with explicit reasons.
Raw predictions/resources/drift events are append-only CSVs. API summaries are atomically
updated; the dashboard never computes or fabricates model results.

Costs: collector+detector CPU and OpenFlow-controller CPU are distinct. sFlow export bytes
and OpenFlow bytes are separate channels. 100% CPU means one logical CPU. No unavailable
controller/packet metric is replaced with a replay proxy. All trials, including failures,
remain in the run index. Quality on sampled flow records is conditional on selection;
packet-window/episode coverage metrics include empty observed windows when labels are known.

Verification covers feature leakage, labels, predict-before-learn, ROC ties, sampling,
packet windows, sFlow bounds, atomic persistence and API path validation. The first pilot
establishes throughput and useful labels before expensive sweeps. Measured low quality is
reported and investigated, not hidden by selecting the best trial.
