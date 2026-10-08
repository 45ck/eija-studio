"""Continuous source-first EIJA journey, composing existing acceptance helpers.

Prepared orchestration only. Root runs serially after the endpoint preflight.
No source mutation, receipt stamping, verification, live provider or owner action.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import socket
import sys
import traceback
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
COMBINED_SHA = "edb80eb0b7cf4555784e2ab0d90e5342f338e9e04da8be04bbf9a20a8c539d42"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_combined(path):
    content = path.read_bytes()
    assert hashlib.sha256(content).hexdigest() == COMBINED_SHA, "Frozen combined dependency changed; review before rebasing"
    spec = importlib.util.spec_from_file_location("source_first_combined_dependency", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, content


def journey_type(combined, runtime, replay, repo):
    class SourceFirstJourney(combined.journey_type(runtime, replay)):
        """Add entry/inspection/restoration seams without copying the scenario engine."""

        def __init__(self, page, out, base):
            super().__init__(page, out, base)
            self.main_case_id = None
            self.whole_flow = []
            self.source_entry = None
            self.initial_connection = None
            self.inspected_success = False

        def note(self, label, value):
            self.whole_flow.append({"label": label, "evidence": value})
            write_json(self.out / "whole-flow-observations.json", self.whole_flow)
            return value

        def source_scope(self, label):
            workbench, status = self.get("workbench"), self.get("status")
            connection = workbench["connection"]
            assert workbench["pack"]["id"] == "eija-review-slice"
            assert status["provider"] == "offline" and status["network_enabled"] is False
            assert status["trusted_fixture"] is False
            assert connection["status"] == "connected" and connection["read_only"] is True
            assert Path(connection["root"]).resolve() == repo
            coverage, facts = connection["coverage"], connection["observed_facts"]
            assert coverage["semantic_complete"] is False
            assert facts["extraction"]["executes_target"] is False
            assert facts["conformance"]["status"] == "NOT_RUN"
            assert facts["declared_model"]["status"] == "DECLARED_REFERENCE_JOURNEY"
            assert facts["declared_model"]["pack_id"] == workbench["pack"]["id"]
            assert facts["declared_model"]["pack_digest"] == workbench["pack"]["digest"]
            if self.initial_connection is not None:
                for key in ("root", "source_hash", "graph_hash", "file_hashes", "pack", "coverage", "observed_facts", "bindings"):
                    assert connection[key] == self.initial_connection[key], "Source capture changed during model journey: " + key
            self.tab("source")
            view = self.page.locator("#source-view")
            replay.expect(view).to_contain_text("Repository snapshot available")
            replay.expect(view).to_contain_text("Tests via source indexing: NOT_RUN")
            replay.expect(view).to_contain_text("Semantic coverage: Partial")
            replay.expect(view).to_contain_text("Conformance: NOT_RUN")
            for value in (connection["root"], connection["source_hash"], connection["graph_hash"],
                          coverage["scope"], facts["declared_model"]["scope"], facts["conformance"]["reason"],
                          *coverage["limitations"], *facts["extraction"]["limitations"]):
                replay.expect(view).to_contain_text(value)
            replay.expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
            self.shot(label + "-source-scope")
            self.note(label + "-source-scope", {"connection": connection, "provider": "offline", "network_enabled": False})
            return workbench

        def entry(self):
            result = super().entry()
            self.stage = "source-first-before-intent"
            assert self.get("cases") == []
            self.initial_connection = self.source_scope("initial")["connection"]
            self.source_entry = self.source_first()
            assert self.source_entry["source"]["source_hash"] == self.initial_connection["source_hash"]
            assert self.get("cases") == [] and self.post_bodies == []
            self.note("source-before-any-case", self.source_entry)
            return result

        def create_candidate(self):
            start = len(self.post_bodies)
            result = super().create_candidate()
            case = result["case"]
            expected = [
                ("/api/cases", {"request": case["request"]}),
                (f"/api/cases/{case['id']}/propose", {"expected_version": 0, "consent": False}),
                (f"/api/cases/{case['id']}/select", {"expected_version": 1, "interpretation": "show_saved_path"}),
            ]
            actual = self.post_bodies[start:]
            assert [(row["path"], row["body"]) for row in actual] == expected
            assert all(row["method"] == "POST" for row in actual)
            assert case["version"] == 2 and case["selected_meaning"] == "show_saved_path"
            run = case["provider_run"]
            assert run["provider"] == "offline" and run["live"] is False and run["egress"] is False
            if self.main_case_id is None:
                self.main_case_id = self.case_id
                self.stage = "inspect-initial-real-model-change"
                before = self.view()
                assert "SAVED" not in case["baseline"]["states"] and "SAVED" in case["candidate"]["states"]
                assert not any(t["id"] == "TR-SAVE" for t in case["baseline"]["transitions"])
                detail = self.assert_comparison_transition("TR-SAVE", case["baseline"], case["candidate"])
                replay.expect(detail).to_be_visible()
                assert self.view() == before and self.snapshot() == result
                assert len(self.post_bodies) == start + 3
                self.note("actual-initial-model-change", {"case_id": self.case_id, "revision": case["version"],
                    "subject": result["subject"], "added_state": "SAVED", "added_transition": "TR-SAVE",
                    "baseline": case["baseline"], "candidate": case["candidate"], "setup_requests": actual})
                self.shot("initial-actual-model-change")
                self.command("Open Model", "model")
            return result

        def evidence_current(self):
            super().evidence_current()
            if self.inspected_success:
                return
            assert self.stage == "repaired-runtime", "Source/formal inspection must occur after successful repair and before undo"
            self.inspected_success = True
            before = self.checkpoint("before-source-formal-limits")
            count = len(self.post_bodies)
            self.inspection_read_only = True
            try:
                workbench = self.source_scope("after-runtime-success")
                source = self.open_source(self.source_entry["source"]["reference"])
                assert source == self.source_entry["source"]
                self.command("Open Evidence", "evidence")
                inventory = self.formal_unavailable_view(before["view"], workbench)
                replay.expect(self.page.locator('#formal [data-inspection-path]')).to_have_count(0)
                after = self.checkpoint("after-source-formal-limits")
                assert after["view"] == before["view"] and after["history"] == before["history"]
                assert len(self.post_bodies) == count
                self.note("success-does-not-promote-source-or-formal-evidence", {
                    "case_id": self.case_id, "revision": before["view"]["case"]["version"],
                    "subject": before["view"]["packet"]["subject"], "source": source, "formal_inventory": inventory,
                    "availability": "NO_DECIDING_RECEIPT", "records": [], "navigation_links": 0, "mutations": 0})
            finally:
                self.inspection_read_only = False

        def assert_case_surface(self, captured, transition):
            case, history = captured["view"]["case"], captured["history"]
            assert self.case_id == case["id"]
            assert self.view() == captured["view"] and self.get(f"cases/{self.case_id}/history") == history
            assert self.revision() == case["version"] and self.semantic() == captured["view"]["packet"]["subject"]["semantic"]
            replay.expect(self.page.locator("#model-version")).to_have_value("working")
            replay.expect(self.page.locator("#transition-select")).to_have_value(transition)
            self.canvas_matches(case["candidate"])
            self.history_matches(history)
            self.reveal_inspector()
            selected = next(t for t in case["candidate"]["transitions"] if t["id"] == transition)
            detail = self.page.locator("#selection-detail")
            replay.expect(detail).to_have_attribute("data-eija-id", case["candidate"]["id"] + ".detail.transition." + transition)
            replay.expect(detail.locator("h3")).to_have_text(selected["action"])
            replay.expect(self.page.locator("#runtime-rule-navigation button")).to_have_count(0)
            replay.expect(detail.locator("[data-runtime-attempt]")).to_have_count(0)

        def case_switch_return(self):
            self.stage = "case-switch-control-setup"
            before = self.checkpoint("main-before-control-case")
            count = len(self.post_bodies)
            self.label += " switch control"
            control = self.create_candidate()
            control_id = self.case_id
            assert control_id != self.main_case_id
            assert len(self.post_bodies) == count + 3
            assert self.get("cases/" + self.main_case_id) == before["view"]
            assert self.get(f"cases/{self.main_case_id}/history") == before["history"]
            control_view = {"view": self.view(), "history": control["history"]}
            self.select_transition("TR-APPROVE")
            self.open_source(self.source_refs()[1])
            self.stage = "case-switch-and-return-read-only"
            self.inspection_read_only = True
            writes = list(self.post_bodies)
            try:
                # Establish contexts after creation: the creation command intentionally resets edit selection.
                self.switch_case(self.main_case_id)
                self.select_save()
                self.assert_comparison_transition("TR-SAVE", before["view"]["case"]["baseline"], before["view"]["case"]["candidate"])
                source = self.open_source(self.source_entry["source"]["reference"])
                assert source == self.source_entry["source"]
                self.command("Open Model", "model")
                self.assert_case_surface(before, "TR-SAVE")
                self.switch_case(control_id)
                self.assert_view("code")
                self.assert_case_surface(control_view, "TR-APPROVE")
                # Source history is repository-scoped; its exact captured reference remains independent of case selection.
                assert self.source_matches(source["reference"]) == source
                self.shot("switch-control-restores-distinct-selection")
                self.switch_case(self.main_case_id)
                self.assert_view("model")
                self.assert_case_surface(before, "TR-SAVE")
                # Inspect the restored comparison before any control can select it again.
                restored = self.main_comparison().locator(".compare-selection")
                replay.expect(restored).to_have_attribute("data-kind", "transition")
                replay.expect(restored).to_have_attribute("data-id", "TR-SAVE")
                self.assert_comparison_transition("TR-SAVE", before["view"]["case"]["baseline"], before["view"]["case"]["candidate"])
                comparison = self.main_comparison().locator(".paired-compare")
                replay.expect(comparison).to_have_attribute("data-case", self.main_case_id)
                replay.expect(comparison).to_have_attribute("data-revision", str(before["view"]["case"]["version"]))
                super().evidence_current()
                assert self.get("cases/" + control_id) == control_view["view"]
                assert self.get(f"cases/{control_id}/history") == control_view["history"]
                assert self.post_bodies == writes, "Case/source/evidence navigation dispatched a mutation"
                self.shot("original-case-returned-with-current-evidence")
                return self.note("case-switch-return", {"main_case_id": self.main_case_id, "control_case_id": control_id,
                    "main_revision": before["view"]["case"]["version"], "control_revision": control["case"]["version"],
                    "main_transition": "TR-SAVE", "control_transition": "TR-APPROVE", "source": source,
                    "both_cases_histories_observations_unchanged": True, "navigation_mutations": 0})
            finally:
                self.inspection_read_only = False

        def run(self):
            primary = super().run()
            assert primary["case_id"] == self.main_case_id and self.inspected_success
            primary_posts = list(self.post_bodies)
            switch = self.case_switch_return()
            assert self.post_bodies[:len(primary_posts)] == primary_posts and len(primary_posts) == 19
            counts = Counter(row["path"].rsplit("/", 1)[-1] for row in self.post_bodies)
            assert dict(counts) == {"cases": 2, "propose": 2, "select": 2, "preview": 5, "edit": 2, "execute": 7, "undo": 1, "redo": 1}
            cases = self.get("cases")
            assert {case["id"] for case in cases} == {self.main_case_id, switch["control_case_id"]} and len(cases) == 2
            assert not self.errors and not self.forbidden and not self.external_attempts
            assert self.http_errors == [{"stage": stage, "status": 409, "path": f"/api/cases/{self.main_case_id}/execute"}
                for stage in ("wrong-role-runtime", "repeated-wrong-role-runtime")]
            return {"primary_journey": primary, "source_first": self.source_entry, "switch_return": switch,
                    "total_posts": len(self.post_bodies), "formal": "unavailable / NO_DECIDING_RECEIPT",
                    "source_conformance": "NOT_RUN", "owner_operations": 0}

    return SourceFirstJourney


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--combined", type=Path, help="Optional exact reviewed combined replay; defaults to the repository module")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    dependency = (args.combined or repo / "tests/hci/combined_rule_recovery.py").resolve()
    out.mkdir(parents=True, exist_ok=False)
    script = Path(__file__).read_bytes()
    (out / "replay-script.py").write_bytes(script)
    result = {"schema": "eija.source-first-whole-journey.v1", "status": "NOT_RUN", "utc": datetime.now(UTC).isoformat(),
        "script_sha256": hashlib.sha256(script).hexdigest(), "dependency_sha256": COMBINED_SHA,
        "scope": "EIJA connected checkout, one continuous model-change case plus one case-isolation control; 1440x900 desktop",
        "browser_started": False, "browser_closed": False, "server_started": False, "server_closed": False,
        "not_run": ["human usability/comprehension study", "arbitrary codebase", "source edits", "fresh verification",
                    "live AI/provider", "owner approval/apply", "whole-product acceptance", "mobile/reflow"]}
    review = runtime = replay = before = address = combined_bytes = None
    try:
        if not __debug__:
            raise ModuleNotFoundError("Assertions require unoptimized Python")
        combined, combined_bytes = load_combined(dependency)
        (out / "combined-dependency.py").write_bytes(combined_bytes)
        runtime, replay, compare_subjects = combined.load_replay(repo)
        assert runtime.ROOT.resolve() == repo
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
                browser = combined.launch_headless(playwright, replay.BrowserError)
                result["browser_started"] = True
                context = None
                try:
                    result["browser_version"] = browser.version
                    context = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    review = journey_type(combined, runtime, replay, repo)(context.new_page(), out, base)
                    result["evidence"] = review.run()
                    result["status"] = "PASS"
                finally:
                    try:
                        if review:
                            review.shot("final")
                    finally:
                        try:
                            if context:
                                context.close()
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
        result["status"], result["error"] = "FAIL", {"message": text, "traceback": trace}
    finally:
        if address:
            with socket.socket() as sock:
                sock.settimeout(.2)
                result["server_closed"] = sock.connect_ex(address) != 0
        if review:
            result.update({"failed_stage": review.stage if result["status"] != "PASS" else None,
                "requests": review.requests, "post_bodies": review.post_bodies, "runtime_responses": review.runtime_responses,
                "javascript_errors": review.errors, "http_errors": review.http_errors, "forbidden": review.forbidden,
                "external": review.external_attempts, "navigation": review.navigation_actions})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
        if before is not None:
            after = runtime.subject()
            write_json(out / "subject-after.json", after)
            result["subject_preservation"] = compare_subjects(before, after)
            result["subject_content_sha256"] = before["content_sha256"]
            if result["subject_preservation"]["status"] != "UNCHANGED":
                result["status"] = "FAIL"
        result["script_preserved"] = Path(__file__).read_bytes() == script
        result["dependency_preserved"] = combined_bytes is not None and dependency.read_bytes() == combined_bytes
        if not result["script_preserved"] or (combined_bytes is not None and not result["dependency_preserved"]):
            result["status"] = "FAIL"
        if (result["browser_started"] and not result["browser_closed"]) or (result["server_started"] and not result["server_closed"]):
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob("*")) if p.is_file()})
    sys.stdout.write(json.dumps({key: result[key] for key in ("status", "browser_closed", "server_closed")}) + "\n")
    sys.stdout.flush()
    return 0 if result["status"] == "PASS" else 2 if result["status"] == "NOT_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
