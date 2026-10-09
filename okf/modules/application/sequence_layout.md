---
type: Module
title: application.sequence_layout
description: Where a scenario's sequence diagram is drawn, and its export (ADR-0195).
resource: repo://src/eija_studio/application/sequence_layout.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_layout.py
  title: application/sequence_layout.py
  hash_method: ast-api-v1
  sha256: ac42d682989218df2510dd9b774c59ab59df10c08f810b13b309260381ca40bb
notes_baseline: c1b49eb81a1fed81b638dfda326c357b31741dfe22b36694eb1d5b4a542e0dd9
---

# application.sequence_layout

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/sequence_layout.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Where a scenario's sequence diagram is drawn, and its export (ADR-0195).

`place` lays a checked scenario out deterministically (`application.sequences`): lifeline columns in order of first
use (actors, then the record, then effect channels) and rows top to bottom, so the page only draws boxes and arrows at
the coordinates it is given. The record's start state is the first state invariant. A refused step gets a reply; a
committed one gets the record's state as a UML state invariant and its effects as asynchronous messages; a step that
expects a refusal sits in a `neg` frame. `export` writes the same sequence as Mermaid and PlantUML through the
existing `diagram_emitters`.
~~~

## Public symbols

* [`ROW`](/symbols/application/sequence_layout/ROW.md) (constant) - no docstring
* [`export`](/symbols/application/sequence_layout/export.md) (function) - The sequence as Mermaid and PlantUML text, through `diagram_emitters`, state invariants as notes (Mermaid has no neg: i…
* [`place`](/symbols/application/sequence_layout/place.md) (function) - no docstring

## Internal imports

* [`application/diagram_emitters`](/modules/application/diagram_emitters.md)
* [`application/diagrams`](/modules/application/diagrams.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.diagram_emitters](/modules/application/diagram_emitters.md) - Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).

## Referenced by

* [application.sequences](/modules/application/sequences.md) - The pack's scenarios drawn as UML sequence diagrams the kernel checks (ADR-0195).
* [application.sequence_layout.ROW](/symbols/application/sequence_layout/ROW.md) - Constant `ROW` in `application/sequence_layout`.
* [application.sequence_layout.export](/symbols/application/sequence_layout/export.md) - The sequence as Mermaid and PlantUML text, through `diagram_emitters`, state invariants as notes (Mermaid has no neg: it is written as opt).
* [application.sequence_layout.place](/symbols/application/sequence_layout/place.md) - `def place(pack: Pack, scenario: Scenario, start: str, steps: list[dict[str, Any]], record: tuple[str, str]) -…` in `application/sequence_layout`.
<!-- okf:generated:end links -->
