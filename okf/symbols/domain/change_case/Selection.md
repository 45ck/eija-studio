---
type: Type Alias
title: domain.change_case.Selection
description: Type alias `Selection` in `domain/change_case`.
resource: repo://src/eija_studio/domain/change_case.py#Selection
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py#Selection
  title: domain/change_case.py
  hash_method: ast-v2
  sha256: fa1c12bf76c8a57f68742b40fff246f39ae0a3ca0fe127df43159e9694568e6e
notes_baseline: 8d0e024dbf97cf36a315413ec4b8546c8ee1567480d56a69bc045e3f721e17c2
---

# domain.change_case.Selection

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/change_case`](/modules/domain/change_case.md) |
| Signature | `Selection = Annotated[PackMeaningSelection \| OwnerPlanSelection, Field(discriminator='kind')]` |
| Code | `repo://src/eija_studio/domain/change_case.py#Selection` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.OwnerPlanSelection](/symbols/domain/change_case/OwnerPlanSelection.md) - `class OwnerPlanSelection(Contract)` in `domain/change_case`.
* [domain.change_case.PackMeaningSelection](/symbols/domain/change_case/PackMeaningSelection.md) - `class PackMeaningSelection(Contract)` in `domain/change_case`.

## Referenced by

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
<!-- okf:generated:end links -->
