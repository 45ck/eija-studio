"""What PlayIDE's AI can do, and what it can't: an honest tour of the AI in the IDE.

One unedited take of the real PlayIDE page (`/play`) on an ephemeral `eija serve`, offline. Every step asserts text
the page renders, so the take doubles as an end-to-end check. The chat's proposer is the offline phrase reader
(`offline-plan-fixture-v1`) and the describer is the offline shape reader (`offline-describe-fixture-v1`): there is no
live model, and the video says so on screen.

What the AI can do: turn plain words into typed UML steps, and turn one sentence into every model and view of a new
system. What it can't: slip a breaking change past the reviewer (the kernel and the reviewer's own prediction catch
it), guess names or limits it cannot read (it refuses instead), write the laws (they are the person's, and the kernel
proves them), let an AI agent in the model break a law, or approve and apply anything (the owner does that). The
build's conformance suite proves the app still matches the model. Nothing is approved or applied.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene
from demos.scenarios.playide_showcase import (
    AGENT_RISKY,
    AI_CARD,
    AI_REQUEST,
    BUILD_TIMEOUT_MS,
    CAUGHT,
    PACK,
)

PACE = 0.7
TITLE = "What PlayIDE's AI can do, and what it can't"
DESCRIPTION = ("A coffee shop app. Customers order drinks, baristas make them, then customers collect them. "
               "Orders have a size (small, medium, large) and notes.")
VAGUE = "make returns faster and add some fraud checks"
UNKNOWN = "remove state Lost"
LIMIT = "add Renew from Overdue to OnLoan for Librarian only if the fine is under 50"
LAW = "add a law that a loan is never deleted"
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
    scene.title_card("What the AI can do. And what it can't.", "The AI proposes. The kernel decides what a change "
                     "means. You check it, and the owner ships it. Offline in this video: no live model.", hold_ms=4200)
    chapter = _Chapters(scene)
    _who_does_what(scene)
    _can_plan(scene, chapter)
    _cannot_sneak(scene, chapter)
    _cannot_guess(scene, chapter)
    _cannot_write_laws(scene, chapter)
    _prove(scene, chapter)
    _can_describe(scene, chapter)
    _agents(scene, chapter)
    _cannot_ship(scene, chapter)
    scene.zoom_out()
    scene.title_card("Can: draft UML from plain words. Can't: decide what it means.", "Typed steps you can read, a kernel "
                     "that refuses what breaks a law, tests and conformance that prove the app matches, and an owner who "
                     "ships. PlayIDE, built on EIJA Studio (Apache-2.0)", hold_ms=5000)


def _ask(scene: Scene, text: str) -> None:
    scene.type_text("#chat-input", text, clear=True)
    scene.click("#chat-send")


def _who_does_what(scene: Scene) -> None:
    scene.caption("Beside the chat, always: the AI proposes steps, you check and try them, the owner approves and applies.")
    scene.zoom("#authority", scale=2.0)
    scene.wait(2200)
    scene.zoom_out()


def _can_plan(scene: Scene, chapter: _Chapters) -> None:
    chapter("Can: plain words to UML steps")
    scene.caption("Ask for a change in plain words. Offline here: a phrase reader stands in for a live model.")
    _ask(scene, AI_REQUEST)
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result")
    scene.caption("It answers with typed UML steps, not a wall of code, and the policy allows them.")
    scene.zoom(AI_CARD, scale=1.4)
    scene.wait(2000)
    scene.zoom_out()
    for step in (1, 2):
        scene.click(f"{AI_CARD} .plan-steps > li:nth-child({step}) .show")
        scene.wait(300)
    scene.click("#tab-states")
    scene.click("#show-changes")
    scene.wait_for(".diff-item", timeout_ms=30_000)
    scene.expect_text("#inspector .diff-item .who.ai", "AI")
    scene.caption("On the diagram you know: the new arrow in green, the removed arrow kept as a dashed ghost, each tagged AI.")
    scene.zoom("#diff-view", scale=1.3)
    scene.wait(2000)
    scene.zoom_out()


def _cannot_sneak(scene: Scene, chapter: _Chapters) -> None:
    chapter("Can't: sneak a break past you")
    scene.wait_for("#diff-consider li.ok, #diff-consider li.bad:not(:has(details))", timeout_ms=60_000)
    scene.expect_text("#diff-consider", "Breaks the sequence")
    scene.caption("Allowed is not the same as right. The kernel checks the result: it breaks the late-return scenario.")
    scene.click("#diff-flags summary")
    scene.zoom("#diff-consider", scale=1.6)
    scene.wait(2000)
    scene.zoom_out()
    scene.click("#show-changes")
    scene.click(f"{AI_CARD} .plan-tools .review-it")
    scene.expect_text("#review-head-text", "2 changes: 1 high risk")
    scene.caption("Review it. Predict first: can a librarian still return an overdue loan?")
    scene.click("#review-item-1 .show")
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Not what you expected")
    scene.caption("The kernel says no. The AI quietly deleted late returns, and your wrong guess caught it.")
    scene.zoom("#review-item-1", scale=1.6)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#tab-sequences")
    scene.click("#seq-list li:has-text('returned late') button")
    scene.wait_for(".seq-verdict.bad", timeout_ms=30_000)
    scene.expect_text("#seq-verdict", "The change shown breaks it")
    scene.caption("The late return as a UML sequence diagram now ends in the kernel's refusal.")
    scene.zoom("#sequence-canvas", scale=1.3)
    scene.wait(1600)
    scene.zoom_out()
    scene.caption("Reject that step. The review runs again on what is left: nothing high risk.")
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.click("#tab-review")
    scene.expect_text("#review-head-text", "1 change: 0 high risk")
    scene.zoom("#review-head-text", scale=1.6)
    scene.wait(1000)
    scene.zoom_out()
    scene.click("#tab-states")


def _refused(scene: Scene, text: str, expected: str, caption: str) -> None:
    _ask(scene, text)
    scene.expect_text(".msg.ai:last-child", expected, timeout_ms=30_000)
    scene.caption(caption)
    scene.zoom(".msg.ai:last-child", scale=1.6)
    scene.wait(2200)
    scene.zoom_out()


def _cannot_guess(scene: Scene, chapter: _Chapters) -> None:
    chapter("Can't: guess what you meant")
    _refused(scene, VAGUE, "I could not read", "Vague asks are not guessed at. It says what it could not read and how to "
             "ask, instead of inventing a change.")
    _refused(scene, UNKNOWN, "The model has no state Lost", "A name the model does not have is refused, not made up.")
    _refused(scene, LIMIT, "I can't plan “under 50”", "A limit it cannot express is refused too. Dropping it silently "
             "would change the model in a way you did not ask for.")


def _cannot_write_laws(scene: Scene, chapter: _Chapters) -> None:
    chapter("Can't: write your laws")
    _refused(scene, LAW, "I could not read", "No plan step writes a law. Laws are what the system must never do, and "
             "they are yours.")
    scene.click("#tab-laws")
    scene.wait_for("#laws-summary.ok, #laws-summary.bad", timeout_ms=120_000)
    scene.expect_text("#laws-summary", "holds on every run the kernel allows")
    scene.caption("You write them in the model. The kernel proves each one over every run it allows.")
    scene.zoom("#laws", scale=1.3)
    scene.wait(2200)
    scene.zoom_out()
    scene.click("#tab-states")


def _prove(scene: Scene, chapter: _Chapters) -> None:
    chapter("Prove the app still matches")
    scene.caption("Build the changed app and check every conformance case against the kernel.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.zoom("#score", scale=1.8)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#dock-close")  # give the diagram the room back for the traffic
    if scene.page.get_attribute("#show-changes", "aria-pressed") == "true":
        scene.click("#show-changes")
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.caption("Simulate users on it: green dots went through, red ones stop where the kernel refused them.")
    scene.zoom("#canvas", scale=1.4)
    scene.wait(2200)
    scene.zoom_out()


def _can_describe(scene: Scene, chapter: _Chapters) -> None:
    chapter("Can: draft a system from a sentence")
    scene.caption("Start a new system by describing it. The offline reader knows a fixed set of app shapes and says what it assumed.")
    scene.click("#system-new")
    scene.wait_for("#systems-describe", timeout_ms=30_000)
    scene.type_text("#systems-describe", DESCRIPTION, clear=True, delay_range_ms=(10, 28))
    scene.type_text("#systems-name", "Coffee shop", clear=True)
    scene.wait_for("#systems-described", timeout_ms=30_000)
    scene.expect_text("#systems-described", "3 recorded by the kernel")
    scene.caption("Every view it will make, checked by the kernel before anything is created. Its tests are recorded by "
                  "the kernel, not written by the AI.")
    scene.zoom("#systems-check", scale=1.35)
    scene.wait(2400)
    scene.zoom_out()
    scene.page.once("dialog", lambda dialog: dialog.accept())  # the reviewed plan is a throwaway: leave it
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "Collected")
    scene.chapter(chapter.n, "Can: draft a system from a sentence")
    scene.caption("A state machine, a class diagram with the fields you named, use cases, screens and sequence diagrams.")
    scene.zoom("#canvas", scale=1.3)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#tab-classes")
    scene.wait_for("#class-canvas svg", timeout_ms=30_000)
    scene.expect_text("#class-canvas", "size")
    scene.zoom("#class-canvas", scale=1.35)
    scene.wait(1600)
    scene.zoom_out()
    scene.click("#tab-states")
    scene.expect_text("#missing", "No laws", timeout_ms=60_000)
    scene.caption("And what it leaves to you: What's missing says no laws. It never writes one for you.")
    scene.zoom("#missing", scale=1.6)
    scene.wait(2400)
    scene.zoom_out()


def _agents(scene: Scene, chapter: _Chapters) -> None:
    chapter("Can't: let an agent break a law")
    scene.caption("AI agents can be part of the system too. The refund desk template has one, as a UML actor.")
    scene.click("#system-menu")
    scene.click("#systems-tab-new")
    scene.click("#systems-templates input[value=refund-desk]")
    scene.type_text("#systems-name", "Refund desk", clear=True)
    scene.page.once("dialog", lambda dialog: dialog.accept())
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "WithSupervisor")
    scene.chapter(chapter.n, "Can't: let an agent break a law")
    _ask(scene, AGENT_RISKY)
    scene.expect_text(f"{AI_CARD} .plan-verdict.bad", "Only a person approves a refund", timeout_ms=30_000)
    scene.caption("Ask the AI to let the support agent approve refunds. The laws refuse: only a person approves a refund.")
    scene.zoom(f"{AI_CARD} .plan-verdict", scale=1.5)
    scene.wait(2400)
    scene.zoom_out()
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.expect_text(CAUGHT, "Caught", timeout_ms=30_000)
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result: adds HandOff")
    scene.caption("Untick that step: caught. The hand-off to a supervisor alone is allowed.")
    scene.zoom(f"{AI_CARD} .plan-verdict", scale=1.5)
    scene.wait(1800)
    scene.zoom_out()


def _cannot_ship(scene: Scene, chapter: _Chapters) -> None:
    chapter("Can't: approve or apply")
    scene.expect_text("#source-status", "Source review required")
    scene.caption("Nothing the AI proposed is in force. Approving and applying is the owner's, in the review workbench, "
                  "after a source review.")
    scene.zoom("#authority", scale=2.0)
    scene.wait(2200)
    scene.zoom_out()
    scene.zoom("#source-status", scale=2.0)
    scene.wait(1600)
    scene.zoom_out()
