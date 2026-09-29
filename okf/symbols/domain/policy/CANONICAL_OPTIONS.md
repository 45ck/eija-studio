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
  sha256: d59b69032ab57f4e780e37f7f4a2b69969e74901123ed198008d8f4ccb89b660
description_override: The four canonical interpretations a provider may propose; only recommend_only is supported.
notes_baseline: e1f3a3dd15801ebdd34ea013cf87f3fede4c8f973b0913e2d00f1e0a1d287d24
---

# domain.policy.CANONICAL_OPTIONS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `CANONICAL_OPTIONS: dict[str, dict[str, Any]] = {'recommend_only': {'label': 'Teacher recommends; registrar decides', 'supported': True, 'consequences': ['Only…` |
| Code | `repo://src/eija_studio/domain/policy.py#CANONICAL_OPTIONS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Labels and consequences are server-owned (ADR-004 in the [POC decision log](/adrs/poc/adr-004.md)); a provider's explanation is never this table. `final_approval` is blocked because it would expand protected authority.

<!-- okf:generated:begin links -->
## Referenced by

* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
