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
  sha256: bdf6dc9221a79f01a9bc1c6672dceffa3a6946cee75f5b521c0b3a34b90345cc
notes_baseline: 0b9b58643451b072ff6b73362a52f602df7189288044fb8bbde6ed0964b2a193
---

# application.ripple.ripple

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/ripple`](/modules/application/ripple.md) |
| Signature | `def ripple(base: Workflow, candidate: Workflow, data: DataModel \| None, screens: tuple[Screens, Screens], builds: tuple[Build, Build], components: Iterable[dict[str, Any]], sequences: dict[str, Any] \| None=None, attributes: Iterable[str]=()) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/ripple.py#ripple` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every diagram's effects of going from `base` to `candidate`. `screens` and `builds` are each (before, after);
`components` are the after build's components (each with its `files`), naming whose files changed; `sequences` is
`application.sequences.check_sequences` of the scenarios on `candidate` against `base`; `attributes` are the
class diagram's attribute changes in words (`data_steps.data_changes`).
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
