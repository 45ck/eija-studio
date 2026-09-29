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
  sha256: 7dc6c55b926374bcfbcdadeef6165b6007df6ffecac6fe85cad3dc14612b8814
notes_baseline: 0ba6d75484559503a4e62cfda9a1e64b7782a8ef3c1279bf64103f30c26b092c
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
* [AC09: Authority](/requirements/ac09.md) - PASS_LOCAL: Teacher final approval is denied under every candidate path and direct API call.
* [AC12: Workflow](/requirements/ac12.md) - PARTIAL: Recommend requires Submitted; registrar Approve/Reject requires Recommended; Submit and Revise remain valid.
* [application.verifier.ACTORS](/symbols/application/verifier/ACTORS.md) - Constant `ACTORS` in `application/verifier`.
* [application.verifier.ORACLE](/symbols/application/verifier/ORACLE.md) - Constant `ORACLE` in `application/verifier`.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory) -> dict[str, Any]` in `application/verifier`.
<!-- okf:generated:end links -->
