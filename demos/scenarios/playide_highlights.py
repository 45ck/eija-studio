"""The PlayIDE highlights: the showcase's story in about two minutes, for the README.

Same storyboard as the full showcase (docs/demos/PLAYIDE-SHOWCASE-STORYBOARD.md), recorded separately rather than cut
from it, so the take is still one unedited run of the real PlayIDE page and still asserts what the page renders. It
keeps the strongest moment of each beat and shorter captions. The chat's proposer is the offline phrase reader
(`offline-plan-fixture-v1`), and the video says so. Verify, approve and apply wait on issue #80 and are a skipped act.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene
from demos.scenarios.playide_showcase import (
    AGENT_RISKY,
    AI_CARD,
    AI_REQUEST,
    BUILD_TIMEOUT_MS,
    PACK,
    PENDING,
    RIPPLE_CARD,
    _test_renew,
)

PACE = 0.75  # tighter holds and motion than the full showcase; every act and assertion still runs
TITLE = "The PlayIDE highlights: design the whole system, then play it"
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
    scene.title_card("Design the whole system. Then play it.", "People, AI agents and software in one UML model. "
                     "Understand every change, yours and the AI's, before you accept it.", hold_ms=3800)
    chapter = _Chapters(scene)
    _design(scene, chapter)
    _edit(scene, chapter)
    _ai(scene, chapter)
    _catch(scene, chapter)
    _prove(scene, chapter)
    _people(scene, chapter)
    _agents(scene, chapter)
    scene.skip(PENDING["ship"])
    scene.zoom_out()
    scene.title_card("Then the owner ships it", "Verify, approve and apply stay with the owner. Not shown yet: they "
                     "wait on the owner's source review (issue #80).", hold_ms=3000)
    scene.title_card("Design the people, the agents and the software.", "Review the change, not the code. The app "
                     "cannot disobey the model. PlayIDE, built on EIJA Studio (Apache-2.0)", hold_ms=4400)


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


def _edit(scene: Scene, chapter: _Chapters) -> None:
    chapter("Your change, at a glance")
    scene.caption("Drag a state onto the diagram. It lands exactly where you drop it. Type its name: no code.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.drag('#draw-palette [data-kind="state"]', "#canvas", position=(width * 0.82, height * 0.82))
    scene.type_text(".inline-edit input", "Lost")
    scene.click('.inline-edit button[type="submit"]')
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "LoanState gains the literal Lost", timeout_ms=60_000)
    scene.click("#show-changes")
    scene.wait_for(".diff-item", timeout_ms=30_000)
    scene.expect_text(".diff-summary", "1 change")
    scene.caption("Your own edit is drawn like any change: what is new is green, on the diagram you know.")
    scene.zoom("#diff-view", scale=1.4)
    scene.wait(1300)
    scene.zoom_out()
    scene.wait_for("#diff-consider li.ok", timeout_ms=60_000)  # the laws are proved on the changed model
    scene.expect_text("#inspector .diff-item .who.you", "You")
    scene.caption("And what to consider, in one place: a warning, the laws, the other diagrams it changes, the tests it adds.")
    scene.click("#diff-flags summary")
    scene.expect_text("#diff-consider", "No record can ever reach Lost")
    scene.zoom("#diff-consider", scale=1.7)
    scene.wait(2000)
    scene.zoom_out()
    scene.click("#show-changes")  # back to the diagram
    scene.caption("The AI proposes a way in, the server re-checks it, and it ripples on.")
    scene.click(f"{RIPPLE_CARD} .follow-ons li.applies button")
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "New use case Renew", timeout_ms=60_000)


def _ai(scene: Scene, chapter: _Chapters) -> None:
    chapter("The AI's change, at a glance")
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
    scene.caption("The same view: a new arrow in green, and the arrow it removes kept as a dashed ghost, never hidden.")
    scene.zoom("#diff-view", scale=1.3)
    scene.wait(1600)
    scene.zoom_out()
    scene.wait_for("#diff-consider li.ok, #diff-consider li.bad:not(:has(details))", timeout_ms=60_000)
    scene.expect_text("#diff-consider", "Breaks the sequence")
    scene.expect_text("#diff-consider", "2 problems")
    scene.expect_text("#inspector .diff-item .who.ai", "AI")
    scene.caption("Each change is tagged AI or You. To consider: two problems, and it breaks the late-return scenario.")
    scene.click("#diff-flags summary")
    scene.zoom("#diff-consider", scale=1.6)
    scene.wait(2200)
    scene.zoom_out()


def _catch(scene: Scene, chapter: _Chapters) -> None:
    chapter("What to consider before you accept")
    scene.click(f"{AI_CARD} .plan-tools .review-it")
    scene.expect_text("#review-head-text", "2 changes: 1 high risk")
    scene.caption("The riskiest change comes first. Predict before you see the answer: can a librarian still return an overdue loan?")
    scene.click("#review-item-1 .show")
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Not what you expected")
    scene.caption("The kernel says no. The AI quietly deleted late returns, and your wrong guess caught it.")
    scene.zoom("#review-item-1", scale=1.6)
    scene.wait(1400)
    scene.zoom_out()
    scene.click("#tab-sequences")
    scene.click("#seq-list li:has-text('returned late') button")
    scene.wait_for(".seq-verdict.bad", timeout_ms=30_000)
    scene.expect_text("#seq-verdict", "The change shown breaks it")
    scene.caption("The late-return scenario as a UML sequence diagram: it now ends in the kernel's refusal.")
    scene.zoom("#sequence-canvas", scale=1.3)
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
    _test_renew(scene)
    scene.caption("Build the changed app, check every conformance case, and simulate the users again.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.click("#tab-states")  # the traffic runs along the state machine's transitions
    if scene.page.get_attribute("#show-changes", "aria-pressed") == "true":
        scene.click("#show-changes")
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.caption("Simulate replays as traffic: green dots went through, red ones stop where the kernel refused them.")
    scene.zoom("#canvas", scale=1.5)
    scene.wait(2600)
    scene.zoom_out()
    scene.click("#tab-laws")
    scene.wait_for("#laws-summary.ok, #laws-summary.bad", timeout_ms=120_000)
    scene.expect_text("#laws-summary", "holds on every run the kernel allows")
    scene.caption("Every law holds on every run the kernel allows.")
    scene.click("#tab-tests")
    scene.expect_text("#tests-summary", "All 8 tests pass", timeout_ms=60_000)
    scene.click("#tab-states")
    scene.click("#health")
    scene.expect_text("#health-text", "5/5 checks")
    scene.expect_text("#check-next", "Every check passes")
    scene.caption("The ring fills only from real checks on what you are looking at.")
    scene.zoom("#checks", scale=1.6)
    scene.wait(1500)
    scene.zoom_out()


def _people(scene: Scene, chapter: _Chapters) -> None:
    chapter("People: who sees what")
    scene.click("#dock-close")
    scene.click("#tab-screens")
    scene.click("#role-lens button[data-role=Clerk]")
    scene.expect_text("#role-app", "A Clerk sees 2 of")
    scene.caption(
        "Design the people too. See the app as a Clerk: the screens the kernel never lets them take are struck through."
    )
    scene.zoom("#screens", scale=1.3)
    scene.wait(2400)
    scene.zoom_out()
    scene.click("#role-lens button[data-role='']")


def _agents(scene: Scene, chapter: _Chapters) -> None:
    chapter("AI agents in the model")
    scene.caption(
        "And the agents. Start Refund desk from a template: an AI agent, a timer and a payment system are UML actors."
    )
    scene.click("#system-menu")
    scene.click("#systems-tab-new")
    scene.click("#systems-templates input[value=refund-desk]")
    scene.type_text("#systems-name", "Refund desk", clear=True)
    scene.page.once("dialog", lambda dialog: dialog.accept())  # the reviewed plan is a throwaway: leave it
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "WithSupervisor")
    scene.chapter(chapter.n, "AI agents in the model")
    scene.click("#tab-usecases")
    scene.zoom("#usecase-canvas", scale=1.2)
    scene.wait(1600)
    scene.zoom_out()
    scene.type_text("#chat-input", AGENT_RISKY)
    scene.click("#chat-send")
    scene.expect_text(f"{AI_CARD} .plan-verdict.bad", "Only a person approves a refund", timeout_ms=30_000)
    scene.caption("A hand-off, plus letting the agent approve? The laws refuse: only a person approves a refund.")
    scene.zoom(f"{AI_CARD} .plan-verdict", scale=1.5)
    scene.wait(2400)
    scene.zoom_out()
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.expect_text("#game-notes", "Caught it", timeout_ms=30_000)
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result: adds HandOff")
    scene.caption("Untick that step: caught. The hand-off alone is allowed.")
    scene.zoom("#health", scale=1.8)
    scene.wait(1800)
    scene.zoom_out()
