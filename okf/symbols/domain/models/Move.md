---
type: Class
title: domain.models.Move
description: 'One transition in a linked object''s lifecycle: `event` moves it from `from_state` to `to_state` (ADR-0241).'
resource: repo://src/eija_studio/domain/models.py#Move
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Move
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 94a69e49c94354a0f91867dbd5653b139ef33a3daa21f3a2e9b1de531c3e5180
notes_baseline: aef589774ca0a7d6e029099919836a6209827e87d21773e00935646b1f008a43
---

# domain.models.Move

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Move(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Move` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One transition in a linked object's lifecycle: `event` moves it from `from_state` to `to_state` (ADR-0241).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `event` | `str` | `Field(pattern='^[a-z][a-zA-Z0-9]{0,39}$')` |
| `from_state` | `str` | `Field(min_length=1, max_length=60)` |
| `to_state` | `str` | `Field(min_length=1, max_length=60)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.models.LinkedObject](/symbols/domain/models/LinkedObject.md) - The lifecycle of the object a record links to through a reference field, such as a deploy request's `target` service (issue #93 item 4, ADR-0241): a small stat…
<!-- okf:generated:end links -->
