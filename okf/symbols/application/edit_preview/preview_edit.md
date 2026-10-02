---
type: Function
title: application.edit_preview.preview_edit
description: The candidate edit would produce from this snapshot, or its refusal without a guessed model.
resource: repo://src/eija_studio/application/edit_preview.py#preview_edit
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/edit_preview.py#preview_edit
  title: application/edit_preview.py
  hash_method: ast-v2
  sha256: d4126d3237ad7343e2a7f49ba7ea728c18994829f6c5e1d46b811bd80fcce2ae
notes_baseline: 1db2bd6cb32caf6ce14dbc93ff2f5e8a6e1c5f437280e0500f72ee5c5af930f2
---

# application.edit_preview.preview_edit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/edit_preview`](/modules/application/edit_preview.md) |
| Signature | `def preview_edit(case: ChangeCase, transaction: Transaction, pack: Pack) -> EditPreview` |
| Code | `repo://src/eija_studio/application/edit_preview.py#preview_edit` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The candidate edit would produce from this snapshot, or its refusal without a guessed model.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.edit_preview.EditPreview](/symbols/application/edit_preview/EditPreview.md) - An uncommitted candidate bound to a captured case revision; no evidence or edit authority.
* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.service.Studio.edit_preview](/symbols/application/service/Studio.edit_preview.md) - Read-only edit preview bound to one case snapshot; the owner edit still requires capability and CAS.
<!-- okf:generated:end links -->
