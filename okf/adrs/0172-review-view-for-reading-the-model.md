---
type: Architecture Decision Record
title: 'ADR-0172: A read-only review view of PlayIDE for people who review the model'
description: The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes".
resource: repo://docs/adr/0172-review-view-for-reading-the-model.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0172-review-view-for-reading-the-model.md
  title: 0172-review-view-for-reading-the-model.md
  hash_method: lf-sha256-v1
  sha256: 6fae5228e4fbcae76597cebaf64050665ec15754e5b40e9c556a355d76928e84
notes_baseline: 111cb2314b75c379968f8af9cfcca2e7f2d96ce7b81d0fa68c514fe2dfc4aa73
---

# ADR-0172: A read-only review view of PlayIDE for people who review the model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0172-review-view-for-reading-the-model.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * `/play?view=review` shows a "Review view · read only" badge with an **Edit** link back, and hides the drawing palette, the chat, every edit tool in the inspector (`edit-tools`), the screen designer's attribute palette and reset button. The screen card is `inert`: readable, not editable. Delete on the canvas does nothing.
> * Everything that reads or runs the model stays: all diagrams, **Permissions** (ADR-0171), Simulate, the run bar and its breakpoints, Build & run with the running app, and the checks ring.
> * The command palette offers "Open the review view (read-only)" and, in it, "Leave the review view (edit)". AI and plan commands are not listed there.
> * The page's session token still gates the page. The view is about what a reviewer sees, not about who may do what. The server's authority does not change.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls](/adrs/0064-hci-ai-interaction.md) - HCI-ADR-0064: AI and agent interaction: proposal cards, delegation fence, isolated owner controls
* [ADR-0171: Who can do what, as a matrix the kernel checks, and reachability questions with a proof or a path](/adrs/0171-permissions-matrix-and-reachability-questions.md) - Access rules are what AI-written apps most often get wrong, and they are what reviewers and auditors ask about first: who can do what, from which state, and ca…

## Referenced by

* [ADR-0173: PlayIDE's workbench shell, after Visual Studio, VS Code, Cursor and draw.io](/adrs/0173-playide-workbench-shell.md) - After watching the recorded tours, the owner said there was "too much going on in sidebar" and that it "feels weird", and asked to "make playIDE really good, c…
* [ADR-0174: Add UML elements without dragging, and edit them where they are](/adrs/0174-add-without-dragging-and-edit-inline.md) - After watching the showcase cut, the owner said "dragging sucks kind of" and asked whether to "use a modal when dragging or not even just edit inline?".
<!-- okf:generated:end links -->
