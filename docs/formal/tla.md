# TLA+ specification and TLC model checking

Evidence kind `tlc_model_check` ([ADR-0018](../adr/0018-formal-vv-portfolio.md), decisions in [ADR-0027](../adr/0027-tla-plus-specification-and-model-checking.md) and [ADR-0028](../adr/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md)).

## What this establishes, and what it does not

**Establishes.** Within the declared bounds (a handful of operation ids, one preview instance, the five-actor fixture directory), every interleaving of commands and directory changes (revocation, assignment loss, restoration) that the TLA+ model allows keeps these safety properties: no teacher ever holds a committed approval; approval is only taken from `Recommended` after a `Recommend` committed (candidate model); an effect is queued at most once per operation id; state, version, operation record and audit move together; a replayed or conflicting operation is never answered to an actor who is not currently authorised; forbidden effects are never emitted; the version never decreases. Separately, and measured rather than assumed, the real `application.runtime.execute` produces the same outcome code and the same state change as the model on every command from every reachable state within the exhaustive bound, and on every step of hundreds of executed traces.

**Does not establish.** Correctness of the Python beyond the compared behaviours; anything beyond the bounds (larger histories, several instances or cases, concurrent connections, crash or power loss, model-hash staleness, `NOT_FOUND`); real identity; delivery of the outbox. A TLC pass is a proof about the model. The model is a hand transcription of the runtime's check order by the same author as the code, so agreement is evidence, not independent validation. The negative controls use seeded defects and hostile workflows that protected policy already rejects; they show the invariants are sensitive, not that the kernel has those defects.

## Run it

```
python -m verification.tla.generate --check     # fast tier: committed model modules match the kernel (nox -s tla_drift)
python -m verification.tla.run                   # full tier (nox -s formal_tla), writes reports/formal/tla.json
python -m verification.tla.run --deep            # release tier (nox -s formal_tla_deep): candidate at 5 operation ids
```

Prerequisites: Java 11+ on `PATH` and the pinned `tla2tools.jar` (v1.7.4, downloaded once into `.cache/tla/`, verified against the sha256 in `verification/tla/TOOLS.lock`). Without Java, or without a downloadable jar, the report says `NOT_RUN` with the reason and the nox session is skipped; it never passes silently. A jar whose hash differs from the lock is a hard failure. TLC's temp and state files stay under `.tmp/tla/`.

## Files

| Path | Role |
|---|---|
| `verification/tla/Excursion.tla` | The specification: state, `Decide` (check order), `Succ`, environment steps, invariants, state-graph dump |
| `verification/tla/ExcursionTrace.tla` | Trace validation: checks observed runtime traces against the model |
| `verification/tla/generate.py` | Renders `generated/MC_*.tla|cfg` from the kernel workflows, actor directory and bounds; `--check` is the drift gate |
| `verification/tla/model.py` | Configurations (safe and negative-control) built from `domain.policy`; command and environment orderings |
| `verification/tla/abstraction.py` | Maps a runtime store to the model state and back (through the `UnitOfWork` port) |
| `verification/tla/conformance.py` | Exhaustive graph exploration on the real runtime, comparison, trace recording |
| `verification/tla/tlc.py`, `render.py`, `run.py` | TLC runner and output parser, counterexample renderer, orchestrator and report |
| `verification/tla/TOOLS.lock` | Pinned TLC release, URL and sha256 |
| `verification/tla/evidence/` | Committed evidence snapshot, named for the platform that produced it |

## The model

State: workflow state, instance version, a record per operation id (actor, action, expected version, result), audit count, outbox rows per operation id, the actor directory (`active`, `assigned` per actor) and the set of emitted effect names. Commands are `(operation id, actor, action, expectedVersion)`; environment steps change one directory bit of a mutable actor (`teacher-assigned`, `registrar`).

`Decide` reproduces the order in `application/runtime.py`:

| # | Check | Outcome code |
|---|---|---|
| 1 | action is modelled | `ACTION_DENIED` |
| 2 | actor is in the directory | `UNKNOWN_ACTOR` |
| 3 | actor is active now | `ACTOR_REVOKED` |
| 4 | actor holds the transition's role | `ROLE_DENIED` |
| 5 | actor is assigned (when the transition guards it) | `ASSIGNMENT_DENIED` |
| 6 | operation id already recorded: different binding, or same binding | `OPERATION_CONFLICT`, `DUPLICATE` |
| 7 | expected version equals the current version | `STALE_VERSION` |
| 8 | current state equals the transition's source | `STATE_DENIED` |
| 9 | every required effect has an adapter | `EFFECT_DENIED` (rolled back) |
| 10 | commit: state, version, audit, outbox and operation record in one step | `COMMITTED` |

Only `COMMITTED` changes state. Steps 1 to 5 precede step 6: a cached success is not continuing authority.

The transition table (source, target, role, assignment guard, audit and notification effects) is generated from the Python `Workflow`; three safe configurations are generated (`baseline`, `candidate`, `candidate_reject_submitted`) and four negative controls.

## Invariants

| Invariant | Meaning | Negative control that violates it |
|---|---|---|
| `TypeOK` | Variables stay in their declared sets | (structural) |
| `NoTeacherApproval` | No committed approval was issued by an actor whose directory role is Teacher | `nc_teacher_approval` |
| `ApprovalRequiresRecommendation` | Candidate model: approval only from `Recommended`, after a `Recommend` committed | (vacuous for baseline) |
| `OutboxAtMostOncePerOperation` | Outbox rows per operation id never exceed what the committed operation queues | `nc_replay_reemits` |
| `AtomicCommit` | Version equals the number of operation records; audit equals the audit effects of the recorded operations | (a replay that re-emits audit also violates it) |
| `ReplayNeverBypassesCurrentAuthority` | No history-dependent answer (`DUPLICATE`, `OPERATION_CONFLICT`, version, state, commit) for an actor not authorised in the current directory | `nc_replay_before_auth` |
| `ForbiddenEffectsNeverEmitted` | `PaymentCaptured` and `ParentDataExported` are never emitted | `nc_forbidden_effect` |
| `VersionMonotonic` (action property) | The version never decreases | (holds by construction; kept as a guard against edits) |

## Results

Snapshot: `verification/tla/evidence/tla-windows11-py312.json` (Windows 11 10.0.26200, Python 3.12.10, OpenJDK Temurin 17.0.19, TLC 2.19 from `tla2tools.jar` v1.7.4; run as `nox -s formal_tla_deep`, result `PASS`, 8 to 12 minutes on the reference PC depending on load). The gate tier (`formal_tla`) is the same without the 5-operation-id row. Timings and counts of a re-run may differ in seconds only; state counts are deterministic.

### Model checking (all invariants and `VersionMonotonic`)

| Configuration | Op ids | States generated | Distinct | Depth | Result |
|---|---|---|---|---|---|
| `baseline` | 4 | 26,017 | 5,520 | 9 | PASS |
| `candidate` | 4 | 16,513 | 3,600 | 9 | PASS |
| `candidate_reject_submitted` | 4 | 29,377 | 6,288 | 9 | PASS |
| `candidate` (`--deep`) | 5 | 130,265 | 27,696 | 10 | PASS |

Bound: operation ids `op1..opN`, expected versions `0..N`, five directory actors plus one unknown actor id in commands, environment steps on `teacher-assigned` and `registrar`. "Exhausted" means TLC's breadth-first search terminated with an empty queue.

### Negative controls (each must fail with its expected invariant)

| Control | What is broken | Violated | States | Depth |
|---|---|---|---|---|
| `nc_teacher_approval` | `Approve` granted to the Teacher role (protected policy rejects it: `PROTECTED_AUTHORITY:Approve`) | `NoTeacherApproval` | 76 | 4 |
| `nc_replay_before_auth` | replay lookup placed before the authority checks | `ReplayNeverBypassesCurrentAuthority` | 2 | 2 |
| `nc_replay_reemits` | a replay re-queues its notification | `OutboxAtMostOncePerOperation` | 76 | 4 |
| `nc_forbidden_effect` | unadapted `PaymentCaptured` emitted instead of `EFFECT_DENIED` (policy rejects it: `EFFECT_POLICY:Approve`) | `ForbiddenEffectsNeverEmitted` | 76 | 4 |

The counterexample for `nc_teacher_approval`, rendered from TLC's trace by `verification/tla/render.py` (all four are in `reports/formal/tla-counterexamples.md` after a run):

| # | step | workflow state | version | audit | outbox rows |
|---|---|---|---|---|---|
| 1 | initial state (Draft, version 0, fixture directory) | Draft | 0 | 0 | - |
| 2 | teacher-assigned executes Submit as op1 (expectedVersion 0): Draft -> Submitted, version 1 | Submitted | 1 | 1 | - |
| 3 | teacher-assigned executes Recommend as op2 (expectedVersion 1): Submitted -> Recommended, version 2 | Recommended | 2 | 2 | op2=1 |
| 4 | teacher-assigned executes Approve as op3 (expectedVersion 2): Recommended -> Approved, version 3 | Approved | 3 | 3 | op2=1 |

The second control shows the point of checking authority before replay: after `op1` is recorded, a spec that consults the operation table first answers `OPERATION_CONFLICT` to an actor that is no longer (or never was) authorised, leaking that the operation exists. The kernel's own test `test_revocation_is_rechecked_before_replay` covers one instance of this; TLC covers every interleaving in the bound.

### Conformance: does the runtime agree with the model?

Measured against the real `application.runtime.execute` on an ephemeral SQLite sandbox.

| Configuration | Graph bound | Reachable states (runtime = spec) | State x command cells compared | Of which committing | Disagreements | Trace validation (6 op ids) |
|---|---|---|---|---|---|---|
| `baseline` | 2 op ids | 208 = 208 | 37,440 | 112 | 0 | 283 traces (13 scenarios, 70 path probes, 200 random), 3,544 steps: agree |
| `candidate` | 3 op ids | 688 = 688 | 247,680 | 312 | 0 | 312 traces (13, 99, 200), 3,952 steps: agree |
| `candidate_reject_submitted` | 2 op ids | 208 = 208 | 37,440 | 96 | 0 | 283 traces (13, 70, 200), 3,535 steps: agree |

* A cell is (reachable state, command). It compares the outcome code (`COMMITTED`, `DUPLICATE`, `ACTOR_REVOKED`, ...) and, for committing commands, the successor state. Environment successors are compared too. Initial states are equal; no state exists on only one side.
* Non-committing commands are additionally checked against the runtime for "state unchanged" (instance state, version, audit, outbox and operation counts), and each replay must return the original result. Runtime-side defects found: 0.
* Trace outcomes exercised (candidate): `COMMITTED` 618, `DUPLICATE` 470, `ACTOR_REVOKED` 795, `ASSIGNMENT_DENIED` 283, `ROLE_DENIED` 454, `OPERATION_CONFLICT` 97, `STALE_VERSION` 100, `STATE_DENIED` 38, `UNKNOWN_ACTOR` 215, plus 882 environment steps. Path probes are a deterministic stride sample when a graph has more than 100 states (`candidate`: 99 of 688).
* Sensitivity: the same comparison against the spec with the seeded replay-before-authority defect reports 168,096 outcome disagreements, and trace validation reports a divergence too. Agreement is therefore not vacuous.

Agreement means: within these bounds and this abstraction, the model and the code make the same decisions. It says nothing about states beyond the bounds, concurrency, crashes, audit bodies or outbox payloads.

### Not run

Nothing in this lane was skipped on the reference PC. Without Java on `PATH` (verified by removing it), `formal_tla` reports `NOT_RUN: java is not on PATH` and the nox session is skipped; without a downloadable jar the reason is the download failure.

## Changing the kernel

If the workflow, the effect table, the fixture directory or a guard changes, `nox -s tla_drift` fails until `python -m verification.tla.generate` is re-run and the diff is reviewed. If a runtime check is added, removed or reordered, `Decide` in `Excursion.tla` must change with it; `formal_tla` then fails on the state-graph comparison until the two agree again, which is the point of measuring conformance rather than assuming it.
