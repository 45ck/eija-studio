---
type: Function
title: domain.laws.separation_breach
description: The other listed action ``actor`` already took on this record, if taking ``action`` now breaks ``law``.
resource: repo://src/eija_studio/domain/laws.py#separation_breach
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#separation_breach
  title: domain/laws.py
  hash_method: ast-v2
  sha256: a505bc41199b93073a31677b95fd71034de4f2ed913e16e2f5a99dcabb5647c4
notes_baseline: 20e725e39acde46f9bb3bc55ef100aa8b59f96330421993e917ee6143f43138b
---

# domain.laws.separation_breach

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def separation_breach(law: DistinctActors, action: str, actor: str, earlier: Iterable[tuple[str, str]]) -> str \| None` |
| Code | `repo://src/eija_studio/domain/laws.py#separation_breach` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The other listed action ``actor`` already took on this record, if taking ``action`` now breaks ``law``.
``earlier`` is the record's (action, actor) history. None when the step is allowed.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.DistinctActors](/symbols/domain/laws/DistinctActors.md) - Separation of duties (issue #149, ADR-0233): on one record, no single actor takes two different ``actions``, such as raising a request and approving it.

## Referenced by

* [application.runtime.check_separation](/symbols/application/runtime/check_separation.md) - Refuse an actor who already took another action of a separation law on this record.
<!-- okf:generated:end links -->
