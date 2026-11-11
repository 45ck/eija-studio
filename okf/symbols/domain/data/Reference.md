---
type: Class
title: domain.data.Reference
description: 'A built to-one association seen from the record: the field `name` holds the id of a stored `target` object.'
resource: repo://src/eija_studio/domain/data.py#Reference
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#Reference
  title: domain/data.py
  hash_method: ast-sig-v1
  sha256: 7fd509c935b71e7bf3d78c936e12a61e4ac5d71bc5882f5dfc1c3d7055db67f2
notes_baseline: 14b31c5b48d5a0614f0cf5f577b51ca94faf017b742e58953a7874b06f25e200
---

# domain.data.Reference

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `class Reference` |
| Code | `repo://src/eija_studio/domain/data.py#Reference` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A built to-one association seen from the record: the field `name` holds the id of a stored `target` object.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` |  |
| `target` | `str` |  |
| `required` | `bool` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.data.references](/symbols/domain/data/references.md) - The record's reference fields, one per built association, in declaration order.
<!-- okf:generated:end links -->
