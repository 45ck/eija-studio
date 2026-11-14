---
type: Architecture Decision Record
title: 'ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects'
description: The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or rejects them.
resource: repo://docs/adr/0156-chat-plan-mode-proposes-typed-steps.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0156-chat-plan-mode-proposes-typed-steps.md
  title: 0156-chat-plan-mode-proposes-typed-steps.md
  hash_method: lf-sha256-v1
  sha256: 5c1da59c5f235baa3be49870f5cec3cee794bdc318822e5f4ea2d89eaed2c2f7
notes_baseline: 3e734fe8bc31f19359bf455681a096c56bc357198fa9e68e288e63060e16cf38
---

# ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0156-chat-plan-mode-proposes-typed-steps.md` |

## Decision outcome (verbatim)

> Chosen option: an application-owned `PlanProposer` port, `application/plan.py`, and an offline proposer.
>
> * `PlanProposer.propose(request, model, pack)` returns a document of steps, each a transaction and a reason. The offline proposer (`adapters/plan_proposals.py`, `offline-plan-fixture-v1`, `live: false`) reads a bounded phrase grammar using exact model names ("add state Lost after Overdue then add Renew from Overdue to Lost for Librarian"), or matches the pack's own proposal rules to a supported meaning with transactions. Anything else is refused with the phrases it understands. It is a fixture, not an AI, and the UI labels it.
> * `propose_plan` treats the document as untrusted: it re-parses every step with `parse_transaction`, bounds the plan to 12 steps and the request to 2,000 characters, and keeps a meaning only if the pack has it.
> * `preview_plan(model, pack, transactions, accepted)` checks each accepted step after the accepted steps before it, so a step that needs a rejected one says `PLAN_STEP_DOES_NOT_APPLY`. The accepted steps are then applied together through `apply_transactions`, the same policy as an owner's edit, so a protected-authority change is refused with the policy's codes. A legal preview returns the candidate model, its semantic hash and the diff.
> * `POST /api/play/plan` and `POST /api/play/plan/preview` expose them. `BuildRequest.plan` lets **Build & run**, **Simulate**, **Screens** and **Components** run on the candidate: the server recomputes it from the steps, never trusting a model the browser sends.
> * The chat panel sits at the top of PlayIDE's sidebar with a "Plan mode" label. Each step has a checkbox; **Preview on the diagram** redraws every tab from the candidate, highlights what changed and shows a banner with **Back to the model**. A plan from a modelled meaning offers **Make it a change case**, which opens a case from the request; its meaning is still chosen in the review workbench.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/quality/inspections/2026-11-14-ai-chat-deeper.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0230: Opt-in live plan mode, and a plan check for coding agents](/adrs/0230-opt-in-live-plan-mode-and-agent-plan-check.md) - On 2026-10-08 the owner kept PlayIDE's chat offline and synthetic: a phrase reader plus the pack's proposal rules, never a model.
* [ADR-0234: Guards over record values](/adrs/0234-guards-over-record-values.md) - Issue #93, item 1.
* [ADR-0237: Time events on transitions](/adrs/0237-time-events.md) - Issue #93, item 2.

## Referenced by

* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review](/adrs/0170-playide-assist-ask-complete-palette-review.md) - PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).
* [ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io](/adrs/0173-playide-workbench-shell.md) - After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, c…
* [ADR-0174: Add UML elements without dragging, and edit them where they are](/adrs/0174-add-without-dragging-and-edit-inline.md) - After watching the showcase cut, the owner said "dragging sucks kind of" and asked whether to "use a modal when dragging or not even just edit inline?".
* [ADR-0175: Review a change as a UML diff you can run, not as a pull request](/adrs/0175-review-a-change-as-a-uml-diff-you-can-run.md) - The owner wants engineers to stop "reviewing changes in a GitHub PR when you can do it through the IDE in a much better, fun, quicker way that is more accurate…
* [ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses](/adrs/0176-how-a-uml-change-looks.md) - The owner asked how a change can be reviewed as a UML change instead of a pull request, and "how you even view a UML change (ghost UI/UX?)".
* [ADR-0177: The law file and the test cases are files PlayIDE opens, edits as drafts and runs](/adrs/0177-law-files-and-test-cases-in-playide.md) - The owner asked where the formal law files and the test cases are.
* [ADR-0198: Undo, redo and autosave of the edited document in PlayIDE](/adrs/0198-undo-redo-and-autosave-of-the-edited-document.md) - PlayIDE is meant to be more robust than the UML tools engineers already use, and every one of those has undo.
* [ADR-0230: Opt-in live plan mode, and a plan check for coding agents](/adrs/0230-opt-in-live-plan-mode-and-agent-plan-check.md) - On 2026-10-08 the owner kept PlayIDE's chat offline and synthetic: a phrase reader plus the pack's proposal rules, never a model.
<!-- okf:generated:end links -->
