# Second-level findings — M2 and M3

Handover note for whoever edits the manuscript source. It answers the M2 and M3 items of the
second-level review ("Team-1-CN-Second level corrections"), which checked the v3 manuscript
against commit `10fc7de`. Every number below was measured from files committed on this branch;
nothing is an estimate unless it says so. The manuscript source is not in this repository, so
no manuscript text has been changed; the statements that need changing are named explicitly.

Neither pipeline is dropped. Both remain in the study with corrected evidence.

## 1. M2 — entropy detector (review item 3)

### 1.1 What the review found

- The paper's M2 numbers come from a 50,000-record prefix run of a superseded configuration.
- 672 of the 1,000 prefix windows are malicious, so precision 0.477 is below the 0.672 base
  rate: the detector was worse than chance, and the paper does not say so.

### 1.2 Provenance of the paper's numbers (confirmed)

`results/sensitivity_summary.csv` is reproduced byte for byte by `run_sensitivity.py` at commit
`541fdb0` on the first 50,000 rows of `BTS1_BTS2_fields_preserved.csv`. That run used ten
attributes (Proto, State, sTtl, sDSb, SrcAddr, Dport, TotPkts, TotBytes, Rate, Dur), no session
resets and the any-malicious-flow window rule. The current shared modules change two of its
windows (TN 147 → 148 at k = 3 and 127 → 128 at k = 2) because of the later session and NaN
handling. The file is kept and documented as the superseded legacy run.

### 1.3 What changed in the repository

| Commit | Contents |
|---|---|
| `3a41b31` | Chance references in every M2 evaluation (`base_rate`, `alarm_rate`, `precision_lift`, `balanced_accuracy`, `mcc`); the legacy any-malicious-flow rule reported beside the default ≥ 0.5 rule; 4 new tests (M2 suite 155 → 159, all passing) |
| `3098b76` | Full-file runs of the current session-aware detector (default plus four sensitivity settings); `summarize_results.py` and `results/m2_results_summary.csv`; per-session counts; README updated |

The detector itself was not changed or tuned, and no setting was selected on these results.

### 1.4 Full-file results of the current detector

Input: complete `BTS1_BTS2_fields_preserved.csv`, 1,215,890 rows, 20 sessions (publisher
SHA-256 verified). Windows of 100 flows, step 50, never crossing a session: 24,311 windows.
Features: Shannon entropy of SrcAddr and of Dport; EWMA α = 0.2 and the median/MAD history
(50 windows, warm-up 10) both reset at each session start; k = 3, MAD floor 10⁻⁴; an alarm
needs both features (two votes). Dport is missing for 857,853 rows (70.6%), including all
457,340 UDP-flood rows; a window with fewer than 10 observed ports is not evaluable.

All windows (warm-up and unevaluable windows count as "no alarm"):

| Run | Rule | Base rate | Precision | Lift | Recall | FPR | Balanced acc. | MCC |
|---|---|---|---|---|---|---|---|---|
| Legacy prefix (paper), k = 3, 2 votes | any malicious flow | 0.672 | 0.477 | 0.71 | 0.246 | 0.552 | 0.347 | −0.302 |
| Full file, default | malicious fraction ≥ 0.5 | 0.612 | 0.563 | 0.92 | 0.029 | 0.035 | 0.497 | −0.018 |
| Full file, default | any malicious flow | 0.653 | 0.679 | 1.04 | 0.032 | 0.029 | 0.502 | 0.010 |
| Full file, k = 2 | any malicious flow | 0.653 | 0.730 | 1.12 | 0.050 | 0.035 | 0.508 | 0.035 |
| Full file, one vote | any malicious flow | 0.653 | 0.664 | 1.02 | 0.063 | 0.060 | 0.501 | 0.006 |
| Full file, missing port as category | any malicious flow | 0.653 | 0.626 | 0.96 | 0.145 | 0.162 | 0.491 | −0.024 |
| Full file, one vote + category | any malicious flow | 0.653 | 0.570 | 0.87 | 0.173 | 0.245 | 0.464 | −0.087 |

Default run, ≥ 0.5 rule: 759 alarms (427 TP, 332 FP) for 14,881 attack windows. Only 7,853
windows (32.3%) are evaluable; on those, precision 0.563 against a base rate of 0.727, recall
0.075, FPR 0.155. Every row, both rules and both scopes, is in `results/m2_results_summary.csv`.

**Reading.** The legacy prefix run was worse than chance (MCC −0.30). The current detector on
the full file is at chance level: no setting exceeds a balanced accuracy of 0.508 or an MCC of
0.035. The "missing port as category" settings exploit the alignment of missing ports with UDP
flood and still do not beat chance.

### 1.5 Why, quantified

- **UDP flood cannot alarm.** UDP flood is 9,129 of the 14,881 attack windows (61.3%). In the two
  UDP-flood sessions, 14,752 of 15,077 windows (97.8%) have no evaluable Dport entropy, so with two
  votes they cannot alarm: UDP-flood recall is 0 (`per_session.csv`, sessions 5 and 15).
- **Other attacks: recall 0.007–0.112** (HTTP flood 0.080, slow-rate DoS 0.060, SYN scan 0.080,
  TCP connect scan 0.077, UDP scan 0.112, SYN flood 0.007).
- **The history fills with attack windows.** In the 18 attack sessions, 23.9% of the 10 warm-up
  windows and 47.9% of the first 60 windows (warm-up plus a full 50-window history) are attack
  windows, which is at the 50% breakdown point of the median/MAD baseline discussed in §5.4.

### 1.6 Manuscript statements to update (v3)

| Location | Current text (abridged) | Measured replacement |
|---|---|---|
| Abstract | "On a 50,000-record prefix, the entropy detector reached precision 0.48 at a window false-positive rate of 0.55." | On the full file (24,311 windows), precision 0.563 against a base rate of 0.612, recall 0.029, FPR 0.035, balanced accuracy 0.497 (chance level). The prefix figure was below chance (base rate 0.672). |
| §1, last paragraph | "M2 only on a 50,000-record prefix" | M2 on the full file (1,215,890 records) |
| Table 2, M2 row | Data: first 50,000 records; label: any malicious flow; evaluation: one committed run and two sensitivity settings; not established: full-file performance, the session-aware revision | Data: full address-preserving file, 24,311 windows; label: ≥ 0.5 malicious flows (any-flow rule also reported); evaluation: session-aware run at default settings and four sensitivity settings; not established: detection above chance, UDP-flood detection, a tuned operating point |
| §3.4 | Ten attributes, binned numeric attributes, no session reset, prefix run; "a later, session-aware revision … has no committed outputs and is not reported" | Two attributes (SrcAddr, Dport entropy); EWMA and history reset per session; Dport over observed values only (≥ 10 per window); both attributes must alarm; full file. Eqs. (5)–(6), α, k, ε and the history length are unchanged. |
| §4.6 | 346 of 1,000 windows; precision 0.477, recall 0.246, F1 0.324, FPR 0.552; sensitivity recall 0.29–0.30, FPR 0.61–0.63 | Use §1.4 above, with the base rate beside every precision. The data-audit sentence (857,853 empty ports, 70.6%, all 457,340 UDP-flood records) is unchanged and correct. |
| §5.4 | "M2 performed poorly on its prefix … needs a full-file evaluation with archived outputs" | Full-file evaluation now archived; chance level; mechanisms in §1.5 |
| §5.6 | "M2 was evaluated only on a prefix, with a superseded configuration." | Remove; state that no M2 setting beats chance and that UDP flood is unobservable to Dport entropy |
| §6 | "The entropy detector performed poorly on a dataset prefix"; future work "evaluate the session-aware entropy detector on the full release" | Performed at chance level on the full release; that future-work item is done |
| Data availability | "Not archived are … the outputs of the full-file M2 run" | The full-file M2 outputs are archived (`M2-entropy/results/`) |

### 1.7 Reproduce

```bash
python M3-sampled-incremental/results/m3-implementation/scripts/fetch_dataset.py --file BTS1_BTS2_fields_preserved.zip
# (or download it from Fairdata and unzip it; CSV SHA-256 37287d5188006135d9575687439e47148c5b7adb1a139bd7cd37acc11cec1b9d)
python M2-entropy/run_m2.py --input BTS1_BTS2_fields_preserved.csv --output-dir M2-entropy/results/5gnidd_default
python M2-entropy/run_m2.py --input BTS1_BTS2_fields_preserved.csv --output-dir M2-entropy/results/sensitivity_k2 --k-sensitivity 2
python M2-entropy/run_m2.py --input BTS1_BTS2_fields_preserved.csv --output-dir M2-entropy/results/sensitivity_vote1 --voting-threshold 1
python M2-entropy/run_m2.py --input BTS1_BTS2_fields_preserved.csv --output-dir M2-entropy/results/sensitivity_dport_category --dport-missing category
python M2-entropy/run_m2.py --input BTS1_BTS2_fields_preserved.csv --output-dir M2-entropy/results/sensitivity_vote1_dport_category --voting-threshold 1 --dport-missing category
gzip -9 -n M2-entropy/results/5gnidd_default/windows.csv   # sensitivity runs keep metrics.json only
python M2-entropy/summarize_results.py
```

Note that `fetch_dataset.py` also rewrites `M3-sampled-incremental/results/m3-implementation/data/manifest.json`;
discard that change or run a copy of the script. Runs here used Python 3.14.7, pandas 3.0.2 and
NumPy 2.4.4 (recorded in each `metrics.json`); each full-file run takes about 12 s.

## 2. M3 — sampled incremental detector (review item 2)

### 2.1 What the review found

- The unsampled N = 1 reference is anomalous in all three scenarios (recall ≈ 0.999, FPR 0.63–0.90),
  so "1-in-2 sampling raises F1 by 0.26" rests on a broken comparator.
- Suspected cause: sFlow datagram batching against 0.1-s windows. Requested: diagnose (timestamps or
  1-s windows), otherwise move M3 to the supplement.

### 2.2 Diagnosis

All of it is measured from the committed `research/results/derived_trial_evidence.zip` (per-window
features, predictions and run summaries of all 54 trials); the raw sFlow exports are not needed.

- **The offline replay is exact.** Replaying every trial reproduces all 12 live quality metrics
  (largest difference 0), and the archived summaries reproduce the committed
  `aggregated_metrics.json`, `paired_deltas.json` and `pareto_recommendations.json` (difference 0).
- **Cause 1, no split.** In 8 of the 9 N = 1 trials the Hoeffding Adaptive Tree stayed a single leaf.
  Its two best splits, mean packet size and byte rate (merits 0.984–0.997 and 0.966–0.988), separate
  the classes almost perfectly and tie: their difference stayed below the Hoeffding bound
  (0.077–0.086), which stayed above the tie threshold τ = 0.05. A tie split needs 3,224 labelled
  windows; the trials had 1,091–1,352.
- **Cause 2, a wrong leaf vote.** River 0.23's naive-Bayes vote adds `log(p) if p > 0 else 0.0`, so a
  density that underflows to 0 counts as certainty. Benign windows (~1,200-byte packets) have zero
  density under the flood class (~53-byte packets), so the leaf scores them as attacks with
  probability ≈ 1.
- **Control.** The one N = 1 trial whose tree did split (drift, trial 2) reached F1 0.990 at FPR 0.016
  as run, which is also why drift N = 1 had a standard deviation of 0.18.
- **Not batching.** At N = 1 only 0.1–1.2% of benign and 1.3–4.2% of attack windows are empty, and the
  archived one-second re-scoring (made during the study) keeps the N = 1 FPR at 0.73–0.81. At one second
  the N = 2 advantage also disappears (F1 0.65–0.68). Batching does make attack windows empty more
  often than benign ones at N ≥ 2 (46–50% against 4.5–7.5% at N = 2), and empty windows are flagged;
  after the fix this, not the learner, limits quality from N = 5.

### 2.3 What changed in the repository

| Commit | Contents |
|---|---|
| `45e80a7` | `m3.naive_bayes`: log-space naive-Bayes vote, identical to River when nothing underflows; `RunConfig.naive_bayes` (`"log_space"` default, `"river"` = the published trials) used by the detector and `evaluate_ablations`; `analyse_research.py` and `compute_sensitivity.py` replay each run with its recorded vote, so committed outputs still reproduce; 5 new tests (M3 suite 138 → 143 passing, 1 skipped as before) |
| `c462b73` | `scripts/reanalyse_naive_bayes.py` and its outputs (`research/N1_Baseline_Reanalysis.md`, `research/results/naive_bayes_reanalysis.json` / `_cells.csv`); M3 README, verification status, methods and reproduction guide state the correction; `research/SHA256SUMS.txt` covers the new and edited files |

The live study, its evidence archive and the committed as-run results, including
`M3_Research_Report.md`/`.pdf`/`.pptx`, are unchanged. Only the vote differs in the re-analysis.

### 2.4 Corrected results

Mean attack F1 / FPR over three trials, as run → corrected; bandwidth (combined IP-layer sFlow and
OpenFlow, baseline scenario) is learner-independent and unchanged.

| N | Baseline | Drift | Unseen | Bandwidth (kbit/s) |
|---|---|---|---|---|
| 1 | 0.692 / 0.887 → **0.997 / 0.006** | 0.778 / 0.629 → **0.985 / 0.016** | 0.688 / 0.901 → **0.994 / 0.012** | 160.5 |
| 2 | 0.956 / 0.090 → 0.963 / 0.074 | 0.954 / 0.095 → 0.959 / 0.084 | 0.962 / 0.077 → 0.968 / 0.063 | 85.1 |
| 5 | 0.777 / 0.473 → 0.807 / 0.438 | 0.776 / 0.488 → 0.785 / 0.461 | 0.777 / 0.494 → 0.799 / 0.456 | 40.3 |
| 10 | 0.688 / 0.710 → 0.715 / 0.693 | 0.702 / 0.726 → 0.706 / 0.708 | 0.709 / 0.719 → 0.729 / 0.703 | 25.1 |
| 20 | 0.601 / 0.820 → 0.677 / 0.839 | 0.614 / 0.906 → 0.657 / 0.845 | 0.630 / 0.912 → 0.681 / 0.827 | 17.9 |
| 50 | 0.615 / 0.761 → 0.661 / 0.802 | 0.614 / 0.922 → 0.649 / 0.914 | 0.595 / 0.854 → 0.650 / 0.891 | 13.4 |

- **Paired against N = 1 (corrected, 95% Student-t, n = 3):** N = 2 changes F1 by −0.034 [−0.051, −0.016]
  (baseline), −0.026 [−0.054, 0.002] (drift) and −0.025 [−0.029, −0.022] (unseen); N = 50 by −0.336 to
  −0.344. Quality now falls as N grows.
- **Quality–cost front:** the equal-weight rule still selects N = 2 in all three scenarios (corrected
  F1 0.959–0.968 at 76.7–85.6 kbit/s); N = 1 joins the front as the highest-quality point.
- **Held-out SYN recall (unseen):** N = 2 0.997 → 0.997; N = 50 0.813 → 0.924.
- **Adaptive versus non-adaptive tree:** still within 0.05 F1 in every cell (largest corrected
  difference 0.0095), so "no benefit from adaptation" stands.
- **Not re-scored:** detection delay, post-drift recovery (e.g. the 6.51 s at N = 2), CPU and latency
  are live measurements of the original learner. Per-trial values for every cell are in
  `naive_bayes_reanalysis.json` (also answering the review's request for per-trial values).

### 2.5 Manuscript statements to update (v3)

| Location | Current text (abridged) | Measured replacement |
|---|---|---|
| Abstract | "the sampled detector reached mean F1 of 0.954–0.962 at 1-in-2 sampling with 46–47% less telemetry" | Unsampled export F1 0.985–0.997; 1-in-2 sampling F1 0.959–0.968 with 46–47% less telemetry (−0.025 to −0.034 F1) |
| §3.5 | HAT settings | Add the log-space naive-Bayes vote; state that the trials ran with River's vote and were re-scored offline from the recorded features |
| §4.7 and Table 6 | Non-monotonic quality; N = 2 best; "F1 at N = 2 exceeded that at N = 1 by 0.264 … 0.274"; N = 1 FPRs of 63–90% | Table in §2.4 and the paired differences; report the as-run N = 1 failure as a diagnosed learner defect (§2.2). Held-out SYN recall 0.997 (N = 2) and 0.924 (N = 50). The "within 0.05 F1" sentence stands. |
| §5.4 | "We did not isolate export batching, feature timing or learner state, so this design cannot explain the non-monotonic curve or the high false-positive rate of unsampled export." | Explained: the learner (no split plus the underflowing vote), not batching; empty windows limit quality from N = 5 |
| §5.6 | M3 limitations | Add: corrected quality is an offline re-scoring of recorded features; delay, recovery and CPU are as run |
| §6 | "the sampled detector exceeded an F1 of 0.95 at 1-in-2 sampling" | Unsampled 0.985–0.997; 1-in-2 sampling 0.959–0.968 for about half the telemetry |
| Data availability | — | Add `scripts/reanalyse_naive_bayes.py` and its outputs |

### 2.6 Reproduce

```bash
cd M3-sampled-incremental/results/m3-implementation
python -m pip install -e .            # Python 3.12, river 0.23.0, numpy 2.5.4, scipy 1.18.1 as in the live study
python scripts/reanalyse_naive_bayes.py   # stops unless both reproduction checks pass; about 5 s
python -m pytest
```
