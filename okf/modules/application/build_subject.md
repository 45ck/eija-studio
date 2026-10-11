---
type: Module
title: application.build_subject
description: Exact generated-build identity.
resource: repo://src/eija_studio/application/build_subject.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/build_subject.py
  title: application/build_subject.py
  hash_method: ast-api-v1
  sha256: cd82f3ab2470c8debebec31b784cbfd92ee91673a0a7dc9126d0a5a038176707
notes_baseline: c61b8a54db5588550352daf2914c85d1129af86a2cd18b155414733f39b6658d
---

# application.build_subject

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/build_subject.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Exact generated-build identity. Hashes bind content; they grant no approval.

The generated subject file is a provenance envelope, excluded from its own
payload hash. All executable files and model contracts remain in that hash.
This module reads only the supplied snapshot, never files beside a pack.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/build_subject/FORMAT.md) (constant) - no docstring
* [`SUBJECT_FILE`](/symbols/application/build_subject/SUBJECT_FILE.md) (constant) - no docstring
* [`build_subject`](/symbols/application/build_subject/build_subject.md) (function) - Bind model, contracts, template bytes and measured implementation to one payload.
* [`checked_build_subject`](/symbols/application/build_subject/checked_build_subject.md) (function) - Check archived identity, optionally binding it to the installed runtime and prior snapshot.
* [`snapshot_contracts`](/symbols/application/build_subject/snapshot_contracts.md) (function) - Parse the very contracts the generated application will load.

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

* [application.c4](/modules/application/c4.md) - Read-only C4 views of generated source and declared model contracts.
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [application.build_subject.FORMAT](/symbols/application/build_subject/FORMAT.md) - Constant `FORMAT` in `application/build_subject`.
* [application.build_subject.SUBJECT_FILE](/symbols/application/build_subject/SUBJECT_FILE.md) - Constant `SUBJECT_FILE` in `application/build_subject`.
* [application.build_subject.build_subject](/symbols/application/build_subject/build_subject.md) - Bind model, contracts, template bytes and measured implementation to one payload.
* [application.build_subject.checked_build_subject](/symbols/application/build_subject/checked_build_subject.md) - Check archived identity, optionally binding it to the installed runtime and prior snapshot.
* [application.build_subject.snapshot_contracts](/symbols/application/build_subject/snapshot_contracts.md) - Parse the very contracts the generated application will load.
<!-- okf:generated:end links -->
