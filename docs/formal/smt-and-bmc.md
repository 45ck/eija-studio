# Z3 policy soundness and bounded model checking

Two formal techniques from the [formal V&V portfolio](../adr/0018-formal-vv-portfolio.md), each a distinct evidence kind that must not be relabelled as the other.

| | SMT policy proof ([ADR-0029](../adr/0029-z3-policy-soundness-proof.md)) | Bounded model check ([ADR-0030](../adr/0030-bounded-model-checking-of-the-real-runtime.md)) |
|---|---|---|
| Evidence kind | `smt_proof` | `bounded_model_check` |
| Subject | `domain.policy.check_policy` | `application.runtime.execute` over `adapters.sqlite_store` (executed, not modelled) |
| Quantifies over | every candidate in the symbolic Transition grammar | every action sequence up to depth *k* over a stated alphabet |
| Tool | Z3 (`z3-solver==5.1.0.0`, MIT) | explicit-state BFS (`verification/bmc`, custom around the real runtime) |
| Report | `reports/formal/smt.json` | `reports/formal/bmc.json` (`bmc_deep.json` for the release tier) |
| Gate | `nox -s formal_smt` (tier full) | `nox -s bmc` (full), `nox -s bmc_deep` (release) |
| Needs | `pip install -e ".[dev,smt]"` | nothing beyond the base install |

A missing prerequisite (no `z3-solver`) produces a `NOT_RUN` report and a skipped nox session, never a pass.

```
.venv/Scripts/python -m verification.smt                 # exit 0 PASS, 1 FAIL, 3 NOT_RUN
.venv/Scripts/python -m verification.bmc --depth 6       # exit 0 PASS, 1 FAIL, 2 INCONCLUSIVE
.venv/Scripts/python -m verification.bmc --depth 8 --tier release
```

## 1. SMT proof of policy soundness

**Claim.** For every candidate `c` in the grammar, `check_policy(c) == []` implies `AuthorityInvariant(c)`.

**Grammar** (`verification/smt/vocabulary.py`, `encoding.py`). One slot per known action (`Submit`, `Recommend`, `Approve`, `Reject`, `Revise`); each present slot has a role, from and to state, six guard literals, eight known effect atoms plus "some other required effect", and forbidden-effect literals. A flag stands for "some unknown action exists" and another for "some unknown state exists". Roles, states and effects outside the known vocabulary are a single `OTHER` value: sound because the policy only compares them by equality or set membership against known constants. No `Transition` validator is assumed, so guards and effect exclusion rest on the policy alone.

**Requirement** (`authority_invariants`), twelve conjuncts reported one by one:

| Invariant | Statement |
|---|---|
| `INV-TEACHER-NOT-DECIDER` | Teacher never holds Approve or Reject |
| `INV-REGISTRAR-ONLY-DECIDES` | Approve and Reject are held by Registrar alone |
| `INV-TEACHER-TRANSITIONS-NEVER-DECIDE` | no Teacher-held transition ends in Approved or Rejected |
| `INV-TEACHER-EMITS-NO-DECISION-AUDIT` | no Teacher-held transition requires an Approved/Rejected audit effect |
| `INV-APPROVE-REQUIRES-RECOMMENDED` | with recommendation enabled, Approve starts from Recommended |
| `INV-APPROVED-ONLY-VIA-APPROVE` | only Approve can end in Approved |
| `INV-RECOMMEND-REQUIRES-ASSIGNMENT` | Recommend carries `actor_assigned` and is held by Teacher |
| `INV-RECOMMEND-CANNOT-CONCLUDE` | Recommend ends in Recommended |
| `INV-REJECT-SOURCE-BOUNDED` | Reject starts from Recommended or Submitted only |
| `INV-FORBIDDEN-EFFECTS-EXCLUDED` | no transition requires `PaymentCaptured` / `ParentDataExported`; all forbid both |
| `INV-MANDATORY-GUARDS-PRESENT` | every transition carries every base guard |
| `INV-CLOSED-WORKFLOW` | starts in Draft, no unknown action, no unknown state |

The statements come from the policy's stated intent (`TECHNICAL_LEAD_REVIEW.md`, `CANONICAL_OPTIONS`), not from the code of `check_policy`. They share the policy's authorship; they are not independently derived requirements.

**Proof.** For each invariant, Z3 is asked whether `canonical AND admits AND NOT invariant` is satisfiable. `unsat` is the proof; `sat` returns a counterexample workflow, decoded into a Python `Workflow` and re-run through the real `check_policy`.

**Accepted set.** All-SAT enumeration of `admits` returns exactly three workflows: the baseline, and the recommendation candidate with Reject starting from Recommended or from Submitted. That equals the set `apply_transaction` can produce. The set is committed as `verification/smt/accepted_set.json`; regenerate with `python -m verification.smt --write-snapshot` after a reviewed policy change. It holds up to extra forbidden-effect atoms: the policy only requires the two mandatory ones to be present, so harmless supersets are also admitted, and the enumeration pins the extras off.

**Faithfulness** (`differential.py`). The encoding is hand-written, so it is compared with the real function. The candidate stream is deterministic: every one-field mutation of the three accepted workflows (roles, states, guards, effects, removed and added transitions, foreign action, states, initial state), then seeded random multi-field mutants and fully random candidates, including candidates built with `model_construct` that pydantic would refuse and strings outside the vocabulary. The exact sorted error list must match, and so must a plain-Python restatement of each invariant. Every clause must have fired and have stayed silent at least once, otherwise agreement on it would be vacuous. The differential test is itself tested: an encoding with a clause dropped, and a weakened real policy, must both be reported as disagreeing. It has already paid for itself once: it caught a missing clause in the first draft of the encoding (Reject must start from Submitted when the recommendation meaning is not enabled).

**Negative controls.** The encoding is re-solved with each clause removed in turn. Removing a clause the invariants depend on yields a counterexample, which is rejected by the real `check_policy` citing the removed clause's code. Eight named controls are asserted (for example removing the Approve role clause violates `INV-TEACHER-NOT-DECIDER`; removing `actor_assigned` violates `INV-RECOMMEND-REQUIRES-ASSIGNMENT`). Clauses the invariant set does not need (for example the Submit role or the extra `actor_assigned` on Approve) are listed in the report rather than presented as proved essential.

### What the SMT proof does not establish

* It is about the policy function on the modelled grammar, not the runtime, SQLite, HTTP or the interpreter.
* Z3 is trusted; there is no independently checked proof object. The encoding could be exported to SMT-LIB for a second solver.
* Faithfulness of the encoding is sampled, not proved.
* The unique-action assumption is real. `check_policy` indexes transitions by action, so a workflow built with `model_construct` that repeats an action hides the first copy. The report contains the witness: a Teacher-held Approve placed before the real one is admitted, while `Workflow.model_validate` rejects it. Soundness therefore depends on every workflow having passed pydantic validation.

## 2. Bounded model checking of the real runtime

**State.** The complete observable database of an ephemeral sandbox (instance, actors, operations, audit log, outbox). **System under test.** `application.runtime.execute` running in `SQLiteStore.transaction()` on a store from `adapters.sqlite_store.sandbox_factory`; the harness only reads, restores observed rows between moves and applies environment moves.

**Moves** (`explorer.py`).

* Commands: every actor (`teacher-assigned`, `teacher-unassigned`, `teacher-revoked`, `registrar`, `viewer`, plus an unknown `ghost`) times every action (the five plus an unmodelled `Bogus`), with the current `expected_version` or one stale value.
* Replays: for every recorded operation id, the identical command, the same id with each other actor, and the same id with each other action.
* Environment: flip `teacher-assigned.active`, `teacher-assigned.assigned` and `registrar.active` by updating the actors table (`--toggles all` adds `teacher-unassigned.assigned` and `teacher-revoked.active`).

**Invariants** (`spec.py`). Step properties: authority on commit; authority before replay; compare-and-swap; state guard; exactly-once operations and operation binding; exact commit effects; replay and rejection leave no trace; no spurious denial; denial reason; no unexpected exception. State properties: version counts commits; audit trail is a valid run of the model ending at the instance state; decisions only by Registrar; approval only after a recommendation; no forbidden effect; effects declared by the model; outbox rows match committed Recommends. The reference model is a same-author oracle. It is deliberately silent on which denial code wins when several apply and strict on the class of outcome and every side effect.

**Search.** Breadth-first with de-duplication, so the first counterexample per invariant is a shortest one. Each report records states, transitions, per-depth new states, outcome-class counts, whether the reachable set closed (`exhausted`), and timings under `measurements` only. A coverage check fails if the alphabet never provokes a denial code, a replay or a revocation, so "no violation" cannot come from an alphabet that never reaches the interesting behaviour. A wall-clock cap (`--max-seconds`) makes a run `INCONCLUSIVE`, never `PASS`.

**Self-test.** `mutants.py` seeds six runtime faults: revocation ignored, assignment ignored, role ignored, replay served before authority is rechecked, stale version accepted, replay reapplies effects. Each must be caught within three moves, with a shortest trace (for example `teacher-assigned Submit v=0 op=op0` then `teacher-revoked Submit v=0 op=op0` for the replay flaw). The state invariants have separate tampered-database tests.

**Tiers.** Full: depth 6, `baseline` and `candidate-reject-from-Recommended`, self-test, drift check of the deterministic statistics in `verification/bmc/expected_statistics.json`. Release: depth 8, all three variants.

### What the bounded model check does not establish

* Bounded: no violation to depth *k* is not a proof at *k+1*, and the reachable set did not close at the depths run.
* One instance, sequential commands: no concurrent writers, crash points or fault injection (`tests/test_runtime.py` covers those separately).
* Actor roles are fixed; only the listed flags change.
* Observes the implementation and SQLite; it does not prove either correct.
* Same-author oracle and same authorship as the runtime; not an independent verification, not a human study.

## How the two connect, and to the rest of the portfolio

The SMT proof says the gate admits only three workflows, all authority-preserving. The bounded model check drives the runtime on exactly those workflows and checks that execution respects the same authority story over sequences (Registrar-only decisions, approval after recommendation, Teacher-held Recommend guarded by assignment, forbidden effects never emitted). Neither replaces the TLA+ model of the protocol (ADR-0027), the Bend laws (ADR-0025) or human review; a receipt from one technique never stands in for another.

## Reproducibility

Reports are JSON with sorted keys and LF line endings; wall-clock and platform appear only under `measurements`. Everything else is deterministic for the same sources, seed (`--seed`, default 20260928) and bounds. The two committed snapshots (`accepted_set.json`, `expected_statistics.json`) are regenerated and compared inside the gates, so a drift fails the session.
