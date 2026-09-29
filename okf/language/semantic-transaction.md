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
  sha256: 4335eff28a388211564bf597615908d3ae6736bac39e4dc85d772af3c1c782c9
notes_baseline: 25de03cf45844342ef27ed00a9d3895d8b548c84f083fdbfce22272d2919a4bf
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: a738fc63c2237230195a71b373626c863a8d8a8b6c53a5866454819666d57de8
  sources_sha256: 25de03cf45844342ef27ed00a9d3895d8b548c84f083fdbfce22272d2919a4bf
---

# Semantic Transaction

<!-- okf:generated:begin facts -->
## Definition

> one typed business-meaning edit. Rule-table, state-view and canvas commands produce the same shape. The open vocabulary (`domain/transactions.py`) adds, renames or removes a state, sets the initial state, adds, retargets or removes a transition, and sets a transition's role, guards or required effects; a pack meaning is a list of them. Whether an edit is allowed is decided by the domain pack's policy and laws, never by the transaction.

Source: `repo://docs/architecture/ARCHITECTURE.md#semantic-transaction`.
<!-- okf:generated:end facts -->

## Notes

Contract: the discriminated union in `domain/transactions.py` (`contracts/semantic-transaction.schema.json`); the class [SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) is the deprecated closed vocabulary. Applied only through `policy.apply_transactions` ([apply_transaction](/symbols/domain/policy/apply_transaction.md)), which checks the pack's policy on the input and the result.

<!-- okf:generated:begin links -->
## Realised in code

* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - DEPRECATED closed vocabulary, superseded by the open one in ``domain.transactions`` (WBS 1.3).
<!-- okf:generated:end links -->
