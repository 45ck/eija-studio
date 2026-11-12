# ADR-0234: Guards over record values

* Status: accepted
* Date: 2026-11-11
* Lane: kernel / executable UML

## Context and problem statement

Issue #93, item 1. UML state machines write guards on transitions: `Approve [amount <= 500]`. Until now, a transition's guards were only about the actor (active, role, assignment), the state, the version and the operation id. A rule such as "a clerk approves small refunds, and larger ones go to a supervisor" could only be drawn as a note. The data model (ADR-0153) already types the record's attributes, and the generated app stores checked values. The kernel never read them.

## Decision drivers

* The kernel decides. A guard is checked at commit time in `runtime.execute`, in the same unit of work, not in a page or a template.
* Fail closed. A missing value, or a value of another kind, never satisfies a guard.
* Every existing model, digest, hash, oracle and recording keeps its exact bytes.
* Every checker that runs the model sees the same rule: the law proof, Simulate, the generated app's conformance oracle and the SCXML differential.

## Considered options

* A typed comparison of one record attribute with a constant, `{attribute, op, value}`, on a transition (chosen).
* An expression language over values (`amount * 2 > limit and ...`): more general, but it needs a parser, a type checker and an encoding in every checker. Revisit when a pack needs it.
* Guards on the action in `pack.json` instead of on the transition: it would hide the guard from the model, the diagrams and the diff.

## Decision outcome

**The model.** A transition may carry `conditions`, up to eight `{attribute, op, value}` guards that must all hold. `op` is one of `eq`, `ne`, `lt`, `le`, `gt` and `ge`.
* The value is a number, a date (`YYYY-MM-DD`), text or true/false.
* Ordering works on numbers and dates only. True/false is compared only with = or ≠.
* When there are no conditions, the field is left out of every dump. That keeps the bytes and the semantic hash of every existing model. The semantic hash sorts conditions, because they are a set.
* Every transition one action labels must carry the same conditions (ADR-0232).

**The data model.** `value_guards.guard_problems` checks guards against the record class: the attribute exists, and the constant fits its type and its choices. `eija build` refuses a model whose guards do not fit, with `VALUE_GUARD_INVALID`.

**The runtime.** After the state check, a transition with conditions reads the record's values through a new `UnitOfWork.values` port. Unless every guard holds, it refuses with `VALUE_GUARD_DENIED`, naming the transition and the attribute. A transition without conditions never calls the port. The Studio's preview records hold no values, so a guarded transition is always refused there. The generated app reads its record's checked `fields`.

**Values that stand for all values.** A guard's truth depends only on which side of each constant a value falls, so `value_guards.points` picks a finite set that covers every region:
* for numbers and dates: each constant, a point below the lowest, a point above the highest, and a point between each neighbouring pair;
* for text and choices: each constant and one other value;
* for true/false: both;
* for every attribute: no value at all.

`valuations` takes one point per guarded attribute, up to 256 combinations. Beyond that, the law proof reports UNKNOWN.

**The checkers.**
* **Law proof.** It runs one search per combination of values, since a record's values never change. It judges `can_reach_end` for each combination, so a record that some values strand is reported, together with those values.
* **Simulate.** It gives each new record one seeded combination, but only for a model with guards, so other seeded runs are unchanged.
* **Generated app.** The oracle gains `value_cases`: every combination for each guarded transition, tried by an actor who may take it. The conformance template checks them, so it now runs nine tests. The app's action options use the same check.
* **SCXML.** A guard becomes a `cond` term over event data: `has_<name> and value_<name> <op> <constant>`. The engine resets datamodel variables on the first restored machine, so the values travel in the event, as the actor does. The differential runs the value cases too.
* **Formal encodings.** TLA+, SMT and BMC refuse a workflow with value guards (`OutsideFormalScope`) instead of encoding it as if it had none.

**The diagrams** write UML's `event [guard]` on the edge, and the diff reports a change of conditions.

### Consequences

* Good: "small refunds by a clerk, large ones by a supervisor" is a rule the kernel enforces, and a reviewer reads it on the state diagram.
* Good: nothing changes for a model without guards.
* Bad: one attribute compared with one constant. There is no arithmetic and no comparison between two attributes.
* Bad: values never change during a run, because there is no action that edits a record's values. When one is added, the law proof's "values never change" assumption must change with it.
* Bad: the TLA+, SMT and BMC encodings do not model guards. The law proof, the oracle and the SCXML differential carry the evidence for guarded models.
* Revisit when: a pack needs arithmetic or a comparison between attributes, actions edit values, or a formal encoding should cover guards.

## Amendment, 12 November 2026: tests and permissions give the record values

Walking PlayIDE in a browser with a guarded pack showed three places where "the Studio's records hold no values" made
the IDE wrong rather than careful:

* **Tests and sequences.** A scenario could not pass a guarded transition, so every test of a guarded happy path failed
  with `VALUE_GUARD_DENIED` and the Sequences tab drew it red. A scenario may now give the record's values,
  `"values": {"renewals": 1}`, which the kernel's guards read (`scenario_run`; the recorder takes them too). The field is
  left out of the dump when empty, so every existing `scenarios.json` keeps its digest. The Tests tab reads "Given a new
  record in Requested with renewals = 1", and a refusal by a guard names the guard and says to give the test values.
* **Permissions.** The matrix said no one may take a guarded action. A cell is about who may act, so each guarded cell
  is now tried on a record whose values meet its guards, picked from `value_guards.combinations`, and the cell shows
  `when [renewals ≤ 3]`.
* **Reachability.** A path is replayed on one record whose values meet every guard on it, and the answer says which
  values. No values meeting them all is `NOT_SHOWN`, never `REACHABLE`. The replay also tries each fixture actor of a
  role in turn, so a separation of duties law (ADR-0233) does not hide a path a second actor can finish.

The kernel is unchanged: it still fails closed on a record without values.
