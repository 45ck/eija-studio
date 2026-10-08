---
type: Ubiquitous Language Term
title: Change Case
description: Aggregate linking one original request to interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision.
resource: repo://docs/architecture/ARCHITECTURE.md#change-case
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#change-case
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: c2d205da3af4cbf0ae55bbddb62ae557250601db9964a44e0dff1d42083bd460
notes_baseline: c6a8b952e5bc701c86ec670b8ad94dc9e6ce3d3bf1be6eb86a945fbd4f6be482
---

# Change Case

<!-- okf:generated:begin facts -->
## Definition

> aggregate linking one original request to interpretations, chosen meaning, baseline, candidate, transactions, receipts and decision. Its revision is not the same as a workflow instance's version.

Source: `repo://docs/architecture/ARCHITECTURE.md#change-case`.
<!-- okf:generated:end facts -->

## Notes

Implemented by [ChangeCase](/symbols/domain/change_case/ChangeCase.md) and driven by the use cases in [Studio](/symbols/application/service/Studio.md). Bounded context: [Authoring](/contexts/authoring.md).

<!-- okf:generated:begin links -->
## Realised in code

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
<!-- okf:generated:end links -->
