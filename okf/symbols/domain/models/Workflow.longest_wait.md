---
type: Method
title: domain.models.Workflow.longest_wait
description: The longest time event on any transition, in seconds; 0 when the model has none (ADR-0236).
resource: repo://src/eija_studio/domain/models.py#Workflow.longest_wait
tags:
- symbol
- domain
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Workflow.longest_wait
  title: domain/models.py
  hash_method: ast-v2
  sha256: a0d1be8d345e0d0522fea12442006f213a2da6d86b6d161539c1415cb2fb8905
notes_baseline: 314e241020030b652df6bbabb96a421687a107cf95d9ef69a1915c12ce884c1c
---

# domain.models.Workflow.longest_wait

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`domain/models`](/modules/domain/models.md) |
| Class | [`Workflow`](/symbols/domain/models/Workflow.md) |
| Signature | `def longest_wait(self) -> int` |
| Code | `repo://src/eija_studio/domain/models.py#Workflow.longest_wait` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The longest time event on any transition, in seconds; 0 when the model has none (ADR-0236). Waiting this
long in a state makes every time event leaving it due.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
