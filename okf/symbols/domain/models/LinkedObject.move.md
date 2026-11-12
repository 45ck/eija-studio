---
type: Method
title: domain.models.LinkedObject.move
description: The state `event` moves the object to from `state`, or None when it has no such move (or the state is unknown).
resource: repo://src/eija_studio/domain/models.py#LinkedObject.move
tags:
- symbol
- domain
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#LinkedObject.move
  title: domain/models.py
  hash_method: ast-v2
  sha256: be9ca15df93b98d0ef402ed18777782cd5effb018c7aae739a4dd0c817bc8aa3
notes_baseline: f82641e6ec5eeb1ebbf74b20e6c9bde80598eaa4ac08ac13801875bda4caa436
---

# domain.models.LinkedObject.move

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`domain/models`](/modules/domain/models.md) |
| Class | [`LinkedObject`](/symbols/domain/models/LinkedObject.md) |
| Signature | `def move(self, event: str, state: str \| None) -> str \| None` |
| Code | `repo://src/eija_studio/domain/models.py#LinkedObject.move` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The state `event` moves the object to from `state`, or None when it has no such move (or the state is
unknown).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
