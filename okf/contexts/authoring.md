---
type: Bounded Context
title: Authoring
description: Owns Requested intent, alternatives, explicit selection, candidate and edits
resource: repo://docs/architecture/ARCHITECTURE.md#authoring
tags:
- ddd
- context-map
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#authoring
  title: ARCHITECTURE.md
  hash_method: md-table-row-v1
  sha256: 65cd3700342afd28dae6c3a10196502c5fb9753fe5184372ae3dc7c0c1905457
---

# Authoring

<!-- okf:generated:begin facts -->
## Owns

Requested intent, alternatives, explicit selection, candidate and edits

## Published contracts

* [`ChangeCase`](/symbols/domain/change_case/ChangeCase.md)
* [`Proposal`](/symbols/domain/models/Proposal.md)
* [`SemanticTransaction`](/symbols/domain/models/SemanticTransaction.md)
* [`LayoutChange`](/symbols/domain/models/LayoutChange.md)

## Implementation

* [`domain/change_case.py`](/modules/domain/change_case.md)
* [`application/service.py`](/modules/application/service.md)

Source: context map row `repo://docs/architecture/ARCHITECTURE.md#authoring`. These are responsibility boundaries inside a modular monolith, not separately deployed services.
<!-- okf:generated:end facts -->

## Notes

Aggregate: [Change Case](/language/change-case.md). Interpretations arrive only through the [ProposalProvider](/symbols/application/ports/ProposalProvider.md) port and stay untrusted until the owner selects one.

<!-- okf:generated:begin links -->
## Published contracts

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.LayoutChange](/symbols/domain/models/LayoutChange.md) - `class LayoutChange(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models` (the source has no docstring).

## Implementing modules

* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
<!-- okf:generated:end links -->
