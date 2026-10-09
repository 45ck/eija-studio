"""The PlayIDE showcase: software engineering as play, once you think in UML.

The storyboard is docs/demos/PLAYIDE-SHOWCASE-STORYBOARD.md. This script drives the real PlayIDE page (`/play`) of
an ephemeral `eija serve` on the library-loan pack, offline, and asserts what the page really renders, so the take
doubles as an e2e check. Beats whose feature has not merged yet are skipped and named in the manifest (a PARTIAL
take), never faked. The chat's proposer is the offline phrase reader (`offline-plan-fixture-v1`), and the video
says so.
"""
from __future__ import annotations

from pathlib import Path

from demos.lib import RunningServer, Scene

TITLE = "The PlayIDE showcase: design the whole system, then play it"
PACK = "packs/library-loan"
AI_REQUEST = "add Renew from Overdue to OnLoan for Librarian then remove transition ReturnLate"
BUILD_TIMEOUT_MS = 600_000
AI_CARD = ".msg.ai:last-child"
APP = "#run-frame >> internal:control=enter-frame >>"  # inside the built app's frame
AGENT_RISKY = "add HandOff from Assessed to WithSupervisor for SupportAgent then allow SupportAgent to ApproveRefund"
RIPPLE_CARD = ".msg:last-child"  # the chat card that shows a drawn change's ripple (ADR-0158)
ROOT = Path(__file__).resolve().parents[2]
EXPORTED = ROOT / "verification/interop/generated/library-loan.puml"  # what PlayIDE exports for the pack (ADR-0190)
EDITED_IN_ANOTHER_TOOL = "Overdue --> OnLoan : Renew [role = Librarian]"
# A support desk drawn in another UML tool, with things PlayIDE cannot carry (a guard term, a second Resolve, a state
# name with spaces): starting a system from it reports each one with its reason (ADR-0190).
DESK_PUML = """@startuml
[*] --> Open
Open --> Triaged : Triage [role = Agent] / Audit:Triaged
Triaged --> Resolved : Resolve [role = Agent and assigned] / Audit:Resolved, Notification:CustomerTold
Triaged --> Escalated : Escalate
Escalated --> Resolved : Fix [role = Engineer and severity > 2]
Escalated --> Resolved : Resolve [role = Engineer]
Escalated --> "Waiting on vendor" : Wait [role = Engineer]
@enduml
@startuml
class Ticket <<record>> {
  +subject : String [1] {maxLength = 120}
  +urgent : Boolean [0..1]
}
@enduml
"""
NEW_SYSTEM_SKETCH = ("Open -> Triaged : Triage [Agent]\nTriaged -> Resolved : Resolve [Agent]\n"
                     "Resolved -> Closed : Close [Customer]")

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
        self.scene.chapter(self.n, title, card=True)


def run(scene: Scene, server: RunningServer) -> None:
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    scene.title_card("Design the whole system. Then play it.",
                     "People, AI agents and software in one UML model. Read every change, yours and the AI's, and let "
                     "the kernel check it before you accept it.", hold_ms=4200)
    chapter = _Chapters(scene)
    _model_is_the_program(scene, chapter)
    _press_play(scene, chapter)
    _fix_in_place(scene, chapter)
    _ripple(scene, chapter)
    _ai_busywork(scene, chapter)
    _review(scene, chapter)
    _prove_it(scene, chapter)
    _people(scene, chapter)
    _whole_system(scene, chapter)
    _stakeholder_view(scene, chapter, server)
    _bring_your_own_uml(scene, chapter, server)
    _agents(scene, chapter)
    _start_your_own(scene, chapter)
    scene.skip(PENDING["ship"])
    scene.clear_caption()
    scene.zoom_out()
    scene.title_card("Then the owner ships it", "Verify, approve and apply stay with the owner in the review workbench. "
                     "Not shown yet: they wait on the owner's source review (issue #80).", hold_ms=3600)
    scene.title_card("Design the people, the agents and the software. Then play it.",
                     "Review the change, not the code. The app cannot disobey the model. You decide what ships. "
                     "PlayIDE, built on EIJA Studio (Apache-2.0)", hold_ms=4600)


def _model_is_the_program(scene: Scene, chapter: _Chapters) -> None:
    chapter("The model is the program")
    scene.caption("A library loan, as a UML state machine. This diagram is not documentation: it is what runs.")
    scene.zoom("#canvas", scale=1.9)
    scene.wait(2200)
    scene.zoom_out()
    scene.caption("One model, many views: classes, use cases, sequences and screens are all drawn from it.", hold_ms=2000)
    for tab, target in (("classes", "#class-canvas"), ("usecases", "#usecase-canvas"), ("sequences", "#sequence-canvas"),
                        ("screens", "#screen-card")):
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


def _fix_in_place(scene: Scene, chapter: _Chapters) -> None:
    chapter("Fix it in place, not in code")
    scene.caption("Design in place. Drag a state onto an empty spot: it lands exactly there. Type its name on the diagram.")
    canvas = scene.page.locator("#canvas").bounding_box()
    width, height = (canvas["width"], canvas["height"]) if canvas else (800.0, 600.0)
    scene.drag('#draw-palette [data-kind="state"]', "#canvas", position=(width * 0.82, height * 0.82))
    scene.type_text(".inline-edit input", "Lost")
    scene.click('.inline-edit button[type="submit"]')
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "LoanState gains the literal Lost", timeout_ms=60_000)
    scene.caption("Each edit is a typed step the policy checks at once. The diagram previews it; nothing is saved.")
    scene.zoom("#canvas", scale=1.8)
    scene.wait(1600)
    scene.zoom_out()
    scene.caption("Every edit can be undone and redone, the AI's included, like in any editor.")
    scene.click("#undo")
    scene.expect_text("#toast", "Undid")
    scene.wait(900)
    scene.click("#redo")
    scene.expect_text(f"{RIPPLE_CARD} .ripple", "LoanState gains the literal Lost", timeout_ms=60_000)
    scene.wait(700)


def _ripple(scene: Scene, chapter: _Chapters) -> None:
    chapter("Your change: what to consider")
    scene.click("#show-changes")
    scene.wait_for(".diff-item", timeout_ms=30_000)
    scene.expect_text(".diff-summary", "1 change")
    scene.caption("Your own edit reads like any change: what is new is green, on the diagram you already know.")
    scene.zoom("#diff-view", scale=1.4)
    scene.wait(1600)
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
    chapter("The AI's change, at a glance")
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
    scene.wait_for("#diff-consider li.ok, #diff-consider li.bad:not(:has(details))", timeout_ms=60_000)
    scene.expect_text("#diff-consider", "Breaks the sequence")
    scene.expect_text("#diff-consider", "2 problems")
    scene.expect_text("#inspector .diff-item .who.ai", "AI")
    scene.caption("Each change is tagged AI or You. To consider: two problems, and it breaks the late-return scenario.")
    scene.click("#diff-flags summary")
    scene.zoom("#diff-consider", scale=1.6)
    scene.wait(2200)
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
    chapter("What to consider before you accept")
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
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#tab-tests")
    scene.expect_text("#tests-summary", "1 of 7 tests fail", timeout_ms=60_000)
    scene.caption("The pack's tests agree: the late-return scenario now fails. Show it on the diagram.")
    scene.click("#tests-list li.broken button:has-text('Show on diagram')")
    scene.caption("The kernel replays the scenario and paints the step that breaks: there is no way back from Overdue.")
    scene.zoom("#canvas", scale=1.3)
    scene.wait(2000)
    scene.zoom_out()
    _broken_sequence(scene)
    scene.click("#tab-review")
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
    scene.goto(f"{server.base_url}/play?view=review#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    chapter("Share it as UML")
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
    scene.click("#tab-states")  # the traffic runs along the state machine's transitions
    if scene.page.get_attribute("#show-changes", "aria-pressed") == "true":
        scene.click("#show-changes")
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.caption("Simulate replays as traffic: green dots went through, red ones stop where the kernel refused them.")
    scene.zoom("#canvas", scale=1.5)
    scene.wait(2600)
    scene.zoom_out()
    scene.caption("Then prove the laws: every rule the policy states, checked over every run the kernel allows.")
    scene.click("#tab-laws")
    scene.wait_for("#laws-summary.ok, #laws-summary.bad", timeout_ms=120_000)
    scene.expect_text("#laws-summary", "holds on every run the kernel allows")
    scene.caption("Every law holds on every reachable run, and the summary says how far the proof searched.")
    scene.zoom("#laws", scale=1.3)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#tab-tests")
    scene.expect_text("#tests-summary", "All 7 tests pass", timeout_ms=60_000)
    scene.caption("And every scenario test passes again on the changed model.")
    scene.wait(1400)
    scene.click("#tab-states")
    scene.click("#health")
    scene.expect_text("#health-text", "5/5 checks")
    scene.expect_text("#check-next", "Every check passes")
    scene.caption("The ring fills only from real checks on what you are looking at. That is the score.")
    scene.zoom("#checks", scale=1.6)
    scene.wait(2400)


def _people(scene: Scene, chapter: _Chapters) -> None:
    """Humans in the model (ADR-0215): what each role sees, and the built app run as one of them."""
    chapter("People: who sees what")
    scene.caption("Design the people too. Pick a role and see the app the way they will.")
    scene.click("#tab-screens")
    scene.click("#role-lens button[data-role=Clerk]")
    scene.expect_text("#role-app", "A Clerk sees 2 of")
    scene.zoom("#role-app", scale=1.5)
    scene.wait(1800)
    scene.zoom_out()
    scene.caption(
        "The screens a Clerk never sees are struck through, because the kernel never lets a Clerk take them."
    )
    scene.zoom("#screen-list", scale=1.6)
    scene.wait(1600)
    scene.zoom_out()
    scene.click("#role-lens button[data-role='']")
    scene.click("#screen-a11y summary")
    scene.expect_text("#screen-a11y", "8 of 9 checks pass")
    scene.expect_text("#screen-a11y", "Renew: itemTitle")
    scene.caption(
        "The screens are checked like the model, against WCAG 2.2 AA. The AI's new Renew screen still needs field labels."
    )
    scene.zoom("#screen-a11y", scale=1.5)
    scene.wait(2000)
    scene.zoom_out()
    scene.click("#outline-roles button:has-text('Librarian')")
    scene.expect_text("#inspector", "assigned only")
    scene.caption(
        "Each actor lists what the kernel lets it do. CheckOut is narrowed by a guard: assigned librarians only."
    )
    scene.zoom("#inspector", scale=1.5)
    scene.wait(2000)
    scene.zoom_out()
    scene.caption("Run as opens the built app acting as that person, with their own actions first.")
    scene.click("#inspector button.run-as[data-actor='librarian-unassigned']")
    scene.expect_text(f"{APP} body", "librarian-unassigned", timeout_ms=BUILD_TIMEOUT_MS)
    scene.click("#dock-tab-run")  # the last build is reused, so bring its panel forward over Simulation
    scene.zoom("#run", scale=1.3)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#dock-close")


def _whole_system(scene: Scene, chapter: _Chapters) -> None:
    """Software architecture (ADR-0203): the workflows this one forms a system with, and where their classes disagree."""
    chapter("Software: the whole system")
    scene.caption(
        "Zoom out to the software. Workflows that share a class form one system, drawn as UML components."
    )
    scene.click("#tab-components")
    scene.click("#component-lens button[data-lens=system]")
    scene.expect_text("#landscape-summary", "disagree", timeout_ms=30_000)
    scene.zoom("#component-bar", scale=1.6)
    scene.wait(1600)
    scene.zoom_out()
    scene.caption(
        "The shared Member class is marked: two workflows' class diagrams disagree about it, before either ships."
    )
    scene.zoom("#landscape", scale=1.25)
    scene.wait(2200)
    scene.zoom_out()
    scene.click("#component-lens button[data-lens=app]")
    scene.click("#tab-states")


def _agents(scene: Scene, chapter: _Chapters) -> None:
    """AI agents, timers and outside systems as actors (ADR-0210), in a real-sector template (#159, #161)."""
    chapter("AI agents in the model")
    scene.caption(
        "Real systems have more than people in them. Start one from a template: permits, payments, parcels, care."
    )
    scene.click("#system-menu")
    scene.click("#systems-tab-new")
    scene.zoom("#systems-templates", scale=1.2)
    scene.wait(1800)
    scene.zoom_out()
    scene.click("#systems-templates input[value=refund-desk]")
    scene.type_text("#systems-name", "Refund desk", clear=True)
    scene.page.once("dialog", lambda dialog: dialog.accept())  # the imported plan is a throwaway: leave it
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "WithSupervisor")
    scene.chapter(
        chapter.n, "AI agents in the model"
    )  # the reload dropped the chip: show it again, same number
    scene.click("#tab-usecases")
    scene.caption(
        "An AI agent triages refunds, a timer escalates, the payment system reports back. Each is a UML actor."
    )
    scene.zoom("#usecase-canvas", scale=1.2)
    scene.wait(2400)
    scene.zoom_out()
    scene.caption("Ask for a hand-off to a supervisor, and slip in letting the agent approve refunds too.")
    scene.type_text("#chat-input", AGENT_RISKY)
    scene.click("#chat-send")
    scene.expect_text(f"{AI_CARD} .plan-verdict.bad", "Only a person approves a refund", timeout_ms=30_000)
    scene.caption(
        "The laws refuse it: only a person approves, and a person acts on every refund before it is paid."
    )
    scene.zoom(f"{AI_CARD} .plan-verdict", scale=1.5)
    scene.wait(2600)
    scene.zoom_out()
    scene.caption("Untick the step that hands the agent the approval: caught. The hand-off alone is allowed, and a person "
                  "still approves every refund.")
    scene.click(f"{AI_CARD} .plan-steps > li:nth-child(2) input")
    scene.expect_text("#game-notes", "Caught it", timeout_ms=30_000)  # the ring's biggest note (ADR-0208)
    scene.expect_text(f"{AI_CARD} .plan-verdict", "The policy allows the result: adds HandOff")
    scene.zoom("#health", scale=1.8)
    scene.wait(1600)
    scene.zoom_out()
    scene.click("#tab-sequences")
    scene.click("#seq-list li:has-text('cannot approve the refund it proposed') button")
    scene.expect_text("#sequence-canvas", "ROLE_DENIED", timeout_ms=30_000)
    scene.caption("A scenario test as a UML sequence diagram: the agent's ApproveRefund() call, refused by the kernel.")
    scene.zoom("#sequence-canvas", scale=1.3)
    scene.wait(2400)
    scene.zoom_out()
    scene.click("#tab-states")
    scene.caption(
        "Simulate: people, agents, timers and systems act, and the kernel refuses what the model forbids."
    )
    scene.click("#simulate")
    scene.expect_text("#sim-summary", "refused by the kernel", timeout_ms=60_000)
    scene.expect_text("#sim", "AI agents", timeout_ms=30_000)
    scene.zoom("#sim", scale=1.3)
    scene.wait(2600)
    scene.zoom_out()
    scene.click("#dock-close")


def _bring_your_own_uml(scene: Scene, chapter: _Chapters, server: RunningServer) -> None:
    scene.goto(f"{server.base_url}/play#{server.token}")
    scene.wait_for("body[data-ready=true]", timeout_ms=60_000)
    chapter("Bring your own UML tools")
    scene.caption("The model goes out as XMI, PlantUML, Mermaid or draw.io, and comes back in.")
    scene.click("#uml-menu")
    scene.zoom("#uml-pop", scale=1.6)
    scene.wait(1600)
    scene.zoom_out()
    scene.page.keyboard.press("Escape")
    # The pack's PlantUML export with one line added, as if edited in another UML tool.
    edited = ROOT / "demos/output/library-loan-edited.puml"
    edited.parent.mkdir(parents=True, exist_ok=True)
    text = EXPORTED.read_text(encoding="utf-8").replace("Returned --> [*]", EDITED_IN_ANOTHER_TOOL + "\nReturned --> [*]", 1)
    edited.write_text(text, encoding="utf-8", newline="\n")
    scene.caption("Edit the PlantUML anywhere and import it. The kernel reads it as typed edits and checks the laws.")
    scene.page.set_input_files("#uml-file", str(edited))
    scene.wait_for("#uml-import-dialog[open]", timeout_ms=30_000)
    scene.expect_text("#uml-import-dialog", "1 edit to the model in force. Laws: HOLDS")
    scene.zoom("#uml-import-dialog", scale=1.3)
    scene.wait(2000)
    scene.zoom_out()
    scene.click("#uml-plan")
    scene.expect_text(RIPPLE_CARD, "Imported from library-loan-edited.puml", timeout_ms=30_000)
    scene.caption("It lands as a plan like any other: previewed, rippled and checked, and nothing is saved.")
    scene.wait(1400)
    desk = ROOT / "demos/output/support-desk.puml"
    desk.write_text(DESK_PUML, encoding="utf-8", newline="\n")
    scene.caption("A whole system can start from a UML file too. What the kernel cannot carry is listed, with the reason.")
    scene.click("#uml-menu")
    scene.click("#uml-new-system")
    scene.page.set_input_files("#systems-uml-file", str(desk))
    scene.expect_text("#systems-import", "4 not imported", timeout_ms=30_000)
    scene.zoom("#systems-import", scale=1.3)
    scene.wait(2400)
    scene.zoom_out()
    scene.click("#systems-close")


def _start_your_own(scene: Scene, chapter: _Chapters) -> None:
    chapter("Start your own system")
    scene.caption("Start your own: name it, name its record, and sketch the state machine one line at a time.")
    scene.click("#system-menu")
    scene.click("#systems-tab-new")
    scene.click("#systems-templates input[value=blank]")
    scene.type_text("#systems-name", "Support desk", clear=True)
    scene.type_text("#systems-record", "Ticket", clear=True)
    scene.type_text("#systems-sketch", NEW_SYSTEM_SKETCH, clear=True, delay_range_ms=(20, 60))
    scene.wait_for("#systems-check.ok", timeout_ms=30_000)
    scene.expect_text("#systems-check", "4 states (starts in Open)")
    scene.caption("The kernel checks the sketch as you type. Then it opens as a system like any other.")
    scene.zoom("#systems-check", scale=1.5)
    scene.wait(1600)
    scene.zoom_out()
    # The imported plan is still open (PlayIDE keeps work in progress), so it asks before leaving: yes, it is a throwaway.
    scene.page.once("dialog", lambda dialog: dialog.accept())
    with scene.page.expect_navigation(timeout=60_000):
        scene.click("#systems-create")
    scene.reattach("body[data-ready=true]")
    scene.expect_text("#outline-states", "Triaged")
    scene.chapter(chapter.n, "Start your own system")  # the reload dropped the chip: show it again, same number
    scene.caption("Support desk, live: the state machine, classes, use cases and screens, all from that sketch.")
    scene.zoom("#canvas", scale=1.6)
    scene.wait(2000)
    scene.zoom_out()


def _broken_sequence(scene: Scene) -> None:
    """The same late-return scenario as a UML sequence diagram (ADR-0195), broken by the change on screen."""
    scene.click("#tab-sequences")
    scene.click("#seq-list li:has-text('returned late') button")
    scene.wait_for(".seq-verdict.bad", timeout_ms=30_000)
    scene.expect_text("#seq-verdict", "The change shown breaks it")
    scene.caption("As a UML sequence diagram, the late return now ends in the kernel's refusal. The model in force still does it.")
    scene.zoom("#sequence-canvas", scale=1.3)
    scene.wait(2200)
    scene.zoom_out()
