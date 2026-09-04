# ML-Based DDoS Detection in SDN Using 5G-NIDD

A comparative study of three methodologies for DDoS
detection in Software-Defined Networking (SDN).

## Methodologies

### M1 — Supervised ML

**Owner:** Sanjay

Labelled traffic + full telemetry using:

- Random Forest
- SVM
- 1-D CNN

### M2 — Entropy-Based Statistical Detection

**Owner:** Jani

Label-free detection using:

- Shannon entropy
- Sliding windows
- Adaptive EWMA thresholds

### M3 — Sampled Telemetry + Incremental ML

**Owners:** Jaivarshan, Nithis

Reduced telemetry using:

- Sampling
- Hoeffding Tree / Adaptive Tree
- Incremental learning
- Concept-drift detection

## Project Structure

```text
M1-supervised-ml/
M2-entropy/
M3-sampled-incremental/
shared/
testbed/
data/
experiments/
docs/
notebooks/
```
