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
notes_baseline: bf2881914abc099767d0162c6a00e5e9c7c3892c2b91e8a657a566b7ba04280c
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

* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
