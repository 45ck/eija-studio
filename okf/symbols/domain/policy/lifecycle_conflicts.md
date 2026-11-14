---
type: Function
title: domain.policy.lifecycle_conflicts
description: 'Links to one class must declare the same lifecycle, its states, initial state and moves in any order (ADR-0241, amended 2026-11-13): an object has one state whichever link names it, and the built app stores one.'
resource: repo://src/eija_studio/domain/policy.py#lifecycle_conflicts
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#lifecycle_conflicts
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 0a679b8122a332dfc040d1cfbfb167ba752d95228705b0b41156284a0880bf6e
notes_baseline: 5acfb798997890fb14341b52db7d98ef175a8db035a735bce2b440be4c750640
---

# domain.policy.lifecycle_conflicts

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def lifecycle_conflicts(model: Workflow) -> list[str]` |
| Code | `repo://src/eija_studio/domain/policy.py#lifecycle_conflicts` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Links to one class must declare the same lifecycle, its states, initial state and moves in any order (ADR-0241,
amended 2026-11-13): an object has one state whichever link names it, and the built app stores one.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [domain.policy.declared_codes](/symbols/domain/policy/declared_codes.md) - Every transition must perform a declared action, held by a declared role, with exactly its declared guards and required effects, and must declare every pack-fo…
<!-- okf:generated:end links -->
