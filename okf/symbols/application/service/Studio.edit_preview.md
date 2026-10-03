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
  sha256: e3ce0cdeab35f9620565e3bc6a6ef72d394fb201188cebae7b986a87a955c85e
notes_baseline: 1fe3dca48b943c815639f1347f1c92ac42e75786ec5c7951d0c251d547c23d56
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
