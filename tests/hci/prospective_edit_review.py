"""Server-derived edit preview and recovery through normal disposable UI controls."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import time
import traceback
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import self_dogfood_replay as replay
from case_preview_navigation import emit, write_json
from ide_journey_edges import Journey
from ide_review_workspace import (
    OBSERVE_COMPARE, OBSERVE_LABEL_CLEARANCE, assert_graph, assert_label_text_separation,
    assert_label_hierarchy, graph_negative_controls,
)
from quality.hci.server import ROOT
from self_dogfood_subject import capture_subject, compare_subjects, file_identity


def subject():
    value = capture_subject(ROOT)
    for name in ("tests/hci/ide_journey_edges.py", "tests/hci/ide_review_workspace.py",
                 "tests/hci/case_preview_navigation.py", "tests/hci/prospective_edit_review.py", "quality/hci/server.py"):
        value["files"][name] = file_identity(ROOT, name)
        value["scope"].append(name)
    value["content_sha256"] = hashlib.sha256(json.dumps(
        {name: item["sha256"] for name, item in value["files"].items()}, sort_keys=True,
    ).encode()).hexdigest()
    return value


class ProspectiveEdit(Journey):
    def __init__(self, page, out, base):
        super().__init__(page, out, base)
        self.hold_preview = False
        self.hold_edit = False
        self.hold_case_get = None
        self.invalid_edit_response = False
        self.held_preview = self.held_edit = self.held_get = None
        self.faults, self.graphs, self.acknowledgements = [], [], []

    def route(self, route):
        request = route.request
        path = urlsplit(request.url).path
        if request.method != "GET" and path.rsplit("/", 1)[-1] in {"verify", "approve", "apply", "export"}:
            self.forbidden.append(path)
            route.abort()
            return
        held = False
        if request.method == "POST" and path.endswith("/edit/preview") and self.hold_preview:
            self.hold_preview = False
            self.held_preview, held = route, True
        elif request.method == "POST" and path.endswith("/edit") and self.hold_edit:
            self.hold_edit = False
            self.held_edit, held = route, True
        elif request.method == "GET" and path == self.hold_case_get:
            self.hold_case_get = None
            self.held_get, held = route, True
        elif request.method == "POST" and path.endswith("/edit") and self.invalid_edit_response:
            self.invalid_edit_response = False
            actual = route.fetch()
            assert actual.status == 200, "Unknown-write control requires a real successful edit"
            self.faults.append({"kind": "malformed-after-real-edit", "path": path,
                                "request": request.post_data_json, "actual_acknowledgement": actual.json()})
            route.fulfill(status=200, content_type="application/json", body="{ response interrupted")
            held = True
        if held:
            self.requests.append({"stage": self.stage, "method": request.method, "path": path})
        else:
            super().route(route)

    def current_ui(self):
        return {"case": self.page.locator("#case-switcher").input_value(),
                "semantic": self.semantic(), "revision": self.revision(),
                "notice": self.page.locator("#notice").text_content(),
                "diagnostic": self.page.locator("#error-json").text_content(),
                "dialog_open": self.page.locator("#edit-preview").is_visible()}

    def require_held_route(self, attribute):
        deadline = time.monotonic() + 60
        while getattr(self, attribute) is None and time.monotonic() < deadline:
            # Pump Playwright while waiting for the actual route callback, not elapsed time.
            self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")
        assert getattr(self, attribute) is not None, f"Fixture did not capture expected {attribute} route"

    def fresh_case(self):
        self.tab("model")
        self.create_candidate()
        return self.edit_preview_snapshot()

    def prepare_choice(self, transition="TR-SAVE", field="role", value="Agent"):
        self.tab("model")
        self.select_transition(transition)
        kinds = {"role": "set_role", "source": "retarget_source", "target": "retarget_target"}
        controls = {"role": "#transition-role", "source": "#model-source", "target": "#target-state"}
        data = self.get(f"cases/{self.case_id}/affordances")
        target = ("role:" if field == "role" else "state:") + value
        choices = [choice for choice in data["affordances"] if choice["element"] == "transition:" + transition
                   and choice["kind"] == kinds[field] and choice["target"] == target]
        assert len(choices) == 1 and choices[0]["legal"] is True, "Fixture requires a server-listed legal edit"
        before = self.edit_preview_snapshot()
        expected = deepcopy(before["view"]["case"]["candidate"])
        next(t for t in expected["transitions"] if t["id"] == transition)[
            {"role": "role", "source": "from_state", "target": "to_state"}[field]] = value
        self.page.locator(controls[field]).select_option(value)
        return before, expected, choices[0]["transaction"], "#edit-" + field

    def open_choice(self, transition="TR-SAVE", field="role", value="Agent"):
        before, expected, transaction, invoker = self.prepare_choice(transition, field, value)
        self.page.locator(invoker).click()
        payload = self.inspect_edit_preview(before, expected, transaction)
        return before, payload, invoker

    def painted_preview(self, payload):
        pair = self.page.locator("#edit-preview-comparison")
        observed = {}
        for side, model in (("before", payload["current"]), ("after", payload["candidate"])):
            board = pair.locator(f'[data-compare-side="{side}"] svg.compare-svg')
            replay.expect(board).to_be_visible()
            observed[side] = board.evaluate(OBSERVE_COMPARE)
            assert_graph(model, observed[side])
        assert_label_hierarchy(payload["current"], payload["candidate"], observed)
        clearance = {side: pair.locator(f'[data-compare-side="{side}"] svg.compare-svg').evaluate(OBSERVE_LABEL_CLEARANCE)
                     for side in ("before", "after")}
        write_json(self.out / f"preview-label-clearance-{len(self.graphs)}.json",
                   {"viewport": self.page.viewport_size, "stage": self.stage, "observed": clearance})
        for item in clearance.values():
            assert_label_text_separation(item)
        self.graphs.append({"stage": self.stage, "current": payload["current"], "proposed": payload["candidate"],
                            "observed": observed,
                            "negative_controls": {side: graph_negative_controls(payload[field], observed[side])
                                                  for side, field in (("before", "current"), ("after", "candidate"))}})
        return observed

    def initial_changed_values(self, payload, width):
        identity = payload["transaction"]["transition"]
        before = next(t for t in payload["current"]["transitions"] if t["id"] == identity)
        after = next(t for t in payload["candidate"]["transitions"] if t["id"] == identity)
        fields = [key for key in before if before[key] != after[key]]
        region = self.page.locator("#edit-preview-comparison .compare-preview-fields")
        replay.expect(region).to_have_attribute("data-kind", "transition")
        replay.expect(region).to_have_attribute("data-id", identity)
        actual_fields = region.locator("[data-field]").evaluate_all("nodes=>nodes.map(node=>node.dataset.field).sort()")
        assert actual_fields == sorted(fields), "Initial summary omits or invents changed fields"
        observed = []
        for field in fields:
            for side, expected in (("before", before[field]), ("after", after[field])):
                value = region.locator(f'[data-field="{field}"] [data-compare-{side}]')
                replay.expect(value).to_have_text(str(expected))
                geometry = value.evaluate(r"""node=>{
                  const rect=r=>({left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height});
                  const dialog=node.closest('dialog'),body=node.closest('.edit-preview-body');
                  const footer=dialog.querySelector('.edit-preview-footer').getBoundingClientRect();
                  const clip={left:0,top:0,right:innerWidth,bottom:Math.min(innerHeight,footer.top)},ancestors=[];
                  const style=getComputedStyle(node),textColor=style.webkitTextFillColor||style.color;
                  let painted=textColor!=='none'&&textColor!=='transparent'&&
                    !/^rgba\([^,]+,[^,]+,[^,]+,\s*0(?:\.0+)?\s*\)$/.test(textColor)&&!/\/\s*0(?:\.0+)?\s*\)$/.test(textColor);
                  for(let el=node;el;el=el.parentElement){
                    const css=getComputedStyle(el),box=el.getBoundingClientRect();
                    painted&&=css.display!=='none'&&!['hidden','collapse'].includes(css.visibility)&&Number(css.opacity)>0;
                    if(el.tagName==='DETAILS'&&!el.open&&!el.querySelector(':scope > summary')?.contains(node))painted=false;
                    if(/auto|scroll|hidden|clip/.test(css.overflowX)){clip.left=Math.max(clip.left,box.left+el.clientLeft);clip.right=Math.min(clip.right,box.left+el.clientLeft+el.clientWidth);}
                    if(/auto|scroll|hidden|clip/.test(css.overflowY)){clip.top=Math.max(clip.top,box.top+el.clientTop);clip.bottom=Math.min(clip.bottom,box.top+el.clientTop+el.clientHeight);}
                    ancestors.push({tag:el.tagName,id:el.id,scrollTop:el.scrollTop,scrollLeft:el.scrollLeft});
                  }
                  const range=document.createRange();range.selectNodeContents(node);
                  const boxes=Array.from(range.getClientRects()).map(rect).filter(box=>box.width>0&&box.height>0);
                  const visible=boxes.length>0&&painted&&boxes.every(box=>box.left>=clip.left&&box.right<=clip.right&&box.top>=clip.top&&box.bottom<=clip.bottom&&
                    [0.1,0.5,0.9].every(f=>node.contains(document.elementFromPoint(box.left+box.width*f,box.top+box.height/2))));
                  return {boxes,clip,footer:rect(footer),textColor,painted,fullyVisible:visible,ancestors,bodyScrollTop:body.scrollTop,dialogScrollTop:dialog.scrollTop};
                }""")
                assert geometry["bodyScrollTop"] == 0 and geometry["dialogScrollTop"] == 0, "Initial value check ran after preview scrolling"
                if width >= 1280:
                    assert geometry["fullyVisible"], {"check": "initial-edited-value-visible", "field": field, "side": side, "expected": expected, "width": width, "geometry": geometry}
                observed.append({"field": field, "side": side, "expected": expected, "geometry": geometry})
        assert observed, "Fixture requires at least one actual changed field"
        return observed

    def close_without_writes(self):
        self.entry()
        self.fresh_case()
        evidence = []
        for transition, field, value, escape, width in (("TR-SAVE", "role", "Agent", False, 1600),
                                                         ("TR-SAVE", "role", "Agent", False, 1280),
                                                         ("TR-VERIFY", "source", "SAVED", True, 1600),
                                                         ("TR-VERIFY", "source", "SAVED", True, 1280),
                                                         ("TR-SAVE", "target", "PREVIEW", True, 320)):
            self.page.set_viewport_size({"width": 1440, "height": 900})
            before, payload, invoker = self.open_choice(transition, field, value)
            self.page.set_viewport_size({"width": width, "height": 900 if width == 1440 else 800})
            self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            initial_values = self.initial_changed_values(payload, width)
            self.painted_preview(payload)
            bounds = self.page.locator("#edit-preview").evaluate("""node=>{const r=node.getBoundingClientRect();
              return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:innerWidth,height:innerHeight,
                body:document.body.scrollWidth,document:document.documentElement.scrollWidth};}""")
            assert bounds["left"] >= 0 and bounds["top"] >= 0 and bounds["right"] <= bounds["width"] and bounds["bottom"] <= bounds["height"], "Preview dialog escapes the viewport"
            assert max(bounds["body"], bounds["document"]) <= bounds["width"], "Preview causes page-wide horizontal overflow"
            self.shot("unsubmitted-" + field)
            self.close_edit_preview(before, escape=escape, keyboard=not escape)
            if width > 850:
                replay.expect(self.page.locator(invoker)).to_be_focused()
            evidence.append({"transition": transition, "field": field, "closed_with": "Escape" if escape else "keyboard Close",
                             "case_history_runtime_and_edit_count_unchanged": True, "viewport_reflow": bounds,
                             "initial_changed_values": initial_values})
        self.page.set_viewport_size({"width": 1440, "height": 900})
        return {"previews": evidence}

    def confirm_full_candidate(self):
        before, payload, _ = self.open_choice()
        after = self.apply_edit_preview(before, payload, keyboard=True)
        assert after["view"]["case"]["version"] == before["view"]["case"]["version"] + 1
        assert after["view"]["case"]["transactions"] == [*before["view"]["case"]["transactions"], payload["transaction"]]
        assert after["history"]["cursor"] == before["history"]["cursor"] + 1
        prior_observations, observations = before["view"]["observations"], after["view"]["observations"]
        assert observations["instances"] == prior_observations["instances"]
        assert observations["outbox"] == prior_observations["outbox"]
        assert observations["events"][:-1] == prior_observations["events"]
        assert observations["events"][-1]["kind"] == "SemanticEdited"
        event = observations["events"][-1]["body"]
        assert event["case_id"] == self.case_id and event["transaction"] == payload["transaction"]
        assert event["from_version"] == before["view"]["case"]["version"] and event["to_version"] == after["view"]["case"]["version"]
        assert event["before_semantic_hash"] == payload["semantic_hash"] and event["after_semantic_hash"] == payload["candidate_semantic_hash"]
        return {"explicit_apply": True, "exact_transaction": payload["transaction"], "full_candidate_matches_preview": True}

    def delayed_preview_close_switch(self):
        evidence = []
        for fail in (False, True):
            self.fresh_case()
            old_id = self.case_id
            before, _, _, invoker = self.prepare_choice()
            self.hold_preview = True
            with self.page.expect_request(lambda r: r.method == "POST" and urlsplit(r.url).path.endswith("/edit/preview")):
                self.page.locator(invoker).click()
            replay.expect(self.page.locator("#edit-preview-status")).to_have_attribute("data-status", "checking")
            self.require_held_route("held_preview")
            self.close_edit_preview(before, escape=True)
            self.fresh_case()
            new_id = self.case_id
            before_late = self.edit_preview_snapshot()
            ui_before_late = self.current_ui()
            route, self.held_preview = self.held_preview, None
            with (
                self.page.expect_request_finished(lambda r, case_id=old_id: r.method == "POST"
                                                  and urlsplit(r.url).path == f"/api/cases/{case_id}/edit/preview"),
                self.page.expect_response(lambda r, case_id=old_id: r.request.method == "POST"
                                          and urlsplit(r.url).path == f"/api/cases/{case_id}/edit/preview") as pending,
            ):
                if fail:
                    self.faults.append({"kind": "late-preview-503", "path": f"/api/cases/{old_id}/edit/preview"})
                    route.fulfill(status=503, content_type="application/json", body=json.dumps({
                        "code": "SYNTHETIC_PREVIEW_UNAVAILABLE", "message": "Late read-only preview failed after closing.",
                    }))
                else:
                    route.continue_()
            assert pending.value.status == (503 if fail else 200)
            self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            self.settled()
            assert self.current_ui() == ui_before_late, "Late preview changed another case's UI/diagnostic"
            assert self.edit_preview_snapshot() == before_late
            assert self.get("cases/" + old_id) == before["view"], "Closed preview changed its old case"
            assert self.get("cases/" + old_id + "/history") == before["history"]
            evidence.append({"closed_case": old_id, "active_case": new_id, "late_status": 503 if fail else 200,
                             "ignored_without_mutation": True})
        return {"late_responses": evidence}

    def acknowledged_refresh_failure(self):
        self.fresh_case()
        self.tab("try")
        self.page.locator("#reset").click()
        self.settled()
        replay.expect(self.page.locator("#runtime-state")).to_have_text("DRAFT")
        before, payload, _ = self.open_choice()
        case_id = self.case_id
        self.hold_edit = True
        with self.page.expect_request(lambda r: r.method == "POST" and urlsplit(r.url).path.endswith("/edit")):
            self.activate_preview_control("#edit-preview-apply", keyboard=True)
        replay.expect(self.page.locator("#edit-preview-status")).to_have_attribute("data-status", "submitting")
        replay.expect(self.page.locator("#edit-preview-cancel")).to_be_disabled()
        self.page.keyboard.press("Enter")
        self.page.keyboard.press("Escape")
        replay.expect(self.page.locator("#edit-preview")).to_be_visible()
        self.hold_case_get = "/api/cases/" + case_id
        self.require_held_route("held_edit")
        route, self.held_edit = self.held_edit, None
        assert route is not None
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path.endswith("/edit")) as pending:
            route.continue_()
        assert pending.value.status == 200
        ack = pending.value.json()
        assert ack["candidate"] == payload["candidate"] and ack["version"] == before["view"]["case"]["version"] + 1
        self.acknowledgements.append(ack)
        replay.expect(self.page.locator("#edit-preview-status")).to_have_attribute("data-status", "committed")
        replay.expect(self.page.locator("#edit-preview-cancel")).to_be_disabled()
        self.page.keyboard.press("Escape")
        replay.expect(self.page.locator("#edit-preview")).to_be_visible()
        replay.expect(self.page.locator("#runtime-state")).to_have_text("Not started")
        replay.expect(self.page.locator("#runtime-actions button:enabled")).to_have_count(0)
        self.require_held_route("held_get")
        route, self.held_get = self.held_get, None
        self.faults.append({"kind": "ack-refresh-503", "path": "/api/cases/" + case_id})
        route.fulfill(status=503, content_type="application/json", body=json.dumps({
            "code": "SYNTHETIC_EDIT_REFRESH_UNAVAILABLE", "message": "The acknowledged edit refresh failed once.",
        }))
        self.settled()
        replay.expect(self.page.locator("#edit-preview-status")).to_have_attribute("data-status", "committed")
        self.shot("acknowledged-edit-before-close-and-retry")
        self.activate_preview_control("#edit-preview-cancel")
        replay.expect(self.page.locator("#edit-preview")).to_be_hidden()
        marker = self.page.locator("#edit-reconciliation")
        replay.expect(marker).to_be_visible()
        replay.expect(marker).to_have_attribute("data-status", "committed")
        replay.expect(marker).to_have_attribute("data-case-id", case_id)
        replay.expect(self.page.locator("#edit-role")).to_be_disabled()
        actual = self.edit_preview_snapshot()
        assert actual["view"]["case"]["candidate"] == payload["candidate"]
        assert actual["edit_posts"] == before["edit_posts"] + 1, "Repeated activation duplicated the semantic edit"
        self.fresh_case()
        replay.expect(marker).to_be_hidden()
        self.switch_case(case_id)
        replay.expect(marker).to_be_hidden()  # Successful authoritative case load reconciles this case only.
        assert self.get("cases/" + case_id) == actual["view"]
        assert self.get("cases/" + case_id + "/history") == actual["history"]
        return {"one_acknowledged_write": True, "escape_during_submit_and_refresh_ignored": True,
                "failed_refresh_marker_survives_close": True, "authoritative_case_return_reconciles": True}

    def unknown_write_reconciliation(self):
        self.fresh_case()
        before, payload, _ = self.open_choice()
        self.invalid_edit_response = True
        self.activate_preview_control("#edit-preview-apply")
        self.settled()
        replay.expect(self.page.locator("#edit-preview-status")).to_have_attribute("data-status", "unknown")
        actual = self.edit_preview_snapshot()
        assert actual["view"]["case"]["candidate"] == payload["candidate"]
        assert actual["view"]["case"]["version"] == before["view"]["case"]["version"] + 1
        assert actual["edit_posts"] == before["edit_posts"] + 1
        self.shot("unknown-edit-before-close")
        self.page.keyboard.press("Escape")
        replay.expect(self.page.locator("#edit-preview")).to_be_hidden()
        marker = self.page.locator("#edit-reconciliation")
        replay.expect(marker).to_be_visible()
        replay.expect(marker).to_have_attribute("data-status", "unknown")
        replay.expect(self.page.locator("#edit-role")).to_be_disabled()
        self.canvas_matches(before["view"]["case"]["candidate"])
        self.page.locator("#edit-reconcile-refresh").click()
        self.settled()
        replay.expect(marker).to_be_hidden()
        self.canvas_matches(payload["candidate"])
        assert self.edit_preview_snapshot() == actual, "Reconciliation changed authoritative facts or retried the edit"
        return {"actual_fixture_commit": True, "outcome_was_unknown": True,
                "persistent_marker_and_edit_block": True, "get_only_reconciliation": True}


def main():
    if not __debug__:
        emit({"status": "NOT_RUN", "reason": "Assertion oracles require unoptimized Python"})
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    before = subject()
    write_json(out / "subject-before.json", before)
    (out / "replay-script.py").write_bytes(Path(__file__).read_bytes())
    result = {"schema": "eija.prospective-edit-browser.v1", "status": "FAIL", "utc": datetime.now(UTC).isoformat(),
              "identity": "normal_source_review_required", "provider": "offline", "checks": [],
              "browser_closed": False, "server_closed": False,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "not_run": ["human usability", "live provider", "owner verify/approve/apply", "complete mobile editing"]}
    review, address = None, None
    try:
        with replay.disposable_server() as base:
            endpoint = urlsplit(base)
            address = (endpoint.hostname, endpoint.port)
            with replay.sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    review = ProspectiveEdit(page, out, base)
                    steps = (("preview-close-escape-no-write", review.close_without_writes),
                             ("explicit-apply-full-candidate", review.confirm_full_candidate),
                             ("late-preview-close-case-switch", review.delayed_preview_close_switch),
                             ("acknowledged-write-refresh-failure", review.acknowledged_refresh_failure),
                             ("unknown-write-reconciliation", review.unknown_write_reconciliation))
                    for name, action in steps:
                        review.stage = name
                        evidence = action()
                        result["checks"].append({"id": name, "status": "PASS", "evidence": evidence})
                        review.shot(name)
                        emit({"check": name, "status": "PASS"})
                    expected = sorted((503, fault["path"]) for fault in review.faults
                                      if fault["kind"] in {"late-preview-503", "ack-refresh-503"})
                    assert sorted((r["status"], r["path"]) for r in review.http_errors) == expected
                    assert not review.errors and not review.forbidden
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
                           "forbidden_attempts": review.forbidden, "fault_controls": review.faults,
                           "navigation_actions": review.navigation_actions,
                           "failed_stage": review.stage if result["status"] != "PASS" else None})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
            write_json(out / "preview-graph-observations.json", review.graphs)
            write_json(out / "acknowledged-edits.json", review.acknowledgements)
        after = subject()
        write_json(out / "subject-after.json", after)
        result["subject_content_sha256"] = before["content_sha256"]
        result["subject_preservation"] = compare_subjects(before, after)
        if result["subject_preservation"]["status"] != "UNCHANGED" or not result["browser_closed"] or not result["server_closed"]:
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                                   for p in sorted(out.rglob("*")) if p.is_file()})
    emit({key: result[key] for key in ("status", "browser_closed", "server_closed", "checks")})
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
