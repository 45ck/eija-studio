"""Shared helper for the demo catalogue tests: put a manifest where the gate expects it under a temp root.

A plain module, not a conftest: the repo-level `tests/conftest.py` is imported by name elsewhere."""
import hashlib
import json
from pathlib import Path

from demos.manifest import manifest_path, video_relpath

SHA = hashlib.sha256(b"video").hexdigest()


def put_manifest(
    root: Path,
    key: str,
    skipped: list[str] | None = None,
    *,
    raw: bytes | None = None,
    drop: tuple[str, ...] = (),
    **overrides: object,
) -> Path:
    """Write a valid manifest (PARTIAL when `skipped` is non-empty) under `root`, apply `overrides`, remove the
    keys in `drop`, or write `raw` bytes verbatim to model a malformed file. Returns its path."""
    path = manifest_path(key, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if raw is not None:
        path.write_bytes(raw)
        return path
    manifest: dict[str, object] = {
        "scenario": key,
        "mode": "record",
        "status": "PARTIAL" if skipped else "PASS",
        "skipped": skipped or [],
        "video": video_relpath(key),
        "video_sha256": SHA,
        "video_bytes": 5,
        "platform": "test",
        "scenario_sha256": SHA,
    }
    manifest.update(overrides)
    for name in drop:
        del manifest[name]
    path.write_bytes(json.dumps(manifest).encode())
    return path
