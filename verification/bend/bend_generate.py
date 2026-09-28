"""Generate ``main.bend``: the EIJA workflow model as a Bend 2 program.

The Bend model is *generated from* the executable Python ``Workflow`` (never hand-copied), so the
model that ``PROOF.bend`` reasons about cannot silently drift from the model the kernel runs. Two
workflows fill two fixed slots of one program: ``Baseline`` (the protected baseline) and
``Candidate`` (the ``recommend_only`` candidate). The hand-written laws (``LAWS.bend``) and proofs
(``PROOF.bend``) are static and are checked against whatever the two slots contain, which is how the
negative controls work: the same proofs are run against a deliberately unsafe workflow.

What this module establishes: given valid ``Workflow`` objects, the emitted text is a deterministic
function of them (sorted universes, no timestamps, LF endings).

What it does NOT establish: that the Bend ``step`` function equals ``application.runtime.execute``.
The mapping (see docs/formal/bend.md) is a modelling decision; ``bend_runner.py`` adds a bounded
differential test against the real runtime, which is evidence of conformance, not a proof of it.

The hand-written laws restate two pieces of kernel policy: which effects are forbidden and which state a
rejection comes from. ``check_laws_against_policy`` compares them with ``policy.FORBIDDEN`` and the workflows,
so a change to the kernel policy fails the drift gate instead of leaving a law silently out of date.

Run ``python verification/bend/bend_generate.py`` to (re)write the committed ``main.bend``, or with
``--check`` to fail when it is stale (the fast drift gate).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import get_args

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eija_studio.application.verifier import ACTORS  # noqa: E402  (the runtime matrix's actor directory)
from eija_studio.domain.models import BASE_GUARDS, Guard, SemanticTransaction, Workflow  # noqa: E402
from eija_studio.domain.policy import FORBIDDEN, apply_transaction, baseline  # noqa: E402

GENERATED_PATH = HERE / "main.bend"
LAWS_PATH = HERE / "LAWS.bend"
# The guards the engine template implements: the mandatory ones (role equality with the fixture, active actor,
# source state; CAS version and operation binding are abstracted) and the optional assignment guard.
MODELLED_GUARDS = frozenset(BASE_GUARDS) | {"actor_assigned"}
UNSAFE_EXAMPLE = ROOT / "examples" / "unsafe-teacher-final-approval.json"
CANDIDATE_EXAMPLE = ROOT / "examples" / "excursion-candidate.json"

SLOTS = ("Baseline", "Candidate")  # the two model slots of one program, in declaration order
_IDENT = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
# Names the fixed part of the program (or Bend's Base) already defines. A workflow that used one as a
# state/role/action/effect name would silently change meaning, so generation refuses.
_RESERVED = frozenset({
    "Actor", "Rule", "Outcome", "Cmd", "Run", "Model", "State", "Role", "Action", "Effect",
    "Baseline", "Candidate", "Some", "None", "Nil", "Con", "True", "False", "Unit", "Empty",
})


class ModelError(ValueError):
    """The workflow cannot be represented faithfully as a Bend model."""


def check_guards_are_modelled() -> None:
    """Refuse to generate when the kernel gains a guard the engine template does not implement."""
    unknown = set(get_args(Guard)) - MODELLED_GUARDS
    if unknown:
        raise ModelError(f"the kernel has guards the Bend engine does not model: {sorted(unknown)}")


def effect_name(effect: str) -> str:
    """``Audit:ExcursionApproved`` -> ``Audit_ExcursionApproved`` (a Bend constructor name)."""
    return effect.replace(":", "_")


def default_models() -> dict[str, Workflow]:
    """The two workflows the committed proofs are about: the baseline and the recommend_only candidate."""
    base = baseline()
    return {"Baseline": base,
            "Candidate": apply_transaction(base, SemanticTransaction(kind="enable_recommendation"))}


def load_workflow(path: Path) -> Workflow:
    """Parse a workflow example. Deliberately does not run ``check_policy``: the unsafe control must load."""
    return Workflow.model_validate_json(path.read_text(encoding="utf-8"))


def _universe(models: dict[str, Workflow]) -> dict[str, list[str]]:
    """Sorted vocabularies shared by the slots. Roles include the runtime matrix's actors (e.g. Viewer)."""
    states = {s for w in models.values() for s in w.states}
    actions = {t.action for w in models.values() for t in w.transitions}
    roles = {t.role for w in models.values() for t in w.transitions} | {role for _, role, _, _ in ACTORS}
    effects = {effect_name(e) for w in models.values() for t in w.transitions
               for e in (*t.required_effects, *t.forbidden_effects)} | {effect_name(e) for e in FORBIDDEN}
    universe = {"State": sorted(states), "Role": sorted(roles), "Action": sorted(actions), "Effect": sorted(effects)}
    seen: set[str] = set(_RESERVED)
    for kind, names in universe.items():
        for name in names:
            if not _IDENT.match(name) or name in seen:
                raise ModelError(f"{kind} name {name!r} is not a usable, unique Bend constructor name")
            seen.add(name)
    return universe


def _enum(kind: str, names: list[str]) -> str:
    return f"type {kind} is Data:\n" + "".join(f"  {n}{{}}\n" for n in names)


def _eq(kind: str, names: list[str]) -> str:
    """Structural equality of an enumeration: one diagonal case per constructor."""
    lines = [f"def {kind}.eq(a: {kind}, b: {kind}) -> Bool:", "  match a:"]
    for n in names:
        lines += [f"    case {n}{{}}:", "      match b:", f"        case {n}{{}}:", "          True{}",
                  "        case _:", "          False{}"]
    return "\n".join(lines) + "\n"


def _name_fn(kind: str, names: list[str]) -> str:
    lines = [f"def {kind}.name(a: {kind}) -> String:", "  match a:"]
    for n in names:
        lines += [f"    case {n}{{}}:", f'      "{n}"']
    return "\n".join(lines) + "\n"


def _rule(workflow: Workflow, action: str) -> str:
    t = next((t for t in workflow.transitions if t.action == action), None)
    if t is None:
        return "None{}"
    effects = ", ".join(f"{effect_name(e)}{{}}" for e in sorted(t.required_effects))
    needs = "True{}" if "actor_assigned" in t.guards else "False{}"
    return (f"Some{{Rule{{{t.from_state}{{}}, {t.to_state}{{}}, {t.role}{{}}, {needs}, [{effects}]}}}}")


def _rule_of(models: dict[str, Workflow], actions: list[str]) -> str:
    lines = ["def rule_of(m: Model, act: Action) -> Maybe<&2, Rule>:", "  match m:"]
    for slot in SLOTS:
        workflow = models[slot]
        present = {t.action for t in workflow.transitions}
        lines += [f"    case {slot}{{}}:", "      match act:"]
        for action in actions:
            if action in present:
                lines += [f"        case {action}{{}}:", f"          {_rule(workflow, action)}"]
        if present != set(actions):
            lines += ["        case _:", "          None{}"]
    return "\n".join(lines) + "\n"


def _initial(models: dict[str, Workflow]) -> str:
    lines = ["def initial(m: Model) -> State:", "  match m:"]
    for slot in SLOTS:
        lines += [f"    case {slot}{{}}:", f"      {models[slot].initial_state}{{}}"]
    return "\n".join(lines) + "\n"


_TYPES = """\
type Model is Data:
  Baseline{}
  Candidate{}

# An actor as the trusted fixture directory describes it at commit time.
type Actor is Data:
  Actor{role: Role, active: Bool, assigned: Bool}

# One transition of the workflow: the state it leaves, the state it enters, the role that may fire it,
# whether the actor must be assigned (guard actor_assigned) and the effects it declares.
type Rule is Data:
  Rule{from: State, to: State, role: Role, needs_assigned: Bool, effects: +List<Effect>}

# What one command does. A denied command changes nothing and emits nothing.
type Outcome is Data:
  Outcome{ok: Bool, state: State, effects: +List<Effect>}

type Cmd is Data:
  Cmd{actor: Actor, action: Action}

# A run monitor: the state and whether the run has ever been in the Recommended state.
type Run is Data:
  Run{state: State, seen: Bool}
"""

_ENGINE = """\
def Actor.role(a: Actor) -> Role:
  Actor{role, active, assigned} = a
  role

def live(a: Actor) -> Bool:
  Actor{role, active, assigned} = a
  active

def role_is(r: Maybe<&2, Rule>, +role: Role) -> Bool:
  match r:
    case None{}:
      False{}
    case Some{rule}:
      Rule{from, to, rrole, needs, effects} = rule
      Role.eq(role, rrole)

def assign_ok(r: Maybe<&2, Rule>, +a: Actor) -> Bool:
  match r:
    case None{}:
      False{}
    case Some{rule}:
      Rule{from, to, rrole, needs, effects} = rule
      Actor{role, active, assigned} = a
      Bool.not(needs) || assigned

def from_ok(r: Maybe<&2, Rule>, s: State) -> Bool:
  match r:
    case None{}:
      False{}
    case Some{rule}:
      Rule{from, to, rrole, needs, effects} = rule
      State.eq(s, from)

# The commit-time check of application/runtime.py, as one conjunction: the transition exists, the
# actor holds its role, is active, is assigned when the transition demands it, and the instance is in
# the transition's source state.
def permits(+r: Maybe<&2, Rule>, +a: Actor, +s: State) -> Bool:
  role_is(r, Actor.role(a)) && (live(a) && (assign_ok(r, a) && from_ok(r, s)))

def target(r: Maybe<&2, Rule>, s: State) -> State:
  match r:
    case None{}:
      s
    case Some{rule}:
      Rule{from, to, rrole, needs, effects} = rule
      to

def emitted(r: Maybe<&2, Rule>) -> +List<Effect>:
  match r:
    case None{}:
      []
    case Some{rule}:
      Rule{from, to, rrole, needs, effects} = rule
      effects

def finish(c: Bool, +r: Maybe<&2, Rule>, +s: State) -> Outcome:
  match c:
    case True{}:
      Outcome{True{}, target(r, s), emitted(r)}
    case False{}:
      Outcome{False{}, s, []}

# One command against one instance state. Every effect a rule declares is emitted on success.
def step(m: Model, a: Actor, act: Action, +s: State) -> Outcome:
  +r = rule_of(m, act)
  finish(permits(r, a, s), r, s)

def Outcome.ok(o: Outcome) -> Bool:
  Outcome{ok, state, effects} = o
  ok

def Outcome.state(o: Outcome) -> State:
  Outcome{ok, state, effects} = o
  state

def Outcome.effects(o: Outcome) -> +List<Effect>:
  Outcome{ok, state, effects} = o
  effects

# True when the command was accepted and left the instance in state t.
def Outcome.enters(+o: Outcome, +t: State) -> Bool:
  Outcome{ok, state, effects} = o
  ok && State.eq(state, t)

# Final state after a sequence of commands (recursion on the sequence, so it terminates).
def replay(cmds: +List<Cmd>, +m: Model, +s: State) -> State:
  match cmds:
    case Nil{}:
      s
    case Con{cmd, rest}:
      Cmd{a, act} = cmd
      replay(rest, m, Outcome.state(step(m, a, act, s)))

# The same replay, also remembering whether the run was ever in the Recommended state.
def replay_run(cmds: +List<Cmd>, +m: Model, r: Run) -> Run:
  match cmds:
    case Nil{}:
      r
    case Con{cmd, rest}:
      Cmd{a, act} = cmd
      Run{+s, seen} = r
      replay_run(rest, m, Run{Outcome.state(step(m, a, act, s)), seen || State.eq(s, Recommended{})})
"""


def render_main(models: dict[str, Workflow]) -> str:
    """Return the text of ``main.bend`` for the given slot -> workflow mapping (deterministic)."""
    if tuple(models) != SLOTS:
        raise ModelError(f"models must be exactly the slots {SLOTS}")
    check_guards_are_modelled()
    universe = _universe(models)
    if "Recommended" not in universe["State"]:
        raise ModelError("the run monitor is defined for the Recommended state, which no slot declares")
    header = ["# GENERATED by verification/bend/bend_generate.py from the executable Python Workflow.",
              "# Do not edit: regenerate (python verification/bend/bend_generate.py); a drift check enforces this.",
              "# Model slots (Workflow.semantic_hash, sha256):"]
    header += [f"#   {slot}: {models[slot].semantic_hash}" for slot in SLOTS]
    parts = ["\n".join(header) + "\n", "import Base\n"]
    parts += [_enum(kind, universe[kind]) for kind in ("State", "Role", "Action", "Effect")]
    parts += [_TYPES]
    parts += [_eq("State", universe["State"]), _eq("Role", universe["Role"]),
              _name_fn("State", universe["State"]), _name_fn("Action", universe["Action"]),
              _name_fn("Effect", universe["Effect"]),
              _initial(models), _rule_of(models, universe["Action"]), _ENGINE]
    return "\n".join(p.rstrip("\n") + "\n" for p in parts)


def _definition(laws: str, name: str) -> str:
    """The text of ``def <name>`` in LAWS.bend, up to the next top-level definition."""
    match = re.search(rf"^def {re.escape(name)}\(.*?(?=^\S)", laws + "\nend", re.MULTILINE | re.DOTALL)
    if match is None:
        raise ModelError(f"LAWS.bend has no `def {name}`")
    return match.group(0)


def check_laws_against_policy(laws: str, models: dict[str, Workflow]) -> None:
    """Fail when the hand-written laws restate the kernel policy differently from the kernel.

    Establishes: the constructors LAWS.bend's ``forbidden`` treats as forbidden are exactly ``policy.FORBIDDEN``
    (with no wildcard that would call an unlisted effect forbidden), and ``reject_source`` names, for each slot,
    the state its Reject transition leaves. Does NOT establish that the laws are the right laws."""
    forbidden = _definition(laws, "forbidden")
    listed = set(re.findall(r"case M\.(\w+)\{\}:\s*\n\s*True\{\}", forbidden))
    wanted = {effect_name(e) for e in FORBIDDEN}
    if listed != wanted or not re.search(r"case _:\s*\n\s*False\{\}", forbidden):
        raise ModelError(f"LAWS.bend `forbidden` lists {sorted(listed)} but policy.FORBIDDEN is {sorted(wanted)}: "
                         "update LAWS.bend deliberately (a law with a stale forbidden list fails open)")
    source = dict(re.findall(r"case M\.(\w+)\{\}:\s*\n\s*M\.(\w+)\{\}", _definition(laws, "reject_source")))
    for slot, workflow in models.items():
        reject = next((t for t in workflow.transitions if t.action == "Reject"), None)
        if reject is None or source.get(slot) != reject.from_state:
            raise ModelError(f"LAWS.bend `reject_source` says {source.get(slot)!r} for {slot} but the workflow's Reject "
                             f"leaves {reject.from_state if reject else None!r}")


def write_text(path: Path, text: str) -> None:
    """Write with LF endings on every platform."""
    path.write_bytes(text.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed main.bend differs from regeneration")
    ap.add_argument("--out", type=Path, default=GENERATED_PATH, help="output path (default: the committed main.bend)")
    args = ap.parse_args(argv)
    models = default_models()
    text = render_main(models)
    check_laws_against_policy(LAWS_PATH.read_text(encoding="utf-8"), models)
    if args.check:
        current = args.out.read_bytes().decode("utf-8") if args.out.exists() else ""
        if current != text:
            print(f"DRIFT: {args.out} differs from regeneration; run python verification/bend/bend_generate.py", file=sys.stderr)
            return 1
        print(f"ok: {args.out} matches regeneration")
        return 0
    write_text(args.out, text)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
