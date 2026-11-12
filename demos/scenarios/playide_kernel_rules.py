"""New in the kernel (November 2026): rules a UML engineer draws, and the kernel enforces, seen in the running PlayIDE.

One unedited take. It opens a library loan with the kernel features of ADR-0231 to ADR-0235 switched on (the same
variant `tests/test_play_kernel_features.py` walks), with the library-fines workflow beside it so its signal
(ADR-0242) is drawn: a guard over record values, one action leaving two states, who may start a record, a
separation-of-duties law, a built reference, and a late return that starts a fine. It builds the app and runs its
conformance suite. Then it starts two systems from shipped templates: the refund desk's composite states and
`after(2 days)` timer (ADR-0240, ADR-0237) and the AI ops deploy that locks its target service (ADR-0241).

Nothing here uses a live model, and nothing is approved or applied. The variant pack is written under `.tmp/` before
the take (`PREPARE_PACK`); no shipped pack changes, and the video says on screen that the rules were switched on.
"""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from demos.lib import RunningServer, Scene

ROOT = Path(__file__).resolve().parents[2]
TITLE = "New in the kernel: rules you draw, the kernel enforces"
PACE = 0.85
BUILD_TIMEOUT_MS = 240_000
GUARD = {"attribute": "renewals", "op": "le", "value": 3}
FOUR_EYES = {"id": "four-eyes", "kind": "distinct_actors", "code": "FOUR_EYES",
             "description": "Whoever checks a loan out does not also take its return.", "actions": ["CheckOut", "Return"]}
__all__ = ["PREPARE_PACK", "TITLE", "prepare_pack", "run"]


def _write(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")


def _rules(pack_dir: Path) -> None:
    """Only members start a loan; CheckOut needs [renewals <= 3]; Return also leaves Overdue; the four-eyes law."""
    doc = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    model = doc["model"]
    model["initiators"] = ["Member"]
    checkout = next(t for t in model["transitions"] if t["action"] == "CheckOut")
    checkout["conditions"] = [GUARD]
    back = copy.deepcopy(next(t for t in model["transitions"] if t["action"] == "Return"))
    model["transitions"].append(back | {"id": "TR-RETURN-OVERDUE", "from_state": "Overdue"})
    doc["laws"].append(FOUR_EYES)
    _write(pack_dir / "pack.json", doc)


def _reference(pack_dir: Path) -> None:
    """The borrower becomes a built reference, so the request screen asks for it."""
    data = json.loads((pack_dir / "data.json").read_text(encoding="utf-8"))
    for link in (a for a in data["associations"] if a["role"] == "borrower"):
        link["built"] = True
    _write(pack_dir / "data.json", data)
    screens = json.loads((pack_dir / "screens.json").read_text(encoding="utf-8"))
    start = next(s for s in screens["screens"] if "use_case" not in s)
    start["fields"].append({"attribute": "borrower", "label": "Borrower"})
    _write(pack_dir / "screens.json", screens)


def _checks_out(scenario: dict) -> bool:
    return any(s["action"] == "CheckOut" and "state" in s["then"] for s in scenario["steps"])


def _test_values(pack_dir: Path) -> None:
    """The tests give the record the values the guard reads."""
    tests = json.loads((pack_dir / "scenarios.json").read_text(encoding="utf-8"))
    for scenario in filter(_checks_out, tests["scenarios"]):
        scenario["values"] = {"renewals": 1}
    _write(pack_dir / "scenarios.json", tests)


def prepare_pack(base: Path | None = None) -> Path:
    """Library loan with the new kernel features (ADR-0231 to ADR-0235), library-fines beside it, under `.tmp/`."""
    base = base or ROOT / ".tmp" / "demo-packs" / "playide_kernel_rules"
    shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True)
    pack_dir = base / "library-loan"
    shutil.copytree(ROOT / "packs" / "library-loan", pack_dir)
    shutil.copytree(ROOT / "packs" / "library-fines", base / "library-fines")
    _rules(pack_dir)
    _reference(pack_dir)
    _test_values(pack_dir)
    return pack_dir


PREPARE_PACK = prepare_pack


class _Chapters:
    def __init__(self, scene: Scene) -> None:
        self.scene, self.n = scene, 0

    def __call__(self, title: str) -> None:
        self.n += 1
        self.scene.chapter(self.n, title, card=True)


def run(scene: Scene, server: RunningServer) -> None:
    scene.pace = PACE
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.title_card("Rules you draw. The kernel enforces them.", "New in November 2026: guards over values, who may "
                     "start, four eyes, references, signals, composite states, timers and linked objects.", hold_ms=3800)
    chapter = _Chapters(scene)
    _values(scene, chapter)
    _several(scene, chapter)
    _starts(scene, chapter)
    _four_eyes(scene, chapter)
    _references(scene, chapter)
    _signals(scene, chapter)
    _prove(scene, chapter)
    _composites(scene, chapter)
    _linked(scene, chapter)
    scene.zoom_out()
    scene.title_card("Draw the rule. The kernel enforces it.", "Every rule here is checked by the kernel, the laws and "
                     "the generated app's tests. PlayIDE, built on EIJA Studio (Apache-2.0)", hold_ms=4400)


def _transition(scene: Scene, tid: str) -> None:
    scene.click(f"#outline-transitions button[data-id='transition:{tid}']")
    scene.wait(500)


def _values(scene: Scene, chapter: _Chapters) -> None:
    chapter("Guards over record values")
    scene.caption("A library loan, with this month's new kernel rules switched on. Start with a guard over values.")
    scene.click("#fit")
    _transition(scene, "TR-CHECKOUT")
    scene.expect_text("#outline-transitions", "CheckOut [renewals ≤ 3]")
    scene.caption("UML's own notation, event [guard]: CheckOut [renewals ≤ 3]. The kernel refuses a fourth renewal.")
    scene.zoom("#canvas text:has-text('renewals')", scale=1.9)
    scene.wait(2200)
    scene.zoom_out()
    scene.click("#tab-access")
    scene.expect_text("#access-panel", "renewals ≤ 3", timeout_ms=30_000)
    scene.caption("The permissions table shows the guard on the action, and which fixture users it lets through.")
    scene.zoom("#access-panel td:has-text('renewals ≤ 3')", scale=1.6)
    scene.wait(2200)
    scene.zoom_out()


def _several(scene: Scene, chapter: _Chapters) -> None:
    chapter("One action from several states")
    _transition(scene, "TR-RETURN-OVERDUE")
    scene.expect_text("#outline-transitions", "Return [Librarian] from Overdue")
    scene.caption("Return now leaves OnLoan and Overdue: one trigger on two transitions, still one rule and one screen.")
    scene.zoom("#outline-transitions", scale=1.8)
    scene.wait(1800)
    scene.zoom_out()
    scene.zoom("#canvas", scale=1.3)
    scene.wait(1800)
    scene.zoom_out()


def _starts(scene: Scene, chapter: _Chapters) -> None:
    chapter("Who may start a record")
    scene.click("#tab-usecases")
    scene.expect_text("#usecase-canvas", "Create", timeout_ms=30_000)
    scene.caption("Only a Member may start a loan. The use case diagram links Member to Create, and the kernel refuses anyone else.")
    scene.zoom("#usecase-canvas text:has-text('Create')", scale=1.6)
    scene.wait(2400)
    scene.zoom_out()


def _four_eyes(scene: Scene, chapter: _Chapters) -> None:
    chapter("Separation of duties")
    scene.click("#tab-laws")
    scene.wait_for("#laws-summary.ok, #laws-summary.bad", timeout_ms=120_000)
    scene.expect_text("#laws-summary", "holds on every run the kernel allows")
    law = "#laws-list > li:has-text('four-eyes')"
    scene.expect_text(law, "Whoever checks a loan out does not also take its return.", timeout_ms=30_000)
    scene.move_to(law)  # scrolls the law into view, under the cursor
    scene.caption("Four eyes, as a law: whoever checks a loan out does not take its return. Proved over every run the kernel allows.")
    scene.zoom(law, scale=1.5)
    scene.wait(2600)
    scene.zoom_out()


def _references(scene: Scene, chapter: _Chapters) -> None:
    chapter("Checked references")
    scene.click("#tab-classes")
    scene.expect_text("#class-canvas", "borrower", timeout_ms=30_000)
    scene.caption("The borrower association is built now: the app stores a member id and refuses one that names nobody.")
    scene.zoom("#class-canvas text:has-text('borrower')", scale=1.7)
    scene.wait(2400)
    scene.zoom_out()


def _signals(scene: Scene, chapter: _Chapters) -> None:
    chapter("Signals between workflows")
    scene.click("#tab-components")
    scene.click("#component-lens button[data-lens=system]")
    scene.expect_text("#landscape-summary", "2 workflows", timeout_ms=30_000)
    scene.expect_text("#landscape", "LateReturn", timeout_ms=30_000)
    scene.caption("A late return sends a signal that starts a fine in the fines workflow. Both ends are checked: "
                  "a signal nobody hears is flagged.")
    scene.zoom("#landscape text:has-text('LateReturn')", scale=1.8)
    scene.wait(2800)
    scene.zoom_out()


def _prove(scene: Scene, chapter: _Chapters) -> None:
    chapter("Prove the app matches")
    scene.click("#tab-states")
    scene.caption("Build the app from the model and run its generated conformance tests against the kernel.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.caption("The suite now also checks who may start, four eyes, value guards and references on the built app.")
    scene.zoom("#score", scale=1.8)
    scene.wait(2200)
    scene.zoom_out()
    scene.click("#tab-tests")
    scene.expect_text("#tests-summary", "pass", timeout_ms=60_000)
    scene.zoom("#tests-summary", scale=1.6)
    scene.wait(1400)
    scene.zoom_out()


def _create_system(scene: Scene, template: str, name: str) -> None:
    def leave(dialog) -> None:  # a plan still open asks before leaving: yes
        dialog.accept()

    scene.click("#system-menu")
    scene.click("#systems-tab-new")
    scene.click(f"#systems-templates input[value={template}]")
    scene.type_text("#systems-name", name, clear=True)
    scene.page.on("dialog", leave)
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.page.remove_listener("dialog", leave)
    scene.reattach("body[data-ready=true]")


def _composites(scene: Scene, chapter: _Chapters) -> None:
    chapter("Composite states and time events")
    scene.caption("A refund desk, from a shipped template.")
    _create_system(scene, "refund-desk", "Refund desk")
    scene.chapter(chapter.n, "Composite states and time events")  # the reload dropped the chip: show it again
    scene.expect_text("#outline-transitions", "after(2 days)")
    scene.click("#tab-states")
    scene.click("#fit")
    _transition(scene, "TR-ESCALATE")
    scene.caption("Deciding is a composite state. If nobody decides, after(2 days) the timer escalates to a supervisor.")
    scene.zoom("#canvas text:has-text('Deciding')", scale=1.6)
    scene.wait(2600)
    scene.zoom_out()
    scene.click("#tab-access")
    scene.expect_text("#access-panel", "TIMER_NOT_DUE", timeout_ms=30_000)
    scene.caption("The timer is an actor too, and the kernel refuses it until the two days have passed.")
    scene.zoom("#access-panel td:has-text('TIMER_NOT_DUE')", scale=1.6)
    scene.wait(2400)
    scene.zoom_out()


def _linked(scene: Scene, chapter: _Chapters) -> None:
    chapter("Actions on linked objects")
    scene.caption("An AI ops deploy, from another template.")
    _create_system(scene, "ai-ops", "AI ops deploys")
    scene.chapter(chapter.n, "Actions on linked objects")
    scene.expect_text("#outline-transitions", "OpenWindow")
    scene.click("#tab-states")
    scene.click("#fit")
    _transition(scene, "TR-WINDOW")
    scene.caption("Opening a deploy window locks its target service: / target.lock. A second window on a busy service is refused.")
    scene.zoom("#canvas text:has-text('target.lock')", scale=1.8)
    scene.wait(2800)
    scene.zoom_out()
