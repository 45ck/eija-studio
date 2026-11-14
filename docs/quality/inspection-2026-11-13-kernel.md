# Inspection of the kernel, 13 November 2026

A Fagan-style inspection of the kernel: the code that decides what a model means. Each work product was read line by
line against its ADRs, and every defect is logged with a severity and a location. Severity: **major** changes what the
kernel allows, refuses or reports, or crashes it; **minor** is a gap a user meets only at an edge. The property and
mutation suites were extended the day before (ADR-0239), so this reading looked for what they cannot see: spec and code
that disagree, two judges of one law that disagree, and inputs no generator produces. Decision record:
[ADR-0246](../adr/0246-kernel-inspection-fixes.md).

## What was inspected

| Work product | Read against |
|---|---|
| `domain/policy.py` (declared codes, transactions, meanings) | ADR-0231, ADR-0232, the pack loader's `_model_problems` |
| `domain/models.py` (`Transition`, `ValueGuard`, `Delay`, `LinkedObject`, `Composite`, `Workflow`) | ADR-0232, ADR-0234, ADR-0237, ADR-0240, ADR-0241, ADR-0242 |
| `domain/laws.py` (table and run judges for every law kind) | ADR-0210, ADR-0221, ADR-0233, the `path_requires_kind` judges as a reference |
| `domain/value_guards.py` (representative values) | ADR-0234, ADR-0239 |
| `domain/transactions.py` (the edit vocabulary) | ADR-0232, ADR-0240 |
| `domain/linked.py`, `domain/signals.py`, `domain/data.py` (record values and references) | ADR-0235, ADR-0241, ADR-0242 |
| `domain/impact.py` (what a change ripples to) | ADR-0231, ADR-0241, the review packet in `application/compiler.py` |
| `application/runtime.py` (`execute`, `initialise`, `receive`) and `application/memo.py` | ADR-0199, ADR-0231 to ADR-0242 |
| `application/law_proof.py` (exhaustive search over the kernel) | ADR-0166, ADR-0221, ADR-0233 |

Checklist applied to each function: boundary cases (empty, initial state, one past a limit), error paths (does every
refusal come out as a `DomainError` with a stable code), ordering and determinism, spec against code, the same rule
judged in two places, and dead or duplicated logic.

## Defect log

| ID | Severity | Location | Defect | Status |
|---|---|---|---|---|
| K1 | major | `domain/policy.py`, `declared_codes` | The policy refused an undeclared initiator (ADR-0231) but not a transition held by an undeclared role. `set_role` to `Ghost` on library-loan `Cancel` passed the policy, and so did the same edit on 63 of the 87 transitions across the shipped packs. No actor can hold such a role, so the action can never run, and role laws (`only_role_holds`, `role_never_holds`) do not catch it. The pack loader already refuses this in a pack's own model. | Fixed: `UNDECLARED_ROLE:<transition id>`. The code names the transition, whose id is pattern-checked, not the free-text role, so a hostile role name cannot reach a diagram's policy note. |
| K2 | major | `domain/laws.py`, `_path_breaks` | A `path_requires` law on the initial state was always reported broken by the table judge: `reachable` counts the start, so a new record "reached" the state without passing the waypoint. `evaluate_run` and the law proof judge that a new record takes no step and do not count it. So the policy refused models that no run breaks, such as `A -> B -> A` with "back to A only via B". `path_requires_kind` already got this right. | Fixed: the table judge asks whether some step enters the state from a state reached without the waypoint. Unchanged for every other state. |
| K3 | major | `domain/models.py`, `ValueGuard.holds` | An ordering guard against a date compared any text as a string. `[due < 2026-12-01]` held for `"1999"`, `""` and `"2026-1-5"`. The ADR says a value of another kind never satisfies a guard. | Fixed: only a real `YYYY-MM-DD` date is ordered against a date; other text fails closed. |
| K4 | major | `domain/models.py`, `_kind` | Anything that was not a bool or a number counted as text, so a list or an object reached the comparison. Under an ordering guard, `runtime.execute` raised a raw `TypeError` (a 500) instead of refusing. | Fixed: a list, object or bytes is no kind a guard compares, so it fails closed with `VALUE_GUARD_DENIED`. |
| K5 | minor | `domain/transactions.py`, `_add_transition` | ADR-0232 lets one action leave several states while its transitions are alike. `add_transition` built the new one from the pack's declaration only, so for an action with a value guard, a time event or a step on a linked object it differed from the existing one and the edit was refused as incoherent. refund-desk `EscalateStale` (`after(2 days)`) and ai-ops `OpenWindow` (`target.lock`) could never gain a source. | Fixed on `main` at the same time by the re-inspection of merged PRs (#257, `_another_source`), which also names a different target or role; this branch keeps that fix and adds its regression tests. |
| K6 | minor | `domain/value_guards.py`, `points` | `dict.fromkeys` merged `True` with `1` and `False` with `0`. For an attribute guarded both as true/false and as a number, the law proof and Simulate never tried the numbers. With `Cancel [x = 1]`, the proof never reached `Cancelled` and judged laws about it vacuous. (The build refuses such a model against a data model with `VALUE_GUARD_TYPE`; the proof runs without one.) | Fixed: points are kept apart from truth values. |
| K7 | major | `domain/impact.py`, `model_impact` | The ripple looked only at transitions. A change to who may start a record, the initial state, the signals that start one, or a linked object's lifecycle had an empty impact, though its semantic hash changed and the kernel behaves differently. The review packet showed nothing affected. | Fixed: `model_changes` names such a change (present only when there is one, so other reports keep their bytes). A start change roots a `record-start` node that ripples to the review packet; a lifecycle change marks the actions that move that object. |
| K8 | minor | `domain/models.py`, `Workflow.initiators` and `LinkedObject.states` | Each initiator and each state of a linked object's lifecycle was an unbounded string, `""` included, where every other role and state name is 1 to 60 characters. | Fixed: both are 1 to 60 characters. The committed JSON schemas and OpenAPI are regenerated. |

## Before and after

Output of one probe script, run on `main` and on this branch (the regression tests in `tests/test_kernel_inspection.py`
assert the "after" column and fail on `main`: 27 failing cases).

| ID | On `main` | With the fix |
|---|---|---|
| K1 | policy codes after giving `Cancel` to `Ghost`: `[]` | `['UNDECLARED_ROLE:TR-CANCEL']`; `['UNDECLARED_ROLE:Cancel']` since 14 November |
| K2 | `path_requires(state=A, via=B)` on `A -> B -> A`: `['BACK_VIA_B']` | `[]` |
| K3 | `[due < 2026-12-01]` for `"1999"`, `""`, `"2026-11-30"`: `[True, True, True]` | `[False, False, True]` |
| K4 | `execute` Cancel with `due = ["2026-01-01"]`: `TypeError: '<' not supported` | `DomainError VALUE_GUARD_DENIED` |
| K5 | add a source to `EscalateStale` / `OpenWindow`: `EDIT_INVALID ... incoherent` | added, with `after(2 days)` / `target.lock` |
| K6 | points for `[x = true]`, `[x = 1]`, `[x = 0]`: `[None, True, False, -1, 0.5, 2]`; proof reaches 4 states | `[None, True, False, -1, 0, 0.5, 1, 2]`; proof reaches `Cancelled` too |
| K7 | impact of "only Librarian may start a record": nothing affected | `model_changes: ['initiators']`, review packet affected |
| K8 | a 61-character initiator: accepted | `ValidationError` |

None of these shows in PlayIDE without an edit the UI does not offer (a role outside the pack, a list as a record
value, a mixed true/false and number guard), so the evidence is the kernel's own output rather than screenshots.

## Checked and found correct

- `runtime.execute` checks authority before the replay lookup and the version before the state, as ADR-0232 says; a
  replay of an action that has since moved the record still finds its transition, because every transition of an
  action shares its role.
- `separation_breach` reads the record's whole history in a sorted, deterministic order; the act is logged in the same
  unit of work as the step.
- `Delay.due` fails closed on an unknown or non-finite elapsed time; `check_linked` refuses an unknown object or state.
- `receive` binds the record values into the operation fingerprint and refuses before the replay lookup when the model
  no longer receives the signal.
- `transition_for` falls back to any transition of the action only for the authority check; `STATE_DENIED` still
  follows when the action does not leave the record's state.
- Composite trees: `_acyclic`, `_known_children` and `_remove_state` keep a composite non-empty and its initial child present.
- The identity memo (`ensure_conforms`) keys on the check function too, so a different check is never served a cached pass.

## Logged, not changed

- The law proof checks separation of duties only where one listed action directly follows another (as its docstring
  says). The kernel itself checks the whole history, so this is a limit of the proof's evidence, not a hole in the
  kernel.
- `[x = 1]` and `[x = 1.0]` hash differently (`guard_keys` compares JSON). They mean the same; the only effect is that
  two transitions of one action written that way are refused as unalike.

## Follow-up: the SMT-gated tests

K1 turned two tests red that run only with the `smt` extra (z3) installed, so the fast tier without z3 skipped them:
`tests/test_pack.py::test_pack_policy_equals_legacy_policy_on_every_smt_differential_candidate` (540 disagreements:
the frozen legacy oracle did not know `UNDECLARED_ROLE`) and `tests/test_formal_smt.py::test_committed_snapshot_matches_regeneration`
(the hand SMT encoding, which the snapshot check runs against `check_policy`, did not either). Fixed: the legacy oracle,
the hand encoding (`verification/smt/encoding.py`) and the generated one (`verification/smt/laws_gen.py`) each gained
the rule, written independently; `accepted_set.json` was regenerated and only its source hashes changed, because on
the excursion pack an undeclared role already breaks `PROTECTED_AUTHORITY`. `UNDECLARED_ROLE` is not reported for a
transition of an undeclared action, which is `UNSUPPORTED_ACTION` already. The generated encoding names the action's one
transition slot (`TR-<ACTION>`), while a pack may name that transition otherwise (ai-ops `StartBuild` is `TR-BUILD`), so
`laws_gate.differential` compared `UNDECLARED_ROLE` codes by slot (`_by_slot`); found by Codex review of #261. On 14 November the code was changed to name the action and `_by_slot` removed (ADR-0246 amendment). Run the SMT tests after any policy change:
`pip install -e '.[smt]'`.

