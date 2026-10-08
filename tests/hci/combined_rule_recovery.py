"""Same-case model-edit, runtime-refusal and repair journey on isolated offline EIJA.

Reuses the checkout's existing replay adapters and records source preservation.
Run browser/heavy checks serially. No fresh verification, approval or apply.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import socket
import sys
import traceback
from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_replay(repo):
    sys.path[:0] = [str(repo / "tests/hci"), str(repo / "src"), str(repo)]
    runtime = importlib.import_module("runtime_evidence_review")
    replay = importlib.import_module("self_dogfood_replay")
    compare_subjects = importlib.import_module("self_dogfood_subject").compare_subjects
    return runtime, replay, compare_subjects


def launch_headless(playwright, browser_error):
    """Let Playwright select its supported headless executable; retain real failures."""
    try:
        return playwright.chromium.launch(headless=True)
    except browser_error as error:
        if "Executable doesn't exist at " in str(error):
            raise ModuleNotFoundError("Configured Playwright headless executable is absent: " + str(error)) from error
        raise


def journey_type(runtime, replay):
    class CombinedJourney(runtime.RuntimeReview):
        """An orchestration of existing helpers, not another workflow interpreter."""

        def __init__(self, page, out, base):
            super().__init__(page, out, base)
            self.post_bodies, self.checkpoints, self.external_attempts = [], [], []
            self.baseline_case = None
            self.strict_ux = True
            page.route("**/*", self.local_only)

        def local_only(self, route):
            if urlsplit(route.request.url).netloc != urlsplit(self.base).netloc:
                self.external_attempts.append({"method": route.request.method,
                                               "origin": urlsplit(route.request.url).netloc})
                route.abort()
            else:
                route.fallback()

        def route(self, route):
            request = route.request
            path = urlsplit(request.url).path
            if path.rsplit("/", 1)[-1] in {"verify", "approve", "apply", "export"}:
                self.requests.append({"stage": self.stage, "method": request.method, "path": path})
                self.forbidden.append(path)
                route.abort()
                return
            if request.method != "GET":
                body = request.post_data_json
                self.post_bodies.append({"stage": self.stage, "path": path,
                                         "method": request.method, "body": body})
                allowed = path == "/api/cases" or bool(re.fullmatch(
                    r"/api/cases/[^/]+/(propose|select|edit/preview|edit|preview|execute|undo|redo)", path))
                if path.endswith("/execute"):
                    allowed = allowed and body.get("action") in {"Propose", "SelectMeaning", "Save"}
                if request.method != "POST" or not allowed:
                    self.requests.append({"stage": self.stage, "method": request.method, "path": path})
                    self.forbidden.append(path)
                    route.abort()
                    return
            super().route(route)

        def key(self, key, selector):
            self.page.keyboard.press(key)
            self.navigation_action("key", selector, key)

        def keyboard_to(self, selector):
            target = self.page.locator(selector)
            replay.expect(target).to_have_count(1)
            for _ in range(100):
                if target.evaluate("node=>node===document.activeElement"):
                    replay.expect(target).to_be_visible()
                    replay.expect(target).to_be_in_viewport()
                    return target
                self.key("Tab", "native traversal to " + selector)
            raise AssertionError("Native keyboard traversal cannot reach " + selector)

        def activate(self, selector):
            self.keyboard_to(selector)
            self.key("Enter", selector)
            self.settled()

        def keyboard_select(self, selector, value):
            target = self.keyboard_to(selector)
            values = target.locator("option").evaluate_all("nodes=>nodes.map(node=>node.value)")
            assert value in values, "Required select choice is unavailable: " + value
            self.key("Home", selector)
            for _ in range(values.index(value)):
                self.key("ArrowDown", selector)
            self.key("Tab", selector)
            replay.expect(target).to_have_value(value)

        def command(self, text, view=None):
            self.navigation_action("keyboard-command", "#command-palette", text)
            self.palette(text)
            if view:
                self.assert_view(view)

        def checkpoint(self, label):
            view = self.view()
            history = self.get(f"cases/{self.case_id}/history")
            packet = view["packet"]
            assert view["case"]["id"] == self.case_id
            assert view["case"]["stage"] == "PREVIEW", "Simulation changed the real change-case stage"
            assert view["case"]["decision"] is None and view["case"]["receipts"] == []
            if self.baseline_case:
                assert view["case"]["baseline"] == self.baseline_case["baseline"]
                assert view["case"]["baseline_version"] == self.baseline_case["baseline_version"]
            assert self.packet() == packet, "Displayed packet differs from authoritative GET"
            assert packet["human_understanding"] == "UNKNOWN" and packet["eligible"] is False
            assert packet["technical_claims"]["runtime_matrix"] == "UNKNOWN"
            assert "SOURCE_REVIEW_REQUIRED" in packet["blockers"]
            assert "RUNTIME_EVIDENCE_UNKNOWN" in packet["blockers"]
            replay.expect(self.page.locator("#case-stage")).to_have_text("PREVIEW")
            replay.expect(self.page.locator("#case-switcher")).to_have_value(self.case_id)
            assert self.revision() == view["case"]["version"]
            record = {"label": label, "view": view, "history": history,
                      "ui": self.ui(), "request_count": len(self.post_bodies)}
            self.checkpoints.append(record)
            write_json(self.out / "checkpoints.json", self.checkpoints)
            return record

        def semantic_event(self, before, after, kind, transaction):
            old, new = before["observations"], after["observations"]
            assert new["instances"] == old["instances"] and new["outbox"] == old["outbox"]
            assert new["events"][:-1] == old["events"], "Semantic command did not preserve the exact audit prefix plus one event"
            event = new["events"][-1]
            assert event["kind"] == kind
            body = event["body"]
            expected = {"case_id": self.case_id, "from_version": before["case"]["version"],
                "to_version": after["case"]["version"], "transaction": transaction,
                "before_semantic_hash": before["packet"]["subject"]["semantic"],
                "after_semantic_hash": after["packet"]["subject"]["semantic"], "discarded_redo": []}
            assert {key: value for key, value in body.items() if key not in {"by", "time"}} == expected
            assert isinstance(body["by"], str) and body["by"]
            assert datetime.fromisoformat(body["time"]).tzinfo is not None

        def select_save(self):
            self.command("Select a transition")
            replay.expect(self.page.locator("#transition-select")).to_be_focused()
            self.keyboard_select("#transition-select", "TR-SAVE")
            replay.expect(self.page.locator("#transition-details")).to_have_attribute(
                "data-eija-id", "eija-review-slice.transition-detail.TR-SAVE")

        def propose_role(self, role):
            before = self.edit_preview_snapshot()
            choice = self.role_choice("TR-SAVE", role, True)
            expected = deepcopy(before["view"]["case"]["candidate"])
            next(t for t in expected["transitions"] if t["id"] == "TR-SAVE")["role"] = role
            self.keyboard_select("#transition-role", role)
            self.activate("#edit-role")
            payload = self.inspect_edit_preview(before, expected, choice["transaction"])
            self.shot(self.stage + "-prospective-comparison")
            return before, payload, choice

        def start_runtime(self):
            self.command("Open Run", "try")
            before = self.checkpoint(self.stage + "-before-reset")
            count = len(self.post_bodies)
            with self.page.expect_response(lambda r: r.request.method == "POST"
                    and urlsplit(r.url).path == f"/api/cases/{self.case_id}/preview") as pending:
                self.activate("#reset")
            response = pending.value
            assert response.status == 200
            instance = response.json()
            after = self.checkpoint(self.stage + "-after-reset")
            assert len(self.post_bodies) == count + 1
            assert after["view"]["case"] == before["view"]["case"]
            assert after["history"] == before["history"]
            assert after["view"]["packet"] == before["view"]["packet"]
            assert after["view"]["observations"]["events"] == before["view"]["observations"]["events"]
            assert after["view"]["observations"]["outbox"] == before["view"]["observations"]["outbox"]
            assert [item for item in after["view"]["observations"]["instances"] if item["id"] != instance["id"]] == before["view"]["observations"]["instances"]
            assert instance["case_id"] == self.case_id and instance["version"] == 0
            assert instance["state"] == "DRAFT"
            assert instance["model_hash"] == after["view"]["packet"]["subject"]["semantic"]
            assert instance in after["view"]["observations"]["instances"]
            replay.expect(self.page.locator("#runtime-state")).to_have_text("DRAFT")
            self.feedback("preview")
            return instance

        def attempt(self, action, actor, expected_status, expected_state, version):
            before = self.checkpoint(self.stage + "-before-" + action)
            count = len(self.runtime_posts())
            self.keyboard_select("#actor", actor)
            with self.page.expect_response(lambda r: r.request.method == "POST"
                    and urlsplit(r.url).path == f"/api/cases/{self.case_id}/execute") as pending:
                self.activate(f'#runtime-actions [data-action="{action}"]')
            response = pending.value
            body, request = response.json(), response.request.post_data_json
            self.runtime_responses.append({"stage": self.stage, "action": action,
                "status": response.status, "path": urlsplit(response.url).path,
                "request": request, "body": body})
            assert response.status == expected_status
            assert request["action"] == action and request["actor_id"] == actor
            assert request["expected_version"] == (version - 1 if expected_status == 200 else version)
            assert len(self.runtime_posts()) == count + 1, "One activation sent duplicate runtime requests"
            after = self.checkpoint(self.stage + "-after-" + action)
            assert after["view"]["case"] == before["view"]["case"]
            assert after["history"] == before["history"]
            assert after["view"]["packet"] == before["view"]["packet"]
            if expected_status == 200:
                transition = next(t for t in after["view"]["case"]["candidate"]["transitions"] if t["action"] == action)
                self.persisted_commit(after["view"], body, request, transition["required_effects"])
                old_events = before["view"]["observations"]["events"]
                new_events = after["view"]["observations"]["events"]
                assert new_events[:len(old_events)] == old_events
                added = new_events[len(old_events):]
                assert len(added) == len(transition["required_effects"]), "Execute appended an extra/missing audit event"
                assert all(item["body"].get("operation_id") == request["operation_id"] for item in added)
                assert body["instance"]["state"] == expected_state and body["instance"]["version"] == version
                self.feedback("committed", action)
            else:
                assert body["code"] == "ROLE_DENIED"
                assert after["view"] == before["view"], "Refusal changed case/runtime/audit/evidence"
                assert before["ui"]["runtime-version"] == after["ui"]["runtime-version"]
                self.feedback("refused", action)
                assert body["code"] in self.page.locator("#error-json").text_content()
                replay.expect(self.page.locator("#runtime-last-commit")).to_contain_text("SelectMeaning")
            replay.expect(self.page.locator("#runtime-state")).to_have_text(expected_state)
            replay.expect(self.page.locator("#runtime-version")).to_contain_text("version " + str(version))
            self.shot(self.stage + "-" + action)
            return body

        def runtime_attempt_snapshot(self):
            return self.page.evaluate("""()=>({
                result:{text:document.querySelector('#runtime-result').textContent,dataset:{...document.querySelector('#runtime-result').dataset}},
                identity:[...document.querySelectorAll('#runtime-attempt-identity dt')].map(n=>[n.textContent,n.nextElementSibling.textContent]),
                last_commit:{text:document.querySelector('#runtime-last-commit').textContent,dataset:{...document.querySelector('#runtime-last-commit').dataset}},
                diagnostic:document.querySelector('#error-json').textContent})""")

        def assert_runtime_attempt_identity(self, snapshot, request, view):
            expected = {"Client request ID": request["operation_id"], "Operation ID": request["operation_id"],
                "Case": self.case_id, "Case revision at request": str(view["case"]["version"]),
                "Candidate semantic hash": view["packet"]["subject"]["semantic"],
                "Review subject hash at request": view["packet"]["subject_hash"],
                "Actor": request["actor_id"], "Action": request["action"], "Instance at request": request["instance_id"],
                "Instance version at request": str(request["expected_version"]), "Latest status": "refused"}
            metadata = dict(snapshot["identity"])
            assert {key: metadata[key] for key in expected} == expected
            assert json.loads(metadata["Exact request"]) == request
            dataset = snapshot["result"]["dataset"]
            expected_data = {"requestId": request["operation_id"], "operationId": request["operation_id"],
                "caseId": self.case_id, "caseRevision": str(view["case"]["version"]),
                "semanticHash": view["packet"]["subject"]["semantic"], "actorId": request["actor_id"],
                "action": request["action"], "instanceId": request["instance_id"],
                "expectedVersion": str(request["expected_version"]), "status": "refused"}
            assert {key: dataset[key] for key in expected_data} == expected_data

        def runtime_rule_roundtrip(self, expected):
            before = self.checkpoint("before-direct-rule-route")
            attempt = self.runtime_responses[-1]
            assert attempt["status"] == 409 and attempt["body"]["code"] == "ROLE_DENIED"
            request = attempt["request"]
            assert request["action"] == expected["action"] == "Save"
            candidate = before["view"]["case"]["candidate"]
            assert [item for item in candidate["transitions"] if item["action"] == request["action"]] == [expected]
            shown = self.runtime_attempt_snapshot()
            self.assert_runtime_attempt_identity(shown, request, before["view"])
            forward = '#runtime-rule-navigation button[data-runtime-rule="' + expected["id"] + '"]'
            replay.expect(self.page.locator(forward)).to_have_text("Inspect Save rule")
            replay.expect(self.page.locator("#runtime-rule-navigation")).to_contain_text(
                "Model rule for the attempted action · revision " + str(before["view"]["case"]["version"]))
            requests = list(self.inspection_requests)
            self.activate(forward)
            self.assert_view("model")
            replay.expect(self.page.locator("#transition-select")).to_be_focused()
            replay.expect(self.page.locator("#transition-select")).to_have_value(expected["id"])
            for selector, field in (("#transition-role", "role"), ("#model-source", "from_state"), ("#target-state", "to_state")):
                replay.expect(self.page.locator(selector)).to_have_value(expected[field])
            back = '#selection-detail button[data-runtime-attempt="' + request["operation_id"] + '"]'
            replay.expect(self.page.locator(back)).to_have_text("Return to Save attempt")
            old_back = self.page.locator(back).element_handle()
            assert self.runtime_attempt_snapshot() == shown
            assert self.inspection_requests == requests, "Inspect rule dispatched a request"
            self.shot("runtime-refusal-exact-rule")
            self.activate(back)
            self.assert_view("try")
            replay.expect(self.page.locator(forward)).to_be_focused()
            return_geometry = self.triage_focus_geometry(self.page.locator(forward))
            assert self.runtime_attempt_snapshot() == shown
            self.assert_runtime_attempt_identity(self.runtime_attempt_snapshot(), request, before["view"])
            assert self.inspection_requests == requests, "Return to attempt dispatched a request"
            self.feedback("refused", "Save")
            self.shot("runtime-refusal-returned")
            # Inspector openness is stored per work area. Explicitly pin it in Run
            # before replacing the attempt, so removal is observed while visible.
            if not self.page.locator("#inspector").is_visible():
                self.command("Toggle inspector")
            replay.expect(self.page.locator("#inspector")).to_be_visible()
            replay.expect(self.page.locator(back)).to_be_visible()
            assert self.runtime_attempt_snapshot() == shown
            assert self.inspection_requests == requests, "Pinning Run inspector dispatched a request"
            # Explicit new branch: another refused command replaces the prior attempt.
            # Its extra POST is declared in the total inventory (19), never hidden.
            prior_stage = self.stage
            self.stage = "repeated-wrong-role-runtime"
            self.attempt("Save", request["actor_id"], 409, "PREVIEW", request["expected_version"])
            self.stage = prior_stage
            replay.expect(self.page.locator(back)).to_have_count(0)
            stale_requests = list(self.inspection_requests)
            stale_shown = self.runtime_attempt_snapshot()
            rejected = old_back.evaluate("""button=>{const focused=document.activeElement,connected=button.isConnected;
                button.click();return {connected,focus_unchanged:document.activeElement===focused};}""")
            assert rejected == {"connected": False, "focus_unchanged": True}
            assert self.runtime_attempt_snapshot() == stale_shown
            assert self.inspection_requests == stale_requests
            request = self.runtime_responses[-1]["request"]
            assert request["operation_id"] != attempt["request"]["operation_id"]
            self.assert_runtime_attempt_identity(stale_shown, request, before["view"])
            self.activate(forward)
            self.assert_view("model")
            replay.expect(self.page.locator("#transition-select")).to_be_focused()
            assert self.runtime_attempt_snapshot() == stale_shown
            assert self.inspection_requests == stale_requests
            back = '#selection-detail button[data-runtime-attempt="' + request["operation_id"] + '"]'
            replay.expect(self.page.locator(back)).to_have_text("Return to Save attempt")
            # Evidence has its own saved inspector preference. Pin it through the
            # actual command before testing Return from that visible inspector.
            self.command("Open Evidence", "evidence")
            if not self.page.locator("#inspector").is_visible():
                self.command("Toggle inspector")
            replay.expect(self.page.locator("#inspector")).to_be_visible()
            replay.expect(self.page.locator(back)).to_be_visible()
            opened_view_requests = self.inspection_requests[len(stale_requests):]
            assert all(item["method"] == "GET" for item in opened_view_requests)
            return_boundary = list(self.inspection_requests)
            self.shot("runtime-rule-return-from-evidence")
            self.activate(back)
            self.assert_view("try")
            replay.expect(self.page.locator(forward)).to_be_focused()
            pinned_return_geometry = self.triage_focus_geometry(self.page.locator(forward))
            assert self.inspection_requests == return_boundary, "Pinned inspector Return dispatched a request"
            assert self.runtime_attempt_snapshot() == stale_shown
            self.assert_runtime_attempt_identity(self.runtime_attempt_snapshot(), request, before["view"])
            after = self.checkpoint("after-direct-rule-roundtrip")
            assert after["view"] == before["view"] and after["history"] == before["history"]
            self.stale_rule_button = self.page.locator(forward).element_handle()
            self.activate(forward)
            self.assert_view("model")
            assert self.runtime_attempt_snapshot() == stale_shown
            assert self.inspection_requests == return_boundary
            write_json(self.out / "runtime-rule-roundtrip.json",
                       {"transition": expected, "first_request": attempt["request"], "second_request": request,
                        "return_geometry": return_geometry, "pinned_return_geometry": pinned_return_geometry,
                        "first_attempt_display": shown, "second_attempt_display": stale_shown,
                        "old_return_after_second_refusal": rejected, "navigation_requests": 0,
                        "open_evidence_requests": opened_view_requests,
                        "attempt_identity_and_contents_preserved": True, "case_history_unchanged": True,
                        "scope": "Native refused Save -> exact model rule -> same attempt; repeated refusal replaces the old return; pinned Evidence inspector returns to the second exact attempt."})

        def stale_rule_after_repair(self):
            requests = list(self.inspection_requests)
            view = self.view()
            captured = self.stale_rule_button.evaluate("""button=>{
                const focused=document.activeElement,connected=button.isConnected;
                button.click();return {connected,focus_unchanged:document.activeElement===focused};
            }""")
            assert captured == {"connected": False, "focus_unchanged": True}, captured
            self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            assert self.inspection_requests == requests, "Stale rule navigation dispatched a request"
            assert self.view() == view
            write_json(self.out / "runtime-rule-stale-after-repair.json",
                       {"observed": captured, "requests": 0, "case_unchanged": True,
                        "scope": "Adversarial programmatic activation of detached pre-repair button; not a native keyboard task."})


        def rules_to_save(self, expected):
            before = self.checkpoint("before-rules-route")
            count = len(self.post_bodies)
            self.command("Open Rules & ripple", "impact")
            subject = self.page.locator("#rules-subject")
            replay.expect(subject).to_have_attribute("data-case-id", self.case_id)
            replay.expect(subject).to_have_attribute("data-revision", str(before["view"]["case"]["version"]))
            replay.expect(subject).to_have_attribute("data-semantic-hash", before["view"]["packet"]["subject"]["semantic"])
            row = self.page.locator('#rule-table [data-transition-id="TR-SAVE"]')
            assert row.locator("td").all_text_contents()[1:] == [expected["role"], expected["from_state"],
                expected["to_state"], ", ".join(expected["guards"])]
            self.shot("wrong-role-in-rules")
            self.activate('#rule-table [data-transition-id="TR-SAVE"] button')
            self.assert_view("model")
            replay.expect(self.page.locator("#transition-select")).to_have_value("TR-SAVE")
            replay.expect(self.page.locator("#transition-role")).to_have_value("Agent")
            after = self.checkpoint("after-rules-route")
            assert after["view"] == before["view"] and after["history"] == before["history"]
            assert len(self.post_bodies) == count, "Rules navigation caused a mutation"

        def evidence_current(self):
            before = self.checkpoint("before-evidence-navigation")
            count = len(self.post_bodies)
            self.command("Open Evidence", "evidence")
            triage = self.page.locator("#evidence-triage")
            packet = before["view"]["packet"]
            replay.expect(triage).to_have_attribute("data-case-id", self.case_id)
            replay.expect(triage).to_have_attribute("data-revision", str(before["view"]["case"]["version"]))
            replay.expect(triage).to_have_attribute("data-subject-hash", packet["subject_hash"])
            actual = triage.locator("li[data-blocker-code]").evaluate_all("nodes=>nodes.map(n=>n.dataset.blockerCode)")
            assert actual == packet["blockers"]
            replay.expect(triage).to_contain_text("Runtime evidence · UNKNOWN")
            replay.expect(self.page.locator("#approve")).to_be_disabled()
            replay.expect(self.page.locator("#apply")).to_be_disabled()
            after = self.checkpoint("after-evidence-navigation")
            assert after["view"] == before["view"] and after["history"] == before["history"]
            assert len(self.post_bodies) == count
            self.shot(self.stage + "-evidence")

        def history_operation(self, operation, model, semantic, cursor):
            before = self.checkpoint("before-" + operation)
            self.command("Open Model", "model")
            with self.page.expect_response(lambda r: r.request.method == "POST"
                    and urlsplit(r.url).path == f"/api/cases/{self.case_id}/{operation}") as pending:
                self.activate("#" + operation + "-edit")
            assert pending.value.status == 200
            assert pending.value.request.post_data_json == {"expected_version": before["view"]["case"]["version"]}
            after = self.checkpoint("after-" + operation)
            assert after["view"]["case"]["version"] == before["view"]["case"]["version"] + 1
            assert after["view"]["case"]["candidate"] == model
            assert after["view"]["packet"]["subject"]["semantic"] == semantic
            assert after["history"]["cursor"] == cursor
            transaction = before["view"]["case"]["transactions"][-1] if operation == "undo" else before["view"]["case"]["redo_transactions"][-1]
            self.semantic_event(before["view"], after["view"], "SemanticUndone" if operation == "undo" else "SemanticRedone", transaction)
            self.canvas_matches(model)
            self.command("Show local case history")
            replay.expect(self.page.locator("#history-pane")).to_be_visible()
            self.history_matches(after["history"])
            self.command("Open Run", "try")
            replay.expect(self.page.locator("#runtime-state")).to_have_text("Not started")
            assert not self.page.locator("#runtime-result").text_content().strip()
            assert not self.page.locator("#runtime-last-commit").text_content().strip()
            self.evidence_current()
            return after

        def run(self):
            self.stage = "entry-and-offline-candidate"
            self.entry()
            self.create_candidate()
            initial = self.checkpoint("initial-candidate")
            self.baseline_case = initial["view"]["case"]
            assert initial["view"]["case"]["version"] == 2
            save = next(t for t in self.baseline_case["candidate"]["transitions"] if t["id"] == "TR-SAVE")
            assert (save["role"], save["from_state"], save["to_state"]) == ("Owner", "PREVIEW", "SAVED")
            for action, role, start, end, effect in (
                    ("Propose", "Agent", "DRAFT", "PROPOSED", "Audit:ReferencePropose"),
                    ("SelectMeaning", "Owner", "PROPOSED", "PREVIEW", "Audit:ReferenceSelectMeaning"),
                    ("Save", "Owner", "PREVIEW", "SAVED", "Audit:ReferenceSave")):
                transition = next(t for t in self.baseline_case["candidate"]["transitions"] if t["action"] == action)
                assert (transition["role"], transition["from_state"], transition["to_state"], transition["required_effects"]) == (role, start, end, [effect])
            self.select_save()
            self.stage = "cancel-prospective-agent-role"
            before, payload, _ = self.propose_role("Agent")
            self.close_edit_preview(before, keyboard=True)
            assert self.checkpoint("after-cancel")["view"] == initial["view"]
            self.stage = "commit-agent-role"
            before, payload, choice = self.propose_role("Agent")
            self.apply_edit_preview(before, payload, keyboard=True)
            self.assert_role_edit({"case": initial["view"]["case"],
                "subject": initial["view"]["packet"]["subject"], "history": initial["history"]},
                "TR-SAVE", "Agent", choice["transaction"])
            changed = self.checkpoint("agent-role-committed")
            self.semantic_event(initial["view"], changed["view"], "SemanticEdited", choice["transaction"])
            actors = self.get("status")["pack"]["actors"]
            agent = next(a["id"] for a in actors if a["role"] == "Agent" and a["active"] and a["assigned"])
            owner = next(a["id"] for a in actors if a["role"] == "Owner" and a["active"] and a["assigned"])
            self.stage = "wrong-role-runtime"
            first_instance = self.start_runtime()
            self.attempt("Propose", agent, 200, "PROPOSED", 1)
            self.attempt("SelectMeaning", owner, 200, "PREVIEW", 2)
            self.attempt("Save", owner, 409, "PREVIEW", 2)
            self.stage = "rules-route-and-owner-repair"
            changed_save = next(t for t in changed["view"]["case"]["candidate"]["transitions"] if t["id"] == "TR-SAVE")
            self.runtime_rule_roundtrip(changed_save)
            before_repair = self.snapshot()
            before, payload, choice = self.propose_role("Owner")
            self.apply_edit_preview(before, payload, keyboard=True)
            self.assert_role_edit(before_repair, "TR-SAVE", "Owner", choice["transaction"])
            repaired = self.checkpoint("owner-role-repaired")
            self.stale_rule_after_repair()
            self.semantic_event(before["view"], repaired["view"], "SemanticEdited", choice["transaction"])
            assert repaired["view"]["case"]["candidate"] == initial["view"]["case"]["candidate"]
            assert repaired["view"]["packet"]["subject"]["semantic"] == initial["view"]["packet"]["subject"]["semantic"]
            self.stage = "repaired-runtime"
            second_instance = self.start_runtime()
            assert second_instance["id"] != first_instance["id"]
            self.attempt("Propose", agent, 200, "PROPOSED", 1)
            self.attempt("SelectMeaning", owner, 200, "PREVIEW", 2)
            self.attempt("Save", owner, 200, "SAVED", 3)
            succeeded = self.checkpoint("same-case-save-succeeded")
            assert len(succeeded["view"]["observations"]["instances"]) == 2
            runtime_events = [item for item in succeeded["view"]["observations"]["events"] if "operation_id" in item["body"]]
            successful_ids = {item["request"]["operation_id"] for item in self.runtime_responses if item["status"] == 200}
            refused_ids = {item["request"]["operation_id"] for item in self.runtime_responses if item["status"] == 409}
            assert len(successful_ids) == 5 and len(refused_ids) == 2
            assert {item["body"]["operation_id"] for item in runtime_events} == successful_ids
            assert len(runtime_events) == 5 and not successful_ids.intersection(refused_ids)
            assert succeeded["view"]["observations"]["outbox"] == []
            self.evidence_current()
            self.stage = "undo-repair"
            self.history_operation("undo", changed["view"]["case"]["candidate"],
                changed["view"]["packet"]["subject"]["semantic"], changed["history"]["cursor"])
            self.stage = "redo-repair"
            final = self.history_operation("redo", repaired["view"]["case"]["candidate"],
                repaired["view"]["packet"]["subject"]["semantic"], repaired["history"]["cursor"])
            assert final["view"]["case"]["version"] == initial["view"]["case"]["version"] + 4
            initial_events = initial["view"]["observations"]["events"]
            final_events = final["view"]["observations"]["events"]
            assert final_events[:len(initial_events)] == initial_events
            assert Counter(item["kind"] for item in final_events[len(initial_events):]) == {
                "SemanticEdited": 2, "SemanticUndone": 1, "SemanticRedone": 1,
                "Audit:ReferencePropose": 2, "Audit:ReferenceSelectMeaning": 2, "Audit:ReferenceSave": 1}
            counts = Counter(row["path"].removeprefix(f"/api/cases/{self.case_id}/") for row in self.post_bodies)
            assert dict(counts) == {"/api/cases": 1, "propose": 1, "select": 1,
                "edit/preview": 3, "edit": 2, "preview": 2, "execute": 7, "undo": 1, "redo": 1}
            cases = self.get("cases")
            assert len(cases) == 1 and cases[0]["id"] == self.case_id
            assert not self.errors and not self.forbidden and not self.external_attempts
            assert self.http_errors == [{"stage": stage, "status": 409,
                                         "path": f"/api/cases/{self.case_id}/execute"}
                                        for stage in ("wrong-role-runtime", "repeated-wrong-role-runtime")]
            return {"case_id": self.case_id, "initial_revision": 2, "final_revision": final["view"]["case"]["version"],
                    "request_counts": dict(counts), "actors": {"Agent": agent, "Owner": owner},
                    "wrong_role_refusal": "ROLE_DENIED", "real_case_stage": "PREVIEW",
                    "simulated_instance_states": ["PREVIEW", "SAVED"], "human_understanding": "UNKNOWN",
                    "runtime_evidence": "UNKNOWN", "owner_operations": 0}

    return CombinedJourney


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out, repo = args.out.resolve(), args.repo.resolve()
    out.mkdir(parents=True, exist_ok=False)
    script = Path(__file__).read_bytes()
    (out / "replay-script.py").write_bytes(script)
    result = {"schema": "eija.combined-modeller-browser.v1", "status": "NOT_RUN",
        "utc": datetime.now(UTC).isoformat(), "script_sha256": hashlib.sha256(script).hexdigest(),
        "scope": "One same-case offline EIJA reference-model edit and isolated synthetic runtime; desktop 1440x900",
        "checks": [], "browser_started": False, "browser_closed": False,
        "server_started": False, "server_closed": False,
        "not_run": ["human comprehension/usability study", "live provider", "fresh verification",
                    "owner approval/apply", "source code mutation", "whole-app acceptance", "mobile/reflow"]}
    review = runtime = replay = before = address = None
    try:
        if not __debug__:
            raise ModuleNotFoundError("Assertions require unoptimized Python")
        runtime, replay, compare_subjects = load_replay(repo)
        assert runtime.ROOT.resolve() == repo, "Imported replay comes from a different checkout"
        if replay.PREREQUISITE_ERROR:
            raise ModuleNotFoundError(replay.PREREQUISITE_ERROR)
        before = runtime.subject()
        write_json(out / "subject-before.json", before)
        with replay.sync_playwright() as playwright:
            result["status"] = "FAIL"
            with replay.disposable_server() as base:
                endpoint = urlsplit(base)
                address = (endpoint.hostname, endpoint.port)
                result["server_started"] = True
                browser = launch_headless(playwright, replay.BrowserError)
                result["browser_started"] = True
                try:
                    result["browser_version"] = browser.version
                    page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    review = journey_type(runtime, replay)(page, out, base)
                    evidence = review.run()
                    result["checks"].append({"id": "same-case-direct-rule-runtime-repair-history", "status": "PASS", "evidence": evidence})
                    result["status"] = "PASS"
                finally:
                    try:
                        if review:
                            review.shot("final")
                    finally:
                        browser.close()
                        result["browser_closed"] = True
    except ModuleNotFoundError as error:
        result["status"] = "FAIL" if result["browser_started"] else "NOT_RUN"
        result["prerequisite"] = str(error)
    except Exception as error:
        text, trace = str(error), traceback.format_exc()
        if replay:
            text, trace = text.replace(replay.TEST_CAPABILITY, "[test-capability]"), trace.replace(replay.TEST_CAPABILITY, "[test-capability]")
        result["error"] = {"message": text, "traceback": trace}
        result["status"] = "FAIL"
    finally:
        if address:
            with socket.socket() as sock:
                sock.settimeout(.2)
                result["server_closed"] = sock.connect_ex(address) != 0
        if review:
            result.update({"failed_stage": review.stage if result["status"] != "PASS" else None,
                "requests": review.requests, "post_bodies": review.post_bodies,
                "runtime_responses": review.runtime_responses, "javascript_errors": review.errors,
                "http_errors": review.http_errors, "forbidden_attempts": review.forbidden,
                "external_attempts": review.external_attempts, "navigation": review.navigation_actions})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
        if before is not None:
            after = runtime.subject()
            write_json(out / "subject-after.json", after)
            result["subject_preservation"] = compare_subjects(before, after)
            result["subject_content_sha256"] = before["content_sha256"]
            if result["subject_preservation"]["status"] != "UNCHANGED":
                result["status"] = "FAIL"
        if (result["browser_started"] and not result["browser_closed"]) or (result["server_started"] and not result["server_closed"]):
            result["status"] = "FAIL"
        result["script_preserved"] = Path(__file__).read_bytes() == script
        if not result["script_preserved"]:
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob("*")) if p.is_file()})
    sys.stdout.write(json.dumps({key: result[key] for key in ("status", "checks", "browser_closed", "server_closed")}) + "\n")
    sys.stdout.flush()
    return 0 if result["status"] == "PASS" else 2 if result["status"] == "NOT_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
