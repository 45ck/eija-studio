"""The visual surface: HTTP endpoint, CSP boundary, vendored renderer integrity, CLI and HTML output."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.diagram_catalog import demo_pair, html_panels
from eija_studio.domain.models import DomainError
from eija_studio.interfaces import cli
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.render_html import html_page, mermaid_js

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src/eija_studio/resources/web"
HEADERS = {"Authorization": "Bearer unit-test-token", "Origin": "http://127.0.0.1:8765"}


def client(studio):
    return TestClient(create_app(studio, "unit-test-token"), base_url="http://127.0.0.1:8765")


def directives(csp: str) -> dict[str, str]:
    return {part.split()[0]: " ".join(part.split()[1:]) for part in csp.split(";") if part.strip()}


def test_diagrams_endpoint_is_guarded_and_generated_from_the_case(studio, selected):
    with client(studio) as c:
        url = f"/api/cases/{selected['id']}/diagrams"
        assert c.get(url).status_code == 401
        assert c.get(url, headers=HEADERS | {"Host": "attacker.invalid"}).status_code == 403
        body = c.get(url, headers=HEADERS).json()
        assert body["format"] == "mermaid" and body["views"]["diff"].splitlines()[2] == "stateDiagram-v2"
        candidate = selected["candidate"]["states"]
        assert "Recommended" in candidate and "state \"added by the candidate (+)\" as legend_added" in body["views"]["diff"]
        assert body["sources"]["candidate"] and body["impact"]["complete"]
        assert set(body["views"]["sequences"]) == {"Approve", "Recommend", "Reject", "Revise", "Submit"}
        assert c.get(url + "?format=dot", headers=HEADERS).json()["unsupported"] == ["class", "sequence"]
        assert c.get(url + "?format=svg", headers=HEADERS).status_code == 422
        assert c.get("/api/cases/nope/diagrams", headers=HEADERS).status_code == 404
        assert c.post(url, headers=HEADERS, json={}).status_code == 405


def test_case_without_candidate_has_no_diff_but_shows_the_baseline(studio):
    case = studio.create("Let teachers sign off excursions.")
    with client(studio) as c:
        body = c.get(f"/api/cases/{case['id']}/diagrams", headers=HEADERS).json()
    assert body["views"]["diff"] is None and body["views"]["state_after"] is None and "Draft" in body["views"]["state_before"]


def test_studio_page_csp_stays_strict_and_only_the_frame_relaxes_styles(studio):
    with client(studio) as c:
        page = directives(c.get("/").headers["content-security-policy"])
        assert page["script-src"] == "'self'" and page["style-src"] == "'self'" and page["default-src"] == "'none'"
        assert page["frame-src"] == "'self'" and page["frame-ancestors"] == "'none'" and "unsafe" not in " ".join(page.values())
        assert c.get("/").headers["x-frame-options"] == "DENY"
        frame = c.get("/visual-frame")
        rules = directives(frame.headers["content-security-policy"])
        assert rules["script-src"] == "'self'" and rules["style-src"] == "'self' 'unsafe-inline'"
        assert rules["connect-src"] == "'none'" and rules["sandbox"] == "allow-scripts" and rules["frame-ancestors"] == "'self'"
        assert "unsafe-eval" not in frame.headers["content-security-policy"] and "unsafe-inline" not in rules["script-src"]
        assert frame.headers["x-frame-options"] == "SAMEORIGIN"
        vendored = c.get("/assets/vendor/mermaid.min.js")
        assert vendored.status_code == 200 and vendored.headers["cache-control"] == "private, max-age=3600"
        assert c.get("/assets/app.js").headers["cache-control"] == "no-store"  # everything else stays uncached
        assert c.get("/assets/vendor/nope.js").headers["cache-control"] == "no-store"
        assert c.get("/assets/visual-frame.js").status_code == 200
        for hidden in ("/assets/vendor/mermaid.LICENSE.txt", "/assets/vendor/VENDOR.json", "/assets/mermaid.min.js"):
            assert c.get(hidden).status_code == 404, hidden


def test_frame_never_gets_the_session_token_or_api_access():
    frame_js = (WEB / "visual-frame.js").read_text(encoding="utf-8")
    assert "fetch(" not in frame_js and "sessionStorage" not in frame_js and "Authorization" not in frame_js
    assert "event.source !== parent" in frame_js and "eval(" not in frame_js and "innerHTML" not in frame_js
    app_js = (WEB / "app.js").read_text(encoding="utf-8")
    assert "e.source!==frame.contentWindow" in app_js and 'sandbox="allow-scripts"' in (WEB / "index.html").read_text(encoding="utf-8")
    assert "allow-same-origin" not in (WEB / "index.html").read_text(encoding="utf-8") + frame_js


def test_vendored_mermaid_matches_its_recorded_pin():
    record = json.loads((WEB / "vendor/mermaid.VENDOR.json").read_text(encoding="utf-8"))
    assert record["package"] == "mermaid" and re.fullmatch(r"\d+\.\d+\.\d+", record["version"]) and record["license"] == "MIT"
    assert hashlib.sha256((WEB / "vendor/mermaid.min.js").read_bytes()).hexdigest() == record["files"]["mermaid.min.js"]["sha256"]
    assert hashlib.sha256((WEB / "vendor/mermaid.LICENSE.txt").read_bytes()).hexdigest() == record["files"]["mermaid.LICENSE.txt"]["sha256"]
    assert f'"{record["version"]}"' in (WEB / "vendor/mermaid.min.js").read_text(encoding="utf-8")  # the bytes are that release


def test_no_cdn_or_remote_script_anywhere_in_the_web_root():
    for name in ("index.html", "visual-frame.html", "app.js", "visual-frame.js"):
        text = (WEB / name).read_text(encoding="utf-8")
        assert not re.search(r"(src|href)=[\"']https?://", text) and "cdn." not in text, name


def test_html_page_is_self_contained_and_escapes_text():
    page = html_page("t <x>", [("h", "n", "graph LR\n  A[\"</script><img src=x>\"]")], renderer="/*stub*/")
    assert "</script><img" not in page and "&lt;/script&gt;" in page and "t &lt;x&gt;" in page
    assert directives(re.search(r'Content-Security-Policy" content="([^"]+)"', page).group(1))["default-src"] == "'none'"
    assert not re.search(r"(src|href)=[\"']https?://", page)
    assert page == html_page("t <x>", [("h", "n", "graph LR\n  A[\"</script><img src=x>\"]")], renderer="/*stub*/")
    assert "</script" not in mermaid_js().lower()


def run_cli(capsysbinary, *argv):
    code = cli.main(list(argv))
    out = capsysbinary.readouterr().out
    return code, out


def test_cli_render_model_file_every_view_and_format(capsysbinary):
    model = str(ROOT / "examples/excursion-candidate.json")
    code, out = run_cli(capsysbinary, "render", "--workflow", model, "--view", "diff", "--format", "mermaid")
    text = out.decode("utf-8")
    assert code == 0 and "stateDiagram-v2" in text and "+ Recommend · Teacher · assigned" in text and b"\r" not in out
    code, out = run_cli(capsysbinary, "render", "--workflow", model, "--view", "impact", "--format", "dot")
    assert code == 0 and out.decode().count("digraph") == 1
    code, out = run_cli(capsysbinary, "render", "--workflow", model, "--view", "sequence", "--action", "Recommend", "--format", "plantuml")
    assert code == 0 and out.startswith(b"@startuml") and b"ASSIGNMENT_DENIED" in out
    code, out = run_cli(capsysbinary, "render", "--workflow", model, "--view", "class")
    assert code == 0 and b"classDiagram" in out


@pytest.mark.parametrize("argv,error", [
    (["render", "--view", "state"], "CONFIGURATION"),
    (["render", "x", "--workflow", "y.json"], "CONFIGURATION"),
    (["render", "--workflow", "examples/excursion-candidate.json", "--view", "sequence"], "ACTION_REQUIRED"),
    (["render", "--workflow", "examples/excursion-candidate.json", "--view", "sequence", "--action", "Recommend", "--format", "dot"], "FORMAT_UNSUPPORTED"),
    (["render", "--workflow", "examples/excursion-candidate.json", "--view", "all"], "CONFIGURATION"),
    (["render", "--workflow", "examples/excursion-candidate.json", "--view", "sequence", "--action", "Nope"], "ACTION_DENIED"),
])
def test_cli_render_errors_are_stable_codes(capsysbinary, monkeypatch, argv, error):
    monkeypatch.chdir(ROOT)
    code, out = run_cli(capsysbinary, *argv)
    assert code == 2 and json.loads(out)["error"] == error


def test_cli_render_case_by_id_and_html(studio, selected, capsysbinary, tmp_path):
    workspace = studio.store.directory
    code, out = run_cli(capsysbinary, "render", selected["id"], "--workspace", str(workspace), "--view", "diff")
    assert code == 0 and b"Recommended" in out
    target = tmp_path / "all.html"
    code, out = run_cli(capsysbinary, "render", selected["id"], "--workspace", str(workspace), "--view", "all", "--format", "html", "--out", str(target))
    page = target.read_text(encoding="utf-8")
    assert code == 0 and page.count('class="mermaid"') == 10 and "mermaid.initialize" in page and len(page) > 1_000_000
    code, out = run_cli(capsysbinary, "render", "does-not-exist", "--workspace", str(workspace))
    assert code == 2 and json.loads(out)["error"] == "NOT_FOUND"


def write_teacher_approves(tmp_path) -> Path:
    data = json.loads((ROOT / "examples/excursion-candidate.json").read_text(encoding="utf-8"))
    for t in data["transitions"]:
        if t["action"] == "Approve":
            t["role"] = "Teacher"
    target = tmp_path / "bad.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    return target


def test_cli_render_marks_a_policy_refused_workflow_and_exits_nonzero(capsysbinary, tmp_path):
    bad = write_teacher_approves(tmp_path)
    for view in ("diff", "state", "impact"):
        code, out = run_cli(capsysbinary, "render", "--workflow", str(bad), "--view", view)
        assert code == 2 and b"POLICY BLOCKED: PROTECTED_AUTHORITY:Approve" in out, view
    assert "+ Approve · Teacher" in run_cli(capsysbinary, "render", "--workflow", str(bad), "--view", "diff")[1].decode("utf-8")
    ok = run_cli(capsysbinary, "render", "--workflow", str(ROOT / "examples/excursion-candidate.json"), "--view", "diff")
    assert ok[0] == 0 and b"POLICY BLOCKED" not in ok[1]  # control: the accepted candidate is unmarked and exits 0
    target = tmp_path / "bad.html"
    assert run_cli(capsysbinary, "render", "--workflow", str(bad), "--view", "all", "--format", "html", "--out", str(target))[0] == 2
    assert "POLICY BLOCKED: PROTECTED_AUTHORITY:Approve" in target.read_text(encoding="utf-8")


def test_cli_render_is_read_only_and_does_not_create_a_workspace_or_key(capsysbinary, tmp_path):
    missing = tmp_path / "no-such-workspace"
    code, out = run_cli(capsysbinary, "render", "case", "--workspace", str(missing))
    assert code == 2 and json.loads(out)["error"] == "NOT_FOUND" and not missing.exists()


def test_html_panels_compose_views_in_the_catalog():
    before, after = demo_pair()
    everything = html_panels("all", before, after)
    assert len(everything) == 5 + len(after.transitions)  # the five non-sequence views + one commit protocol per action
    assert not {"Diff view", "Impact view"} & {h for h, _, _ in html_panels("all", before, None)}  # no candidate: no diff or ripple
    with pytest.raises(DomainError) as e:
        html_panels("diff", before, None)
    assert e.value.code == "CANDIDATE_REQUIRED"


def test_committed_screenshots_are_from_the_current_model():
    """A stale-image tripwire that needs no browser: the sidecar written by scripts/capture_visual_screenshots.py
    records which models the PNGs were drawn from. It does not prove the pixels; the release session regenerates them."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import capture_visual_screenshots as capture  # noqa: PLC0415 - scripts/ is not a package; put on sys.path only for this test
    recorded = json.loads(capture.SIDECAR.read_text(encoding="utf-8"))
    assert recorded == capture.source_record(), "docs/assets/*.png are stale: run `nox -s visual_screenshots` and commit the images and sidecar"
    for name in recorded["images"]:
        assert (capture.ASSETS / name).is_file()
