---
type: Function
title: domain.policy.declared_codes
description: Every transition must perform a declared action, held by a declared role, with exactly its declared guards and required effects, and must declare every pack-forbidden effect forbidden.
resource: repo://src/eija_studio/domain/policy.py#declared_codes
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#declared_codes
  title: domain/policy.py
  hash_method: ast-v2
  sha256: d5328dfbe5b08e9c1e27c8259c7b453fd800cd731035390c232192f96dde7277
notes_baseline: a5d00c947a3454c37b199b013305421b994b1d6af2f877f6d4b5719c05c0be50
---

# domain.policy.declared_codes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def declared_codes(model: Workflow, pack: Pack) -> list[str]` |
| Code | `repo://src/eija_studio/domain/policy.py#declared_codes` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every transition must perform a declared action, held by a declared role, with exactly its declared guards and
required effects, and must declare every pack-forbidden effect forbidden.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.lifecycle_conflicts](/symbols/domain/policy/lifecycle_conflicts.md) - Links to one class must declare the same lifecycle, its states, initial state and moves in any order (ADR-0241, amended 2026-11-13): an object has one state wh…

## Referenced by

* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
<!-- okf:generated:end links -->
