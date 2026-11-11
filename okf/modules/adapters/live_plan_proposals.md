---
type: Module
title: adapters.live_plan_proposals
description: 'Live plan proposer for the PlayIDE chat (ADR-0230): a model reads the request, the pack decides the steps.'
resource: repo://src/eija_studio/adapters/live_plan_proposals.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/live_plan_proposals.py
  title: adapters/live_plan_proposals.py
  hash_method: ast-api-v1
  sha256: fd37aa7c9d7c10f70c68f64bc01ed39891098855d43e0d974fdd1fb07bdcab34
notes_baseline: f1aa754efe97327d5650a3f32a9995cfe8c41bc90c0dbc39357a6ba326197139
---

# adapters.live_plan_proposals

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/live_plan_proposals.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Live plan proposer for the PlayIDE chat (ADR-0230): a model reads the request, the pack decides the steps.

Opt-in only. The offline proposer stays the default; this one is used for a request only when the Studio was
started with a networked provider and ``--allow-network``, and the person ticked consent for that request.

The model never writes steps. Exact phrases ("add state X after Y") are still read by the offline grammar, so a
precise request costs nothing and never leaves the machine. Anything else goes to the provider, whose first
alternative must be one of the pack's meanings; that meaning's own transactions become the plan, and the kernel
then checks it like any other. An unsafe meaning is planned as asked and refused by its law (issue #152), never
swapped for a safe one. A meaning with nothing to plan is refused with the model's explanation.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/ports`](/modules/application/ports.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
