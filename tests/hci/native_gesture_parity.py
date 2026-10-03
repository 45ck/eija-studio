"""Native pointer/form parity on an isolated offline EIJA reference-model IDE.

Reuses existing replay adapters and records exact source and HTTP observations.
Run browser/heavy checks serially. No verification, approval or apply.
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
TRANSITION = "TR-SAVE"
ALLOWED = {"kind": "retarget_transition", "transition": TRANSITION, "end": "source", "state": "VERIFIED"}
REFUSED = {"kind": "retarget_transition", "transition": TRANSITION, "end": "source", "state": "DRAFT"}
REFUSAL_CODES = ["REFERENCE_SEQUENCE:VERIFIED"]
REFUSAL_REFS = ["law:verified-requires-preview", "state:VERIFIED"]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def expected_candidate(model, transaction):
    """Independent full-model expectation: replace only the named literal field."""
    result = deepcopy(model)
    rows = [row for row in result["transitions"] if row["id"] == transaction["transition"]]
    assert len(rows) == 1
    field, value = ("role", transaction["role"]) if transaction["kind"] == "set_role" else (
        "from_state" if transaction["end"] == "source" else "to_state", transaction["state"])
    rows[0][field] = value
    return result


def load_adapters(repo):
    sys.path[:0] = [str(repo / "tests/hci"), str(repo / "src"), str(repo)]
    replay = importlib.import_module("self_dogfood_replay")
    prospective = importlib.import_module("prospective_edit_review")
    Journey = importlib.import_module("ide_journey_edges").Journey
    compare_subjects = importlib.import_module("self_dogfood_subject").compare_subjects
    assert prospective.ROOT.resolve() == repo
    return replay, prospective, Journey, compare_subjects


def journey_type(replay, Journey):
    class GestureParity(Journey):
        def __init__(self, page, out, base):
            super().__init__(page, out, base)
            self.post_bodies, self.gestures, self.external, self.checkpoints = [], [], [], []
            self.secondary = None
            page.route("**/*", self.local_only)

        def local_only(self, route):
            if urlsplit(route.request.url).netloc != urlsplit(self.base).netloc:
                self.external.append({"method": route.request.method, "origin": urlsplit(route.request.url).netloc})
                route.abort()
            else:
                route.fallback()

        def route(self, route):
            request, path = route.request, urlsplit(route.request.url).path
            if request.method != "GET":
                self.post_bodies.append({"stage": self.stage, "path": path, "body": request.post_data_json})
                allowed = request.method == "POST" and (path == "/api/cases" or re.fullmatch(
                    r"/api/cases/[^/]+/(propose|select|edit/preview|edit)", path))
                if not allowed:
                    self.requests.append({"stage": self.stage, "method": request.method, "path": path})
                    self.forbidden.append(path)
                    route.abort()
                    return
            super().route(route)

        def native_activate(self, selector):
            self.keyboard_to(selector)
            target = self.page.locator(selector)
            replay.expect(target).to_be_focused()
            replay.expect(target).to_be_visible()
            replay.expect(target).to_be_in_viewport()
            self.page.keyboard.press("Enter")
            self.navigation_action("native-keyboard-activate", selector, "Enter")
            self.settled()

        def select_save(self):
            self.palette("Select a transition")
            replay.expect(self.page.locator("#transition-select")).to_be_focused()
            self.keyboard_select("#transition-select", TRANSITION)
            self.navigation_action("native-keyboard-select", "#transition-select", TRANSITION)
            replay.expect(self.page.locator("#transition-details")).to_have_attribute(
                "data-eija-id", "eija-review-slice.transition-detail." + TRANSITION)

        def checkpoint(self, name):
            value = self.edit_preview_snapshot()
            case, packet = value["view"]["case"], value["view"]["packet"]
            assert case["stage"] == "PREVIEW" and case["decision"] is None and case["receipts"] == []
            assert packet["human_understanding"] == "UNKNOWN" and not packet["eligible"]
            assert "SOURCE_REVIEW_REQUIRED" in packet["blockers"]
            assert value["view"]["observations"]["instances"] == []
            assert value["view"]["observations"]["outbox"] == []
            self.checkpoints.append({"name": name, "snapshot": value})
            write_json(self.out / "checkpoints.json", self.checkpoints)
            return value

        def choice(self, transaction, legal):
            choices = self.get(f"cases/{self.case_id}/affordances")["affordances"]
            matches = [item for item in choices if item["transaction"] == transaction]
            assert len(matches) == 1 and matches[0]["legal"] is legal
            return matches[0]

        def native_drag(self, transaction, legal):
            assert transaction["kind"] == "retarget_transition" and transaction["transition"] == TRANSITION
            replay.expect(self.page.locator("#transition-select")).to_have_value(TRANSITION)
            self.native_activate("#canvas-fit")  # Explicit UI Overview makes both rendered hit regions reachable.
            handle_selector = f'#model-canvas .edit-handle[data-end="{transaction["end"]}"] circle'
            state_selector = f'#model-canvas .model-node[data-state="{transaction["state"]}"] .state-box'
            handle, target = self.page.locator(handle_selector), self.page.locator(state_selector)
            for locator in (handle, target):
                replay.expect(locator).to_have_count(1)
                replay.expect(locator).to_be_visible()
                replay.expect(locator).to_be_in_viewport()
            start_box, target_box = handle.bounding_box(), target.bounding_box()
            assert start_box and target_box
            start = {"x": start_box["x"] + start_box["width"] / 2, "y": start_box["y"] + start_box["height"] / 2}
            end = {"x": target_box["x"] + target_box["width"] / 2, "y": target_box["y"] + target_box["height"] / 2}
            hit = """point=>{const node=document.elementFromPoint(point.x,point.y);return {
              handle:node?.closest('.edit-handle')?.dataset.end||null,
              state:node?.closest('.model-node')?.dataset.state||null,
              inViewport:point.x>0&&point.x<innerWidth&&point.y>0&&point.y<innerHeight};}"""
            start_hit, end_hit = self.page.evaluate(hit, start), self.page.evaluate(hit, end)
            assert start_hit["inViewport"] and start_hit["handle"] == transaction["end"]
            assert end_hit["inViewport"] and end_hit["state"] == transaction["state"]
            observation = {"stage": self.stage, "transaction": transaction, "start_box": start_box, "target_box": target_box,
                           "start": start, "end": end, "start_hit": start_hit, "end_hit": end_hit,
                           "input": "Playwright mouse.move / mouse.down / mouse.move(steps=12) / mouse.up"}
            self.gestures.append(observation)
            self.page.mouse.move(**start)
            self.page.mouse.down()
            try:
                node = self.page.locator(f'#model-canvas .model-node[data-state="{transaction["state"]}"]')
                replay.expect(node).to_have_class(re.compile(r"\bdrop-" + ("legal" if legal else "refused") + r"\b"))
                replay.expect(self.page.locator("#model-canvas .drag-guide")).to_have_count(1)
                self.page.mouse.move(end["x"], end["y"], steps=12)
                observation["release_hit"] = self.page.evaluate(hit, end)
                assert observation["release_hit"]["state"] == transaction["state"]
                self.shot(self.stage + "-native-drag")
            finally:
                self.page.mouse.up()
            self.navigation_action("native-pointer-drag", handle_selector, transaction["state"])
            replay.expect(self.page.locator("#model-canvas .drag-guide")).to_have_count(0)
            replay.expect(self.page.locator("#model-canvas .drop-legal,#model-canvas .drop-refused")).to_have_count(0)
            write_json(self.out / "native-gestures.json", self.gestures)

        def open_endpoint_preview(self, mode, before, transaction=ALLOWED, legal=True):
            choice = self.choice(transaction, legal)
            count = len(self.post_bodies)
            if mode == "pointer":
                self.native_drag(transaction, legal)
            else:
                assert mode == "keyboard" and transaction["end"] == "source"
                self.keyboard_select("#model-source", transaction["state"])
                self.navigation_action("native-keyboard-select", "#model-source", transaction["state"])
                self.native_activate("#edit-source")
            payload = self.inspect_edit_preview(before,
                expected_candidate(before["view"]["case"]["candidate"], transaction) if legal else None,
                transaction, legal=legal)
            assert self.post_bodies[count:] == [{"stage": self.stage, "path": f"/api/cases/{self.case_id}/edit/preview",
                                                "body": {"transaction": transaction}}]
            if not legal:
                assert choice["codes"] == payload["codes"] == REFUSAL_CODES
                assert choice["refs"] == payload["refs"] == REFUSAL_REFS
            self.shot(self.stage + "-preview")
            return payload

        def assert_commit(self, before, after, transaction, model):
            old, new = before["view"], after["view"]
            assert new["case"]["candidate"] == model
            assert new["case"]["baseline"] == old["case"]["baseline"]
            assert new["case"]["baseline_version"] == old["case"]["baseline_version"]
            assert new["case"]["version"] == old["case"]["version"] + 1
            assert new["case"]["transactions"] == old["case"]["transactions"] + [transaction]
            assert after["history"]["cursor"] == before["history"]["cursor"] + 1
            assert len(after["history"]["edits"]) == len(before["history"]["edits"]) + 1
            assert after["history"]["edits"][:-1] == before["history"]["edits"]
            assert after["history"]["edits"][-1]["transaction"] == transaction
            assert new["observations"]["instances"] == old["observations"]["instances"]
            assert new["observations"]["outbox"] == old["observations"]["outbox"]
            assert new["observations"]["events"][:-1] == old["observations"]["events"]
            event = new["observations"]["events"][-1]
            assert event["kind"] == "SemanticEdited"
            body = event["body"]
            assert {key: value for key, value in body.items() if key not in {"by", "time"}} == {
                "case_id": self.case_id, "from_version": old["case"]["version"], "to_version": new["case"]["version"],
                "transaction": transaction, "before_semantic_hash": old["packet"]["subject"]["semantic"],
                "after_semantic_hash": new["packet"]["subject"]["semantic"], "discarded_redo": []}
            assert isinstance(body["by"], str) and body["by"] and datetime.fromisoformat(body["time"]).tzinfo is not None
            self.canvas_matches(model)

        def equivalent_case(self, mode):
            self.stage = mode + "-setup"
            self.label = "QA endpoint parity " + mode
            self.create_candidate()
            self.select_save()
            before = self.checkpoint(mode + "-before")
            assert before["view"]["case"]["version"] == 2
            save = next(row for row in before["view"]["case"]["candidate"]["transitions"] if row["id"] == TRANSITION)
            assert (save["from_state"], save["to_state"], save["role"]) == ("PREVIEW", "SAVED", "Owner")
            self.stage = mode + "-cancel"
            first = self.open_endpoint_preview(mode, before)
            self.close_edit_preview(before, escape=True)
            assert self.checkpoint(mode + "-after-cancel") == before
            self.stage = mode + "-commit"
            final_preview = self.open_endpoint_preview(mode, before)
            assert first == final_preview, "Reopening the same unsubmitted edit changed its preview"
            after = self.apply_edit_preview(before, final_preview, keyboard=True)
            self.assert_commit(before, after, ALLOWED, expected_candidate(before["view"]["case"]["candidate"], ALLOWED))
            self.checkpoint(mode + "-after-commit")
            self.shot(mode + "-committed-model")
            return {"case_id": self.case_id, "before": before, "preview": final_preview, "after": after}

        def refused_gesture(self):
            self.stage = "refused-endpoint-gesture"
            self.select_save()
            before = self.checkpoint("before-refused-gesture")
            payload = self.open_endpoint_preview("pointer", before, REFUSED, False)
            self.close_edit_preview(before, keyboard=True)
            assert self.checkpoint("after-refused-gesture") == before
            return {"transaction": REFUSED, "codes": payload["codes"], "refs": payload["refs"], "model_unchanged": True}

        def stale_gesture(self, case_id):
            self.stage = "stale-gesture-setup"
            self.switch_case(case_id)
            self.select_save()
            stale = self.checkpoint("stale-page-before-concurrent-edit")
            transaction = dict(ALLOWED, state="PREVIEW")
            self.choice(transaction, True)
            second_out = self.out / "second-page"
            second_out.mkdir()
            second = GestureParity(self.page.context.new_page(), second_out, self.base)
            self.secondary = second
            def assert_stale_surface():
                assert self.revision() == stale["view"]["case"]["version"]
                assert self.semantic() == stale["view"]["packet"]["subject"]["semantic"]
                self.canvas_matches(stale["view"]["case"]["candidate"])
                replay.expect(self.page.locator("#transition-select")).to_have_value(TRANSITION)
                replay.expect(self.page.locator("#model-source")).to_have_value("VERIFIED")
            try:
                second.stage = "concurrent-role-edit"
                second.entry()
                second.switch_case(case_id)
                second.select_save()
                before = second.checkpoint("before-concurrent-role-edit")
                role = {"kind": "set_role", "transition": TRANSITION, "role": "Agent"}
                second.choice(role, True)
                model = expected_candidate(before["view"]["case"]["candidate"], role)
                second.keyboard_select("#transition-role", "Agent")
                second.native_activate("#edit-role")
                payload = second.inspect_edit_preview(before, model, role)
                winner = second.apply_edit_preview(before, payload, keyboard=True)
                second.assert_commit(before, winner, role, model)
                assert second.post_bodies == [
                    {"stage": "concurrent-role-edit", "path": f"/api/cases/{case_id}/edit/preview", "body": {"transaction": role}},
                    {"stage": "concurrent-role-edit", "path": f"/api/cases/{case_id}/edit",
                     "body": {"expected_version": before["view"]["case"]["version"], "transaction": role}}]
                assert_stale_surface()
                authoritative = self.checkpoint("winner-before-stale-gesture")
                assert authoritative["view"] == winner["view"] and authoritative["history"] == winner["history"]
                self.stage = "stale-native-gesture"
                count = len(self.post_bodies)
                self.native_drag(transaction, True)
                replay.expect(self.page.locator("#edit-preview-status")).to_have_attribute("data-status", "stale")
                replay.expect(self.page.locator("#edit-preview-apply")).to_be_disabled()
                raw = json.loads(self.page.locator("#edit-preview-json").text_content())
                assert self.edit_preview_responses[-1]["body"] == raw
                assert raw["case_id"] == case_id and raw["version"] == winner["view"]["case"]["version"]
                assert raw["current"] == winner["view"]["case"]["candidate"] and raw["transaction"] == transaction
                assert raw["candidate"] == expected_candidate(raw["current"], transaction) and raw["legal"] is True
                replay.expect(self.page.locator("#edit-preview")).to_have_attribute("data-revision", str(stale["view"]["case"]["version"]))
                assert json.loads(self.page.locator("#edit-preview-diagnostic").text_content())["code"] == "EDIT_PREVIEW_STALE"
                assert self.post_bodies[count:] == [{"stage": self.stage, "path": f"/api/cases/{case_id}/edit/preview", "body": {"transaction": transaction}}]
                assert self.checkpoint("after-stale-gesture") == authoritative
                assert_stale_surface()
                self.shot("stale-gesture-retained-model")
                self.close_edit_preview(authoritative, escape=True)
                assert_stale_surface()
                self.palette("Refresh current model")
                self.canvas_matches(winner["view"]["case"]["candidate"])
                assert self.revision() == winner["view"]["case"]["version"]
                assert self.semantic() == winner["view"]["packet"]["subject"]["semantic"]
                assert self.checkpoint("after-stale-refresh") == authoritative
                assert not second.errors and not second.http_errors and not second.forbidden and not second.external
                return {"stale_revision": stale["view"]["case"]["version"], "winner_revision": winner["view"]["case"]["version"],
                        "status": "EDIT_PREVIEW_STALE", "gesture_edit_posts": 0, "refresh_matches_winner": True}
            finally:
                write_json(second_out / "observations.json", {"requests": second.requests, "post_bodies": second.post_bodies,
                    "oracles": second.oracles, "errors": second.errors, "http_errors": second.http_errors,
                    "forbidden": second.forbidden, "external": second.external})
                second.page.close()

        def run(self):
            self.entry()
            pointer = self.equivalent_case("pointer")
            keyboard = self.equivalent_case("keyboard")
            assert pointer["case_id"] != keyboard["case_id"]
            for field in ("baseline", "candidate", "transactions"):
                assert pointer["before"]["view"]["case"][field] == keyboard["before"]["view"]["case"][field]
                assert pointer["after"]["view"]["case"][field] == keyboard["after"]["view"]["case"][field]
            for field in ("current", "candidate", "transaction", "semantic_hash", "candidate_semantic_hash"):
                assert pointer["preview"][field] == keyboard["preview"][field], field
            refusal = self.refused_gesture()
            stale = self.stale_gesture(pointer["case_id"])
            assert not self.errors and not self.http_errors and not self.forbidden and not self.external
            counts = Counter(row["path"].rsplit("/", 1)[-1] for row in self.post_bodies)
            assert counts == {"cases": 2, "propose": 2, "select": 2, "preview": 6, "edit": 2}
            write_json(self.out / "parity.json", {"pointer": pointer, "keyboard": keyboard, "refused": refusal, "stale": stale})
            return {"pointer_and_keyboard_candidates_identical": True, "typed_transaction": ALLOWED,
                    "cases": [pointer["case_id"], keyboard["case_id"]], "cancelled_previews": 2,
                    "committed_parity_edits": 2, "refused_gesture": refusal, "stale_gesture": stale,
                    "primary_request_counts": dict(counts), "concurrent_real_role_edits": 1}

    return GestureParity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    script = Path(__file__).read_bytes()
    (out / "replay-script.py").write_bytes(script)
    result = {"schema": "eija.native-gesture-parity.v1", "status": "NOT_RUN", "utc": datetime.now(UTC).isoformat(),
              "script_sha256": hashlib.sha256(script).hexdigest(), "scope": "EIJA synthetic reference model; 1440x900 desktop",
              "browser_started": False, "browser_closed": False, "server_started": False, "server_closed": False,
              "not_run": ["human usability study", "arbitrary codebase", "touch/mobile gesture", "source edits", "live AI", "owner approval/apply"]}
    replay = prospective = review = before = address = None
    try:
        if not __debug__:
            raise ModuleNotFoundError("Unoptimized Python assertions are required")
        replay, prospective, Journey, compare_subjects = load_adapters(repo)
        if replay.PREREQUISITE_ERROR:
            raise ModuleNotFoundError(replay.PREREQUISITE_ERROR)
        before = prospective.subject()
        write_json(out / "subject-before.json", before)
        with replay.sync_playwright() as playwright:
            result["status"] = "FAIL"
            with replay.disposable_server() as base:
                endpoint = urlsplit(base)
                address = (endpoint.hostname, endpoint.port)
                result["server_started"] = True
                try:
                    browser = playwright.chromium.launch(headless=True)
                except replay.BrowserError as error:
                    if "Executable doesn't exist at " in str(error):
                        raise ModuleNotFoundError("Configured Playwright headless executable is absent: " + str(error)) from error
                    raise
                result["browser_started"] = True
                context = None
                try:
                    result["browser_version"] = browser.version
                    context = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                    page = context.new_page()
                    review = journey_type(replay, Journey)(page, out, base)
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
                           "requests": review.requests, "post_bodies": review.post_bodies,
                           "javascript_errors": review.errors, "http_errors": review.http_errors,
                           "forbidden": review.forbidden, "external": review.external, "navigation": review.navigation_actions})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
        if before is not None:
            after = prospective.subject()
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
    sys.stdout.write(json.dumps({key: result[key] for key in ("status", "browser_closed", "server_closed")}) + "\n")
    sys.stdout.flush()
    return 0 if result["status"] == "PASS" else 2 if result["status"] == "NOT_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
