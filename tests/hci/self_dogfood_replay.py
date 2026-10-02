"""Real browser checks against the explicitly authorised disposable EIJA server.

No target-source execution, personal browser profiles, CSP bypass or owner approval.
The optional recording is a scripted UI demonstration, never human-value evidence.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import re
import socket
import sys
import tempfile
import threading
import time
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import uvicorn
from self_dogfood_subject import capture_subject, compare_subjects

from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import Workflow
from eija_studio.interfaces.http import create_app

try:
    from axe_playwright_python.base import AXE_FILE_PATH
    from axe_playwright_python.sync_playwright import Axe
    from playwright.sync_api import Error as BrowserError
    from playwright.sync_api import expect, sync_playwright
except ImportError as error:
    PREREQUISITE_ERROR = str(error)
else:
    PREREQUISITE_ERROR = None

EXPECTED = (
    "ide-entry", "offline-intent", "source-navigation", "canvas-controls",
    "checked-edit", "semantic-diff", "refused-edit", "undo-redo", "reload", "view-modes", "workspace-panels", "keyboard",
    "evidence-truth", "viewport", "accessibility", "readability", "reflow-320", "axe-observations",
    "runtime-errors", "owner-boundary",
)
TEST_CAPABILITY = uuid4().hex


def require_only_save_role_change(before, after):
    expected = deepcopy(before)
    save = next(t for t in expected["transitions"] if t["id"] == "TR-SAVE")
    assert save["role"] == "Owner"
    save["role"] = "Agent"
    assert after == expected, "Accepted edit changed more than the selected Save role."


@contextlib.contextmanager
def disposable_server(repository_root=None):
    """Create this script's own offline workspace and loopback server; never attach to a live owner session."""
    repo = Path(__file__).resolve().parents[2]
    pack = repo / "packs/eija-review-slice"
    if not (pack / "pack.json").is_file():
        raise RuntimeError("Run this script from an EIJA checkout containing packs/eija-review-slice.")
    scratch_root = repo / ".tmp"
    scratch_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="self-dogfood-browser-", dir=scratch_root) as directory:
        workspace = Path(directory).resolve()
        if not workspace.is_relative_to(scratch_root.resolve()):
            raise RuntimeError("Disposable workspace escaped the checkout scratch directory.")
        studio = build_studio(workspace, pack=pack, repository_root=repo if repository_root is None else repository_root)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            app = create_app(studio, TEST_CAPABILITY, port=port)
            server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
            thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
            thread.start()
            deadline = time.monotonic() + 20
            try:
                while not server.started:
                    if not thread.is_alive() or time.monotonic() > deadline:
                        raise RuntimeError("Disposable server did not become ready.")
                    time.sleep(.05)
                yield f"http://127.0.0.1:{port}/"
            finally:
                server.should_exit = True
                thread.join(timeout=15)
                if thread.is_alive():
                    raise RuntimeError("Disposable server did not stop cleanly.")


class Review:
    def __init__(self, page, out, base, record=False):
        self.page, self.out, self.base = page, out, base
        self.record = record
        self.checks, self.requests, self.errors, self.http_errors, self.forbidden = [], [], [], [], []
        self.stage = "entry"
        self.label = "QA " + uuid4().hex[:8]
        self.case_id = None
        self.server_view = None
        page.on("pageerror", lambda error: self.errors.append(str(error)))
        page.on("response", self.response)
        page.route("**/api/**", self.route)

    def route(self, route):
        request = route.request
        path = urlsplit(request.url).path
        self.requests.append({"stage": self.stage, "method": request.method, "path": path})
        if request.method != "GET" and path.rsplit("/", 1)[-1] in {"approve", "apply"}:
            self.forbidden.append(path)
            route.abort()
        else:
            route.continue_()

    def response(self, response):
        path = urlsplit(response.url).path
        if response.status == 200 and response.request.method == "GET" and re.fullmatch(r"/api/cases/[^/]+", path):
            self.server_view = response.json()
        if response.status >= 400:
            self.http_errors.append({"stage": self.stage, "status": response.status, "path": path})

    def settled(self):
        expect(self.page.locator("body")).not_to_have_attribute("aria-busy", "true", timeout=60000)

    def step(self, name, action):
        self.stage = name
        evidence = action()
        self.checks.append({"id": name, "status": "PASS", "evidence": evidence})
        self.page.screenshot(path=str(self.out / (name + ".png")))
        self.recording_pause()

    def recording_pause(self):
        if self.record:
            time.sleep(1)  # Video pacing only; all synchronization uses locator assertions.

    def tab(self, name):
        target = self.page.locator(f'[data-tab="{name}"]')
        if name in {"impact", "visual", "source"} and not target.is_visible():
            self.page.locator("#reference-views > summary").click()
        target.click()
        self.settled()

    def packet(self):
        return json.loads(self.page.locator("#packet").text_content())

    def semantic(self):
        return self.packet()["subject"]["semantic"]

    def revision(self):
        text = self.page.locator("#case-id").inner_text()
        return int(re.search(r"REVISION (\d+)", text)[1])

    def entry(self):
        response = self.page.goto(self.base + "#" + TEST_CAPABILITY)
        expect(self.page.locator("#connection")).to_contain_text("offline", timeout=60000)
        self.settled()
        expect(self.page.locator("#model-canvas svg")).to_be_visible()
        expect(self.page.locator("#create-panel")).to_be_hidden()
        expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        return {"model_visible_without_case": True, "request_form_closed": True,
                "content_security_policy": response.headers.get("content-security-policy"), "csp_modified": False}

    def intent(self):
        self.page.locator("#new-case").click()
        expect(self.page.locator("#request")).to_be_visible()
        self.page.locator("#request").fill(
            self.label + ": Show the optional saved candidate path in EIJA's review journey."
        )
        with self.page.expect_response(lambda response: response.request.method == "POST"
                                       and urlsplit(response.url).path == "/api/cases") as pending:
            self.page.locator("#create").click()
        created = pending.value.json()
        self.case_id = created["id"]
        self.settled()
        expect(self.page.locator("#case-stage")).to_have_text("DRAFT")
        self.tab("change")
        self.page.locator("#propose").click()
        expect(self.page.locator("#case-stage")).to_have_text("PROPOSED", timeout=30000)
        expect(self.page.locator('[data-eija-id="eija-review-slice.state.SAVED"]')).to_have_count(0)
        self.page.get_by_role("button", name="Select this meaning", exact=True).click()
        expect(self.page.locator("#case-stage")).to_have_text("PREVIEW", timeout=30000)
        self.tab("model")
        expect(self.page.locator('#model-canvas [data-state="SAVED"]')).to_have_count(1)
        return {"stages": ["DRAFT", "PROPOSED", "PREVIEW"], "candidate_hash": self.semantic()}

    def source(self):
        self.page.locator('#domain-tree [data-eija-id="eija-review-slice.term.change-case"]').click()
        self.page.locator("#selection-detail").get_by_role(
            "button", name="repo://src/eija_studio/domain/change_case.py#ChangeCase", exact=True,
        ).click()
        expect(self.page.locator("#source-reader")).to_contain_text("class ChangeCase", timeout=30000)
        expect(self.page.locator("#source-file")).to_contain_text("change_case.py")
        expect(self.page.locator("#source-metadata")).to_contain_text("lines")
        code = self.page.locator("#source-reader").inner_text()
        metadata = self.page.locator("#source-metadata").inner_text()
        self.page.screenshot(path=str(self.out / "source-code.png"))
        self.recording_pause()
        self.tab("source")
        expect(self.page.locator("#source-view")).to_contain_text("Conformance: NOT_RUN")
        region = self.page.locator(".source-table-wrap").first
        region.focus()
        expect(region).to_be_focused()
        expect(region).to_have_attribute("role", "region")
        return {"source_excerpt_contains_class": "class ChangeCase" in code, "metadata": metadata,
                "conformance": "NOT_RUN", "source_table_keyboard_reachable": True}

    def canvas(self):
        self.tab("model")
        before_hash = self.semantic()
        board = self.page.locator("#model-canvas svg")
        before = board.get_attribute("viewBox")
        self.page.locator("#canvas-zoom-in").click()
        expect(board).not_to_have_attribute("viewBox", before)
        zoomed = board.get_attribute("viewBox")
        self.page.locator("#canvas-zoom-out").click()
        expect(board).not_to_have_attribute("viewBox", zoomed)
        self.page.locator("#canvas-fit").click()
        fitted = board.get_attribute("viewBox")
        box = board.bounding_box()
        x, y = box["x"] + box["width"] * .4, box["y"] + box["height"] * .85
        self.page.mouse.move(x, y)
        self.page.locator("#model-canvas").focus()
        self.page.keyboard.down("Space")
        self.page.mouse.down()
        self.page.mouse.move(x + 100, y - 40, steps=8)
        self.page.mouse.up()
        self.page.keyboard.up("Space")
        expect(board).not_to_have_attribute("viewBox", fitted)
        self.page.locator("#canvas-fit").click()
        assert self.semantic() == before_hash
        self.page.locator("#canvas-readable").click()
        return {"zoom_and_pan_changed_viewport": True, "semantic_unchanged": before_hash}

    def edit(self):
        self.tab("model")
        self.page.locator("#transition-select").select_option("TR-SAVE")
        self.original_hash, self.original_version = self.semantic(), self.revision()
        self.before_edit_view = self.server_view
        writes = sum(item["method"] == "POST" and item["path"].endswith("/edit") for item in self.requests)
        self.page.locator("#transition-role").select_option("Agent")
        self.page.locator("#edit-role").click()
        self.settled()
        expect(self.page.locator("#transition-details")).to_contain_text("TR-SAVE · Agent")
        self.changed_hash = self.semantic()
        assert self.changed_hash != self.original_hash
        assert self.revision() == self.original_version + 1
        assert sum(item["method"] == "POST" and item["path"].endswith("/edit")
                   for item in self.requests) == writes + 1
        return {"before": self.original_hash, "after": self.changed_hash,
                "version_before": self.original_version, "version_after": self.revision()}

    def comparison_models(self):
        case = self.server_view["case"]
        before = self.before_edit_view["case"]
        assert case["id"] == self.case_id and case["version"] == self.revision()
        assert before["baseline"] == case["baseline"]
        baseline = Workflow.model_validate(case["baseline"])
        candidate = Workflow.model_validate(case["candidate"])
        assert candidate.semantic_hash == self.semantic() == self.changed_hash
        require_only_save_role_change(before["candidate"], case["candidate"])
        assert "TR-SAVE" not in {t.id for t in baseline.transitions}
        return case, before, baseline, candidate

    def semantic_diff(self):
        case, before, baseline, candidate = self.comparison_models()
        self.tab("review")
        article = self.page.locator('[data-eija-id="review.transition.TR-SAVE"]')
        expect(article.locator(".before")).to_contain_text("Not present")
        expect(article.locator(".after")).to_contain_text("Agent · Save")
        expect(article.locator(".after")).to_contain_text("PREVIEW")
        expect(article.locator(".after")).to_contain_text("SAVED")
        expect(article.locator(".diff-table")).to_contain_text("Role")
        article.scroll_into_view_if_needed()
        self.page.screenshot(path=str(self.out / "changes-before-after.png"))
        self.recording_pause()
        record = {"case_id": case["id"], "version": case["version"], "baseline": case["baseline"],
                  "candidate": case["candidate"], "previous_candidate": before["candidate"],
                  "baseline_semantic": baseline.semantic_hash, "candidate_semantic": candidate.semantic_hash,
                  "edit_delta": {"transition": "TR-SAVE", "field": "role", "before": "Owner", "after": "Agent"}}
        (self.out / "semantic-diff-response.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        article.get_by_role("button", name="Inspect in model", exact=True).click()
        expect(self.page.locator('[data-tab="model"]')).to_have_attribute("aria-selected", "true")
        assert self.semantic() == candidate.semantic_hash and self.revision() == case["version"]
        return {"baseline_semantic": baseline.semantic_hash, "candidate_semantic": candidate.semantic_hash,
                "case_baseline_diff": "TR-SAVE is added with Agent role", "accepted_edit_delta": record["edit_delta"],
                "response_artifact": "semantic-diff-response.json", "context_preserved": True}

    def refusal(self):
        self.page.locator("#transition-select").select_option("TR-APPROVE")
        before, version = self.semantic(), self.revision()
        writes = sum(item["method"] == "POST" and item["path"].endswith("/edit") for item in self.requests)
        self.page.locator("#transition-role").select_option("Agent")
        self.page.locator("#edit-role").click()
        expect(self.page.locator("#notice")).to_contain_text("EDIT_REFUSED")
        expect(self.page.locator("#notice")).to_contain_text("REFERENCE_AUTHORITY:Approve")
        self.settled()
        after_writes = sum(item["method"] == "POST" and item["path"].endswith("/edit") for item in self.requests)
        assert self.semantic() == before and self.revision() == version and writes == after_writes
        return {"diagnostic": "REFERENCE_AUTHORITY:Approve", "semantic_and_version_unchanged": True,
                "edit_post_not_sent": True}

    def history(self):
        self.page.locator("#undo-edit").click()
        self.settled()
        assert self.semantic() == self.original_hash
        undone_version = self.revision()
        self.page.locator("#redo-edit").click()
        self.settled()
        assert self.semantic() == self.changed_hash and self.revision() == undone_version + 1
        return {"undo_exact_hash": self.original_hash, "redo_exact_hash": self.changed_hash}

    def reload(self):
        version = self.revision()
        self.page.reload()
        expect(self.page.locator("#connection")).to_contain_text("offline", timeout=60000)
        self.settled()
        self.page.locator("#case-list button").filter(has_text=self.label).click()
        self.settled()
        self.tab("model")
        assert self.semantic() == self.changed_hash and self.revision() == version
        expect(self.page.locator("#undo-edit")).to_be_enabled()
        return {"same_candidate_after_reload": self.changed_hash, "version": version}

    def keyboard(self):
        self.page.keyboard.press("Control+k")
        expect(self.page.locator("#command-palette")).to_be_visible()
        expect(self.page.locator("#palette-search")).to_be_focused()
        self.page.keyboard.press("Escape")
        expect(self.page.locator("#command-palette")).to_be_hidden()
        model_tab = self.page.locator('[data-tab="model"]')
        model_tab.focus()
        model_tab.press("ArrowRight")
        expect(self.page.locator('[data-tab="code"]')).to_be_focused()
        expect(self.page.locator('[data-tab="code"]')).to_have_attribute("aria-selected", "true")
        self.tab("model")
        group = self.page.locator('#domain-tree [data-eija-id="eija-review-slice.group.term"]')
        group.focus()
        group.press("ArrowRight")
        expect(self.page.locator('#domain-tree [data-eija-id="eija-review-slice.term.change-case"]')).to_be_focused()
        self.page.keyboard.press("Enter")
        expect(self.page.locator("#selection-detail")).to_contain_text("Change Case")
        splitter = self.page.locator("#explorer-resizer")
        splitter.focus()
        before_width = self.page.locator("#domain-tree").bounding_box()["width"]
        splitter.press("ArrowRight")
        after_width = self.page.locator("#domain-tree").bounding_box()["width"]
        assert before_width != after_width
        splitter.press("ArrowLeft")
        return {"palette_focus_and_escape": True, "tab_arrows": True, "tree_arrows_and_enter": True,
                "splitter_keyboard_resize": [before_width, after_width]}

    def view_modes(self):
        before, version = self.semantic(), self.revision()
        self.page.locator("#model-version").select_option("baseline")
        expect(self.page.locator('#model-canvas [data-state="SAVED"]')).to_have_count(0)
        expect(self.page.locator("#edit-role")).to_be_disabled()
        self.page.locator("#model-version").select_option("working")
        expect(self.page.locator('#model-canvas [data-state="SAVED"]')).to_have_count(1)
        self.page.locator('[data-bottom="history-pane"]').click()
        self.page.locator("#case-history .history-row").first.get_by_role("button", name="View model").click()
        expect(self.page.locator("#model-version")).to_have_value("history")
        expect(self.page.locator("#edit-role")).to_be_disabled()
        expect(self.page.locator('#model-canvas [data-eija-id="eija-review-slice.transition.TR-SAVE"]')).to_have_attribute(
            "aria-label", "Save, Owner, PREVIEW to SAVED. Select transition.",
        )
        self.page.screenshot(path=str(self.out / "historical-preview.png"))
        self.page.locator("#model-version").select_option("working")
        self.page.locator("#transition-select").select_option("TR-SAVE")
        expect(self.page.locator("#transition-details")).to_contain_text("TR-SAVE · Agent")
        assert self.semantic() == before and self.revision() == version
        return {"baseline_and_history_read_only": True, "history_owner_current_agent": True,
                "candidate_and_revision_unchanged": True}

    def panels(self):
        before = self.semantic()
        dimensions = {}
        layout = self.page.locator("#workspace-layout")
        layout_was_open = layout.get_attribute("open") is not None
        for name, control in (("explorer", "#toggle-explorer"), ("inspector", "#toggle-inspector"),
                              ("bottom", "#toggle-bottom")):
            original = self.page.locator("#model-canvas").bounding_box()
            if layout.get_attribute("open") is None:
                self.page.locator("#layout-summary").click()
            self.page.locator(control).click()
            expect(self.page.locator(control)).to_have_attribute("aria-expanded", "false")
            expanded = self.page.locator("#model-canvas").bounding_box()
            key = "height" if name == "bottom" else "width"
            assert expanded[key] > original[key]
            if layout.get_attribute("open") is None:
                self.page.locator("#layout-summary").click()
            self.page.locator(control).click()
            expect(self.page.locator(control)).to_have_attribute("aria-expanded", "true")
            dimensions[name] = {"before": original[key], "collapsed": expanded[key]}
        if layout_was_open:
            self.page.locator("#layout-summary").click()
        assert self.semantic() == before
        return {"canvas_reclaims_panel_space": dimensions, "semantic_unchanged": before}

    def evidence(self):
        self.tab("evidence")
        expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        expect(self.page.locator("#approve")).to_be_disabled()
        expect(self.page.locator("#apply")).to_be_disabled()
        assert self.packet()["human_understanding"] == "UNKNOWN"
        assert "SOURCE_REVIEW_REQUIRED" in self.packet()["blockers"]
        self.page.locator("#verify").click()
        expect(self.page.locator("#notice")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        self.settled()
        expect(self.page.locator("#approve")).to_be_disabled()
        return {"source_review": "REQUIRED", "human_understanding": "UNKNOWN",
                "verification": "REFUSED_SOURCE_REVIEW_REQUIRED", "approval_disabled": True}

    def viewport(self):
        self.tab("model")
        results = []
        for width, height in ((1600, 1100), (1280, 800)):
            self.page.set_viewport_size({"width": width, "height": height})
            self.page.locator("#canvas-fit").click()
            body = self.page.locator("body").bounding_box()
            canvas = self.page.locator("#model-canvas").bounding_box()
            assert body["width"] <= width + 1 and body["height"] <= height + 1
            assert canvas["width"] >= 400 and canvas["height"] >= 260
            assert canvas["y"] >= 0 and canvas["y"] + canvas["height"] <= height
            results.append({"viewport": [width, height], "body": body, "canvas": canvas})
            self.page.screenshot(path=str(self.out / f"viewport-{width}.png"))
        self.page.set_viewport_size({"width": 1600, "height": 1100})
        return results

    def accessibility(self):
        unnamed = []
        buttons = self.page.locator("button, [role=button]")
        for index in range(buttons.count()):
            control = buttons.nth(index)
            if not control.is_visible():
                continue
            named = (control.get_attribute("aria-label") or control.get_attribute("aria-labelledby")
                     or control.inner_text().strip() or control.get_attribute("title"))
            if not named:
                unnamed.append(control.get_attribute("id") or "unnamed button")
        assert not unnamed
        expect(self.page.locator('.tabs [role="tab"][aria-selected="true"]')).to_have_attribute("tabindex", "0")
        expect(self.page.locator("#source-status")).to_have_attribute("role", "status")
        return {"visible_buttons_have_names": True, "active_tab_keyboard_reachable": True,
                "scope": "DOM names, live status and keyboard checks; axe observations are reported separately."}

    def readability(self):
        results = []
        for width, height in ((1600, 1100), (1280, 800)):
            self.page.set_viewport_size({"width": width, "height": height})
            self.page.locator("#canvas-readable").click()
            default = self.label_sizes()
            assert default["state_label_min_px"] >= 14
            self.page.screenshot(path=str(self.out / f"readable-{width}.png"))
            self.page.locator("#canvas-fit").click()
            overview = self.label_sizes()
            self.page.screenshot(path=str(self.out / f"overview-{width}.png"))
            results.append({"viewport": [width, height], "readable": default, "overview": overview,
                            "scope": "Overview may shrink labels; use 100% and pan to inspect details."})
        self.page.set_viewport_size({"width": 1600, "height": 1100})
        self.page.locator("#canvas-readable").click()
        return results

    def label_sizes(self):
        labels = self.page.locator("#model-canvas .state-label")
        heights = [labels.nth(index).bounding_box()["height"] for index in range(labels.count())]
        matrix = self.page.locator("#model-canvas svg").evaluate("element => {const m=element.getScreenCTM(); return {x:Math.hypot(m.a,m.b),y:Math.hypot(m.c,m.d)};}")
        return {"state_label_min_px": min(heights), "zoom": self.page.locator("#canvas-zoom").inner_text(),
                "label_count": len(heights), "actual_scale": matrix}

    def reflow(self):
        before, version = self.semantic(), self.revision()
        results = []
        for height in (800, 568):
            self.page.set_viewport_size({"width": 320, "height": height})
            for tab in ("change", "impact", "try", "evidence", "source", "code", "model"):
                self.tab(tab)
                expect(self.page.locator(f'[data-tab="{tab}"]')).to_have_attribute("aria-selected", "true")
            expect(self.page.locator("#model-canvas svg")).to_be_visible()
            self.page.locator("#canvas-readable").click()
            bounds = self.page.locator("body").evaluate("""element => ({
                body_width: element.scrollWidth, document_width: document.documentElement.scrollWidth,
                viewport_width: innerWidth
            })""")
            assert bounds["body_width"] <= 321 and bounds["document_width"] <= 321
            readable = self.label_sizes()
            results.append({"viewport": [320, height], "bounds": bounds, "readable": readable})
            self.page.screenshot(path=str(self.out / f"reflow-320-{height}.png"))
            assert readable["state_label_min_px"] >= 14, f"100% labels shrink at 320x{height}: {readable}"
            assert abs(readable["actual_scale"]["x"] - 1) < .005 and abs(readable["actual_scale"]["y"] - 1) < .005
        assert self.semantic() == before and self.revision() == version
        self.page.set_viewport_size({"width": 1600, "height": 1100})
        self.page.locator("#canvas-readable").click()
        return {"seven_tabs_clickable_without_force": True, "viewports": results,
                "candidate_and_revision_unchanged": True, "scope": "320 CSS pixels, not a mobile usability study."}

    def axe_observations(self):
        axe = Axe.from_file(AXE_FILE_PATH)
        views = []
        for tab in ("model", "change", "evidence", "source"):
            self.tab(tab)
            result = axe.run(self.page, options={
                "runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]},
                "resultTypes": ["violations", "incomplete"],
            }).response
            views.append({"view": tab, "axe_version": result["testEngine"]["version"],
                          "violations": result["violations"], "incomplete": result["incomplete"]})
        (self.out / "axe.json").write_text(json.dumps(views, indent=2) + "\n", encoding="utf-8")
        self.tab("model")
        assert not any(view["violations"] for view in views), "axe violations: inspect axe.json"
        return {"automatic_violations": 0, "incomplete": [
            {"view": view["view"], "rule": item["id"], "impact": item.get("impact"),
             "targets": [node["target"] for node in item["nodes"]]}
            for view in views for item in view["incomplete"]],
            "review_status": "REVIEW_REQUIRED" if any(view["incomplete"] for view in views) else "NO_ITEMS",
            "scope": "Zero automated violations is not full WCAG conformance; incomplete checks need review."}


def run_steps(review):
    try:
        for name, action in zip(EXPECTED[:-2], (
            review.entry, review.intent, review.source, review.canvas, review.edit, review.semantic_diff,
            review.refusal, review.history, review.reload, review.view_modes, review.panels,
            review.keyboard, review.evidence, review.viewport, review.accessibility,
            review.readability, review.reflow, review.axe_observations,
        ), strict=True):
            review.step(name, action)
    except Exception as error:
        review.checks.append({"id": review.stage, "status": "FAIL", "reason": str(error)})
        review.page.screenshot(path=str(review.out / "failure.png"), full_page=True)


def final_checks(review):
    unexpected = [item for item in review.http_errors
                  if item["stage"] != "evidence-truth" or item["status"] != 409]
    review.checks.append({"id": "runtime-errors", "status": "FAIL" if review.errors or unexpected else "PASS",
                         "javascript_errors": review.errors, "http_errors": review.http_errors})
    review.checks.append({"id": "owner-boundary", "status": "FAIL" if review.forbidden else "PASS",
                         "forbidden_requests": review.forbidden})
    return complete_report(review)


def complete_report(review):
    completed = {item["id"] for item in review.checks}
    review.checks.extend({"id": name, "status": "NOT_RUN", "reason": "An earlier dependent check failed."}
                        for name in EXPECTED if name not in completed)
    return {"checks": review.checks, "case_id": review.case_id, "requests": review.requests,
            "outcome": "PASS" if all(item["status"] == "PASS" for item in review.checks) else "FAIL"}


def browser_run(args, base, playwright):
    browser = playwright.chromium.launch(headless=True, slow_mo=100 if args.record else 0)
    options = {"viewport": {"width": 1600, "height": 1100}, "device_scale_factor": 1}
    if args.record:
        options |= {"record_video_dir": str(args.out / "video"),
                    "record_video_size": {"width": 1600, "height": 1100}}
    context = browser.new_context(**options)
    page = context.new_page()
    review = Review(page, args.out, base, args.record)
    try:
        run_steps(review)
        report = final_checks(review) | {"browser": browser.version}
        (args.out / "accessibility-snapshot.txt").write_text(page.locator("body").aria_snapshot(), encoding="utf-8")
        video = page.video
        context.close()
        if video:
            report["video"] = str(video.path())
        return report
    finally:
        browser.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).resolve().parents[2] / "reports/self-dogfood-browser")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report = {"schema": "eija.ide-browser-observations.v1", "utc": datetime.now(UTC).isoformat(),
              "identity": "normal_source_review_required", "human_value": "NOT_MEASURED",
              "scope": "Disposable local synthetic workspace; scripted isolated Chromium context."}
    report |= observe_subject(args)
    (args.out / "observations.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(json.dumps({
        "outcome": report["outcome"], "checks": [(item["id"], item["status"]) for item in report["checks"]],
        "report": str(args.out / "observations.json"),
    }) + "\n")
    return {"PASS": 0, "FAIL": 1, "NOT_RUN": 2}[report["outcome"]]


def not_run(reason):
    return {"outcome": "NOT_RUN", "checks": [
        {"id": name, "status": "NOT_RUN", "reason": reason} for name in EXPECTED],
    }


def observe_subject(args):
    repo = Path(__file__).resolve().parents[2]
    before = capture_subject(repo)
    try:
        report = execute(args)
    finally:
        after = capture_subject(repo)
        comparison = compare_subjects(before, after)
        manifest = {"before": before, "after": after, "comparison": comparison}
        (args.out / "subject-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    report["source_preservation"] = comparison | {"manifest": "subject-manifest.json"}
    if comparison["status"] != "UNCHANGED":
        report["outcome"] = "FAIL"
    return report


def execute(args):
    if not __debug__:
        return not_run("Run without Python -O: assertions are the test oracles.")
    if PREREQUISITE_ERROR:
        return not_run("Install the hci extra: " + PREREQUISITE_ERROR)
    try:
        with disposable_server() as base, sync_playwright() as playwright:
            return browser_run(args, base, playwright)
    except BrowserError as error:
        if "Executable doesn't exist" in str(error):
            return not_run("Install the isolated browser: python -m playwright install chromium")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
