---
type: Class
title: domain.formal.RuntimeShape
description: 'What a runtime-matrix receipt for the current subject must cover: the pack''s fixture actors and declared actions, and one of the allowed state sets (exactly the model''s states when the model is known).'
resource: repo://src/eija_studio/domain/formal.py#RuntimeShape
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#RuntimeShape
  title: domain/formal.py
  hash_method: ast-sig-v1
  sha256: fc9d2aa9cdf2f6ba11d47ba702d2938bc6d57b92267134a54038ffc58727c1a8
notes_baseline: f2f6b8b7a0cef4e5d57ea1b2bb2d2f1efadf379486c193e0f95538213911c6ee
---

# domain.formal.RuntimeShape

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `class RuntimeShape` |
| Code | `repo://src/eija_studio/domain/formal.py#RuntimeShape` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
What a runtime-matrix receipt for the current subject must cover: the pack's fixture actors and declared
actions, and one of the allowed state sets (exactly the model's states when the model is known).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `actors` | `frozenset[str]` |  |
| `actions` | `frozenset[str]` |  |
| `state_sets` | `tuple[frozenset[str], ...]` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.evidence.expected_shape](/symbols/domain/evidence/expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.evidence.runtime_shape](/symbols/domain/evidence/runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
<!-- okf:generated:end links -->
