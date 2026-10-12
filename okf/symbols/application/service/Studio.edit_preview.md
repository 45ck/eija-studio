---
type: Method
title: application.service.Studio.edit_preview
description: Read-only edit preview bound to one case snapshot; the owner edit still requires capability and CAS.
resource: repo://src/eija_studio/application/service.py#Studio.edit_preview
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.edit_preview
  title: application/service.py
  hash_method: ast-v2
  sha256: 59f353692ee2ef096edd6a23f2ac4c9e76d4af82a0b7d72e9fa146a5a5f2d82e
notes_baseline: 9315a75dceded5f7f43e6060dc5882e9a92450312e02c36f5aad27951b985201
---

# application.service.Studio.edit_preview

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def edit_preview(self, case_id: str, tx: Transaction) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.edit_preview` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Read-only edit preview bound to one case snapshot; the owner edit still requires capability and CAS.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.edit_preview.preview_edit](/symbols/application/edit_preview/preview_edit.md) - The candidate edit would produce from this snapshot, or its refusal without a guessed model.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
