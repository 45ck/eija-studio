---
type: Class
title: domain.models.Composite
description: 'A UML composite state (issue #93 item 3, ADR-0240): a named group of states, or of other composites, with the child a transition into the group enters first.'
resource: repo://src/eija_studio/domain/models.py#Composite
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Composite
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 54682768b36bac766d2ceace6e0fa75a0c1b176ef8d186fb5e6823bb10001504
notes_baseline: 2f2ee384340f8eed90ec38b9eb805ecabe8aa91d1ccdf336f18eac88f9ed9284
---

# domain.models.Composite

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Composite(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Composite` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A UML composite state (issue #93 item 3, ADR-0240): a named group of states, or of other composites, with the
child a transition into the group enters first. A record is always in exactly one plain state; the composite is the
set of states inside it. The kernel runs the flat machine, so a composite never changes what a step does. A
transition the group's states all share is drawn once from the group, and SCXML gets a nested `<state>`.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` | `Field(min_length=1, max_length=60)` |
| `states` | `tuple[str, ...]` | `Field(min_length=1, max_length=32)` |
| `initial` | `str` | `Field(min_length=1, max_length=60)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.models.Workflow.composite](/symbols/domain/models/Workflow.composite.md) - `def composite(self, name: str) -> Composite | None` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
