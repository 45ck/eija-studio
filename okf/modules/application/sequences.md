---
type: Module
title: application.sequences
description: 'Sequence diagrams the kernel checks (ADR-0185): can this model produce this interaction?'
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
  sha256: 974634d8448ce64b046b59755bd9120f64901c1c0d80face0d3f0588bdabe112
notes_baseline: 24440b7a658edb397ea5950e78c6221fca037ab435b37b5382d5dc9b00a072a4
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
Sequence diagrams the kernel checks (ADR-0185): can this model produce this interaction?

Each sequence (`domain.sequences`) is unfolded into its traces: an `opt` doubles them (with and without the operand), an
`alt` multiplies them by its operands, and a `neg` is tried in place and then undone. Every trace runs on fresh
records through `runtime.execute`, with the pack's fixture actors, against an in-memory unit of work, so each message's
verdict is the kernel's own answer, not a reading of the diagram:

* OK: the kernel committed the message on every trace that reaches it; the record's state after it is drawn as a UML
  state invariant on the record's lifeline, and the effects it performed as asynchronous messages.
* BROKEN: on some trace the kernel refused it. The refusal code and the trace's operand choices say why; the trace
  stops there, so later messages on it are not reached.
* A `neg` fragment HOLDS when the kernel refuses some message of its operand (with the code it names, if any), and is
  BROKEN when the kernel lets the whole forbidden trace through.

A sequence is PRODUCIBLE when nothing in it is BROKEN. With `base`, the model in force, every verdict is also worked
out on it, so a change shows which scenarios it breaks or fixes, and each message carries its action's status in the
change (`ghost_diff`, ADR-0176). `sequence_layout` places the result, so the page only draws boxes and arrows at
the coordinates it is given. What this does NOT establish: that a scenario is the right one, or anything
about actors the pack does not list; sequences are examples, the laws (ADR-0166) are the universal claims.
~~~

## Public symbols

* [`CASE`](/symbols/application/sequences/CASE.md) (constant) - no docstring
* [`Event`](/symbols/application/sequences/Event.md) (type-alias) - no docstring
* [`FORMAT`](/symbols/application/sequences/FORMAT.md) (constant) - no docstring
* [`LIMITS`](/symbols/application/sequences/LIMITS.md) (constant) - no docstring
* [`MAX_DEFAULTS`](/symbols/application/sequences/MAX_DEFAULTS.md) (constant) - no docstring
* [`MAX_PATHS`](/symbols/application/sequences/MAX_PATHS.md) (constant) - no docstring
* [`Seen`](/symbols/application/sequences/Seen.md) (type-alias) - no docstring
* [`WHY`](/symbols/application/sequences/WHY.md) (constant) - no docstring
* [`check_sequences`](/symbols/application/sequences/check_sequences.md) (function) - Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [`default_sequences`](/symbols/application/sequences/default_sequences.md) (function) - Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.
* [`record_name`](/symbols/application/sequences/record_name.md) (function) - The record lifeline's default name and its class: `loan : Loan` when the pack has a data model.
* [`sequences_for`](/symbols/application/sequences/sequences_for.md) (function) - The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default").

## Internal imports

* [`application/ghost_diff`](/modules/application/ghost_diff.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`application/sequence_layout`](/modules/application/sequence_layout.md)
* [`application/simulation`](/modules/application/simulation.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/sequences`](/modules/domain/sequences.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ghost_diff](/modules/application/ghost_diff.md) - How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.sequence_layout](/modules/application/sequence_layout.md) - Where a checked sequence is drawn, and its export (ADR-0185).
* [application.simulation](/modules/application/simulation.md) - Seeded simulation of people using the app built from a model (ADR-0152).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.sequences](/modules/domain/sequences.md) - Sequences: UML interactions between the pack's actors and its records, kept beside the pack (ADR-0185).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.sequences.CASE](/symbols/application/sequences/CASE.md) - Constant `CASE` in `application/sequences`.
* [application.sequences.Event](/symbols/application/sequences/Event.md) - Type alias `Event` in `application/sequences`.
* [application.sequences.FORMAT](/symbols/application/sequences/FORMAT.md) - Constant `FORMAT` in `application/sequences`.
* [application.sequences.LIMITS](/symbols/application/sequences/LIMITS.md) - Constant `LIMITS` in `application/sequences`.
* [application.sequences.MAX_DEFAULTS](/symbols/application/sequences/MAX_DEFAULTS.md) - Constant `MAX_DEFAULTS` in `application/sequences`.
* [application.sequences.MAX_PATHS](/symbols/application/sequences/MAX_PATHS.md) - Constant `MAX_PATHS` in `application/sequences`.
* [application.sequences.Seen](/symbols/application/sequences/Seen.md) - Type alias `Seen` in `application/sequences`.
* [application.sequences.WHY](/symbols/application/sequences/WHY.md) - Constant `WHY` in `application/sequences`.
* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [application.sequences.default_sequences](/symbols/application/sequences/default_sequences.md) - Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`.
* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's default name and its class: `loan : Loan` when the pack has a data model.
* [application.sequences.sequences_for](/symbols/application/sequences/sequences_for.md) - The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default").
<!-- okf:generated:end links -->
