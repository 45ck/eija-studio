---
type: Ubiquitous Language Term
title: Workflow Definition
description: Immutable typed states/transitions/roles/guards/effect declarations.
resource: repo://docs/architecture/ARCHITECTURE.md#workflow-definition
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#workflow-definition
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: a3b2d6334691c583daa1e8c9ed4af6c1f48cebcb338f5d04a09e405489daef93
---

# Workflow Definition

<!-- okf:generated:begin facts -->
## Definition

> immutable typed states/transitions/roles/guards/effect declarations. A normalized semantic hash treats definition order as non-semantic. Identifiers, states, roles and rules remain meaningful.

Source: `repo://docs/architecture/ARCHITECTURE.md#workflow-definition`.
<!-- okf:generated:end facts -->

## Notes

Contract: [Workflow](/symbols/domain/models/Workflow.md) with edges [Transition](/symbols/domain/models/Transition.md). Bounded context: [Execution](/contexts/execution.md). Identity: [semantic_hash](/symbols/domain/models/Workflow.semantic_hash.md).

<!-- okf:generated:begin links -->
## Realised in code

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
