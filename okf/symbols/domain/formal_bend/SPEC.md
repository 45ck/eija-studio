---
type: Constant
title: domain.formal_bend.SPEC
description: Constant `SPEC` in `domain/formal_bend`.
resource: repo://src/eija_studio/domain/formal_bend.py#SPEC
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bend.py#SPEC
  title: domain/formal_bend.py
  hash_method: ast-v2
  sha256: 1827fd8874bad73e0f6c25e0ef7154c3930c59815c6bcf43ae05271778fa7f75
notes_baseline: 2a83fe6b0039c9cd30e137846a6cdaec5fb26521c8e27a2e3f87764ef1b2e74d
---

# domain.formal_bend.SPEC

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/formal_bend`](/modules/domain/formal_bend.md) |
| Signature | `SPEC = KindSpec(kind='bend_proof', claim='authority_laws_model', method='formal-bend-proof-v1', protocol=PROTOCOL, level=LEVEL_SEALED_TOOL, establishes=ESTABLI…` |
| Code | `repo://src/eija_studio/domain/formal_bend.py#SPEC` |
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
* [domain.formal_bend.DOES_NOT_ESTABLISH](/symbols/domain/formal_bend/DOES_NOT_ESTABLISH.md) - Constant `DOES_NOT_ESTABLISH` in `domain/formal_bend`.
* [domain.formal_bend.ESTABLISHES](/symbols/domain/formal_bend/ESTABLISHES.md) - Constant `ESTABLISHES` in `domain/formal_bend`.
* [domain.formal_bend.PREREQUISITES](/symbols/domain/formal_bend/PREREQUISITES.md) - Constant `PREREQUISITES` in `domain/formal_bend`.
* [domain.formal_bend.PROTOCOL](/symbols/domain/formal_bend/PROTOCOL.md) - Constant `PROTOCOL` in `domain/formal_bend`.
* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bend.describe](/symbols/domain/formal_bend/describe.md) - `def describe(a: dict[str, Any]) -> dict[str, Any]` in `domain/formal_bend`.
* [domain.formal_bend.explain](/symbols/domain/formal_bend/explain.md) - Negative-control counterexamples whose fault class is one the kernel's own policy reports.

## Referenced by

* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
<!-- okf:generated:end links -->
