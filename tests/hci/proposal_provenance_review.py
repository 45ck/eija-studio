"""Disposable proposal provenance and outcome replay; offline fixture only."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import socket
import sys
import time
import traceback
from collections import Counter
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load_runtime(repo):
    sys.path[:0] = [str(repo / "tests/hci"), str(repo / "src"), str(repo)]
    runtime = importlib.import_module("runtime_evidence_review")
    replay = importlib.import_module("self_dogfood_replay")
    domain = importlib.import_module("eija_studio.domain.models")
    subject = importlib.import_module("self_dogfood_subject")
    return runtime, replay, domain.DomainError, subject.compare_subjects


def fixture_type(DomainError):
    class OfflineFixture:
        """Delegate real pack answers; one named refusal and missing-model control."""
        def __init__(self):
            self.calls = []
            self.counts = Counter()

        def __call__(self, studio):
            assert studio.provider.name == "offline" and studio.provider.networked is False
            assert studio.identity_provider()["trusted_fixture"] is False
            delegate, fixture = studio.provider, self

            class ControlledOffline:
                name, networked = "offline", False

                def doctor(self):
                    return delegate.doctor()

                def propose(self, request, model):
                    fixture.counts[request] += 1
                    index = fixture.counts[request]
                    control = "refusal" if "[case-a]" in request and index == 2 else (
                        "missing-model" if "[case-b]" in request else "real-offline")
                    fixture.calls.append({"request_hash": digest(request), "call": index, "control": control})
                    if control == "refusal":
                        raise DomainError("SYNTHETIC_PROVIDER_REFUSED", "Named offline regression fixture refusal.")
                    answer = delegate.propose(request, model)
                    assert answer.provider == "offline" and answer.live is False and answer.model == "fixture-v1"
                    return replace(answer, model="") if control == "missing-model" else answer

            studio.provider = ControlledOffline()
    return OfflineFixture


def review_type(runtime, replay):
    class ProposalReview(runtime.RuntimeReview):
        def __init__(self, page, out, base):
            super().__init__(page, out, base)
            self.mode = None
            self.held_proposal = None
            self.get_fault = None
            self.proposals = []
            self.posts = []
            self.controls = []
            self.external = []
            self.snapshots = []
            self.request_focus = []
            self.expected_http = []
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
                allowed = request.method == "POST" and (path == "/api/cases" or path.endswith("/propose"))
                if not allowed:
                    self.forbidden.append(path)
                    route.abort()
                    return
                body = request.post_data_json
                redacted = ({"request_hash": digest(body["request"]), "request_text": "[synthetic fixture redacted]"}
                            if path == "/api/cases" else {"expected_version": body["expected_version"], "consent": body["consent"]})
                self.posts.append({"stage": self.stage, "method": request.method, "path": path, "body": redacted})
            if request.method == "POST" and path.endswith("/propose"):
                assert set(request.post_data_json) == {"expected_version", "consent"}
                assert request.post_data_json["consent"] is False
                mode, self.mode = self.mode, None
                if mode:
                    self.requests.append({"stage": self.stage, "method": request.method, "path": path})
                    record = {"mode": mode, "path": path, "request": request.post_data_json}
                    self.controls.append(record)
                    if mode == "hold":
                        self.held_proposal = route
                    elif mode == "abort-before-server":
                        route.abort("failed")
                    else:
                        actual = route.fetch()
                        assert actual.status == 200, "Post-commit fault requires real accepted offline proposal"
                        record["actual_acknowledgement"] = actual.json()
                        if mode == "abort-after-commit":
                            route.abort("failed")
                        elif mode == "invalid-after-commit":
                            route.fulfill(status=200, content_type="application/json", body="{ interrupted proposal")
                        else:
                            raise AssertionError("Unknown proposal fault")
                    return
            if request.method == "GET" and path == self.get_fault:
                self.get_fault = None
                self.requests.append({"stage": self.stage, "method": request.method, "path": path})
                self.expected_http.append((503, path))
                bootstrap = self.stage.startswith("failed-bootstrap-")
                self.controls.append({"mode": "bootstrap-503" if bootstrap else "refresh-503", "path": path})
                route.fulfill(status=503, content_type="application/json", body=json.dumps({
                    "code": "SYNTHETIC_BOOTSTRAP_UNAVAILABLE" if bootstrap else "SYNTHETIC_PROPOSAL_REFRESH_UNAVAILABLE",
                    "message": "Named disposable bootstrap failure." if bootstrap else "Named disposable refresh failure."}))
                return
            super().route(route)

        def response(self, response):
            super().response(response)
            path = urlsplit(response.url).path
            if response.request.method == "POST" and path.endswith("/propose"):
                try:
                    body = response.json()
                except Exception:
                    body = {"response": "invalid JSON retained as a named transport control"}
                self.proposals.append({"path": path, "status": response.status, "body": body})

        def no_authority(self, view, status):
            case = view["case"]
            assert case["candidate"] is None and case["selected_meaning"] is None
            assert case["selected_by"] is None and case["decision"] is None and case["receipts"] == []
            assert case["transactions"] == [] and case["redo_transactions"] == [] and case["layout"] == {}
            assert view["observations"]["instances"] == [] and view["observations"]["outbox"] == []
            # No selected candidate has a deliberately minimal blocked packet.
            # Source trust is a separate status fact, not a candidate-less blocker.
            assert view["packet"]["eligible"] is False
            assert view["packet"] == {"eligible": False, "status": "BLOCKED", "blockers": ["MEANING_REQUIRED"],
                                      "human_understanding": "UNKNOWN", "blocked_meanings": []}
            assert status["trusted_fixture"] is False
            replay.expect(self.page.locator("#source-status")).to_be_visible()
            replay.expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
            replay.expect(self.page.locator("#options .selected")).to_have_count(0)
            for selector in ("#verify", "#approve", "#apply", "#reset"):
                replay.expect(self.page.locator(selector)).to_be_disabled()

        def create_case(self, marker):
            self.page.set_viewport_size({"width": 1280, "height": 900})
            self.page.locator("#start-intent").click()
            text = marker + " Show the optional saved candidate path in EIJA's review journey."
            self.page.locator("#request").fill(text)
            with self.page.expect_response(lambda r: r.request.method == "POST" and urlsplit(r.url).path == "/api/cases") as pending:
                self.page.locator("#create").click()
            self.case_id = pending.value.json()["id"]
            self.settled()
            self.tab("change")
            view = self.view()
            assert view["case"]["request"] == text and view["case"]["version"] == 0
            self.assert_provenance(view)
            replay.expect(self.page.locator("#propose")).to_be_enabled()
            return self.case_id

        def phase(self, status):
            region = self.page.locator("#proposal-activity")
            replay.expect(region).to_have_attribute("data-status", status)
            replay.expect(region).to_have_attribute("data-case-id", self.case_id)
            replay.expect(region).to_be_visible()
            return region.text_content()

        def assert_provenance(self, view):
            case, run = view["case"], view["case"]["provider_run"]
            root = self.page.locator("#proposal-provenance")
            replay.expect(root).to_have_attribute("data-case-id", case["id"])
            replay.expect(root).to_have_attribute("data-revision", str(case["version"]))
            replay.expect(root).to_have_attribute("data-run-id", run["id"] if run else "")
            status = self.get("status")
            assert status["provider"] == "offline" and status["provider_networked"] is False
            replay.expect(self.page.locator("#proposal-provider")).to_have_text("Configured for new requests: offline · local provider.")
            actual = self.page.locator("#proposal-metadata").evaluate("""root=>[...root.querySelectorAll('dt')].map(n=>[n.textContent,n.nextElementSibling.textContent])""")
            if run is None:
                assert case["proposal"] is None and case["stage"] == "DRAFT"
                assert actual == [["Provenance", "No accepted proposal is present in this loaded case."]]
                replay.expect(self.page.locator("#proposal-origin")).to_have_text("No proposal loaded for this case.")
            else:
                assert case["stage"] == "PROPOSED"
                assert case["proposal"] is not None and run["provider"] == "offline" and run["live"] is False and run["egress"] is False
                assert run["usage"] == {} and run["request_hash"] == digest(case["request"])
                assert run["model"] in {"fixture-v1", ""}
                elapsed = str(int(run["elapsed_seconds"])) if float(run["elapsed_seconds"]).is_integer() else str(run["elapsed_seconds"])
                assert actual == [
                    ["Proposal run", run["id"]], ["Provider", run["provider"]], ["Actual model", run["model"] or "Not supplied"],
                    ["Mode", "Offline fixture · no model call"], ["Recorded at", run["timestamp"]], ["Elapsed", elapsed + " s"],
                    ["Request hash", run["request_hash"]], ["Egress", "No network egress reported"], ["Usage / accounting", "Not supplied"]]
                origin = "Loaded proposal: offline · " + (run["model"] or "Actual model not supplied") + " · Offline fixture · no model call."
                replay.expect(self.page.locator("#proposal-origin")).to_have_text(origin)
                received = [event for event in view["observations"]["events"] if event["kind"] == "ProposalReceived"
                            and event["body"].get("case_id") == case["id"] and event["body"]["run"]["id"] == run["id"]]
                assert len(received) == 1 and received[0]["body"]["run"] == run
            events = [event for event in view["observations"]["events"] if event["body"].get("case_id") == case["id"]
                      and event["kind"] in {"ProviderCallStarted", "ProposalReceived", "ProviderCallNotAccepted"}]
            events.sort(key=lambda row: row["seq"])
            shown = self.page.locator("#proposal-events [data-event-seq]").evaluate_all("""nodes=>nodes.map(n=>({seq:Number(n.dataset.eventSeq),kind:n.dataset.eventKind,text:n.textContent}))""")
            assert [(row["seq"], row["kind"]) for row in shown] == [(event["seq"], event["kind"]) for event in events[-5:]]
            for row, event in zip(shown, events[-5:], strict=True):
                body = event["body"]
                identity = body["run"]["id"] if event["kind"] == "ProposalReceived" else body["attempt_id"]
                assert row["text"].endswith(" · run " + identity)
                if event["kind"] == "ProviderCallStarted":
                    assert "completion not implied" in row["text"] and body["provider"] in row["text"]
                elif event["kind"] == "ProviderCallNotAccepted":
                    assert body["error_code"] in row["text"]
                else:
                    assert "Offline fixture · no model call" in row["text"] and body["run"]["provider"] in row["text"]
            replay.expect(self.page.locator("#proposal-events-heading")).to_have_text(
                f'Recorded provider activity · {len(events)} event' + ("" if len(events) == 1 else "s"))
            self.no_authority(view, status)
            captured = {"stage": self.stage, "view": view, "metadata": actual, "events": shown,
                        "activity": self.page.locator("#proposal-activity").text_content()}
            self.snapshots.append(captured)
            write_json(self.out / "provenance-observations.json", self.snapshots)

        def reveal_proposal_controls(self):
            """Reach native summaries before a retry; disclosure changes never submit."""
            posts = list(self.posts)
            for selector in ("#interpretation-panel", "#proposal-controls"):
                disclosure = self.page.locator(selector)
                replay.expect(disclosure).to_have_count(1)
                if disclosure.get_attribute("open") is None:
                    summary = selector + " > summary"
                    self.keyboard_to(summary)
                    replay.expect(self.page.locator(summary)).to_be_focused()
                    self.page.keyboard.press("Enter")
                    self.navigation_action("native-keyboard-disclosure", summary, "Enter")
                replay.expect(disclosure).to_have_attribute("open", "")
            replay.expect(self.page.locator("#propose")).to_be_visible()
            assert self.posts == posts, "Opening proposal controls submitted a request"

        def request_proposal(self, mode=None, *, expected_focus=None):
            self.mode = mode
            before = len(self.posts)
            self.reveal_proposal_controls()
            self.keyboard_to("#propose")
            replay.expect(self.page.locator("#propose")).to_be_enabled()
            self.page.keyboard.press("Enter")
            if mode == "hold":
                deadline = time.monotonic() + 10
                while self.held_proposal is None and time.monotonic() < deadline:
                    self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")
                assert self.held_proposal is not None
                self.phase("pending")
                replay.expect(self.page.locator("#propose")).to_be_disabled()
                for key in ("Enter", "Enter", "Space"):
                    self.page.keyboard.press(key)
                self.page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
                assert len(self.posts) == before + 1, "Pending repeated keys sent another proposal"
                self.shot("proposal-pending-disabled")
                held, self.held_proposal = self.held_proposal, None
                held.continue_()
            self.settled()
            assert len(self.posts) == before + 1, "One request activation sent duplicate proposal POSTs"
            if expected_focus is not None:
                # Observe completion before any later navigation; never repair focus in the replay.
                target = self.page.locator(expected_focus)
                replay.expect(target).to_be_visible()
                replay.expect(target).to_be_focused()
                geometry = self.triage_focus_geometry(target)
                observed = self.page.evaluate("""() => ({active: document.activeElement.id,
                    interpretationOpen: document.querySelector('#interpretation-panel').open,
                    controlsOpen: document.querySelector('#proposal-controls').open})""")
                assert observed["interpretationOpen"] is True
                assert observed["controlsOpen"] is (expected_focus == "#propose")
                self.request_focus.append({"stage": self.stage, "expected": expected_focus,
                                           "observed": observed, "geometry": geometry})
                write_json(self.out / "request-focus-observations.json", self.request_focus)

        def refresh_only(self):
            posts = list(self.posts)
            self.palette("Refresh current model")
            assert self.posts == posts, "Manual refresh retried a proposal"
            return self.view()

        def disclosure(self, view, suffix):
            observations = []
            for width in (1280, 320):
                self.page.set_viewport_size({"width": width, "height": 800})
                self.tab("change")
                self.keyboard_to("#proposal-record > summary")
                summary = self.page.locator("#proposal-record > summary")
                replay.expect(summary).to_be_focused()
                if self.page.locator("#proposal-record").get_attribute("open") is not None:
                    self.page.keyboard.press("Enter")
                self.page.keyboard.press("Space")
                replay.expect(self.page.locator("#proposal-record")).to_have_attribute("open", "")
                focus = self.triage_focus_geometry(summary)
                self.assert_provenance(view)
                geometry = self.page.locator("#proposal-record").evaluate("""root=>{
                    const boxes=[...root.querySelectorAll('dt,dd,p,h3')].map(n=>({text:n.textContent,rect:n.getBoundingClientRect().toJSON()}));
                    return {boxes,rect:root.getBoundingClientRect().toJSON(),width:innerWidth,documentWidth:document.documentElement.scrollWidth};
                }""")
                assert geometry["documentWidth"] <= width + 1
                for item in geometry["boxes"]:
                    assert item["rect"]["left"] >= -1 and item["rect"]["right"] <= width + 1, geometry
                audit = replay.Axe.from_file(replay.AXE_FILE_PATH).run(self.page, options={
                    "runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]},
                    "resultTypes": ["violations", "incomplete"]}).response
                observations.append({"width": width, "focus": focus, "geometry": geometry,
                                     "axe": {"version": audit["testEngine"]["version"], "violations": audit["violations"], "incomplete": audit["incomplete"]}})
                write_json(self.out / ("disclosure-" + suffix + ".json"), observations)
                self.shot("proposal-" + suffix + "-" + str(width))
                assert not audit["violations"]
                self.page.keyboard.press("Enter")
                replay.expect(self.page.locator("#proposal-record")).not_to_have_attribute("open", "")
                self.page.keyboard.press("Tab")
                replay.expect(summary).not_to_be_focused()
                self.page.keyboard.press("Shift+Tab")
                replay.expect(summary).to_be_focused()
            self.page.set_viewport_size({"width": 1280, "height": 900})
            return observations

        def failed_bootstrap(self):
            observations = []
            for endpoint in ("status", "workbench"):
                self.stage = "failed-bootstrap-" + endpoint
                self.get_fault = "/api/" + endpoint
                start = len(self.requests)
                # Reusing the same URL/fragment can be a same-document navigation.
                # Reload subsequent visits to run the actual application bootstrap.
                document = (self.page.goto(self.base + "#" + replay.TEST_CAPABILITY)
                            if endpoint == "status" else self.page.reload())
                assert document is not None and document.status == 200
                assert document.request.is_navigation_request() and document.request.resource_type == "document"
                replay.expect(self.page.locator("#error-json")).to_contain_text("SYNTHETIC_BOOTSTRAP_UNAVAILABLE")
                self.settled()
                self.tab("change")
                proposal = self.page.locator("#propose")
                replay.expect(proposal).to_be_visible()
                replay.expect(proposal).to_be_disabled()
                native = proposal.evaluate("node=>({tag:node.tagName,disabled:node.disabled,attribute:node.hasAttribute('disabled')})")
                assert native == {"tag": "BUTTON", "disabled": True, "attribute": True}
                notice = self.page.locator("#notice").text_content()
                # The two native summaries precede the checkbox in both directions.
                # Record every stop and prove the disabled proposal is always skipped.
                self.keyboard_to("#create")
                tab_order = ["create"]
                for key, stops in (
                    ("Tab", ("interpretation-summary", "proposal-controls-summary", "egress")),
                    ("Shift+Tab", ("proposal-controls-summary", "interpretation-summary", "create")),
                    ("Tab", ("interpretation-summary", "proposal-controls-summary", "egress")),
                ):
                    for target in stops:
                        self.page.keyboard.press(key)
                        replay.expect(self.page.locator("#" + target)).to_be_focused()
                        replay.expect(proposal).not_to_be_focused()
                        observed = self.page.evaluate("() => document.activeElement.id")
                        assert observed == target
                        tab_order.append(observed)
                # These keys land on the next reachable checkbox, never on the disabled proposal.
                self.page.keyboard.press("Enter")
                self.page.keyboard.press("Space")
                self.page.keyboard.press("Space")
                replay.expect(self.page.locator("#egress")).not_to_be_checked()
                replay.expect(self.page.locator("#proposal-activity")).to_be_hidden()
                replay.expect(self.page.locator("#proposal-activity")).not_to_have_attribute("data-status", "pending")
                replay.expect(self.page.locator("#notice")).to_have_text(notice)
                assert "Requesting an untrusted proposal" not in notice and not self.posts
                assert self.get_fault is None
                inventory = [row for row in self.requests[start:] if row["path"].startswith("/api/")]
                assert Counter((row["method"], row["path"]) for row in inventory) == {
                    ("GET", "/api/status"): 1, ("GET", "/api/workbench"): 1}, inventory
                observations.append({"failed_get": self.get_fault or "/api/" + endpoint, "native": native,
                                     "document_status": document.status, "navigation": "goto" if endpoint == "status" else "reload",
                                     "tab_order": tab_order,
                                     "activation_keys_target": "egress checkbox; disabled proposal skipped",
                                     "notice": notice, "requests": inventory, "proposal_posts": 0})
                write_json(self.out / "bootstrap-disabled-observations.json", observations)
                self.shot("bootstrap-disabled-" + endpoint)
            self.stage = "successful-bootstrap"
            start = len(self.requests)
            document = self.page.reload()
            assert document is not None and document.status == 200
            assert document.request.is_navigation_request() and document.request.resource_type == "document"
            # Retain Review.entry's baseline assertions using this reload response;
            # invoking entry() here would perform another same-document goto.
            replay.expect(self.page.locator("#connection")).to_contain_text("offline", timeout=60000)
            self.settled()
            replay.expect(self.page.locator("#model-canvas svg")).to_be_visible()
            replay.expect(self.page.locator("#create-panel")).to_be_hidden()
            replay.expect(self.page.locator("#source-status")).to_contain_text("SOURCE_REVIEW_REQUIRED")
            self.tab("change")
            replay.expect(self.page.locator("#propose")).to_be_disabled()
            assert not self.posts
            inventory = [row for row in self.requests[start:] if row["path"].startswith("/api/")]
            assert Counter((row["method"], row["path"]) for row in inventory) == {
                ("GET", "/api/status"): 1, ("GET", "/api/workbench"): 1, ("GET", "/api/cases"): 1}, inventory
            observations.append({"successful_entry": True, "document_status": document.status, "navigation": "reload",
                                 "requests": inventory, "proposal_posts": 0,
                                 "baseline_entry": {"model_visible_without_case": True, "request_form_closed": True,
                                                    "content_security_policy": document.headers.get("content-security-policy"),
                                                    "csp_modified": False}})
            write_json(self.out / "bootstrap-disabled-observations.json", observations)
            return observations

        def run(self):
            bootstrap = self.failed_bootstrap()
            self.stage = "pending-and-offline-accept"
            case_a = self.create_case("[case-a]")
            self.request_proposal("hold", expected_focus="#proposal-controls-summary")
            self.phase("received")
            accepted = self.view()
            assert accepted["case"]["version"] == 1
            self.assert_provenance(accepted)
            self.disclosure(accepted, "offline-accepted")

            self.stage = "structured-provider-refusal"
            self.expected_http.append((409, "/api/cases/" + case_a + "/propose"))
            self.request_proposal(expected_focus="#propose")
            assert "SYNTHETIC_PROVIDER_REFUSED" in self.phase("refused")
            self.assert_provenance(accepted)  # Loaded snapshot remains unchanged on refusal.
            refused = self.view()
            assert refused["case"] == accepted["case"]
            assert refused["observations"]["events"][:-2] == accepted["observations"]["events"]
            assert [event["kind"] for event in refused["observations"]["events"][-2:]] == ["ProviderCallStarted", "ProviderCallNotAccepted"]
            assert refused["observations"]["events"][-1]["body"]["error_code"] == "SYNTHETIC_PROVIDER_REFUSED"
            self.assert_provenance(self.refresh_only())
            self.phase("refused")

            self.stage = "transport-unknown-without-server-dispatch"
            before = self.view()
            self.request_proposal("abort-before-server")
            self.phase("unknown")
            assert self.view() == before
            self.assert_provenance(before)
            self.assert_provenance(self.refresh_only())
            assert "still unconfirmed" in self.phase("unknown")

            self.stage = "lost-acknowledgement-after-real-commit"
            before = self.view()
            self.request_proposal("abort-after-commit")
            self.phase("unknown")
            self.assert_provenance(before)
            committed = self.view()
            assert committed["case"]["version"] == before["case"]["version"] + 1
            assert committed["case"]["provider_run"]["id"] != before["case"]["provider_run"]["id"]
            self.assert_provenance(self.refresh_only())
            replay.expect(self.page.locator("#proposal-activity")).to_be_hidden()

            self.stage = "acknowledged-case-refresh-failed"
            before = self.view()
            self.get_fault = "/api/cases/" + case_a
            self.request_proposal()
            assert "acknowledged; workspace refresh is incomplete" in self.phase("received")
            self.assert_provenance(before)
            committed = self.view()
            assert committed["case"]["version"] == before["case"]["version"] + 1
            # A failed manual refresh must not clear the acknowledgement warning.
            self.get_fault = "/api/cases"
            self.refresh_only()
            assert "acknowledged; workspace refresh is incomplete" in self.phase("received")
            self.assert_provenance(committed)
            self.assert_provenance(self.refresh_only())
            assert "No meaning was selected automatically" in self.phase("received")

            self.stage = "acknowledged-list-refresh-failed"
            before = self.view()
            self.get_fault = "/api/cases"
            self.request_proposal()
            assert "acknowledged; workspace refresh is incomplete" in self.phase("received")
            committed = self.view()
            assert committed["case"]["version"] == before["case"]["version"] + 1
            self.assert_provenance(committed)
            self.assert_provenance(self.refresh_only())
            assert "No meaning was selected automatically" in self.phase("received")
            final_a = self.view()
            self.disclosure(final_a, "latest-five-provider-events")

            self.stage = "invalid-acknowledgement-missing-model-fixture"
            case_b = self.create_case("[case-b]")
            before = self.view()
            self.request_proposal("invalid-after-commit")
            assert "RESPONSE_INVALID" in self.phase("unknown")
            self.assert_provenance(before)
            final_b = self.view()
            assert final_b["case"]["version"] == 1 and final_b["case"]["provider_run"]["model"] == ""
            self.assert_provenance(self.refresh_only())
            replay.expect(self.page.locator("#proposal-activity")).to_be_hidden()
            self.disclosure(final_b, "model-not-supplied")

            self.stage = "case-isolation"
            posts = list(self.posts)
            for identity, expected, forbidden_run in ((case_a, final_a, final_b["case"]["provider_run"]["id"]),
                                                      (case_b, final_b, final_a["case"]["provider_run"]["id"])):
                self.switch_case(identity)
                self.tab("change")
                self.assert_provenance(expected)
                assert forbidden_run not in self.page.locator("#proposal-provenance").text_content()
                replay.expect(self.page.locator("#proposal-activity")).to_be_hidden()
                assert self.view() == expected
            assert self.posts == posts
            counts = Counter(row["path"] for row in self.posts)
            assert counts == {"/api/cases": 2, "/api/cases/" + case_a + "/propose": 6, "/api/cases/" + case_b + "/propose": 1}, counts
            assert len(self.posts) == 9
            assert sorted((item["status"], item["path"]) for item in self.http_errors) == sorted(self.expected_http)
            assert not self.errors and not self.forbidden and not self.external
            return {"cases": [case_a, case_b], "post_inventory": dict(counts), "post_count": 9,
                    "bootstrap_disabled": bootstrap, "editable_case_enables_proposal": True,
                    "request_focus": self.request_focus,
                    "final_versions": [final_a["case"]["version"], final_b["case"]["version"]],
                    "accepted_proposals": 5, "meaning_selections": 0, "provider": "offline",
                    "synthetic_controls": ["one provider refusal", "one missing-model metadata response", "named transport/refresh faults"],
                    "human_understanding": "UNKNOWN", "live_provider": "NOT_RUN"}
    return ProposalReview


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    script = Path(__file__).read_bytes()
    (out / "replay-script.py").write_bytes(script)
    result = {"schema": "eija.proposal-provenance-browser.v1", "status": "NOT_RUN", "utc": datetime.now(UTC).isoformat(),
              "script_sha256": hashlib.sha256(script).hexdigest(), "identity": "normal_source_review_required",
              "browser_started": False, "browser_closed": False, "server_started": False, "server_closed": False,
              "not_run": ["live provider", "model correctness", "provider billing", "human comprehension", "owner operations",
                          "configured provider differs from recorded provider", "valid JSON acknowledgement with invalid case contract",
                          "late old-case response while another case active", "manual server restart recovery"]}
    runtime = replay = fixture = review = before = address = None
    try:
        if not __debug__:
            raise ModuleNotFoundError("Assertions require unoptimized Python")
        runtime, replay, DomainError, compare_subjects = load_runtime(repo)
        assert runtime.ROOT.resolve() == repo
        if replay.PREREQUISITE_ERROR:
            raise ModuleNotFoundError(replay.PREREQUISITE_ERROR)
        before = runtime.subject()
        write_json(out / "subject-before.json", before)
        fixture = fixture_type(DomainError)()
        with replay.sync_playwright() as playwright:
            result["status"] = "FAIL"
            with replay.disposable_server(before_serve=fixture) as base:
                endpoint = urlsplit(base)
                address = (endpoint.hostname, endpoint.port)
                result["server_started"] = True
                browser = playwright.chromium.launch(headless=True)
                result["browser_started"] = True
                try:
                    page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
                    review = review_type(runtime, replay)(page, out, base)
                    result["evidence"] = review.run()
                    assert len(fixture.calls) == 6
                    assert Counter(call["control"] for call in fixture.calls) == {"real-offline": 4, "refusal": 1, "missing-model": 1}
                    result["status"] = "PASS"
                finally:
                    try:
                        if review:
                            review.shot("final")
                    finally:
                        browser.close()
                        result["browser_closed"] = True
    except ModuleNotFoundError as error:
        result["status"] = "NOT_RUN" if not result["browser_started"] else "FAIL"
        result["prerequisite"] = str(error)
    except Exception as error:
        text, trace = str(error), traceback.format_exc()
        if replay:
            text = text.replace(replay.TEST_CAPABILITY, "[test-capability]")
            trace = trace.replace(replay.TEST_CAPABILITY, "[test-capability]")
        result["status"], result["error"] = "FAIL", {"message": text, "traceback": trace}
    finally:
        if address:
            with socket.socket() as sock:
                sock.settimeout(.2)
                result["server_closed"] = sock.connect_ex(address) != 0
        if fixture:
            result["fixture_calls"] = fixture.calls
        if review:
            result.update({"stage": review.stage, "requests": review.requests, "redacted_posts": review.posts,
                           "controls": review.controls, "http_errors": review.http_errors, "javascript_errors": review.errors,
                           "external_attempts": review.external, "forbidden_attempts": review.forbidden})
            write_json(out / "authoritative-get-oracles.json", review.oracles)
        if before:
            after = runtime.subject()
            write_json(out / "subject-after.json", after)
            result["subject_preservation"] = compare_subjects(before, after)
            if result["subject_preservation"]["status"] != "UNCHANGED":
                result["status"] = "FAIL"
        if (result["server_started"] and not result["server_closed"]) or (result["browser_started"] and not result["browser_closed"]):
            result["status"] = "FAIL"
        result["script_preserved"] = Path(__file__).read_bytes() == script
        if not result["script_preserved"]:
            result["status"] = "FAIL"
        write_json(out / "result.json", result)
        write_json(out / "artifact-manifest.json", {str(path.relative_to(out)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in sorted(out.rglob("*")) if path.is_file()})
    sys.stdout.write(json.dumps({"status": result["status"], "browser_closed": result["browser_closed"], "server_closed": result["server_closed"]}) + "\n")
    return 0 if result["status"] == "PASS" else 2 if result["status"] == "NOT_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
