# Evidence kinds: what the kernel accepts, and what it does not

The review packet shows the runtime matrix plus every **formal evidence kind**, each with its status, assumptions, bounds and
what it does not establish. Decisions: [ADR-0145](adr/0145-per-kind-evidence-admissibility.md) (the per-kind admissibility model)
and [ADR-0146](adr/0146-formal-receipt-formats-binding-and-not-run.md) (artifact formats, binding, NOT_RUN). Code:
`domain/formal*.py` (pure checks), `domain/evidence.py` (envelope and aggregation), `application/formal.py` (intake and packet
view), `adapters/formal/` (report readers).

The rule for every row: **the kernel recomputes the verdict from the raw typed artifact. A supplied green label is never
evidence, and a tool's own FAIL or incomplete label can only lower a status.**

| Kind (claim) | What it establishes | What it does NOT establish | Binds to | Recomputed vs sealed | Prerequisites |
|---|---|---|---|---|---|
| `integration_test` (`runtime_matrix`) | the real runtime agrees with a same-author oracle on all 125 declared actor x state x action cells | crash durability, concurrency, arbitrary sequences, human outcomes | all five technical subject dimensions | **recomputed** (expected vs actual cells, complete coverage, shape) | none |
| `bend_proof` (`authority_laws_model`) | for the Bend model generated from the current baseline and candidate, 8 authority laws hold for all actors, states and command sequences; the proofs fail on 6 seeded-unsafe models, each with a confirmed counterexample | anything about the Python runtime or SQLite; that the model equals the runtime (conformance is a bounded differential test of 225+ cells); that no other fault escapes; that the laws are the right ones | semantic hashes of the current baseline **and** candidate (recomputed); `main.bend` regenerated from them, and the current `LAWS.bend`, `PROOF.bend`, generator (attested) | verdict, laws, controls, bounds and semantic binding **recomputed**; that Bend answered `PROVEN` (no exported certificate) **sealed tool verdict** | Docker with the pinned Bend image; else `NOT_RUN` |
| `smt_proof` (`policy_soundness`) | for every candidate in the symbolic Transition grammar, if `check_policy` admits it then 12 authority invariants hold; the encoding agrees with the real policy on 1000+ differential candidates; the policy admits exactly the workflows the kernel can produce | the runtime, SQLite or HTTP; that Z3 is right (no checkable proof object); that the encoding equals the function (sampled, not proved); that the invariants are the right requirement | the candidate's semantic hash must be in the proved admitted set (recomputed); the bytes of `domain/policy.py` and `domain/models.py` (attested) | invariants, non-vacuity, controls, differential counts, admitted set **recomputed**; Z3's `unsat` **sealed tool verdict** | `z3-solver` (`pip install -e .[smt]`), `python -m verification.smt`; else `NOT_RUN` |
| `bounded_model_check` (`runtime_safety_bounded`) | no reachable state or step within the stated depth (at least 6) and alphabet violates the safety invariants when the real runtime executes every fixture actor, stale versions, replays and revocations; each of 6 seeded runtime faults is caught by the same search | anything beyond the depth; concurrency, crashes, fault injection; that the runtime or SQLite is correct; independence of the oracle | the candidate's semantic hash must be among the explored models (recomputed); the bytes of the runtime sources (attested) | bounds, coverage, counterexamples, self-test **recomputed**; the counts themselves (the search is not re-run) **sealed tool verdict** | `python -m verification.bmc` report; else `NOT_RUN` |
| `tlc_model_check` | planned: the TLA+ protocol model under TLC | not built yet: `UNKNOWN` by construction | planned | planned | Java, TLC |
| property test, mutation score | planned | not built yet: `UNKNOWN` by construction | planned | planned | Hypothesis, mutmut |

## What each status means in the packet

| Status | Meaning | Blocks technical eligibility? |
|---|---|---|
| `PASS` | the kernel recomputed a pass from raw content, every required negative control failed as pinned, bounds meet the declared minimum, and the receipt binds to the current subject | no |
| `FAIL` | a counterexample, a refuted invariant, a control the proof did not reject, a contradiction, a tampered or malformed artifact, or an unauthentic receipt | **yes** (`FORMAL_EVIDENCE_FAIL:<kind>`) |
| `CONFLICT` | authenticated PASS and FAIL receipts for the same subject; never averaged | **yes** |
| `STALE` | the receipt is about another subject: a different semantic hash, or changed model, law or source bytes | no |
| `NOT_RUN` | a prerequisite (Docker, z3, a saved run) is missing; the reason is shown | no |
| `UNKNOWN` | no receipt, or evidence incomplete: a missing law, control or mutant, a bound below the declared minimum, an unaccepted tool version | no |

UNKNOWN, NOT_RUN and STALE never block, and they are never shown as green: each appears in `technical_claims` as
`formal_<kind>` and in `formal_evidence` with its reasons. The formal kinds are **additional** to the runtime matrix, which stays
required.

## Where to see it

* **Studio:** the Evidence tab lists each kind under the claim cards (text only, no markup from artifacts is interpreted).
* **CLI:** `eija verify <case> --expected-version N` prints the packet as JSON on stdout and one line per kind on stderr;
  `eija compile <workflow.json>` adds `formal_evidence` and, for a blocked model, `formal_explanations`. `--no-formal` skips them.
* **Unsafe change:** for a candidate the policy blocks (for example a teacher holding Approve), the packet's `explanations` attach
  the seeded negative-control counterexample of the same fault class (a Bend trace `Submit, Recommend, Approve` by a teacher
  ending in `Approved`, or the Z3 witness of the removed policy clause). It is labelled as a seeded unsafe model that explains the
  block, not a proof about the candidate.

A proposed meaning the policy refuses never becomes a candidate, so before any meaning is selected the packet lists it under
`blocked_meanings` with the what-if model's policy errors and the same explanation (the Studio Evidence tab shows both).

## Known limits of this evidence

* Every formal receipt is a `sealed_tool_verdict` today: the kernel recomputes coverage, controls, bounds and binding, not the
  tool's own answer.
* The receipt's subject dimensions are stamped when the receipt is collected; for an older report the proof-time binding is the
  artifact's own (model hashes, admitted set, named file and source hashes). A source the report does not name is not bound.
* Anyone who can write `reports/formal/` or a committed snapshot can supply an internally consistent report; only git review covers
  the snapshots.

## Reading the evidence level

* `recomputed`: the kernel re-derived the outcome from raw observations of its own semantics.
* `sealed_tool_verdict`: a solver's or prover's verdict without a certificate the kernel can check, accepted under the sealed local
  producer. It is weaker than `recomputed`. The HMAC key owner can forge any receipt
  ([SECURITY_AND_TRUST.md](SECURITY_AND_TRUST.md)); recomputation narrows what anyone else can do.

## Adding a kind

Add `domain/formal_<name>.py` with the typed artifact shape, pinned required items, declared minimum bounds and a pure `check`
returning findings, register it in `domain/evidence_kinds.py`, add an adapter reader that copies raw fields (no verdict) and a
NOT_RUN path, and add the tamper, stale, forged-label, missing-control, below-bound and NOT_RUN tests that
`tests/test_evidence_kinds.py` shows for the existing kinds.
