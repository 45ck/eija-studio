"""Measured release identity, not a proof of correctness or author authenticity."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json, platform
from importlib.metadata import version
from eija_studio.domain.models import Workflow, fingerprint

PACKAGE = Path(__file__).resolve().parents[1]


def implementation_files() -> dict[str, str]:
    paths = list(PACKAGE.rglob("*.py")) + list((PACKAGE / "resources" / "web").rglob("*"))
    return {str(p.relative_to(PACKAGE)).replace("\\", "/"): sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file() and "__pycache__" not in p.parts}


def identity() -> dict:
    files = implementation_files()
    manifest = PACKAGE / "resources" / "trusted_build.json"
    try:
        trusted = json.loads(manifest.read_text())["files"]
    except (OSError, ValueError, KeyError):
        trusted = {}
    return {"implementation": fingerprint(files), "policy": files["domain/policy.py"],
            "harness": files["application/verifier.py"], "trusted_fixture": files == trusted,
            "environment": fingerprint({"python": platform.python_version(), "os": platform.system(),
                "dependencies": {x: version(x) for x in ("pydantic", "fastapi", "uvicorn", "httpx")}})}


def subject(model: Workflow, layout: dict) -> dict:
    current = identity()
    return {**{k: current[k] for k in ("implementation", "policy", "harness", "environment")},
            "semantic": model.semantic_hash, "presentation": fingerprint(layout)}
