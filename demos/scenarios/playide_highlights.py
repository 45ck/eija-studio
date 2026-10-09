"""The PlayIDE highlights: the showcase's story in about two minutes, for the README.

Same storyboard as the full showcase (docs/demos/PLAYIDE-SHOWCASE-STORYBOARD.md), recorded separately rather than cut
from it, so the take is still one unedited run of the real PlayIDE page and still asserts what the page renders. It
keeps the strongest moment of each beat and shorter captions. The chat's proposer is the offline phrase reader
(`offline-plan-fixture-v1`), and the video says so. Verify, approve and apply wait on issue #80 and are a skipped act.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene
from demos.scenarios.playide_showcase import AI_CARD, AI_REQUEST, BUILD_TIMEOUT_MS, PACK, PENDING, RIPPLE_CARD

PACE = 0.8  # tighter holds and motion than the full showcase; every act and assertion still runs
TITLE = "The PlayIDE highlights: software engineering as play, in two minutes"
__all__ = ["PACK", "TITLE", "run"]


class _Chapters:
    """Numbers the chapters shown, each opened by a short motion-graphic card."""

    def __init__(self, scene: Scene) -> None:
        self.scene, self.n = scene, 0

    def __call__(self, title: str) -> None:
        self.n += 1
        self.scene.chapter(self.n, title, card=True)


def run(scene: Scene, server: RunningServer) -> None:
    scene.pace = PACE
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.title_card("Software engineering, played.", "Design it in UML. Press play. Let the AI do the busywork, "
                     "and catch what it gets wrong.", hold_ms=3400)
    chapter = _Chapters(scene)
    _design(scene, chapter)
    _play(scene, chapter)
    _edit(scene, chapter)
    _ai(scene, chapter)
    _catch(scene, chapter)
    _prove(scene, chapter)
    scene.skip(PENDING["ship"])
    scene.zoom_out()
    scene.title_card("Then the owner ships it", "Verify, approve and apply stay with the owner. Not shown yet: they "
                     "wait on the owner's source review (issue #80).", hold_ms=3000)
    scene.title_card("Less typing. No diff archaeology.", "Review the change, not the code. The app cannot disobey "
                     "the model. PlayIDE, built on EIJA Studio (Apache-2.0)", hold_ms=4200)


def _design(scene: Scene, chapter: _Chapters) -> None:
    chapter("The model is the program")
    scene.caption("A library loan as a UML state machine. It is not documentation: it is what runs.")
    scene.zoom("#canvas", scale=1.8)
    scene.wait(1000)
    scene.zoom_out()
    scene.caption("Classes and use cases are drawn from the same model.", hold_ms=1400)
    for tab, target in (("classes", "#class-canvas"), ("usecases", "#usecase-canvas")):
        scene.click(f"#tab-{tab}", duration_ms=340)
        scene.highlight(target, duration_ms=800)
        scene.wait(500)
    scene.click("#tab-states", duration_ms=340)


def _play(scene: Scene, chapter: _Chapters) -> None:
    chapter("Press play")
    scene.caption("Set a breakpoint on a state, like on a line of code, and press Run.")
    scene.click("#outline-states button:has-text('Overdue')")
    scene.click("#inspector button:has-text('Add breakpoint')")
    scene.select_option("#run-speed", "40")
    scene.click("#run-play")
    scene.expect_text("#run-status", "Paused at step", timeout_ms=60_000)
    scene.caption("Seeded users act, the kernel decides every step, and it stops where you asked.")
    scene.zoom("#canvas", scale=1.7)
    scene.wait(1500)
    scene.zoom_out()
    scene.click("#run-stop")
    scene.expect_text("#run-status", "Stopped the run")
    scene.click("#dock-close")


def _edit(scene: Scene, chapter: _Chapters) -> None:
    chapter("Edit in place, watch it ripple")
    scene.caption("Pick State, click the diagram, type the name. No code.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.click('#draw-palette [data-kind="state"]')
    scene.click_at("#canvas", (width * 0.82, height * 0.82))
    scene.type_text(".inline-edit input", "Lost")
    scene.click('.inline-edit button[type="submit"]')
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "LoanState gains the literal Lost", timeout_ms=60_000)
    scene.caption("The change ripples: the class diagram gains the literal, and nothing leads into Lost yet.")
    scene.zoom(f"{RIPPLE_CARD} .ripple-list", scale=1.5)
    scene.wait(1300)
    scene.zoom_out()
    scene.caption("The AI proposes a way in, the server re-checks it, and it ripples on.")
    scene.click(f"{RIPPLE_CARD} .follow-ons li.applies button")
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "New use case Renew", timeout_ms=60_000)


def _ai(scene: Scene, chapter: _Chapters) -> None:
    chapter("Let the AI do the busywork")
    scene.caption("Ask in plain words. Offline here: a phrase reader stands in for a live model.")
    scene.type_text("#chat-input", AI_REQUEST)
    scene.click("#chat-send")
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result")
    scene.caption("Typed UML steps, not a wall of code, and the policy allows them. Looks fine. Is it?")
    for step in (1, 2):
        scene.click(f"{AI_CARD} .plan-steps > li:nth-child({step}) .show")
        scene.wait(400)
    scene.click("#tab-states")
    scene.click("#show-changes")
    scene.wait_for(".diff-item", timeout_ms=30_000)
    scene.caption("Both models on one layout: added in green, the removed arrow kept as a ghost.")
    scene.zoom("#diff-view", scale=1.3)
    scene.wait(1400)
    scene.zoom_out()


def _catch(scene: Scene, chapter: _Chapters) -> None:
    chapter("Review the change, not the code")
    scene.click(f"{AI_CARD} .plan-tools .review-it")
    scene.expect_text("#review-head-text", "2 changes: 1 high risk")
    scene.caption("Predict before you see the answer: can a librarian still return an overdue loan?")
    scene.click("#review-item-1 .show")
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Not what you expected")
    scene.caption("The kernel says no. The AI quietly deleted late returns, and your wrong guess caught it.")
    scene.zoom("#review-item-1", scale=1.6)
    scene.wait(1400)
    scene.zoom_out()
    scene.click("#tab-tests")
    scene.expect_text("#tests-summary", "1 of 7 tests fail", timeout_ms=60_000)
    scene.caption("A scenario test agrees, and shows the step that breaks on the diagram.")
    scene.click("#tests-list li.broken button:has-text('Show on diagram')")
    scene.zoom("#canvas", scale=1.3)
    scene.wait(1400)
    scene.zoom_out()
    scene.caption("Reject that step. The review runs again on what is left.")
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.click("#tab-review")
    scene.expect_text("#review-head-text", "1 change: 0 high risk")
    scene.zoom("#review-head-text", scale=1.6)
    scene.wait(900)
    scene.zoom_out()


def _prove(scene: Scene, chapter: _Chapters) -> None:
    chapter("Prove it")
    scene.caption("Build the changed app, check every conformance case, and simulate the users again.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.click("#tab-laws")
    scene.wait_for("#laws-summary.ok, #laws-summary.bad", timeout_ms=120_000)
    scene.expect_text("#laws-summary", "holds on every run the kernel allows")
    scene.caption("Every law holds on every run the kernel allows.")
    scene.zoom("#laws", scale=1.3)
    scene.wait(1300)
    scene.zoom_out()
    scene.click("#tab-tests")
    scene.expect_text("#tests-summary", "All 7 tests pass", timeout_ms=60_000)
    scene.click("#tab-states")
    scene.click("#health")
    scene.expect_text("#health-text", "5/5 checks")
    scene.caption("The ring fills only from real checks on what you are looking at.")
    scene.zoom("#checks", scale=1.6)
    scene.wait(1500)
    scene.zoom_out()
