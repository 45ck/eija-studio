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
  sha256: 5db058fa13ac7b1df205e5e22b175d0911ea1ed63c1d8e6e8fdd799395b28862
notes_baseline: 5bb480b1e6aedceef4a5c361a7a8590304f88fde8a2d2786b294c824ada575d0
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
