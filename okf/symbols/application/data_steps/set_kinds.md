---
type: Function
title: application.data_steps.set_kinds
description: '`pack` with each role-kind step applied in turn: a draft held in memory, checked as any pack is, so the kind laws are bound to the new kinds.'
resource: repo://src/eija_studio/application/data_steps.py#set_kinds
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#set_kinds
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: 2dace2a149233290d83200384d9dde3b7557f0481d695201416d6186b3a0f2f4
notes_baseline: 9f9c8373e543fb9b95315f49abd129bc22b88d6171c6e0f3418ac2c1b9ddcd2a
---

# application.data_steps.set_kinds

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def set_kinds(pack: Pack, steps: Sequence[SetRoleKind]) -> Pack` |
| Code | `repo://src/eija_studio/application/data_steps.py#set_kinds` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`pack` with each role-kind step applied in turn: a draft held in memory, checked as any pack is, so the kind laws
are bound to the new kinds. A role the pack does not declare is refused, and so is a draft in which a kind law can
no longer be met by any role. `pack` itself when there are none.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.SetRoleKind](/symbols/application/data_steps/SetRoleKind.md) - Make the actor holding `role` a person, an AI agent, a timer or an external system (ADR-0210).
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.derive](/symbols/domain/pack/derive.md) - A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios…

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
<!-- okf:generated:end links -->
