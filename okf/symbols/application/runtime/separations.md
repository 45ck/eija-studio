---
type: Function
title: application.runtime.separations
description: 'The pack''s separation-of-duties laws in force on ``model`` that name ``action`` (issue #149, ADR-0233).'
resource: repo://src/eija_studio/application/runtime.py#separations
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#separations
  title: application/runtime.py
  hash_method: ast-v2
  sha256: c2c2c6a20c163ad5c71753e88c7f3ff3d2157a8f3b2e44886a44aecfc23bd623
notes_baseline: 15a3101d828890d631eaf6eec07314634c76a01002fb3a5a9a740c874caf0591
---

# application.runtime.separations

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def separations(pack: Pack, model: Workflow, action: str) -> list[DistinctActors]` |
| Code | `repo://src/eija_studio/application/runtime.py#separations` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's separation-of-duties laws in force on ``model`` that name ``action`` (issue #149, ADR-0233).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.DistinctActors](/symbols/domain/laws/DistinctActors.md) - Separation of duties (issue #149, ADR-0233): on one record, no single actor takes two different ``actions``, such as raising a request and approving it.
* [domain.laws.applies](/symbols/domain/laws/applies.md) - `def applies(law: _Law, actions: set[str]) -> bool` in `domain/laws`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
<!-- okf:generated:end links -->
