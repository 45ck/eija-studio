---
type: Class
title: application.ports.SystemDescriber
description: Turns a description of an app into {name, record, sketch, fields, reading} for "Describe your app" (ADR-0216).
resource: repo://src/eija_studio/application/ports.py#SystemDescriber
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#SystemDescriber
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: 9e516f7eeedd383fe2568f881bd1c681d5897b03cd3d82fea55b1b342ddd6e52
notes_baseline: a57fcaf5f63feae0f2fda02e460062b501d401cdbe93471f857b4c4dff42142e
---

# application.ports.SystemDescriber

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class SystemDescriber(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#SystemDescriber` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Turns a description of an app into {name, record, sketch, fields, reading} for "Describe your app" (ADR-0216).
Untrusted; no IO or persistence. `sketch` is in the state machine's label notation, `fields` are data-model
attributes, and `reading` says in words what was read and assumed.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` |  |
| `live` | `bool` |  |

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def describe(self, text: str) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.describe_system.describe_documents](/symbols/application/describe_system/describe_documents.md) - The documents of a new system described in `text`, checked by the kernel, and what the describer read.
<!-- okf:generated:end links -->
