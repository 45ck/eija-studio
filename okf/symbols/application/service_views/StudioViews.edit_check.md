---
type: Method
title: application.service_views.StudioViews.edit_check
description: 'Dry-run one edit: {legal, codes, refs}.'
resource: repo://src/eija_studio/application/service_views.py#StudioViews.edit_check
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.edit_check
  title: application/service_views.py
  hash_method: ast-v2
  sha256: a8ee930cd1f32ffce5731154aa8b44d34bf5d5f2d12884a16dd39640509184e2
notes_baseline: e33e144ed361c6fc9094ddf1d086866154921544c0ecaafcf6eff7e70c413732
---

# application.service_views.StudioViews.edit_check

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def edit_check(self, case_id: str, tx: Transaction) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.edit_check` |
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
