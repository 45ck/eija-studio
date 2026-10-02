# Definition of done: IDE proof of concept and feasibility

## Current scope: 2 October 2026

Deliver a **complete, polished, non-linear EIJA IDE for UML-literate engineers using AI**, first connected to EIJA's own checkout. The concept is demonstrated when engineers can freely explore domain concepts, edit supported models, follow source, inspect agent changes, review impact/evidence, revisit history and recover from refused or stale edits. A wizard, disconnected shell or filmed happy path does not close this goal.

The **proof of concept (POC)** makes that working experience tangible; the **proof of feasibility (POF)** lets another engineer reproduce setup, use and scoped evidence from a clean checkout. The WOW walkthrough, focused clips and README visuals are captured from the verified product. See the [mission and readiness criteria](MISSION.md#prototype-readiness) and [self-dogfood engineering/UX acceptance](SELF-DOGFOOD-ACCEPTANCE.md).

Planned foundations include a configured read-only EIJA repository connection, supported tracked Python and annotated UI extraction, a domain tree, server-checked model editors and repository-impact views. Planned agent reads include pack context, affordances and dry-run edit/impact checks. **This documentation publication does not implement those capabilities.** Implementation, clean-checkout replay, integrated UX acceptance and the new run record remain pending.

Repository intake, structural facts, behavior bindings and verified properties have separate coverage. Initial model editing changes the supported candidate, not connected repository source. External applications follow EIJA acceptance. Live model validation and the engineer study remain NOT_RUN; no novelty, superiority or universal code generation is claimed. Keep source-review status explicit and complete the maintainer gate legitimately before claiming trusted verification/apply.

## Historical H1a definition: 29 September 2026

The criteria and exclusions below preserve the earlier excursion-only H1a plan. In particular, the former workbench/diagram-editing exclusions are superseded for the current self-dogfood milestone above. They are not evidence that either milestone has passed. Use the mission and current acceptance contract above for the release goal; the old exclusions do not reduce the full IDE or UX requirement.

The POC is done when a stranger can clone the repository, run it on their machine, and watch an AI agent's change to a business rule be reviewed **by meaning**, with generated diagrams, formal evidence (UNKNOWN visible) and a human decision. It is deliberately the "H1a" slice of [the ship horizons](LANE-MAP.md): a bounded domain (the excursion workflow), not yet arbitrary repositories. See [the product thesis](PRODUCT-THESIS.md) for why.

### Historical acceptance criteria

| # | Criterion | Evidence that closes it | Needs |
|---|---|---|---|
| 1 | **Fresh clone runs.** Clone, install, `eija serve` on Windows, macOS and Linux; no red error banner on a release build. | a clean-clone install log per platform; `eija doctor` output | owner restamp at the release checkpoint (or an approved dev-mode policy) |
| 2 | **An agent proposes through MCP.** A real agent (Claude Code, Codex, OpenCode or Gemini CLI) proposes a rule change; it cannot select meaning, approve or apply. | a live smoke record per agent that was actually logged in (`NOT_RUN` otherwise); the MCP authority-boundary tests | providers, agents lanes |
| 3 | **Reviewed by meaning.** The Studio shows the semantic before/after diff and the ripple, generated from the executable model, not hand-drawn. | drift gate on generated diagrams; golden tests | visual lane |
| 4 | **Evidence, honestly.** The review packet shows the runtime matrix plus **formal evidence kinds** (SMT proof, bounded model check, TLC model check, Bend proof, property test, mutation score) each with its assumptions and bounds; anything unrun or out of scope is UNKNOWN, never green. | per-kind admissibility recomputed from raw artifacts (like the runtime matrix today); negative controls fail | formal lanes and the `evidence-kinds` lane |
| 5 | **The unsafe change is stopped.** An agent proposal that would give teachers final approval is blocked by policy, and the formal check produces a counterexample. | a recorded run with the counterexample rendered | evidence-kinds, visual |
| 6 | **One end-to-end test.** A pytest exercises the whole chain offline: MCP propose, diagrams, verification, formal evidence, owner decision. | the test, run in the full gate tier | `e2e` lane |
| 7 | **Gates green on main.** ruff, mypy (linux and win32), architecture, complexity, dependencies, ADR index, tests. | `nox -t full` output | quality lane |
| 8 | **Honest README.** Every claim links to evidence or is marked planned; a 60 second recording of the flow; ADR list and OSS register visible. | link check; README claims audit | oss lane, demos re-record |

### Historical exclusions

Reviewing changes to an arbitrary repository (needs the `weave` compiler), the redesigned IDE workbench, drag-and-drop UML editing, design-pattern views, image generation, multi-user or hosted operation. These are the next horizons, not omissions.

### Historical owner steps

Restamping the release fixture; supplying API keys; consenting to live provider spend; approving publication (tag, README, recording).

### Historical status

Tracked in the pull request list and the lane map, not here, so this file does not go stale.
