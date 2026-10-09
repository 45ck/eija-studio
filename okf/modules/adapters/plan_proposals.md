---
type: Module
title: adapters.plan_proposals
description: 'Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack''s modelled meanings, never an LLM.'
resource: repo://src/eija_studio/adapters/plan_proposals.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/plan_proposals.py
  title: adapters/plan_proposals.py
  hash_method: ast-api-v1
  sha256: 1b723951afa5170129bfaff13a870aba0424f46fbea35eba449a6d7be2d06157
notes_baseline: 5ba70d6442f866c244022b0c7328fd82be7cfe004ae209ef4ea8e944923fbd58
---

# adapters.plan_proposals

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/plan_proposals.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Offline plan proposer for the PlayIDE chat (ADR-0156): a bounded phrase grammar and the pack's modelled meanings,
never an LLM. Its plans are untrusted proposals like any other; the application re-checks every step.

It also proposes follow-on edits for a ripple (ADR-0158) by fixed rules: the default screen for a new use case, no screen for a
removed one, and a transition into a state nothing reaches or out of a state left with no way out, using a declared
action the model does not use yet. These are guesses for the person to accept or reject, re-checked like any step.

A request is split into clauses ("then", ";", new lines). Each clause must be one complete phrase using exact model
names, for example "add state Archived after <state>" or "add <action> from <state> to Archived for <role>". A request
none of whose clauses match a phrase is matched against the pack's proposal rules, and a supported meaning with transactions
becomes the plan. Anything else is refused with the phrases it understands.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/plan_data_phrases`](/modules/adapters/plan_data_phrases.md)
* [`application/new_system`](/modules/application/new_system.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.plan_data_phrases](/modules/adapters/plan_data_phrases.md) - The data-model and role-kind phrases of the offline plan proposer (ADR-0202, #156): add a field to a class, remove one, make one required or optional, and say…
* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
