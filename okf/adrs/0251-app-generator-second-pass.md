---
type: Architecture Decision Record
title: 'ADR-0251: One status table, retryable creates and bounded requests in the generated app'
description: The second inspection of the app generator (record) found that the API contract and the server kept the status of each refusal in two copies that had drifted, that the signals route was missing from the contract, that a…
resource: repo://docs/adr/0251-app-generator-second-pass.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0251-app-generator-second-pass.md
  title: 0251-app-generator-second-pass.md
  hash_method: lf-sha256-v1
  sha256: cc4d2ae6794da43807b759811d04f7579c44826a02d682b4b4e425e27f862724
notes_baseline: 7b20794ec2499e75885fd420872e60b126375c04409845605af5fed47ed689ce
---

# ADR-0251: One status table, retryable creates and bounded requests in the generated app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-14 |
| Lane | app generator (ADR-0150, ADR-0207, ADR-0249) |
| Source | `repo://docs/adr/0251-app-generator-second-pass.md` |

## Decision outcome (verbatim)

> Chosen option: one table. `app_http.REFUSALS` maps each status to its codes, `status_of(code)` answers it, and every code the kernel, the data checks and the app can raise must be in it (a test reads them from the sources). `ROLE_CANNOT_START` and `SEPARATION_DENIED` move from 409 to 403: both are about who is acting. A new `REQUEST_TIMEOUT` (408) answers a request whose body does not arrive within 30 seconds.
>
> Creating a record or a stored object takes an optional `operation_id`. It is bound to the whole request (title, actor, fields, or class, actor, fields), as the kernel binds an action: the same request again returns the first result with status 200 and `duplicate: true`; the id with anything else is `OPERATION_CONFLICT`. An act still requires its id, and the contract now says so. The page sends one id per draft and drops it when the draft or the actor changes.
>
> Values, references and the data digest are checked inside the write. The record list is one query; the model hash is computed once; the audit has an index on the record it belongs to.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
* [ADR-0207: Each built app's API contract, written from the model](/adrs/0207-each-built-apps-api-contract-written-from-the-model.md) - The System lens (ADR-0203) draws each workflow's provided interface as its actions.
* [ADR-0249: Fixes from the inspection of the app generator](/adrs/0249-app-generator-inspection-fixes.md) - The 13 November 2026 inspection (record) found ten defects in the generated app and its conformance suite.
<!-- okf:generated:end links -->
