# Second inspection of the kernel, 14 November 2026

The first inspection ([13 November](inspection-2026-11-13-kernel.md), ADR-0246) read each kernel function line by line
against its own ADR. This second pass looked where that one did not: how the features meet, invariants that held only
because every caller happened to keep them, and whether every executor of the kernel gives the kernel's answer. It
also checked that the day's kernel-adjacent merges agree with the kernel. Severity: **major** changes what the kernel
allows, refuses or reports; **minor** is a gap a user meets only at an edge. Decision record:
[ADR-0250](../adr/0250-kernel-second-inspection.md).

## What was inspected

| Area | Read against |
|---|---|
| Starting a record: `runtime.initialise` and every caller (Studio preview, Simulate, the law proof, permissions and reach, the app oracle, the built app's `create`) | ADR-0231, ADR-0242, the built app's template |
| Laws against edits: every law kind against `rename_state`, `remove_state`, `set_initial` and removing an action | ADR-0210, ADR-0221, ADR-0232, the pack loader's law checks |
| The kernel's own entry points against the application's: `execute`, `initialise`, `receive` | ADR-0199, every `WORKFLOW_PACK_MISMATCH` caller |
| Executors: `runtime`, `simulation.MemorySession`, `oracle_session.OracleSession`, `law_proof`, SCXML projection | ADR-0150, ADR-0152, ADR-0237, ADR-0240, ADR-0241 |
| Feature pairs: time events with composites and self-loops; value guards with signals; linked objects with shared objects and two links to one class; separation of duties with replay and record creation | ADR-0233 to ADR-0242 |
| Today's merges touching the kernel's neighbours: #251 (Simulate slips), #257 (`_another_source`, lifecycle conflicts), #260 (object cases), #261 (SMT encodings) | the kernel after #258 |

## Defect log

| ID | Severity | Location | Defect | Status |
|---|---|---|---|---|
| D1 | major | `application/runtime.py`, `initialise`; `application/simulation.py`, `_step` | The kernel refuses a revoked actor every action, and the built app refused one starting a record, but `initialise` knew only a role. Simulate asked the kernel and let revoked users start records in every shipped pack, though its own docstring says the kernel refuses them. The app oracle wrote the built app's expectation by hand instead of asking the kernel. | Fixed: `initialise(actor_id=...)` refuses an unknown (`UNKNOWN_ACTOR`) or revoked (`ACTOR_REVOKED`) actor and judges their role against the initiators. Simulate and `create_cases` use it; the oracle's bytes are unchanged. |
| D2 | major | `domain/laws.py`, `evaluate_table` | A law names a state. Renaming or removing that state left the law judging a model without it, where it held vacuously. Rename `Returned` and let a Member's `Cancel` enter the renamed state: the policy passed it, though three laws about `Returned` forbid it. 27 protected states in 10 of 11 shipped packs could be laundered this way. | Fixed: a law that protects one state is broken when the model lacks it (`laws.PROTECTING`). The generated SMT encoding has the same rule. |
| D3 | minor | `application/runtime.py`, `execute`, `initialise`, `receive` | Every application entry point refused a workflow of another pack, but the kernel did not. It judged a model under any pack it was given, and a model named for one pack could pass another's policy and run as its workflow. | Fixed: `WORKFLOW_PACK_MISMATCH` before the policy check. |

## Before and after

The output of one probe script, run on `main` (41369a2) and on this branch. The regression tests in
`tests/test_kernel_inspection_2.py` assert the "after" column; on `main` the file does not even import (`PROTECTING`).

| ID | On `main` | With the fix |
|---|---|---|
| D1 | Simulate, 11 packs, seed 1, 500 steps: 277 records started by revoked actors; `initialise` has no `actor_id` | 0; `initialise(actor_id="librarian-revoked")` gives `ACTOR_REVOKED`, logged as a refused start |
| D2 | library-loan: rename `Returned` to `Done`, then retarget `Cancel` (Member) to `Done`: accepted | `POLICY_BLOCKED`: `FINAL_STATE_LEFT:Returned`, `LOAN_RETURN_WITHOUT_CHECKOUT`, `PROTECTED_STATE:Returned` |
| D3 | `initialise` of a library-loan model named `excursion` under the library-loan pack: record created | `WORKFLOW_PACK_MISMATCH` |

PlayIDE shows D1 in Simulate's run log. On `main` a revoked user appears as "created R4". Now the log reads "tried to
start a record: refused, ACTOR_REVOKED", and break-on-refusal stops there, on the initial state. D2 shows when a state
is renamed on the canvas: the rename is now refused at review with the laws it breaks. D3 needs a crafted model.

## Today's merges against the kernel

- #251 (Simulate counts a slip against its state): agrees. A refused start now uses the same path (`transition`
  None, `from` the initial state), so break-on-refusal names the initial state.
- #257 (`_another_source`, `lifecycle_conflicts`): agrees. Two links to one class must declare one lifecycle, so
  the built app's `object_cases`, which take the first lifecycle of a class (#260), cannot pick the wrong one.
- #260 (object cases, signals over HTTP): agrees. Signal-started records skip `initiators` by design (ADR-0242).
- #261 (`UNDECLARED_ROLE` in the SMT encodings): agrees. The generated encoding's differential, swept over all 11
  packs with every single mutant, shows 0 disagreements with D2 in place.

## Checked and found correct

- Time events: every committed step, a self-loop included, restarts the clock in all three sessions (the kernel's
  port contract, `MemorySession`, `OracleSession`). An unknown entry time is never due.
- Linked objects: one transition moves each link once, so the runtime's per-step object states and `linked._moved`
  agree. A missing link (an optional reference left empty) fails closed with `LINKED_OBJECT_REFUSED`.
- Value guards: a record started by a signal has no values the kernel reads, so every guard on its steps fails closed.
  Unicode digits are not a date (`date.fromisoformat` refuses them after the pattern matches).
- Policy notes in diagrams: hostile initiator names, newlines included, stay escaped in every emitted format.

## Logged, not changed

- A time event on a transition SCXML hoists onto a composite reads, in UML, as time in the composite. The kernel
  measures time in the current leaf state. The SCXML export sends `elapsed` as event data, so the two engines agree, but
  a person reading the chart could expect the UML meaning.
- Composites are part of the semantic hash, though they never change what a step does (ADR-0240). Regrouping states
  makes Studio preview records stale. Changing this would change committed hashes.
- `after(1 days)` and `after(24 hours)` mean the same but compare unequal, so two transitions of one action written
  that way are refused as unalike (the same limit as `[x = 1]` and `[x = 1.0]` in the first inspection).
- Separation of duties does not count creating a record as an act. A creator may take any one listed action. No
  shipped pack has a `distinct_actors` law; a pack that needs "the raiser never approves" lists the raising action.
- Laws are judged on the transition table without value guards, time events or linked objects, so the policy can
  refuse a transition no run can take. The law proof judges runs and is the reference.
