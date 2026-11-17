"""The AI builds it, PlayIDE proves it: the whole system from one sentence, changed in plain words, then checked.

One unedited take of the real PlayIDE page (`/play`) on an ephemeral `eija serve`, offline. Every step asserts text the
page renders. The describer and the chat's proposer are the offline readers (`offline-describe-fixture-v1`,
`offline-plan-fixture-v1`): there is no live model, and the video says so.

The story: the AI drafts every model and view of a coffee shop from one sentence and changes it in plain words; the
kernel records the tests again; the app is built from the same model and every conformance case (UI options, HTTP API,
stored records) matches the kernel, drawn as a UML deployment of browser, process and database. Then the guarantee
at work on a system with laws: the library loan, where the AI's change that would delete late returns is caught
before it lands, and every law is proved over every run the kernel allows; and the refund desk, where a change that
would let the AI agent approve refunds is refused by a law. Two closing cards quote the repository's formal
gates (Z3, TLA+, SCXML, seeded divergence, properties), run on the same commit. Nothing is approved or
applied.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene
from demos.scenarios.playide_greenfield import CARD, DESCRIPTION, ROUNDS
from demos.scenarios.playide_showcase import (
    AGENT_RISKY,
    AI_CARD,
    AI_REQUEST,
    BUILD_TIMEOUT_MS,
    CAUGHT,
    PACK,
)

PACE = 0.72
TITLE = "The AI builds it. PlayIDE proves it."
# The repository's formal gates, run on the recorded commit (nox -s formal_smt formal_tla scxml_differential
# conformance_divergence property; see docs/demos/2026-11-17-PLAYIDE-AI-BUILDS-PROVED.md). Re-run them before re-recording.
PROOFS = ("Z3 proves the change policy's 15 safety invariants (15 of 15 UNSAT), with 0 disagreements across 2,572 "
          "differential cases. TLA+ model-checks 15,408 workflow states, and finds all 4 planted bugs.")
TESTED = ("12,256 cases agree with an independent SCXML engine. 553 deliberately wrong apps are built: every one is "
          "caught or refused. 117 property tests pass.")
__all__ = ["PACK", "TITLE", "run"]


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
    scene.title_card("The AI builds it. PlayIDE proves it.", "From one sentence to a running app, every change "
                     "checked by a deterministic kernel, proved against its laws and tested across the whole stack. "
                     "Offline AI in this video: no live model.", hold_ms=4400)
    chapter = _Chapters(scene)
    _drafts(scene, chapter)
    _changes(scene, chapter)
    _builds(scene, chapter)
    _caught(scene, chapter)
    _proved(scene, chapter)
    _agents(scene, chapter)
    scene.zoom_out()
    scene.title_card("Behind it: proofs, not just tests", PROOFS, hold_ms=5600)
    scene.title_card("And checked against itself", TESTED, hold_ms=5200)
    scene.title_card("The AI builds it. PlayIDE proves it.", "Proved against the model and its laws, the same model from "
                     "diagram to app to API to database. The owner still ships. PlayIDE, built on EIJA Studio "
                     "(Apache-2.0)", hold_ms=4800)


def _ask(scene: Scene, text: str) -> None:
    scene.type_text("#chat-input", text, clear=True)
    scene.click("#chat-send")


def _look(scene: Scene, target: str, caption: str, scale: float = 1.4, hold: int = 2200) -> None:
    scene.caption(caption)
    scene.zoom(target, scale=scale)
    scene.wait(hold)
    scene.zoom_out()


def _new_from_template(scene: Scene, template: str, name: str, state: str) -> None:
    scene.click("#system-menu")
    scene.click("#systems-tab-new")
    scene.click(f"#systems-templates input[value={template}]")
    scene.type_text("#systems-name", name, clear=True)
    scene.page.once("dialog", lambda dialog: dialog.accept())  # a draft in progress is a throwaway: leave it
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", state)


def _drafts(scene: Scene, chapter: _Chapters) -> None:
    chapter("The AI drafts the whole system")
    scene.caption("Describe the app in one sentence: who does what, and what it records.")
    scene.click("#system-new")
    scene.wait_for("#systems-describe", timeout_ms=30_000)
    scene.type_text("#systems-describe", DESCRIPTION, clear=True, delay_range_ms=(10, 26))
    scene.type_text("#systems-name", "Coffee shop", clear=True)
    scene.wait_for("#systems-described", timeout_ms=30_000)
    scene.expect_text("#systems-described", "3 recorded by the kernel")
    _look(scene, "#systems-check", "Every model and view it will make, checked by the kernel before anything exists.",
          scale=1.35, hold=2400)
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "Collected")
    scene.chapter(chapter.n, "The AI drafts the whole system")
    _look(scene, "#canvas", "A UML state machine that runs.", scale=1.3, hold=1600)
    scene.click("#tab-classes")
    scene.wait_for("#class-canvas svg", timeout_ms=30_000)
    scene.expect_text("#class-canvas", "size")
    _look(scene, "#class-canvas", "A class diagram with the fields you named.", scale=1.35, hold=1500)
    scene.click("#tab-sequences")
    scene.click('#seq-list button:has-text("Order reaches Collected")')
    scene.expect_text("#seq-verdict", "Order reaches Collected", timeout_ms=30_000)
    _look(scene, "#sequence-canvas", "Tests the kernel recorded by running the model, drawn as sequence diagrams.",
          scale=1.4, hold=1800)
    scene.click("#tab-states")


def _changes(scene: Scene, chapter: _Chapters) -> None:
    chapter("The AI changes it in plain words")
    scene.caption("Customers pay before brewing starts. Ask in chat. Offline here: a phrase reader stands in for a live model.")
    _ask(scene, ROUNDS[0])
    scene.expect_text(f"{CARD} .plan-verdict", "The policy allows the result")
    scene.expect_text(f"{CARD} .plan-steps", "new action Pay")
    _look(scene, CARD, "Typed UML steps, checked by the policy, tagged AI.", scale=1.35, hold=2000)
    scene.click(f"{CARD} .plan-tools .primary")  # preview it on the diagram
    scene.wait_for("#plan-banner:not([hidden])", timeout_ms=30_000)
    scene.expect_text("#missing", "No test takes Pay", timeout_ms=60_000)
    _look(scene, "#missing", "The kernel notices at once: the recorded way to Collected no longer holds, because paying "
          "comes first.", scale=1.6, hold=2200)
    scene.click("#missing-update-tests")
    scene.expect_text("#missing", "Order reaches Collected recorded again", timeout_ms=60_000)
    scene.wait_for('#missing [data-view="tests"].ready', timeout_ms=60_000)
    scene.click("#tab-sequences")
    scene.click('#seq-list button:has-text("Order reaches Collected")')
    scene.expect_text("#sequence-canvas", "Pay", timeout_ms=30_000)
    _look(scene, "#sequence-canvas", "One click and the kernel records the tests again: the sequence now pays first.",
          scale=1.4, hold=1800)
    scene.click("#tab-states")


def _builds(scene: Scene, chapter: _Chapters) -> None:
    chapter("Built and checked across the stack")
    scene.caption("Build the app from the same model and check every conformance case against the kernel.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.wait_for("#run-frame", timeout_ms=60_000)
    _look(scene, "#run", "The running app: its screens, buttons and rules come from the model, not from hand-written code.",
          scale=1.3, hold=2200)
    _look(scene, "#score", "Every case matches: what the app offers, what its HTTP API answers, and what it stores.",
          scale=1.8, hold=1800)
    scene.click("#tab-components")
    scene.click("#component-lens button[data-lens=deployment]")
    scene.expect_text("#deployment", "conformance cases", timeout_ms=30_000)
    _look(scene, "#deployment", "Browser, Python process and SQLite file, as a UML deployment diagram read from the built "
          "app. One model, every layer.", scale=1.35, hold=2600)
    scene.click("#component-lens button[data-lens=app]")
    scene.click("#tab-states")


def _caught(scene: Scene, chapter: _Chapters) -> None:
    chapter("Proved before it lands")
    scene.caption("Now a system with laws: a library loan. Ask for a renewal, and the AI also removes late returns.")
    _new_from_template(scene, "library-loan", "Library loan", "Overdue")
    scene.chapter(chapter.n, "Proved before it lands")
    _ask(scene, AI_REQUEST)
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result")
    scene.click("#show-changes")
    scene.wait_for(".diff-item", timeout_ms=30_000)
    scene.wait_for("#diff-consider li.ok, #diff-consider li.bad:not(:has(details))", timeout_ms=60_000)
    scene.expect_text("#diff-consider", "Breaks the sequence")
    scene.click("#diff-flags summary")
    _look(scene, "#diff-consider", "Before anything lands, the kernel runs the changed model: it breaks the late-return "
          "scenario.", scale=1.6, hold=2400)
    scene.click("#show-changes")
    scene.click(f"{AI_CARD} .plan-tools .review-it")
    scene.expect_text("#review-head-text", "2 changes: 1 high risk")
    scene.click("#review-item-1 .show")
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Not what you expected")
    _look(scene, "#review-item-1", "Ranked high risk, with the kernel's answer: a librarian could no longer return an "
          "overdue loan.", scale=1.6, hold=2000)
    scene.caption("Drop that step. Everything is checked again on what is left: nothing high risk.")
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.click("#tab-review")
    scene.expect_text("#review-head-text", "1 change: 0 high risk")
    scene.zoom("#review-head-text", scale=1.6)
    scene.wait(1000)
    scene.zoom_out()
    scene.click("#tab-states")


def _proved(scene: Scene, chapter: _Chapters) -> None:
    chapter("Every law, every run")
    scene.click("#tab-laws")
    scene.wait_for("#laws-summary.ok, #laws-summary.bad", timeout_ms=120_000)
    scene.expect_text("#laws-summary", "holds on every run the kernel allows")
    _look(scene, "#laws", "Not sampled: every reachable configuration of the changed model is searched, and every law "
          "holds on every run.", scale=1.3, hold=2800)
    scene.click("#tab-states")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    if scene.page.get_attribute("#show-changes", "aria-pressed") == "true":
        scene.click("#show-changes")
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    _look(scene, "#canvas", "Rebuilt, every conformance case matches again, and simulated users run through it.",
          scale=1.4, hold=2200)


def _agents(scene: Scene, chapter: _Chapters) -> None:
    chapter("AI agents inside the guarantee")
    scene.caption("AI agents can be part of the system too: the refund desk has one, as a UML actor.")
    _new_from_template(scene, "refund-desk", "Refund desk", "WithSupervisor")
    scene.chapter(chapter.n, "AI agents inside the guarantee")
    _ask(scene, AGENT_RISKY)
    scene.expect_text(f"{AI_CARD} .plan-verdict.bad", "Only a person approves a refund", timeout_ms=30_000)
    _look(scene, f"{AI_CARD} .plan-verdict", "Ask to let the agent approve refunds: the law refuses it. Only a person "
          "approves a refund.", scale=1.5, hold=2400)
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.expect_text(CAUGHT, "Caught", timeout_ms=30_000)
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result: adds HandOff")
    _look(scene, f"{AI_CARD} .plan-verdict", "The rest goes through. The guarantee does not slow the AI down; it decides "
          "what lands.", scale=1.5, hold=2000)
