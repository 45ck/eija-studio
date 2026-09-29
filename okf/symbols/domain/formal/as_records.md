---
type: Function
title: domain.formal.as_records
description: 'Defensive view for display-only helpers: a list of dicts, or nothing.'
resource: repo://src/eija_studio/domain/formal.py#as_records
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#as_records
  title: domain/formal.py
  hash_method: ast-v2
  sha256: d0521210bc8b8c3763a9f4124bed27164ca93170ca0213f29756f9169a0c4bd3
notes_baseline: 875c39f31d10178954ca6430cd28a6edcf3b6a8b92bd2268c7e5b4a2aa445d46
---

# domain.formal.as_records

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def as_records(value: Any) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/formal.py#as_records` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Defensive view for display-only helpers: a list of dicts, or nothing.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.formal_bend.explain](/symbols/domain/formal_bend/explain.md) - Negative-control counterexamples whose fault class is one the kernel's own policy reports.
* [domain.formal_smt.explain](/symbols/domain/formal_smt/explain.md) - Leave-one-out counterexamples for the policy clauses behind the policy errors the kernel reports.
<!-- okf:generated:end links -->
