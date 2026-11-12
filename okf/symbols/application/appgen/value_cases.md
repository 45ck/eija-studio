---
type: Function
title: application.appgen.value_cases
description: For each transition with guards over record values, an actor who may take it tries it on records holding every combination of values its guards can tell apart (`value_guards.combinations`), and the kernel's answer (ADR-…
resource: repo://src/eija_studio/application/appgen.py#value_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#value_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: 5beb1f46b0d2fd13ac6e25c0e2ac31e559a41d0bc0fe5fe90afffcfc13bb72aa
notes_baseline: 1c53f8b5922e3b0ce0e7469736205c99dc80cb9272502580aafa66148ee2cae2
---

# application.appgen.value_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def value_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#value_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
For each transition with guards over record values, an actor who may take it tries it on records holding every
combination of values its guards can tell apart (`value_guards.combinations`), and the kernel's answer (ADR-0234).
Empty for a model without value guards, so every other oracle keeps its exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ValueGuard](/symbols/domain/models/ValueGuard.md) - A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234).
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.value_guards.MAX_VALUATIONS](/symbols/domain/value_guards/MAX_VALUATIONS.md) - Constant `MAX_VALUATIONS` in `domain/value_guards`.
* [domain.value_guards.combinations](/symbols/domain/value_guards/combinations.md) - `valuations` over these guards, grouped by attribute.
<!-- okf:generated:end links -->
