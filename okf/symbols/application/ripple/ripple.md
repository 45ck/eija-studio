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
  sha256: c16e8fb96bbc8ac020ecd25e5a85fd7b15d20ff37e22842d7d45aa3349e547f4
notes_baseline: c0ea5991f14069a2d39083b7d01dd3218a909324fe2320a9f73a0bca78723fb2
---

# application.ripple.ripple

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/ripple`](/modules/application/ripple.md) |
| Signature | `def ripple(base: Workflow, candidate: Workflow, data: DataModel \| None, screens: tuple[Screens, Screens], builds: tuple[Build, Build], components: Iterable[dict[str, Any]]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/ripple.py#ripple` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every diagram's effects of going from `base` to `candidate`. `screens` and `builds` are each (before, after);
`components` are the after build's components (each with its `files`), naming whose files changed.
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
