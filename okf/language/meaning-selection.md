---
type: Ubiquitous Language Term
title: Meaning Selection
description: A local owner's explicit choice of one canonical supported interpretation.
resource: repo://docs/architecture/ARCHITECTURE.md#meaning-selection
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#meaning-selection
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: 649a4875725910e78cf29f6a1532296f4942aa4e6d9f449797fa9ebe25bad178
notes_baseline: 31a8b99059340421ea25aed9d0920bf3c003a14d762bdebec873c1a90938b0f1
---

# Meaning Selection

<!-- okf:generated:begin facts -->
## Definition

> a local owner's explicit choice of one canonical supported interpretation. A provider explanation is not this event. Unsupported teacher-final-approval remains blocked rather than being rewritten as recommendation.

Source: `repo://docs/architecture/ARCHITECTURE.md#meaning-selection`.
<!-- okf:generated:end facts -->

## Notes

Performed by [Studio.select](/symbols/application/service/Studio.select.md) with the `select` capability. The supported meanings are in [CANONICAL_OPTIONS](/symbols/domain/policy/CANONICAL_OPTIONS.md); `final_approval` stays blocked.

<!-- okf:generated:begin links -->
## Realised in code

* [domain.pack.Meaning](/symbols/domain/pack/Meaning.md) - One interpretation of a request.
<!-- okf:generated:end links -->
