"""Named diagram views over a baseline and an optional candidate Workflow.

This is the single entry used by the CLI (`eija render`), the HTTP endpoint and the committed docs, so
all three show the same generated text for the same model (ADR-0019, ADR-0023).
"""
from __future__ import annotations

from eija_studio.domain.models import DomainError, SemanticTransaction, Workflow
from eija_studio.domain.policy import apply_transaction, baseline
from .diagram_emitters import FORMATS, emit
from .diagrams import (
    class_model, commit_sequence, diff_graph, diff_summary, impact_graph, journey_graph, mark_blocked, policy_violations,
    stable_impact, state_graph,
)

__all__ = ["FORMATS", "VIEWS", "VIEW_FORMATS", "case_diagrams", "demo_pair", "docs_bundle", "html_panels", "render_view"]

VIEWS = ("state", "diff", "sequence", "class", "journey", "impact")
# Formats each view is emitted in. Sequence and class have no Graphviz form (DOT has no such diagram).
VIEW_FORMATS = {v: FORMATS for v in ("state", "diff", "journey", "impact")} | {
    "sequence": ("mermaid", "plantuml"), "class": ("mermaid", "plantuml")}


def demo_pair() -> tuple[Workflow, Workflow]:
    """Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended)."""
    base = baseline()
    return base, apply_transaction(base, SemanticTransaction(kind="enable_recommendation"))


def _need_candidate(view: str, after: Workflow | None) -> Workflow:
    if after is None:
        raise DomainError("CANDIDATE_REQUIRED", f"The {view} view compares a baseline with a candidate; none is available")
    return after


def render_view(view: str, fmt: str, before: Workflow, after: Workflow | None = None, action: str | None = None) -> str:
    """Generated diagram text for one view. `state`, `journey` and `sequence` describe the candidate when
    there is one, else the baseline; `diff` and `impact` require a candidate. A workflow the protected policy
    refuses is still drawn, but carries a visible POLICY BLOCKED marker naming the codes (a picture must not
    make a change the kernel would refuse look routine)."""
    if view not in VIEWS:
        raise DomainError("VIEW_UNKNOWN", f"Unknown view {view!r}; use one of {', '.join(VIEWS)}")
    subject = after if after is not None else before
    if view == "state":
        diagram = state_graph(subject, role="candidate" if after is not None else "baseline")
    elif view == "diff":
        diagram = diff_graph(before, _need_candidate(view, after))
    elif view == "impact":
        diagram = impact_graph(before, _need_candidate(view, after))
    elif view == "journey":
        diagram = journey_graph(subject)
    elif view == "class":
        return emit(class_model(), fmt)
    elif action is None:
        raise DomainError("ACTION_REQUIRED", "The sequence view needs an action: " + ", ".join(sorted(t.action for t in subject.transitions)))
    else:
        diagram = commit_sequence(subject, action)
    return emit(mark_blocked(diagram, policy_violations(subject)), fmt)


def html_panels(view: str, before: Workflow, after: Workflow | None, action: str | None = None) -> list[tuple[str, str, str]]:
    """(heading, note, Mermaid text) for `eija render --format html`. `view="all"` is every view that applies:
    one commit-protocol panel per action, and no diff or ripple when there is no candidate."""
    subject = after if after is not None else before
    note = f"Generated from the workflow's semantic hash {subject.semantic_hash[:16]}."
    wanted = VIEWS if view == "all" else (view,)
    panels: list[tuple[str, str, str]] = []
    for name in wanted:
        if name == "sequence" and action is None and view == "all":
            panels += [(f"Commit protocol: {t.action}", "Order of checks and writes in one commit.", render_view("sequence", "mermaid", before, after, t.action))
                       for t in sorted(subject.transitions, key=lambda t: t.action)]
        elif name in {"diff", "impact"} and after is None and view == "all":
            continue
        else:
            panels.append((name.capitalize() + " view", note, render_view(name, "mermaid", before, after, action)))
    return panels


def case_diagrams(before: Workflow, after: Workflow | None, fmt: str = "mermaid") -> dict:
    """Every view for one change case as one JSON-friendly payload. `sources` carries the semantic hashes the
    text was generated from, so a viewer can compare them with the review packet's evidence subject."""
    subject = after if after is not None else before
    views: dict = {"state_before": render_view("state", fmt, before), "state_after": None, "diff": None, "impact": None,
                   "journey": render_view("journey", fmt, before, after), "class": None, "sequences": {}}
    summary, impact = None, None
    if after is not None:
        views["state_after"] = render_view("state", fmt, before, after)
        views["diff"] = render_view("diff", fmt, before, after)
        views["impact"] = render_view("impact", fmt, before, after)
        summary = diff_summary(before, after)
        report = stable_impact(before, after)
        impact = {k: report[k] for k in ("changed_actions", "affected", "complete", "frontier", "envelope")}
    if fmt in VIEW_FORMATS["class"]:
        views["class"] = render_view("class", fmt, before)
    if fmt in VIEW_FORMATS["sequence"]:
        views["sequences"] = {t.action: render_view("sequence", fmt, before, after, t.action)
                              for t in sorted(subject.transitions, key=lambda t: t.action)}
    return {"format": fmt, "sources": {"baseline": before.semantic_hash, "candidate": after.semantic_hash if after else None},
            "policy_violations": list(policy_violations(subject)), "views": views, "summary": summary, "impact": impact,
            "unsupported": sorted(v for v in ("sequence", "class") if fmt not in VIEW_FORMATS[v])}


def _page(title: str, blurb: str, text: str, extra: str = "") -> str:
    return (f"<!-- GENERATED by scripts/generate_diagrams.py from the executable model; do not edit. "
            f"`python scripts/generate_diagrams.py --check` fails when this file drifts. -->\n# {title}\n\n{blurb}\n\n{extra}"
            f"```mermaid\n{text}```\n")


def _cell(text: str) -> str:
    return text.replace("|", r"\|")


def _plain(value: object) -> str:
    return ", ".join(value) if isinstance(value, list) else str(value)


def _summary_table(before: Workflow, after: Workflow) -> str:
    s = diff_summary(before, after)
    rows = [("added states", ", ".join(s["added_states"]) or "none"), ("removed states", ", ".join(s["removed_states"]) or "none"),
            ("added actions", ", ".join(s["added_actions"]) or "none"), ("removed actions", ", ".join(s["removed_actions"]) or "none")]
    rows += [(f"changed `{a}`", "; ".join(f"{c['field']}: {_plain(c['before'])} → {_plain(c['after'])}" for c in changes))
             for a, changes in s["changed_actions"].items()]
    return "| Change | Detail |\n|---|---|\n" + "".join(f"| {_cell(k)} | {_cell(v)} |\n" for k, v in rows) + "\n"


def docs_bundle() -> dict[str, str]:
    """Markdown pages for docs/diagrams/, keyed by file name. GitHub renders the Mermaid blocks. The drift
    check regenerates this and compares bytes with the committed files."""
    before, after = demo_pair()
    pages = {
        "state-baseline.md": _page("State machine: baseline", "The active excursion workflow, as the runtime interprets it.",
                                   render_view("state", "mermaid", before)),
        "state-candidate.md": _page("State machine: recommend-only candidate",
                                    "The candidate produced by the `enable_recommendation` semantic transaction.",
                                    render_view("state", "mermaid", before, after)),
        "diff.md": _page("Visual diff: baseline vs candidate",
                         "Nodes: green added, red dashed removed, amber changed. Edges cannot be coloured in a Mermaid state diagram, so a label starting with `+`, `-` or `~` marks an added, removed or changed transition.",
                         render_view("diff", "mermaid", before, after), _summary_table(before, after)),
        "impact.md": _page("Ripple: what the change touches",
                           "From `domain.impact.model_impact`: changed rules flow through runtime, state view, journey, obligation and receipt "
                           "into the review packet and the local decision. The mapping is the model's own, not every real-world consequence.",
                           render_view("impact", "mermaid", before, after)),
        "journey.md": _page("Journeys by role (candidate)", "Each lane lists only transitions that role may perform.",
                            render_view("journey", "mermaid", before, after)),
        "class.md": _page("Domain contracts", "Introspected from the frozen Pydantic contracts in `eija_studio.domain`. "
                          "Stereotypes are the curated vocabulary of `docs/architecture/ARCHITECTURE.md`.",
                          render_view("class", "mermaid", before)),
    }
    for t in sorted(after.transitions, key=lambda t: t.action):
        pages[f"sequence-{t.action.lower()}.md"] = _page(
            f"Commit protocol: {t.action}", f"Derived from the `{t.action}` transition's guards and effects, in the order "
            "`application.runtime.execute` runs them.", render_view("sequence", "mermaid", before, after, t.action))
    names = sorted(pages)
    pages["README.md"] = ("<!-- GENERATED by scripts/generate_diagrams.py; do not edit. -->\n# Generated diagrams\n\n"
                          "Every file here is generated from the executable model (ADR-0019). Do not edit them: change the model and "
                          "run `python scripts/generate_diagrams.py --write`. The nox session `diagrams_drift` fails when a file differs "
                          "from a fresh render. See [docs/visual.md](../visual.md).\n\n"
                          + "".join(f"- [{n}]({n})\n" for n in names))
    return pages
