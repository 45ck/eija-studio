# EIJA mission and delivery goals

Established **2 October 2026**, incorporating the owner's clarification that the goal is a complete, polished IDE experience, not a minimal demo. This is the current mission for prioritizing work. It does not declare the product or its validation complete. This clarification supersedes earlier wording that a small working slice alone was sufficient for the WOW release.

## Mission

**Help UML-literate engineers build with AI while retaining an accurate understanding of what their software means and what an agent changes.**

EIJA makes domain concepts, language, rules and consequences visible through an editable model, source connections and evidence. Engineers can prompt or model; the workbench helps them inspect and direct the result. The central product problem is comprehension: being able to explain a change, detect a harmful change of meaning and maintain the software afterward.

The first connected project is **EIJA itself**. Finish a coherent, polished local IDE across the supported workflow before broadening to external applications. The engineer must be able to explore, edit, inspect agent changes, follow source, review evidence, revisit history and recover from mistakes without being funnelled through a wizard. Repository intake, structural extraction, selected behavior bindings, verified properties and source transformation are separate support levels. A source link is not a proof of behavior; a model check is not a universal guarantee about a codebase.

The [product thesis](PRODUCT-THESIS.md) defines the wider design direction. The [self-dogfood acceptance contract](SELF-DOGFOOD-ACCEPTANCE.md) defines the current engineering flow. The [research and V&V protocol](../research/2026-10-02-vv-protocol.md) defines how stronger benefit claims can eventually be tested.

## Goal 1: a WOW demo people can understand

Deliver a **complete, polished, source-grounded IDE experience for the supported workflow**, then demonstrate that product through a clear walkthrough and useful showcase clips. A viewer should be able to identify the intended rule change, see which source and model elements it affects, understand a refusal or unknown, and inspect the evidence behind the result. An engineer must also be able to use those capabilities outside the recording's chosen path.

The release bar includes a non-linear explorer/editor workbench, usable diagrams, source navigation, agent changes, review, persistent evidence/status, history, keyboard interaction and recoverable edits. A reskinned wizard, attractive shell, disconnected panels or one carefully staged path is insufficient. Scope remains bounded by honest language and verification support; the experience within that scope must feel complete and work well. The four scenes below remain a roadmap and may have separate capability prerequisites; finishing one scene does not certify the full IDE experience.

The four flagship scenes guide expansion:

| Scene | What the viewer should see | Capability required before recording it as working |
|---|---|---|
| Build and evolve with AI | The same feature developed and changed repeatedly, with the resulting domain meaning and drift visible | Frozen starting snapshots, task sequence and an independent behavior oracle; complete results for both comparison conditions. No scripted claim that another tool must fail. |
| Explain an agent's change | A semantic before/after view, known dependency ripple, actual source references and evidence/unknowns in one coherent review | Source-connected model facts and reproducible impact/evidence for the exact demonstrated revision. This is the first connected IDE's central review scene. |
| Edit UML and see the consequence | A permitted model edit changes supported behavior; an unsafe edit is refused with a useful explanation | Real server-checked typed edits and an observed runtime consequence. Candidate-runtime changes and repository-source changes must be labeled distinctly; do not imply general code generation. |
| Coordinate parallel changes | Two individually plausible changes overlap semantically; the combined result is checked before landing | Reproducible worktree fixtures, semantic overlap checks and gates on the actual merge result. A graph or animation alone cannot demonstrate safe landing. |

Visual and interaction quality are release criteria across ordinary use, not a final coat of paint for a recording. Explorer, editors, source, changes, review, evidence and history must preserve their shared selection and state as the engineer navigates in different orders. Require legible labels and source details, useful diagram routing and zoom/fit, discoverable actions, visible focus, clear loading/error/success feedback, no clipping or collisions that obscure meaning, keyboard alternatives and persistent source/evidence status. Edits must be cancellable or safely recoverable; stale and refused actions must preserve valid work. Record actual response times and fix disruptive waits rather than hiding them in an edit. The [IDE UX rubric](SELF-DOGFOOD-ACCEPTANCE.md#ide-ux-rubric) is part of acceptance. A reviewer should use the product and understand the walkthrough without needing this chat.

Capture content only after the integrated product has passed the supported engineering and UX journeys, using retained, verified runs: a short flagship walkthrough, focused clips showing individual capabilities, and useful stills for the README. Each published artifact names its demonstrated revision and scope, labels fixture or live-agent activity accurately, and links to reproduction/evidence. Captions and editing may clarify the run; they must not manufacture results or splice failure and success into a misleading continuous interaction. Preserve the underlying run record. Remove private paths, secrets and irrelevant personal content before publication.

## Goal 2: GitHub proof of concept and proof of feasibility

The owner intends **both POC and POF**:

- **Proof of concept:** a coherent IDE experience makes the product idea tangible. The engineer can explore freely, inspect the meaning and consequences of an AI-style proposal, edit the supported model, follow actual source, review evidence and history, and recover safely across normal and failure paths.
- **Proof of feasibility:** another engineer can obtain the declared code revision, follow documented setup, use the supported IDE workflow and reproduce its scoped checks and evidence without relying on the author's private environment.

These labels describe an engineering demonstration, not a mathematical proof of all software. The GitHub package should include runnable source, a clear README, current setup instructions, declared platform/dependency prerequisites, a bounded acceptance record, replayable fixtures/evidence, license and third-party notices, and the demo/video links. State what works, what is partially supported and what has not run. A polished video alone does not close POF; a passing test command alone does not close POC.

## Prototype readiness

The POC/POF package is ready when the following checks are evidenced for **the complete supported IDE experience**, including normal navigation and recovery rather than only the recorded path:

| Readiness check | Required evidence |
|---|---|
| The coherent IDE works | Ordinary browser-to-server journeys cover explorer/editor navigation, model edits, source links, agent changes, review/evidence, history and safe recovery. Traverse these in more than one order without losing context or making contradictory panels. The walkthrough agrees with the usable product. |
| Tests distinguish safe and unsafe behavior | Targeted tests and negative controls cover the supported model edit, refusal, stale state/evidence, read-only source boundary and displayed source/model correspondence. Applicable local gates run on the final integrated tree; skipped capabilities stay explicit. |
| A clean checkout can start | Record setup and replay from a clean checkout using the documented supported platform and dependencies. Offline fixtures support reproducible checks but do not replace using the integrated IDE. Live-agent claims require an actual recorded live run. Do not claim platforms not tested. |
| Evidence is replayable and scoped | Retain exact revision/content identity, model/pack/configuration, tool versions, commands, raw results, negative controls and declared extraction/verification limits. Expected and observed behavior are distinguishable. |
| Source review is handled honestly | Keep `SOURCE_REVIEW_REQUIRED` visible when implementation differs from the owner-reviewed fixture. A development POC may demonstrate read-only/model-edit capabilities with that restriction explicitly shown. Claim trusted verification or apply only after the maintainer's source-review gate is legitimately complete; agents never restamp or bypass it. |
| Licenses and source boundaries are clear | Check the OSS register, pinned/vendor provenance and required license notices. Exclude private logs, credentials, unrelated source and unlicensed artifacts. Record any dependency or redistribution limitation. |
| The UX and presentation are ready | Pass the IDE UX rubric on actual working journeys: readable unclipped layout, intelligible diagrams, coherent navigation, safe edit recovery, history, keyboard focus and feedback. Record review findings and fix consequential usability defects. Then produce the walkthrough and clips; test counts and video editing cannot substitute for this gate. |
| GitHub reflects the artifact | Publish reviewed progress through focused commits and documentation/implementation PRs as work proceeds. Use auto-merge only where repository rules and required checks permit it. Coordinate the POC/POF release so the README, runnable code/artifact revision, setup and reproduction steps, evidence links and limitations agree. Earlier progress PRs do not establish release readiness. Do not present planned scenes or historical test totals as current results. |

An expected, disclosed source-review restriction or unsupported capability is different from an undisclosed defect in an advertised path. Data loss, source mutation through the read-only connection, false evidence attribution, a missed declared critical fixture or a broken advertised flow blocks readiness. Fix those before packaging.

The full supported IDE experience is required for the WOW/POC release. Universal external-codebase coverage, every formal engine, production deployment and a statistically decisive human study remain separate claims and milestones. The parallel-landing flagship scene has its own real implementation requirements. Live model effectiveness, human comprehension improvement and superiority to alternatives remain NOT_RUN until supported; these limits do not excuse an incomplete or frustrating interface within the workflow being delivered.

## Build on maintained OSS

OSS reuse is non-negotiable. Start with maintained frameworks, parsers/compiler indexes, graph/diagram libraries, storage, testing tools, provers and model checkers that already solve the underlying problem. EIJA owns its domain contracts and the adapters/generators that connect those tools into the product.

Before adding a new engine or substantial custom subsystem, record the capability gap, maintained alternatives evaluated, fit/limitations, license, pinned provenance, integration cost and replacement path in the [OSS register](../oss/REGISTER.md), with an ADR when the architecture changes. Reuse and adapt before reimplementing. Do not invent a parser, solver, renderer, orchestrator or test runner merely for a distinctive architecture. A custom exception must explain the concrete unsupported need and remain replaceable. Follow [ADR-0016](../adr/0016-oss-first-adapters-not-engines.md).

Existing dependencies are not automatically endorsed forever: verify maintenance and suitability when making an adoption/change decision. UI polish should be built on appropriate existing primitives without creating a second semantic kernel in JavaScript. Deterministic code owns supported facts, edits and checks; AI proposes interpretation and explanation within those boundaries.

## Organize delivery around evidence

Use one active integration path and one integrating writer. Assign a named owner to each changed file/module; parallel contributors stage disjoint patches and hand off originals, changed files and checks. Do not add worktrees by default. Reuse the existing checkout/worktrees; create another only for a concrete isolation need with an owner and cleanup/handoff plan. Never reset or overwrite another contributor's work.

Keep a small milestone ledger with: outcome, owner, dependencies, files, acceptance observation, evidence location, current status and next action. The ledger links to the existing acceptance/run records rather than duplicating test totals. Mark implemented, integrated, exercised and ready separately. Record unresolved failures and NOT_RUN checks alongside successes. Read the mission before adding another backend, diagram, abstraction or experiment: it should complete the supported IDE experience, improve engineers' understanding and control, or supply necessary readiness evidence.

The critical path is:

**EIJA connection and semantic contracts → coherent explorer/editors/source/agent-review/evidence/history → integrated engineering and UX journeys, including recovery → clean-checkout replay and usability fixes → evidence-derived video and GitHub POC/POF package.**

The four flagship scenes remain the demonstration roadmap, with their own tested capability prerequisites. External adoption and formal human-benefit evaluation follow the EIJA target. Their scope stays explicit, while the integrated IDE and UX gate is mandatory for the supported product release. Run resource-heavy gates serially. Broaden tests when a change or unresolved defect justifies it, rather than repeating already-passing expensive checks without new information.

## Current goal status

| Outcome | Current state | Evidence needed to advance |
|---|---|---|
| Full supported self-dogfood IDE | Integrating; final combined result not established by this mission | [Acceptance and current run record](SELF-DOGFOOD-ACCEPTANCE.md#run-record) |
| WOW walkthrough and clips from the usable IDE | Not declared ready | Passing integrated engineering/UX journeys, resolved consequential usability findings and captured artifacts tied to the run |
| GitHub POC/POF package | Not declared ready | Prototype readiness checklist above, clean-checkout replay, content/license checks and coordinated publication |
| Four-scene expansion | Staged goal; no all-four completion claim | Per-scene capability and replay evidence |
| External/held-out adoption and human benefit | Later; NOT_RUN | Separately selected targets and predeclared [V&V protocol](../research/2026-10-02-vv-protocol.md) |

Update these states from retained results at each milestone. This mission adds goals and priorities; it does not itself publish to GitHub, create a release, operate an external account or satisfy an owner source-review decision.
