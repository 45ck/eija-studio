"""Hypothesis strategies for workflows, plus an independent normal form used as an oracle.

``normal_form`` is deliberately written without ``Workflow.semantic_hash``: it is the test's own
definition of "the same workflow" (order of states, transitions, guards and effects is not semantic;
everything else, including identifiers, is). The properties then require ``semantic_hash`` equality to
coincide exactly with normal-form equality.
"""
from __future__ import annotations

from typing import Any

from hypothesis import assume, strategies as st
from pydantic import ValidationError

from eija_studio.domain.models import BASE_GUARDS, Workflow

NAMES = st.text(alphabet=st.characters(blacklist_categories=("Cs", "Cc")), min_size=1, max_size=10)
IDENTIFIERS = st.from_regex(r"[A-Z][A-Z0-9_-]{0,10}", fullmatch=True)
EFFECTS = st.text(alphabet="ABCDEFGHIJ:_", min_size=1, max_size=8)
OPTIONAL_GUARDS = ("actor_assigned",)


@st.composite
def transition_parts(draw, states: list[str], transition_id: str, action: str) -> dict[str, Any]:
    optional = draw(st.lists(st.sampled_from(OPTIONAL_GUARDS), unique=True))
    guards = draw(st.permutations(list(BASE_GUARDS) + optional))
    effects = draw(st.lists(EFFECTS, unique=True, max_size=6))
    cut = draw(st.integers(0, len(effects)))
    return {"id": transition_id, "action": action, "from_state": draw(st.sampled_from(states)),
            "to_state": draw(st.sampled_from(states)), "role": draw(NAMES), "guards": list(guards),
            "required_effects": effects[:cut], "forbidden_effects": draw(st.permutations(effects[cut:]))}


@st.composite
def workflows(draw, max_states: int = 6, max_transitions: int = 6) -> Workflow:
    """Structurally valid workflows (not necessarily policy-valid: ``semantic_hash`` is policy-agnostic)."""
    states = draw(st.lists(NAMES, min_size=1, max_size=max_states, unique=True))
    count = draw(st.integers(1, max_transitions))
    ids = draw(st.lists(IDENTIFIERS, min_size=count, max_size=count, unique=True))
    actions = draw(st.lists(NAMES, min_size=count, max_size=count, unique=True))
    transitions = [draw(transition_parts(states, i, a)) for i, a in zip(ids, actions, strict=False)]
    pack_id = draw(st.from_regex(r"[a-z][a-z0-9-]{0,39}", fullmatch=True))  # Workflow.id is the pack id (WBS 1.1)
    return Workflow.model_validate({"id": pack_id, "states": states, "initial_state": draw(st.sampled_from(states)),
                                    "transitions": transitions})


@st.composite
def reordered(draw, workflow: Workflow) -> Workflow:
    """The same workflow with states, transitions, guards and effects listed in a different order."""
    data = workflow.model_dump(mode="json")
    data["states"] = draw(st.permutations(data["states"]))
    data["transitions"] = draw(st.permutations(data["transitions"]))
    for transition in data["transitions"]:
        for key in ("guards", "required_effects", "forbidden_effects"):
            transition[key] = draw(st.permutations(transition[key]))
    return Workflow.model_validate(data)


def normal_form(workflow: Workflow) -> tuple:
    """Order-free identity of a workflow, independent of ``semantic_hash``."""
    return (frozenset(workflow.states), workflow.initial_state, frozenset(
        (t.id, t.action, t.from_state, t.to_state, t.role, frozenset(t.guards),
         frozenset(t.required_effects), frozenset(t.forbidden_effects)) for t in workflow.transitions))


EDIT_KINDS = ("rename_state", "add_state", "set_initial", "retarget_from", "retarget_to", "change_role",
              "rename_action", "rename_id", "toggle_guard", "add_required_effect", "add_forbidden_effect",
              "drop_effect", "move_effect", "drop_transition", "add_transition", "swap_ids")


@st.composite
def semantic_edits(draw, workflow: Workflow) -> tuple[str, Workflow]:
    """One edit to a workflow. The result may equal the original (a no-op edit); callers compare
    normal forms. Edits that produce an invalid workflow are discarded with ``assume``."""
    data = workflow.model_dump(mode="json")
    kind = draw(st.sampled_from(EDIT_KINDS))
    index = draw(st.integers(0, len(data["transitions"]) - 1))
    t = data["transitions"][index]
    if kind == "rename_state":
        old, new = draw(st.sampled_from(data["states"])), draw(NAMES)
        assume(new not in data["states"])
        data["states"] = [new if s == old else s for s in data["states"]]
        data["initial_state"] = new if data["initial_state"] == old else data["initial_state"]
        for u in data["transitions"]:
            u["from_state"], u["to_state"] = (new if u[k] == old else u[k] for k in ("from_state", "to_state"))
    elif kind == "add_state":
        new = draw(NAMES)
        assume(new not in data["states"])
        data["states"].append(new)
    elif kind == "set_initial":
        data["initial_state"] = draw(st.sampled_from(data["states"]))
    elif kind in ("retarget_from", "retarget_to"):
        t["from_state" if kind == "retarget_from" else "to_state"] = draw(st.sampled_from(data["states"]))
    elif kind == "change_role":
        t["role"] = draw(NAMES)
    elif kind == "rename_action":
        t["action"] = draw(NAMES)
    elif kind == "rename_id":
        t["id"] = draw(IDENTIFIERS)
    elif kind == "toggle_guard":
        guard = draw(st.sampled_from(OPTIONAL_GUARDS + BASE_GUARDS))
        t["guards"] = [g for g in t["guards"] if g != guard] if guard in t["guards"] else t["guards"] + [guard]
    elif kind in ("add_required_effect", "add_forbidden_effect"):
        key = "required_effects" if kind == "add_required_effect" else "forbidden_effects"
        effect = draw(EFFECTS)
        # A duplicate is a different question (see test_duplicate_forbidden_effect_is_not_a_semantic_difference).
        assume(effect not in t["required_effects"] + t["forbidden_effects"])
        t[key].append(effect)
    elif kind == "drop_effect":
        key = draw(st.sampled_from(["required_effects", "forbidden_effects"]))
        assume(t[key])
        t[key].pop(draw(st.integers(0, len(t[key]) - 1)))
    elif kind == "move_effect":
        source, target = draw(st.sampled_from([("required_effects", "forbidden_effects"), ("forbidden_effects", "required_effects")]))
        assume(t[source])
        t[target].append(t[source].pop(draw(st.integers(0, len(t[source]) - 1))))
    elif kind == "drop_transition":
        assume(len(data["transitions"]) > 1)
        data["transitions"].pop(index)
    elif kind == "add_transition":
        data["transitions"].append(draw(transition_parts(data["states"], draw(IDENTIFIERS), draw(NAMES))))
    else:  # swap_ids
        other = draw(st.integers(0, len(data["transitions"]) - 1))
        data["transitions"][other]["id"], t["id"] = t["id"], data["transitions"][other]["id"]
    try:
        return kind, Workflow.model_validate(data)
    except ValidationError:
        assume(False)
        raise
