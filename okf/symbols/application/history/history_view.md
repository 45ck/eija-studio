---
type: Function
title: application.history.history_view
description: Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
resource: repo://src/eija_studio/application/history.py#history_view
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/history.py#history_view
  title: application/history.py
  hash_method: ast-v2
  sha256: 7b301812f163ea8286e90ddae480d7967fb91059efd27957eabe86e378a7bd8d
notes_baseline: f490b6bc1a5aa4dc511122877f93a2e37c449c179f9711f1915693f5479d2053
---

# application.history.history_view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/history`](/modules/application/history.md) |
| Signature | `def history_view(case: ChangeCase, pack: Pack, events: list[dict[str, Any]]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/history.py#history_view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.service_views.StudioViews.history](/symbols/application/service_views/StudioViews.history.md) - Reconstructed semantic revisions and append-only command audit; never changes the case.
<!-- okf:generated:end links -->
