# ML-Based DDoS Detection in SDN Using 5G-NIDD

A comparative study of three methodologies for DDoS
detection in Software-Defined Networking (SDN).

## Status

| Methodology | Owner | Status in this repository |
|---|---|---|
| M1 — Supervised ML | Sanjay | **Implemented and evaluated** — see [`M1-supervised-ml/README.md`](M1-supervised-ml/README.md) |
| M2 — Entropy-Based Statistical Detection | Jani | Directory contains only its original scaffolding and a `.gitkeep` file |
| M3 — Sampled Telemetry + Incremental ML | Jaivarshan, Nithis | Directory contains only its original scaffolding and a `.gitkeep` file |

The M2/M3 rows state only what is currently present in the repository.

## Methodologies

### M1 — Supervised ML

**Owner:** Sanjay

Labelled traffic + full telemetry using:

- Random Forest
- SVM
- 1-D CNN

Random Forest, SVM (Nystroem RBF approximation + LinearSVC) and a 1-D CNN
are trained on a 67-feature flow representation of the 5G-NIDD
`Combined.csv` Argus records and compared at a common
validation-selected FPR <= 1% operating point, with a secondary
unseen-capture experiment. The evaluation is **within-capture
(within-session)** and does not establish unseen-session generalisation.

- Documentation: [`M1-supervised-ml/README.md`](M1-supervised-ml/README.md)
- Results index: [`M1-supervised-ml/README.md` §0](M1-supervised-ml/README.md)
- Model comparison: [`M1-supervised-ml/results/evaluation/model_comparison.md`](M1-supervised-ml/results/evaluation/model_comparison.md)
- Secondary experiment: [`M1-supervised-ml/results/unseen_capture/unseen_capture_comparison.md`](M1-supervised-ml/results/unseen_capture/unseen_capture_comparison.md)
- Figures: [`M1-supervised-ml/results/plots/`](M1-supervised-ml/results/plots/)

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
