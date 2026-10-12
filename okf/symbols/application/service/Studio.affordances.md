---
type: Method
title: application.service.Studio.affordances
description: Which single edits of the case's working model the kernel would accept (read-only).
resource: repo://src/eija_studio/application/service.py#Studio.affordances
tags:
- symbol
- application
- method
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.affordances
  title: application/service.py
  hash_method: ast-v2
  sha256: 07ac9408e2cc560075ff10a061d2d22234aeb64311d14ad83f8cb733bb8c3091
notes_baseline: 0c33bd5f93f69cc73247b076d721fb9a516448e01cf848fc29fa45d9e97b8e15
---

# application.service.Studio.affordances

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def affordances(self, case_id: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.affordances` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Which single edits of the case's working model the kernel would accept (read-only).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.affordance.affordances](/symbols/domain/affordance/affordances.md) - Every single-step retarget and role change of ``model``, each with its dry-run verdict.
<!-- okf:generated:end links -->
