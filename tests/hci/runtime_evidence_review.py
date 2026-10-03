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
        self.case_get_diagnostic = None
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
            diagnostic, self.case_get_diagnostic = self.case_get_diagnostic, None
            body = diagnostic or {
                "code": "SYNTHETIC_REFRESH_UNAVAILABLE", "message": "Regression fixture: one refresh failed.",
            }
            mode = "case-get-diagnostic-overflow" if diagnostic else "case-get-503"
            self.faults.append({"stage": self.stage, "mode": mode, "path": path, "response": body})
            route.fulfill(status=503, content_type="application/json", body=json.dumps(body))
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
            self.open_bottom("problems-pane")
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
        self.open_bottom("history-pane")
        self.page.locator("#history-undo").focus()
        self.page.locator("#history-undo").press("Enter")
        self.settled()
        assert self.view()["case"]["candidate"] == view["case"]["candidate"], "History undo from Run did not restore prior candidate"
        self.tab("evidence")
        self.open_bottom("history-pane")
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

    def raw_region_keyboard(self, selector, expected, label, *, status_text=False):
        """Real Tab entry and native scrolling; content and server state have separate oracles."""
        region = self.page.locator(selector)
        entry_trail = []
        if status_text:
            entry = self.page.locator('.editor-navigation [data-tab][aria-current="page"]')
            replay.expect(entry).to_have_count(1)
            entry_view = entry.get_attribute("data-tab")
            entry.focus()
            for _ in range(6):
                self.page.keyboard.press("Tab")
                entry_trail.append(self.page.evaluate("() => ({id:document.activeElement.id, tag:document.activeElement.tagName})"))
                if region.evaluate("n => document.activeElement === n"):
                    break
        else:
            disclosure = region.locator("..")
            summary = disclosure.locator(":scope > summary")
            summary.focus()
            if disclosure.get_attribute("open") is None:
                summary.press("Enter")
            summary.focus()
            self.page.keyboard.press("Tab")
        replay.expect(region).to_be_visible()
        before_text = region.text_content()
        actual = before_text if status_text else json.loads(before_text)
        assert actual == expected, f"{selector}: raw data does not match its independent oracle"
        replay.expect(region).to_be_focused()
        replay.expect(region).to_have_attribute("role", "status" if status_text else "region")
        replay.expect(region).to_have_attribute("aria-label", label)
        if status_text:
            replay.expect(region).to_have_attribute("aria-live", "polite")
        geometry = region.evaluate("""n => {
            const style = getComputedStyle(n);
            return {clientHeight:n.clientHeight, scrollHeight:n.scrollHeight,
                    focusVisible:n.matches(':focus-visible'), outlineStyle:style.outlineStyle,
                    outlineWidth:parseFloat(style.outlineWidth), outlineColor:style.outlineColor};
        }""")
        assert geometry["scrollHeight"] > geometry["clientHeight"] + 2, f"{selector}: overflow was not exercised"
        assert geometry["focusVisible"] and geometry["outlineStyle"] != "none" and geometry["outlineWidth"] >= 2
        def capture_scroll(checkpoint):
            observed = region.evaluate("""n => {
                const chain = [];
                for (let node = n; node; node = node.parentElement) {
                    const rect = node.getBoundingClientRect(), style = getComputedStyle(node);
                    chain.push({id:node.id, tag:node.tagName, scrollTop:node.scrollTop,
                                scrollLeft:node.scrollLeft, clientHeight:node.clientHeight,
                                scrollHeight:node.scrollHeight, overflowY:style.overflowY,
                                rect:{x:rect.x,y:rect.y,width:rect.width,height:rect.height}});
                }
                return {viewport:[innerWidth,innerHeight], focused:document.activeElement===n,
                        activeId:document.activeElement?.id, activeTag:document.activeElement?.tagName,
                        nativeScroll:n.__eijaQaRawScroll || null, chain};
            }""")
            observations = getattr(self, "raw_scroll_observations", [])
            observations.append({"region": selector, "checkpoint": checkpoint, **observed})
            self.raw_scroll_observations = observations
            write_json(self.out / "raw-scroll-observations.json", observations)

        def arm_scroll_end(key):
            supported = region.evaluate("""(n, key) => {
                const state = {key, supported:'onscrollend' in n, ended:false, events:[]};
                n.__eijaQaRawScroll = state;
                if (state.supported) {
                    const finished = event => {
                        if (event.target !== n) return;
                        state.events.push({type:event.type, isTrusted:event.isTrusted, scrollTop:n.scrollTop});
                        state.ended = event.isTrusted;
                        n.removeEventListener('scrollend', finished);
                    };
                    n.addEventListener('scrollend', finished);
                }
                return state.supported;
            }""", key)
            capture_scroll("armed-" + key)
            assert supported, f"{selector}: NOT_RUN native scrollend is required for keyboard-scroll synchronization"

        def wait_scroll_end():
            self.page.wait_for_function("s => document.querySelector(s).__eijaQaRawScroll?.ended === true",
                                        arg=selector)

        capture_scroll("before-Control+Home")
        try:
            if region.evaluate("n => n.scrollTop") != 0:
                arm_scroll_end("Control+Home")
                region.press("Control+Home")
                self.page.wait_for_function("s => document.querySelector(s).scrollTop === 0", arg=selector)
                wait_scroll_end()
                capture_scroll("Control+Home-scroll-complete")
            else:
                capture_scroll("Control+Home-skipped-already-at-top")
            self.page.wait_for_function("s => document.querySelector(s).scrollTop === 0", arg=selector)
            capture_scroll("at-top-before-PageDown")
            arm_scroll_end("PageDown")
            region.press("PageDown")
            capture_scroll("PageDown-dispatched")
            self.page.wait_for_function("s => document.querySelector(s).scrollTop > 0", arg=selector)
            capture_scroll("PageDown-movement-observed")
            wait_scroll_end()
            after_scroll = region.evaluate("n => n.scrollTop")
            assert after_scroll > 0, f"{selector}: native completion lost the required region scroll"
            capture_scroll("PageDown-scroll-complete")
        except Exception:
            capture_scroll("scroll-failure")
            viewport = self.page.viewport_size
            self.shot(f"raw-scroll-failure-{selector.removeprefix('#')}-{viewport['width']}")
            raise
        if status_text:
            self.shot(f"notice-keyboard-focused-{entry_view}-{self.page.viewport_size['width']}")
        self.page.keyboard.press("Tab")
        replay.expect(region).not_to_be_focused()
        forward_exit = self.page.evaluate("() => document.activeElement.id || document.activeElement.tagName")
        self.page.keyboard.press("Shift+Tab")
        replay.expect(region).to_be_focused()
        self.page.keyboard.press("Shift+Tab")
        if status_text:
            replay.expect(region).not_to_be_focused()
            backward_exit = self.page.evaluate("() => document.activeElement.id || document.activeElement.tagName")
        else:
            replay.expect(summary).to_be_focused()
            backward_exit = "parent summary"
        assert region.text_content() == before_text, f"{selector}: navigation changed raw bytes"
        return {"region": selector, "geometry": geometry, "scrollTopAfterPageDown": after_scroll,
                "forwardExit": forward_exit, "backwardExit": backward_exit, "entryTrail": entry_trail,
                "exact_data_unchanged": True}

    def raw_diagnostics_keyboard(self):
        """Opened overflow states: actual packet/audit and an explicitly synthetic oversized error."""
        if self.page.url == "about:blank":
            self.entry()
        setup = self.fresh_preview()
        self.execute("Propose", setup["agent"], 200)
        before = self.view()
        before_posts = len([r for r in self.requests if r["method"] == "POST"])
        self.page.locator("#start-intent").click()
        replay.expect(self.page.locator("#notice")).to_have_text("")
        replay.expect(self.page.locator("#notice")).not_to_be_visible()
        self.tab("try")
        assert self.view() == before, "Opening an unsent intent changed the persisted subject"
        assert len([r for r in self.requests if r["method"] == "POST"]) == before_posts
        self.case_get_fault = "/api/cases/" + self.case_id
        fixture = {
            "code": "SYNTHETIC_DIAGNOSTIC_OVERFLOW",
            "message": "Synthetic oversized diagnostic: keyboard scrolling coverage only; no kernel decision.",
            "details": {"fixture": "raw-diagnostic-keyboard-overflow", "lines": [
                f"Synthetic diagnostic line {number:02d}: retain this exact value while scrolling."
                for number in range(48)
            ]},
        }
        self.case_get_diagnostic = fixture
        self.refresh()
        expected_error = {"code": fixture["code"], "message": fixture["code"] + ": " + fixture["message"],
                          "details": fixture["details"]}
        assert self.view() == before, "The one-GET diagnostic fixture changed persisted data"
        posts = len([r for r in self.requests if r["method"] == "POST"])
        observations, audits = [], []
        axe = replay.Axe.from_file(replay.AXE_FILE_PATH)
        try:
            for width, height in ((1440, 900), (1280, 800), (320, 800)):
                self.page.set_viewport_size({"width": width, "height": height})
                self.tab("try")
                self.open_bottom("problems-pane")
                rows = [self.raw_region_keyboard("#trace", before["observations"],
                                                "Persisted audit and simulated outbox"),
                        self.raw_region_keyboard("#error-json", expected_error, "Exact server diagnostic")]
                for view in ("try", "evidence"):
                    if view == "evidence":
                        self.tab(view)
                        rows.append(self.raw_region_keyboard("#packet", before["packet"],
                                                             "Raw review packet and source-review boundary"))
                    if width == 320:
                        rows.append(self.raw_region_keyboard("#notice", expected_error["message"],
                                                             "Workspace status and diagnostic", status_text=True))
                    result = axe.run(self.page, options={
                        "runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]},
                        "resultTypes": ["violations", "incomplete"],
                    }).response
                    audits.append({"viewport": [width, height], "view": view, "axe_version": result["testEngine"]["version"],
                                   "violations": result["violations"], "incomplete": result["incomplete"]})
                    write_json(self.out / "axe-open-raw-diagnostics.json", audits)
                    self.shot(f"raw-diagnostics-{view}-{width}")
                observations.append({"viewport": [width, height], "regions": rows})
                write_json(self.out / "raw-diagnostics-keyboard.json", observations)
                assert self.view() == before, "Keyboard raw-data inspection changed persisted facts"
                assert len([r for r in self.requests if r["method"] == "POST"]) == posts
            # The behavioral oracle must detect deliberate removal from sequential keyboard navigation.
            region = self.page.locator("#packet")
            summary = region.locator("..").locator(":scope > summary")
            original = region.get_attribute("tabindex")
            try:
                region.evaluate("n => n.tabIndex = -1")
                summary.focus()
                self.page.keyboard.press("Tab")
                assert not region.evaluate("n => n === document.activeElement"), "Negative control did not omit keyboard entry"
            finally:
                region.evaluate("(n, value) => value === null ? n.removeAttribute('tabindex') : n.setAttribute('tabindex', value)", original)
            summary.focus()
            self.page.keyboard.press("Tab")
            replay.expect(region).to_be_focused()
            assert json.loads(region.text_content()) == before["packet"]
            assert not any(audit["violations"] for audit in audits), "Opened raw-region axe violations: inspect retained report"
        finally:
            self.page.set_viewport_size({"width": 1440, "height": 900})
        return {"viewports": observations, "error_fixture": fixture, "actual_packet_and_audit": True,
                "notice_keyboard_scope": "Actual overflowing status on Run and Evidence at 320x800",
                "empty_notice_hidden": True,
                "persisted_data_unchanged": True, "keyboard_omission_control": True,
                "axe_violations": 0, "axe_incomplete": sum(len(audit["incomplete"]) for audit in audits),
                "scope": "Synthetic accessibility checks; not a human usability study or real oversized server failure."}

    def triage_keyboard_entry(self, selector):
        """Start at real Evidence navigation, then reach the target only with native Tab."""
        self.tab("evidence")
        entry = self.page.locator('[data-tab="evidence"]')
        entry.focus()
        target, trail = self.page.locator(selector), []
        replay.expect(target).to_have_count(1)
        for _ in range(24):
            self.page.keyboard.press("Tab")
            trail.append(self.page.evaluate("""()=>({id:document.activeElement.id,tag:document.activeElement.tagName,
                blocker:document.activeElement.dataset.blockerCode||null})"""))
            if target.evaluate("n=>document.activeElement===n"):
                break
        replay.expect(target).to_be_focused()
        return {"selector": selector, "native_tab_trail": trail, "geometry": self.triage_focus_geometry(target)}

    def triage_focus_geometry(self, target):
        replay.expect(target).to_be_focused()
        geometry = target.evaluate("""n=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n);
            let clip={left:0,top:0,right:innerWidth,bottom:innerHeight};
            for(let p=n.parentElement;p;p=p.parentElement){const c=getComputedStyle(p),b=p.getBoundingClientRect();
                if(/auto|scroll|hidden|clip/.test(c.overflowX)){clip.left=Math.max(clip.left,b.left);clip.right=Math.min(clip.right,b.right);}
                if(/auto|scroll|hidden|clip/.test(c.overflowY)){clip.top=Math.max(clip.top,b.top);clip.bottom=Math.min(clip.bottom,b.bottom);}}
            return {rect:r.toJSON(),clip,focusVisible:n.matches(':focus-visible'),outlineStyle:s.outlineStyle,
                outlineWidth:parseFloat(s.outlineWidth),documentWidth:document.documentElement.scrollWidth,width:innerWidth};}""")
        assert geometry["focusVisible"] and geometry["outlineStyle"] != "none" and geometry["outlineWidth"] >= 2
        box, clip = geometry["rect"], geometry["clip"]
        assert box["left"] >= clip["left"] - 1 and box["right"] <= clip["right"] + 1
        assert box["top"] >= clip["top"] - 1 and box["bottom"] <= clip["bottom"] + 1
        assert geometry["documentWidth"] <= geometry["width"] + 1
        return geometry

    def triage_evidence_inventory(self, view):
        packet = view["packet"]
        expected_claims = packet["technical_claims"]
        actual_claims = self.page.locator("#formal details[data-claim]").evaluate_all("""nodes=>nodes.map(n=>({
            name:n.dataset.claim,status:n.querySelector('summary .evidence-status').textContent}))""")
        assert len(actual_claims) == len(expected_claims)
        assert {row["name"]: row["status"] for row in actual_claims} == expected_claims
        actual_records = self.page.locator("#formal details[data-evidence-kind]").evaluate_all("""nodes=>nodes.map(n=>({
            kind:n.dataset.evidenceKind,index:n.dataset.evidenceIndex,
            status:n.querySelector('summary .evidence-status').textContent}))""")
        expected_records = [{"kind": row["kind"], "index": str(index), "status": row["status"]}
                            for index, row in enumerate(packet["formal_evidence"])]
        assert actual_records == expected_records, "Triage navigation changed the formal record inventory/order/status"
        assert self.packet() == packet
        subject = self.page.locator("#evidence-subject")
        for key, value in {"case-id": view["case"]["id"], "revision": str(view["case"]["version"]),
                           "subject-hash": packet["subject_hash"], "displayed-model": "working",
                           "comparison-case-id": view["case"]["id"], "comparison-revision": str(view["case"]["version"]),
                           "comparison-kind": "transition", "comparison-id": "TR-SAVE"}.items():
            replay.expect(subject).to_have_attribute("data-" + key, value)
        replay.expect(subject).to_contain_text("Model inspector selection: transition · TR-VERIFY")
        replay.expect(subject).to_contain_text("Evidence scope: case-wide")
        replay.expect(self.page.locator("#evidence .human-status")).to_contain_text("Human comprehension: UNKNOWN")
        replay.expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        return {"claims": actual_claims, "formal_records": actual_records}

    def evidence_triage(self):
        """Actual packet blockers and keyboard destinations; no fabricated check payloads."""
        if self.page.url == "about:blank":
            self.entry()
        self.create_candidate()
        before = self.view()
        history = self.get(f"cases/{self.case_id}/history")
        writes = [row for row in self.requests if row["method"] != "GET"]
        packet = before["packet"]
        assert "SOURCE_REVIEW_REQUIRED" in packet["blockers"]
        assert "RUNTIME_EVIDENCE_UNKNOWN" in packet["blockers"] and packet["technical_claims"]["runtime_matrix"] == "UNKNOWN"
        assert packet["human_understanding"] == "UNKNOWN" and not packet["eligible"]
        self.select_transition("TR-VERIFY")
        self.select_comparison("transition", "TR-SAVE")
        self.tab("evidence")
        observations = []
        try:
            for width, height in ((1280, 800), (320, 800)):
                self.page.set_viewport_size({"width": width, "height": height})
                self.tab("evidence")
                triage = self.page.locator("#evidence-triage")
                actual = triage.locator("li[data-blocker-code]").evaluate_all("nodes=>nodes.map(n=>n.dataset.blockerCode)")
                assert actual == packet["blockers"], "Visible triage inventory/order differs from the actual packet"
                replay.expect(triage).to_have_attribute("data-case-id", self.case_id)
                replay.expect(triage).to_have_attribute("data-revision", str(before["case"]["version"]))
                replay.expect(triage).to_have_attribute("data-subject-hash", packet["subject_hash"])
                for code in packet["blockers"]:
                    row = triage.locator(f'li[data-blocker-code="{code}"]')
                    replay.expect(row).to_be_visible()
                    assert row.locator("strong").inner_text().strip() and row.locator("p").inner_text().strip()
                replay.expect(triage).to_contain_text("Runtime evidence · UNKNOWN")
                replay.expect(triage).to_contain_text("Source review required")
                inventory = self.triage_evidence_inventory(before)
                self.shot(f"evidence-triage-entry-{width}")
                source = self.triage_keyboard_entry('#evidence-triage button[data-blocker-code="SOURCE_REVIEW_REQUIRED"]')
                self.page.keyboard.press("Enter")
                target = self.page.locator("#source-review-problem")
                replay.expect(target).to_be_focused()
                replay.expect(target).to_be_visible()
                replay.expect(target).to_have_attribute("data-problem-code", "SOURCE_REVIEW_REQUIRED")
                replay.expect(self.page.locator("#problems-pane")).to_be_visible()
                source["focused_diagnostic"] = target.text_content()
                source["destination_geometry"] = self.triage_focus_geometry(target)
                self.shot(f"evidence-triage-source-diagnostic-{width}")
                self.page.locator("#collapse-bottom").click()
                runtime = self.triage_keyboard_entry('#evidence-triage button[data-blocker-code="RUNTIME_EVIDENCE_UNKNOWN"]')
                self.page.keyboard.press("Enter")
                check = self.page.locator('#formal details[data-claim="runtime_matrix"]')
                replay.expect(check).to_have_count(1)
                replay.expect(check).to_have_attribute("open", "")
                replay.expect(check.locator("summary")).to_be_focused()
                replay.expect(check.locator("summary .evidence-status")).to_have_text(packet["technical_claims"]["runtime_matrix"])
                runtime["focused_check"] = check.text_content()
                runtime["destination_geometry"] = self.triage_focus_geometry(check.locator("summary"))
                self.shot(f"evidence-triage-runtime-check-{width}")
                codes = self.triage_keyboard_entry(".evidence-blocker-codes > summary")
                disclosure = self.page.locator(".evidence-blocker-codes")
                if disclosure.get_attribute("open") is None:
                    self.page.keyboard.press("Enter")
                replay.expect(disclosure).to_have_attribute("open", "")
                replay.expect(self.page.locator("#blockers")).to_be_visible()
                replay.expect(self.page.locator("#blockers")).to_have_text("Review blocked: " + ", ".join(packet["blockers"]))
                self.shot(f"evidence-triage-exact-codes-{width}")
                self.page.keyboard.press("Enter")
                replay.expect(disclosure).not_to_have_attribute("open", "")
                assert self.triage_evidence_inventory(before) == inventory
                assert self.view() == before and self.get(f"cases/{self.case_id}/history") == history
                assert [row for row in self.requests if row["method"] != "GET"] == writes
                observations.append({"viewport": [width, height], "actual_blockers": actual, "inventory": inventory,
                                     "source": source, "runtime": runtime, "raw_codes": codes})
                write_json(self.out / "evidence-triage-keyboard.json", observations)
        finally:
            self.page.set_viewport_size({"width": 1440, "height": 900})
        return {"viewports": observations, "unchanged_case_history_observations": True, "navigation_writes": 0,
                "packet_fixture": "real normal-server packet; no verification/runtime command or synthetic response",
                "coverage_limit": "Malformed/duplicate/stale mapping counterexamples are Node-only; no human or axe claim."}

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
    parser.add_argument("--scenario", choices=("baseline", "all", "diagnostics", "triage"), default="baseline")
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
                                 ("busy-keyboard-no-duplicate", review.busy_keyboard),
                                 ("raw-diagnostics-keyboard", review.raw_diagnostics_keyboard),
                                 ("evidence-triage-keyboard", review.evidence_triage)]
                        result["not_run"] = ["human usability", "live provider", "owner approval/apply"]
                    if args.scenario == "diagnostics":
                        steps = [("raw-diagnostics-keyboard", review.raw_diagnostics_keyboard)]
                        result["not_run"] = ["other runtime recovery scenarios", "human usability", "live provider", "owner approval/apply"]
                    if args.scenario == "triage":
                        steps = [("evidence-triage-keyboard", review.evidence_triage)]
                        result["not_run"] = ["runtime recovery scenarios", "raw-diagnostic overflow", "axe audit",
                                             "malformed/duplicate/stale packet browser fixtures", "human usability",
                                             "live provider", "owner approval/apply"]
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
                                             + [(503, item["path"]) for item in review.faults if item["mode"] in {"case-get-503", "case-get-diagnostic-overflow"}])
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
