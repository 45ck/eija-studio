---
type: Class
title: domain.formal.Assessment
description: '`class Assessment` in `domain/formal`.'
resource: repo://src/eija_studio/domain/formal.py#Assessment
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#Assessment
  title: domain/formal.py
  hash_method: ast-sig-v1
  sha256: 381007327453fd61db540f493c0ec01f3629a48c1316237b3707e0eea9f808a9
notes_baseline: 87faa2484e7366b5ea7684cd0c131d76c0f6bb6fa6013de4d58a3f88926d49cf
---

# domain.formal.Assessment

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `class Assessment` |
| Code | `repo://src/eija_studio/domain/formal.py#Assessment` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `status` | `str` |  |
| `reasons` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.evidence.assess_formal_receipt](/symbols/domain/evidence/assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.formal.Findings](/symbols/domain/formal/Findings.md) - Collects reasons by severity.
* [domain.formal.Findings.result](/symbols/domain/formal/Findings.result.md) - `def result(self) -> Assessment` in `domain/formal`.
* [domain.formal.KindSpec](/symbols/domain/formal/KindSpec.md) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [domain.formal.not_run_reason](/symbols/domain/formal/not_run_reason.md) - A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS.
* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
