---
type: Module
title: application.verifier
description: Bounded synthetic runtime experiments.
resource: repo://src/eija_studio/application/verifier.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/verifier.py
  title: application/verifier.py
  hash_method: ast-api-v1
  sha256: 0a4795050927ac3abc66a911ca8c70fc6d812cb41d5bc8f6c056020620661efa
---

# application.verifier

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/verifier.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Bounded synthetic runtime experiments. Not a theorem prover or human study.
~~~

## Public symbols

* [`ACTORS`](/symbols/application/verifier/ACTORS.md) (constant) - no docstring
* [`ORACLE`](/symbols/application/verifier/ORACLE.md) (constant) - no docstring
* [`verify_runtime`](/symbols/application/verifier/verify_runtime.md) (function) - no docstring

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; domain-specific policy stays in domain.policy.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [Assurance](/contexts/assurance.md) - Owns Subject dimensions, verification observations, admissibility and freshness
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [AC09: Authority](/requirements/ac09.md) - Teacher final approval is denied under every candidate path and direct API call.
* [AC12: Workflow](/requirements/ac12.md) - Recommend requires Submitted; registrar Approve/Reject requires Recommended; Submit and Revise remain valid.
* [application.verifier.ACTORS](/symbols/application/verifier/ACTORS.md) - `ACTORS = [('teacher-assigned', 'Teacher', True, True), ('teacher-unassigned', 'Teacher', True, False), ('teacher-revoked', 'Teacher', False, True), (…` in `ap…
* [application.verifier.ORACLE](/symbols/application/verifier/ORACLE.md) - `ORACLE = {'Submit': ('Teacher', 'Draft', 'Submitted'), 'Recommend': ('Teacher', 'Submitted', 'Recommended'), 'Approve': ('Registrar', 'Recommended',…` in `app…
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
<!-- okf:generated:end links -->
