---
type: Function
title: application.runtime.check_separation
description: Refuse an actor who already took another action of a separation law on this record.
resource: repo://src/eija_studio/application/runtime.py#check_separation
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#check_separation
  title: application/runtime.py
  hash_method: ast-v2
  sha256: 06def3444ae336970195e73f35fb9fb02e07e16489ceb77295735429b1a764ca
notes_baseline: 3f04b462196dc22afd0f70e22b01616b6a50ed6a5ee310b59bd7e81d3d583f7e
---

# application.runtime.check_separation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def check_separation(laws: list[DistinctActors], action: str, actor_id: str, acts: list[tuple[str, str]]) -> None` |
| Code | `repo://src/eija_studio/application/runtime.py#check_separation` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Refuse an actor who already took another action of a separation law on this record. ``acts`` is the record's
(action, actor) history as the unit of work recorded it.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.DistinctActors](/symbols/domain/laws/DistinctActors.md) - Separation of duties (issue #149, ADR-0233): on one record, no single actor takes two different ``actions``, such as raising a request and approving it.
* [domain.laws.separation_breach](/symbols/domain/laws/separation_breach.md) - The other listed action ``actor`` already took on this record, if taking ``action`` now breaks ``law``.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
<!-- okf:generated:end links -->
