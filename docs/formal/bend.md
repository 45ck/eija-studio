# Bend 2 machine-checked authority laws

This lane machine-checks EIJA's protected authority laws with [Bend 2](https://github.com/bendlang/bend)
(Apache-2.0, "a fast language that blocks AI mistakes via proof"). Evidence kind: `bend_proof`
([ADR-0018](../adr/0018-formal-vv-portfolio.md), decisions in [ADR-0025](../adr/0025-bend-machine-checked-laws.md)
and [ADR-0026](../adr/0026-bend-model-generation-controls-conformance.md)).

The one-sentence claim: **for the Bend model generated from the executable `Workflow`, eight laws about who
may approve, what must precede approval, who may recommend, where rejection may start and which effects may
be emitted hold for all actors, all states and all command sequences, checked by Bend's proof kernel.**
The claim is about the model. It is not a proof about the Python runtime (see [What is not proven](#what-is-not-proven)).

## What is in `verification/bend/`

| File | Written by | Role |
|---|---|---|
| `main.bend` | **generated** by `bend_generate.py` from the Python `Workflow` | The model: states, roles, actions, effects, one `Rule` per transition, `step` (one command) and `replay` (a sequence). Two slots: `Baseline` and `Candidate` (recommend_only). Committed; a drift check fails if it differs from regeneration. |
| `LAWS.bend` | human-readable, hand-written | The laws, stated once, in Bend. This is the file a reviewer reads and the file an AI must not edit to make a proof pass. |
| `PROOF.bend` | hand-written (by an AI agent in this lane), machine-checked | One `def Laws.<name>` per law, plus shared lemmas. It is checked, not trusted: the kernel accepts it or does not. |
| `Dockerfile`, `.dockerignore` | hand-written | Pinned checker image (below). |
| `bend_runner.py`, `bend_controls.py`, `bend_conformance.py`, `bend_slicing.py` | hand-written | Gate orchestration, negative controls, runtime conformance, per-law attribution. |
| `evidence/bend.json` | generated (maintainers, `--snapshot`) | Committed snapshot of a complete run; names the platform that produced it. |

## The laws

Each law quantifies over **every** actor (any role, active or revoked, assigned or not), action and state.
The two sequence laws also quantify over every command sequence of any length. Names are the Bend `law` names.

| # | Law | Applies to |
|---|---|---|
| 1 | `teacher_never_approves`: whatever a Teacher does, the accepted command never leaves the instance Approved | both models |
| 2 | `teacher_sequences_never_approve`: no sequence of teacher-only commands reaches Approved from the initial state | both models, all sequences |
| 3 | `approved_only_from_recommended`: any accepted command into Approved fires from Recommended | candidate |
| 4 | `every_path_to_approved_passes_recommended`: every path to Approved passes through Recommended | candidate, all sequences, any actors |
| 5 | `revoked_teacher_cannot_recommend`: a revoked teacher can never recommend | both models |
| 6 | `unassigned_teacher_cannot_recommend`: an unassigned teacher can never recommend, active or not | both models |
| 7 | `reject_only_from_declared_source`: Reject is accepted only from the model's declared rejection source (Submitted in the baseline, Recommended in the shipped candidate) | both models |
| 8 | `forbidden_effects_never_emitted`: no command ever emits `PaymentCaptured` or `ParentDataExported` | both models |

Laws 7 and 8 restate two pieces of kernel policy by hand: the forbidden-effect list (`policy.FORBIDDEN`) and, per
model, the state a rejection leaves (`reject_source`). They are spec inputs written in `LAWS.bend`, not generated.
`bend_generate.py --check` (the `bend_drift` session) and the proof gate compare them with `policy.FORBIDDEN` and the
workflows' Reject transitions and fail on a difference, so a new forbidden effect cannot leave law 8 silently out of
date (a wildcard would have treated it as allowed). What the check does not do is decide whether the law is the right law.

Law 4 uses a run monitor: a run records whether it was ever in `Recommended`, and the law says a run in
`Approved` always has that record. It is proved by induction over the command sequence from an invariant
that every command preserves.

## How the proof is built (why it is not specific to the shipped tables)

`PROOF.bend` is written once and is independent of the numbers in the models:

1. **Engine lemmas** about `step` (a guard conjunction `permits` followed by `finish`, which either commits
   the rule's target and effects or changes nothing): `step_prop` reduces "prove P of a step" to "prove P when
   permitted" and "prove P when denied"; `permits_role` and `permits_from` extract the role and source-state
   facts from a permitted command.
2. **Table certificates**: closed computations over the finitely many (model, action) rules, for example "a rule
   owned by the Teacher role never targets Approved". A certificate is `Unit{}` exactly when the generated table
   satisfies the fact, so a model that violates a law makes the certificate, and therefore the proof, fail to check.
3. **Induction** over the command sequence for laws 2 and 4.

That is what lets the same, unchanged proofs be run against unsafe models as negative controls.

## Reproduce

Prerequisites: Docker (Docker Desktop on Windows), `python -m pip install -e ".[dev]"`. Building the pinned image
downloads about 300 MB of pinned Bend and Lean archives, so it is opt-in: pass `--build` (or set `EIJA_BEND_BUILD=1`)
the first time and after any Dockerfile change. Without the image the gate reports `NOT_RUN`; proof runs use no network.

```bash
python verification/bend/bend_generate.py --check          # fast: committed main.bend == regeneration
python verification/bend/bend_runner.py --build             # complete gate; writes reports/formal/bend.json
python verification/bend/bend_runner.py --quick             # skip per-law attribution of the controls
nox -s bend_drift                                           # fast tier
nox -s formal_bend_quick -- --build                         # full tier (needs Docker; --build only when the image is missing)
nox -s formal_bend                                          # release tier (needs Docker and the image)
EIJA_BEND_DOCKER_TESTS=1 python -m pytest tests/test_formal_bend.py   # the opt-in Docker test (same proof, same fault)
```

To run Bend by hand on the committed files (what the gate does, minus the reporting):

```bash
docker run --rm --network none -v "$PWD/verification/bend:/work:ro" "eija-bend-checker:2.0.32-$(sha256sum verification/bend/Dockerfile | cut -c1-12)" PROOF.bend --verdict
```
The image tag carries the first 12 hex digits of the Dockerfile hash, so worktrees with different Dockerfiles never overwrite each other's image.

The expected output is `ALL PROOFS CHECK`. `--verdict` rechecks every definition with BendTT, a small
kernel that Bend's authors prove sound in Lean. Without `--verdict` Bend prints `ALL PROOFS CHECK` and then
"Use --verdict for mathematical validity": that is only its front-end check. The gate never counts such output as a
proof (it classifies it `CHECKED_NO_VERDICT`), and every run it does count, including each per-law run, uses `--verdict`.

### Pins

| Component | Pin |
|---|---|
| Bend | 2.0.32, Linux x64 release archive verified by sha256 `5c365ddb12954d0933cef751802e0f7d9875f842edcb80f9661f89cd1a9ff7b6` (the pin of record; the same checksum the official installer checks). The git tag `v2.0.32` commit `573002f01ec6c52416d44489543f69a9625facf8` is declared in the Dockerfile and reported as `declared_bend_commit_unverified`: nothing ties the archive to it |
| Lean (only to compile the BendTT kernel) | 4.34.0, archive verified by sha256 |
| Base image | `ubuntu:24.04@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4` |
| Dockerfile frontend | `docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e` (the build stage also runs an unpinned `apt-get install zstd`; only the checksummed Lean archive and the recorded kernel hashes reach the verdict) |
| Container | `--network none --read-only --cap-drop ALL --security-opt no-new-privileges`, files mounted read-only |

The official installer (`bend-lang.com/install.sh`) always installs the latest release, so the image performs
its steps against a fixed version instead. The report records the image id and the Dockerfile hash of the run.

Reproducibility check (2026-09-28, Windows 11, Docker Desktop 29.8.0): a `docker build --no-cache` from the Dockerfile
rebuilt the image in about 2.5 minutes and produced the same BendTT kernel binary as the cached image
(`bendtt` sha256 `dade0de15006991fd731172ab5628571a0007b4955765ac04ae25da686fc8d35`, compiled from `bendtt.lean`
sha256 `7f6ef51c9f75d7de91c15f790fb3385189b1129e7bc13812c9d8aa30a2c73dec`), and `bend PROOF.bend --verdict` printed
`ALL PROOFS CHECK` on it. That is one observation on one machine, not a reproducible-build guarantee.

Docker unavailable, daemon stopped, or the image not built (and `--build` not given): the gate reports `NOT_RUN`
(exit code 3; a nox session is skipped) and never `PASS`. A proof run that starts and then times out or is killed (for
example out of memory) is a `FAIL` (exit code 1), not a skip; a timed-out container is removed.

## Evidence

`reports/formal/bend.json` (`kind: bend_proof`) records: the model `semantic_hash` of both slots and the
sha256 of `main.bend`, `LAWS.bend`, `PROOF.bend` and the generator; the Bend version, commit, image id and
platform; the full `bend PROOF.bend --verdict` result and, for each law, a result from running that law alone
(a slice of `LAWS.bend`/`PROOF.bend`) under `--verdict`; every negative control; the conformance results; and the
limits below. A snapshot of a complete run is committed as `verification/bend/evidence/bend.json`. The snapshot is
unsigned: tests check that its recorded hashes match the committed files (including the Dockerfile and the
generator), not that a run produced it. It is reproducible with `bend_runner.py --snapshot`, and an independent full
run matched it apart from the platform field.

### Negative controls (the trust anchor)

The unchanged proofs are run against models that violate a law. Each must fail, **exactly** the laws it was
designed to break must fail, and a concrete counterexample computed by Bend must show the property really is
violated (so "the proof fails" is backed by "the law is false here"):

| Control | Seeded fault | Laws that must fail |
|---|---|---|
| `teacher_final_approval` | `examples/unsafe-teacher-final-approval.json`: the Teacher performs Approve | 1, 2 |
| `approve_skips_recommendation` | Approve fires from Submitted | 3, 4 |
| `unassigned_may_recommend` | Recommend loses the `actor_assigned` guard | 6 |
| `reject_from_draft` | Reject fires from Draft | 7 |
| `payment_effect_emitted` | Approve declares `PaymentCaptured` | 8 |
| `engine_ignores_revocation` | the guard evaluator ignores `active` | 5 |

For the five model-level controls the kernel's own `check_policy` independently reports the fault
(`PROTECTED_AUTHORITY`, `PROTECTED_STATE`, `GUARD_POLICY`, `UNSUPPORTED_REJECTION_SOURCE`, `EFFECT_POLICY`); the
report records this next to Bend's verdict. Bend adds a machine-checked statement about *all sequences*, which the
policy check does not make. Every law is targeted by at least one control (tested).

### Conformance to the runtime (a differential test, not a proof)

Bend's `step` is evaluated on every cell of the runtime's own verification matrix (5 actors × states × 5 actions
for both models: 225 cells) and compared with `application.runtime.execute` in a disposable SQLite sandbox:
accepted or denied, the resulting state and the audit/outbox effect counts must agree cell by cell. Six witness
traces (safe path reaches Approved; teacher cannot approve after recommending; unassigned and revoked teachers are
denied; reject then revise; baseline approval) are run through both. The witnesses also show the safe path is
*reachable*, so the safety laws are not satisfied vacuously by a model that denies everything.

## What is not proven

* **Python runtime conformance.** The laws are about the generated Bend model. The differential test above is
  evidence that the model agrees with `execute` on a finite sample; it is not a proof that they agree everywhere.
* **What the model abstracts.** Instance `version` (compare-and-swap), operation replay and binding, audit and outbox
  persistence, crash durability, SQLite transactions, the HTTP layer, authenticity of the actor directory
  (a synthetic fixture), and the guards `expected_version` and `operation_binding` are not modelled. `role_current`
  is modelled as role equality with the fixture and `state_equals` as source-state equality.
* **The runtime's extra effect check.** The runtime additionally raises `EFFECT_DENIED` for effect kinds it has no
  adapter for. The model does not: it emits a rule's declared effects on success, which is more permissive, so law 8
  is at least as strong as the runtime.
* **Completeness of the laws.** Eight laws are not the whole policy. Nothing here shows they are the *right* laws;
  they are authored by the same team as the model and are not an independently blinded specification.
* **Soundness of `check_policy`** over the whole transaction grammar (the Z3 lane's claim).
* **Other faults.** The controls show sensitivity to six seeded faults, not that no other fault escapes the laws.
* **The tool chain.** Bend 2 is new software. `--verdict` shifts trust to BendTT, whose soundness theorem is Bend's
  authors' Lean development (for the declarative theory), which this project has not audited. The Bend front end
  that elaborates each `law` into a type, resolves imports and translates to BendTT input, and the parser of
  BendTT's input (`partial def`s), are trusted, unproven code outside that theorem. The Docker Desktop VM and host
  are trusted.
* **The guard semantics of the engine.** The generator derives each rule's role, source, target, effects and whether
  it needs the assigned guard from the Workflow. The conjunction that combines them (`permits`) is a fixed,
  hand-written template that equals the runtime's `check_actor` today (conformance agrees on 225 cells). The kernel's
  guard vocabulary is closed and generation refuses a guard the template does not model, but a change to what a
  guard means still needs a template edit and review.

Nothing in this lane edits the kernel, stamps the release fixture or weakens a policy to make a proof pass.
Providers and agents still never select meaning, approve or apply.

## Extending the laws

Edit `LAWS.bend` deliberately (a human decision, reviewed as a diff), add the proof to `PROOF.bend`, add a
negative control that breaks exactly the new law to `bend_controls.py`, add the law name to this page and to the
expected list in `tests/test_formal_bend.py`, regenerate with `bend_generate.py` when the model changes, and rerun
the gate. A law without a control that can break it has no demonstrated sensitivity, and the test suite says so.
