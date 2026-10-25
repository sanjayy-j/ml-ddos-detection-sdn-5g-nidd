# Current M3 completion checkpoint - 20 October 2026

The declared controlled M3 study is complete: 54 accepted official live trials, 18 cells, three distinct trial IDs per cell. `research/results/research_readiness.json` has `ready=true`, no missing cells and no input-read errors. This certifies the declared evidence package, not novelty, production readiness or publication acceptance.

## Scientific evidence

- Every trial uses actual OVS sampling at its declared N and preserves independent full-frame TX/RX and kernel-timestamp checks, zero capture drops, and prediction-before-current-label chronology.
- The final report builder rechecked all 594 raw-artifact SHA256 links. Raw summaries remain immutable; analysis verifies backing ablation/sensitivity files and derives completion flags in memory.
- Stored HAT quality reproduces exactly for all 54 runs. All runs have HT and fixed-majority quality ablations and one-second raw-export sensitivity results.
- All 80 prepared packet/mapping files match frozen hashes. The annotation archive contains three pinned flow-label snapshots and 40 mapping files. The derived trial archive contains 378 entries for 54 runs. Both pass CRC and safe-member checks.
- The fixed protocol and the failed technical attempts/retry explanation remain preserved. No quality threshold excluded a trial or selected a rerun.

## Findings and scope

N=2 is the descriptive equal-weight quality/cost selection in every primary scenario. Mean F1 is 0.956 (baseline), 0.954 (drift) and 0.962 (unseen). Combined IP-layer bandwidth falls by 46.94%, 45.90% and 46.40% respectively versus N=1. Corresponding false-positive rates are 8.96%, 9.51% and 7.72%.

These are fixed-traffic repeatability estimates, not general population or deployment guarantees. As run, the curve is non-monotonic, one-second results differ, and even selected settings retain material false positives.

Correction (second-level review): the non-monotonic curve came from the N=1 learner, not from sampling. In 8 of 9 N=1 trials the tree never split, and River 0.23's naive-Bayes leaf vote treats an underflowed density as certainty. Replaying the exact recorded features reproduces every live quality metric (difference 0); with a log-space vote and nothing else changed, N=1 reaches F1 0.985-0.997 at FPR 0.006-0.016, N=2 0.959-0.968 at FPR 0.063-0.084, and quality falls as N grows. The equal-weight rule still selects N=2. Details: `research/N1_Baseline_Reanalysis.md`; data: `research/results/naive_bayes_reanalysis.json`. Recovery meets the declared criterion in 3/3 N=2 drift trials (mean 6.506 seconds); other outcomes and external alarm counts remain visible. No causal benefit of ADWIN is asserted.

## Software and artifacts

- Windows: 139 Python tests passed, 81% measured `m3` coverage; Ruff passes.
- Linux: 138 passed, one optional report-rendering test skipped, one upstream Starlette/httpx warning. Reporting dependencies were not added to the frozen live-study runtime.
- Frontend: 18 tests passed, including four real-API checks; production TypeScript/Vite build passes. Three new checks cover measured IP-channel cost selection/summing and comparison display; a real accepted-live check also exercises the published-only bundle.
- The published bundle is separately unpacked for review; its accepted-live API/UI test passes without the omitted raw captures. This is archived evidence display, not a fresh raw-capture validation.
- Final report: 11 pages; text/headings/glyph checks and every rendered page inspected. A regression test prevents table captions from separating from their tables.
- Final presentation: 10 slides, four editable native charts with workbook snapshots, package/layout/font/import checks pass; every final slide rendered and inspected. Literal chart means use 12 significant digits for Excel portability; full precision remains in analysis files.
- Browser visual verification was explicitly waived by the user. No browser visual-pass claim is made. PowerPoint was not opened; slide previews and package checks do not establish native PowerPoint execution.
- PDF build environment: Windows CPython 3.12.2, ReportLab 4.5.1, pypdf 6.21.1 and Matplotlib 3.11.2. Live Python package versions are recorded separately in `requirements/research-linux.txt`.

## Completion boundary

Implementation, declared experiments, analysis, report, slides, derived evidence and reproduction/demo instructions are complete within M3 scope. Physical 5G deployment, automatic mitigation, M1/M2 implementation and broad unseen-capture generalization were not part of this study. Human scientific review must still assess contribution novelty and venue suitability.

---

The following entries are historical checkpoints. Their pending lists describe their original dates, not the completed state above.
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
