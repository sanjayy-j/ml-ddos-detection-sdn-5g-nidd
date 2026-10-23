"""Phase 3.4 route (a) analysis — is the carrier gain prior estimation?

Adding causal window aggregates lets the Random Forest detect a small
number of records carrying the dominant ambiguous vector, which the
67-feature baseline cannot do at all (they are one identical vector
there). This script tests whether that gain is temporal information or a
block-local label prior.

Every capture block is one attack session, so win{K}_frac_udp and its
siblings approximate a block fingerprint. All carriers lie in blocks 4
and 14, and their label prior differs sharply between them (block 14:
every carrier malicious; block 4: a minority). If the detections
concentrate where the prior is certain, and if precision inside the
mixed block is no better than that block's own prior, the gain is prior
estimation - a soft capture identifier - rather than evidence that
temporal aggregation separates the ambiguous records.

Run from the repository root.
"""

import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "M1-supervised-ml")
from models.random_forest import build_random_forest
from preprocessing.data_loader import load_config_file
from preprocessing.features import build_target
from preprocessing.pipeline import load_processed
from preprocessing.splitting import detect_capture_blocks, make_split
from evaluation.thresholds import PRIMARY_FPR_CAP, select_threshold_at_fpr

K = 50
cfg = load_config_file(f"M1-supervised-ml/config/m1_config_window_k{K}.yaml")
raw = pd.read_csv("data/raw/Combined.csv",
                  usecols=["Unnamed: 0","Offset","Proto","Dur","TotPkts","TotBytes",
                           "State","sTtl","Rate","Cause","Label"], low_memory=False)
base = load_config_file("M1-supervised-ml/config/m1_config.yaml")
y_all = build_target(raw, base).to_numpy()
blocks = detect_capture_blocks(raw, base)
assign = make_split(y_all, blocks, base)
carrier_all = ((raw["Proto"].astype(str).str.lower()=="udp") & (raw["Dur"]==0) &
               (raw["TotPkts"]==1) & (raw["TotBytes"]==42) &
               (raw["State"].astype(str)=="REQ") & (raw["sTtl"]==63) &
               (raw["Rate"]==0) & (raw["Cause"].astype(str)=="Status")).to_numpy()
te = assign == "test"
carrier, blk = carrier_all[te], blocks[te]

data = load_processed(cfg, Path("."))
m = build_random_forest(cfg, max_depth=20, min_samples_leaf=20, max_features="sqrt")
m.fit(data["X"]["train"], data["y"]["train"])
vs = m.predict_proba(data["X"]["val"])[:,1]
thr = float(select_threshold_at_fpr(data["y"]["val"], vs, PRIMARY_FPR_CAP)["threshold"])
ts = m.predict_proba(data["X"]["test"])[:,1]
pred = (ts >= thr).astype(np.int8)
y_te = data["y"]["test"]
assert len(carrier) == len(y_te)

print(f"  K={K}, frozen threshold {thr:.6f}")
print(f"  detected carriers overall: {int(pred[carrier].sum()):,} of {int(carrier.sum()):,}")
print("\n  %6s %12s %12s %12s %14s" % ("block","carriers","malicious","detected","detected mal."))
for b in sorted(set(blk[carrier])):
    s = carrier & (blk == b)
    det = pred[s].astype(bool)
    print("  %6d %12s %12s %12s %14s" % (
        b, f"{int(s.sum()):,}", f"{int(y_te[s].sum()):,}",
        f"{int(det.sum()):,}", f"{int((det & y_te[s].astype(bool)).sum()):,}"))
d = pred[carrier].astype(bool)
b14 = (blk[carrier] == 14)
print(f"\n  share of detected carriers lying in block 14 (100% malicious carriers): "
      f"{100*(d & b14).sum()/max(d.sum(),1):.2f}%")
print(f"  block 14 share of all test carriers: {100*b14.sum()/carrier.sum():.2f}%")
