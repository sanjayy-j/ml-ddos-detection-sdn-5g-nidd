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

In progress on this branch; this section will be added when the M3 analysis is committed.
