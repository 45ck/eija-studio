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
  sha256: ab7da0be123202284f9cab880670605da39a7b42faff6c43f10ea1c6af1a78b1
notes_baseline: 66ff13c8d33a90d6139b253b47d980cfdc82bdb8fc967e4f35577fcfc75fba62
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
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence.assess_formal_receipt](/symbols/domain/evidence/assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [domain.formal.KindSpec](/symbols/domain/formal/KindSpec.md) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
