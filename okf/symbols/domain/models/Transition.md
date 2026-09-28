---
type: Class
title: domain.models.Transition
description: 'One typed edge: action, from/to state, required role, guards, required effects and forbidden effects.'
resource: repo://src/eija_studio/domain/models.py#Transition
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Transition
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 9a1cad3bceaf4d96a0c5a0f57751fbfaf6158b92dcc95625a0dc7886af7e3b65
description_override: 'One typed edge: action, from/to state, required role, guards, required effects and forbidden effects.'
---

# domain.models.Transition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Transition(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Transition` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern='^[A-Z][A-Z0-9_-]{0,63}$')` |
| `action` | `str` | `Field(min_length=1, max_length=60)` |
| `from_state` | `str` | `Field(min_length=1, max_length=60)` |
| `to_state` | `str` | `Field(min_length=1, max_length=60)` |
| `role` | `str` | `Field(min_length=1, max_length=60)` |
| `guards` | `tuple[Guard, ...]` |  |
| `required_effects` | `tuple[str, ...]` |  |
| `forbidden_effects` | `tuple[str, ...]` |  |

## Methods

* [`guarded`](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition`
<!-- okf:generated:end facts -->

## Notes

The validator [guarded](/symbols/domain/models/Transition.guarded.md) refuses removal of any mandatory guard, duplicate guards or effects, and an effect that is both required and forbidden. Extra fields are rejected (`extra=forbid`), which is how unknown operators fail before preview.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models` (the source has no docstring).
* [domain.models.Guard](/symbols/domain/models/Guard.md) - `Guard = Literal['actor_active', 'role_current', 'actor_assigned', 'state_equals', 'expected_version', 'operation_binding']` in `domain/models` (the source has…

## Referenced by

* [Execution](/contexts/execution.md) - Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
* [domain.models.Transition.guarded](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models` (the source has no docstring).
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
