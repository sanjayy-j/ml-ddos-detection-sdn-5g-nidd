# Stage L — Secondary Unseen-Capture Generalisation Experiment

_Generated 2026-09-07T22:34:54+00:00 by `experiments/compare_unseen_capture.py` from frozen Stage I and Stage L artifacts. No model was loaded, no inference run, no threshold selected._

## 1. What this experiment is — and is not

This is a **secondary** evaluation. It does **not** replace the primary Stage E within-capture protocol, whose results remain the project's primary results.

Eight whole capture blocks — **[1, 3, 10, 12, 15, 16, 17, 19]** — were held out entirely. Models were trained, selected and thresholded using only the twelve development blocks **[0, 2, 4, 5, 6, 7, 8, 9, 11, 13, 14, 18]**.

| Partition | Rows | Malicious % |
|---|---|---|
| dev_train | 854,725 | 60.7092 |
| dev_val | 187,638 | 60.7079 |
| held_out | 173,527 | 60.7081 |

Preprocessing was fitted on **development-train only** (854,725 rows; scaler confirmed to have seen exactly that many). No primary preprocessor, matrix or model was reused.

## 2. The interpretation constraint — read before the numbers

**UDPFlood is absent from the held-out blocks and is NOT evaluable under this holdout.** It could not be included: every feasible whole-block subset containing block 4 or 14 carries a 42.9-43.5 pp class-prior shift. No substitute attack type was used.

This matters because the ambiguous mass that dominates the primary evaluation is almost entirely UDP flood:

| Population | Rows in conflicting feature vectors |
|---|---|
| Primary Stage E test | **56.2%** |
| Stage L held-out blocks | **0.0046%** |

The two evaluations therefore score **different and unequally difficult populations**. Any metric difference between them must be interpreted jointly with this conflict disparity and with the differing class composition — **it must NOT be read as a pure improvement in generalisation.**

## 3. Feature-vector novelty

| Statistic | Stage L held-out | Primary test |
|---|---|---|
| Rows whose vector occurs in development | 45.1734% | 73.9498% |
| Rows whose vector is unseen | 54.8266% | 26.0502% |
| Rows in conflicting vectors | 0.0046% | 56.2% |
| Unseen vectors that are conflicting | 0.0% | 0.8842% |

The held-out population is substantially more novel (54.8266% of rows carry a feature vector never seen in development, versus 26.0502% for the primary test). Novelty alone does not demonstrate generalisation; it characterises how different the evaluation population is.

## 4. Held-out results vs primary results

> The two rows per model are **not directly rankable** — different test populations, different difficulty (see §2).

| Model | Evaluation | Accuracy | Precision | Recall | F1 | FPR | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|
| Random Forest | secondary (unseen-capture) | 0.999867 | 0.999877 | 0.999905 | 0.999891 | 0.000191 | 1.000000 | 1.000000 |
| Random Forest | primary (within-capture) | 0.655771 | 0.988566 | 0.438040 | 0.607079 | 0.007828 | 0.852824 | 0.867387 |
| SVM (Nystroem + LinearSVC) | secondary (unseen-capture) | 0.984688 | 0.995407 | 0.979297 | 0.987286 | 0.006981 | 0.998848 | 0.998758 |
| SVM (Nystroem + LinearSVC) | primary (within-capture) | 0.653874 | 0.982406 | 0.437687 | 0.605575 | 0.012111 | 0.850177 | 0.879445 |
| 1-D CNN | secondary (unseen-capture) | 0.994618 | 0.993356 | 0.997807 | 0.995577 | 0.010311 | 0.999909 | 0.999946 |
| 1-D CNN | primary (within-capture) | 0.650985 | 0.997443 | 0.426182 | 0.597197 | 0.001688 | 0.850978 | 0.864283 |

## 5. Per-block held-out results

**Random Forest**

| Block | BS | Attack types | Rows | Malicious % | Accuracy | Precision | Recall | F1 | FPR | Specificity |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | TCPConnectScan | 11,645 | 86.063 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 1.000000 |
| 3 | 0 | ICMPFlood | 18,279 | 3.354 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 1.000000 |
| 10 | 1 | SYNScan | 11,526 | 86.969 | 0.999740 | 0.999701 | 1.000000 | 0.999850 | 0.001997 | 0.998003 |
| 12 | 1 | UDPScan | 10,305 | 77.817 | 0.998933 | 0.999875 | 0.998753 | 0.999314 | 0.000437 | 0.999563 |
| 15 | 1 | SYNFlood | 14,108 | 34.938 | 0.999858 | 0.999594 | 1.000000 | 0.999797 | 0.000218 | 0.999782 |
| 16 | 1 | HTTPFlood | 93,650 | 69.077 | 0.999925 | 0.999892 | 1.000000 | 0.999946 | 0.000242 | 0.999758 |
| 17 | 1 | SlowrateDoS | 12,656 | 55.681 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 1.000000 |
| 19 | 1 | Benign | 1,358 | 0.000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 |

**SVM (Nystroem + LinearSVC)**

| Block | BS | Attack types | Rows | Malicious % | Accuracy | Precision | Recall | F1 | FPR | Specificity |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | TCPConnectScan | 11,645 | 86.063 | 0.991413 | 0.999396 | 0.990621 | 0.994989 | 0.003697 | 0.996303 |
| 3 | 0 | ICMPFlood | 18,279 | 3.354 | 0.992888 | 0.867580 | 0.929853 | 0.897638 | 0.004925 | 0.995075 |
| 10 | 1 | SYNScan | 11,526 | 86.969 | 0.995836 | 0.998103 | 0.997107 | 0.997605 | 0.012650 | 0.987350 |
| 12 | 1 | UDPScan | 10,305 | 77.817 | 0.992140 | 0.996995 | 0.992892 | 0.994939 | 0.010499 | 0.989501 |
| 15 | 1 | SYNFlood | 14,108 | 34.938 | 0.993408 | 0.981481 | 1.000000 | 0.990654 | 0.010132 | 0.989868 |
| 16 | 1 | HTTPFlood | 93,650 | 69.077 | 0.977672 | 0.997663 | 0.969949 | 0.983611 | 0.005076 | 0.994924 |
| 17 | 1 | SlowrateDoS | 12,656 | 55.681 | 0.993205 | 0.989866 | 0.998013 | 0.993923 | 0.012837 | 0.987163 |
| 19 | 1 | Benign | 1,358 | 0.000 | 0.979381 | 0.000000 | 0.000000 | 0.000000 | 0.020619 | 0.979381 |

**1-D CNN**

| Block | BS | Attack types | Rows | Malicious % | Accuracy | Precision | Recall | F1 | FPR | Specificity |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | TCPConnectScan | 11,645 | 86.063 | 0.985144 | 0.999898 | 0.982838 | 0.991295 | 0.000616 | 0.999384 |
| 3 | 0 | ICMPFlood | 18,279 | 3.354 | 0.998687 | 0.962323 | 1.000000 | 0.980800 | 0.001359 | 0.998641 |
| 10 | 1 | SYNScan | 11,526 | 86.969 | 0.999913 | 0.999900 | 1.000000 | 0.999950 | 0.000666 | 0.999334 |
| 12 | 1 | UDPScan | 10,305 | 77.817 | 0.997477 | 0.999875 | 0.996882 | 0.998376 | 0.000437 | 0.999563 |
| 15 | 1 | SYNFlood | 14,108 | 34.938 | 0.999575 | 0.999189 | 0.999594 | 0.999391 | 0.000436 | 0.999564 |
| 16 | 1 | HTTPFlood | 93,650 | 69.077 | 0.992718 | 0.990047 | 0.999505 | 0.994754 | 0.022446 | 0.977554 |
| 17 | 1 | SlowrateDoS | 12,656 | 55.681 | 0.999368 | 0.998866 | 1.000000 | 0.999433 | 0.001426 | 0.998574 |
| 19 | 1 | Benign | 1,358 | 0.000 | 0.989691 | 0.000000 | 0.000000 | 0.000000 | 0.010309 | 0.989691 |

Block 19 is benign-only, so recall and precision are undefined there and report as 0; its false-positive rate is the meaningful quantity.

## 6. Per-attack-type held-out results

| Attack type | Random Forest | SVM (Nystroem + LinearSVC) | 1-D CNN |
|---|---|---|---|
| HTTPFlood | 1.000000 | 0.969949 | 0.999505 |
| ICMPFlood | 1.000000 | 0.929853 | 1.000000 |
| SYNFlood | 1.000000 | 1.000000 | 0.999594 |
| SYNScan | 1.000000 | 0.997107 | 1.000000 |
| SlowrateDoS | 1.000000 | 0.998013 | 1.000000 |
| TCPConnectScan | 1.000000 | 0.990621 | 0.982838 |
| UDPScan | 0.998753 | 0.992892 | 0.996882 |
| _Benign (FPR)_ | 0.000191 | 0.006981 | 0.010311 |
| **UDPFlood** | **NOT PRESENT / NOT EVALUABLE** | **NOT PRESENT / NOT EVALUABLE** | **NOT PRESENT / NOT EVALUABLE** |

## 7. Limitations

- **UDPFlood is not evaluable** under this holdout; Stage L cannot measure unseen-capture generalisation for the project's dominant failure mode.
- The held-out population is far less ambiguous than the primary test population, so held-out metrics are **not** comparable to primary metrics as a like-for-like improvement.
- Thresholds were fitted on development-validation, whose composition differs sharply from the held-out blocks; this alone can move the achieved operating point.
- This remains an offline flow-level evaluation. It does **not** establish real-world SDN/5G deployment performance, and does not cover controller integration, telemetry cost or mitigation.
- Results are specific to the evaluated 67-feature representation.

