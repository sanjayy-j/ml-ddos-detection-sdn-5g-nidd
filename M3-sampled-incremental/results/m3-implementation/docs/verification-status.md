# Verified implementation checkpoint — 11 October 2026

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
