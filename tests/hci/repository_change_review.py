"""Real immutable Code changes review; independent Git oracles and isolated browser faults."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import socket
import traceback
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

import self_dogfood_replay as replay
from case_preview_navigation import emit, write_json
from ide_review_workspace import subject_identity
from self_dogfood_subject import compare_subjects, file_identity

from eija_studio.adapters.providers.process import resolve_command, run_bounded
from quality.hci.server import ROOT

BASE = "9c22d425ee33e52980a95b33330babec43c6aa59"
HEAD = "c666b6bb76905c0c9bd03e81cac0922136c4cf3e"
TREES = {BASE: "a24d5c145114f847418f1b805afbca6a2c971450", HEAD: "e5fa4c8af6959d3b212fdae3599cddaac9053a4d"}
APP = APP_PATH = "src/eija_studio/resources/web/app.js"
PUBLIC_PATHS = (
    "docs/engineering/2026-10-02-VALIDATION-CHECKPOINT.md", "docs/hci/REPORT.md",
    "docs/hci/report.snapshot.json", "docs/hci/trace.snapshot.json", APP,
    "tests/hci/case_preview_navigation.md", "tests/hci/case_preview_navigation.py", "tests/test_case_navigation.py",
)
APP_BLOBS = {BASE: "fd1905b04f8b14fdb21de0ebc25a97e1283affc2", HEAD: "9e041c4c51c7b18e36d8959e7201863fac1b47fe"}
SYMBOLS = {"repo://" + APP + "#" + quote(fragment, safe="/."): (kind, first, last, status)
           for fragment, kind, first, last, status in (
               ("js/function/cases", "function", 44, 51, "changed"),
               ("js/function/load", "function", 66, 72, "changed"),
               ('js/assignment/$("create").onclick', "assignment", 97, 97, "changed"),
               ('js/assignment/$("case-switcher").onchange', "assignment", 328, 328, "changed"),
               ("js/function/task", "function", 43, 43, "unchanged"))}
CASES_REF = "repo://" + APP + "#js/function/cases"
TASK_REF = "repo://" + APP + "#js/function/task"
CHANGED_SITES = [ref.split("#", 1)[1] for ref, spec in SYMBOLS.items() if spec[3] == "changed"]


def git_read(root, *args):
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    command = [*resolve_command("git"), "--no-optional-locks", "--no-replace-objects",
               "-c", "core.fsmonitor=false", "-C", str(root), *args]
    result = run_bounded(command, input=None, env=env, timeout=15, max_bytes=4 * 1024 * 1024)
    result.check_returncode()
    return result.stdout


@lru_cache(maxsize=1)
def collect_git_oracles(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    changed = git_read(root, "diff", "--no-ext-diff", "--no-textconv", "--no-renames",
                       "--name-only", "-z", BASE, HEAD).rstrip("\0").split("\0")
    assert len(changed) == len(set(changed)) == 9 and set(PUBLIC_PATHS) < set(changed), "git_inventory"
    result = {"changed_total": 9, "excluded_count": 1, "sides": {}, "diffs": {}, "hashes": {}}
    for revision in (BASE, HEAD):
        assert git_read(root, "rev-parse", "--verify", revision + "^{commit}").strip() == revision, "git_commit"
        assert git_read(root, "rev-parse", revision + "^{tree}").strip() == TREES[revision], "git_tree"
        entries = git_read(root, "ls-tree", "-r", "-z", revision, "--", *PUBLIC_PATHS).rstrip("\0").split("\0")
        files = {}
        for entry in entries:
            metadata, path = entry.split("\t", 1)
            mode, kind, blob = metadata.split()
            assert kind == "blob" and path in PUBLIC_PATHS, "git_public_blob"
            text = git_read(root, "cat-file", "blob", blob)
            raw = text.encode("utf-8")
            files[path] = {"blob": blob, "mode": mode, "file_sha256": hashlib.sha256(raw).hexdigest(),
                           "byte_length": len(raw), "status": "captured", "text": text}
        assert files[APP]["blob"] == APP_BLOBS[revision], "git_app_blob"
        result["sides"][revision] = files
        manifest = [[path, row["file_sha256"]] for path, row in sorted(files.items())]
        canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        result["hashes"][revision] = "sha256:" + hashlib.sha256(b"eija.repository.source.v1\0" + canonical.encode()).hexdigest()
    assert result["sides"][BASE][APP]["text"].splitlines()[42] == result["sides"][HEAD][APP]["text"].splitlines()[42], "git_task_changed"
    for base, head in ((BASE, HEAD), (HEAD, BASE)):
        result["diffs"][base] = {path: git_read(root, "-c", "core.quotePath=true", "diff", "--no-ext-diff", "--no-textconv",
            "--no-renames", "--no-color", "--text", "--diff-algorithm=myers", "--no-indent-heuristic",
            "--src-prefix=a/", "--dst-prefix=b/", "--unified=3", base, head, "--", path) for path in PUBLIC_PATHS}
    return result


def _git_identity(payload, oracle, base, head):
    assert (base, head) in ((BASE, HEAD), (HEAD, BASE)), "git_fixture_pair"
    for name, revision in (("base", base), ("head", head)):
        assert payload[name]["commit"] == revision and payload[name]["tree"] == TREES[revision], "git_pair"
        assert payload[name]["changed_source_hash"] == oracle["hashes"][revision], "git_capture_hash"
    assert re.fullmatch(r"[0-9a-f]{64}", payload["comparison_id"]), "git_comparison_id"
    assert payload["read_only"] is True and payload["status"] == "partial", "git_scope"


def _git_metadata(actual, expected):
    if expected is None:
        assert actual is None, "git_absent_side"
        return
    assert actual is not None and actual["blob"] == expected["blob"], "git_blob"
    for key in ("mode", "file_sha256", "byte_length", "status"):
        assert actual[key] == expected[key], "git_file_identity: " + key


def assert_comparison(payload, base=BASE, head=HEAD, oracle=None):
    oracle = collect_git_oracles() if oracle is None else oracle
    _git_identity(payload, oracle, base, head)
    assert payload["schema"] == "eija.repository.change.v1", "git_schema"
    assert payload["coverage"] == {"changed_paths_total": 9, "displayed_paths": 8,
        "excluded_by_reason": {"private_or_dependency_path": 1}, "inventory_reconciles": True}, "git_coverage"
    assert payload["scope"]["semantic_complete"] is False, "git_semantic_scope"
    assert payload["scope"]["behavior"] == "NOT_RUN by source comparison", "git_behavior_scope"
    assert sorted(row["path"] for row in payload["files"]) == sorted(PUBLIC_PATHS), "git_paths"
    for row in payload["files"]:
        path = row["path"]
        status = "added" if path not in oracle["sides"][base] else "deleted" if path not in oracle["sides"][head] else "modified"
        assert row["status"] == status, "git_change_kind"
        for side, revision in (("before", base), ("after", head)):
            _git_metadata(row[side], oracle["sides"][revision].get(path))
    app = next(row for row in payload["files"] if row["path"] == APP)
    changed = [row["reference"] for row in app["symbols"] if row["status"] != "unchanged"]
    assert sorted(changed) == sorted(ref for ref, spec in SYMBOLS.items() if spec[3] == "changed"), "git_changed_sites"
    for reference, (kind, first, last, status) in SYMBOLS.items():
        matches = [row for row in app["symbols"] if row["reference"] == reference]
        assert len(matches) == 1 and matches[0]["status"] == status and matches[0]["kind"] == kind, "git_symbol_status"
        for side in ("before", "after"):
            symbol = matches[0][side]
            assert (symbol["reference"], symbol["kind"], symbol["start_line"], symbol["end_line"]) == (reference, kind, first, last), "git_symbol_range"
        assert (matches[0]["before"]["syntax_digest"] == matches[0]["after"]["syntax_digest"]) == (status == "unchanged"), "git_syntax_relation"


def assert_file(comparison, payload, oracle=None):
    oracle = collect_git_oracles() if oracle is None else oracle
    base, head = comparison["base"]["commit"], comparison["head"]["commit"]
    path, reference = payload["path"], payload["selected_reference"]
    assert path in PUBLIC_PATHS, "git_selection"
    _git_identity(payload, oracle, base, head)
    assert payload["schema"] == "eija.repository.change-file.v1", "git_file_schema"
    assert all(payload[key] == comparison[key] for key in ("base", "head", "comparison_id")), "git_selection_identity"
    assert reference is None or (path == APP and reference in SYMBOLS), "git_fixture_reference"
    for side, revision in (("before", base), ("after", head)):
        expected = oracle["sides"][revision].get(path)
        actual = payload[side]
        _git_metadata(actual, expected)
        if expected is None:
            continue
        lines = expected["text"].splitlines(keepends=True)
        start, end = (1, len(lines)) if reference is None else SYMBOLS[reference][1:3]
        first, last = max(1, start - 3), min(len(lines), end + 3, max(1, start - 3) + 199)
        selected = "".join(lines[first - 1:last])
        text = selected.encode("utf-8")[:32768].decode("utf-8", errors="ignore")
        assert actual["range"] == {"start": first, "end": first + max(1, len(text.splitlines())) - 1}, "git_excerpt_range"
        assert actual["text"] == text and actual["snippet_sha256"] == hashlib.sha256(text.encode()).hexdigest(), "git_excerpt_text"
        assert actual["truncated"] == (last < end or text != selected), "git_excerpt_truncation"
        if reference is not None:
            symbol = actual["symbol"]
            assert (symbol["reference"], symbol["kind"], symbol["start_line"], symbol["end_line"]) == (reference, SYMBOLS[reference][0], start, end), "git_symbol_range"
        impact = payload["known_impact"][side]
        assert impact["complete"] is False and impact["captured_source_hash"] == payload["base" if side == "before" else "head"]["changed_source_hash"], "git_impact_scope"
        if reference is not None:
            assert impact["status"] == "UNKNOWN_TARGET" and "impact" not in impact, "git_unknown_impact"
    assert payload["unified_diff"] == {"status": "AVAILABLE", "text": oracle["diffs"][base][path], "context_lines": 3, "truncated": False}, "git_unified_diff"


def oracle_negative_controls(comparison, file_payload, oracle=None):
    """Pure observation mutations; no API replies, Git objects, or DOM are altered."""
    oracle = collect_git_oracles() if oracle is None else oracle
    assert_file(comparison, file_payload, oracle)
    mutants = {name: deepcopy(file_payload) for name in ("wrong_pair", "wrong_blob", "wrong_range")}
    mutants["wrong_pair"]["head"]["commit"] = comparison["base"]["commit"]
    mutants["wrong_blob"]["after"]["blob"] = APP_BLOBS[comparison["base"]["commit"]]
    mutants["wrong_range"]["after"]["range"]["start"] += 1
    expected = {"wrong_pair": "git_pair", "wrong_blob": "git_blob", "wrong_range": "git_excerpt_range"}
    detected = {}
    for name, mutant in mutants.items():
        try:
            assert_file(comparison, mutant, oracle)
        except AssertionError as error:
            assert str(error) == expected[name], "git_negative_reason: " + name
            detected[name] = str(error)
        else:
            raise AssertionError("git_negative_missed: " + name)
    return detected


class RepositoryReview(replay.Review):
    def __init__(self, page, out, base):
        self.oracles, self.controls, self.held, self.injected = [], [], [], []
        self.comparison = self.file = None
        super().__init__(page, out, base)

    def route(self, route):
        request = route.request
        parsed = urlsplit(request.url)
        query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
        self.requests.append({"stage": self.stage, "method": request.method, "path": parsed.path, "query": query})
        if request.method != "GET":
            self.forbidden.append(parsed.path)
            route.abort()
            return
        control = next((item for item in self.controls if item["path"] == parsed.path
                        and all(query.get(key) == value for key, value in item["query"].items())), None)
        if control is None:
            route.continue_()
            return
        self.controls.remove(control)
        action = control["action"]
        evidence = {"stage": self.stage, "path": parsed.path, "query": query, "action": action}
        self.injected.append(evidence)
        if action == "503":
            route.fulfill(status=503, content_type="application/json", body=json.dumps({"code": "QA_TRANSPORT_FAILURE", "message": "Deliberate isolated-browser transport failure", "details": {}}))
            return
        if action == "hold":
            # Pause immediately; the test fetches this real response after its request event.
            self.held.append((route, None, None, evidence))
            return
        try:
            actual = route.fetch(timeout=60000)
        except replay.BrowserError as error:
            self.errors.append("Controlled response fetch failed: " + str(error).replace(replay.TEST_CAPABILITY, "[test-capability]"))
            with contextlib.suppress(replay.BrowserError):
                route.abort()
            return
        assert actual.status == 200, f"Fault control requires a real successful GET; got {actual.status}"
        payload = actual.json()
        evidence["actual_body"] = payload
        changed = deepcopy(payload)
        if action == "wrong-pair":
            changed["head"]["commit"] = changed["base"]["commit"]
        elif action == "wrong-blob":
            changed["after"]["blob"] = "0" * 40
        elif action == "wrong-range":
            changed["after"]["symbol"]["start_line"] += 1
        else:
            raise AssertionError(f"Unknown controlled fault {action}")
        evidence["injected_body"] = changed
        route.fulfill(response=actual, body=json.dumps(changed))

    def arm(self, action, endpoint="repository/change", **query):
        self.controls.append({"action": action, "path": "/api/" + endpoint, "query": query})

    def oracle(self, endpoint, **query):
        response = self.page.context.request.get(self.base + "api/" + endpoint, params=query,
            headers={"Authorization": "Bearer " + replay.TEST_CAPABILITY}, timeout=60000)
        payload = response.json()
        self.oracles.append({"stage": self.stage, "path": "/api/" + endpoint, "query": query, "status": response.status, "body": payload})
        assert response.status == 200, f"Independent {endpoint} GET failed: HTTP {response.status}"
        return payload

    def status(self, expected):
        replay.expect(self.page.locator("#repository-comparison-status")).to_have_attribute("data-status", expected, timeout=60000)

    def pair_ui(self, comparison):
        root = self.page.locator(".repository-review")
        for attr, value in (("comparison-id", comparison["comparison_id"]), ("base-commit", comparison["base"]["commit"]), ("head-commit", comparison["head"]["commit"])):
            replay.expect(root).to_have_attribute("data-" + attr, value)
        replay.expect(root.locator(".repository-scope")).to_contain_text("Behavior · NOT_RUN")
        for side in ("base", "head"):
            replay.expect(self.page.locator("#repository-loaded-" + side)).to_have_text(comparison[side]["commit"])
        label = self.page.locator("#repository-loaded-pair").get_attribute("aria-label")
        assert all(comparison[side]["commit"] in label for side in ("base", "head")), "Accepted pair accessibility label lost exact full commit identities"
        return root

    def submit(self, base=BASE, head=HEAD, expected="captured"):
        if self.page.locator("#repository-revisions").get_attribute("open") is None:
            self.page.locator("#repository-revisions-summary").click()
            self.navigation_action("click", "#repository-revisions-summary")
        self.page.locator("#repository-base").fill(base)
        self.page.locator("#repository-head").fill(head)
        self.page.locator("#repository-compare").click()
        self.status(expected)

    def accept_pair(self, base=BASE, head=HEAD):
        self.submit(base, head)
        comparison = self.oracle("repository/change", base=base, head=head)
        assert_comparison(comparison, base, head)
        self.pair_ui(comparison)
        self.comparison, self.file = comparison, None
        return comparison

    def show_files(self):
        self.page.locator("#repository-show-files").click()
        replay.expect(self.page.locator("#repository-change-navigator")).to_be_visible()

    def select(self, path=APP_PATH, reference=None, expected="captured-file"):
        if reference is None:
            self.show_files()
            target = self.page.locator(f'[data-repository-path="{path}"]')
            assert target.count() == 1, f"Expected one changed path button for {path}"
            replay.expect(target).to_have_attribute("aria-label", re.compile(re.escape(path) + r"$"))
        else:
            summary = self.page.locator(".repository-file-header summary").filter(has_text=re.compile(r"^\d+ extracted syntax references$"))
            assert summary.count() == 1, "Expected one discoverable syntax reference disclosure"
            if summary.locator("..").get_attribute("open") is None:
                summary.click()
                self.navigation_action("click", "extracted syntax references summary")
            target = self.page.locator(f'[data-repository-reference="{reference}"]')
            if target.count() == 0:
                self.page.locator("select[data-repository-symbol-filter]").select_option("all")
                self.navigation_action("select", "select[data-repository-symbol-filter]", "all")
            assert target.count() == 1, f"Expected one known syntax reference for {reference}"
            replay.expect(target).to_have_attribute("title", reference)
        target.click()
        self.status(expected)
        if expected != "captured-file":
            return None
        query = {"base": self.comparison["base"]["commit"], "head": self.comparison["head"]["commit"], "path": path}
        if reference:
            query["reference"] = reference
        detail = self.oracle("repository/change/file", **query)
        assert_file(self.comparison, detail)
        self.file = detail
        return detail

    def view(self, name, keyboard=False):
        target = self.page.locator(f'[data-repository-view="{name}"]')
        if keyboard:
            current = self.page.locator('[data-repository-view][aria-selected="true"]')
            current.focus()
            self.page.keyboard.press("Home")
            for _ in range(("diff", "before", "after", "syntax", "impact").index(name)):
                self.page.keyboard.press("ArrowRight")
            replay.expect(target).to_be_focused()
        else:
            target.click()
        replay.expect(target).to_have_attribute("aria-selected", "true")
        replay.expect(self.page.locator(".repository-file-view")).to_have_attribute("data-repository-visible-view", name)

    def assert_detail_ui(self, detail):
        self.pair_ui(self.comparison)
        self.view("diff")
        replay.expect(self.page.locator("pre[data-repository-diff=git]")).to_be_visible()
        assert self.page.locator("pre[data-repository-diff=git]").text_content() == detail["unified_diff"]["text"], "Displayed Git diff differs from the immutable GET/Git oracle"
        for side in ("before", "after"):
            self.view(side)
            value = detail[side]
            if value is None:
                replay.expect(self.page.locator(".repository-file-view")).to_contain_text("Not present")
                replay.expect(self.page.locator("pre[data-repository-source]")).to_have_count(0)
                continue
            text = self.page.locator(f'pre[data-repository-source="{side}"]')
            replay.expect(text).to_be_visible()
            assert text.text_content() == value["text"], f"{side} historical text differs from exact Git-backed excerpt"
            start, end = value["range"]["start"], value["range"]["end"]
            assert self.page.locator(".repository-line-numbers").text_content() == "\n".join(str(i) for i in range(start, end + 1)), "Historical line-number range is wrong"
            panel = self.page.locator(".repository-file-view")
            replay.expect(panel.locator(".repository-code")).to_have_attribute("aria-label", f"{side.title()} historical source, {detail['path']}, lines {start} to {end}")
            metadata = panel.locator("details")
            if metadata.get_attribute("open") is None:
                metadata.locator(":scope > summary").click()
            for identity in (detail["base" if side == "before" else "head"]["commit"], value["blob"], value["file_sha256"], value["snippet_sha256"]):
                replay.expect(metadata).to_contain_text(identity)
        assert not any(item["path"] == "/api/repository/source" for item in self.requests), "Historical source incorrectly used the live-source endpoint"

    def empty_entry(self):
        entry = super().entry()
        self.tab("review")
        self.navigation_action("click", '[data-tab="review"]')
        local = self.page.locator("#comparison-code-tab")
        replay.expect(local).to_be_visible()
        local.click()
        self.navigation_action("click", "#comparison-code-tab")
        replay.expect(self.page.locator('[data-tab="review"]')).to_have_attribute("aria-selected", "true")
        replay.expect(local).to_have_attribute("aria-selected", "true")
        replay.expect(self.page.locator("#repository-changes")).to_be_visible()
        replay.expect(self.page.locator("#review")).to_be_hidden()
        self.status("empty")
        replay.expect(self.page.locator(".repository-review")).to_contain_text("Choose two immutable revisions")
        assert not any(item["path"].startswith("/api/repository/change") for item in self.requests), "Code changes fetched a fabricated default pair"
        assert self.oracle("cases") == [], "Read-only code comparison started with a case"
        return entry

    def inventory(self):
        comparison = self.accept_pair()
        self.show_files()
        actual = self.page.locator("[data-repository-path]").evaluate_all("nodes=>nodes.map(node=>({path:node.dataset.repositoryPath,text:node.textContent}))")
        assert [item["path"] for item in actual] == [item["path"] for item in comparison["files"]] == list(PUBLIC_PATHS)
        replay.expect(self.page.locator(".repository-coverage")).to_contain_text("9 changed paths · 8 displayed · 1 excluded")
        replay.expect(self.page.locator(".repository-status")).to_contain_text("PARTIAL")
        replay.expect(self.page.locator("pre[data-repository-source]")).to_have_count(0)
        return {"coverage": comparison["coverage"], "changed_syntax": CHANGED_SITES, "task_syntax": "unchanged", "behavior": "NOT_RUN"}

    def historical_sources(self):
        whole = self.select()
        self.assert_detail_ui(whole)
        visible_refs = self.page.locator("[data-repository-reference]").evaluate_all("nodes=>nodes.map(node=>node.dataset.repositoryReference)")
        assert sorted(visible_refs) == sorted(ref for ref, spec in SYMBOLS.items() if spec[3] == "changed"), "Default syntax filter did not expose exactly the four changed sites"
        selected = self.select(reference=CASES_REF)
        self.assert_detail_ui(selected)
        self.view("syntax")
        panel = self.page.locator(".repository-file-view")
        replay.expect(panel).to_contain_text("does not establish a behavioral change")
        identity = self.page.locator("details[data-repository-selected-reference]")
        replay.expect(identity).to_have_attribute("data-repository-selected-reference", CASES_REF)
        if identity.get_attribute("open") is None:
            identity.locator(":scope > summary").click()
            self.navigation_action("click", "selected syntax identity summary")
        replay.expect(identity.locator("code")).to_have_text(CASES_REF)
        self.view("impact")
        replay.expect(panel).to_contain_text("not a complete impact set")
        for side in ("before", "after"):
            scope = selected["known_impact"][side]
            replay.expect(panel).to_contain_text(scope["status"])
            replay.expect(panel).to_contain_text(scope["captured_source_hash"])
        task = self.select(reference=TASK_REF)
        self.assert_detail_ui(task)
        assert task["before"]["symbol"]["syntax_digest"] == task["after"]["symbol"]["syntax_digest"], "Unchanged task syntax acquired unequal digests"
        replay.expect(self.page.locator("select[data-repository-symbol-filter]")).to_have_value("all")
        self.select(reference=CASES_REF)
        self.view("after")
        return {"path": APP_PATH, "reference": CASES_REF, "comparison_id": selected["comparison_id"],
                "unchanged_reference_reachable_via_all": TASK_REF, "oracle_controls": oracle_negative_controls(self.comparison, selected)}

    def keyboard_absent_side(self):
        added = next(row["path"] for row in self.comparison["files"] if row["status"] == "added")
        self.show_files()
        first = self.page.locator("[data-repository-path]").first
        first.focus()
        self.page.keyboard.press("Home")
        index = PUBLIC_PATHS.index(added)
        for _ in range(index):
            self.page.keyboard.press("ArrowDown")
        replay.expect(self.page.locator("[data-repository-path]").nth(index)).to_be_focused()
        self.page.keyboard.press("Enter")
        self.status("captured-file")
        detail = self.oracle("repository/change/file", base=BASE, head=HEAD, path=added)
        assert_file(self.comparison, detail)
        assert detail["before"] is None and detail["after"]["status"] == "captured", "Fixed added file did not expose absent Before side"
        self.file = detail
        self.assert_detail_ui(detail)
        self.view("before", keyboard=True)
        replay.expect(self.page.locator(".repository-file-view")).to_contain_text("Not present")
        self.select()
        self.select(reference=CASES_REF)
        return {"added_path": added, "keyboard_navigation": True, "before": "not present"}

    def transport_recovery(self):
        old = self.file
        self.view("after")
        self.arm("503", base=HEAD, head=BASE)
        self.submit(HEAD, BASE, "unavailable")
        self.pair_ui(self.comparison)
        replay.expect(self.page.locator("#repository-comparison-status")).to_contain_text("Displaying retained immutable pair")
        replay.expect(self.page.locator("#repository-review [role=alert]")).to_contain_text("QA_TRANSPORT_FAILURE")
        assert self.page.locator('pre[data-repository-source="after"]').text_content() == old["after"]["text"], "Failure lost the accepted historical text"
        self.page.screenshot(path=str(self.out / "retained-after-503.png"), full_page=True)
        reverse = self.accept_pair(HEAD, BASE)
        replay.expect(self.page.locator("pre[data-repository-source]")).to_have_count(0)
        replay.expect(self.page.locator("#repository-review [role=alert]")).to_have_count(0)
        self.select()
        self.select(reference=CASES_REF)
        self.assert_detail_ui(self.file)
        self.accept_pair()
        self.select()
        self.select(reference=CASES_REF)
        return {"refused_status": 503, "retry_pair": reverse["comparison_id"], "old_file_cleared_on_acceptance": True}

    def late_and_invalid_responses(self):
        old = self.file
        self.view("after")
        self.arm("hold", base=HEAD, head=BASE)
        with self.page.expect_request(lambda request: urlsplit(request.url).path == "/api/repository/change"
                                      and parse_qs(urlsplit(request.url).query).get("base") == [HEAD], timeout=60000):
            self.submit(HEAD, BASE, "loading")
        assert len(self.held) == 1, "Expected the matched request to be paused before fetching its genuine response"
        route, _, _, evidence = self.held[0]
        actual = route.fetch(timeout=60000)
        assert actual.status == 200, f"Delayed control requires a real successful GET; got {actual.status}"
        payload = actual.json()
        evidence["actual_body"] = payload
        self.held[0] = (route, actual, payload, evidence)
        self.pair_ui(self.comparison)
        replay.expect(self.page.locator("#repository-comparison-status")).to_contain_text("Displaying retained immutable pair")
        assert self.page.locator('pre[data-repository-source="after"]').text_content() == old["after"]["text"]
        assert len(self.held) == 1, "Expected one actual delayed reverse comparison response"
        self.page.screenshot(path=str(self.out / "retained-while-pending.png"), full_page=True)
        accepted = self.accept_pair()
        route, actual, payload, evidence = self.held.pop()
        with self.page.expect_response(lambda r: urlsplit(r.url).path == "/api/repository/change" and parse_qs(urlsplit(r.url).query).get("base") == [HEAD]):
            route.fulfill(response=actual, body=json.dumps(payload))
        self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        evidence["released_after"] = accepted["comparison_id"]
        self.status("captured")
        self.pair_ui(accepted)
        replay.expect(self.page.locator("pre[data-repository-source]")).to_have_count(0)
        self.arm("wrong-pair", base=HEAD, head=BASE)
        self.submit(HEAD, BASE, "unavailable")
        self.pair_ui(accepted)
        replay.expect(self.page.locator("#repository-review [role=alert]")).to_contain_text("CHANGE_SUBJECT_MISMATCH")
        self.accept_pair()
        self.select()
        for fault in ("wrong-blob", "wrong-range"):
            self.arm(fault, "repository/change/file", base=BASE, head=HEAD, path=APP_PATH, reference=CASES_REF)
            previous = self.file
            self.select(reference=CASES_REF, expected="unavailable-file")
            replay.expect(self.page.locator("#repository-review [role=alert]")).to_contain_text("CHANGE_SUBJECT_MISMATCH")
            self.pair_ui(accepted)
            self.assert_detail_ui(previous)
            self.select(reference=CASES_REF)
            self.assert_detail_ui(self.file)
        return {"late_genuine_response_ignored": True, "corrupt_response_controls": ["wrong-pair", "wrong-blob", "wrong-range"], "limits": "Deliberate local response corruption; not real upstream failures."}

    def keyboard_disclosures(self):
        request_count = len(self.requests)
        source = self.file["after"]["text"]
        observations = []
        for name, details in (("revisions", self.page.locator("#repository-revisions")),
                              ("source-identity", self.page.locator(".repository-file-view details"))):
            summary = details.locator(":scope > summary")
            summary.scroll_into_view_if_needed()
            summary.focus()
            replay.expect(summary).to_be_focused()
            was_open = details.get_attribute("open") is not None
            if was_open:
                self.page.keyboard.press("Enter")
                self.navigation_action("key", name + " summary", "Enter (close)")
                replay.expect(details).not_to_have_attribute("open", "")
            self.page.keyboard.press("Enter")
            self.navigation_action("key", name + " summary", "Enter (open)")
            replay.expect(details).to_have_attribute("open", "")
            replay.expect(summary).to_be_focused()
            if name == "revisions":
                replay.expect(self.page.locator("#repository-base")).to_be_visible()
                assert self.page.locator("#repository-base").input_value() == BASE
                assert self.page.locator("#repository-head").input_value() == HEAD
            else:
                replay.expect(details).to_contain_text(self.file["after"]["blob"])
                replay.expect(details).to_contain_text(self.file["after"]["snippet_sha256"])
            self.page.screenshot(path=str(self.out / (name + "-keyboard-expanded.png")), full_page=True)
            self.page.keyboard.press("Enter")
            self.navigation_action("key", name + " summary", "Enter (close)")
            replay.expect(details).not_to_have_attribute("open", "")
            replay.expect(summary).to_be_focused()
            observations.append({"disclosure": name, "initially_open": was_open, "opened_and_closed_by_keyboard": True})
        assert self.page.locator('pre[data-repository-source="after"]').text_content() == source, "Native disclosures changed accepted source"
        assert len(self.requests) == request_count, "Disclosure-only interaction unexpectedly fetched repository state"
        self.pair_ui(self.comparison)
        return observations

    def source_geometry(self):
        side = self.file["after"]
        observed = self.page.locator('pre[data-repository-source="after"]').evaluate(r"""(pre, expected) => {
            const box=r=>({x:r.x,y:r.y,width:r.width,height:r.height,top:r.top,bottom:r.bottom,left:r.left,right:r.right});
            const clip={top:0,bottom:innerHeight,left:0,right:innerWidth};
            const ancestors=[];
            for(let node=pre.parentElement;node;node=node.parentElement){
                const style=getComputedStyle(node),r=node.getBoundingClientRect();
                if(/auto|scroll|hidden|clip/.test(style.overflowY)){clip.top=Math.max(clip.top,r.top+node.clientTop);clip.bottom=Math.min(clip.bottom,r.top+node.clientTop+node.clientHeight);ancestors.push({tag:node.tagName,id:node.id,className:node.className,rect:box(r),scrollTop:node.scrollTop,clientHeight:node.clientHeight,scrollHeight:node.scrollHeight});}
            }
            const text=pre.firstChild;
            if(!text||text.nodeType!==Node.TEXT_NODE)throw new Error('Expected exact historical source text node');
            const lines=text.textContent.split('\n');if(lines.at(-1)==='')lines.pop();
            let offset=0;
            const lineBoxes=lines.map((line,index)=>{
                const range=document.createRange();range.setStart(text,offset);range.setEnd(text,offset+line.length);
                const rect=range.getBoundingClientRect();offset+=line.length+1;
                const number=expected.start+index,selected=number>=expected.symbolStart&&number<=expected.symbolEnd;
                const fullyVisible=rect.height>0&&rect.top>=clip.top-1&&rect.bottom<=clip.bottom+1;
                return {line:number,selected,fullyVisible,rect:box(rect)};
            });
            const region=pre.closest('.repository-code').getBoundingClientRect();
            return {viewport:{width:innerWidth,height:innerHeight},region:box(region),clip,ancestors,
                visibleRegionHeight:Math.max(0,Math.min(region.bottom,clip.bottom)-Math.max(region.top,clip.top)),
                fontSize:parseFloat(getComputedStyle(pre).fontSize),lineHeight:getComputedStyle(pre).lineHeight,
                lines:lineBoxes,selectedLinesFullyVisible:lineBoxes.filter(line=>line.selected).every(line=>line.fullyVisible),
                fullyVisibleLineCount:lineBoxes.filter(line=>line.fullyVisible).length};
        }""", {"start": side["range"]["start"], "symbolStart": side["symbol"]["start_line"], "symbolEnd": side["symbol"]["end_line"]})
        assert observed["visibleRegionHeight"] > 0, "Historical source region has no visible content area"
        assert observed["fontSize"] >= 14, "Historical source font fell below the existing 14px readability setting"
        assert [item["line"] for item in observed["lines"] if item["selected"]] == list(range(side["symbol"]["start_line"], side["symbol"]["end_line"] + 1)), "Geometry observation lost selected function lines"
        return observed

    def accessibility(self):
        self.view("after")
        disclosure_observations = self.keyboard_disclosures()
        observations = []
        for width, height in ((1600, 1100), (1280, 800), (320, 800)):
            self.page.set_viewport_size({"width": width, "height": height})
            self.view("after", keyboard=True)
            self.pair_ui(self.comparison)
            source_panel = self.page.locator(".repository-file-view")
            source_panel.focus()
            self.page.keyboard.press("Control+Home")
            self.navigation_action("key", ".repository-file-view", "Control+Home")
            self.page.wait_for_function("()=>document.querySelector('.repository-file-view').scrollTop===0")
            geometry = self.source_geometry()
            if width >= 1280:
                assert geometry["selectedLinesFullyVisible"], {"check": "selected-function-vertical-visibility", "geometry": geometry}
            assert self.page.locator('pre[data-repository-source="after"]').text_content() == self.file["after"]["text"]
            bounds = self.page.evaluate("({body:document.body.scrollWidth,document:document.documentElement.scrollWidth,viewport:innerWidth})")
            assert max(bounds["body"], bounds["document"]) <= width + 1, bounds
            self.page.screenshot(path=str(self.out / f"historical-source-{width}.png"), full_page=True)
            scroll = self.page.locator(".repository-code")
            before_scroll = scroll.evaluate("node=>({left:node.scrollLeft,width:node.clientWidth,total:node.scrollWidth})")
            if before_scroll["total"] > before_scroll["width"] + 1:
                scroll.focus()
                direction = "ArrowRight" if before_scroll["left"] + before_scroll["width"] < before_scroll["total"] - 1 else "ArrowLeft"
                self.page.keyboard.press(direction)
                self.page.wait_for_function("previous=>document.querySelector('.repository-code').scrollLeft!==previous", arg=before_scroll["left"])
            observations.append({"viewport": [width, height], "bounds": bounds, "keyboard_source_scroll": before_scroll, "source_geometry": geometry})
        self.page.set_viewport_size({"width": 1600, "height": 1100})
        axe = []
        for name in ("diff", "after"):
            self.view(name, keyboard=True)
            audit = replay.Axe.from_file(replay.AXE_FILE_PATH).run(self.page, options={
                "runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]},
                "resultTypes": ["violations", "incomplete"],
            }).response
            axe.append({"view": name, "result": audit})
        write_json(self.out / "axe-repository-review.json", axe)
        assert not any(item["result"]["violations"] for item in axe), "Automatic accessibility violations; inspect axe-repository-review.json"
        assert not self.errors and not self.forbidden, {"javascript": self.errors, "forbidden": self.forbidden}
        assert self.oracle("cases") == [], "Immutable review unexpectedly changed case inventory"
        assert not any(item["path"] == "/api/repository/source" for item in self.requests), "Historical review called live source"
        assert all(item["method"] == "GET" for item in self.requests)
        assert not self.controls and not self.held, "An expected negative control was not exercised"
        assert [(item["status"], item["path"]) for item in self.http_errors] == [(503, "/api/repository/change")], self.http_errors
        write_json(self.out / "source-region-geometry.json", {"disclosures": disclosure_observations, "viewports": observations,
            "scope": "Actual vertical clipping; selected function lines must fit at desktop sizes. Narrow source remains keyboard reachable. No HCI budget changed."})
        return {"viewports": observations, "keyboard_disclosures": disclosure_observations, "automatic_violations": 0, "incomplete": sum(len(item["result"]["incomplete"]) for item in axe), "human_study": "NOT_RUN"}


def run_subject():
    subject = subject_identity()
    for name in ("tests/hci/repository_change_review.py", "tests/hci/repository_change_review.md"):
        subject["scope"].append(name)
        subject["files"][name] = file_identity(ROOT, name)
    subject["content_sha256"] = hashlib.sha256(json.dumps({path: item["sha256"] for path, item in subject["files"].items()}, sort_keys=True).encode()).hexdigest()
    return subject


def main():
    if not __debug__:
        emit({"status": "NOT_RUN", "reason": "Python optimization disables assertion oracles"})
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if replay.PREREQUISITE_ERROR:
        emit({"status": "NOT_RUN", "reason": replay.PREREQUISITE_ERROR})
        return 2
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    before = run_subject()
    write_json(out / "subject-before.json", before)
    result = {"schema": "eija.repository-change-browser.v1", "status": "FAIL", "checks": [], "browser_closed": False, "server_closed": False,
              "base": BASE, "head": HEAD, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope": "Immutable read-only historical code comparison, not model or behavior verification.",
              "not_measured": ["human comprehension", "owner operations", "live providers", "behavioral equivalence", "arbitrary repositories", "live checkout mutation"]}
    review = endpoint = None
    try:
        with replay.disposable_server() as base, replay.sync_playwright() as playwright:
            parsed = urlsplit(base)
            endpoint = (parsed.hostname, parsed.port)
            browser = playwright.chromium.launch(headless=True)
            result["browser_version"] = browser.version
            try:
                context = browser.new_context(viewport={"width": 1600, "height": 1100}, reduced_motion="reduce")
                page = context.new_page()
                page.set_default_timeout(60000)
                review = RepositoryReview(page, out, base)
                for name, action in (("empty-readonly-entry", review.empty_entry), ("immutable-inventory", review.inventory),
                    ("exact-historical-source", review.historical_sources), ("keyboard-absent-side", review.keyboard_absent_side),
                    ("transport-failure-retry", review.transport_recovery), ("late-and-corrupt-response-identity", review.late_and_invalid_responses),
                    ("responsive-accessibility", review.accessibility)):
                    review.step(name, action)
                    emit({"id": name, "status": "PASS"})
                result["status"] = "PASS"
            finally:
                try:
                    if review is not None:
                        review.page.screenshot(path=str(out / "final.png"), full_page=True)
                finally:
                    try:
                        if review is not None:
                            for route, _, _, _ in review.held:
                                with contextlib.suppress(replay.BrowserError):
                                    route.abort()
                    finally:
                        browser.close()
                        result["browser_closed"] = True
    except Exception as error:
        result["status"] = "FAIL"
        result["error"] = {"type": type(error).__name__, "message": str(error).replace(replay.TEST_CAPABILITY, "[test-capability]"),
                           "traceback": traceback.format_exc().replace(replay.TEST_CAPABILITY, "[test-capability]")}
    finally:
        if endpoint is not None:
            with socket.socket() as probe:
                probe.settimeout(0.2)
                result["server_closed"] = probe.connect_ex(endpoint) != 0
        if review is not None:
            result.update(checks=review.checks, failed_stage=review.stage if result["status"] != "PASS" else None,
                          requests=review.requests, http_errors=review.http_errors, javascript_errors=review.errors,
                          forbidden_attempts=review.forbidden, navigation_actions=review.navigation_actions)
            write_json(out / "authoritative-get-oracles.json", review.oracles)
            write_json(out / "negative-controls.json", review.injected)
        after = run_subject()
        write_json(out / "subject-after.json", after)
        result["subject_preservation"] = compare_subjects(before, after)
        result["subject_content_sha256"] = before["content_sha256"]
        if result["subject_preservation"]["status"] != "UNCHANGED" or not result["browser_closed"] or not result["server_closed"]:
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {p.relative_to(out).as_posix(): {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                                  for p in sorted(out.rglob("*")) if p.is_file()})
    emit({key: result.get(key) for key in ("status", "browser_closed", "server_closed", "subject_preservation")})
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
