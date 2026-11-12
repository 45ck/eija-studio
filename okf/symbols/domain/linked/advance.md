---
type: Function
title: domain.linked.advance
description: The objects' states after `transition` (unchanged when it moves none), or None when one of its moves is not possible from their states.
resource: repo://src/eija_studio/domain/linked.py#advance
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/linked.py#advance
  title: domain/linked.py
  hash_method: ast-v2
  sha256: 3861f2d1a8d5f5dc2eaf9c2fa931e3633075ded4b203d1884e38adf9c420d71d
notes_baseline: 7447e236ce6535da80ad6afb6dd551cba88e44e45069ef4940955de958bb79b1
---

# domain.linked.advance

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/linked`](/modules/domain/linked.md) |
| Signature | `def advance(model: Workflow, transition: Transition \| None, objects: dict[str, str]) -> dict[str, str] \| None` |
| Code | `repo://src/eija_studio/domain/linked.py#advance` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The objects' states after `transition` (unchanged when it moves none), or None when one of its moves is not
possible from their states.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
