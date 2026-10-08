"""Real Rules navigation against server-returned models in a disposable workspace.

No owner verification, approval/apply, live providers or personal browser profile.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import traceback
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import self_dogfood_replay as replay
from case_preview_navigation import emit, write_json
from ide_journey_edges import Journey
from quality.hci.server import ROOT
from self_dogfood_subject import capture_subject, compare_subjects, file_identity

SCRIPT = "tests/hci/rules_ripple_review.py"


def subject_identity():
    subject = capture_subject(ROOT)
    for name in ("tests/hci/ide_journey_edges.py", "tests/hci/case_preview_navigation.py", "quality/hci/server.py"):
        subject["scope"].append(name)
        subject["files"][name] = file_identity(ROOT, name)
    subject["scope"].append(SCRIPT)
    content = Path(__file__).read_bytes()
    subject["files"][SCRIPT] = {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
    hashes = {name: item["sha256"] for name, item in subject["files"].items()}
    subject["content_sha256"] = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return subject


OBSERVE_MODEL = """board => {
  const paint = element => {const style=getComputedStyle(element), rect=element.getBoundingClientRect();
    return {displayed:element.checkVisibility(), width:rect.width,height:rect.height,
      fill:style.fill,stroke:style.stroke,strokeWidth:parseFloat(style.strokeWidth),opacity:Number(style.opacity)};};
  const nodes=[...board.querySelectorAll('.model-node')].map(group=>({group,
    state:group.dataset.state,shape:group.querySelector('rect.state-box'),
    text:group.querySelector('.state-label').textContent,
    label:paint(group.querySelector('.state-label'))}));
  const contact=(path,at)=>{const screen=path.getPointAtLength(at).matrixTransform(path.getScreenCTM());
    return nodes.filter(node=>node.shape.isPointInStroke(screen.matrixTransform(node.shape.getScreenCTM().inverse())))
      .map(node=>node.state).sort();};
  return {nodes:nodes.map(({state,text,label,shape})=>({state,text,label,shape:paint(shape)})),
    edges:[...board.querySelectorAll('.model-edge')].map(group=>{
      const path=group.querySelector('path.edge-line'), label=group.querySelector('.edge-label');
      return {id:group.dataset.eijaId,selected:group.getAttribute('aria-pressed'),text:label.textContent,
        label:paint(label),path:paint(path),source:contact(path,0),target:contact(path,path.getTotalLength())};})};
}"""


class RulesReview(Journey):
    def __init__(self, page, out, base):
        super().__init__(page, out, base)
        self.observations = []
        self.case_a = None

    def route(self, route):
        request = route.request
        path = urlsplit(request.url).path
        if request.method != "GET" and path.rsplit("/", 1)[-1] in {"verify", "approve", "apply", "export"}:
            self.requests.append({"stage": self.stage, "method": request.method, "path": path})
            self.forbidden.append(path)
            route.abort()
        else:
            super().route(route)

    def view(self):
        value = self.get("cases/" + self.case_id)
        assert value["case"]["id"] == self.case_id, "GET case identity mismatch"
        return value

    def inventory(self, model):
        rows = self.page.locator("#rule-table > tr").evaluate_all(
            """rows=>rows.map(row=>({id:row.dataset.transitionId,status:row.dataset.changeStatus,
              marker:row.querySelector('.diff-tag')?.textContent||'',
              cells:[row.querySelector('td button')?.textContent,...[...row.querySelectorAll('td')].slice(1).map(cell=>cell.textContent)]}))"""
        )
        expected = [[t["action"], t["role"], t["from_state"], t["to_state"], ", ".join(t["guards"])]
                    for t in model["transitions"]]
        self.observations.append({"stage": self.stage, "rules": rows, "expected": expected})
        assert [row["cells"] for row in rows] == expected, "Rules inventory/fields differ from authoritative model"
        baseline = self.view()["case"]["baseline"] if self.case_id else None
        previous = {item["id"]: item for item in baseline["transitions"]} if baseline else {}
        for row, rule in zip(rows, model["transitions"], strict=True):
            old = previous.get(rule["id"])
            fields = ("action", "role", "from_state", "to_state", "guards", "required_effects", "forbidden_effects")
            same = old is not None and all((sorted(rule[key]) == sorted(old[key]) if isinstance(rule[key], list)
                                           else rule[key] == old[key]) for key in fields)
            status = "baseline" if baseline is None else "added" if old is None else "unchanged" if same else "changed"
            assert row["id"] == rule["id"] and row["status"] == status, "Rule identity/change marker differs from server snapshots"
            assert row["marker"] == ({"added": "Added", "changed": "Changed"}.get(status, "")), "Visible change marker differs"
        return rows

    def candidate_subject(self, view):
        subject = self.page.locator("#rules-subject")
        replay.expect(subject).to_be_visible()
        text = subject.text_content()
        assert view["case"]["id"] in text, "Rules subject omits exact current case"
        replay.expect(subject).to_have_attribute("data-case-id", view["case"]["id"])
        replay.expect(subject).to_have_attribute("data-revision", str(view["case"]["version"]))
        replay.expect(subject).to_have_attribute("data-semantic-hash", view["packet"]["subject"]["semantic"])
        assert "candidate" in text.lower(), "Rules subject does not identify its current candidate"

    def assert_current_inspector(self, view, ident):
        model = view["case"]["candidate"]
        transition = next(t for t in model["transitions"] if t["id"] == ident)
        observed = {"stage": self.stage, "model_view": self.page.locator("#model-version").input_value(),
                    "selected_transition": self.page.locator("#transition-select").input_value(),
                    "selected_detail": self.page.locator("#selection-detail").text_content(),
                    "canvas": self.page.locator("#model-canvas svg").evaluate(OBSERVE_MODEL)}
        self.observations.append(observed)
        write_json(self.out / "observations.json", self.observations)
        assert observed["model_view"] == "working", "Candidate rule opened a baseline/historical Model view"
        replay.expect(self.page.locator("#transition-select")).to_have_value(ident)
        replay.expect(self.page.locator("#model-source")).to_have_value(transition["from_state"])
        replay.expect(self.page.locator("#target-state")).to_have_value(transition["to_state"])
        replay.expect(self.page.locator("#transition-role")).to_have_value(transition["role"])
        for label, field in (("Guards", "guards"), ("Required effects", "required_effects"), ("Forbidden effects", "forbidden_effects")):
            detail = self.page.locator("#transition-details details").filter(has=self.page.locator("summary", has_text=label))
            assert detail.locator("li").all_text_contents() == (transition[field] or ["None declared"]), f"Inspector {field} differs"
        options = self.page.locator("#transition-select option").evaluate_all("nodes=>nodes.map(node=>node.value).filter(Boolean)")
        assert sorted(options) == sorted(t["id"] for t in model["transitions"]), "Transition dropdown retains wrong model inventory"
        replay.expect(self.page.locator("#selection-detail")).to_have_attribute("data-eija-id", f"eija-review-slice.detail.transition.{ident}")
        replay.expect(self.page.locator(f'#domain-tree [data-kind="transition"][data-item-id="{ident}"]')).to_have_attribute("aria-selected", "true")
        self.canvas_matches(model)
        nodes = observed["canvas"]["nodes"]
        assert sorted(node["state"] for node in nodes) == sorted(model["states"]), "Painted node inventory differs"
        for node in nodes:
            assert node["text"] == node["state"] and node["label"]["displayed"], "State label is absent/unpainted"
            assert node["shape"]["width"] > 0 and node["shape"]["height"] > 0, "State has no painted geometry"
        edges = observed["canvas"]["edges"]
        assert len(edges) == len(model["transitions"]), "Painted transition inventory differs"
        for rule in model["transitions"]:
            edge = next(item for item in edges if item["id"] == f"eija-review-slice.transition.{rule['id']}")
            assert edge["text"] == rule["action"] and edge["label"]["displayed"], "Painted action label differs"
            assert edge["source"] == [rule["from_state"]] and edge["target"] == [rule["to_state"]], "Painted route attaches to wrong state"
            assert edge["path"]["stroke"] not in {"none", "transparent"} and edge["path"]["strokeWidth"] > 0, "Route not painted"
            assert edge["selected"] == str(rule["id"] == ident).lower(), "Painted selection identity differs"
        assert self.packet() == view["packet"], "Navigation replaced authoritative packet"
        replay.expect(self.page.locator("#case-switcher")).to_have_value(self.case_id)
        return observed

    def choose_rule(self, action, *, keyboard=False):
        button = self.page.locator("#rule-table").get_by_role("button", name=action, exact=True)
        if keyboard:
            button.focus()
            button.press("Enter")
            self.navigation_action("key", f"#rule-table button:{action}", "Enter")
        else:
            button.click()
            self.navigation_action("click", f"#rule-table button:{action}")
        self.settled()

    def empty_baseline(self):
        self.entry()
        workbench = self.get("workbench")
        cases = self.get("cases")
        self.tab("impact")
        rows = self.inventory(workbench["model"])
        assert self.get("cases") == cases, "Opening Rules created a case"
        return {"inventory_rows": len(rows), "case_created": False}

    def baseline_to_candidate(self):
        if not self.checks:
            self.entry()
        else:
            self.tab("model")
        before = self.create_candidate()
        self.case_a = self.case_id
        view = self.view()
        assert not any(t["id"] == "TR-SAVE" for t in view["case"]["baseline"]["transitions"]), "Fixture baseline must lack Save"
        assert any(t["id"] == "TR-SAVE" for t in view["case"]["candidate"]["transitions"]), "Fixture candidate must contain Save"
        self.page.locator("#model-version").select_option("baseline")
        self.canvas_matches(view["case"]["baseline"])
        self.tab("impact")
        self.inventory(view["case"]["candidate"])
        self.candidate_subject(view)
        scroller = self.page.get_by_role("region", name="Current model transition rules; scroll for all columns", exact=True)
        replay.expect(scroller).to_have_attribute("tabindex", "0")
        self.shot("baseline-preview-rules-before-click")
        self.choose_rule("Save")
        observed = self.assert_current_inspector(view, "TR-SAVE")
        self.assert_unchanged(before)
        return {"opened_current_candidate": True, "selection": observed["selected_transition"]}

    def history_to_candidate(self):
        self.tab("model")
        self.select_transition("TR-SAVE")
        before = self.view()
        self.page.locator("#transition-role").select_option("Agent")
        preview_before = self.edit_preview_snapshot()
        preview_expected = deepcopy(before["case"]["candidate"])
        next(t for t in preview_expected["transitions"] if t["id"] == "TR-SAVE")["role"] = "Agent"
        self.page.locator("#edit-role").click()
        preview = self.inspect_edit_preview(preview_before, preview_expected)
        self.apply_edit_preview(preview_before, preview)
        view = self.view()
        expected = deepcopy(before["case"]["candidate"])
        next(t for t in expected["transitions"] if t["id"] == "TR-SAVE")["role"] = "Agent"
        assert view["case"]["candidate"] == expected, "Authorized role edit changed unrelated model facts"
        snapshot = self.snapshot()
        self.open_bottom("history-pane")
        self.page.locator("#case-history .history-row").first.get_by_role("button", name="View model", exact=True).click()
        replay.expect(self.page.locator("#model-version")).to_have_value("history")
        self.canvas_matches(snapshot["history"]["selection"]["model"])
        self.tab("impact")
        self.inventory(expected)
        self.choose_rule("Save", keyboard=True)
        self.assert_current_inspector(view, "TR-SAVE")
        self.assert_unchanged(snapshot)
        return {"historical_role": "Owner", "current_role": "Agent", "navigation_writes": False}

    def changes_inspection(self):
        before = self.snapshot()
        self.tab("model")
        self.page.locator("#model-version").select_option("baseline")
        self.select_comparison("transition", "TR-SAVE")
        self.main_comparison().locator('[data-compare-action="inspect-model"]').click()
        self.settled()
        self.assert_current_inspector(self.view(), "TR-SAVE")
        self.assert_unchanged(before)
        return {"comparison_inspects_current_candidate": True}

    def case_roundtrip(self):
        case_a = self.case_id
        saved_a = self.snapshot()
        self.create_candidate()
        case_b = self.case_id
        saved_b = self.snapshot()
        for case_id, snapshot in ((case_b, saved_b), (case_a, saved_a), (case_b, saved_b)):
            self.switch_case(case_id)
            self.tab("model")
            self.page.locator("#model-version").select_option("baseline")
            self.tab("impact")
            self.inventory(snapshot["case"]["candidate"])
            self.choose_rule("Save")
            self.assert_current_inspector(self.view(), "TR-SAVE")
            self.assert_unchanged(snapshot)
        self.switch_case(case_a)
        return {"same_transition_id": "TR-SAVE", "case_a_role": "Agent", "case_b_role": "Owner", "cases": [case_a, case_b]}

    def evidence_context(self):
        before = self.snapshot()
        view = self.view()
        self.tab("impact")
        self.candidate_subject(view)
        self.page.locator("#rules-evidence").click()
        replay.expect(self.page.locator("#evidence-subject")).to_be_visible()
        replay.expect(self.page.locator("#evidence-subject")).to_have_attribute("data-subject-hash", view["packet"]["subject_hash"])
        assert self.packet() == view["packet"], "Rules evidence link changed packet"
        packet = view["packet"]
        assert self.page.locator("#formal details[data-claim]").count() == len(packet["technical_claims"])
        for name, value in packet["technical_claims"].items():
            row = self.page.locator(f'#formal details[data-claim="{name}"]')
            assert row.count() == 1, "Technical claim was dropped or repeated"
            replay.expect(row.locator("summary .evidence-status")).to_have_text(value)
        formal_rows = self.page.locator("#formal details[data-evidence-kind]")
        assert formal_rows.count() == len(packet["formal_evidence"])
        for index, record in enumerate(packet["formal_evidence"]):
            replay.expect(formal_rows.nth(index)).to_have_attribute("data-evidence-kind", record["kind"])
            replay.expect(formal_rows.nth(index).locator("summary .evidence-status")).to_have_text(record["status"])
        for code in view["packet"]["blockers"]:
            replay.expect(self.page.locator("#blockers")).to_contain_text(code)
        self.assert_unchanged(before)
        return {"exact_subject": view["packet"]["subject_hash"], "scope": "Current case-wide packet, not a rule-specific verdict"}

    def impact_navigation(self):
        before = self.snapshot()
        view = self.view()
        refs = view["packet"]["impact"]["affected"]
        assert refs, "Fixture must report affected references"
        observed = []
        for ref in refs:
            self.select_comparison("transition", "TR-SAVE")
            detail = self.main_comparison().locator(".compare-context > details").first
            if detail.get_attribute("open") is None:
                detail.locator(":scope > summary").click()
                self.navigation_action("click", "#review-chapters .compare-context > details:first-child > summary")
            inventory = self.main_comparison().locator("[data-compare-impact], [data-compare-impact-unavailable]").evaluate_all(
                "nodes=>nodes.map(n=>n.dataset.compareImpact||n.dataset.compareImpactUnavailable)"
            )
            assert sorted(inventory) == sorted(refs), "Impact UI omits or invents authoritative references"
            kind, _, action = ref.partition(":")
            transitions = [t for model in (view["case"]["baseline"], view["case"]["candidate"])
                           for t in model["transitions"] if t["action"] == action]
            ids = {t["id"] for t in transitions}
            candidate_action = any(t["action"] == action for t in view["case"]["candidate"]["transitions"])
            target = "review" if kind in {"rule", "state-view"} and len(ids) == 1 else (
                "try" if kind == "runtime" and candidate_action else "impact" if kind == "journey" and candidate_action else
                "evidence" if (kind in {"obligation", "receipt"} and transitions) or ref in {"review-packet", "local-decision"} else None)
            if target is None:
                note = self.main_comparison().locator(f'[data-compare-impact-unavailable="{ref}"]')
                replay.expect(note).to_be_visible()
                assert note.evaluate("n=>n.tagName") == "P", "Unsupported projection masquerades as navigation"
                observed.append({"reference": ref, "status": "unavailable"})
                continue
            navigation_start = len(self.requests)
            button = self.main_comparison().locator(f'[data-compare-impact="{ref}"]')
            button.focus()
            button.press("Enter")
            self.navigation_action("key", f"#review-chapters [data-compare-impact={ref}]", "Enter")
            self.settled()
            replay.expect(self.page.locator("#" + target)).to_be_visible()
            focus = self.page.evaluate("""()=>{const n=document.activeElement;return {id:n.id,tag:n.tagName,
              visible:n.checkVisibility(),pane:n.closest('.tab-content,.comparison-content')?.id};}""")
            assert focus["tag"] != "BODY" and focus["visible"], "Impact navigation lost visible focus"
            if target == "review":
                replay.expect(self.main_comparison().locator(".compare-selection")).to_have_attribute("data-id", next(iter(ids)))
            elif target == "evidence":
                replay.expect(self.page.locator("#evidence-subject")).to_have_attribute("data-subject-hash", view["packet"]["subject_hash"])
                if ref == "local-decision":
                    replay.expect(self.page.locator("#review-decision")).to_have_attribute("open", "")
                    assert focus["id"] == "review-subject", "Decision navigation did not focus its explicit review location"
                else:
                    assert focus["id"] == "evidence-subject", "Case-wide evidence navigation lost its subject focus"
            elif target == "impact":
                self.candidate_subject(view)
                replay.expect(self.page.locator("#rules-journeys")).to_have_attribute("open", "")
            elif target == "try":
                replay.expect(self.page.locator("#runtime-state")).to_have_text("Not started")
            assert not self.page.locator("#acknowledge").is_checked(), "Navigation acknowledged an owner decision"
            assert all(not value for value in self.page.locator("#questions input").evaluate_all("nodes=>nodes.map(n=>n.value)")), "Navigation filled review answers"
            requests = self.requests[navigation_start:]
            assert all(item["method"] == "GET" for item in requests), "Impact navigation performed a mutation"
            assert not any(item["path"] == "/api/repository/source" for item in requests), "Projection reference guessed a source binding"
            assert self.view() == view, "Impact navigation changed the server case/packet/runtime observations"
            observed.append({"reference": ref, "target": target, "focus": focus})
        self.assert_unchanged(before)
        return {"references": observed, "no_execution_or_owner_mutations": True,
                "unknown_and_ambiguous_fixture_controls": "NOT_RUN: this server fixture has only its declared generated references"}

    def keyboard_viewports(self):
        before = self.snapshot()
        view = self.view()
        observations = []
        for width, height in ((1440, 900), (1280, 800)):
            self.page.set_viewport_size({"width": width, "height": height})
            self.tab("impact")
            self.candidate_subject(view)
            self.inventory(view["case"]["candidate"])
            self.shot(f"rules-first-view-{width}")
            for ident in ("rules-state-flow", "rules-journeys", "rules-edit"):
                details = self.page.locator("#" + ident)
                summary = details.locator(":scope > summary")
                summary.focus()
                opened = details.get_attribute("open") is not None
                summary.press("Enter")
                assert (details.get_attribute("open") is not None) != opened, "Native disclosure did not toggle"
                summary.press("Enter")
                assert (details.get_attribute("open") is not None) == opened, "Disclosure did not return to prior state"
                assert summary.evaluate("node=>node===document.activeElement"), "Disclosure lost keyboard focus"
                self.navigation_action("key", "#" + ident + " > summary", "Enter twice")
            assert self.page.locator("#journeys p").all_text_contents() == view["packet"]["projections"]["journeys"], "Disclosed journeys lost authoritative facts"
            scroller = self.page.get_by_role("region", name="Current model transition rules; scroll for all columns", exact=True)
            scroller.focus()
            scroller.press("Home")
            horizontal = scroller.evaluate("n=>({left:n.scrollLeft,width:n.clientWidth,total:n.scrollWidth})")
            if horizontal["total"] > horizontal["width"]:
                scroller.press("ArrowRight")
                self.page.wait_for_function("() => document.querySelector('#rule-table').closest('[role=region]').scrollLeft > 0")
                scroller.press("Home")
            assert scroller.evaluate("n=>document.activeElement===n"), "Table scroller lost keyboard focus"
            bounds = self.page.evaluate("()=>({viewport:innerWidth,body:document.body.scrollWidth,document:document.documentElement.scrollWidth})")
            assert bounds["body"] <= width and bounds["document"] <= width, "Rules page overflows horizontally"
            self.choose_rule("Save", keyboard=True)
            self.assert_current_inspector(view, "TR-SAVE")
            self.shot(f"rules-model-{width}")
            observations.append({"width": width, "height": height, "bounds": bounds, "table": horizontal})
        self.assert_unchanged(before)
        return {"viewports": observations, "keyboard": True, "human_usability": "NOT_RUN"}


def main():
    if not __debug__:
        emit({"status": "NOT_RUN", "reason": "Assertion oracles require Python without -O/-OO."})
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--scenario", choices=("all", "candidate-context"), default="all")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    if replay.PREREQUISITE_ERROR:
        write_json(out / "result.json", {"status": "NOT_RUN", "reason": replay.PREREQUISITE_ERROR})
        return 3
    before = subject_identity()
    write_json(out / "subject-before.json", before)
    (out / "replay-script.py").write_bytes(Path(__file__).read_bytes())
    result = {"schema": "eija.rules-ripple-browser.v1", "status": "FAIL", "scenario": args.scenario,
              "utc": datetime.now(UTC).isoformat(), "identity": "normal_source_review_required", "provider": "offline",
              "browser_closed": False, "server_closed": False, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "not_covered": ["human usability", "live providers", "owner operations", "unknown/ambiguous impact fixture", "removed rule fixture"]}
    review, address = None, None
    try:
        with replay.disposable_server() as base:
            endpoint = urlsplit(base)
            address = (endpoint.hostname, endpoint.port)
            with replay.sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                result["browser_version"] = browser.version
                try:
                    page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    page.set_default_timeout(30000)
                    review = RulesReview(page, out, base)
                    actions = [("baseline-to-current-candidate", review.baseline_to_candidate)]
                    if args.scenario == "all":
                        actions = [("empty-baseline-inventory", review.empty_baseline), *actions,
                                   ("history-to-current-candidate", review.history_to_candidate),
                                   ("changes-inspect-current", review.changes_inspection),
                                   ("case-roundtrip", review.case_roundtrip),
                                   ("rules-evidence-subject", review.evidence_context),
                                   ("impact-reference-navigation", review.impact_navigation),
                                   ("keyboard-viewports", review.keyboard_viewports)]
                    for name, action in actions:
                        review.step(name, action)
                        emit({"check": name, "status": "PASS"})
                    assert not review.errors and not review.forbidden and not review.http_errors, "Unexpected browser or HTTP failures"
                    result["status"] = "PASS"
                finally:
                    try:
                        if review is not None:
                            page.screenshot(path=str(out / "final.png"), full_page=True)
                    finally:
                        browser.close()
                        result["browser_closed"] = True
    except Exception as error:  # Retain unexpected browser/oracle failures and close owned resources.
        result["error"] = {"type": type(error).__name__, "message": str(error).replace(replay.TEST_CAPABILITY, "[test-capability]"),
                           "traceback": traceback.format_exc().replace(replay.TEST_CAPABILITY, "[test-capability]")}
        emit({"status": "FAIL", "error": result["error"]})
    finally:
        if address is not None:
            with socket.socket() as probe:
                probe.settimeout(.2)
                result["server_closed"] = probe.connect_ex(address) != 0
        if not result["browser_closed"] or not result["server_closed"]:
            result["status"] = "FAIL"
        if review is not None:
            result.update({"checks": review.checks, "failed_stage": review.stage if result["status"] != "PASS" else None,
                           "requests": review.requests, "http_errors": review.http_errors, "javascript_errors": review.errors,
                           "forbidden_attempts": review.forbidden, "navigation_actions": review.navigation_actions})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
            write_json(out / "observations.json", review.observations)
        after = subject_identity()
        write_json(out / "subject-after.json", after)
        result["subject_preservation"] = compare_subjects(before, after)
        if result["subject_preservation"]["status"] != "UNCHANGED":
            result["status"] = "FAIL"
        result["subject_content_sha256"] = before["content_sha256"]
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {path.relative_to(out).as_posix(): {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                                                    for path in sorted(out.rglob("*")) if path.is_file()})
    emit({key: result[key] for key in ("status", "browser_closed", "server_closed", "subject_preservation")})
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
