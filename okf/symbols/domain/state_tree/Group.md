---
type: Class
title: domain.state_tree.Group
description: What the tree check reads of a composite state (`models.Composite`, frozen, so read-only here).
resource: repo://src/eija_studio/domain/state_tree.py#Group
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/state_tree.py#Group
  title: domain/state_tree.py
  hash_method: ast-sig-v1
  sha256: 1aded265c2cd5a2cdc7b88282d255f1d2f5dc419de7af4a033d3dbdbadef3b31
notes_baseline: 901e3ad86984707adf7d6bc214491e8e216fc19f3c39986f386f031fa3e9898d
---

# domain.state_tree.Group

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/state_tree`](/modules/domain/state_tree.md) |
| Signature | `class Group(Protocol)` |
| Code | `repo://src/eija_studio/domain/state_tree.py#Group` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
What the tree check reads of a composite state (`models.Composite`, frozen, so read-only here).
~~~

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def name(self) -> str`
* `def states(self) -> tuple[str, ...]`
* `def initial(self) -> str`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.state_tree.is_tree](/symbols/domain/state_tree/is_tree.md) - Composite names are new and unique, each holds known, distinct children including its initial one, each state or composite has at most one parent, and no compo…
<!-- okf:generated:end links -->
