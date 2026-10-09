"""The demo scenario catalogue: the single source of truth (ADR-0048).

`REGISTRY.md` is generated from this module and a gate fails if the two drift. A scenario module may
exist only when its status is not `blocked`, and a `blocked` scenario names the lanes it waits for -
never a stub file pretending to run. A scenario whose lanes have all landed but which has no script yet is
`unscripted`, not `blocked`: nothing else is in its way.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Literal, cast

from demos.manifest import load_manifest, manifest_path, stale_warnings, video_problems

Status = Literal["recorded", "recorded-partial", "scripted-not-recorded", "unscripted", "blocked"]
STATUSES: tuple[Status, ...] = ("recorded", "recorded-partial", "scripted-not-recorded", "unscripted", "blocked")

# Lanes known to the roadmap. Wave 1 is being built in parallel worktrees; wave 2 lanes were identified
# while scaffolding this catalogue because no wave-1 lane delivers them.
WAVE1_LANES = frozenset({
    "providers", "visual", "bend", "tla", "smt-bmc", "property", "mutation", "quality",
    "metrics", "hci", "agents", "okf", "oss", "demos",
})
WAVE2_LANES = frozenset({
    "uml-editor",    # interactive drag-and-drop UML canvas that issues typed semantic transactions
    "ddd-language",  # ubiquitous-language editor and DDD context/aggregate tree in the Studio
    "imagegen",      # in-Studio image generation via the provider port (consent + spend gated)
    "personas-e2e",  # personas / ICP artefacts and generated e2e scenarios tied to them
})
KNOWN_LANES = WAVE1_LANES | WAVE2_LANES
# Lanes that have landed on the integration branch (PR #29, 2026-09-29): every wave-1 lane. A scenario waits only for
# lanes NOT in this set, so this is the one place to edit when a wave-2 lane lands. A landed lane's Docker- or
# Java-backed sessions can still be NOT_RUN on a given machine; that is a run prerequisite, not a lane dependency.
LANDED_LANES = WAVE1_LANES

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Scenario:
    key: str
    title: str
    status: Status
    depends_on: tuple[str, ...]
    story: str

    @property
    def waits_for(self) -> tuple[str, ...]:
        """The lanes this scenario still waits for: the ones it uses that have not landed."""
        return tuple(d for d in self.depends_on if d not in LANDED_LANES)

    @property
    def module(self) -> str:
        return f"demos.scenarios.{self.key}"

    def manifest(self, root: Path = ROOT) -> Path:
        """Small committed evidence (hash, size, platform, skipped acts). The video itself is a large
        binary kept out of git (`demos/output/`, gitignored) and published as a release asset."""
        return manifest_path(self.key, root)


SCENARIOS: tuple[Scenario, ...] = (
    Scenario("assurance_loop", "The assurance loop: intent to applied baseline", "recorded-partial", (),
             "A vague request becomes explicit meanings; the owner selects one; the rule is exercised as "
             "different synthetic actors (including denials); evidence is computed; the owner approves the "
             "exact revision, then separately applies it. Needs no other lane: it is the shipped v0.2 flow."),
    Scenario("ide_walkthrough", "The IDE walkthrough: EIJA reviews a change to itself", "recorded-partial", (),
             "Connected read-only to its own checkout, EIJA shows the model of its review workflow, follows a "
             "concept into its exact source, turns a plain-language request into an owner-selected meaning, reviews "
             "the before/after model change, previews a kernel-checked edit without writing it, exercises the rules "
             "as an agent and the owner, and shows verification blocked until the owner reviews changed source."),
    Scenario("playide_tour", "The PlayIDE tour: design, build, simulate and check an AI's change", "recorded", (),
             "On the library-loan pack, PlayIDE shows the state machine, class, use case and component diagrams and the "
             "screen designer; builds and runs the app with its conformance cases; simulates users; draws a state and a "
             "transition from the palette; and checks an offline AI proposal step by step, rejecting the step the "
             "policy refuses, before building and simulating the result."),
    Scenario("playide_ripple", "PlayIDE ripple: change one diagram, see the others follow", "recorded", (),
             "On the library-loan pack, a state dragged onto the state machine ripples into the class diagram's state "
             "enumeration and is flagged unreachable; the offline AI's follow-on transition, re-checked by the policy, "
             "ripples into a new use case, a default screen and regenerated components, and the app is built. Then an "
             "AI-proposed removal strands a screen so the app cannot be built; the AI's follow-on removes it, the design "
             "check confirms, and the app builds with the checks ring showing that the diagrams agree."),
    Scenario("playide_showcase", "The PlayIDE showcase: software engineering as play", "recorded-partial", (),
             "The storyboarded showcase (docs/demos/PLAYIDE-SHOWCASE-STORYBOARD.md): the model is the program; press "
             "play and watch seeded users run through it; fix it in place; let the AI propose the busywork and check "
             "it step by step; prove it with conformance and simulation. Beats whose feature has not merged are "
             "skipped and named in the manifest."),
    Scenario("playide_highlights", "The PlayIDE highlights: the showcase in two minutes", "recorded-partial", (),
             "The showcase's story at README length, recorded as its own unedited take: the model is the program, "
             "press play to a breakpoint, edit in place and watch it ripple, let the offline AI propose a change, "
             "catch the step that deletes late returns with a prediction and the broken sequence diagram, then prove it "
             "with conformance, simulation, the laws and the scenario tests. Verify, approve and apply wait on #80."),
    Scenario("playide_review", "Review an AI's change in PlayIDE, not in a pull request", "recorded", (),
             "On the library-loan pack, an offline AI plan adds a renewal and quietly deletes late returns. The Review tab "
             "draws both models on one UML diagram, ranks each change by risk and shows what the kernel does differently "
             "for every fixture user. The reviewer predicts before each answer, catches the deleted path, asks for a "
             "change, rejects the step, reviews again and builds the result. Nothing is approved or applied."),
    Scenario("agent_change_review","Reviewing an agent's change by meaning, not by diff", "unscripted",
             ("agents", "providers", "visual"),
             "An agent (Claude Code, Codex, OpenCode or Gemini via MCP) proposes; the developer sees the "
             "meaning, the ripple into other models and the evidence - and the agent cannot approve."),
    Scenario("visual_diff_and_ripple", "Change a rule, watch the generated UML diff and ripple", "unscripted",
             ("visual",),
             "Before/after state machine, commit sequence and impact graph generated from the executable "
             "model, with added/removed/changed elements highlighted."),
    Scenario("uml_drag_and_drop", "Drag and drop UML that stays true to the code", "blocked",
             ("visual", "uml-editor"),
             "Edit the state diagram on a canvas; each gesture issues the same typed semantic transaction "
             "as the rule table, so the picture and the code cannot disagree."),
    Scenario("ubiquitous_language_ddd_tree", "Ubiquitous language and a DDD tree", "blocked",
             ("okf", "ddd-language"),
             "Define terms once; watch contexts, aggregates and invariants form a navigable tree linked "
             "to code and to the OKF wiki."),
    Scenario("image_generation_in_studio", "Generate images inside the Studio", "blocked",
             ("providers", "imagegen"),
             "Consent-gated image generation for journey and persona artefacts, kept as untrusted "
             "provider output like every other proposal."),
    Scenario("e2e_tests_personas_icp", "Personas, ICP and the e2e tests behind them", "blocked",
             ("personas-e2e", "quality", "property", "hci"),
             "Personas and the ideal customer profile drive generated e2e scenarios, shown next to the "
             "running app and the UML behind it."),
    Scenario("formal_vv_tour", "Formal V&V tour: Bend, TLA+, Z3, properties, mutation", "unscripted",
             ("bend", "tla", "smt-bmc", "property", "mutation"),
             "Each technique checks the same model; a deliberately unsafe variant fails in each, and every "
             "claim states what it does not prove."),
    Scenario("metrics_and_hci_dashboard", "Quantitative metrics and HCI-law budgets", "unscripted",
             ("metrics", "hci"),
             "Package metrics, complexity, latency against the Doherty threshold, Fitts/Hick/KLM budgets."),
    Scenario("okf_wiki_tour", "The OKF wiki, deterministically linked to code", "unscripted",
             ("okf",),
             "Follow a concept page to the exact code it describes; change the code and watch the page "
             "go stale in the gate."),
)


def check_consistency(scenarios: tuple[Scenario, ...] = SCENARIOS, root: Path = ROOT) -> list[str]:
    """Return human-readable problems; empty means the catalogue and the code agree."""
    problems: list[str] = []
    keys = [s.key for s in scenarios]
    problems += [f"duplicate key: {k}" for k in sorted({k for k in keys if keys.count(k) > 1})]
    for scenario in scenarios:
        problems += _check_scenario(scenario, root)
    return problems


def _check_scenario(s: Scenario, root: Path) -> list[str]:
    problems: list[str] = []
    unknown = sorted(set(s.depends_on) - KNOWN_LANES)
    if unknown:
        problems.append(f"{s.key}: unknown lane(s) {unknown}")
    has_module = find_spec(s.module) is not None
    if s.status == "blocked" and not s.waits_for:
        problems.append(f"{s.key}: status 'blocked' but every lane it needs has landed; it is 'unscripted' (or scripted)")
    if s.status != "blocked" and s.waits_for:
        problems.append(f"{s.key}: status {s.status!r} but it still waits for lane(s) {list(s.waits_for)}; it is 'blocked'")
    if s.status in ("blocked", "unscripted") and has_module:
        problems.append(f"{s.key}: {s.status} scenario must not have a module (ADR-0048)")
    if s.status not in ("blocked", "unscripted") and not has_module:
        problems.append(f"{s.key}: status {s.status!r} requires module {s.module}")
    return problems + _check_manifest(s, root)


def _check_manifest(s: Scenario, root: Path) -> list[str]:
    manifest = s.manifest(root)
    if s.status not in ("recorded", "recorded-partial"):
        return [f"{s.key}: manifest exists but status is {s.status!r}"] if manifest.exists() else []
    if not manifest.exists():
        return [f"{s.key}: status {s.status!r} but manifest {manifest.name} is missing"]
    loaded, problems = load_manifest(s.key, root)
    if loaded is None:
        return problems
    skipped = cast("list[str]", loaded["skipped"])  # shape-checked by load_manifest
    if s.status == "recorded" and skipped:
        problems.append(f"{s.key}: 'recorded' requires no skipped acts, manifest lists {len(skipped)}; "
                        "use 'recorded-partial'")
    if s.status == "recorded-partial" and not skipped:
        problems.append(f"{s.key}: 'recorded-partial' but the manifest lists no skipped acts; use 'recorded'")
    return problems + video_problems(s.key, loaded, root)


def manifest_warnings(scenarios: tuple[Scenario, ...] = SCENARIOS, root: Path = ROOT) -> list[str]:
    """Non-failing notes (a recording that predates the current script). Empty for unreadable manifests:
    those are already failures in `check_consistency`."""
    notes: list[str] = []
    for s in scenarios:
        if s.status in ("recorded", "recorded-partial") and s.manifest(root).exists():
            loaded, _ = load_manifest(s.key, root)
            if loaded is not None:
                notes += stale_warnings(s.key, loaded, root)
    return notes


def render_markdown(scenarios: tuple[Scenario, ...] = SCENARIOS) -> str:
    """Deterministic REGISTRY.md text (no timestamps)."""
    counts = {status: sum(s.status == status for s in scenarios) for status in STATUSES}
    lines = [
        "# Demo scenario registry",
        "",
        "<!-- Generated by `python -m demos registry --write` from demos/scenarios/registry.py. "
        "Do not edit. -->",
        "",
        f"**{counts['recorded']} recorded, {counts['recorded-partial']} recorded in part (an act was skipped "
        f"and is listed in its manifest), {counts['scripted-not-recorded']} scripted (not yet recorded), "
        f"{counts['unscripted']} unscripted (every lane it needs has landed; no script exists yet), "
        f"{counts['blocked']} blocked** on lanes that have not landed "
        "([ADR-0048](../../docs/adr/0048-scenario-dependency-gating.md)).",
        "",
        "| Scenario | Status | Waits for | Story |",
        "|---|---|---|---|",
    ]
    for s in scenarios:
        waits = ", ".join(
            f"`{d}`" + (" (wave 2)" if d in WAVE2_LANES else "") for d in s.waits_for
        ) or "nothing"
        lines.append(f"| `{s.key}` — {s.title} | {s.status} | {waits} | {s.story} |")
    lines += ["", "Every wave-1 lane has landed on the integration branch; the lanes a blocked scenario waits for are wave-2 "
              "capabilities the owner asked to demo that no wave-1 lane delivers.", ""]
    return "\n".join(lines)
