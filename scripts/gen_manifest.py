#!/usr/bin/env python3
"""Regenerate MANIFEST.json: sha256 and size of every shipped file. Byte integrity only; no network access.

    python scripts/gen_manifest.py           # rewrite MANIFEST.json
    python scripts/gen_manifest.py --check   # exit 1 if the committed manifest is not what a rewrite would produce

The scope is explicit so a reviewer can read it: the fixed file list below plus every git-tracked file under TREES
(the package that goes into the wheel, the JSON contracts and the examples). Generated evidence, junk and the
manifest itself are never listed. `scripts/check_manifest.py` verifies the result against the working tree. This
script never touches `src/eija_studio/resources/trusted_build.json` (owner-only, see `scripts/stamp_release.py`);
it only hashes that file's current bytes.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"
RELEASE = "0.2.0"
FIXED_FILES = (
    ".agents/skills/eija-studio/SKILL.md", ".github/workflows/test.yml", ".gitignore", "AGENTS.md", "CHANGELOG.md",
    "NOTICE.md", "README.md", "docs/OPERATIONS.md", "docs/SECURITY_AND_TRUST.md", "docs/TECHNICAL_LEAD_REVIEW.md",
    "docs/architecture/ARCHITECTURE.md", "docs/verification/ACCEPTANCE_MATRIX.csv", "docs/verification/VERIFICATION.md",
    "evidence/browser-component-report.json", "evidence/browser-network-report.json", "evidence/coverage.txt",
    "evidence/environment.json", "evidence/http-smoke-report.json", "evidence/live-provider-status.json",
    "evidence/release-report.json", "evidence/wheel-smoke-report.json", "provenance/PROVENANCE.md",
    "provenance/source-inputs.json", "pyproject.toml", "requirements-tested.txt", "scripts/browser_component_smoke.py",
    "scripts/browser_smoke.py", "scripts/check_manifest.py", "scripts/gen_manifest.py", "scripts/http_smoke.py",
    "scripts/stamp_release.py", "scripts/verify_release.py", "scripts/wheel_smoke.py", "start.ps1", "start.sh",
)
TREES = ("src/eija_studio", "contracts", "examples")
SKIP_PARTS = {"__pycache__"}


def tracked(tree: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "--", tree], cwd=ROOT, capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8").split("\0") if p and not SKIP_PARTS & set(p.split("/"))]


def scope() -> list[str]:
    paths = set(FIXED_FILES)
    for tree in TREES:
        paths.update(tracked(tree))
    return sorted(paths)


def build() -> dict:
    files = []
    for rel in scope():
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"gen_manifest: {rel} is in scope but is not a file; fix FIXED_FILES or restore it")
        data = path.read_bytes()
        files.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return {
        "release": RELEASE,
        "algorithm": "sha256",
        "scope": "Shipped files excluding this manifest itself; byte integrity, not author identity or correctness",
        "files": files,
    }


def main(argv: list[str]) -> int:
    text = json.dumps(build(), indent=2) + "\n"
    if "--check" in argv:
        current = MANIFEST.read_text(encoding="utf-8") if MANIFEST.is_file() else ""
        if current != text:
            print("MANIFEST.json is stale: run `python scripts/gen_manifest.py`")
            return 1
        print("MANIFEST.json is current")
        return 0
    MANIFEST.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote MANIFEST.json ({len(json.loads(text)['files'])} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
