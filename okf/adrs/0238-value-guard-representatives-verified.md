---
type: Architecture Decision Record
title: 'ADR-0238: Verify value-guard representatives by property and mutation, and fix what that found'
description: ADR-0231 to ADR-0235 added initiators, one action from several states, separation of duties, guards over record values and built associations.
resource: repo://docs/adr/0238-value-guard-representatives-verified.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0238-value-guard-representatives-verified.md
  title: 0238-value-guard-representatives-verified.md
  hash_method: lf-sha256-v1
  sha256: a0a935b86e2c789cb1c5672b4312d4119dbf5a7cb72ccbc220cf1e042d66b0cc
notes_baseline: 4821712174f927239c5784e86ada666303833b927a4c72c3e6c94bf8c0fc3e8a
---

# ADR-0238: Verify value-guard representatives by property and mutation, and fix what that found

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | kernel / verification (issue #221) |
| Source | `repo://docs/adr/0238-value-guard-representatives-verified.md` |

## Decision outcome (verbatim)

> **Property tests.** `tests/property/test_value_guards.py` states the claim for numbers (including integers beyond the float range and floats beyond 2**53), dates, text and true/false; that guards fail closed on missing, mistyped and non-finite values; that `combinations` is the full product or refuses; that siblings of one action share guards by literal; that the ripple reports a guard change exactly when the guards differ; and that `separation_breach` agrees with a naive reading of ADR-0233. The workflow generators now produce value guards and initiators, and the semantic-hash normal form and edits cover them.
>
> **What they found, and the fixes.** Each has a fast-tier regression test in `tests/test_value_guard_edges.py`.
>
> 1. *Representatives collapsed at large constants.* For floats from 2**53 up, `c - 1 == c`, so the "below" point was the constant itself: no representative made `amount ≠ 9007199254740996.0` or `amount < c` true. `_numbers` now takes the first of `c ± 1`, the next float, or the next whole number that lies strictly on the right side.
> 2. *Overflow.* Two integer constants beyond the float range made `(a + b) / 2` raise `OverflowError`, crashing the law proof. `_between` now tries the midpoint, `a/2 + b/2`, the next float above `a` and the next whole number, skipping any that overflow, and invents no point between two adjacent floats.
> 3. *NaN and infinity.* `json.loads` accepts `NaN` and `Infinity`, and `check_values` accepted them as numbers. NaN satisfied every `≠` guard, a pattern no representative has. Records now refuse non-finite numbers (`FIELD_TYPE`), and a guard over one fails closed.
> 4. *`true` equalled `1`.* Pydantic equality compares `True == 1`, so `[paid = true]` and `[paid = 1]` were one guard: two transitions of one action with those guards passed the ADR-0232 shape rule though no value satisfies both, the pair was refused as a duplicate on one transition, and the ripple saw no change between them. Guards are now compared by their JSON (`models.guard_keys`), as the semantic hash already did.
> 5. *Duplicate forbidden effects* (a strict xfail since ADR-0031's deep profile): `['X', 'X']` and `['X']` meant the same but hashed differently. The contract now refuses the duplicate, as it does a duplicate required effect.
>
> The property run also showed `test_mutations_are_refused_by_both_or_neither[workflow]` never saw an accepted near-miss once value guards were in the schema; its repair step now keeps only guards the contract accepts.
>
> **Mutation.** `domain/value_guards.py` and `domain/laws.py` are mutation targets with floors in `quality/mutation/baseline.json`. First run: 432 mutants, 0 survivors (2 timeouts, counted as detected).
>
> The same run showed the full-tier `mutation_quick` gate was red on main: three mutants of the ADR-0231 check `UNDECLARED_INITIATOR:<role>` in `policy.declared_codes` survived, because only `tests/test_initiators.py` asserted it and that file is not in the policy target's selection. `tests/test_policy_authority.py` now asserts the exact codes for declared and undeclared initiators; `policy.py` is back to 132 of 132 killed. All three floors were taken in one Linux run, so the baseline's platform is now Linux (CPython 3.13); the previous floor came from Windows.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://quality/mutation/baseline.json`
* `repo://tests/property/test_value_guards.py`
* `repo://tests/test_initiators.py`
* `repo://tests/test_policy_authority.py`
* `repo://tests/test_value_guard_edges.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0031: Property-based testing with Hypothesis, in two profiles](/adrs/0031-property-based-testing-with-hypothesis.md) - The kernel's guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to…
* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…
* [ADR-0034: What is mutated, how a score is defined, and the ratchet](/adrs/0034-mutation-measurement-and-ratchet.md) - ADR-0033 picks the engine.
* [ADR-0231: Who may start a record](/adrs/0231-who-may-start-a-record.md) - Issue #142: a workflow said who may take each transition, but not who may start a record.
* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
* [ADR-0233: Separation of duties](/adrs/0233-separation-of-duties.md) - Issue #149.
* [ADR-0235: Built associations as checked reference fields](/adrs/0235-built-associations.md) - Issue #145, step 2.
<!-- okf:generated:end links -->
