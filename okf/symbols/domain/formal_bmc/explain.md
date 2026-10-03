---
type: Function
title: domain.formal_bmc.explain
description: 'The bounded search explains no policy error: its faults are runtime faults, not workflow faults.'
resource: repo://src/eija_studio/domain/formal_bmc.py#explain
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bmc.py#explain
  title: domain/formal_bmc.py
  hash_method: ast-v2
  sha256: d28ae19cfc1017c16f9700fbd705566a4fbdaf7d68358cffcfc2ddd39a603120
notes_baseline: b23c295766cb571c295f85eac0b183568ddc1d317693cb11d89271f1c5eb1d5d
---

# domain.formal_bmc.explain

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal_bmc`](/modules/domain/formal_bmc.md) |
| Signature | `def explain(a: dict[str, Any], policy_errors: tuple[str, ...]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/formal_bmc.py#explain` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The bounded search explains no policy error: its faults are runtime faults, not workflow faults.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.formal_bmc.SPEC](/symbols/domain/formal_bmc/SPEC.md) - Constant `SPEC` in `domain/formal_bmc`.
<!-- okf:generated:end links -->
