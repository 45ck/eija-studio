---
type: Class
title: domain.evidence.FormalVerdict
description: The status of one evidence kind for the current subject, with the receipt that decided it.
resource: repo://src/eija_studio/domain/evidence.py#FormalVerdict
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#FormalVerdict
  title: domain/evidence.py
  hash_method: ast-sig-v1
  sha256: c86841b657d8147ff80901fc2b8cd2a8403e2d396382497e09ecf60af89f4b86
notes_baseline: 6f3f0ed36499913bf3d4656a1cc0dd4a5912efa7cd88a99f27aefb4879871208
---

# domain.evidence.FormalVerdict

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `class FormalVerdict` |
| Code | `repo://src/eija_studio/domain/evidence.py#FormalVerdict` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
The status of one evidence kind for the current subject, with the receipt that decided it.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `str` |  |
| `status` | `str` |  |
| `receipts` | `int` |  |
| `reasons` | `tuple[str, ...]` |  |
| `receipt` | `dict[str, Any] \| None` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
<!-- okf:generated:end links -->
