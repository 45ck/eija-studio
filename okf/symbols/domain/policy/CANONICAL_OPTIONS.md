---
type: Constant
title: domain.policy.CANONICAL_OPTIONS
description: The four canonical interpretations a provider may propose; only recommend_only is supported.
resource: repo://src/eija_studio/domain/policy.py#CANONICAL_OPTIONS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#CANONICAL_OPTIONS
  title: domain/policy.py
  hash_method: ast-v2
  sha256: ef257190456b001db445a0ee9faa1bc9ea2c41d84284c4bd3930c7950afd8420
description_override: The four canonical interpretations a provider may propose; only recommend_only is supported.
notes_baseline: e1f3a3dd15801ebdd34ea013cf87f3fede4c8f973b0913e2d00f1e0a1d287d24
---

# domain.policy.CANONICAL_OPTIONS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `CANONICAL_OPTIONS = {'recommend_only': {'label': 'Teacher recommends; registrar decides', 'supported': True, 'consequences': ['Only active, assigned teachers r…` |
| Code | `repo://src/eija_studio/domain/policy.py#CANONICAL_OPTIONS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Labels and consequences are server-owned (ADR-004 in the [POC decision log](/adrs/poc/adr-004.md)); a provider's explanation is never this table. `final_approval` is blocked because it would expand protected authority.

<!-- okf:generated:begin links -->
## Referenced by

* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict` in `application/service`.
* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict` in `application/service`.
<!-- okf:generated:end links -->
