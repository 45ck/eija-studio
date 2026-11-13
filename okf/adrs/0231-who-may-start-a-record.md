---
type: Architecture Decision Record
title: 'ADR-0231: Who may start a record'
description: 'Issue #142: a workflow said who may take each transition, but not who may start a record.'
resource: repo://docs/adr/0231-who-may-start-a-record.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0231-who-may-start-a-record.md
  title: 0231-who-may-start-a-record.md
  hash_method: lf-sha256-v1
  sha256: 452cae68f005cd74a962f174e530c8f596f4e189b9568bcfa9bffb74d8a7f7f7
notes_baseline: c81ce5701318b737ee63e73e3663dafdfdad210ae8b3bad6d19372ce8509482b
---

# ADR-0231: Who may start a record

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | kernel / generated apps / PlayIDE |
| Source | `repo://docs/adr/0231-who-may-start-a-record.md` |

## Decision outcome (verbatim)

> `Workflow.initiators` is a tuple of role names, empty by default, at most 16, no duplicates. Empty means today's meaning, any active actor, and the key is left out of the serialised model so every existing hash is unchanged. When it names roles:
>
> * `runtime.initialise(..., role=)` refuses any other creator with `ROLE_CANNOT_START` (refs `role:<name>`) and writes nothing. Without a role (previews, the access matrix, the oracle starting records on the kernel's behalf) there is no check.
> * The policy adds `UNDECLARED_INITIATOR:<role>` for a role the pack does not declare.
> * The generated app's `create` passes the actor's role. The oracle gains `start_cases` (one per active fixture actor) only when initiators are named, and the generated conformance test `test_only_the_named_roles_start_records` checks them.
> * The seeded simulation lets only initiators start records; others act on existing ones.
> * Every generated app now has seven conformance tests, not six; the receipt check (`GENERATED_TESTS`) expects seven, so an app built from an older template reads as FAIL and must be rebuilt.
> * PlayIDE's permissions panel, flow card and use case diagram show who may start a record; the diagram associates each initiator with "Create".

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* Amendment, 13 November 2026: UML exports say initiators are not carried

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/quality/inspection-2026-11-13-merged-prs.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0239: Verify value-guard representatives by property and mutation, and fix what that found](/adrs/0239-value-guard-representatives-verified.md) - ADR-0231 to ADR-0235 added initiators, one action from several states, separation of duties, guards over record values and built associations.
<!-- okf:generated:end links -->
