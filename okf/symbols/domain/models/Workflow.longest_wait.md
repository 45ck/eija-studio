---
type: Method
title: domain.models.Workflow.longest_wait
description: The longest time event on any transition, in seconds; 0 when the model has none (ADR-0237).
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
  sha256: 43d0a821d2fe39ead4e07718114d2bdc6f454f904e573666bf2de60c14916902
notes_baseline: 0a609f502ff44c115abd1a870d247490fe285dd383d54eae41dca928bd572fc6
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
The longest time event on any transition, in seconds; 0 when the model has none (ADR-0237). Waiting this
long in a state makes every time event leaving it due.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
