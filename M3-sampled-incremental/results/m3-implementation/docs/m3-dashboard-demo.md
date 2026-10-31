# M3 dashboard walkthrough

This short walkthrough displays **recorded results**, not a new network replay.
[Open the 25-second animated walkthrough](media/m3-walkthrough.gif).

1. Overview: 54 completed primary trials in the published evidence store.
2. N=1, baseline, seed 42: 99.8% F1 and 160.43 kbit/s combined IP-layer bandwidth.
3. N=2, baseline, seed 42: 97.3% F1 and 86.18 kbit/s. Compare the timeline and metrics.
4. Sampling trade-off: each dot is one compatible trial; observation accounting
   separates evaluated, warm-up and unlabeled windows.

The animation is assembled from four actual dashboard screenshots. It is a
sequence of recorded views, rather than a continuous screen recording. Its
individual-trial values differ from the three-repeat means in the README.

This is a controlled Mininet/OVS study with constructed replay timing and oracle
labels revealed after prediction. See [setup and scope](../README.md).
