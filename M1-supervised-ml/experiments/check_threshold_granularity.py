"""Phase 3.3 analysis — is the FPR-constrained selection granularity-bound?

The validation-to-test FPR ratio differs by an order of magnitude between
the three models (10.39x, 1.21x, 9.30x on the published window). The
explanation is the validation denominator: the rule takes the lowest
threshold whose validation FPR is <= 1%, so it should land just under the
cap, and only does so for the SVC, whose decision values are smooth.

This script checks that claim directly for the Random Forest by printing
the validation FPR at the next LOWER available ROC threshold. If that FPR
exceeds the 1% cap, the selection had no closer operating point available
and its headroom is forced by score granularity rather than chosen.

Run from the repository root; trains the published configuration, which
is deterministic, so it reproduces the committed frozen threshold.
"""

import sys, numpy as np
sys.path.insert(0, "M1-supervised-ml")
from sklearn.metrics import roc_curve
from models.random_forest import build_random_forest
from preprocessing.data_loader import load_config_file
from preprocessing.pipeline import load_processed
from pathlib import Path

cfg = load_config_file("M1-supervised-ml/config/m1_config.yaml")
data = load_processed(cfg, Path("."))
m = build_random_forest(cfg, max_depth=20, min_samples_leaf=20, max_features="sqrt")
m.fit(data["X"]["train"], data["y"]["train"])
s = m.predict_proba(data["X"]["val"])[:, 1]
y = data["y"]["val"]
fpr, tpr, thr = roc_curve(y, s)
frozen = 0.4787342346089332
i = int(np.argmin(np.abs(thr - frozen)))
print(f"  distinct validation score values: {len(np.unique(s)):,}")
print(f"  ROC operating points: {len(thr):,}")
print(f"  frozen threshold index {i}: thr={thr[i]:.10f} fpr={fpr[i]:.8f} tpr={tpr[i]:.6f}")
print("\n  neighbourhood (ROC thresholds descend as index rises):")
for j in range(max(0, i-2), min(len(thr), i+4)):
    tag = "  <- frozen" if j == i else ""
    print(f"    idx {j}: threshold={thr[j]:.10f}  val_fpr={fpr[j]:.8f}  val_recall={tpr[j]:.6f}{tag}")
nxt = i + 1
print(f"\n  next LOWER available threshold: {thr[nxt]:.10f}")
print(f"  its validation FPR: {fpr[nxt]:.8f} = {100*fpr[nxt]:.4f}%")
print(f"  exceeds the 1% cap: {fpr[nxt] > 0.01}")
print(f"  jump factor from the frozen point: {fpr[nxt]/fpr[i]:.1f}x")
