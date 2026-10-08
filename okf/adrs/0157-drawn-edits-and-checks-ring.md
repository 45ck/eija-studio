---
type: Architecture Decision Record
title: 'ADR-0157: Drawn edits join the plan, and a checks ring rewards checking'
description: The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
resource: repo://docs/adr/0157-drawn-edits-and-checks-ring.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0157-drawn-edits-and-checks-ring.md
  title: 0157-drawn-edits-and-checks-ring.md
  hash_method: lf-sha256-v1
  sha256: f57372cbd618950d55762cbd7a6d2d545bdf851e7eaf27d79beaa66d4b16dc43
notes_baseline: 1d4ecef5557fd6e043f68977fe4614e4284556fcca1f9b891d9203ec44ba9bbd
---

# ADR-0157: Drawn edits join the plan, and a checks ring rewards checking

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0157-drawn-edits-and-checks-ring.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **Palette.** The state machine tab has a UML palette: State, Transition and Initial. Each can be dragged onto the diagram (dropped on a state, it starts there) or pressed. The inspector shows a short form, and the result joins the plan as a typed step (`add_state`, `add_transition`, `set_initial`). A selected state offers "Add a transition from here", "Start records here", "Rename…" and "Remove". A selected transition offers "Let <role> take it", "Move an end…" and "Remove". Delete removes the selection. Every drawn step is labelled "You"; AI steps are labelled "AI".
> * **Same check.** `preview_plan` now returns each step's text, so the server words every step, drawn or proposed. A legal drawn change is previewed at once. A plan's card in the chat is the one list of steps; a newer AI plan retires the old card.
> * **Checks ring.** The header shows a four-part ring. Each part is a real check on the model being shown (the base model, or the previewed plan with the screens on screen):
>   * every AI step looked at on the diagram ("Show me");
>   * the screens pass the design check;
>   * Build & run passed conformance for exactly this view;
>   * Simulate ran on exactly this view.
>   Any change to the plan or the screens empties the build and simulation parts until they are run again.
> * **Points.** Points are earned only for checking:
>   * +1 for looking at an AI step on the diagram;
>   * +3 for unticking an AI step when that alone turns a refused plan into one the policy allows (a step the policy caught);
>   * +3 for a conformance pass on a previewed AI change;
>   * +2 for simulating one.
>   Each award is given once per step or per plan state. Making steps, accepting them or drawing earns nothing. Points live in the page for the session; they are not evidence and are never stored.

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

* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…

## Referenced by

* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0170: PlayIDE asks about the selection, completes exact names, has a command palette and keyboard plan review](/adrs/0170-playide-assist-ask-complete-palette-review.md) - PlayIDE's chat proposes typed steps (ADR-0156) and rewards checking them (ADR-0157).
<!-- okf:generated:end links -->
