---
type: Method
title: application.service.Studio.edit_check
description: 'Dry-run one edit: {legal, codes, refs}.'
resource: repo://src/eija_studio/application/service.py#Studio.edit_check
tags:
- symbol
- application
- method
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.edit_check
  title: application/service.py
  hash_method: ast-v2
  sha256: f2fac6889be0e5f04f0eec39a3323bcd95733cf15e61fee2f40d877df2cb94aa
notes_baseline: b218fb077cfaf4b485539e33ce7b1513074a92409b246e22c7e7e077e93b909a
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
