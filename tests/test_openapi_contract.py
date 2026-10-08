"""The committed API contract is a snapshot of FastAPI's generator, never a handwritten schema.

Regenerate with create_app(build_studio(disposable_workspace), synthetic_token).openapi(),
serialised as indented JSON with a final newline. No server, provider call or owner action is needed.
"""
from __future__ import annotations

import json
from pathlib import Path

from eija_studio.interfaces.http import create_app


def test_committed_openapi_matches_the_current_routes(studio):
    path = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"
    generated = create_app(studio, "synthetic-openapi-contract-test").openapi()
    assert json.loads(path.read_text(encoding="utf-8")) == generated
