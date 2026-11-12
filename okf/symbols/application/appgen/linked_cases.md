---
type: Function
title: application.appgen.linked_cases
description: For each transition that moves linked objects, an actor who may take it tries it with the objects in every state of their lifecycles, and the kernel's answer, with the objects' states after a commit (ADR-0241).
resource: repo://src/eija_studio/application/appgen.py#linked_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#linked_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: b7e23a4409bdc09cb626c5787dba31d7d582eaf8ed8b34c1140fc0c622b312e8
notes_baseline: 6d43c34880a2b52de89247f534c5a517c973f705a0d3279238a49872e4eabcf0
---

# application.appgen.linked_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def linked_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#linked_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
For each transition that moves linked objects, an actor who may take it tries it with the objects in every
state of their lifecycles, and the kernel's answer, with the objects' states after a commit (ADR-0241). Empty for a
model without linked objects, so every other oracle keeps its exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.oracle_session.OracleSession](/symbols/application/oracle_session/OracleSession.md) - In-memory answers to exactly the port calls `execute` makes for one instance.
* [application.oracle_session.kernel_answer](/symbols/application/oracle_session/kernel_answer.md) - `def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,…` in `application/oracle_session`.
* [domain.linked.combinations](/symbols/domain/linked/combinations.md) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
