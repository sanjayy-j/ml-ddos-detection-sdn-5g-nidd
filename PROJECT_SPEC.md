# Project Specification

## Project

ML-Based DDoS Detection in SDN Using the 5G-NIDD Dataset

## Methodologies

### M1 — Supervised ML

Owner: Sanjay

- Labelled 5G-NIDD data
- Argus flow-record statistics from `Combined.csv`
  (per-flow duration, packet/byte counts, rates, TTL, protocol and
  connection-state fields; the file contains no IP-address, port or
  wall-clock timestamp columns)
- Random Forest
- SVM
- 1-D CNN
- Supervised classification

### M2 — Entropy-Based Statistical Detection

Owner: Jani

- Shannon entropy
- Source-IP / destination-port distributions
- Sliding windows
- Adaptive EWMA threshold
- No labelled training data

### M3 — Sampled Telemetry + Incremental ML

Owners: Jaivarshan, Nithis

- sFlow/IPFIX-style sampling
- Sampling-rate sweep
- Hoeffding Tree / Adaptive Tree
- River
- Concept-drift adaptation
- Accuracy-versus-overhead analysis

## Common Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- False-positive rate
- Time-to-detect
- Controller CPU usage
- Controller memory usage
- Flow-table entry count
- Throughput
- Per-flow inference time

## Common Evaluation Principle

M1, M2 and M3 must ultimately be evaluated under
comparable traffic scenarios and with consistent metric
definitions.

## Dataset

5G-NIDD

Raw dataset files should not be committed to GitHub.

## SDN Environment

- Mininet
- Open vSwitch
- Ryu / ONOS
- OpenFlow

## Important

Do not independently change the common feature schema,
labels, evaluation metrics, or experimental protocol
without discussing it with the team.
