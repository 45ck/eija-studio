---
type: Function
title: application.appgen.create_cases
description: 'Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.'
resource: repo://src/eija_studio/application/appgen.py#create_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#create_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: c1819816202c2105006f0eea352d49840dc25f7ae8a4d44d55922e9fb3691c5e
notes_baseline: 48fa08be9f2fceabe223ae93f617ccb18b6d3bc127f9216e768e53993417a039
---

# application.appgen.create_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def create_cases(pack: Pack, model: Workflow, data: DataModel \| None) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#create_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts
in, or the refusal. Revoked and unknown actors are refused as the kernel refuses them an action; a model that names
its initiators refuses anyone else (ADR-0231); everyone else gets a record in the model's initial state.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.UNKNOWN_ACTOR](/symbols/application/appgen/UNKNOWN_ACTOR.md) - Constant `UNKNOWN_ACTOR` in `application/appgen`.
* [application.appgen.absent](/symbols/application/appgen/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - Start a record.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
