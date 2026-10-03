"""Bounded necessary-state inspection, separate from the timed owner journey.

Uses the existing Runner, DOM probe and axe. All disclosures are opened through
native input. These observations are geometry/accessibility evidence, not human
comprehension measurements. Longer scrolled content and fault matrices remain
explicitly outside this first tranche.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import replace
from pathlib import Path
from urllib.parse import urlsplit

from .journey import JourneyError, Ref, Runner, Step, journey, new_page, open_studio
from .server import studio_server

SCHEMA = "eija.hci.inspection.v1"
VIEWPORTS = ((1440, 900), (320, 568))
CHOOSER = ("work-views", "panels", "layout", "connections")
INTENT = ("record", "controls", "alternatives")
PLANNED = [
    {"id": "intermediate-widths", "reason": "1280, 1600 and 390 inspection widths are not in this tranche."},
    {
        "id": "scrolled-detail-content",
        "reason": "Only the viewport after native disclosure activation is audited; lower scroll positions remain unmeasured.",
    },
    {
        "id": "compact-panes",
        "reason": "Explorer and inspector drawers are mutually exclusive at narrow widths; their individual open states remain planned.",
    },
    {
        "id": "proposal-failures",
        "reason": "Pending, refused, unknown-outcome and refresh-failure detail states remain in dedicated replay coverage, outside this density pass.",
    },
    {
        "id": "formal-and-agent-details",
        "reason": "Formal record, source boundary and agent-edit detail density remain planned.",
    },
]


def required_states() -> list[str]:
    """Frozen scope, independent of whichever states the browser managed to reach."""
    rows = []
    for width, _height in VIEWPORTS:
        rows.extend(f"workspace-{name}-{width}" for name in CHOOSER)
        rows.extend(f"intent-{name}-{width}" for name in INTENT)
        if width == 1440:
            rows.extend(("domain-inspector-1440", "canvas-view-1440"))
        rows.append(f"runtime-attempt-{width}")
    return rows


def case_subject(payload: dict) -> dict:
    """Allowlisted identity from an observed real case GET, not application globals."""
    case, packet = payload["case"], payload["packet"]
    candidate = case.get("candidate")
    return {
        "case_id": case["id"],
        "revision": case["version"],
        "stage": case["stage"],
        "subject_hash": packet.get("subject_hash"),
        "semantic_hash": (packet.get("subject") or {}).get("semantic"),
        "candidate_json_sha256": hashlib.sha256(
            json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if candidate is not None
        else None,
        "origin": "observed GET /api/cases/{case_id}",
    }


def safe_reason(exc: Exception) -> str:
    lines = str(exc).splitlines()
    return re.sub(r"https?://\S+", "<URL>", f"{type(exc).__name__}: {lines[0] if lines else ''}")


OBSERVE = """() => {
    const ids=['workspace-dialog','change','model','try','explorer','inspector',
      'domain-tree','selection-detail','model-canvas','canvas-view','proposal-record',
      'proposal-controls','proposal-alternatives','runtime-attempt-details','runtime-result'];
    const elements=Object.fromEntries(ids.map(id=>{
      const el=document.getElementById(id);if(!el)return [id,null];
      const r=el.getBoundingClientRect();return [id,{visible:window.__hci.isVisible('#'+id),
        open:el.tagName==='DETAILS'||el.tagName==='DIALOG'?el.open:null,
        rect:{x:r.x,y:r.y,w:r.width,h:r.height},scrollTop:el.scrollTop,
        scrollLeft:el.scrollLeft,clientHeight:el.clientHeight,scrollHeight:el.scrollHeight}];
    }));
    return {case_id:document.getElementById('case-switcher').value,
      stage:document.getElementById('case-stage').textContent.trim(),
      navigator:document.getElementById('navigator-mode').value,
      transition:document.getElementById('transition-select').value,
      selected_tree:[...document.querySelectorAll('#domain-tree [aria-selected="true"]')]
        .map(el=>({kind:el.dataset.kind,id:el.dataset.itemId})),
      runtime:{...document.getElementById('runtime-result').dataset},
      elements,focus:window.__hci.focus()};
}"""


class Inspection:
    """One ordinary case per viewport; setup actions never enter owner metrics."""

    def __init__(self, page, out: Path, result: dict) -> None:
        self.page, self.out, self.result = page, out, result
        self.runner = Runner(page, "pointer", audit=False)
        self.subject: dict | None = None
        self.requests: list[dict] = []
        page.on("request", self._request)
        page.on("response", self._response)

    def _request(self, request) -> None:
        path = urlsplit(request.url).path
        if path.startswith("/api/"):
            self.requests.append({"method": request.method, "path": path})

    def _response(self, response) -> None:
        path = urlsplit(response.url).path
        if (
            response.request.method == "GET"
            and response.status == 200
            and re.fullmatch(r"/api/cases/[^/]+", path)
        ):
            self.subject = case_subject(response.json())

    def click(self, selector: str) -> None:
        self.runner.run([Step(f"inspection-{len(self.runner.steps)}", selector, "click", Ref(css=selector))])

    def select(self, selector: str, value: str) -> None:
        # Native Tab/Arrow navigation, no programmatic select_option or DOM focus.
        self.runner.modality = "keyboard"
        try:
            self.runner.run(
                [Step(f"inspection-{len(self.runner.steps)}", selector, "select", Ref(css=selector), value)]
            )
        finally:
            self.runner.modality = "pointer"

    def details(self, selector: str, opened: bool) -> None:
        target = self.page.locator(selector)
        if target.count() != 1:
            raise JourneyError(f"Missing disclosure {selector}")
        if (target.get_attribute("open") is not None) != opened:
            self.click(selector + " > summary")
        if (target.get_attribute("open") is not None) != opened:
            raise JourneyError(f"Disclosure {selector} did not {'open' if opened else 'close'}")

    def tab(self, name: str) -> None:
        # These first-tranche routes are direct main tabs; absence is a coverage failure.
        self.click(f'[data-tab="{name}"]')
        if not self.page.locator("#" + name).is_visible():
            raise JourneyError(f"Work view {name} did not become visible")

    def workspace(self) -> None:
        if not self.page.locator("#workspace-dialog").is_visible():
            self.click("#open-workspace")
        if not self.page.locator("#workspace-dialog").is_visible():
            raise JourneyError("Workspace did not open")

    def chooser_state(self, name: str) -> None:
        self.workspace()
        for other in CHOOSER:
            self.details("#workspace-" + other, other == name)

    def reveal(self, pane: str) -> None:
        if self.page.locator("#" + pane).is_visible():
            return
        self.workspace()
        self.details("#workspace-layout", True)
        self.click("#toggle-" + pane)
        if self.page.locator("#workspace-dialog").is_visible():
            raise JourneyError("Layout toggle did not dismiss Workspace")
        if not self.page.locator("#" + pane).is_visible():
            raise JourneyError(f"Pane {pane} did not become visible")

    def observe(self, state_id: str, prepare, *, story: str) -> None:
        row = next(row for row in self.result["states"] if row["id"] == state_id)
        start, before = len(self.requests), self.subject
        try:
            prepare()
            self.runner.settle()
            requests = self.requests[start:]
            if any(request["method"] != "GET" for request in requests):
                raise JourneyError("Inspection navigation unexpectedly issued a mutation request")
            if self.subject is None or before != self.subject:
                raise JourneyError("Inspection navigation changed or lacks its observed case identity")
            observed = self.page.evaluate(OBSERVE)
            if observed["case_id"] != self.subject["case_id"] or observed["stage"] != self.subject["stage"]:
                raise JourneyError("Displayed case identity disagrees with the observed case GET")
            name = "inspection/" + state_id
            self.runner.checkpoint(name)
            image = self.out / (state_id + ".png")
            self.page.screenshot(path=str(image), full_page=False)
            capture = {
                "path": "inspection/" + image.name,
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
            }
            self.runner.views[name].update(subject=self.subject, observed=observed, screenshot=capture)
            row.update(
                status="PASS",
                view=name,
                story=story,
                subject=self.subject,
                screenshot=capture,
                requests=requests,
                observation="Viewport after native input; no scripted scroll reset",
            )
            row.pop("reason", None)
        except Exception as exc:
            row.update(status="FAIL", reason=safe_reason(exc), requests=self.requests[start:])
            raise

    def proposal_states(self, width: int) -> None:
        for name in CHOOSER:
            self.observe(
                f"workspace-{name}-{width}", lambda name=name: self.chooser_state(name), story="US02 / H05"
            )
        self.click("#close-workspace")
        # Keep only the inspected optional disclosure open. Required origin/summary stay visible.
        for name in INTENT:

            def prepare(name=name):
                for other in INTENT:
                    self.details("#proposal-" + other, other == name)

            self.observe(f"intent-{name}-{width}", prepare, story="US03 / H04 / H05")
        self.details("#proposal-alternatives", False)

    def domain_state(self) -> None:
        self.tab("model")
        self.reveal("explorer")
        self.select("#navigator-mode", "domain")
        group = '#domain-tree .tree-group[data-kind="transition"]'
        if self.page.locator(group).get_attribute("aria-expanded") != "true":
            self.click(group + " > span")
        self.click(group + " > [role=group] > .tree-leaf:first-child")
        self.reveal("inspector")
        if self.page.locator("#navigator-mode").input_value() != "domain":
            raise JourneyError("Domain navigator was not pinned")
        if not self.page.locator("#transition-inspector").is_visible():
            raise JourneyError("Selected transition inspector is not visible")
        selected = self.page.locator(group + ' .tree-leaf[aria-selected="true"]')
        if (
            selected.count() != 1
            or selected.get_attribute("data-item-id") != self.page.locator("#transition-select").input_value()
        ):
            raise JourneyError("Pinned domain selection and inspector disagree")

    def run(self, width: int) -> None:
        steps = journey()

        def segment(first: str, last: str) -> None:
            ids = [step.id for step in steps]
            for step in steps[ids.index(first) : ids.index(last) + 1]:
                # Keep real key input for native actor select controls in setup too.
                self.runner.modality = "keyboard" if step.kind == "select" else "pointer"
                self.runner.run([replace(step, view=None, audit_visit=None)])
            self.runner.modality = "pointer"

        segment("open-change", "ask-interpretations")
        self.proposal_states(width)
        segment("select-meaning", "select-meaning")
        if width == 1440:
            self.observe("domain-inspector-1440", self.domain_state, story="US06 / H05")
            self.observe("canvas-view-1440", lambda: self.details("#canvas-view", True), story="US06 / H05")
            self.details("#canvas-view", False)
        # The canonical synthetic actor sequence ends in a real refused command.
        segment("open-try", "denied-recommend")
        if self.page.locator("#runtime-result").get_attribute("data-status") != "refused":
            raise JourneyError("The runtime inspection fixture did not reach its refused attempt")
        self.observe(
            f"runtime-attempt-{width}",
            lambda: self.details("#runtime-attempt-details", True),
            story="US08 / H09",
        )


def run_inspection(browser, *, out: Path, identity: str = "harness") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    required = required_states()
    result = {
        "schema": SCHEMA,
        "required_states": required,
        "planned_states": PLANNED,
        "states": [{"id": name, "status": "NOT_RUN", "reason": "State not reached"} for name in required],
        "views": {},
        "errors": [],
        "http_failures": [],
        "steps": [],
        "operators": [],
        "pointer_targets": [],
        "requests": [],
        "scope": "Offline Excursion case; native pointer actions and native keyboard selections; separate from canonical owner metrics",
    }
    for width, height in VIEWPORTS:
        try:
            with studio_server(f"inspection-{width}", identity) as url:
                context, page = new_page(browser)
                inspection = Inspection(page, out, result)
                try:
                    page.set_viewport_size({"width": width, "height": height})
                    open_studio(page, url)
                    inspection.run(width)
                finally:
                    runner = inspection.runner
                    result["views"].update(runner.views)
                    for key in ("errors", "http_failures", "steps", "operators", "pointer_targets"):
                        result[key].extend(getattr(runner, key))
                    result["requests"].extend(inspection.requests)
                    context.close()
        except Exception as exc:
            reason = safe_reason(exc)
            result["errors"].append(f"inspection-{width}: {reason}")
            for row in result["states"]:
                if row["id"].endswith(f"-{width}") and row["status"] == "NOT_RUN":
                    row["reason"] = "Earlier setup or state failed: " + reason
    return result
