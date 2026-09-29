---
type: Constant
title: domain.policy.CANONICAL_OPTIONS
description: The four canonical interpretations a provider may propose; only recommend_only is supported.
resource: repo://src/eija_studio/domain/policy.py#CANONICAL_OPTIONS
tags:
- symbol
- domain
- constant
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#CANONICAL_OPTIONS
  title: domain/policy.py
  hash_method: ast-v2
  sha256: d59b69032ab57f4e780e37f7f4a2b69969e74901123ed198008d8f4ccb89b660
description_override: The four canonical interpretations a provider may propose; only recommend_only is supported.
notes_baseline: bba1e12981ef068bdeb8e770298e1c5ee7312b83b1c0d6e3298a198ab3aba7a7
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 3c0ab625dc99074e639d148f6f2f81ad3a24dc252c702288bd377cc0e1039eca
  sources_sha256: bba1e12981ef068bdeb8e770298e1c5ee7312b83b1c0d6e3298a198ab3aba7a7
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
