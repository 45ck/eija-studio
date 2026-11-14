---
type: Module
title: domain.state_tree
description: 'Composite states form a tree over a workflow''s states (issue #93 item 3, ADR-0240).'
resource: repo://src/eija_studio/domain/state_tree.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/state_tree.py
  title: domain/state_tree.py
  hash_method: ast-api-v1
  sha256: b121e9179c29adcaa774d3502a3977ebcd46ff3f25c317b7649134db838e25b5
notes_baseline: d901a1067de0bd63fe00c2d4fea619ab9d26ab4f39ebef3d668c8082365a784b
---

# domain.state_tree

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/state_tree.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Composite states form a tree over a workflow's states (issue #93 item 3, ADR-0240).

Kept apart from `models.py` so the contracts module stays small; `Workflow` asks `is_tree` when it validates. Pure.
~~~

## Public symbols

* [`Group`](/symbols/domain/state_tree/Group.md) (class) - What the tree check reads of a composite state (`models.Composite`, frozen, so read-only here).
* [`is_tree`](/symbols/domain/state_tree/is_tree.md) (function) - Composite names are new and unique, each holds known, distinct children including its initial one, each state or compos…
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.state_tree.Group](/symbols/domain/state_tree/Group.md) - What the tree check reads of a composite state (`models.Composite`, frozen, so read-only here).
* [domain.state_tree.is_tree](/symbols/domain/state_tree/is_tree.md) - Composite names are new and unique, each holds known, distinct children including its initial one, each state or composite has at most one parent, and no compo…
<!-- okf:generated:end links -->
