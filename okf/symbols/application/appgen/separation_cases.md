---
type: Function
title: application.appgen.separation_cases
description: One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same record; the kernel's answer to the second (ADR-0233).
resource: repo://src/eija_studio/application/appgen.py#separation_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#separation_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 11916062e00640c7f18d04ca0880ab30106b89651083fb90ec330b44b1e2f1b5
notes_baseline: ab8c44e191f8d11c87ca314da6c1e7303db59ee682106a31c66d59d223694809
---

# application.appgen.separation_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def separation_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#separation_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One fixture actor takes an action of a separation-of-duties law, then tries another the law names, on the same
record; the kernel's answer to the second (ADR-0233). Only where the actor's role may take both, since otherwise
the role check refuses first. Empty without such a law, so every other oracle keeps its exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
