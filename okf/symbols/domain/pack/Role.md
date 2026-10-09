---
type: Class
title: domain.pack.Role
description: 'A role and the kind of actor that holds it (ADR-0210): a person by default, or an AI agent, a timer or an external system.'
resource: repo://src/eija_studio/domain/pack.py#Role
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#Role
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: a1bfd211ed868dcbd829cd5bf26561bc5cbebefedd0d7f8c4ce78eaf94857d33
notes_baseline: d3068de4a1939c99f88f1a8c0050a2b2ea091f3eb6ec3743bfe20b9ccb5bb27e
---

# domain.pack.Role

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class Role(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#Role` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A role and the kind of actor that holds it (ADR-0210): a person by default, or an AI agent, a timer or an
external system. The kernel authorises every kind alike; laws such as ``only_kind_holds`` tell them apart.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(min_length=1, max_length=60)` |
| `description` | `str` | `Field(default='', max_length=400)` |
| `kind` | `RoleKind` | `'human'` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.RoleKind](/symbols/domain/laws/RoleKind.md) - Type alias `RoleKind` in `domain/laws`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
