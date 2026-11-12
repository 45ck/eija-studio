"""The formal models' scope: one rule per action (ADR-0232) and no guards over record values (ADR-0234), no time events (ADR-0237).

The kernel lets one action leave several states (issue #148) and lets a transition carry guards over the record's
values or a time event (issue #93). The TLA+, SMT, Bend and BMC encodings still describe a workflow as one value-free transition per
action, so a workflow outside that shape is refused here rather than silently encoded as something it is not. The law
proof, the generated app's conformance oracle and the SCXML differential cover value guards and time events instead.
"""
from __future__ import annotations

from collections import Counter

from eija_studio.domain.models import Workflow


class OutsideFormalScope(ValueError):
    """The workflow has an action that leaves several states, a guard over record values or a time event; the encodings
    model none of them."""


def require_formal_scope(workflow: Workflow) -> Workflow:
    several = sorted(action for action, n in Counter(t.action for t in workflow.transitions).items() if n > 1)
    if several:
        raise OutsideFormalScope(f"{', '.join(several)} leave several states; the formal encodings model one transition per action")
    guarded = sorted(t.id for t in workflow.transitions if t.conditions)
    if guarded:
        raise OutsideFormalScope(f"{', '.join(guarded)} have guards over record values; the formal encodings do not model them")
    timed = sorted(t.id for t in workflow.transitions if t.after is not None)
    if timed:
        raise OutsideFormalScope(f"{', '.join(timed)} have time events; the formal encodings do not model time")
    return workflow
