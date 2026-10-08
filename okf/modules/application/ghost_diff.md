---
type: Module
title: application.ghost_diff
description: 'How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).'
resource: repo://src/eija_studio/application/ghost_diff.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ghost_diff.py
  title: application/ghost_diff.py
  hash_method: ast-api-v1
  sha256: 42bb6d835c568907266c01a56ee0f5525fabceea75f1a1a29491730b0cc7108f
notes_baseline: 4669bf9b18a833c809a448fccd6a3430cebb1deafc737c2e2cef867d96f1f0a1
---

# application.ghost_diff

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/ghost_diff.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).

`ghost_diff(before, after)` is a pure function of two `Workflow`s. It returns the union of their states and
transitions, each with a status, so a page can draw the model in force, the change, and every step between them on
one stable layout:

* `same`, `added` and `removed` by membership. A removed state or transition stays in the picture as a ghost, so a
  deleted path is seen rather than missed (LemonTree, for example, does not draw a deleted element at all).
* `changed`: the action keeps its endpoints and any other field changed. `fields` lists each one with its before and
  after, using `domain.impact.changed_fields`, the one definition of "changed" the ripple and the Mermaid diff share.
* `moved`: the action now joins other states. The new route is drawn, and the old one stays as a `was` ghost
  (key `was:<id>`), so a moved arrow is one change, not an unrelated delete and add.

Every change is also listed, in a fixed order, with a sentence and the cell it is about, so a reviewer can step
through them like hunks in a code review. What this does NOT establish: whether a change is right or what it does at
run time; the ripple (ADR-0158) and the kernel answer those.
~~~

## Public symbols

* [`FIELD_TEXT`](/symbols/application/ghost_diff/FIELD_TEXT.md) (constant) - no docstring
* [`FORMAT`](/symbols/application/ghost_diff/FORMAT.md) (constant) - no docstring
* [`ghost_diff`](/symbols/application/ghost_diff/ghost_diff.md) (function) - The union of two state machines, each element with its status, and the ordered list of changes.

## Internal imports

* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [application.sequences](/modules/application/sequences.md) - Sequence diagrams the kernel checks (ADR-0185): can this model produce this interaction?
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.ghost_diff.FIELD_TEXT](/symbols/application/ghost_diff/FIELD_TEXT.md) - Constant `FIELD_TEXT` in `application/ghost_diff`.
* [application.ghost_diff.FORMAT](/symbols/application/ghost_diff/FORMAT.md) - Constant `FORMAT` in `application/ghost_diff`.
* [application.ghost_diff.ghost_diff](/symbols/application/ghost_diff/ghost_diff.md) - The union of two state machines, each element with its status, and the ordered list of changes.
<!-- okf:generated:end links -->
