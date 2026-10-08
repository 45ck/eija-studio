"""PlayIDE ripple: change one UML diagram, see the effect on the others, and take the AI's re-checked follow-ons.

Drives the real PlayIDE page (`/play`) of an ephemeral `eija serve` on the library-loan pack, offline. Every step
asserts text the page really renders, so the recording doubles as an e2e check. Follow-on edits come from the offline
rule-based proposer (`offline-plan-fixture-v1`), not a live model, and the video says so (ADR-0158).
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "PlayIDE ripple: change one diagram, see the others follow"
PACK = "packs/library-loan"
BUILD_TIMEOUT_MS = 600_000
CARD = ".msg:last-child"


def run(scene: Scene, server: RunningServer) -> None:
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.title_card("Change one diagram. Watch the others follow.", "PlayIDE: the AI helps, the kernel checks.")
    _draw_a_state(scene)
    _take_the_follow_on(scene)
    _remove_an_action(scene)
    scene.clear_caption()
    scene.title_card("One model. Five diagrams. Every change checked.", "PlayIDE, built on EIJA Studio (Apache-2.0)")


def _draw_a_state(scene: Scene) -> None:
    scene.caption("A library loan as a UML state machine. Drag a new state onto it.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.drag('#draw-palette [data-kind="state"]', "#canvas", position=(width * 0.82, height * 0.82))
    scene.type_text(".draft-form input", "Lost")
    scene.click('.draft-form button[type="submit"]')
    scene.expect_text(f"{CARD} .ripple", "LoanState gains the literal Lost", timeout_ms=60_000)
    scene.caption("The change ripples. Every tab shows how many of its elements it touches.")
    scene.highlight(".tabs", duration_ms=1800)
    scene.caption("Nothing leads into Lost yet, so no record could ever get there. That is a warning.")
    scene.highlight(f"{CARD} .ripple-list", duration_ms=2200)
    scene.click(f"{CARD} .ripple-item:has-text('LoanState gains')")
    scene.expect_text("#inspector", "Class diagram: LoanState gains the literal Lost")
    scene.caption("On the class diagram, the record's state enumeration gains the new literal.")
    scene.highlight("#class-canvas", duration_ms=2000)


def _take_the_follow_on(scene: Scene) -> None:
    scene.caption("The AI proposes a follow-on: a way into Lost. It is offline here, and the server re-checks it.")
    scene.highlight(f"{CARD} .follow-ons", duration_ms=2200)
    scene.click(f"{CARD} .follow-ons li.applies button")
    scene.expect_text(f"{CARD} .plan-verdict", "adds Renew", timeout_ms=60_000)
    scene.expect_text(f"{CARD} .ripple", "New use case Renew", timeout_ms=60_000)
    scene.caption("That ripples too: Renew is a new use case for the Librarian...")
    scene.click(f"{CARD} .ripple-item:has-text('New use case Renew')")
    scene.highlight("#usecase-canvas", duration_ms=1800)
    scene.caption("...it gets its own screen...")
    scene.click(f"{CARD} .ripple-item:has-text('gets a default screen')")
    scene.highlight("#screen-card", duration_ms=1600)
    scene.caption("...and the generated app changes. The component diagram shows which files.")
    scene.click(f"{CARD} .ripple-item:has-text('app/model.json is regenerated')")
    scene.highlight("#component-canvas", duration_ms=1800)
    scene.click("#tab-states")
    scene.caption("Build it: the new app must match the kernel on every conformance case.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.highlight("#score", duration_ms=1400)


def _remove_an_action(scene: Scene) -> None:
    scene.caption("Now a change that breaks another diagram. Ask the AI to remove the late return.")
    scene.type_text("#chat-input", "remove ReturnLate")
    scene.click("#chat-send")
    scene.expect_text(f"{CARD} .ripple", "the diagrams no longer agree", timeout_ms=60_000)
    scene.caption("Its screen is now stranded, so the app cannot be built. Found as you change it, not at build time.")
    scene.highlight(f"{CARD} .ripple-list", duration_ms=2400)
    scene.click(f"{CARD} .ripple-item.problem:has-text('Late return')")
    scene.expect_text("#screen-problems", "SCREEN_UNKNOWN_USE_CASE")
    scene.highlight("#screen-problems", duration_ms=1800)
    scene.caption("The AI proposes removing the screen. The design check confirms it fixes the problem.")
    scene.click(f"{CARD} .follow-ons li:has-text('Remove the screen') button")
    scene.expect_text(f"{CARD} .ripple", "every diagram still agrees", timeout_ms=60_000)
    scene.highlight(f"{CARD} .ripple", duration_ms=1800)
    scene.caption("It also warns that overdue loans are now stuck. You decide; here we build anyway.")
    scene.click("#tab-states")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.click("#health")
    scene.expect_text("#check-list", "They agree")
    scene.caption("The checks ring: each part is a real check, including that the diagrams agree.")
    scene.highlight("#checks", duration_ms=2600)
