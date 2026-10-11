"""Exact generated-build identity. Hashes bind content; they grant no approval.

The generated subject file is a provenance envelope, excluded from its own
payload hash. All executable files and model contracts remain in that hash.
This module reads only the supplied snapshot, never files beside a pack.
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from eija_studio.domain.data import DataModel
from eija_studio.domain.models import DomainError, Workflow, fingerprint
from eija_studio.domain.pack import Pack
from eija_studio.domain.screens import Screens

FORMAT = "eija.build-subject.v1"
SUBJECT_FILE = "app/build-subject.json"


def snapshot_contracts(files: dict[str, str]) -> tuple[Pack, Workflow, DataModel | None, Screens]:
    """Parse the very contracts the generated application will load."""
    pack = Pack.model_validate_json(files["app/pack.json"])
    model = Workflow.model_validate_json(files["app/model.json"])
    screens = Screens.model_validate_json(files["app/screens.json"])
    data = DataModel.model_validate_json(files["app/data.json"]) if "app/data.json" in files else None
    if model.id != pack.id or screens.id != pack.id or (data is not None and data.id != pack.id):
        raise DomainError("BUILD_SNAPSHOT_MISMATCH", "Generated contracts do not belong to the same pack")
    return pack, model, data, screens


def build_subject(files: dict[str, str], *, implementation_digest: str,
                  template_paths: Iterable[str]) -> dict[str, Any]:
    """Bind model, contracts, template bytes and measured implementation to one payload."""
    pack, model, data, screens = snapshot_contracts(files)
    payload = {name: content for name, content in files.items() if name != SUBJECT_FILE}
    paths = sorted(set(template_paths))
    subject = {"format": FORMAT, "model_hash": model.semantic_hash, "workflow_digest": fingerprint(model),
               "pack_digest": pack.digest, "data_digest": data.digest if data else None,
               "screens_digest": screens.digest, "templates_digest": fingerprint({p: payload[p] for p in paths}),
               "template_paths": paths, "implementation_digest": implementation_digest,
               "payload_paths": sorted(payload), "generated_files_hash": fingerprint(payload)}
    return subject | {"digest": fingerprint(subject)}


def checked_build_subject(files: dict[str, str], *, implementation_digest: str | None = None,
                          expected_subject: dict[str, Any] | None = None) -> dict[str, Any]:
    """Check archived identity, optionally binding it to the installed runtime and prior snapshot."""
    try:
        supplied = json.loads(files[SUBJECT_FILE])
        expected = build_subject(files, implementation_digest=supplied["implementation_digest"],
                                 template_paths=supplied["template_paths"])
    except (KeyError, TypeError, ValueError) as error:
        raise DomainError("BUILD_SUBJECT_INVALID", "Generated build identity is missing or invalid") from error
    if supplied != expected:
        raise DomainError("BUILD_SUBJECT_MISMATCH", "Generated files differ from their build identity")
    if implementation_digest is not None and implementation_digest != expected["implementation_digest"]:
        raise DomainError("BUILD_IMPLEMENTATION_MISMATCH",
                          "BUILD_IMPLEMENTATION_MISMATCH: installed implementation differs from this build; rebuild before running")
    if expected_subject is not None and expected != expected_subject:
        raise DomainError("BUILD_SUBJECT_CHANGED", "Build identity changed during the operation; rebuild and check again")
    return expected
