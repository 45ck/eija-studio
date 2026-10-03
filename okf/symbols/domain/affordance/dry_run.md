---
type: Function
title: domain.affordance.dry_run
description: '{legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.'
resource: repo://src/eija_studio/domain/affordance.py#dry_run
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/affordance.py#dry_run
  title: domain/affordance.py
  hash_method: ast-v2
  sha256: f0dbfc19e3b4a52db3d0bbc91a99d1b9bcf55f04e3c27d745cbc528ddfcfbb16
notes_baseline: 672fa31db50a91c48d9194abff3d58a61c517fedac582d4a029b04959c43b7f8
---

# domain.affordance.dry_run

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/affordance`](/modules/domain/affordance.md) |
| Signature | `def dry_run(model: Workflow, tx: Transaction, pack: Pack) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/domain/affordance.py#dry_run` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
{legal, codes, refs} of applying ``tx`` to ``model`` under ``pack``, without applying it anywhere.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.service.Studio.edit_check](/symbols/application/service/Studio.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
<!-- okf:generated:end links -->
