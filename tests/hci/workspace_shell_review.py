"""Focused real-browser Workspace and case-inventory recovery checks.

Run with the existing normal-identity disposable CLI server. Successful inventory
responses always come from that server; controls only delay requests or fail one
GET with an explicitly synthetic 503. No browser execution occurs on import.
"""
from __future__ import annotations

import argparse
import hashlib
import socket
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

from case_preview_navigation import PreviewNavigation, emit, run_subject, write_json
from quality.hci.server import ROOT, studio_server
from self_dogfood_replay import WORKSPACE_VIEWS
from self_dogfood_subject import compare_subjects, file_identity


def workspace_focus_kind(focus):
    """Distinguish an owned dialog focus from the narrowly observed native UA boundary."""
    assert focus.get("dialogOpen") is True and focus.get("dialogModal") is True, "Workspace is no longer modal"
    if focus.get("inside") is True and focus.get("documentHasFocus") is True:
        return "dialog"
    if (focus.get("inside") is False and focus.get("documentHasFocus") is False
            and focus.get("tag") == "BODY" and focus.get("id") == ""):
        return "ua_boundary"
    raise AssertionError("Native modal focus reached the background page or an unrecognized outside state")


def assert_workspace_reentry(focus, expected_control):
    assert workspace_focus_kind(focus) == "dialog", "Native Tab did not return from browser controls"
    assert focus.get("control") == expected_control, "Native Tab returned to the wrong dialog control"


class WorkspaceReview(PreviewNavigation):
    def __init__(self, page, out, launch_url):
        self.inventory_controls = []
        super().__init__(page, out, launch_url)

    def readonly_get(self, path):
        response = self.page.context.request.get(
            self.base + "api/" + path,
            headers={"Authorization": "Bearer " + self.capability},
        )
        assert response.status == 200, f"Independent GET {path}: HTTP {response.status}"
        value = response.json()
        self.oracles.append({"stage": self.stage, "path": "/api/" + path, "body": value})
        return value

    def shot(self, name):
        self.page.screenshot(path=str(self.out / (name + ".png")))

    def snapshot(self):
        inventory = self.readonly_get("cases")
        return {
            "inventory": inventory,
            "cases": {item["id"]: self.get_case(item["id"]) for item in inventory},
            "history": {item["id"]: self.readonly_get(f'cases/{item["id"]}/history') for item in inventory},
        }

    def writes(self):
        return [row for row in self.requests if row["method"] != "GET"]

    def assert_unchanged(self, before, writes):
        assert self.snapshot() == before, "Navigation/recovery changed case, history, observations or inventory"
        assert self.writes() == writes, "Navigation/recovery sent a mutation"

    def hold_inventory(self):
        assert self.held_route is None and self.hold_path is None
        self.hold_path = "/api/cases"
        self.inventory_controls.append({"stage": self.stage, "mode": "hold_real_request", "path": "/api/cases"})

    def release_inventory(self):
        assert self.held_route is not None, "Expected actual inventory request was not intercepted"
        route, self.held_route = self.held_route, None
        route.continue_()  # Original request reaches the real server; no success payload is synthesized.

    def empty_loading(self):
        assert self.readonly_get("cases") == [], "The disposable server must start with a genuinely empty inventory"
        before, writes = self.snapshot(), self.writes()
        self.hold_inventory()
        self.page.goto(self.launch_url)
        expect(self.page.locator("#case-switcher")).to_have_attribute("data-list-state", "loading")
        expect(self.page.locator("#case-switcher")).to_be_disabled()
        expect(self.page.locator("#case-picker-status")).to_contain_text("Refreshing case list")
        expect(self.page.locator("#case-picker-retry")).to_be_hidden()
        self.shot("initial-real-inventory-loading")
        self.release_inventory()
        self.settled()
        expect(self.page.locator("#case-switcher")).to_have_attribute("data-list-state", "ready")
        expect(self.page.locator("#case-switcher")).to_be_hidden()
        expect(self.page.locator("#case-picker-status")).to_have_text("No change cases yet.")
        expect(self.page.locator("#start-intent")).to_be_visible()
        expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        self.assert_unchanged(before, writes)
        return {"actual_inventory": [], "loading_then_empty": True, "successful_payload": "real server GET"}

    def empty_failure_retry(self):
        before, writes = self.snapshot(), self.writes()
        self.fault_path = "/api/cases"
        self.page.reload()
        expect(self.page.locator("#case-switcher")).to_have_attribute("data-list-state", "unavailable")
        self.settled()
        expect(self.page.locator("#case-switcher")).to_be_visible()
        expect(self.page.locator("#case-switcher")).to_be_disabled()
        expect(self.page.locator("#case-picker-status")).to_contain_text("Case list unavailable")
        expect(self.page.locator("#case-picker-status")).not_to_contain_text("No change cases yet")
        expect(self.page.locator("#case-picker-retry")).to_be_visible()
        self.shot("empty-inventory-one-shot-503")
        diagnostic = self.page.locator("#error-json").text_content()
        count = self.page.locator("#problem-count").inner_text()
        assert int(count) > 0
        expect(self.page.locator("#focus-problem-count")).to_have_text(count)
        self.page.locator("#collapse-bottom").click()
        expect(self.page.locator("#bottom-pane")).to_be_hidden()
        self.page.locator("#focus-problems").click()
        expect(self.page.locator('[data-bottom="problems-pane"]')).to_be_focused()
        assert self.page.locator("#error-json").text_content() == diagnostic
        self.hold_inventory()
        self.page.locator("#case-picker-retry").click()
        expect(self.page.locator("#case-switcher")).to_have_attribute("data-list-state", "loading")
        expect(self.page.locator("#case-picker-status")).to_contain_text("Refreshing case list")
        self.assert_unchanged(before, writes)
        self.release_inventory()
        self.settled()
        expect(self.page.locator("#case-switcher")).to_be_hidden()
        expect(self.page.locator("#case-picker-retry")).to_be_hidden()
        expect(self.page.locator("#start-intent")).to_be_focused()
        expect(self.page.locator("#error-details")).to_be_hidden()
        self.assert_unchanged(before, writes)
        return {"fault": "one synthetic 503", "retry_loading": True, "recovery_focus": "start-intent",
                "actual_problem_count": count, "exact_diagnostic_retained_after_reopen": True}

    def create_real_cases(self):
        before = len(self.writes())
        first = self.create("Workspace A " + self.label, candidate=False)
        second = self.create("Workspace B " + self.label, candidate=False)
        self.case_id = second
        inventory = self.readonly_get("cases")
        assert {item["id"] for item in inventory} == {first, second}
        additions = self.writes()[before:]
        assert len(additions) == 2 and all(row["method"] == "POST" and row["path"] == "/api/cases" for row in additions)
        self.assert_case_identity(self.get_case(second))
        return {"cases": [first, second], "setup_posts": 2, "selected_meanings": 0,
                "scope": "two real draft cases; no proposals, runtime, edit, verification or owner decisions"}

    def refresh_from_command(self):
        self.page.keyboard.press("Control+k")
        expect(self.page.locator("#command-palette")).to_be_visible()
        self.page.locator("#palette-search").fill("Refresh current model")
        self.page.locator("#palette-search").press("ArrowDown")
        target = self.page.locator("#palette-results").get_by_role("button", name="Refresh current model", exact=True)
        expect(target).to_be_focused()
        target.press("Enter")

    def retained_inventory_retry(self):
        before, writes = self.snapshot(), self.writes()
        view = before["cases"][self.case_id]
        self.fault_path = "/api/cases"
        self.refresh_from_command()
        expect(self.page.locator("#case-switcher")).to_have_attribute("data-list-state", "unavailable")
        self.settled()
        expect(self.page.locator("#case-picker-status")).to_contain_text("Retained choices")
        expect(self.page.locator("#case-switcher")).to_be_enabled()
        self.assert_case_identity(view)
        expected = {item["id"] for item in before["inventory"]}
        options = self.page.locator('#case-switcher option:not([value=""])').evaluate_all("nodes=>nodes.map(n=>n.value)")
        assert set(options) == expected and len(options) == len(expected)
        self.shot("retained-inventory-one-shot-503")
        self.hold_inventory()
        self.page.locator("#case-picker-retry").click()
        expect(self.page.locator("#case-switcher")).to_have_attribute("data-list-state", "loading")
        expect(self.page.locator("#case-picker-status")).to_contain_text("Retained choices")
        self.assert_case_identity(view)
        # A real user moves focus while the retry is pending; completion must not steal it.
        self.open_workspace()
        self.page.locator("#close-workspace").click()
        expect(self.page.locator("#open-workspace")).to_be_focused()
        self.release_inventory()
        self.settled()
        expect(self.page.locator("#case-switcher")).to_have_attribute("data-list-state", "ready")
        expect(self.page.locator("#case-picker-status")).to_be_hidden()
        expect(self.page.locator("#open-workspace")).to_be_focused()
        self.assert_case_identity(view)
        self.assert_unchanged(before, writes)
        return {"retained_case": self.case_id, "retained_inventory": sorted(expected),
                "retry_used_real_server": True, "user_moved_focus_preserved": True}

    def modal_keyboard(self):
        opener, dialog = self.page.locator("#open-workspace"), self.page.locator("#workspace-dialog")
        opener.focus()
        opener.press("Enter")
        expect(dialog).to_be_visible()
        expect(self.page.locator("#close-workspace")).to_be_focused()
        before = self.page.locator("body").get_attribute("class")
        seen, panels, trail = set(), set(), []

        def observe_focus(key):
            focus = self.page.evaluate("""() => {const n=document.activeElement,d=document.querySelector('#workspace-dialog');return {
                tag:n.tagName,id:n.id,control:n.id||(n.matches('#workspace-layout > summary')?'workspace-layout-summary':''),
                inside:d.contains(n),documentHasFocus:document.hasFocus(),
                dialogOpen:d.open,dialogModal:d.matches(':modal'),outerHTML:n.outerHTML.slice(0,600),
                view:n.dataset.workspaceView||null,panel:n.dataset.workspacePanel||null};} """)
            trail.append({"key": key, **focus})
            write_json(self.out / (self.stage + "-modal-focus-trail.json"), trail)
            return focus

        def step_past_scroll_container(focus, key):
            if focus["control"] != "workspace-dialog":
                return focus
            assert_workspace_reentry(focus, "workspace-dialog")
            assert focus["tag"] == "DIALOG"
            geometry = dialog.evaluate("n=>({clientHeight:n.clientHeight,scrollHeight:n.scrollHeight,scrollTop:n.scrollTop})")
            assert geometry["clientHeight"] > 0 and geometry["scrollHeight"] > geometry["clientHeight"], "Unexpected non-scrolling dialog stop"
            trail[-1]["native_scroll_region"] = geometry
            self.page.keyboard.press(key)
            return observe_focus(key + ": one step past native dialog scroll region")

        previous = observe_focus("Enter: open Workspace")
        assert_workspace_reentry(previous, "close-workspace")
        assert self.page.locator("#workspace-layout").get_attribute("open") is None
        # Deliberate negative control: native modality must reject a background focus() attempt.
        self.page.locator("#start-intent").evaluate("node => node.focus()")
        assert_workspace_reentry(observe_focus("negative control: background focus attempt"), "close-workspace")
        for key in ("Control+k", "Control+b"):
            self.page.keyboard.press(key)
            observe_focus(key)
            expect(dialog).to_be_visible()
            expect(self.page.locator("#command-palette")).to_be_hidden()
            assert self.page.locator("body").get_attribute("class") == before
        for _ in range(40):
            self.page.keyboard.press("Tab")
            focus = observe_focus("Tab")
            if workspace_focus_kind(focus) == "ua_boundary":
                assert previous["control"] == "workspace-layout-summary", "Browser boundary occurred before the last control"
                self.shot(self.stage + "-modal-forward-ua-boundary")
                self.page.keyboard.press("Tab")
                focus = observe_focus("Tab: one same-direction return from browser controls")
                focus = step_past_scroll_container(focus, "Tab")
                assert_workspace_reentry(focus, "close-workspace")
            previous = focus
            if focus["view"]:
                seen.add(focus["view"])
            if focus["panel"]:
                panels.add(focus["panel"])
            if focus["id"] == "close-workspace":
                break
        else:
            raise AssertionError("Native Workspace focus cycle did not return to Close")
        assert seen == set(WORKSPACE_VIEWS)
        assert panels == {"problems-pane", "evidence-pane", "history-pane"}
        self.page.keyboard.press("Shift+Tab")
        backward = observe_focus("Shift+Tab")
        backward = step_past_scroll_container(backward, "Shift+Tab")
        if workspace_focus_kind(backward) == "ua_boundary":
            self.shot(self.stage + "-modal-backward-ua-boundary")
            self.page.keyboard.press("Shift+Tab")
            backward = observe_focus("Shift+Tab: one same-direction return from browser controls")
        assert_workspace_reentry(backward, "workspace-layout-summary")
        self.page.keyboard.press("Escape")
        observe_focus("Escape")
        expect(dialog).to_be_hidden()
        expect(opener).to_be_focused()
        expect(opener).to_have_attribute("aria-expanded", "false")
        assert self.page.locator("body").get_attribute("class") == before
        return trail

    def panel_routes(self):
        rows = []
        for target in ("problems-pane", "evidence-pane", "history-pane"):
            if self.page.locator("#bottom-pane").is_visible():
                self.page.locator("#collapse-bottom").click()
            self.open_workspace().locator(f'[data-workspace-panel="{target}"]').click()
            expect(self.page.locator("#workspace-dialog")).to_be_hidden()
            expect(self.page.locator(f"#{target}")).to_be_visible()
            expect(self.page.locator(f'[data-bottom="{target}"]')).to_be_focused()
            text = self.page.locator(f"#{target}").text_content()
            self.page.locator("#collapse-bottom").click()
            expect(self.page.locator("#focus-problems")).to_be_focused()
            expect(self.page.locator("#bottom-pane")).to_be_hidden()
            expect(self.page.locator("#panel-resizer")).to_be_hidden()
            assert self.page.locator("#bottom-pane").get_attribute("hidden") is not None
            closed = self.page.locator("#bottom-pane").evaluate("""n=>({height:n.getBoundingClientRect().height,
                painted:[...n.querySelectorAll('button,input,select,textarea,a[href],[tabindex]')]
                  .filter(x=>x.getClientRects().length).map(x=>x.id||x.tagName)})""")
            assert closed == {"height": 0, "painted": []}, "Closed panel still renders focus targets"
            # Probe real keyboard traversal across the panel's DOM boundary, not a forced focus into hidden content.
            last = self.page.locator("#workspace").locator(':is(button,input,select,textarea,a[href],[tabindex]):visible')
            eligible = last.evaluate_all("nodes=>nodes.map((n,i)=>({i,ok:!n.disabled&&n.tabIndex>=0})).filter(x=>x.ok).map(x=>x.i)")
            assert eligible
            last.nth(eligible[-1]).focus()
            for _ in range(2):
                self.page.keyboard.press("Tab")
                assert not self.page.locator("#bottom-pane").evaluate("n=>n.contains(document.activeElement)")
            self.page.locator("#focus-problems").click()
            expect(self.page.locator("#problems-pane")).to_be_visible()
            expect(self.page.locator('[data-bottom="problems-pane"]')).to_be_focused()
            self.open_bottom(target)
            assert self.page.locator(f"#{target}").text_content() == text, "Collapse/reopen discarded panel content"
            rows.append({"panel": target, "closed": closed, "problems_recovery": True})
        self.page.locator("#collapse-bottom").click()
        return rows

    def viewport_workspace(self, width, height):
        self.page.set_viewport_size({"width": width, "height": height})
        self.page.locator("#start-intent").click()
        unsent = "Unsubmitted Workspace navigation note"
        self.page.locator("#request").fill(unsent)
        self.tab("model")
        before, writes = self.snapshot(), self.writes()
        view = before["cases"][self.case_id]
        trail = self.modal_keyboard()
        for name in WORKSPACE_VIEWS:
            self.workspace_view(name)
            self.assert_case_identity(view)
        self.tab("model")
        panels = self.panel_routes()
        expect(self.page.locator("#status-evidence")).to_be_visible()
        expect(self.page.locator("#status-evidence")).to_contain_text("human UNKNOWN")
        expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        assert self.page.locator("#request").input_value() == unsent
        geometry = self.page.evaluate("""()=>({width:innerWidth,height:innerHeight,
            documentWidth:document.documentElement.scrollWidth,documentHeight:document.documentElement.scrollHeight,
            bottomHeight:document.querySelector('#bottom-pane').getBoundingClientRect().height,
            workspace:document.querySelector('#workspace').getBoundingClientRect().toJSON(),
            status:document.querySelector('#status-evidence').getBoundingClientRect().toJSON()})""")
        assert geometry["documentWidth"] <= width + 1, "Workspace causes page-level horizontal overflow"
        assert geometry["documentHeight"] <= height + 1, "Workspace escapes its viewport"
        assert geometry["bottomHeight"] == 0 and geometry["workspace"]["width"] > 0
        assert 0 <= geometry["status"]["top"] < geometry["status"]["bottom"] <= height + 1
        self.shot(f"workspace-closed-panel-{width}")
        self.assert_unchanged(before, writes)
        return {"viewport": [width, height], "keyboard_cycle": trail, "work_routes": list(WORKSPACE_VIEWS),
                "panel_routes": panels, "geometry": geometry, "unsent_input_preserved": True,
                "scope": "default-pack shell; Repository is unconnected, not a source-conformance test"}


def main():
    if not __debug__:
        emit({"status": "NOT_RUN", "reason": "Assertions require unoptimized Python"})
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    before = run_subject()
    write_json(out / "subject-before.json", before)
    script = Path(__file__).read_bytes()
    (out / "replay-script.py").write_bytes(script)
    result = {"schema": "eija.workspace-shell-browser.v1", "status": "FAIL", "utc": datetime.now(UTC).isoformat(),
              "identity": "normal_source_review_required", "pack": "default_excursion", "provider": "offline",
              "script_sha256": hashlib.sha256(script).hexdigest(), "checks": [],
              "helpers": {name: file_identity(ROOT, name) for name in (
                  "quality/hci/server.py", "tests/hci/case_preview_navigation.py",
                  "tests/hci/self_dogfood_replay.py", "tests/hci/self_dogfood_subject.py")},
              "browser_closed": False, "server_closed": False,
              "not_run": ["connected repository semantics", "runtime/edit flows already covered separately",
                          "canonical HCI budgets", "axe audit", "human usability", "live provider", "owner decisions"]}
    review, address = None, None
    try:
        with studio_server("workspace-shell-browser", identity="release", timeout=60) as launch_url:
            parsed = urlsplit(launch_url)
            address = (parsed.hostname, parsed.port)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    page.set_default_timeout(15000)
                    review = WorkspaceReview(page, out, launch_url)
                    for name, action in (
                        ("actual-empty-inventory-loading", review.empty_loading),
                        ("empty-inventory-failure-retry", review.empty_failure_retry),
                        ("two-real-case-setup", review.create_real_cases),
                        ("retained-inventory-retry-focus", review.retained_inventory_retry),
                        ("workspace-1440", lambda: review.viewport_workspace(1440, 900)),
                        ("workspace-1280", lambda: review.viewport_workspace(1280, 800)),
                        ("workspace-320", lambda: review.viewport_workspace(320, 800)),
                    ):
                        review.step(name, action)
                        emit({"check": name, "status": "PASS"})
                    assert len(review.injected) == 2 and review.http_errors == review.injected
                    assert not review.errors and not review.forbidden
                    assert len(review.writes()) == 2 and all(row["path"] == "/api/cases" for row in review.writes())
                    result["status"] = "PASS"
                finally:
                    try:
                        if review and review.held_route is not None:
                            review.held_route.abort()
                            review.held_route = None
                        if review:
                            review.shot("final")
                    finally:
                        browser.close()
                        result["browser_closed"] = True
    except Exception as error:
        message = str(error).replace(review.capability, "[test-capability]") if review else str(error)
        result["error"] = {"type": type(error).__name__, "message": message}
    finally:
        if address:
            with socket.socket() as sock:
                sock.settimeout(.2)
                result["server_closed"] = sock.connect_ex(address) != 0
        if review:
            result.update({"checks": review.checks, "failed_stage": review.stage if result["status"] != "PASS" else None,
                           "requests": review.requests, "http_errors": review.http_errors,
                           "injected_failures": review.injected, "delayed_requests": review.inventory_controls,
                           "javascript_errors": review.errors, "forbidden_attempts": review.forbidden,
                           "navigation_actions": review.navigation_actions})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
        after = run_subject()
        write_json(out / "subject-after.json", after)
        result["subject_preservation"] = compare_subjects(before, after)
        result["subject_content_sha256"] = before["content_sha256"]
        result["script_after_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        result["helpers_after"] = {name: file_identity(ROOT, name) for name in result["helpers"]}
        if result["helpers_after"] != result["helpers"]:
            result["status"] = "FAIL"
        if result["script_after_sha256"] != result["script_sha256"]:
            result["status"] = "FAIL"
        if result["subject_preservation"]["status"] != "UNCHANGED" or not result["server_closed"] or not result["browser_closed"]:
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {path.relative_to(out).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                                                   for path in sorted(out.rglob("*")) if path.is_file()})
    emit({key: result[key] for key in ("status", "browser_closed", "server_closed", "checks")})
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
