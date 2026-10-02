"""Normal-identity disposable runtime feedback proof; no owner operations."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import traceback
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import self_dogfood_replay as replay
from case_preview_navigation import emit, write_json
from ide_journey_edges import Journey
from quality.hci.server import ROOT
from self_dogfood_subject import capture_subject, compare_subjects, file_identity


def subject():
    value = capture_subject(ROOT)
    for name in ("tests/hci/ide_journey_edges.py", "tests/hci/case_preview_navigation.py",
                 "tests/hci/runtime_evidence_review.py", "quality/hci/server.py"):
        value["files"][name] = file_identity(ROOT, name)
        value["scope"].append(name)
    value["content_sha256"] = hashlib.sha256(json.dumps(
        {name: item["sha256"] for name, item in value["files"].items()}, sort_keys=True,
    ).encode()).hexdigest()
    return value


class RuntimeReview(Journey):
    def __init__(self, page, out, base):
        super().__init__(page, out, base)
        self.runtime_responses = []
        self.observations = []
        self.execute_fault = None
        self.case_get_fault = None
        self.held_route = None
        self.faults = []

    def route(self, route):
        request = route.request
        path = urlsplit(request.url).path
        if request.method != "GET" and path.rsplit("/", 1)[-1] in {"verify", "approve", "apply", "export"}:
            self.requests.append({"stage": self.stage, "method": request.method, "path": path})
            self.forbidden.append(path)
            route.abort()
        elif request.method == "POST" and path.endswith("/execute") and self.execute_fault:
            fault, self.execute_fault = self.execute_fault, None
            self.requests.append({"stage": self.stage, "method": request.method, "path": path})
            record = {"stage": self.stage, "mode": fault, "path": path, "request": request.post_data_json}
            self.faults.append(record)
            if fault == "abort":
                route.abort("failed")
            elif fault == "invalid-after-commit":
                actual = route.fetch()
                assert actual.status == 200, "Invalid-response control requires an actual accepted server commit"
                record["actual_server_response"] = actual.json()
                route.fulfill(status=200, content_type="application/json", body="{ response interrupted")
            elif fault == "hold":
                self.held_route = route
            else:
                raise AssertionError("Unrecognized fault mode")
        elif request.method == "GET" and path == self.case_get_fault:
            self.case_get_fault = None
            self.requests.append({"stage": self.stage, "method": request.method, "path": path})
            self.faults.append({"stage": self.stage, "mode": "case-get-503", "path": path})
            route.fulfill(status=503, content_type="application/json", body=json.dumps({
                "code": "SYNTHETIC_REFRESH_UNAVAILABLE", "message": "Regression fixture: one refresh failed.",
            }))
        else:
            super().route(route)

    def ui(self):
        return {name: self.page.locator("#" + name).text_content() for name in (
            "runtime-state", "runtime-version", "runtime-result", "notice", "error-json",
        )}

    def view(self):
        return self.get("cases/" + self.case_id)

    def runtime_posts(self):
        return [r for r in self.requests if r["method"] == "POST" and r["path"].endswith("/execute")]

    def persisted_commit(self, view, response, request, required_effects):
        assert response["committed"] is True and response["duplicate"] is False
        instance = response["instance"]
        assert instance["case_id"] == self.case_id and instance["id"] == request["instance_id"]
        assert instance["version"] == request["expected_version"] + 1
        assert instance["model_hash"] == view["packet"]["subject"]["semantic"]
        assert [item for item in view["observations"]["instances"] if item["id"] == instance["id"]] == [instance]
        assert sorted(response["effects"]) == sorted(required_effects)
        events = [item for item in view["observations"]["events"]
                  if item["body"].get("operation_id") == request["operation_id"]]
        assert sorted(item["kind"] for item in events) == sorted(required_effects), "Persisted audit effect count/identity differs"
        for event in events:
            assert event["body"]["actor_id"] == request["actor_id"] and event["body"]["instance_id"] == instance["id"]
            assert event["body"]["result"] == response, "Audit result differs from acknowledged execution"
        assert view["observations"]["outbox"] == [], "EIJA audit-only fixture unexpectedly produced outbox effects"

    def feedback(self, expected_status, action=None):
        result = self.page.locator("#runtime-result")
        replay.expect(result).to_have_attribute("data-status", expected_status)
        replay.expect(result).to_be_visible()
        if action:
            replay.expect(result).to_contain_text(action)
            replay.expect(result).to_have_attribute("data-action", action)
            replay.expect(result).to_have_attribute("data-case-id", self.case_id)
            records = [item for item in [*self.runtime_responses, *self.faults]
                       if item.get("path") == "/api/cases/" + self.case_id + "/execute"
                       and item.get("request", {}).get("action") == action]
            assert records, "No actual request captured for displayed attempt identity"
            request = records[-1]["request"]
            for field in ("operation_id", "actor_id", "instance_id", "expected_version"):
                replay.expect(result).to_have_attribute("data-" + field.replace("_", "-"), str(request[field]))
            view = self.view()
            replay.expect(result).to_have_attribute("data-case-revision", str(view["case"]["version"]))
            replay.expect(result).to_have_attribute("data-semantic-hash", view["packet"]["subject"]["semantic"])
        return result.text_content()

    def fresh_preview(self):
        self.tab("model")
        self.create_candidate()
        view = self.view()
        model = view["case"]["candidate"]
        first = next(t for t in model["transitions"] if t["action"] == "Propose")
        actors = self.get("status")["pack"]["actors"]
        agent = next(a["id"] for a in actors if a["role"] == "Agent" and a["active"] and a["assigned"])
        owner = next(a["id"] for a in actors if a["role"] == "Owner" and a["active"] and a["assigned"])
        self.tab("try")
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path.endswith("/preview")) as pending:
            self.page.locator("#reset").click()
        assert pending.value.status == 200
        instance = pending.value.json()
        self.settled()
        assert instance["state"] == first["from_state"] and instance["version"] == 0
        replay.expect(self.page.locator("#runtime-state")).to_have_text(instance["state"])
        return {"view": view, "first": first, "agent": agent, "owner": owner, "instance": instance}

    def refresh(self):
        self.page.keyboard.press("Control+k")
        replay.expect(self.page.locator("#palette-search")).to_be_focused()
        self.page.keyboard.type("Refresh current model")
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        replay.expect(self.page.locator("#command-palette")).not_to_be_visible()
        self.settled()

    def execute(self, action, actor, status, *, keyboard=False):
        self.page.locator("#actor").select_option(actor)
        target = self.page.locator(f'#runtime-actions [data-action="{action}"]')
        with self.page.expect_response(lambda response: response.request.method == "POST"
                                       and urlsplit(response.url).path == f"/api/cases/{self.case_id}/execute") as pending:
            if keyboard:
                target.focus()
                target.press("Enter")
            else:
                target.click()
        response = pending.value
        body = response.json()
        self.runtime_responses.append({"stage": self.stage, "action": action, "status": response.status,
                                       "path": urlsplit(response.url).path,
                                       "request": response.request.post_data_json, "body": body})
        assert response.status == status, f"{action}: expected HTTP {status}, got {response.status}"
        self.settled()
        return body

    def denied_after_success(self):
        if self.page.url == "about:blank":
            self.entry()
        self.create_candidate()
        view = self.get("cases/" + self.case_id)
        model = view["case"]["candidate"]
        first = next(t for t in model["transitions"] if t["action"] == "Propose")
        denied = next(t for t in model["transitions"] if t["action"] == "SelectMeaning")
        assert first["from_state"] == model["initial_state"] and first["to_state"] == denied["from_state"]
        assert first["role"] == "Agent" and denied["role"] == "Owner", "Fixture must isolate a wrong-role denial"
        actors = self.get("status")["pack"]["actors"]
        actor = next(a["id"] for a in actors if a["role"] == first["role"] and a["active"] and a["assigned"])
        self.tab("try")
        self.page.locator("#reset").click()
        self.settled()
        replay.expect(self.page.locator("#runtime-state")).to_have_text(first["from_state"])
        self.stage = "allowed-propose"
        committed = self.execute(first["action"], actor, 200)
        assert committed["committed"] is True and committed["duplicate"] is False
        assert committed["instance"]["state"] == first["to_state"] and committed["instance"]["version"] == 1
        assert sorted(committed["effects"]) == sorted(first["required_effects"])
        before = self.get("cases/" + self.case_id)
        self.persisted_commit(before, committed, self.runtime_responses[-1]["request"], first["required_effects"])
        assert committed["instance"] in before["observations"]["instances"]
        allowed_ui = self.ui()
        replay.expect(self.page.locator("#runtime-result")).to_contain_text("Committed: Propose")
        self.shot("allowed-propose")
        self.stage = "denied-select-meaning"
        refusal = self.execute(denied["action"], actor, 409, keyboard=True)
        after = self.get("cases/" + self.case_id)
        denied_ui = self.ui()
        self.observations.append({"allowed": allowed_ui, "denied": denied_ui, "refusal": refusal,
                                  "persisted_case_equal": after["case"] == before["case"],
                                  "persisted_observations_equal": after["observations"] == before["observations"]})
        write_json(self.out / "display-observations.json", self.observations)
        self.shot("denied-before-refresh")
        assert after == before, "Denied attempt changed persisted case, instance, audit/effect records or packet"
        replay.expect(self.page.locator("#runtime-state")).to_have_text(first["to_state"])
        assert denied_ui["runtime-version"] == allowed_ui["runtime-version"], "Denial changed displayed persisted version"
        assert refusal["code"] in denied_ui["error-json"], "Actual refusal absent from diagnostic"
        executes = [r for r in self.requests if r["method"] == "POST" and r["path"].endswith("/execute")]
        assert len(executes) == 2, "An activation sent a duplicate execute request"
        assert denied_ui["runtime-result"] != allowed_ui["runtime-result"], (
            "Latest denied SelectMeaning still displays the preceding Committed: Propose as its Run result"
        )
        assert "SelectMeaning" in denied_ui["runtime-result"] and refusal["code"] in denied_ui["runtime-result"], (
            "Latest Run attempt omits its action or authoritative denial code"
        )
        if self.strict_ux:
            self.feedback("refused", "SelectMeaning")
            audit = self.page.locator("#runtime-audit")
            assert audit.get_attribute("open") is None, "Runtime audit starts expanded"
            audit.locator(":scope > summary").focus()
            audit.locator(":scope > summary").press("Enter")
            replay.expect(self.page.locator("#trace")).to_be_visible()
            assert json.loads(self.page.locator("#trace").text_content()) == after["observations"], "Opened audit omits persisted facts"
            self.refresh()
            replay.expect(audit).to_have_attribute("open", "")
            assert json.loads(self.page.locator("#trace").text_content()) == after["observations"]
            self.page.locator('[data-bottom="problems-pane"]').click()
            replay.expect(self.page.locator("#problems")).to_be_visible()
            replay.expect(self.page.locator("#problems")).to_contain_text("SOURCE_REVIEW_REQUIRED")
            identity = self.page.locator("#runtime-attempt-details")
            if identity.get_attribute("open") is None:
                identity.locator(":scope > summary").focus()
                identity.locator(":scope > summary").press("Enter")
            exact = self.page.locator("#runtime-attempt-identity")
            replay.expect(exact).to_be_visible()
            replay.expect(identity).to_contain_text(refusal["code"])
            replay.expect(identity).to_contain_text(refusal["message"])
            for field in ("operation_id", "actor_id", "instance_id"):
                replay.expect(exact).to_contain_text(self.runtime_responses[-1]["request"][field])
        return {"allowed_action": first["action"], "denied_action": denied["action"],
                "refusal_code": refusal["code"], "persisted_state_unchanged_by_denial": True, "execute_requests": 2}

    def transport_unknown(self):
        setup = self.fresh_preview()
        committed = self.execute("Propose", setup["agent"], 200)
        before = self.view()
        count = len(self.runtime_posts())
        self.page.locator("#actor").select_option(setup["owner"])
        self.execute_fault = "abort"
        with self.page.expect_event("requestfailed", predicate=lambda r: urlsplit(r.url).path.endswith("/execute")):
            self.page.locator('#runtime-actions [data-action="SelectMeaning"]').click()
        self.settled()
        after = self.view()
        assert after == before, "Abort-before-forward control unexpectedly changed persisted facts"
        text = self.feedback("unknown", "SelectMeaning")
        assert "unknown" in text.lower(), "Transport failure is presented as a confirmed refusal or commit"
        replay.expect(self.page.locator("#runtime-state")).to_have_text(committed["instance"]["state"])
        replay.expect(self.page.locator("#runtime-last-commit")).to_contain_text("Propose")
        assert len(self.runtime_posts()) == count + 1, "Transport failure triggered automatic duplicate submission"
        return {"actual_fixture_commit": False, "displayed_outcome": "unknown", "automatic_retry": False}

    def invalid_response_unknown(self):
        setup = self.fresh_preview()
        before = self.view()
        count = len(self.runtime_posts())
        self.page.locator("#actor").select_option(setup["agent"])
        self.execute_fault = "invalid-after-commit"
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path.endswith("/execute")):
            self.page.locator('#runtime-actions [data-action="Propose"]').click()
        self.settled()
        after = self.view()
        actual = self.faults[-1]["actual_server_response"]
        self.persisted_commit(after, actual, self.faults[-1]["request"], setup["first"]["required_effects"])
        assert actual["committed"] is True and actual["duplicate"] is False
        assert actual["instance"] in after["observations"]["instances"]
        assert actual["instance"]["version"] == setup["instance"]["version"] + 1
        assert sorted(actual["effects"]) == sorted(setup["first"]["required_effects"])
        assert before["observations"] != after["observations"], "Control failed to commit a real operation"
        text = self.feedback("unknown", "Propose")
        assert "unknown" in text.lower(), "Malformed commit response is falsely presented as definite success/refusal"
        replay.expect(self.page.locator("#runtime-state")).to_have_text(setup["instance"]["state"])
        assert len(self.runtime_posts()) == count + 1, "Invalid response caused automatic execution retry"
        return {"actual_fixture_commit": True, "displayed_outcome": "unknown", "automatic_retry": False}

    def committed_refresh_failed(self):
        setup = self.fresh_preview()
        before_count = len(self.runtime_posts())
        self.case_get_fault = "/api/cases/" + self.case_id
        committed = self.execute("Propose", setup["agent"], 200)
        view = self.view()
        self.persisted_commit(view, committed, self.runtime_responses[-1]["request"], setup["first"]["required_effects"])
        assert committed["instance"] in view["observations"]["instances"]
        text = self.feedback("committed", "Propose")
        assert "refresh" in text.lower() and any(word in text.lower() for word in ("failed", "unavailable")), (
            "Acknowledged commit omits the failed case refresh qualifier"
        )
        replay.expect(self.page.locator("#runtime-state")).to_have_text(committed["instance"]["state"])
        self.shot("committed-refresh-failed-before-retry")
        self.refresh()
        assert self.view() == view, "GET-only reconciliation changed persisted case/instance/effects"
        assert len(self.runtime_posts()) == before_count + 1, "Refresh recovery re-executed the action"
        self.feedback("committed", "Propose")
        return {"commit_acknowledged": True, "refresh_failed": True, "recovery_execute_count": 0}

    def context_isolation(self):
        setup = self.fresh_preview()
        committed = self.execute("Propose", setup["agent"], 200)
        view = self.view()
        first_case = self.case_id
        previous_result = self.page.locator("#runtime-result").evaluate("n=>({text:n.textContent,data:{...n.dataset}})")
        self.refresh()
        assert self.view() == view
        assert self.page.locator("#runtime-result").evaluate("n=>({text:n.textContent,data:{...n.dataset}})") == previous_result
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path.endswith("/preview")) as pending:
            self.page.locator("#reset").click()
        reset = pending.value.json()
        self.settled()
        assert reset["id"] != committed["instance"]["id"] and reset["version"] == 0
        self.feedback("preview")
        assert not self.page.locator("#runtime-result").get_attribute("data-operation-id"), "Reset retained old execute identity"
        assert not self.page.locator("#runtime-last-commit").text_content().strip(), "Reset retained another instance's commit"
        self.execute("Propose", setup["agent"], 200)
        self.tab("model")
        self.select_transition("TR-SAVE")
        self.page.locator("#transition-role").select_option("Agent")
        preview_before = self.edit_preview_snapshot()
        preview_expected = json.loads(json.dumps(view["case"]["candidate"]))
        next(rule for rule in preview_expected["transitions"] if rule["id"] == "TR-SAVE")["role"] = "Agent"
        self.page.locator("#edit-role").click()
        preview = self.inspect_edit_preview(preview_before, preview_expected)
        self.apply_edit_preview(preview_before, preview)
        changed = self.view()
        assert changed["packet"]["subject"]["semantic"] != view["packet"]["subject"]["semantic"]
        expected = json.loads(json.dumps(view["case"]["candidate"]))
        next(rule for rule in expected["transitions"] if rule["id"] == "TR-SAVE")["role"] = "Agent"
        assert changed["case"]["candidate"] == expected, "Fixture edit changed more than the Save role"
        self.tab("try")
        replay.expect(self.page.locator("#runtime-state")).to_have_text("Not started")
        assert not self.page.locator("#runtime-result").get_attribute("data-operation-id"), "Candidate edit retained stale operation"
        assert not self.page.locator("#runtime-last-commit").text_content().strip(), "Candidate edit retained stale commit"
        self.page.locator('[data-bottom="history-pane"]').click()
        self.page.locator("#history-undo").focus()
        self.page.locator("#history-undo").press("Enter")
        self.settled()
        assert self.view()["case"]["candidate"] == view["case"]["candidate"], "History undo from Run did not restore prior candidate"
        self.tab("evidence")
        self.page.locator('[data-bottom="history-pane"]').click()
        self.page.locator("#history-redo").focus()
        self.page.locator("#history-redo").press("Enter")
        self.settled()
        assert self.view()["case"]["candidate"] == changed["case"]["candidate"], "History redo from Evidence did not restore edited candidate"
        self.fresh_preview()
        assert self.case_id != first_case
        self.switch_case(first_case)
        self.tab("try")
        replay.expect(self.page.locator("#runtime-state")).to_have_text("Not started")
        assert not self.page.locator("#runtime-result").get_attribute("data-operation-id"), "Case switch leaked operation identity"
        assert not self.page.locator("#runtime-last-commit").text_content().strip(), "Case switch leaked acknowledged commit"
        return {"same_case_retained": True, "reset_isolated": True, "semantic_edit_clears": True,
                "cross_case_clears": True, "keyboard_history_undo_from_run_redo_from_evidence": True}

    def creation_entry(self):
        self.entry()
        observations = []
        for width, height in ((1440, 900), (320, 800)):
            self.page.set_viewport_size({"width": width, "height": height})
            replay.expect(self.page.locator("#start-intent")).to_be_visible()
            replay.expect(self.page.locator("#new-case")).to_have_count(0)
            controls = self.page.locator("button").evaluate_all("""nodes=>nodes.filter(n=>n.checkVisibility()
              && /new (intent|change case)/i.test(n.getAttribute('aria-label')||n.textContent)).map(n=>n.id)""")
            assert controls == ["start-intent"], "Duplicate or missing visible creation entry"
            observations.append({"viewport": [width, height], "visible_creation_controls": controls})
            self.shot("single-creation-entry-" + str(width))
        self.page.set_viewport_size({"width": 1440, "height": 900})
        return {"observations": observations, "case_creation_required_sidebar": False}

    def busy_keyboard(self):
        setup = self.fresh_preview()
        count = len(self.runtime_posts())
        self.page.locator("#actor").select_option(setup["agent"])
        target = self.page.locator('#runtime-actions [data-action="Propose"]')
        self.execute_fault = "hold"
        target.focus()
        with self.page.expect_request(lambda r: r.method == "POST" and urlsplit(r.url).path.endswith("/execute")):
            target.press("Enter")
        replay.expect(self.page.locator("body")).to_have_attribute("aria-busy", "true")
        self.feedback("pending", "Propose")
        assert self.held_route is not None, "Fixture did not retain the pending execute"
        self.page.keyboard.press("Enter")
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path.endswith("/execute")) as pending:
            route, self.held_route = self.held_route, None
            route.continue_()
        assert pending.value.status == 200
        committed = pending.value.json()
        self.runtime_responses.append({"stage": self.stage, "action": "Propose", "status": pending.value.status,
                                       "path": urlsplit(pending.value.url).path,
                                       "request": pending.value.request.post_data_json, "body": committed})
        self.settled()
        view = self.view()
        assert committed["instance"] in view["observations"]["instances"]
        self.persisted_commit(view, committed, self.runtime_responses[-1]["request"], setup["first"]["required_effects"])
        assert committed["instance"]["version"] == 1 and committed["duplicate"] is False
        assert len(self.runtime_posts()) == count + 1, "Busy keyboard activation submitted more than once"
        self.feedback("committed", "Propose")
        replay.expect(self.page.locator('#runtime-actions [data-action="Propose"]')).to_be_focused()
        return {"keyboard_activations": 2, "execute_requests": 1, "committed_version": 1}


def main():
    if not __debug__:
        emit({"status": "NOT_RUN", "reason": "Assertions require unoptimized Python"})
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scenario", choices=("baseline", "all"), default="baseline")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    before = subject()
    write_json(out / "subject-before.json", before)
    script = Path(__file__).read_bytes()
    (out / "replay-script.py").write_bytes(script)
    result = {"schema": "eija.runtime-evidence-browser.v1", "status": "FAIL", "utc": datetime.now(UTC).isoformat(),
              "identity": "normal_source_review_required", "provider": "offline", "scenario": args.scenario, "checks": [],
              "script_sha256": hashlib.sha256(script).hexdigest(), "browser_closed": False, "server_closed": False,
              "not_run": ["uncertain network/invalid response", "committed then refresh failed", "runtime context isolation",
                          "human usability", "live provider", "owner approval/apply"]}
    review, address = None, None
    try:
        with replay.disposable_server() as base:
            endpoint = urlsplit(base)
            address = (endpoint.hostname, endpoint.port)
            with replay.sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    review = RuntimeReview(page, out, base)
                    review.strict_ux = args.scenario == "all"
                    steps = [("denied-after-success", review.denied_after_success)]
                    if args.scenario == "all":
                        steps = [("single-creation-entry", review.creation_entry), *steps,
                                 ("transport-outcome-unknown", review.transport_unknown),
                                 ("invalid-response-after-real-commit", review.invalid_response_unknown),
                                 ("committed-refresh-failed", review.committed_refresh_failed),
                                 ("context-history-isolation", review.context_isolation),
                                 ("busy-keyboard-no-duplicate", review.busy_keyboard)]
                        result["not_run"] = ["human usability", "live provider", "owner approval/apply"]
                    for name, action in steps:
                        review.stage = name
                        evidence = action()
                        result["checks"].append({"id": name, "status": "PASS", "evidence": evidence})
                        review.shot(name)
                        emit({"check": name, "status": "PASS"})
                    assert not review.errors and not review.forbidden
                    actual_errors = sorted((item["status"], item["path"]) for item in review.http_errors)
                    expected_errors = sorted([(item["status"], item["path"]) for item in review.runtime_responses
                                              if item["status"] >= 400]
                                             + [(503, item["path"]) for item in review.faults if item["mode"] == "case-get-503"])
                    assert actual_errors == expected_errors, "Unexpected HTTP errors occurred beyond named controls"
                    result["status"] = "PASS"
                finally:
                    try:
                        if review:
                            review.shot("final")
                    finally:
                        browser.close()
                        result["browser_closed"] = True
    except Exception as error:
        result["error"] = {"message": str(error).replace(replay.TEST_CAPABILITY, "[test-capability]"),
                           "traceback": traceback.format_exc().replace(replay.TEST_CAPABILITY, "[test-capability]")}
    finally:
        if address:
            with socket.socket() as sock:
                sock.settimeout(.2)
                result["server_closed"] = sock.connect_ex(address) != 0
        if review:
            result.update({"requests": review.requests, "javascript_errors": review.errors, "http_errors": review.http_errors,
                           "forbidden_attempts": review.forbidden, "runtime_responses": review.runtime_responses,
                           "fault_controls": review.faults,
                           "failed_stage": review.stage if result["status"] != "PASS" else None})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
        after = subject()
        write_json(out / "subject-after.json", after)
        result["subject_preservation"] = compare_subjects(before, after)
        result["subject_content_sha256"] = before["content_sha256"]
        if result["subject_preservation"]["status"] != "UNCHANGED" or not result["browser_closed"] or not result["server_closed"]:
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                                   for p in sorted(out.rglob("*")) if p.is_file()})
    emit({key: result[key] for key in ("status", "browser_closed", "server_closed", "checks")})
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
