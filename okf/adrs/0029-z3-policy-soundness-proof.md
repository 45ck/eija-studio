---
type: Architecture Decision Record
title: 'ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates'
description: '`domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner.'
resource: repo://docs/adr/0029-z3-policy-soundness-proof.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0029-z3-policy-soundness-proof.md
  title: 0029-z3-policy-soundness-proof.md
  hash_method: lf-sha256-v1
  sha256: ee8559abfabb1c39576596417ec7cb731f1d42686778a9781f7c0106645c6a0e
notes_baseline: 8cafdab5e3a53329beb2d7a3e0cba638a8cd081662ff4fad323f57e2a7f7d9de
---

# ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-28 |
| Lane | smt-bmc (formal: Z3 policy soundness) |
| Source | `repo://docs/adr/0029-z3-policy-soundness-proof.md` |

## Decision outcome (verbatim)

> Chosen option: "Z3 with a hand-written encoding in `verification/smt/`", because it is the mature, MIT-licensed solver, it decides this finite problem in milliseconds, and the encoding stays small enough to review next to `policy.py`.
>
> * **Grammar.** One slot per known action (unique actions, as `Workflow.coherent` guarantees), each with role, from, to, six guard literals, eight known effect atoms plus one "any other required effect" flag, and forbidden-effect literals. Roles, states and effects outside the known vocabulary are one `OTHER` value each. No `Transition` validator is assumed, so the policy alone must enforce guards and effect exclusion.
> * **Encoding.** `check_policy` becomes 105 named clauses, each producing one error code.
> * **Theorem.** For every candidate, the encoded policy admitting `c` implies each of fifteen independently reported invariants (`INV-TEACHER-NOT-DECIDER`, `INV-APPROVE-REQUIRES-RECOMMENDED`, `INV-RECOMMEND-REQUIRES-ASSIGNMENT`, `INV-FORBIDDEN-EFFECTS-EXCLUDED`, `INV-MANDATORY-GUARDS-PRESENT`, and others). Each is an UNSAT query on `canonical AND admits AND NOT invariant`. The requirement's constants (forbidden effects, base guards, decision audit kinds) are literals typed from the documentation, not imported from the kernel; the encoded policy imports them. Weakening the kernel constant therefore refutes an invariant instead of weakening the requirement with it.
> * **Complete characterisation.** All-SAT enumeration of the admitted set returns exactly baseline plus the recommendation candidate with rejection source Recommended or Submitted, which equals the set `apply_transaction` can produce. The result is committed as `verification/smt/accepted_set.json` with a drift check. The snapshot embeds semantic digests (parsed program, without formatting, comments, docstrings and, only in a module with `from __future__ import annotations`, annotations; every import, alias included, stays in the digest, because an alias can rebind a builtin) of `policy.py` and `models.py`, not raw byte hashes, so a reformat does not fail the gate and a change to the executable structure does. A first version dropped `typing` imports and all policy annotations and let a two-line backdoor through (independent review of PR #25); tests now plant an import alias and an evaluated annotation.
> * **Faithfulness (sampled, not proved).** A deterministic differential test compares the encoding with the real function on every one-field mutation of the three accepted workflows and on seeded random candidates, including candidates that bypass pydantic validators and foreign strings. It compares the exact sorted error list, not only accepted or rejected, and requires every clause to have fired and to have stayed silent at least once. The differential test is itself tested: dropping a clause from the encoding must produce disagreements, and so must weakening the real policy.
> * **Negative controls.** For every clause the encoding is re-solved without it; 66 of the 105 clauses are critical to the invariant set and each yields a counterexample that the real `check_policy` rejects citing the deleted clause's code. Only 30 of the 66 stay critical if the pydantic validators are assumed; the other 36 have witnesses that only `model_construct` can build (the policy is the sole defence there, which is why no validator is assumed). The 39 clauses not needed by the invariants (required-effect exactness, the Submit and Revise role and source, and others) are listed, not hidden.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://verification/smt/accepted_set.json`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.

## Referenced by

* [ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container](/adrs/0025-bend-machine-checked-laws.md) - The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle.
* [ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC](/adrs/0027-tla-plus-specification-and-model-checking.md) - The v0.2 runtime matrix checks one step from each state.
* [ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts](/adrs/0145-per-kind-evidence-admissibility.md) - `domain.evidence.assess_receipt` recomputes admissibility for one claim only: the runtime matrix (`runtime_matrix` / `integration_test`).
* [Formal: Z3 policy soundness and bounded model checking](/lanes/0029-formal-z3-policy-soundness-and-bounded.md) - Capability lane with ADR numbers 0029–0030 reserved.
<!-- okf:generated:end links -->
