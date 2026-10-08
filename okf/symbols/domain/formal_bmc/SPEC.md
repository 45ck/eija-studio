---
type: Constant
title: domain.formal_bmc.SPEC
description: Constant `SPEC` in `domain/formal_bmc`.
resource: repo://src/eija_studio/domain/formal_bmc.py#SPEC
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bmc.py#SPEC
  title: domain/formal_bmc.py
  hash_method: ast-v2
  sha256: 600c33d670140ab030be9c6f0afc462646c10f98eb3022147de8f99127b563f0
notes_baseline: 7d9e514b141deaa01bbc89f0ce4fd9240a41d1fe8991c3c91a2140c2541a1a95
---

# domain.formal_bmc.SPEC

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/formal_bmc`](/modules/domain/formal_bmc.md) |
| Signature | `SPEC = KindSpec(kind='bounded_model_check', claim='runtime_safety_bounded', method='formal-bounded-model-check-v1', protocol=PROTOCOL, level=LEVEL_SEALED_TOOL,…` |
| Code | `repo://src/eija_studio/domain/formal_bmc.py#SPEC` |
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
* [domain.formal_bmc.DOES_NOT_ESTABLISH](/symbols/domain/formal_bmc/DOES_NOT_ESTABLISH.md) - Constant `DOES_NOT_ESTABLISH` in `domain/formal_bmc`.
* [domain.formal_bmc.ESTABLISHES](/symbols/domain/formal_bmc/ESTABLISHES.md) - Constant `ESTABLISHES` in `domain/formal_bmc`.
* [domain.formal_bmc.PREREQUISITES](/symbols/domain/formal_bmc/PREREQUISITES.md) - Constant `PREREQUISITES` in `domain/formal_bmc`.
* [domain.formal_bmc.PROTOCOL](/symbols/domain/formal_bmc/PROTOCOL.md) - Constant `PROTOCOL` in `domain/formal_bmc`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_bmc.describe](/symbols/domain/formal_bmc/describe.md) - `def describe(a: dict[str, Any]) -> dict[str, Any]` in `domain/formal_bmc`.
* [domain.formal_bmc.explain](/symbols/domain/formal_bmc/explain.md) - The bounded search explains no policy error: its faults are runtime faults, not workflow faults.

## Referenced by

* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
<!-- okf:generated:end links -->
