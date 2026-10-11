# PlayIDE roadmap

Status as of **2026-10-11**. This replaces the 29 September lane-status snapshot. It describes the current working tree and approved direction, not a claim that every local change has reached `main` or passed release acceptance. Use Git history and linked run records for exact revisions; old test totals do not describe new code.

PlayIDE makes engineering understandable and enjoyable through a living model of the system. It addresses **comprehension debt**: the understanding people still owe software that changes faster than they can explain it. Cities: Skylines, tycoon games, Roblox tycoons and Minecraft inspire building, trying, inspecting consequences and improving systems. The applications extend beyond games.

The audience remains UML-literate engineers, including people increasingly building through prompts. Prompt-first creation, model-first editing and source-first exploration belong in one nonlinear workbench. See the [product thesis](engineering/PRODUCT-THESIS.md), [mission](engineering/MISSION.md) and [continuous delivery contract](engineering/PLAYIDE-DELIVERY.md).

## What exists, and what the evidence establishes

Track four separate states: **implemented** (code exists), **integrated** (connected through the intended product path), **exercised** (observed for a named subject) and **release-ready** (the applicable acceptance criteria are met). A row can have an implementation while its evidence remains PARTIAL, FAIL, STALE or NOT_RUN.

| Capability | Implementation and integration | Evidence and release boundary |
|---|---|---|
| Typed workflow kernel, generated views, edit checks, source connection and agent inspection | Existing foundation; the local workbench connects model, source, review and history | The [8 October integration record](engineering/2026-10-08-IDE-ON-MAIN.md) is historical. Current combined SD01–SD12 and UX01–UX08 acceptance remains open. |
| Exact workflow draft transfer and activation | Owner `POST /api/cases/from-plan`, provenance, candidate checks and existing atomic application are implemented | [Activation contract](engineering/PLAYIDE-ACTIVATION.md) and [service checker](engineering/PLAYIDE-ACTIVATION-EVIDENCE.md). Synthetic owner fixtures exercise mechanics; they do not approve this implementation. |
| Effects, requirements and lifecycle capability map | Connected/grouped effects and capability views are implemented | Explicit links and known-graph consequences have bounded coverage. Prose, policy and executable meaning remain separate. |
| Design + Play and shared generated-app presentation | Paired studio/app layout and shared template improvements exist locally | [Design contract](design/PLAYIDE-DESIGN-AND-PLAY.md). Earlier recordings cover their named revisions, not later tracing/C4 changes. |
| Actual-action tracing and C4 | New local runtime bridge, UI and C4 route exist; integration is being verified | Current combined browser, identity and recovery evidence is incomplete. Presence of code or a drawn connection is not a passed runtime check. |
| AI creation and proposals | Offline phrase reader plus existing provider adapters; a general live PlayIDE creation experience remains incomplete | A consented live pilot is NOT_RUN for this milestone. Fixtures do not establish provider effectiveness. |
| Data-dependent actions, general migrations and connected workflows | Next executable semantics; multiple drawn workflows do not yet establish coordinated runtime behaviour | Remain unsupported until typed meaning, persistence, refusal and recovery contracts are exercised. |
| Production operations, external adoption and measured human benefit | Later milestones | NOT_RUN. The local trusted-user application is not a shared production service. |

`SOURCE_REVIEW_REQUIRED` stays visible for changed implementation. A labelled development preview can demonstrate supported capabilities with this restriction. Trusted verification/activation claims require legitimate owner source review; agents never restamp or fabricate that decision.

## Milestones

Ship small verified increments directly to `main` throughout these milestones. The exit criteria define stronger product claims, not a reason to hold every improvement until the end. See [delivery and checks](engineering/PLAYIDE-DELIVERY.md#ship-continuously).

| Milestone | Useful outcome and next scope | Exit evidence |
|---|---|---|
| **M0 — Baseline** | Preserve existing work, reconcile dated documents, map capabilities to existing requirements/issues and split accumulated work into coherent commits | Exact revision/content inventory; implemented/integrated/exercised/release states; fixed M1 acceptance list. This documentation is part of M0, not its completion. |
| **M1 — Coherent local workbench** | Complete tracing and C4, shared selections, persistent navigation/recovery, generated-app states and reviewable proposals. Finish PlayIDE's own read-only source dogfooding | Ordinary browser journey: inspect → edit → effects → check → refusal → repair → owner approval → activate → reopen. Fresh SD01–SD12 and UX01–UX08 observations, clean setup, negative controls and inspected demos; owner checkpoint separately recorded. |
| **M2 — Real data and safe evolution** | RefundDesk typed action inputs, value conditions, bounded calculations and record updates through the existing kernel. Same-schema revision adoption first; explicit migrations before schema/state changes retain real records | Refused values preserve records; accepted effects are transactional. Compatibility preview, backup, migration validation and recovery are exercised through the app. |
| **M3 — Relationships and connected workflows** | References, multiplicities, aggregate invariants and bounded queries, then versioned events, correlation, idempotency, outbox delivery, timers and recovery | Club application → moderation → Minecraft access → welcome message against isolated services; duplicates and an unavailable service recover without duplicate effects. VibeCord remains separate. |
| **M4 — Source/model evolution and parallel changes** | Graded repository support; first bounded, statically resolved Python rename/refactoring; agent/worktree visibility and semantic overlap checks | Refuse dynamic/unresolved transformations. Detect a conflict between individually valid branches, resolve it and check the actual combined result. No built-in code editor. |
| **M5 — Operable shared applications** | Authenticated identities, resource permissions, protected secrets, deployment/configuration, quotas, monitoring/cost, backup, retention and incident recovery | Independent deployment, unauthorised-access refusal, restart/restore and actionable failures. Rollback accounts for migrated data and irreversible external effects. |

M1 includes a versioned, server-derived build/review subject covering workflow, pack, data, screens, generator/templates and implementation. Evidence also identifies checker and configuration. Preserve existing case/selection contracts and keep old evidence historical; identity is not proof of correctness.

## The whole product, not only diagrams

- **Domain and meaning:** DDD vocabulary, contexts, aggregates, requirements, business rules and laws share stable identities and explicit links. Inferred concepts stay proposals until confirmed. Every construct says executable, checked design or unsupported.
- **Everyday work:** explorer, tabs, splits, search, command palette, inspector, problems, evidence and history preserve context. Source facts, model simulations and observed behaviour remain distinguishable across UML and C4.
- **AI and collaboration:** selection-grounded proposals show provenance, scope, uncertainty and request status. Agents propose, deterministic services check, owners decide. Parallel changes are checked on their combined result.
- **Product craft:** workbench and generated apps both need good forms, validation, empty/busy/error states, keyboard operation, readable layout and recovery. Customisable presentation never silently changes policy. Reward recorded useful outcomes.
- **Lifecycle and portability:** versioned packs/adapters, export, migration, configuration, operations, security and recovery are explicit capabilities. Reuse maintained dependencies and one kernel; retain the local-first Apache-2.0 project.

## Acceptance and progress

The [self-dogfood contract](engineering/SELF-DOGFOOD-ACCEPTANCE.md) remains authoritative for **SD01–SD12** and **UX01–UX08**. Reuse **AC** IDs from the [acceptance matrix](verification/ACCEPTANCE_MATRIX.csv); its dated status columns are historical. Existing issue references include [#79](https://github.com/45ck/eija-studio/issues/79) for HCI budgets, [#93](https://github.com/45ck/eija-studio/issues/93) for connected workflows, [#145](https://github.com/45ck/eija-studio/issues/145) for relationships and [#152](https://github.com/45ck/eija-studio/issues/152) for live chat. These are traceability links, not assertions about current GitHub issue state; check before creating duplicates.

Keep implementation checks, model fidelity, usability and human benefit as distinct evidence. The [V&V protocol](research/2026-10-02-vv-protocol.md) governs the later engineer comparison. Fresh installation, actual rendering/response measurements and meaningful negative controls cannot be replaced by test counts or a polished recording.

Record 30–90-second actual-app clips after verifying each demonstrated increment; retain raw media, build/revision identities, results and skipped functionality. Keep failures visible and distinguish fixtures, simulations, local apps and real integrations. Publish longer walkthroughs when the full supported journey is ready. Audience response, enjoyment and comprehension improvement remain hypotheses until observed.

Older [lane hubs](engineering/LANE-MAP.md), [WBS](engineering/WBS.md) and [September status](engineering/STATUS.md) preserve design history. Their old branch/PR sequencing is superseded by the initial direct-main policy. [Future work](engineering/FUTURE-WORK.md) preserves unresolved technical leads without presenting every historical deferral as a fresh audit.

## Historical lane and reserved ADR allocations

These allocations preserve the [ADR registry](adr/README.md) and earlier lane map. They identify responsibility and prevent number collisions; they are not current progress statuses, required branch names or a sequence of releases. Individual ADRs retain their own accepted/proposed status.

| ADR block | Lane responsibility |
|---|---|
| 0021-0022 | Proposal providers and CLI isolation |
| 0023-0024 | Generated UML, visual diff and sandboxed rendering |
| 0025-0026 | Bend laws and proofs |
| 0027-0028 | TLA+/TLC and trace conformance |
| 0029-0030 | SMT soundness and bounded model checking |
| 0031-0032 | Property-based and model-based testing |
| 0033-0034 | Mutation analysis |
| 0035-0036 | Quality gates and architecture checks |
| 0037-0038 | Metrics and quantitative models |
| 0039-0040 | HCI and usability instrumentation |
| 0041-0042 | Agent integration, MCP and skills |
| 0043-0044 | OSS community, documentation and release |
| 0045-0046 | OKF knowledge base |
| 0047-0048 | Recordings and scenario dependency gates |
| 0049-0050 | Interactive UML editor |
| 0051-0052 | Ubiquitous language and DDD tree |
| 0053-0054 | Consent-gated image generation |
| 0055-0056 | Personas and end-to-end scenarios |
| 0057-0088 | HCI research and workbench UX |
| 0089-0112 | Weave linked graph, compiler and lint |
| 0113-0136 | Definition of done, claims and evaluations |
| 0137-0144 | Pattern recognition and checked refactoring |
| 0145-0152 | Evidence kinds and end-to-end integration; includes reserved integration block 0147-0149 |
