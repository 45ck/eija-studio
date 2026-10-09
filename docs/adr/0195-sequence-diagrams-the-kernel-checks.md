# ADR-0195: Sequence diagrams are the pack's scenarios, drawn in UML and checked by the kernel step by step

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026: users are UML-literate engineers who expect several diagram kinds in proper notation, each tied to the kernel)

## Context and problem statement

Engineers who read UML expect sequence diagrams beside the state machine, class, use case and component diagrams. PlayIDE had sequences only as generated pictures: the commit protocol of one `execute` (`application/diagrams.py`) and the Simulate run log. Nothing drew a scenario ("a librarian lends a book, a clerk marks it overdue, the librarian takes it back late") as a sequence diagram an engineer can read and edit, showed whether the model can actually do it, or showed which scenarios an AI's change breaks.

ADR-0177 added the pack's scenarios (`scenarios.json`, the Tests tab) while this was being built. A scenario is exactly what a sequence diagram of one record shows: who calls what, in order, and what must happen. A second scenario file for the Sequences tab would be a parallel source of the same facts, which AGENTS.md rules out.

A sequence diagram drawn in an ordinary tool can say anything. Here it must be a view of the one model: a message the model can't produce has to be flagged on the diagram, with the reason.

## Decision drivers

* One interpreter: the kernel decides every message, as it does for Simulate, the run bar, Permissions and the laws. No second reading of the diagram.
* Proper UML notation: lifelines, synchronous calls, replies, state invariants, asynchronous messages and combined fragments.
* One source per fact: the scenarios in `scenarios.json` are the only scenarios, and a scenario adds no rule. Who may act, from where and with what effect stays in the state machine.
* A change shows its effect: the same scenarios on the model in force and on the change shown, through the ripple (ADR-0158) and the change view (ADR-0176).
* Readable and editable without a second canvas interaction model (the generic add and edit rework belongs to the UX lane).

## Considered options

* **Draw the pack's scenarios (`scenarios.json`, ADR-0177) as sequence diagrams, checked by their runner `scenario_run`, laid out on the server and drawn with maxGraph (chosen).**
* A separate `sequences.json` (`eija.sequences.v1`) with `opt`, `alt` and `neg` fragments and its own trace runner. Built first, then dropped when ADR-0177 landed: two scenario files and two runners for one kind of fact.
* Extend `eija.scenarios.v1` with `opt` and `alt` now. Left for later: it changes the Tests tab's format and runner, which the executable UML lane owns; a scenario with branches is several test cases until then.
* Mermaid's `sequenceDiagram` (vendored, MIT). Kept for export, not chosen to draw: its output is a static SVG in a sandboxed frame (ADR-0024) with no per-message selection or styling, it has no `neg` operator, and it would be a third rendering stack in the page.
* PlantUML (GPL, or the MIT build): a Java process and static images. Reference only; we emit its text.
* js-sequence-diagrams (BSD-2): unmaintained since 2017, depends on Raphaël and Underscore, no fragments.
* ZenUML (MIT): a Vue application with its own DSL and editor; a second model of the interaction rather than a view of ours.
* Generic graph layout (Dagre, elkjs): a sequence diagram has no graph layout problem. The 2026-10-08 survey already recommended computing lifeline and message positions deterministically in Python.
* Deriving sequences only from Simulate traces. Not chosen alone: a trace says what random users did, not the scenario an engineer means. A trace can still become a sequence later.

## Decision outcome

Chosen option.

* `application/sequences.py` `check_sequences(pack, model, scenarios, base)` runs each scenario with `scenario_run.run_scenario`, the runner the Tests tab and `eija scenarios` use, so every step is `runtime.execute`'s answer on an in-memory session. Each step becomes a message with a verdict:
  * OK: the kernel did what the step expects, and the record moved to the state it names.
  * HOLDS: a step that expects a refusal, refused with that code.
  * BROKEN: the kernel did something else. The step's sentence and the kernel's reason in words (from the refusal code, the actor's role and the transition's) say what.
  * NOT_REACHED: an earlier step was broken.
  A scenario is PRODUCIBLE when no step is BROKEN. With `base`, the model in force, each scenario also runs there, so a change says which scenarios it `breaks` or `fixes`, and each message carries its action's status from `ghost_diff`.
* The UML mapping: the step's actor and the record are lifelines (`loan : Loan` from the data model), each step is a synchronous call, the record's start state and its state after each committed step are state invariants, the transition's required effects are asynchronous messages to `«effect»` lifelines, a refusal is a dashed reply, and a step that expects a refusal sits in a `neg` combined fragment, the UML for a trace that must not happen, labelled with the code it expects.
* `application/sequence_layout.py` computes the layout: lifeline columns in order of first use and rows top to bottom. The page draws boxes and arrows at those coordinates. It also exports each sequence as Mermaid and PlantUML through the existing `diagram_emitters`; `diagrams.Fragment` gains `operator` (`opt` or `neg`). Mermaid has no `neg`, so it is written as an `opt` labelled `neg:`, and PlantUML as `group neg`.
* `POST /api/play/sequences` takes the request the Tests tab's route takes (an optional draft of `scenarios.json`). The ripple (`POST /api/play/ripple`) lists the pack's scenarios a plan breaks (warning `SEQUENCE_BROKEN`) or fixes.
* The **Sequences** tab (`play-sequence.js`, `play-sequence.css`) lists the scenarios with their verdicts and draws the selected one. A step the model can't do is red, with the kernel's reason in the verdict line, the tooltip and the inspector. While a plan or change case is shown, a message says what it was on the model in force; with the Changes view on, messages whose action the change adds, changes or removes take that view's colours. Editing works on the one draft the Tests tab keeps (`window.PlayTests`): add a step in the row under the diagram (it expects what the kernel does now, through `/api/play/tests/try`, so a refused step arrives inside a `neg`), change a step's actor, action or expectation, take the kernel's outcome as the expectation, move or delete a step, set the title and start state, add or delete scenarios. Every edit is checked again on the server. Nothing is saved: **Export** copies Mermaid or PlantUML, or downloads `scenarios.json`. The review view (ADR-0172) hides the editing tools.

### Consequences

* Good: one scenario, two views. The test case a person writes in the Tests tab is the sequence diagram an engineer reads here, and an edit in either shows in both.
* Good: a plan that breaks a scenario shows up in the ripple, on the tab badge and on the diagram before anyone accepts it.
* Bad: scenarios run with the pack's fixture actors on one record. They show what those actors can do, not every real actor; the laws (ADR-0166) are the universal claims.
* Bad: no `opt`, `alt`, `loop` or `par`, because scenarios have none; a branching story is several scenarios. The ripple checks the pack's scenarios, not an unsaved draft.
* Revisit when: scenarios gain branches or several records (issue #93), Simulate traces should become scenarios in one click, or the UX lane's inline-edit rework lands and the canvas itself can edit messages.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| maxGraph 0.25.0 (Apache-2.0, vendored) | Adopted to draw and select; it has no sequence layout or lifeline shape, so the frame tab is a 10-line shape after draw.io's `umlFrame` (Apache-2.0, geometry only) | draw.io's UML sequence stencils if maxGraph ships them |
| Mermaid 12.0.0 (MIT, vendored) | Static SVG in a sandboxed frame, no selection or per-message style, no `neg`; kept as an export format | Render the export in the sandboxed frame for a read-only view |
| PlantUML (GPL / MIT build) | Java process, static images; reference only | Exported text renders in any PlantUML |
| js-sequence-diagrams (BSD-2), ZenUML (MIT) | Unmaintained, or a second DSL and editor beside the model | — |
| Existing `scenarios.json` and `scenario_run` (ADR-0177) | Adopted: the scenarios are the only scenarios, and their runner decides every step through `runtime.execute` | — |
