---
type: Function
title: domain.state_tree.is_tree
description: Composite names are new and unique, each holds known, distinct children including its initial one, each state or composite has at most one parent, and no composite holds itself.
resource: repo://src/eija_studio/domain/state_tree.py#is_tree
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/state_tree.py#is_tree
  title: domain/state_tree.py
  hash_method: ast-v2
  sha256: 0d9f898c682585a0634264d9024fd3438b73cf447ed7e3c9de9966bf1c5e0950
notes_baseline: ada4cded1e463fec75351017737edcfd99cf8ca948364ab0611362c4ab09a0bf
---

# domain.state_tree.is_tree

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/state_tree`](/modules/domain/state_tree.md) |
| Signature | `def is_tree(states: tuple[str, ...], composites: Sequence[Group]) -> bool` |
| Code | `repo://src/eija_studio/domain/state_tree.py#is_tree` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Composite names are new and unique, each holds known, distinct children including its initial one, each state or
composite has at most one parent, and no composite holds itself. True when there are none.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.state_tree.Group](/symbols/domain/state_tree/Group.md) - What the tree check reads of a composite state (`models.Composite`, frozen, so read-only here).
<!-- okf:generated:end links -->
