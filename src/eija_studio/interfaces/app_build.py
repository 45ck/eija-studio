"""`eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from hashlib import sha256
from importlib.resources import files as resource_files
from pathlib import Path
from typing import Any, Callable

from eija_studio import __version__
from eija_studio.application.appgen import generate
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack

MANIFEST = "BUILD.json"
TEMPLATES = {  # resource template -> path in the generated app
    "init.py.tmpl": "app/__init__.py",
    "service.py.tmpl": "app/service.py",
    "server.py.tmpl": "app/server.py",
    "web/index.html.tmpl": "app/web/index.html",
    "web/app.js.tmpl": "app/web/app.js",
    "web/app.css.tmpl": "app/web/app.css",
    "run.py.tmpl": "run.py",
    "test_conformance.py.tmpl": "tests/test_conformance.py",
}
TEST_TIMEOUT_S = 600


def add_parser(subs) -> None:
    build = subs.add_parser("build", help="Generate a runnable app from a model and check it against the kernel")
    build.add_argument("--pack", type=Path, help="Domain pack directory or JSON file (defaults to EIJA_PACK or packs/default.json)")
    build.add_argument("--workflow", type=Path, help="Build this workflow JSON instead of the pack's own model")
    build.add_argument("--out", type=Path, required=True, help="Output directory: new, empty, or a previous build")
    build.add_argument("--no-test", action="store_true", help="Skip the conformance run (reported as NOT_RUN)")


def app_files(pack, model: Workflow) -> tuple[dict[str, str], dict]:
    generated, manifest = generate(pack, model)
    root = resource_files("eija_studio.resources").joinpath("appgen")
    static = {target: root.joinpath(source).read_text(encoding="utf-8") for source, target in TEMPLATES.items()}
    return static | {"tests/__init__.py": ""} | generated, manifest


def _previous(out: Path) -> list[str]:
    """Files a previous build wrote. Anything else in a non-empty directory means it is not ours to overwrite."""
    if not out.exists() or not any(out.iterdir()):
        return []
    try:
        listed = json.loads((out / MANIFEST).read_text(encoding="utf-8"))["files"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise DomainError("OUTPUT_EXISTS", "The output directory is not empty and is not a previous build") from exc
    return [p for p in listed if isinstance(p, str) and ".." not in Path(p).parts and not Path(p).is_absolute()]


def write(out: Path, files: dict[str, str]) -> dict[str, str]:
    for stale in _previous(out):
        (out / stale).unlink(missing_ok=True)
    hashes = {}
    for relative, text in sorted(files.items()):
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = text.encode("utf-8")
        target.write_bytes(data)
        hashes[relative] = sha256(data).hexdigest()
    return hashes


def conformance(out: Path) -> dict:
    """Run the generated tests as a separate process, exactly as a user of the app would."""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
    try:
        run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], cwd=out, env=env,
                             capture_output=True, text=True, timeout=TEST_TIMEOUT_S, check=False)
    except subprocess.TimeoutExpired:
        return {"status": "FAIL", "detail": f"timed out after {TEST_TIMEOUT_S} s"}
    tail = (run.stderr or run.stdout).strip().splitlines()[-3:]
    return {"status": "PASS" if run.returncode == 0 else "FAIL", "detail": " | ".join(tail)}


def build(args, pack: Pack, identity_of: Callable[[Pack], dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    """Write, test and record one build. Returns the exit code and a summary for the caller to print."""
    model = Workflow.model_validate_json(args.workflow.read_text(encoding="utf-8")) if args.workflow else pack.model
    files, manifest = app_files(pack, model)
    out = args.out.resolve()
    hashes = write(out, files)
    result = conformance(out) if not args.no_test else {"status": "NOT_RUN", "detail": "--no-test"}
    identity = identity_of(pack)
    manifest |= {"generator": f"eija-studio {__version__}", "files": hashes, "conformance": result,
                 "kernel_source_review": "RELEASE_FIXTURE_MATCH" if identity["trusted_fixture"] else "SOURCE_REVIEW_REQUIRED"}
    (out / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {"app": str(out), "run": f"python {out / 'run.py'}", "conformance": result["status"],
               "cases": manifest["oracle"]["cases"], "model": manifest["model_semantic_hash"][:12],
               "kernel_source_review": manifest["kernel_source_review"]}
    return 2 if result["status"] == "FAIL" else 0, summary
