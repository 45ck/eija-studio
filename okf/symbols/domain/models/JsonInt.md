---
type: Type Alias
title: domain.models.JsonInt
description: Type alias `JsonInt` in `domain/models`.
resource: repo://src/eija_studio/domain/models.py#JsonInt
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#JsonInt
  title: domain/models.py
  hash_method: ast-v2
  sha256: 609609ea27642054a9a3774fab21d58410f78d51fed914b1746f6cab06a08bf5
notes_baseline: 31ef4e8b61b58f3cb934ed30a5190f19ea9f4af2033368299c58146b06b07652
---

# domain.models.JsonInt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `JsonInt = Annotated[int, BeforeValidator(_json_integer)]` |
| Code | `repo://src/eija_studio/domain/models.py#JsonInt` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.change_case.OwnerPlanRequest](/symbols/domain/change_case/OwnerPlanRequest.md) - Exact accepted workflow commands and the identities of their reviewed preview.
* [domain.change_case.OwnerPlanStep](/symbols/domain/change_case/OwnerPlanStep.md) - Reported proposal provenance, never a capability or an owner decision.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
