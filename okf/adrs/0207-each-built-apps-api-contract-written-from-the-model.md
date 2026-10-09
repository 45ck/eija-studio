---
type: Architecture Decision Record
title: 'ADR-0207: Each built app''s API contract, written from the model'
description: The System lens (ADR-0203) draws each workflow's provided interface as its actions.
resource: repo://docs/adr/0207-each-built-apps-api-contract-written-from-the-model.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0207-each-built-apps-api-contract-written-from-the-model.md
  title: 0207-each-built-apps-api-contract-written-from-the-model.md
  hash_method: lf-sha256-v1
  sha256: 5906edbc5adc2a45549c132f99e32e7f3be55c2ea81007a5a5bc3646ad9aab4e
notes_baseline: 4b84fe9e81081f1206340c28e452a795b32ee4b391b385fbc892bff4b7bc4ecd
---

# ADR-0207: Each built app's API contract, written from the model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE software architecture views (issue #144; follows ADR-0150, ADR-0203 and ADR-0206) |
| Source | `repo://docs/adr/0207-each-built-apps-api-contract-written-from-the-model.md` |

## Decision outcome (verbatim)

> Chosen option. `application.api_contract.api_contract(pack, model, data)` is pure, and `POST /api/play/api-contract` returns it for the model on screen.
>
> * The `Fields` schema says what `check_values` accepts for the record class: types, lengths, choices and required attributes, with an empty or null value counted as missing.
> * `Action` lists the model's actions, each with the roles that take it. `Actor` lists the pack's fixture directory, which the description says is not authentication.
> * The refusals are documented by the status the server sends them with: 400 for a malformed request or a field that breaks the record class, 403 for an actor who may not act, 404 for no such record, and 409 for a step the kernel refuses.
>
> The oracles are in `tests/test_api_contract.py`:
>
> * Every route the generated server answers, read from its `do_GET` and `do_POST`, is in the document, and nothing else is.
> * The 400 and 403 codes are the server's own `INVALID` and `FORBIDDEN` sets.
> * Every value Hypothesis draws from the `Fields` schema of every shipped pack passes `check_values`. Values the schema refuses are refused by `check_values` too.
> * The document validates with `openapi-spec-validator` (the `interop-api` extra). Without that extra, this check is NOT_RUN.
>
> In PlayIDE, the Deployment lens's Python process and the open workflow in the System lens offer **Download the API contract (OpenAPI 3.1)**.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_api_contract.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
* [ADR-0203: A system landscape of the workflows that share classes](/adrs/0203-system-landscape-of-workflows-that-share-classes.md) - PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.
* [ADR-0206: A deployment view read from the built app's files](/adrs/0206-a-deployment-view-read-from-the-built-apps-files.md) - PlayIDE had no deployment view.
<!-- okf:generated:end links -->
