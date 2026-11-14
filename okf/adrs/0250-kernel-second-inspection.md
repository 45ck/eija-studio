---
type: Architecture Decision Record
title: 'ADR-0250: Who starts a record is checked like who acts, and a law never protects a state that is gone'
description: The first inspection of the kernel (ADR-0246) read each kernel function against its own ADR.
resource: repo://docs/adr/0250-kernel-second-inspection.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0250-kernel-second-inspection.md
  title: 0250-kernel-second-inspection.md
  hash_method: lf-sha256-v1
  sha256: 72b06f49a8db36d7a51e6949d1c58874e9065036f6247c1132ba500480bc761d
notes_baseline: e35f48e45f5baea4543b1e6096ef0a9ca55579a86aba68554eb46697c8e643f2
---

# ADR-0250: Who starts a record is checked like who acts, and a law never protects a state that is gone

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-14 |
| Lane | kernel (second, deeper inspection of the kernel) |
| Source | `repo://docs/adr/0250-kernel-second-inspection.md` |

## Decision outcome (verbatim)

> * **Starting a record (D1)**: `initialise(..., actor_id=...)` asks the session for the actor (`UNKNOWN_ACTOR`), refuses
>   a revoked one with `ACTOR_REVOKED`, and judges their role against the model's initiators. Simulate starts records
>   through it and logs a refused start as a `REFUSED` step with `start: true`, counted under `starts_refused`. The app
>   oracle's `create_cases` asks the kernel, and its expectations are byte-identical. `role=` stays for previews and
>   oracles that start a record on the kernel's behalf.
> * **Laws on a missing state (D2)**: a law that protects one state is broken when the model does not have that state:
>   `state_final`, `role_never_enters`, `state_only_via`, `only_kind_enters`, `path_requires` and `path_requires_kind`
>   (`laws.PROTECTING`). Its own code is reported, with refs `law:<id>` and `state:<state>`. A law that requires something
>   of a state (`action_target`, `action_source_in`, `can_reach_end`, `closed_shape`) is already stricter without it,
>   and is unchanged. The generated SMT encoding (`verification/smt/laws_gen.py`) has the same rule, and its differential
>   agrees with `check_policy` on every candidate of every shipped pack. Refusing the edits instead would leave a
>   model imported or written by hand unprotected; judging the law covers every way a state can go.
> * **Model and pack (D3)**: the runtime refuses a model whose id is not its pack's with `WORKFLOW_PACK_MISMATCH` before
>   the policy check, as every application entry point already did.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_kernel_inspection_2.py`
* `repo://verification/smt/laws_gen.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0246: The kernel refuses undeclared roles, judges path laws alike, and fails value guards closed](/adrs/0246-kernel-inspection-fixes.md) - A Fagan inspection of the kernel (inspection record) read the policy, the model contracts, the law judges, the value guards, the edit vocabulary, the impact ri…
<!-- okf:generated:end links -->
