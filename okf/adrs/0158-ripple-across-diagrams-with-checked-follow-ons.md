---
type: Architecture Decision Record
title: 'ADR-0158: A change ripples across every diagram, and the AI''s follow-on edits are re-checked'
description: 'PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.'
resource: repo://docs/adr/0158-ripple-across-diagrams-with-checked-follow-ons.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0158-ripple-across-diagrams-with-checked-follow-ons.md
  title: 0158-ripple-across-diagrams-with-checked-follow-ons.md
  hash_method: lf-sha256-v1
  sha256: cd96beb1a51b13bfc5bd0a0eb20b78a69232906934ea9869c3084e88b2d7c6f4
notes_baseline: ab1aa0c4351cbaa80edd65b9c9466a807b19ff2b46618c58ace6b9801228784b
---

# ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0158-ripple-across-diagrams-with-checked-follow-ons.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * **Ripple** (`application/ripple.py`, `POST /api/play/ripple`). Given the request's accepted plan steps and the designer's screens, the server compares the saved system (the active model with the pack's screens) with the plan's version. Every effect is `added`, `removed`, `changed`, `warning` (the app still builds) or `problem` (out of step):
>   * **State machine:** added and removed states and actions, changed actions, a new initial state; `STATE_UNREACHABLE` for a state that no transition now leads into, and `STATE_NO_EXIT` for a state that had a way out and now has none.
>   * **Class diagram:** the record class has a `state` association to a derived `«enumeration» <Record>State`, whose literals are the state machine's states. A state added or removed is a literal added or removed.
>   * **Use cases:** use cases (actions) added or gone, actor associations (role takes action) added or gone, and actors added or gone.
>   * **Screens:** default screens the build would add, screens dropped, and every design problem the change introduces (`check_screens`).
>   * **Components:** each drawn component whose generated files differ between the two builds, and `SCREENS_BLOCKED` when the plan's version cannot be built.
>   * **Conformance:** the number of oracle cases before and after.
>   A plan *agrees* when it has no `problem`; warnings are shown but do not block.
> * **Follow-ons.** When the ripple has warnings or problems, the server asks the plan proposer (the `PlanProposer` port gains `follow_on`) for follow-on steps: a state-machine transaction, or a screen step that adds or removes one screen. `check_follow_ons` re-checks each one on its own: a transaction with the plan through the policy (`apply_transactions`), a screen step by the design check. A screen step that does not reduce the design problems is refused (`FOLLOW_ON_FIXES_NOTHING`). The offline proposer (`offline-plan-fixture-v1`) uses fixed rules:
>   * a default screen for a use case without one, and no screen for a use case that is gone;
>   * for an unreachable state, a transition into it from the nearest reachable state before it, using a declared action the model does not use yet;
>   * for a state with no way out, a transition to an end state its neighbours lead to.
>   These are guesses. The page labels them AI, offline fixture, not a live model.
> * **Page.** Each diagram tab carries a badge with its count of effects: amber for warnings, red for problems. While the plan is previewed, added and changed elements are marked on each diagram; on the model without the plan, removed ones are marked in red. The plan's card in the chat lists the ripple by diagram. Clicking an effect opens that diagram at that element. The card also lists the AI follow-ons with an Add button for each one the server accepts:
>   * a transaction joins the plan as an AI step;
>   * a screen step replaces the designer's screens.
>   Either way the plan, the screens and the ripple are checked again.
> * **Checks ring.** A fifth part, "Diagrams agree", is green when there is no change or the current ripple has no problem. Following ADR-0157, points come only from checking: +1 the first time you open the ripple on each other diagram, for each version of the plan. Taking a follow-on earns nothing.

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

* [ADR-0153: Data models as UML class diagrams, checked in the built app](/adrs/0153-data-models-as-uml-class-diagrams.md) - Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.
* [ADR-0155: Component diagrams read from the generated code](/adrs/0155-component-diagrams-read-from-the-generated-code.md) - The owner's roadmap asks for component diagrams after use cases and screens.
* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
<!-- okf:generated:end links -->
