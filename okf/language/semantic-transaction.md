---
type: Ubiquitous Language Term
title: Semantic Transaction
description: One typed business-meaning edit.
resource: repo://docs/architecture/ARCHITECTURE.md#semantic-transaction
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#semantic-transaction
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: a502ff98ad37179777b9eff37955595f381753b1c03328cf8777261d678fcea9
---

# Semantic Transaction

<!-- okf:generated:begin facts -->
## Definition

> one typed business-meaning edit. Rule-table and state-view commands produce the same shape. The supported operations are enabling recommendation and changing the registrar rejection source between the declared states.

Source: `repo://docs/architecture/ARCHITECTURE.md#semantic-transaction`.
<!-- okf:generated:end facts -->

## Notes

Contract: [SemanticTransaction](/symbols/domain/models/SemanticTransaction.md). Applied only by [apply_transaction](/symbols/domain/policy/apply_transaction.md), which re-checks the protected policy on the result.

<!-- okf:generated:begin links -->
## Realised in code

* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
