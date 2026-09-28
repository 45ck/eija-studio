"""Recording manifests: what a committed `demos/recordings/<key>.json` must contain and how it is checked.

The video is a large gitignored binary, so a clean clone has only the manifest. The gate therefore validates
the manifest's shape always, and the video's hash only when the file happens to be present locally.
Nothing here depends on git history: no commit hashes, no timestamps.

What this establishes: the manifest is well formed and (when the file is present) describes that exact
video. What it does NOT establish: that the video shows the current UI. `scenario_sha256` lets a reviewer see
when the script has changed since the take (reported as a warning, never a silent pass).
"""
from __future__ import annotations

import hashlib
import json
import platform
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SHA256 = re.compile(r"[0-9a-f]{64}")
# key -> expected JSON type. `bool` is rejected for ints below (True is an int in Python).
REQUIRED_FIELDS: dict[str, type] = {
    "scenario": str,
    "mode": str,
    "status": str,
    "skipped": list,
    "video": str,
    "video_sha256": str,
    "video_bytes": int,
    "platform": str,
    "scenario_sha256": str,
}
HASH_FIELDS = ("video_sha256", "scenario_sha256")


def manifest_path(key: str, root: Path = ROOT) -> Path:
    return root / "demos" / "recordings" / f"{key}.json"


def video_relpath(key: str) -> str:
    """The manifest's `video` value: always posix, whatever platform recorded it."""
    return f"demos/output/{key}.webm"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scenario_sha256(key: str, root: Path = ROOT) -> str:
    """Hash of the scenario module's source; line endings are normalised so every checkout agrees."""
    source = (root / "demos" / "scenarios" / f"{key}.py").read_bytes().replace(b"\r\n", b"\n")
    return sha256_hex(source)


def build_manifest(
    key: str, *, skipped: list[str], video: Path, root: Path = ROOT, status: str | None = None
) -> dict[str, object]:
    """The manifest for a fresh recording of `key`. Deterministic given the same inputs."""
    data = video.read_bytes()
    return {
        "scenario": key,
        "mode": "record",
        "status": status or ("PARTIAL" if skipped else "PASS"),
        "skipped": list(skipped),
        "video": video_relpath(key),
        "video_sha256": sha256_hex(data),
        "video_bytes": len(data),
        "platform": f"{platform.system()} {platform.release()} / Python {platform.python_version()}",
        "scenario_sha256": scenario_sha256(key, root),
    }


def write_manifest(key: str, manifest: dict[str, object], root: Path = ROOT) -> Path:
    path = manifest_path(key, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return path


def load_manifest(key: str, root: Path = ROOT) -> tuple[dict[str, object] | None, list[str]]:
    """Read and shape-check a manifest. Returns (manifest or None, problems); never raises on bad content."""
    path = manifest_path(key, root)
    try:
        loaded = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, [f"{key}: manifest {path.name} is unreadable or not valid JSON ({error})"]
    if not isinstance(loaded, dict):
        return None, [f"{key}: manifest {path.name} must be a JSON object, not {type(loaded).__name__}"]
    problems = _shape_problems(key, path.name, loaded)
    return (None if problems else loaded), problems


def _shape_problems(key: str, name: str, manifest: dict[str, object]) -> list[str]:
    return _field_problems(key, name, manifest) + _value_problems(key, manifest)


def _field_problems(key: str, name: str, manifest: dict[str, object]) -> list[str]:
    """Every required key is present and has the right JSON type."""
    problems: list[str] = []
    for field_name, expected in REQUIRED_FIELDS.items():
        if field_name not in manifest:
            problems.append(f"{key}: manifest {name} is missing required key {field_name!r}")
            continue
        value = manifest[field_name]
        if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
            problems.append(f"{key}: manifest key {field_name!r} must be {expected.__name__}")
    return problems


def _value_problems(key: str, manifest: dict[str, object]) -> list[str]:
    """Well-typed values must also be sensible: hashes, skipped acts, scenario name, posix video path."""
    problems: list[str] = []
    for field_name in HASH_FIELDS:
        value = manifest.get(field_name)
        if isinstance(value, str) and not _SHA256.fullmatch(value):
            problems.append(f"{key}: manifest key {field_name!r} is not a lowercase sha256 hex digest")
    skipped = manifest.get("skipped")
    if isinstance(skipped, list) and not all(isinstance(item, str) for item in skipped):
        problems.append(f"{key}: manifest key 'skipped' must be a list of strings")
    if manifest.get("scenario") not in (None, key):
        problems.append(f"{key}: manifest names scenario {manifest.get('scenario')!r}")
    if isinstance(manifest.get("video"), str) and manifest["video"] != video_relpath(key):
        problems.append(f"{key}: manifest 'video' must be the posix path {video_relpath(key)!r}")
    return problems


def video_problems(key: str, manifest: dict[str, object], root: Path = ROOT) -> list[str]:
    """If the gitignored video is present locally its hash must match; absent is fine (clean clone)."""
    video = root / video_relpath(key)
    if not video.is_file():
        return []
    actual = sha256_hex(video.read_bytes())
    if actual != manifest["video_sha256"]:
        return [f"{key}: {video_relpath(key)} sha256 {actual[:12]}... does not match the manifest "
                f"({str(manifest['video_sha256'])[:12]}...): re-record or restore the recorded file"]
    return []


def stale_warnings(key: str, manifest: dict[str, object], root: Path = ROOT) -> list[str]:
    """Non-failing notes: the script changed since the take, so the video may not show the current flow."""
    try:
        current = scenario_sha256(key, root)
    except OSError:
        return []
    if current != manifest["scenario_sha256"]:
        return [f"{key}: scenario source changed since the recording (scenario_sha256 differs); "
                "the video shows an earlier take. Re-record before treating it as current."]
    return []
