---
type: Constant
title: domain.pack.PACKS_ROOT
description: Constant `PACKS_ROOT` in `domain/pack`.
resource: repo://src/eija_studio/domain/pack.py#PACKS_ROOT
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#PACKS_ROOT
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 86f795091c233f809446a65737627192e14e3ee32769f0d64372f3c458a55fb6
notes_baseline: 10d32b38083ffd9479197b6cf61079130909e59596f26e9792929f7029be59ed
---

# domain.pack.PACKS_ROOT

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `PACKS_ROOT = Path(__file__).resolve().parents[3] / 'packs'` |
| Code | `repo://src/eija_studio/domain/pack.py#PACKS_ROOT` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.pack.default_location](/symbols/domain/pack/default_location.md) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
* [domain.pack.find_pack](/symbols/domain/pack/find_pack.md) - The pack a workflow belongs to (``Workflow.id``): a pack loaded in this process, else the repository pack of that id.
<!-- okf:generated:end links -->
