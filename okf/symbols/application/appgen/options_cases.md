---
type: Function
title: application.appgen.options_cases
description: 'What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether the kernel would take it from there at version 0, with its r…'
resource: repo://src/eija_studio/application/appgen.py#options_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#options_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: cd7fd037cd3e72e8f0a02586b188a8ea93aef62417bc0bd34647286d0c885f0d
notes_baseline: 1bfb089ac69195d90d908e69dec71f3b92dd06fc141c9649e7759261308126ee
---

# application.appgen.options_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def options_cases(pack: Pack, model: Workflow, data: DataModel \| None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/appgen.py#options_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid
values: every action leaving that state, and whether the kernel would take it from there at version 0, with its
refusal code when it would not.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.UNKNOWN_ACTOR](/symbols/application/appgen/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/appgen`.
* [application.appgen.absent](/symbols/application/appgen/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.appgen.valid_values](/symbols/application/appgen/valid_values.md) - A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
