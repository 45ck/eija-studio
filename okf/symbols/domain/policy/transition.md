---
type: Function
title: domain.policy.transition
description: Builds a Transition whose guards and effects come from the protected tables, never from caller input.
resource: repo://src/eija_studio/domain/policy.py#transition
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#transition
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 5cfd823f12167550486daf9b77e0f38a281690f2a3508340ff2b0006c4a4d8a8
description_override: Builds a Transition whose guards and effects come from the protected tables, never from caller input.
notes_baseline: 729b494d9a90757214d89e5ab2d79f6cfd31409c0a04ac52aacda3d1f5e2424c
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: e4dcb5910fdfcdf2e8d6b9ab45a46c39ed0d163d496f03c58bb10fb394f31b2e
  sources_sha256: 729b494d9a90757214d89e5ab2d79f6cfd31409c0a04ac52aacda3d1f5e2424c
---

# domain.policy.transition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def transition(action: str, source: str, target: str, role: str, pack: Pack \| None=None, *, transition_id: str \| None=None) -> Transition` |
| Code | `repo://src/eija_studio/domain/policy.py#transition` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A transition for a declared action, with the action's declared guards and effects and the pack's forbidden effects.
~~~
<!-- okf:generated:end facts -->

## Notes

A transition for an action the pack declares: id `TR-<ACTION>` unless given, guards and required effects from the action's declaration, forbidden effects from the pack. An undeclared action is `UNSUPPORTED_ACTION`.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
