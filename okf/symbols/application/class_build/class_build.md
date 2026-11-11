---
type: Function
title: application.class_build.class_build
description: Which classes and associations the built app stores and checks, and what to consider about the rest.
resource: repo://src/eija_studio/application/class_build.py#class_build
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/class_build.py#class_build
  title: application/class_build.py
  hash_method: ast-v2
  sha256: 8b1341e8c594c3eff6490110aa46ee9ef7bccc20881805764a3b22bc680b0936
notes_baseline: 07e53f530be214fef8ff0d159e869da9defd1537716af54eb9f91959033ea5df
---

# application.class_build.class_build

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/class_build`](/modules/application/class_build.md) |
| Signature | `def class_build(data: DataModel) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/class_build.py#class_build` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Which classes and associations the built app stores and checks, and what to consider about the rest.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.class_build.FORMAT](/symbols/application/class_build/FORMAT.md) - Constant `FORMAT` in `application/class_build`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.

## Referenced by

* [application.c4.app_c4](/symbols/application/c4/app_c4.md) - Current generated-source architecture, plus explicit fixture and data-design limits.
<!-- okf:generated:end links -->
