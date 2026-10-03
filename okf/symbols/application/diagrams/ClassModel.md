---
type: Class
title: application.diagrams.ClassModel
description: '`class ClassModel` in `application/diagrams`.'
resource: repo://src/eija_studio/application/diagrams.py#ClassModel
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#ClassModel
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: 400ac3eab3773424c07c421b26f8f0a0d85b86f6f74e89aae955150366eeba05
notes_baseline: d44ab380756b5c70572995be4eaefc6a747f3f0b8c1f61356732d41c616ae9d6
---

# application.diagrams.ClassModel

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class ClassModel` |
| Code | `repo://src/eija_studio/application/diagrams.py#ClassModel` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `title` | `str` |  |
| `classes` | `tuple[ClassNode, ...]` |  |
| `relations` | `tuple[Relation, ...]` |  |
| `provenance` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.ClassNode](/symbols/application/diagrams/ClassNode.md) - `class ClassNode` in `application/diagrams`.
* [application.diagrams.Relation](/symbols/application/diagrams/Relation.md) - `class Relation` in `application/diagrams`.

## Referenced by

* [application.diagram_emitters.emit](/symbols/application/diagram_emitters/emit.md) - Serialise a diagram model.
* [application.diagrams.Diagram](/symbols/application/diagrams/Diagram.md) - Type alias `Diagram` in `application/diagrams`.
* [application.diagrams.class_model](/symbols/application/diagrams/class_model.md) - Domain contracts introspected from the Pydantic models.
<!-- okf:generated:end links -->
