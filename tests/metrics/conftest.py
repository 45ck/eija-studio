"""The metrics lane's tooling lives in quality/ (never shipped); make it importable for its tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
