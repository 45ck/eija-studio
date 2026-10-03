"""Check that the hand-written Bend laws and the engine template still agree with the kernel policy.

The laws (``LAWS.bend``) restate two pieces of kernel policy: which effects are forbidden and which state a rejection
comes from. ``check_laws_against_policy`` compares them with ``policy.FORBIDDEN`` and the workflows, so a change to the
kernel policy fails the drift gate instead of leaving a law silently out of date (a wildcard ``forbidden`` would treat a
new forbidden effect as allowed: law 8 would fail open). ``check_guards_are_modelled`` refuses a kernel guard the fixed
engine template does not implement.

This lives beside the generator, not in it, on purpose: ``bend_generate.py`` is hashed into the committed proof evidence
(``domain.formal_bend.MODEL_FILES``), and these checks do not change the model, so they must not make the proof stale.

Run ``python verification/bend/bend_policy.py`` (the ``bend_drift`` session does; the proof gate does too).
"""
# ruff: noqa: T201  (command-line tool: printing the verdict is its output)
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import get_args

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))  # the repo root, so `verification.bend.*` resolves when run as a script

from eija_studio.domain.models import BASE_GUARDS, Guard, Workflow  # noqa: E402
from eija_studio.domain.policy import FORBIDDEN  # noqa: E402
from verification.bend.bend_generate import ModelError, default_models, effect_name  # noqa: E402

LAWS_PATH = HERE / "LAWS.bend"
# The guards the engine template implements: the mandatory ones (role equality with the fixture, active actor,
# source state; CAS version and operation binding are abstracted) and the optional assignment guard.
MODELLED_GUARDS = frozenset(BASE_GUARDS) | {"actor_assigned"}


def check_guards_are_modelled() -> None:
    """Refuse when the kernel gains a guard the engine template does not implement."""
    unknown = set(get_args(Guard)) - MODELLED_GUARDS
    if unknown:
        raise ModelError(f"the kernel has guards the Bend engine does not model: {sorted(unknown)}")


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


def check_all() -> None:
    """Every policy-consistency check the drift gate and the proof gate run (raises ``ModelError``)."""
    check_guards_are_modelled()
    check_laws_against_policy(LAWS_PATH.read_text(encoding="utf-8"), default_models())


def main() -> int:
    try:
        check_all()
    except ModelError as error:
        print(f"DRIFT: {error}", file=sys.stderr)
        return 1
    print("ok: LAWS.bend and the engine template agree with the kernel policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
