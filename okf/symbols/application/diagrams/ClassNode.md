---
type: Class
title: application.diagrams.ClassNode
description: '`class ClassNode` in `application/diagrams`.'
resource: repo://src/eija_studio/application/diagrams.py#ClassNode
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#ClassNode
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: 5e9514c56d7c1895335c5b1aae60c66d9cbb1bc1bc4eab51bad4763592221ed4
notes_baseline: c3426ec758d1c62f763319334d5203cbcb9930fe71f5ad2b50d10e3eb975f559
---

# application.diagrams.ClassNode

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class ClassNode` |
| Code | `repo://src/eija_studio/application/diagrams.py#ClassNode` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` |  |
| `stereotype` | `str \| None` |  |
| `members` | `tuple[Member, ...]` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Member](/symbols/application/diagrams/Member.md) - `class Member` in `application/diagrams`.

## Referenced by

* [application.diagrams.ClassModel](/symbols/application/diagrams/ClassModel.md) - `class ClassModel` in `application/diagrams`.
* [application.diagrams.class_model](/symbols/application/diagrams/class_model.md) - Domain contracts introspected from the Pydantic models.
<!-- okf:generated:end links -->
