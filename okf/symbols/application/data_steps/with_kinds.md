---
type: Function
title: application.data_steps.with_kinds
description: '`pack` with the roles'' kinds these steps set, a draft held in memory; `PLAN_KIND_FIXED` on a system with a law about kinds, and `EDIT_INVALID` for a role the pack does not declare.'
resource: repo://src/eija_studio/application/data_steps.py#with_kinds
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#with_kinds
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: ba72a24735595cefb473fa98963676a6a57f03b1acc8740c0a882f52386b3d44
notes_baseline: 80b8fc8080a7d2280cc024954ebd0d149fef12c5474523a387558993f367d555
---

# application.data_steps.with_kinds

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def with_kinds(pack: Pack, steps: Sequence[DataEdit]) -> Pack` |
| Code | `repo://src/eija_studio/application/data_steps.py#with_kinds` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`pack` with the roles' kinds these steps set, a draft held in memory; `PLAN_KIND_FIXED` on a system with a law
about kinds, and `EDIT_INVALID` for a role the pack does not declare.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.DataEdit](/symbols/application/data_steps/DataEdit.md) - Type alias `DataEdit` in `application/data_steps`.
* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - `class SetRoleKind(Contract)` in `application/data_steps`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.derive](/symbols/domain/pack/derive.md) - A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios…

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
<!-- okf:generated:end links -->
