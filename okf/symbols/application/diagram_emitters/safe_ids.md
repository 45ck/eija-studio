---
type: Function
title: application.diagram_emitters.safe_ids
description: Stable identifier map.
resource: repo://src/eija_studio/application/diagram_emitters.py#safe_ids
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_emitters.py#safe_ids
  title: application/diagram_emitters.py
  hash_method: ast-v2
  sha256: f997516c050003cd3a039c076615343fcff6f2364a274703c7778373ddef7909
notes_baseline: be17403ab5bec240b457e00b6dc8c6bdd8dee6a6d264dc260d907c8a83d8fef5
---

# application.diagram_emitters.safe_ids

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagram_emitters`](/modules/application/diagram_emitters.md) |
| Signature | `def safe_ids(raw: list[str] \| set[str] \| tuple[str, ...]) -> dict[str, str]` |
| Code | `repo://src/eija_studio/application/diagram_emitters.py#safe_ids` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Stable identifier map. Assigned in sorted order, so it does not depend on definition order.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
