"""The registry gate must FAIL cleanly (a message, never a traceback) on a bad manifest, and check the video hash."""
import hashlib
import json
import platform

import pytest

from manifest_helpers import put_manifest

from demos.manifest import (
    build_manifest,
    load_manifest,
    scenario_sha256,
    stale_warnings,
    video_relpath,
    write_manifest,
)
from demos.scenarios.registry import SCENARIOS, Scenario, check_consistency, manifest_warnings

KEY = "assurance_loop"
PARTIAL = Scenario(KEY, "x", "recorded-partial", (), "story")


def _problems(root):
    return check_consistency((PARTIAL,), root)


def test_valid_manifest_passes(tmp_path):
    put_manifest(tmp_path, KEY, ["Act 4 skipped"])
    assert _problems(tmp_path) == []


@pytest.mark.parametrize("raw", [b"{not json", b"", b"\xff\xfe\x00", b"[]", b"42", b'"text"', b"null"])
def test_malformed_manifest_is_a_fail_line_not_a_traceback(tmp_path, raw):
    put_manifest(tmp_path, KEY, raw=raw)
    problems = _problems(tmp_path)
    assert problems and all(isinstance(p, str) and KEY in p for p in problems)


@pytest.mark.parametrize(
    "name", ["scenario", "mode", "status", "skipped", "video", "video_sha256", "video_bytes", "platform", "scenario_sha256"]
)
def test_every_required_key_is_enforced(tmp_path, name):
    put_manifest(tmp_path, KEY, ["Act 4 skipped"], drop=(name,))
    assert any(f"missing required key '{name}'" in p for p in _problems(tmp_path))


@pytest.mark.parametrize(
    "overrides",
    [
        {"video_bytes": "5"},
        {"video_bytes": True},
        {"skipped": "Act 4"},
        {"skipped": [1]},
        {"video_sha256": "abc"},
        {"scenario_sha256": "G" * 64},
        {"scenario": "other"},
    ],
)
def test_wrong_types_and_values_fail(tmp_path, overrides):
    put_manifest(tmp_path, KEY, **({"skipped": ["Act 4"]} | overrides))
    assert _problems(tmp_path)


def test_video_path_must_be_posix(tmp_path):
    put_manifest(tmp_path, KEY, ["Act 4 skipped"], video="demos\\output\\assurance_loop.webm")
    assert any("posix path" in p for p in _problems(tmp_path))


def test_absent_video_is_fine_in_a_clean_clone(tmp_path):
    put_manifest(tmp_path, KEY, ["Act 4 skipped"])
    assert not (tmp_path / video_relpath(KEY)).exists()
    assert _problems(tmp_path) == []


def test_present_video_must_match_the_manifest_hash(tmp_path):
    put_manifest(tmp_path, KEY, ["Act 4 skipped"])
    video = tmp_path / video_relpath(KEY)
    video.parent.mkdir(parents=True)
    video.write_bytes(b"a different take")
    assert any("does not match the manifest" in p for p in _problems(tmp_path))
    video.write_bytes(b"video")  # conftest's manifest records sha256(b"video")
    assert _problems(tmp_path) == []


def test_build_manifest_is_posix_deterministic_and_complete(tmp_path, monkeypatch):
    # platform.system() runs a WMI query on Windows that can fail under memory pressure; not what is tested here.
    monkeypatch.setattr(platform, "system", lambda: "TestOS")
    monkeypatch.setattr(platform, "release", lambda: "1")
    (tmp_path / "demos" / "scenarios").mkdir(parents=True)
    (tmp_path / "demos" / "scenarios" / f"{KEY}.py").write_bytes(b"line one\r\nline two\r\n")
    video = tmp_path / "some" / "where" / "take.webm"
    video.parent.mkdir(parents=True)
    video.write_bytes(b"frames")
    manifest = build_manifest(KEY, skipped=["Act 4"], video=video, root=tmp_path)
    assert manifest["video"] == "demos/output/assurance_loop.webm"  # posix, and the final name, not the temp take
    assert manifest["video_sha256"] == hashlib.sha256(b"frames").hexdigest()
    assert manifest["video_bytes"] == 6 and manifest["status"] == "PARTIAL"
    assert set(manifest) >= {"scenario_sha256", "platform", "skipped", "mode"}
    assert not any(k in manifest for k in ("commit", "timestamp", "date"))  # commit-independent
    write_manifest(KEY, manifest, tmp_path)
    loaded, problems = load_manifest(KEY, tmp_path)
    assert problems == [] and loaded == json.loads(json.dumps(manifest))


def test_scenario_hash_ignores_line_endings(tmp_path):
    (tmp_path / "demos" / "scenarios").mkdir(parents=True)
    path = tmp_path / "demos" / "scenarios" / f"{KEY}.py"
    path.write_bytes(b"a\nb\n")
    lf = scenario_sha256(KEY, tmp_path)
    path.write_bytes(b"a\r\nb\r\n")
    assert scenario_sha256(KEY, tmp_path) == lf
    path.write_bytes(b"a\nc\n")
    assert scenario_sha256(KEY, tmp_path) != lf


def test_stale_scenario_warns_but_does_not_fail(tmp_path):
    (tmp_path / "demos" / "scenarios").mkdir(parents=True)
    (tmp_path / "demos" / "scenarios" / f"{KEY}.py").write_bytes(b"changed since the take\n")
    put_manifest(tmp_path, KEY, ["Act 4 skipped"])  # scenario_sha256 is a different hash
    assert _problems(tmp_path) == []
    notes = manifest_warnings((PARTIAL,), tmp_path)
    assert len(notes) == 1 and "earlier take" in notes[0]
    loaded, _ = load_manifest(KEY, tmp_path)
    assert loaded is not None and stale_warnings(KEY, loaded, tmp_path) == notes


def test_shipped_manifest_is_valid_and_honest_about_staleness():
    loaded, problems = load_manifest(KEY)
    assert problems == [] and loaded is not None
    assert loaded["skipped"], "the shipped take skipped act 4; the manifest must say so"
    assert any(s.key == KEY for s in SCENARIOS)
