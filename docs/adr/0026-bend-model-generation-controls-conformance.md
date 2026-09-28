# ADR-0026: The Bend model is generated from the Workflow; negative controls and conformance accompany every proof

* Status: proposed (accepted when the `lane/bend` pull request merges)
* Date: 2026-09-28
* Lane: bend (formal: Bend laws and proofs)

## Context and problem statement

A proof is only as meaningful as the model it is about and the specification it proves. Two failure modes
matter here: a hand-copied Bend model drifts from the Python `Workflow` the kernel runs, and a proof that is
satisfied by every model (including an unsafe one, or one that denies everything) is worthless. What must accompany
a `bend_proof` so its result can be trusted, and what may it claim?

## Decision drivers

* One source of truth: the executable Python `Workflow` (no parallel rule/state sources; AGENTS.md).
* Deterministic generated artefacts with a drift check; LF line endings.
* A proof must be shown to fail on an unsafe model (negative control) and the laws must not hold vacuously.
* Honest labels: a proof about a model is not a proof about the runtime.

## Considered options

* Hand-write the Bend model once and review it against the Python code.
* Generate `main.bend` from the `Workflow`, commit it, and fail a fast drift check when it differs from regeneration.
* Generate the model on every run and never commit it.

## Decision outcome

Chosen option: "generate and commit `main.bend`, with a drift check", because a committed generated file is reviewable
in a pull request and the drift check (no Docker) makes stale models a fast-tier failure.

* **Two slots.** One program holds the `Baseline` and the `Candidate` (recommend_only) workflows as `Rule` tables of
  one shared engine (`step`, `replay`). `LAWS.bend` and `PROOF.bend` are static and independent of the table contents.
* **The step semantics are the commit-time decision of `application/runtime.py`** (role, active, assigned, source state);
  version CAS, operation replay and effect persistence are deliberately not modelled and are listed as not proven.
* **Negative controls are mandatory evidence.** `bend_controls.py` generates unsafe models (the kernel's
  `examples/unsafe-teacher-final-approval.json`, and faults against each other law, one at the engine level). The unchanged
  proofs must fail on each, exactly the laws each was designed to break must fail (each law is checked alone by slicing the
  two files), and a Bend-evaluated counterexample must show the property is really violated. The test suite requires every
  law to be targeted by a control.
* **Conformance is a differential test, and is labelled as one.** Bend's `step` is compared cell by cell with the real
  runtime on the runtime verification matrix (225 cells) and on witness traces; the traces also show the safe path is
  reachable, so the laws are not vacuous.
* **Claims.** A `bend_proof` PASS requires: `main.bend` current; full `--verdict` result; per-law results; every control
  failing as designed; conformance agreeing. The report lists what is not proven. No lane text may describe the result
  as a proof of the Python runtime, of SQLite behaviour, or of the completeness of the laws.
* **Generation refuses** state/role/action/effect names that are not valid, unique Bend constructor names or collide with
  the fixed part of the program, rather than emitting a model that means something else.

### Consequences

* Good: the proved model cannot silently drift from the code; a green proof is accompanied by evidence that it can
  turn red; the limits are in the report next to the result.
* Bad: the engine template is a second implementation of the runtime decision that must be kept in step (the conformance
  test is what detects a divergence); new operators in the kernel require a template change and new laws.
* Revisit when: the kernel gains a new guard or operator (AGENTS.md: every new operator needs semantics, projection,
  identity effects and a negative oracle), or trace conformance from the TLA+ lane can replace the matrix comparison.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Pydantic (already the `Workflow` contract) | Bend has no JSON or Python import; a text generator is needed | `bend_generate.py` emits Bend source; replace when Bend gains structured import |
| pytest, Docker | Reused for tests and the container | none needed |
| mutmut/cosmic-ray (mutation lane) | They mutate Python code, not a Bend model; the controls seed model faults deliberately and attribute them to named laws | The mutation lane may add Python-level mutants; the model controls remain |
