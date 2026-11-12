---
type: Architecture Decision Record
title: 'ADR-0238: Integers in request contracts are JSON integers'
description: '`contracts/*.schema.json` declare integer fields as `"type": "integer"`.'
resource: repo://docs/adr/0238-json-integers-in-request-contracts.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0238-json-integers-in-request-contracts.md
  title: 0238-json-integers-in-request-contracts.md
  hash_method: lf-sha256-v1
  sha256: 39cafc689e4e89a9da3f288ade91c98b9d887816c507cbc4ab8c97a8087ad39b
notes_baseline: 3a298bf64cf340cd1c490113edf0ada6b9496b47256a101b36d456f64667679b
---

# ADR-0238: Integers in request contracts are JSON integers

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | kernel / contracts (issue #235) |
| Source | `repo://docs/adr/0238-json-integers-in-request-contracts.md` |

## Decision outcome (verbatim)

> `domain.models.JsonInt` is used for `LayoutChange.x`/`y`, `ExecuteCommand.expected_version`, and `ChangeCase.version`,
> `baseline_version` and `layout`. The owner-plan request's `round` and `expected_baseline_version` use it too, since
> they had the same strict-int refusal of `1.0`. The three xfails are removed, so the property test now checks the
> contracts and the models agree on every integer coercion. A fast regression test in `tests/test_hostile_input.py`
> pins the cases.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/property/test_contract_schemas.py`
* `repo://tests/test_hostile_input.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
