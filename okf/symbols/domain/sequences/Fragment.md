---
type: Class
title: domain.sequences.Fragment
description: '`class Fragment(Contract)` in `domain/sequences`.'
resource: repo://src/eija_studio/domain/sequences.py#Fragment
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#Fragment
  title: domain/sequences.py
  hash_method: ast-sig-v1
  sha256: 80a766993cb6068a6046331aad262a62495fc4a9f4a815348ee376bd1a02d492
notes_baseline: 660523765d6f19f4add13a50d59b995ca281bd4f7940325beead1c20533609ef
---

# domain.sequences.Fragment

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `class Fragment(Contract)` |
| Code | `repo://src/eija_studio/domain/sequences.py#Fragment` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `fragment` | `Literal['opt', 'alt', 'neg']` |  |
| `operands` | `tuple[Operand, ...]` | `Field(min_length=1, max_length=4)` |
| `refused` | `str \| None` | `Field(default=None, pattern='^[A-Z][A-Z_:]{0,59}$')` |

## Methods

* [`shape`](/symbols/domain/sequences/Fragment.shape.md) - `def shape(self) -> Fragment`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.sequences.Operand](/symbols/domain/sequences/Operand.md) - `class Operand(Contract)` in `domain/sequences`.

## Referenced by

* [domain.sequences.Fragment.shape](/symbols/domain/sequences/Fragment.shape.md) - `def shape(self) -> Fragment` in `domain/sequences`.
* [domain.sequences.Step](/symbols/domain/sequences/Step.md) - Type alias `Step` in `domain/sequences`.
<!-- okf:generated:end links -->
