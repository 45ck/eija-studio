---
type: Architecture Decision Record
title: 'ADR-0185: Sequence diagrams as scenarios the kernel checks, message by message'
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
  sha256: f194b802a66a2d7e3af1dab28ad4033397cf9333d4feef7cae2ae3c81e39e0ae
notes_baseline: c8c303515d7297831c39c1233ce40c36aea7229c607dbc7fcb6272a83dad0360
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
> * `domain/sequences.py` holds the contract `eija.sequences.v1`: interactions with records (lifelines of the record class) and steps. A step is a message (`actor`, a fixture actor id; `action`; `record`) or a combined fragment: `opt [guard]`, `alt [guard] / [guard]` (two to four operands) or `neg` (an invalid trace, optionally with the refusal code it expects). Operands hold messages only; fragments do not nest. The file sits beside `pack.json` with its own digest, like `screens.json`. The library-loan pack ships three scenarios in its `sequences.json`.
> * `application/sequences.py`:
>   * `default_sequences(pack, model)` generates scenarios for a pack without the file: the shortest path to each final state taken by actors the kernel should let through, and one `neg` where someone in another role tries the first step. They are generated from the model in force, so a change is checked against the scenarios it had.
>   * `check_sequences(pack, model, sequences, base)` unfolds each sequence into its traces (an `opt` doubles them, an `alt` multiplies them, at most 64) and runs every trace on fresh records through `runtime.execute` with an in-memory unit of work (`simulation.MemorySession`). A message is OK when the kernel commits it on every trace that reaches it, and BROKEN when it refuses it on some trace: the refusal code, a sentence and the trace's operand choices say why, and later messages on that trace are NOT_REACHED. A `neg` is tried in place and undone; it HOLDS when the kernel refuses it (with the named code, if any) and is BROKEN when the kernel lets the forbidden trace through. With `base`, every verdict is also worked out on the model in force, each sequence says whether the change `breaks` or `fixes` it, and each message carries its action's status from `ghost_diff`.
>   * `application/sequence_layout.py` computes the layout: lifeline columns in order of first use (actors, records, effect channels) and rows top to bottom. The page draws boxes and arrows at those coordinates.
>   * It also exports each sequence as Mermaid and PlantUML through the existing `diagram_emitters`. `diagrams.Fragment` gains `operator` (`opt`, `alt`, `neg`) and `alternatives`; Mermaid has no `neg`, so it is written as an `opt` labelled `neg:`, and PlantUML as `group neg`.
> * `POST /api/play/sequences` takes the request Build & run takes, plus an optional edited document. The ripple (`POST /api/play/ripple`) lists the pack's scenarios a plan breaks (warning `SEQUENCE_BROKEN`) or fixes.
> * The **Sequences** tab (`play-sequence.js`, `play-sequence.css`) lists the sequences with their verdicts and draws the selected one: actors as stick figures, the record and effect channels as boxes, dashed lifelines, filled-arrow calls, dashed refusal replies (red when unexpected, green when a `neg` expects them), `{State}` invariants on the record's lifeline after each message, effects as open-arrow asynchronous messages, and fragments as frames with the UML pentagon tab and guards. A message the model can't produce is red, with the kernel's reason in the verdict line, the tooltip and the inspector. While a plan or change case is shown, a message says what it was on the model in force; with the Changes view on, messages whose action the change adds, changes or removes take that view's colours. Editing is in the add-message row and the inspector: change a message's actor, action or record, move or delete it, wrap it in `opt`, `alt` or `neg`, edit guards and the expected refusal, add or delete sequences. Every edit is checked again on the server. Nothing is saved: **Export** copies Mermaid or PlantUML, or downloads `sequences.json` to keep beside the pack. The review view (ADR-0172) hides the editing tools.

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
<!-- okf:generated:end links -->
