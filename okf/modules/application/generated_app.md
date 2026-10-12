---
type: Module
title: application.generated_app
description: Shared generation and exact-app evidence operations for the existing kernel and checker.
resource: repo://src/eija_studio/application/generated_app.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py
  title: application/generated_app.py
  hash_method: ast-api-v1
  sha256: 7fe2ae1d2cf675c0ab3ed72d8c47586cfaaf53c2d68be5760d6cb7dc7066270b
notes_baseline: c885821461bc2cbe590f267e027a3b788e947dbbaf800b5a925ccf343c11549f
verified:
- by: process:playide-service-cohesion
  at: '2026-10-12T05:30:41Z'
  notes_sha256: 0215813655871ed10dfeac9a336755d8bf1930d2140e1de0f51c2e845e9caa8f
  sources_sha256: c885821461bc2cbe590f267e027a3b788e947dbbaf800b5a925ccf343c11549f
---

# application.generated_app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/generated_app.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Shared generation and exact-app evidence operations for the existing kernel and checker.
~~~

## Public symbols

* [`TEMPLATES`](/symbols/application/generated_app/TEMPLATES.md) (constant) - no docstring
* [`activation_association`](/symbols/application/generated_app/activation_association.md) (function) - Exact-app provenance to be committed atomically with the active model by Studio.
* [`app_build_blockers`](/symbols/application/generated_app/app_build_blockers.md) (function) - no docstring
* [`app_build_view`](/symbols/application/generated_app/app_build_view.md) (function) - Keep workflow evidence separate from generated application execution evidence.
* [`app_current`](/symbols/application/generated_app/app_current.md) (function) - Remeasure a selected application's current bytes through the existing port.
* [`assemble_app`](/symbols/application/generated_app/assemble_app.md) (function) - One generator and snapshot identity for previews and approved artifacts.
* [`bind_subject`](/symbols/application/generated_app/bind_subject.md) (function) - no docstring
* [`capture_app`](/symbols/application/generated_app/capture_app.md) (function) - Bind the checked payload to this exact selected case; persistence stays in Studio.
* [`require_app_current`](/symbols/application/generated_app/require_app_current.md) (function) - A workflow-only historical case remains unbound; a bound app must still be current.
* [`review_snapshot`](/symbols/application/generated_app/review_snapshot.md) (function) - Derive canonical contracts and the review binding through the shared pure assembler.
* [`validate_review_payload`](/symbols/application/generated_app/validate_review_payload.md) (function) - The selected payload and installed implementation must satisfy the same build-subject contract.
* [`verify_app`](/symbols/application/generated_app/verify_app.md) (function) - Seal the observed checker artifact, without approving or writing the case.

## Internal imports

* [`application/appgen`](/modules/application/appgen.md)
* [`application/build_subject`](/modules/application/build_subject.md)
* [`application/ports`](/modules/application/ports.md)
* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/evidence`](/modules/domain/evidence.md)
* [`domain/generated_app`](/modules/domain/generated_app.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/screens`](/modules/domain/screens.md)
<!-- okf:generated:end facts -->

## Notes

The assembler renders the supplied model, data, screens and static templates into one generated file inventory and build subject. `review_snapshot` obtains the pack's data and screen contracts through their existing resource loaders before calling that assembler. Binding and conformance projections use the existing typed contracts and receipt policy; a digest identifies reviewed bytes rather than proving their behavior.

`capture_app`, `app_current` and `verify_app` perform observations through the application-owned GeneratedApps port. They are not pure projections: the adapter can retain a frozen payload, remeasure bytes or run the isolated checker. `verify_app` seals the returned observation using the supplied signer, clock and ID function; failed observations remain failures under the domain evidence rules.

`require_app_current` refuses a bound app whose measurement is absent or stale. Historical workflow-only cases remain unbound. `activation_association` only constructs provenance metadata. Studio retains capability checks, source-review refusal, signed owner decisions, version/baseline checks and transactional persistence; these helpers do not approve or apply a case.

<!-- okf:generated:begin links -->
## Imports

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.build_subject](/modules/application/build_subject.md) - Exact generated-build identity.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.generated_app](/modules/domain/generated_app.md) - Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

## Referenced by

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [application.generated_app.TEMPLATES](/symbols/application/generated_app/TEMPLATES.md) - Constant `TEMPLATES` in `application/generated_app`.
* [application.generated_app.activation_association](/symbols/application/generated_app/activation_association.md) - Exact-app provenance to be committed atomically with the active model by Studio.
* [application.generated_app.app_build_blockers](/symbols/application/generated_app/app_build_blockers.md) - `def app_build_blockers(case: ChangeCase, view: dict[str, Any]) -> list[str]` in `application/generated_app`.
* [application.generated_app.app_build_view](/symbols/application/generated_app/app_build_view.md) - Keep workflow evidence separate from generated application execution evidence.
* [application.generated_app.app_current](/symbols/application/generated_app/app_current.md) - Remeasure a selected application's current bytes through the existing port.
* [application.generated_app.assemble_app](/symbols/application/generated_app/assemble_app.md) - One generator and snapshot identity for previews and approved artifacts.
* [application.generated_app.bind_subject](/symbols/application/generated_app/bind_subject.md) - `def bind_subject(subject: dict[str, Any], binding: GeneratedAppBinding | None) -> dict[str, Any]` in `application/generated_app`.
* [application.generated_app.capture_app](/symbols/application/generated_app/capture_app.md) - Bind the checked payload to this exact selected case; persistence stays in Studio.
* [application.generated_app.require_app_current](/symbols/application/generated_app/require_app_current.md) - A workflow-only historical case remains unbound; a bound app must still be current.
* [application.generated_app.review_snapshot](/symbols/application/generated_app/review_snapshot.md) - Derive canonical contracts and the review binding through the shared pure assembler.
* [application.generated_app.validate_review_payload](/symbols/application/generated_app/validate_review_payload.md) - The selected payload and installed implementation must satisfy the same build-subject contract.
* [application.generated_app.verify_app](/symbols/application/generated_app/verify_app.md) - Seal the observed checker artifact, without approving or writing the case.
<!-- okf:generated:end links -->
