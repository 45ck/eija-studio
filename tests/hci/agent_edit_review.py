"""Actual agent proposal, owner candidate edit, linked UML and pointer-drag acceptance.

Uses the user's installed Chrome with an isolated disposable offline workspace.
No recording, live inference, source writes, owner verification or baseline apply.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import socket
import sys
import tempfile
import traceback
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

try:
    import self_dogfood_replay as replay
    from case_preview_navigation import emit, write_json
    from ide_review_workspace import OBSERVE_COMPARE, assert_graph, graph_negative_controls
    from prospective_edit_review import ProspectiveEdit
    from quality.hci.server import ROOT
    from rules_ripple_review import RulesReview
    from self_dogfood_subject import capture_subject, compare_subjects, file_identity
except ImportError as error:
    sys.stdout.write(json.dumps({"status": "NOT_RUN", "reason": str(error)}) + "\n")
    raise SystemExit(3) from error


SCRIPT = "tests/hci/agent_edit_review.py"
REQUEST = "Move Verify source to SAVED"
TRANSACTION = {"kind": "retarget_transition", "transition": "TR-VERIFY", "end": "source", "state": "SAVED"}
SOURCE = "repo://src/eija_studio/application/service.py#Studio.verify"
STEPS = (
    "visible-synthetic-setup", "real-proposal-cancel-no-write", "explicit-owner-candidate-edit",
    "linked-model-changes-rules-source", "actual-endpoint-drag-apply-undo",
    "unsupported-and-protected-refusals", "late-proposal-case-switch", "evidence-and-authority-boundaries",
)


def subject_identity():
    subject = capture_subject(ROOT)
    for name in (SCRIPT, "tests/hci/agent_edit_review.md", "tests/hci/ide_journey_edges.py",
                 "tests/hci/ide_review_workspace.py", "tests/hci/prospective_edit_review.py",
                 "tests/hci/rules_ripple_review.py", "tests/hci/case_preview_navigation.py", "quality/hci/server.py"):
        subject["files"][name] = file_identity(ROOT, name)
        if name not in subject["scope"]:
            subject["scope"].append(name)
    subject["content_sha256"] = hashlib.sha256(json.dumps(
        {name: item["sha256"] for name, item in subject["files"].items()}, sort_keys=True,
    ).encode()).hexdigest()
    return subject


def expected_source(model, state):
    """Independent whole-model oracle: only this named transition's source may change."""
    expected = deepcopy(model)
    matches = [item for item in expected["transitions"] if item["id"] == "TR-VERIFY"]
    assert len(matches) == 1 and state in expected["states"]
    assert matches[0]["from_state"] != state, "The fixture must exercise a real semantic change"
    matches[0]["from_state"] = state
    return expected


class AgentEdit(ProspectiveEdit):
    def __init__(self, page, out, base):
        self.request_records, self.proposal_responses, self.proposal_records = [], [], []
        self.observations, self.source_records, self.drag_records = [], [], []
        self.hold_proposal, self.held_proposal = False, None
        self.expected_http_errors = []
        self.initial, self.agent_applied = None, None
        super().__init__(page, out, base)

    def route(self, route):
        request = route.request
        path = urlsplit(request.url).path
        record = {"stage": self.stage, "method": request.method, "path": path}
        if request.method == "POST":
            record["body"] = request.post_data_json
        self.request_records.append(record)
        if request.method == "POST" and path.endswith("/edit/propose") and self.hold_proposal:
            self.hold_proposal = False
            self.held_proposal = route
            self.requests.append({key: record[key] for key in ("stage", "method", "path")})
            return
        super().route(route)

    def response(self, response):
        super().response(response)
        if response.request.method == "POST" and urlsplit(response.url).path.endswith("/edit/propose"):
            self.proposal_responses.append({"stage": self.stage, "path": urlsplit(response.url).path,
                                            "status": response.status, "request": response.request.post_data_json,
                                            "body": response.json()})

    def view(self):
        return self.get("cases/" + self.case_id)

    def immutable(self, before):
        assert self.edit_preview_snapshot() == before, "Read-only proposal/navigation changed complete case/history/runtime or submitted an edit"

    def setup(self):
        self.entry()
        self.tab("source")
        cases_before_connection = self.get("cases")
        with self.page.expect_response(lambda response: response.request.method == "GET"
                                       and urlsplit(response.url).path == "/api/workbench") as refreshed:
            self.page.locator("#refresh-source").click()
        self.settled()
        assert refreshed.value.status == 200
        self.workbench = self.get("workbench")
        connection = self.workbench["connection"]
        assert connection["status"] == "connected", connection
        assert connection["read_only"] is True and Path(connection["root"]).resolve() == ROOT.resolve()
        assert refreshed.value.json()["connection"] == connection, "Visible refresh and independent GET describe different connections"
        assert re.fullmatch(r"sha256:[a-f0-9]{64}", connection["source_hash"])
        assert re.fullmatch(r"sha256:[a-f0-9]{64}", connection["graph_hash"])
        assert re.fullmatch(r"[a-f0-9]{64}", connection["pack"]["digest"])
        assert all(re.fullmatch(r"[a-f0-9]{64}", digest) for digest in connection["file_hashes"].values())
        manifest = [[path, digest] for path, digest in sorted(connection["file_hashes"].items())]
        manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
        assert connection["source_hash"] == "sha256:" + hashlib.sha256(b"eija.repository.source.v1\x00" + manifest_bytes).hexdigest()
        assert connection["pack"]["digest"] == self.workbench["pack"]["digest"]
        source_path = "src/eija_studio/application/service.py"
        assert connection["file_hashes"][source_path] == hashlib.sha256((ROOT / source_path).read_bytes()).hexdigest()
        replay.expect(self.page.locator("#source-view").get_by_role("heading", name="Repository snapshot available", exact=True)).to_be_visible()
        replay.expect(self.page.locator('#source-view .source-badge[data-status="connected"]')).to_be_visible()
        assert self.get("cases") == cases_before_connection, "Refreshing the configured checkout created or changed a case"
        self.shot("configured-checkout-refreshed-through-ui")
        self.create_candidate()
        self.initial = self.edit_preview_snapshot()
        assert "SAVED" in self.initial["view"]["case"]["candidate"]["states"]
        assert next(t for t in self.initial["view"]["case"]["candidate"]["transitions"]
                    if t["id"] == "TR-VERIFY")["from_state"] == "PREVIEW"
        self.tab("change")
        panel = self.page.locator("#agent-edit-panel")
        replay.expect(panel).to_be_visible()
        text = panel.inner_text().lower()
        assert "offline" in text and "synthetic" in text, "Agent origin must be visibly labelled"
        assert "model" in text and "source" in text, "Candidate/source scope must be visible"
        self.immutable(self.initial)
        return {"setup": "normal UI create/propose/owner-select of the synthetic saved-path meaning",
                "case_id": self.case_id, "provider": "offline", "live_inference": False,
                "initial": self.initial, "visible_agent_scope": text,
                "repository_setup": {"configured_root": connection["root"], "refreshed_through_ui": True,
                                     "read_only": True, "source_hash": connection["source_hash"],
                                     "graph_hash": connection["graph_hash"]}}

    def propose(self, request=REQUEST, *, status=200):
        self.tab("change")
        before = self.edit_preview_snapshot()
        self.page.locator("#agent-edit-request").fill(request)
        path = f"/api/cases/{self.case_id}/edit/propose"
        with self.page.expect_response(lambda response: response.request.method == "POST"
                                       and urlsplit(response.url).path == path) as pending:
            self.page.locator("#agent-edit-propose").click()
        response = pending.value
        assert response.status == status, f"Actual proposal response: HTTP {response.status}, expected {status}"
        assert response.request.post_data_json == {"request": request, "expected_version": before["view"]["case"]["version"]}
        if status != 200:
            self.expected_http_errors.append((status, path))
        self.settled()
        replay.expect(self.page.locator("#edit-preview")).to_be_hidden()
        self.immutable(before)
        return before, response.json()

    def assert_proposal(self, before, wrapper, expected, transaction, *, legal=True, request=REQUEST):
        case = before["view"]["case"]
        assert wrapper["scope"] == "typed-edit-proposal"
        assert wrapper["provider"] == "offline" and wrapper["model"] == "typed-edit-fixture-v1"
        assert wrapper["live"] is False and wrapper["trust"] == "UNTRUSTED_PROPOSAL"
        assert wrapper["request"] == request
        assert wrapper["pack"] == {"id": self.workbench["pack"]["id"], "digest": self.workbench["pack"]["digest"]}
        preview = wrapper["preview"]
        assert preview["scope"] == "semantic-edit-preview" and preview["applied"] is False and preview["persisted"] is False
        assert preview["case_id"] == case["id"] and preview["version"] == case["version"] and preview["stage"] == case["stage"]
        assert preview["semantic_hash"] == before["view"]["packet"]["subject"]["semantic"]
        assert preview["current"] == case["candidate"] and preview["transaction"] == transaction and preview["legal"] is legal
        assert preview["candidate"] == expected, "Actual proposer changed more than the independently intended field"
        assert preview["candidate_semantic_hash"] == (replay.Workflow.model_validate(expected).semantic_hash if legal else None)
        replay.expect(self.page.locator("#agent-edit-status")).to_have_attribute("data-status", "proposed" if legal else "refused")
        replay.expect(self.page.locator("#agent-edit-preview")).to_be_enabled()
        details = self.page.locator("#agent-edit-details")
        if details.get_attribute("open") is None:
            details.locator(":scope > summary").click()
        replay.expect(self.page.locator("#agent-edit-json")).to_be_visible()
        assert json.loads(self.page.locator("#agent-edit-json").text_content()) == wrapper, "Visible proposal differs from actual server result"
        details.locator(":scope > summary").click()
        if legal:
            summary = self.page.locator("#agent-edit-summary")
            replay.expect(summary).to_contain_text("PREVIEW")
            replay.expect(summary).to_contain_text("SAVED")
        self.proposal_records.append({"stage": self.stage, "before": before, "actual_wrapper": wrapper,
                                      "independent_expected_candidate": expected})
        self.immutable(before)
        return preview

    def open_proposal_preview(self, before, wrapper, expected, *, legal=True):
        self.page.locator("#agent-edit-preview").click()
        payload = self.inspect_edit_preview(before, expected, wrapper["preview"]["transaction"], legal=legal)
        assert payload == wrapper["preview"], "Explicit review did not recheck the same current proposal"
        if legal:
            self.painted_preview(payload)
        return payload

    def proposal_cancel(self):
        before, wrapper = self.propose()
        expected = expected_source(before["view"]["case"]["candidate"], "SAVED")
        self.assert_proposal(before, wrapper, expected, TRANSACTION)
        payload = self.open_proposal_preview(before, wrapper, expected)
        self.initial_changed_values(payload, 1440)
        self.shot("real-agent-proposal-before-cancel")
        self.close_edit_preview(before, escape=True)
        replay.expect(self.page.locator("#agent-edit-preview")).to_be_enabled()
        self.saved_proposal = (before, wrapper, expected)
        return {"actual_proposer": wrapper, "no_automatic_edit_or_preview": True,
                "complete_state_unchanged_after_escape": True}

    def checked_apply(self, before, payload):
        after = self.apply_edit_preview(before, payload)
        previous, current = before["view"]["case"], after["view"]["case"]
        assert current["baseline"] == previous["baseline"]
        assert current["transactions"] == [*previous["transactions"], payload["transaction"]]
        assert after["history"]["cursor"] == before["history"]["cursor"] + 1
        old, new = before["view"]["observations"], after["view"]["observations"]
        assert new["instances"] == old["instances"] and new["outbox"] == old["outbox"]
        assert new["events"][:-1] == old["events"] and new["events"][-1]["kind"] == "SemanticEdited"
        event = new["events"][-1]["body"]
        assert event["case_id"] == self.case_id and event["transaction"] == payload["transaction"]
        assert event["from_version"] == previous["version"] and event["to_version"] == current["version"]
        assert event["before_semantic_hash"] == payload["semantic_hash"] and event["after_semantic_hash"] == payload["candidate_semantic_hash"]
        self.acknowledgements.append({"stage": self.stage, "before": before, "preview": payload, "after": after})
        return after

    def owner_apply(self):
        before, wrapper, expected = self.saved_proposal
        payload = self.open_proposal_preview(before, wrapper, expected)
        self.agent_applied = self.checked_apply(before, payload)
        assert self.agent_applied["view"]["case"]["candidate"] == expected
        status = self.page.locator("#agent-edit-status")
        replay.expect(status).to_have_attribute("data-status", "applied")
        replay.expect(status).to_be_visible()
        replay.expect(status).to_be_focused()
        saved_focus = status.evaluate("node=>({active_id:document.activeElement.id,status:node.dataset.status,text:node.textContent})")
        assert saved_focus["active_id"] == "agent-edit-status"
        self.shot("saved-agent-result-focused-before-navigation")
        self.tab("change")
        replay.expect(self.page.locator("#agent-edit-status")).to_have_attribute("data-status", "applied")
        for ident in ("model", "changes", "rules"):
            replay.expect(self.page.locator("#agent-edit-" + ident)).to_be_visible()
        return {"exactly_one_explicit_edit": True, "full_candidate": expected,
                "semantic_hash": payload["candidate_semantic_hash"], "baseline_unchanged": True,
                "saved_result_focus_before_navigation": saved_focus}

    def inspect_working(self, view):
        return RulesReview.assert_current_inspector(self, view, "TR-VERIFY")

    def main_graph(self, view):
        observations = {}
        for side, model in (("before", view["case"]["baseline"]), ("after", view["case"]["candidate"])):
            observed = self.main_comparison().locator(f'[data-compare-side="{side}"] svg.compare-svg').evaluate(OBSERVE_COMPARE)
            assert_graph(model, observed)
            observations[side] = {"observed": observed, "negative_controls": graph_negative_controls(model, observed)}
        self.graphs.append({"stage": self.stage, "main_comparison": observations})
        return observations

    def linked_navigation(self):
        before = self.edit_preview_snapshot()
        view = before["view"]
        self.page.locator("#agent-edit-model").click()
        self.settled()
        self.inspect_working(view)
        self.tab("change")
        self.page.locator("#agent-edit-changes").click()
        self.settled()
        selection = self.main_comparison().locator(".compare-selection")
        replay.expect(selection).to_have_attribute("data-kind", "transition")
        replay.expect(selection).to_have_attribute("data-id", "TR-VERIFY")
        self.assert_comparison_transition("TR-VERIFY", view["case"]["baseline"], view["case"]["candidate"])
        self.main_graph(view)
        self.main_comparison().locator('[data-compare-action="inspect-model"]').click()
        self.settled()
        self.inspect_working(view)
        self.tab("change")
        self.page.locator("#agent-edit-rules").click()
        self.settled()
        RulesReview.inventory(self, view["case"]["candidate"])
        RulesReview.candidate_subject(self, view)
        rule = self.page.locator('#rule-table > tr[data-transition-id="TR-VERIFY"]')
        replay.expect(rule).to_have_attribute("data-change-status", "changed")
        rule.get_by_role("button", name="Verify", exact=True).click()
        self.settled()
        self.inspect_working(view)
        self.select_comparison("transition", "TR-VERIFY")
        terms = [term for term in self.workbench["language"]["terms"] if "transition:TR-VERIFY" in term.get("refs", [])]
        assert any(SOURCE in term["binds"] for term in terms), "Source navigation must use a declared binding"
        with self.page.expect_response(lambda response: urlsplit(response.url).path == "/api/repository/source") as pending:
            self.main_comparison().locator(f'[data-compare-reference="{SOURCE}"]').click()
        self.settled()
        connection = self.workbench["connection"]
        source = self.get("repository/source?" + urlencode({"reference": SOURCE, "expected_source_hash": connection["source_hash"]}))
        assert pending.value.status == 200 and pending.value.json() == source
        assert parse_qs(urlsplit(pending.value.url).query)["expected_source_hash"] == [connection["source_hash"]]
        assert source["status"] == "connected" and source["reference"] == SOURCE
        assert source["source_hash"] == connection["source_hash"] and source["graph_hash"] == connection["graph_hash"]
        assert source["file_hash"] == connection["file_hashes"][source["path"]]
        assert source["pack_digest"] == self.workbench["pack"]["digest"]
        assert re.fullmatch(r"[a-f0-9]{64}", source["snippet_hash"])
        assert hashlib.sha256(source["text"].encode()).hexdigest() == source["snippet_hash"]
        lines = source["text"].replace("\r\n", "\n").split("\n")
        if lines[-1] == "":
            lines.pop()
        assert self.page.locator("#source-reader .source-line code").all_text_contents() == [line or " " for line in lines]
        assert self.page.locator("#source-reader .line-number").all_text_contents() == [str(source["lines"]["start"] + n) for n in range(len(lines))]
        replay.expect(self.page.locator("#source-reference")).to_have_value(SOURCE)
        self.source_records.append(source)
        self.shot("declared-source-is-read-only")
        self.tab("review")
        replay.expect(selection).to_have_attribute("data-id", "TR-VERIFY")
        self.immutable(before)
        return {"selected_transition": "TR-VERIFY", "linked_views": ["Model", "Changes", "Rules", "Source"],
                "source_reference": SOURCE, "source_hash": source["source_hash"], "all_navigation_read_only": True}

    def undo_to(self, expected_model):
        self.tab("model")
        before = self.edit_preview_snapshot()
        with self.page.expect_response(lambda response: response.request.method == "POST"
                                       and urlsplit(response.url).path == f"/api/cases/{self.case_id}/undo") as pending:
            self.page.locator("#undo-edit").click()
        assert pending.value.status == 200
        assert pending.value.request.post_data_json == {"expected_version": before["view"]["case"]["version"]}
        self.settled()
        after = self.edit_preview_snapshot()
        assert pending.value.json()["candidate"] == expected_model == after["view"]["case"]["candidate"]
        assert after["view"]["case"]["version"] == before["view"]["case"]["version"] + 1
        assert after["history"]["cursor"] == before["history"]["cursor"] - 1
        assert after["edit_posts"] == before["edit_posts"]
        assert after["view"]["case"]["baseline"] == before["view"]["case"]["baseline"]
        self.canvas_matches(expected_model)
        return after

    def pointer_drag_apply_undo(self):
        self.tab("model")
        self.select_transition("TR-VERIFY")
        before = self.edit_preview_snapshot()
        expected = expected_source(before["view"]["case"]["candidate"], "PREVIEW")
        transaction = {**TRANSACTION, "state": "PREVIEW"}
        choices = self.get(f"cases/{self.case_id}/affordances")["affordances"]
        assert any(choice["transaction"] == transaction and choice["legal"] for choice in choices)
        self.page.locator("#canvas-fit").click()
        handle = self.page.locator('#model-canvas .edit-handle[data-end="source"] circle')
        target = self.page.locator('#model-canvas .model-node[data-state="PREVIEW"] .state-box')
        replay.expect(handle).to_be_visible()
        replay.expect(target).to_be_visible()
        start, finish = handle.bounding_box(), target.bounding_box()
        assert start and finish and min(start["width"], start["height"], finish["width"], finish["height"]) > 0
        start_point = {"x": start["x"] + start["width"] / 2, "y": start["y"] + start["height"] / 2}
        end_point = {"x": finish["x"] + finish["width"] / 2, "y": finish["y"] + finish["height"] / 2}
        assert self.page.evaluate("p=>document.elementFromPoint(p.x,p.y)?.closest('.edit-handle')?.dataset.end", start_point) == "source"
        assert self.page.evaluate("p=>document.elementFromPoint(p.x,p.y)?.closest('.model-node')?.dataset.state", end_point) == "PREVIEW"
        self.page.mouse.move(**start_point)
        self.page.mouse.down()
        guide = self.page.locator("#model-canvas .drag-guide")
        replay.expect(guide).to_have_count(1)  # Pointerdown starts a zero-length guide; movement gives it painted length.
        replay.expect(target.locator("xpath=..")).to_have_class(re.compile(r"\bdrop-legal\b"))
        self.page.mouse.move(**end_point, steps=16)
        replay.expect(guide).to_be_visible()
        painted_guide = guide.evaluate("""node=>{
          const matrix=node.getScreenCTM(),style=getComputedStyle(node);
          const start=new DOMPoint(node.x1.baseVal.value,node.y1.baseVal.value).matrixTransform(matrix);
          const finish=new DOMPoint(node.x2.baseVal.value,node.y2.baseVal.value).matrixTransform(matrix);
          return {start:{x:start.x,y:start.y},finish:{x:finish.x,y:finish.y},length:node.getTotalLength(),
            stroke:style.stroke,stroke_width:Number.parseFloat(style.strokeWidth),
            stroke_opacity:Number(style.strokeOpacity),opacity:Number(style.opacity)};
        }""")
        assert painted_guide["length"] > 0 and painted_guide["stroke_width"] > 0
        assert painted_guide["stroke"] not in {"none", "transparent"}
        assert painted_guide["stroke_opacity"] > 0 and painted_guide["opacity"] > 0
        for key, point in (("start", start_point), ("finish", end_point)):
            assert all(abs(painted_guide[key][axis] - point[axis]) <= 2 for axis in ("x", "y")), "Painted guide endpoints do not track the physical pointer gesture"
        record = {"phase": "pointer-moved", "physical_pointer_gesture": True,
                  "start": start_point, "finish": end_point, "painted_guide": painted_guide,
                  "transaction": transaction}
        self.drag_records.append(record)
        self.immutable(before)
        self.shot("actual-source-endpoint-drag-in-progress")
        with self.page.expect_response(lambda response: response.request.method == "POST"
                                       and urlsplit(response.url).path == f"/api/cases/{self.case_id}/edit/preview"):
            self.page.mouse.up()
        replay.expect(guide).to_have_count(0)
        replay.expect(self.page.locator("#model-canvas .drop-legal, #model-canvas .drop-refused")).to_have_count(0)
        self.navigation_action("pointer-drag", '#model-canvas .edit-handle[data-end="source"]',
                               {"transition": "TR-VERIFY", "from": "SAVED", "to": "PREVIEW", "start": start_point, "finish": end_point})
        payload = self.inspect_edit_preview(before, expected, transaction)
        self.painted_preview(payload)
        self.checked_apply(before, payload)
        self.undo_to(before["view"]["case"]["candidate"])
        restored = self.undo_to(self.initial["view"]["case"]["candidate"])
        record.update({"phase": "complete", "preview_did_not_write": True, "explicit_apply": True,
                       "first_undo_restored_agent_edit": True, "second_undo_restored_initial_candidate": True,
                       "restored_candidate": restored["view"]["case"]["candidate"]})
        return record

    def refusals(self):
        unsupported = "Create a unicorn billing engine"
        before, failure = self.propose(unsupported, status=409)
        assert failure["code"] == "EDIT_REQUEST_UNSUPPORTED"
        replay.expect(self.page.locator("#agent-edit-status")).to_have_attribute("data-status", "failed")
        replay.expect(self.page.locator("#agent-edit-status")).to_contain_text("EDIT_REQUEST_UNSUPPORTED")
        replay.expect(self.page.locator("#agent-edit-preview")).not_to_be_visible()
        self.immutable(before)
        request = "Allow Agent to Approve"
        before, wrapper = self.propose(request)
        transaction = {"kind": "set_role", "transition": "TR-APPROVE", "role": "Agent"}
        self.assert_proposal(before, wrapper, None, transaction, legal=False, request=request)
        assert "REFERENCE_AUTHORITY:Approve" in wrapper["preview"]["codes"]
        payload = self.open_proposal_preview(before, wrapper, None, legal=False)
        self.close_edit_preview(before, escape=True)
        return {"unsupported": failure, "protected_law_codes": payload["codes"],
                "protected_law_refs": payload["refs"], "complete_state_unchanged": True}

    def late_case_switch(self):
        original_id = self.case_id
        original = self.edit_preview_snapshot()
        self.create_candidate()
        other_id = self.case_id
        other = self.edit_preview_snapshot()
        self.switch_case(original_id)
        self.tab("change")
        self.page.locator("#agent-edit-request").fill(REQUEST)
        self.hold_proposal = True
        with self.page.expect_request(lambda request: request.method == "POST"
                                      and urlsplit(request.url).path == f"/api/cases/{original_id}/edit/propose"):
            self.page.locator("#agent-edit-propose").click()
        replay.expect(self.page.locator("#agent-edit-status")).to_have_attribute("data-status", "requesting")
        self.require_held_route("held_proposal")
        self.switch_case(other_id)
        self.tab("change")
        replay.expect(self.page.locator("#agent-edit-preview")).not_to_be_visible()
        ui = {"status": self.page.locator("#agent-edit-status").text_content(),
              "request": self.page.locator("#agent-edit-request").input_value()}
        route, self.held_proposal = self.held_proposal, None
        with self.page.expect_response(lambda response: response.request.method == "POST"
                                       and urlsplit(response.url).path == f"/api/cases/{original_id}/edit/propose") as pending:
            route.continue_()
        assert pending.value.status == 200 and pending.value.json()["preview"]["case_id"] == original_id
        self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        assert self.page.locator("#agent-edit-status").text_content() == ui["status"]
        assert self.page.locator("#agent-edit-request").input_value() == ui["request"]
        replay.expect(self.page.locator("#agent-edit-preview")).not_to_be_visible()
        replay.expect(self.page.locator("#edit-preview")).to_be_hidden()
        self.immutable(other)
        assert self.get("cases/" + original_id) == original["view"]
        assert self.get("cases/" + original_id + "/history") == original["history"]
        self.switch_case(original_id)
        return {"held_actual_request": original_id, "switched_to": other_id,
                "response": pending.value.json(), "late_response_ignored": True,
                "both_complete_cases_unchanged": True}

    def boundaries(self):
        before = self.edit_preview_snapshot()
        self.tab("evidence")
        packet = before["view"]["packet"]
        assert "SOURCE_REVIEW_REQUIRED" in packet["blockers"] and packet["human_understanding"] == "UNKNOWN"
        replay.expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        replay.expect(self.page.locator("#evidence .human-status")).to_contain_text("UNKNOWN")
        assert before["view"]["case"]["baseline"] == self.initial["view"]["case"]["baseline"]
        assert self.get("workbench")["connection"]["source_hash"] == self.workbench["connection"]["source_hash"]
        self.immutable(before)
        assert not self.forbidden and not self.errors
        assert sorted((item["status"], item["path"]) for item in self.http_errors) == sorted(self.expected_http_errors)
        prohibited = {"verify", "approve", "apply", "export"}
        assert not [item for item in self.request_records if item["method"] != "GET" and item["path"].rsplit("/", 1)[-1] in prohibited]
        mutations = [item for item in self.request_records if item["method"] != "GET"]
        for item in mutations:
            assert item["method"] == "POST", "Unexpected HTTP mutation method"
            assert item["path"] == "/api/cases" or re.fullmatch(
                r"/api/cases/[^/]+/(?:propose|select|edit/propose|edit/preview|edit|undo)", item["path"],
            ), "Unexpected endpoint outside the declared candidate-edit journey"
        assert sum(item["path"].endswith("/edit") for item in mutations) == 2
        assert sum(item["path"].endswith("/undo") for item in mutations) == 2
        return {"source_review": "SOURCE_REVIEW_REQUIRED", "human_comprehension": "UNKNOWN",
                "source_and_baseline_unchanged": True, "forbidden_endpoint_attempts": [],
                "javascript_errors": [], "only_expected_http_errors": self.expected_http_errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    repository_temp_root = Path(tempfile.gettempdir()).resolve()
    prerequisite = None
    if not __debug__:
        prerequisite = "Assertion oracles require Python without -O/-OO"
    elif replay.PREREQUISITE_ERROR:
        prerequisite = replay.PREREQUISITE_ERROR
    elif repository_temp_root.is_relative_to(ROOT.resolve()):
        prerequisite = ("Repository source mirrors require a temporary directory outside the connected checkout. "
                        "Set TMPDIR, TEMP and TMP to an existing external directory before starting Python; "
                        f"actual tempfile.gettempdir() is {repository_temp_root}")
    elif sys.platform == "win32" and shutil.disk_usage("C:/").free < 10 * 1024 ** 3:
        prerequisite = "C: free space is below the existing 10 GiB browser guard"
    if prerequisite:
        result = {"status": "NOT_RUN", "reason": prerequisite, "repository_temp_root": str(repository_temp_root)}
        write_json(out / "result.json", result)
        emit(result)
        return 3
    before = subject_identity()
    write_json(out / "subject-before.json", before)
    (out / "replay-script.py").write_bytes(Path(__file__).read_bytes())
    result = {"schema": "eija.agent-edit-browser.v1", "status": "FAIL", "utc": datetime.now(UTC).isoformat(),
              "identity": "normal_source_review_required", "provider": "offline", "live": False,
              "browser_channel": "chrome", "recording": False, "checks": [],
              "repository_temp_root": str(repository_temp_root),
              "browser_closed": False, "server_closed": False,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "not_run": ["human value/usability", "live inference", "arbitrary request interpretation",
                          "source transformation", "owner verification/approval/baseline apply", "same-case concurrent revision race"]}
    review, address = None, None
    try:
        with replay.disposable_server() as base:
            endpoint = urlsplit(base)
            address = (endpoint.hostname, endpoint.port)
            with replay.sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
                result["browser_version"] = browser.version
                try:
                    page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    page.set_default_timeout(30000)
                    review = AgentEdit(page, out, base)
                    actions = (review.setup, review.proposal_cancel, review.owner_apply, review.linked_navigation,
                               review.pointer_drag_apply_undo, review.refusals, review.late_case_switch, review.boundaries)
                    assert len(actions) == len(STEPS)
                    for name, action in zip(STEPS, actions, strict=True):
                        review.stage = name
                        evidence = action()
                        result["checks"].append({"id": name, "status": "PASS", "evidence": evidence})
                        review.shot(name)
                        emit({"check": name, "status": "PASS"})
                    result["status"] = "PASS"
                finally:
                    try:
                        if review:
                            review.shot("final")
                    finally:
                        browser.close()
                        result["browser_closed"] = True
    except Exception as error:
        result["error"] = {"type": type(error).__name__, "message": str(error).replace(replay.TEST_CAPABILITY, "[test-capability]"),
                           "traceback": traceback.format_exc().replace(replay.TEST_CAPABILITY, "[test-capability]")}
        if "Chromium distribution 'chrome' is not found" in str(error) or "Executable doesn't exist" in str(error):
            result["status"] = "NOT_RUN"
            result["reason"] = "Installed Chrome is unavailable; no browser fallback was used"
    finally:
        if address:
            with socket.socket() as probe:
                probe.settimeout(.2)
                result["server_closed"] = probe.connect_ex(address) != 0
        if review:
            result.update({"requests": review.request_records, "javascript_errors": review.errors,
                           "http_errors": review.http_errors, "forbidden_attempts": review.forbidden,
                           "navigation_actions": review.navigation_actions,
                           "failed_stage": review.stage if result["status"] != "PASS" else None})
            for filename, value in (("authoritative-get-oracles.json", review.oracles),
                                    ("proposal-responses.json", review.proposal_responses),
                                    ("proposal-observations.json", review.proposal_records),
                                    ("painted-graph-observations.json", review.graphs),
                                    ("model-navigation-observations.json", review.observations),
                                    ("acknowledged-edits.json", review.acknowledgements),
                                    ("source-observations.json", review.source_records),
                                    ("pointer-drag-observations.json", review.drag_records)):
                write_json(out / filename, value)
        after = subject_identity()
        write_json(out / "subject-after.json", after)
        result["subject_content_sha256"] = before["content_sha256"]
        result["subject_preservation"] = compare_subjects(before, after)
        if result["subject_preservation"]["status"] != "UNCHANGED" or not result["server_closed"]:
            result["status"] = "FAIL"
        if result["status"] == "PASS" and not result["browser_closed"]:
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {path.relative_to(out).as_posix():
            {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(out.rglob("*")) if path.is_file()})
    emit({"status": result["status"], "browser_closed": result["browser_closed"], "server_closed": result["server_closed"],
          "checks": [{"id": check["id"], "status": check["status"]} for check in result["checks"]],
          "failed_stage": result.get("failed_stage"), "result": str(out / "result.json")})
    return 0 if result["status"] == "PASS" else 3 if result["status"] == "NOT_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
