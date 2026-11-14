# ADR-0246: The kernel refuses undeclared roles, judges path laws alike, and fails value guards closed

* Status: accepted
* Date: 2026-11-13
* Lane: kernel (Fagan inspection of the kernel)

## Context and problem statement

A Fagan inspection of the kernel ([inspection record](../quality/inspection-2026-11-13-kernel.md)) read the policy,
the model contracts, the law judges, the value guards, the edit vocabulary, the impact ripple and the runtime against
their ADRs. It found eight defects (K1 to K8). The ones that change kernel semantics:

* The policy let a transition be held by a role the pack does not declare, though it refuses an undeclared initiator
  (ADR-0231) and the pack loader refuses an undeclared role in a pack's own model.
* The table judge of `path_requires` counted a new record in the initial state as entering it without the waypoint;
  the run judge and the law proof did not. The two judges of one law disagreed, so the policy refused models no run breaks.
* A value guard ordered any text against a date as a string, and let a list or an object reach the comparison, where it
  raised `TypeError` out of `execute`.
* `add_transition` could not give an action with a value guard, a time event or a linked step a second source, which
  ADR-0232 allows.
* The impact ripple ignored changes outside the transitions (how a record starts, linked lifecycles).

## Decision drivers

* One rule, one meaning: where two judges decide the same law, they agree.
* Fail closed with a stable code; never a raw exception out of the kernel.
* Existing models, packs, hashes and reports keep their bytes.

## Considered options

* For K1: a code naming the role (`UNDECLARED_ROLE:Ghost`, like `UNDECLARED_INITIATOR`), or one naming the transition.
* For K2: make the run judge count a new record as entering the initial state, or make the table judge not count it.
* For K7: list model-level changes beside the report, or map each to the actions it affects.

## Decision outcome

* **K1**: `policy.declared_codes` adds `UNDECLARED_ROLE:<transition id>` for each transition held by an undeclared role
  (`UNDECLARED_ROLE:<action>` since the amendment below).
  The transition id is pattern-checked; a role is free text, and the policy codes are drawn into diagram notes, where a
  hostile role name could inject markup (`tests/test_diagrams.py` caught that with the role in the code).
* **K2**: the table judge of `path_requires` asks whether some step enters the state from a state a record reaches
  without the waypoint, as `path_requires_kind` already does. A new record has taken no step. Unchanged for any state
  other than the initial one.
* **K3, K4**: `ValueGuard.holds` orders text against a date only when the text is a real date, and a value that is not a
  bool, a number or a string is no kind a guard compares. Both fail closed (`VALUE_GUARD_DENIED` at runtime).
* **K5**: `add_transition` gives a new source of an existing action that action's value guards, time event and linked
  steps, so its transitions stay alike. #257 landed the same fix (`transactions._another_source`) while this was open;
  its code is kept and the K5 tests here cover it.
* **K6**: `value_guards.points` keeps `1` apart from `True` and `0` apart from `False`.
* **K7**: `model_impact` adds `model_changes` (only when non-empty) naming `initial_state`, `initiators`, `receives` or
  `objects`. A start change roots a `record-start` node rippling to the review packet; a lifecycle change marks the
  actions that move that object as changed.
* **K8**: each initiator and each linked-object state is a 1 to 60 character name, as every other role and state is.

The composite-tree helpers moved from `models.py` to `domain/state_tree.py` unchanged, to keep `models.py` above the
maintainability floor (MI-01) after the additions.

### Consequences

* Good: every shipped pack's model still passes the policy; every committed model hash, report and receipt is
  unchanged (`model_changes` is absent when empty).
* Good: each defect has a regression test in `tests/test_kernel_inspection.py` that fails on the code before the fix,
  and the file is in the mutation selection of `policy.py`, `models.py`, `laws.py` and `value_guards.py`.
* Bad: a stored candidate that gave an action to an undeclared role is now `POLICY_BLOCKED`. No such candidate can run,
  so nothing that worked stops working.
* Bad: kernel change, so it needs owner source review (#80).
* Revisit when: the pack gains a way to declare a role from PlayIDE; `UNDECLARED_ROLE` then points at that edit.

## Amendment, 14 November 2026: `UNDECLARED_ROLE` names the action

The integration review of the day's fixes ([record](../quality/inspections/2026-11-14-integration-review.md), I3)
changed K1's code from `UNDECLARED_ROLE:<transition id>` to `UNDECLARED_ROLE:<action>`.

* A role belongs to the action: every transition an action labels shares it (ADR-0232), so a transition-id code
  repeated one refusal once per source state.
* The code is only reported for an action the pack declares, so the name is the pack's, like `GUARD_POLICY:<action>`
  and `EFFECT_POLICY:<action>`. The reason for avoiding the free-text role in a code, markup in diagram notes, still
  holds.
* The SMT grammar has one slot per action. With transition ids, the generated clause had to name a slot `TR-<ACTION>`,
  and `laws_gate` mapped each pack's own transition ids to those slots (`_by_slot`, from #261). Both encodings, the
  legacy oracle and the policy now name the action, and the mapping is gone.

Nothing stored used the old form: the code shipped on 13 November and no model that has it can run.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| none | No new module or dependency; fixes to existing kernel functions, and one module split out of `models.py` | none needed |
