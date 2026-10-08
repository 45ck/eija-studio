---
type: Function
title: domain.evidence.assess_formal_receipt
description: 'Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix''s order, then the kind''s own check.'
resource: repo://src/eija_studio/domain/evidence.py#assess_formal_receipt
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#assess_formal_receipt
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: 74f4dea5e20a5b5d41da62c6e5bb7657a0ef9accc3ba83b2b679347237ef8977
notes_baseline: eded8537b259dd9f6e6e1575e1146663bacf1fabcde2f3e464d254de3fe6e5e0
---

# domain.evidence.assess_formal_receipt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def assess_formal_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context \| None=None) -> Assessment` |
| Code | `repo://src/eija_studio/domain/evidence.py#assess_formal_receipt` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.

A supplied ``status`` label is never read. Structural defects are FAIL, an unknown protocol version is UNKNOWN.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
* [domain.formal.Assessment](/symbols/domain/formal/Assessment.md) - `class Assessment` in `domain/formal`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.

## Referenced by

* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
<!-- okf:generated:end links -->
