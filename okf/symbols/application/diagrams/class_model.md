---
type: Function
title: application.diagrams.class_model
description: Domain contracts introspected from the Pydantic models.
resource: repo://src/eija_studio/application/diagrams.py#class_model
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#class_model
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: 47576c62ab0b1423bbae0a5146a2e628ae6333cbecfca36ae8df4b029458e68b
notes_baseline: f3ba32993f388d58399b2f88d420a2830f15e10c0a3fd3a69ee5598ac4f55743
---

# application.diagrams.class_model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def class_model() -> ClassModel` |
| Code | `repo://src/eija_studio/application/diagrams.py#class_model` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Domain contracts introspected from the Pydantic models. A field typed as another contract, or as a
named `Literal` alias (an enumeration), becomes a composition or association edge with its
multiplicity; every other field is a typed member.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [application.diagrams.ClassModel](/symbols/application/diagrams/ClassModel.md) - `class ClassModel` in `application/diagrams`.
* [application.diagrams.ClassNode](/symbols/application/diagrams/ClassNode.md) - `class ClassNode` in `application/diagrams`.
* [application.diagrams.Member](/symbols/application/diagrams/Member.md) - `class Member` in `application/diagrams`.
* [application.diagrams.Relation](/symbols/application/diagrams/Relation.md) - `class Relation` in `application/diagrams`.
<!-- okf:generated:end links -->
