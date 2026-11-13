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
  sha256: c0f766c8b281b90f66848773d28a7420d203d0850010ff06b109b0dccf30ae2e
notes_baseline: ac78b96ab3699b01f4786766faa32f4ca3070db15dc60bc8dcb3392677b2a614
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
is a step too: when the model names who may start one, a record without them does not exist (ADR-0231).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
