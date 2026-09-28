---
type: Ubiquitous Language Term
title: Effect Intent
description: A transactionally queued synthetic notification or audit append.
resource: repo://docs/architecture/ARCHITECTURE.md#effect-intent
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#effect-intent
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: 1c04519ec91acb9b6d24bfb69761071bdc699bc201a890ad0a8733715dd6cbcc
---

# Effect Intent

<!-- okf:generated:begin facts -->
## Definition

> a transactionally queued synthetic notification or audit append. An enqueue is not external delivery. No payment/export/notification delivery adapter is implemented.

Source: `repo://docs/architecture/ARCHITECTURE.md#effect-intent`.
<!-- okf:generated:end facts -->

## Notes

Declared in [EFFECTS](/symbols/domain/policy/EFFECTS.md), enqueued by [execute](/symbols/application/runtime/execute.md) through the [UnitOfWork](/symbols/application/ports/UnitOfWork.md). No delivery adapter exists in v0.2.

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
