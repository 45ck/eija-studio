---
type: Function
title: domain.laws.protected
description: The one state ``law`` protects, if it is a law of that kind.
resource: repo://src/eija_studio/domain/laws.py#protected
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#protected
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 1d30a822c95749d128698122f211acbebc0a8c10cb9745ce87b6da606202eccf
notes_baseline: 8ecdebfcf91d8fad0ceb3658cc0357be98003bb01f5eea1d773a22ae7c3e36ce
---

# domain.laws.protected

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `def protected(law: _Law) -> str \| None` |
| Code | `repo://src/eija_studio/domain/laws.py#protected` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The one state ``law`` protects, if it is a law of that kind.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.OnlyKindEnters](/symbols/domain/laws/OnlyKindEnters.md) - Every transition entering ``state`` is held by a role of one of ``role_kinds``.
* [domain.laws.PathRequires](/symbols/domain/laws/PathRequires.md) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [domain.laws.PathRequiresKind](/symbols/domain/laws/PathRequiresKind.md) - Every path from the initial state to ``state`` includes a step by a role of one of ``role_kinds``, the step entering ``state`` included: a human in the loop be…
* [domain.laws.RoleNeverEnters](/symbols/domain/laws/RoleNeverEnters.md) - No transition held by ``role`` enters ``state``.
* [domain.laws.StateFinal](/symbols/domain/laws/StateFinal.md) - No transition leaves ``state``.
* [domain.laws.StateOnlyVia](/symbols/domain/laws/StateOnlyVia.md) - Every transition entering ``state`` performs one of ``actions``.

## Referenced by

* [domain.laws.protects_absent](/symbols/domain/laws/protects_absent.md) - Whether ``law`` protects a state the model does not have: the law is broken, never vacuously kept.
<!-- okf:generated:end links -->
