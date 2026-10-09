---
type: Function
title: domain.laws.reachable
description: States reachable from ``start`` without passing through ``blocked`` (cycle-safe).
resource: repo://src/eija_studio/domain/laws.py#reachable
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#reachable
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 0f6baef5fe7363ef04c0accc57ccb0410d595df5c5159a2e6a45e1fd625ebb36
notes_baseline: a10a950c6ab196adc5654dbe599877b3820ab301b0b9b56060d4194fc1497cba
---

# domain.laws.reachable

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def reachable(edges: Iterable[tuple[str, str]], start: str, blocked: str \| None=None) -> set[str]` |
| Code | `repo://src/eija_studio/domain/laws.py#reachable` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
States reachable from ``start`` without passing through ``blocked`` (cycle-safe).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.stuck_states](/symbols/domain/laws/stuck_states.md) - The states a record can get to from ``initial`` along ``edges`` from which no end of ``law`` can be reached.
<!-- okf:generated:end links -->
