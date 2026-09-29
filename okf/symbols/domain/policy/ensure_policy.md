---
type: Function
title: domain.policy.ensure_policy
description: Raises DomainError POLICY_BLOCKED when check_policy reports any finding; called before every model is executed or transformed.
resource: repo://src/eija_studio/domain/policy.py#ensure_policy
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#ensure_policy
  title: domain/policy.py
  hash_method: ast-v2
  sha256: aa2469b554f5c4a5bd365235abc8161b7bd6b055670a8fd333d549bb766adc40
description_override: Raises DomainError POLICY_BLOCKED when check_policy reports any finding; called before every model is executed or transformed.
notes_baseline: d66cf47bd6fa859d683cfe1f3136af735b84b123a211c9575bdb61e1ad22da79
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 312b0eeb38c5cfced74e46d324621d279dcf1de42e83f930ffdb3934cf837adb
  sources_sha256: d66cf47bd6fa859d683cfe1f3136af735b84b123a211c9575bdb61e1ad22da79
---

# domain.policy.ensure_policy

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def ensure_policy(model: Workflow, pack: Pack \| None=None) -> None` |
| Code | `repo://src/eija_studio/domain/policy.py#ensure_policy` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The fail-closed wrapper: [runtime.execute](/symbols/application/runtime/execute.md), [runtime.initialise](/symbols/application/runtime/initialise.md) and `apply_transactions` all call it, so an out-of-policy model cannot be previewed, run or produced by an edit even if a caller skipped verification. The message lists the sorted finding codes from [check_policy](/symbols/domain/policy/check_policy.md); `details` carries the codes and the law/element refs.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
* [domain.policy.policy_refs](/symbols/domain/policy/policy_refs.md) - The laws and model elements a refusal points at (``law:<id>``, ``transition:<id>``, ``state:<id>``), sorted.

## Referenced by

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).
<!-- okf:generated:end links -->
