---
type: Class
title: domain.models.Principal
description: A named holder of capabilities (select, edit, approve, apply); OWNER has all four, AGENT has none.
resource: repo://src/eija_studio/domain/models.py#Principal
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Principal
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 01ac48f871213011c5cf34adc48fa83b2c455c5618ad5d4ddcf20c7a2bcd0d7d
description_override: A named holder of capabilities (select, edit, approve, apply); OWNER has all four, AGENT has none.
notes_baseline: 571ade4d077e9f587d443ac187dfe78d8c5e5ea1b201aa1657a8afb181b71ed4
---

# domain.models.Principal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Principal(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Principal` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` |  |
| `capabilities` | `frozenset[str]` |  |

## Methods

* [`require`](/symbols/domain/models/Principal.require.md) - `def require(self, capability: str) -> None`
<!-- okf:generated:end facts -->

## Notes

Capabilities are checked with [require](/symbols/domain/models/Principal.require.md) at the start of each governance use case. This is a single-user local capability, not institutional identity ([Authority](/language/authority.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [Governance](/contexts/governance.md) - Owns Local capabilities, exact-revision acknowledgement, active baseline version
* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.service.Studio.redo](/symbols/application/service/Studio.redo.md) - Reapply the next undone typed command through the same interpreter and policy checks.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.undo](/symbols/application/service/Studio.undo.md) - Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix.
* [domain.models.AGENT](/symbols/domain/models/AGENT.md) - Constant `AGENT` in `domain/models`.
* [domain.models.OWNER](/symbols/domain/models/OWNER.md) - Constant `OWNER` in `domain/models`.
* [domain.models.Principal.require](/symbols/domain/models/Principal.require.md) - `def require(self, capability: str) -> None` in `domain/models`.
<!-- okf:generated:end links -->
