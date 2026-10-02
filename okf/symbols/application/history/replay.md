---
type: Function
title: application.history.replay
description: Fail closed when stored commands no longer explain the candidate under the exact active pack.
resource: repo://src/eija_studio/application/history.py#replay
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/history.py#replay
  title: application/history.py
  hash_method: ast-v2
  sha256: cf899d8a13fcc36bcfbeadf050a50c224869a51d8ff12d437073fc803d175b5d
notes_baseline: dde79c73da06fcaac3c839428ecb7e1aa7bbce9e7bba25e5435ab9fc983d329c
---

# application.history.replay

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/history`](/modules/application/history.md) |
| Signature | `def replay(case: ChangeCase, pack: Pack) -> SemanticHistory` |
| Code | `repo://src/eija_studio/application/history.py#replay` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Fail closed when stored commands no longer explain the candidate under the exact active pack.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.history.SemanticHistory](/symbols/application/history/SemanticHistory.md) - Validated replay; models includes the selected meaning followed by each applied owner edit.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).

## Referenced by

* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
* [application.history.history_view](/symbols/application/history/history_view.md) - Read-only models for navigation plus actual command audit entries; no invented legacy timestamps.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.redo](/symbols/application/service/Studio.redo.md) - Reapply the next undone typed command through the same interpreter and policy checks.
* [application.service.Studio.undo](/symbols/application/service/Studio.undo.md) - Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix.
<!-- okf:generated:end links -->
