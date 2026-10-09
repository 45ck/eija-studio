---
type: Function
title: domain.laws.stuck_states
description: The states a record can get to from ``initial`` along ``edges`` from which no end of ``law`` can be reached.
resource: repo://src/eija_studio/domain/laws.py#stuck_states
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#stuck_states
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 45ee324c143cd5546b4a9b689709a211bfd83877b35d32234519e551cca48b79
notes_baseline: 18bf6e1cdf91486269874aba03a3b4352db462393d69888d54a04966bcbad32f
---

# domain.laws.stuck_states

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def stuck_states(law: CanReachEnd, edges: Iterable[tuple[str, str]], initial: str) -> list[str]` |
| Code | `repo://src/eija_studio/domain/laws.py#stuck_states` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The states a record can get to from ``initial`` along ``edges`` from which no end of ``law`` can be reached.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.CanReachEnd](/symbols/domain/laws/CanReachEnd.md) - From every state a record can get to, some run still reaches one of ``states`` (its ends): no record is left in a dead end or a loop with no way out.
* [domain.laws.reachable](/symbols/domain/laws/reachable.md) - States reachable from ``start`` without passing through ``blocked`` (cycle-safe).
<!-- okf:generated:end links -->
