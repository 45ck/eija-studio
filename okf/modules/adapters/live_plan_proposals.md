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
  sha256: f59e81100262b5b4d9765ad6584d30a9cc6257e93249fcee213d4a07dd1c7814
notes_baseline: 6e8dfa60a5cbb43c161c8d501e2ed899fd46aad5c069b67d141ceabd0a53b840
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

A request that is partly exact phrases and partly prose is refused before anything is sent: the model plans one
meaning, so the clauses the grammar read would be dropped from the plan without a word. One call runs at a time;
a second while one is in flight is refused with PROVIDER_BUSY, so a double send is never billed twice.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/plan_proposals`](/modules/adapters/plan_proposals.md)
* [`application/ports`](/modules/application/ports.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.plan_proposals](/modules/adapters/plan_proposals.md) - Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack's modelled meanings, never an LLM.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
