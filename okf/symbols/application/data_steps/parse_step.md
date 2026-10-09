---
type: Function
title: application.data_steps.parse_step
description: 'A plan step: a data-model step, or else a kernel transaction (`parse_transaction`).'
resource: repo://src/eija_studio/application/data_steps.py#parse_step
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#parse_step
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: c248a068926a9d22b54156cad3cc3250d5d1939a5f7034641cf7eb27e31d48b8
notes_baseline: cffeb7c72a98dc53407ced9f330c521b15cd5c7a271085eb6825787e1ae0f3cc
---

# application.data_steps.parse_step

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def parse_step(data: Any) -> Step` |
| Code | `repo://src/eija_studio/application/data_steps.py#parse_step` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A plan step: a data-model step, or else a kernel transaction (`parse_transaction`). Malformed is `EDIT_INVALID`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.DATA_STEP_KINDS](/symbols/application/data_steps/DATA_STEP_KINDS.md) - Constant `DATA_STEP_KINDS` in `application/data_steps`.
* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.

## Referenced by

* [application.ripple.check_follow_ons](/symbols/application/ripple/check_follow_ons.md) - The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through the policy (`base` with `plan` and the step), a scr…
<!-- okf:generated:end links -->
