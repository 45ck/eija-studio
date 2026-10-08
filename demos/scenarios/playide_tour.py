"""The PlayIDE tour: design a system in UML, build and run it, simulate users, and check an AI's change.

Drives the real PlayIDE page (`/play`) of an ephemeral `eija serve` on the library-loan pack, offline. Every step
asserts text the page really renders, so the recording doubles as an e2e check. The chat's proposer is the offline
phrase reader (`offline-plan-fixture-v1`), not a live model, and the video says so.
"""
from __future__ import annotations

from demos.lib import RunningServer, Scene

TITLE = "The PlayIDE tour: design, build, simulate and check an AI's change"
PACK = "packs/library-loan"
AI_REQUEST = "add state Archived after Returned then allow Member to CheckOut"
BUILD_TIMEOUT_MS = 600_000


def run(scene: Scene, server: RunningServer) -> None:
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.title_card("PlayIDE", "UML you can trust to build apps.")
    _diagrams(scene)
    _build_and_simulate(scene)
    _draw(scene)
    _ai_change(scene)
    scene.clear_caption()
    scene.title_card("AI proposes. The kernel checks. You decide.", "PlayIDE, built on EIJA Studio (Apache-2.0)")


def _tab(scene: Scene, name: str, text: str, target: str) -> None:
    scene.click(f"#tab-{name}")
    scene.caption(text)
    scene.highlight(target, duration_ms=1400)


def _diagrams(scene: Scene) -> None:
    scene.caption("A library loan, modelled as a UML state machine. The model is the source of truth.")
    scene.highlight("#canvas", duration_ms=1600)
    _tab(scene, "classes", "Its data model is a UML class diagram. The record class becomes the app's form.", "#class-canvas")
    _tab(scene, "usecases", "Use cases come from the model: who may do what.", "#usecase-canvas")
    _tab(scene, "screens", "Each use case gets a screen, designed against the record class and checked as you edit.", "#screen-card")
    scene.expect_text("#screen-problems", "Design check passed")


def _build_and_simulate(scene: Scene) -> None:
    scene.caption("Build & run generates the app and checks every case against the kernel before it starts.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.highlight("#score", duration_ms=1400)
    scene.caption("The real app runs beside the model. It asks the kernel for every decision.")
    scene.highlight("#run", duration_ms=1800)
    _tab(scene, "components", "Its UML component diagram is read from the generated code, not drawn by hand.", "#component-canvas")
    scene.click("#tab-states")
    scene.caption("Simulate sends seeded users through the kernel. Thick lines are busy; refusals show where people got stuck.")
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.highlight("#sim", duration_ms=2200)
    scene.click("#sim-clear")


def _draw(scene: Scene) -> None:
    scene.caption("Design in place. Drag a state from the palette onto the diagram.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.drag('#draw-palette [data-kind="state"]', "#canvas", position=(width * 0.82, height * 0.82))
    scene.type_text(".draft-form input", "Lost")
    scene.click('.draft-form button[type="submit"]')
    scene.expect_text(".plan-verdict", "The policy allows the result")
    scene.caption("Then a transition: who may take it, and where it goes.")
    scene.click("#outline-states button:has-text('Overdue')")
    scene.click("#inspector button:has-text('Add a transition from here')")
    scene.select_option(".draft-form label:has-text('To') select", "Lost")
    scene.select_option(".draft-form label:has-text('Action') select", "Renew")
    scene.select_option(".draft-form label:has-text('Who may take it') select", "Librarian")
    scene.click('.draft-form button[type="submit"]')
    scene.expect_text(".plan-verdict", "adds Renew")
    scene.caption("Every edit is a typed step the policy checks. The diagram previews it; nothing is saved yet.")
    scene.highlight("#plan-banner", duration_ms=1600)


def _ai_change(scene: Scene) -> None:
    scene.caption("Now ask the AI. Offline here: a deterministic phrase reader stands in for a live model.")
    scene.type_text("#chat-input", AI_REQUEST)
    scene.click("#chat-send")
    card = ".msg.ai:last-child"
    scene.expect_text(f"{card} .plan-verdict", "The policy refuses")
    scene.caption("It proposes typed steps. The policy refuses one: who may check a loan out is protected.")
    scene.highlight(f"{card} .plan", duration_ms=1800)
    scene.caption("Check each step on the diagram. Points come from checking the AI, never from making changes.")
    scene.click(f"{card} .plan-steps > li:nth-child(1) .show")
    scene.wait(1200)
    scene.click(f"{card} .plan-steps > li:nth-child(2) .show")
    scene.expect_text("#inspector", "Let Member take")
    scene.wait(1200)
    scene.caption("Reject the step the policy caught.")
    scene.click(f"{card} .plan-steps > li:nth-child(2) input")
    scene.expect_text(f"{card} .plan-verdict", "The policy allows the result")
    scene.click(f"{card} .plan-tools .primary")
    scene.expect_text("#plan-banner-text", "Previewing the plan")
    scene.caption("Then test the AI's change for real: build it, run its conformance cases, and simulate it.")
    scene.click("#build")
    scene.expect_text("#score", "cases match the kernel", timeout_ms=BUILD_TIMEOUT_MS)
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.click("#health")
    scene.expect_text("#health-text", "4/4 checks")
    scene.caption("Every part of the ring is a real check on what you are looking at.")
    scene.highlight("#checks", duration_ms=2600)
