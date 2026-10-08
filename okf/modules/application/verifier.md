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
  sha256: 44c863ddc1da8b2964c83d7d8a2bbb9c0423d96117a65bf872a9ee8b7849ce8a
notes_baseline: c2b30b77267b938b55659a0c1e94398f328443f7bd0485ec61c9c0590ac4fe55
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

* [`verify_runtime`](/symbols/application/verifier/verify_runtime.md) (function) - no docstring

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [Assurance](/contexts/assurance.md) - Owns Subject dimensions, verification observations, admissibility and freshness
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [AC09: Authority](/requirements/ac09.md) - PASS_LOCAL: Teacher final approval is denied under every candidate path and direct API call.
* [AC12: Workflow](/requirements/ac12.md) - PARTIAL: Recommend requires Submitted; registrar Approve/Reject requires Recommended; Submit and Revise remain valid.
* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack | None=None)…` in `application/verifier`.
<!-- okf:generated:end links -->
