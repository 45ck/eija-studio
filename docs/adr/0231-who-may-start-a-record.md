# ADR-0231: Who may start a record

* Status: accepted
* Date: 2026-11-11
* Lane: kernel / generated apps / PlayIDE

## Context and problem statement

Issue #142: a workflow said who may take each transition, but not who may start a record. Any active actor could create one, so a model could not say "only members open a loan" and the generated app could not be checked against it. The use case diagram drew "Create record" with no actor for the same reason.

## Decision drivers

* Existing models keep their meaning, their bytes and their semantic hashes.
* The runtime refuses, the generated app refuses, and the conformance oracle proves it; a UI hint is not enough.
* An unknown role is a policy finding, not a silent no-op.

## Considered options

* An optional `initiators` list of role names on `Workflow` (chosen).
* A pseudo-transition from a "none" state: models the start as an action, but changes every model's shape and hash and every place that walks transitions.
* A pack-level rule outside the model: the model would no longer be the source of truth for who may act.

## Decision outcome

`Workflow.initiators` is a tuple of role names, empty by default, at most 16, no duplicates. Empty means today's meaning, any active actor, and the key is left out of the serialised model so every existing hash is unchanged. When it names roles:

* `runtime.initialise(..., role=)` refuses any other creator with `ROLE_CANNOT_START` (refs `role:<name>`) and writes nothing. Without a role (previews, the access matrix, the oracle starting records on the kernel's behalf) there is no check.
* The policy adds `UNDECLARED_INITIATOR:<role>` for a role the pack does not declare.
* The generated app's `create` passes the actor's role. The oracle gains `start_cases` (one per active fixture actor) only when initiators are named, and the generated conformance test `test_only_the_named_roles_start_records` checks them.
* The seeded simulation lets only initiators start records; others act on existing ones.
* Every generated app now has seven conformance tests, not six; the receipt check (`GENERATED_TESTS`) expects seven, so an app built from an older template reads as FAIL and must be rebuilt.
* PlayIDE's permissions panel, flow card and use case diagram show who may start a record; the diagram associates each initiator with "Create".

### Consequences

* Good: "who may start" is checked end to end, from the model to the built app's tests, with a negative control (an app that ignores the role fails conformance).
* Good: no existing model, receipt or hash changes.
* Bad: the chat's proposal rules cannot yet add or remove initiators; a change to them is a direct model edit.
* Bad: kernel change; needs owner source review (#80) like every kernel change.
* Revisit when: starting a record needs a guard (a condition, not just a role), or plans need a transaction to change initiators.
