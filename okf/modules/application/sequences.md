---
type: Module
title: application.sequences
description: The pack's scenarios drawn as UML sequence diagrams the kernel checks (ADR-0195).
resource: repo://src/eija_studio/application/sequences.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequences.py
  title: application/sequences.py
  hash_method: ast-api-v1
  sha256: 9c8a14539594b0fd107c857dee1df1fc278ffb2f369125488895e6eafbaf7174
notes_baseline: 39550b3071c74bcc1f599992d3dfb106956b7753f51faa2968fedc7b2d8c75bd
---

# application.sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/sequences.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The pack's scenarios drawn as UML sequence diagrams the kernel checks (ADR-0195).

There is one source of scenarios: `scenarios.json` (`domain.scenarios`, ADR-0177), run by `scenario_run`. A sequence
diagram is a view of one scenario: the actors and the record are lifelines, each step is a call from its actor to the
record, a step that expects a move shows the record's state after it as a UML state invariant, and a step that
expects a refusal is a `neg` combined fragment, the UML for a trace that must not happen. Each message's verdict is
the kernel's own answer for that step:

* OK: the kernel did what the step expects; the record moved to the state it names.
* HOLDS: a `neg` step the kernel refused, with the code the step names.
* BROKEN: the kernel did something else. The step's sentence and the kernel's reason say what.
* NOT_REACHED: an earlier step was broken, so the scenario stopped there.

A sequence is PRODUCIBLE when no step is BROKEN. With `base`, the model in force, every scenario is also run on it, so
a change shows which scenarios it breaks or fixes, and each message carries its action's status in the change
(`ghost_diff`, ADR-0176). `sequence_layout` places the result, so the page only draws boxes and arrows at the
coordinates it is given. What this does NOT establish: that a scenario is the right one, or anything about actors
the pack does not list; scenarios are examples, the laws (ADR-0166) are the universal claims.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/sequences/FORMAT.md) (constant) - no docstring
* [`LIMITS`](/symbols/application/sequences/LIMITS.md) (constant) - no docstring
* [`WHY`](/symbols/application/sequences/WHY.md) (constant) - no docstring
* [`check_sequences`](/symbols/application/sequences/check_sequences.md) (function) - Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, f…
* [`record_name`](/symbols/application/sequences/record_name.md) (function) - The record lifeline's name and its class: `loan : Loan` when the pack has a data model.

## Internal imports

* [`application/ghost_diff`](/modules/application/ghost_diff.md)
* [`application/scenario_run`](/modules/application/scenario_run.md)
* [`application/sequence_layout`](/modules/application/sequence_layout.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ghost_diff](/modules/application/ghost_diff.md) - How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).
* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [application.sequence_layout](/modules/application/sequence_layout.md) - Where a scenario's sequence diagram is drawn, and its export (ADR-0195).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.sequences.FORMAT](/symbols/application/sequences/FORMAT.md) - Constant `FORMAT` in `application/sequences`.
* [application.sequences.LIMITS](/symbols/application/sequences/LIMITS.md) - Constant `LIMITS` in `application/sequences`.
* [application.sequences.WHY](/symbols/application/sequences/WHY.md) - Constant `WHY` in `application/sequences`.
* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's name and its class: `loan : Loan` when the pack has a data model.
<!-- okf:generated:end links -->
