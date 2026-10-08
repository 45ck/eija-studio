"""The PlayIDE showcase: software engineering as play, once you think in UML.

The storyboard is docs/demos/PLAYIDE-SHOWCASE-STORYBOARD.md. This script drives the real PlayIDE page (`/play`) of
an ephemeral `eija serve` on the library-loan pack, offline, and asserts what the page really renders, so the take
doubles as an e2e check. Beats whose feature has not merged yet are skipped and named in the manifest (a PARTIAL
take), never faked. The chat's proposer is the offline phrase reader (`offline-plan-fixture-v1`), and the video
says so.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "The PlayIDE showcase: software engineering as play"
PACK = "packs/library-loan"
AI_REQUEST = "add state Archived after Returned then allow Member to CheckOut"
BUILD_TIMEOUT_MS = 600_000

# Beats that wait on work still in progress. Each becomes a real act when its feature merges (see the storyboard).
PENDING = {
    "ripple": "beat 4 (one change ripples across the diagrams, AI proposes the follow-on edits) waits on the "
              "cross-diagram impact feature",
    "review": "beat 6 (review the change as a UML diff in PlayIDE, not a GitHub PR) waits on the in-IDE review view",
    "ship": "beat 8 (verify, approve and apply) waits on the owner's source review and restamp (issue #80)",
}


class _Chapters:
    """Numbers the chapters actually shown, so a skipped beat leaves no gap in the video."""

    def __init__(self, scene: Scene) -> None:
        self.scene, self.n = scene, 0

    def __call__(self, title: str) -> None:
        self.n += 1
        self.scene.chapter(self.n, title)


def run(scene: Scene, server: RunningServer) -> None:
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.title_card("Software engineering, played.",
                     "Design it in UML. Press play. Watch it run. Let the AI do the busywork, and check it.",
                     hold_ms=3400)
    chapter = _Chapters(scene)
    _model_is_the_program(scene, chapter)
    _press_play(scene, chapter)
    _fix_by_dragging(scene, chapter)
    scene.skip(PENDING["ripple"])
    _ai_busywork(scene, chapter)
    scene.skip(PENDING["review"])
    _prove_it(scene, chapter)
    scene.skip(PENDING["ship"])
    scene.clear_caption()
    scene.zoom_out()
    scene.title_card("Less typing. No diff archaeology.",
                     "Review the change, not the code. The app cannot disobey the model. You decide what ships. "
                     "PlayIDE, built on EIJA Studio (Apache-2.0)", hold_ms=4200)


def _model_is_the_program(scene: Scene, chapter: _Chapters) -> None:
    chapter("The model is the program")
    scene.caption("A library loan, as a UML state machine. This diagram is not documentation: it is what runs.")
    scene.zoom("#canvas", scale=1.9)
    scene.wait(2200)
    scene.zoom_out()
    scene.caption("One model, many views: classes, use cases and screens are all drawn from it.", hold_ms=1800)
    for tab, target in (("classes", "#class-canvas"), ("usecases", "#usecase-canvas"), ("screens", "#screen-card")):
        scene.click(f"#tab-{tab}", duration_ms=380)
        scene.highlight(target, duration_ms=900)
    scene.expect_text("#screen-problems", "Design check passed")
    scene.click("#tab-states")


def _press_play(scene: Scene, chapter: _Chapters) -> None:
    chapter("Press play")
    scene.caption("Debug the design, not the code. Select a state and set a breakpoint on it, as you would on a line.")
    scene.click("#outline-states button:has-text('Overdue')")
    scene.click("#inspector button:has-text('Add breakpoint')")
    scene.select_option("#run-speed", "40")
    scene.caption("Press Run. Seeded users act on the model, and the kernel decides every step.")
    scene.click("#run-play")
    scene.expect_text("#run-status", "Paused at step", timeout_ms=60_000)
    scene.caption("It stops where you asked. The current step is marked on the diagram, with who did what and why.")
    scene.zoom("#canvas", scale=1.7)
    scene.wait(1800)
    scene.zoom("#debug", scale=1.5)
    scene.wait(1800)
    scene.zoom_out()
    scene.caption("Now break whenever the kernel refuses, like breaking on exceptions, and continue.")
    scene.check("#break-refusal")
    scene.click("#run-play")
    scene.expect_text("#run-status", "Paused at step", timeout_ms=60_000)
    scene.caption("Thick lines are busy paths. The red step is where someone got stuck, and the kernel says why.")
    scene.zoom("#canvas", scale=1.7)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#run-stop")
    scene.expect_text("#run-status", "Stopped the run")
    scene.caption("Build & run generates the real app and checks every case against the kernel before it starts.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.zoom("#score", scale=1.7)
    scene.wait(900)
    scene.caption("The app runs beside the model, and it cannot disobey it: every decision it makes is the kernel's.")
    scene.zoom("#run", scale=1.3)
    scene.wait(1400)
    scene.zoom_out()
    scene.click("#tab-states")


def _fix_by_dragging(scene: Scene, chapter: _Chapters) -> None:
    chapter("Fix it by dragging, not typing")
    scene.caption("Design in place. Drag a new state from the palette onto the diagram.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.drag('#draw-palette [data-kind="state"]', "#canvas", position=(width * 0.82, height * 0.82))
    scene.type_text(".draft-form input", "Lost")
    scene.click('.draft-form button[type="submit"]')
    scene.expect_text(".plan-verdict", "The policy allows the result")
    scene.caption("Connect it: pick where it goes and who may take it. Three choices, no code.")
    scene.click("#outline-states button:has-text('Overdue')")
    scene.click("#inspector button:has-text('Add a transition from here')")
    scene.select_option(".draft-form label:has-text('To') select", "Lost")
    scene.select_option(".draft-form label:has-text('Action') select", "Renew")
    scene.select_option(".draft-form label:has-text('Who may take it') select", "Librarian")
    scene.click('.draft-form button[type="submit"]')
    scene.expect_text(".plan-verdict", "adds Renew")
    scene.caption("Each gesture is a typed step the policy checks at once. The diagram previews it; nothing is saved.")
    scene.zoom("#canvas", scale=1.8)
    scene.wait(2200)
    scene.zoom_out()


def _ai_busywork(scene: Scene, chapter: _Chapters) -> None:
    chapter("Let the AI do the busywork")
    scene.caption("Ask for a bigger change in plain words. Offline here: a deterministic phrase reader stands in "
                  "for a live model.")
    scene.type_text("#chat-input", AI_REQUEST)
    scene.click("#chat-send")
    card = ".msg.ai:last-child"
    scene.expect_text(f"{card} .plan-verdict", "The policy refuses")
    scene.caption("It answers with typed UML steps, not a wall of code. The policy already refuses one.")
    scene.zoom(f"{card} .plan", scale=1.5)
    scene.wait(1600)
    scene.caption("Look at each step on the diagram. Points come from checking the AI, never from making changes.")
    scene.click(f"{card} .plan-steps > li:nth-child(2) .show")
    scene.expect_text("#inspector", "Let Member take")
    scene.wait(1000)
    scene.caption("Untick the step the policy caught. Keep the rest.")
    scene.click(f"{card} .plan-steps > li:nth-child(2) input")
    scene.expect_text(f"{card} .plan-verdict", "The policy allows the result")
    scene.click(f"{card} .plan-tools .primary")
    scene.expect_text("#plan-banner-text", "Previewing the plan")
    scene.zoom_out()
    scene.click(f"{card} .plan-steps > li:nth-child(1) .show")
    scene.expect_text("#inspector", "State Archived")
    scene.wait(900)


def _prove_it(scene: Scene, chapter: _Chapters) -> None:
    chapter("Prove it, then play again")
    scene.caption("Build the changed system, run its conformance cases, and send the users through again.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.click("#health")
    scene.expect_text("#health-text", "5/5 checks")
    scene.caption("The ring fills only from real checks on what you are looking at. That is the score.")
    scene.zoom("#checks", scale=1.6)
    scene.wait(2400)
