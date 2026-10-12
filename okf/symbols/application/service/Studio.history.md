---
type: Method
title: application.service.Studio.history
description: Reconstructed semantic revisions and append-only command audit; never changes the case.
resource: repo://src/eija_studio/application/service.py#Studio.history
tags:
- symbol
- application
- method
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.history
  title: application/service.py
  hash_method: ast-v2
  sha256: a6f005ed5451a967313a03f792c7c8ec4ebffaadecc45f860a69cb6af424882c
notes_baseline: 84ae1445b697fde46e18071776f575c9576b7eade39d4c74b4aa4457cd2f61c3
---

# application.service.Studio.history

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def history(self, case_id: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.history` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Reconstructed semantic revisions and append-only command audit; never changes the case.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.history.history_view](/symbols/application/history/history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
<!-- okf:generated:end links -->
