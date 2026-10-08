---
type: Function
title: application.memo.ensure_conforms
description: '`ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check''s own.'
resource: repo://src/eija_studio/application/memo.py#ensure_conforms
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/memo.py#ensure_conforms
  title: application/memo.py
  hash_method: ast-v2
  sha256: e161b270f5152fa53bfaf1ca279976b2042407d5b58f3287a88b1e0a74b29166
notes_baseline: a2299cf2ba12c53e3f8c5624b9365c0e918f297ac0db461d0dec7e1d8a7fe77b
---

# application.memo.ensure_conforms

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/memo`](/modules/application/memo.md) |
| Signature | `def ensure_conforms(model: Workflow, pack: Pack, ensure: Callable[[Workflow, Pack], None]) -> None` |
| Code | `repo://src/eija_studio/application/memo.py#ensure_conforms` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again,
so the error is always the check's own. The check is part of the key, so a different check is asked afresh.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
<!-- okf:generated:end links -->
