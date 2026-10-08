---
type: Constant
title: domain.formal_smt.SPEC
description: Constant `SPEC` in `domain/formal_smt`.
resource: repo://src/eija_studio/domain/formal_smt.py#SPEC
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_smt.py#SPEC
  title: domain/formal_smt.py
  hash_method: ast-v2
  sha256: 191dfb5203c9a163907f3c34f2bf77c371c0e907fbb687f252e52a5026c8996e
notes_baseline: 607528fa60cb1fa2f2d7f29dce78d8bd855c31be585a23cef012c97880d30327
---

# domain.formal_smt.SPEC

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/formal_smt`](/modules/domain/formal_smt.md) |
| Signature | `SPEC = KindSpec(kind='smt_proof', claim='policy_soundness', method='formal-smt-proof-v1', protocol=PROTOCOL, level=LEVEL_SEALED_TOOL, establishes=ESTABLISHES,…` |
| Code | `repo://src/eija_studio/domain/formal_smt.py#SPEC` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.KindSpec](/symbols/domain/formal/KindSpec.md) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [domain.formal.LEVEL_SEALED_TOOL](/symbols/domain/formal/LEVEL_SEALED_TOOL.md) - Constant `LEVEL_SEALED_TOOL` in `domain/formal`.
* [domain.formal_smt.DOES_NOT_ESTABLISH](/symbols/domain/formal_smt/DOES_NOT_ESTABLISH.md) - Constant `DOES_NOT_ESTABLISH` in `domain/formal_smt`.
* [domain.formal_smt.ESTABLISHES](/symbols/domain/formal_smt/ESTABLISHES.md) - Constant `ESTABLISHES` in `domain/formal_smt`.
* [domain.formal_smt.PREREQUISITES](/symbols/domain/formal_smt/PREREQUISITES.md) - Constant `PREREQUISITES` in `domain/formal_smt`.
* [domain.formal_smt.PROTOCOL](/symbols/domain/formal_smt/PROTOCOL.md) - Constant `PROTOCOL` in `domain/formal_smt`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
* [domain.formal_smt.describe](/symbols/domain/formal_smt/describe.md) - `def describe(a: dict[str, Any]) -> dict[str, Any]` in `domain/formal_smt`.
* [domain.formal_smt.explain](/symbols/domain/formal_smt/explain.md) - Leave-one-out counterexamples for the policy clauses behind the policy errors the kernel reports.

## Referenced by

* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
<!-- okf:generated:end links -->
