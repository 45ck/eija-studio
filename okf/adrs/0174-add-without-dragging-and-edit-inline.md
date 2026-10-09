---
type: Architecture Decision Record
title: 'ADR-0174: Add UML elements without dragging, and edit them where they are'
description: After watching the showcase cut, the owner said "dragging sucks kind of" and asked whether to "use a modal when dragging or not even just edit inline?".
resource: repo://docs/adr/0174-add-without-dragging-and-edit-inline.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0174-add-without-dragging-and-edit-inline.md
  title: 0174-add-without-dragging-and-edit-inline.md
  hash_method: lf-sha256-v1
  sha256: 209e88b54ef0bc079e69178d3232f893756fa91f9af6748a2e9e5fd3fe3239b7
notes_baseline: 49f56c87615d0d0852f3ec30b72d0de30300fadd52c40ae16d4cd2ffed5b8ad6
---

# ADR-0174: Add UML elements without dragging, and edit them where they are

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0174-add-without-dragging-and-edit-inline.md` |

## Decision outcome (verbatim)

> | Gesture | What happens |
> |---|---|
> | Click State in the palette, then click the diagram | A name editor opens at that point. Clicking on a state places the new state after it. |
> | Click Transition, then the state it leaves, then the state it goes to | An editor under the target asks only for the action and who may take it. Clicking the same state twice makes a self-transition. |
> | Click Initial, then a state | The step is added at once. |
> | Double-click empty space | A new state's name editor opens there. |
> | Double-click a state | Rename it in place. |
> | Double-click a transition | Change who may take it. |
> | Drag from the palette (kept) | Drops into the same editor, at the drop point. |
> | Enter or Space on a palette item | The full form opens in the inspector, as before, so the keyboard needs no pointing. |
>
> * An armed palette item shows as pressed, the cursor becomes a crosshair and the hint under the diagram says what to click next. A tool places one element and is put down; Escape or clicking the item again puts it down sooner.
> * In the editor, Enter adds the step to the plan and Escape drops it. Clicking elsewhere drops an editor that is still empty; one with something typed stays until Enter or Escape.
> * The review view ignores every one of these gestures.
> * The code is in `play.js` (`arm`, `inlineEdit`, `onCanvasClick`, `onCanvasDoubleClick`, `wireCanvas`) and `play.css`. It reuses `formFor` and `addStep`, so the steps are the same typed transactions as before. The demo recorder gains `Scene.click_at` for clicking a point on the diagram.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* Amendment, 9 October 2026: shapes land where you put them
* Amendment, 9 October 2026: the diagram stays on camera
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_play_canvas_on_camera.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
* [ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review](/adrs/0170-playide-assist-ask-complete-palette-review.md) - PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).
* [ADR-0172: A read-only review view of PlayIDE for people who review the model](/adrs/0172-review-view-for-reading-the-model.md) - The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes".
* [ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io](/adrs/0173-playide-workbench-shell.md) - After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, c…
* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).

## Referenced by

* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).
<!-- okf:generated:end links -->
