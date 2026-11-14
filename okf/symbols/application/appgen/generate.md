---
type: Function
title: application.appgen.generate
description: Return the per-model files and the build manifest (without file hashes or test results).
resource: repo://src/eija_studio/application/appgen.py#generate
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#generate
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 83492c4604678a869341eaeca9ee8b60426562d0e34be238743c9a1c290fb180
notes_baseline: bd5750cbb8f7d8a75b6ce9da153a6ae2d006e9ca203f82c5af2b0273aef37f9f
---

# application.appgen.generate

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def generate(pack: Pack, model: Workflow \| None=None, data: DataModel \| None=None, screens: Screens \| None=None) -> tuple[dict[str, str], dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/appgen.py#generate` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Return the per-model files and the build manifest (without file hashes or test results).

Refuses a model the protected policy blocks: an app is never built from a workflow the kernel would refuse. Nor from
screens with design problems (ADR-0154); without screens, each use case gets a default one.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.app_runs.create_cases](/symbols/application/app_runs/create_cases.md) - Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts in, or the refusal.
* [application.app_runs.journeys](/symbols/application/app_runs/journeys.md) - For each transition, a record started through the app and walked to it: the shortest run from the initial state whose last step is that transition, each step t…
* [application.app_runs.options_cases](/symbols/application/app_runs/options_cases.md) - What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid values: every action leaving that state, and whether…
* [application.app_runs.rules](/symbols/application/app_runs/rules.md) - The rule table the app shows: each action once, every state it leaves, where it leads and who takes it.
* [application.appgen.CASE_KINDS](/symbols/application/appgen/CASE_KINDS.md) - Constant `CASE_KINDS` in `application/appgen`.
* [application.appgen.FORMAT](/symbols/application/appgen/FORMAT.md) - Constant `FORMAT` in `application/appgen`.
* [application.appgen.app_limits](/symbols/application/appgen/app_limits.md) - `def app_limits(data: DataModel | None) -> list[str]` in `application/appgen`.
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [application.appgen.oracle_cases](/symbols/application/appgen/oracle_cases.md) - Every state x action x actor x expected version, then the same request replayed.
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
* [application.appgen.stock](/symbols/application/appgen/stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [application.appgen.valid_values](/symbols/application/appgen/valid_values.md) - A valid record: a sample of each attribute, and each reference naming the first `stock` object of its class.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.
* [domain.linked.along](/symbols/domain/linked/along.md) - For each state a record can reach, the states its linked objects are in when only this record moves them, from every object in its initial state: the first suc…
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.navigation.navigation_for](/symbols/domain/navigation/navigation_for.md) - Project actual supported panels from one canonical workflow/data/screens snapshot.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One default screen per use case.
* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.

## Referenced by

* [application.generated_app.assemble_app](/symbols/application/generated_app/assemble_app.md) - One generator and snapshot identity for previews and approved artifacts.
<!-- okf:generated:end links -->
