---
type: Method
title: application.service.Studio.edit_check
description: 'Dry-run one edit: {legal, codes, refs}.'
resource: repo://src/eija_studio/application/service.py#Studio.edit_check
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.edit_check
  title: application/service.py
  hash_method: ast-v2
  sha256: 7c698592c2a9a833fe93693980b8af48fda4ce51ebd0a039160d67920e9f0ef4
notes_baseline: fb8d6aa4599d67becad7b12e720de19baf6de3e1a9c23bce04499d93eeb1cc7f
---

# application.service.Studio.edit_check

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def edit_check(self, case_id: str, tx: Transaction) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.edit_check` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Dry-run one edit: {legal, codes, refs}. No authority is needed because nothing is written.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.affordance.dry_run](/symbols/domain/affordance/dry_run.md) - {legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
