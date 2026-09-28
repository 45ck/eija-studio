"""Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).

Every builder here is a pure function of domain values: a `Workflow`, a `model_impact` report or the
Pydantic contracts themselves. There is no second source of truth and no hand-drawn element. Builders
produce a small format-neutral intermediate model; `diagram_emitters` turns it into Mermaid, PlantUML
or Graphviz DOT text.

What this establishes: a diagram is a deterministic projection, so reordering the definition of the
same workflow cannot change the output and the text can be regenerated and compared byte-for-byte.
What it does NOT establish: that the model is correct, that a projection is complete beyond the
mapping in `domain.impact`, or that a reader understood it. Parts of a picture are modelled rather
than derived: the commit-protocol order (checked against the real runtime by a spy test, not read
from it) and the DDD stereotypes (a curated vocabulary). A picture is a review aid, not evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import types
import typing
from typing import Any, Literal, get_args, get_origin

from pydantic import BaseModel

from eija_studio.domain import models as domain_models
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.impact import changed_fields, model_impact
from eija_studio.domain.models import (
    Alternative, DomainError, ExecuteCommand, LayoutChange, Principal, Proposal, SemanticTransaction,
    Transition, Workflow,
)
from eija_studio.domain.policy import check_policy

Status = Literal["same", "added", "removed", "changed", "affected", "blocked"]
STATUS_ORDER: tuple[str, ...] = ("blocked", "added", "removed", "changed", "affected", "same")


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    status: str = "same"
    cluster: str | None = None


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    label: str = ""
    status: str = "same"


@dataclass(frozen=True)
class Cluster:
    id: str
    label: str


@dataclass(frozen=True)
class Graph:
    """A state machine (`kind="state"`) or a flow (`kind="flow"`) of labelled nodes and edges."""
    kind: Literal["state", "flow"]
    title: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    clusters: tuple[Cluster, ...] = ()
    initial: str | None = None
    terminals: tuple[str, ...] = ()
    direction: Literal["LR", "TB"] = "LR"
    legend: tuple[tuple[str, str], ...] = ()  # (status, meaning), in STATUS_ORDER
    provenance: tuple[str, ...] = ()
    initial_label: str = ""  # start-marker edge label; "+ start" when the initial state changed (diff only)
    initial_removed: str | None = None  # the initial state the baseline had, drawn as a removed start edge (diff only)


@dataclass(frozen=True)
class Participant:
    id: str
    label: str


@dataclass(frozen=True)
class Message:
    source: str
    target: str
    text: str
    reply: bool = False


@dataclass(frozen=True)
class Note:
    over: tuple[str, ...]
    text: str


@dataclass(frozen=True)
class Fragment:
    """A conditional block (`opt`): the steps happen only when `label` holds."""
    label: str
    steps: tuple[Step, ...]


Step = Message | Note | Fragment


@dataclass(frozen=True)
class Sequence:
    title: str
    participants: tuple[Participant, ...]
    steps: tuple[Step, ...]
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class Member:
    name: str
    type: str


@dataclass(frozen=True)
class ClassNode:
    name: str
    stereotype: str | None
    members: tuple[Member, ...]


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    label: str
    multiplicity: str  # "1", "0..1", "*" or "1..*", on the target end
    association: bool = False  # False: composition (owner contains target); True: plain reference


@dataclass(frozen=True)
class ClassModel:
    title: str
    classes: tuple[ClassNode, ...]
    relations: tuple[Relation, ...]
    provenance: tuple[str, ...] = ()


Diagram = Graph | Sequence | ClassModel

LEGEND_TEXT = {
    "added": "added by the candidate (+)",
    "removed": "removed by the candidate (-)",
    "changed": "changed (~)",
    "affected": "affected downstream",
    "same": "unchanged",
    "blocked": "blocked by the protected excursion policy",
}


def _provenance(*workflows: tuple[str, Workflow]) -> tuple[str, ...]:
    return tuple(f"{role}: workflow {wf.id} semantic_hash={wf.semantic_hash}" for role, wf in workflows)


def _edge_label(t: Transition) -> str:
    return f"{t.action} · {t.role}" + (" · assigned" if "actor_assigned" in t.guards else "")


def _edge_key(t: Transition) -> tuple[str, str, str]:
    return (t.from_state, t.to_state, t.action)


def _terminals(states: set[str], edges: tuple[Edge, ...]) -> tuple[str, ...]:
    has_out = {e.source for e in edges}
    return tuple(sorted(s for s in states if s not in has_out))


def state_graph(workflow: Workflow, *, role: str = "workflow") -> Graph:
    """The state machine exactly as the runtime interprets it: states, and one edge per transition."""
    edges = tuple(Edge(t.from_state, t.to_state, _edge_label(t)) for t in sorted(workflow.transitions, key=_edge_key))
    return Graph("state", f"{workflow.id} state machine", tuple(Node(s, s) for s in sorted(workflow.states)), edges,
                 initial=workflow.initial_state, terminals=_terminals(set(workflow.states), edges),
                 direction="TB", provenance=_provenance((role, workflow)))


def _describe(old: Transition, new: Transition, field: str) -> str:
    """What one changed field became: `role Registrar→Teacher`, `guards +actor_assigned -x`."""
    before, after = getattr(old, field), getattr(new, field)
    if isinstance(before, tuple):
        added, removed = sorted(set(after) - set(before)), sorted(set(before) - set(after))
        return f"{field} " + " ".join([f"+{x}" for x in added] + [f"-{x}" for x in removed])
    return f"{field} {before}→{after}"


def _changed_label(old: Transition, new: Transition) -> str:
    return "~ " + _edge_label(new) + " · " + ", ".join(_describe(old, new, f) for f in changed_fields(old, new))


def _shown(value: Any) -> Any:
    return sorted(value) if isinstance(value, tuple) else value


def diff_summary(before: Workflow, after: Workflow) -> dict[str, Any]:
    """Structured diff of two workflows: states, and transitions by action with each changed field's before and after."""
    a, b = {t.action: t for t in before.transitions}, {t.action: t for t in after.transitions}
    changed = {k: [{"field": f, "before": _shown(getattr(a[k], f)), "after": _shown(getattr(b[k], f))} for f in changed_fields(a[k], b[k])]
               for k in sorted(set(a) & set(b)) if changed_fields(a[k], b[k])}
    initial = {"before": before.initial_state, "after": after.initial_state} if before.initial_state != after.initial_state else None
    return {"initial_state": initial, "added_states": sorted(set(after.states) - set(before.states)),
            "removed_states": sorted(set(before.states) - set(after.states)),
            "added_actions": sorted(set(b) - set(a)), "removed_actions": sorted(set(a) - set(b)),
            "changed_actions": changed}


def _action_edges(old: Transition | None, new: Transition | None) -> list[Edge]:
    """Edges one action contributes: same endpoints in both is one same/changed edge, else removed and/or added."""
    if old is not None and new is not None and _edge_key(old) == _edge_key(new):
        if not changed_fields(old, new):
            return [Edge(new.from_state, new.to_state, _edge_label(new))]
        return [Edge(new.from_state, new.to_state, _changed_label(old, new), "changed")]
    edges = []
    if old is not None:
        edges.append(Edge(old.from_state, old.to_state, "- " + _edge_label(old), "removed"))
    if new is not None:
        edges.append(Edge(new.from_state, new.to_state, "+ " + _edge_label(new), "added"))
    return edges


def _diff_edges(before: Workflow, after: Workflow) -> tuple[Edge, ...]:
    a, b = {t.action: t for t in before.transitions}, {t.action: t for t in after.transitions}
    edges = [e for action in sorted(set(a) | set(b)) for e in _action_edges(a.get(action), b.get(action))]
    return tuple(sorted(edges, key=lambda e: (e.source, e.target, e.label.lstrip("+-~ "), e.status)))


def _touched(edges: tuple[Edge, ...], before: Workflow, after: Workflow) -> set[str]:
    """States next to a non-same edge, plus both initial states when the initial state moved."""
    touched = {n for e in edges if e.status != "same" for n in (e.source, e.target)}
    return touched | {before.initial_state, after.initial_state} if before.initial_state != after.initial_state else touched


def _diff_legend(used: set[str]) -> tuple[tuple[str, str], ...]:
    """Legend rows for the statuses in use; none at all when nothing changed (an empty diff has no legend)."""
    return tuple((s, LEGEND_TEXT[s]) for s in STATUS_ORDER if s in used) if used - {"same"} else ()


def _state_status(state: str, before: Workflow, after: Workflow, touched: set[str]) -> str:
    if state not in before.states:
        return "added"
    if state not in after.states:
        return "removed"
    return "changed" if state in touched else "same"


def diff_graph(before: Workflow, after: Workflow) -> Graph:
    """Baseline vs candidate on one canvas. Edge status: an edge only in `after` is added, only in `before`
    removed, same endpoints with any changed field (`domain.impact.changed_fields`) changed, and a `~` label
    names the fields. A state is added or removed by membership and `changed` when its incident edges differ or
    it is (or was) the initial state of a workflow whose initial state moved, which makes the ripple around an
    edit visible."""
    edges = _diff_edges(before, after)
    moved = before.initial_state != after.initial_state
    states = set(before.states) | set(after.states)
    nodes = tuple(Node(s, s, _state_status(s, before, after, _touched(edges, before, after))) for s in sorted(states))
    used = {n.status for n in nodes} | {e.status for e in edges} | ({"added", "removed"} if moved else set())
    start: dict[str, Any] = {"initial_label": "+ start", "initial_removed": before.initial_state} if moved else {}
    return Graph("state", f"{after.id} baseline vs candidate", nodes, edges, initial=after.initial_state,
                 terminals=_terminals(states, edges), direction="TB", legend=_diff_legend(used),
                 provenance=_provenance(("baseline", before), ("candidate", after)), **start)


NODE_KIND = {"rule": "Rule", "runtime": "Runtime", "state-view": "State view", "journey": "Journey",
             "obligation": "Obligation", "receipt": "Receipt"}
SHARED_NODE = {"review-packet": "Review packet", "local-decision": "Local decision"}


IMPACT_LEGEND = {"changed": "changed rule (root of the ripple)", "affected": "affected downstream", "same": "unaffected"}


def _impact_node(node_id: str, roots: set[str], affected: set[str]) -> Node:
    kind, _, action = node_id.partition(":")
    label = f"{NODE_KIND[kind]} · {action}" if action else SHARED_NODE.get(kind, kind)
    status = "changed" if node_id in roots else "affected" if node_id in affected else "same"
    return Node(node_id, label, status, cluster=action or None)


def _impact_edges(graph: dict[str, list[str]], affected: set[str]) -> tuple[Edge, ...]:
    return tuple(Edge(s, t, "", "affected" if s in affected else "same") for s in sorted(graph) for t in sorted(set(graph[s])))


def _impact_legend(nodes: tuple[Node, ...]) -> tuple[tuple[str, str], ...]:
    used = {n.status for n in nodes}
    return tuple((s, IMPACT_LEGEND[s]) for s in ("changed", "affected", "same") if s in used)


def _impact_provenance(before: Workflow, after: Workflow, report: dict[str, Any]) -> tuple[str, ...]:
    closure = "complete within this mapping" if report["complete"] else "INCOMPLETE, frontier " + ",".join(report["frontier"])
    return (*_provenance(("baseline", before), ("candidate", after)), "closure: " + closure, "envelope: " + report["envelope"])


def impact_graph(before: Workflow, after: Workflow, impact: dict[str, Any] | None = None) -> Graph:
    """The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`:
    changed rules -> runtime -> state view -> journey -> obligation -> receipt -> review packet -> decision.
    The mapping is the model's own; consequences outside it are not drawn (see the `envelope` note)."""
    report = impact if impact is not None else model_impact(before, after)
    roots = {"rule:" + a for a in report["changed_actions"]}
    affected = set(report["affected"])
    ids = sorted(set(report["graph"]) | {t for targets in report["graph"].values() for t in targets})
    nodes = tuple(_impact_node(i, roots, affected) for i in ids)
    actions = sorted({n.cluster for n in nodes if n.cluster})
    return Graph("flow", f"{after.id} change ripple", nodes, _impact_edges(report["graph"], affected),
                 tuple(Cluster(a, f"Action {a}") for a in actions), direction="LR", legend=_impact_legend(nodes),
                 provenance=_impact_provenance(before, after, report))


def journey_graph(workflow: Workflow) -> Graph:
    """One swim-lane per role listing exactly the transitions that role may perform. Derived from
    `Transition.role`, not from prose, so a journey cannot promise an action the runtime would refuse."""
    roles = sorted({t.role for t in workflow.transitions})
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []
    for role in roles:
        for t in sorted((t for t in workflow.transitions if t.role == role), key=_edge_key):
            for state in (t.from_state, t.to_state):
                nodes[f"{role}::{state}"] = Node(f"{role}::{state}", state, cluster=role)
            edges.append(Edge(f"{role}::{t.from_state}", f"{role}::{t.to_state}", t.action + (" · assigned" if "actor_assigned" in t.guards else "")))
    return Graph("flow", f"{workflow.id} journeys by role", tuple(nodes[k] for k in sorted(nodes)), tuple(edges),
                 tuple(Cluster(r, f"{r} journey") for r in roles), provenance=_provenance(("workflow", workflow)))


GUARD_FAILURES = {  # guard -> (label, stable error code raised by application.runtime); base guards in runtime order
    "actor_active": ("actor is not active at commit time", "ACTOR_REVOKED"),
    "role_current": ("actor lacks the transition's role", "ROLE_DENIED"),
    "actor_assigned": ("actor is not assigned in the trusted directory", "ASSIGNMENT_DENIED"),
}


def commit_sequence(workflow: Workflow, action: str) -> Sequence:
    """The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is
    checked BEFORE any replay lookup, then replay/operation binding, CAS on the instance version, state
    guard, state write, audit and outbox effects, operation record, single commit.

    Guards and effects come from the transition. The ORDER is hand-encoded here, not read from the runtime:
    tests/test_diagrams.py replays the real `execute` through a recording unit of work and compares the call
    order, so a reordering in the runtime fails that test, but the runtime source is never parsed. Effects are
    listed audit first, then outbox, each sorted: their order inside the one transaction is non-semantic
    (see `Workflow.semantic_hash`)."""
    t = next((x for x in workflow.transitions if x.action == action), None)
    if t is None:
        raise DomainError("ACTION_DENIED", f"Action {action!r} is not modelled; modelled: {', '.join(sorted(x.action for x in workflow.transitions))}")
    steps = [*_authority_steps(t), *_replay_and_state_steps(t), *_effect_steps(t), *_closing_steps()]
    return Sequence(f"{action} commit protocol", _participants(t), tuple(steps), _provenance(("workflow", workflow)))


def _authority_steps(t: Transition) -> list[Step]:
    steps: list[Step] = [
        Message("Caller", "Runtime", f"execute {t.action} (operation_id, expected_version)"),
        Message("Runtime", "Runtime", "ensure_policy(model)"),
        Message("Runtime", "Store", "load instance (model_hash must equal the workflow semantic hash)"),
        Message("Runtime", "Store", "load actor from trusted directory"),
        Note(("Runtime",), f"authorise BEFORE replay: role {t.role}" + (", assignment required" if "actor_assigned" in t.guards else "")),
    ]
    if t.forbidden_effects:
        steps.append(Note(("Runtime",), "forbidden effects, never emitted: " + ", ".join(sorted(t.forbidden_effects))))
    for guard in ("actor_active", "role_current", "actor_assigned"):
        if guard != "actor_assigned" or guard in t.guards:  # `check_actor` tests active and role unconditionally
            reason, code = GUARD_FAILURES[guard]
            steps.append(Fragment(f"guard {guard} fails: {reason}", (Message("Runtime", "Caller", code, reply=True),)))
    return steps


def _replay_and_state_steps(t: Transition) -> list[Step]:
    return [
        Message("Runtime", "Store", "find operation by operation_id"),
        Fragment("guard operation_binding: id already bound", (
            Message("Runtime", "Caller", "OPERATION_CONFLICT if another request, else duplicate result (no effects)", reply=True),)),
        Fragment("guard expected_version fails", (Message("Runtime", "Caller", "STALE_VERSION", reply=True),)),
        Fragment(f"guard state_equals fails: state is not {t.from_state}", (Message("Runtime", "Caller", "STATE_DENIED", reply=True),)),
        Message("Runtime", "Store", f"compare-and-set instance: {t.from_state} → {t.to_state}, version + 1"),
    ]


def _effect_steps(t: Transition) -> list[Step]:
    """Audit writes, then outbox enqueues, then effects without an adapter (refused); each group sorted."""
    effects = sorted(t.required_effects)
    steps: list[Step] = [Message("Runtime", "Audit", f"append {e}") for e in effects if e.startswith("Audit:")]
    steps += [Message("Runtime", "Outbox", f"enqueue {e}") for e in effects if e.startswith("Notification:")]
    steps += [Fragment(f"effect {e} has no adapter", (Message("Runtime", "Caller", "EFFECT_DENIED", reply=True),))
              for e in effects if not e.startswith(("Audit:", "Notification:"))]
    return steps


def _closing_steps() -> list[Step]:
    return [
        Message("Runtime", "Store", "record operation (operation_id, binding, result)"),
        Message("Store", "Store", "commit state + audit + outbox + operation in ONE transaction"),
        Message("Runtime", "Caller", "result, sent only after the transaction commits", reply=True),
    ]


def _participants(t: Transition) -> tuple[Participant, ...]:
    used = {"Caller", "Runtime", "Store"}
    used |= {"Audit"} if any(e.startswith("Audit:") for e in t.required_effects) else set()
    used |= {"Outbox"} if any(e.startswith("Notification:") for e in t.required_effects) else set()
    return tuple(Participant(i, i) for i in ("Caller", "Runtime", "Store", "Audit", "Outbox") if i in used)


CONTRACTS: tuple[type[BaseModel], ...] = (ChangeCase, Workflow, Transition, Proposal, Alternative, SemanticTransaction,
                                          LayoutChange, ExecuteCommand, Principal)
# Curated vocabulary from docs/architecture/ARCHITECTURE.md; tests assert every key is a real contract.
DDD_ROLE = {"ChangeCase": "aggregate-root", "Workflow": "value-object", "Transition": "value-object",
            "Proposal": "value-object", "Alternative": "value-object", "SemanticTransaction": "command",
            "LayoutChange": "command", "ExecuteCommand": "command", "Principal": "value-object"}


def _literal_aliases() -> dict[Any, str]:
    """Module-level `Literal[...]` aliases of the domain (Guard, Interpretation) become enumerations."""
    return {obj: name for name, obj in sorted(vars(domain_models).items()) if get_origin(obj) is Literal}


def _unwrap(annotation: Any) -> tuple[Any, str]:
    """Reduce an annotation to (element type, multiplicity)."""
    origin = get_origin(annotation)
    if origin in (typing.Union, types.UnionType):
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1 and len(args) < len(get_args(annotation)):
            return _unwrap(args[0])[0], "0..1"
    if origin in (tuple, list, set, frozenset):
        return get_args(annotation)[0], "*"
    return annotation, "1"


def _union_text(args: tuple[Any, ...]) -> str:
    return " | ".join(sorted(_type_text(a) for a in args if a is not type(None)) + (["None"] if type(None) in args else []))


def _type_text(annotation: Any) -> str:
    origin, args = get_origin(annotation), get_args(annotation)
    if origin is Literal:
        return "Literal<" + "|".join(str(a) for a in args) + ">"
    if origin in (typing.Union, types.UnionType):
        return _union_text(args)
    if origin in (tuple, list, set, frozenset):
        return f"{origin.__name__}<{_type_text(args[0])}>"
    if origin is dict:
        return f"dict<{_type_text(args[0])}, {_type_text(args[1])}>"
    if origin is not None:
        return str(annotation).replace("typing.", "")
    return "None" if annotation is type(None) else getattr(annotation, "__name__", str(annotation))


def _contract_class(model: type[BaseModel], known: set[str], aliases: dict[Any, str]) -> tuple[ClassNode, list[Relation], set[str]]:
    """One contract as a class node, its relations to other contracts or enumerations, and the enumerations it uses."""
    members: list[Member] = []
    relations: list[Relation] = []
    enums: set[str] = set()
    for name, field in model.model_fields.items():
        element, mult = _unwrap(field.annotation)
        if getattr(element, "__name__", None) in known:
            if mult == "*" and any(type(m).__name__ == "MinLen" and m.min_length >= 1 for m in field.metadata):
                mult = "1..*"
            relations.append(Relation(model.__name__, element.__name__, name, mult))
        elif element in aliases:
            enums.add(aliases[element])
            relations.append(Relation(model.__name__, aliases[element], name, mult, association=True))
        else:
            members.append(Member(name, _type_text(field.annotation)))
    return ClassNode(model.__name__, DDD_ROLE.get(model.__name__), tuple(members)), relations, enums


def class_model() -> ClassModel:
    """Domain contracts introspected from the Pydantic models. A field typed as another contract, or as a
    named `Literal` alias (an enumeration), becomes a composition or association edge with its
    multiplicity; every other field is a typed member."""
    known = {c.__name__ for c in CONTRACTS}
    aliases = _literal_aliases()
    classes: list[ClassNode] = []
    relations: list[Relation] = []
    enums: set[str] = set()
    for model in sorted(CONTRACTS, key=lambda c: c.__name__):
        node, found, used = _contract_class(model, known, aliases)
        classes.append(node)
        relations += found
        enums |= used
    by_name = {name: obj for obj, name in aliases.items()}
    classes += [ClassNode(n, "enumeration", tuple(Member(str(v), "") for v in get_args(by_name[n]))) for n in sorted(enums)]
    relations.sort(key=lambda r: (r.source, r.target, r.label))
    return ClassModel("Domain contracts", tuple(classes), tuple(relations),
                      ("source: pydantic models in eija_studio.domain (frozen, extra=forbid)",))


BLOCKED_ID = "policy-blocked"


def policy_violations(workflow: Workflow) -> tuple[str, ...]:
    """Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
    A non-empty result means the runtime would raise POLICY_BLOCKED before doing anything else."""
    return tuple(check_policy(workflow))


def mark_blocked(diagram: Diagram, violations: tuple[str, ...]) -> Diagram:
    """Make a policy-refused workflow look refused: a red node (graphs) or a note (sequences) naming the
    codes, plus a provenance line. Without it a protected-authority change would draw like any other edit.
    The class diagram describes the fixed contracts, not a workflow, so it is returned unchanged."""
    if not violations:
        return diagram
    text = "POLICY BLOCKED: " + "; ".join(violations)
    if isinstance(diagram, Graph):
        taken = {n.id for n in diagram.nodes}
        node_id = BLOCKED_ID
        while node_id in taken:
            node_id += "_"
        return replace(diagram, nodes=(*diagram.nodes, Node(node_id, text, "blocked")),
                       provenance=(*diagram.provenance, "policy: " + text))
    if isinstance(diagram, Sequence):
        note = Note(("Runtime",), text + "; execute raises POLICY_BLOCKED before any state is read")
        return replace(diagram, steps=(note, *diagram.steps), provenance=(*diagram.provenance, "policy: " + text))
    return diagram
