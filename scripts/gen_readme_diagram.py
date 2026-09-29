"""Generate the README before/after excursion diagrams from the real executable model.

What this establishes: the Mermaid text between the README markers is the output of the visual lane's own
generators (`application.diagram_catalog.render_view`, the code behind `eija render`) for
`domain.policy.baseline()` and `domain.policy.apply_transaction(..., enable_recommendation)`, and the change
list and impact list come from `application.diagrams.diff_summary` and `domain.impact.model_impact`. If the
model or a generator changes and the README does not, `--check` fails (nox session `readme_diagram`).

What this does NOT establish: that the diagram is a proof of anything, or that it is the reviewed change.
Nothing here is hand-drawn, and nothing here is an authority decision.

    python scripts/gen_readme_diagram.py --write   # regenerate README.md in place
    python scripts/gen_readme_diagram.py --check   # exit 1 when README.md is stale
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eija_studio.application.diagram_catalog import render_view
from eija_studio.application.diagrams import diff_summary
from eija_studio.domain.impact import model_impact
from eija_studio.domain.models import SemanticTransaction, Workflow
from eija_studio.domain.policy import apply_transaction, baseline, check_policy

BEGIN = "<!-- BEGIN GENERATED: excursion-diff (scripts/gen_readme_diagram.py; do not edit by hand) -->"
END = "<!-- END GENERATED: excursion-diff -->"
README = ROOT / "README.md"


def mermaid(view: str, before: Workflow, after: Workflow | None = None) -> str:
    """The exact text `eija render --view VIEW --format mermaid` prints, without the trailing newline."""
    return render_view(view, "mermaid", before, after).rstrip(chr(10))


def change_lines(before: Workflow, after: Workflow) -> list[str]:
    """Bullets for the semantic diff, from `diff_summary` (a pure function of the two typed models)."""
    d = diff_summary(before, after)
    lines = [f"- new state `{s}`" for s in d["added_states"]]
    lines += [f"- removed state `{s}`" for s in d["removed_states"]]
    lines += [f"- new action `{a}`" for a in d["added_actions"]]
    lines += [f"- removed action `{a}`" for a in d["removed_actions"]]
    for action, fields in d["changed_actions"].items():
        lines += [f"- `{action}` {f['field']}: `{f['before']}` becomes `{f['after']}`" for f in fields]
    return lines


def _group_affected(affected: list[str]) -> list[str]:
    """Bullets for impact artefact ids: `kind:Action` ids grouped by kind, bare ids listed as they are."""
    grouped: dict[str, list[str]] = {}
    for artefact in sorted(affected):
        kind, sep, action = artefact.partition(":")
        grouped.setdefault(kind, []).append(action if sep else "")
    return [f"- `{kind}:` {', '.join(actions)}" if actions[0] else f"- `{kind}`" for kind, actions in grouped.items()]


def _fence(text: str) -> list[str]:
    return ["```mermaid", text, "```"]


def render_block() -> str:
    """The full generated README section (markers included)."""
    before = baseline()
    after = apply_transaction(before, SemanticTransaction(kind="enable_recommendation"))
    impact = model_impact(before, after)

    # A protected-authority violation, to show the policy is not decorative: a candidate that hands
    # the registrar's final approval to Teacher is rejected by the kernel's own check_policy.
    unsafe = after.model_copy(update={"transitions": tuple(
        t.model_copy(update={"role": "Teacher"}) if t.action == "Approve" else t for t in after.transitions)})

    parts = [
        BEGIN,
        "**Diff** (`eija render --workflow examples/excursion-candidate.json --view diff --format mermaid`): "
        "green is added, amber is changed, a `+` label is a new or changed transition and a `-` label is a "
        "transition the candidate no longer has. The first two comment lines carry the semantic hashes of the "
        "two workflows the diagram was generated from.",
        "",
        *_fence(mermaid("diff", before, after)),
        "",
        "<details><summary>The same two workflows as separate state diagrams "
        "(<code>--view state</code>, baseline then candidate)</summary>",
        "",
        "Baseline:",
        "",
        *_fence(mermaid("state", before)),
        "",
        "Candidate (`recommend_only`):",
        "",
        *_fence(mermaid("state", before, after)),
        "",
        "</details>",
        "",
        "What changed, from `diff_summary` over the two typed models (not written by hand):",
        "",
        *change_lines(before, after),
        "",
        f"The kernel's own impact closure, `domain.impact.model_impact(baseline, candidate)`, reaches "
        f"{len(impact['affected'])} artefacts from the changed action{'s' if len(impact['changed_actions']) != 1 else ''} "
        f"{', '.join(f'`{a}`' for a in impact['changed_actions'])} "
        f"(`complete: {impact['complete']}`). It follows a fixed rule, runtime, state view, journey, obligation, "
        f"receipt, review packet, local decision chain per action, so it is the encoded projection mapping, "
        f"not every real-world consequence. Draw it with `--view impact`; the affected artefacts are:",
        "",
        *_group_affected(impact["affected"]),
        "",
        f"`check_policy(baseline)` -> `{check_policy(before)}`. "
        f"`check_policy(candidate)` -> `{check_policy(after)}`. "
        f"A candidate that lets a Teacher approve is rejected: `check_policy(unsafe)` -> `{check_policy(unsafe)}`.",
        END,
    ]
    return chr(10).join(parts)


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
