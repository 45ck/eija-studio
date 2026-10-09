---
type: Function
title: application.ripple.ripple
description: Every diagram's effects of going from `base` to `candidate`.
resource: repo://src/eija_studio/application/ripple.py#ripple
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ripple.py#ripple
  title: application/ripple.py
  hash_method: ast-v2
  sha256: 2c68d3c0c32090eabd6cb9be65a145a592a201ce97558894aa30d6b6e74c8a6c
notes_baseline: b29fe4f1a71c22ad417a89b70a0f45a19879a5ac4340cc521b396bc2f88d6e6d
---

# application.ripple.ripple

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/ripple`](/modules/application/ripple.md) |
| Signature | `def ripple(base: Workflow, candidate: Workflow, data: DataModel \| None, screens: tuple[Screens, Screens], builds: tuple[Build, Build], components: Iterable[dict[str, Any]], sequences: dict[str, Any] \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/ripple.py#ripple` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every diagram's effects of going from `base` to `candidate`. `screens` and `builds` are each (before, after);
`components` are the after build's components (each with its `files`), naming whose files changed; `sequences` is
`application.sequences.check_sequences` of the scenarios on `candidate` against `base`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ripple.Build](/symbols/application/ripple/Build.md) - Type alias `Build` in `application/ripple`.
* [application.ripple.FORMAT](/symbols/application/ripple/FORMAT.md) - Constant `FORMAT` in `application/ripple`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
<!-- okf:generated:end links -->
