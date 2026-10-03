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
PRIMARY_VIEWS = ("model", "code", "change", "review", "try", "evidence")
WORKSPACE_VIEWS = (*PRIMARY_VIEWS, "impact", "visual", "source")


def require_only_save_role_change(before, after):
    expected = deepcopy(before)
    save = next(t for t in expected["transitions"] if t["id"] == "TR-SAVE")
    assert save["role"] == "Owner"
    save["role"] = "Agent"
    assert after == expected, "Accepted edit changed more than the selected Save role."


@contextlib.contextmanager
def disposable_server(repository_root=None, *, pack_path=None, before_serve=None):
    """Own offline server. Optional fixture setup runs before HTTP starts, only in this throw-away workspace."""
    repo = Path(__file__).resolve().parents[2]
    pack = repo / "packs/eija-review-slice" if pack_path is None else Path(pack_path)
    if not (pack / "pack.json").is_file():
        raise RuntimeError("Run this script from an EIJA checkout containing packs/eija-review-slice.")
    scratch_root = repo / ".tmp"
    scratch_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="self-dogfood-browser-", dir=scratch_root) as directory:
        workspace = Path(directory).resolve()
        if not workspace.is_relative_to(scratch_root.resolve()):
            raise RuntimeError("Disposable workspace escaped the checkout scratch directory.")
        studio = build_studio(workspace, pack=pack, repository_root=repo if repository_root is None else repository_root)
        if before_serve is not None:
            before_serve(studio)
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
        self.navigation_actions = []
        self.edit_preview_responses, self.edit_preview_records = [], []
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
        if response.status == 200 and response.request.method == "POST" and path.endswith("/edit/preview"):
            self.edit_preview_responses.append({"path": path, "body": response.json()})

    def edit_preview_snapshot(self):
        values = {}
        for name, path in (("view", f"cases/{self.case_id}"), ("history", f"cases/{self.case_id}/history")):
            response = self.page.context.request.get(self.base + "api/" + path,
                headers={"Authorization": "Bearer " + TEST_CAPABILITY})
            assert response.status == 200, f"Prospective-edit oracle GET {path}: HTTP {response.status}"
            values[name] = response.json()
        values["edit_posts"] = sum(item["method"] == "POST" and item["path"].endswith("/edit") for item in self.requests)
        return values

    def inspect_edit_preview(self, before, expected_candidate=None, transaction=None, *, legal=True):
        dialog = self.page.locator("#edit-preview")
        expect(dialog).to_be_visible()
        expect(self.page.locator("#edit-preview-status")).to_have_attribute("data-status", "ready" if legal else "refused")
        payload = json.loads(self.page.locator("#edit-preview-json").text_content())
        assert self.edit_preview_responses and self.edit_preview_responses[-1] == {
            "path": f"/api/cases/{self.case_id}/edit/preview", "body": payload}, "Visible preview differs from actual response"
        case = before["view"]["case"]
        assert payload["case_id"] == case["id"] and payload["version"] == case["version"] and payload["stage"] == case["stage"]
        assert payload["semantic_hash"] == before["view"]["packet"]["subject"]["semantic"]
        assert payload["current"] == case["candidate"] and payload["legal"] is legal
        assert payload["scope"] == "semantic-edit-preview" and payload["applied"] is False and payload["persisted"] is False
        if transaction is not None:
            assert payload["transaction"] == transaction, "Server preview describes a different typed transaction"
        expect(dialog).to_have_attribute("data-case-id", case["id"])
        expect(dialog).to_have_attribute("data-revision", str(case["version"]))
        expect(dialog).to_have_attribute("data-semantic-hash", payload["semantic_hash"])
        assert self.edit_preview_snapshot() == before, "Preview changed case, history, runtime observations or sent /edit"
        if legal:
            assert expected_candidate is not None, "Legal preview needs an independent expected full candidate"
            assert payload["candidate"] == expected_candidate, "Preview changes more than the intended fields"
            proposed_hash = Workflow.model_validate(expected_candidate).semantic_hash
            assert payload["candidate_semantic_hash"] == proposed_hash
            expect(dialog).to_have_attribute("data-proposed-semantic-hash", proposed_hash)
            expect(self.page.locator("#edit-preview-apply")).to_be_enabled()
            pair = self.page.locator("#edit-preview-comparison")
            ident = payload["transaction"]["transition"]
            selected = pair.locator(".compare-selection")
            expect(selected).to_have_attribute("data-kind", "transition")
            expect(selected).to_have_attribute("data-id", ident)
            fields = ("action", "role", "from_state", "to_state", "guards", "required_effects", "forbidden_effects")
            for side, model in (("before", payload["current"]), ("after", expected_candidate)):
                board = pair.locator(f'[data-compare-side="{side}"]')
                states = board.locator("g.compare-node[data-state]").evaluate_all("nodes=>nodes.map(n=>n.dataset.state).sort()")
                edges = board.locator("g.compare-edge[data-transition]").evaluate_all("nodes=>nodes.map(n=>n.dataset.transition).sort()")
                assert states == sorted(model["states"]) and edges == sorted(t["id"] for t in model["transitions"])
                transition = next(t for t in model["transitions"] if t["id"] == ident)
                for field in fields:
                    text = selected.locator(f'[data-field="{field}"] td').nth(0 if side == "before" else 1).text_content()
                    actual = json.loads(text.removesuffix(" (none declared)")) if isinstance(transition[field], list) else text
                    assert actual == transition[field], f"Prospective {side} {field} differs from full server snapshot"
            expect(pair.locator('[data-compare-action="evidence"]')).to_have_count(0)
            expect(pair.locator('[data-compare-reference]')).to_have_count(0)
        else:
            assert payload["candidate"] is None and payload["candidate_semantic_hash"] is None
            expect(self.page.locator("#edit-preview-apply")).to_be_disabled()
            expect(self.page.locator("#edit-preview-comparison .paired-compare")).to_have_count(0)
        self.edit_preview_records.append({"stage": self.stage, "before": before, "server_preview": payload,
                                          "expected_candidate": expected_candidate})
        (self.out / "prospective-edit-observations.json").write_text(json.dumps(self.edit_preview_records, indent=2) + "\n", encoding="utf-8")
        return payload

    def activate_preview_control(self, selector, *, keyboard=False):
        if keyboard:
            for _ in range(80):
                if self.page.locator(selector).evaluate("node=>node===document.activeElement"):
                    break
                self.page.keyboard.press("Tab")
                self.navigation_action("key", "#edit-preview", "Tab")
            else:
                raise AssertionError(f"Preview control {selector} is not keyboard reachable")
            self.page.keyboard.press("Enter")
            self.navigation_action("key", selector, "Enter")
        else:
            self.page.locator(selector).click()
            self.navigation_action("click", selector)

    def apply_edit_preview(self, before, payload, *, keyboard=False):
        with self.page.expect_response(lambda r: r.request.method == "POST"
                                       and urlsplit(r.url).path == f"/api/cases/{self.case_id}/edit") as pending:
            self.activate_preview_control("#edit-preview-apply", keyboard=keyboard)
        assert pending.value.status == 200, f"Confirmed edit: HTTP {pending.value.status}"
        assert pending.value.request.post_data_json == {"expected_version": before["view"]["case"]["version"],
                                                        "transaction": payload["transaction"]}
        ack = pending.value.json()
        assert ack["id"] == self.case_id and ack["version"] == before["view"]["case"]["version"] + 1
        assert ack["candidate"] == payload["candidate"]
        self.settled()
        expect(self.page.locator("#edit-preview")).to_be_hidden(timeout=60000)
        after = self.edit_preview_snapshot()
        assert after["view"]["case"]["candidate"] == payload["candidate"]
        assert after["edit_posts"] == before["edit_posts"] + 1, "Apply did not send exactly one edit"
        return after

    def close_edit_preview(self, before, *, escape=False, keyboard=False):
        if escape:
            self.page.keyboard.press("Escape")
            self.navigation_action("key", "#edit-preview", "Escape")
        else:
            self.activate_preview_control("#edit-preview-cancel", keyboard=keyboard)
        expect(self.page.locator("#edit-preview")).to_be_hidden()
        assert self.edit_preview_snapshot() == before, "Closing an unsubmitted preview changed persisted facts"

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

    def assert_view(self, name):
        assert name in WORKSPACE_VIEWS, f"Unknown workspace view: {name}"
        region = "comparison-workspace" if name == "review" else name
        expect(self.page.locator(f"#{region}")).to_be_visible()
        current = self.page.locator('[data-tab][aria-current="page"]')
        expect(current).to_have_count(1 if name in PRIMARY_VIEWS else 0)
        if name in PRIMARY_VIEWS:
            expect(self.page.locator(f'[data-tab="{name}"]')).to_have_attribute("aria-current", "page")
        else:
            expect(self.page.locator(f'[data-tab="{name}"]')).to_have_count(0)

    def open_workspace(self):
        dialog = self.page.locator("dialog#workspace-dialog")
        if not dialog.is_visible():
            self.page.locator("#open-workspace").click()
            self.navigation_action("click", "#open-workspace")
        expect(dialog).to_be_visible()
        expect(dialog).to_have_attribute("open", "")
        expect(dialog.locator("button[data-workspace-view]")).to_have_count(len(WORKSPACE_VIEWS))
        for name in WORKSPACE_VIEWS:
            expect(dialog.locator(f'button[data-workspace-view="{name}"]')).to_be_visible()
        expect(self.page.locator("button[data-tab]")).to_have_count(len(PRIMARY_VIEWS))
        expect(self.page.locator('[data-tab][role="tab"], [role="tablist"] [data-tab]')).to_have_count(0)
        expect(self.page.locator("[data-tab][aria-selected]")).to_have_count(0)
        return dialog

    def workspace_view(self, name):
        assert name in WORKSPACE_VIEWS, f"Unknown workspace view: {name}"
        dialog = self.open_workspace()
        selector = f'[data-workspace-view="{name}"]'
        dialog.locator(selector).click()
        self.navigation_action("click", "#workspace-dialog " + selector)
        expect(dialog).to_be_hidden()
        self.settled()
        self.assert_view(name)
        destination = f'[data-tab="{name}"]' if name in PRIMARY_VIEWS else f"#{name}"
        expect(self.page.locator(destination)).to_be_focused()

    def tab(self, name):
        assert name in WORKSPACE_VIEWS, f"Unknown workspace view: {name}"
        target = self.page.locator(f'[data-tab="{name}"]')
        if name not in PRIMARY_VIEWS or not target.is_visible():
            self.workspace_view(name)
            return
        target.click()
        self.navigation_action("click", f'[data-tab="{name}"]')
        self.settled()
        self.assert_view(name)

    def workspace_keyboard_routes(self):
        dialog = self.open_workspace()
        expect(self.page.locator("#close-workspace")).to_be_focused()
        routes = ("model", "change", "impact", "review", "code", "try", "evidence", "visual", "source")
        for name in routes:
            self.page.keyboard.press("Tab")
            self.navigation_action("key", "#workspace-dialog", "Tab")
            target = dialog.locator(f'[data-workspace-view="{name}"]')
            expect(target).to_be_focused()
            expect(target).to_be_enabled()
            expect(target).to_be_in_viewport()
            self.assert_view("model")
        self.page.keyboard.press("Escape")
        self.navigation_action("key", "#workspace-dialog", "Escape")
        expect(dialog).to_be_hidden()
        expect(self.page.locator("#open-workspace")).to_be_focused()
        return list(routes)

    def open_bottom(self, panel):
        assert panel in {"problems-pane", "evidence-pane", "history-pane"}, f"Unknown bottom panel: {panel}"
        selector = f'[data-bottom="{panel}"]'
        target = self.page.locator(selector)
        if target.is_visible():
            target.click()
            self.navigation_action("click", selector)
        else:
            dialog = self.open_workspace()
            choice = f'[data-workspace-panel="{panel}"]'
            dialog.locator(choice).click()
            self.navigation_action("click", "#workspace-dialog " + choice)
        expect(self.page.locator("#workspace-dialog")).to_be_hidden()
        expect(self.page.locator(f"#{panel}")).to_be_visible()
        expect(target).to_have_attribute("aria-selected", "true")
        expect(target).to_be_focused()

    def open_layout(self):
        dialog = self.open_workspace()
        layout = dialog.locator("details#workspace-layout")
        if layout.get_attribute("open") is None:
            dialog.locator("#workspace-layout > summary").click()
            self.navigation_action("click", "#workspace-dialog #workspace-layout > summary")
        expect(layout).to_have_attribute("open", "")
        return dialog

    def toggle_layout(self, selector):
        dialog = self.open_layout()
        dialog.locator(selector).click()
        self.navigation_action("click", "#workspace-dialog " + selector)
        expect(dialog).to_be_hidden()
        expect(self.page.locator("#open-workspace")).to_be_focused()
        expect(self.page.locator("#workspace-layout")).to_have_attribute("open", "")

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
        self.page.locator("#start-intent").click()
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

    def navigation_action(self, kind, selector, value=None):
        self.navigation_actions.append({"stage": self.stage, "action": kind, "selector": selector, "value": value})

    def reveal_explorer(self):
        if self.page.locator("#toggle-explorer").get_attribute("aria-expanded") != "true":
            self.toggle_layout("#toggle-explorer")
        expect(self.page.locator("#toggle-explorer")).to_have_attribute("aria-expanded", "true")
        expect(self.page.locator("#explorer")).to_be_visible()

    def reveal_inspector(self):
        if self.page.locator("#toggle-inspector").get_attribute("aria-expanded") != "true":
            self.toggle_layout("#toggle-inspector")
        expect(self.page.locator("#toggle-inspector")).to_have_attribute("aria-expanded", "true")
        expect(self.page.locator("#inspector")).to_be_visible()

    def open_explorer_disclosure(self, selector):
        self.reveal_explorer()
        disclosure = self.page.locator(selector)
        if disclosure.get_attribute("open") is None:
            disclosure.locator(":scope > summary").click()
            self.navigation_action("click", selector + " > summary")

    def navigator_mode(self, mode):
        self.reveal_explorer()
        control = self.page.locator("#navigator-mode")
        if control.input_value() != mode:
            control.select_option(mode)
            self.navigation_action("select", "#navigator-mode", mode)
        expect(control).to_have_value(mode)

    def expand_tree_group(self, kind):
        self.reveal_explorer()
        selector = f'#domain-tree .tree-group[data-kind="{kind}"]'
        group = self.page.locator(selector)
        if group.get_attribute("aria-expanded") != "true":
            group.locator(":scope > span").click()
            self.navigation_action("click", selector + " > span")
        expect(group).to_have_attribute("aria-expanded", "true")
        return group

    def domain_group(self, kind):
        self.navigator_mode("domain")
        return self.expand_tree_group(kind)

    def select_transition(self, ident):
        self.tab("model")
        self.expand_tree_group("transition")
        selector = f'#domain-tree [data-kind="transition"][data-item-id="{ident}"]'
        self.page.locator(selector).click()
        self.navigation_action("click", selector)
        expect(self.page.locator("#transition-select")).to_have_value(ident)

    def main_comparison(self):
        return self.page.locator("#review-chapters")

    def main_comparison_navigation(self):
        return self.page.locator("#task-navigator")

    def select_comparison(self, kind, ident):
        self.tab("review")
        self.navigator_mode("task")
        selector = f'[data-compare-key="{kind}:{ident}"]'
        control = self.main_comparison_navigation().locator(selector)
        disclosure = control.locator("xpath=ancestor::details[1]")
        if disclosure.count() and disclosure.get_attribute("open") is None:
            disclosure.locator(":scope > summary").click()
            self.navigation_action("click", "#task-navigator " + selector + " ancestor details > summary")
        control.click()
        self.navigation_action("click", "#task-navigator " + selector)
        detail = self.main_comparison().locator(".compare-selection")
        expect(detail).to_have_attribute("data-kind", kind)
        expect(detail).to_have_attribute("data-id", ident)
        return detail

    def assert_comparison_transition(self, ident, baseline, candidate):
        detail = self.select_comparison("transition", ident)
        old = next((item for item in baseline["transitions"] if item["id"] == ident), None)
        new = next((item for item in candidate["transitions"] if item["id"] == ident), None)
        fields = ("action", "role", "from_state", "to_state", "guards", "required_effects", "forbidden_effects")
        for field in fields:
            row = detail.locator(f'[data-field="{field}"]')
            expect(row).to_have_count(1)
            cells = row.locator("td")
            expect(cells).to_have_count(2)
            for index, model in enumerate((old, new)):
                value = None if model is None else model[field]
                actual = cells.nth(index).text_content()
                if value is None:
                    assert actual == "Not present", (field, index, actual)
                elif isinstance(value, list):
                    assert json.loads(actual.removesuffix(" (none declared)")) == value, (field, index, actual, value)
                else:
                    assert actual == str(value), (field, index, actual, value)
        for side, model in (("before", old), ("after", new)):
            expect(self.main_comparison().locator(f'[data-compare-side="{side}"] [data-transition="{ident}"]')).to_have_count(int(model is not None))
        return detail

    def source(self):
        self.domain_group("term")
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
        self.select_transition("TR-SAVE")
        self.original_hash, self.original_version = self.semantic(), self.revision()
        self.before_edit_view = self.server_view
        preview_before = self.edit_preview_snapshot()
        expected = deepcopy(preview_before["view"]["case"]["candidate"])
        next(t for t in expected["transitions"] if t["id"] == "TR-SAVE")["role"] = "Agent"
        writes = sum(item["method"] == "POST" and item["path"].endswith("/edit") for item in self.requests)
        self.page.locator("#transition-role").select_option("Agent")
        self.page.locator("#edit-role").click()
        preview = self.inspect_edit_preview(preview_before, expected)
        self.apply_edit_preview(preview_before, preview)
        expect(self.page.locator("#transition-details")).to_have_attribute(
            "data-eija-id", "eija-review-slice.transition-detail.TR-SAVE")
        expect(self.page.locator("#transition-role")).to_have_value("Agent")
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
        article = self.assert_comparison_transition("TR-SAVE", case["baseline"], case["candidate"])
        expect(article.locator('[data-field="role"]')).to_contain_text("Role")
        expected_save = next(item for item in case["candidate"]["transitions"] if item["id"] == "TR-SAVE")
        assert {key: expected_save[key] for key in ("role", "action", "from_state", "to_state")} == {
            "role": "Agent", "action": "Save", "from_state": "PREVIEW", "to_state": "SAVED"}
        article.scroll_into_view_if_needed()
        self.page.screenshot(path=str(self.out / "changes-before-after.png"))
        self.recording_pause()
        record = {"case_id": case["id"], "version": case["version"], "baseline": case["baseline"],
                  "candidate": case["candidate"], "previous_candidate": before["candidate"],
                  "baseline_semantic": baseline.semantic_hash, "candidate_semantic": candidate.semantic_hash,
                  "edit_delta": {"transition": "TR-SAVE", "field": "role", "before": "Owner", "after": "Agent"}}
        (self.out / "semantic-diff-response.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        article.get_by_role("button", name="Inspect in model", exact=True).click()
        expect(self.page.locator('[data-tab="model"]')).to_have_attribute("aria-current", "page")
        assert self.semantic() == candidate.semantic_hash and self.revision() == case["version"]
        return {"baseline_semantic": baseline.semantic_hash, "candidate_semantic": candidate.semantic_hash,
                "case_baseline_diff": "TR-SAVE is added with Agent role", "accepted_edit_delta": record["edit_delta"],
                "response_artifact": "semantic-diff-response.json", "context_preserved": True}

    def refusal(self):
        self.select_transition("TR-APPROVE")
        before, version = self.semantic(), self.revision()
        preview_before = self.edit_preview_snapshot()
        writes = sum(item["method"] == "POST" and item["path"].endswith("/edit") for item in self.requests)
        self.page.locator("#transition-role").select_option("Agent")
        self.page.locator("#edit-role").click()
        preview = self.inspect_edit_preview(preview_before, legal=False)
        assert "REFERENCE_AUTHORITY:Approve" in preview["codes"]
        expect(self.page.locator("#notice")).to_contain_text("EDIT_REFUSED")
        expect(self.page.locator("#notice")).to_contain_text("REFERENCE_AUTHORITY:Approve")
        self.settled()
        after_writes = sum(item["method"] == "POST" and item["path"].endswith("/edit") for item in self.requests)
        assert self.semantic() == before and self.revision() == version and writes == after_writes
        self.close_edit_preview(preview_before)
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
        before = self.edit_preview_snapshot()
        case = before["view"]["case"]
        version = self.revision()
        assert case["id"] == self.case_id and case["version"] == version
        self.page.reload()
        expect(self.page.locator("#connection")).to_contain_text("offline", timeout=60000)
        self.settled()
        self.page.locator("#case-switcher").select_option(self.case_id)
        self.navigation_action("select_option", "#case-switcher", self.case_id)
        self.settled()
        selected = self.page.locator("#case-switcher option:checked")
        expect(selected).to_have_count(1)
        expect(selected).to_have_attribute("value", self.case_id)
        expect(selected).to_have_attribute("title", case["request"])
        expect(selected).to_have_text(f'{case["request"]} · {case["stage"]} · {case["id"]}')
        expect(self.page.locator("#case-title")).to_have_text(case["request"])
        expect(self.page.locator("#case-stage")).to_have_text(case["stage"])
        assert self.edit_preview_snapshot() == before, "Reload navigation changed the authoritative case or history"
        assert self.packet() == before["view"]["packet"], "Reload displayed another case or review revision"
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
        self.tab("model")
        expect(self.page.locator('[data-tab="model"]')).to_be_focused()
        self.page.keyboard.press("Tab")
        self.navigation_action("key", '[data-tab="model"]', "Tab")
        expect(self.page.locator('[data-tab="code"]')).to_be_focused()
        expect(self.page.locator('[data-tab="model"]')).to_have_attribute("aria-current", "page")
        expect(self.page.locator('[data-tab="code"]')).not_to_have_attribute("aria-current", "page")
        expect(self.page.locator("#code")).to_be_hidden()
        self.page.keyboard.press("Enter")
        self.navigation_action("key", '[data-tab="code"]', "Enter")
        self.settled()
        self.assert_view("code")
        expect(self.page.locator('[data-tab="code"]')).to_be_focused()
        self.tab("model")
        self.domain_group("term")
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
        return {"palette_focus_and_escape": True, "primary_button_tab_then_enter": True,
                "tab_focus_does_not_activate_view": True, "tree_arrows_and_enter": True,
                "splitter_keyboard_resize": [before_width, after_width]}

    def view_modes(self):
        before, version = self.semantic(), self.revision()
        self.page.locator("#model-version").select_option("baseline")
        expect(self.page.locator('#model-canvas [data-state="SAVED"]')).to_have_count(0)
        expect(self.page.locator("#edit-role")).to_be_disabled()
        self.page.locator("#model-version").select_option("working")
        expect(self.page.locator('#model-canvas [data-state="SAVED"]')).to_have_count(1)
        self.open_bottom("history-pane")
        self.page.locator("#case-history .history-row").first.get_by_role("button", name="View model").click()
        expect(self.page.locator("#model-version")).to_have_value("history")
        expect(self.page.locator("#edit-role")).to_be_disabled()
        expect(self.page.locator('#model-canvas [data-eija-id="eija-review-slice.transition.TR-SAVE"]')).to_have_attribute(
            "aria-label", "Save, Owner, PREVIEW to SAVED. Select transition.",
        )
        self.page.screenshot(path=str(self.out / "historical-preview.png"))
        self.page.locator("#model-version").select_option("working")
        self.select_transition("TR-SAVE")
        expect(self.page.locator("#transition-details")).to_have_attribute(
            "data-eija-id", "eija-review-slice.transition-detail.TR-SAVE")
        expect(self.page.locator("#transition-role")).to_have_value("Agent")
        assert self.semantic() == before and self.revision() == version
        return {"baseline_and_history_read_only": True, "history_owner_current_agent": True,
                "candidate_and_revision_unchanged": True}

    def panels(self):
        before = self.semantic()
        dimensions = {}
        self.reveal_explorer()
        self.reveal_inspector()
        self.open_bottom("history-pane")
        for name, control in (("explorer", "#toggle-explorer"), ("inspector", "#toggle-inspector"),
                              ("bottom", "#toggle-bottom")):
            original = self.page.locator("#model-canvas").bounding_box()
            self.toggle_layout(control)
            expect(self.page.locator(control)).to_have_attribute("aria-expanded", "false")
            expanded = self.page.locator("#model-canvas").bounding_box()
            key = "height" if name == "bottom" else "width"
            assert expanded[key] > original[key]
            self.toggle_layout(control)
            expect(self.page.locator(control)).to_have_attribute("aria-expanded", "true")
            dimensions[name] = {"before": original[key], "collapsed": expanded[key]}
        assert self.semantic() == before
        return {"canvas_reclaims_panel_space": dimensions, "semantic_unchanged": before,
                "layout_choices_close_workspace_and_restore_focus": True,
                "layout_disclosure_stays_expanded": True}

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
        primary = self.page.locator("button[data-tab]")
        expect(primary).to_have_count(len(PRIMARY_VIEWS))
        expect(self.page.locator('[data-tab][role="tab"], [role="tablist"] [data-tab]')).to_have_count(0)
        expect(self.page.locator("[data-tab][aria-selected]")).to_have_count(0)
        for name in PRIMARY_VIEWS:
            expect(self.page.locator(f'button[data-tab="{name}"]')).to_have_js_property("tabIndex", 0)
        expect(self.page.locator('[data-tab][aria-current="page"]')).to_have_count(1)
        expect(self.page.locator('[data-tab="model"]')).to_have_attribute("aria-current", "page")
        expect(self.page.locator("#source-status")).to_have_attribute("role", "status")
        return {"visible_buttons_have_names": True, "six_primary_buttons_in_tab_order": True,
                "current_primary_view_marked": True,
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
            for view in ("change", "impact", "try", "evidence", "source", "code", "review", "visual", "model"):
                self.workspace_view(view)
            for view in PRIMARY_VIEWS:
                self.tab(view)
                expect(self.page.locator(f'[data-tab="{view}"]')).to_have_attribute("aria-current", "page")
            self.tab("model")
            keyboard_routes = self.workspace_keyboard_routes()
            expect(self.page.locator("#model-canvas svg")).to_be_visible()
            self.page.locator("#canvas-readable").click()
            bounds = self.page.locator("body").evaluate("""element => ({
                body_width: element.scrollWidth, document_width: document.documentElement.scrollWidth,
                viewport_width: innerWidth
            })""")
            assert bounds["body_width"] <= 321 and bounds["document_width"] <= 321
            readable = self.label_sizes()
            results.append({"viewport": [320, height], "bounds": bounds, "readable": readable,
                            "workspace_routes_reached_by_native_tab": keyboard_routes})
            self.page.screenshot(path=str(self.out / f"reflow-320-{height}.png"))
            assert readable["state_label_min_px"] >= 14, f"100% labels shrink at 320x{height}: {readable}"
            assert abs(readable["actual_scale"]["x"] - 1) < .005 and abs(readable["actual_scale"]["y"] - 1) < .005
        assert self.semantic() == before and self.revision() == version
        self.page.set_viewport_size({"width": 1600, "height": 1100})
        self.page.locator("#canvas-readable").click()
        return {"nine_workspace_views_clickable_without_force": True,
                "six_primary_buttons_clickable_without_force": True, "viewports": results,
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
            "navigation_actions": review.navigation_actions,
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
