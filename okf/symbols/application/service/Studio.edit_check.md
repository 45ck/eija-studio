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
  sha256: b27055f8c0e214ce47a25eb60007cf9ec76e8b84a82b0f5f360d193299f40818
notes_baseline: 23340271c076f3ee28884d6250d4af1d9b2994a88a3be38ffcf0a5ac1225b053
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
