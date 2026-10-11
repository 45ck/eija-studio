"""Print engineering observations; optional output goes only to the requested report path."""
import argparse
import json
from pathlib import Path

from .run import run_activation_checks

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", type=Path)
arguments = parser.parse_args()
report = run_activation_checks()
content = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
if arguments.out is not None:
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(content, encoding="utf-8", newline="\n")
print(json.dumps({"status": report["status"], "observed_behavior": report["observed_behavior"]["status"],
                  "checks": report["observed_behavior"]["passed"], "total": report["observed_behavior"]["total"],
                  "mutations_detected": report["negative_controls"]["detected"],
                  "mutations_total": report["negative_controls"]["total"],
                  "source_review": report["source"]["review_status"]}))
raise SystemExit(0 if report["status"] == "PASS" else 1)
