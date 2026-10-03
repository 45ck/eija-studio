---
type: Function
title: domain.formal_bend.explain
description: Negative-control counterexamples whose fault class is one the kernel's own policy reports.
resource: repo://src/eija_studio/domain/formal_bend.py#explain
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bend.py#explain
  title: domain/formal_bend.py
  hash_method: ast-v2
  sha256: 0ad3d55df34f4e62d5475d9f505ca75860d271d0b7d2f1dfd14d00309b90b4f6
notes_baseline: 3127317bb0f83ae97d90011919509a03fa330ea39f674cde4a3d7095fed67710
---

# domain.formal_bend.explain

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal_bend`](/modules/domain/formal_bend.md) |
| Signature | `def explain(a: dict[str, Any], policy_errors: tuple[str, ...]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/formal_bend.py#explain` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Negative-control counterexamples whose fault class is one the kernel's own policy reports.

Display only: a seeded unsafe model with the same fault, not a proof about the candidate.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.as_records](/symbols/domain/formal/as_records.md) - Defensive view for display-only helpers: a list of dicts, or nothing.

## Referenced by

* [domain.formal_bend.SPEC](/symbols/domain/formal_bend/SPEC.md) - Constant `SPEC` in `domain/formal_bend`.
<!-- okf:generated:end links -->
