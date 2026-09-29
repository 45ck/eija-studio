# UI to model linking: what exists, what EIJA should build

Lane: weave. Dossier: ui-model-linking. Access date for every URL: 2026-09-29. Status: research input for ADR block 0089-0112, not a decision.

## Decisions first

| # | Decision | Confidence | Evidence |
|---|---|---|---|
| 1 | Give every UI node one stable key (an attribute, not a position) and keep the meaning of that key in a **sidecar UI model** (canonical JSON, content-addressed) that points at domain concepts, transitions, requirements, API operations and tokens. The DOM carries only the key. | Medium: a design synthesis. Each part has precedent (JSON Forms `scope`, Storybook static index, Playwright `testIdAttribute`); the combination is untested. | sections 2.1, 2.5, 2.8 |
| 2 | Detect mismatch with **set operations over sorted IDs** from three sources: the sidecar, the domain model and a rendered-DOM capture. Every diagnostic is an anti-join or a set difference, so output is byte-stable. | High for determinism of the comparison; the capture step is only as deterministic as the pinned browser | section 4 |
| 3 | The strongest cheap check is **enabled-set equality**: for each (workflow state, actor) pair, the UI controls that are enabled must equal the transitions the kernel allows. State and actor sets are small and enumerable here. | Medium. Bounded by the enumeration; says nothing about untested states | sections 2.3, 4 |
| 4 | **Generate** what can be generated (action buttons, form fields, rule tables) from the model; **link and lint** what cannot. Naked Objects, Django admin and JSON Forms show the projection idea; none of them fits the vanilla-JS Studio as a dependency. | High that projection removes a drift class; low that any listed tool should be adopted | sections 2.2, 5 |
| 5 | Locate by role and accessible name first, use the key attribute for identity and traceability. Two channels; a mismatch between them and the model is a diagnostic. | High (Testing Library and Playwright both rank role above test id) | sections 2.4, 2.8 |
| 6 | Use DTCG 2025.10 tokens with a reverse-domain `$extensions` key for the token-to-concept link. Do not adopt a token toolchain yet. | Medium | section 2.5 |
| 7 | Do **not** adopt IFML, UsiXML, CAMELEON tooling or W3C MBUI as engines. They are useful vocabulary and a reference for what a UI model must contain. | High | section 2.1 |
| 8 | A passing UI link check proves that links are consistent and complete over the enumerated states. It does not prove the UI is correct, usable or understood. Label it that way. | High | AGENTS.md; section 7 |

## 1. Scope and method

- Question: how can each UI element carry a verifiable link to the domain concept and requirement it realises, and how is a mismatch found deterministically?
- **Search limitation.** The session's web-search budget was exhausted (200 of 200) before this dossier started, so I issued no successful search. Every source below was opened by direct URL, chosen from prior knowledge. Coverage is therefore limited to tools and specs I already knew to look for. Nothing is cited from a search snippet.
- **Extraction limitation.** Pages were read through a summarising fetch tool. Statements marked "(fetch summary)" are as returned and were not re-checked against the primary text. Repository licence, archive flag, last push and latest release come from `gh api repos/<owner>/<repo>` and `.../releases/latest` on 2026-09-29.
- **Not opened (treat as UNVERIFIED):** Harel 1987 (ScienceDirect HTTP 403; Weizmann mirror connection reset); Pawson's 2004 thesis (TLS error; the pattern is described from a Wikipedia summary, a tertiary source); Tretmans on `ioco` (not retrieved); UsiXML (host certificate mismatch, so no current status); ACM DL for Foster et al. (403; I read the University of Pennsylvania preprint instead).
- Local reads (this worktree, no execution of web code): `src/eija_studio/resources/web/{index.html,app.js,app.css}`, `contracts/openapi.json`, `examples/*.json`, `docs/architecture/ARCHITECTURE.md`, `docs/adr/README.md`, `docs/oss/REGISTER.md`, the okf lane `okf/index.md`, the hci lane `docs/hci/REPORT.md`, the agents lane `docs/agents/contract.md`, and the owner's ProofMap Lite `README.md` and `docs/gap-audit.md` (read with the owner's `gh` login).
- Untrusted-data rule applied: no fetched page was followed as instructions; no fetched code was run.

### What the Studio UI looks like today (MEASUREMENT, local static reads)

| Fact | Value | Why it matters |
|---|---|---|
| UI size | `index.html` 17 lines, `app.js` 32 lines, vanilla JS, no framework, no component model | Heavy MBUI/IFML tooling is out of proportion; the link contract must work on plain DOM |
| Interactive elements in static HTML | 28 (`button`, `input`, `select`, `textarea`, `a`); 27 carry an `id` or `data-tab` | Identity already exists as `id`; one is unkeyed |
| Controls created by JS | 3 `el("button", ...)` sites (case list, meaning options, runtime actions); none sets an `id` | Dynamically created controls are invisible to a static HTML scan |
| Action buttons | `for(const action of ["Submit","Recommend","Approve","Reject","Revise"])`, a literal list in `app.js`. `examples/excursion-baseline.json` has 4 of those actions (no Recommend); `examples/excursion-candidate.json` has all 5 | The UI duplicates the workflow's action vocabulary by hand. This is exactly the drift class the thesis names |
| Enabled state | Action buttons use `b.disabled=!instance\|\|closed`, not the workflow guard | UI enabledness is not derived from the kernel's allowed transitions |
| API calls | `api("cases")`, `api("status")`, ..., and one dynamic path, `` api(`cases/${id}/${action}`) `` | A static scan cannot resolve the dynamic one; it needs an explicit declaration |
| Design tokens | `:root` defines 10 CSS custom properties (9 colours and `--radius`); `var(--...)` is used 54 times in `app.css`; 10 distinct hex colour literals appear outside `:root` | Partial tokenisation; the link from token to concept does not exist |
| `data-testid` | 0 occurrences | There is no test-id contract yet |
| OpenAPI | `contracts/openapi.json` is OpenAPI 3.1.0 with 18 paths; `operationId`s are FastAPI-generated, for example `new_case_api_cases_post` | They are derived from path and function names, so a rename changes them. Stable explicit ids would be a kernel change and needs its own ADR |

## 2. Tools and schools

### 2.1 Model-based UI development: CAMELEON, W3C MBUI, IFML, UsiXML

- **CAMELEON.** Calvary et al., "A Unifying Reference Framework for multi-target user interfaces", *Interacting with Computers* 15(3), 2003, pp. 289-308 ([DOI](https://doi.org/10.1016/S0953-5438(03)00010-9), read via [OUP](https://academic.oup.com/iwc/article-lookup/doi/10.1016/S0953-5438(03)00010-9)). Four levels: task and concepts, abstract UI, concrete UI, final UI, joined by reification and abstraction. The W3C Note [Introduction to Model-Based User Interfaces](https://www.w3.org/TR/mbui-intro/) (7 Jan 2014) restates them as Task and Domain models, AUI, CUI, FUI.
- **W3C MBUI.** The working group is [closed](https://www.w3.org/2011/mbui/); [Task Models](https://www.w3.org/TR/task-models/) (ConcurTaskTrees-based, tasks manipulate domain objects with pre- and postconditions) and [Abstract UI Models](https://www.w3.org/TR/abstract-ui/) are Working Group Notes of 8 April 2014. The AUI Note says the group "is no longer progressing it along the W3C Recommendation Track".
- **IFML.** OMG [IFML 1.0](https://www.omg.org/spec/IFML/1.0/About-IFML), adopted February 2015 under a Non-Assert IPR mode; it models view containers, view components, events, control flow and binding to data objects. The [ifml.org](https://www.ifml.org/) site shows no update after 2015 (fetch summary). Open-source tooling on GitHub: `ifml/ifml-editor` (MIT, last push 2015-08-26) and `B3rn475/IFMLEdit.org` (MIT, last push 2025-06-29, 25 stars). I found no evidence of a maintained, widely used IFML toolchain.
- **UsiXML.** Status UNVERIFIED (site inaccessible). Do not build on it.
- **What it gives EIJA.** A checklist of what a UI model must contain: task or intent, domain binding, containers, events, flows. Our sidecar node kinds map onto it: `view`, `region`, `control`, `field`, `status`. CAMELEON's *reification* (abstract to concrete) and *abstraction* (concrete to abstract) name the two directions of our link check: model-to-UI coverage and UI-to-model provenance.
- **Cost of adopting more.** Standards without a live tool ecosystem, XMI interchange, and a metamodel heavier than a 49-line UI.
- **Verdict:** inspiration only. Do not depend on it. If IFML export is ever wanted it is an export target from the sidecar, not a source.

### 2.2 UI as a projection of the domain model: Naked Objects, Causeway, Django admin, schema-driven forms

- **Naked Objects.** Pattern from Pawson's 2004 Trinity College Dublin thesis (secondary source: [Wikipedia](https://en.wikipedia.org/wiki/Naked_objects); the thesis PDF was not readable). Three principles as summarised: business logic encapsulated on domain objects; the UI a direct representation of them; the UI created automatically from the object definitions.
- **Apache Causeway** (formerly Apache Isis): [site](https://causeway.apache.org/) says it "dynamically generates a UI and API" for Spring Boot apps; Apache-2.0; repo `apache/causeway`, last push 2026-09-28, not archived. It is JVM/Spring/Wicket. As a dependency it would add a second runtime to a Python kernel: reject as dependency, keep as the reference for the *pattern*.
- **Django admin.** [Docs](https://docs.djangoproject.com/en/stable/ref/contrib/admin/): "It reads metadata from your models to provide a quick, model-centric interface". Django is BSD-3-Clause and active. Same pattern, Python, but tied to Django ORM models.
- **JSON Forms** (MIT, v3.8.0, 2026-06-16): [docs](https://jsonforms.io/docs/) separate a data schema from a UI schema; a control binds to a property by `scope`, a JSON Pointer such as `#/properties/name`. This is the cleanest *checkable link* in the survey: a dangling pointer is a deterministic error. **react-jsonschema-form** (Apache-2.0, v6.10.1, 2026-09-16; [docs](https://rjsf-team.github.io/react-jsonschema-form/docs/)) builds forms from JSON Schema with a `uiSchema` for presentation. Both are React-centred; the Studio is not React.
- **What it gives EIJA.** The idea, not the code: (a) the action list and rule table should be *generated* from the `Workflow` (the current hard-coded five-action list is the counter-example); (b) where a UI field edits a domain contract, link it by JSON Pointer into the existing Pydantic-generated `contracts/*.schema.json`, and lint that the pointer resolves.
- **Cost.** Generation constrains layout; a generic UI is rarely the best UI. Keep generation for tables, action lists and forms, and hand-author the rest.
- **Verdicts:** Causeway reject as dependency, inspiration; Django admin inspiration; JSON Forms and RJSF inspiration (the `scope` pointer pattern is adopted as a mechanism, the libraries are not).

### 2.3 Statecharts as the shared behavioural model: Harel, SCXML, XState, Sismic, model-based UI testing

- **Harel statecharts.** Original paper (Sci. Comput. Programming, 1987) not opened; UNVERIFIED beyond the citation. [SCXML](https://www.w3.org/TR/scxml/) is a W3C Recommendation (1 Sept 2015) with compound, parallel and history states, a data model and `invoke`; it states that it adopts Harel's semantics (fetch summary).
- **XState** (MIT, `xstate@5.33.2`, 2026-09-15, active). [Docs](https://stately.ai/docs/xstate): statecharts and the actor model; the docs do not mention SCXML compatibility. [Graph utilities](https://stately.ai/docs/xstate-graph) live in `xstate/graph` (`getShortestPaths`, `getSimplePaths`, `getPathsFromEvents`, `createTestModel`); the separate `@xstate/graph` package is deprecated (fetch summary).
- **Sismic** (Python, LGPL-3.0, 1.6.12, 2026-09-28): YAML statecharts, interpreter, design-by-contract on states and transitions, runtime monitoring, BDD ([README](https://github.com/AlexandreDecan/sismic)). Closest in spirit to EIJA's kernel, but LGPL and a second statechart semantics beside `Workflow`.
- **GraphWalker** (MIT): directed-graph model-based testing; path generators and stop conditions; the Java project's last release is 4.3.3 (2024-09-26), and a Rust rewrite `graphwalker-rs` (MIT, pushed 2026-09-22) is the current focus per [graphwalker.github.io](http://graphwalker.github.io/) (fetch summary). `altwalker/altwalker` is GPL-3.0 (no dependency).
- **What it gives EIJA.** EIJA already has a typed `Workflow` (states, transitions, roles, guards). It is the statechart. The UI must not hold a second copy of it. Two concrete uses: (1) the UI asks the API for the set of currently available actions (server-computed from the kernel), so enabledness cannot drift; (2) a bounded model-based UI test enumerates (state, actor) pairs from `Workflow`, drives the UI to each with shortest paths (plain BFS, about 20 lines) and asserts enabled-set equality. No XState or GraphWalker needed for a workflow of this size.
- **Cost.** One browser run per enumerated state and a stable way to reach states. Chrome runs are the slow, heavy step on this PC; run them serially.
- **Verdicts:** SCXML export target (interchange, if another lane wants it); XState optional process or export target (`Workflow` to machine JSON), not a dependency of the kernel; Sismic optional process at most (LGPL); GraphWalker optional process, not needed at current size; AltWalker reject.

### 2.4 The accessibility tree as a semantic bridge

- [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/) (Recommendation, 6 June 2023) defines the accessibility tree and a role taxonomy with abstract roles that authors must not use. [Accname 1.2](https://www.w3.org/TR/accname-1.2/) specifies the accessible-name algorithm (labelledby, label, native label, content, title); fetched status: Working Draft dated 23 September 2026 (fetch summary, unverified in detail).
- Playwright [aria snapshots](https://playwright.dev/docs/aria-snapshots) return a YAML of role, accessible name and states (`page.ariaSnapshot()`, `toMatchAriaSnapshot`); matching is case-sensitive, whitespace-collapsing and order-sensitive; the docs state no determinism caveat, which is an absence of a claim, not a guarantee. Playwright is Apache-2.0, 1.63.0 (2026-09-04); the hci lane already uses it.
- **What it gives EIJA.** The role and accessible name are what a human and an assistive tool perceive; they are also machine-readable. A rule "the accessible name of the control realising concept C must be C's glossary label or a registered synonym" is a **ubiquitous-language lint on the UI as perceived**, and it is computed by the browser, not by our parser. That closes the gap that a static scan of `app.js` string literals cannot: it sees rendered text.
- **Cost and limit.** Needs a browser. Names and roles may differ between browser engines and versions (UNVERIFIED; not tested), so the evidence must record the pinned browser version and platform, and a missing browser reports `NOT_RUN`. Not every domain concept has a visible label.
- **Verdict:** Playwright dependency in the `graph` extra (or reuse the hci lane's pin; check for a version conflict before adding); ARIA and Accname spec-level references; axe-core stays the hci lane's (MPL-2.0, file-level copyleft: an unmodified dependency in an Apache-2.0 project is allowed per the [MPL FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)).

### 2.5 Design tokens to components to domain concepts

- The [Design Tokens Format Module 2025.10](https://www.designtokens.org/tr/2025.10/format/) is stable ("considered stable"), published 28 Oct 2025 as a Final Community Group Report under the W3C Community Final Specification Agreement (not a W3C Standard). Tokens have `$value`, `$type`, optional `$description`, `$deprecated`, and `$extensions` namespaced in reverse-domain form; aliases use `{group.token}` or `$ref`; both require circular-reference detection (fetch summary). The `drafts` URL is a preview draft and must not be implemented.
- **Style Dictionary** (Apache-2.0, v5.5.5, 2026-09-20): first-class DTCG support since v4, but full 2025.10 support is "a work in progress in v5" per its [DTCG page](https://styledictionary.com/info/dtcg/).
- **What it gives EIJA.** A token file is a canonical JSON graph with alias edges, so it can be a set of nodes in the link graph. A token carrying `$extensions: {"dev.eija.realises": ["term:review-packet"]}` links a visual property to a domain concept, for example a "blocked" status colour to the concept Blocker. Lint: every `var(--x)` in CSS resolves to a token; every token is used or marked deprecated; hard-coded colour literals are flagged (10 today, section 1).
- **Cost.** Only worthwhile if tokens carry *semantic* names (status, severity), not raw palette values. Today's 9 colours are palette-named (`--green`, `--pale`).
- **Verdict:** adopt the DTCG file format for the sidecar's token layer; Style Dictionary is an optional process (Node), deferred.

### 2.6 Storybook CSF and component metadata

- [CSF](https://storybook.js.org/docs/api/csf) is "an open standard based on ES6 modules": default export meta (`component`, `title`, `parameters`, `tags`), named exports as stories, `args`, `play` functions; CSF 3 is current with a "CSF Next (Preview)". [Indexers](https://storybook.js.org/docs/api/main-config/main-config-indexers) build the story index **without executing stories**, with `id`, `title`, `tags`, `importPath`. [Tags](https://storybook.js.org/docs/writing-stories/tags) can carry custom values such as personas or ownership. Storybook is MIT (`v10.6.0`, 2026-09-02). Its [AI docs](https://storybook.js.org/docs/ai) describe an MCP server and a components manifest, both "in preview". `storybookjs/eslint-plugin-storybook` is archived (pushed 2025-11-07).
- [Custom Elements Manifest](https://github.com/webcomponents/custom-elements-manifest) (BSD-3-Clause, v2.1.0 2024-05-06, JSON Schema) is a schema for describing custom elements.
- **What it gives EIJA.** The Studio has no components, so Storybook adds a build chain for no link value today. The pattern is useful if the UI is ever componentised: a story's `tags` (for example `concept:review-packet`, `req:ACC-07`) plus static indexing would give component-to-concept links that a Python reader can parse from `index.json` without a browser. Record as a future adapter, not now.
- **Verdict:** optional process, deferred; CEM inspiration for a component-metadata schema.

### 2.7 Contract-first APIs: OpenAPI, JSON Schema, AsyncAPI

- [OpenAPI 3.2.1](https://spec.openapis.org/oas/latest.html) (10 Sept 2026, Apache-2.0): `operationId` "MUST be unique among all operations"; the Schema Object follows JSON Schema 2020-12; `x-` extensions are allowed. [JSON Schema](https://json-schema.org/specification) 2020-12 is still IETF drafts, not RFCs. [AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/latest) (Apache-2.0) describes channels, operations and messages, and extends JSON Schema draft-07.
- Tools: **Schemathesis** (MIT, v4.28.0) generates API tests from OpenAPI; **oasdiff** (Apache-2.0, v1.32.1, Go) reports breaking changes between two specs; **Spectral** (Apache-2.0, v6.16.3, Node) lints OpenAPI/AsyncAPI with custom rulesets ([Schemathesis](https://github.com/schemathesis/schemathesis), [oasdiff](https://github.com/oasdiff/oasdiff), [Spectral](https://github.com/stoplightio/spectral) READMEs). The FastAPI-generated `contracts/openapi.json` is the existing contract (OpenAPI 3.1.0).
- **What it gives EIJA.** `operationId` is the natural key for UI-to-API links: `ui:evidence/verify` `calls` `op:verify_...`. Two checks: every declared `calls` resolves in `openapi.json`; a changed operation (oasdiff or a plain sorted diff of our own canonical JSON) yields the set of UI nodes that call it through the existing closure. Static scanning of `app.js` finds literal paths only; the dynamic `cases/${id}/${action}` must be declared in the sidecar.
- **Cost.** Explicit `operation_id=` on each route is a `src/` change (own ADR). AsyncAPI has no target: the outbox is not a broker interface (ARCHITECTURE.md).
- **Verdicts:** OpenAPI and JSON Schema are already dependencies of the kernel; oasdiff and Spectral optional processes; Schemathesis optional process (it tests the API, not the UI link, so it is adjacent); AsyncAPI reject for now; Pact (MIT; consumer-driven contracts) reject for a single-consumer monolith.

### 2.8 Test-id traceability and page objects

- Testing Library [ranks queries](https://testing-library.com/docs/queries/about/): role, label, placeholder, text, display value; then alt text and title; test ids last, only "for cases where you can't match by role or text or it doesn't make sense". Playwright [locators](https://playwright.dev/docs/locators) recommend role first, call `getByTestId` "the most resilient way" but not user-facing, and make `testIdAttribute` configurable; locators are strict (more than one match throws).
- HTML `data-*` [attributes](https://html.spec.whatwg.org/multipage/dom.html#embedding-custom-non-visible-data-with-the-data-*-attributes) are for private use by the page's own scripts and styles, and are not for cross-site communication. That fits a same-origin key. WHATWG spec licence: CC BY 4.0 (fetch summary).
- Fowler's [Page Object](https://martinfowler.com/bliki/PageObject.html) (2013) wraps a page with an application-specific API and favours assertion-free page objects.
- **What it gives EIJA.** Make the key attribute `data-eija-key` and set Playwright `testIdAttribute` to it. Then tests, the hci lane's journey and the link checker all use one identity. A *generated* page-object registry (`keys.py`: one constant per UI node, emitted from the sidecar) removes hand-typed test ids and makes "test T touches UI node N" a scannable edge. Tests should still prefer `get_by_role`; the key is for identity and traceability, and the checker asserts the two agree.
- **Cost.** Keys on JS-created controls need code changes in `src/` (own PR).
- **Verdict:** adopt the two-channel convention; page-object pattern adopt as generated code.

### 2.9 Lessons from ProofMap Lite

Owner's repo, README and `docs/gap-audit.md`. Its loop is draw.io map to semantic graph to Change Bundle to prompt to OpenFastTrace to proof report, with UWE content and navigation-model views, API views via OpenAPI, and inferred model views (GAP-030 to GAP-032). Relevant lessons, all from its gap register:

| Lesson | ProofMap evidence | EIJA consequence |
|---|---|---|
| Presence and freshness gates prove files exist, not that they are right | GAP-002, GAP-023: a manifest with one file passed until the full expected view set was required | Check *completeness against the domain model*, not file presence |
| Inferred model views contradicted project boundaries | GAP-024: an ERD implied runtime tables the project rejected | Mark inferred links `inferred` and never let them satisfy a gate; only declared links count |
| A typed trace contract per view was needed | GAP-030: allowed labels, edges, required graph nodes per view | The sidecar node kinds and edge kinds need a closed schema |
| Timestamps caused churn | GAP-003 | No wall-clock in artefacts (determinism doctrine) |
| Drift warnings were closed with prose | GAP-029 | A diagnostic is cleared by a link change or a recorded waiver with owner and expiry, never by prose |
| Dashboard preferred the bootstrap change over the latest | GAP-035 | Select by content hash and explicit id, not by name order or mtime |

## 3. Options table

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| CAMELEON framework | Paper (publisher terms) | Published 2003; W3C Note 2014 | inspiration | Level vocabulary; no tooling | [OUP](https://academic.oup.com/iwc/article-lookup/doi/10.1016/S0953-5438(03)00010-9), [W3C](https://www.w3.org/TR/mbui-intro/) |
| W3C MBUI Task Models and AUI | W3C document licence | Notes; WG closed | inspiration | Task-to-domain binding and AUI concepts; abandoned track | [Task](https://www.w3.org/TR/task-models/), [AUI](https://www.w3.org/TR/abstract-ui/), [WG](https://www.w3.org/2011/mbui/) |
| IFML 1.0 | OMG spec, Non-Assert IPR | Adopted 2015; site stale | inspiration (export target only if asked) | No maintained toolchain found | [OMG](https://www.omg.org/spec/IFML/1.0/About-IFML), [ifml.org](https://www.ifml.org/) |
| IFMLEdit.org | MIT | Last push 2025-06-29, 25 stars | reject | Small, single-maintainer web editor; we generate, not edit | [repo](https://github.com/B3rn475/IFMLEdit.org) |
| UsiXML | UNVERIFIED | UNVERIFIED | reject (until verified) | Site inaccessible | none |
| Apache Causeway | Apache-2.0 | Active, last push 2026-09-28 | inspiration; reject as dependency | JVM and Spring; pattern only | [site](https://causeway.apache.org/) |
| Django admin | BSD-3-Clause | Active (docs show 6.1) | inspiration | Model-metadata-driven UI; Django-bound | [docs](https://docs.djangoproject.com/en/stable/ref/contrib/admin/) |
| JSON Forms | MIT | v3.8.0, 2026-06-16 | inspiration (mechanism: `scope` pointer) | Checkable pointer link; renderers are React/Angular/Vue | [docs](https://jsonforms.io/docs/) |
| react-jsonschema-form | Apache-2.0 | v6.10.1, 2026-09-16 | inspiration | React only | [docs](https://rjsf-team.github.io/react-jsonschema-form/docs/) |
| SCXML | W3C Recommendation, W3C copyright | 2015, stable | export target | Interchange for the workflow statechart | [W3C](https://www.w3.org/TR/scxml/) |
| XState | MIT | 5.33.2, 2026-09-15 | export target / optional process | Second runtime for a JS-only benefit; graph utilities are in `xstate/graph` | [docs](https://stately.ai/docs/xstate-graph) |
| Sismic | LGPL-3.0 | 1.6.12, 2026-09-28 | optional process (inspiration) | Contracts on statecharts; LGPL and a second semantics | [repo](https://github.com/AlexandreDecan/sismic) |
| GraphWalker | MIT | Java 4.3.3 (2024-09-26); Rust rewrite pushed 2026-09-22 | optional process | Path generation we can write in 20 lines at current size | [site](http://graphwalker.github.io/), [repo](https://github.com/GraphWalker/graphwalker-project) |
| AltWalker | GPL-3.0 | Pushed 2025-10-27 | reject | GPL; cannot be a dependency of an Apache-2.0 package | [repo](https://github.com/altwalker/altwalker) |
| Playwright (Python) | Apache-2.0 | 1.63.0, 2026-09-04 | dependency (optional extra) | Aria snapshots, strict locators, `testIdAttribute`; already used by hci | [aria](https://playwright.dev/docs/aria-snapshots), [locators](https://playwright.dev/docs/locators) |
| axe-core | MPL-2.0 | 4.13.0, 2026-08-05 | dependency (hci lane owns it) | File-level copyleft; unmodified use is allowed | [FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/) |
| WAI-ARIA 1.2, Accname 1.2 | W3C document licence | Rec 2023-06-06; Accname WD (fetch summary) | dependency (spec reference) | Role taxonomy and name algorithm | [ARIA](https://www.w3.org/TR/wai-aria-1.2/), [Accname](https://www.w3.org/TR/accname-1.2/) |
| DTCG Format Module 2025.10 | W3C Community Final Specification Agreement | Stable, 2025-10-28 | dependency (file format) | Token graph with `$extensions` for links | [spec](https://www.designtokens.org/tr/2025.10/format/) |
| Style Dictionary | Apache-2.0 | v5.5.5, 2026-09-20; 2025.10 support incomplete | optional process (deferred) | Node build tool; not needed to lint tokens | [DTCG page](https://styledictionary.com/info/dtcg/) |
| Storybook | MIT | v10.6.0, 2026-09-02; AI features in preview | optional process (deferred) | No components in the Studio today; static index and tags are the useful part | [CSF](https://storybook.js.org/docs/api/csf), [indexers](https://storybook.js.org/docs/api/main-config/main-config-indexers) |
| Custom Elements Manifest | BSD-3-Clause | v2.1.0, 2024-05-06 | inspiration | JSON-Schema-described component metadata | [repo](https://github.com/webcomponents/custom-elements-manifest) |
| OpenAPI 3.2.1 / JSON Schema 2020-12 | Apache-2.0 / BSD-style spec licence | Current | dependency (already used) | Contract for UI-to-API links | [OAS](https://spec.openapis.org/oas/latest.html), [JSON Schema](https://json-schema.org/specification) |
| AsyncAPI 3.1.0 | Apache-2.0 | Current | reject (for now) | No broker or event interface | [spec](https://www.asyncapi.com/docs/reference/specification/latest) |
| oasdiff / Spectral / Schemathesis | Apache-2.0 / Apache-2.0 / MIT | 1.32.1 / 6.16.3 / 4.28.0 | optional process | Contract diff, custom lint, API tests; each is a separate CLI | [oasdiff](https://github.com/oasdiff/oasdiff), [Spectral](https://github.com/stoplightio/spectral), [Schemathesis](https://github.com/schemathesis/schemathesis) |
| Pact JS | MIT (LICENSE file text) | v17.1.4, 2026-09-07 | reject | Consumer-driven contracts need several consumers | [repo](https://github.com/pact-foundation/pact-js) |
| Testing Library | MIT | dom-testing-library 10.4.2 | inspiration | Query-priority principle; JS-only | [docs](https://testing-library.com/docs/queries/about/) |
| Page Object | Pattern | 2013 | adopt as generated registry | Removes hand-typed ids | [Fowler](https://martinfowler.com/bliki/PageObject.html) |
| RDFa 1.1 | W3C, Primer is a Note | 2015 | reject | Inline semantics in attributes is heavier than one key plus a sidecar | [Primer](https://www.w3.org/TR/rdfa-primer/) |
| tree-sitter (`py-tree-sitter`) | MIT | Active (pushed 2026-08-30) | optional process | Robust JS call-site extraction if regex proves brittle (not tested here) | [repo](https://github.com/tree-sitter/py-tree-sitter) |

## 4. How a mismatch is detected

The link graph has UI nodes (`ui:<view>/<control>`), domain nodes (concept, transition, invariant), requirement nodes, API operations, tokens and tests. A UI node's identity is its key. The sidecar file is JSON in EIJA's canonical form (RFC 8785 JCS is the reference for the rules: sorted properties by UTF-16 code unit, ECMAScript number serialisation; it is Informational, not a standard, per the [RFC](https://www.rfc-editor.org/rfc/rfc8785)). Diagnostics, each a pure function of three inputs (sidecar S, domain model D, rendered capture R) and sorted by (code, node id):

| Code | Detects | Operation | Needs a browser? |
|---|---|---|---|
| UIL-001 dangling link | UI node points at a concept, transition, requirement, operation or token that does not exist | anti-join S.links against D and contracts | no |
| UIL-002 uncovered domain action | A transition a role can invoke has no UI trigger node | anti-join D.transitions against S.triggers | no |
| UIL-003 orphan or unkeyed element | Element with a key not in S, or an interactive element with no key | R.keys minus S.keys; R.interactive minus R.keys | yes |
| UIL-004 label drift | Accessible name differs from the linked term's label or its registered synonyms | compare R.aria name with the glossary | yes |
| UIL-005 enabledness mismatch | For a (state, actor) pair, enabled UI triggers differ from kernel-allowed transitions | symmetric difference of two sorted sets | yes |
| UIL-006 API mismatch | `calls` does not resolve to an `operationId`; a called operation changed | join S.calls against `openapi.json` | no |
| UIL-007 token drift | `var(--x)` with no token; token unused; raw colour literal | parse CSS, join against the DTCG file | no |
| UIL-008 no evidence link | UI node with no test referencing its key | anti-join S.keys against test key references | no |

- **Determinism.** Inputs are canonical JSON; comparison is set algebra over sorted strings; the output is canonical JSON ordered by (code, id) and contains no timestamp. For capture, sort by key rather than DOM order, and record the browser build and platform as evidence metadata. Same inputs and same browser build give the same bytes. That last clause is a claim to test (repeat runs, compare hashes), not a fact I measured.
- **Two tiers, honestly labelled.** The static tier (UIL-001, 002, 006, 007, 008) needs only Python. The rendered tier (UIL-003, 004, 005) needs Chrome and reports `NOT_RUN` without it. Static parsing cannot see the JS-created controls (3 creation sites here), so the static tier reports "static-visible only", never "complete".
- **Completeness is relative to an enumeration.** UIL-005 is complete over the enumerated (state, actor) pairs. It is a bounded conformance check between two models, not a proof about the UI, and a proof about the workflow model is not a proof about the code. Report it as MEASUREMENT with the enumeration size.
- **Negative oracle.** Each diagnostic ships with a deliberately broken fixture (delete a link, rename a key, add a workflow action) that must fail. AGENTS.md already requires a negative oracle for new operators.
- **Ripple.** A rename of a term or transition uses the existing `closure()` in `domain/impact.py` over the extended edge set. That is a least fixed point, cycle-safe, with no silent depth cap. Adding UI edges adds no new algorithm.

## 5. Mathematics and computer science schools

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Relational algebra / Datalog | UIL-001, 002, 003, 006, 008 are anti-joins and set differences; stratified negation gives them a fixed meaning | Diagnostics are declarative, order-independent, explainable (each row names the missing edge) | Needs the weave query layer to expose joins. A hand-written loop is enough at this size | adopt (as sorted set operations first; Datalog later if the rule count grows) | sections 2.7, 4 |
| Order theory, fixed points | Impact closure over UI edges (existing `closure()`) | Deterministic ripple for term renames; termination on cycles | None new | adopt (already in kernel) | `src/eija_studio/domain/impact.py` |
| Content addressing / Merkle | UI node hash = hash of (key, role, accessible name, links, tokens); bundle hash over sorted node hashes | Skip re-verification of unchanged nodes; the okf lane already links pages by content hash | Hash proves change, not correctness | adopt | `okf/index.md` (okf lane) |
| Bidirectional transformations (lenses) | Domain-to-UI `get`; for editable forms a `put` with laws GetPut and PutGet | Round-trip property tests for form serialisation | Full lens languages are heavy; only the two laws are useful | adapt: property-test form round trips (property lane); theory-only otherwise | [Foster et al., TOPLAS preprint](https://www.cis.upenn.edu/~bcpierce/papers/lenses-toplas-final.pdf) |
| Statecharts and model-based testing | Generate (state, actor) enumeration and shortest paths from `Workflow`; coverage goal: all states, all enabled transitions | Reproducible UI journeys from the model; UIL-005 | Browser time; must reach states through the real API | adopt (BFS in Python) | [XState graph docs](https://stately.ai/docs/xstate-graph), [GraphWalker](http://graphwalker.github.io/) |
| Refinement types, closed schemas | Sidecar JSON Schema with `enum` of existing node ids; JSON Pointer `scope` links | Dangling references cannot be written by an agent (static), the mechanism the agent dossier already proposes | Schema regeneration when the model changes | adapt (generated schema) | [JSON Forms](https://jsonforms.io/docs/) |
| Abstraction and reification (CAMELEON levels) | Name the two directions: model-to-UI coverage, UI-to-model provenance | Shared vocabulary in diagnostics | It is naming, not an algorithm | theory-only | [OUP](https://academic.oup.com/iwc/article-lookup/doi/10.1016/S0953-5438(03)00010-9) |
| Conformance relations (`ioco`) | Formal input-output conformance between a model and an implementation | Would generalise UIL-005 to traces | Not opened this session; UNVERIFIED. Heavy for a small UI | theory-only | UNVERIFIED |
| Category theory | Functorial data migration for model-to-UI mappings | None that is implementable here beyond the relational join | Vocabulary cost for readers | theory-only | none |
| Information theory, probabilistic assurance | Would score link coverage or predict drift | No evidence found this session that it beats a plain ratio (linked nodes / nodes); do not invent a probability | Risk of false precision | theory-only; report plain ratios | none |
| Mutation of links | Delete or rename a link; the checker must fail | Measures whether the link checker can detect drift; ties into the mutation lane | Extra fixtures | adopt | AGENTS.md (negative oracle rule) |

## 6. Implications for EIJA

1. **Add a sidecar UI model** (`graph/schema/ui-model.schema.json`, generated from a typed model) with node kinds `view`, `region`, `control`, `field`, `status`, `table`; edge kinds `realises`, `satisfies`, `labels` (term), `calls` (operationId), `styled-by` (token), `exercised-by` (test). Closed enums, canonical JSON, hashed. Only declared links count; inferred candidates are labelled and never satisfy a gate (ProofMap GAP-024).
2. **One key attribute**, `data-eija-key`, on every interactive and status element, including JS-created ones. Set Playwright `testIdAttribute` to it. The hci lane's recommendation to re-focus "by data-action / id" benefits from the same key.
3. **Stop hard-coding the action list.** Either the server returns available actions for the current instance and actor, or the UI receives the workflow's action list from the case packet. Both are `src/` changes and need their own ADR and regression test; until then UIL-002 and UIL-005 will report today's drift (5-action literal against the 4-action baseline) as findings.
4. **Ship the static tier first** (UIL-001, 002, 006, 007, 008), Python only, no browser, `nox` session `graph` in `quality/sessions/graph.py`, tagged `fast`. Ship the rendered tier (UIL-003, 004, 005) as `full`, `NOT_RUN` without Chrome, serial, one browser.
5. **Reuse, don't duplicate:** okf lane page `resource` URIs (`repo://...`) and content hashes for concept nodes; visual lane for diagrams as projections (the UI model can be rendered by the same generator); hci lane's Playwright and axe results attached to UI node keys; agents lane exposes one query tool, `ui_links(node)`, with bounded output.
6. **Make the glossary the label authority.** UIL-004 compares the browser's accessible name with the ubiquitous-language term plus registered synonyms. Requirement: the language lane's term ids must be stable; that interface is not defined by me and needs agreement with the okf lane.
7. **Tokens:** adopt the DTCG file with a `dev.eija.*` extension for concept links; add UIL-007; defer Style Dictionary. Introduce semantic token names (status, severity) before linking, or the link is decoration.
8. **Explicit `operation_id` on FastAPI routes** so `calls` links survive renames; declare the dynamic `cases/${id}/${action}` route in the sidecar; use oasdiff as an optional process for "which UI nodes call a breaking-changed operation".
9. **Do not adopt** IFML, UsiXML, Causeway, Storybook or a second statechart engine now. Revisit Storybook when the UI is componentised (trigger: more than one reusable component with its own states), and IFML export only if an outside consumer asks.
10. **Measure, don't assert.** The claim that linked UI helps agents or reviewers is unmeasured (00-PRODUCT-THESIS.md, open questions). Add link-completeness as a plain ratio and plan the evaluation with pass^k over pre-registered tasks (hci and eval lanes).

## 7. Gaps and unverified items

- No successful web search in this session (budget exhausted); tools I did not think to open are missing. Candidates not covered: WebRatio, Eclipse Sirius, Figma Code Connect, Backstage-style software catalogs, Playwright component testing, Angular/Vue metadata extractors, Fluent and gettext catalogs (Unicode MessageFormat 2 was opened: UTS #35 Part 9, version 48.2 "stable", per fetch summary, but I did not evaluate catalogs as a link mechanism).
- Not opened: Harel 1987; Pawson thesis (Wikipedia used as a secondary source); Tretmans `ioco`; UsiXML.
- Accname 1.2 status is as returned by the fetch summary; its "deterministic given a fixed DOM" reading is the tool's paraphrase, not a checked quotation.
- Cross-browser equality of accessible names and aria snapshots: UNVERIFIED. Determinism of repeated captures with a pinned Chrome build: not measured; test it before claiming it.
- Version pins for `Playwright` and `axe` may conflict with the hci lane's extra; not checked.
- I did not check whether `tree-sitter` or an HTML/JS parser extracts the Studio's call sites more robustly than a regex; the dynamic-path limitation stands either way.
- Effects on agent success and human comprehension are UNMEASURED. `human_understanding` stays UNKNOWN.
- The proposed diagnostics (UIL-001 to UIL-008), the sidecar, and the two-tier split are a design, not built or tested. Nothing here has been run against the Studio beyond the static counts in section 1.
- Numbers in section 1 are counts from a regex and `html.parser` pass over the source; regex counts are lower bounds for JS-created elements.
