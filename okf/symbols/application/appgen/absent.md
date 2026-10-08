---
type: Function
title: application.appgen.absent
description: A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
resource: repo://src/eija_studio/application/appgen.py#absent
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#absent
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 9a536bf6e2b9a8e44c5f8753ff097f86a9004b2365b75ee9965b6e45f3b7240d
notes_baseline: aa2bdf64a50b74b0b27093448f3b4d78dc07851b2cc2a78d44cfd779819847b3
---

# application.appgen.absent

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def absent(base: str, taken: set[str]) -> str` |
| Code | `repo://src/eija_studio/application/appgen.py#absent` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
<!-- okf:generated:end links -->
