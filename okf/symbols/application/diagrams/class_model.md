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
  sha256: 9f5db4152d9dc3eb50be9ae6d4f7f5ff4210d1b4c39443c26704a7622eb816c6
notes_baseline: 25045aa0ae61249e06ecaa5d887d3ef538b45a74c3cee170e554062ed4ebfbfd
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
