"""Make the M1 package importable regardless of the working directory."""

import sys
from pathlib import Path

M1_ROOT = Path(__file__).resolve().parents[1]
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))
