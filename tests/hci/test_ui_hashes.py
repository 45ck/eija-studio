"""The HCI UI identity covers recursive shipped bytes, without reading outside WEB."""

import hashlib
import json
from pathlib import Path

import pytest

from quality.hci import journey, report


def _web(tmp_path, monkeypatch, assets):
    web = tmp_path / "web"
    for name, content in assets.items():
        path = web / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    monkeypatch.setattr(journey, "WEB", web)
    return web


def test_ui_hashes_cover_nested_assets_with_sorted_relative_keys(tmp_path, monkeypatch):
    assets = {
        "vendor/z.js": b"vendor-z\r\n",
        "app.js": b"application\n",
        "vendor/app.js": b"distinct vendor with the same basename\n",
        "vendor/deep/LICENSE.txt": b"license\n",
        "vendor/deep/asset.VENDOR.json": b'{"version": 1}\n',
    }
    web = _web(tmp_path, monkeypatch, assets)
    (web / "empty-directory").mkdir()
    (tmp_path / "outside.js").write_bytes(b"not a shipped asset")

    actual = journey.ui_hashes()
    assert list(actual) == sorted(assets)
    assert actual == {name: hashlib.sha256(content).hexdigest() for name, content in assets.items()}
    assert actual == journey.ui_hashes()
    assert actual["app.js"] != actual["vendor/app.js"]


def test_nested_asset_addition_and_removal_change_the_identity(tmp_path, monkeypatch):
    web = _web(tmp_path, monkeypatch, {"app.js": b"stable"})
    before = journey.ui_hashes()
    added = web / "vendor" / "deep" / "diagram.js"
    added.parent.mkdir(parents=True)
    added.write_bytes(b"new dependency")
    after = journey.ui_hashes()
    assert after != before
    assert set(after) - set(before) == {"vendor/deep/diagram.js"}
    assert after["app.js"] == before["app.js"]
    added.unlink()
    assert journey.ui_hashes() == before


def test_resolved_external_asset_is_never_read(tmp_path, monkeypatch):
    web = _web(tmp_path, monkeypatch, {"app.js": b"safe", "vendor/escaped.js": b"link fixture"})
    escaped = web / "vendor" / "escaped.js"
    outside = tmp_path / "private.js"
    outside.write_bytes(b"outside scope")
    resolve = Path.resolve
    read_bytes = Path.read_bytes
    reads = []

    def resolved(path, *args, **kwargs):
        # Model a symlink/junction target deterministically, without Windows link privileges.
        return outside if path == escaped else resolve(path, *args, **kwargs)

    def guarded_read(path):
        assert path not in {escaped, outside}, "an asset resolving outside WEB must not be read"
        reads.append(path)
        return read_bytes(path)

    monkeypatch.setattr(Path, "resolve", resolved)
    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    with pytest.raises(ValueError, match=r"^UI asset resolves outside WEB: vendor/escaped\.js$"):
        journey.ui_hashes()
    assert reads == [web / "app.js"]


def test_nested_vendor_mutation_invalidates_strict_evidence(tmp_path, monkeypatch):
    web = _web(tmp_path, monkeypatch, {"app.js": b"stable", "vendor/diagram.js": b"before"})
    raw = json.loads(report.TRACE.read_text(encoding="utf-8"))
    raw["environment"]["ui_sha256"] = journey.ui_hashes()
    snapshot = report.build_report(raw)
    paths = {
        "trace_path": tmp_path / "trace.snapshot.json",
        "snapshot_path": tmp_path / "report.snapshot.json",
        "report_path": tmp_path / "REPORT.md",
    }
    paths["trace_path"].write_bytes(report.dump_trace(raw).encode("utf-8"))
    paths["snapshot_path"].write_bytes(report.dumps(snapshot).encode("utf-8"))
    paths["report_path"].write_bytes(report.render_markdown(snapshot).encode("utf-8"))
    ok, message = report.check_docs(strict=True, **paths)
    assert ok, message

    (web / "vendor" / "diagram.js").write_bytes(b"after")
    assert journey.ui_hashes()["app.js"] == raw["environment"]["ui_sha256"]["app.js"]
    ok, message = report.check_docs(strict=True, **paths)
    assert not ok and message.startswith("STALE:"), message
    ok, message = report.check_docs(**paths)
    assert ok and "informational" in message, message
