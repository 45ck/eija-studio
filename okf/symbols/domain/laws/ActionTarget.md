---
type: Class
title: domain.laws.ActionTarget
description: Every transition performing ``action`` ends in ``state``.
resource: repo://src/eija_studio/domain/laws.py#ActionTarget
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#ActionTarget
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 1da4d1048a12c39d869a6578e46317ab6a57514697ef9e41f70f551b544e77e8
notes_baseline: 4f3971827981e732337440cb5bb819e73c6325db747bb3a8b523f35509ef28e5
---

# domain.laws.ActionTarget

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class ActionTarget(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#ActionTarget` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every transition performing ``action`` ends in ``state``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['action_target']` |  |
| `action` | `Name` |  |
| `state` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
<!-- okf:generated:end links -->
