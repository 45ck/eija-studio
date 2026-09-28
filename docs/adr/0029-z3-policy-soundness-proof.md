# ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates

* Status: proposed
* Date: 2026-09-28
* Lane: smt-bmc (formal: Z3 policy soundness)

## Context and problem statement

`domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner. The v0.2 evidence for it is example-based: protected-policy mutation tests and a five-actor by five-state by five-action matrix. Neither shows that **no** candidate in the Transition grammar can slip through with a Teacher holding Approve, an Approve that skips Recommended, a Recommend without the assignment guard, a forbidden effect or a missing mandatory guard. ADR-0018 reserves an `smt_proof` evidence kind for exactly this claim.

## Decision drivers

* The claim must quantify over the whole grammar, not over sampled candidates.
* The proof must be about the policy that actually runs, so the encoding needs a faithfulness check against the real function.
* The requirement (AuthorityInvariant) must be stated separately from the code it judges, or the proof is a tautology.
* A proof that cannot fail proves nothing: negative controls must show that removing a policy clause yields a counterexample.
* OSS first (ADR-0016); the policy stays hand-written and reviewable.

## Considered options

* **Z3 (z3-solver, MIT) over a hand-written encoding, plus a differential faithfulness test** (chosen).
* CrossHair (symbolic execution of the Python function, Z3 backend): would remove the hand-written encoding. Spiked on 2026-09-29 (`crosshair-tool==0.0.111`, Python 3.12, 40 s per condition, a scratch check not committed): asked to confirm "no candidate the policy admits has a Teacher-held Approve" it answered `Not confirmed`, and asked to confirm the deliberately false "every candidate is rejected" it also answered `Not confirmed`, i.e. it could not construct even one admitted `Workflow` (validation runs in pydantic-core, which it cannot execute symbolically). That is a short, time-boxed spike of one configuration, not a proof that CrossHair cannot work with a hand-written strategy or a different timeout; it is evidence only that the out-of-the-box route is not usable now. Kept as a follow-up second route.
* CVC5 / Yices: equivalent for this finite problem; no reason to add a second solver until an independent proof check is wanted (the encoding can be exported as SMT-LIB).
* Exhaustive enumeration in plain Python: the grammar has well over 2^100 candidates, so it does not terminate.

## Decision outcome

Chosen option: "Z3 with a hand-written encoding in `verification/smt/`", because it is the mature, MIT-licensed solver, it decides this finite problem in milliseconds, and the encoding stays small enough to review next to `policy.py`.

* **Grammar.** One slot per known action (unique actions, as `Workflow.coherent` guarantees), each with role, from, to, six guard literals, eight known effect atoms plus one "any other required effect" flag, and forbidden-effect literals. Roles, states and effects outside the known vocabulary are one `OTHER` value each. No `Transition` validator is assumed, so the policy alone must enforce guards and effect exclusion.
* **Encoding.** `check_policy` becomes 105 named clauses, each producing one error code.
* **Theorem.** For every candidate, the encoded policy admitting `c` implies each of fifteen independently reported invariants (`INV-TEACHER-NOT-DECIDER`, `INV-APPROVE-REQUIRES-RECOMMENDED`, `INV-RECOMMEND-REQUIRES-ASSIGNMENT`, `INV-FORBIDDEN-EFFECTS-EXCLUDED`, `INV-MANDATORY-GUARDS-PRESENT`, and others). Each is an UNSAT query on `canonical AND admits AND NOT invariant`. The requirement's constants (forbidden effects, base guards, decision audit kinds) are literals typed from the documentation, not imported from the kernel; the encoded policy imports them. Weakening the kernel constant therefore refutes an invariant instead of weakening the requirement with it.
* **Complete characterisation.** All-SAT enumeration of the admitted set returns exactly baseline plus the recommendation candidate with rejection source Recommended or Submitted, which equals the set `apply_transaction` can produce. The result is committed as `verification/smt/accepted_set.json` with a drift check. The snapshot embeds semantic digests (parsed program, without formatting, comments, docstrings, typing-only imports and policy annotations) of `policy.py` and `models.py`, not raw byte hashes, so a reformat does not fail the gate and any executable change does.
* **Faithfulness (sampled, not proved).** A deterministic differential test compares the encoding with the real function on every one-field mutation of the three accepted workflows and on seeded random candidates, including candidates that bypass pydantic validators and foreign strings. It compares the exact sorted error list, not only accepted or rejected, and requires every clause to have fired and to have stayed silent at least once. The differential test is itself tested: dropping a clause from the encoding must produce disagreements, and so must weakening the real policy.
* **Negative controls.** For every clause the encoding is re-solved without it; 66 of the 105 clauses are critical to the invariant set and each yields a counterexample that the real `check_policy` rejects citing the deleted clause's code. Only 30 of the 66 stay critical if the pydantic validators are assumed; the other 36 have witnesses that only `model_construct` can build (the policy is the sole defence there, which is why no validator is assumed). The 39 clauses not needed by the invariants (required-effect exactness, the Submit and Revise role and source, and others) are listed, not hidden.

### Consequences

* Good: a closed, machine-checked statement of what the policy guarantees and a complete list of what it admits (up to extra forbidden-effect atoms), with two alarms: a semantic-digest drift check that fires on any executable change to `policy.py` or `models.py`, and a differential sample that catches one-clause and few-field divergences between the encoding and the real function.
* Good: the differential test and the shared-constant weakening (dropping a forbidden effect from the kernel) each have a negative control that must fail.
* Bad: the encoding is hand-written; faithfulness is sampled, not proved. Review showed a narrow seven-field conjunctive backdoor in `check_policy` evades the sample (only the digest drift failed, and regeneration clears it), so the digest plus review of any regeneration is the real alarm. Z3 is in the trusted base and no proof object is checked independently.
* Bad: soundness depends on `Workflow` validation (unique actions). `check_policy` indexes transitions by action, so a `model_construct`-built workflow with a duplicated Approve is admitted (witness in the report). Not fixed here: a kernel change needs its own regression test and ADR; recorded as a follow-up.
* Bad: the invariant is the authors' reading of the policy's intent. It is not an independently derived requirement.
* Revisit when: `policy.py` gains a new action, guard or effect (the drift check fails); or when an independent proof checker or CrossHair route is available.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Z3 (z3-solver), CVC5, CrossHair | Z3 is adopted unchanged; only the encoding, the invariant statements and the differential harness are custom. CrossHair was spiked (see options) and could not construct an admitted `Workflow` out of the box; CVC5 was not evaluated | Export the encoding to SMT-LIB for a second solver; retry CrossHair with a hand-written strategy for `Workflow` and diff the verdicts |
