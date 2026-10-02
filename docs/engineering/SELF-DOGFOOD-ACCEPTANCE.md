# EIJA self-dogfood acceptance

Decision date: **2 October 2026**. Audience: UML-literate engineers who use coding agents. First connected project: **EIJA's own checkout**. This is a delivery and measurement contract; it is not a test-results report.

The intended result is a **complete, polished, non-linear IDE experience across the supported EIJA workflow**. An engineer can explore the project and domain, work in model editors, inspect agent changes, follow actual source, review consequences and evidence, revisit history and recover safely. These capabilities must work together in ordinary use. A wizard, attractive shell or single happy-path demonstration does not meet the owner's clarified goal. External projects follow EIJA acceptance; no external repository is selected here. Supported semantics and evidence remain bounded and explicit.

## Milestones and actual status

| Milestone | Deliverable | Status at preparation |
|---|---|---|
| Existing main foundations | Synthetic excursion workflow/kernel, typed transactions, generated views, computed runtime evidence and agent MCP surface | Present in documentation baseline `8712d6c`. Historical records describe earlier checks; no new integrated acceptance result is asserted here. |
| Source-connected foundations | Configured read-only EIJA connection; tracked Python/annotated UI coverage; domain tree; source/impact views; server-checked SVG model editor; agent read surfaces | **IN_DEVELOPMENT; NOT_DELIVERED_BY_THIS_DOCS_CHANGE**. Implementation and integration evidence are pending. Foundation checks alone do not close the IDE release goal. |
| Complete supported IDE and UX | Non-linear explorer/editors/source navigation, agent changes, review/evidence/history, keyboard control, clear feedback and recoverable edits | **PENDING_ACCEPTANCE**. Close only when integrated engineering and UX journeys below pass; do not infer this from foundation test totals. |
| Integrated engineering acceptance | Current-tree targeted tests, meaningful negative controls, ordinary browser-to-server checks and applicable local gates | **NOT_RUN** in this document. Stage-specific tests or earlier gate totals do not close it. |
| Live model pilot | A real selected agent uses the supported interface on the declared EIJA task, with versions, inputs, costs and outcomes retained | **NOT_RUN**. Mocked providers and synthetic MCP calls are engineering evidence only. |
| Human comprehension validation | UML-literate engineers make scored review decisions using a predeclared comparison and independent oracle | **NOT_RUN**. Acknowledgements, recordings and generated explanations do not measure comprehension. |
| External adoption and held-out generality | Owner-selected external repository followed by an evaluator-selected held-out case after the relevant adapter freezes | **NOT_RUN; later milestone**. EIJA is not held-out evidence for itself. |

These states change only through linked observations for the exact subject, not because the implementation work was assigned or a document was updated. Historical figures in the README and the v0.2 [acceptance matrix](../verification/ACCEPTANCE_MATRIX.csv) remain dated evidence for earlier scopes. The planned flow below is an acceptance specification, not a claim that all its controls or tool schemas are present on main.

## First-flow contract

This numbered sequence is a baseline test journey, not the product's navigation model. Engineers must also be able to begin with source, a concept, a model edit or an agent change, move among views and revisit prior work without restarting a wizard. Passing this sequence alone is insufficient; the integrated IDE contract and UX rubric are also required.

1. Launch EIJA locally from the documented checkout and connect its explicitly configured repository root. The connection preserves source files and reports scope; it is not an arbitrary filesystem browser.
2. Inspect the domain/language tree alongside real source references, extraction diagnostics and known-edge repository impact. The initial deterministic scope is supported **tracked Python and statically annotated UI**. Untracked, unsupported, excluded or unparseable content must not silently become verified structure.
3. Open a supported model change. The SVG editor renders the authoritative server model. Select a transition, request an affordance or edit check, and submit a typed model edit through the existing owner interaction. The browser does not create a second policy or workflow interpreter.
4. Compare the resulting model, diagrams and evidence. Accepted edits reload authoritative state; refused or stale edits keep the previous state and show actionable server reasons. Model editing does not rewrite the connected repository's source.
5. Let an agent inspect the same facts through read-only pack context, affordances, `edit_check` and `repository_impact`. These are planned additions to the agent surface. Their final tool names and argument schemas must be documented in the [agent contract](../agents/contract.md) when implemented; the current contract does not promise them.
6. Preserve the existing separation between an untrusted proposal, owner meaning selection and owner approval/apply. A read or dry run grants no authority. Agents do not operate owner-only endpoints or use a test principal as a real owner's approval.

Retain the existing excursion workflow as a regression fixture. Any additional model packs introduced during implementation must add variation checks; their presence or execution is not claimed for this documentation baseline, and packs are not external repository connections.

## Integrated IDE contract

The workbench is one coherent environment. Views share authoritative identity and state; the browser keeps only presentation/interaction state and server results. It must not introduce a parallel policy interpreter.

| Surface | Required working behavior |
|---|---|
| Explorer | Browse project/domain concepts and related artifacts, keep selection visible, reveal the active item and open the relevant editor/source without losing context. |
| Editors and diagrams | Revisit open model/edit views, inspect actual guards/roles, select and change supported elements, zoom/pan/fit meaningful diagrams, and redraw accepted changes from authoritative server state. No disconnected decorative canvas. |
| Source navigation | Follow a supported concept/change to the exact source location and return to the model/review context. Clearly distinguish extracted facts, explicit bindings and unconfirmed interpretation. Source remains read-only in this connection. |
| Agent changes | Inspect a selected proposal/change, its provenance and before/after meaning; move directly to affected concepts, source and review. Switching cases must not leak selections or evidence from another case. |
| Review and evidence | Inspect semantic change, known impact paths, refusals and per-kind evidence without hiding source-review or unknown/stale status. Panels agree on the current case/model revision. |
| History and recovery | Revisit prior changes and understand what changed. Cancel an unsubmitted edit; recover from refusals, stale versions and failures without losing the last valid state. Any undo/restore must use the existing typed/server contract and preserve the audit trail. |
| Keyboard and commands | Reach and operate core actions with visible focus, logical traversal and discoverable commands/shortcuts. Meaningful pointer interactions have keyboard alternatives. |
| Feedback and responsiveness | Selection, navigation and edits give clear feedback. Longer operations show progress/busy state and a usable recovery/cancel route where supported. No silent no-op, duplicate submission or frozen-looking screen. |

## IDE UX rubric

Record each row as PASS, FAIL, PARTIAL or NOT_RUN against the actual integrated application, with browser/viewport, journey and evidence. A consequential failure in these rows blocks the WOW/POC release even if unit tests are green. A formal participant study is separate; this is hands-on product acceptance.

| ID | Criterion | Required observation |
|---|---|---|
| UX01 | Coherent non-linear navigation | Complete model-first, source-first and agent-change-first journeys; move among explorer, editor, source, review/evidence and history, then return. Selection/context remain correct and reopening views does not restart the work. |
| UX02 | Readable, well-composed layout | Inspect declared supported desktop viewports, long labels, empty/error states and panel resizing/scrolling. No clipped controls/text, overlapping panels or hidden critical evidence; information hierarchy makes the next useful action clear. |
| UX03 | Useful diagrams | Check supported pack/model variations: readable node/edge labels, understandable direction and routing, selection, zoom/pan/fit and return to the selected element. Diagram collisions or layout changes must not obscure rules or misrepresent endpoints. |
| UX04 | Edits are understandable and recoverable | Perform, cancel and revisit a supported edit; trigger unsafe, stale and failed actions. Preserve the last valid model/source and useful focus/context; show the actual refusal/recovery path. Exercise any exposed undo/restore against its server semantics. |
| UX05 | Review, history and evidence stay in sync | Switch between changes/revisions, inspect before/after and impact, revisit history and stale evidence. Every panel identifies the correct subject; no old green state survives as current. |
| UX06 | Core keyboard use works | Complete selection, source navigation, a supported edit and refusal recovery without relying on pointer-only controls. Verify visible focus, logical order, discoverable commands and no keyboard trap. |
| UX07 | Feedback feels responsive and reliable | Record timings for representative navigation, index/load and edit/redraw operations. Immediate actions react visibly; longer actions show status. Test double activation, failure and retry; no silent or duplicate effects. Record and fix disruptive waits. |
| UX08 | Product quality survives unscripted use | Perform a hands-on review beyond the recording route; retain findings and their fixes. The reviewer can explain the current task, changed rule, evidence limit and next action from the UI. Capture video only after consequential usability defects are resolved. This is not a measured human-comprehension study. |

The demo and content derive from this working product. Editing a recording cannot close a UX failure. The [mission](MISSION.md) retains four flagship scenes with separate capability prerequisites; their roadmap status must not be confused with current working functionality.

## Required observations

| ID | Acceptance observation | Evidence and failure control |
|---|---|---|
| SD01 | A fresh documented setup reaches the workbench and the configured EIJA connection | Record platform, Python/dependency versions, commands, subject revision/content manifest, errors and elapsed time. Do not claim untested platforms. |
| SD02 | Repository connection is read-only and bounded | Compare source manifests before/after; confirm root/configuration boundaries and rejected unsupported input. Include/exclude counts and reasons must reconcile with the declared inventory. |
| SD03 | Structural extraction is reproducible | Same snapshot, configuration and adapter produce the same canonical graph, diagnostics and impact. Compare independently annotated sample symbols/UI bindings; plant an incorrect reference and ensure the oracle detects it. |
| SD04 | Source and domain facts remain distinguishable | Every displayed link names its source and method. Missing/dynamic/unresolved relationships stay unknown. A declared binding does not become proof of behavior merely because it exists. |
| SD05 | The SVG/domain tree matches the server model | Compare stable element identities, transition endpoints, roles and labels against server data. A deliberately false rendered endpoint must fail the oracle. |
| SD06 | Legal and illegal edits exercise the real kernel | Select safe and unsafe affordances independently of the UI. A safe edit changes exactly the declared transaction/version; an illegal edit preserves prior state and exposes the exact reason. Repeat for the supported packs. |
| SD07 | Stale interaction cannot overwrite current work | Change the version after obtaining an affordance, then submit the stale edit. Expect a refusal/reload path, not silent overwrite. A layout-only change must not become a semantic edit. |
| SD08 | Agent inspection cannot mutate or decide | Snapshot cases, baselines and source around MCP reads/dry runs. Unsupported owner operations are absent or refused. Exercise pack context, affordances, edit checks and repository impact using the documented schemas. |
| SD09 | Impact means closure of the known graph | Retain a witness path and compare against an independently enumerated bounded fixture. Missing extraction remains visible; graph closure alone does not establish all real-world consequences. |
| SD10 | Evidence is current only for its declared subject | Substitute a model, source/configuration digest or tool identity and verify rejection/staleness. Preserve original observations. Unsupported laws, missing tools and incomplete checks cannot become PASS. |
| SD11 | An ordinary user can use the coherent IDE | Exercise actual browser-to-server transport and the integrated navigation/edit/review/history/recovery journeys in UX01–UX08. Component/bridged tests and a single filmed happy path do not count as this end-to-end acceptance. |
| SD12 | Documentation and release boundary are honest | Current links resolve; generated documentation is checked where applicable. `SOURCE_REVIEW_REQUIRED` remains visible for changed implementation, and its expected release check failure is recorded separately from functional defects. |

For each observation record PASS, FAIL, PARTIAL or NOT_RUN, the exact command/journey, raw artifact location, scope and unresolved limitations. A claimed pass needs a meaningful negative control where specified. Code review may support a finding but cannot replace execution for an execution criterion.

## What verification does and does not establish

Software verification checks EIJA's own contracts. Formal analysis checks encoded laws under stated assumptions and bounds. Model fidelity checks whether the model and source/runtime bindings describe the chosen behavior. Product validation checks whether engineers actually understand and maintain the result better. These are different claims.

Record law/property identity, model/pack digest, source revision or content manifest, checker and adapter versions, environment, bounds, assumptions, raw results and controls. Hashes establish identity; they do not establish truth. Checks from the same author can share a mistake, so preserve independent fixtures and report their provenance.

The maintainer's source-review fixture is a separate release boundary. Run the applicable release verification and report the expected mismatch; do not stamp it, bypass it, edit receipts or change oracles to get a green gate. A disposable synthetic harness may test owner-flow mechanics only when clearly labeled; it does not create a real owner decision.

## Measurable V&V and product validation

First complete the deterministic self-dogfood fixtures. Record valid changes accepted, declared unsafe fixtures detected, false refusals, stale-evidence rejections, incorrect/missing links, extraction coverage, unsupported cases, repeatability, setup time and total engineering effort. Keep unknown behavior in the coverage denominator. Passing positive examples alone is insufficient.

Then run the separately authorized live model pilot and an engineer feasibility study under the [dated V&V protocol](../research/2026-10-02-vv-protocol.md). Compare the same tasks, coding model, source context and ordinary tests with and without EIJA. Use an independently frozen answer key and retain all failed or abandoned runs. The human primary endpoint is correct review decisions within a fixed time, with critical misses and false rejection of safe changes reported separately. Also measure explanation accuracy, confidence calibration, setup/review/rework time and follow-up maintenance.

Diagram usefulness, test counts, gate counts, self-reported confidence and model-generated evaluations cannot substitute for those observations. The [alternatives review](../research/2026-10-02-current-alternatives.md) identifies strong specification, modeling and guided-review baselines; it does not establish that EIJA is novel or better.

## Completion and later work

Close the source-connected foundation milestone when its actual engineering checks pass, but do not call the IDE/WOW goal complete on that basis. Close the supported IDE release only when both SD01–SD12 and UX01–UX08 have the required integrated observations, consequential usability defects are resolved, scoped limitations are visible and the run record is reviewable. Stop closure for source mutation/data loss, false evidence attribution, a missed declared critical fixture, a broken supported path, unrecoverable edits or an incoherent/unusable core interface. The expected maintainer source-review mismatch stays an explicit limitation; it is not hidden as success.

A complete supported IDE experience does not require pretending to offer universal code generation, general two-way source transformation, every proof backend or a statistical superiority result. Those claims remain explicit and separately evidenced. Finish the EIJA target before choosing an external application. The four flagship scenes remain the demonstration roadmap; cross-worktree semantic conflict/combined-result checks and held-out adoption receive their own implementation and execution records. Any unimplemented scene remains planned, never simulated as working.

## Run record

**Current integrated run: PENDING.** No completed run is claimed by this document. The integrator must add a dated run-report link here after retaining the observations; until then README links resolve to this explicit pending state.

The run report must identify:

- Date, platform, source commit plus dirty-content manifest, pack/model/adapter versions and tested connection scope.
- Commands and results for SD01–SD12 and UX01–UX08, artifact references, negative-control outcomes and resolved/unresolved usability findings.
- Freshness and coverage limitations; tests skipped or not run, with reasons.
- The outcome of applicable local gates and release verification, including any expected source-review mismatch.
- Separate states for source-connected foundations, full supported IDE/UX acceptance, demo/content readiness, live model validation, human study and external/held-out generality.

Do not replace this pending state with inherited test totals or a claim based solely on successful patch application.
