"""Greenfield in PlayIDE: describe an app, get every view, then build it with chat and the canvas (ADR-0201..0203).

The storyboard is docs/demos/PLAYIDE-GREENFIELD-STORYBOARD.md. This script drives the real PlayIDE page (`/play`) of
an ephemeral `eija serve`, offline. It starts the way Lovable or Replit do: one box to describe the app, which makes
every model and view (state machine, class diagram, use cases, screens, tests and sequences, components). Then it mixes
chat asks with direct edits on the diagram: a new requirement, a state drawn by hand, the fields the form needs, a
rename and a role, and going back on a decision. What's missing, across every view, says what is not ready after each
round. It ends by building the app and running it. Every step asserts what the page renders, so the take doubles as an
end-to-end check. The describer and the chat's proposer are the offline readers, and the video says so. Nothing is
approved or applied.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "Greenfield in PlayIDE: describe an app, get every view, then build it in chat and on the canvas"
PACE = 0.8
DESCRIPTION = ("A coffee shop app. Customers order drinks, baristas make them, then customers collect them. "
               "Orders have a size (small, medium, large) and notes.")
CARD = ".msg.ai:last-child"  # the plan card moves under the latest ask
BUILD_TIMEOUT_MS = 600_000
ROUNDS = (
    "add Pay from Placed to Paid for Customer then move Start source to Paid",
    "add Refund from Paid to Refunded for Barista",
    "add field pickupTime as text then make size required",
    "rename state Ready to AwaitingPickup then allow Manager to Cancel",
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
    scene.title_card("Greenfield, in UML", "Describe an app in one box and get every model and view of it. Then change "
                     "it in chat or on the diagram, and see what is still missing.", hold_ms=3600)
    chapter = _Chapters(scene)
    _describe(scene, chapter)
    _every_view(scene, chapter)
    _requirement(scene, chapter)
    _by_hand(scene, chapter)
    _fields(scene, chapter)
    _rename_and_role(scene, chapter)
    _change_your_mind(scene, chapter)
    _run_it(scene, chapter)
    scene.zoom_out()
    scene.title_card("Vibe-code it. Then read it.", "Describe it, ask, drag, and read every round in UML with what is "
                     "missing. Offline describer and proposer; nothing is applied until the owner says so. PlayIDE, built "
                     "on EIJA Studio (Apache-2.0)", hold_ms=4600)


def _ask(scene: Scene, text: str) -> None:
    scene.type_text("#chat-input", text, clear=True)
    scene.click("#chat-send")


def _missing(scene: Scene, text: str, caption: str, scale: float = 1.6) -> None:
    scene.expect_text("#missing", text, timeout_ms=60_000)
    scene.caption(caption)
    scene.zoom("#missing", scale=scale)
    scene.wait(1700)
    scene.zoom_out()


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


def _describe(scene: Scene, chapter: _Chapters) -> None:
    chapter("Describe it")
    scene.caption("Start like Lovable or Replit: say what the app is for, who does what, and what it records.")
    scene.click("#system-new")
    scene.wait_for("#systems-describe", timeout_ms=30_000)
    scene.type_text("#systems-describe", DESCRIPTION, clear=True, delay_range_ms=(12, 35))
    scene.type_text("#systems-name", "Coffee shop", clear=True)
    scene.wait_for("#systems-described", timeout_ms=30_000)
    scene.expect_text("#systems-described", "3 recorded by the kernel")
    scene.caption("Before anything is made, every view it will have, checked by the kernel. The reader is offline: "
                  "a fixed set of app shapes, and it says what it assumed.")
    scene.zoom("#systems-check", scale=1.35)
    scene.wait(2600)
    scene.zoom_out()
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "Collected")
    scene.chapter(chapter.n, "Describe it")  # the reload dropped the chip: show it again


def _every_view(scene: Scene, chapter: _Chapters) -> None:
    chapter("Every model and view")
    scene.caption("A running system already: the state machine, from the shape it read and the roles you named.")
    scene.zoom("#canvas", scale=1.35)
    scene.wait(1300)
    scene.zoom_out()
    scene.click("#tab-classes")
    scene.wait_for("#class-canvas svg", timeout_ms=30_000)
    scene.expect_text("#class-canvas", "size")
    scene.caption("The class diagram, with the fields you described: the built app's form.")
    scene.zoom("#class-canvas", scale=1.4)
    scene.wait(1300)
    scene.zoom_out()
    scene.click("#tab-sequences")
    scene.expect_text("body", "Order reaches Collected", timeout_ms=30_000)
    scene.caption("Test cases recorded by the kernel, drawn as sequence diagrams: the way to each end, and one refusal.")
    scene.wait(1800)
    scene.click("#tab-states")
    _missing(scene, "No laws", "What's missing, across every view. No law is written for you: laws are yours to set.")


def _requirement(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 1: a new requirement")
    scene.caption("Customers pay before brewing starts. Ask in chat. Offline here: a phrase reader stands in for a live model.")
    _ask(scene, ROUNDS[0])
    scene.expect_text(f"{CARD} .plan-verdict", "The policy allows the result")
    scene.expect_text(f"{CARD} .plan-steps", "new action Pay")
    scene.zoom(CARD, scale=1.35)
    scene.wait(1500)
    scene.zoom_out()
    scene.click(f"{CARD} .plan-tools .primary")  # preview it on the diagram
    scene.wait_for("#plan-banner:not([hidden])", timeout_ms=30_000)
    scene.expect_text("#missing", "No test takes Pay", timeout_ms=60_000)
    _missing(scene, "Order reaches Collected” fails", "What's missing follows the work in progress: no test takes Pay yet, and the "
             "recorded way to Collected now fails, because paying comes first. Tests pin down what the kernel did.")


def _by_hand(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 2: draw it, then ask")
    scene.caption("Or drag a state onto the diagram, like draw.io, and type its name.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.drag('#draw-palette [data-kind="state"]', "#canvas", position=(width * 0.84, height * 0.55))
    scene.type_text(".inline-edit input", "Refunded")
    scene.click('.inline-edit button[type="submit"]')
    _missing(scene, "Refunded cannot be reached", "Nothing leads into Refunded yet, and the list says so.")
    _ask(scene, ROUNDS[1])
    scene.expect_text(f"{CARD} .plan-steps", "new action Refund")
    scene.expect_text("#missing", "No test takes Refund", timeout_ms=60_000)
    scene.caption("Mixed: your drawn state and the AI's transition, each tagged You or AI. The reachability problem is gone.")
    scene.zoom(CARD, scale=1.3)
    scene.wait(1600)
    scene.zoom_out()


def _fields(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 3: the form")
    _ask(scene, ROUNDS[2])
    scene.expect_text(f"{CARD} .plan-verdict", "Order gains pickupTime")
    scene.click("#tab-classes")
    scene.wait_for("#class-canvas svg", timeout_ms=30_000)
    scene.expect_text("#class-canvas", "+ pickupTime")
    scene.caption("The class diagram shows the draft: pickupTime is new, size is now required. The built app's form follows.")
    scene.zoom("#class-canvas", scale=1.4)
    scene.wait(1700)
    scene.zoom_out()
    scene.click("#tab-states")


def _rename_and_role(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 4: rename, and a new role")
    _ask(scene, ROUNDS[3])
    scene.expect_text(f"{CARD} .plan-steps", "new role Manager")
    scene.expect_text(f"{CARD} .plan-verdict", "role Manager")
    scene.caption("Every transition follows the rename. Manager is a new role with a test user, and the verdict says what is new.")
    scene.zoom(f"{CARD} .plan-verdict", scale=1.6)
    scene.wait(1600)
    scene.zoom_out()
    _changes(scene, "round")
    scene.caption("Read this round alone in the Changes view, with what to consider.")
    scene.zoom("#diff-view", scale=1.25)
    scene.wait(1600)
    scene.zoom_out()
    _close_changes(scene)


def _change_your_mind(scene: Scene, chapter: _Chapters) -> None:
    chapter("Round 5: change your mind")
    scene.caption("No cancelling after all. Removing a state that is in use removes its transition first, as its own step.")
    _ask(scene, ROUNDS[4])
    scene.expect_text(f"{CARD} .plan-summary", "rounds")
    scene.expect_text(f"{CARD} .plan-verdict", "The policy allows the result")
    _missing(scene, "Order reaches Cancelled” fails", "Cancelling is gone, so its recorded test fails too. The list points you to Tests.")
    _changes(scene, "all")
    scene.caption("Every round together, against what you described: the system you built.")
    scene.zoom("#diff-view", scale=1.25)
    scene.wait(2000)
    scene.zoom_out()
    _close_changes(scene)


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
    scene.expect_text("#status-saved", "Saved", timeout_ms=30_000)
    scene.zoom("#system-controls", scale=1.6)
    scene.wait(1300)
    scene.zoom_out()
