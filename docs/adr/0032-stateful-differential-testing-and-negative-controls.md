# ADR-0032: Stateful differential testing against a specification-derived reference, with mutant negative controls

* Status: accepted
* Date: 2026-09-28
* Lane: property (testing)

## Context and problem statement

The runtime's promises are about *histories*: replay never repeats effects, a revoked actor cannot replay a cached success, a crash rolls back everything, an edit makes old instances stale but an edit back does not. The verifier's 125-cell matrix checks one step from a fresh instance with a same-author oracle. Neither shows that arbitrary sequences of executes, replays, revocations, resets and edits keep the durable state equal to what the specification requires. Separately, a green property suite means nothing if the same suite would also be green against a broken kernel.

## Decision drivers

* A second expression of the rules, written from the specification text and not from `application/runtime.py`.
* Every guarantee claimed must have been shown able to fail.
* No claim of independence that authorship does not support.

## Considered options

* Hypothesis `RuleBasedStateMachine` driving the real `Studio` on the SQLite adapter, compared after every step with a naive reference model (chosen)
* Reusing the verifier oracle as the reference (rejected: it is the object the receipts already rest on, and covers one step only)
* Mutation testing of the kernel (a separate lane, ADR-0033/0034; complementary, not a substitute: it mutates the kernel and asks whether any test notices, while these controls mutate the kernel and require *this* suite to notice)

## Decision outcome

Chosen option: "stateful differential test plus explicit mutants".

* `tests/property/property_reference.py` is the reference model. Its docstring cites the ARCHITECTURE.md "Runtime commit sequence" and ADR-007/011 clauses it implements, and records the one ordering the specification leaves open (where "is the action modelled?" sits). It shares the policy vocabulary with the kernel and the same authors and project, so it is a *differential oracle*, not a blinded holdout. Reports and documentation say so.
* `tests/property/test_runtime_differential.py` generates sequences (fresh, replayed and conflicting operation ids; correct and stale versions; injected faults after each commit step; actor revocation, reassignment and re-roling; reset; the typed rejection-source edit) and, after each step, compares instances, audit, outbox, operations and case version with the reference, and each outcome (committed, replayed, refusal code) with its prediction. After the run it requires that every outcome kind was reached, so the walk cannot pass by never leaving the start state.
* `test_reference_detects_mutants.py` and `test_properties_detect_mutants.py` monkeypatch deliberately wrong behaviour into the running kernel (replay before authority, conflict answered as replay, stale version ignored, assignment or revocation unchecked; order-sensitive or field-dropping hashes; a depth-capped or off-by-one closure; an assessor that skips the artifact hash, trusts the matrix or ignores the subject; schemas that are looser or stricter than the model) and require the relevant property to fail with an `AssertionError`.
* A property that finds a real kernel defect does not silently patch the kernel in this lane: it is committed as `xfail(strict=True)` with the reason, and the fix is a separate kernel change.

### Consequences

* Good: the same-author oracle problem is named and bounded, and each guarantee is shown to be falsifiable.
* Good: the harness can be pointed at another persistence backend (the extension contract in ARCHITECTURE.md requires reproducing UnitOfWork/CAS/replay semantics).
* Bad: if specification and reference share a misreading, both agree and the bug survives. Only a blinded second author, or the formal lanes (TLA+ trace conformance), narrows this.
* Bad: mutants patch module attributes and Hypothesis' per-test settings; they are tied to the pinned versions.
* Revisit when: a persistence backend other than SQLite is added, or a blinded author is available to write a second reference from the specification alone.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Hypothesis stateful testing, Schemathesis stateful, TLA+ (formal lane) | Hypothesis supplies the engine; the reference model is EIJA-specific by definition (it encodes EIJA's rules). Schemathesis' stateful mode links OpenAPI operations, not a domain state machine. TLA+ trace conformance is the formal lane's tool and is complementary | Replace the reference with a model generated from the TLA+ specification when that lane lands |
