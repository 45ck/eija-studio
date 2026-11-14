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
  sha256: 0aae38c1b576a68e4195802c88e080bdec2ac54f2ae251ebe346eb11ad82015e
notes_baseline: 12ba2eb5fdc634718d07e645db2e96457f586a644794e58310e41d908a502b33
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
* Amendment, 13 November 2026: the built app reads them too

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/quality/inspection-2026-11-13-merged-prs.md`
* `repo://tests/property/test_contract_schemas.py`
* `repo://tests/test_hostile_input.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
