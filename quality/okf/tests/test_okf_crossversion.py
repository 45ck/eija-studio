"""The committed source hashes must reproduce under every CPython this machine has (3.11, 3.12, 3.13).

A missing interpreter is reported as NOT_RUN (a skip with the reason), never as a pass. Extra interpreters
are found on PATH (``python3.X``), through the Windows ``py`` launcher, or listed in ``EIJA_OKF_PYTHONS``
(paths separated by ``os.pathsep``).
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CROSSCHECK = ROOT / "quality" / "okf" / "crosscheck.py"
WANTED = ("3.11", "3.12", "3.13")


def _version_of(python: str) -> str | None:
    try:
        out = subprocess.run([python, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _candidates() -> list[str]:
    found = [sys.executable, *filter(None, os.environ.get("EIJA_OKF_PYTHONS", "").split(os.pathsep))]
    found += [path for minor in WANTED if (path := shutil.which(f"python{minor}"))]
    if os.name == "nt" and shutil.which("py"):
        listing = subprocess.run(["py", "-0p"], capture_output=True, text=True, timeout=60).stdout
        found += [line.split(None, 2)[-1].strip() for line in listing.splitlines() if line.strip().lower().endswith("python.exe")]
    return [p for p in dict.fromkeys(found) if Path(p).is_file()]


def _interpreters() -> dict[str, str]:
    by_version: dict[str, str] = {}
    for python in _candidates():
        version = _version_of(python)
        if version in WANTED:
            by_version.setdefault(version, python)
    return by_version


@pytest.fixture(scope="module")
def interpreters() -> dict[str, str]:
    return _interpreters()


@pytest.mark.parametrize("version", WANTED)
def test_committed_hashes_reproduce_under_this_python(version, interpreters):
    if version not in interpreters:
        pytest.skip(f"NOT_RUN: no CPython {version} found (set EIJA_OKF_PYTHONS or install it); hash stability there is unverified")
    done = subprocess.run([interpreters[version], str(CROSSCHECK), "--root", str(ROOT)], capture_output=True, text=True, timeout=300)
    report = json.loads(done.stdout)
    assert report["python"].startswith(version)
    assert report["checked"] > 150
    assert report["mismatches"] == [] and done.returncode == 0


def test_crosscheck_detects_a_drifted_hash(tmp_path):
    """Negative control: a wrong recorded hash must be reported, so a silent 'checked 0 / passed' cannot happen."""
    root = tmp_path / "repo"
    (root / "okf").mkdir(parents=True)
    (root / "mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    page = ("---\ntype: Function\nsources:\n- resource: repo://mod.py#f\n  title: mod.py\n  hash_method: ast-v1\n  sha256: " + "0" * 64 + "\n---\nbody\n")
    (root / "okf" / "f.md").write_text(page, encoding="utf-8")
    done = subprocess.run([sys.executable, str(CROSSCHECK), "--root", str(root)], capture_output=True, text=True, timeout=60)
    report = json.loads(done.stdout)
    assert done.returncode == 1 and report["checked"] == 1 and len(report["mismatches"]) == 1
    empty = tmp_path / "empty"
    (empty / "okf").mkdir(parents=True)
    assert subprocess.run([sys.executable, str(CROSSCHECK), "--root", str(empty)], capture_output=True, text=True, timeout=60).returncode == 1
