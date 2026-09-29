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
  sha256: d6198d74fc99204a9b537fac19455dcf141156609652726a5b223a66b34e9099
notes_baseline: 09c54346f29559e179e219706f3870a20267a8f6eb282112c0e149b556c1dc11
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

* [`application/formal`](/modules/application/formal.md)
* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/evidence`](/modules/domain/evidence.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [Assurance](/contexts/assurance.md) - Owns Subject dimensions, verification observations, admissibility and freshness
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
<!-- okf:generated:end links -->
