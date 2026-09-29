---
type: Function
title: domain.formal_smt.explain
description: Leave-one-out counterexamples for the policy clauses behind the policy errors the kernel reports.
resource: repo://src/eija_studio/domain/formal_smt.py#explain
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_smt.py#explain
  title: domain/formal_smt.py
  hash_method: ast-v2
  sha256: 52febd1c9aee6c946fd743ead7051bf41e550ab0ed7c264db5d2a2ff6bf47195
notes_baseline: 72c9f611d993892de4ebe1761bce0571ca01620e9383e716a6b8035d7923006a
---

# domain.formal_smt.explain

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal_smt`](/modules/domain/formal_smt.md) |
| Signature | `def explain(a: dict[str, Any], policy_errors: tuple[str, ...]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/formal_smt.py#explain` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Leave-one-out counterexamples for the policy clauses behind the policy errors the kernel reports.

Display only: deleting the clause that blocks this fault lets a candidate with the fault through.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.as_records](/symbols/domain/formal/as_records.md) - Defensive view for display-only helpers: a list of dicts, or nothing.

## Referenced by

* [domain.formal_smt.SPEC](/symbols/domain/formal_smt/SPEC.md) - Constant `SPEC` in `domain/formal_smt`.
<!-- okf:generated:end links -->
