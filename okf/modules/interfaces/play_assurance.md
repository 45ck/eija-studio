---
type: Module
title: interfaces.play_assurance
description: Read-only assurance review.
resource: repo://src/eija_studio/interfaces/play_assurance.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/play_assurance.py
  title: interfaces/play_assurance.py
  hash_method: ast-api-v1
  sha256: 0340cfc17e06e7cbc5061c6211c4dc46761bcfa225ee0839fa634840eb9472f7
notes_baseline: 58811c20c260233184c34a58f4426e4049cc6031c5e821c9560c65df7b90285c
---

# interfaces.play_assurance

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/play_assurance.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Read-only assurance review. Draft prose and laws never gain application authority.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/capabilities`](/modules/application/capabilities.md)
* [`application/law_proof`](/modules/application/law_proof.md)
* [`application/plan`](/modules/application/plan.md)
* [`application/requirement_trace`](/modules/application/requirement_trace.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.capabilities](/modules/application/capabilities.md) - Explicit support levels for the workbench; design visibility is not execution.
* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.requirement_trace](/modules/application/requirement_trace.md) - A bounded declared trace adapter, separate from policy and verification execution.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
<!-- okf:generated:end links -->
