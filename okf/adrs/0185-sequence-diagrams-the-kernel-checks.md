---
type: Architecture Decision Record
title: 'ADR-0185: Sequence diagrams are the pack''s scenarios, drawn in UML and checked by the kernel step by step'
description: Engineers who read UML expect sequence diagrams beside the state machine, class, use case and component diagrams.
resource: repo://docs/adr/0185-sequence-diagrams-the-kernel-checks.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0185-sequence-diagrams-the-kernel-checks.md
  title: 0185-sequence-diagrams-the-kernel-checks.md
  hash_method: lf-sha256-v1
  sha256: 96a072e686c12ab90407a1a9d97d1966a28bc8fdd2301b1e5f633a666fb1e8cc
notes_baseline: 9936aa41fa8cebfa2f7daed580a343ae3c54ed6510524b5afbca800ab62c3c2f
---

# ADR-0185: Sequence diagrams as scenarios the kernel checks, message by message

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026: users are UML-literate engineers who expect several diagram kinds in proper notation, each tied to the kernel) |
| Source | `repo://docs/adr/0185-sequence-diagrams-the-kernel-checks.md` |

## Decision outcome (verbatim)

> Chosen option.
>
> * `application/sequences.py` `check_sequences(pack, model, scenarios, base)` runs each scenario with `scenario_run.run_scenario`, the runner the Tests tab and `eija scenarios` use, so every step is `runtime.execute`'s answer on an in-memory session. Each step becomes a message with a verdict:
>   * OK: the kernel did what the step expects, and the record moved to the state it names.
>   * HOLDS: a step that expects a refusal, refused with that code.
>   * BROKEN: the kernel did something else. The step's sentence and the kernel's reason in words (from the refusal code, the actor's role and the transition's) say what.
>   * NOT_REACHED: an earlier step was broken.
>   A scenario is PRODUCIBLE when no step is BROKEN. With `base`, the model in force, each scenario also runs there, so a change says which scenarios it `breaks` or `fixes`, and each message carries its action's status from `ghost_diff`.
> * The UML mapping: the step's actor and the record are lifelines (`loan : Loan` from the data model), each step is a synchronous call, the record's start state and its state after each committed step are state invariants, the transition's required effects are asynchronous messages to `«effect»` lifelines, a refusal is a dashed reply, and a step that expects a refusal sits in a `neg` combined fragment, the UML for a trace that must not happen, labelled with the code it expects.
> * `application/sequence_layout.py` computes the layout: lifeline columns in order of first use and rows top to bottom. The page draws boxes and arrows at those coordinates. It also exports each sequence as Mermaid and PlantUML through the existing `diagram_emitters`; `diagrams.Fragment` gains `operator` (`opt` or `neg`). Mermaid has no `neg`, so it is written as an `opt` labelled `neg:`, and PlantUML as `group neg`.
> * `POST /api/play/sequences` takes the request the Tests tab's route takes (an optional draft of `scenarios.json`). The ripple (`POST /api/play/ripple`) lists the pack's scenarios a plan breaks (warning `SEQUENCE_BROKEN`) or fixes.
> * The **Sequences** tab (`play-sequence.js`, `play-sequence.css`) lists the scenarios with their verdicts and draws the selected one. A step the model can't do is red, with the kernel's reason in the verdict line, the tooltip and the inspector. While a plan or change case is shown, a message says what it was on the model in force; with the Changes view on, messages whose action the change adds, changes or removes take that view's colours. Editing works on the one draft the Tests tab keeps (`window.PlayTests`): add a step in the row under the diagram (it expects what the kernel does now, through `/api/play/tests/try`, so a refused step arrives inside a `neg`), change a step's actor, action or expectation, take the kernel's outcome as the expectation, move or delete a step, set the title and start state, add or delete scenarios. Every edit is checked again on the server. Nothing is saved: **Export** copies Mermaid or PlantUML, or downloads `scenarios.json`. The review view (ADR-0172) hides the editing tools.

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

* [ADR-0024: Render Mermaid in a sandboxed frame so the Studio page keeps its strict CSP](/adrs/0024-sandboxed-frame-for-mermaid-rendering.md) - The Studio page ships `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancest…
* [ADR-0158: A change ripples across every diagram, and the AI's follow-on edits are re-checked](/adrs/0158-ripple-across-diagrams-with-checked-follow-ons.md) - PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the components of the built app.
* [ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE](/adrs/0166-laws-proved-over-every-run-for-any-pack.md) - Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned…
* [ADR-0172: A read-only review view of PlayIDE for people who review the model](/adrs/0172-review-view-for-reading-the-model.md) - The owner set the audience as people who know UML, and noted that UML "is meant for non technical people to review it sometimes".
* [ADR-0176: How a UML change looks: one stable layout, removed parts kept as ghosts, and lenses](/adrs/0176-how-a-uml-change-looks.md) - The owner asked how a change can be reviewed as a UML change instead of a pull request, and "how you even view a UML change (ghost UI/UX?)".
* [ADR-0177: The law file and the test cases are files PlayIDE opens, edits as drafts and runs](/adrs/0177-law-files-and-test-cases-in-playide.md) - The owner asked where the formal law files and the test cases are.
<!-- okf:generated:end links -->
