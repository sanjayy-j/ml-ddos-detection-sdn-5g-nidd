# Verified implementation checkpoint — 19 October 2026

This is a verified increment, not completion of the full real-time M3 study.

## Newly verified on 19 October

- Completed official BS2 GTP-removed archive: 1,533,058,010 bytes; publisher SHA256 `a155cefbe18ec565ac447e5bc1f9faf1b9dc65d565e077c6263a3055a72638d3` matches. Extracted inputs are registered with parent hashes. The old partial download was preserved separately.
- Full original capture audits: SYN 79,339/93,312 packets matched (85.03%); ICMP 295,311/313,667 (94.15%). No contradictory-label overlaps were observed; unmatched/invalid traffic remains unknown.
- Investigated the initial UDP audit's zero matched flood packets. Argus suppressed actual zero ports in display output. Native binary-flow zero-port filters confirmed exact offsets; the code fills only independently confirmed blanks. The old prepared labels and initial audit remain retained.
- Corrected full UDP audit: 647,522/656,389 matched (98.65%): 230,118 benign, 417,404 UDP flood, 8,867 unknown, zero conflicting-label overlaps. Audit artifacts are local under `output/sdn/`.
- Full original SYN offline packet-window pilot `cabcf6d4afbb46c0805f54c522cbbe8c`: 93,312 input packets, 1,538 scored windows, 17 labelled warm-up windows, 350 unlabelled windows. Attack F1=0.8962566845, precision=0.9544419134, recall=0.8447580645, ROC-AUC=0.9420962711. Immediate oracle labels are revealed after prediction. This is offline packet replay, not real-time accuracy or the repeated sampling study.
- Prepared six bounded official SYN/benign blocks with exact source-packet mappings, MAC-only changes, documented artificial pacing and disclosed packet reuse. Class/rate blocks are controlled scenarios, not natural chronology or independent held-out traffic.
- First actual official-packet collection `official_pilot_d3d2c04879134a4ebf140a98c1236847` failed because independent captures dropped packets. It remains failed; no score was accepted. Root-namespace testbed IPv6 solicitations were also identified rather than labelled as dataset traffic.
- Retried with native Linux capture storage, a larger buffer and IPv6 disabled only on isolated lab interfaces. Collection `official_pilot_70a99e824f1b4ebfa9b666a0320c17e2` passed: TX=26,400 and RX=26,400, zero kernel drops, zero unknown frames and exact prepared-frame multiplicity matches. The collector run is `7b7c4b23e0e74181acfc488752dc7965`; its labels remain unavailable because this stage is live collection, not live learning.
- Recorded-export scoring run `4f75259a458243318a7482224586f4ee` completed: 26,400 decoded samples, 18 labelled warm-up windows, 36 scored windows, 23 unlabelled windows; F1=0.9230769231. The source is `official_5g_nidd_recorded_sflow` and `evaluation_timing=post_hoc_recorded_live_exports`. Sender/receiver evidence is independently revalidated; datagram sequence, sampling and source-compatible headers are checked. **This is post-hoc inference on genuine switch exports, not real-time detection accuracy.** Timing/recovery metrics are unavailable by design.
- Final Python regression suite: **78 passed**, with one upstream Starlette/httpx deprecation warning. Ruff checks and Git whitespace checks pass. Frontend source was unchanged; its earlier verification remains historical, not a fresh visual test.

## Current remaining work

- Integrate independently verified supervision into the real-time inference path without relying on future labels, and distinguish oracle-supervised experimental operation from production label availability.
- Finalize chronological/constructed baseline, drift and unseen-attack scenarios with explicit boundaries, no leakage and transparent reused-data policies.
- Automate and complete the six actual switch rates with three trials per scenario. The 54-trial final matrix has not been run.
- Establish physical attack onset, live unsampled packets-to-detect, detector learning CPU cost and post-drift recovery criteria/analysis. Post-hoc latency cannot stand in for live inference cost.
- Produce final comparable quality/cost tables, repeated-run variation, Pareto/knee analysis, populated dashboard visual checks, report, slides and demo rehearsal.

See [capture-replay-contract.md](capture-replay-contract.md) for exact scope, commands and validation gates. Data, prepared traces and raw outputs remain outside Git; the manifest and reproducible code are versioned.

## Historical checkpoint — 11 October 2026

The original initial checkpoint follows for context. Its pending list is historical and is superseded by the current remaining-work list above.

This is a checkpoint, not a claim that the full M3 study is finished.

## Verified

- Authoritative public 5G-NIDD release retrieved from Fairdata; publisher archive checksums verified. Combined CSV contains 1,215,890 records; per-session CSVs and BS2 Argus metadata are available locally.
- Backend/model/protocol/API tests: 33 passing. Includes actual River HAT/ADWIN learning, predict-before-learn, checksum rejection, UDP decoding/health, missing-versus-zero metrics, API validation, independent flow observation, conservative packet/flow interval matching and unsampled packet counting.
- Frontend: production build and 13 tests passing (including three against actual saved API data); production dependency audit reports zero vulnerabilities. Desktop/mobile connection-error layouts visually inspected. Populated browser screenshots remain unverified because browser transports became unavailable; populated panels are covered by real-API render tests.
- Real Mininet/OVS/OS-Ken diagnostic: N=1 and N=10 both produced zero ping loss and actual sFlow exports. Raw exports and evidence are retained in `output/sdn/` (not committed).
- Actual M3 live collector integration completed: run `3506ba4c54344f20a1ee2bf4eeb533d4` received 1,051 decoded samples over 22 windows. Its controller CPU, OpenFlow capture bandwidth and OVS entry-count measurements are real. Its traffic is a benign connectivity probe, not an official-data attack experiment; quality metrics are unavailable.
- Official UDPFlood2 flow-record pilot: run `3b972edbde1a487a9fd5accd9f075b5a`, 20,000 input records, 1,000 warm-up and 19,000 evaluated. F1 approximately 0.9934 for this limited prefix under immediate oracle-label online learning. This is **not** live accuracy, a held-out batch test, or final evidence across the complete release.
- An initial real-data run rejected the per-session `Label=UDPFlood` encoding. The parser now accepts the authoritative attack-family label while rejecting conflicts. The failed run and logs were preserved.
- Official CSV-to-Argus label joins verified for 314,757 BS2 flows: ICMP 14,452, SYN 14,108, UDP 286,197. Unique Offset joins preserve full Argus epoch intervals and numeric ports; endpoint/protocol/packet-count/byte-count/duration/display-time checks found zero contradictions or missing rows. This establishes flow labels, not yet packet-capture coverage.

## Still pending

- Official packet-capture download and publisher checksum verification.
- Validate the implemented packet matcher against actual official captures: coverage, overlap conflicts and timestamp alignment. CSV display timestamps alone are insufficient.
- Prepared official traces, reproducible baseline/drift/unseen scenarios, and scored live replay.
- Six actual switch sampling rates with three trials per approved scenario.
- Detection delay, unsampled packets-to-detect and post-drift recovery analysis from verified annotations.
- Populated browser visual inspection, final charts/report/demo rehearsal.

Generated outputs, downloaded archives, environments and temporary files are intentionally outside version control. The manifest records provenance; repeat validation on another machine rather than treating a stored checkpoint as fresh proof.
# Research extension: 20 October 2026

The causal N=1 validation pilot `2dd988ddfafd420f8efc050390492dbe` passed
independent full-frame TX/RX matching and receiver-kernel timestamp matching for
9,600 selected official packets. Prediction completion precedes independent
label reading. Source is `official_realtime_verified`, with
`research.study_role=validation_pilot`, excluded from primary aggregation.
Pilot F1=0.8938547486, recall=0.9907120743, FPR=0.2253086420.
This is a technical pilot, not the final repeated study or a novelty claim.

The earlier observer-VLAN failure and startup failures are retained under
`output/research/causal_validation/`. Linux PACKET_AUXDATA now restores
kernel-stripped VLAN tags using authoritative metadata; a regression test covers
this case. No packet content or label is guessed to force a match.

The 54-trial randomized primary matrix is in progress. Current full-suite
checkpoint:129 Python tests passed,81% measured Python coverage,14 frontend
tests passed including real API checks. Browser inventory currently contains no
connected browser, so rendered dashboard visual checks remain unverified.
