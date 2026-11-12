---
type: Function
title: domain.models.guard_keys
description: Value guards as a set compared by their JSON, as the semantic hash compares them.
resource: repo://src/eija_studio/domain/models.py#guard_keys
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#guard_keys
  title: domain/models.py
  hash_method: ast-v2
  sha256: 15985ca2855fafc71e2f3c91cc68c69041f9c8d542395cdd57f43ab17748d3b5
notes_baseline: 34d507be08e412ecc2e40d0ecc3254ed5dfb1448367832ae3ccf8417eb88cad2
---

# domain.models.guard_keys

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `def guard_keys(conditions: tuple[ValueGuard, ...]) -> frozenset[str]` |
| Code | `repo://src/eija_studio/domain/models.py#guard_keys` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Value guards as a set compared by their JSON, as the semantic hash compares them. Pydantic equality would make
``[x = true]`` equal ``[x = 1]`` (``True == 1`` in Python), though no record value satisfies both.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.

## Referenced by

* [domain.impact.changed_fields](/symbols/domain/impact/changed_fields.md) - Semantic differences of one action's transition.
* [domain.models.Transition.guarded](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models`.
<!-- okf:generated:end links -->
