"""Greenfield in PlayIDE: a new app built in chat, round after round (ADR-0201).

The storyboard is docs/demos/PLAYIDE-GREENFIELD-STORYBOARD.md. This script drives the real PlayIDE page (`/play`) of
an ephemeral `eija serve`, offline, starts a new system from a three-line sketch, and builds it in five asks: a new
feature, a new requirement, a rename, a new role, and going back on the first decision. After every round it reads the
change in the Changes view (that round alone, then every round), and at the end builds the app and runs it. Every
step asserts what the page renders, so the take doubles as an end-to-end check. The chat's proposer is the offline
phrase reader (`offline-plan-fixture-v1`), and the video says so. Nothing is approved or applied.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "Greenfield in PlayIDE: build a new app in chat, round after round"
PACE = 0.8
SKETCH = "Placed -> Brewing : Start [Barista]\nBrewing -> Ready : Finish [Barista]\nReady -> Collected : Collect [Customer]"
CARD = ".msg.ai:last-child"  # the plan card moves under the latest ask
BUILD_TIMEOUT_MS = 600_000
ROUNDS = (
    "add Cancel from Placed to Cancelled for Customer",
    "add Pay from Placed to Paid for Customer then move Start source to Paid",
    "rename state Ready to AwaitingPickup",
    "allow Manager to Cancel",
    "remove state Cancelled",
)
__all__ = ["TITLE", "run"]


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
    scene.title_card("Greenfield, in UML", "A new app from three lines, built in chat one small ask at a time. "
                     "Every round is checked by the kernel, and you can read each one.", hold_ms=3600)
    chapter = _Chapters(scene)
    _sketch(scene, chapter)
    _feature(scene, chapter)
    _requirement(scene, chapter)
    _rename_and_role(scene, chapter)
    _change_your_mind(scene, chapter)
    _run_it(scene, chapter)
    scene.zoom_out()
    scene.title_card("Vibe-code it. Then read it.", "Fast asks, typed UML steps, the kernel's verdict on every round. "
                     "Offline proposer; nothing is applied until the owner says so. PlayIDE, built on EIJA Studio "
                     "(Apache-2.0)", hold_ms=4600)


def _ask(scene: Scene, text: str) -> None:
    scene.type_text("#chat-input", text, clear=True)
    scene.click("#chat-send")


def _changes(scene: Scene, scope: str) -> None:
    """Open the Changes view on `scope` ("round" or "all") and wait until To consider has its answers."""
    if scene.page.get_attribute("#show-changes", "aria-pressed") != "true":
        scene.click("#show-changes")
    scene.wait_for(".diff-scope", timeout_ms=30_000)
    scene.click(f'.diff-scope [data-scope="{scope}"]', duration_ms=380)
    scene.wait_for(f'.diff-scope [data-scope="{scope}"][aria-checked="true"]', timeout_ms=30_000)
    scene.wait_for("#diff-consider li.ok, #diff-consider li.muted:has-text('no laws')", timeout_ms=60_000)


def _close_changes(scene: Scene) -> None:
    if scene.page.get_attribute("#show-changes", "aria-pressed") == "true":
        scene.click("#show-changes")


def _sketch(scene: Scene, chapter: _Chapters) -> None:
    chapter("Start from three lines")
    scene.caption("A coffee order, sketched in the state machine's own label notation: From -> To : Action [Role].")
    scene.click("#system-menu")
    scene.click("#systems-tab-new")
    scene.click("#systems-templates input[value=blank]")
    scene.type_text("#systems-name", "Coffee orders", clear=True)
    scene.type_text("#systems-record", "Order", clear=True)
    scene.type_text("#systems-sketch", SKETCH, clear=True, delay_range_ms=(20, 55))
    scene.wait_for("#systems-check.ok", timeout_ms=30_000)
    scene.expect_text("#systems-check", "4 states (starts in Placed)")
    scene.caption("The kernel checks the sketch as you type.")
    scene.zoom("#systems-check", scale=1.5)
    scene.wait(1300)
    scene.zoom_out()
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "Collected")
    scene.chapter(chapter.n, "Start from three lines")  # the reload dropped the chip: show it again
    scene.caption("That is a running system already: a state machine, a record class, use cases and an app.")
    scene.zoom("#canvas", scale=1.5)
    scene.wait(1200)
    scene.zoom_out()


def _feature(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 1: a feature")
    scene.caption("Ask for what the system lacks. Offline here: a phrase reader stands in for a live model.")
    _ask(scene, ROUNDS[0])
    scene.expect_text(f"{CARD} .plan-verdict", "The policy allows the result")
    scene.expect_text(f"{CARD} .plan-steps", "new action Cancel")
    scene.caption("Two typed UML steps: the state it needs, then the transition. Cancel is a new action, declared the "
                  "way a sketch declares one.")
    scene.zoom(CARD, scale=1.4)
    scene.wait(1800)
    scene.zoom_out()
    scene.click(f"{CARD} .plan-tools .primary")  # preview it on the diagram
    scene.wait_for("#plan-banner:not([hidden])", timeout_ms=30_000)
    scene.zoom("#canvas", scale=1.5)
    scene.wait(1200)
    scene.zoom_out()


def _requirement(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 2: a new requirement")
    scene.caption("Customers pay before brewing starts. The ask is planned on top of round 1, not instead of it.")
    _ask(scene, ROUNDS[1])
    scene.expect_text(f"{CARD} .plan-summary", "2 rounds")
    scene.expect_text(f"{CARD} .plan-verdict", "The policy allows the result")
    scene.zoom(f"{CARD} .round-head >> nth=-1", scale=1.5)
    scene.wait(1000)
    scene.zoom_out()
    _changes(scene, "round")
    scene.expect_text(".diff-summary", "3 changes")
    scene.caption("Read this round alone: Paid is new, Pay is new, and Start moved. Its old route stays as a ghost.")
    scene.zoom("#diff-view", scale=1.3)
    scene.wait(2000)
    scene.zoom_out()
    scene.caption("And what to consider about this round: the other diagrams it changes and the tests it adds.")
    scene.zoom("#diff-consider", scale=1.6)
    scene.wait(1800)
    scene.zoom_out()
    _close_changes(scene)


def _rename_and_role(scene: Scene, chapter: _Chapters) -> None:
    chapter("Rounds 3 and 4: rename, and a new role")
    _ask(scene, ROUNDS[2])
    scene.expect_text(f"{CARD} .plan-summary", "3 rounds")
    scene.caption("Rename a state. Every transition that touches it follows.")
    _ask(scene, ROUNDS[3])
    scene.expect_text(f"{CARD} .plan-steps", "new role Manager")
    scene.expect_text(f"{CARD} .plan-verdict", "New in this system: actions Cancel, Pay; role Manager")
    scene.caption("A manager may cancel too. Manager is a new role, with a test user, and the verdict says what is new.")
    scene.zoom(f"{CARD} .plan-verdict", scale=1.6)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#tab-access")
    scene.wait_for("#access-panel table", timeout_ms=60_000)
    scene.caption("Who can do what, from each state, every cell tried in the kernel.")
    scene.zoom("#access-panel", scale=1.3)
    scene.wait(1500)
    scene.zoom_out()
    scene.click("#tab-states")


def _change_your_mind(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 5: change your mind")
    scene.caption("No cancelling after all. Removing a state that is in use removes its transition first, as its own step.")
    _ask(scene, ROUNDS[4])
    scene.expect_text(f"{CARD} .plan-summary", "5 rounds")
    scene.expect_text(f"{CARD} .plan-verdict", "The policy allows the result")
    _changes(scene, "round")
    scene.expect_text(".diff-summary", "removed")
    scene.caption("This round removes Cancelled and Cancel: drawn as faded ghosts, never just gone.")
    scene.zoom("#diff-view", scale=1.3)
    scene.wait(1800)
    scene.zoom_out()
    _changes(scene, "all")
    scene.caption("Every round together, against the sketch you started from: the system you built.")
    scene.zoom("#diff-view", scale=1.25)
    scene.wait(2000)
    scene.zoom_out()
    _close_changes(scene)
    scene.caption("Each step stays in the plan, tagged AI or You. Untick any one and everything is checked again.")
    scene.zoom(CARD, scale=1.25)
    scene.wait(1500)
    scene.zoom_out()


def _run_it(scene: Scene, chapter: _Chapters) -> None:
    chapter("Run it, every round")
    scene.caption("Build the app from the model, check every conformance case, and simulate users on it.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.wait_for("#run-frame", timeout_ms=60_000)
    scene.zoom("#run", scale=1.3)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.caption("Save keeps every round, with what you asked, to carry on later. Nothing is applied.")
    scene.click("#system-save")
    scene.expect_text("#system-saved", "Saved", timeout_ms=30_000)
    scene.zoom("#system-controls", scale=1.6)
    scene.wait(1300)
    scene.zoom_out()
