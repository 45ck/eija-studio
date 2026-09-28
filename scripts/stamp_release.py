#!/usr/bin/env python3
"""MAINTAINER ONLY: identify a reviewed candidate build; this is NOT a source-review proof.
Never call this automatically at startup, installation, or from an agent workflow.
"""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eija_studio.adapters.identity import implementation_files
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--acknowledge-self-authored-fixture", action="store_true", required=True)
parser.parse_args()
path = ROOT / "src/eija_studio/resources/trusted_build.json"
path.write_text(json.dumps({"trust_level": "self-authored-release-fixture-not-independent-review", "files": implementation_files()}, indent=2) + "\n")
print(path)
