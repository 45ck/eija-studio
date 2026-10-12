---
type: Module
title: interfaces.http
description: Loopback-only local adapter.
resource: repo://src/eija_studio/interfaces/http.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/http.py
  title: interfaces/http.py
  hash_method: ast-api-v1
  sha256: 09b90bf6d712e70e2d64e951866282753d9ecd145bf6a521cd93a88bc25b934d
notes_baseline: cc857b45ba8503f871ecd07b40103f734eacdc34f5d79470551140d915ea002a
verified:
- by: process:playide-presentation-map
  at: '2026-10-11T09:52:45.4581269Z'
  notes_sha256: 33aaa542f287ba49fcc02372422c34f3bd1a8a219717983cd49151ee543f11db
  sources_sha256: cc857b45ba8503f871ecd07b40103f734eacdc34f5d79470551140d915ea002a
---

# interfaces.http

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/http.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Loopback-only local adapter. No public hosting, CORS, remote provider proxy or raw file endpoint.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/diagram_catalog`](/modules/application/diagram_catalog.md)
* [`application/edit_preview`](/modules/application/edit_preview.md)
* [`application/edit_proposal`](/modules/application/edit_proposal.md)
* [`application/plan`](/modules/application/plan.md)
* [`application/repository`](/modules/application/repository.md)
* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/transactions`](/modules/domain/transactions.md)
* [`interfaces/play`](/modules/interfaces/play.md)
* [`interfaces/play_systems`](/modules/interfaces/play_systems.md)
<!-- okf:generated:end facts -->

## Notes

Static workbench assets use an exact allowlist, including the presentation map's
JavaScript and stylesheet. Linking an asset from HTML does not expose it: an
unlisted filename returns a JSON 404, which the browser correctly rejects when
requested as a script or stylesheet. Keep the real file MIME types, `nosniff`
and normal page CSP; do not add a fallback or relax the security policy.

`tests/test_presentation.py::test_presentation_assets_are_real_files_with_expected_mime_and_normal_security`
checks both files' bodies and MIME types, the page policy and an unlisted backup
filename refusal. Static asset registration does not grant access to application
commands or change the session and Origin checks.

<!-- okf:generated:begin links -->
## Imports

* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.edit_preview](/modules/application/edit_preview.md) - Read-only edit projection over one captured case, using the same interpreter as owner edits.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.repository](/modules/application/repository.md) - Read-only repository evidence port; this does not grant project execution or approval.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
<!-- okf:generated:end links -->
