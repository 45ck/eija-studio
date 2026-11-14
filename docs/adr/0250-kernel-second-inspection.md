# ADR-0250: Who starts a record is checked like who acts, and a law never protects a state that is gone

* Status: accepted
* Date: 2026-11-14
* Lane: kernel (second, deeper inspection of the kernel)

## Context and problem statement

The first inspection of the kernel ([ADR-0246](0246-kernel-inspection-fixes.md)) read each kernel function against its
own ADR. A second pass ([inspection record](../quality/inspection-2026-11-14-kernel.md)) read how the features meet:
starting a record against acting on one, laws against the edits that rename what they name, and each executor of the
kernel (Studio preview, Simulate, the app oracle, the law proof, the built app) against the others. It found three
defects:

* `runtime.initialise` knew only the creator's role. The built app refused a revoked actor starting a record with
  `ACTOR_REVOKED`, and its oracle expected that, but wrote the expectation down by hand. Simulate asked the kernel, which
  said yes: in every shipped pack, revoked users started records (277 in a 500-step run of each pack).
* Laws name states. `rename_state` renames a state everywhere in the model, but not in the pack's protected laws. A law
  about `Returned` then judged a model with no `Returned` and held without protecting anything. Renaming the end state of
  a loan and then letting a Member's `Cancel` enter it passed the policy, though each law about that state forbids it.
  Removing a state did the same. This affected 27 states across 10 of the 11 shipped packs.
* `execute`, `initialise` and `receive` judged a model under whatever pack they were given. Every application entry
  point refused a workflow of another pack (`WORKFLOW_PACK_MISMATCH`), but the kernel itself did not. A model named for
  one pack could pass another pack's policy and run as its workflow.

## Decision drivers

* One rule, one place: the kernel decides, and the executors and oracles ask it.
* A protected law never goes quiet because of an edit the IDE offers.
* Existing models, packs, hashes and oracles keep their bytes.

## Considered options

* For starting a record: check the actor in each caller (Simulate, the built app, the oracle), or in the kernel.
* For laws on a missing state: rename the state inside the laws too (but laws are protected; the IDE never writes them),
  refuse `rename_state` and `remove_state` on a protected state, or judge a law that protects a missing state broken.

## Decision outcome

* **Starting a record (D1)**: `initialise(..., actor_id=...)` asks the session for the actor (`UNKNOWN_ACTOR`), refuses
  a revoked one with `ACTOR_REVOKED`, and judges their role against the model's initiators. Simulate starts records
  through it and logs a refused start as a `REFUSED` step with `start: true`, counted under `starts_refused`. The app
  oracle's `create_cases` asks the kernel, and its expectations are byte-identical. `role=` stays for previews and
  oracles that start a record on the kernel's behalf.
* **Laws on a missing state (D2)**: a law that protects one state is broken when the model does not have that state:
  `state_final`, `role_never_enters`, `state_only_via`, `only_kind_enters`, `path_requires` and `path_requires_kind`
  (`laws.PROTECTING`). Its own code is reported, with refs `law:<id>` and `state:<state>`. A law that requires something
  of a state (`action_target`, `action_source_in`, `can_reach_end`, `closed_shape`) is already stricter without it,
  and is unchanged. The generated SMT encoding (`verification/smt/laws_gen.py`) has the same rule, and its differential
  agrees with `check_policy` on every candidate of every shipped pack. Refusing the edits instead would leave a
  model imported or written by hand unprotected; judging the law covers every way a state can go.
* **Model and pack (D3)**: the runtime refuses a model whose id is not its pack's with `WORKFLOW_PACK_MISMATCH` before
  the policy check, as every application entry point already did.

### Consequences

* Good: every shipped pack's model and supported meaning still passes; every committed oracle, hash and report is
  unchanged, except Simulate's reports, which no longer contain records started by revoked users.
* Good: each defect has a regression test in `tests/test_kernel_inspection_2.py`, and the file is in the mutation
  selection of `laws.py` and `runtime.py`.
* Bad: a pack author who writes a law protecting a state that only a meaning adds must scope it with `when`, or the
  baseline is refused. No shipped pack does this.
* Bad: a model that drops a protected state on purpose needs its pack's laws changed too. That is a change to protected
  policy, so a person makes it.
* Bad: kernel change, so it needs owner source review (#80).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| none | No new module or dependency; fixes to existing kernel functions | none needed |
