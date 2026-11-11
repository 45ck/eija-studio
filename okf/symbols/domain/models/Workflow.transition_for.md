---
type: Method
title: domain.models.Workflow.transition_for
description: The transition ``action`` takes from ``state``; without a state, or when it does not leave that state, any transition it labels (they differ only in id and source, ADR-0232).
resource: repo://src/eija_studio/domain/models.py#Workflow.transition_for
tags:
- symbol
- domain
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Workflow.transition_for
  title: domain/models.py
  hash_method: ast-v2
  sha256: 127277e3b98915f047a0f275070cb5f63402abcd2d4bcd18cbdfb240466ee314
notes_baseline: 1eef1a69b950622d684645a7d710f8b04b45e76fc85403583cf20e2c3b988d0b
---

# domain.models.Workflow.transition_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`domain/models`](/modules/domain/models.md) |
| Class | [`Workflow`](/symbols/domain/models/Workflow.md) |
| Signature | `def transition_for(self, action: str, state: str \| None=None) -> Transition \| None` |
| Code | `repo://src/eija_studio/domain/models.py#Workflow.transition_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The transition ``action`` takes from ``state``; without a state, or when it does not leave that state,
any transition it labels (they differ only in id and source, ADR-0232). None when the action is not modelled.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
