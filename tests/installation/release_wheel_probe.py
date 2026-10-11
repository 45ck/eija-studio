"""Strict installed release oracle, invoked only by scripts/wheel_smoke.py."""
import json
from pathlib import Path
import subprocess
import sys

scratch = Path(sys.argv[2])


def run(arguments):
    result = subprocess.run([sys.executable, "-I", "-m", "eija_studio", *arguments], cwd=scratch,  # noqa: S603 - fixed CLI fixture arguments, no shell
                            capture_output=True, text=True, encoding="utf-8", check=False, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


doctor = json.loads(run(["doctor", "--provider", "offline"]))
assert doctor["release_fixture_matches"] is True
run(["demo", "--provider", "offline", "--out", str(scratch / "demo.json")])
export = json.loads((scratch / "demo.json").read_text(encoding="utf-8"))
assert export["payload"]["packet"]["eligible"]
assert export["payload"]["case"]["decision"] is None
run(["check-export", str(scratch / "demo.json")])
run(["compile", str(scratch / "candidate.json"), "--provider", "offline", "--out", str(scratch / "compiled"), "--verify"])
compiled = json.loads((scratch / "compiled/compiled.json").read_text(encoding="utf-8"))
assert not compiled["policy_errors"]
assert len(compiled["receipt"]["artifact"]["cells"]) == 125
sys.stdout.write(json.dumps({"checks": ["installed release source fixture matches", "verified demo remains unapproved",
                              "export integrity", "compiler creates actual 125-cell runtime receipt"],
                  "source_review": "MATCHES_RELEASE_FIXTURE", "owner_approval_or_baseline_apply": "NOT_RUN"}) + "\n")
