"""The canonical owner journey as data, plus Playwright drivers that execute it and record a trace.

Nothing here applies HCI laws; it records raw, reproducible observations (geometry of every pointer
target, choice counts, focus stops, click -> DOM-update timings, axe results). `analysis.py` turns
the trace into Fitts / Hick-Hyman / KLM / Doherty / WCAG numbers.

Journey (brief): create case -> ask for interpretations -> select recommend_only -> Try: reset,
Submit and Recommend as teacher-assigned, Approve as registrar, denied as teacher-unassigned -> run
verification -> acknowledge -> approve -> apply. The three review answers are SCRIPTED fixture
answers typed by the driver. They exercise the UI; they say nothing about human comprehension.

Stable public API (reused by other pipelines, for example the UX research lane; add, do not change):
`journey()`, `Step`, `Ref`, `Expect`, `Decision`, `Runner`, `run_pass()`, `collect()`, `prerequisites()`,
`new_page()`, `open_studio()`, `run_axe()`, `keystrokes()`, `ui_hashes()`. Validity limits: the journey is
scripted (one expert-style path, synthetic data, offline provider), so timings and operator counts describe
that path only; a missing prerequisite must be reported as NOT_RUN by the caller, never as a pass.
"""

# ruff: noqa: PLC0415 - playwright and axe belong to the optional `hci` extra: imported lazily so a machine without them reports NOT_RUN instead of failing at import
from __future__ import annotations

import hashlib
import importlib.metadata
import platform
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .server import ROOT, studio_server

PROBE = Path(__file__).with_name("probe.js")
WEB = ROOT / "src" / "eija_studio" / "resources" / "web"
VIEWPORT = {"width": 1440, "height": 900}
AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
MAX_TABS = 150
QUIET_MS = 150
SETTLE_TIMEOUT_MS = 20000
SHIFTED = set('~!@#$%^&*()_+{}|:"<>?')


class JourneyError(RuntimeError):
    """The UI did not do what the journey step expected; the run is invalid, not slow."""


class ReleaseIdentityUnavailable(JourneyError):
    """Approval is blocked because the running source is not the owner-stamped build (SOURCE_REVIEW_REQUIRED).

    A missing prerequisite, not a UI defect: reported as NOT_RUN, never as pass or as a UI failure."""


# --- journey specification --------------------------------------------------------------------
@dataclass(frozen=True)
class Ref:
    """Where a control is: a CSS selector, or an ARIA role + exact name (optionally within a CSS scope)."""

    css: str | None = None
    role: str | None = None
    name: str | None = None
    within: str | None = None

    def locate(self, page):
        scope = page.locator(self.within) if self.within else page
        if self.css:
            return scope.locator(self.css)
        return scope.get_by_role(self.role, name=self.name, exact=True)

    @property
    def label(self) -> str:
        return self.css or f"{self.within + ' ' if self.within else ''}{self.role}[{self.name}]"


@dataclass(frozen=True)
class Expect:
    """Post-condition that must hold after the action settles."""

    kind: str  # text_equals | text_contains | visible | enabled | count
    css: str
    value: Any = None


@dataclass(frozen=True)
class Decision:
    """A choice point: how many alternatives compete for the same intent (CSS selectors, unioned)."""

    name: str
    selectors: tuple[str, ...]


@dataclass(frozen=True)
class Step:
    id: str
    label: str
    kind: str  # click | type | select | check
    ref: Ref
    text: str = ""
    think: str | None = None  # rationale for one KLM M operator placed before this step
    decision: Decision | None = None
    expect: Expect | None = None
    view: str | None = None  # checkpoint name after the step (axe, target audit, chunks)
    audit_visit: str | None = None  # extra un-modelled tab visit for coverage: data-tab name


ANSWERS = (("authority", "Registrar"), ("assignment", "No"), ("reject_entry", "Recommended"))
REQUEST = "Let teachers sign off excursions."
TABS = Decision("choose a work area", (".tabs button",))
ACTION_CHOICE = Decision("choose a lifecycle action", ("#runtime-actions button",))
ACTOR_CHOICE = Decision("choose the acting role", ("#actor option",))


def _action(name: str) -> Ref:
    return Ref(within="#runtime-actions", role="button", name=name)


def journey() -> list[Step]:
    """The canonical mouse-and-keyboard owner journey. M operators carry their rationale."""
    steps = [
        Step("type-request", "Type the change request", "type", Ref(css="#request"), REQUEST,
             think="Recall the change to request (start of the unit task)", view="create-panel"),
        Step("create-case", "Create Change Case", "click", Ref(css="#create"),
             expect=Expect("visible", "#workspace"), view="change-empty"),
        Step("ask-interpretations", "Ask for interpretations", "click", Ref(css="#propose"),
             expect=Expect("count", ".option", 3), view="change-options"),
        Step("select-meaning", "Select the supported meaning (recommend_only)", "click",
             Ref(within=".option", role="button", name="Select this meaning"),
             think="Compare the three interpretations and choose one",
             decision=Decision("choose an interpretation", (".option button",)),
             expect=Expect("visible", "#editor"), view="change-selected", audit_visit="impact"),
        Step("open-try", "Open the Try tab", "click", Ref(css='[data-tab="try"]'),
             decision=TABS, expect=Expect("visible", "#reset"), view="try-idle"),
        Step("reset-preview", "Start / reset preview", "click", Ref(css="#reset"),
             expect=Expect("text_equals", "#runtime-state", "Draft"), view="try-draft"),
        Step("submit-teacher", "Submit as teacher-assigned", "click", _action("Submit"),
             decision=ACTION_CHOICE, expect=Expect("text_equals", "#runtime-state", "Submitted")),
        Step("recommend-teacher", "Recommend as teacher-assigned", "click", _action("Recommend"),
             decision=ACTION_CHOICE, expect=Expect("text_equals", "#runtime-state", "Recommended")),
        Step("actor-registrar", "Switch actor to registrar", "select", Ref(css="#actor"), "registrar",
             think="Decide which role must act next", decision=ACTOR_CHOICE),
        Step("approve-registrar", "Approve as registrar", "click", _action("Approve"),
             decision=ACTION_CHOICE, expect=Expect("text_equals", "#runtime-state", "Approved")),
        Step("actor-unassigned", "Switch actor to teacher-unassigned (negative control)", "select",
             Ref(css="#actor"), "teacher-unassigned", think="Choose the unauthorised role to probe",
             decision=ACTOR_CHOICE),
        Step("denied-recommend", "Recommend as teacher-unassigned (expect denial)", "click",
             _action("Recommend"), decision=ACTION_CHOICE,
             expect=Expect("text_contains", "#notice", "DENIED"), view="try-denied"),
        Step("open-evidence", "Open Evidence & Decision", "click", Ref(css='[data-tab="evidence"]'),
             decision=TABS, expect=Expect("visible", "#verify")),
        Step("run-verification", "Run bounded verification", "click", Ref(css="#verify"),
             expect=Expect("enabled", "#approve"), view="evidence-verified"),
    ]
    for key, value in ANSWERS:
        steps.append(Step(f"answer-{key}", f"Answer review question '{key}'", "type", Ref(css=f"#q-{key}"),
                          value, think="Read the question and recall the fixture answer"))
    steps += [
        Step("acknowledge", "Acknowledge unknowns", "check", Ref(css="#acknowledge"),
             think="Read the acknowledgement before agreeing", expect=Expect("enabled", "#approve")),
        Step("approve-exact", "Approve exact local revision", "click", Ref(css="#approve"),
             expect=Expect("text_equals", "#case-stage", "APPROVED"), view="evidence-approved"),
        Step("apply-baseline", "Apply to local baseline", "click", Ref(css="#apply"),
             think="Confirm the intent to change the local baseline",
             expect=Expect("text_equals", "#case-stage", "APPLIED"), view="applied"),
    ]
    return steps


def keystrokes(text: str) -> int:
    """KLM K operators to type `text`: one per character plus one Shift per shifted character."""
    return sum(1 + (1 if (c.isupper() or c in SHIFTED) else 0) for c in text)


# --- driver -------------------------------------------------------------------------------------
class Runner:
    """Executes steps against one page and records a JSON-serialisable trace."""

    def __init__(self, page, modality: str, audit: bool) -> None:
        self.page, self.modality, self.audit = page, modality, audit
        self.hands = "mouse" if modality == "pointer" else "keyboard"
        self.pointer: tuple[float, float] | None = None
        self.operators: list[dict] = []
        self.pointer_targets: list[dict] = []
        self.steps: list[dict] = []
        self.views: dict[str, dict] = {}
        self.errors: list[str] = []
        self.http_failures: list[dict] = []
        self.current_step = "load"
        page.on("pageerror", lambda e: self.errors.append("pageerror: " + str(e)))
        page.on("console", lambda m: self.errors.append("console.error: " + m.text) if m.type == "error" else None)
        page.on("response", self._on_response)

    def _on_response(self, response) -> None:
        if response.status >= 400:
            path = response.url.split("?", 1)[0].split("#", 1)[0]
            self.http_failures.append({"step": self.current_step, "status": response.status,
                                       "method": response.request.method, "path": "/" + path.split("/", 3)[3]})

    # -- operators
    def op(self, step: Step, symbol: str, note: str, **extra: Any) -> None:
        self.operators.append({"step": step.id, "op": symbol, "note": note, **extra})

    def _hands_to(self, step: Step, device: str) -> None:
        if self.hands != device:
            self.op(step, "H", f"hands to {device}")
            self.hands = device

    # -- waiting
    def settle(self) -> dict:
        result = self.page.evaluate(f"() => window.__hci.waitQuiet({QUIET_MS}, {SETTLE_TIMEOUT_MS})")
        if not result["ok"]:
            raise JourneyError("page did not settle (aria-busy or mutations) within the timeout")
        return result

    def check(self, step: Step) -> None:
        e = step.expect
        if not e:
            return
        deadline = time.monotonic() + 8
        while True:
            if self._holds(e):
                return
            if time.monotonic() > deadline:
                blockers = self.page.evaluate("() => window.__hci.text('#blockers')") or ""
                if "SOURCE_REVIEW_REQUIRED" in blockers:
                    raise ReleaseIdentityUnavailable(
                        f"step {step.id}: approval is blocked by SOURCE_REVIEW_REQUIRED (source differs from the owner-stamped "
                        "fixture); --identity release needs a release-stamped build. Use the default harness identity for UI measurement.")
                raise JourneyError(f"step {step.id}: expectation {e.kind} {e.css!r} {e.value!r} did not hold")
            time.sleep(0.05)

    def _holds(self, e: Expect) -> bool:
        if e.kind == "text_equals":
            return self.page.evaluate("(s) => window.__hci.text(s)", e.css) == e.value
        if e.kind == "text_contains":
            return e.value in (self.page.evaluate("(s) => window.__hci.text(s)", e.css) or "")
        if e.kind == "visible":
            return self.page.evaluate("(s) => window.__hci.isVisible(s)", e.css)
        if e.kind == "enabled":
            return self.page.evaluate("(s) => window.__hci.isEnabled(s)", e.css)
        if e.kind == "count":
            return self.page.locator(e.css).count() == e.value
        raise ValueError(e.kind)

    # -- execution
    def run(self, steps: list[Step]) -> None:
        for step in steps:
            self._run_step(step)

    def _run_step(self, step: Step) -> None:
        self.current_step = step.id
        record: dict[str, Any] = {"id": step.id, "label": step.label, "kind": step.kind, "ref": step.ref.label}
        if step.decision:
            record["decision"] = {
                "name": step.decision.name,
                "selectors": list(step.decision.selectors),
                "n_choices": self.page.evaluate("(s) => window.__hci.choices(s)", list(step.decision.selectors)),
                "n_screen": self.page.evaluate("() => window.__hci.screenChoices()"),
            }
        if step.think:
            self.op(step, "M", step.think)
        locator = step.ref.locate(self.page)
        if locator.count() != 1:
            raise JourneyError(f"step {step.id}: {step.ref.label} matched {locator.count()} elements, expected 1")
        getattr(self, "_do_" + step.kind)(step, locator, record)
        self.check(step)
        if step.audit_visit and self.audit:
            self._audit_visit(step.audit_visit)
        if step.view and self.audit:
            self.checkpoint(step.view)
        self.steps.append(record)

    def _record_interaction(self, record: dict) -> None:
        self.settle()
        interaction = self.page.evaluate("() => window.__hci.lastInteraction()")
        record["interaction"] = interaction
        record["focus_lost_after"] = self.page.evaluate("() => window.__hci.focus().lost")

    # pointer primitives
    def _point(self, step: Step, locator, record: dict, *, fitts: bool = True) -> tuple[float, float]:
        self._hands_to(step, "mouse")
        before = self.page.evaluate("() => window.scrollY")
        locator.scroll_into_view_if_needed()
        record["scrolled"] = bool(self.page.evaluate("() => window.scrollY") != before)
        info = locator.evaluate("(el) => window.__hci.targetOf(el)")
        if info["disabled"]:
            raise JourneyError(f"step {step.id}: target is disabled")
        box = info["effective"]
        cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
        if not locator.evaluate("(el, p) => window.__hci.hitOk(el, p[0], p[1])", [cx, cy]):
            raise JourneyError(f"step {step.id}: pointer landing point is covered by another element")
        self.page.mouse.move(cx, cy)
        if fitts:
            self.pointer_targets.append({
                "step": step.id, "name": info["name"], "selector": info["selector"], "tag": info["tag"],
                "from": list(self.pointer) if self.pointer else None, "to": [cx, cy],
                "effective": box, "raw": info["raw"], "via_label": info["via_label"], "scrolled": record["scrolled"],
            })
        self.pointer = (cx, cy)
        self.op(step, "P", f"point at {info['name']}", fitts=fitts)
        record["target"] = {"name": info["name"], "selector": info["selector"], "effective": box, "raw": info["raw"]}
        return cx, cy

    def _press_release(self, step: Step) -> None:
        self.page.mouse.down()
        self.page.mouse.up()
        self.op(step, "B", "button press")
        self.op(step, "B", "button release")

    def _do_click(self, step: Step, locator, record: dict) -> None:
        if self.modality == "pointer":
            self._point(step, locator, record)
            self._press_release(step)
        else:
            self._focus_to(step, locator, record)
            self.page.keyboard.press("Enter")
            self.op(step, "K", "Enter")
        self._record_interaction(record)

    def _do_check(self, step: Step, locator, record: dict) -> None:
        if self.modality == "pointer":
            self._point(step, locator, record)
            self._press_release(step)
        else:
            self._focus_to(step, locator, record)
            self.page.keyboard.press("Space")
            self.op(step, "K", "Space")
        self._record_interaction(record)

    def _type_keys(self, step: Step, text: str) -> None:
        self._hands_to(step, "keyboard")
        self.page.keyboard.press("Control+A")
        self.op(step, "K", "Ctrl")
        self.op(step, "K", "A")
        self.page.keyboard.type(text)
        for char in text:
            if char.isupper() or char in SHIFTED:
                self.op(step, "K", "Shift")
            self.op(step, "K", f"key {char!r}")

    def _do_type(self, step: Step, locator, record: dict) -> None:
        if self.modality == "pointer":
            self._point(step, locator, record)
            self._press_release(step)
        else:
            self._focus_to(step, locator, record)
        self._type_keys(step, step.text)
        record["typed_chars"] = len(step.text)
        actual = locator.input_value()
        if actual != step.text:
            raise JourneyError(f"step {step.id}: field holds {actual!r}, expected {step.text!r}")
        self.settle()

    def _do_select(self, step: Step, locator, record: dict) -> None:
        values = locator.evaluate("(el) => [...el.options].map((o) => o.value)")
        current = locator.evaluate("(el) => el.selectedIndex")
        wanted = values.index(step.text)
        if self.modality == "pointer":
            # Native popups are not observable in the DOM: model open (P,B,B) then choose (P,B,B).
            self._point(step, locator, record)
            self.op(step, "B", "open list (press)")
            self.op(step, "B", "open list (release)")
            self.op(step, "P", "point at option (native popup; geometry not observable)")
            self.op(step, "B", "choose option (press)")
            self.op(step, "B", "choose option (release)")
            locator.select_option(step.text)
        else:
            self._focus_to(step, locator, record)
            key = "ArrowDown" if wanted > current else "ArrowUp"
            for _ in range(abs(wanted - current)):
                self.page.keyboard.press(key)
                self.op(step, "K", key)
        if locator.input_value() != step.text:
            raise JourneyError(f"step {step.id}: select holds {locator.input_value()!r}, expected {step.text!r}")
        self.settle()

    # keyboard primitive
    def _focus_to(self, step: Step, locator, record: dict) -> None:
        stops: list[dict] = []
        for _ in range(MAX_TABS + 1):
            if locator.evaluate("(el) => el === document.activeElement"):
                break
            if len(stops) == MAX_TABS:
                raise JourneyError(f"step {step.id}: not reachable within {MAX_TABS} Tab presses")
            self.page.keyboard.press("Tab")
            self.op(step, "K", "Tab")
            stops.append(self.page.evaluate("() => window.__hci.focus()"))
        record["tab_presses"] = len(stops)
        record["focus_stops"] = [{k: s.get(k) for k in ("name", "selector", "visible_ring", "focus_visible", "lost", "rect")} for s in stops]
        # keep the pointer-free record shape parallel to the pointer run
        info = locator.evaluate("(el) => window.__hci.targetOf(el)")
        record["target"] = {"name": info["name"], "selector": info["selector"], "effective": info["effective"], "raw": info["raw"]}

    # -- audits
    def _audit_visit(self, tab: str) -> None:
        """Visit a work area only to audit it (not part of the modelled journey)."""
        self.page.locator(f'[data-tab="{tab}"]').click()
        self.settle()
        self.checkpoint(f"{tab}-tab")

    def checkpoint(self, name: str) -> None:
        page = self.page
        self.views[name] = {
            "controls": page.evaluate("() => window.__hci.controls()"),
            "chunks_viewport": page.evaluate("() => window.__hci.chunks('viewport')"),
            "chunks_page": page.evaluate("() => window.__hci.chunks('page')"),
            "tabbable": page.evaluate("() => window.__hci.tabbableCount()"),
            "geometry": page.evaluate("() => window.__hci.geometry()"),
            "visual_state_only": page.evaluate("() => window.__hci.visualStateOnly()"),
            "axe": run_axe(page),
        }

    def responsive_audit(self) -> dict:
        """Reflow (WCAG 1.4.10) and target audit at narrow widths, tab by tab, on the final state."""
        out: dict[str, Any] = {}
        for width, height in ((390, 844), (320, 568)):
            self.page.set_viewport_size({"width": width, "height": height})
            rows = {}
            for tab in ("change", "impact", "try", "evidence"):
                self.page.locator(f'[data-tab="{tab}"]').click()
                self.settle()
                geo = self.page.evaluate("() => window.__hci.geometry()")
                rows[tab] = {"scroll_width": geo["scrollWidth"], "inner_width": geo["innerWidth"],
                             "controls": self.page.evaluate("() => window.__hci.controls()")}
            out[f"{width}x{height}"] = rows
        self.page.set_viewport_size(VIEWPORT)
        return out


def run_axe(page) -> dict:
    """axe-core (via axe-playwright-python) restricted to WCAG 2.0-2.2 A/AA tags."""
    from axe_playwright_python.base import AXE_FILE_PATH
    from axe_playwright_python.sync_playwright import Axe

    axe = Axe.from_file(AXE_FILE_PATH)  # explicit UTF-8 read; the package default would use the platform locale (cp1252 here)
    options = {"runOnly": {"type": "tag", "values": AXE_TAGS}, "resultTypes": ["violations", "incomplete"]}
    response = axe.run(page, options=options).response
    return {
        "axe_core": response.get("testEngine", {}).get("version"),
        "violations": [
            {"id": v["id"], "impact": v.get("impact"), "help": v["help"], "help_url": v["helpUrl"], "tags": sorted(v["tags"]),
             "nodes": [{"target": ", ".join(n["target"]) if isinstance(n["target"][0], str) else str(n["target"]),
                        "html": n["html"][:200], "summary": (n.get("failureSummary") or "")[:400]} for n in v["nodes"]]}
            for v in sorted(response["violations"], key=lambda item: item["id"])
        ],
        "incomplete": [{"id": v["id"], "impact": v.get("impact"), "count": len(v["nodes"])}
                       for v in sorted(response["incomplete"], key=lambda item: item["id"])],
    }


# --- orchestration ------------------------------------------------------------------------------
def prerequisites() -> tuple[bool, str]:
    """(True, chrome version) or (False, reason). A False result must be reported NOT_RUN, never PASS."""
    try:
        import axe_playwright_python  # noqa: F401 - presence check only
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        return False, f"python packages missing ({exc}); install the hci extra: pip install -e .[hci]"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            version = browser.version
            browser.close()
        return True, version
    except Exception as exc:  # any launch failure is a missing prerequisite, reported as NOT_RUN
        return False, "Google Chrome (channel 'chrome') could not be launched: " + str(exc).splitlines()[0]


def new_page(browser):
    context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
    context.add_init_script(path=str(PROBE))
    return context, context.new_page()


def open_studio(page, url: str) -> None:
    page.goto(url)
    page.locator("#connection").filter(has_text="offline").wait_for()
    page.evaluate("() => window.__hci.waitQuiet(150, 10000)")


def run_pass(browser, modality: str, *, audit: bool, label: str, identity: str = "harness") -> dict:
    """One full journey on a fresh server + workspace + browser context."""
    with studio_server(label, identity) as url:
        context, page = new_page(browser)
        try:
            runner = Runner(page, modality, audit)
            open_studio(page, url)
            if audit:
                runner.checkpoint("start")
            runner.run(journey())
            responsive = runner.responsive_audit() if audit and modality == "pointer" else None
            return {
                "modality": modality, "steps": runner.steps, "operators": runner.operators,
                "pointer_targets": runner.pointer_targets, "views": runner.views,
                "responsive": responsive, "errors": runner.errors, "http_failures": runner.http_failures,
            }
        finally:
            context.close()


def ui_hashes() -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(WEB.iterdir()) if p.is_file()}


def collect(repeats: int = 3, headless: bool = True, identity: str = "harness") -> dict:
    """Run the pointer journey `repeats` times (first one fully audited) plus one keyboard-only pass."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=headless)
        try:
            passes = [run_pass(browser, "pointer", audit=(i == 0), label=f"pointer{i}", identity=identity) for i in range(repeats)]
            keyboard = run_pass(browser, "keyboard", audit=False, label="keyboard", identity=identity)
            environment = {
                "platform": platform.platform(), "python": platform.python_version(), "chrome": browser.version,
                "playwright": importlib.metadata.version("playwright"),
                "axe_playwright_python": importlib.metadata.version("axe-playwright-python"),
                "axe_core": passes[0]["views"]["start"]["axe"]["axe_core"],
                "viewport": VIEWPORT, "headless": headless, "repeats": repeats, "ui_sha256": ui_hashes(),
                "provider": "offline (synthetic)", "identity_source": "pytest-harness" if identity == "harness" else "release (real eija serve)", "device_scale_factor": 1,
            }
        finally:
            browser.close()
    return {"environment": environment, "pointer_passes": passes, "keyboard_pass": keyboard}
