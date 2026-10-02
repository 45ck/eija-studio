---
type: Method
title: application.service.Studio.affordances
description: Which single edits of the case's working model the kernel would accept (read-only).
resource: repo://src/eija_studio/application/service.py#Studio.affordances
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.affordances
  title: application/service.py
  hash_method: ast-v2
  sha256: 8159480cd832349200097c5db6fa18f8fffc1371b0d1fca1ac202f51f1239310
notes_baseline: e4926178dad2090b1ccc27918dc532abdf58f2868e3ecfc99fe402b8f2be8a26
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
