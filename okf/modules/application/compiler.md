---
type: Module
title: application.compiler
description: 'Compiler: model → projections + impacts + obligations + computed review packet.'
resource: repo://src/eija_studio/application/compiler.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/compiler.py
  title: application/compiler.py
  hash_method: ast-api-v1
  sha256: 6cd8935598852df04d62177fc03d8cfe0b0c91bcbeec0b9b6d4ed06e81159292
notes_baseline: 22552f5c45023fdbcebb032bab9d18195903360b86ce46990567730134511142
---

# application.compiler

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/compiler.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Compiler: model → projections + impacts + obligations + computed review packet.

This is a bounded semantic/report compiler, not a general source-code compiler.
~~~

## Public symbols

* [`compile_case`](/symbols/application/compiler/compile_case.md) (function) - no docstring
* [`subject_for`](/symbols/application/compiler/subject_for.md) (function) - no docstring

## Internal imports

* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/evidence`](/modules/domain/evidence.md)
* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Protected excursion policy.

## Referenced by

* [Assurance](/contexts/assurance.md) - Owns Subject dimensions, verification observations, admissibility and freshness
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo…` in `application/compiler`.
* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict, identity: dict) -> dict` in `application/compiler`.
<!-- okf:generated:end links -->
