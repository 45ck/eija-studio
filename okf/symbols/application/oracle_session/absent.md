---
type: Function
title: application.oracle_session.absent
description: A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
resource: repo://src/eija_studio/application/oracle_session.py#absent
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/oracle_session.py#absent
  title: application/oracle_session.py
  hash_method: ast-v2
  sha256: 9a536bf6e2b9a8e44c5f8753ff097f86a9004b2365b75ee9965b6e45f3b7240d
notes_baseline: 9ed16b678b9e8ab5584b0ec32063e28a8706137d7e1c947850aa2c4aefc9bf1c
---

# application.oracle_session.absent

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/oracle_session`](/modules/application/oracle_session.md) |
| Signature | `def absent(base: str, taken: set[str]) -> str` |
| Code | `repo://src/eija_studio/application/oracle_session.py#absent` |
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

* [application.app_runs.create_cases](/symbols/application/app_runs/create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.app_runs.options_cases](/symbols/application/app_runs/options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether…
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [application.appgen.object_cases](/symbols/application/appgen/object_cases.md) - Objects of each class a record refers to, created through the app (ADR-0235): a valid one, which starts in its lifecycle's initial state when the model gives i…
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.signal_cases](/symbols/application/appgen/signal_cases.md) - Each signal the model receives, delivered with valid record values, and the kernel's answer (a record started in the initial state), then the first one under a…
<!-- okf:generated:end links -->
