---
type: Function
title: application.appgen.timer_cases
description: For each transition with a time event, an actor who may take it tries it on a record that has been in the source state half the time and the whole time, and the kernel's answer (ADR-0237).
resource: repo://src/eija_studio/application/appgen.py#timer_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#timer_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: b9acb98778fc485127838d819c84b7513f3814b8fc7eabfe4d51fb6619b45480
notes_baseline: cf45e05420dc74458d9cf93ff60319b109cf38fc1d1159ccd336357f26dec5be
---

# application.appgen.timer_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def timer_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#timer_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
For each transition with a time event, an actor who may take it tries it on a record that has been in the source
state half the time and the whole time, and the kernel's answer (ADR-0237). Empty for a model without time events,
so every other oracle keeps its exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.oracle_session.OracleSession](/symbols/application/oracle_session/OracleSession.md) - In-memory answers to exactly the port calls `execute` makes for one instance.
* [application.oracle_session.kernel_answer](/symbols/application/oracle_session/kernel_answer.md) - `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
