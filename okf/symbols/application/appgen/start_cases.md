---
type: Function
title: application.appgen.start_cases
description: Each active fixture actor starting a record, and the kernel's answer.
resource: repo://src/eija_studio/application/appgen.py#start_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#start_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 39024ecd200f87a5d5ce133cdfe120ab0d4826cee78279853d7fcf9b5b3759fe
notes_baseline: cbd59e8157aab1fe43d7a32b9791b662682b1536e9fed852777a51b38fc87572
---

# application.appgen.start_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def start_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#start_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Each active fixture actor starting a record, and the kernel's answer. Only for a model that names initiators,
so the oracle of every other model keeps its exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.may_start](/symbols/application/appgen/may_start.md) - Whether the model lets this role start a record (ADR-0231): any role when it names no initiators.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
