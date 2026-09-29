---
type: Architecture Decision Record
title: 'ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC'
description: The v0.2 runtime matrix checks one step from each state.
resource: repo://docs/adr/0027-tla-plus-specification-and-model-checking.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0027-tla-plus-specification-and-model-checking.md
  title: 0027-tla-plus-specification-and-model-checking.md
  hash_method: lf-sha256-v1
  sha256: 4cf9cd505ecddb75d82b8437282c0b05acb5fc94cc41f6928bf444f4b5778c3c
notes_baseline: a85542c9a186457767ec1577254ea28bc28d75fe2adeab5111f0b391a71bacb8
---

# ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | tla (formal V&V, evidence kind `tlc_model_check`, see [ADR-0018](repo://docs/adr/0018-formal-vv-portfolio.md)) |
| Source | `repo://docs/adr/0027-tla-plus-specification-and-model-checking.md` |

## Decision outcome (verbatim)

> Chosen option: **TLA+ / TLC**, with these parts.
>
> * `verification/tla/Excursion.tla` is a hand-written transcription of `application/runtime.py::execute` in the runtime's own order: modelled action, directory actor, active, role, assignment (authority, now), replay lookup (binding conflict or duplicate), CAS version, state check, then one atomic step (state, version, audit, outbox, operation record). Directory changes are environment steps.
> * Everything that is data comes from the executable Python model. `verification/tla/generate.py` renders the transition table, effect classification, actor directory, forbidden effects and bounds into `verification/tla/generated/MC_*.tla|cfg`. A drift check (`nox -s tla_drift`, tier `fast`) fails when the committed files differ from a fresh generation.
> * TLC is pinned (`verification/tla/TOOLS.lock`: release, URL, sha256). Missing Java or an unfetchable jar reports `NOT_RUN`; a hash mismatch is a hard error.
> * Invariants: `TypeOK`, `NoTeacherApproval`, `ApprovalRequiresRecommendation`, `OutboxAtMostOncePerOperation`, `AtomicCommit`, `ReplayNeverBypassesCurrentAuthority`, `ForbiddenEffectsNeverEmitted`, and the action property `VersionMonotonic`.
> * Negative controls are part of the evidence: a workflow granting `Approve` to the Teacher role (which protected policy rejects), a decision order that looks up the replay before authority, a replay that re-queues its effects, and an unadapted forbidden effect that is emitted instead of rejected. Each must produce its expected TLC counterexample, which is rendered step by step.
> * The report `reports/formal/tla.json` has kind `tlc_model_check` and records TLC version, jar hash, bounds, states generated and distinct, depth, results, counterexamples and conformance statistics.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://verification/tla/generate.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
* [ADR-0028: Model-to-code conformance by exhaustive graph comparison and TLC trace validation](/adrs/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md) - A TLA+ proof about `Excursion.tla` is a proof about the model.
* [ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates](/adrs/0029-z3-policy-soundness-proof.md) - `domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner.

## Referenced by

* [ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container](/adrs/0025-bend-machine-checked-laws.md) - The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle.
* [ADR-0030: Bounded model checking by explicit-state search over the real runtime](/adrs/0030-bounded-model-checking-of-the-real-runtime.md) - The runtime matrix in `application/verifier.py` is one-step: five actors times five states times five actions, each cell from a fresh instance.
* [Formal: TLA+/TLC specification and trace conformance](/lanes/0027-formal-tla-tlc-specification-and-trace.md) - Capability lane with ADR numbers 0027–0028 reserved.
<!-- okf:generated:end links -->
