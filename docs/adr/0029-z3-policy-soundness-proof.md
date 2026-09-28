# ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates

* Status: accepted
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
* CrossHair (symbolic execution of the Python function, Z3 backend): would remove the hand-written encoding, but `check_policy` builds dicts and sets over pydantic models; support for that is patchy, and a failure would be opaque. Revisit as a second, independent route.
* CVC5 / Yices: equivalent for this finite problem; no reason to add a second solver until an independent proof check is wanted (the encoding can be exported as SMT-LIB).
* Exhaustive enumeration in plain Python: the grammar has well over 2^100 candidates, so it does not terminate.

## Decision outcome

Chosen option: "Z3 with a hand-written encoding in `verification/smt/`", because it is the mature, MIT-licensed solver, it decides this finite problem in milliseconds, and the encoding stays small enough to review next to `policy.py`.

* **Grammar.** One slot per known action (unique actions, as `Workflow.coherent` guarantees), each with role, from, to, six guard literals, eight known effect atoms plus one "any other required effect" flag, and forbidden-effect literals. Roles, states and effects outside the known vocabulary are one `OTHER` value each. No `Transition` validator is assumed, so the policy alone must enforce guards and effect exclusion.
* **Encoding.** `check_policy` becomes 105 named clauses, each producing one error code.
* **Theorem.** For every candidate, `check_policy(c) == []` implies each of twelve independently reported invariants (`INV-TEACHER-NOT-DECIDER`, `INV-APPROVE-REQUIRES-RECOMMENDED`, `INV-RECOMMEND-REQUIRES-ASSIGNMENT`, `INV-FORBIDDEN-EFFECTS-EXCLUDED`, `INV-MANDATORY-GUARDS-PRESENT`, and others). Each is an UNSAT query on `canonical AND admits AND NOT invariant`.
* **Complete characterisation.** All-SAT enumeration of the admitted set returns exactly baseline plus the recommendation candidate with rejection source Recommended or Submitted, which equals the set `apply_transaction` can produce. The result is committed as `verification/smt/accepted_set.json` with a drift check.
* **Faithfulness.** A deterministic differential test compares the encoding with the real function on every one-field mutation of the three accepted workflows and on seeded random candidates, including candidates that bypass pydantic validators and foreign strings. It compares the exact sorted error list, not only accepted or rejected, and requires every clause to have fired and to have stayed silent at least once. The differential test is itself tested: dropping a clause from the encoding must produce disagreements, and so must weakening the real policy.
* **Negative controls.** For every clause the encoding is re-solved without it; 63 of the 105 clauses are critical to the invariant set and each yields a counterexample that the real `check_policy` rejects citing the deleted clause's code. Clauses not needed by the invariants (for example the Submit role) are listed, not hidden.

### Consequences

* Good: a closed, machine-checked statement of what the policy guarantees, a complete list of what it admits, and a differential alarm if `policy.py` drifts from the encoding.
* Good: the exercise found a real bug in the first draft of the encoding (the without-recommendation Reject source), caught by the differential test rather than by review.
* Bad: the encoding is hand-written; faithfulness is sampled, not proved. Z3 is in the trusted base and no proof object is checked independently.
* Bad: soundness depends on `Workflow` validation (unique actions). `check_policy` indexes transitions by action, so a `model_construct`-built workflow with a duplicated Approve is admitted (witness in the report). Not fixed here: a kernel change needs its own regression test and ADR; recorded as a follow-up.
* Bad: the invariant is the authors' reading of the policy's intent. It is not an independently derived requirement.
* Revisit when: `policy.py` gains a new action, guard or effect (the drift check fails); or when an independent proof checker or CrossHair route is available.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Z3 (z3-solver), CVC5, CrossHair | Z3 is adopted unchanged; only the encoding, the invariant statements and the differential harness are custom, because no tool derives an SMT model of an arbitrary pydantic-based Python function | Export the encoding to SMT-LIB for a second solver; try CrossHair against `check_policy` directly and diff the verdicts |
