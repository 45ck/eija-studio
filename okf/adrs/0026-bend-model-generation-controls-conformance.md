---
type: Architecture Decision Record
title: 'ADR-0026: The Bend model is generated from the Workflow; negative controls and conformance accompany every proof'
description: A proof is only as meaningful as the model it is about and the specification it proves.
resource: repo://docs/adr/0026-bend-model-generation-controls-conformance.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0026-bend-model-generation-controls-conformance.md
  title: 0026-bend-model-generation-controls-conformance.md
  hash_method: lf-sha256-v1
  sha256: 7e382a361305c4fa74a92dcb356aee3bb71bd4041d5e9ba50e3e494cb62c3a36
notes_baseline: fe98571209c7636336f770092b970d424a9aefa4f268d1e2851e18891825955d
---

# ADR-0026: The Bend model is generated from the Workflow; negative controls and conformance accompany every proof

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed (accepted when the `lane/bend` pull request merges) |
| Date | 2026-09-28 |
| Lane | bend (formal: Bend laws and proofs) |
| Source | `repo://docs/adr/0026-bend-model-generation-controls-conformance.md` |

## Decision outcome (verbatim)

> Chosen option: "generate and commit `main.bend`, with a drift check", because a committed generated file is reviewable
> in a pull request and the drift check (no Docker) makes stale models a fast-tier failure.
>
> * **Two slots.** One program holds the `Baseline` and the `Candidate` (recommend_only) workflows as `Rule` tables of
>   one shared engine (`step`, `replay`). `LAWS.bend` and `PROOF.bend` are static and independent of the table contents.
> * **The step semantics are the commit-time decision of `application/runtime.py`** (role, active, assigned, source state);
>   version CAS, operation replay and effect persistence are deliberately not modelled and are listed as not proven.
> * **Negative controls are mandatory evidence.** `bend_controls.py` generates unsafe models (the kernel's
>   `examples/unsafe-teacher-final-approval.json`, and faults against each other law, one at the engine level). The unchanged
>   proofs must fail on each, exactly the laws each was designed to break must fail (each law is checked alone by slicing the
>   two files), and a Bend-evaluated counterexample must show the property is really violated. The test suite requires every
>   law to be targeted by a control.
> * **Conformance is a differential test, and is labelled as one.** Bend's `step` is compared cell by cell with the real
>   runtime on the runtime verification matrix (225 cells) and on witness traces; the traces also show the safe path is
>   reachable, so the laws are not vacuous.
> * **Claims.** A `bend_proof` PASS requires: `main.bend` current; full `--verdict` result; per-law results; every control
>   failing as designed; conformance agreeing. The report lists what is not proven. No lane text may describe the result
>   as a proof of the Python runtime, of SQLite behaviour, or of the completeness of the laws.
> * **Laws that restate kernel policy are checked against it.** `forbidden` (law 8) and `reject_source` (law 7) are
>   hand-written in `LAWS.bend`; `bend_policy.check_laws_against_policy` fails the drift gate when they differ from

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://examples/unsafe-teacher-final-approval.json`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container](/adrs/0025-bend-machine-checked-laws.md) - The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle.
* [Formal: Bend laws and proofs](/lanes/0025-formal-bend-laws-and-proofs.md) - Capability lane with ADR numbers 0025–0026 reserved.
<!-- okf:generated:end links -->
