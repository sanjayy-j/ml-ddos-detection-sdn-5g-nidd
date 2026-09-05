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
tensorflow   # required only for the Stage E 1-D CNN; not yet installed
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

## 17. Next stage

Stage E — train and evaluate Random Forest, SVM and the 1-D CNN on the
prepared matrices, reporting Accuracy, Precision, Recall, F1, ROC-AUC,
FPR, TP/TN/FP/FN, plus training time, total inference time and per-flow
inference time.
