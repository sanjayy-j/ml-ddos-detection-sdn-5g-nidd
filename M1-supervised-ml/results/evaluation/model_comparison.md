# M1 Supervised Models — Final Comparison and Interpretation

_Generated 2026-09-07T14:12:23+00:00 by `experiments/generate_comparison.py` from the canonical Stage D/I artifacts. No model was trained, loaded or run to produce this document._

## 1. Scope of this comparison

Three supervised models — Random Forest, SVM (Nystroem RBF approximation + LinearSVC) and a 1-D CNN — are compared **under the current feature representation** (67 encoded features from Stage D) and **under the common operating-point protocol**: the decision threshold was chosen to maximise validation recall subject to validation FPR <= 1%, ties broken toward the highest threshold, and frozen before any test evaluation.

Split sizes: train 851,106, validation 182,382, test 182,402. All three models share the same representation, split, target definition and leakage exclusions, so differences below are attributable to the model families rather than to differing inputs.

Canonical numbers live in [`three_model_fpr1pct_summary.csv`](three_model_fpr1pct_summary.csv), [`three_model_fpr_budget.csv`](three_model_fpr_budget.csv), [`three_model_per_attack_type.csv`](three_model_per_attack_type.csv) and [`three_model_confusion_matrices.csv`](three_model_confusion_matrices.csv); figures are in `results/plots/`. That summary CSV already carries every field required for a machine-readable comparison, so it is referenced here rather than duplicated.

## 2. Definitive comparison (frozen FPR <= 1% operating point, test set)

| Metric | Random Forest | SVM | 1-D CNN |
|---|---|---|---|
| Frozen threshold | 0.478734 | -0.062874 | 0.471731 |
| Accuracy | 0.655771 | 0.653874 | 0.650985 |
| Precision | 0.988566 | 0.982406 | 0.997443 |
| Recall | 0.438040 | 0.437687 | 0.426182 |
| F1 | 0.607079 | 0.605575 | 0.597197 |
| False Positive Rate | 0.007828 | 0.012111 | 0.001688 |
| Specificity | 0.992172 | 0.987889 | 0.998312 |
| ROC-AUC | 0.852824 | 0.850177 | 0.850978 |
| PR-AUC | 0.867387 | 0.879445 | 0.864283 |
| Inference (approx. batch throughput) | ~0.0017 ms/flow | ~0.0068 ms/flow | ~0.0038 ms/flow |
| Training time | ~31 s | ~3,094 s | ~160 s |
| Model size | 172,630 tree nodes | 513 linear weights (+bias) | 10,561 trainable parameters |

Confusion matrices (test, N = 182,402; actual benign 71,670, actual malicious 110,732):

| Model | TN | FP | FN | TP |
|---|---|---|---|---|
| Random Forest | 71,109 | 561 | 62,227 | 48,505 |
| SVM (Nystroem + LinearSVC) | 70,802 | 868 | 62,266 | 48,466 |
| 1-D CNN | 71,549 | 121 | 63,540 | 47,192 |

> **Inference figures are approximate amortised batch-throughput measurements** — total wall-clock time to score the whole test split divided by the row count — **not single-flow latency**. They come from single timed runs on a load-variable machine (the identical RF scoring call produced 0.0011 and 0.0017 ms/flow on two occasions), so they indicate relative cost only.

## 3. FPR-budget behaviour (validation)

| Validation FPR budget | Random Forest | SVM | 1-D CNN |
|---|---|---|---|
| <= 0.1% | 0.534044 | 0.527777 | 0.531380 |
| <= 1.0% | 0.534044 | 0.535083 | 0.531380 |
| <= 5.0% | 0.534044 | 0.541459 | 0.531380 |
| <= 10.0% | 0.534044 | 0.541459 | 0.531380 |

Random Forest and 1-D CNN produce **discrete score distributions**: every budget resolves to the same threshold, at an achieved validation FPR of 0.000754 and 0.000181 respectively — far below the 1% cap. Widening the alarm budget therefore buys them no additional recall. Only SVM (Nystroem + LinearSVC) traces distinct thresholds, and even there recall rises only from 0.527777 to 0.541459 across a hundred-fold change in budget.

**Relationship to the frozen test results.** The threshold was selected on validation alone and then applied once to the test split. Validation and test recall differ as a result: for example RF moves from 0.534044 (validation) to 0.438040 (test), and the SVM's achieved FPR moves from 0.009992 to 0.012111. That drift is an ordinary consequence of fixing an operating point on one split and measuring it on another; no threshold was adjusted in response to test behaviour.

## 4. Per-attack-type interpretation (test)

| Attack Type | Support | Random Forest | SVM | 1-D CNN |
|---|---|---|---|---|
| ICMPFlood | 174 | 1.000000 | 1.000000 | 1.000000 |
| SYNFlood | 1,459 | 1.000000 | 1.000000 | 1.000000 |
| UDPScan | 2,387 | 1.000000 | 0.994554 | 0.996230 |
| SYNScan | 3,007 | 1.000000 | 0.997672 | 1.000000 |
| TCPConnectScan | 3,009 | 1.000000 | 0.997341 | 1.000000 |
| SlowrateDoS | 10,971 | 1.000000 | 0.999271 | 0.999544 |
| HTTPFlood | 21,123 | 0.999953 | 0.986555 | 0.999527 |
| UDPFlood | 68,602 | 0.092942 | 0.097023 | 0.074138 |
| _Benign (FPR)_ | 71,670 | 0.007828 | 0.012111 | 0.001688 |

Seven of the eight attack types are detected at 0.9866 or better by all three models. **UDP flood is the single common failure mode**: RF 0.0929, SVM 0.0970, CNN 0.0741 on 68,602 test flows.

**How much this establishes.** All three classifiers consume the same 67-feature representation, so their agreement provides corroboration across model families rather than three independent tests of the representation itself. It does not, on its own, prove a UDP-flood-specific limitation. The independent evidence is the Stage D exact-vector analysis summarised next, which was computed combinatorially from the data before any model was trained.

## 5. Representation-level explanation

After preprocessing the data has **67 model features**. Across 1,215,890 rows there are only 345,621 distinct feature vectors, and **33,709 of those vectors occur with both labels**. Assigning each distinct vector its majority label — the best any deterministic function of these features can do — still leaves **281,533 forced errors**, an empirical ceiling of **76.8455%** overall and **78.6258%** on the test split (Stage D review, README §12).

Exact feature-vector repetition across splits is substantial: 686,830 rows share a feature vector with another split, **72.97%** of test rows share a vector with training data, and **18.07%** of test rows are label-pure repeats of training rows.

The representation therefore contains many identical feature vectors associated with both labels, so a deterministic classifier using only these features cannot perfectly separate the classes. This is a property of the representation, not evidence that the three model families were badly implemented.

> **Scope of the ceiling.** This is the *empirical* ceiling under the evaluated exact-feature-vector representation and majority-rule analysis. It is **not** a universal theoretical limit for every possible model or for richer feature sets: a representation with additional or different features (for example window- or session-level aggregates) is not bound by it.

## 6. Principal findings

1. **Random Forest leads on accuracy, recall and F1** at the common operating point (0.655771, 0.438040, 0.607079), under the current feature representation.
2. **The CNN attains the lowest test FPR (0.001688) and highest precision (0.997443), together with the lowest recall (0.426182)** — it sits at the most conservative point of the trade-off.
3. **The SVM attains the highest PR-AUC (0.879445), but its frozen test operating point exceeds the 1% target at FPR 0.012111 (1.211%)** — the threshold met the constraint on validation (0.009992) and drifted on test.
4. **ROC-AUC is tightly clustered** (0.850177-0.852824), indicating broadly similar discrimination under the current feature representation.
5. **All three lose substantial recall under the strict FPR constraint** — recall spans 0.426182-0.438040, so roughly 56-57% of malicious test flows go undetected at this alarm budget.
6. **UDP flood is the major common attack-category failure mode** (0.0741-0.0970 recall), while the other seven attack types are detected almost completely.
7. **The representation-level conflict analysis explains both the convergence and the limits** of the three families: with 33,709 conflicting feature vectors and 281,533 forced errors, no deterministic classifier on this representation can separate the ambiguous mass.

## 7. Cost and complexity

Training cost differs by two orders of magnitude: RF ~31 s, CNN ~160 s, SVM ~3,094 s. Model complexity is expressed in each family's own units and is **not** comparable across rows: 172,630 tree nodes, 513 linear weights over the Nystroem feature map, 10,561 trainable parameters.

Approximate batch throughput orders as RF (~0.0017 ms/flow) < CNN (~0.0038) < SVM (~0.0068). These are machine-dependent, single-run measurements of amortised batch throughput and must not be read as deployment latency; no memory figures or hardware-normalised conclusions are offered because none were measured. On this evidence RF is the cheapest to both train and score, while the SVM is the most expensive on both counts.

## 8. Evaluation scope and limitations

M1 is evaluated under a **within-capture (within-session) protocol**: all 20 capture sessions contribute to train, validation and test, split by position within each session and label stream. Results measure the ability to classify later flows from capture sessions the model has already observed.

The experiment **does not establish**:

- unseen-capture generalisation
- unseen-session generalisation
- unseen-base-station generalisation
- unseen-attack generalisation

In particular this comparison **does not establish unseen-session generalisation**, and no figure or table here should be presented as if it did.

Further constraints on interpretation:

- Exact feature-vector repetition across splits is extensive (see §5), so part of the measured performance reflects repeated flow patterns rather than generalisation to novel ones.
- `Combined.csv` contains no wall-clock timestamp, IP-address or port fields, so no temporal or endpoint-identity analysis is possible from this data (`RunTime` is a flow duration, not a timestamp).
- `Attack Type` and `Attack Tool` are analysis metadata only and were never model inputs; they are used solely for the per-attack breakdown.
- This is a flow-level offline evaluation. It does not represent the complete SDN deployment loop — controller integration, telemetry collection cost and mitigation actions are out of scope.

