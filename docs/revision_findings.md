# Revision findings — measured results for the first-level corrections

Handover note for whoever edits the manuscript source. Every number below was
measured from the committed artifacts in this repository; nothing here is an
estimate unless it says so. Where a measurement contradicts the current
manuscript, the manuscript text that needs changing is named explicitly.

The manuscript source (`.docx`/`.odt`) is not in this repository and was not
available to this work, so none of these changes have been applied to the
paper. Document editing is the manuscript author's task; this file exists so
that it can be done from measured numbers rather than re-derived.

Reproduce anything here with the scripts named in each section.

## 1. What is new in the repository

| Commit | Contents |
|---|---|
| `cf5264e` | TTL ablation (item 2): config, results, and the seed-sweep / window-feature harnesses |
| `d07fa41` | Five-seed sweep results (item 1): `results/seed_sweep/seed_sweep_runs.csv` |
| `99c495d` | `split.rotate_fraction` for the alternative contiguous cut (item 4), `--hparams-from`, three tests, five-seed summary statistics |

New scripts:

- `M1-supervised-ml/experiments/seed_sweep.py` — retrains any subset of the
  three models under any set of seeds, reusing the already-selected
  hyperparameters and the locked FPR ≤ 1% threshold protocol. No grid is
  re-run. Validated: Random Forest at seed 42 reproduces the published
  baseline to six decimals (threshold 0.478734, accuracy 0.655771, recall
  0.438040, F1 0.607079, FPR 0.007828, ROC-AUC 0.852824).
- `M1-supervised-ml/experiments/build_window_features.py` — causal window
  aggregates for item 3, route (a).

Test suite: 252 tests pass (249 published plus three for the split rotation).

One pre-existing bug was fixed to make item 2 runnable: `--skip-search` in
`train_random_forest.py` wrote the literal string `"config"` into the search
record, which was then passed back as `max_features='config'` and crashed the
refit. That code path had never been exercised. The search grid always supplies
all three keys, so no real search run changes behaviour.

## 2. Item 2 — TTL ablation

`sTtl` and `dTtl` moved to `drop_columns`, giving 65 encoded features instead
of 67. `sHops` and `dHops` stay dropped (the config records them as fully
determined by `sTtl`/`dTtl`), so no TTL proxy re-enters the representation.
Random Forest hyperparameters pinned to the Stage F selections, so only the
features change. All ten leakage checks pass; split sizes and class priors are
unchanged.

Command: `prepare_data.py` then `train_random_forest.py --skip-search` then
`evaluate_rf_at_fpr.py`, all with
`config/m1_config_ablation_no_ttl.yaml`.

| Metric | 67 features | 65 features (no TTL) | Δ |
|---|---|---|---|
| Frozen threshold | 0.478734 | 0.466751 | −0.011983 |
| Accuracy | 0.655771 | 0.655579 | −0.000192 |
| Precision | 0.988566 | 0.988359 | −0.000207 |
| Recall | 0.438040 | 0.437814 | −0.000226 |
| F1 | 0.607079 | 0.606823 | −0.000256 |
| FPR | 0.007828 | 0.007967 | +0.000140 |
| ROC-AUC | 0.852824 | 0.852522 | −0.000302 |
| PR-AUC | 0.867387 | 0.867026 | −0.000361 |
| TP / TN / FP / FN | 48,505 / 71,109 / 561 / 62,227 | 48,480 / 71,099 / 571 / 62,252 | −25 / −10 / +10 / +25 |

Both confusion matrices recompute to their reported metrics exactly.

New top-10 importances: `sMeanPktSz` 0.127535, `Proto_tcp` 0.086249, `SynAck`
0.066200, `Dur` 0.064431, `TcpRtt` 0.060826, `TotBytes` 0.056215, `SrcWin`
0.055660, `SrcBytes` 0.051639, `Rate` 0.047714, `SrcRate` 0.044269.

Per-attack recall is unchanged except HTTPFlood (0.999953 → 0.999811) and
UDPScan (1.000000 → 0.990783). **UDP-flood recall is identical to six
decimals: 0.092942.**

Label-conflict bound, Eq. (5): conflicting vectors 33,709 → 33,714; ceiling
76.8455% → 76.8437%.

**Establishes:** removing both TTL fields costs 25 of 110,732 malicious test
records. `sTtl` tops the impurity ranking but the model does not depend on it —
the dominance reflects redundancy, not reliance, and the remaining features
carry the same signal. This answers the host-fingerprint concern raised via
ref [15] and leaves the representation limit intact, so it strengthens the
paper's central argument rather than weakening it.

**Does not establish:** anything about the SVC or the CNN, which were not
re-run because the Random Forest result is unambiguous; and nothing about
whether TTL would matter under a different split or a richer representation.

Note for the text: the faculty's "importance 0.167 vs 0.095" compares `sTtl`
(0.166699) with `sMeanPktSz` (0.095296), the next-ranked feature — not with
`dTtl`, which is 0.016534. The TTL-dominance point stands as written.

## 3. Item 1 — five training seeds

Seeds **42, 43, 44, 45, 46**; all three models; hyperparameters read from the
committed run records; no grid re-run; threshold re-frozen on validation at
FPR ≤ 1% for each seed; test scored once per run.

Command: `seed_sweep.py --models RandomForest,SVM,CNN_1D --seeds 42,43,44,45,46`
Artifacts: `results/seed_sweep/seed_sweep_runs.csv` (15 runs),
`results/seed_sweep/seed_sweep_summary.csv`.

Internal consistency of all 15 runs: TP+TN+FP+FN = 182,402, TP+FN = 110,732,
TN+FP = 71,670, and every reported metric reproduces from its confusion matrix
to six decimals.

| Metric | Random Forest | Nyström + linear SVC | 1-D CNN |
|---|---|---|---|
| Accuracy | 0.654951 ± 0.001834 | 0.653386 ± 0.000756 | 0.651353 ± 0.000211 |
| Precision | 0.990781 ± 0.004952 | 0.980993 ± 0.003928 | 0.999090 ± 0.000927 |
| Recall | 0.435706 ± 0.005218 | 0.437532 ± 0.001711 | 0.426083 ± 0.000073 |
| F1 | 0.605219 ± 0.004160 | 0.605152 ± 0.001187 | 0.597394 ± 0.000124 |
| FPR | 0.006310 ± 0.003395 | 0.013113 ± 0.002816 | 0.000600 ± 0.000612 |
| ROC-AUC | 0.852770 ± 0.000039 | 0.849342 ± 0.001979 | 0.851527 ± 0.000309 |
| PR-AUC | 0.867367 ± 0.000015 | 0.879265 ± 0.000639 | 0.864500 ± 0.000124 |
| Frozen threshold | 0.489364 ± 0.023719 | −0.059072 ± 0.036946 | 0.524894 ± 0.056995 |

The threshold-free metrics are very stable (ROC-AUC SD 0.00004–0.0020, PR-AUC
SD 0.00002–0.0006), so the paper's central claims survive the seed objection.

### 3.1 Random Forest: a score plateau, not cherry-picking

Seeds 42, 44, 45 and 46 produce **bitwise identical** confusion matrices —
TP 48,505 / TN 71,109 / FP 561 / FN 62,227 — at four different frozen
thresholds (0.460267, 0.478734, 0.486741, 0.496627). Seed 43 is the sole
outlier (threshold 0.524450, FP 17, recall 0.426372).

The published seed 42 is therefore the **modal** result, matched by three of
the other four seeds. The mean sits below it only because one seed fell onto a
different plateau. This is the discrete-score effect §4.3 already documents:
identical inputs produce identical scores, the Random Forest takes few distinct
score values, and several thresholds land on the same operating point.

**Do not describe the published Random Forest numbers as a favourable
selection.** They are the typical result, and saying otherwise would be a false
confession.

### 3.2 CNN: seed 42 is atypical, and the cause is training length

CNN FPR by seed: **0.001688** (42), 0.000391 (43), 0.000363 (44), 0.000209
(45), 0.000349 (46). The published seed 42 is roughly four times the mean of
0.000600.

The cause is visible in the run record: seed 42 **early-stopped at epoch 19
with best epoch 14**, where the other four ran 26–30 epochs (best 21–30).
Early stopping is driven by validation PR-AUC, so seed 42 is the least-trained
of the five. The published CNN FPR should be reported as the highest of five
seeds, with the shorter training run given as the reason.

### 3.3 Claims in the current manuscript that these runs change

| Location | As printed | Across five seeds |
|---|---|---|
| Abstract, p. 1 | "precision of 0.982–0.997" | **0.974–1.000** (min SVC seed 46, max CNN seed 45) |
| Abstract, p. 1 | "recall of only 0.426–0.438" | **0.426–0.440** (min CNN seed 43, max SVC seed 46) |
| Table 5 / §4.1 / §5.1 | ROC-AUC 0.850–0.853, "within 0.003 of one another" | **0.846–0.853**, a spread of 0.0068 — more than double the stated 0.003 |

The abstract's wording on the alarm budget — "decision thresholds chosen to
keep **validation** false alarms at or below 1%" — is precise and needs no
change. It is the *test* FPR that exceeds the budget, which Table 6 already
reports.

**The SVC exceeded the 1% test FPR budget on all five seeds:** 0.012111 (42),
0.010493 (43), 0.012027 (44), 0.013060 (45), 0.017874 (46). This strengthens
the §4.3 threshold-transfer finding; it should be stated as "all five seeds"
rather than as a single-run observation.

### 3.4 Cost comparison needs correcting

Measured over five seeds, with the published single run for comparison:

| Model | Five-seed range | Published (seed 42) |
|---|---|---|
| Random Forest | 33.3–34.0 s | 31.1 s |
| 1-D CNN | 205–343 s | 159.6 s |
| Nyström + linear SVC | 1,341–3,093 s | 3,093.6 s |

**No standard deviation is quoted for training time, because the spread is not
a seed effect.** The published SVC run and sweep seed 42 are the *same seed*
and the *same configuration*, yet took 3,093.6 s and 1,858.6 s respectively —
a 1.7× difference from machine load alone. Table 5 already notes that timings
come from a machine whose load was not controlled; these ranges should be read
the same way, as indicative of relative cost only.

The CNN comparison has a second, real cause: the published run early-stopped at
19 epochs where the others ran 26–30, so part of its lower time is less
training, not faster training.

The ordering RF ≪ CNN ≪ SVC holds throughout, but any "100×" style claim should
be stated as a range rather than computed from the single published pair, which
happens to combine the slowest SVC run with the shortest CNN run.

## 4. Item 4 — alternative contiguous split

`split.rotate_fraction = 0.70` rotates each (block, label) stream before the
contiguous cut, giving train = [0.70,1.00)+[0.00,0.40), validation =
[0.40,0.55), test = [0.55,0.70). Validation and test are both strictly
contiguous; only train wraps.

Verified row by row against the published split:

- new test ∩ published test = **0 rows**; new validation ∩ published test = **0 rows**;
- **100%** of the new test rows (182,402) come from the published *training* split;
- train overlap 486,322 / 851,106 = **57.14%**, exactly 0.40/0.70 as the geometry predicts;
- split sizes and class priors identical to the published split by construction
  (851,106 / 182,382 / 182,402, all ≈60.71% malicious); all ten leakage checks pass.

This is what item 4 requires: the FPR-constrained protocol is applied to data
that never informed it.

Default `rotate_fraction = 0.0` reproduces the published protocol byte for
byte — verified by comparing all 20 blocks × 6 columns of the regenerated
manifest against the committed one (no differences), and covered by a test.

### 4.1 Results, seed 42

| Model | Published test | Rotated test |
|---|---|---|
| Random Forest | acc 0.655771, recall 0.438040, FPR 0.007828, ROC-AUC 0.852824 | acc 0.727278, recall 0.552433, FPR 0.002581, ROC-AUC 0.872863 |
| Nyström + linear SVC | acc 0.653874, recall 0.437687, FPR 0.012111, ROC-AUC 0.850177 | acc 0.722794, recall 0.544856, FPR 0.002288, ROC-AUC 0.871860 |
| 1-D CNN | acc 0.650985, recall 0.426182, FPR 0.001688, ROC-AUC 0.850978 | acc 0.724109, recall 0.545597, FPR 0.000084, ROC-AUC 0.873574 |

All three score markedly higher on the rotated window. **Pooled recall must not
be used to interpret this**, for the reason below.

### 4.2 The difference is UDP-flood ambiguity by capture position

Pooled recall on this dataset is almost entirely a function of the UDP-flood
records in the window, because UDP-flood recall is ~0.09 while the other seven
types are detected at ≥0.986. Per attack type, Random Forest at the locked
operating point:

| Attack type | Support | Published recall | Rotated recall | Δ detected |
|---|---|---|---|---|
| UDPFlood | 68,602 | 0.092942 | **0.277645** | **+12,671** |
| HTTPFlood | 21,123 | 0.999953 | 0.999905 | −1 |
| TCPConnectScan | 3,009 | 1.000000 | 0.999335 | −2 |
| UDPScan | 2,387 | 1.000000 | 0.999581 | −1 |
| SYNScan | 3,007 | 1.000000 | 1.000000 | 0 |
| SlowrateDoS | 10,971 | 1.000000 | 1.000000 | 0 |
| SYNFlood | 1,459 | 1.000000 | 1.000000 | 0 |
| ICMPFlood | 174 | 1.000000 | 1.000000 | 0 |

Net true-positive change +12,667, of which UDP-flood accounts for 12,671 —
**the whole effect**; the other seven types lose 4 records between them.

**The attack-type composition of the two windows is identical.** The split is
stratified per (block, label), so every block contributes exactly 15% of its
rows to test regardless of rotation: UDP-flood support is 68,602 in both
windows and its share of test malicious rows is 61.95% in both. An explanation
based on the rotated window containing *fewer* UDP-flood rows is therefore
wrong — there are exactly as many.

What differs is how many of those UDP-flood records carry the dominant
conflicting feature vector (udp, Dur = 0, TotPkts = 1, TotBytes = 42,
State = REQ, sTtl = 63, Rate = 0, Cause = Status), which occurs 271,476 times
in the dataset as 159,875 UDP-flood and 111,601 benign records and is
irreducibly ambiguous:

| Test window | UDP-flood rows carrying the dominant ambiguous vector |
|---|---|
| Published, tail of each stream | 51,933 / 68,602 = **75.70%** |
| Rotated, old [0.55, 0.70) | 27,137 / 68,602 = **39.56%** |

### 4.2.1 How much of the effect ambiguity density explains — measured

Splitting the UDP-flood test rows by whether they carry the dominant vector
(`udpflood_by_ambiguity_*.csv` in each `split_composition/` directory):

| | Published window | Rotated window |
|---|---|---|
| Carrier support | 51,933 | 27,137 |
| **Carrier recall** | **0.000000** | **0.000000** |
| Non-carrier support | 16,669 | 41,465 |
| **Non-carrier recall** | **0.382506** | **0.459351** |

Carrier recall is exactly zero in both windows: under the FPR ≤ 1% cap the
models never fire on the ambiguous vector, because 111,601 of its 271,476
occurrences are benign. Every UDP-flood true positive comes from non-carriers.

Decomposing the +12,671 UDP-flood true positives:

- holding non-carrier recall at the published 0.382506 and applying it to the
  rotated window's 41,465 non-carriers predicts 15,861 detections;
- so **ambiguity density explains 9,485 of 12,671 = 74.9%**;
- the residual **3,186 = 25.1%** is non-carrier recall itself rising from
  0.382506 to 0.459351, a 20.1% relative improvement, attributable to the
  different training composition and the different frozen threshold
  (0.503424 against 0.478734).

So density is the dominant mechanism but **not the whole effect**, and the
write-up should quote the 75/25 split rather than claiming UDP-flood ambiguity
accounts for all of it. (The commit that first recorded this analysis,
`4ad4254`, says UDP flood "accounts for the entire effect" of the *pooled*
change, which is true at the attack-type level — UDP flood supplies 12,671 of
the +12,667 net change — but it should not be read as ambiguity density alone
explaining the within-UDP-flood change. This section is the measured
statement.)

The vector's density rises along capture position inside both UDP-flood
sessions:

| Position in stream | Block 4 | Block 14 |
|---|---|---|
| [0.00, 0.40) | 25.80% | 19.05% |
| [0.40, 0.55) | 10.47% | 44.76% |
| [0.55, 0.70) | 42.44% | 46.37% |
| [0.70, 0.85) | 46.73% | 46.48% |
| [0.85, 1.00) | **59.43%** | **71.55%** |

**Wording for the paper.** UDP-flood records carrying the ambiguous 42-byte
single-packet vector are unevenly distributed along capture position, becoming
denser toward the end of each session. The published test window is the tail of
each stream and is therefore ambiguity-heavy; a window drawn from the middle of
the stream contains the same number of UDP-flood records but fewer ambiguous
ones.

**Do not write** that the rotated split shows the published results were
uncontaminated, and **do not write** that the published window was
intrinsically harder. Neither follows. The comparison shows where the
irreducible ambiguity sits in capture order, not that the protocol was clean.

### 4.2.2 What this experiment actually establishes

This is more than a pass on item 4, and it should not be presented as an
awkward result to explain away.

The same model, the same hyperparameters and the same locked operating-point
protocol swing pooled recall from 0.438040 to 0.552433 on the basis of **window
position alone**, with the entire movement inside a single attack type. All
three model families move together — rotated recall 0.552433 (Random Forest),
0.544856 (SVC), 0.545597 (CNN) — so this is a property of the data, not of any
one learner.

Two consequences for the paper:

1. **Pooled recall is an unstable quantity across contiguous windows on this
   dataset.** A ±0.11 swing is available from the choice of which contiguous
   15% serves as test, with no change to the model or the protocol. Any
   published 5G-NIDD recall figure that does not state its window position is
   therefore not comparable with any other, which sharpens the paper's
   methodological critique considerably.
2. **This is direct evidence for the Eq. (5) representation-limit argument.**
   Carrier recall is exactly 0.000000 in both windows, so the detectable
   fraction of UDP-flood traffic is fixed by how many records carry an
   irreducibly ambiguous vector, and nothing the model does changes it. The
   label-conflict bound is not an abstract ceiling computed off to one side of
   the results — it is the mechanism that moves the headline number.

**Per-attack-type recall conditioned on ambiguity is the only statistic that is
comparable between windows.** Pooled recall, pooled accuracy and pooled F1 all
inherit the window's ambiguity composition and should not be compared across
splits — in this paper or against the 99%-accuracy literature.

Consistent with this, the rotated split shares more feature vectors across
splits than the published one: **711,650** rows versus **686,830**
(`leakage_audit.json` in each results directory). Dataset-level ambiguity is of
course unchanged — 33,709 conflicting vectors, 632,402 rows, ceiling 76.8455%
in both, since that is a property of the representation and not of the split.

### 4.3 Boundary asymmetry, to state explicitly

`purge_rows` is 0, so no gap is inserted at any split boundary. In capture
order the rotated test window at [0.55, 0.70) is immediately **followed** by
training data as well as preceded by it, whereas the published test window ends
the stream and has training data on one side only. The rotated window therefore
has adjacency to training rows on both edges. This is a property of the
alternative cut that should be reported, not hidden; running it with
`purge_rows > 0` would quantify how much it matters and has not been done.

### 4.4 Confound in the CNN comparison

CNN early stopping is driven by validation PR-AUC, and the rotation changes the
validation set, so part of any old-vs-new CNN difference is training length
rather than the split. The fresh-split run is therefore repeated across seeds
42, 43 and 44; results for 43 and 44 will be appended here. A single-seed CNN
comparison must not be reported without this confound stated.

## 5. Item 3 — what is and is not computable

The faculty asked for per-source and per-second aggregates (flows per source
per second, bytes per second). **Neither is computable from `Combined.csv`:**

- there is no source identifier — the 51 columns are Argus flow statistics with
  no address or port field;
- there is no clock — `Offset` is an int64 byte offset into the capture (it
  reaches 38,032,036 over 1,215,890 rows, about one distinct value per row),
  and `Dur`/`RunTime` are durations, not timestamps.

**Route (a), temporal window aggregates** — implemented in
`build_window_features.py`: causal aggregates (flow count, byte sum/mean,
packet sum/mean, protocol mix) over the K records immediately preceding each
row within its own capture block, K ∈ {10, 50, 100}. Windows never cross a
block boundary, are strictly backward-looking, and read no label column. This
tests **temporal** aggregation using row order as a proxy for time — the same
proxy M2 relies on. It is **not** per-source aggregation, and the write-up must
say so.

**Route (b), the per-session Fairdata files** — the stronger test, and much
cheaper than first assumed. None of these files are currently on disk
(`M3-sampled-incremental/results/m3-implementation/data/` holds only
`manifest.json`), but the manifest records official filenames, sizes and
publisher checksums:

| Archive | Download | Extracts to |
|---|---|---|
| `BS2_each_attack_argus.zip` | 10.2 MB | ~57.8 MB, 10 per-session `.argus` |
| `BS2_each_attack_csv.zip` | 17.3 MB | ~171 MB |
| `BS1_each_attack_csv.zip` | 23.5 MB | ~251 MB |
| `BTS1_BTS2_fields_preserved.zip` | 44.4 MB | 450 MB CSV |
| `BS2 GTP removed.zip` | 1.43 GB | packet captures — not needed for flow features |

M3's own committed code (`sdn/inspect_session_labels.py`,
`sdn/prepare_flow_labels.py`) reads `SrcAddr`, `DstAddr`, `Sport`, `Dport`,
`StartTime` and `LastTime` from these exports, so the faculty's actual request
**is** computable from route (b), for roughly 95 MB of downloads using the
existing `scripts/fetch_dataset.py`. Route (b) has not been authorised and has
not been run.

## 6. Verification of the numbers already in the paper

Re-checked against the committed artifacts before any revision. All reconcile
exactly.

| Table | Check | Result |
|---|---|---|
| Table 3 | 9 session rows and all 4 column totals vs `split_manifest.csv` | exact; all 20 blocks covered |
| Table 5 | 36 metric and count cells vs `three_model_fpr1pct_summary.csv` and the confusion CSV | all match; every metric recomputes from the printed TN/FP/FN/TP; all three sum to n = 182,402 |
| Table 6 | the derived "Test FPR ÷ validation FPR" column (0.9 / 10.4 / 1.2 / 9.3) and the "recall fell 0.096–0.105" claim | exact from unrounded values: 0.8913, 10.3873, 1.2121, 9.3063; drops 0.0960 / 0.0974 / 0.1052 |
| Table 7 | 21 cells vs the three Stage L records | all match; all three sum to n = 173,527 |

Minor consistency point, not an error: the paper calls the second base station
**BS2** (Table 3 caption) while the repository artifacts label the two stations
**BS0** and **BS1**. Worth aligning so a reviewer comparing paper to repo is
not tripped up.

For item S1 (§4.2, p. 14), the unrounded values are **0.786126** (Random Forest
test accuracy at the F1-selected threshold, from
`random_forest/test_metrics.json`: 0.786126248615695) against the ceiling
**0.786258** (`empirical_feature_space_ceiling`). The difference is
0.00013175 = 0.0132 pp, so the arithmetic in the paper is correct; only the
printed 4-dp values make it read as 0.02 pp.

## 7. Length — measured, for item 6

Body text with the running header stripped: **11,496 words over 25 pages**,
mean **460 words/page**.

| Page | Words | Content |
|---|---|---|
| 1 | 507 | Front matter, abstract |
| 2–4 | 568 / 649 / 450 | §1, §2, Table 1 |
| 5–6 | 228 / 246 | §3.1, Figure 1 |
| 7 | 415 | Table 2, §3.2, Table 3 |
| 8–9 | 521 / 592 | §3.3, Table 4 |
| 10–11 | 640 / 615 | §3.4 M2 methods, §3.5 M3 methods |
| 12–15 | 440 / 303 / 414 / 301 | §3.6, §4.1–4.4, Tables 5–7, Figures 2–3 |
| 16–19 | 231 / 346 / 213 / 440 | §4.5 M2 results, §4.6 M3 results, Tables 8–9, Figures 4–5 |
| 20–21 | 631 / 702 | §5.1–5.5 |
| 22 | 572 | §5.6, Table 10 |
| 23 | 544 | §6, Declarations |
| 24–25 | 566 / 362 | References |

**Correction to the correction list:** M2/M3-dedicated material is about
**7–8 of 25 pages (≈30%)**, not half. Pages 16–19 average only 258 words/page
against the 460 mean, because they are mostly synthetic-data figures and
tables — which is probably why they read as occupying more. The underlying
point stands: those pages carry the least evidence per page.

The page budget must also absorb the new Phase 3 results, estimated at
**+2.5 pages** (three tables plus roughly 900 words), so reaching ≤ 15 pages
means removing about 12.5 pages of existing material, not 10.

Measured savings available, assuming all three paradigms stay in the paper:
merging Figure 1 + Table 2 + Table 10 into one compact status table ≈ −1.4 pp;
dropping Table 1's last three rows and compressing it ≈ −0.7 pp; condensing the
M2 and M3 methods and results into one shorter diagnostics section ≈ −4.5 pp;
tightening related work ≈ −0.8 pp; tightening the discussion and folding §5.4
in ≈ −1.5 pp; trimming the introduction ≈ −0.3 pp; shortening acknowledgements
≈ −0.2 pp. That totals about −9.4 pp, giving roughly **18 pages** with the new
results included, or **16–17 pages** if Figures 2–3 and the §4.4 held-out table
move to supplementary material.

These are estimates (±1 page) from the measured word counts and page
occupancy; they can only be confirmed by rendering the revised source. On this
evidence ≤ 15 pages is not reachable while all three paradigms and the four new
experiments stay in the main text, so the target needs either supplementary
material or a word with the editor.

Whatever is cut, the evidence grading that Figure 1, Table 2 and Table 10 carry
should survive as a single compact table with one row per pipeline and explicit
columns for data source, evidence type, and what is *not* established. That
grading is what the review praised; reformatting it is fine, losing it is not.

## 8. Open items

- **ORCIDs** — not available. Leave placeholders for Nithis Nandhan E,
  Sanjay J, Jani Rose Lawwellman and Kalaavathi B; keep Jaivarshan V's existing
  0009-0001-4147-3934. None have been invented here.
- **Tagged release (item 5)** — no tag exists (`origin` has 0 tags) and
  `aa5a572`, cited on pp. 7, 13, 22 and 23, is absent from history. A tag name
  has not been chosen, and nothing has been tagged or pushed for it. The tag
  should be created only once items 1–4 have landed.
- **Figures 2–5 and the derived-analysis scripts** — not in the repository and
  not recoverable; they were produced outside version control. Data and code
  availability must say that plainly rather than implying they are archived.
  Replacement plotting scripts are planned.
- **Route (b) for item 3** — not authorised; see §5 for the cost estimate.
- **Scope** — removing the M2 or M3 sections is a co-author decision that has
  not been taken. All planning here assumes all three paradigms stay.
