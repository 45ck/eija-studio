---
type: Module
title: interfaces.uml_interop
description: '`eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).'
resource: repo://src/eija_studio/interfaces/uml_interop.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/uml_interop.py
  title: interfaces/uml_interop.py
  hash_method: ast-api-v1
  sha256: efc77f4268b7f14512f266a4061172beeb1fed5054b6f790d2c422e182dfcddc
notes_baseline: 044b85365eef8a7af8881e11f0f641c72222875d163558e9d480e2b9c72439d7
---

# interfaces.uml_interop

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/uml_interop.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
`eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).

Export prints the file (or writes `--out`) and lists on stderr what no UML file carries. Import prints the JSON report
and, with `--out-dir`, writes the candidate `workflow.json` and `data.json` so they can go through `eija laws`,
`eija render` and `eija build`. Neither command changes a pack: keeping an import is an owner's decision.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
