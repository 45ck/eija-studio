---
type: Bounded Context
title: Assurance
description: Owns Subject dimensions, verification observations, admissibility and freshness
resource: repo://docs/architecture/ARCHITECTURE.md#assurance
tags:
- ddd
- context-map
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#assurance
  title: ARCHITECTURE.md
  hash_method: md-table-row-v1
  sha256: 329604fa944636e5b4e20f2d9dbe48a1e85673d511daaf85ed9787babb73967f
---

# Assurance

<!-- okf:generated:begin facts -->
## Owns

Subject dimensions, verification observations, admissibility and freshness

## Published contracts

* EvidenceReceipt JSON (no public symbol of this name)
* compilation/review packet (no public symbol of this name)

## Implementation

* [`domain/evidence.py`](/modules/domain/evidence.md)
* [`application/verifier.py`](/modules/application/verifier.md)
* [`application/compiler.py`](/modules/application/compiler.md)

Source: context map row `repo://docs/architecture/ARCHITECTURE.md#assurance`. These are responsibility boundaries inside a modular monolith, not separately deployed services.
<!-- okf:generated:end facts -->

## Notes

Evidence is recomputed, not trusted: [assess_receipt](/symbols/domain/evidence/assess_receipt.md). Verification techniques and their limits are in [verification](/verification/).

<!-- okf:generated:begin links -->
## Implementing modules

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
<!-- okf:generated:end links -->
