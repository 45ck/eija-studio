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
  sha256: 97abccd1b15543520af8f54539ecd1898fb05a0fc4f2c39d32b3448cc34380db
notes_baseline: 52637451c19f139541e22d438e479a3d5c7e4be329fddefb2bbc6c9a65a67265
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
A combined fragment. `opt` (the default): the steps happen only when `label` holds. `neg`: the steps are an
invalid trace, one that must not happen.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `label` | `str` |  |
| `steps` | `tuple[Step, ...]` |  |
| `operator` | `Literal['opt', 'neg']` | `'opt'` |
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
