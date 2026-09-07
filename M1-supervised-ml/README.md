# M1 — Supervised Machine Learning

Supervised baseline for DDoS/malicious-traffic detection on the 5G-NIDD
dataset, comparing **Random Forest**, **SVM** and a **1-D CNN**.

> **Status:** Stage D complete — data pipeline only.
> No models have been trained and no detection results exist yet.
> Nothing in this document should be read as an experimental result.

---

## 1. Objective

Classify individual network flow records as **Benign (0)** or
**Malicious (1)** using labelled 5G-NIDD flow features, under a
leakage-safe and reproducible protocol, so that the three model
families can be compared on identical data.

## 2. Dataset

- **File:** `data/raw/Combined.csv` (git-ignored, ~263 MB, never committed)
- **Shape:** 1,215,890 rows x 52 columns
- **Target:** `Label` — Malicious 738,153 (60.71%) / Benign 477,737 (39.29%)
- **Structure:** the file concatenates **20 contiguous capture sessions** —
  2 base stations x 10 sessions. Blocks are detected where the Argus
  `Offset` column resets (19 resets); the single decrease in `Unnamed: 0`
  marks the base-station boundary. `Offset` is non-decreasing *inside*
  every block, so row order equals capture order.

Configure the path in `config/m1_config.yaml` (`dataset.raw_path`,
repo-relative). The dataset is never downloaded automatically.

## 3. Target definition

| Raw `Label` | Binary target |
|---|---|
| `Benign` | 0 |
| `Malicious` | 1 |

Malicious is the positive class. Any label value not declared in
`positive_class_values`/`negative_class_values` raises an error — labels
are never silently coerced.

`Attack Type` and `Attack Tool` are retained in the raw frame for later
per-attack / per-tool analysis but are **structurally barred** from the
feature matrix: both are perfectly aligned with `Label` (every non-Benign
attack type maps to Malicious, and vice versa), so either would trivially
reveal the target.

## 4. Feature selection

**31 of 52 columns** are retained (26 numeric + 5 categorical), expanding
to **67 model features** after one-hot encoding. Full per-column
rationale: [`results/feature_decisions.csv`](results/feature_decisions.csv)
and [`results/feature_decisions.md`](results/feature_decisions.md).

### Retained

- **Categorical (one-hot):** `Proto`, `sDSb`, `dDSb`, `Cause`, `State`
- **Numeric:** `Dur`, `sTtl`, `dTtl`, `TotPkts`, `SrcPkts`, `DstPkts`,
  `TotBytes`, `SrcBytes`, `DstBytes`, `sMeanPktSz`, `dMeanPktSz`, `Load`,
  `SrcLoad`, `DstLoad`, `Loss`, `SrcLoss`, `DstLoss`, `pLoss`, `Rate`,
  `SrcRate`, `DstRate`, `SrcWin`, `DstWin`, `TcpRtt`, `SynAck`, `AckDat`

### Excluded (21 columns)

| Columns | Reason |
|---|---|
| `Unnamed: 0`, `Seq`, `Offset` | Identifiers / acquisition artifacts encoding capture position |
| `RunTime`, `Mean`, `Sum`, `Min`, `Max` | **Byte-identical copies of `Dur`** (verified) |
| `sTos`, `dTos` | Redundant numeric encodings of `sDSb`/`dDSb` (`sTos`↔`sDSb` verified **bijective**, 12↔12 levels) |
| `sHops`, `dHops` | Deterministic functions of the retained, finer `sTtl`/`dTtl` |
| `SrcGap`, `DstGap` | Near-zero variance: 77% missing, and ~all present values are exactly `0.0` |
| `SrcTCPBase`, `DstTCPBase` | TCP initial sequence numbers — pseudo-random identifiers (up to 2^32) |
| `sVid`, `dVid` | Constant (single value 610); `P(malicious \| present) = 0.00` — a pure capture artifact |
| `Label`, `Attack Type`, `Attack Tool` | Target and target-derived metadata |

The `sTos`/`dTos`/`sHops`/`dHops` and `SrcGap`/`DstGap` exclusions were
**discovered during Stage D verification**, not inherited from the
original inspection notes.

> **Ambiguous column kept with a caveat:** `Cause` (Argus record type:
> Start/Status/Shutdown) is acquisition-related but is a legitimate flow
> attribute. It is retained and flagged for an ablation check in Stage E.

Feature *exclusion/cleaning* (above) is kept strictly separate from
*optional feature selection* (PCA / SelectKBest / RFE / mutual
information), **none** of which is applied — that decision is deferred
until model behaviour on the real schema is observed.

## 5. Missing-value strategy

Missingness is highly structured, and identical missing masks group as:

| Group | Missing | Meaning |
|---|---|---|
| `sTos`,`sDSb`,`sTtl`,`sHops` | 0.02% | 214 non-IP L2 frames (lldp/llc/arp) |
| `dTos`,`dDSb`,`dTtl`,`dHops` | 77.56% | no reverse traffic observed |
| `SrcGap`,`DstGap`,`SrcTCPBase` | 77.08% | **exactly** `Proto != tcp` (0 mismatches) |
| `SrcWin` / `DstWin` / `DstTCPBase` | 80.1% / 85.4% / 81.1% | TCP-only fields |

- **Numeric:** median imputation, fitted on the training split only.
- **Categorical:** an explicit `__missing__` level (absence of a
  destination DSCP class is genuine network semantics, not noise).
- **No missingness-indicator columns are added.** Two reasons: (a) the
  missingness is already fully explained by retained observed features
  (`SrcGap` missing ⟺ `Proto != tcp`, exactly), so indicators add no
  information; (b) indicators would encode capture artifacts — e.g.
  `P(malicious | sVid missing) = 0.67` vs `P(malicious | present) = 0.00`.
  Rows are never dropped for being incomplete.

## 6. Numerical preprocessing

`median impute → skew-gated log1p → StandardScaler`

5G-NIDD flow statistics are extremely heavy-tailed (`Load` skew ≈ 188,
`DstRate` ≈ 191). Rather than transforming everything blindly, `log1p` is
applied **per column** only when, on the **training split**:

```
skew > log1p_skew_threshold (2.0)   AND   min >= 0
```

On the real data this transforms **25 of 26** numeric columns and
correctly leaves `Dur` (skew 0.741) untouched. The non-negativity guard
keeps `log1p` valid; all retained numeric features were verified
non-negative, with no infinities anywhere.

## 7. Categorical encoding

One-hot (`handle_unknown="ignore"`), so nominal categories never receive
an artificial ordinal ordering, and a category unseen during training
becomes an all-zero block at transform time instead of an error. This
representation is valid for all three model families.

## 8. Split methodology

**`block_label_contiguous`** — within each of the 20 capture blocks, and
within each label stream *separately*, rows are cut by position:
first 70% → train, next 15% → validation, last 15% → test.

Rejected alternatives, with measured evidence:

| Alternative | Why rejected |
|---|---|
| Random row split | Scatters adjacent, highly-correlated flows from the same attack burst across train/test |
| Plain contiguous cut per block | Attacks occupy a time window inside each capture → prior shifts **train 69.4% → val 47.8% → test 32.9%** malicious, with single-class val/test segments in 8 blocks |
| Full block hold-out | Each attack type exists in only **2** blocks (one per base station) → removes whole attack types from training |
| Base-station split (BS0/BS1) | Prior shifts **44.1% → 85.5%** malicious |

The chosen strategy preserves the class prior by construction
(**60.709% / 60.709% / 60.708%** malicious, spread 0.0017pp), keeps all
20 blocks, both base stations and all 9 attack types in every split, and
respects capture order within each class stream. It uses **no RNG** and
is therefore exactly reproducible.

### 8.1 Stage E audit — why this protocol is the primary one

Stage E re-derived the block structure independently and quantified every
practical alternative before confirming the choice. Measured results:

| Protocol | Train / Val / Test | Prior spread | Coverage | Test rows whose vector occurs in train |
|---|---|---|---|---|
| **A. block_label_contiguous (current)** | 70 / 15 / 15% | **0.001 pp** | all 20 blocks, 9 attack types, 6 tools, both BS in every split | 72.97% |
| B1. global contiguous (whole file) | 70 / 15 / 15% | **50.34 pp** | val is 99.97% malicious from 1 block; 4 attack types absent from test | 35.62% |
| B2. per-block contiguous (unstratified) | 70 / 15 / 15% | **36.52 pp** | ICMPFlood absent from test | 81.69% |
| C. block-held-out | **infeasible** | **≥ 27.82 pp** | see below | — |
| D. base-station held out | 49 / 11 / 40% | **41.36 pp** | full coverage | **74.45%** |

**C is structurally infeasible.** Each of the 10 session types exists in
exactly 2 blocks (one per base station), so a three-way block hold-out
that keeps every attack type in training is impossible. Exhaustively
searching all 1,024 one-block-per-session pairings gives a **minimum test
fraction of 40.07%** and a **minimum train/test prior gap of 27.82 pp**;
**zero** pairings reach a gap below 2 pp. The cause is block-size
dominance: block 4 (UDPFlood, BS0) is 38.47% of the dataset and is 62%
benign, while block 14 (UDPFlood, BS1) is 23.54% and is 98% malicious, so
whichever one lands in test drags the prior with it.

**Cross-split repetition cannot be fixed by any split.** Feature-vector
overlap is a property of the data, not the partition: holding out an
entire base station *raises* it (74.45%) and holding out whole unseen
capture sessions only lowers it to 69.66%, versus 72.97% for the current
protocol. 5G-NIDD flow records repeat massively (345,621 distinct vectors
for 1,215,890 rows), so ~70% overlap is intrinsic at this granularity.
Choosing D or C would therefore pay a 27–41 pp prior distortion and buy
essentially no reduction in repetition exposure.

### 8.2 What the overlap is — and is not

The 72.97% figure must not be reported as "data leakage" without
qualification. Five distinct things are separated here:

| Category | Present? | Evidence |
|---|---|---|
| 1. Preprocessing / target leakage | **No** | preprocessing fitted on train rows only (scaler saw exactly 851,106); target, `Attack Type`, `Attack Tool` and identifiers structurally barred |
| 2. Exact-feature repetition | **Yes, 72.97%** | intrinsic to the data; unchanged by any split (see §8.1) |
| 3. Capture/session dependence | **Yes** | all 20 blocks appear in all splits by design |
| 4. Memorisation opportunity | **Yes, 18.07% of test rows** | label-pure vectors shared with train, scored 99.90% by a lookup table (§12.1) |
| 5. Genuine generalisation | **Partially measured** | 27.03% of test rows have a vector never seen in train |

Only categories 3 and 4 limit the interpretation; category 1 — the one
that would invalidate results — is absent.

### 8.3 Exact wording for describing M1's evaluation scope

> M1 is evaluated under a **within-capture (within-session) protocol**:
> all 20 capture sessions contribute to train, validation and test, split
> by position within each session and label stream. Results therefore
> measure the ability to classify **later flows from capture sessions the
> model has already observed**, with substantial exact-feature repetition
> between splits (72.97% of test rows share a feature vector with
> training data; 18.07% are label-pure repeats). Results **do not**
> measure unseen-capture, unseen-session, unseen-base-station or
> unseen-attack generalisation, and must not be described as such.

An optional `split.purge_rows` gap discards rows at each segment boundary
to reduce adjacency correlation (default `0`).

Manifest: [`results/split_manifest.csv`](results/split_manifest.csv)
(per block: base station, attack types, row counts, label counts, split
assignment).

| Split | Rows | Malicious |
|---|---|---|
| train | 851,106 | 60.71% |
| val | 182,382 | 60.71% |
| test | 182,402 | 60.71% |

### 8.4 Recommended secondary experiment (not implemented)

Because the primary protocol cannot measure unseen-capture
generalisation, a **secondary** experiment is recommended for a later
stage. It is *not* implemented now and does not affect the primary
protocol.

Hold out the **BS1 captures of the six small sessions** — blocks
10, 11, 12, 13, 15, 17 (SYNScan, TCPConnectScan, UDPScan, ICMPFlood,
SYNFlood, SlowrateDoS/Slowloris) — while their BS0 counterparts remain in
training, so no attack type is removed from training:

| Property | Value |
|---|---|
| Test rows | 74,700 (6.14% of dataset) |
| Test malicious | 54.34% (train pool 61.13%, gap 6.79 pp) |
| Attack types absent from train pool | **none** |
| Attack types testable | 6 + Benign |
| Test rows whose vector occurs in train pool | 69.66% |

This deliberately excludes the giant UDPFlood blocks (4/14), which is
exactly what makes it feasible where a full block hold-out is not. A
leave-one-attack-out variant is also definable for unseen-*attack*
generalisation, but it changes the research question from "detect known
attack classes" to "detect novel attacks" and should be reported
separately if used.

### 8.5 M1 / M2 / M3 comparability

`PROJECT_SPEC.md` requires the three methodologies to be evaluated under
comparable traffic scenarios with consistent metric definitions. M1 can
guarantee the metric definitions and the underlying capture sessions, but
**not an identical split**: M1 classifies individual flow records, whereas
M2 (entropy over sliding windows) and M3 (sampled telemetry, incremental
learning) operate on different aggregation units, so a row-level partition
has no exact counterpart there. What M1 can offer for alignment is the
capture-block structure (`results/split_manifest.csv`, 20 blocks with base
station, session, attack type and tool), which is defined on the raw
capture and is therefore reusable by any methodology. Forcing an
artificial identical row split is **not** attempted. No claim is made here
about M2/M3 internals.

## 9. Duplicate policy

Duplicates are **quantified, never silently removed** — repeated flow
patterns are genuine network behaviour and dropping them would alter the
experimental distribution. `duplicates.drop_exact_duplicates` is an
explicit opt-in (currently unimplemented by design).

| Metric | Value |
|---|---|
| Unique feature vectors | 345,621 of 1,215,890 |
| Duplicate rows | 870,269 |
| Groups carrying **both** labels | 33,709 |
| **Irreducible (Bayes) error** | **281,533 rows = 23.15%** |
| Implied ceiling on accuracy | **≈76.85% overall / 78.63% on test** |

See §12 — this is the single most important limitation of M1.

## 10. Class imbalance

The imbalance is mild (60.71% / 39.29%), so **no resampling and no SMOTE**
is used. Strategy is `class_weight`:
`class_weight="balanced"` for Random Forest and SVM, and an equivalent
Keras `class_weight` for the CNN. Any divergence must be documented.

## 11. Model-compatible representation

All three models consume **the same canonical 67-feature matrix** in
**the same fixed order** ([`results/feature_order.json`](results/feature_order.json)),
so comparisons are not confounded by differing inputs.

- **Random Forest** — the matrix directly; one-hot avoids false ordinality.
  Scaling is harmless to trees and is kept for a single shared representation.
- **SVM** — the same matrix; standardisation is required for the RBF kernel.
  **Computational strategy:** an RBF `SVC` is O(n²)–O(n³), so the full
  ~851k-row training split is intractable. A **reproducible stratified
  subsample of the training split only** is used
  (`models.svm.train_subsample`, default 50,000 rows, seeded, preserving
  the training class proportion — verified 60.71%). Validation and test
  remain complete and untouched; the subsample is never chosen using test
  performance. Indices are saved to `svm_train_indices.npy`. The SVM is
  **not** replaced by another model family.
- **1-D CNN (TensorFlow/Keras)** — input shape **(67, 1)**: each feature
  occupies one position along the convolution axis with a single channel.
  > **Limitation, stated explicitly:** this is a *spatial* arrangement of
  > tabular features. Feature ordering carries **no temporal meaning**,
  > and the CNN must **not** be described as capturing temporal
  > dependencies between flows. It is a comparative deep-learning model
  > for tabular network features only.

## 12. Known limitations

> All figures below were recomputed directly from the saved processed
> 67-feature matrices during the Stage D review (not from the raw frame).

1. **[!] 23.15% irreducible label ambiguity.** 33,709 of 345,621 distinct
   processed feature vectors carry *both* labels, covering 632,402 rows.
   Summing per-vector minority counts gives **281,533 forced errors**:

   | Scope | Rows | Unique vectors | Conflicting vectors | Forced errors | Ceiling |
   |---|---|---|---|---|---|
   | overall | 1,215,890 | 345,621 | 33,709 | 281,533 | **76.85%** |
   | train | 851,106 | 258,881 | 31,529 | 197,846 | 76.75% |
   | val | 182,382 | 52,114 | 6,496 | 41,957 | 77.00% |
   | test | 182,402 | 47,559 | 3,287 | 38,987 | **78.63%** |

   No function of these 67 features can exceed **78.63%** accuracy on the
   test split — that is a hard mathematical cap. A train-fitted
   exact-vector lookup table scores **73.51%** on test (§12.1); that number
   is a **memorisation reference baseline, not a lower bound or floor** —
   a trained model may legitimately score below it.

2. **[!] Forced errors fall almost entirely on Benign traffic — FPR floor
   ≈ 58.9%.** Malicious is the majority in essentially every conflicting
   group, so the accuracy-optimal rule labels those vectors Malicious.
   **281,529 of the 281,533** forced errors are Benign rows — **58.93% of
   all Benign traffic**. Accuracy and false-positive rate cannot both be
   good on this representation:

   | Rule on conflicting vectors | Max recall | Implied FPR |
   |---|---|---|
   | predict Malicious (accuracy-optimal) | 99.999% | **>= 58.93%** |
   | predict Benign (FPR-minimising) | **<= 52.47%** | low |

   A ~59% false-positive rate is operationally unusable for a DDoS
   detector, so **FPR — not accuracy — is the binding constraint on M1.**
   Report the full confusion matrix; headline accuracy would be misleading.

3. **Dominant conflicting vector (verified exactly):**
   `udp, Dur=0, TotPkts=1, TotBytes=42, State=REQ, sTtl=63, Rate=0`
   occurs **271,476 times (22.33% of the dataset)** — 159,875 UDPFlood and
   111,601 Benign, all with `Cause=Status`. At this flow-feature
   granularity these hping3 UDP-flood records are byte-identical to benign
   single-packet UDP flow records, so no function of these features can
   separate them. 99.997% of conflicted rows are UDP; seven of the eight
   attack types have **zero** forced errors (HTTPFlood has 4).
   **UDPFlood is therefore the most ambiguous/difficult attack type at the
   current flow-feature granularity.** No claim is made here about how any
   model will actually perform on it — that is a Stage E measurement.
   Window/aggregate representations (as in M2 and M3) operate at a
   different granularity and are not subject to this particular limit.

4. **[!] The split measures WITHIN-session generalisation only.** All 20
   capture blocks appear in all three splits, so **no capture session is
   ever held out**. **72.97%** of test rows have a feature vector that also
   occurs in train, and **18.07%** of test rows are label-pure duplicates of
   training rows (memorisable without generalising). Results must **not**
   be described as unseen-capture, unseen-session or unseen-attack
   generalisation.

5. `Cause` is acquisition-related and retained pending a Stage E ablation
   (see review notes: MI with the label is only 0.006 nats against a label
   entropy of 0.670, and five attack sessions are 100% `Start`).

6. Results are per-flow only. Controller CPU/memory, flow-table counts,
   throughput and time-to-detect are **not** derivable from this offline
   pipeline and are deliberately not fabricated — they belong to later
   SDN/testbed measurement.

### 12.1 Memorisation baseline — exact definition

A lookup table fitted on train and applied to test, used in Stage E as the
reference any model must beat to show it learned more than repetition.

- **Seen** = the test row's exact 67-feature vector occurs **at least once
  in the training split**. **Unseen** = it occurs zero times in train.
  (Seen/unseen is defined against *train only*; it is unrelated to whether
  a vector is label-pure globally.)
- **Prediction, seen:** the majority label of that vector's training rows.
  Vectors that are **conflicting in train** are handled by this same
  majority rule — no row is excluded. Exact 50/50 ties (**31,221** train
  vectors) break to **Malicious**.
- **Prediction, unseen:** the **training-set majority class = Malicious**
  (train is 60.709% malicious). This fallback is a choice, not a
  derivation: using Benign instead gives 57.80%.
- **Formula:** `accuracy = (# test rows whose predicted label equals its
  true label) / 182,402`.

| Group | Correct | Rows | Accuracy |
|---|---|---|---|
| seen in train | 95,106 | 133,098 | 71.4556% |
| ├ train-vector label-pure | 32,983 | 33,017 | 99.8970% |
| └ train-vector conflicting | 62,123 | 100,081 | 62.0727% |
| unseen in train | 38,983 | 49,304 | 79.0666% |
| **total** | **134,089** | **182,402** | **73.5129%** |

Reconciles exactly: 133,098 + 49,304 = 182,402 and 95,106 + 38,983 =
134,089. For context, the trivial always-Malicious rule scores **60.71%**.
The 79.07% on unseen rows reflects the class prior (those rows are 38,983
malicious vs 10,321 benign), not memorisation.

## 13. Leakage audit

Generated at every run → [`results/leakage_audit.json`](results/leakage_audit.json).
All 10 checks currently **PASS**: target excluded; `Attack Type`/`Attack
Tool` excluded; identifiers excluded; all 15 excluded columns absent;
preprocessing fitted on training rows only (scaler saw exactly 851,106
rows); no NaN/inf in any matrix; class prior stable across splits; feature
order deterministic and unique; cross-split duplicate vectors quantified;
no missingness indicators added.

## 14. Reproducibility

- Single `seed` in the config (42); the split itself uses no RNG.
- Preprocessing is fitted on training data only and serialised to
  `preprocessor.joblib`, reloadable for identical transforms (tested).
- Deterministic feature ordering, recorded in `feature_order.json`.
- Every run rewrites the manifests, metadata and audit.
- Paths are repo-relative; no machine-specific absolute paths.

## 15. Layout

```
M1-supervised-ml/
├── config/
│   ├── m1_config.yaml              # real experiment configuration
│   └── m1_config.synthetic.yaml    # loader/validation test config
├── preprocessing/
│   ├── data_loader.py              # config-driven CSV loading (no column logic)
│   ├── validation.py               # schema + dataset-level validation
│   ├── features.py                 # target construction + feature policy
│   ├── splitting.py                # block detection + the split + manifest
│   ├── transformers.py             # skew-gated log1p + ColumnTransformer
│   ├── reporting.py                # feature decision report
│   └── pipeline.py                 # orchestration, artifacts, leakage audit
├── experiments/
│   └── prepare_data.py             # Stage D CLI entrypoint
├── tests/                          # 101 tests, no 263 MB dependency
└── results/                        # generated reports (tracked, small)
```

Processed matrices go to `M1-supervised-ml/data/processed/`
(**git-ignored**, ~325 MB) and are regenerated by the CLI.

## 16. How to run

Dependencies (a repository-wide dependency file is deliberately deferred
until M2/M3 are developed):

```
pandas  numpy  scikit-learn  pyyaml  joblib  pytest
tensorflow   # 2.21.0 — Stage H 1-D CNN
matplotlib   # 3.11.1 — Stage J figures
```

Prepare the dataset (from the repository root):

```bash
python M1-supervised-ml/experiments/prepare_data.py \
    --config M1-supervised-ml/config/m1_config.yaml
```

Useful flags: `--dataset-path PATH` (override the configured path),
`--no-save` (run the audit without writing artifacts), `--nrows N`
(smoke test only — **not** a valid experimental run).

Run the tests (they use synthetic data only and do not need the real
dataset):

```bash
cd M1-supervised-ml && python -m pytest tests/ -q
```

## 16A. Stage F — Random Forest results

> Primary evaluation scope: **within-capture (within-session) generalisation**
> (see §8.3). These are not unseen-capture, unseen-session,
> unseen-base-station or unseen-attack results.

### Configuration

Selected by a fully-enumerated 18-candidate grid
(`max_depth` x `min_samples_leaf` x `max_features`) scored on
**validation PR-AUC** — threshold-free, so model choice stays independent
of threshold choice. The test split was not read until the configuration
and threshold were locked.

| Setting | Value |
|---|---|
| n_estimators | 200 |
| max_depth | 20 |
| min_samples_leaf | 20 |
| max_features | sqrt |
| class_weight | balanced (no SMOTE, no resampling) |
| random_state | 42 |
| decision threshold | **0.30** (selected on validation only) |

All 18 candidates were statistically indistinguishable — PR-AUC range
**0.000167**, accuracy range **0.000022** — so the tie-break selected the
simplest/cheapest model. Hyperparameters barely matter here: performance
is governed by the irreducible ambiguity of the representation (§12), not
by model capacity. Training took **31.1 s**; test inference **0.20 s**
(**0.0011 ms per flow**); the whole grid **966 s**.

### Test results (single locked evaluation)

| Metric | Value |
|---|---|
| Accuracy | **0.786126** |
| Precision | 0.739484 |
| Recall (TPR) | **0.999991** |
| F1 | 0.850230 |
| **False Positive Rate** | **0.544300** |
| Specificity (TNR) | 0.455700 |
| ROC-AUC | 0.852824 |
| PR-AUC | 0.867387 |

Confusion matrix (Malicious = positive), `FPR = FP / (FP + TN)`:

| | Predicted Benign | Predicted Malicious |
|---|---|---|
| **Actual Benign** | TN = 32,660 | **FP = 39,010** |
| **Actual Malicious** | FN = 1 | TP = 110,731 |

### Baseline comparison

| Reference | Accuracy | RF vs reference |
|---|---|---|
| Always-Malicious | 0.607077 | **+17.90 pp** |
| Exact-vector memorisation | 0.735129 | **+5.10 pp** |
| Empirical feature-space ceiling | 0.786258 | **−0.0132 pp** |

The RF **beats both baselines** and sits **0.0132 pp below the empirical
ceiling** — it has essentially saturated what this 67-feature
representation can express. No further modelling effort can add more than
~0.01 pp of accuracy at this granularity.

### 16A.1 The threshold criterion is the key caveat

The pre-registered rule was "keep 0.5 unless validation F1 improves by
>= 0.005". Validation F1 peaked at **0.835 at threshold 0.30**, so 0.30
was locked. That rule was applied correctly and on validation only — but
it drove the model to an operationally poor corner. The validation sweep
is almost **bimodal**, mirroring the Stage D frontier:

| Validation threshold | Recall | FPR | F1 |
|---|---|---|---|
| <= 0.35 | ~1.000 | ~0.611 | 0.835 |
| 0.40 - 0.45 | ~0.798 | ~0.286 | 0.805 |
| >= 0.47 | ~0.534 | **0.00075** | 0.696 |

Because Malicious is the majority class (60.7%), maximising F1 pushes the
model to label nearly everything malicious. The consequence is a **54.4%
test FPR — 39,010 of 71,670 benign flows misclassified**, which is
operationally unusable for a DDoS detector even though accuracy is near
the ceiling.

The alternative operating point (threshold ~0.47, **validation** FPR
0.00075 with recall 0.534) has **not** been evaluated on test, because
selecting it after seeing test results would be test-driven tuning. Which
criterion the project adopts is a decision to take **before** any further
test evaluation.

### 16A.2 Per-attack-type results (at the locked threshold)

| Attack Type | Support | Recall |
|---|---|---|
| UDPFlood | 68,602 | 1.000000 |
| HTTPFlood | 21,123 | 0.999953 |
| SlowrateDoS | 10,971 | 1.000000 |
| TCPConnectScan | 3,009 | 1.000000 |
| SYNScan | 3,007 | 1.000000 |
| UDPScan | 2,387 | 1.000000 |
| SYNFlood | 1,459 | 1.000000 |
| ICMPFlood | 174 | 1.000000 |
| **Benign** | **71,670** | **FPR 0.5443** (39,010 FP) |

**These recall figures must not be read as strong per-attack
discrimination.** At threshold 0.30 the model labels 82% of all test rows
malicious, so near-perfect recall is obtained together with a 54.4% false
positive rate. Per-tool results follow the same pattern (Hping3, Nmap,
Torshammer, Slowloris 1.000; Goldeneye 0.999953).

### 16A.3 Feature importance

Impurity importance aggregated to source columns (top 10): `sTtl` 0.167,
`Proto` 0.118, `sMeanPktSz` 0.095, `SynAck` 0.065, `Dur` 0.056,
`TcpRtt` 0.048, `Load` 0.043, `Rate` 0.042, `SrcRate` 0.040,
`SrcBytes` 0.036.

Permutation importance (validation only, 60k rows, PR-AUC scoring) is
**~0.000 for every feature except `sTtl` (0.0089)** — the metric is
dominated by the ambiguous duplicate vectors, so no single feature
changes it much.

On the flagged `Cause` question: `Cause` ranks **19th** with impurity
importance **0.0122** and a **negative** permutation importance
(−0.0077). It is **not** dominant, so the planned Stage D ablation is
lower priority than expected. Importance indicates model reliance within
this experiment only — it is not evidence of causality.

### 16A.4 Common operating-point protocol for Stage G/H (agreed before SVM/CNN)

The Stage F RF test result above (threshold 0.30) **remains the official
Stage F result and is not revised**. Separately, a *common* operating
point is fixed here, on **validation data only**, so that RF, SVM and the
1-D CNN are compared at the same alarm budget in Stage G/H.

**Validation ROC frontier is a step function.** 49,325 validation rows
(27%) share a single RF score (p = 0.4605) and are 58.91% malicious —
the dominant ambiguous vector group of §12. That whole mass flips at
once, so no threshold lands between FPR 0.075% and 30%:

| FPR constraint | Threshold | Max validation recall | Achieved FPR |
|---|---|---|---|
| <= 0.1% | 0.4787 | 0.534044 | 0.000754 |
| <= 1% | 0.4787 | 0.534044 | 0.000754 |
| <= 5% | 0.4787 | 0.534044 | 0.000754 |
| <= 10% | 0.4787 | 0.534044 | 0.000754 |
| (<= 0.05%) | 0.6116 | 0.531425 | 0.000000 |
| (<= 30%) | 0.3981 | 0.805108 | 0.299976 |

All four candidate constraints select the **identical** RF operating
point, so the choice among them cannot flatter RF. Detail:
[`results/random_forest/validation_fpr_operating_points.csv`](results/random_forest/validation_fpr_operating_points.csv).

**Primary criterion: FPR <= 1% on validation.** Rationale: it is a
conventional operational alarm budget for intrusion detection, it is
comfortably achievable by RF (0.075%, with headroom), and it is loose
enough that models with smoother score distributions than RF's — which
SVM and the CNN are likely to have — are not forced into a degenerate
point, as <= 0.1% might. <= 5% and <= 10% were rejected as too permissive:
on the 71,670 benign test flows they would license roughly 3,600 and
7,200 false alarms respectively.

**Selection rule within the constraint:** choose the threshold maximising
**validation recall subject to validation FPR <= 1%**; break ties toward
the **highest** threshold (most conservative, furthest from the decision
boundary). The threshold is fitted on validation only and frozen before
any test evaluation. If a model cannot satisfy the constraint at any
threshold, that must be reported as a failure to meet the operating
point — the constraint is not relaxed per model.

**Secondary reporting (required for every model):**

- Threshold-independent **ROC-AUC** and **PR-AUC** (note the positive
  class is the majority at 60.7%, so the PR-AUC no-skill baseline is
  0.607, not 0.5).
- The full **ROC curve (FPR vs TPR)** and **precision-recall curve**, all
  three models on shared axes.
- **Recall at a range of fixed alarm budgets** (0.1% / 1% / 5% / 10%
  FPR) rather than a single point — this is robust to the score-mass
  dead zone above, which can make one cap arbitrarily equivalent to
  another for some models but not others.
- The **full confusion matrix** and the **achieved** FPR at the fixed
  operating point (discrete scores mean the achieved FPR can sit far
  below the cap).
- **Per-attack-type recall** at the fixed operating point.
- **Per-flow inference time**, for the SDN deployment framing.

Accuracy alone must not be used to rank the three models: §12 shows it is
capped at 78.63% by the representation, and Stage F showed near-ceiling
accuracy coexisting with a 54.4% FPR.

### 16A.5 Secondary RF evaluation at the FPR-constrained operating point

The Stage F result above (threshold 0.30) is the **original,
default-threshold characterisation and remains unchanged**. Because it
was produced under the earlier F1-oriented rule, it was not comparable
with Stage G's SVM. This authorised **second** evaluation applies the
locked protocol (§16A.4) to the **same already-trained forest** — the
Stage F `random_forest.joblib` was loaded and reused; **nothing was
retrained**, and every Stage F artifact was verified unmodified.

The two RF results are labelled distinctly and both are retained:

| Label | Threshold | Artifact |
|---|---|---|
| RF @ default threshold (original Stage F) | 0.30 | `test_metrics.json` |
| RF @ FPR-constrained operating point (secondary) | 0.478734 | `test_metrics_fpr_constrained.json` |

Validation budget table — every budget collapses onto one point, the
quantisation effect described in §16A.4:

| Budget | Threshold | Val recall | Achieved val FPR |
|---|---|---|---|
| <= 0.1% / 1% / 5% / 10% | 0.478734 | 0.534044 | 0.000754 |

**Frozen threshold: 0.478734** (validation only, ties to highest).

**RF test results at that frozen threshold (single pass):**

| Metric | Value |
|---|---|
| Accuracy | 0.655771 |
| Precision | 0.988566 |
| Recall | 0.438040 |
| F1 | 0.607079 |
| **FPR** | **0.007828** |
| Specificity | 0.992172 |
| ROC-AUC | 0.852824 |
| PR-AUC | 0.867387 |

| | Predicted Benign | Predicted Malicious |
|---|---|---|
| **Actual Benign** | TN = 71,109 | FP = 561 |
| **Actual Malicious** | FN = 62,227 | TP = 48,505 |

### 16A.6 RF vs SVM at the common operating point

Both models at validation FPR <= 1% (the CNN is not yet implemented, so
this is **not** the full Stage H comparison):

| Metric | RF | SVM | Better |
|---|---|---|---|
| Accuracy | **0.655771** | 0.653874 | RF (+0.19 pp) |
| Precision | **0.988566** | 0.982406 | RF |
| Recall | **0.438040** | 0.437687 | RF (+0.04 pp) |
| F1 | **0.607079** | 0.605575 | RF |
| **FPR (test)** | **0.007828** | 0.012111 | **RF** |
| ROC-AUC | **0.852824** | 0.850177 | RF |
| PR-AUC | 0.867387 | **0.879445** | SVM |
| Inference | **0.0011 ms/flow** | 0.0068 ms/flow | RF (6x) |
| Training | **31 s** | 3,094 s | RF (100x) |

Per-attack recall at the same operating point:

| Attack Type | RF | SVM |
|---|---|---|
| ICMPFlood / SYNFlood / SYNScan / TCPConnectScan / UDPScan | 1.000000 | 0.994-1.000 |
| SlowrateDoS | 1.000000 | 0.999271 |
| HTTPFlood | 0.999953 | 0.986555 |
| **UDPFlood** | **0.092942** | **0.097023** |

Reading: the two model families are **near-indistinguishable** on this
representation — recall differs by 0.04 pp. RF holds a small edge on
almost every metric plus a 6x inference and 100x training advantage; the
SVM's only win is PR-AUC (a threshold-free ranking measure), and it
overshot the 1% budget on test (1.21%) whereas RF stayed under (0.78%).
RF is also cleaner on the non-UDP attacks (all 100%), while the SVM
detects marginally more UDP flood.

Both independently reproduce the Stage D structural result: at a 1% alarm
budget, **every attack type is detected at ~99-100% except UDP flood, at
~9-10%**. That agreement across two unrelated model families is evidence
that the limit is a property of the per-flow feature representation, not
of any one classifier.

## 16B. Stage G — Support Vector Machine results

> Evaluation scope: **within-capture (within-session) generalisation** (§8.3).
> Not unseen-capture, unseen-session, unseen-base-station or unseen-attack.

### Strategy: Nystroem RBF approximation + LinearSVC

A full `SVC(kernel="rbf")` on the 851,106-row training split is not
usable here. Measured on this hardware:

| Approach | Train rows used | Fit | Val inference | ms/flow | val PR-AUC | val ROC-AUC |
|---|---|---|---|---|---|---|
| True RBF `SVC`, Stage D 50k subsample | 50,000 (5.9%) | 56 s | 246.5 s | 1.3515 | 0.86877 | 0.79169 |
| **Nystroem(RBF) + LinearSVC** | **851,106 (100%)** | see below | 1.3 s | **0.0068** | **0.90871** | 0.86820 |
| Plain LinearSVC (linear only) | 851,106 (100%) | 27 s | 0.03 s | 0.0002 | 0.87335 | — |

`SVC` fit time is quadratic (0.4 s / 1.7 s / 7.3 s at n = 5k / 10k / 20k),
extrapolating to ~3.7 h on the full split, and ~55% of rows become
support vectors so *inference* cost also grows with training size. The
kernel-approximation route trains on **all** training rows, scores ~200x
faster per flow, and scores higher on validation. It stays genuinely
SVM-based: an explicit finite-dimensional RBF feature map followed by a
hinge-loss maximum-margin classifier — an approximation of an RBF SVM,
not a different model family.

`gamma` uses sklearn's `scale` heuristic **computed on training data
only** (0.032651) and is then frozen. The feature map is fitted on
training rows only. `ChunkedNystroem` transforms in float32 row blocks
because `Nystroem.transform` returns float64 and materialising
851,106 x 1024 needs ~7 GB, which drove this 16 GB machine into swap
during probing — `n_components=1024` was therefore excluded before the
run, on measured evidence.

### Hyperparameter search (validation only, PR-AUC)

`class_weight` was **not** searched: Stage D fixed class weighting as the
imbalance strategy and it is held constant across RF/SVM/CNN so the model
comparison is not confounded.

| n_components | C | val PR-AUC | val ROC-AUC | fit (s) |
|---|---|---|---|---|
| 256 | 0.01 | 0.903976 | 0.857222 | 46 |
| 256 | 0.1 | 0.905573 | 0.860996 | 81 |
| 256 | 1.0 | 0.907280 | 0.865675 | 444 |
| 256 | 10.0 | 0.907879 | 0.867275 | 1,096 |
| 512 | 0.01 | 0.905067 | 0.859298 | 173 |
| 512 | 0.1 | 0.906876 | 0.863324 | 408 |
| **512** | **1.0** | **0.908711** | 0.868196 | **1,363** |
| 512 | 10.0 | 0.909544 | 0.870052 | **10,747** |

Best PR-AUC was `512 / C=10` (0.909544), but `512 / C=1.0` (0.908711)
lies within the 0.001 tie tolerance, so the documented tie-break selected
the **cheaper** model: it fits in 1,363 s instead of 10,747 s for a
statistically indistinguishable score. The `C=10 / 512` candidate **did
converge** — the run emitted no convergence warnings — but was
substantially slower than every alternative (~3 hours, roughly 8x the
selected configuration), which is the expected consequence of the weaker
regularisation at large `C` lengthening the optimisation. It is therefore
impractical to re-run on this hardware, though not invalid.

**Tie-window sensitivity (methodological note).** The two leading
candidates are separated by only **0.000833 PR-AUC**:

| Candidate | val PR-AUC | fit (s) |
|---|---|---|
| best raw: `n_components=512, C=10` | 0.909544 | 10,747 |
| **selected: `n_components=512, C=1`** | **0.908711** | **1,363** |

With a tie tolerance of **0.001**, the selected configuration fell inside
the window and won on the documented cheaper-model tie-break. Because the
gap is far smaller than the tolerance, **validation performance does not
meaningfully distinguish these configurations** — the choice is decided by
cost, not by evidence of better generalisation. Note also that the window
is anchored on the best raw score: had it been anchored slightly lower,
`256 / C=10` (0.907879) would also have entered and, under the same
tie-break, would have been selected instead. The rule was applied as
specified; this is a sensitivity to record, not a defect.

**Selected: `n_components=512, C=1.0, class_weight=balanced, seed=42`**
(converged in 91 iterations). Training on all 851,106 rows: **3,094 s**
in the final refit (the same configuration took 1,363 s during the grid;
the difference is memory pressure on this machine, not a change in the
computation). Inference: 1.24 s for 182,402 test flows =
**0.0068 ms per flow**.

### Operating point (locked protocol, §16A.4)

Validation recall at each alarm budget — note the SVM has a genuinely
smooth score distribution, so unlike RF the budgets select *distinct*
thresholds:

| Budget | Threshold | Val recall | Achieved val FPR |
|---|---|---|---|
| <= 0.1% | 0.041083 | 0.527777 | 0.000977 |
| **<= 1% (primary)** | **-0.062874** | **0.535083** | 0.009992 |
| <= 5% | -0.088434 | 0.541459 | 0.019076 |
| <= 10% | -0.088434 | 0.541459 | 0.019076 |

Even so, a 100x wider alarm budget buys only +1.4 pp of recall, and the
5%/10% budgets both saturate at 1.9% achieved FPR — the same irreducible
ambiguity wall described in §12. **Frozen threshold: -0.062874**,
selected on validation only and applied to test exactly once. Scores are
`decision_function` margins; no probability calibration was applied.

### Test results (single evaluation at the frozen threshold)

| Metric | Value |
|---|---|
| Accuracy | 0.653874 |
| Precision | 0.982406 |
| Recall (TPR) | 0.437687 |
| F1 | 0.605575 |
| **False Positive Rate** | **0.012111** |
| Specificity (TNR) | 0.987889 |
| ROC-AUC | 0.850177 |
| PR-AUC | 0.879445 |
| Inference | 0.0068 ms/flow |

| | Predicted Benign | Predicted Malicious |
|---|---|---|
| **Actual Benign** | TN = 70,802 | FP = 868 |
| **Actual Malicious** | FN = 62,266 | TP = 48,466 |

Test FPR (1.21%) slightly exceeds the 1% validation cap, and test recall
(0.438) falls below validation recall (0.535) — an ordinary
validation-to-test generalisation gap, reported rather than corrected.

Against the reference points: it **beats** the always-Malicious baseline
(0.607077) but **does not beat** the exact-vector memorisation baseline
(0.735129) on accuracy, and sits 13.24 pp below the empirical ceiling.
That is expected and not a defect — at a 1% alarm budget the model must
classify the ambiguous mass as benign, which costs accuracy by
construction. Accuracy is not the ranking metric (§16A.4).

### Per-attack-type results — the substantive finding

| Attack Type | Support | Recall |
|---|---|---|
| ICMPFlood | 174 | 1.000000 |
| SYNFlood | 1,459 | 1.000000 |
| SlowrateDoS | 10,971 | 0.999271 |
| SYNScan | 3,007 | 0.997672 |
| TCPConnectScan | 3,009 | 0.997341 |
| UDPScan | 2,387 | 0.994554 |
| HTTPFlood | 21,123 | 0.986555 |
| **UDPFlood** | **68,602** | **0.097023** |
| Benign | 71,670 | FPR 0.012111 (868 FP) |

At a 1% alarm budget the SVM detects **every attack type at 98.7-100%
except UDP flood, where it detects 9.7%** (61,946 of 68,602 missed). By
tool: Nmap 0.9967, Slowloris 0.9985, Torshammer 0.9994, Goldeneye 0.9866,
**Hping3 0.1180** (Hping3 is dominated by the UDP flood captures).

This is exactly the behaviour Stage D predicted. The dominant ambiguous
vector is benign-vs-UDPFlood, so a model constrained to a low false-alarm
rate must assign that mass to Benign and forfeit most UDP-flood
detection. The trade-off is a property of per-flow features at this
granularity, not a deficiency of the SVM, and it is the concrete
motivation for the window/aggregate approaches in M2 and M3.

### Limitations

1. **Not yet comparable to the Stage F RF result.** RF's official test
   result was produced under the earlier F1-oriented threshold rule
   (threshold 0.30, FPR 54.4%); this SVM result uses the locked FPR <= 1%
   protocol. The two are at different operating points and must not be
   compared directly. Evaluating both at the common operating point is
   Stage H work and has not been performed.
2. `C=10 / n_components=512` converged but is not practically
   re-runnable here (~3 h, ~8x the selected configuration's fit time).
3. `n_components=512` sits at this machine's memory ceiling (~6.5 GB);
   `1024` is infeasible.
4. Test FPR (1.21%) modestly exceeds the 1% cap fitted on validation.

## 16C. Stage H — 1-D CNN results

> Evaluation scope: **within-capture (within-session) generalisation** (§8.3).
> Not unseen-capture, unseen-session, unseen-base-station or unseen-attack.

### Environment

TensorFlow **2.21.0**, Keras **3.15.1**, Python 3.13.7, **CPU only**
(native Windows has no TF GPU support since 2.11). Installing TF was
purely additive — `numpy 2.5.2` already satisfied its `numpy>=1.26.0`
requirement, so no existing project dependency was downgraded. It did
upgrade `protobuf` to 7.36.1, which is incompatible with `grpcio-status`
and `proto-plus` present in the wider environment; neither is used
anywhere in M1. No `requirements.txt` was created — dependencies remain
documented in this README, per the Stage B decision.

### Input representation (and its limitation)

The Stage D canonical matrix is reshaped `(n, 67) -> (n, 67, 1)` by a
pure `np.reshape`, so **feature order is preserved exactly** and no
feature is reordered; the run asserts `Z[:, :, 0] == X` before training.

**This is a tabular vector, not a temporal signal.** Consequently:

* `Conv1D` here is **not** temporal convolution and does not model packet
  or flow sequences over time.
* Convolution presumes neighbouring positions are related; for a tabular
  vector that adjacency is an artifact of column order, so feature
  ordering can influence which features a kernel can combine.
* This evaluates a convolutional architecture over a fixed feature
  vector. It establishes **nothing** about CNNs for genuine temporal
  network-sequence modelling.

A further property, pinned by test: because both convolutions use `same`
padding and are followed by `GlobalAveragePooling1D`, the network is
**length-agnostic at inference** — it silently accepts a wrong-width
matrix instead of raising, unlike RF and SVM. Shape discipline therefore
has to come from the caller.

### Architecture and training

```text
Input(67, 1)
Conv1D(32, k=3, ReLU, padding=same)
Conv1D(64, k=3, ReLU, padding=same)
GlobalAveragePooling1D
Dense(64, ReLU) -> Dropout(0.2) -> Dense(1, sigmoid)
```

**10,561 parameters.** Binary cross-entropy, Adam (lr 1e-3), batch size
512, max 30 epochs, `EarlyStopping(monitor=val_pr_auc, mode=max,
patience=5, restore_best_weights=True)`, seed 42 via
`keras.utils.set_random_seed`. Class weighting uses sklearn's `balanced`
formula — `{0: 1.272556, 1: 0.823601}` — identical in construction to the
RF and SVM strategy. Early stopping used **validation only**; the chosen
model ran 19 epochs with best epoch 14.

### Hyperparameter search (validation PR-AUC, 16 candidates)

Full factorial: `filters {(32,64),(64,128)}` x `kernel {3,5}` x
`dropout {0.2,0.3}` x `lr {1e-3,3e-4}`.

| filters | k | dropout | lr | params | val PR-AUC | fit (s) |
|---|---|---|---|---|---|---|
| 64x128 | 5 | 0.2 | 1e-3 | 49,793 | 0.901287 | 656 |
| 64x128 | 5 | 0.3 | 1e-3 | 49,793 | 0.901265 | 730 |
| 32x64 | 5 | 0.2 | 1e-3 | 14,721 | 0.901253 | 254 |
| 32x64 | 5 | 0.3 | 1e-3 | 14,721 | 0.901183 | 178 |
| **32x64** | **3** | **0.2** | **1e-3** | **10,561** | **0.900768** | **151** |
| 32x64 | 3 | 0.3 | 3e-4 | 10,561 | 0.900417 | 215 |

**All 16 candidates fall inside the 0.001 tie tolerance** — the full
spread is 0.90042-0.90129, i.e. **0.00087**. Architecture and
hyperparameters are therefore *not distinguished by validation
performance* on this representation, exactly as observed for RF (18
candidates, spread 0.000167) and SVM. The documented tie-break
(fewest parameters, then smaller kernel, then faster) selected the
**cheapest model in the grid**: `32x64, k=3, dropout 0.2, lr 1e-3` —
10,561 parameters, 151 s, versus 49,793 parameters and 656 s for the
nominal best, for 0.0005 PR-AUC.

Search wall-time totalled 25,500 s, but that figure is inflated by
environmental stalls, not computation: `64x128/k=5/lr=3e-4` logged
16,748 s and another 3,577 s, while the *same architecture* at lr=1e-3
took 656 s. Learning rate does not change per-epoch cost, so those two
timings reflect machine slowdown (the same effect seen in Stage F), and
should not be read as architecture cost.

### Operating point (locked protocol, §16A.4)

| Budget | Threshold | Val recall | Achieved val FPR |
|---|---|---|---|
| <= 0.1% / 1% / 5% / 10% | 0.471731 | 0.531380 | 0.000181 |

Like RF (and unlike the SVM), every budget collapses onto a single point.
**Frozen threshold: 0.471731**, selected on validation only, applied to
test exactly once. Validation at that point: accuracy 0.715432,
precision 0.999779, recall 0.531380, FPR 0.000181, PR-AUC 0.900768.

### Test results (single evaluation at the frozen threshold)

| Metric | Value |
|---|---|
| Accuracy | 0.650985 |
| Precision | 0.997443 |
| Recall | 0.426182 |
| F1 | 0.597197 |
| **False Positive Rate** | **0.001688** |
| Specificity | 0.998312 |
| ROC-AUC | 0.850978 |
| PR-AUC | 0.864283 |
| Inference | 0.0038 ms/flow |

| | Predicted Benign | Predicted Malicious |
|---|---|---|
| **Actual Benign** | TN = 71,549 | FP = 121 |
| **Actual Malicious** | FN = 63,540 | TP = 47,192 |

Training 160 s; test inference 0.70 s. It beats the always-Malicious
baseline (0.607077) but **not** the memorisation baseline (0.735129), and
sits 13.53 pp below the empirical ceiling — expected at a 1% alarm
budget, where the ambiguous mass must be assigned to Benign.

### Per-attack-type results

| Attack Type | Support | Recall |
|---|---|---|
| ICMPFlood / SYNFlood / SYNScan / TCPConnectScan | 174 / 1,459 / 3,007 / 3,009 | 1.000000 |
| SlowrateDoS | 10,971 | 0.999544 |
| HTTPFlood | 21,123 | 0.999527 |
| UDPScan | 2,387 | 0.996230 |
| **UDPFlood** | **68,602** | **0.074138** |
| Benign | 71,670 | FPR 0.001688 (121 FP) |

## 16D. Three-model comparison at validation FPR <= 1%

All three at the same locked operating point. The original RF
threshold-0.30 result (§16A) is preserved separately as the
default-threshold characterisation and is **not** part of this table.

| Metric | RF | SVM | CNN |
|---|---|---|---|
| Threshold | 0.478734 | -0.062874 | 0.471731 |
| Accuracy | **0.655771** | 0.653874 | 0.650985 |
| Precision | 0.988566 | 0.982406 | **0.997443** |
| Recall | **0.438040** | 0.437687 | 0.426182 |
| F1 | **0.607079** | 0.605575 | 0.597197 |
| **Test FPR** | 0.007828 | 0.012111 | **0.001688** |
| ROC-AUC | **0.852824** | 0.850177 | 0.850978 |
| PR-AUC | 0.867387 | **0.879445** | 0.864283 |
| Inference (ms/flow) | **0.0017** | 0.0068 | 0.0038 |
| Training | **31 s** | 3,094 s | 160 s |
| UDPFlood recall | 0.092942 | **0.097023** | 0.074138 |

**Threshold-independent metrics** (ROC-AUC 0.850-0.853, PR-AUC
0.864-0.879) are within ~0.015 of each other across all three families.
Note the positive class is the **majority** at 60.7%, so the no-skill
PR-AUC reference is **~0.607, not 0.5**; PR-AUC and ROC-AUC are computed
on different axes and must not be compared to one another. Full ROC and
PR curve data for the CNN is saved in `results/cnn/test_roc_curve.csv`
and `test_pr_curve.csv` (matplotlib is not installed in this
environment, so curve *data* is persisted rather than rendered plots).

**How to read the inference times.** The `ms/flow` figures are
**amortised batch throughput** — total wall-clock time to score the
complete 182,402-row test split, divided by the number of rows. They are
**not** single-flow latency measurements, and so do not represent the
cost of classifying one flow in isolation, which is the quantity an SDN
deployment would care about. Each is also a **single timed run** on a
machine subject to substantial run-to-run load variation (the same
variation that inflated some Stage F/H fit times); repeated timing of the
identical RF scoring call, for instance, produced 0.0011 and 0.0017
ms/flow. The timings should therefore be interpreted **approximately**,
as an indication of relative cost rather than precise measurements.

**Reading.** The three classifiers exhibit broadly similar
discrimination under the current feature representation and
operating-point protocol: recall spans 0.426-0.438 (1.2 pp) and accuracy
0.651-0.656 (0.5 pp). They differ mainly in where they sit on the
precision/FPR trade-off — the CNN is the most conservative (FPR 0.17%,
precision 99.74%, lowest recall), RF is the best-balanced and by far the
cheapest to train and run, and the SVM has the best threshold-free
ranking (PR-AUC) but the highest FPR and slowest inference.

Most importantly, **all three independently reproduce the Stage D
structural result**: at a 1% alarm budget every attack type is detected
at ~99-100% except UDP flood, at **7-10%**. Three unrelated model
families converging on the same failure mode is strong evidence that the
limit belongs to the per-flow feature representation, not to any
classifier. Note the scope of that evidence: because all three
classifiers consume the **same** 67-feature representation, their
agreement provides corroboration across model families rather than three
independent tests of the representation itself. The independent argument
for the limit is the Stage D exact-vector analysis (§12), which
established the ambiguity combinatorially, before any model was
trained. Accuracy must not be used to rank these models (§12: it is
capped at 78.63%, and Stage F showed near-ceiling accuracy coexisting
with a 54.4% FPR).

### CNN-specific limitations

1. The representation is tabular, not sequential — see above. No temporal
   claim is supported.
2. Feature ordering is the Stage D order; a different ordering could
   change what the convolution kernels can combine.
3. The network is length-agnostic at inference and will not reject a
   wrong-width input.
4. Architecture choice is not distinguished by validation performance
   (all 16 candidates within tolerance), so the selected architecture
   reflects the cost tie-break, not measured superiority.
5. The previously established representation limits all still apply:
   ~78.63% empirical accuracy ceiling, extensive exact-feature
   repetition, conflicting feature vectors, UDP-flood ambiguity, and
   high FPR at unrestricted recall. **A CNN cannot recover information
   that is absent from the feature representation.**

## 16E. Stage I — consolidated evaluation

Stage I is an **audit and consolidation** stage: it re-reads the frozen
Stage F/G/H artifacts, re-derives every metric from the saved confusion
matrices, and assembles directly comparable tables. No model was
retrained, no score recomputed, and no threshold re-selected. All ten
protected source artifacts were verified byte-identical before and after
(the run aborts if any changes).

Regenerate with:

```bash
python M1-supervised-ml/experiments/consolidate_evaluation.py
```

Outputs (additive, under `results/evaluation/`):
`three_model_fpr1pct_summary.csv`, `three_model_fpr_budget.csv`,
`three_model_per_attack_type.csv`, `three_model_confusion_matrices.csv`,
`metric_consistency_audit.csv`, `evaluation_metadata.json`. The Stage H
`results/model_comparison_fpr1pct.csv` is a subset of the summary table
and is left unmodified.

### Metric consistency audit

Every rate metric was re-derived from the stored TP/TN/FP/FN using
`accuracy=(TP+TN)/N`, `precision=TP/(TP+FP)`, `recall=TP/(TP+FN)`,
`F1=2PR/(P+R)`, `FPR=FP/(FP+TN)`, `specificity=TN/(TN+FP)`.

**21 checks across the three models: all consistent, maximum absolute
deviation exactly 0.000e+00** (tolerance 1e-9). No artifact required
correction and none was modified.

### Common protocol and frozen thresholds

All three models share the Stage D 67-feature representation, the Stage E
`block_label_contiguous` split (train 851,106 / validation 182,382 / test
182,402, test malicious prevalence 60.7077%), the binary target, and the
locked rule: *maximise validation recall subject to validation FPR <= 1%,
ties to the highest threshold, frozen before test*.

| Model | Frozen threshold | Val recall | Val FPR |
|---|---|---|---|
| Random Forest | 0.478734 | 0.534044 | 0.000754 |
| SVM | -0.062874 | 0.535083 | 0.009992 |
| 1-D CNN | 0.471731 | 0.531380 | 0.000181 |

### Confusion matrices at the frozen operating point

| Model | TN | FP | FN | TP |
|---|---|---|---|---|
| Random Forest | 71,109 | 561 | 62,227 | 48,505 |
| SVM | 70,802 | 868 | 62,266 | 48,466 |
| 1-D CNN | 71,549 | 121 | 63,540 | 47,192 |

All three reconcile to the same test split: N = 182,402, actual benign
71,670, actual malicious 110,732 — confirming they were evaluated on an
identical, unmodified test set.

### Canonical comparison

Full table in `three_model_fpr1pct_summary.csv`; the headline numbers are
already given in §16D and are not duplicated here. Cost measures, which
§16D reports only partially:

| Model | Training | Model size | Batch throughput |
|---|---|---|---|
| Random Forest | 31.1 s | 172,630 tree nodes | 0.0017 ms/flow |
| SVM | 3,093.6 s | 513 linear weights (+bias) | 0.0068 ms/flow |
| 1-D CNN | 159.6 s | 10,561 trainable parameters | 0.0038 ms/flow |

Model size is measured in each family's own natural unit and is **not**
comparable across rows. The throughput caveat of §16D applies unchanged:
these are **amortised batch-throughput** figures over the whole test
split, **not single-flow latency**, from single timed runs on a
load-variable machine, and should be read approximately.

### FPR-budget behaviour (validation)

| Budget | RF recall | SVM recall | CNN recall |
|---|---|---|---|
| <= 0.1% | 0.534044 | 0.527777 | 0.531380 |
| <= 1% | 0.534044 | 0.535083 | 0.531380 |
| <= 5% | 0.534044 | 0.541459 | 0.531380 |
| <= 10% | 0.534044 | 0.541459 | 0.531380 |

RF and the CNN have **discrete score distributions**, so all four budgets
collapse onto a single threshold (0.478734 and 0.471731 respectively) at
an achieved FPR far below the cap (0.075% and 0.018%) — widening the
alarm budget buys them nothing. Only the SVM's smoother scores select
distinct thresholds, and even there a 100x wider budget adds just 1.4 pp
of recall before saturating at 1.9% achieved FPR. The
`budgets_collapsed` column in `three_model_fpr_budget.csv` records this
per model.

### Threshold-independent metrics

| Model | ROC-AUC | PR-AUC |
|---|---|---|
| Random Forest | 0.852824 | 0.867387 |
| SVM | 0.850177 | **0.879445** |
| 1-D CNN | 0.850978 | 0.864283 |

Both use **Malicious = 1 as the positive class**, scored in the correct
direction (each model's higher score means more malicious: RF/CNN
probabilities, SVM decision-function margins). Because the positive class
is the **majority** at 60.7077%, the **no-skill PR-AUC reference is
~0.607, not 0.5**; PR-AUC and ROC-AUC are computed on different axes and
must not be compared with one another.

### Per-attack-type comparison

| Attack Type | Support | RF | SVM | CNN |
|---|---|---|---|---|
| ICMPFlood | 174 | 1.000000 | 1.000000 | 1.000000 |
| SYNFlood | 1,459 | 1.000000 | 1.000000 | 1.000000 |
| SYNScan | 3,007 | 1.000000 | 0.997672 | 1.000000 |
| TCPConnectScan | 3,009 | 1.000000 | 0.997341 | 1.000000 |
| SlowrateDoS | 10,971 | 1.000000 | 0.999271 | 0.999544 |
| UDPScan | 2,387 | 1.000000 | 0.994554 | 0.996230 |
| HTTPFlood | 21,123 | 0.999953 | 0.986555 | 0.999527 |
| **UDPFlood** | **68,602** | **0.092942** | **0.097023** | **0.074138** |
| Benign (FPR) | 71,670 | 0.007828 | 0.012111 | 0.001688 |

Seven of the eight attack types are detected at 98.7-100% by all three
models. UDP flood is detected at **7.4-9.7%** by all three.

**Interpretation, stated with its proper scope:** because all three
classifiers consume the same 67-feature representation, their agreement
provides corroboration across model families rather than three
independent tests of the representation itself. The independent Stage D
exact-vector ambiguity analysis (§12) remains the stronger
representation-level evidence.

### Scope and limitations

This consolidation inherits every limitation of the underlying stages and
introduces no new evidence. In particular the Stage E protocol is
**within-capture (within-session)**: all 20 capture blocks contribute to
train, validation and test. It does **not** measure unseen-capture,
unseen-session, unseen-base-station or unseen-attack generalisation, and
results must not be described as such. The §12 representation limits
(78.63% empirical accuracy ceiling, extensive exact-feature repetition,
conflicting feature vectors, UDP-flood ambiguity) continue to apply.

## 16F. Stage J — figures

Nine report-ready figures under `results/plots/`, generated from saved
evaluation artifacts only. Regenerate with:

```bash
python M1-supervised-ml/experiments/generate_plots.py
```

Plotting loads **no model**, generates **no prediction** and selects
**no threshold**; the data path is `saved artifacts -> plotting ->
figures`. Provenance for every figure (source artifact, split, operating
point, generating script) is recorded in `results/plots/plot_manifest.json`.
All 9 PNGs were verified **byte-identical across two consecutive runs**.
Rendered with matplotlib **3.11.1**.

### Authorised curve export (prerequisite)

Stages F and G persisted only scalar AUCs, so RF and SVM had no
test-curve points and the combined ROC/PR figures could not be drawn.
An explicitly authorised one-off export
(`experiments/export_curves.py`) loaded the **existing saved models** and
re-scored the test split **solely to persist curve data**:

| Model | Score type | ROC pts | PR pts |
|---|---|---|---|
| Random Forest | `predict_proba` positive-class probability | 2,154 | 2,269 |
| SVM | `decision_function` margin (higher = Malicious) | 2,116 | 2,057 |
| 1-D CNN | reused from Stage H — not regenerated | 2,106 | 2,049 |

No model was retrained or modified, no threshold selected, and no
existing artifact overwritten. As an integrity check the export
recomputed ROC-AUC/PR-AUC from the fresh scores and required them to
match the Stage F/G recorded values — both matched **exactly**
(deviation 0.00e+00), confirming these are the same frozen predictions.
Provenance is in `results/evaluation/curve_export_metadata.json`.

### Figures

| File | Split | Shows |
|---|---|---|
| `roc_curves_test.png` | test | Combined ROC, AUC per legend entry, no-skill diagonal |
| `precision_recall_curves_test.png` | test | Combined PR, PR-AUC per legend, no-skill = 0.607 |
| `fpr_recall_validation.png` | **validation** | Recall vs achieved FPR at the 0.1/1/5/10% budgets |
| `model_metrics_fpr1pct_test.png` | test | Recall / Precision / F1, with FPR on its own panel |
| `per_attack_recall_test.png` | test | Recall by attack type, all three models |
| `confusion_matrix_{rf,svm,cnn}.png` | test | Absolute counts (+ row %) per model |
| `computational_cost.png` | — | Training time and batch throughput |

**Validation vs test.** Only `fpr_recall_validation.png` shows validation
data — it is where the operating point was *chosen*. Every other figure
shows **test** results at thresholds frozen beforehand
(RF 0.478734, SVM -0.062874, CNN 0.471731). No figure depicts a threshold
selected on test data.

### Reading the figures

**ROC.** All three curves lie almost exactly on top of one another
(AUC 0.850-0.853) — the visual form of the §16D finding that the
classifiers discriminate similarly under this representation. The sharp
elbow near FPR ~0.55 is the ambiguous-vector mass of §12 flipping as a
block, not a modelling artifact.

**Precision-Recall.** The no-skill line is drawn at the **test malicious
prevalence 0.607**, not 0.5, because the positive class is the majority.
PR-AUC and ROC-AUC are on different axes and are not comparable with each
other.

**FPR budget.** RF and the CNN appear as **single stars**: their discrete
score distributions collapse all four budgets onto one threshold, at
achieved FPR far below the cap (0.075% and 0.018%), so a wider alarm
budget buys them nothing. Only the SVM traces a line, and even it gains
just ~1.4 pp of recall across a 100x range before saturating.

**Per-attack recall.** Seven of eight attack types sit at 0.99-1.00 for
all three models; UDP flood alone drops to 0.07-0.10. The y-axis is the
full 0-1 range — the gap is not exaggerated by scaling. As established in
§16D/§16E: because all three classifiers consume the same 67-feature
representation, their agreement provides corroboration across model
families rather than three independent tests of the representation
itself; the Stage D exact-vector analysis (§12) remains the stronger
representation-level evidence. `Attack Type` is analysis metadata only
and was never a model input.

**Confusion matrices.** Absolute counts are mandatory and shown; the row
percentage is added for context. Cell shading is row-normalised so the
benign and malicious rows are individually readable despite their
different totals. No normalised-only variant was produced.

**Computational cost.** Training time uses a log scale (31 s to 3,094 s).
Throughput is labelled `~x.xxx ms` at three decimals deliberately:
these are **amortised batch-throughput** figures over the whole test
split, **not single-flow latency**, from single timed runs on a
load-variable machine, so extra precision would be false. They indicate
relative cost only.

### Limitations

These figures visualise the existing frozen evaluation and add no new
evidence. They inherit every limitation of Stages D-I: the protocol is
**within-capture (within-session)**, so **no figure establishes
unseen-capture, unseen-session, unseen-base-station or unseen-attack
generalisation**. The §12 representation limits (78.63% empirical
accuracy ceiling, exact-feature repetition, conflicting feature vectors,
UDP-flood ambiguity) continue to apply.

## 17. Next stage

Stages F, G, H, I and J are **complete**. Random Forest (§16A), SVM (§16B) and
the 1-D CNN (§16C) have each been trained on the prepared matrices and
evaluated at the locked validation FPR <= 1% operating point, reporting
Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, FPR, TP/TN/FP/FN,
training time and per-flow inference time; the three-model comparison is
in §16D.

Identified but **not yet performed**:

- the secondary unseen-capture experiment defined in §8.4 (hold out
  blocks 10, 11, 12, 13, 15, 17) — the only design available here that
  would measure unseen-session generalisation, which the primary
  protocol explicitly does not;
- the `Cause` ablation flagged in §16A.3;
- comparison against M2 (entropy) and M3 (sampled telemetry), which
  operate at the window/aggregate granularity where UDP flood may be
  separable (§16D).
