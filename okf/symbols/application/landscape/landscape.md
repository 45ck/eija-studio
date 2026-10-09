---
type: Function
title: application.landscape.landscape
description: 'The system the workflow `focus` is part of: its workflows, actors, links and findings (ADR-0203).'
resource: repo://src/eija_studio/application/landscape.py#landscape
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/landscape.py#landscape
  title: application/landscape.py
  hash_method: ast-v2
  sha256: 46ef302a26cb5432f624bea8526bd23e18db5152b284ba10fe6bf7911402f9a2
notes_baseline: 57e03f720b42a2462d56e670e038a57dbc81e1fb440fbc9622a7173a6b48dd80
---

# application.landscape.landscape

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/landscape`](/modules/application/landscape.md) |
| Signature | `def landscape(focus: str, systems: Iterable[tuple[Pack, DataModel \| None, Workflow]], unreadable: Iterable[str]=()) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/landscape.py#landscape` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The system the workflow `focus` is part of: its workflows, actors, links and findings (ADR-0203).

`systems` are the workflows that could be part of it (the packs beside the open one, each with its data model and the
model shown for it), the open one included. Workflows that share no class with the open one's system are listed
under `elsewhere`, so nothing is silently left out; `unreadable` names folders whose documents the kernel's checks
refused.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.landscape.FORMAT](/symbols/application/landscape/FORMAT.md) - Constant `FORMAT` in `application/landscape`.
* [application.landscape.LIMITS](/symbols/application/landscape/LIMITS.md) - Constant `LIMITS` in `application/landscape`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
