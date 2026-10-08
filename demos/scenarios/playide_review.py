"""Review an AI's change in PlayIDE, not in a pull request.

Drives the real PlayIDE page (`/play`) of an ephemeral `eija serve` on the library-loan pack, offline. The AI's plan
(the offline phrase reader, `offline-plan-fixture-v1`, not a live model) adds a renewal and quietly deletes late
returns. The reviewer sees the change on the UML, predicts what the kernel will do before it is shown, gets one
prediction wrong, asks for a change, rejects the risky step, reviews again and builds the result. Every step asserts
text the page really renders. Nothing is approved or applied: that stays with the owner.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "Review an AI's change in PlayIDE, not in a pull request"
PACK = "packs/library-loan"
AI_REQUEST = "add Renew from Overdue to OnLoan for Librarian then remove transition ReturnLate"
BUILD_TIMEOUT_MS = 600_000
CARD = ".msg.ai:last-child"


def run(scene: Scene, server: RunningServer) -> None:
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.title_card("Review the change, not the diff", "An AI's change, checked as UML you can run.")
    _ask(scene)
    _first_review(scene)
    _fix_and_review_again(scene)
    scene.clear_caption()
    scene.title_card("Look. Predict. Run. Decide.", "PlayIDE, built on EIJA Studio (Apache-2.0)")


def _ask(scene: Scene) -> None:
    scene.caption("A library loan, modelled as a UML state machine. We ask the AI to let librarians renew overdue loans.")
    scene.highlight("#canvas", duration_ms=1400)
    scene.caption("Offline here: a deterministic phrase reader stands in for a live model.")
    scene.type_text("#chat-input", AI_REQUEST)
    scene.click("#chat-send")
    scene.expect_text(f"{CARD} .plan-verdict", "The policy allows the result")
    scene.caption("The policy allows the plan. In a pull request this would be a diff to read. Here we review it as the model.")
    scene.highlight(f"{CARD} .plan", duration_ms=1600)
    scene.click(f"{CARD} .plan-tools .review-it")
    scene.expect_text("#review-head-text", "2 changes: 1 high risk")


def _first_review(scene: Scene) -> None:
    scene.caption("Both models on one diagram: the new path in green, the deleted path dashed in red.")
    scene.highlight("#review-canvas", duration_ms=1800)
    scene.caption("Below the diagram, the kernel ran every user on every action on both models. These are the outcomes that changed.")
    scene.highlight("#review-head-text", duration_ms=1400)
    scene.caption("The riskiest change comes first. Look at it on the diagram.")
    scene.click("#review-item-1 .show")
    scene.expect_text("#review-item-1", "Remove ReturnLate")
    scene.caption("Before the answer is shown, predict it. Can a librarian still return an overdue loan?")
    scene.highlight("#review-item-1 .predict", duration_ms=1400)
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Not what you expected")
    scene.caption("The kernel says no. The plan deleted late returns: a surprise caught before anything changed.")
    scene.highlight("#review-item-1", duration_ms=2000)
    scene.click("#review-item-1 .verdict-tools button:has-text('Needs a change')")
    scene.type_text("#review-item-1 textarea", "Keep ReturnLate: an overdue loan must still be returnable.")
    scene.caption("The new path is what we asked for. Look, predict, decide.")
    scene.click("#review-item-2 .show")
    scene.click("#review-item-2 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-2 .answer", "Right")
    scene.click("#review-item-2 .verdict-tools button:has-text('Looks right')")
    scene.click("#review-finish")
    scene.expect_text("#review-summary", "Changes requested: 1 of 2")
    scene.caption("The review is a record of what was checked, bound to both models' hashes. Points came from checking, not from approving.")
    scene.highlight("#review-summary", duration_ms=2200)


def _fix_and_review_again(scene: Scene) -> None:
    scene.caption("Reject the step that deleted late returns. The review runs again on what is left.")
    scene.click(f"{CARD} .plan-steps > li:nth-child(2) input")
    scene.expect_text("#review-head-text", "1 change: 0 high risk")
    scene.click("#review-item-1 .show")
    scene.click("#review-item-1 .predict-tools button:has-text('Yes')")
    scene.expect_text("#review-item-1 .answer", "Right")
    scene.click("#review-item-1 .verdict-tools button:has-text('Looks right')")
    scene.click("#review-finish")
    scene.expect_text("#review-summary", "Every change looks right")
    scene.caption("Then test it for real: build the app from the reviewed model and run its conformance cases.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.highlight("#score", duration_ms=1400)
    scene.caption("Approving and applying stay with the owner in the review workbench. The AI never decides.")
    scene.highlight("#review-summary", duration_ms=1800)
