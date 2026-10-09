---
type: Architecture Decision Record
title: 'ADR-0221: A law that every record can still reach an end'
description: Writing the five sector packs (docs/sector-packs.md) turned up laws a real team would want and the law DSL could not say.
resource: repo://docs/adr/0221-every-record-can-reach-an-end.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0221-every-record-can-reach-an-end.md
  title: 0221-every-record-can-reach-an-end.md
  hash_method: lf-sha256-v1
  sha256: da57062ce3448a6a8ffef2895e66be6b50cb005ffc8e68ee4ad60f4dfc6a8859
notes_baseline: c5a69223cde43660109ce5581f5b767108b74965e5e09e58c80ddcbb5dc2d922
---

# ADR-0221: A law that every record can still reach an end

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE (owner ask, 9 October 2026: many tasks across sectors to refine the demo; issue #151, law kinds the sector packs could not state) |
| Source | `repo://docs/adr/0221-every-record-can-reach-an-end.md` |

## Decision outcome (verbatim)

> * **`can_reach_end`** (`states`: the ends) in `domain/laws.py`. From every state a record can get to from the initial state, some end is still reachable. A state no record can reach strands nobody, so it does not count: a new state can be drawn before its steps.
> * **Missing resolver.** Every end must be a declared state (one in the model or one a meaning adds), or the pack is refused when it loads (`laws[...]: state ... is not declared`).
> * **Policy.** `evaluate_table` reports one violation naming the law and every stuck state (`state:<id>` refs), so an edit or a chat plan that strands a state is refused and the refusal points at the states.
> * **Law proof.** Method `reach`: the breadth-first search over the kernel's configurations now records every step the kernel committed, and the law is judged on those steps. BROKEN carries the stuck states and the shortest run to the first one. A single run is never judged (`evaluate_run` skips it): the law is about the runs a record could still take.
> * **Evidence policy.** HOLDS from the proof is evidence about the model and the kernel's guards over the bounded actor classes; it says nothing about whether anyone will in fact finish a record.
> * **Example.** `packs/building-permit` law `no-application-stuck` (ends Completed, PermitRefused, Withdrawn, Lapsed). Its supported change, lapsing an issued permit, adds `Lapsed`, an end the law names, and is allowed. Its new unsupported meaning, putting an application on hold with no way back, is refused with `APPLICATION_STUCK` and `state:OnHold`.
> * **Negative oracle.** `tests/test_reach_end_law.py`: a kernel that never lets the permit manager act leaves review and information requests looping, and the proof must report `InReview`, `InfoRequested` and `Registered` stuck with the run `AcceptLodgement, StartReview`; removing both decisions from the table must be refused naming the same states.

## Sections

* Context and problem statement
* Decision drivers
* What existing tools do
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_reach_end_law.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
