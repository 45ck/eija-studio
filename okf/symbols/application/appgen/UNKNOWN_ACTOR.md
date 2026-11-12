---
type: Constant
title: application.appgen.UNKNOWN_ACTOR
description: Constant `UNKNOWN_ACTOR` in `application/appgen`.
resource: repo://src/eija_studio/application/appgen.py#UNKNOWN_ACTOR
tags:
- symbol
- application
- constant
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#UNKNOWN_ACTOR
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 97c137064dc9952d143e62fddcc867a22ac590e8a92a9a446f5c959b9d37e9a5
notes_baseline: 1ced7d519677a83b0f91b9db65b4efa477617a4d23555a5fc9005e7a20bb54f1
---

# application.appgen.UNKNOWN_ACTOR

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `UNKNOWN_ACTOR = 'unknown-actor'` |
| Code | `repo://src/eija_studio/application/appgen.py#UNKNOWN_ACTOR` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.appgen.create_cases](/symbols/application/appgen/create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.appgen.options_cases](/symbols/application/appgen/options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether…
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
<!-- okf:generated:end links -->
