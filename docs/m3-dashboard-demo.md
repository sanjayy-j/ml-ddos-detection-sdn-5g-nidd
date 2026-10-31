# M3 dashboard walkthrough

This is a short walkthrough of **recorded results**, not a recording of a new
Mininet experiment. [Open the animated screenshot walkthrough](media/m3-walkthrough.gif).

1. **Overview:** the dashboard contains 54 completed primary trials, with no
   running or failed primary trials in this published evidence store.
2. **Unsampled reference:** select `N=1`, baseline, seed 42. This individual trial
   displays 99.8% F1 and 160.43 kbit/s combined sFlow/OpenFlow IP-layer bandwidth.
   The timeline shows predictions against independent experimental labels.
3. **Sampled comparison:** select `N=2`, baseline, seed 42. This individual trial
   displays 97.3% F1 and 86.18 kbit/s. Sampling lowers monitoring traffic and
   also changes prediction quality. These are individual trials, not cell means.
4. **All compatible trials:** inspect the sampling trade-off plot. Each dot is
   one trial. Use the repeated-trial results table in the main README for mean
   results, and the current study package for uncertainty and false positives.

The animation is assembled from four unaltered dashboard screenshots, held for
approximately 25 seconds in total. It is a sequence of recorded views rather
than a continuous screen recording. The overview, both metric views and the
comparison plot all come from the current 54-trial kernel-clock study.

The lab uses official 5G-NIDD packet selections, constructed equal-rate replay
and oracle labels revealed after prediction. These results do not establish
physical 5G deployment performance or production label availability.

To inspect the same evidence yourself, follow [the dashboard setup](../README.md#run-the-m3-dashboard).
