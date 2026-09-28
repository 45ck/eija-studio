---
type: Ubiquitous Language Term
title: Evidence Receipt
description: A dated local verifier observation set attached to technical subject dimensions.
resource: repo://docs/architecture/ARCHITECTURE.md#evidence-receipt
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#evidence-receipt
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: 423a4605891c528d1565cd57fc9ce9d83d16edd32d6f3da8152eb9e81907be5f
notes_baseline: 394c9726c3aebfd9629caf0213ae156bc7e39ef78842f78994f9cb9decc92a94
---

# Evidence Receipt

<!-- okf:generated:begin facts -->
## Definition

> a dated local verifier observation set attached to technical subject dimensions. Its raw artifact is retained. Applicability is recomputed; a receipt's own green label is not trusted. A local HMAC is an integrity seal, not external certification.

Source: `repo://docs/architecture/ARCHITECTURE.md#evidence-receipt`.
<!-- okf:generated:end facts -->

## Notes

Assessed by [assess_receipt](/symbols/domain/evidence/assess_receipt.md) and combined by [aggregate_status](/symbols/domain/evidence/aggregate_status.md); produced by [verify_runtime](/symbols/application/verifier/verify_runtime.md). Technique: [Bounded runtime matrix](/verification/integration-test.md). Bounded context: [Assurance](/contexts/assurance.md).

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
