---
type: Constant
title: domain.laws.KIND_LAWS
description: Constant `KIND_LAWS` in `domain/laws`.
resource: repo://src/eija_studio/domain/laws.py#KIND_LAWS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#KIND_LAWS
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 674c9c961d9e03a84dcdb874f9be4e05d3efb6910e13b4736dcb477ee7e14986
notes_baseline: a0762e8b743685b2dc9c475af45829115360cd03759c63b828fe5f6804d8be6d
---

# domain.laws.KIND_LAWS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `KIND_LAWS = (OnlyKindHolds, OnlyKindEnters, PathRequiresKind)` |
| Code | `repo://src/eija_studio/domain/laws.py#KIND_LAWS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.OnlyKindEnters](/symbols/domain/laws/OnlyKindEnters.md) - Every transition entering ``state`` is held by a role of one of ``role_kinds``.
* [domain.laws.OnlyKindHolds](/symbols/domain/laws/OnlyKindHolds.md) - Every transition performing ``action`` is held by a role of one of ``role_kinds`` (e.g.
* [domain.laws.PathRequiresKind](/symbols/domain/laws/PathRequiresKind.md) - Every path from the initial state to ``state`` includes a step by a role of one of ``role_kinds``, the step entering ``state`` included: a human in the loop be…
<!-- okf:generated:end links -->
