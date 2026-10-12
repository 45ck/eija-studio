"""Actual browser edit/review/activation/restart journey, using a labelled synthetic owner.

Positive and negative observations use the real services and generated app. This proves
local mechanics, never a legitimate owner decision or a production deployment. No source
fixture is restamped, no security header is relaxed, and no signed-in browser is reused.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from demos.lib.server import _kill_process_tree
from eija_studio.domain.models import AGENT, DomainError
from exact_app_browser_server import FIXTURE_MARK, synthetic_app, synthetic_studio

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ExactAppServer:
    base_url: str
    token: str
    workspace: Path
    pid: int


@contextmanager
def exact_app_server(workspace: Path, *, synthetic: bool = True):
    """Start a fresh Python process, reopening only the caller's synthetic workspace."""
    marker = workspace / "synthetic-fixture.json"
    if workspace.exists() and not marker.exists() and any(workspace.iterdir()):
        raise RuntimeError("Refusing to mark or open an existing unowned workspace as a synthetic fixture")
    workspace.mkdir(parents=True, exist_ok=True)
    if not marker.exists():
        marker.write_text(json.dumps({"identity_source": FIXTURE_MARK,
                                     "scope": "Disposable local mechanics; no real owner approval"}) + "\n",
                          encoding="utf-8", newline="\n")
    synthetic_studio(workspace)  # Refuse a foreign or unmarked workspace before launching a child.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    token = uuid4().hex
    base = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT / "tests")))
    env["EIJA_PROVIDER"] = "offline"
    with (workspace / "browser-server.log").open("a", encoding="utf-8") as log:
        argv = [sys.executable, str(ROOT / "tests/exact_app_browser_server.py"),
                "--workspace", str(workspace), "--port", str(port)]
        if not synthetic:
            argv.append("--measured-source")
        process = subprocess.Popen(  # noqa: S603 - fixed Python entrypoint and caller-owned scratch path
            argv,
            stdin=subprocess.PIPE, stdout=log, stderr=log, env=env,
            start_new_session=sys.platform != "win32",
        )
        assert process.stdin is not None
        process.stdin.write((token + "\n").encode("ascii"))
        process.stdin.close()
        deadline = time.monotonic() + 30
        try:
            with httpx.Client(trust_env=False, timeout=1) as client:
                while True:
                    try:
                        if client.get(base + "/play").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError("Synthetic browser server did not start; see browser-server.log")
                    time.sleep(.05)
                yield ExactAppServer(base, token, workspace, process.pid)
        finally:
            with suppress(httpx.HTTPError):
                httpx.post(base + "/api/play/stop", headers={"Authorization": "Bearer " + token,
                           "Origin": base}, json={}, trust_env=False, timeout=10)
            _kill_process_tree(process)


def open_play(page, server: ExactAppServer, case_id: str | None = None) -> None:
    suffix = "?case=" + case_id if case_id else ""
    response = page.goto(f"{server.base_url}/play{suffix}#{server.token}")
    assert response is not None and response.status == 200
    assert "script-src 'self'" in response.headers["content-security-policy"]
    assert "unsafe-eval" not in response.headers["content-security-policy"]
    assert "unsafe-inline" not in response.headers["content-security-policy"]
    page.wait_for_selector("body[data-ready=true]", timeout=60_000)


def add_renewal_in_ui(page) -> None:
    """Only ordinary controls edit the supported workflow; no browser-side model injection."""
    page.locator('#outline-states [data-id="state:Overdue"]').click()
    page.locator("#inspector").get_by_role("button", name="Add a transition from here", exact=True).click()
    form = page.locator("#inspector .draft-form")
    form.get_by_label("From", exact=True).select_option("Overdue")
    form.get_by_label("To", exact=True).select_option("OnLoan")
    form.get_by_label("Action", exact=True).select_option("Renew")
    form.get_by_label("Who may take it", exact=True).select_option("Librarian")
    with page.expect_response("**/api/play/plan/preview") as checked:
        form.get_by_role("button", name="Add to the plan", exact=True).click()
    assert checked.value.status == 200 and checked.value.json()["legal"] is True
    page.wait_for_selector('#outline-transitions [data-id="transition:TR-RENEW"]')
    assert page.evaluate("PlayIDE.status().baseline_version") == 0


def refuse_unsafe_return_in_ui(page, on_refusal=None) -> dict:
    """A requested book cannot be returned before checkout; recover without changing the active model."""
    before = page.evaluate("PlayIDE.model()")
    page.locator('#outline-transitions [data-id="transition:TR-RETURN"]').click()
    page.locator("#inspector").get_by_role("button", name="Move an end…", exact=True).click()
    form = page.locator("#inspector .draft-form")
    end = form.get_by_label("Move Return's", exact=True)
    state = form.get_by_label("to state", exact=True)
    assert end.get_attribute("aria-label") == "Move Return's"
    assert state.get_attribute("aria-label") == "to state"
    end.select_option("source")
    state.select_option("Requested")
    with page.expect_response("**/api/play/plan/preview") as checked:
        form.get_by_role("button", name="Add to the plan", exact=True).click()
    report = checked.value.json()
    assert checked.value.status == 200 and report["legal"] is False
    assert "LOAN_RETURN_WITHOUT_CHECKOUT" in report["codes"]
    page.wait_for_selector(".plan-verdict.bad:has-text('LOAN_RETURN_WITHOUT_CHECKOUT')")
    assert page.evaluate("PlayIDE.model()") == before
    if on_refusal is not None:
        on_refusal(report)
    page.click("#undo")
    page.wait_for_function("() => PlayIDE.activationDraft().request.steps.length === 0")
    assert page.evaluate("PlayIDE.model()") == before
    return report


def inspect_diff(page, on_inspect=None) -> None:
    page.click("#show-changes")
    page.wait_for_selector("#diff-view:not([hidden])")
    page.wait_for_selector("#inspector .diff-item.added")
    assert "Renew" in page.locator("#inspector .diff-list").inner_text()
    if on_inspect is not None:
        on_inspect()
    page.click("#tab-states")


def transfer_and_check(page, on_build=None, on_transfer=None) -> dict:
    page.click("#activation-open")
    with page.expect_response("**/api/play/build") as candidate_built:
        page.click("#activation-build")
    assert candidate_built.value.status == 200
    built = candidate_built.value.json()
    candidate_digest = built["subject"]["digest"]
    if on_build is not None:
        on_build(built)
    page.click("#activation-open")
    page.wait_for_function("() => !document.getElementById('activation-transfer').disabled")
    with page.expect_response("**/api/cases/from-plan") as transferred:
        page.click("#activation-transfer")
    assert transferred.value.status == 200
    assert transferred.value.request.post_data_json["expected_build_digest"] == candidate_digest
    case = transferred.value.json()
    assert case["selection"]["kind"] == "owner_plan"
    assert case["transactions"][0]["action"] == "Renew"
    page.wait_for_function("() => !document.getElementById('activation-check').disabled")
    if on_transfer is not None:
        on_transfer(case)
    with page.expect_response(f"**/api/cases/{case['id']}/verify") as checked:
        page.click("#activation-check")
    assert checked.value.status == 200
    page.wait_for_function("() => !document.getElementById('activation-check').disabled")
    view = page.evaluate("id => PlayIDE.api('/api/cases/' + id)", case["id"])
    assert view["packet"]["eligible"] is True
    assert view["packet"]["human_understanding"] == "UNKNOWN"
    assert view["packet"]["app_build"]["freshness"] == "CURRENT"
    assert view["packet"]["app_build"]["conformance"]["status"] == "PASS"
    assert view["packet"]["subject"]["generated_app"]
    assert view["packet"]["app_build"]["subject"]["digest"] == candidate_digest
    assert "SYNTHETIC" in page.locator("#activation-source").inner_text().upper()
    assert candidate_digest[:16] in page.locator("#activation-app-summary").inner_text()
    assert "PASS" in page.locator("#activation-app-check").inner_text()
    return view


def approve_in_ui(page, view: dict, *, incorrect: bool = False) -> None:
    """Submit explicit synthetic test answers through visible controls, never inferred authority."""
    details = page.locator("#activation-decision")
    if not details.evaluate("element => element.open"):
        details.locator("summary").click()
    answers = {"checkout_authority": "Librarian", "return_entry": "OnLoan"}
    for question in view["packet"]["questions"]:
        assert question["id"] in answers, "New questions require deliberate fixture review, not copied expected answers"
        page.locator(f"#activation-questions input[name='{question['id']}']").fill(
            "Member" if incorrect else answers[question["id"]])
    page.check("#activation-acknowledge")
    with page.expect_response(f"**/api/cases/{view['case']['id']}/approve") as approved:
        page.click("#activation-approve")
    response = approved.value
    if incorrect:
        assert response.status == 409 and response.json()["code"] == "MEANING_CHECK_FAILED"
        page.wait_for_selector("#activation-status:has-text('MEANING_CHECK_FAILED')")
    else:
        assert response.status == 200 and response.json()["stage"] == "APPROVED"
        page.wait_for_function("() => !document.getElementById('activation-apply').disabled")


def refresh_case_in_ui(page, case_id: str) -> dict:
    with page.expect_response(f"**/api/cases/{case_id}") as refreshed:
        page.click("#activation-refresh")
    assert refreshed.value.status == 200
    page.wait_for_function("() => !document.getElementById('activation-refresh').disabled")
    return refreshed.value.json()


def launch_app(page) -> dict:
    if page.locator("#activation").evaluate("element => element.open"):
        page.click("#activation-close")
    if page.get_attribute("#toggle-play", "aria-pressed") != "true":
        page.click("#toggle-play")
    button = "#play-empty-build" if page.locator("#play-empty-build").is_visible() else "#play-rebuild"
    with page.expect_response("**/api/play/build") as built:
        page.click(button)
    result = built.value.json()
    assert built.value.status == 200 and result["conformance"]["status"] == "PASS"
    page.wait_for_function("() => window.PlayLive && PlayLive.snapshot().fresh", timeout=60_000)
    return result


def app_frame(page):
    element = page.locator("#run-frame").element_handle()
    assert element is not None
    frame = element.content_frame()
    assert frame is not None
    frame.wait_for_selector("#actor")
    frame.wait_for_selector("#actor option[value=librarian-assigned]", state="attached")
    return frame


def observe_record(frame, actor: str) -> dict:
    """Read the real app API independently of the frontend's internal framework or state."""
    return frame.evaluate("""async actor => {
      const records = await fetch('/api/records').then(response => response.json());
      const record = records.find(item => item.title === 'The Design of Everyday Things');
      if (!record) throw new Error('The created loan was not persisted');
      return fetch('/api/records/' + record.id + '?actor=' + encodeURIComponent(actor)).then(response => response.json());
    }""", actor)


def execute_in_ui(page, on_action=None) -> dict:
    """Observe newly approved behaviour in the actual generated app and its committed trace."""
    frame = app_frame(page)
    assert frame.locator("html").get_attribute("data-frontend") == "react"
    frame.locator('[data-nav-id="new-record"]').click()
    assert frame.locator("#title").evaluate("element => element === document.activeElement")
    frame.locator("#actor").select_option("librarian-assigned")
    frame.locator("#title").fill("The Design of Everyday Things")
    frame.locator("#field-itemTitle").fill("The Design of Everyday Things")
    frame.locator("#field-memberCard").fill("PLAY-001")
    frame.locator("#field-dueDate").fill("2026-10-10")
    frame.locator("#field-format").select_option("Book")
    frame.locator("#create-button").click()
    frame.wait_for_function("() => document.getElementById('current-state').textContent === 'Requested'")
    actions = (("CheckOut", "librarian-assigned", "OnLoan"),
               ("MarkOverdue", "clerk", "Overdue"), ("Renew", "librarian-assigned", "OnLoan"))
    for index, (action, actor, state) in enumerate(actions, 1):
        frame.locator("#actor").select_option(actor)
        frame.wait_for_function("action => { const button = document.querySelector('#options button[title=' + action + ']');"
                                "return button && !button.disabled; }", arg=action)
        frame.locator(f"#options button[title={action}]").click()
        frame.locator("#action-screen button:not(.quiet)").click()
        frame.wait_for_function("expected => document.getElementById('current-state').textContent === expected", arg=state)
        page.wait_for_function("count => PlayLive.snapshot().entries.length === count", arg=index)
        if on_action is not None:
            on_action(action, observe_record(frame, actor))
    page.wait_for_function("() => PlayLive.snapshot().entries.length === 3")
    observed = observe_record(frame, "librarian-assigned")
    trace = page.evaluate("PlayLive.snapshot().entries")
    assert [(entry["action"], entry["from"], entry["to"]) for entry in trace] == [
        ("CheckOut", "Requested", "OnLoan"), ("MarkOverdue", "OnLoan", "Overdue"), ("Renew", "Overdue", "OnLoan")]
    assert observed["record"]["version"] == 3 and observed["record"]["state"] == "OnLoan"
    assert observed["record"]["model_hash"] == trace[-1]["modelHash"]
    assert observed["history"][-1]["operation"] == trace[-1]["operationId"]
    return {"record": observed["record"], "trace": trace}


def workspace_snapshot(workspace: Path) -> dict:
    studio = synthetic_studio(workspace)
    cases = studio.store.list_cases()
    with studio.store.transaction() as unit:
        active = unit.active()
        counts = unit.effect_counts()
        observations = {case["id"]: unit.observations(case["id"]) for case in cases}
    return {"active": active, "cases": cases, "effect_counts": counts, "observations": observations}


def assert_agent_cannot_approve(workspace: Path, view: dict) -> None:
    studio = synthetic_studio(workspace)
    before = workspace_snapshot(workspace)
    with pytest.raises(DomainError) as denied:
        studio.approve(view["case"]["id"], view["case"]["version"], view["packet"]["subject_hash"],
                       {"checkout_authority": "Librarian", "return_entry": "OnLoan"}, True, AGENT)
    assert denied.value.code == "AUTHORITY_REQUIRED"
    assert workspace_snapshot(workspace) == before


def test_disposable_server_exposes_the_real_systems_listing_without_writing(tmp_path):
    """The capture fixture must include the same systems routes as the ordinary CLI."""
    workspace = tmp_path / "isolated synthetic owner"
    workspace.mkdir()
    (workspace / "synthetic-fixture.json").write_text(
        json.dumps({"identity_source": FIXTURE_MARK}) + "\n", encoding="utf-8")
    token, port = uuid4().hex, 8765
    app = synthetic_app(workspace, token, port)
    origin = f"http://127.0.0.1:{port}"
    headers = {"Authorization": "Bearer " + token, "Origin": origin}
    before = workspace_snapshot(workspace)
    try:
        with TestClient(app, base_url=origin) as client:
            assert client.get("/api/play/systems").status_code == 401
            response = client.get("/api/play/systems", headers=headers)
            assert response.status_code == 200
            listing = response.json()
            assert listing["current"]["id"] == "library-loan"
            assert Path(listing["current"]["pack"]) == (ROOT / "packs/library-loan").resolve()
            assert Path(listing["current"]["workspace"]) == workspace.resolve()
            assert Path(listing["home"]) == (workspace / "systems").resolve()
            assert listing["systems"] == listing["recent"] == []
            assert "library-loan" in {template["id"] for template in listing["templates"]}
            assert listing["sketch_help"]
            assert client.get("/api/play/draft", headers=headers).json()["draft"] is None
        assert workspace_snapshot(workspace) == before
        assert not (workspace / "systems").exists()
    finally:
        app.state.play.stop()


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: set EIJA_BROWSER_TESTS=1 for actual browser")
def test_exact_generated_app_is_reviewed_activated_and_reopened_in_a_fresh_process(tmp_path):
    browser_api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the demos extra")
    with browser_api.sync_playwright() as playwright:
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except browser_api.Error as error:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(error).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 1000})
            page.add_init_script("""window.__journeyCspViolations = [];
              document.addEventListener('securitypolicyviolation', event => {
                window.__journeyCspViolations.push({directive:event.effectiveDirective, blocked:event.blockedURI});
              });""")
            errors: list[dict] = []
            csp_errors: list[str] = []
            app_console: list[dict] = []
            synthetic_capabilities: set[str] = set()
            expected_console_conflicts: dict[tuple[str, str], int] = {}
            phase = "open"

            def safe_text(value):
                if value is None:
                    return None
                for capability in synthetic_capabilities:
                    value = value.replace(capability, "[synthetic-capability-redacted]")
                return value

            def observe_console(message):
                text = safe_text(message.text)
                if "content security policy" in text.casefold() or "content-security-policy" in text.casefold():
                    csp_errors.append(text)
                if message.type in {"error", "warning"}:
                    app_console.append({"kind": message.type, "text": text, "phase": phase,
                        "source": safe_text(message.location.get("url", "").split("?", 1)[0].split("#", 1)[0])})

            page.on("pageerror", lambda error: errors.append({"message": safe_text(str(error)),
                    "stack": safe_text(getattr(error, "stack", None)), "phase": phase,
                    "url": safe_text(page.url.split("#", 1)[0])}))
            page.on("console", observe_console)
            workspace = tmp_path / "isolated synthetic owner"
            with exact_app_server(workspace) as server:
                synthetic_capabilities.add(server.token)
                first_pid = server.pid
                open_play(page, server)
                before = workspace_snapshot(workspace)
                phase = "unsafe model edit and recovery"
                refuse_unsafe_return_in_ui(page)
                assert workspace_snapshot(workspace) == before
                phase = "ordinary model edit and UML diff"
                add_renewal_in_ui(page)
                inspect_diff(page)
                phase = "exact app build, transfer and checks"
                view = transfer_and_check(page)
                case_url = server.base_url + "/api/cases/" + view["case"]["id"]
                expected_console_conflicts = {
                    (case_url + "/approve", "authority and understanding refusals"): 1,
                    (case_url + "/apply", "changed app bundle refusal"): 1,
                    (case_url + "/apply", "duplicate activation refusal"): 1,
                }
                phase = "authority and understanding refusals"
                assert_agent_cannot_approve(workspace, view)
                before = workspace_snapshot(workspace)
                approve_in_ui(page, view, incorrect=True)
                assert workspace_snapshot(workspace) == before
                view = refresh_case_in_ui(page, view["case"]["id"])
                phase = "explicit synthetic approval"
                approve_in_ui(page, view)
                reviewed_subject = view["packet"]["app_build"]["subject"]
                # Simulate an actual disk payload change after approval; do not alter the recorded subject or receipts.
                payload = workspace / "generated-reviews" / view["case"]["app_build"]["digest"] / "app/web/index.html"
                original = payload.read_bytes()
                before = workspace_snapshot(workspace)
                phase = "changed app bundle refusal"
                try:
                    payload.write_bytes(original + b"\n<!-- deliberately changed after synthetic approval -->\n")
                    with page.expect_response(f"**/api/cases/{view['case']['id']}/apply") as refused:
                        page.click("#activation-apply")
                    assert refused.value.status == 409 and refused.value.json()["code"] == "GATE_BLOCKED"
                    assert workspace_snapshot(workspace) == before
                    page.wait_for_selector("#activation-status:has-text('GATE_BLOCKED')")
                finally:
                    payload.write_bytes(original)
                refresh_case_in_ui(page, view["case"]["id"])
                phase = "restore, recheck and explicit reapproval"
                page.wait_for_function("() => !document.getElementById('activation-check').disabled")
                with page.expect_response(f"**/api/cases/{view['case']['id']}/verify") as rechecked:
                    page.click("#activation-check")
                assert rechecked.value.status == 200
                page.wait_for_function("() => !document.getElementById('activation-check').disabled")
                view = page.evaluate("id => PlayIDE.api('/api/cases/' + id)", view["case"]["id"])
                assert view["packet"]["app_build"]["subject"] == reviewed_subject
                approve_in_ui(page, view)
                phase = "atomic activation"
                with page.expect_response(f"**/api/cases/{view['case']['id']}/apply") as activated:
                    page.click("#activation-apply")
                assert activated.value.status == 200 and activated.value.json()["stage"] == "APPLIED"
                page.wait_for_function("() => PlayIDE.status().baseline_version === 1")
                assert page.evaluate("PlayIDE.status().active_app_build.subject") == reviewed_subject
                current = workspace_snapshot(workspace)
                phase = "duplicate activation refusal"
                # Duplicate activation is a safe refusal and does not increment the active revision.
                duplicate = page.evaluate("id => PlayIDE.api('/api/cases/' + id).then(view => "
                    "PlayIDE.api('/api/cases/' + id + '/apply', {expected_version:view.case.version}).catch(error => "
                    "({code:error.code})))", view["case"]["id"])
                assert duplicate["code"] == "CASE_CLOSED"
                assert workspace_snapshot(workspace) == current
            with exact_app_server(workspace) as restarted:
                synthetic_capabilities.add(restarted.token)
                phase = "fresh process reopen"
                assert restarted.pid != first_pid
                open_play(page, restarted)
                assert page.evaluate("PlayIDE.status().baseline_version") == 1
                assert page.evaluate("PlayIDE.status().active_app_build.subject") == reviewed_subject
                assert page.locator('#outline-transitions [data-id="transition:TR-RENEW"]').count() == 1
                phase = "build the active approved app after restart"
                built = launch_app(page)
                assert built["subject"] == reviewed_subject
                assert built["approval"]["status"] == "ACTIVE_APPROVED"
                assert built["approval"]["case_id"] == view["case"]["id"]
                assert page.evaluate("PlayIDE.runningBuild().subject") == reviewed_subject
                phase = "real React navigation, creation and committed actions"
                observed = execute_in_ui(page)
                violations = [violation for frame in page.frames
                              for violation in frame.evaluate("window.__journeyCspViolations || []")]
                violations = json.loads(safe_text(json.dumps(violations)))
                unexpected_console = []
                for entry in app_console:
                    key = (entry["source"], entry["phase"])
                    if (entry["kind"] == "error"
                        and entry["text"] == "Failed to load resource: the server responded with a status of 409 (Conflict)"
                        and expected_console_conflicts.get(key, 0) > 0):
                        expected_console_conflicts[key] -= 1
                    else:
                        unexpected_console.append(entry)
                (workspace / "journey-result.json").write_text(json.dumps({
                    "scope": "Actual local mechanics; explicit synthetic owner and fixture actors",
                    "outcome": "PASS" if not errors and not csp_errors and not violations and not unexpected_console else "FAIL",
                    "first_process": first_pid, "reopened_process": restarted.pid,
                    "case_id": view["case"]["id"], "reviewed_subject": reviewed_subject,
                    "active_revision": 1, "runtime": observed, "page_errors": errors,
                    "csp_messages": csp_errors, "csp_violations": violations,
                    "app_console": app_console,
                    "unexpected_console": unexpected_console,
                    "console_scope": "Only one native 409 message per exact reviewed-case URL and deliberate refusal phase is expected; other warnings/errors fail",
                    "limitations": ["Not legitimate owner approval", "Not deployed or externally integrated",
                                    "Not full UX acceptance or measured human comprehension"],
                }, indent=2) + "\n", encoding="utf-8", newline="\n")
                assert violations == []
                assert csp_errors == []
                assert errors == [], json.dumps(errors, indent=2)
                assert unexpected_console == [], json.dumps(unexpected_console, indent=2)
        finally:
            chrome.close()
