# Research study: predeclared evaluation and readiness gates

This is an evidence checklist, not a promise of publication or positive results.
HAT, ADWIN and sFlow are established techniques. Any paper must explain its
specific empirical contribution and compare it with related work; their use alone
is not methodological novelty. A rigorous negative result may still be useful.

## Fixed primary study

- Six **actual switch** sampling rates: N = 1, 2, 5, 10, 20, 50.
- Baseline, drift, unseen-attack scenarios; three distinct trial IDs per cell:
  **54 accepted live trials**. Failed and rejected attempts remain in the raw archive.
- Primary packet windows: **0.1 seconds**. One-second sensitivity uses the same
  recorded raw exports and independent packet truth, recomputed into one-second
  windows; do not average nonlinear 0.1-second feature vectors.
- Match the predeclared replay rate across classes. Do not make benign/flood
  detection trivial by selecting different rates for their replay segments.
- Keep traffic, replay settings, model settings and version fixed within each
  comparison. Pair N versus N=1 using the same scenario and trial ID.
- Both classes must be present in scored observations. Unknown/conflicting
  labels stay unknown; label availability must never precede prediction.
- Delayed oracle labels are experimental supervision, not a claim that a deployed
  detector knows which real-world packets are malicious.

## Physical timing and censoring

Independent receiver/kernel packet epochs define attack onset. Prediction
`observed_time` denotes actual prediction completion relative to origin, not
the start of a feature window. Detection delay is completion minus first labelled
flood packet after warm-up. Count **all original IP packets of every class** from
that onset through completion inclusive, not just sampled or flood packets.

Report separate episodes after predeclared benign gaps (default 0.5 seconds).
Keep false-positive alerts; sampling-induced errors do not get filtered away.
No detected attack means a censored, unavailable delay/count, not zero. Include
optional feature-window start/end bounds to associate alerts with an episode.

Recovery after each predeclared drift boundary uses rolling **balanced accuracy
at least 0.90 over 40 scored post-boundary observations**, sustained for **three
consecutive checks**. Every check requires both classes. Report the first check's
time and the later confirmation time. No qualifying streak is censored. A
baseline-relative alternative must be explicitly declared before inspecting data,
not tuned afterward to obtain a recovery claim.

## Statistics and comparisons

Retain trial values and failures. Report mean, **sample** standard deviation, and
unbounded two-sided 95% **Student-t** mean intervals (n=3 gives t=4.30265).
Intervals may extend beyond a metric's logical range; do not silently clip them.
Three repeats on fixed traffic quantify controlled repeatability, not broad
population generalization. Censored observations are not imputed as zero, and
their counts must remain visible.

Compute exact paired trial-wise differences from N=1 before summarizing them.
Do not subtract independent averages or pair unrelated trial IDs. Only identical
provenance, feature schema, model settings, versions and replay conditions belong
in a comparison group. Missing metrics or incompatible units must stay unavailable.

Pareto points maximize F1 and minimize **measured sFlow plus measured OpenFlow
bandwidth**, both in kbit/s. Missing channels or serialized-payload proxies are
ineligible. The descriptive recommendation is closest to the normalized ideal
point using weighted Euclidean distance, quality weight 0.5, normalized over all
eligible candidates. It is not an optimization proof, universal best N, or
statistical superiority claim. Keep uncertainty visible.

Quality-only ablations replay exactly the recorded feature/label sequence through
HAT+ADWIN, nonadaptive Hoeffding Tree, and a fixed warm-up-majority dummy (tie
predicts benign). All models predict before learning the current revealed label.
The dummy never learns from evaluation labels. Recorded `label_available_time`
controls when prior labels can train each model; no current observation is
learned before its prediction. An absent availability timestamp explicitly marks
the ablation as immediate-oracle-label supervision, not a delayed-label result.
These offline ablations do **not**
establish equivalent live latency, CPU or bandwidth performance.

## Machine-readable handoff contract

`scripts/analyse_research.py --runs output/runs --output output/research` reads
`run_summary.json` recursively. It never starts a network or fabricates missing
results. No qualifying trials yields empty tables and a failed readiness checklist.

Accepted run summaries require:

```text
source: official_realtime_verified
status: completed
validation.accepted: true
run_id, scenario, sampling_rate, seed
config: trial_id, window_seconds, fixed replay/model/label-delay settings
feature_schema, provenance, versions, model_parameters (when applicable)
metrics.<name>: {value, unit, status: measured}
raw_hashes: nonempty artifact-name-to-SHA256 mapping
validation: actual_switch_config_verified, independent_tx_rx_match,
  zero_capture_drops, raw_hashes_verified, chronological_prediction_before_label,
  both_classes_scored (all true)
research: ablations_completed, sensitivity_completed (with saved backing results)
```

Prediction helpers accept `label`/`predicted` or CSV `y_true`/`y_pred`,
`warmup: true` or `phase: warmup`, and `observed_time`. `completion_epoch` can be
provided directly for physical timing. Packet events use `epoch`, `label`,
optional `is_ip`. Feature records in `features.jsonl` contain `features`, label,
warm-up phase, and any family annotations. Preserve exact original feature order.
With delayed supervision, include `observed_time` and `label_available_time`
(relative to the same origin) for every labelled feature row.
The analysis script derives quality ablations if these feature records exist;
it never edits raw run summaries. One-second sensitivity needs separately saved
backing results and cannot be declared complete just because a flag is set.

Outputs: aggregate JSON/CSV, paired deltas, quality ablations, descriptive Pareto
JSON/PNG where supported, and research readiness JSON. Measurement keys for the
combined cost analysis are `sflow_bandwidth_kbit_s` and
`openflow_bandwidth_kbit_s`, unit `kbit/s`.

## Completion and honest limits

All 54 cells' trials need verified switch configuration, independent TX/RX
agreement, zero capture drops, raw hash links, correct prediction/label chronology,
both-class support, ablations and sensitivity evidence. Review results for class
imbalance, label gaps, capture losses, and source/flow identity confounds.
Do not add an unregistered gate such as F1 > 0.95 after seeing results.

The lab replays **controlled dataset-derived traffic**, not natural 5G traffic,
a physical 5G/RAN deployment, or production attacker behaviour. Host scheduling,
shared CPU, replay pacing, sampling randomness and short episodes affect results.
Only one official release and selected captures are studied; conclusions must
remain scoped. Packet/flow identity, kernel arrival versus original capture time,
sampling correction and oracle-label delay assumptions must be disclosed.

Paper readiness additionally needs source-verified related work, a clear research
question and contribution, complete methods, real results, reproducibility notes,
limitations, final figures, and human review. Passing automated gates cannot
guarantee novelty, peer-review acceptance, or that every scientific claim is sound.
