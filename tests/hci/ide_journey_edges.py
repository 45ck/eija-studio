"""Independent browser journeys through the real disposable, normal-identity IDE.

Mutations use ordinary controls. GET responses supply the model/history/source oracle.
One transport fault is an aborted real GET, never a fabricated model response.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import self_dogfood_replay as replay
from self_dogfood_subject import capture_subject, compare_subjects, file_identity

STORIES = (
    "source-first", "intent-first-changes", "cross-case-history-source",
    "cancel-unsubmitted-edit", "stale-second-page", "transport-retry", "keyboard-edit-refusal",
)
SCRIPT = "tests/hci/ide_journey_edges.py"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def redacted(error):
    return str(error).replace(replay.TEST_CAPABILITY, "[test-capability]")


class Journey(replay.Review):
    def __init__(self, page, out, base):
        super().__init__(page, out, base)
        self.oracles = []
        self.abort_get = None
        self.aborted = []
        self.expected_http = []

    def route(self, route):
        path = urlsplit(route.request.url).path
        if route.request.method == "GET" and path == self.abort_get:
            self.abort_get = None
            self.aborted.append(path)
            route.abort("failed")
            return
        super().route(route)

    def get(self, path):
        response = self.page.context.request.get(
            self.base + "api/" + path,
            headers={"Authorization": "Bearer " + replay.TEST_CAPABILITY},
        )
        assert response.status == 200, f"Oracle GET {path}: HTTP {response.status}"
        payload = response.json()
        self.oracles.append({"path": path, "body": payload})
        return payload

    def snapshot(self, case_id=None):
        case_id = case_id or self.case_id
        view = self.get("cases/" + case_id)
        return {"case": view["case"], "subject": view["packet"]["subject"],
                "history": self.get(f"cases/{case_id}/history")}

    def assert_unchanged(self, before):
        after = self.snapshot(before["case"]["id"])
        assert after == before, "Navigation/draft/refusal changed the authoritative case, subject or history."
        return after

    def shot(self, name):
        self.page.screenshot(path=str(self.out / (name + ".png")), full_page=True)

    def create_candidate(self):
        self.intent()
        return self.snapshot()

    def switch_case(self, case_id):
        self.page.locator("#case-switcher").select_option(case_id)
        self.settled()
        self.case_id = case_id
        expect = replay.expect
        view = self.get("cases/" + case_id)
        expect(self.page.locator("#case-title")).to_have_text(view["case"]["request"])
        expect(self.page.locator("#case-switcher")).to_have_value(case_id)
        expect(self.page.locator("#case-id")).to_contain_text(case_id[:10])
        expect(self.page.locator("#case-id")).to_contain_text(f"REVISION {view['case']['version']}")
        expect(self.page.locator("#case-stage")).to_have_text(view["case"]["stage"])

    def canvas_matches(self, model):
        states = self.page.locator("#model-canvas [data-state]").evaluate_all(
            "nodes => nodes.map(node => node.getAttribute('data-state'))"
        )
        assert sorted(states) == sorted(model["states"]), "Canvas states disagree with the GET model."
        expected = sorted(f"{t['action']}, {t['role']}, {t['from_state']} to {t['to_state']}. Select transition."
                          for t in model["transitions"])
        actual = self.page.locator("#model-canvas .model-edge").evaluate_all(
            "nodes => nodes.map(node => node.getAttribute('aria-label'))"
        )
        assert sorted(actual) == expected, "Canvas transitions disagree with the GET model."

    def history_matches(self, history):
        replay.expect(self.page.locator("#history-count")).to_have_text(str(len(history["edits"])))
        rows = self.page.locator("#case-history .history-row")
        replay.expect(rows).to_have_count(1 + len(history["edits"]) + len(history["redo"]))
        text = self.page.locator("#case-history").text_content()
        assert f"Case revision {history['version']}" in text
        assert f"semantic cursor {history['cursor']}" in text
        for item in [history["selection"], *history["edits"], *history["redo"]]:
            assert item["semantic_hash"] in text
        assert self.page.locator("#undo-edit").is_enabled() == history["can_undo"]
        assert self.page.locator("#redo-edit").is_enabled() == history["can_redo"]

    def source_refs(self):
        workbench = self.get("workbench")
        refs = list(dict.fromkeys(ref for term in workbench["language"]["terms"]
                                 for ref in term.get("binds", []) if ref.startswith("repo://")))
        assert len(refs) >= 2, "This story needs two declared source bindings."
        return refs

    def source_matches(self, ref):
        data = self.get("repository/source?" + urlencode({"reference": ref}))
        assert data["status"] == "connected", "Declared source binding is unavailable."
        replay.expect(self.page.locator("#source-reference")).to_have_value(data["reference"])
        replay.expect(self.page.locator("#source-file")).to_contain_text(data["path"])
        lines = re.split(r"\r?\n", data["text"])
        if lines and lines[-1] == "":
            lines.pop()
        actual = self.page.locator("#source-reader .source-line code").all_text_contents()
        assert actual == [line or " " for line in lines], "Visible source differs from the captured GET text."
        numbers = self.page.locator("#source-reader .line-number").all_text_contents()
        assert numbers == [str(data["lines"]["start"] + index) for index in range(len(lines))]
        meta = self.page.locator("#source-metadata").text_content()
        for name in ("source_hash", "graph_hash", "file_hash", "snippet_hash"):
            assert data[name] in meta, f"Visible source lacks its captured {name}."
        return {key: data[key] for key in ("reference", "source_hash", "file_hash", "snippet_hash")}

    def open_source(self, ref):
        self.tab("code")
        self.page.locator("#source-reference").fill(ref)
        self.page.locator("#source-reference").press("Enter")
        replay.expect(self.page.locator("#source-reader .source-line").first).to_be_visible(timeout=30000)
        return self.source_matches(ref)

    def role_choice(self, transition, role, legal):
        data = self.get(f"cases/{self.case_id}/affordances")
        choices = [entry for entry in data["affordances"] if entry["element"] == "transition:" + transition
                   and entry["kind"] == "set_role" and entry["target"] == "role:" + role]
        assert len(choices) == 1 and choices[0]["legal"] is legal, "Fixture role affordance changed."
        return choices[0]

    def edit_role(self, transition="TR-SAVE", role="Agent"):
        choice = self.role_choice(transition, role, True)
        self.tab("model")
        self.page.locator("#transition-select").select_option(transition)
        self.page.locator("#transition-role").select_option(role)
        self.page.locator("#edit-role").click()
        self.settled()
        return choice

    def assert_role_edit(self, before, transition, role, transaction):
        after = self.snapshot()
        expected = deepcopy(before["case"]["candidate"])
        next(t for t in expected["transitions"] if t["id"] == transition)["role"] = role
        assert after["case"]["candidate"] == expected, "Edit changed more than its selected role."
        assert after["case"]["baseline"] == before["case"]["baseline"]
        assert after["case"]["version"] == before["case"]["version"] + 1
        assert after["case"]["transactions"] == [*before["case"]["transactions"], transaction]
        assert after["history"]["cursor"] == before["history"]["cursor"] + 1
        self.canvas_matches(expected)
        return after

    def palette(self, command):
        self.page.keyboard.press("Control+k")
        replay.expect(self.page.locator("#palette-search")).to_be_focused()
        self.page.keyboard.type(command)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        replay.expect(self.page.locator("#command-palette")).not_to_be_visible()
        self.settled()

    def keyboard_to(self, selector):
        target = self.page.locator(selector)
        for _ in range(80):
            if target.evaluate("node => node === document.activeElement"):
                return
            self.page.keyboard.press("Tab")
        raise AssertionError(f"Keyboard cannot reach {selector} in 80 Tab presses.")

    def keyboard_select(self, selector, value):
        self.keyboard_to(selector)
        select = self.page.locator(selector)
        values = select.locator("option").evaluate_all("nodes => nodes.map(node => node.value)")
        assert value in values
        self.page.keyboard.press("Home")
        for _ in range(values.index(value)):
            self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Tab")
        replay.expect(select).to_have_value(value)

    def source_first(self):
        workbench = self.get("workbench")
        before = self.get("cases")
        identity = self.open_source(self.source_refs()[0])
        self.shot("source-first-open")
        self.tab("model")
        self.canvas_matches(workbench["model"])
        replay.expect(self.page.locator("#case-stage")).to_have_text("BASELINE")
        assert self.get("cases") == before
        assert not any(r["method"] == "POST" for r in self.requests)
        return {"source": identity, "baseline_without_case": True}

    def intent_first_changes(self):
        before = self.create_candidate()
        self.tab("review")
        replay.expect(self.page.locator("#review-chapters")).to_contain_text("Save")
        replay.expect(self.page.locator('[data-eija-id="review.transition.TR-SAVE"]')).to_be_visible()
        self.assert_unchanged(before)
        return {"case": self.case_id, "subject": before["subject"], "provider": "offline"}

    def cross_case_history_source(self):
        first = self.create_candidate()["case"]["id"]
        self.label += " second"
        second = self.create_candidate()["case"]["id"]
        refs = self.source_refs()
        self.page.locator("#transition-select").select_option("TR-APPROVE")
        second_source = self.open_source(refs[1])
        self.switch_case(first)
        self.edit_role()
        before_first, before_second = self.snapshot(first), self.snapshot(second)
        self.page.locator('[data-bottom="history-pane"]').click()
        self.page.locator("#case-history .history-row").first.get_by_role("button", name="View model").click()
        historical = before_first["history"]["selection"]["model"]
        self.canvas_matches(historical)
        first_source = self.open_source(refs[0])
        self.switch_case(second)
        replay.expect(self.page.locator("#model-version")).to_have_value("working")
        replay.expect(self.page.locator("#transition-select")).to_have_value("TR-APPROVE")
        self.canvas_matches(before_second["case"]["candidate"])
        self.history_matches(before_second["history"])
        # Source is repository-scoped: its URI and captured hashes, not the case, identify it.
        shown_reference = self.page.locator("#source-reference").input_value()
        assert shown_reference in {first_source["reference"], second_source["reference"]}, "Source navigation changed to an unopened reference."
        shared_source = self.source_matches(shown_reference)
        selected = next(t for t in before_second["case"]["candidate"]["transitions"] if t["id"] == "TR-APPROVE")
        selection = self.page.locator("#selection-detail").inner_text()
        self.shot("second-case-restored")
        selection_leaked = selected["action"] not in selection
        self.switch_case(first)
        replay.expect(self.page.locator("#model-version")).to_have_value("history")
        self.canvas_matches(historical)
        self.history_matches(before_first["history"])
        self.tab("model")
        replay.expect(self.page.locator("#model-empty")).to_contain_text("Read-only historical preview")
        replay.expect(self.page.locator("#edit-role")).to_be_disabled()
        self.shot("first-case-history-restored")
        self.page.locator("#model-version").select_option("working")
        self.canvas_matches(before_first["case"]["candidate"])
        self.assert_unchanged(before_first)
        self.assert_unchanged(before_second)
        assert not selection_leaked, "Case B restored its transition but leaked case A's inspector selection."
        return {"cases": [first, second], "repository_source": shared_source, "historical_preview_restored": True}

    def cancel_unsubmitted_edit(self):
        before = self.create_candidate()
        self.page.locator("#transition-select").select_option("TR-SAVE")
        original = self.page.locator("#transition-role").input_value()
        self.page.locator("#transition-role").select_option("Agent")
        writes = len([r for r in self.requests if r["method"] == "POST"])
        self.assert_unchanged(before)
        cancel = self.page.get_by_role("button", name="Cancel draft", exact=True)
        if cancel.count():
            cancel.click()
            replay.expect(self.page.locator("#transition-role")).to_have_value(original)
            result = {"cancel_control": True}
        else:
            self.page.locator("#transition-role").press("Escape")
            self.shot("unsent-draft-no-cancel")
            retained = self.page.locator("#transition-role").input_value()
            self.page.locator("#transition-role").select_option(original)
            result = {"status": "GAP", "reason": "No explicit Cancel draft control; manual reselection is not cancellation.",
                      "escape_retained_draft": retained != original}
        assert len([r for r in self.requests if r["method"] == "POST"]) == writes
        self.assert_unchanged(before)
        return result | {"authoritative_case_subject_history_unchanged": True}

    def stale_second_page(self):
        before = self.create_candidate()
        self.page.locator("#transition-select").select_option("TR-SAVE")
        self.page.locator("#transition-role").select_option("Agent")
        second = Journey(self.page.context.new_page(), self.out, self.base)
        try:
            second.entry()
            second.switch_case(self.case_id)
            choice = second.edit_role()
            winner = second.assert_role_edit(before, "TR-SAVE", "Agent", choice["transaction"])
            self.page.locator("#edit-role").click()
            self.settled()
            replay.expect(self.page.locator("#notice")).to_contain_text("STALE_VERSION")
            self.expected_http.append({"status": 409, "path": f"/api/cases/{self.case_id}/edit"})
            self.assert_unchanged(winner)
            self.canvas_matches(before["case"]["candidate"])
            self.shot("stale-rejected")
            self.palette("Refresh current model")
            self.canvas_matches(winner["case"]["candidate"])
            self.assert_unchanged(winner)
            assert not second.errors and not second.http_errors and not second.forbidden
            return {"stale_version": before["case"]["version"], "accepted_version": winner["case"]["version"],
                    "stale_write_refused": True, "refresh_restored_server_model": True}
        finally:
            write_json(self.out / "second-page.json", {"requests": second.requests, "oracles": second.oracles,
                                                       "errors": second.errors, "forbidden": second.forbidden})
            second.page.close()

    def transport_retry(self):
        before = self.create_candidate()
        self.page.locator("#transition-select").select_option("TR-SAVE")
        self.abort_get = f"/api/cases/{self.case_id}"
        self.palette("Refresh current model")
        assert self.aborted == [f"/api/cases/{self.case_id}"]
        replay.expect(self.page.locator("#error-json")).to_contain_text("REQUEST_FAILED")
        failed_diagnostic = json.loads(self.page.locator("#error-json").text_content())
        self.canvas_matches(before["case"]["candidate"])
        replay.expect(self.page.locator("#transition-select")).to_have_value("TR-SAVE")
        self.assert_unchanged(before)
        self.shot("transport-error-state-retained")
        self.palette("Refresh current model")
        self.canvas_matches(before["case"]["candidate"])
        self.assert_unchanged(before)
        replay.expect(self.page.locator("#notice")).not_to_have_class("error")
        replay.expect(self.page.locator("#error-details")).to_be_hidden()
        replay.expect(self.page.locator("#problems")).not_to_contain_text(failed_diagnostic["message"])
        return {"aborted_gets": self.aborted, "server_state_preserved": True, "explicit_retry": True}

    def keyboard_edit_refusal(self):
        before = self.create_candidate()
        allowed = self.role_choice("TR-SAVE", "Agent", True)
        self.palette("Select a transition")
        self.keyboard_select("#transition-select", "TR-SAVE")
        self.keyboard_select("#transition-role", "Agent")
        self.keyboard_to("#edit-role")
        self.page.keyboard.press("Enter")
        self.settled()
        after = self.assert_role_edit(before, "TR-SAVE", "Agent", allowed["transaction"])
        self.shot("keyboard-supported-edit")
        refused = self.role_choice("TR-APPROVE", "Agent", False)
        self.palette("Select a transition")
        self.keyboard_select("#transition-select", "TR-APPROVE")
        self.keyboard_select("#transition-role", "Agent")
        self.keyboard_to("#edit-role")
        writes = sum(r["method"] == "POST" and r["path"].endswith("/edit") for r in self.requests)
        self.page.keyboard.press("Enter")
        self.settled()
        replay.expect(self.page.locator("#notice")).to_contain_text("EDIT_REFUSED")
        diagnostic = json.loads(self.page.locator("#error-json").text_content())
        assert diagnostic["details"]["codes"] == refused["codes"]
        assert diagnostic["details"]["refs"] == refused["refs"]
        assert sum(r["method"] == "POST" and r["path"].endswith("/edit") for r in self.requests) == writes
        self.assert_unchanged(after)
        self.canvas_matches(after["case"]["candidate"])
        replay.expect(self.page.locator("#edit-role")).to_be_focused()
        return {"keyboard_only_after_fixture_setup": True, "refusal_codes": refused["codes"],
                "refused_transaction_not_committed": True}


def run_story(browser, base, out, name):
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(viewport={"width": 1600, "height": 1100}, device_scale_factor=1)
    journey = Journey(context.new_page(), folder, base)
    journey.stage = name
    try:
        journey.entry()
        evidence = getattr(journey, name.replace("-", "_"))()
        status = evidence.pop("status", "PASS")
        result = {"id": name, "status": status, "evidence": evidence}
    except Exception as error:
        result = {"id": name, "status": "FAIL", "reason": redacted(error)}
    try:
        journey.shot("final")
    except replay.BrowserError as error:
        result = result | {"status": "FAIL", "screenshot_error": redacted(error)}
    unexpected = [item for item in journey.http_errors
                  if {key: item[key] for key in ("status", "path")} not in journey.expected_http]
    if journey.errors or journey.forbidden or unexpected:
        result["status"] = "FAIL"
    result |= {"javascript_errors": journey.errors, "unexpected_http": unexpected,
               "forbidden_requests": journey.forbidden, "case_id": journey.case_id}
    write_json(folder / "oracle-responses.json", journey.oracles)
    write_json(folder / "requests.json", journey.requests)
    write_json(folder / "result.json", result)
    context.close()
    sys.stdout.write(json.dumps({"story": name, "status": result["status"], "reason": result.get("reason")}) + "\n")
    sys.stdout.flush()
    return result


def subject(root):
    result = capture_subject(root)
    result["scope"].append(SCRIPT)
    result["files"][SCRIPT] = file_identity(root, SCRIPT) | {"git_state": "explicit-test-subject"}
    identities = {name: item["sha256"] for name, item in result["files"].items()}
    result["content_sha256"] = hashlib.sha256(json.dumps(identities, sort_keys=True).encode()).hexdigest()
    return result


def execute(args):
    if not __debug__ or replay.PREREQUISITE_ERROR:
        return {"outcome": "NOT_RUN", "checks": [],
                "reason": replay.PREREQUISITE_ERROR or "Python -O disables the assertion oracles."}
    try:
        with replay.disposable_server() as base, replay.sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                results = [run_story(browser, base, args.out, name) for name in args.story]
                return {"checks": results, "browser": browser.version,
                        "outcome": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"}
            finally:
                browser.close()
    except replay.BrowserError as error:
        if "Executable doesn't exist" in str(error):
            return {"outcome": "NOT_RUN", "checks": [], "reason": "Isolated Chromium is not installed."}
        raise


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=root / "reports/ide-journey-edges")
    parser.add_argument("--story", choices=STORIES, action="append", help="Run named stories; default is all seven.")
    args = parser.parse_args()
    args.story = list(dict.fromkeys(args.story or STORIES))
    args.out.mkdir(parents=True, exist_ok=True)
    before = subject(root)
    try:
        report = execute(args)
    except Exception as error:
        report = {"outcome": "FAIL", "checks": [], "reason": redacted(error)}
    finally:
        after = subject(root)
        comparison = compare_subjects(before, after)
        write_json(args.out / "subject-manifest.json", {"before": before, "after": after, "comparison": comparison})
    if comparison["status"] != "UNCHANGED":
        report["outcome"] = "FAIL"
    completed = {item["id"] for item in report["checks"]}
    report["checks"].extend({"id": name, "status": "NOT_RUN", "reason": report.get("reason", "Not selected.")}
                            for name in STORIES if name not in completed)
    report |= {"schema": "eija.ide-journey-edges.v1", "utc": datetime.now(UTC).isoformat(),
               "identity": "normal_source_review_required", "human_value": "NOT_MEASURED",
               "source_preservation": comparison, "selected_stories": args.story,
               "scope": "Synthetic isolated local browser; no owner approval/apply or live provider."}
    write_json(args.out / "observations.json", report)
    sys.stdout.write(json.dumps({"outcome": report["outcome"], "report": str(args.out / "observations.json"),
                                 "checks": [(item["id"], item["status"]) for item in report["checks"]]}) + "\n")
    return {"PASS": 0, "FAIL": 1, "NOT_RUN": 2}[report["outcome"]]


if __name__ == "__main__":
    raise SystemExit(main())
