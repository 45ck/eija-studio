"""The full tier fetches its pinned Java tools itself, and never uses a jar whose digest differs from the pin."""
from __future__ import annotations

import hashlib
import io
import json
import urllib.error

from quality.tools import pinned_jars


def _pin(monkeypatch, tmp_path, body: bytes):
    path = tmp_path / "tool.jar"
    monkeypatch.setitem(pinned_jars.JARS, "tool", lambda: ("https://example.invalid/tool.jar",
                                                           hashlib.sha256(body).hexdigest(), path))
    return path


def test_a_verified_jar_already_present_is_not_downloaded_again(monkeypatch, tmp_path):
    path = _pin(monkeypatch, tmp_path, b"jar")
    path.write_bytes(b"jar")
    monkeypatch.setattr(pinned_jars.urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(AssertionError("fetched")))
    assert pinned_jars.ensure("tool") is None


def test_a_download_is_verified_then_kept(monkeypatch, tmp_path):
    path = _pin(monkeypatch, tmp_path, b"jar")
    monkeypatch.setattr(pinned_jars.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"jar"))
    assert pinned_jars.ensure("tool") is None and path.read_bytes() == b"jar"
    assert pinned_jars.main(["tool"]) == 0


def test_a_tampered_download_is_discarded_and_reported_not_run(monkeypatch, tmp_path, capsys):
    path = _pin(monkeypatch, tmp_path, b"jar")
    path.write_bytes(b"old and wrong")
    monkeypatch.setattr(pinned_jars.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"evil"))
    assert "does not match its pinned sha256" in pinned_jars.ensure("tool")
    assert path.read_bytes() == b"old and wrong" and not list(tmp_path.glob("*.part"))  # never replaced by the bad bytes
    assert pinned_jars.main(["tool"]) == 3 and capsys.readouterr().out.startswith("NOT_RUN: ")


def test_no_network_is_not_run_not_a_crash(monkeypatch, tmp_path):
    _pin(monkeypatch, tmp_path, b"jar")

    def offline(*args, **kwargs):
        raise urllib.error.URLError("offline")
    monkeypatch.setattr(pinned_jars.urllib.request, "urlopen", offline)
    assert pinned_jars.ensure("tool") == "could not download tool.jar (URLError)"
    assert pinned_jars.main(["tool", "nope"]) == 2  # an unknown tool name is a usage error


def test_the_pins_are_the_ones_the_gates_check():
    url, sha, path = pinned_jars.JARS["alloy"]()
    lock = json.loads((pinned_jars.ROOT / "graph" / "formal" / "TOOLS.lock").read_text(encoding="utf-8"))["alloy"]
    # Read, not imported: under xdist a top-level `graph` can resolve to tests/graph instead of the repository's graph/.
    run_alloy = (pinned_jars.ROOT / "graph" / "formal" / "run_alloy.py").read_text(encoding="utf-8")
    assert (url, sha) == (lock["url"], lock["sha256"]) and f'ROOT / ".tmp" / "tools" / "{path.name}"' in run_alloy
    url, sha, path = pinned_jars.JARS["plantuml"]()
    assert url.endswith("/" + path.name) and len(sha) == 64 and path.parent == pinned_jars.TOOLS
