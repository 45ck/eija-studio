"""Real default-pack browser regression for case navigation and runtime ownership.

Use the existing normal-identity disposable CLI server and replay UI helpers.
Only one-shot failed GET responses are injected; all successful data is real.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

from quality.hci.server import ROOT, studio_server
from self_dogfood_replay import Review
from self_dogfood_subject import capture_subject, compare_subjects, file_identity


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def emit(value):
    sys.stdout.write(json.dumps(value) + "\n")
    sys.stdout.flush()


def run_subject():
    subject = capture_subject(ROOT)
    try:
        script = Path(__file__).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return subject  # A work-only run separately records its script SHA.
    subject["scope"].append(script)
    subject["files"][script] = file_identity(ROOT, script)
    content = {name: item["sha256"] for name, item in subject["files"].items()}
    subject["content_sha256"] = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    return subject


class PreviewNavigation(Review):
    def __init__(self, page, out, launch_url):
        parsed = urlsplit(launch_url)
        self.capability = parsed.fragment
        self.launch_url = launch_url
        self.fault_path = None
        self.hold_path = None
        self.held_route = None
        self.injected = []
        self.oracles = []
        self.runtime_responses = []
        super().__init__(page, out, f"{parsed.scheme}://{parsed.netloc}/")

    def route(self, route):
        request = route.request
        path = urlsplit(request.url).path
        self.requests.append({"stage": self.stage, "method": request.method, "path": path})
        if request.method != "GET" and path.rsplit("/", 1)[-1] in {"approve", "apply", "verify", "export"}:
            self.forbidden.append(path)
            route.abort()
        elif request.method == "GET" and path == self.hold_path:
            self.hold_path = None
            self.held_route = route  # Resume only after the real busy UI is exercised.
        elif request.method == "GET" and path == self.fault_path:
            self.fault_path = None
            self.injected.append({"stage": self.stage, "path": path, "status": 503})
            route.fulfill(status=503, content_type="application/json", body=json.dumps({
                "code": "SYNTHETIC_CASE_UNAVAILABLE",
                "message": "Regression fixture: this case GET failed once.",
            }))
        else:
            route.continue_()

    def response(self, response):
        super().response(response)
        path = urlsplit(response.url).path
        if response.status == 200 and response.request.method == "POST" and path.endswith(("/preview", "/execute")):
            self.runtime_responses.append({"path": path, "body": response.json()})

    def get_case(self, case_id):
        path = "api/cases/" + case_id
        response = self.page.context.request.get(
            self.base + path, headers={"Authorization": "Bearer " + self.capability},
        )
        assert response.status == 200, f"Independent GET {path}: HTTP {response.status}"
        value = response.json()
        self.oracles.append({"stage": self.stage, "path": "/" + path, "body": value})
        return value

    def entry(self):
        self.page.goto(self.launch_url)
        expect(self.page.locator("#connection")).to_contain_text("offline", timeout=60000)
        self.settled()
        expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        expect(self.page.locator('#model-canvas [data-state="Submitted"]')).to_have_count(1)

    def create(self, suffix, candidate=False):
        request = "Let teachers sign off excursions. Preview navigation " + suffix
        self.page.locator("#start-intent").click()
        self.page.locator("#request").fill(request)
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path == "/api/cases") as pending:
            self.page.locator("#create").click()
        created = pending.value.json()
        self.settled()
        case_id = created["id"]
        expect(self.page.locator("#case-switcher")).to_have_value(case_id)
        if candidate:
            self.page.locator("#propose").click()
            self.settled()
            self.page.locator('[data-meaning="recommend_only"]').click()
            self.settled()
        view = self.get_case(case_id)
        assert view["case"]["request"] == request
        assert bool(view["case"]["candidate"]) is candidate
        return case_id

    def switch(self, case_id, control):
        if control == "dropdown":
            self.page.locator("#case-switcher").select_option(case_id)
        else:
            request = self.get_case(case_id)["case"]["request"]
            self.page.locator("#case-list button").filter(has_text=request).click()
        self.settled()

    def ui_state(self):
        return {name: self.page.locator("#" + name).inner_text() for name in (
            "runtime-state", "runtime-version", "runtime-result", "case-title", "case-id",
        )} | {"case-switcher": self.page.locator("#case-switcher").input_value()}

    def assert_case_identity(self, view):
        case = view["case"]
        expect(self.page.locator("#case-switcher")).to_have_value(case["id"])
        expect(self.page.locator("#case-title")).to_have_text(case["request"])
        expect(self.page.locator("#case-id")).to_contain_text(case["id"][:10])
        expect(self.page.locator('#case-list button[aria-current="true"]')).to_have_count(1)
        expect(self.page.locator('#case-list button[aria-current="true"]')).to_have_attribute("title", case["request"])
        assert self.packet() == view["packet"], "Displayed review packet differs from the retained case/revision."

    def execute(self, action):
        self.page.locator("#actor").select_option("teacher-assigned")
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path.endswith("/execute")) as pending:
            self.page.locator(f'#runtime-actions [data-action="{action}"]').click()
        response = pending.value
        assert response.status == 200, f"Runtime {action}: HTTP {response.status}"
        payload = response.json()
        self.settled()
        assert payload["committed"] is True and payload["duplicate"] is False
        return payload

    def prepare_submitted(self):
        self.switch(self.first, "dropdown")
        self.tab("try")
        self.page.locator("#reset").click()
        self.settled()
        expect(self.page.locator("#runtime-state")).to_have_text("Draft")
        submitted = self.execute("Submit")
        assert submitted["instance"]["state"] == "Submitted"
        view = self.get_case(self.first)
        assert submitted["instance"] in view["observations"]["instances"]
        expect(self.page.locator("#runtime-state")).to_have_text("Submitted")
        expect(self.page.locator("#runtime-result")).to_contain_text("Committed: Submit.")
        return view, self.ui_state(), submitted["instance"]

    def refresh_same(self):
        before, ui, instance = self.prepare_submitted()
        posts = [x for x in self.requests if x["method"] != "GET"]
        self.page.keyboard.press("Control+k")
        expect(self.page.locator("#palette-search")).to_be_focused()
        self.page.keyboard.type("Refresh current model")
        self.page.keyboard.press("ArrowDown")
        with self.page.expect_response(lambda r: r.request.method == "GET" and urlsplit(r.url).path == "/api/cases/" + self.first) as pending:
            self.page.keyboard.press("Enter")
        assert pending.value.status == 200 and pending.value.json() == before, "Refresh did not read the authoritative case."
        expect(self.page.locator("#command-palette")).not_to_be_visible()
        self.settled()
        assert self.get_case(self.first) == before, "Refresh modified persisted case/runtime/evidence."
        assert self.ui_state() == ui, "Same-case refresh lost or changed the runtime preview/result."
        assert [x for x in self.requests if x["method"] != "GET"] == posts
        self.assert_case_identity(before)
        return {"case": self.first, "instance": instance, "authoritative_get_unchanged": True, "runtime_ui_unchanged": True}

    def failed_switch(self, control):
        before, ui, instance = self.prepare_submitted()
        other_before = self.get_case(self.second)
        posts = [x for x in self.requests if x["method"] != "GET"]
        self.fault_path = "/api/cases/" + self.second
        self.switch(self.second, control)
        expect(self.page.locator("#notice")).to_contain_text("SYNTHETIC_CASE_UNAVAILABLE")
        assert self.fault_path is None, "The intended case GET was not faulted."
        self.assert_case_identity(before)
        assert self.ui_state() == ui, "Failed navigation lost the retained case runtime preview/result."
        assert self.get_case(self.first) == before, "Failed navigation modified the retained case."
        assert self.get_case(self.second) == other_before, "Failed navigation modified the destination case."
        assert [x for x in self.requests if x["method"] != "GET"] == posts
        self.page.screenshot(path=str(self.out / f"{self.stage}-retained-submitted.png"), full_page=True)
        result = self.execute("Recommend")
        expected = instance | {"state": "Recommended", "version": instance["version"] + 1}
        assert result["instance"] == expected, "Continuation did not commit against the original preview instance."
        after = self.get_case(self.first)
        assert expected in after["observations"]["instances"]
        assert after["case"] == before["case"], "Runtime continuation changed the semantic case."
        assert self.get_case(self.second) == other_before, "Continuation touched the other case."
        expect(self.page.locator("#runtime-state")).to_have_text("Recommended")
        expect(self.page.locator("#runtime-result")).to_contain_text("Committed: Recommend.")
        self.assert_case_identity(after)
        return {"control": control, "case": self.first, "destination": self.second,
                "submitted_instance": instance, "continued_instance": expected,
                "failed_navigation_mutation_count": 0, "display_identity_retained": True}

    def successful_switch(self):
        before = self.get_case(self.first)
        other_before = self.get_case(self.second)
        expect(self.page.locator("#runtime-state")).to_have_text("Recommended")
        expect(self.page.locator("#runtime-result")).to_contain_text("Committed: Recommend.")
        posts = [x for x in self.requests if x["method"] != "GET"]
        self.switch(self.second, "dropdown")
        self.tab("try")
        self.assert_case_identity(other_before)
        expect(self.page.locator("#runtime-state")).to_have_text("Not started")
        expect(self.page.locator("#runtime-version")).to_have_text("No candidate state has been executed")
        expect(self.page.locator("#runtime-result")).to_have_text("")
        expect(self.page.locator("#runtime-actions button:enabled")).to_have_count(0)
        assert self.get_case(self.first) == before and self.get_case(self.second) == other_before
        assert [x for x in self.requests if x["method"] != "GET"] == posts
        return {"from_case": self.first, "to_case": self.second, "runtime_state": "Not started",
                "runtime_result": "", "all_actions_disabled": True, "authoritative_gets_unchanged": True}


    def busy_switch(self):
        before, ui, instance = self.prepare_submitted()
        other_before = self.get_case(self.second)
        marker = len(self.requests)
        self.hold_path = "/api/doctor"
        with self.page.expect_request(lambda r: r.method == "GET" and urlsplit(r.url).path == "/api/doctor"):
            self.page.locator("#doctor").click()
        expect(self.page.locator("body")).to_have_attribute("aria-busy", "true")
        assert self.held_route is not None, "The owned doctor's real GET was not held."
        self.page.locator("#case-switcher").select_option(self.second)
        self.assert_case_identity(before)
        assert self.ui_state() == ui, "Busy navigation changed the current preview or displayed case."
        assert self.requests[marker:] == [{"stage": self.stage, "method": "GET", "path": "/api/doctor"}], "Busy selection started a case navigation or write."
        assert self.get_case(self.first) == before and self.get_case(self.second) == other_before
        self.page.screenshot(path=str(self.out / "busy-dropdown-retained-submitted.png"), full_page=True)
        self.injected.append({"stage": self.stage, "path": "/api/doctor", "status": 503})
        self.held_route.fulfill(status=503, content_type="application/json", body=json.dumps({
            "code": "SYNTHETIC_DOCTOR_UNAVAILABLE", "message": "Regression fixture: held diagnostics GET failed.",
        }))
        self.held_route = None
        self.settled()
        expect(self.page.locator("#notice")).to_contain_text("SYNTHETIC_DOCTOR_UNAVAILABLE")
        assert self.ui_state() == ui
        self.assert_case_identity(before)
        assert self.get_case(self.first) == before and self.get_case(self.second) == other_before
        assert self.requests[marker:] == [{"stage": self.stage, "method": "GET", "path": "/api/doctor"}], "Busy completion queued a destination navigation or write."
        result = self.execute("Recommend")
        expected = instance | {"state": "Recommended", "version": instance["version"] + 1}
        assert result["instance"] == expected
        after = self.get_case(self.first)
        assert expected in after["observations"]["instances"] and after["case"] == before["case"]
        assert self.get_case(self.second) == other_before
        expect(self.page.locator("#runtime-state")).to_have_text("Recommended")
        expect(self.page.locator("#runtime-result")).to_contain_text("Committed: Recommend.")
        self.assert_case_identity(after)
        return {"case": self.first, "ignored_destination": self.second, "held_get": "/api/doctor",
                "response": 503, "navigation_or_mutation_during_busy": False,
                "submitted_instance": instance, "continued_instance": expected}


def main():
    if not __debug__:
        emit({"status": "NOT_RUN", "reason": "Python optimization disables assertion oracles; rerun without -O/-OO."})
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    before = run_subject()
    write_json(out / "subject-before.json", before)
    result = {"schema": "eija.case-preview-browser.v1", "utc": datetime.now(UTC).isoformat(),
              "identity": "normal_source_review_required", "pack": "default_excursion", "provider": "offline",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "helpers": {p: file_identity(ROOT, p) for p in ("quality/hci/server.py", "tests/hci/self_dogfood_replay.py", "tests/hci/self_dogfood_subject.py")},
              "checks": [], "browser_closed": False, "server_closed": False, "status": "FAIL",
              "limits": "Synthetic fixture navigation only; no live provider, owner decisions or human-value measurement."}
    review = None
    server_address = None
    try:
        with studio_server("case-preview-browser", identity="release", timeout=60) as launch_url:
            server_url = urlsplit(launch_url)
            server_address = (server_url.hostname, server_url.port)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    context = browser.new_context(viewport={"width": 1600, "height": 1000}, reduced_motion="reduce")
                    page = context.new_page()
                    page.set_default_timeout(30000)
                    review = PreviewNavigation(page, out, launch_url)
                    review.entry()
                    review.first = review.create("A", candidate=True)
                    review.second = review.create("B")
                    for name, action in (
                        ("same-case-refresh", review.refresh_same),
                        ("failed-case-list-503", lambda: review.failed_switch("list")),
                        ("failed-dropdown-503", lambda: review.failed_switch("dropdown")),
                        ("busy-dropdown-doctor-503", review.busy_switch),
                        ("different-case-clears-preview", review.successful_switch),
                    ):
                        review.step(name, action)
                        emit({"check": name, "status": "PASS"})
                    assert len(review.injected) == 3
                    assert review.http_errors == review.injected, "Unexpected HTTP error or missing synthetic 503."
                    assert not review.errors and not review.forbidden
                    result["status"] = "PASS"
                finally:
                    try:
                        if review is not None:
                            page.screenshot(path=str(out / "final.png"), full_page=True)
                    finally:
                        browser.close()
                        result["browser_closed"] = True
        result["server_closed"] = True
    except Exception as error:
        result["status"] = "FAIL"
        message = str(error)
        if review is not None:
            message = message.replace(review.capability, "[test-capability]")
        result["error"] = {"type": type(error).__name__, "message": message}
        emit({"status": "FAIL", "error": result["error"]})
    finally:
        if server_address is not None:
            with socket.socket() as probe:
                probe.settimeout(0.2)
                result["server_closed"] = probe.connect_ex(server_address) != 0
        if not result["server_closed"] or not result["browser_closed"]:
            result["status"] = "FAIL"
        if review is not None:
            result.update({"checks": review.checks, "failed_stage": review.stage if result["status"] != "PASS" else None,
                           "requests": review.requests, "http_errors": review.http_errors, "injected": review.injected,
                           "javascript_errors": review.errors, "forbidden_attempts": review.forbidden,
                           "runtime_responses": review.runtime_responses})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
        after = run_subject()
        write_json(out / "subject-after.json", after)
        result["subject_preservation"] = compare_subjects(before, after)
        if result["subject_preservation"]["status"] != "UNCHANGED":
            result["status"] = "FAIL"
        result["subject_content_sha256"] = before["content_sha256"]
        write_json(out / "result.json", result)
        files = {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                 for p in sorted(out.iterdir()) if p.is_file()}
        write_json(out / "artifact-manifest.json", files)
    emit({"status": result["status"], "checks": len(result["checks"]),
                      "browser_closed": result["browser_closed"], "server_closed": result["server_closed"],
                      "subject": result["subject_preservation"]})
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
