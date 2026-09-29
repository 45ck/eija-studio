"""Stateful differential test: the real Studio + SQLite against an independent reference model.

Hypothesis drives random *sequences* of operations (execute with fresh/replayed/conflicting operation
ids, correct and stale versions, actor revocation and reassignment, preview reset, the typed
rejection-source edit, and injected mid-commit faults). After every step the durable state (instances,
audit, outbox, operations, case version) must equal what ``property_reference.ReferenceRuntime``
predicts from the specification text.

What this establishes: no reachable sequence of these operations, within the bounds of the generators,
makes the kernel disagree with a second expression of the specified rules; refused and faulted commands
leave no trace. What it does NOT establish: correctness of the specification, coverage of operations
outside the generators (concurrency, crash-during-fsync), or that the reference is independent of its
author. The negative controls in ``test_reference_detects_mutants.py`` show the harness can fail.
"""
from __future__ import annotations

from dataclasses import replace

from hypothesis import HealthCheck, event, settings, strategies as st
from hypothesis.stateful import (Bundle, RuleBasedStateMachine, initialize, invariant, multiple, rule,
                                 run_state_machine_as_test)

from . import property_reference as ref
from eija_studio.domain.models import AGENT, OWNER, DomainError, ExecuteCommand, SemanticTransaction
from .property_support import MAIN_OUTCOMES, OUTCOMES, ephemeral_studio, examples, scratch_directory, selected_case, set_actor

ACTOR_IDS = tuple(ref.FIXTURE_DIRECTORY)
UNKNOWN_ACTOR = "ghost-actor"
UNKNOWN_INSTANCE = "ghost-instance"
BOGUS_ACTION = "Bogus"

# Every outcome the walks must reach, so a green run cannot mean "the walk never left the initial
# state". Asserted after the run (deterministic under the derandomized ci profile).
REQUIRED_OUTCOMES = {
    "Committed", "Replayed", "Faulted", "Reset", "Edit", "DirectoryChange",
    "Refused:ACTOR_REVOKED", "Refused:ROLE_DENIED", "Refused:ASSIGNMENT_DENIED", "Refused:STALE_VERSION",
    "Refused:STATE_DENIED", "Refused:OPERATION_CONFLICT", "Refused:STALE_INSTANCE", "Refused:ACTION_DENIED",
    "Refused:UNKNOWN_ACTOR", "Refused:NOT_FOUND", "Refused:AUTHORITY_REQUIRED",
}


class InjectedFault(RuntimeError):
    """Raised from the kernel's ``fault`` hook to simulate a crash between commit steps."""


def raise_at(point: str):
    def fault(reached: str) -> None:
        if reached == point:
            raise InjectedFault(point)
    return fault


def note(label: str) -> None:
    OUTCOMES[label] += 1
    event(label)


class PreviewRuntimeMachine(RuleBasedStateMachine):
    """One Change Case with a selected candidate model; instances, actors and the model evolve."""

    instances = Bundle("instances")
    issued = Bundle("issued")

    def __init__(self) -> None:
        super().__init__()
        self._scratch = scratch_directory()
        self.studio = ephemeral_studio(self._scratch.__enter__())
        case = selected_case(self.studio)
        self.case_id = case["id"]
        self.reference = ref.ReferenceRuntime(case_version=case["version"])
        self._operations = 0
        self.committed: list[ref.Command] = []  # commands that committed: the interesting ones to retry
        self.baseline_audit = self.observe()["counts"]["audit"]

    def teardown(self) -> None:
        self._scratch.__exit__(None, None, None)

    # --- helpers ------------------------------------------------------------------------------------

    def observe(self) -> dict:
        """Everything durable about the case, read in one transaction."""
        with self.studio.store.transaction() as u:
            return {
                "observations": u.observations(self.case_id),
                "counts": u.effect_counts(),
                "operations": {r[0] for r in u.db.execute("SELECT id FROM operations")},
                "case_version": u.load_case(self.case_id)["version"],
            }

    def command(self, instance: str, actor: str, action: str, delta: int) -> ref.Command:
        """A command with a never-before-used operation id; ``delta`` skews the expected version."""
        self._operations += 1
        known = self.reference.instances.get(instance)
        return ref.Command(f"op-{self._operations}", actor, instance, action, max(0, (known.version if known else 0) + delta))

    def send(self, command: ref.Command, fault=None) -> ref.Command:
        """Run one command through the real kernel and compare with the reference prediction."""
        expected = self.reference.predict(command)
        wire = ExecuteCommand(operation_id=command.operation_id, actor_id=command.actor_id,
                              instance_id=command.instance_id, action=command.action,
                              expected_version=command.expected_version)
        try:
            result = self.studio.execute(self.case_id, wire, fault=fault)
        except InjectedFault:
            assert isinstance(expected, ref.Committed), f"fault fired but the reference predicts {expected}"
            note("Faulted")  # rolled back: the reference is deliberately not advanced
            return command
        except DomainError as error:
            assert expected == ref.Refused(error.code), f"kernel refused {error.code}; reference predicts {expected}"
            note(f"Refused:{error.code}")
            return command
        assert not isinstance(expected, ref.Refused), f"kernel accepted a command the reference refuses with {expected.code}"
        assert fault is None or isinstance(expected, ref.Replayed), "a commit that reached the fault hook returned success"
        if isinstance(expected, ref.Committed):
            assert result["committed"] is True and result["duplicate"] is False
            assert (result["instance"]["state"], result["instance"]["version"]) == (expected.state, expected.version)
            assert result["effects"] == list(expected.effects)
            self.reference.execute(command)
            self.committed.append(command)
            note("Committed")
        else:
            assert result["duplicate"] is True and result["committed"] is False and result["effects"] == []
            original = result["original_result"]
            assert (original["instance"]["state"], original["instance"]["version"]) == (expected.original.state, expected.original.version)
            assert original["effects"] == list(expected.original.effects)
            note("Replayed")
        return command

    def committing_options(self, instance: str) -> list[tuple[str, str]]:
        """(actor, action) pairs the reference says would commit right now. Used only to bias generation
        toward deep sequences; the outcome is still checked against the real kernel."""
        probe = lambda actor, action: ref.Command("probe", actor, instance, action, self.reference.instances[instance].version)  # noqa: E731
        return [(actor, action) for action in self.reference.enabled_actions(instance) for actor in ACTOR_IDS
                if isinstance(self.reference.predict(probe(actor, action)), ref.Committed)]

    # --- rules: instances ---------------------------------------------------------------------------

    @initialize(target=instances, state=st.none() | st.sampled_from(ref.STATES))
    def first_instance(self, state):
        return self.do_reset(state, self.reference.case_version)

    @rule(target=instances, state=st.none() | st.sampled_from(ref.STATES) | st.just("Nonexistent"),
          version_delta=st.sampled_from([0, 0, 0, 1, -1]))
    def reset(self, state, version_delta):
        """Reset creates a fresh isolated instance; a stale case version or unknown state is refused."""
        return self.do_reset(state, max(0, self.reference.case_version + version_delta))

    def do_reset(self, state, case_version):
        refusal = self.reference.predict_reset(state, case_version)
        try:
            item = self.studio.reset_preview(self.case_id, case_version, state)
        except DomainError as error:
            assert refusal == ref.Refused(error.code), f"reset refused {error.code}; reference predicts {refusal}"
            note(f"Refused:{error.code}")
            return multiple()
        assert refusal is None, f"reset accepted; reference predicts {refusal}"
        assert (item["state"], item["version"]) == (state or ref.INITIAL_STATE, 0)
        self.reference.reset(item["id"], state)
        note("Reset")
        return item["id"]

    # --- rules: execution ---------------------------------------------------------------------------

    @rule(target=issued, instance=instances, data=st.data())
    def execute_plausible(self, instance, data):
        """An action enabled in the instance's state, usually by a role holder, usually at the right version."""
        action = data.draw(st.sampled_from(self.reference.enabled_actions(instance) or list(ref.ACTIONS)))
        actor = data.draw(st.sampled_from(self.reference.holders(action) + list(ACTOR_IDS)))
        return self.send(self.command(instance, actor, action, data.draw(st.sampled_from([0, 0, 0, 0, 1, -1]))))

    @rule(target=issued, instance=instances, data=st.data(), delta=st.sampled_from([0, 0, 0, 1, -1]))
    def execute_committing(self, instance, data, delta):
        """A command the reference says will commit (when one exists), sometimes with a stale version:
        drives the state machine forward and probes optimistic concurrency where everything else passes."""
        options = self.committing_options(instance)
        actor, action = data.draw(st.sampled_from(options)) if options else (ACTOR_IDS[0], ref.ACTIONS[0])
        return self.send(self.command(instance, actor, action, delta))

    @rule(target=issued, instance=instances, data=st.data())
    def execute_enabled_by_any_actor(self, instance, data):
        """A state-correct action by any of the five actors at the right version: isolates role,
        assignment and revocation checks from every other refusal."""
        action = data.draw(st.sampled_from(self.reference.enabled_actions(instance) or list(ref.ACTIONS)))
        return self.send(self.command(instance, data.draw(st.sampled_from(ACTOR_IDS)), action, 0))

    @rule(target=issued, instance=instances, actor=st.sampled_from((*ACTOR_IDS, UNKNOWN_ACTOR)),
          action=st.sampled_from((*ref.ACTIONS, BOGUS_ACTION)), delta=st.sampled_from([0, 0, 1, -1, 5]))
    def execute_any(self, instance, actor, action, delta):
        """Unbiased command: mostly refusals, which must leave no trace."""
        return self.send(self.command(instance, actor, action, delta))

    @rule(target=issued, actor=st.sampled_from(ACTOR_IDS), action=st.sampled_from(ref.ACTIONS))
    def execute_unknown_instance(self, actor, action):
        return self.send(self.command(UNKNOWN_INSTANCE, actor, action, 0))

    def pick_to_retry(self, command: ref.Command, data, prefer_committed: bool) -> ref.Command:
        """Retrying a *committed* command is what exercises replay; a refused one only shows that its
        operation id stayed unused. Both are worth drawing."""
        return data.draw(st.sampled_from(self.committed)) if prefer_committed and self.committed else command

    @rule(command=issued, data=st.data(), prefer_committed=st.booleans())
    def retry_identical(self, command, data, prefer_committed):
        """Same operation id and body: original result while authorised, a refusal once revoked or stale."""
        self.send(self.pick_to_retry(command, data, prefer_committed))

    @rule(command=issued, other_instance=instances, data=st.data(), prefer_committed=st.booleans())
    def retry_conflicting(self, command, other_instance, data, prefer_committed):
        """Reuse an operation id with one bound field changed: must never replay or commit."""
        command = self.pick_to_retry(command, data, prefer_committed)
        changed = data.draw(st.sampled_from([
            replace(command, actor_id=data.draw(st.sampled_from(ACTOR_IDS))),
            replace(command, instance_id=other_instance),
            replace(command, action=data.draw(st.sampled_from(ref.ACTIONS))),
            replace(command, expected_version=command.expected_version + 1)]))
        self.send(changed)

    @rule(instance=instances, data=st.data(), point=st.sampled_from(["after_state", "after_effects", "after_operation"]))
    def execute_with_crash(self, instance, data, point):
        """A crash between commit steps must roll everything back (state, audit, outbox, operation)."""
        options = self.committing_options(instance)
        actor, action = data.draw(st.sampled_from(options or [(a, b) for a in ACTOR_IDS for b in ref.ACTIONS]))
        self.send(self.command(instance, actor, action, 0), fault=raise_at(point))

    # --- rules: trusted directory and semantic edit -------------------------------------------------

    @rule(actor=st.sampled_from(ACTOR_IDS), column=st.sampled_from(["active", "assigned", "role"]), data=st.data())
    def change_directory(self, actor, column, data):
        """Revoke, reinstate, (un)assign or re-role an actor, as an external assignment feed would."""
        if column == "role":
            value = data.draw(st.sampled_from(ref.ROLES))
            set_actor(self.studio, actor, column, value)
        else:
            value = data.draw(st.booleans())
            set_actor(self.studio, actor, column, int(value))
        self.reference.set_actor(actor, column, value)
        note("DirectoryChange")

    @rule(source=st.sampled_from(ref.REJECTION_SOURCES), owner=st.booleans(), version_delta=st.sampled_from([0, 0, 0, 1]))
    def edit_rejection_source(self, source, owner, version_delta):
        """The typed semantic edit: old instances become stale unless the resulting model is unchanged."""
        expected_version = self.reference.case_version + version_delta
        refusal = self.reference.predict_edit(expected_version, owner)
        try:
            self.studio.edit(self.case_id, expected_version,
                             SemanticTransaction(kind="set_rejection_source", rejection_source=source),
                             OWNER if owner else AGENT)
        except DomainError as error:
            assert refusal == ref.Refused(error.code), f"edit refused {error.code}; reference predicts {refusal}"
            note(f"Refused:{error.code}")
            return
        assert refusal is None, f"edit accepted; reference predicts {refusal}"
        self.reference.apply_edit(source)
        note("Edit")

    # --- invariants: the durable state equals the reference after every step -------------------------

    @invariant()
    def durable_state_matches_reference(self):
        seen, model = self.observe(), self.reference
        stored = {i["id"]: (i["state"], i["version"]) for i in seen["observations"]["instances"]}
        assert stored == {k: (v.state, v.version) for k, v in model.instances.items()}
        audit = [(e["kind"], e["body"]["operation_id"], e["body"]["actor_id"], e["body"]["instance_id"])
                 for e in seen["observations"]["events"] if e["kind"].startswith("Audit:")]
        assert audit == model.audit
        assert seen["counts"]["audit"] - self.baseline_audit == len(model.audit)
        outbox = {(r["operation_id"], r["kind"]) for r in seen["observations"]["outbox"]}
        assert outbox == model.outbox and seen["counts"]["outbox"] == len(model.outbox)
        assert seen["operations"] == set(model.operations) and seen["counts"]["operations"] == len(model.operations)
        assert seen["case_version"] == model.case_version

    @invariant()
    def version_counts_committed_transitions(self):
        """Every commit writes exactly one audit entry, so an instance's version is its audit-entry count."""
        model = self.reference
        for instance_id, instance in model.instances.items():
            assert instance.version == sum(1 for entry in model.audit if entry[3] == instance_id)


def run_machine(machine=PreviewRuntimeMachine, *, base_examples: int = 80, steps: int = 30) -> None:
    """Run ``machine`` under the active profile; raises the first falsifying assertion."""
    run_state_machine_as_test(machine, settings=settings(
        max_examples=examples(base_examples), stateful_step_count=steps, suppress_health_check=list(HealthCheck)))


def test_kernel_agrees_with_reference_model():
    """The real runtime and the reference model agree after every step of every generated sequence."""
    OUTCOMES.clear()
    run_machine()
    MAIN_OUTCOMES.update(OUTCOMES)
    missing = REQUIRED_OUTCOMES - set(OUTCOMES)
    assert not missing, f"the generated sequences never reached: {sorted(missing)}"
