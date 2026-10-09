---
type: Architecture Decision Record
title: 'ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses'
description: The owner asked how a change can be reviewed as a UML change instead of a pull request, and "how you even view a UML change (ghost UI/UX?)".
resource: repo://docs/adr/0176-how-a-uml-change-looks.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0176-how-a-uml-change-looks.md
  title: 0176-how-a-uml-change-looks.md
  hash_method: lf-sha256-v1
  sha256: 5d904ed20dd701a36cb0e236e0966bf73881e0272fd7c06c3213edb33e4103ba
notes_baseline: 916845390dfd986aa74c866e1365f902bcaf14fad605f8ec463f3a80ccfee98b
---

# ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for the state machine |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0176-how-a-uml-change-looks.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **Server.** `application/ghost_diff.py` (`ghost_diff(before, after)`, format `eija.ghost-diff.v1`) is a pure function of two `Workflow`s. It returns every state and transition of both models, each with a status:
>   * `same`, `added` or `removed`, by membership;
>   * `changed`, with each changed field's before and after;
>   * `moved`, for an action that now joins other states. The new route is drawn, and the old one stays as a `was` ghost, so a moved arrow reads as one change rather than an unrelated delete and add.
>
>   It also returns a numbered list of changes in a fixed order, each with a sentence and the cell it is about. A moved initial state is one change. Reordering either model changes nothing. `POST /api/play/diff` diffs the change shown (a change case's candidate and any accepted plan steps) against the model in force (the active baseline or the case's baseline). It is read-only.
> * **The Changes view.** On the state machine tab, a **Changes** button with a count appears whenever there is a change. It swaps the editable canvas for the change drawn on one layout of both models:
>   * **Changes:** added elements in green with `+`, changed in amber with `~`, moved in amber with `↷` and the old route as a dashed `was` ghost, and removed elements kept as faded, dashed, struck-through ghosts with `−`. Unchanged elements fade back as context (**Fade unchanged**).
>   * **Before:** the model in force, with nothing the change adds.
>   * **After:** the change, with nothing it removes.
>   * **Onion skin:** a slider between Before and After.
>
>   No state moves between lenses. The change list under the diagram says each change in a sentence. `[` and `]` (or the arrows) step through it, and the inspector shows the change with a before and after table for each changed field. `B`, `C` and `A` pick a lens while focus is in the view. Another tab, or pressing **Changes** again, returns to the editable diagram.
> * **Stable preview.** While a plan can be previewed, the state machine tab lays out the model in force and the candidate together, in a fixed order. Preview and Back to the model no longer move any state, and a removed state leaves its gap.
> * **One renderer for every view of a change.** The renderer is `window.PlayDiff.mount(box, ghost, options)`. It returns lenses, the onion skin, `show(change)` and `fit()`. The Review tab (ADR-0175) now draws its canvas with it: `POST /api/play/review` also returns the union, the canvas lays it out top to bottom, and the review's knock-on states are tinted amber. There is one way a change is drawn, not two.

## Sections

* Context and problem statement
* Decision drivers
* What existing tools do
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0153: Data models as UML class diagrams, checked in the built app](/adrs/0153-data-models-as-uml-class-diagrams.md) - Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.
* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE](/adrs/0166-laws-proved-over-every-run-for-any-pack.md) - Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned…
* [ADR-0175: Review a change as a UML diff you can run, not as a pull request](/adrs/0175-review-a-change-as-a-uml-diff-you-can-run.md) - The owner wants engineers to stop "reviewing changes in a GitHub PR when you can do it through the IDE in a much better, fun, quicker way that is more accurate…

## Referenced by

* [ADR-0195: Sequence diagrams are the pack's scenarios, drawn in UML and checked by the kernel step by step](/adrs/0195-sequence-diagrams-the-kernel-checks.md) - Engineers who read UML expect sequence diagrams beside the state machine, class, use case and component diagrams.
* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).
<!-- okf:generated:end links -->
