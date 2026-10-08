"""Bounded real-revision proof of failed/busy navigation identity; no owner actions.

Run only against separately exported, manifest-verified copies of the fixed pair.
The probe controls transport faults, never browser application globals or successful data.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import socket
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from unittest.mock import patch

from playwright.sync_api import expect, sync_playwright

from eija_studio.adapters.repository_changes import _git_read, _tree, _validate_root
from eija_studio.domain.models import fingerprint
from quality.hci import server as server_harness
from self_dogfood_replay import Review
from self_dogfood_subject import dependencies, excluded_path, file_identity

PAIR = {"base": "9c22d425ee33e52980a95b33330babec43c6aa59", "head": "c666b6bb76905c0c9bd03e81cac0922136c4cf3e"}
SCOPES = ("src", "packs", "pyproject.toml")
PACK = "packs/eija-review-slice"
APP = "src/eija_studio/resources/web/app.js"
MAX_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES = 3000, 8 * 1024 * 1024, 64 * 1024 * 1024
REQUESTS = {"A": "Navigation proof A: retain this draft when navigation fails.",
            "B": "Navigation proof B: a different draft destination."}
POLICY = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-src 'self'; "
          "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
CONDITIONS = {"viewport": {"width": 1600, "height": 1000}, "device_scale_factor": 1,
              "reduced_motion": "reduce", "locale": "en-AU", "timezone_id": "Australia/Sydney",
              "bypass_csp": False}
PRIMARY = ("failed-dropdown-retains-current-case", "busy-dropdown-retains-current-case")
CONTROLS = ("successful_retry", "successful_switch_after_busy")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def identity_matches(observed, case_id, request):
    return (observed["dropdown"] == case_id and observed["title"] == request
            and case_id[:10] in observed["case_label"] and observed["list_count"] == 1
            and observed["list_title"] == request and observed["stage"] == "DRAFT")


def in_scope(name):
    return name == "pyproject.toml" or name.startswith(("src/", "packs/"))


def export_root(value):
    path = Path(value)
    info = path.lstat()
    require(path.is_absolute() and path.is_dir() and not path.is_symlink()
            and not getattr(info, "st_file_attributes", 0) & 0x400, "EXPORT_ROOT_INVALID")
    return path.resolve(strict=True)


def read_manifest(path):
    require(path.is_file() and path.stat().st_size <= 2 * 1024 * 1024, "EXPORT_MANIFEST_LIMIT")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(value.get("schema") == "eija.navigation-pair-exports.v1", "EXPORT_MANIFEST_SCHEMA")
    require(value.get("scope") == list(SCOPES) and value.get("pack") == PACK, "EXPORT_SCOPE_MISMATCH")
    repository = Path(value["repository_root"]).resolve(strict=True)
    _validate_root(repository)
    roots = [export_root(value[side]["root"]) for side in PAIR]
    require(roots[0] != roots[1] and not roots[0].is_relative_to(roots[1])
            and not roots[1].is_relative_to(roots[0]), "EXPORT_ROOTS_OVERLAP")
    require(all(root != repository and not root.is_relative_to(repository) for root in roots), "EXPORT_IS_SHARED_CHECKOUT")
    return value, repository


def validate_export(repository, spec, expected_commit):
    """Bind exported bytes to local Git objects, not merely a caller's commit label."""
    require(spec.get("commit") == expected_commit, "WRONG_IMMUTABLE_REVISION")
    tree = _tree(repository, expected_commit)
    require(spec.get("tree") == tree.tree, "WRONG_IMMUTABLE_TREE")
    expected = {name: obj for name, obj in tree.inventory.items() if in_scope(name)}
    require(0 < len(expected) <= MAX_FILES and set(spec.get("files", {})) == set(expected), "EXPORT_INVENTORY_MISMATCH")
    root = export_root(spec["root"])
    actual = set()
    for directory, directories, filenames in os.walk(root, followlinks=False):
        require(all(not (Path(directory) / part).is_symlink()
                    and not getattr((Path(directory) / part).lstat(), "st_file_attributes", 0) & 0x400
                    for part in directories), "EXPORT_LINK_DIRECTORY")
        for name in filenames:
            actual.add((Path(directory) / name).relative_to(root).as_posix())
            require(len(actual) <= MAX_FILES, "EXPORT_FILE_LIMIT")
    require(actual == set(expected), "UNEXPECTED_OR_MISSING_EXPORT_FILE")
    total, files = 0, {}
    for name, obj in sorted(expected.items()):
        require(excluded_path(name) is None and obj.kind == "blob" and obj.mode in {"100644", "100755"}, "EXPORT_ENTRY_UNSUPPORTED")
        path = root.joinpath(*PurePosixPath(name).parts)
        require(path.lstat().st_size <= MAX_FILE_BYTES, "EXPORT_FILE_BYTE_LIMIT")
        identity = file_identity(root, name)
        total += identity["bytes"]
        require(identity["bytes"] <= MAX_FILE_BYTES and total <= MAX_TOTAL_BYTES, "EXPORT_BYTE_LIMIT")
        with path.open("rb") as stream:
            data = stream.read(MAX_FILE_BYTES + 1)
        require(len(data) <= MAX_FILE_BYTES and hashlib.sha256(data).hexdigest() == identity["sha256"], "EXPORT_CHANGED_DURING_VALIDATION")
        algorithm = "sha1" if len(obj.oid) == 40 else "sha256"
        blob = hashlib.new(algorithm, b"blob " + str(len(data)).encode() + b"\0" + data, usedforsecurity=False).hexdigest()
        expected_identity = identity | {"git_blob": blob}
        require(blob == obj.oid and spec["files"][name] == expected_identity, "EXPORT_BLOB_MISMATCH")
        files[name] = expected_identity
    return {"commit": expected_commit, "tree": tree.tree, "files": files,
            "content_sha256": fingerprint(files), "bytes": total, "scope": list(SCOPES)}


def implementation_identity(subject):
    prefix = "src/eija_studio/"
    files = {name.removeprefix(prefix): row["sha256"] for name, row in subject["files"].items()
             if name.startswith(prefix) and (name.endswith(".py") or name.startswith(prefix + "resources/web/"))}
    return fingerprint(files)


def validate_intake(path, subjects):
    require(path.is_file() and path.stat().st_size <= 4 * 1024 * 1024, "INTAKE_REPORT_LIMIT")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(value.get("schema") == "eija.repository.change.v1", "INTAKE_SCHEMA_MISMATCH")
    for side, commit in PAIR.items():
        require(value[side]["commit"] == commit and value[side]["tree"] == subjects[side]["tree"], "INTAKE_PAIR_MISMATCH")
    row = next(item for item in value["files"] if item["path"] == APP)
    for key, side in (("before", "base"), ("after", "head")):
        require(row[key]["file_sha256"] == subjects[side]["files"][APP]["sha256"], "INTAKE_APP_BYTES_MISMATCH")
    return {"comparison_id": value["comparison_id"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "boundary": "Pair/app bytes linked to source intake; this report adds only the named navigation observations."}


@contextlib.contextmanager
def export_server(root, label):
    """Configure the existing real-CLI harness for a verified export; no new server engine."""
    environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("EIJA_")}
    environment.update({"EIJA_PACK": str(root / PACK), "PYTHONDONTWRITEBYTECODE": "1"})
    with patch.object(server_harness, "ROOT", root), patch.dict(os.environ, environment, clear=True), \
            server_harness.studio_server(label, identity="release", timeout=60) as launch:
        yield launch


class NavigationPair(Review):
    def __init__(self, page, out, launch_url, subject):
        parsed = urlsplit(launch_url)
        self.capability, self.launch_url = parsed.fragment, launch_url
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.subject = subject
        self.fault_path = self.hold_path = self.held_route = None
        self.injected, self.oracles, self.worker_events = [], [], []
        super().__init__(page, out, self.origin + "/")
        page.context.route("**/*", self.route)
        page.context.on("serviceworker", self.record_service_worker)

    def record_service_worker(self, worker):
        self.worker_events.append({"stage": self.stage, "path": urlsplit(worker.url).path})

    def route(self, route):
        request, path = route.request, urlsplit(route.request.url).path
        self.requests.append({"stage": self.stage, "method": request.method, "path": path})
        allowed_create = request.method == "POST" and path == "/api/cases" and self.stage == "fixture-create"
        if request.service_worker is not None or request.headers.get("service-worker") == "script":
            self.forbidden.append({"method": request.method, "path": path, "kind": "service_worker_request"})
            route.abort()
        elif not request.url.startswith(self.origin + "/") or (request.method != "GET" and not allowed_create):
            self.forbidden.append({"method": request.method, "path": path})
            route.abort()
        elif path == self.hold_path:
            self.hold_path, self.held_route = None, route
        elif path == self.fault_path:
            self.fault_path = None
            self.injected.append({"stage": self.stage, "path": path, "status": 503})
            route.fulfill(status=503, content_type="application/json", body=json.dumps({
                "code": "PAIR_CASE_UNAVAILABLE", "message": "Controlled navigation proof: case read failed once."}))
        else:
            route.continue_()

    def api_get(self, path):
        response = self.page.context.request.get(self.base + "api/" + path, headers={"Authorization": "Bearer " + self.capability})
        require(response.status == 200, "INDEPENDENT_GET_FAILED")
        value = response.json()
        self.oracles.append({"stage": self.stage, "path": "/api/" + path, "body": value})
        return value

    def entry(self):
        require(not self.page.context.service_workers, "FRESH_CONTEXT_HAS_SERVICE_WORKER")
        response = self.page.goto(self.launch_url)
        require(response is not None and response.status == 200, "ENTRY_FAILED")
        require(response.headers.get("content-security-policy") == POLICY, "NORMAL_CSP_REQUIRED")
        expect(self.page.locator("#connection")).to_contain_text("offline", timeout=60000)
        self.settled()
        expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
        status = self.api_get("status")
        require(status["provider"] == "offline" and not status["network_enabled"]
                and not status["provider_networked"] and not status["trusted_fixture"], "NORMAL_OFFLINE_IDENTITY_REQUIRED")
        require(status["pack"]["id"] == "eija-review-slice", "SELF_DOGFOOD_PACK_REQUIRED")
        served = self.page.context.request.get(self.base + "assets/app.js")
        require(served.status == 200 and hashlib.sha256(served.body()).hexdigest() == self.subject["files"][APP]["sha256"], "SERVED_APP_IDENTITY_MISMATCH")
        self.page.screenshot(path=str(self.out / "entry.png"), full_page=True)
        return {"csp": POLICY, "status": status, "served_app_sha256": self.subject["files"][APP]["sha256"],
                "implementation_binding": {"basis": "Verified export bytes and configured CLI launch root; app.js additionally checked over HTTP",
                                           "expected_export_implementation_sha256": implementation_identity(self.subject),
                                           "http_packet_implementation_subject": "NOT_EXPOSED_IN_DRAFT"}}

    def create_draft(self, label):
        self.stage = "fixture-create"
        self.page.locator("#start-intent").click()
        self.page.locator("#request").fill(REQUESTS[label])
        with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path == "/api/cases") as pending:
            self.page.locator("#create").click()
        require(pending.value.status == 200, "DRAFT_CREATION_FAILED")
        case_id = pending.value.json()["id"]
        self.settled()
        view = self.api_get("cases/" + case_id)
        require(view["case"]["request"] == REQUESTS[label] and view["case"]["stage"] == "DRAFT"
                and view["case"]["candidate"] is None, "FIXTURE_IS_NOT_UNSELECTED_DRAFT")
        packet = view["packet"]
        require(packet["status"] == "BLOCKED" and packet["eligible"] is False
                and packet["blockers"] == ["MEANING_REQUIRED"] and "subject" not in packet, "DRAFT_PACKET_CONTRACT_MISMATCH")
        return case_id

    def identity(self):
        selected = self.page.locator('#case-list button[aria-current="true"]')
        return {"dropdown": self.page.locator("#case-switcher").input_value(),
                "title": self.page.locator("#case-title").inner_text(),
                "case_label": self.page.locator("#case-id").inner_text(),
                "list_count": selected.count(), "list_title": selected.get_attribute("title") if selected.count() == 1 else None,
                "stage": self.page.locator("#case-stage").inner_text()}

    def matches(self, observed, label):
        return identity_matches(observed, self.ids[label], REQUESTS[label])

    def reveal_explorer(self):
        """Both pinned revisions expose the Explorer toggle directly in the title bar."""
        toggle = self.page.locator("#toggle-explorer")
        if toggle.get_attribute("aria-expanded") != "true":
            toggle.click()
            self.navigation_action("click", "#toggle-explorer")
        expect(self.page.locator("#explorer")).to_be_visible()

    def navigate(self, label, control="dropdown"):
        case_id = self.ids[label]
        if control == "list":
            self.open_explorer_disclosure("#explorer details.case-explorer")
        with self.page.expect_response(lambda r: r.request.method == "GET" and urlsplit(r.url).path == "/api/cases/" + case_id) as pending:
            if control == "list":
                self.page.locator("#case-list button").filter(has_text=REQUESTS[label]).click()
            else:
                self.page.locator("#case-switcher").select_option(case_id)
        require(pending.value.status == 200, "CONTROL_NAVIGATION_GET_FAILED")
        self.settled()
        require(self.matches(self.identity(), label), "CONTROL_NAVIGATION_IDENTITY_FAILED")

    def snapshots(self):
        return {label: self.api_get("cases/" + case_id) for label, case_id in self.ids.items()}

    def no_navigation_writes(self, marker):
        return all(row["method"] == "GET" for row in self.requests[marker:])

    def failed_dropdown(self):
        self.stage = PRIMARY[0]
        self.navigate("A")
        before, marker = self.snapshots(), len(self.requests)
        fault_path = "/api/cases/" + self.ids["B"]
        self.fault_path = fault_path
        with self.page.expect_response(lambda r: r.request.method == "GET" and urlsplit(r.url).path == fault_path) as pending:
            self.page.locator("#case-switcher").select_option(self.ids["B"])
        require(pending.value.status == 503 and self.fault_path is None, "DESIGNATED_FAILURE_NOT_OBSERVED")
        self.settled()
        expect(self.page.locator("#notice")).to_contain_text("PAIR_CASE_UNAVAILABLE")
        observed = self.identity()
        require(self.snapshots() == before and self.no_navigation_writes(marker), "FAILURE_CHANGED_PERSISTED_CASES")
        self.page.screenshot(path=str(self.out / "failed-dropdown.png"), full_page=True)
        return {"id": PRIMARY[0], "passes": self.matches(observed, "A"), "observed": observed,
                "expected": {"active_case": self.ids["A"], "request": REQUESTS["A"], "stage": "DRAFT"},
                "state_unchanged": True, "write_count": 0}

    def busy_dropdown(self):
        self.stage = PRIMARY[1]
        self.navigate("A")
        before = self.snapshots()
        self.reveal_explorer()
        marker = len(self.requests)
        self.hold_path = "/api/doctor"
        with self.page.expect_request(lambda r: r.method == "GET" and urlsplit(r.url).path == "/api/doctor"):
            self.page.locator("#doctor").click()
        expect(self.page.locator("body")).to_have_attribute("aria-busy", "true")
        require(self.held_route is not None, "DESIGNATED_BUSY_GET_NOT_HELD")
        self.page.locator("#case-switcher").select_option(self.ids["B"])
        observed = self.identity()
        require(self.requests[marker:] == [{"stage": self.stage, "method": "GET", "path": "/api/doctor"}], "BUSY_ACTION_STARTED_NAVIGATION")
        require(self.snapshots() == before, "BUSY_ACTION_CHANGED_PERSISTED_CASES")
        self.page.screenshot(path=str(self.out / "busy-dropdown.png"), full_page=True)
        # The successful control response is the real held request, not a synthetic body.
        self.held_route.continue_()
        self.held_route = None
        self.settled()
        require(self.requests[marker:] == [{"stage": self.stage, "method": "GET", "path": "/api/doctor"}], "BUSY_COMPLETION_QUEUED_NAVIGATION")
        require(self.snapshots() == before and self.no_navigation_writes(marker), "BUSY_COMPLETION_CHANGED_CASES")
        return {"id": PRIMARY[1], "passes": self.matches(observed, "A") and self.matches(self.identity(), "A"),
                "observed": observed, "after_completion": self.identity(),
                "expected": {"active_case": self.ids["A"], "request": REQUESTS["A"], "stage": "DRAFT"},
                "state_unchanged": True, "write_count": 0}

    def run(self):
        entry = self.entry()
        self.ids = {label: self.create_draft(label) for label in ("A", "B")}
        require(len(set(self.ids.values())) == 2, "FIXTURE_CASE_IDS_MUST_DIFFER")
        self.page.screenshot(path=str(self.out / "drafts-created.png"), full_page=True)
        failed = self.failed_dropdown()
        self.stage = "successful-retry-control"
        self.navigate("B", control="list")
        retry = self.identity()
        busy = self.busy_dropdown()
        self.stage = "successful-switch-after-busy-control"
        self.navigate("B", control="list")
        require(not self.worker_events and not self.page.context.service_workers, "SERVICE_WORKER_OBSERVED")
        require(not self.errors and not self.forbidden, "BROWSER_OR_FORBIDDEN_ACTION_FAILURE")
        require(self.http_errors == self.injected and len(self.injected) == 1, "UNEXPECTED_HTTP_ERROR")
        posts = [row for row in self.requests if row["method"] != "GET"]
        require(len(posts) == 2 and all(row["path"] == "/api/cases" for row in posts), "ONLY_TWO_DRAFT_CREATIONS_ALLOWED")
        return {"status": "OBSERVED", "entry": entry, "cases": self.ids, "oracles": [failed, busy],
                "controls": {"successful_retry": {"passes": True, "control": "case_list", "observed": retry},
                             "successful_switch_after_busy": {"passes": True, "control": "case_list", "observed": self.identity()}},
                "requests": self.requests, "injected": self.injected, "http_errors": self.http_errors,
                "javascript_errors": self.errors, "forbidden_attempts": self.forbidden,
                "service_worker_events": self.worker_events, "active_service_worker_count": len(self.page.context.service_workers),
                "owner_action_count": 0, "provider_call_count": 0}


def run_side(browser, spec, subject, out, side):
    root = Path(spec["root"]).resolve(strict=True)
    out.mkdir()
    result, review, address = {"status": "NOT_RUN", "context_closed": False, "server_closed": False}, None, None
    try:
        with export_server(root, "navigation-pair-" + side) as launch:
            parsed = urlsplit(launch)
            address = parsed.hostname, parsed.port
            context = browser.new_context(**CONDITIONS)
            try:
                page = context.new_page()
                page.set_default_timeout(30000)
                review = NavigationPair(page, out, launch, subject)
                result.update(review.run())
            except Exception:
                try:
                    page.screenshot(path=str(out / "failure.png"), full_page=True)
                    result["failure_screenshot"] = "failure.png"
                except Exception:
                    result["failure_screenshot"] = "UNAVAILABLE"
                raise
            finally:
                context.close()
                result["context_closed"] = True
    except Exception as error:
        result["status"] = "INFRASTRUCTURE_FAILURE"
        message = str(error)
        if review is not None:
            message = message.replace(review.capability, "[disposable-capability]")
        result["error"] = {"type": type(error).__name__, "message": message[:1500]}
    finally:
        if address is not None:
            with socket.socket() as probe:
                probe.settimeout(0.2)
                result["server_closed"] = probe.connect_ex(address) != 0
        if review is not None:
            write_json(out / "independent-get-observations.json", review.oracles)
            result["diagnostics"] = {"stage": review.stage, "requests": review.requests,
                                     "http_errors": review.http_errors, "injected": review.injected,
                                     "javascript_errors": review.errors, "forbidden_attempts": review.forbidden,
                                     "service_worker_events": review.worker_events}
        if not result["context_closed"] or not result["server_closed"]:
            result["status"] = "INFRASTRUCTURE_FAILURE"
        write_json(out / "result.json", result)
    return result


def evaluate_pair(results):
    if set(results) != set(PAIR) or any(result["status"] != "OBSERVED" for result in results.values()):
        return {"status": "NOT_PROVEN", "reason": "Both sides must complete the same scenario and controls."}
    records = {side: {row["id"]: row for row in result["oracles"]} for side, result in results.items()}
    if any(set(rows) != set(PRIMARY) for rows in records.values()):
        return {"status": "NOT_PROVEN", "reason": "Every named property must have an observation on both sides."}
    if any(set(result["controls"]) != set(CONTROLS)
           or not all(control["passes"] for control in result["controls"].values()) for result in results.values()):
        return {"status": "NOT_PROVEN", "reason": "Successful retry/switch controls must pass on both sides."}
    for name in PRIMARY:
        old, new = records["base"][name], records["head"][name]
        expected_counterexample = old["observed"]["dropdown"] == results["base"]["cases"]["B"]
        expected_counterexample &= old["observed"]["title"] == REQUESTS["A"]
        expected_counterexample &= old["observed"]["list_title"] == REQUESTS["A"]
        expected_counterexample &= results["base"]["cases"]["A"][:10] in old["observed"]["case_label"]
        expected_counterexample &= old["observed"]["list_count"] == 1 and old["observed"]["stage"] == "DRAFT"
        after_matches = identity_matches(new["observed"], results["head"]["cases"]["A"], REQUESTS["A"])
        if name == PRIMARY[1]:
            after_matches &= identity_matches(new["after_completion"], results["head"]["cases"]["A"], REQUESTS["A"])
        if old["passes"] or not expected_counterexample or not new["passes"] or not after_matches:
            return {"status": "NOT_PROVEN", "reason": "The designated before-fail/after-pass oracle was not met.", "oracle": name}
    return {"status": "PASS", "scope": "Two displayed-navigation identity properties in the specified synthetic transport conditions.",
            "before": "Designated dropdown/header mismatch observed for both properties", "after": "Both properties and successful controls passed"}


def helper_subject():
    return {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "server_helper_sha256": hashlib.sha256(Path(server_harness.__file__).read_bytes()).hexdigest(),
            "review_helper_sha256": hashlib.sha256(Path(sys.modules[Review.__module__].__file__).read_bytes()).hexdigest(),
            "subject_helper_sha256": hashlib.sha256(Path(sys.modules[file_identity.__module__].__file__).read_bytes()).hexdigest(),
            "git_comparison_adapter_sha256": hashlib.sha256(Path(sys.modules[_git_read.__module__].__file__).read_bytes()).hexdigest(),
            "git_capture_adapter_sha256": hashlib.sha256(Path(sys.modules["eija_studio.adapters.repository_capture"].__file__).read_bytes()).hexdigest(),
            "process_adapter_sha256": hashlib.sha256(Path(sys.modules["eija_studio.adapters.providers.process"].__file__).read_bytes()).hexdigest(),
            "canonical_identity_module_sha256": hashlib.sha256(Path(sys.modules[fingerprint.__module__].__file__).read_bytes()).hexdigest(),
            "python": sys.version, "dependencies": dependencies(), "conditions": CONDITIONS}


def preservation(repository, manifest, subjects, harness):
    try:
        after = {side: validate_export(repository, manifest[side], commit) for side, commit in PAIR.items()}
        return {"source_after": after, "source_preservation": "UNCHANGED" if after == subjects else "CHANGED",
                "harness_preservation": "UNCHANGED" if helper_subject() == harness else "CHANGED"}
    except Exception as error:
        return {"source_preservation": "UNVERIFIED", "harness_preservation": "UNVERIFIED",
                "preservation_error": {"type": type(error).__name__, "message": "Export/harness identity could not be confirmed after the run."}}


def git_authors(repository):
    result = {}
    for side, commit in PAIR.items():
        author, date = _git_read(repository, "show", "-s", "--format=%an%x00%aI", commit).decode().strip().split("\0", 1)
        result[side] = {"name": author[:200], "date": date[:80], "source": "Git commit author fields; not agent attribution"}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exports", required=True, type=Path)
    parser.add_argument("--intake", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--browser-executable", type=Path, help="Explicit installed Chromium or headless-shell binary; the exact launched executable is hashed")
    args = parser.parse_args()
    require(__debug__, "PYTHON_OPTIMIZATION_UNSUPPORTED")
    manifest, repository = read_manifest(args.exports)
    subjects = {side: validate_export(repository, manifest[side], commit) for side, commit in PAIR.items()}
    intake = validate_intake(args.intake, subjects)
    out = args.out.resolve()
    require(all(not out.is_relative_to(Path(manifest[side]["root"]).resolve()) for side in PAIR), "OUTPUT_INSIDE_EXPORT")
    out.mkdir(parents=True, exist_ok=False)
    run_identity = helper_subject()
    report = {"schema": "eija.navigation-pair-observation.v1", "utc": datetime.now(UTC).isoformat(),
              "pair": PAIR, "identity": run_identity, "intake": intake,
              "service_worker_policy": "Browser default in fresh contexts; worker registration requests, worker events or active workers fail the proof. Playwright block init-script was independently shown to fault on an empty sandboxed frame.",
              "exports_manifest_sha256": hashlib.sha256(args.exports.read_bytes()).hexdigest(),
              "source_before": subjects, "browser_closed": False, "results": {}, "status": "NOT_PROVEN",
              "provenance": {"declared_agent_assistance": manifest.get("declared_agent_assistance", "NOT_PROVIDED"),
                             "git_author_metadata": git_authors(repository),
                             "boundary": "Git author metadata does not establish AI authorship; assistance is a separate declaration."},
              "not_established": ["Preview-instance retention or clearing", "All four changed sites are behaviorally correct",
                                  "Human comprehension improvement", "Complete source/model conformance", "Live provider or owner behavior"]}
    try:
        with sync_playwright() as playwright:
            binary = (args.browser_executable or Path(playwright.chromium.executable_path)).resolve()
            require(binary.is_file(), "CHROMIUM_NOT_INSTALLED")
            with binary.open("rb") as stream:
                binary_sha = hashlib.file_digest(stream, "sha256").hexdigest()
            browser = playwright.chromium.launch(headless=True, executable_path=str(binary))
            try:
                report["browser"] = {"version": browser.version, "engine": "chromium", "playwright": version("playwright"),
                                     "executable_name": binary.name, "executable_sha256": binary_sha, "headless": True}
                for side in PAIR:
                    report["results"][side] = run_side(browser, manifest[side], subjects[side], out / side, side)
            finally:
                browser.close()
                report["browser_closed"] = True
        report["evaluation"] = evaluate_pair(report["results"])
        report["status"] = report["evaluation"]["status"]
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)[:1500]}
    finally:
        report.update(preservation(repository, manifest, subjects, run_identity))
        if report["source_preservation"] != "UNCHANGED" or report["harness_preservation"] != "UNCHANGED" or not report["browser_closed"]:
            report["status"] = "NOT_PROVEN"
        write_json(out / "result.json", report)
        artifacts = {path.relative_to(out).as_posix(): {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
                     for path in sorted(out.rglob("*")) if path.is_file()}
        write_json(out / "artifact-manifest.json", artifacts)
    sys.stdout.write(json.dumps({"status": report["status"], "out": str(out)}) + "\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
