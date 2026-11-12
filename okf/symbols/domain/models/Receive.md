---
type: Class
title: domain.models.Receive
description: 'A signal another workflow of the system sends that starts a record here (issue #93 item 5, ADR-0242): the signal effect `signal` declared by the pack `sender`.'
resource: repo://src/eija_studio/domain/models.py#Receive
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Receive
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: a15e86a782916c1c40e72f9c99a681dc192a62c97fa89cf9a75ef8088a24dcb4
notes_baseline: 0710c9eb2885653187713843300acc533ef13a5291faed38dbf705db1a09592d
---

# domain.models.Receive

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Receive(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Receive` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A signal another workflow of the system sends that starts a record here (issue #93 item 5, ADR-0242): the
signal effect `signal` declared by the pack `sender`.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `signal` | `str` | `Field(pattern='^Signal:[A-Z][A-Za-z0-9]{0,59}$')` |
| `sender` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.Workflow.receiving](/symbols/domain/models/Workflow.receiving.md) - The declaration that `signal` from `sender` starts a record here, if there is one (ADR-0242).
<!-- okf:generated:end links -->
