---
type: Class
title: application.diagrams.Fragment
description: A combined fragment.
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
  sha256: c5356556d6e9dd672cc382ab597d2a78addbc5bb642f735c5191567718e1beaf
notes_baseline: bcdac63c7fe57cee6c2719d6bf29189793cbf12163ac7cd0b41edfb366f32bb4
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
A combined fragment. `opt` (the default): the steps happen only when `label` holds. `alt`: the steps under
`label`, else each of `alternatives` (label, steps). `neg`: the steps are an invalid trace.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `label` | `str` |  |
| `steps` | `tuple[Step, ...]` |  |
| `operator` | `Literal['opt', 'alt', 'neg']` | `'opt'` |
| `alternatives` | `tuple[tuple[str, tuple[Step, ...]], ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Step](/symbols/application/diagrams/Step.md) - Type alias `Step` in `application/diagrams`.

## Referenced by

* [application.diagrams.Step](/symbols/application/diagrams/Step.md) - Type alias `Step` in `application/diagrams`.
* [application.sequence_layout.export](/symbols/application/sequence_layout/export.md) - The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt).
<!-- okf:generated:end links -->
