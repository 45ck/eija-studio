---
type: Class
title: domain.pack.ActionSpec
description: The declared guards and required effects of one action; the policy holds every transition to them.
resource: repo://src/eija_studio/domain/pack.py#ActionSpec
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#ActionSpec
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: d96dbd1d39869abb7654419d6facd1915522dec5057f30290d1160f553485daf
notes_baseline: 4506b04d74d8954e1554b0c4b5ed8f2d418d58f907f0559b743f9f89ab5e4147
---

# domain.pack.ActionSpec

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class ActionSpec(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#ActionSpec` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
The declared guards and required effects of one action; the policy holds every transition to them.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(min_length=1, max_length=60)` |
| `guards` | `tuple[Guard, ...]` | `Field(min_length=1)` |
| `required_effects` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Guard](/symbols/domain/models/Guard.md) - Type alias `Guard` in `domain/models`.

## Referenced by

* [domain.pack.Pack.action](/symbols/domain/pack/Pack.action.md) - `def action(self, name: str) -> ActionSpec | None` in `domain/pack`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
