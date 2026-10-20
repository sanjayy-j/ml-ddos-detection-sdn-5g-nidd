# M3 demonstration script

## Preparation

Start the read-only project server from this implementation directory:

```sh
m3 serve --runs output/runs --port 8000
```

Open `http://127.0.0.1:8000/`. A built frontend is required; otherwise run
`npm ci` and `npm run build` inside `frontend/` first. Use the published trial
index to choose a completed run whose source badge is **Validated official live
trial**. Avoid technical pilots and provisional/failed attempts when presenting
primary study conclusions. Keep the manuscript and aggregate CSV open separately.

## Three-minute explanation

**0:00 - Purpose.** "We investigate how collecting fewer packet headers affects
flood detection and monitoring cost. This is M3 only. We use existing adaptive
trees, not a new machine-learning algorithm."

**0:25 - Source and live path.** Show the provenance checksum and live-sFlow mode.
"Original packets come from the official 5G-NIDD release. We replay selected,
labelled packets at equal rates in an isolated SDN emulator. The physical 5G
network and natural traffic timing are outside this experiment."

**0:50 - Independent evidence.** "Separate sender and receiver captures verify
forwarding. A victim-side observer uses full original packets and kernel receive
timestamps to supply experimental truth. The detector predicts before reading
each current label. Unknown labels are not safe-traffic labels."

**1:15 - Detection.** Select a validated N=1 trial and show its prediction timeline.
Explain precision, recall, F1 and false-positive rate in plain terms. Show at
least one incorrect prediction if available. "High recall alone is insufficient
when normal traffic also produces many alerts."

**1:45 - Cost.** Change to a compatible trial at another N. Show sampled count,
detector/controller CPU, sFlow and OpenFlow costs. "This screen shows individual
trials. The report summarizes all three repeats and uncertainty. Choose combined
IP-layer bandwidth on this screen to match the report. Legacy
payload/frame fields remain separately labelled."

**2:10 - Research results.** Show the report's repeated-trial tables, paired
intervals, ablations, sensitivity and descriptive Pareto recommendation. Use the
actual reported N and numbers, not a remembered pilot or the best individual run.

**2:35 - Limitations.** "Inputs and labels are controlled. Repeats share fixed
traffic. Sampling and host timing vary. The drift scenario changes family and
cadence together. Oracle labels enable adaptation. We cannot claim universal
zero-day protection, physical 5G performance or automatic attack blocking."

## Questions to expect

- **Is N=1 M1?** No. It is the unsampled M3 reference, with the same adaptive model.
- **Does an ADWIN alarm prove an attack?** No. It indicates a prediction-error
  distribution change. HAT's internal adaptation is separate.
- **What does unavailable mean?** A metric is censored, inapplicable or lacks
  sufficient evidence. It is not an invented zero.
- **Are labels available in deployment?** Not automatically. This is an
  experimental oracle study with an explicit prediction-before-label order.
- **Is this publication accepted?** No acceptance or novelty guarantee is made.
  The evidence package supports scientific review.

## Manual checks and known limits

The user explicitly waived browser visual verification on 20 October 2026.
Automated UI tests, real local API integration and the production frontend build
are separate checks. Do not say a human/browser visual pass occurred.
Presentation previews do not prove that PowerPoint itself was opened or tested.
