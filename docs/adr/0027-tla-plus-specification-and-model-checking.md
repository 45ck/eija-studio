# ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC

* Status: accepted
* Date: 2026-09-29
* Lane: tla (formal V&V, evidence kind `tlc_model_check`, see [ADR-0018](0018-formal-vv-portfolio.md))

## Context and problem statement

The v0.2 runtime matrix checks one step from each state. The properties that matter most to EIJA are about **histories**: authority is re-checked at commit time even when an operation is replayed after revocation; an effect is queued at most once per operation id; a teacher never obtains final approval by any interleaving of commands and directory changes. One-step tests cannot establish those, and an explicit-state model checker can, within declared bounds, with a counterexample when they fail.

## Decision drivers

* The check must cover the commit protocol (authorise, replay lookup, binding conflict, CAS, state check, atomic effects), not only the transition table.
* Actor directory changes (revocation, assignment) must interleave anywhere, because replay-after-revocation is the interesting attack.
* Model data must not be retyped: a transition table copied by hand drifts silently.
* An invariant that cannot fail proves nothing, so each key invariant needs a seeded violation.
* OSS first ([ADR-0016](0016-oss-first-adapters-not-engines.md)); Java 17 and Windows must be enough.

## Considered options

* TLA+ with the TLC explicit-state model checker (chosen). MIT, released jars, counterexample traces, runs on Java 11+.
* Apalache (symbolic checker for TLA+): stronger for unbounded integers, but needs type annotations and a JVM/Scala toolchain and adds nothing at these small bounds.
* Alloy 6 or Quint: comparable, but neither has a trace-validation idiom in the form used by ADR-0028.
* A Python explicit-state search over the real runtime: kept as a separate lane (bounded model checking, ADR-0029/0030). It checks the code but cannot state an invariant independently of the code it runs.

## Decision outcome

Chosen option: **TLA+ / TLC**, with these parts.

* `verification/tla/Excursion.tla` is a hand-written transcription of `application/runtime.py::execute` in the runtime's own order: modelled action, directory actor, active, role, assignment (authority, now), replay lookup (binding conflict or duplicate), CAS version, state check, then one atomic step (state, version, audit, outbox, operation record). Directory changes are environment steps.
* Everything that is data comes from the executable Python model. `verification/tla/generate.py` renders the transition table, effect classification, actor directory, forbidden effects and bounds into `verification/tla/generated/MC_*.tla|cfg`. A drift check (`nox -s tla_drift`, tier `fast`) fails when the committed files differ from a fresh generation.
* TLC is pinned (`verification/tla/TOOLS.lock`: release, URL, sha256). Missing Java or an unfetchable jar reports `NOT_RUN`; a hash mismatch is a hard error.
* Invariants: `TypeOK`, `NoTeacherApproval`, `ApprovalRequiresRecommendation`, `OutboxAtMostOncePerOperation`, `AtomicCommit`, `ReplayNeverBypassesCurrentAuthority`, `ForbiddenEffectsNeverEmitted`, and the action property `VersionMonotonic`.
* Negative controls are part of the evidence: a workflow granting `Approve` to the Teacher role (which protected policy rejects), a decision order that looks up the replay before authority, a replay that re-queues its effects, and an unadapted forbidden effect that is emitted instead of rejected. Each must produce its expected TLC counterexample, which is rendered step by step.
* The report `reports/formal/tla.json` has kind `tlc_model_check` and records TLC version, jar hash, bounds, states generated and distinct, depth, results, counterexamples and conformance statistics.

### Consequences

* Good: the interleavings of commands and directory changes are exhausted up to the bound, not sampled. A weakened invariant or a re-ordered protocol is caught.
* Good: model data cannot drift from the code unnoticed.
* Bad: the check order in `Decide` is a hand transcription. ADR-0028 measures agreement with the code instead of assuming it.
* Bad: the bound is small (4 operation ids in the gate, 5 with `--deep`); results say nothing about larger histories, several instances, or concurrency across connections.
* Bad: the model and the code share an author. Agreement is not independent validation.
* Revisit when: the kernel gains a second instance per case, a real revocation API, or an asynchronous outbox worker (the model must then grow), or when a TLC release with a published digest and `ALIAS` support supersedes the pinned one.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| TLA+/TLC | Used as is; only the EIJA specification, generator, runner and renderer are custom | Any TLC 2.19+ jar with a matching TOOLS.lock entry |
| Apalache, Alloy, Quint | Not adopted (see options) | Generated MC modules are TLC-specific; a second checker would need a second generator |
| Python-to-TLA+ translators | None was found that renders Pydantic workflow contracts as a TLC model (search was brief, not exhaustive) | `generate.py` is string rendering of data only; replace it if a maintained translator appears |
