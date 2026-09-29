---
type: Architecture Decision Record
title: 'ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts'
description: '`domain.evidence.assess_receipt` recomputes admissibility for one claim only: the runtime matrix (`runtime_matrix` / `integration_test`).'
resource: repo://docs/adr/0145-per-kind-evidence-admissibility.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0145-per-kind-evidence-admissibility.md
  title: 0145-per-kind-evidence-admissibility.md
  hash_method: lf-sha256-v1
  sha256: 9ad3615905ebdde3a2101ee51e130171f670ec5d1016e8c253d98125da457f5d
notes_baseline: a2ad8fe7f611e22cf46dfbfd3ceacf7a226626b7208fbdd72048d2a71f31b3c0
---

# ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed (accepted when the `lane/evidence-kinds` pull request merges) |
| Date | 2026-09-29 |
| Lane | evidence-kinds (POC criteria 4 and 5) |
| Source | `repo://docs/adr/0145-per-kind-evidence-admissibility.md` |

## Decision outcome (verbatim)

> Chosen option: "recompute from raw typed artifacts, per kind", with these rules.
>
> 1. **A kind is a registered `KindSpec`** (`domain/evidence_kinds.py`): claim, method, protocol version, evidence level, what it
>    establishes, what it does NOT establish, prerequisites, a pure `check(artifact, context) -> Assessment`, a `describe` for the
>    packet and an `explain` for policy blocks. A kind that is not registered is `UNKNOWN` by construction. The runtime matrix path
>    is unchanged (`assess_receipt` keeps its behaviour for `runtime_matrix` / `integration_test`).
> 2. **The envelope is checked in the runtime matrix's order** (claim and kind, subject dimensions, artifact hash, producer, method,
>    protocol) so a stale or tampered receipt is judged the same way for every kind. A hash mismatch or a malformed artifact is
>    `FAIL`; an unknown producer or protocol version is `UNKNOWN`; a receipt for another subject is `STALE`.
> 3. **Statuses** are the existing algebra `PASS / FAIL / STALE / UNKNOWN / CONFLICT` plus a distinct **`NOT_RUN`** for a missing
>    prerequisite (Docker, Java, z3, a saved run). Combination: authenticated PASS and FAIL never average (`CONFLICT`); FAIL beats
>    everything but CONFLICT; PASS beats STALE, NOT_RUN and UNKNOWN; then STALE, NOT_RUN, UNKNOWN. No receipt at all is `UNKNOWN`
>    ("no receipt attached"), so absence is visible.
> 4. **Within a kind, findings have a severity:** STALE (about another subject), then FAIL (a counterexample, a contradiction, a
>    control that did not fail, a structural defect), then UNKNOWN (evidence missing, incomplete, below a declared minimum bound, an
>    unaccepted tool version). Only PASS when there is no finding. Each finding is a text reason shown in the packet.
> 5. **The tool's own labels can only lower.** A `FAIL`, `PARTIAL`, `INCONCLUSIVE` or failed tool check reported by the tool caps the
>    status; a `PASS` label is ignored (the kernel recomputes).
> 6. **Negative controls are pinned by the kernel**, not read from the artifact: the kernel knows which seeded faults each proof
>    must reject and which laws each must break. A missing control is `UNKNOWN`; a control the proof did not reject, or that broke

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

* [ADR-0000: v0.2 proof-of-concept decision log (ADR-001 … ADR-014)](/adrs/0000-poc-decision-log.md) - These fourteen decisions shipped with EIJA Studio 0.2.0 and are kept verbatim as one log.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
* [ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container](/adrs/0025-bend-machine-checked-laws.md) - The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle.
* [ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates](/adrs/0029-z3-policy-soundness-proof.md) - `domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner.
* [ADR-0030: Bounded model checking by explicit-state search over the real runtime](/adrs/0030-bounded-model-checking-of-the-real-runtime.md) - The runtime matrix in `application/verifier.py` is one-step: five actors times five states times five actions, each cell from a fresh instance.

## Referenced by

* [ADR-0146: Formal receipt formats, binding to the subject, and NOT_RUN semantics](/adrs/0146-formal-receipt-formats-binding-and-not-run.md) - ADR-0145 decides that the kernel recomputes formal evidence per kind.
<!-- okf:generated:end links -->
