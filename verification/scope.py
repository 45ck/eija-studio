"""The formal models' scope: each encodes one rule per action (ADR-0232).

The kernel lets one action leave several states (issue #148). The TLA+, SMT, Bend and BMC encodings still describe a
workflow as one transition per action, so a workflow outside that shape is refused here rather than silently encoded
as only one of its transitions.
"""
from __future__ import annotations

from collections import Counter

from eija_studio.domain.models import Workflow


class OutsideFormalScope(ValueError):
    """The workflow has an action that leaves several states; the formal encodings do not model it."""


def require_one_transition_per_action(workflow: Workflow) -> Workflow:
    several = sorted(action for action, n in Counter(t.action for t in workflow.transitions).items() if n > 1)
    if several:
        raise OutsideFormalScope(f"{', '.join(several)} leave several states; the formal encodings model one transition per action")
    return workflow
