# M2 — Entropy-Based Statistical Detection (5G-NIDD)

Part of *ML-Based DDoS Detection in SDN Using the 5G-NIDD Dataset*. This module detects
anomalous traffic windows from **Shannon entropy of the source-IP distribution** and
**Shannon entropy of the destination-port distribution** (two separate features), smoothed
with EWMA and judged by adaptive median/MAD thresholds. It is label-free: labels are used only
afterwards, for evaluation.

## Pipeline

```
CSV (chunked, 4-7 columns only)  ->  sessions from Rank resets
 -> flow-count sliding windows (never cross a session)
 -> H(SrcAddr), H(Dport) per window            (SrcAddr_entropy, Dport_entropy)
 -> EWMA per feature                           (*_ewma; state RESET at each session start)
 -> rolling median/MAD baseline + threshold    (history RESET at each session start)
 -> per-feature alarms -> voting -> window_anomaly
 -> evaluation vs. dataset Label (after detection)
```

Files: `entropy.py`, `features.py`, `windowing.py`, `window_entropy.py`, `ewma.py`,
`thresholds.py`, `pipeline.py` (original modules); `data_loader.py`, `evaluation.py`,
`run_m2.py` (loader, evaluation, CLI); `run_pipeline.py` (original generic runner, kept as is).

## Setup

Python 3.10+ (tested on 3.12.3 with pandas 3.0.2, numpy 2.4.4). No other dependencies.

```bash
pip install pandas numpy
unzip BTS1_BTS2_fields_preserved.zip          # -> BTS1_BTS2_fields_preserved.csv (~450 MB)
```

## Input data

Required columns (names verified against `BTS1_BTS2_fields_preserved.csv`; the loader stops with
an explicit message if one is missing and never substitutes another field):

| Purpose | Column | Notes |
|---|---|---|
| Source IP | `SrcAddr` | 121 distinct values, never empty |
| Destination port | `Dport` | tokens kept **verbatim**: decimals (`853`), hex (`0x0800`, ICMP rows), Argus service names (`http`); **empty for 857,853 rows (70.6%)** |
| Ordering / sessions | `Rank` | strictly +1 inside a capture file, restarts at 1 per file |
| Ground truth | `Label` | `Benign` / `Malicious` (`Attack Type`, `Attack Tool` optional) |

Facts about this dataset that shape the implementation:
* **No session-ID column.** A new session starts at the first row and wherever `Rank` <= previous
  `Rank`. The file contains **20 sessions**; no Rank gaps occur inside any of them.
* **`StartTime` is only `mm:ss.f`** (no hour/date, wraps, not monotone inside sessions), so it
  is *not* used. Ordering = original file order, which is Rank order inside each session.
* **Missing `Dport`**: all 857,853 empty cells are UDP/SCTP/LLDP/ARP rows, including **every
  `UDPFlood` row (457,340)** and 400,513 benign rows. Nothing is imputed.
  Default (`--dport-missing exclude`): `Dport` entropy is computed over *observed* ports only; a
  window with fewer than `--min-observed` (10) observed ports gets NaN entropy ("not evaluable":
  EWMA holds state, no alarm possible). Per-window `Dport_observed_count` / `Dport_missing_count`
  are written to `windows.csv`. Alternative `--dport-missing category` treats missing as one
  explicit `__missing__` category. Because missingness is perfectly aligned with UDPFlood, this
  option lets the detector exploit a data artifact, so interpret it with care.

## Run

From the folder that contains `M2-entropy/`:

```bash
python M2-entropy/run_m2.py --input /path/to/BTS1_BTS2_fields_preserved.csv
```
Full file (1,215,890 rows): about 1 minute, modest memory (only needed columns are read, in chunks).
Quick check on a slice: add `--max-rows 60000` (truncates sessions).

Main options (defaults in brackets): `--window-size [100]`, `--step-size [50]` (flows),
`--alpha [0.2]`, `--history-len [50]`, `--min-history [10]`, `--k-sensitivity [3.0]`,
`--direction lower|upper|both [both]`, `--voting-threshold [2]` (1 = either feature alarms,
2 = both), `--dport-missing exclude|category [exclude]`, `--min-observed [10]`,
`--attack-fraction [0.5]`, `--output-dir [M2-entropy/results/m2_run]`, `--no-eval`.
Run `python M2-entropy/run_m2.py --help` for all.

## Output (in `--output-dir`, separate from source code)

* `windows.csv` — one row per window: `window_id, start_idx, end_idx` (positional row range),
  `session_id`, `SrcAddr_entropy`, `Dport_entropy`, `*_ewma`, baselines/MAD/thresholds, per-feature
  `*_alarm`, `threshold_is_warmup`, `threshold_is_valid`, `window_anomaly`, and (unless
  `--no-eval`) `malicious_fraction`, `y_true`, `dominant_attack_type`.
* `metrics.json` — arguments, environment, data-quality statistics (rows, sessions, missing
  counts by label / attack type / protocol / session, port token kinds), pipeline summary and
  evaluation (confusion matrix, precision, recall, F1, FPR, accuracy, per-attack-type recall).

### Evaluation protocol used
A window is an *attack* window if >= `--attack-fraction` (0.5) of its flows have `Label ==
Malicious`; prediction = `window_anomaly`. Two scopes are reported: **all windows** (warm-up and
unevaluable windows count as "no alarm") and **evaluable windows** (not warm-up, valid).
Windows overlap (step < size), so counts are windows, not flows. The team protocol document was
not in the M2 sources; if M1/M3 use another rule (e.g. flow-level), re-derive from `windows.csv`
(`malicious_fraction`, `start_idx`, `end_idx`) or change `--attack-fraction`.
`metrics.json` also reports, under `evaluation_any_malicious_flow`, the same predictions scored
with the rule of the legacy prefix run (a window is an attack if any of its flows is malicious).
Every metric block includes chance references: `base_rate` (share of attack windows),
`precision_lift` (precision / base rate), `balanced_accuracy` and `mcc`. A detector whose alarms
are independent of the labels has precision equal to the base rate, so a lift below 1, a balanced
accuracy below 0.5 or a negative MCC means worse than chance.

## Tests

```bash
cd M2-entropy
python -m unittest discover -s tests -v
```
Tests are self-contained (synthetic data in the real schema); the dataset is not needed.

## Changes relative to the repository version
* `ewma.py`: `smooth_entropy_dataframe` now resets EWMA state at session boundaries
  (`session_id` auto-detected, or `session_col=`) and has `nan_policy` (`raise` default, `hold`).
  Previously EWMA state leaked from the end of one session into the start of the next.
* `pipeline.py`: passes session boundaries and `nan_policy="hold"` to EWMA.
* `features.py`, `window_entropy.py`: opt-in `unobserved_missing_cols` / `min_observed` so missing
  values are excluded and counted instead of filled (defaults unchanged).
* New: `data_loader.py`, `evaluation.py`, `run_m2.py`, tests, this README.

## Limitations
* Only `SrcAddr`/`Dport` entropy is used (the M2 method). The older library default feature set
  (Proto, State, sTtl, ...) is untouched but not used by `run_m2.py`.
* `Dport` is missing for most UDP traffic, so port entropy cannot characterise UDPFlood; see above.
* Thresholds/parameters are untuned defaults; no hyper-parameter search was done.
* Window definition is flow-count based (no usable timestamps).

## Included results (genuine, produced by this code on the uploaded dataset)
All full-file runs read the complete `BTS1_BTS2_fields_preserved.csv` (1,215,890 rows, 20
sessions; SHA-256 `37287d51…1b9d`, as in the M3 data manifest).
`results/5gnidd_default/` (`metrics.json`, `windows.csv.gz`, `per_session.csv`) is the default-configuration run:
`python M2-entropy/run_m2.py --input BTS1_BTS2_fields_preserved.csv --output-dir M2-entropy/results/5gnidd_default`.
`results/sensitivity_*/metrics.json` are the same data with `--k-sensitivity 2`, `--voting-threshold 1`,
`--dport-missing category`, or the last two together; they are illustrative sensitivity runs, **not
tuned or selected** results. Re-running overwrites them. Raw dataset files are not included.
`results/m2_results_summary.csv` tabulates every run under both window-labelling rules, with the
chance references; regenerate it with `python M2-entropy/summarize_results.py`.

`results/sensitivity_summary.csv` is the **legacy prefix run** (superseded): `run_sensitivity.py`
with the older ten-attribute feature set (Proto, State, sTtl, sDSb, SrcAddr, Dport, TotPkts,
TotBytes, Rate, Dur), no session resets and the any-malicious-flow rule, on the first 50,000 rows
only (1,000 windows). Running `run_sensitivity.py` from commit `541fdb0` reproduces it byte for
byte. The current shared modules change two of its windows (TN 147 -> 148 for k = 3 and
127 -> 128 for k = 2), because of the later session and NaN handling in EWMA.

| Run (all windows) | Rule | Windows | Base rate | Precision | Lift | Recall | FPR | Balanced acc. | MCC |
|---|---|---|---|---|---|---|---|---|---|
| Legacy prefix, k = 3, 2 votes | any malicious flow | 1,000 | 0.672 | 0.477 | 0.71 | 0.246 | 0.552 | 0.347 | -0.302 |
| Full file, default | malicious fraction >= 0.5 | 24,311 | 0.612 | 0.563 | 0.92 | 0.029 | 0.035 | 0.497 | -0.018 |
| Full file, default | any malicious flow | 24,311 | 0.653 | 0.679 | 1.04 | 0.032 | 0.029 | 0.502 | 0.010 |

The legacy prefix run was worse than chance. On the full file the current detector is at chance
level: no setting reaches a balanced accuracy above 0.508 or an MCC above 0.035. UDP flood makes up
9,129 of the 14,881 attack windows (>= 0.5 rule), and 14,752 of the 15,077 windows of the two
UDP-flood sessions have no observed destination port, so with two votes they cannot alarm
(UDP-flood recall 0). Per-session counts are in `results/5gnidd_default/per_session.csv`.
