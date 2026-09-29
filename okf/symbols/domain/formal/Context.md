---
type: Class
title: domain.formal.Context
description: What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
resource: repo://src/eija_studio/domain/formal.py#Context
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#Context
  title: domain/formal.py
  hash_method: ast-sig-v1
  sha256: c15104a6585b8d1f4c71c4ce9f0fcf758c3aaa0a05929d2c3402a5f3150f33d4
notes_baseline: d773c269937c0f0c6e61a8672e05e9484f9950164f4e75d5b7053e097e643458
---

# domain.formal.Context

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `class Context` |
| Code | `repo://src/eija_studio/domain/formal.py#Context` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.

``candidate_semantic`` is ``Workflow.semantic_hash`` of the candidate under review and
``baseline_semantic`` that of the baseline; both are recomputed from the Workflow objects by the caller.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `candidate_semantic` | `str` |  |
| `baseline_semantic` | `str \| None` | `None` |
| `runtime` | `RuntimeShape \| None` | `None` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.RuntimeShape](/symbols/domain/formal/RuntimeShape.md) - What a runtime-matrix receipt for the current subject must cover: the pack's fixture actors and declared actions, and one of the allowed state sets (exactly th…

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.assess_formal_receipt](/symbols/domain/evidence/assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [domain.evidence.runtime_shape](/symbols/domain/evidence/runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
* [domain.formal.KindSpec](/symbols/domain/formal/KindSpec.md) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
