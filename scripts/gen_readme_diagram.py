"""Generate the README before/after excursion state diagrams from the real executable model.

What this establishes: the Mermaid text between the README markers is a deterministic projection of
`domain.policy.baseline()` and `domain.policy.apply_transaction(..., enable_recommendation)`. If the
model changes and the README does not, `--check` fails (nox session `readme_diagram`).

What this does NOT establish: that the diagram is a proof of anything, or that it is the reviewed
change. The visual lane replaces it with the full generated diff (ADR-0019). Nothing here is
hand-drawn, and nothing here is an authority decision.

    python scripts/gen_readme_diagram.py --write   # regenerate README.md in place
    python scripts/gen_readme_diagram.py --check   # exit 1 when README.md is stale
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eija_studio.domain.impact import model_impact
from eija_studio.domain.models import SemanticTransaction, Workflow
from eija_studio.domain.policy import apply_transaction, baseline, check_policy

BEGIN = "<!-- BEGIN GENERATED: excursion-diff (scripts/gen_readme_diagram.py; do not edit by hand) -->"
END = "<!-- END GENERATED: excursion-diff -->"
README = ROOT / "README.md"


def _edge_label(t, tag: str) -> str:
    return f"{t.action} / {t.role}{tag}"


def state_diagram(model: Workflow, *, new_states: set[str], changed: dict[str, str]) -> str:
    """Mermaid stateDiagram-v2 for one model. `changed` maps transition id -> tag such as ' (new)'."""
    lines = ["stateDiagram-v2", "    direction LR", f"    [*] --> {model.initial_state}"]
    lines.extend(f"    {t.from_state} --> {t.to_state}: {_edge_label(t, changed.get(t.id, ''))}"
                 for t in sorted(model.transitions, key=lambda x: x.id))
    if new_states:
        lines.append("    classDef added fill:#ffe8b3,stroke:#b26a00,color:#000")
        lines.extend(f"    class {state} added" for state in sorted(new_states))
    return "\n".join(lines)


def diff(before: Workflow, after: Workflow) -> dict[str, list[str]]:
    """Structural diff by transition id. Pure function of the two typed models."""
    b = {t.id: t for t in before.transitions}
    a = {t.id: t for t in after.transitions}
    out: dict[str, list[str]] = {"states": [], "added": [], "changed": [], "removed": []}
    out["states"] = sorted(set(after.states) - set(before.states))
    for tid in sorted(a.keys() - b.keys()):
        t = a[tid]
        out["added"].append(f"`{tid}` {t.role}: {t.from_state} -> {t.to_state}")
    for tid in sorted(b.keys() - a.keys()):
        out["removed"].append(f"`{tid}`")
    for tid in sorted(a.keys() & b.keys()):
        old, new = b[tid], a[tid]
        if old == new:
            continue
        fields = [f"{f}: {getattr(old, f)} -> {getattr(new, f)}"
                  for f in ("from_state", "to_state", "role", "guards", "required_effects")
                  if getattr(old, f) != getattr(new, f)]
        out["changed"].append(f"`{tid}` {'; '.join(fields)}")
    return out


def _group_affected(affected: list[str]) -> list[str]:
    """Bullets for impact artefact ids: `kind:Action` ids grouped by kind, bare ids listed as they are."""
    grouped: dict[str, list[str]] = {}
    for artefact in sorted(affected):
        kind, sep, action = artefact.partition(":")
        grouped.setdefault(kind, []).append(action if sep else "")
    return [f"- `{kind}:` {', '.join(actions)}" if actions[0] else f"- `{kind}`" for kind, actions in grouped.items()]


def render_block() -> str:
    """The full generated README section (markers included)."""
    before = baseline()
    after = apply_transaction(before, SemanticTransaction(kind="enable_recommendation"))
    d = diff(before, after)
    new_ids = {t.id for t in after.transitions} - {t.id for t in before.transitions}
    b_by = {t.id: t for t in before.transitions}
    changed_ids = {t.id for t in after.transitions if t.id in b_by and b_by[t.id] != t}
    tags = {**dict.fromkeys(new_ids, " (new)"), **dict.fromkeys(changed_ids, " (changed)")}
    impact = model_impact(before, after)

    # A protected-authority violation, to show the policy is not decorative: a candidate that hands
    # the registrar's final approval to Teacher is rejected by the kernel's own check_policy.
    unsafe = after.model_copy(update={"transitions": tuple(
        t.model_copy(update={"role": "Teacher"}) if t.action == "Approve" else t for t in after.transitions)})

    parts = [
        BEGIN,
        "**Before**: the baseline workflow (`domain.policy.baseline()`).",
        "",
        "```mermaid",
        state_diagram(before, new_states=set(), changed={}),
        "```",
        "",
        "**After**: the `recommend_only` candidate (`apply_transaction(baseline, enable_recommendation)`). "
        "The amber state is new; edge labels say `(new)` or `(changed)`.",
        "",
        "```mermaid",
        state_diagram(after, new_states=set(d["states"]), changed=tags),
        "```",
        "",
        "What changed, diffed from the two typed models by `scripts/gen_readme_diagram.py` (not written by hand):",
        "",
        *[f"- new state `{s}`" for s in d["states"]],
        *[f"- added {line}" for line in d["added"]],
        *[f"- changed {line}" for line in d["changed"]],
        *[f"- removed {line}" for line in d["removed"]],
        "",
        f"The kernel's own impact closure, `domain.impact.model_impact(baseline, candidate)`, reaches "
        f"{len(impact['affected'])} artefacts from the changed action{'s' if len(impact['changed_actions']) != 1 else ''} "
        f"{', '.join(f'`{a}`' for a in impact['changed_actions'])} "
        f"(`complete: {impact['complete']}`). It follows a fixed rule → runtime → state view → journey → obligation → "
        f"receipt → review packet → local decision chain per action, so it is the encoded projection mapping, "
        f"not every real-world consequence:",
        "",
        *_group_affected(impact["affected"]),
        "",
        f"`check_policy(baseline)` -> `{check_policy(before)}`. "
        f"`check_policy(candidate)` -> `{check_policy(after)}`. "
        f"A candidate that lets a Teacher approve is rejected: `check_policy(unsafe)` -> `{check_policy(unsafe)}`.",
        "",
        "<!-- TODO(visual lane): when docs/assets/visual-diff.png exists on main, add "
        "![generated visual diff](docs/assets/visual-diff.png) here and drop this block. -->",
        END,
    ]
    return "\n".join(parts)


def splice(text: str, block: str) -> str:
    """Replace the marked region of `text` with `block`. Raises if markers are missing."""
    start, end = text.find(BEGIN), text.find(END)
    if start < 0 or end < 0 or end < start:
        raise SystemExit(f"README.md is missing the generated-region markers:\n  {BEGIN}\n  {END}")
    return text[:start] + block + text[end + len(END):]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    current = README.read_bytes().decode("utf-8")
    updated = splice(current, render_block())
    if args.write:
        README.write_bytes(updated.encode("utf-8"))
        print("README.md: generated region rewritten")
        return 0
    if updated != current:
        print("FAIL README.md excursion diagram is stale; run: python scripts/gen_readme_diagram.py --write")
        return 1
    print("PASS README.md excursion diagram matches domain.policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
