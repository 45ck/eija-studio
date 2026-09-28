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
---

# domain.models.Principal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Principal(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Principal` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

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

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models` (the source has no docstring).

## Referenced by

* [Governance](/contexts/governance.md) - Owns Local capabilities, exact-revision acknowledgement, active baseline version
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknowns: bool, principal: Principal, scope: s…` in `ap…
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service` (the source has no docstring).
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict` in `application/service` (the source has no docstring).
* [domain.models.AGENT](/symbols/domain/models/AGENT.md) - `AGENT = Principal(id='agent', capabilities=frozenset())` in `domain/models` (the source has no docstring).
* [domain.models.OWNER](/symbols/domain/models/OWNER.md) - `OWNER = Principal(id='local-owner', capabilities=frozenset({'select', 'edit', 'approve', 'apply'}))` in `domain/models` (the source has no docstring).
* [domain.models.Principal.require](/symbols/domain/models/Principal.require.md) - `def require(self, capability: str) -> None` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
