---
type: Function
title: application.appgen.object_cases
description: 'Objects of each class a record refers to, created through the app (ADR-0235): a valid one, which starts in its lifecycle''s initial state when the model gives it one (ADR-0241), then each value missing, of the wrong type…'
resource: repo://src/eija_studio/application/appgen.py#object_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#object_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: bc8248f4e6268c26e71517c3bfcce18ddf0b08ccb935ed0fb649d5230b43ec6a
notes_baseline: 60a5c7ca3076e576924c6e1ccc995bd231aa5d14a5d42533a168b3da004338b4
---

# application.appgen.object_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def object_cases(pack: Pack, model: Workflow, data: DataModel \| None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/appgen.py#object_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Objects of each class a record refers to, created through the app (ADR-0235): a valid one, which starts in its
lifecycle's initial state when the model gives it one (ADR-0241), then each value missing, of the wrong type, too
long or not a choice, and the data model's answer for each. Empty when no association is built, so other oracles
keep their exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.stock](/symbols/application/appgen/stock.md) - One valid object of each class a record refers to (ADR-0235), stored before the data cases run.
* [application.oracle_session.absent](/symbols/application/oracle_session/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
