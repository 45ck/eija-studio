# ADR-0185: Sequence diagrams as scenarios the kernel checks, message by message

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026: users are UML-literate engineers who expect several diagram kinds in proper notation, each tied to the kernel)

## Context and problem statement

Engineers who read UML expect sequence diagrams beside the state machine, class, use case and component diagrams. PlayIDE had sequences only as generated pictures: the commit protocol of one `execute` (`application/diagrams.py`) and the Simulate run log. Nothing let an engineer write down a scenario ("a librarian lends, then either takes it back on time, or a clerk marks it overdue and it comes back late") and find out whether the model can actually do it, or see which scenarios an AI's change breaks.

A sequence diagram drawn in an ordinary tool can say anything. Here it must be a view of the one model: a message the model can't produce has to be flagged on the diagram, with the reason.

## Decision drivers

* One interpreter: the kernel decides every message, as it does for Simulate, the run bar, Permissions and the laws. No second reading of the diagram.
* Proper UML notation: lifelines, synchronous calls, replies, state invariants, asynchronous messages and combined fragments.
* One source per fact: a scenario adds no rule. Who may act, from where and with what effect stays in the state machine; a sequence only names actors and actions in order.
* A change shows its effect: the same scenarios on the model in force and on the change shown, through the ripple (ADR-0158) and the change view (ADR-0176).
* Readable and editable without a second canvas interaction model (the generic add and edit rework belongs to the UX lane).

## Considered options

* **Scenarios in `sequences.json`, checked by `runtime.execute`, laid out on the server and drawn with maxGraph (chosen).**
* Mermaid's `sequenceDiagram` (vendored, MIT). Kept for export, not chosen to draw: its output is a static SVG in a sandboxed frame (ADR-0024) with no per-message selection or styling, it has no `neg` operator, and it would be a third rendering stack in the page.
* PlantUML (GPL, or the MIT build): a Java process and static images. Reference only; we emit its text.
* js-sequence-diagrams (BSD-2): unmaintained since 2017, depends on Raphaël and Underscore, no fragments.
* ZenUML (MIT): a Vue application with its own DSL and editor; a second model of the interaction rather than a view of ours.
* Generic graph layout (Dagre, elkjs): a sequence diagram has no graph layout problem. The 2026-10-08 survey already recommended computing lifeline and message positions deterministically in Python.
* Deriving sequences only from Simulate traces. Not chosen alone: a trace says what random users did, not the scenario an engineer means. A trace can still become a sequence later.

## Decision outcome

Chosen option.

* `domain/sequences.py` holds the contract `eija.sequences.v1`: interactions with records (lifelines of the record class) and steps. A step is a message (`actor`, a fixture actor id; `action`; `record`) or a combined fragment: `opt [guard]`, `alt [guard] / [guard]` (two to four operands) or `neg` (an invalid trace, optionally with the refusal code it expects). Operands hold messages only; fragments do not nest. The file sits beside `pack.json` with its own digest, like `screens.json`. `packs/library-loan/sequences.json` has three scenarios.
* `application/sequences.py`:
  * `default_sequences(pack, model)` generates scenarios for a pack without the file: the shortest path to each final state taken by actors the kernel should let through, and one `neg` where someone in another role tries the first step. They are generated from the model in force, so a change is checked against the scenarios it had.
  * `check_sequences(pack, model, sequences, base)` unfolds each sequence into its traces (an `opt` doubles them, an `alt` multiplies them, at most 64) and runs every trace on fresh records through `runtime.execute` with an in-memory unit of work (`simulation.MemorySession`). A message is OK when the kernel commits it on every trace that reaches it, and BROKEN when it refuses it on some trace: the refusal code, a sentence and the trace's operand choices say why, and later messages on that trace are NOT_REACHED. A `neg` is tried in place and undone; it HOLDS when the kernel refuses it (with the named code, if any) and is BROKEN when the kernel lets the forbidden trace through. With `base`, every verdict is also worked out on the model in force, each sequence says whether the change `breaks` or `fixes` it, and each message carries its action's status from `ghost_diff`.
  * `application/sequence_layout.py` computes the layout: lifeline columns in order of first use (actors, records, effect channels) and rows top to bottom. The page draws boxes and arrows at those coordinates.
  * It also exports each sequence as Mermaid and PlantUML through the existing `diagram_emitters`. `diagrams.Fragment` gains `operator` (`opt`, `alt`, `neg`) and `alternatives`; Mermaid has no `neg`, so it is written as an `opt` labelled `neg:`, and PlantUML as `group neg`.
* `POST /api/play/sequences` takes the request Build & run takes, plus an optional edited document. The ripple (`POST /api/play/ripple`) lists the pack's scenarios a plan breaks (warning `SEQUENCE_BROKEN`) or fixes.
* The **Sequences** tab (`play-sequence.js`, `play-sequence.css`) lists the sequences with their verdicts and draws the selected one: actors as stick figures, the record and effect channels as boxes, dashed lifelines, filled-arrow calls, dashed refusal replies (red when unexpected, green when a `neg` expects them), `{State}` invariants on the record's lifeline after each message, effects as open-arrow asynchronous messages, and fragments as frames with the UML pentagon tab and guards. A message the model can't produce is red, with the kernel's reason in the verdict line, the tooltip and the inspector. While a plan or change case is shown, a message says what it was on the model in force; with the Changes view on, messages whose action the change adds, changes or removes take that view's colours. Editing is in the add-message row and the inspector: change a message's actor, action or record, move or delete it, wrap it in `opt`, `alt` or `neg`, edit guards and the expected refusal, add or delete sequences. Every edit is checked again on the server. Nothing is saved: **Export** copies Mermaid or PlantUML, or downloads `sequences.json` to keep beside the pack. The review view (ADR-0172) hides the editing tools.

### Consequences

* Good: an engineer can write the scenario they mean in UML and see, message by message, whether the model produces it, with the kernel's own refusal code.
* Good: `neg` fragments make forbidden scenarios executable checks ("a member never lends to themselves"), and a plan that breaks a scenario shows up in the ripple before anyone accepts it.
* Bad: scenarios run with the pack's fixture actors. They show what those actors can do, not every real actor; the laws (ADR-0166) are the universal claims.
* Bad: fragments do not nest, and `loop`, `par` and `break` are not supported. The ripple checks the pack's or default scenarios, not ones edited in the tab and not downloaded.
* Revisit when: Simulate traces should become sequences in one click, when packs gain cross-object messages (issue #93), or when the UX lane's inline-edit rework lands and the canvas itself can edit messages.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| maxGraph 0.25.0 (Apache-2.0, vendored) | Adopted to draw and select; it has no sequence layout or lifeline shape, so the frame tab is a 10-line shape after draw.io's `umlFrame` (Apache-2.0, geometry only) | draw.io's UML sequence stencils if maxGraph ships them |
| Mermaid 12.0.0 (MIT, vendored) | Static SVG in a sandboxed frame, no selection or per-message style, no `neg`; kept as an export format | Render the export in the sandboxed frame for a read-only view |
| PlantUML (GPL / MIT build) | Java process, static images; reference only | Exported text renders in any PlantUML |
| js-sequence-diagrams (BSD-2), ZenUML (MIT) | Unmaintained, or a second DSL and editor beside the model | — |
| Existing `runtime.execute` and `simulation.MemorySession` | Adopted: every message is the kernel's own answer | — |
