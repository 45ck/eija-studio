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
AI_REQUEST = "add Renew from Overdue to OnLoan for Librarian then remove transition ReturnLate"
BUILD_TIMEOUT_MS = 600_000
AI_CARD = ".msg.ai:last-child"
RIPPLE_CARD = ".msg:last-child"  # the chat card that shows a drawn change's ripple (ADR-0158)

# Beats that wait on work still in progress. Each becomes a real act when its feature merges (see the storyboard).
PENDING = {
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
    _ripple(scene, chapter)
    _ai_busywork(scene, chapter)
    _review(scene, chapter)
    _prove_it(scene, chapter)
    scene.skip(PENDING["ship"])
    scene.clear_caption()
    scene.title_card("Then the owner ships it", "Verify, approve and apply stay with the owner in the review workbench. "
                     "Not shown yet: they wait on the owner's source review (issue #80).", hold_ms=3600)
    _stakeholder_view(scene, chapter, server)
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
    scene.click("#dock-close")  # give the diagram the room back; Simulate reopens the panel
    scene.click("#tab-states")


def _fix_by_dragging(scene: Scene, chapter: _Chapters) -> None:
    chapter("Fix it by dragging, not typing")
    scene.caption("Design in place. Drag a new state from the palette onto the diagram.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.drag('#draw-palette [data-kind="state"]', "#canvas", position=(width * 0.82, height * 0.82))
    scene.type_text(".draft-form input", "Lost")
    scene.click('.draft-form button[type="submit"]')
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "LoanState gains the literal Lost", timeout_ms=60_000)
    scene.caption("Each gesture is a typed step the policy checks at once. The diagram previews it; nothing is saved.")
    scene.zoom("#canvas", scale=1.8)
    scene.wait(1800)
    scene.zoom_out()


def _ripple(scene: Scene, chapter: _Chapters) -> None:
    chapter("Watch it ripple")
    scene.caption("One change ripples through the whole model. Every tab counts the elements it touches.")
    scene.zoom(".tabs", scale=1.8)
    scene.wait(1600)
    scene.zoom_out()
    scene.caption("And it catches what you missed: nothing leads into Lost yet, so no record could ever get there.")
    scene.zoom(f"{RIPPLE_CARD} .ripple-list", scale=1.5)
    scene.wait(1800)
    scene.zoom_out()
    scene.click(f"{RIPPLE_CARD} .ripple-item:has-text('LoanState gains')")
    scene.expect_text("#inspector", "Class diagram: LoanState gains the literal Lost")
    scene.caption("On the class diagram, the record's state enumeration gains the new literal.")
    scene.zoom("#class-canvas", scale=1.4)
    scene.wait(1600)
    scene.zoom_out()
    scene.caption("The AI proposes the follow-on: a way into Lost. Offline here, and the server re-checks it.")
    scene.zoom(f"{RIPPLE_CARD} .follow-ons", scale=1.5)
    scene.wait(1400)
    scene.zoom_out()
    scene.click(f"{RIPPLE_CARD} .follow-ons li.applies button")
    scene.expect_text(f"{RIPPLE_CARD} .plan-verdict", "adds Renew", timeout_ms=60_000)
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "New use case Renew", timeout_ms=60_000)
    scene.caption("That ripples too: Renew becomes a use case for the Librarian, with its own screen.")
    scene.click(f"{RIPPLE_CARD} .ripple-item:has-text('New use case Renew')")
    scene.zoom("#usecase-canvas", scale=1.3)
    scene.wait(1600)
    scene.zoom_out()
    scene.click(f"{RIPPLE_CARD} .ripple-item:has-text('gets a default screen')")
    scene.highlight("#screen-card", duration_ms=1400)
    scene.click("#tab-states")


def _ai_busywork(scene: Scene, chapter: _Chapters) -> None:
    chapter("Let the AI do the busywork")
    scene.caption("Ask for a bigger change in plain words: let librarians renew overdue loans. Offline here: a "
                  "deterministic phrase reader stands in for a live model.")
    scene.type_text("#chat-input", AI_REQUEST)
    scene.click("#chat-send")
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result")
    scene.caption("It answers with typed UML steps, not a wall of code, and the policy allows them. Looks fine. Is it?")
    scene.zoom(f"{AI_CARD} .plan", scale=1.5)
    scene.wait(1800)
    scene.zoom_out()
    scene.caption("Look at each step on the diagram. Points come from checking the AI, never from making changes.")
    for step in (1, 2):
        scene.click(f"{AI_CARD} .plan-steps > li:nth-child({step}) .show")
        scene.wait(900)
    scene.click("#tab-states")
    scene.click("#show-changes")
    scene.wait_for(".diff-item", timeout_ms=30_000)
    scene.caption("Changes draws both models on one layout: added in green, the removed arrow kept as a dashed ghost.")
    scene.expect_text(".diff-summary", "changes:")
    scene.zoom("#diff-view", scale=1.3)
    scene.wait(1800)
    scene.zoom_out()
    scene.caption("Step through the changes like hunks in a code review. Compare flips between before and after; nothing moves.")
    scene.click("#diff-view button[aria-label='Next change']")
    scene.expect_text("#diff-pos", "Change 1 of")
    scene.wait(900)
    scene.click("#diff-view button[aria-label='Next change']")
    scene.wait(900)
    scene.click("#diff-compare")
    scene.click(".lens button[data-lens=before]")
    scene.wait(1100)
    scene.click(".lens button[data-lens=after]")
    scene.wait(1100)
    scene.click(".lens button[data-lens=changes]")
    scene.wait(700)


def _review(scene: Scene, chapter: _Chapters) -> None:
    chapter("Review the change, not the code")
    scene.click(f"{AI_CARD} .plan-tools .review-it")
    scene.expect_text("#review-head-text", "2 changes: 1 high risk")
    scene.caption("Both models on one diagram: the new path in green, the deleted path dashed in red.")
    scene.zoom("#review-canvas", scale=1.4)
    scene.wait(2000)
    scene.zoom_out()
    scene.caption("The riskiest change comes first. Before the kernel's answer is shown, predict it: can a librarian "
                  "still return an overdue loan?")
    scene.click("#review-item-1 .show")
    scene.expect_text("#review-item-1", "Remove ReturnLate")
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Not what you expected")
    scene.caption("The kernel says no. The AI quietly deleted late returns, and your wrong guess caught it.")
    scene.zoom("#review-item-1", scale=1.6)
    scene.wait(2200)
    scene.zoom_out()
    scene.click("#review-item-1 .verdict-tools button:has-text('Needs a change')")
    scene.type_text("#review-item-1 textarea", "Keep ReturnLate: an overdue loan must still be returnable.")
    scene.click("#review-item-2 .show")
    scene.click("#review-item-2 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-2 .answer", "Right")
    scene.click("#review-item-2 .verdict-tools button:has-text('Looks right')")
    scene.click("#review-finish")
    scene.expect_text("#review-summary", "Changes requested: 1 of 2")
    scene.caption("Reject the step that deleted late returns. The review runs again on what is left, and it passes.")
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.expect_text("#review-head-text", "1 change: 0 high risk")
    scene.click("#review-item-1 .show")
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Right")
    scene.click("#review-item-1 .verdict-tools button:has-text('Looks right')")
    scene.click("#review-finish")
    scene.expect_text("#review-summary", "Every change looks right")
    scene.zoom("#review-summary", scale=1.6)
    scene.wait(1600)
    scene.zoom_out()


def _stakeholder_view(scene: Scene, chapter: _Chapters, server: RunningServer) -> None:
    chapter("Share it as UML")
    scene.goto(f"{server.base_url}/play?view=review#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.expect_text("#review-badge", "Review view")
    scene.caption("A stakeholder opens the same UML read-only: the diagrams, who may do what, and the runs. No "
                  "editing tools, no chat.")
    scene.zoom("#review-badge", scale=1.8)
    scene.wait(1400)
    scene.zoom_out()
    scene.click("#tab-access")
    scene.caption("Permissions answer the question a stakeholder actually asks: who can do what, and from where.")
    scene.zoom("#access-panel", scale=1.3)
    scene.wait(2200)
    scene.zoom_out()


def _prove_it(scene: Scene, chapter: _Chapters) -> None:
    chapter("Prove it, then play again")
    scene.caption("Build the changed system, run its conformance cases, and send the users through again.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.caption("Then prove the laws: every rule the policy states, checked over every run the kernel allows.")
    scene.click("#tab-laws")
    scene.wait_for("#laws-summary.ok, #laws-summary.bad", timeout_ms=120_000)
    scene.expect_text("#laws-summary", "holds on every run the kernel allows")
    scene.caption("Every law holds on every reachable run, and the summary says how far the proof searched.")
    scene.zoom("#laws", scale=1.3)
    scene.wait(2200)
    scene.zoom_out()
    scene.click("#tab-states")
    scene.click("#health")
    scene.expect_text("#health-text", "5/5 checks")
    scene.caption("The ring fills only from real checks on what you are looking at. That is the score.")
    scene.zoom("#checks", scale=1.6)
    scene.wait(2400)
