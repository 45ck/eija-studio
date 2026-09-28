"""Bounded conformance of the Bend model against the real Python runtime, and witness traces.

The Bend laws are proved about a *model*. This module supplies the evidence that the model is not
vacuous and not obviously wrong about the code it is derived from:

* ``matrix``: for both slots, every (actor x state x action) cell of the runtime's own verification
  matrix (``application/verifier.py`` ACTORS/ORACLE) is evaluated by Bend's ``step`` and by
  ``application.runtime.execute`` in a disposable SQLite sandbox. Accepted/denied, the resulting
  state and the number of audit/outbox effects must agree cell by cell.
* ``witnesses``: short command sequences show that the safe path is *reachable* (a model that denies
  everything would satisfy every safety law) and that seeded faults have concrete counterexamples.

What this establishes: on these finitely many cells and traces the Bend model and the runtime agree.
What it does NOT establish: agreement everywhere (one-step cells and a few traces are a sample, not a
proof of conformance); anything about SQLite durability, CAS versions, operation replay or the
HTTP layer, none of which the Bend model represents. A cell comparison is a differential test.
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from bend_generate import SLOTS
from eija_studio.application.runtime import execute, initialise
from eija_studio.application.verifier import ACTORS, ORACLE, verify_runtime
from eija_studio.adapters.sqlite_store import sandbox_factory
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow

ACTOR_ID = {a[0]: a for a in ACTORS}
_HEADER = "import Base\nimport ./main.bend as M\n\n"
_HELPERS = """\
def bstr(b: Bool) -> String:
  match b:
    case True{}:
      "T"
    case False{}:
      "F"

def effs(es: +List<M.Effect>) -> String:
  match es:
    case Nil{}:
      ""
    case Con{e, rest}:
      M.Effect.name(e) ++ "," ++ effs(rest)

def show(+mname: String, +aname: String, +act: M.Action, +s: M.State, o: M.Outcome) -> String:
  M.Outcome{ok, st, es} = o
  mname ++ "|" ++ aname ++ "|" ++ M.State.name(s) ++ "|" ++ M.Action.name(act) ++ "|" ++ bstr(ok) ++ "|" ++ M.State.name(st) ++ "|" ++ effs(es) ++ ";"
"""


def _actor(actor_id: str) -> str:
    _, role, active, assigned = ACTOR_ID[actor_id]
    return f"M.Actor{{M.{role}{{}}, {'True' if active else 'False'}{{}}, {'True' if assigned else 'False'}{{}}}}"


def matrix_programs(models: dict[str, Workflow]) -> dict[str, str]:
    """One Bend value program per (slot, actor), each printing that actor's cells.

    Bend prints a value program by normalising it, and a string is a linked list of characters, so the
    result of one run must stay small: a single program for all 250 cells overflows the machine stack.
    """
    programs = {}
    for slot in SLOTS:
        for actor_id, *_ in ACTORS:
            cells = [f'show("{slot}", "{actor_id}", M.{action}{{}}, M.{state}{{}}, '
                     f'M.step(M.{slot}{{}}, {_actor(actor_id)}, M.{action}{{}}, M.{state}{{}}))'
                     for state in models[slot].states for action in ORACLE]
            name = f"matrix_{slot}_{actor_id.replace('-', '_')}.bend"
            programs[name] = _HEADER + _HELPERS + "\ndef main() -> String:\n  " + _balanced(cells) + "\n"
    return programs


def _balanced(exprs: list[str]) -> str:
    """Concatenate string expressions as a balanced tree (a long flat ``++`` chain is deeply nested)."""
    if len(exprs) == 1:
        return exprs[0]
    mid = len(exprs) // 2
    return f"({_balanced(exprs[:mid])} ++ {_balanced(exprs[mid:])})"


@dataclass(frozen=True)
class BendCell:
    accepted: bool
    state: str
    audit: int
    outbox: int


def parse_matrix(output: str) -> dict[tuple[str, str, str, str], BendCell]:
    """Parse the quoted string a matrix program prints."""
    text = output.strip()
    if not (text.startswith('"') and text.endswith('"')):
        raise ValueError("unexpected Bend output for the matrix program")
    cells: dict[tuple[str, str, str, str], BendCell] = {}
    for record in text[1:-1].split(";"):
        if not record:
            continue
        slot, actor, state, action, ok, after, effects = record.split("|")
        names = [e for e in effects.split(",") if e]
        cells[(slot, actor, state, action)] = BendCell(
            ok == "T", after, sum(n.startswith("Audit_") for n in names), sum(n.startswith("Notification_") for n in names))
    return cells


def python_matrix(models: dict[str, Workflow], workspace: Path) -> dict[tuple[str, str, str, str], BendCell]:
    """The same cells, observed by executing the real runtime in a disposable sandbox."""
    sandbox = sandbox_factory(workspace)
    cells: dict[tuple[str, str, str, str], BendCell] = {}
    for slot in SLOTS:
        receipt = verify_runtime(models[slot], {}, sandbox)
        for c in receipt["artifact"]["cells"]:
            a = c["actual"]
            cells[(slot, c["actor"], c["state"], c["action"])] = BendCell(a["accepted"], a["state"], a["audit"], a["outbox"])
    return cells


def compare_matrices(bend: dict, python: dict) -> dict:
    """Cell-by-cell agreement report. Any disagreement is listed with both observations."""
    missing = sorted(set(python) ^ set(bend))
    mismatches = [{"cell": list(k), "bend": vars(bend[k]), "python": vars(python[k])}
                  for k in sorted(set(python) & set(bend)) if bend[k] != python[k]]
    return {"cells": len(python), "agree": len(python) - len(mismatches) - len(missing),
            "mismatches": mismatches, "unmatched_cells": [list(k) for k in missing]}


@dataclass(frozen=True)
class Witness:
    name: str
    slot: str
    steps: tuple[tuple[str, str], ...]  # (actor id, action)
    final_state: str  # what a correct model reaches
    why: str


GOOD_WITNESSES: tuple[Witness, ...] = (
    Witness("safe_path_reaches_approved", "Candidate",
            (("teacher-assigned", "Submit"), ("teacher-assigned", "Recommend"), ("registrar", "Approve")), "Approved",
            "the intended path is reachable: teacher submits and recommends, registrar approves"),
    Witness("teacher_cannot_approve_after_recommending", "Candidate",
            (("teacher-assigned", "Submit"), ("teacher-assigned", "Recommend"), ("teacher-assigned", "Approve")), "Recommended",
            "the teacher's Approve is denied and the instance stays Recommended"),
    Witness("unassigned_teacher_cannot_recommend", "Candidate",
            (("teacher-assigned", "Submit"), ("teacher-unassigned", "Recommend")), "Submitted",
            "an unassigned teacher's Recommend is denied"),
    Witness("revoked_teacher_cannot_submit", "Candidate", (("teacher-revoked", "Submit"),), "Draft",
            "a revoked teacher's command is denied"),
    Witness("registrar_rejects_then_teacher_revises", "Candidate",
            (("teacher-assigned", "Submit"), ("teacher-assigned", "Recommend"), ("registrar", "Reject"), ("teacher-assigned", "Revise")),
            "Draft", "rejection returns the instance to Draft for revision"),
    Witness("baseline_registrar_approves_submitted", "Baseline",
            (("teacher-assigned", "Submit"), ("registrar", "Approve")), "Approved",
            "the baseline needs no recommendation"),
)


def witness_program(slot: str, steps: tuple[tuple[str, str], ...]) -> str:
    cmds = ", ".join(f"M.Cmd{{{_actor(a)}, M.{act}{{}}}}" for a, act in steps)
    return (_HEADER + f"def main() -> String:\n  M.State.name(M.replay([{cmds}], M.{slot}{{}}, M.initial(M.{slot}{{}})))\n")


def effects_program(slot: str, actor_id: str, action: str, state: str) -> str:
    """Value program printing the effects one command emits (a fault probe for effect laws)."""
    step = f"M.step(M.{slot}{{}}, {_actor(actor_id)}, M.{action}{{}}, M.{state}{{}})"
    return _HEADER + _HELPERS + f"\ndef main() -> String:\n  effs(M.Outcome.effects({step}))\n"


def parse_state(output: str) -> str:
    return output.strip().strip('"')


def python_witness(model: Workflow, steps: tuple[tuple[str, str], ...], workspace: Path) -> str:
    """Final state after the same commands through the real runtime (denied commands change nothing)."""
    with sandbox_factory(workspace)() as store:
        with store.transaction() as u:
            item = initialise(u, "witness", model)
        for actor_id, action in steps:
            with store.transaction() as u:
                version = u.find_instance(item["id"], "witness")["version"]
            command = ExecuteCommand(operation_id=uuid4().hex, actor_id=actor_id, instance_id=item["id"],
                                     action=action, expected_version=version)
            try:
                with store.transaction() as u:
                    execute(u, "witness", model, command)
            except DomainError:
                pass
        with store.transaction() as u:
            return u.find_instance(item["id"], "witness")["state"]


def scratch_workspace(root: Path) -> Path:
    """A throwaway sandbox parent directory inside the checkout (the system temp may be a slow disk)."""
    root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="conformance-", dir=root))
