---
type: Class
title: application.diagrams.Fragment
description: 'A conditional block (`opt`): the steps happen only when `label` holds.'
resource: repo://src/eija_studio/application/diagrams.py#Fragment
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#Fragment
  title: application/diagrams.py
  hash_method: ast-sig-v1
  sha256: 08bc90a3c3a0f4425636811226f232de12fe617c75d32e4206586c91dd36243d
notes_baseline: 929a0d9d92fd1b1da0f3ae6a2832e4f3551e405ca1d372e0aecaffa836fb1794
---

# application.diagrams.Fragment

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `class Fragment` |
| Code | `repo://src/eija_studio/application/diagrams.py#Fragment` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A conditional block (`opt`): the steps happen only when `label` holds.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `label` | `str` |  |
| `steps` | `tuple[Step, ...]` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Step](/symbols/application/diagrams/Step.md) - Type alias `Step` in `application/diagrams`.

## Referenced by

* [application.diagrams.Step](/symbols/application/diagrams/Step.md) - Type alias `Step` in `application/diagrams`.
<!-- okf:generated:end links -->
