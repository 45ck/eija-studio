---
type: Class
title: domain.laws.RequiresEvidence
description: A review needs evidence of this kind; judged by the evidence matrix, never by the table.
resource: repo://src/eija_studio/domain/laws.py#RequiresEvidence
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#RequiresEvidence
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: ce40fd7aea352cd741cae91728c378afad3798cc13143077fe6b957ec2185ab9
notes_baseline: 32dacdcb6c168214769d029822d928b5cb5b1b367fd9f3ca5eed30049c010a55
---

# domain.laws.RequiresEvidence

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class RequiresEvidence(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#RequiresEvidence` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A review needs evidence of this kind; judged by the evidence matrix, never by the table.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['requires_evidence']` |  |
| `evidence` | `str` | `Field(pattern='^[a-z][a-z0-9_]{0,39}$')` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
