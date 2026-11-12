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
  sha256: 58f8abeca724aa3179b186adac9da17cc0182d6e65e15b100646d1a302fb90ac
notes_baseline: d304d113fb0b48908596860ebb29a918fca6c73b4ee8853bbb085bf7adcd88aa
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
