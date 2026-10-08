---
type: Function
title: application.scxml.scxml_id
description: An XML/SCXML-safe id for a state or event name.
resource: repo://src/eija_studio/application/scxml.py#scxml_id
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scxml.py#scxml_id
  title: application/scxml.py
  hash_method: ast-v2
  sha256: 2b3656a17e288687d85fcfdcbffac216f43d93eae1934cc7af7b80ea160e18a0
notes_baseline: 2ec261d584b9ed7697214401a677efa12bb7b272d5fc7b0d876e122f0ac815c6
---

# application.scxml.scxml_id

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def scxml_id(name: str) -> str` |
| Code | `repo://src/eija_studio/application/scxml.py#scxml_id` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
An XML/SCXML-safe id for a state or event name. Plain names are kept; any other name becomes `_` and its UTF-8
bytes in hex. A plain name never starts with `_`, so the mapping is one-to-one.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.scxml.to_scxml](/symbols/application/scxml/to_scxml.md) - The model as an SCXML document.
<!-- okf:generated:end links -->
