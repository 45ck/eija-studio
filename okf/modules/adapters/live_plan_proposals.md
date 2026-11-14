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
  sha256: 2858a0c03cfdb74be62f253ae147d76d6d3e8f36f5461b7eda6d04b9afa8e9a1
notes_baseline: b9d603864c4ef618facc1c81ad0c6c49587f3f8c3735f718b9d9828eb303b44a
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
A request shaped like an exact phrase but naming something the model lacks ("add state X after Nowhere") gets the
phrase reader's answer and is not sent: the model would read it as some meaning and plan that instead.
Every call that leaves the machine is written to the audit log, as `Studio.propose` writes its own: started, then
received or not accepted, with a hash of the request and never the request itself.
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
