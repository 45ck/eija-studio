---
type: Class
title: domain.laws.When
description: Condition under which a law applies.
resource: repo://src/eija_studio/domain/laws.py#When
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#When
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 38f84cd415582d81dc0265af9fc38e52524d5e62fce482b401b6d4fcb2e80e4c
notes_baseline: 209072dbd4b7c381f1c4708ea7e1bac8046491193483df05f084dfef2226d29f
---

# domain.laws.When

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class When(Contract)` |
| Code | `repo://src/eija_studio/domain/laws.py#When` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Condition under which a law applies. Both unset means always.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `action_present` | `Name \| None` | `None` |
| `action_absent` | `Name \| None` | `None` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
<!-- okf:generated:end links -->
