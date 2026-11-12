# ADR-0242: Conformance that catches a divergent app by behaviour

* Status: accepted
* Date: 2026-11-12
* Lane: app generation / verification

## Context and problem statement

The pitch for `eija build` (ADR-0150) is that the generated app's conformance tests prove the app matches its model. Until now that claim was checked from one side only: every pack's app passed its own tests. Nothing checked the other side, that the tests fail when the app does *not* match.

The repository's negative controls (`tests/test_appgen.py`, eight seeded breaks) all passed, but each one edited a generated file without resealing the build identity (`app/build-subject.json`). Every one of them was caught by the identity check in `setUpClass`, before any behavioural test ran. They showed tamper detection. They did not show that the behavioural tests would catch a wrong app that had been built consistently, such as one built from the wrong model or by a faulty template.

We built a harness that asks the real question. For library-loan, its first run found 30 of 130 single-element divergences that the generated suite missed (some later turned out to be equivalent; see below). The main holes:

* **The initial state was never checked.** Every case seeded its record straight into a state, so an app whose records started in `Cancelled` passed.
* **Only effect names were compared.** An audit entry written as a notification, a notification sent to the wrong recipient or to nobody, and a notification that names no record all passed. The last one was a real defect: every outbox row's `record_id` held the case id `app`.
* **No record was ever created and then acted on.** An app that did not stamp its records with their data model refused every action on them (`STALE_DATA`) and still passed.
* **Revoked and unknown actors were never tried at create time.** Who may start a record was checked only for models that name initiators.
* **The edges of the data rules were not checked.** A text limit one shorter, a dropped choice, or an optional attribute made required all passed.
* **What the app offers was not checked.** `options()` (the buttons and their reasons) could ignore the actor, the value guards or separation of duties.
* **The HTTP API was not checked.** It could drop the expected version or the record values, or answer a refusal with 200.
* **The rule table had a bug.** It was keyed by action, so an action that leaves several states (ADR-0232) showed only one source.
* **Three tests were empty for every shipped pack.** No shipped pack names initiators, carries a separation-of-duties law, has value guards or builds an association, so `start_cases`, `separation_cases`, `value_cases` and the reference checks never ran on a shipped app.

## Decision drivers

* A divergence must be caught by behaviour, not by a hash. Identity checks stay, but they cannot be the evidence.
* The oracle is still the kernel's answer (or the data model's), never the generator's reading of the model.
* No shipped pack changes, so models, digests, the law proofs and the SCXML charts keep their bytes.
* Use the open-source tools we already have. cosmic-ray (ADR-0033) mutates Python source, and the kernel lane uses it. Our divergences are mostly in models and data models, which are JSON contracts, so a source mutator cannot express them. The harness is a small, purpose-built generator of single-element changes (see the register).

## Decision outcome

**The harness.** `python -m verification.conformance.divergence` builds, for every shipped pack and two feature variants, real apps that are wrong in exactly one way. It runs each one's generated tests in a fresh process, as `eija build` does. The two families:

* **Model divergence.** The app is built from a model, data model or pack that differs in one element:
  * a transition is dropped, moved to another source or target, or given another role;
  * the assignment guard is added or dropped, or a required effect is added or dropped;
  * a value guard is dropped or flipped;
  * the initial state is moved, or an initiator is added or dropped;
  * an effect's kind or recipient is changed;
  * a fixture actor's active or assigned flag is flipped;
  * an attribute is dropped, retyped, made required or optional, given a shorter limit, or loses a choice;
  * a built association is dropped, unbuilt or given another multiplicity;
  * a separation-of-duties law is dropped.

  The app keeps the reviewed oracle and tests. Only the identity fields (model hash, data and screens digests) are pointed at the divergent app, and the build identity is resealed, so only behaviour can fail the suite.
* **Code divergence.** One of 23 seeded faults in `app/service.py` or `app/server.py`, resealed the same way. A fault in code a subject's app never reaches is not applicable to it, not missed. For example, a fault in the value-guard check applies only to a model with value guards.

Each divergence ends up CAUGHT, REFUSED (no app is built: the model is invalid or the protected policy refuses it), EQUIVALENT, or MISSED. Only one kind of divergence may be EQUIVALENT: dropping a forbidden effect. The kernel performs only required effects, and the policy checks forbidden ones at build time. Any MISSED divergence fails the check. For each law, the harness also runs the law proof on every model divergence, and every divergence the proof finds BROKEN must be CAUGHT or REFUSED.

The two feature variants exist only in the harness, so the shipped packs keep their bytes:

* refund-desk with initiators, a separation-of-duties law and a value guard;
* library-loan with its record's associations built, and `Return` leaving two states.

**The oracle gains four lists, and the generated suite gains five tests** (it now runs 16, with the time-event test from ADR-0237 and the linked-object test from ADR-0241):

* `written` on every committed case and journey step holds the kernel's audit entries and outbox rows `[effect, recipient]`, recorded by the oracle session. The effects test compares them, and checks that each outbox row names the record.
* `create_cases`: every fixture actor, and one unknown actor, starting a record with valid values. The case gives the state and version the record starts in, or the refusal (`UNKNOWN_ACTOR`, `ACTOR_REVOKED`, `ROLE_CANNOT_START`).
* `journeys`: for each reachable transition, a record created through the app and walked to it. Each step is taken by the first fixture actor the kernel allows, and the case holds the kernel's answer and writes for each step. A second record created beside it must stay untouched.
* `options_cases`: for every state and actor, the actions offered and why one is refused, as the kernel answers at version 0.
* `rules`: the rule table the app shows, with every source state of each action.
* The data cases gain each text attribute at its exact limit, every declared choice, and a record with only its required values.
* The same state × action × actor × version cases, and the create cases, are sent through the app's HTTP API.
* The separation test also checks that the app does not offer the second action.

**The fixes.** The outbox names the record acted on (`Session.record_id`). The rule table lists every source of an action (`server.transitions()`).

**Gates.** `nox -s conformance_divergence` (full tier) runs the harness on library-loan and the two variants. `nox -s conformance_divergence_all` (release tier) runs every pack and both variants, about 20 minutes on four cores. `tests/test_conformance_divergence.py` (fast tier) runs every divergence that used to be missed, plus the controls: a resealed app with no divergence passes, and every seeded fault still matches the templates.

### Consequences

* Good: "the conformance tests prove the app matches the model" now has evidence from both sides, for every element kind the model has, on every shipped pack.
* Good: the four kernel features no shipped pack uses are now checked on a built app.
* Bad: the oracle is bigger, and the generated suite takes about a second longer on the largest packs, mostly for HTTP.
* Bad: the harness is still bounded by the fixture directory. A divergence that only an actor outside it would notice stays invisible, as ADR-0150 already says.
* Bad: the oracle is still the kernel's own answer. A kernel bug that the app repeats is not caught here. The SCXML differential (ADR-0165) and the kernel's mutation testing (ADR-0033) cover that.
* Revisit when: the model gains a new element kind (add its divergence to the harness), or a shipped pack starts using a feature that only the variants exercise today.
