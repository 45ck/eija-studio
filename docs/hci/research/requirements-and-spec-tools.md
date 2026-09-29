# Requirements and spec tools: research dossier

Dossier: requirements-spec. Lane: lane/ux-research. Access date for every URL in this file: 2026-09-29. Status: research input to HCI-ADRs (block 0057-0088); nothing here is a decision yet.

## 0. Decisions first

| # | Recommendation for EIJA | Verdict basis |
|---|---|---|
| 1 | The ubiquitous-language tree is the primary navigation surface, not a tab. One tree, one selection, everything else (requirements, states, journeys, tests, evidence) renders as facets of the selected node. | Tree pattern is standard (APG); trace views work as "selected item plus neighbours" (Jama Trace View) |
| 2 | Suspect state is computed by the kernel from content hashes of the fields that carry meaning, never set by hand, and is cleared only by an owner action that is logged. | DOORS, DOORS Next and Jama use per-attribute triggers (Polarion only via search summary); DOORS and Jama let users clear by hand, which is where trust erodes |
| 3 | Show requirement -> design -> task -> test as a fixed left-to-right lane with one glyph per hop, and show "no downstream" as an explicit gap glyph. | Jama Trace View, Kiro spec phases, Spec Kit consistency report |
| 4 | Review by meaning: group an agent's change into ordered chapters (core change first, consequences second, glue last), each chapter naming the model elements it touches. | Linear Guided Reviews; Spec Kit `analyze`; OpenSpec delta sections |
| 5 | Acceptance criteria are authored in a constrained sentence form (EARS-style templates or Given/When/Then) with template slots, so the kernel can parse them and the UI can lint them. | EARS (Mavin 2009); Gherkin reference |
| 6 | Do not adopt the "three markdown files per feature, generate everything, review prose" workflow as the main surface. Practitioners report it as verbose and tedious to review. | Böckeler 2025; HN thread |
| 7 | Every roll-up shows numerator and denominator and keeps UNKNOWN as its own bucket (never merged into pass or fail). | Azure DevOps "requirements without tests" widget is the closest precedent; none of the products surveyed has a first-class UNKNOWN |

Every layout or timing claim below is a PREDICTION or a design hypothesis unless it cites a measurement. No user study has been run. Section 6 lists what would have to be measured.

## 1. Scope and method

- Searches: about 35 WebSearch queries across the products named in the task, plus law and standard look-ups. The shared WebSearch budget (200 calls) ran out near the end, so the last two look-ups (KLM operator times, Hick-Hyman formula source) were not done.
- Opened: official docs, changelogs, first-party blog posts, GitHub repository pages and the GitHub REST API for star counts, two peer-reviewed or arXiv papers, and two practitioner write-ups. The full URL list is in section 7.
- Page summaries came from WebFetch, which returns a model-written summary of the page, not raw text. Wording in this file is paraphrase. Where a page returned nothing useful (Polarion docs, Springer chapter, Linear sync-engine article) the claim is marked as search-snippet only or UNVERIFIED.
- Web content was treated as data. Nothing fetched was executed.
- Not accessible: paywalled or login-gated content (Springer chapter, Polarion help behind Siemens redirect), and any product UI itself. No product was run; all UI observations are from documentation text, not from screenshots or hands-on use.
- Products cannot be compared on measured usability here. Love and hate claims come from practitioner write-ups and review aggregators and are weak evidence (confidence low to medium).

## 2. Per-product findings

### 2.1 Spec-driven AI tools

#### AWS Kiro

What it is today: an agentic IDE where a "spec" is three markdown files per feature (`requirements.md` or `bugfix.md`, `design.md`, `tasks.md`) generated in phases with an approval gate between phases. Source: [Kiro specs](https://kiro.dev/docs/specs/), [Feature specs](https://kiro.dev/docs/specs/feature-specs/).

| Pattern | Why it works (law or principle) | Source |
|---|---|---|
| Phase gates: requirements -> design -> tasks, each approved before the next is generated. A "Quick Spec" option removes the gates. | User control and freedom; error prevention (a wrong requirement is caught before it multiplies into design and tasks). The Quick Spec escape hatch is flexibility and efficiency of use (heuristics 3, 5, 7). | [Feature specs](https://kiro.dev/docs/specs/feature-specs/), [NN/g heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) |
| Requirements-First vs Design-First entry points, not switchable after start. | Match the user's mental model; fewer modes. Costs flexibility: docs advise creating a new spec to switch. | [Best practices](https://kiro.dev/docs/specs/best-practices/) |
| EARS sentences for acceptance criteria ("WHEN ... THE SYSTEM SHALL ..."). | Constrained syntax reduces ambiguity and makes each criterion machine-extractable, which Kiro exploits for property tests. | [Feature specs](https://kiro.dev/docs/specs/feature-specs/), [Correctness](https://kiro.dev/docs/specs/correctness/) |
| Properties extracted from EARS criteria, shown in the design with hover revealing the source requirement and linked task; failing property tests report a shrunk counterexample. | Recognition over recall (heuristic 6): the link is visible at the point of use. Shrunk counterexamples are error diagnosis (heuristic 9). | [Correctness](https://kiro.dev/docs/specs/correctness/), [PBT blog](https://kiro.dev/blog/property-based-testing/) |
| Task dependency graph run in "waves"; independent tasks run concurrently; live per-task status. | Visibility of system status (heuristic 1). | [Kiro specs](https://kiro.dev/docs/specs/) |
| "Sync Files" in `tasks.md` regenerates tasks after requirement or design edits; a chat request can scan code and mark finished tasks. | Attempts to close the spec-to-code drift loop. Docs list "don't treat specs as static" as a pitfall, which admits drift is the normal failure. | [Best practices](https://kiro.dev/docs/specs/best-practices/) |

Love and hate: a Thoughtworks author found Kiro the lightest of three tools but "like using a sledgehammer to crack a nut" for a small bug, which became four user stories with sixteen acceptance criteria (single case, n=1) ([Böckeler, martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)). HN commenters on the same article report the agent not following every instruction and unpredictable code deletion ([HN item](https://news.ycombinator.com/item?id=45610996)).

Verdict: ADAPT. Adopt phase gates, constrained criteria, visible requirement-to-property links and shrunk counterexamples. Avoid generating a full document trio for small changes; EIJA needs a size-proportional path.

#### GitHub Spec Kit

What it is today: an MIT-licensed toolkit of slash commands and templates for coding agents. Full path: constitution, specify, clarify, plan, checklist, tasks, analyze, implement, converge (9 steps); short path skips clarify, checklist, analyze (5 steps). Artifacts: `spec.md`, `plan.md`, `tasks.md`, `checklists/`. Source: [quickstart](https://github.github.com/spec-kit/quickstart.html), [repo](https://github.com/github/spec-kit).

| Pattern | Why it works | Source |
|---|---|---|
| `analyze` is a read-only consistency report across artifacts, separate from generation. | Separating checker from generator is the same split as EIJA's propose/check. Read-only means the checker cannot silently edit the thing it judges. | [quickstart](https://github.github.com/spec-kit/quickstart.html) |
| `clarify` folds answers back into the spec. | Ambiguity resolved once, recorded in the artifact (recognition over recall). | [quickstart](https://github.github.com/spec-kit/quickstart.html) |
| Checklists are "reviewer-owned" and `implement` gates on unchecked items. | Human-owned gate; error prevention. | [quickstart](https://github.github.com/spec-kit/quickstart.html) |
| `converge` verifies the code against tasks and appends tasks if gaps remain, or reports "Converged". | A terminal state with a name beats an open-ended feeling of done. Closest precedent to EIJA's evidence verdicts. | [quickstart](https://github.github.com/spec-kit/quickstart.html) |
| Constitution: project principles evaluated throughout. | Standing constraints checked at each step, not restated per prompt. Comparable to EIJA invariants. | [spec-kit repo](https://github.com/github/spec-kit) |

Love and hate: the same Böckeler write-up calls Spec Kit output repetitive and tedious to review, and she preferred reviewing code directly (single reviewer, n=1) ([source](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)). Adoption is very high regardless (139,274 stars, 12,475 forks on 2026-09-29, GitHub API), so pull is real even where review ergonomics are poor.

Verdict: ADAPT. Adopt read-only `analyze` and named terminal state. Avoid markdown-file-per-phase as the reviewing surface.

#### OpenSpec

What it is today: MIT-licensed, brownfield-oriented spec workflow (70,589 stars on 2026-09-29). Current truth lives in `openspec/specs/`; each change is a folder with proposal, delta specs, design, tasks. Source: [repo](https://github.com/Fission-AI/OpenSpec), [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md).

| Pattern | Why it works | Source |
|---|---|---|
| Delta specs: ADDED / MODIFIED / REMOVED requirement sections rather than restating the whole spec. | A change is shown as a small diff by meaning; review cost scales with the change, not the spec. | [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) |
| Archive merges deltas into the main specs and moves the change folder to a dated archive. | Explicit promotion step from proposed to accepted; retains rationale. | [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) |
| Artifacts are "enablers, not gates" (proposal, then specs and design, then tasks). | Flexibility; dependency graph, not a wizard. | [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) |
| Scenarios in GIVEN / WHEN / THEN form under each requirement. | Testable statement per requirement. | [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) |

Known defects, from open issues (titles only, single reports): validation and apply disagreeing about a delta; CRLF specs rewritten to LF producing whole-file diffs ([#1869](https://github.com/Fission-AI/OpenSpec/issues/1869), [#1935](https://github.com/Fission-AI/OpenSpec/issues/1935)). Lesson: promotion of a delta into truth is the riskiest step and needs a check that runs before, not after, the merge.

Verdict: ADAPT. The ADDED/MODIFIED/REMOVED vocabulary is a good scaffold for review-by-meaning; EIJA generates the delta from the model diff rather than from a hand-written file.

### 2.2 Requirements-management tools (traceability)

#### Jama Connect

What it is today: requirements and test management with upstream/downstream relationships, suspect links and Trace View. Source: [Relationships](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/relationships.html), [Trace View](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/trace-view.html), [Clear suspect links](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/relationships/clear-suspect-links.html).

| Pattern | Why it works | Source |
|---|---|---|
| Trace View is columns by level: source item, then direct downstream to the right; each level header shows a unique-item count. | Spatial consistency: left-to-right is always upstream-to-downstream (consistency and standards). Counts give a roll-up without opening anything. | [Trace View](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/trace-view.html) |
| A red "!" marks a missing relationship required by the relationship rule. | A gap is drawn where the link would be, so absence is visible. Note it relies on colour plus a glyph, which passes WCAG 1.4.1 only because of the glyph. | same; [WCAG 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) |
| Blue arrows to travel upstream or downstream; inline edit and add-related-item without leaving Trace View. | Keeps the user in one context (fewer mode switches, lower interaction cost). | [Trace View](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/trace-view.html) |
| Suspect triggers only on fields the org admin selects per item type; users clear one or all suspect links by hand. | Field-level triggers cut noise. Manual Clear/Clear All is the weak point: the docs page does not describe permissions or an audit trail (UNVERIFIED whether they exist). | [Clear suspect links](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/relationships/clear-suspect-links.html) |
| Compare Versions gives a side-by-side of the upstream change, to decide whether a suspect downstream item needs edits. | Suspect flag is paired with the reason for suspicion. | [Jama blog](https://www.jamasoftware.com/blog/2025/09/13/the-importance-of-suspect-tracking-in-requirements-management/) (vendor marketing; medium confidence) |

Verdict: ADOPT the column layout, gap glyph, and flag-plus-diff pairing. ADAPT suspect clearing: EIJA clears only via an owner decision record.

#### IBM DOORS and DOORS Next

What it is today: the long-running requirements tools. Classic DOORS marks linked objects suspect when the object they link to changes; DOORS Next replaces this with "link validity". Source: [DOORS suspect links](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors/9.7.2?topic=data-suspect-links-changed-objects), [DOORS Next link validity](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors-next/7.1.0?topic=projects-link-validity).

| Pattern | Why it works | Source |
|---|---|---|
| A change is suspect-relevant only if it touches an attribute flagged "Affect change dates" (DOORS) or "Affects Link Validity" (DOORS Next). Title and Description count by default; State does not. | Trigger on meaning-bearing fields, not on every edit. Direct precedent for hashing only semantic fields. | both IBM pages |
| DOORS Next shows a validity icon next to each link and an optional summary column; admins may switch it off "to reduce the clutter". | An honest admission that status marks on every row cost attention. | [link validity](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors-next/7.1.0?topic=projects-link-validity) |
| Validity is shared across baselines and streams, and the docs warn it cannot show which artifacts changed; compare configurations instead. | Two questions kept apart: "is this link still meaningful" versus "what changed". | search summary of [IBM ELM link validity](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/lifecycle-management/7.0.3?topic=management-link-validity); page not opened, medium confidence |
| Classic DOORS: clearing a suspect link at the source also clears it at the target. | Efficient, but one person's click removes the warning for the other end. | [DOORS suspect links](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors/9.7.2?topic=data-suspect-links-changed-objects) |

Love and hate: review-site text (PeerSpot, Capterra, Visure vendor page) says DOORS Next feels complex, slows with scale, and is hard for occasional users. These are aggregated opinions with vendor bias in some sources; confidence low ([PeerSpot](https://www.peerspot.com/products/ibm-doors-next-reviews), [Visure](https://visuresolutions.com/ibm-doors-guide/disadvantages/), seen via search only).

Verdict: ADOPT per-field validity triggers and the "affects" flag as a schema property. AVOID hand-cleared status and per-row icon noise as the default.

#### Polarion

What it is today: Siemens ALM with a traceability matrix and an Auto-Suspect option. Primary Siemens pages returned no usable text (redirects and an empty shell), so this section rests on search-result summaries of the same docs and a community thread (medium-low confidence). Reported: Auto-Suspect sets a suspect attribute on links to child work items when a linked item is modified; the flag is per link and can be toggled in the work item editor ([search result](https://docs.plm.automation.siemens.com/content/polarion/19.2/help/en_US/user_and_administration_help/user_guide/work_items/link_work_items/suspect_links.html), page body not read). Matrix documentation not read.

Verdict: UNVERIFIED for interaction detail. Useful only as a fourth data point that suspect logic is directional (parent to child).

#### Azure DevOps Boards

What it is today: work items with typed links to branches, commits, PRs, builds, releases and tests. Source: [End-to-end traceability](https://learn.microsoft.com/en-us/azure/devops/cross-service/end-to-end-traceability?view=azure-devops), [Requirements traceability](https://learn.microsoft.com/en-us/azure/devops/pipelines/test/requirements-traceability?view=azure-devops).

| Pattern | Why it works | Source |
|---|---|---|
| The "Requirements quality" dashboard widget lists requirements in scope with test pass rate, failed-test count, and a way to spot requirements with no linked test. | Roll-up with numerator and an explicit "no evidence" case; drill-down on the failed count opens the test results. | [Requirements traceability](https://learn.microsoft.com/en-us/azure/devops/pipelines/test/requirements-traceability?view=azure-devops) |
| Development and Deployment sections on the work item form show linked branches, PRs, builds, stages. | Trace lives on the item, not in a separate report. | [End-to-end traceability](https://learn.microsoft.com/en-us/azure/devops/cross-service/end-to-end-traceability?view=azure-devops) |
| From a test result, create a bug that carries the error, stack trace and links back to requirement and test. | Failure to requirement in one hop. | same |
| MCP prompts such as "list user stories with no linked test cases" are documented as a supported query path. | Gap queries are common enough to be first-class prompts. Also a hint that a query surface belongs beside the tree. | same |

Verdict: ADAPT. The "requirements with no test" question must be one click, and EIJA should split it into UNKNOWN (never checked) and FAIL.

#### Jira, Confluence, Productboard, Notion, Linear

These are planning tools, not verification tools. They matter for tree, hierarchy, roll-up and agent-delegation patterns.

**Jira.** Default hierarchy has three levels (epic, story-level, sub-task); changing it affects all company-managed spaces, cannot be undone, and breaks existing parent-child relationships; extra levels need Premium or Enterprise ([hierarchy](https://support.atlassian.com/jira-cloud-administration/docs/configure-the-issue-type-hierarchy/)). Links are a name plus an outward and an inward description, giving direction-aware phrasing on each end ([link types](https://support.atlassian.com/jira-cloud-administration/docs/configure-issue-linking/)). Pattern to adopt: paired inward/outward verbs on links ("is refined by" / "refines"). Pattern to avoid: a hierarchy that is admin-only and irreversible. Critics blame slow screens and too many fields; only blog evidence was found (low confidence, [DEV](https://dev.to/imdone/why-developers-hate-jira-and-what-were-doing-about-it-1h06)). Verdict: ADAPT link phrasing, AVOID field sprawl.

**Confluence.** The Product Requirements blueprint uses a Page Properties macro on each page and a report macro on an index page that shows status and owner per requirement; instructional text disappears when typing starts ([blueprint](https://confluence.atlassian.com/doc/product-requirements-blueprint-329975392.html)). Pattern: structured properties on a prose page, aggregated elsewhere. That is a form of "generated view from source" and it works because the index is derived. Atlassian's claim that Rovo keeps Jira and Confluence pages in sync is from a search summary only and is UNVERIFIED. Verdict: ADAPT the derived index; AVOID free-prose requirements the kernel cannot parse.

**Productboard.** Hierarchy of product, component, subcomponent, feature, subfeature, with drag and drop reordering; the docs tell users not to nest subcomponents in subcomponents ([hierarchy](https://support.productboard.com/hc/en-us/articles/360058212253-Build-your-product-hierarchy)). Insights link to features and objectives feed a weighted score ([search summary](https://support.productboard.com/hc/en-us/articles/360058212333-Add-features-to-your-hierarchy), page not opened). Pattern: a depth budget stated in the docs. Verdict: ADAPT with a hard depth budget tied to the DDD structure (context, aggregate, entity/value, term = 4 levels).

**Notion.** Sub-items render as "nested in toggle" or "flattened list" in table, list and timeline views; filters can show parents only, parents plus matching sub-items, or sub-items only; dependencies shift dates automatically ([sub-items and dependencies](https://www.notion.com/help/tasks-and-dependencies)). Pattern: one tree, a filter with three explicit scoping modes. That answers "when I filter, do I keep my ancestors?" Verdict: ADOPT the three-mode filter for the language tree.

**Linear.** Hierarchy issue -> cycle/project -> initiative with views as filters ([concepts](https://linear.app/docs/conceptual-model)). Design write-up: theme generated from three variables (base, accent, contrast) in LCH instead of 98 per-theme variables; reduced visual noise; Inter Display for headings ([redesign](https://linear.app/now/how-we-redesigned-the-linear-ui)). Agents: the human stays the primary assignee and an agent "cannot be the primary assignee"; delegation is supplementary ([assigning](https://linear.app/docs/assigning-issues)); the Agent Interaction Guidelines state that an agent must disclose itself, show state, and that humans keep accountability ([AIG](https://linear.app/developers/aig)). Review: Guided Reviews split a diff into chapters that show the core of the change first, then consequences, with glue code separate; structural diff highlighting; approval state syncs to GitHub ([Reviews](https://linear.app/docs/diffs), [agent-era review](https://linear.app/now/reviewing-code-in-the-agent-era)). Linear says PR volume rose about 50% and that structured review lets reviewers keep their bar (self-reported, medium). Verdict: ADOPT the assignee/delegate split as the UI form of "AI proposes, owner decides"; ADAPT chapters so each chapter names model elements, not files; ADAPT the base/accent/contrast token generation for EIJA tokens.

### 2.3 Executable-spec tooling

#### Cucumber / Gherkin, Behave, SpecFlow and Reqnroll

What it is today: Gherkin is the Given/When/Then feature-file language with Feature, Rule (v6+), Scenario, Background, Scenario Outline and Examples, tags and data tables ([reference](https://cucumber.io/docs/gherkin/reference/)). Behave is the Python implementation with tags, formatters and steps ([Behave](https://behave.readthedocs.io/en/latest/philosophy/)). SpecFlow reached end of life on 2024-12-31 and the community fork Reqnroll (over 5,000 projects by early 2025) took over; the closed-source LivingDoc did not transfer and no open replacement for Azure DevOps is planned ([Reqnroll](https://reqnroll.net/news/2025/01/specflow-end-of-life-has-been-announced/)).

| Pattern | Why it works | Source |
|---|---|---|
| `Rule` groups scenarios under one business rule. | A tree level between feature and example; readers scan rules, open examples on demand (progressive disclosure). | [reference](https://cucumber.io/docs/gherkin/reference/) |
| Declarative over imperative steps: state intent, keep UI mechanics in step code. | Scenarios survive implementation change; shorter text. | [Better Gherkin](https://cucumber.io/docs/bdd/better-gherkin/) |
| Tags for filtering and selective runs. | Cheap faceting without a schema. | [reference](https://cucumber.io/docs/gherkin/reference/) |
| Living documentation as a generated report of scenario results. | The document is checked by running it. Lesson from SpecFlow: keep the renderer open source or the ecosystem breaks. | [Reqnroll](https://reqnroll.net/news/2025/01/specflow-end-of-life-has-been-announced/) |

Verdict: ADAPT. EIJA journeys and acceptance examples can map to Rule and Scenario; the kernel, not a hidden runner, owns pass/fail/UNKNOWN. A scenario with no step binding must show as UNKNOWN, not as a green skipped test (Behave and Cucumber undefined-step behaviour was not verified this session, UNVERIFIED).

#### Storybook

What it is today: a component workshop with a testing widget at the bottom of the sidebar; after a run each story and component shows a pass, fail or error indicator; the widget reports totals, and pressing the failure count filters the sidebar to failing stories; a watch mode re-runs tests on edit; a11y and visual test types appear in the same widget; selecting a result opens the debugging panel for that story ([Vitest addon](https://storybook.js.org/docs/writing-tests/integrations/vitest-addon), [writing tests](https://storybook.js.org/docs/writing-tests)).

| Pattern | Why it works | Source |
|---|---|---|
| Status glyph on every tree row, roll-up counts in a persistent footer. | Recognition over recall; status is in the navigation, not a separate report. | [Vitest addon](https://storybook.js.org/docs/writing-tests/integrations/vitest-addon) |
| Click the failure count to filter the tree to failures. | One action from summary to the affected set (Fitts: large, always-in-place target; interaction cost of one click). | same |
| Watch mode with live status. | Sub-second feedback keeps the flow of thought (see the 1-second limit in section 3). | same; [NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/) |
| Result selection navigates to the debug panel. | Failure to diagnosis in one hop. | same |

Verdict: ADOPT. This is the closest existing model for how verification status should sit in EIJA's tree.

## 3. Cross-cutting findings

**Traceability visualisation choice depends on task and size.** A comparative study with 24 participants reports that matrices and graphs are preferred for management tasks, hyperlinks for implementation and testing tasks; matrices lose readability as the artifact set grows and lose hierarchy ([Which traceability visualization is suitable, Springer chapter, via search summary; page not opened, medium confidence](https://link.springer.com/chapter/10.1007/978-3-642-28714-5_17)). Implication: inline links as the default for developers, a matrix for audit and export only.

**Engineers do not all use traces the same way.** An interview study of change-impact analysis found engineers differ in how they seek information, some do not find traceability particularly useful, and tools should offer search, browse and trace side by side ([Borg, Alegroth, Runeson 2017](https://arxiv.org/abs/1703.01897)). Implication: the ripple view needs a query box and a tree, not only a graph.

**Traceability research names three goals: ubiquitous, trustworthy, purposeful** ([Antoniol et al. 2017](https://arxiv.org/abs/1710.03129)). Suspect flags that people clear by hand undermine the second.

**Response time limits.** 0.1 s feels instantaneous, 1 s is the limit for uninterrupted flow of thought, 10 s is the limit for attention; original 1993, updated 2014 ([NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/)). The Doherty 400 ms threshold was not verified this session and is not used here.

**Progressive disclosure.** NN/g warns that designs beyond 2 disclosure levels typically show low usability because users get lost ([NN/g](https://www.nngroup.com/articles/progressive-disclosure/)). This is a practitioner rule of thumb, not a controlled result.

**Tree keyboard model.** The W3C APG tree view defines arrow keys, Home/End, type-ahead, `*` to expand siblings, and `aria-level`, `aria-setsize`, `aria-posinset` for large or lazily loaded trees ([APG](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)).

**Colour must not be the only carrier of meaning** (WCAG 2.2 SC 1.4.1, level A) ([Understanding SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)). Fitts's law: movement time grows with distance and shrinks with target width; screen-edge advantage does not apply to touch ([NN/g](https://www.nngroup.com/articles/fitts-law/)). Hick's law: decision time grows with the number and complexity of choices ([Laws of UX](https://lawsofux.com/hicks-law/), practitioner summary; primary Hick 1952 and Hyman 1953 papers not opened). Validity limits: Fitts applies to pointing, not keyboard; Hick applies to unpracticed choice among equiprobable alternatives and overstates cost for experts who know where things are.

**EARS.** Published at the IEEE Requirements Engineering Conference 2009 (Mavin, Wilkinson, Harwood, Novak; pp. 317-322); five templates trialled on aero engine control requirements, addressing eight named problems including ambiguity ([Manchester record](https://research.manchester.ac.uk/en/publications/easy-approach-to-requirements-syntax-ears/)). Current template forms: ubiquitous, state-driven ("While"), event-driven ("When"), optional feature ("Where"), unwanted behaviour ("If ... then"), complex ([Mavin site](https://alistairmavin.com/ears/)). Limit: evidence is from one domain and one organisation; the "EARS reduces errors" claim in secondary sources was not traced to a controlled study here.

## 4. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| Spec Kit: 139,274 stars, 12,475 forks, MIT, created 2025-08-21, last push 2026-09-28 | [GitHub API](https://api.github.com/repos/github/spec-kit) | high |
| OpenSpec: 70,589 stars, 4,840 forks, MIT, created 2025-08-05 | [GitHub API](https://api.github.com/repos/Fission-AI/OpenSpec) | high |
| Spec Kit full path is 9 commands; short path is 5 | [quickstart](https://github.github.com/spec-kit/quickstart.html) | high |
| A minor bug fix became 4 user stories with 16 acceptance criteria in Kiro (one observation, n=1) | [Böckeler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) | medium |
| Kiro property tests run 100 cases per property via Hypothesis (per first-party blog example) | [Kiro PBT blog](https://kiro.dev/blog/property-based-testing/) | medium |
| Kiro runs independent tasks in dependency "waves" | [Kiro specs](https://kiro.dev/docs/specs/) | high |
| EARS: 5 templates originally, 8 problems addressed, RE'09, pp. 317-322 | [Manchester](https://research.manchester.ac.uk/en/publications/easy-approach-to-requirements-syntax-ears/) | high |
| Linear theme: 3 input variables replace 98 per theme; LCH colour space | [Linear redesign](https://linear.app/now/how-we-redesigned-the-linear-ui) | high |
| Linear redesign was a six-week focused sprint | [Linear redesign](https://linear.app/now/how-we-redesigned-the-linear-ui) | medium |
| Linear agent sessions have 6 states (pending, active, error, awaitingInput, complete, stale) | search summary of [Linear developers](https://linear.app/developers/agent-interaction); page not opened | medium |
| Linear: agent cannot be primary assignee; human remains responsible | [Linear docs](https://linear.app/docs/assigning-issues) | high |
| Linear reports about 50% higher PR volume; self-reported | [Linear blog](https://linear.app/now/reviewing-code-in-the-agent-era) | medium |
| Jira default hierarchy: 3 levels; changes irreversible; custom levels need Premium/Enterprise | [Atlassian](https://support.atlassian.com/jira-cloud-administration/docs/configure-the-issue-type-hierarchy/) | high |
| Productboard hierarchy: product, component, subcomponent, feature, subfeature (5 levels) | [Productboard](https://support.productboard.com/hc/en-us/articles/360058212253-Build-your-product-hierarchy) | high |
| Notion sub-item filter has 3 scoping modes; 2 nesting display modes in table/list/timeline | [Notion](https://www.notion.com/help/tasks-and-dependencies) | high |
| DOORS Next: Title and Description affect link validity by default; State does not | [IBM](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors-next/7.1.0?topic=projects-link-validity) | high |
| Traceability visualisation study: 24 participants | [Springer](https://link.springer.com/chapter/10.1007/978-3-642-28714-5_17) via search summary | medium |
| SpecFlow end of life 2024-12-31; Reqnroll over 5,000 projects by early 2025 | [Reqnroll](https://reqnroll.net/news/2025/01/specflow-end-of-life-has-been-announced/) | medium |
| Response-time limits 0.1 s, 1 s, 10 s | [NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/) | high |
| Progressive disclosure: more than 2 levels typically low usability | [NN/g](https://www.nngroup.com/articles/progressive-disclosure/) | medium (rule of thumb) |

## 5. Implications for EIJA

Each is a hypothesis for an HCI-ADR, not a measured result.

1. **Tree as the spine.** One keyboard-navigable tree (APG tree model) of the ubiquitous language and DDD structure: context, aggregate, entity or value object, term. Depth budget 4 levels, enforced by the model, following Productboard's explicit depth warning and NN/g's caution on nesting. PREDICTION (unmodelled; to be computed with the KLM in the task-flow files): type-ahead reaches a known term in a few keystrokes regardless of tree size. Validity limit: assumes the user knows the term's name; browsing by arrow keys scales with depth and sibling count.
2. **Every row carries a status glyph and a count, and the footer carries the roll-up.** Follow Storybook: click a count to filter to that state. Keep four states as distinct glyph shapes, not colours alone: pass, fail, UNKNOWN, stale (suspect). Do not merge UNKNOWN into anything.
3. **Selection drives a facet strip, not tabs.** Selecting a term shows a Trace View style lane: requirement, state, journey, test, persona, evidence, left to right, with counts per lane and a gap glyph where a required link is missing (Jama Trace View). This replaces the four-tab baseline for the review task. PREDICTION: removes one tab switch per lookup relative to the baseline, to be tested on the task-flow files.
4. **Suspect is computed, field-scoped and asymmetric.** The kernel hashes only fields marked meaning-bearing (per DOORS Next "Affects Link Validity" and Jama admin-chosen fields) and shows the diff that caused the flag next to the flag (Jama Compare Versions). Clearing is an owner decision with a record; no "Clear All" (DOORS and Jama offer manual clearing; no audit trail was described on the pages read).
5. **Review by meaning uses ordered chapters.** Group an agent's change by model element: core change first, consequences second, glue last (Linear Guided Reviews), labelled with ADDED / MODIFIED / REMOVED at the requirement, state, journey and test level (OpenSpec). Each chapter lists the ripple targets it touches. Approve and apply exist only as owner controls; an agent is shown as a delegate, never as the assignee (Linear).
6. **Size-proportional spec path.** Small edit: one line and one criterion, no design file. Large change: full chain. Spec Kit's short path (5 steps) versus full path (9) and Kiro's Quick Spec show the need; Böckeler's 4-stories-for-a-bug case shows the cost of no such path.
7. **Acceptance criteria are template-constrained.** EARS-style slots or Given/When/Then, parsed by the kernel and linted inline. A criterion with no check bound to it is UNKNOWN. Consider property extraction as Kiro does, but label the result "property test, N cases, not a proof".
8. **Timing budgets (PREDICTION).** Tree expand, select and filter under 100 ms (feels instantaneous); trace lane load under 1 s (keeps flow); anything longer shows a progress state with a cancel (10 s limit). Compute suspect and roll-ups incrementally so the tree does not wait on the kernel.
9. **Density budget from precedent.** DOORS Next lets admins hide validity icons to cut clutter, which supports one glyph per row and details on selection rather than a badge stack. Starting target stays within the 12-container and 120-word budgets; needs calibration against a reference screen of Linear, Jama Trace View and Storybook.
10. **Offer search, browse and trace together.** The Borg et al. interviews show engineers differ; give a command box for terms and gap queries ("requirements with no test", as in the Azure DevOps prompt list), the tree for browsing, and the lane for tracing.
11. **Keep any generated renderer open and inside the kernel's checks.** SpecFlow's LivingDoc closure is the cautionary case; ADR-013 (no build-time framework, text via DOM text nodes) already fits: a tree and a lane are plain DOM.

## 6. Study protocol sketch (not executed)

To turn predictions into evidence: within-subject, 12 or more developers, tasks drawn from the excursion-workflow domain: (a) find the requirement affected by an agent change; (b) decide whether a suspect flag needs action; (c) find requirements with no evidence. Compare baseline UI against the proposed tree and lane. Measure time on task, errors, and the count of UNKNOWN items misread as pass (target zero). Pre-register the hypotheses, report effect sizes with intervals, and do not claim benefit before this is run.

## 7. Gaps and unverified items

- **Polarion**: primary docs unreadable; suspect behaviour and matrix layout UNVERIFIED beyond search summaries.
- **DOORS Next**: Links Explorer visual design and baseline compare UI not read; link-validity page read, ELM 7.0.3 page seen via search only.
- **Notion, Confluence** as requirements tools: only help pages on sub-items and one blueprint were read. Rovo sync claim UNVERIFIED.
- **Kiro**: how requirement numbers appear in `tasks.md` and the "Update tasks" UI were not stated on pages read; UI observed only through docs text.
- **Cucumber/Behave**: undefined-step and pending-step reporting not verified; matters for UNKNOWN handling.
- **Spec drift evidence** is anecdotal (one blog, one HN thread). No quantitative study of drift found.
- **Love and hate** claims: review aggregators and vendor pages (PeerSpot, Visure) are biased; treat as low confidence.
- **Not done**: KLM operator times and Hick-Hyman constants (search budget exhausted, Wikipedia GOMS page lists operators but no values), Doherty threshold, CVD and contrast checks, hands-on use of any product, timing measurement of any product.
- **Springer traceability study** authors, year and full findings not read; only a search summary of participants and preferences.
- Linear sync-engine claims (local-first, optimistic UI) come from search summaries and third-party write-ups; the official article returned no body text. Not used as evidence above.

### URLs opened this session (access date 2026-09-29)

Kiro: kiro.dev/docs/specs/, /docs/specs/feature-specs/, /docs/specs/best-practices/, /docs/specs/correctness/, /blog/property-based-testing/, /changelog/.
Spec Kit: github.com/github/spec-kit, github.github.com/spec-kit/quickstart.html, api.github.com/repos/github/spec-kit.
OpenSpec: github.com/Fission-AI/OpenSpec, .../docs/concepts.md, api.github.com/repos/Fission-AI/OpenSpec.
Practitioner: martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html, news.ycombinator.com/item?id=45610996.
Jama: help.jamasoftware.com pages for Trace View, Relationships, Clear suspect links; jamasoftware.com blog 2025/09/13 suspect tracking.
IBM: ibm.com/docs DOORS 9.7.2 suspect links, DOORS 9.7.1 links and traceability, DOORS Next 7.1.0 link validity.
Polarion: docs.sw.siemens.com and related redirects (no usable body), projekt.eplm.de (login shell).
Azure DevOps: learn.microsoft.com end-to-end-traceability, requirements-traceability.
Atlassian: support.atlassian.com issue linking, hierarchy; confluence.atlassian.com product requirements blueprint.
Productboard: support.productboard.com build-your-product-hierarchy. Notion: notion.com/help/tasks-and-dependencies.
Linear: linear.app/now/how-we-redesigned-the-linear-ui, /docs/conceptual-model, /changelog, /developers/aig, /docs/assigning-issues, /docs/diffs, /now/reviewing-code-in-the-agent-era, /now/code-review-should-be-fast, /now/scaling-the-linear-sync-engine.
Executable specs: cucumber.io/docs/gherkin/reference/, cucumber.io/docs/bdd/better-gherkin/, behave.readthedocs.io philosophy, reqnroll.net SpecFlow end-of-life post, storybook.js.org writing-tests and vitest-addon.
EARS and papers: research.manchester.ac.uk EARS record, alistairmavin.com/ears/, arxiv.org/abs/2306.10972, /abs/1703.01897, /abs/1710.03129, link.springer.com chapter (redirect only).
HCI: nngroup.com response-times, ten heuristics, fitts-law, progressive-disclosure; lawsofux.com/hicks-law; w3.org APG treeview; w3.org WCAG22 use-of-color; en.wikipedia.org/wiki/GOMS.
