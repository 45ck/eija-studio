---
type: Function
title: application.access.reach
description: Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?
resource: repo://src/eija_studio/application/access.py#reach
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/access.py#reach
  title: application/access.py
  hash_method: ast-v2
  sha256: 751207c83e3aa8144adcace1c8e39fb07f7e0115153c2d50de3d4f11bd0d5e71
notes_baseline: e8184390b72f039e2b22727fd7913ae902ca71ea758db83a5d306526d4eafb9c
---

# application.access.reach

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/access`](/modules/application/access.md) |
| Signature | `def reach(pack: Pack, model: Workflow, target: str, without: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/access.py#reach` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Can a record reach `target` with no step taken by role `without` (or at all, when it is None)? Starting the record
is a step too: when the model names who may start one, a record without them does not exist (ADR-0231), unless a
signal from another workflow starts it (ADR-0242).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.access.meeting](/symbols/application/access/meeting.md) - A record's values that meet every guard over values of these transitions (ADR-0234): {} when they have none, None when no values meet them all.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
