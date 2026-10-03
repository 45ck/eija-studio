"""External EIJA capture adapter. Never run --record before the parent releases the slot.

The repository is imported read-only. Setup uses the accepted disposable review-pack server.
--rehearse uses headless installed Chrome, screenshots and assertions, without video or overlays.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

sys.dont_write_bytecode = True


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--describe-subject", action="store_true", help="Read identity only; never launch a browser")
    modes.add_argument("--rehearse", action="store_true", help="Headless Chrome; screenshots only; wait for root's browser slot")
    modes.add_argument("--record", action="store_true", help="Explicit video opt-in; only after recording-slot release")
    parser.add_argument("--story", choices=("hero", "pr-clip"), default="hero")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--expected-subject-sha256")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()
    args.repo = args.repo.resolve()
    if not (args.repo / "tests/hci/agent_edit_review.py").is_file():
        parser.error("--repo must contain the accepted agent-edit replay")
    if not args.describe_subject:
        if args.out is None or not re.fullmatch(r"[a-f0-9]{64}", args.expected_subject_sha256 or ""):
            parser.error("--out and exact lowercase --expected-subject-sha256 are required")
        args.out = args.out.resolve()
        if args.out.exists():
            parser.error("--out must be a fresh directory; prior takes are never overwritten")
        if not args.out.is_relative_to(Path("D:/Temp").resolve()) or args.out.is_relative_to(args.repo):
            parser.error("--out must be outside the checkout, under D:/Temp")
    if args.rehearse and args.headed:
        parser.error("--rehearse is headless; it cannot take the foreground")
    return args


TEXT_GEOMETRY = r"""node=>{
  const box=r=>({left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height});
  const rect=node.getBoundingClientRect(),style=getComputedStyle(node),matrix=node.getScreenCTM?.();
  const clip={left:0,top:0,right:innerWidth,bottom:innerHeight};
  let painted=node.checkVisibility();
  for(let el=node;el;el=el.parentElement){const css=getComputedStyle(el),r=el.getBoundingClientRect();
    painted&&=css.display!=='none'&&!['hidden','collapse'].includes(css.visibility)&&Number(css.opacity)>0;
    if(/auto|scroll|hidden|clip/.test(css.overflowX)){clip.left=Math.max(clip.left,r.left);clip.right=Math.min(clip.right,r.right);}
    if(/auto|scroll|hidden|clip/.test(css.overflowY)){clip.top=Math.max(clip.top,r.top);clip.bottom=Math.min(clip.bottom,r.bottom);}}
  return {text:node.textContent,box:box(rect),clip,painted,
    fully_visible:painted&&rect.width>0&&rect.height>0&&rect.left>=clip.left&&rect.right<=clip.right&&rect.top>=clip.top&&rect.bottom<=clip.bottom,
    font_css_px:parseFloat(style.fontSize),screen_scale:matrix?Math.hypot(matrix.a,matrix.b):1};
}"""


def run_capture(args, accepted, replay, Recorder, record_take, encode, pr_cli):
    out = args.out
    out.mkdir(parents=True, exist_ok=False)
    result = {"status": "FAIL", "mode": "record" if args.record else "rehearse", "story": args.story,
              "browser_channel": "chrome", "headless": not args.headed, "recording": args.record,
              "recording_csp_bypass_for_cursor_overlay": bool(args.record),
              "normal_csp_acceptance": "separate agent_edit_review evidence; this capture does not replace it",
              "trim_alignment": "Measured from recorder actor entry, not a video-frame timestamp; review exported first/last frames against retained raw take",
              "provider": "offline", "live": False, "source_review": "SOURCE_REVIEW_REQUIRED",
              "driver_sha256": digest(Path(__file__)), "checks": [], "scenes": [], "readability": [],
              "browser_closed": False, "server_closed": False,
              "not_claimed": ["live inference", "source transformation", "baseline approval", "human demand or usability"]}
    temporary_root = Path(tempfile.gettempdir()).resolve()
    result["temporary_root"] = str(temporary_root)
    if not __debug__ or temporary_root.is_relative_to(args.repo) or not temporary_root.is_relative_to(Path("D:/Temp").resolve()):
        result.update(status="NOT_RUN", reason="Use unoptimized Python and external D:/Temp TMPDIR/TEMP/TMP before process startup")
        write_json(out / "result.json", result)
        return result
    if sys.platform == "win32" and shutil.disk_usage("C:/").free < 10 * 1024 ** 3:
        result.update(status="NOT_RUN", reason="C: is below the existing 10 GiB browser guard")
        write_json(out / "result.json", result)
        return result
    before = accepted.subject_identity()
    write_json(out / "subject-before.json", before)
    if before["content_sha256"] != args.expected_subject_sha256:
        result.update(status="NOT_RUN", reason="Expected subject hash does not match current checkout", actual_subject_sha256=before["content_sha256"])
        write_json(out / "result.json", result)
        return result
    media_sources = {str(path.relative_to(args.repo)): digest(path) for path in [
        args.repo / "demos/lib/recorder.py", args.repo / "demos/prgif/record.py",
        args.repo / "demos/prgif/cli.py", args.repo / "demos/prgif/encode.py", args.repo / "demos/prgif/fit.py"]}
    result["recorder_source_sha256"] = media_sources
    (out / "capture-driver.py").write_bytes(Path(__file__).read_bytes())
    review = browser = address = take = None
    viewport = (1920, 1080) if args.story == "hero" else (1280, 1080)
    result["viewport"] = {"width": viewport[0], "height": viewport[1]}
    clock = {}

    class Actor:
        def __init__(self, scene):
            self.scene, self.page = scene, scene.page

        def click(self, selector):
            self.aim(selector)
            if args.record:
                self.scene._press_feedback()
            self.page.locator(selector).click()

        def paste(self, selector, text):
            self.click(selector)
            self.page.locator(selector).fill(text)

        def aim(self, selector):
            target = self.page.locator(selector)
            target.wait_for(state="visible")
            target.scroll_into_view_if_needed()
            box = target.bounding_box()
            assert box and box["width"] > 0 and box["height"] > 0
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            if args.record:
                self.scene._animate_to(x, y, 220)
            else:
                self.page.mouse.move(x, y)
                self.scene._cursor = (x, y)

        def hold(self, name, milliseconds):
            assert shutil.disk_usage("C:/").free >= 10 * 1024 ** 3, "C: fell below the 10 GiB capture guard"
            review.shot(name)
            result["scenes"].append({"id": name, "elapsed_s": round(time.monotonic() - clock["origin"], 3),
                                     "reading_pause_ms": milliseconds if args.record else 0})
            self.scene.wait(milliseconds)

        def tab(self, name):
            self.click(f'[data-tab="{name}"]')
            review.settled()
            review.assert_view(name)

        def pair(self, selector, view, *, preview):
            pair = self.page.locator(selector)
            self.click(selector + ' [data-compare-action="focus"]')
            self.click(selector + ' [data-compare-action="readable"]')
            replay.expect(pair.locator("[data-compare-scale]")).to_have_text("100%")
            observations = []
            for side, model in (("before", view["current"] if preview else view["case"]["baseline"]),
                                ("after", view["candidate"] if preview else view["case"]["candidate"])):
                board = pair.locator(f'[data-compare-side="{side}"] svg.compare-svg')
                observed = board.evaluate(accepted.OBSERVE_COMPARE)
                accepted.assert_graph(model, observed)
                transition = next(t for t in model["transitions"] if t["id"] == "TR-VERIFY")
                texts = [board.locator('[data-transition="TR-VERIFY"] .compare-edge-label'),
                         *[board.locator(f'[data-state="{state}"] .compare-state-label')
                           for state in {transition["from_state"], transition["to_state"]}]]
                for text in texts:
                    measured = text.evaluate(TEXT_GEOMETRY)
                    assert measured["fully_visible"], {"scene": selector, "side": side, "clipped_label": measured}
                    assert abs(measured["screen_scale"] - 1) < .02, "UML labels are not at native scale"
                    observations.append({"side": side, **measured})
            result["readability"].append({"scene": selector, "scale": "100%", "labels": observations})

        def choose_model(self, value):
            assert value in {"baseline", "working"}
            select = self.page.locator("#model-version")
            assert select.locator("option").all_text_contents()[:2] == ["Working model", "Original baseline"]
            replay.expect(select.locator(f'option[value="{value}"]')).to_be_enabled()
            self.click("#model-version")
            self.scene.wait(250)
            select.press("Home")
            if value == "baseline":
                select.press("ArrowDown")
            select.press("Enter")
            review.settled()
            replay.expect(select).to_have_value(value)
            review.assert_view("model")

        def model(self, *, for_drag=False, source_state="SAVED", recenter=True):
            if recenter:
                self.tab("model")
            else:
                review.assert_view("model")
            replay.expect(self.page.locator("#transition-select")).to_have_value("TR-VERIFY")
            if recenter:
                if self.page.locator("#canvas-view").get_attribute("open") is None:
                    self.click("#canvas-view > summary")
                self.click("#canvas-readable")
                replay.expect(self.page.locator("#canvas-zoom")).to_have_text("100%")
                self.click("#canvas-view > summary")
            if for_drag:
                selectors = ['#model-canvas .edit-handle[data-end="source"] circle',
                             '#model-canvas .model-node[data-state="PREVIEW"] .state-box']
                boxes = [self.page.locator(selector).bounding_box() for selector in selectors]
                canvas = self.page.locator("#model-canvas").bounding_box()
                assert canvas and all(boxes)
                left = min(box["x"] for box in boxes)
                right = max(box["x"] + box["width"] for box in boxes)
                top = min(box["y"] for box in boxes)
                bottom = max(box["y"] + box["height"] for box in boxes)
                assert right-left < canvas["width"]-24 and bottom-top < canvas["height"]-24
                self.aim("#model-canvas")
                self.page.mouse.wheel((left+right)/2-canvas["x"]-canvas["width"]/2,
                                      (top+bottom)/2-canvas["y"]-canvas["height"]/2)
                self.page.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
            model_labels = []
            for selector in (f'#model-canvas [data-state="{source_state}"] .state-label',
                             '#model-canvas [data-eija-id$=".TR-VERIFY"] .edge-label'):
                measured = self.page.locator(selector).evaluate(TEXT_GEOMETRY)
                assert measured["fully_visible"], measured
                assert abs(measured["screen_scale"] - 1) < .02, "Displayed-model labels are not at native scale"
                model_labels.append(measured)
            result["readability"].append({"scene": "model", "model_view": self.page.locator("#model-version").input_value(),
                                          "stage": review.stage, "scale": "100%", "labels": model_labels})
            replay.expect(self.page.locator("#canvas-zoom")).to_have_text("100%")

    class CaptureReview(accepted.AgentEdit):
        def inspect_baseline(self, view):
            from rules_ripple_review import OBSERVE_MODEL

            model = view["case"]["baseline"]
            assert model != view["case"]["candidate"], "Model switch fixture needs different whole models"
            self.assert_view("model")
            replay.expect(self.page.locator("#model-version")).to_have_value("baseline")
            replay.expect(self.page.locator("#model-empty")).to_contain_text("Original baseline")
            replay.expect(self.page.locator("#model-empty")).to_contain_text("read only")
            replay.expect(self.page.locator("#model-empty")).to_be_visible()
            replay.expect(self.page.locator("#transition-select")).to_have_value("TR-VERIFY")
            replay.expect(self.page.locator("#model-canvas .edit-handle")).to_have_count(0)
            for control in ("#edit-source", "#edit-target", "#edit-role"):
                replay.expect(self.page.locator(control)).to_be_disabled()
            self.canvas_matches(model)
            observed = self.page.locator("#model-canvas svg").evaluate(OBSERVE_MODEL)
            self.observations.append({"stage": self.stage, "model_view": "baseline",
                                      "independent_expected_model": model, "canvas": observed})
            write_json(self.out / "observations.json", self.observations)
            assert sorted(node["state"] for node in observed["nodes"]) == sorted(model["states"])
            for node in observed["nodes"]:
                assert node["text"] == node["state"] and node["label"]["displayed"]
                assert node["shape"]["width"] > 0 and node["shape"]["height"] > 0
                assert node["label"]["opacity"] > 0 and node["label"]["fill"] not in {"none", "transparent"}
                assert node["shape"]["displayed"] and node["shape"]["opacity"] > 0
            assert len(observed["edges"]) == len(model["transitions"])
            for rule in model["transitions"]:
                edge = next(item for item in observed["edges"] if item["id"] == f"eija-review-slice.transition.{rule['id']}")
                assert edge["text"] == rule["action"] and edge["label"]["displayed"]
                assert edge["label"]["opacity"] > 0 and edge["label"]["fill"] not in {"none", "transparent"}
                assert edge["source"] == [rule["from_state"]] and edge["target"] == [rule["to_state"]]
                assert edge["path"]["stroke"] not in {"none", "transparent"} and edge["path"]["strokeWidth"] > 0
                assert edge["path"]["displayed"] and edge["path"]["opacity"] > 0
                assert edge["selected"] == str(rule["id"] == "TR-VERIFY").lower()
            replay.expect(self.page.locator('#model-canvas [data-state="SAVED"]')).to_have_count(0)

        def entry(self):
            self.scene.goto(self.base + "#" + replay.TEST_CAPABILITY)
            replay.expect(self.page.locator("#connection")).to_contain_text("offline", timeout=60000)
            self.settled()
            replay.expect(self.page.locator("#model-canvas svg")).to_be_visible()
            replay.expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
            return {"source_review_required": True}

        def assert_proposal(self, before, wrapper, expected, transaction, *, legal=True, request=accepted.REQUEST):
            # Keep the complete acceptance oracle without opening a JSON disclosure in the film.
            case = before["view"]["case"]
            assert wrapper["scope"] == "typed-edit-proposal"
            assert wrapper["provider"] == "offline" and wrapper["model"] == "typed-edit-fixture-v1"
            assert wrapper["live"] is False and wrapper["trust"] == "UNTRUSTED_PROPOSAL" and wrapper["request"] == request
            assert wrapper["pack"] == {"id": self.workbench["pack"]["id"], "digest": self.workbench["pack"]["digest"]}
            preview = wrapper["preview"]
            assert preview["scope"] == "semantic-edit-preview" and preview["applied"] is False and preview["persisted"] is False
            assert preview["case_id"] == case["id"] and preview["version"] == case["version"] and preview["stage"] == case["stage"]
            assert preview["semantic_hash"] == before["view"]["packet"]["subject"]["semantic"]
            assert preview["current"] == case["candidate"] and preview["transaction"] == transaction and preview["legal"] is legal
            assert preview["candidate"] == expected
            assert preview["candidate_semantic_hash"] == (replay.Workflow.model_validate(expected).semantic_hash if legal else None)
            assert self.proposal_responses[-1]["body"] == wrapper and self.proposal_responses[-1]["status"] == 200
            replay.expect(self.page.locator("#agent-edit-status")).to_have_attribute("data-status", "proposed" if legal else "refused")
            replay.expect(self.page.locator("#agent-edit-preview")).to_be_enabled()
            assert json.loads(self.page.locator("#agent-edit-json").text_content()) == wrapper
            replay.expect(self.page.locator("#agent-edit-summary")).to_be_visible()
            if legal:
                replay.expect(self.page.locator("#agent-edit-summary")).to_contain_text("PREVIEW")
                replay.expect(self.page.locator("#agent-edit-summary")).to_contain_text("SAVED")
            self.proposal_records.append({"stage": self.stage, "before": before, "actual_wrapper": wrapper,
                                          "independent_expected_candidate": expected})
            self.immutable(before)
            return preview

    def boundary(expected_edits, expected_undos):
        final = review.edit_preview_snapshot()
        packet = final["view"]["packet"]
        assert "SOURCE_REVIEW_REQUIRED" in packet["blockers"] and packet["human_understanding"] == "UNKNOWN"
        assert final["view"]["case"]["baseline"] == review.initial["view"]["case"]["baseline"]
        assert review.get("workbench")["connection"]["source_hash"] == review.workbench["connection"]["source_hash"]
        assert not review.errors and not review.http_errors and not review.forbidden
        writes = [item for item in review.request_records if item["method"] != "GET"]
        for item in writes:
            assert item["method"] == "POST"
            assert item["path"] == "/api/cases" or re.fullmatch(r"/api/cases/[^/]+/(?:propose|select|edit/propose|edit/preview|edit|undo)", item["path"])
        assert sum(item["path"].endswith("/edit") for item in writes) == expected_edits
        assert sum(item["path"].endswith("/undo") for item in writes) == expected_undos
        result["final_state"] = final

    def act(scene):
        nonlocal review, browser
        clock["origin"] = time.monotonic()
        browser = scene.page.context.browser
        result["browser_version"] = browser.version
        scene.page.set_default_timeout(30000)
        review = CaptureReview(scene.page, out, base)
        review.scene = scene
        review.stage = "disclosed-synthetic-setup"
        review.setup()
        # Source stays read-only throughout. Fetch the independent oracle before the
        # filmed sequence; the actual later UI navigation must return this whole value.
        source_oracle = None
        if args.story == "hero":
            connection = review.workbench["connection"]
            source_oracle = review.get("repository/source?" + urlencode({"reference": accepted.SOURCE, "expected_source_hash": connection["source_hash"]}))
            review.immutable(review.initial)
        actor = Actor(scene)
        if args.story == "hero":
            clock["start"] = time.monotonic() - clock["origin"]
        actor.paste("#agent-edit-request", accepted.REQUEST)
        review.immutable(review.initial)
        if args.story == "pr-clip":
            clock["start"] = time.monotonic() - clock["origin"]
        result["setup"] = {"disclosed": "UI-created saved-path synthetic candidate; whole request filled through the real input",
                            "request_prefilled_before_clip": args.story == "pr-clip",
                            "independent_read_only_source_oracle_before_story": source_oracle is not None,
                            "case_id": review.case_id, "initial": review.initial}
        actor.hold("request-ready", 1000 if args.story == "pr-clip" else 1200)
        review.stage = "real-offline-proposal"
        before = review.edit_preview_snapshot()
        with scene.page.expect_response(lambda response: response.request.method == "POST"
                                        and urlsplit(response.url).path == f"/api/cases/{review.case_id}/edit/propose") as pending:
            actor.click("#agent-edit-propose")
        assert pending.value.status == 200
        assert pending.value.request.post_data_json == {"request": accepted.REQUEST, "expected_version": before["view"]["case"]["version"]}
        wrapper = pending.value.json()
        expected = accepted.expected_source(before["view"]["case"]["candidate"], "SAVED")
        review.assert_proposal(before, wrapper, expected, accepted.TRANSACTION)
        replay.expect(scene.page.locator("#edit-preview")).to_be_hidden()
        actor.hold("offline-proposal-visible", 1200 if args.story == "pr-clip" else 1800)
        review.stage = "kernel-preview-at-native-scale"
        actor.click("#agent-edit-preview")
        payload = review.inspect_edit_preview(before, expected, accepted.TRANSACTION)
        assert payload == wrapper["preview"]
        review.painted_preview(payload)
        review.initial_changed_values(payload, viewport[0])
        actor.pair("#edit-preview-comparison", payload, preview=True)
        actor.hold("readable-proposed-uml", 4000)
        result["checks"].append({"id": "real-proposal-and-complete-preview", "status": "PASS"})
        if args.story == "pr-clip":
            review.immutable(before)
            clock["end"] = time.monotonic() - clock["origin"]
            boundary(0, 0)
            return

        review.stage = "explicit-owner-candidate-apply"
        actor.aim("#edit-preview-apply")
        applied = review.checked_apply(before, payload)
        replay.expect(scene.page.locator("#agent-edit-status")).to_have_attribute("data-status", "applied")
        replay.expect(scene.page.locator("#agent-edit-status")).to_be_focused()
        actor.hold("candidate-saved-baseline-unchanged", 2600)
        actor.click("#agent-edit-changes")
        review.settled()
        selected = review.main_comparison().locator(".compare-selection")
        replay.expect(selected).to_have_attribute("data-id", "TR-VERIFY")
        actor.pair("#review-chapters", applied["view"], preview=False)
        actor.hold("readable-persisted-uml", 4000)
        result["checks"].append({"id": "explicit-apply-and-second-native-scale-uml", "status": "PASS"})

        review.stage = "linked-model-rules-source"
        actor.click('#review-chapters [data-compare-action="inspect-model"]')
        review.settled()
        review.inspect_working(applied["view"])
        actor.model()
        actor.hold("same-transition-in-model", 1800)
        review.stage = "real-baseline-candidate-dropdown-switch"
        before_switch = review.edit_preview_snapshot()
        assert before_switch == applied
        actor.choose_model("baseline")
        baseline_verify = next(rule for rule in applied["view"]["case"]["baseline"]["transitions"] if rule["id"] == "TR-VERIFY")
        actor.model(source_state=baseline_verify["from_state"])
        review.inspect_baseline(applied["view"])
        review.immutable(before_switch)
        actor.hold("original-baseline-selected-read-only", 1800)
        actor.choose_model("working")
        actor.model()
        review.inspect_working(applied["view"])
        review.immutable(before_switch)
        actor.hold("working-candidate-restored-from-dropdown", 1800)
        result["model_switches"] = {"control": "#model-version", "input": "native select click/Home/ArrowDown/Enter",
                                   "sequence": ["working", "baseline", "working"], "read_only_baseline": True,
                                   "whole_models_checked": True, "complete_server_state_unchanged": True}
        review.stage = "linked-model-rules-source"
        actor.tab("change")
        actor.click("#agent-edit-rules")
        review.settled()
        accepted.RulesReview.inventory(review, applied["view"]["case"]["candidate"])
        accepted.RulesReview.candidate_subject(review, applied["view"])
        actor.hold("same-transition-in-rules", 2200)
        actor.click('#rule-table > tr[data-transition-id="TR-VERIFY"] button')
        review.settled()
        review.inspect_working(applied["view"])
        actor.tab("change")
        actor.click("#agent-edit-changes")
        review.settled()
        terms = [term for term in review.workbench["language"]["terms"] if "transition:TR-VERIFY" in term.get("refs", [])]
        assert any(accepted.SOURCE in term["binds"] for term in terms), "Source navigation needs a declared binding"
        with scene.page.expect_response(lambda response: urlsplit(response.url).path == "/api/repository/source") as source_response:
            actor.click(f'#review-chapters [data-compare-reference="{accepted.SOURCE}"]')
        review.settled()
        connection = review.workbench["connection"]
        source = source_oracle
        assert source is not None
        assert source_response.value.status == 200 and source_response.value.json() == source
        assert parse_qs(urlsplit(source_response.value.url).query)["expected_source_hash"] == [connection["source_hash"]]
        assert source["status"] == "connected" and source["read_only"] is True and source["reference"] == accepted.SOURCE
        assert source["source_hash"] == connection["source_hash"] and source["graph_hash"] == connection["graph_hash"]
        assert source["file_hash"] == connection["file_hashes"][source["path"]]
        assert source["pack_digest"] == review.workbench["pack"]["digest"]
        assert hashlib.sha256(source["text"].encode()).hexdigest() == source["snippet_hash"]
        lines = source["text"].replace("\r\n", "\n").split("\n")
        if lines[-1] == "":
            lines.pop()
        assert scene.page.locator("#source-reader .source-line code").all_text_contents() == [line or " " for line in lines]
        assert scene.page.locator("#source-reader .line-number").all_text_contents() == [str(source["lines"]["start"] + n) for n in range(len(lines))]
        replay.expect(scene.page.locator("#source-reference")).to_have_value(accepted.SOURCE)
        review.assert_view("code")
        replay.expect(scene.page.locator("#source-reader")).to_have_attribute("data-source-hash", connection["source_hash"])
        replay.expect(scene.page.locator("#source-file")).to_contain_text(source["path"])
        replay.expect(scene.page.locator("#code .read-only-badge")).to_have_text("READ ONLY")
        source_scene = []
        for target in (scene.page.locator("#source-file"), scene.page.locator("#code .read-only-badge"),
                       scene.page.locator("#source-reader .source-line code").first):
            measured = target.evaluate(TEXT_GEOMETRY)
            assert measured["fully_visible"], {"scene": "declared-source", "label": measured}
            source_scene.append(measured)
        result["readability"].append({"scene": "declared-source", "labels": source_scene})
        review.source_records.append(source)
        actor.hold("declared-source-link-source-unchanged", 1200)
        review.immutable(applied)
        result["checks"].append({"id": "same-identity-model-rules-declared-source", "status": "PASS"})

        review.stage = "native-scale-endpoint-drag"
        actor.model(for_drag=True)
        before_drag = review.edit_preview_snapshot()
        resting_guidance = scene.page.locator("#model-empty").text_content()
        target_model = accepted.expected_source(before_drag["view"]["case"]["candidate"], "PREVIEW")
        transaction = {**accepted.TRANSACTION, "state": "PREVIEW"}
        choices = review.get(f"cases/{review.case_id}/affordances")["affordances"]
        assert any(choice["transaction"] == transaction and choice["legal"] for choice in choices)
        handle_selector = '#model-canvas .edit-handle[data-end="source"] circle'
        actor.aim(handle_selector)
        start = scene.page.locator(handle_selector).bounding_box()
        finish = scene.page.locator('#model-canvas .model-node[data-state="PREVIEW"] .state-box').bounding_box()
        assert start and finish
        start_point = {"x": start["x"]+start["width"]/2, "y": start["y"]+start["height"]/2}
        end_point = {"x": finish["x"]+finish["width"]/2, "y": finish["y"]+finish["height"]/2}
        assert scene.page.evaluate("p=>document.elementFromPoint(p.x,p.y)?.closest('.edit-handle')?.dataset.end", start_point) == "source"
        assert scene.page.evaluate("p=>document.elementFromPoint(p.x,p.y)?.closest('.model-node')?.dataset.state", end_point) == "PREVIEW"
        scene.page.mouse.move(**start_point)
        scene.page.mouse.down()
        guide = scene.page.locator("#model-canvas .drag-guide")
        replay.expect(guide).to_have_count(1)
        replay.expect(scene.page.locator('#model-canvas .edit-handle[data-end="source"]')).to_have_class(re.compile(r"\bdrag-active\b"))
        replay.expect(scene.page.locator('#model-canvas .model-node[data-state="SAVED"]')).to_have_class(re.compile(r"\bdrop-neutral\b"))
        replay.expect(scene.page.locator('#model-canvas .model-node[data-state="PREVIEW"]')).to_have_class(re.compile(r"\bdrop-legal\b"))
        if args.record:
            scene._animate_to(end_point["x"], end_point["y"], 700, steps=24)
        else:
            scene.page.mouse.move(**end_point, steps=24)
        replay.expect(guide).to_be_visible()
        replay.expect(scene.page.locator('#model-canvas .model-node[data-state="PREVIEW"]')).to_have_class(re.compile(r"\bdrop-hover\b"))
        replay.expect(scene.page.locator("#model-empty")).to_have_text("Release to preview Verify source: SAVED → PREVIEW.")
        geometry = guide.evaluate("""n=>{const m=n.getScreenCTM(),s=getComputedStyle(n),a=new DOMPoint(n.x1.baseVal.value,n.y1.baseVal.value).matrixTransform(m),b=new DOMPoint(n.x2.baseVal.value,n.y2.baseVal.value).matrixTransform(m);return{start:{x:a.x,y:a.y},finish:{x:b.x,y:b.y},length:n.getTotalLength(),stroke:s.stroke,width:parseFloat(s.strokeWidth),opacity:Number(s.strokeOpacity)*Number(s.opacity)}}""")
        assert geometry["length"] > 0 and geometry["width"] > 0 and geometry["opacity"] > 0 and geometry["stroke"] not in {"none", "transparent"}
        for key, point in (("start", start_point), ("finish", end_point)):
            assert all(abs(geometry[key][axis]-point[axis]) <= 2 for axis in ("x", "y"))
        review.immutable(before_drag)
        actor.hold("real-endpoint-drag-at-100-percent", 700)
        with scene.page.expect_response(lambda response: response.request.method == "POST" and urlsplit(response.url).path.endswith("/edit/preview")):
            scene.page.mouse.up()
        replay.expect(guide).to_have_count(0)
        replay.expect(scene.page.locator("#model-canvas .drag-active, #model-canvas .drop-hover")).to_have_count(0)
        replay.expect(scene.page.locator("#model-empty")).to_have_text(resting_guidance)
        preview = review.inspect_edit_preview(before_drag, target_model, transaction)
        actor.pair("#edit-preview-comparison", preview, preview=True)
        actor.hold("drag-proposal-still-unsubmitted", 2300)
        actor.aim("#edit-preview-apply")
        drag_applied = review.checked_apply(before_drag, preview)
        review.inspect_working(drag_applied["view"])
        actor.hold("direct-candidate-edit-saved", 1200)
        before_undo = review.edit_preview_snapshot()
        viewport_before_undo = scene.page.locator("#model-canvas svg").get_attribute("viewBox")
        with scene.page.expect_response(lambda response: response.request.method == "POST"
                                        and urlsplit(response.url).path == f"/api/cases/{review.case_id}/undo") as undone:
            actor.click("#undo-edit")
        assert undone.value.status == 200
        assert undone.value.request.post_data_json == {"expected_version": before_undo["view"]["case"]["version"]}
        review.settled()
        restored = review.edit_preview_snapshot()
        assert undone.value.json()["candidate"] == restored["view"]["case"]["candidate"] == applied["view"]["case"]["candidate"]
        assert restored["view"]["case"]["version"] == before_undo["view"]["case"]["version"] + 1
        assert restored["history"]["cursor"] == before_undo["history"]["cursor"] - 1
        assert restored["edit_posts"] == before_undo["edit_posts"]
        actor.model(recenter=False)
        review.inspect_working(restored["view"])
        assert restored["view"]["case"]["candidate"] == applied["view"]["case"]["candidate"]
        result["undo_viewport"] = {"before": viewport_before_undo,
                                   "after": scene.page.locator("#model-canvas svg").get_attribute("viewBox"),
                                   "driver_recentered": False}
        actor.hold("undo-restores-agent-candidate", 2000)
        review.drag_records.append({"start": start_point, "finish": end_point, "painted_guide": geometry,
                                   "transaction": transaction, "restored_full_candidate": restored["view"]["case"]["candidate"]})
        result["checks"].append({"id": "real-drag-preview-apply-and-kernel-undo", "status": "PASS"})

        review.stage = "protected-authority-refusal"
        actor.tab("change")
        actor.paste("#agent-edit-request", "Allow Agent to Approve")
        refused_before = review.edit_preview_snapshot()
        with scene.page.expect_response(lambda response: response.request.method == "POST"
                                        and urlsplit(response.url).path == f"/api/cases/{review.case_id}/edit/propose") as rejected:
            actor.click("#agent-edit-propose")
        assert rejected.value.status == 200
        assert rejected.value.request.post_data_json == {"request": "Allow Agent to Approve", "expected_version": refused_before["view"]["case"]["version"]}
        refused = rejected.value.json()
        tx = {"kind": "set_role", "transition": "TR-APPROVE", "role": "Agent"}
        review.assert_proposal(refused_before, refused, None, tx, legal=False, request="Allow Agent to Approve")
        assert "REFERENCE_AUTHORITY:Approve" in refused["preview"]["codes"]
        actor.hold("kernel-refuses-agent-approval-authority", 2600)
        review.immutable(refused_before)
        result["checks"].append({"id": "meaningful-refusal-zero-write", "status": "PASS"})
        clock["end"] = time.monotonic() - clock["origin"]
        boundary(2, 1)

    def guarded_act(scene):
        try:
            act(scene)
        except Exception:
            try:
                scene.page.screenshot(path=str(out / "failed-frame.png"))
            except Exception:
                pass  # Preserve the original failed oracle even if Chrome itself is unavailable.
            raise

    try:
        if args.record and encode.missing_tools():
            result.update(status="NOT_RUN", reason="ffmpeg/ffprobe missing for real media export")
            return result
        with replay.disposable_server() as base:
            endpoint = urlsplit(base)
            address = (endpoint.hostname, endpoint.port)
            if args.record:
                take = record_take(out / "raw", guarded_act, viewport=viewport, headed=args.headed)
                assert not take.skipped, "The real recorder skipped part of the story"
            else:
                with Recorder(headless=True, viewport=viewport).session(out / "unused-video", dry_run=True) as scene:
                    guarded_act(scene)
        result["status"] = "PASS"
    except Exception as error:
        result["error"] = {"type": type(error).__name__, "message": str(error).replace(replay.TEST_CAPABILITY, "[fixture-capability]"),
                           "traceback": traceback.format_exc().replace(replay.TEST_CAPABILITY, "[fixture-capability]")}
        if "could not launch the system Chrome" in str(error):
            result["status"] = "NOT_RUN"
    finally:
        result["browser_closed"] = browser is not None and not browser.is_connected()
        if address:
            with socket.socket() as probe:
                probe.settimeout(.2)
                result["server_closed"] = probe.connect_ex(address) != 0
        if review:
            result["failed_stage"] = review.stage if result["status"] != "PASS" else None
            result["requests"] = review.request_records
            result["javascript_errors"] = review.errors
            result["http_errors"] = review.http_errors
            result["forbidden_attempts"] = review.forbidden
            for name, value in (("actual-proposals", review.proposal_responses), ("proposal-oracles", review.proposal_records),
                                ("get-oracles", review.oracles), ("painted-models", review.graphs),
                                ("actual-edits", review.acknowledgements), ("source-reads", review.source_records),
                                ("pointer-gesture", review.drag_records)):
                write_json(out / (name + ".json"), value)
        after = accepted.subject_identity()
        write_json(out / "subject-after.json", after)
        result["subject_preservation"] = accepted.compare_subjects(before, after)
        result["recorder_preserved"] = all(digest(args.repo / name) == value for name, value in media_sources.items())
        result["capture_timeline"] = clock
        if result["subject_preservation"]["status"] != "UNCHANGED" or not result["recorder_preserved"]:
            result["status"] = "FAIL"
        if result["status"] == "PASS" and not (result["browser_closed"] and result["server_closed"]):
            result["status"] = "FAIL"
        write_json(out / "result.json", result)

    if args.record and take is not None:
        result["raw_video"] = {"path": str(take.video), "sha256": digest(take.video), "bytes": take.video.stat().st_size}
        if result["status"] == "PASS":
            try:
                start, duration = clock["start"], clock["end"]-clock["start"]
                if args.story == "pr-clip":
                    info = encode.probe(take.video)
                    assert info.duration_s-start <= 20, "Complete PR take exceeds20s; retain raw and shorten story, never speed/cut"
                    conversion = argparse.Namespace(mode="convert", video=take.video, trim_start=start, out=out / "agent-proposal.gif",
                                                    max_width=1280, max_seconds=20.0, max_speedup=1.0)
                    transcript = io.StringIO()
                    with contextlib.redirect_stdout(transcript):
                        code = pr_cli.run(conversion)
                    text = transcript.getvalue()
                    (out / "pr-gif-cli.log").write_text(text, encoding="utf-8", newline="\n")
                    assert code == 0, "The real demos pr-gif CLI converter failed"
                    report, _ = json.JSONDecoder().raw_decode(text[text.index("{"):])
                    assert report["speed"] == 1 and report["tail_cut"] is False and report["seconds"] <= 20
                    assert report["width"] == 1280, "GIF downscaled below native readable width; retain failed take for review"
                    assert conversion.out.stat().st_size == report["bytes"] < 5_000_000
                    result["media"] = {**report, "sha256": digest(conversion.out), "path": str(conversion.out)}
                else:
                    assert duration <= 120, "Hero exceeds the bounded two-minute scene; retain raw and shorten actual interactions"
                    media = out / "agent-edit-hero.mp4"
                    command = [encode.tool("ffmpeg"), "-v", "error", "-y", "-i", str(take.video), "-ss", f"{start:.3f}",
                               "-t", f"{duration:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(media)]
                    encoded = subprocess.run(command, capture_output=True, text=True, timeout=240, check=False)
                    (out / "hero-encode.log").write_text(encoded.stderr, encoding="utf-8", newline="\n")
                    assert encoded.returncode == 0 and media.is_file(), "Actual raw-video trim/encode failed"
                    info = encode.probe(media)
                    assert (info.width, info.height) == viewport and abs(info.duration_s-duration) < .5
                    result["media"] = {"path": str(media), "sha256": digest(media), "bytes": media.stat().st_size,
                                       "seconds": info.duration_s, "width": info.width, "height": info.height, "speed": 1}
            except Exception as error:
                result["status"] = "FAIL"
                result["media_error"] = {"type": type(error).__name__, "message": str(error)}
    write_json(out / "result.json", result)
    if args.rehearse and any(path.suffix.lower() in {".webm", ".mp4", ".gif"} for path in out.rglob("*") if path.is_file()):
        result.update(status="FAIL", reason="Screenshot-only rehearsal unexpectedly produced media")
        write_json(out / "result.json", result)
    write_json(out / "artifact-manifest.json", {path.relative_to(out).as_posix(): {"sha256": digest(path), "bytes": path.stat().st_size}
                                                for path in sorted(out.rglob("*")) if path.is_file()})
    return result


def main():
    args = parse_args()
    for directory in (args.repo / "src", args.repo, args.repo / "tests/hci"):
        sys.path.insert(0, str(directory))
    try:
        import agent_edit_review as accepted
        import self_dogfood_replay as replay
        from demos.lib import Recorder
        from demos.prgif import cli as pr_cli, encode
        from demos.prgif.record import record as record_take
    except ImportError as error:
        sys.stdout.write(json.dumps({"status": "NOT_RUN", "reason": str(error)}) + "\n")
        return 3
    if args.describe_subject:
        subject = accepted.subject_identity()
        sys.stdout.write(json.dumps({"subject_sha256": subject["content_sha256"], "driver_sha256": digest(Path(__file__))}) + "\n")
        return 0
    result = run_capture(args, accepted, replay, Recorder, record_take, encode, pr_cli)
    sys.stdout.write(json.dumps({"status": result["status"], "mode": result["mode"], "story": result["story"],
                                "checks": result["checks"], "media": result.get("media"), "result": str(args.out / "result.json")}) + "\n")
    return 0 if result["status"] == "PASS" else 3 if result["status"] == "NOT_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
