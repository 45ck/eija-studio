# Synthesis: what the research says the Studio should be

Lane `lane/ux-research`. Date 2026-09-29. Inputs: the ten dossiers in this folder (read in full) plus the repo files named in section 9. Status: research input for HCI-ADRs 0057-0088. Nothing here is a decision and nothing here is a measurement of EIJA users.

## 0. Decisions first

| # | Conclusion | Confidence | Where the evidence is |
|---|---|---|---|
| 1 | The open space is **assurance by meaning for AI-generated change**: review a typed semantic operation (not a line), see its ripple across five models with UNKNOWN kept separate, read evidence with its bound, and leave the decision to the owner. Parts exist in separate products; no surveyed product combines them in the documentation read. | Medium: absence claims rest on docs and changelogs; no product was run | section 4; AIC§0 #5, AIC§4 |
| 2 | Build the Studio around one spine: a **ubiquitous-language / DDD tree** whose selection drives a facet lane (requirement, state, journey, test, persona, evidence). This replaces the four tabs of the baseline. | Medium: tree, trace lane and status footer are each established patterns; the combination is untested | REQ§0 #1, REQ§5; MOK§5 |
| 3 | The picture is a **projection**. Gestures emit typed operation requests; the kernel accepts or refuses with a reason; layout is stored apart from meaning and keyed by stable id. | Medium: GLSP and Sirius describe this; no editor was run | DGM§3.1, DGM§5; MOK§5 #3 |
| 4 | **UNKNOWN is a first-class result** in every count and roll-up, with a shape, a word and the bound. Two mainstream tools turn "no result" into success (GitHub skipped required check, Codecov `if_not_found`). | High for the products' documented behaviour | REV§0, REV§4, REV§11 |
| 5 | **Approval stays human-only, deliberate and rare.** Do not adopt classifier, `auto_review`, "allowed" tool mode or approving AI reviews. Optimise time to evidence, not time to approve. | High for the invariant; medium for the rubber-stamping risk (vendor-reported 93% prompt approval, verified) | AIC§2.1, LAW§3, REV§2; V2 |
| 6 | Every layout, timing and colour claim is a **PREDICTION with a stated band**. The dossiers give KLM bands of plus or minus 21 % and Fitts ID in bits, not milliseconds. No user-benefit claim exists until a user study runs. | High | LAW§2.1, 2.4; all dossiers |
| 7 | The baseline's problems are text volume, type and container sprawl, not gradients (measured: 0 gradients, 0 shadows, 0 blur; 13 font sizes, 7 weights, 10 eyebrows, 404 words). | High: I measured it (section 6, C3) | SLP§3.3; R1 |
| 8 | Small server changes are prerequisites for fonts and any asset beyond two files: `font-src`, the `/assets` allowlist, caching. Each is security-relevant and needs a record. | High: read in `http.py` | VIS§2.6; R2 |

## 1. How to read this file

**Source ids.** `XXX§n` means section n of a dossier in this folder. The dossier authors opened the URLs on 2026-09-29 and recorded them at the end of each dossier; I did not re-open those pages except where marked V.

| Id | Dossier file | Lane topic |
|---|---|---|
| AIC | `ai-coding-and-vibe-coding-products.md` | AI coding and vibe-coding products, trust research |
| ADC | `ai-design-and-canvas-tools.md` | AI design and canvas tools, grounding |
| DGM | `diagramming-and-uml-tools.md` | Diagramming and UML, canvas libraries |
| REQ | `requirements-and-spec-tools.md` | Requirements, traceability, spec-driven AI tools |
| MOK | `mockup-and-prototyping-tools.md` | Figma, Penpot, Sketch, Storybook and similar |
| REV | `review-diff-and-assurance-uis.md` | Review, visual diff, gates, traces, proof status |
| LAW | `hci-laws-and-quantitative-models.md` | Laws, formulas, validity limits, oracles |
| VIS | `visual-design-foundations.md` | Colour, type, motion, icons, tokens |
| DEV | `developer-tool-craft-benchmarks.md` | Developer-tool craft, OSS components |
| SLP | `ai-generated-ui-slop-and-first-impressions.md` | Slop tells, first impressions, computable metrics |

**Pages I opened myself this session (access date 2026-09-29).**

| Id | URL | What I confirmed |
|---|---|---|
| V1 | https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1 s, 1 s, 10 s limits; origins Miller 1968 and Card et al. 1991 |
| V2 | https://anthropic.com/engineering/claude-code-auto-mode | 93% of permission prompts approved; classifier 0.4% false positive on n=10,000 real traffic, 17% false negative on n=52 real overeager actions (vendor-reported) |
| V3 | https://www.designtokens.org/tr/2025.10/format/ | Final Community Group Report, 28 October 2025; "not a W3C Standard"; considered stable |
| V4 | https://www.designtokens.org/tr/2025.10/color/ | Same status; colour `$value` has `colorSpace`, `components`, optional `alpha`, optional 6-digit `hex`; `oklch` supported; no "do not implement" text |
| V5 | https://linear.app/docs/assigning-issues | An agent cannot be the primary assignee; the human stays assignee and responsible |
| V6 | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | SC 2.5.7 (Level AA): dragging functionality needs a single-pointer non-dragging alternative |
| V7 | https://www.nngroup.com/articles/progressive-disclosure/ | 2006 article: designs beyond 2 disclosure levels typically have low usability |
| R1 | Repo `src/eija_studio/resources/web/{index.html,app.css,app.js}` | Baseline counts by my own script (section 6, C3); no tree, palette, counterexample view or drag; layout edited by numeric X/Y fields |
| R2 | Repo `src/eija_studio/interfaces/http.py` lines 61-63, 80-82 | CSP is `default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:`; all responses `no-store`; `/assets/` serves only `app.js` and `app.css` |
| R3 | Repo `src/eija_studio/domain/evidence.py` | Kernel evidence statuses in code: PASS, FAIL, CONFLICT, STALE, UNKNOWN |

**Confidence** follows the dossiers: high (primary or standard read, or first-party documentation), medium (summaries, single sources, vendor claims), low (opinion, snippet-only). Vendor statistics are vendor-reported.

**Limits that apply to the whole file.** WebFetch returns model-written summaries, not raw pages. No product was used hands-on by any dossier author; every UI observation comes from documentation, changelogs, first-party blogs and some third-party write-ups. "No surveyed product does X" means "not found in the pages read".

## 2. Pattern matrix

Cells say what the product does today, with a source id. A dash means the dossiers found nothing (either not surveyed or not present; each dossier's gaps section says which). Columns are product families, not a ranking. Matrix A covers authoring surfaces, B change review and authority, C assurance and navigation.

### 2.A Authoring surfaces

| Capability | AI coding and vibe-coding | Diagram and UML | Design, mockup, prototype | Requirements and spec | Assurance and formal | Craft benchmarks |
|---|---|---|---|---|---|---|
| **Canvas editing** | Lovable Visual Edits: stable component ids map a DOM click to source; a no-LLM path exists (ADC§2.7). v0 Design Mode edits without credits, Tailwind only (ADC§2.6). Claude Design: chat, comment, direct edit, sliders on one canvas (ADC§2.1). Cursor Design Mode injects the selected element into chat, third-party write-up (AIC§2.2) | GLSP: client sends operation requests, server validates and applies (DGM§2.9). draw.io: hover arrows create connectors, Tab / Alt+Tab traverse shapes and parents (DGM§2.1). draw.io re-edit of Mermaid resets positions and connector paths (DGM§2.1). FigJam Tidy is an explicit command (DGM§2.3). Ilograph has no manual layout (DGM§2.10). tldraw announces "n of total" in a live region (DGM§2.5) | Figma layers panel: drag to reparent; server rejects cycle-creating moves; last-writer-wins per property (MOK§2.1). Framer variants are named states with transitions (MOK§2.4). ProtoPie trigger, condition, response grammar (MOK§2.5). Axure notes on widgets hold requirements (MOK§2.7) | Kiro design.md shows properties with hover to the source requirement (REQ§2.1) | Alloy visualiser: graph, table, text views and projections of one instance (REV§5) | Zed frame budget 8.33 ms at 120 Hz (DEV§2.4) |
| **Tree navigation** | Claude Code agent view: rows grouped by state with a one-line summary (AIC§2.1) | Ilograph resource tree plus perspectives plus finder (DGM§2.10). Structurizr one model, many views (DGM§2.8) | Figma and Penpot layers (Penpot: no search documented) (MOK§2.1, 2.2). Axure Outline is searchable and sortable (MOK§2.7) | APG tree keyboard model (REQ§3). Notion: three filter modes keep or drop ancestors (REQ§2.2). Productboard states a depth budget (REQ§2.2). Jira hierarchy is admin-only and irreversible (REQ§2.2). Storybook: status glyph on every row, roll-up in a footer, click a count to filter (REQ§2.3) | Nx graph: focus, search, edge provenance (REV§8) | VS Code names each surface and its purpose (DEV§2.3) |
| **Tokens and design system** | v0: a component, prop or token that cannot be verified from sources must not be used (ADC§2.6). Figma Make kits disclose token extraction loss (ADC§2.3). DESIGN.md: tokens plus rationale, lint, diff, DTCG export; alpha (ADC§2.5). Claude Design tests the extracted system before an org-wide toggle (ADC§2.1) | — | DTCG 2025.10 in Penpot; set order silently cascades (MOK§2.2). Sketch extends colour variables, Display P3 (MOK§2.3). Figma variables with modes (MOK§2.1) | — | — | Linear: 3 inputs (base, accent, contrast) replace 98 theme variables (DEV§2.1; REQ§2.2). Geist: 10 scales x 10 role-named steps (DEV§2.7). Radix 12 role steps; Primer 3 tiers and 9 themes (VIS§2.5). DTCG 2025.10 is a Final Community Group Report, not a W3C Standard (V3, V4) |

### 2.B Change review and authority

| Capability | AI coding and vibe-coding | Diagram, design, mockup | Requirements and spec | Review and assurance | Craft benchmarks |
|---|---|---|---|---|---|
| **Agent plan and diff display** | Line and hunk diffs: Codex scopes (unstaged, staged, commit, branch, last turn), Zed multibuffer, Claude Code Desktop (AIC§2.3, 2.8, 2.1). Devin Review reorders hunks by intent using a model (AIC§2.7). Plan mode before edits: Claude Code, Jules, Replit, Factory (AIC§2.1, 2.10) | Figma Dev Mode "Compare changes" against earlier versions (MOK§2.1) | OpenSpec ADDED / MODIFIED / REMOVED deltas, hand-written (REQ§2.1). Linear Guided Reviews: core first, consequences second, glue last (REQ§2.2). Spec Kit `analyze` is a read-only consistency report (REQ§2.1) | GitHub Viewed with progress; Reviewable keeps marks per revision (REV§2). Graphite orders by dependency, not alphabet (REV§2). CodeRabbit walkthrough is AI-authored (REV§2). Alphabetical order is judged optimal by 10.2% of 1,355 surveyed developers (REV§2) | VS Code Keep / Undo per edit or for all (DEV§2.3). Warp blocks bind actions to one unit of work (DEV§2.9) |
| **Semantic diff** | Only Devin, and it is an LLM judgement with no deterministic check (AIC§0 #1) | Chromatic, Percy, Applitools compare pictures; match levels declare what counts as a difference (REV§3) | OpenSpec deltas are semantic but authored by hand; validation and apply disagreed in reported issues (REQ§2.1) | SemanticDiff, difftastic, GumTree parse ASTs and hide non-semantic edits; SemanticDiff states it cannot guarantee hidden edits are irrelevant (REV§7) | — |
| **Approval UX** | 93% of Claude Code prompts approved (V2); auto mode uses a second model. Codex modes `on-request`, `never`, `granular`, `auto_review` (AIC§2.3). Factory: risk class versus autonomy level, block wins (AIC§2.10). Copilot agent returns a PR under branch protection (AIC§2.5) | Figma "Ready for dev" is a designer-set flag (MOK§2.1). Sketch MCP off by default with per-call confirmation, but `run_code` writes anything (MOK§2.3). Penpot MCP: advice to describe before applying, no mechanism (MOK§2.2). Claude Design "Published" toggle is a human gate (ADC§2.1) | Linear: agent cannot be primary assignee (V5). Spec Kit checklists are reviewer-owned and gate `implement` (REQ§2.1). Kiro phase gates (REQ§2.1) | Copilot review can submit approving reviews, preview, off by default (REV§0). Gerrit submit requirements: 6 statuses incl. NOT_APPLICABLE, OVERRIDDEN (REV§2). GitHub counts a skipped required check as success (REV§4). Chromatic: Pending until a checklist completes (REV§3) | Stripe FocusView blocks the page for a consequential task; ContextView is a side drawer (DEV§2.8). Zed tool permissions allowed, denied, confirmed (DEV§2.4) |
| **Undo and checkpoints** | Claude Code rewind lists what it does not track (Bash, most subagent edits, external edits). Bolt restore leaves database state. Windsurf: "Reverts are currently irreversible" (AIC§2.1, 2.9, 2.4) | — | OpenSpec archive moves an accepted delta into truth; reported CRLF and validation defects (REQ§2.1) | — | VS Code checkpoints before each request (DEV§2.3) |
| **Parallel agent status** | Claude Code agent view; Cursor Agents Window, vendor admits engineers still micromanage; Codex worktree per thread (AIC§2.1, 2.2; ADC§2.12) | Stitch agent manager (ADC§2.4) | Kiro task waves (REQ§2.1) | Gerrit attention set: whose turn it is (REV§2) | — |

### 2.C Assurance and navigation

| Capability | AI coding and vibe-coding | Diagram, design, mockup | Requirements and spec | Review and assurance | Craft benchmarks |
|---|---|---|---|---|---|
| **Requirements traceability** | Kiro links properties to requirements and tasks; "Sync Files" regenerates tasks; docs list "don't treat specs as static" (REQ§2.1) | Figma Code Connect maps design component to code component as data (MOK§2.1). Storybook CSF: a story is one named state (MOK§2.9) | Jama Trace View: columns by level, counts per level, "!" where a required link is missing; suspect links cleared by hand. DOORS Next: link validity triggered only by flagged attributes. Azure DevOps: requirements with no linked test (REQ§2.2) | Nx affected: over-approximates on purpose; Backstage typed relations with inverses (REV§8) | — |
| **Proof and evidence display** | Kiro: property tests are "evidence of correctness, not a proof"; pass or fail, no tri-state (AIC§2.6). No surveyed AI coding product shows proofs, model checks or mutation score (AIC§0 #5) | Storybook coverage widget lists untested states (MOK§2.9) | Storybook: status glyph per row, click count to filter (REQ§2.3) | Dafny: quiet green bar for verified, stale and in-progress are distinct. GNATprove: Justified separate from Proved. Lean: `#print axioms`. Stryker: 8 mutant states, two denominators. Quint and Alloy print the bound. Codecov: `if_not_found` defaults to success. SonarQube: 2 states (REV§4, REV§6) | — |
| **Counterexample and trace replay** | Kiro shrinks a failing property to a minimal input (REQ§2.1) | Storybook Interactions: pause, resume, rewind, step, failure pinned to the step (MOK§2.9) | — | TLA+ Toolbox: one row per state, changed variables highlighted, expression column, double-click jumps to the action. Quint prints seed and says simulator counterexamples are not minimal. Hypothesis shrinks and stores for replay (REV§5) | — |
| **Command palette** | — | Figma Cmd/Ctrl+K adapts to permissions (MOK§2.1). Axure `/` Quick Actions (MOK§2.7). Eraser `/` or Ctrl+J opens the AI (DGM§2.11) | Azure DevOps documents "user stories with no linked test" as a query (REQ§2.2) | — | Linear: prefixes, acts on selection, `?` searchable sheet. Superhuman: shows the shortcut in results. VS Code: prefixes. JetBrains: synonyms. Zed: key binding beside each command. Obsidian: pinned commands. Raycast: accessories and detail pane (DEV§2.1-2.11) |

### 2.D Repeated observations across the matrix

1. Every AI coding product surveyed reviews at line or hunk level; the one that groups by intent uses a model (AIC§0 #1).
2. Honest bounds and separate "assumed" columns exist in formal tools (GNATprove, Quint, Alloy, Lean) but not in the AI coding tools surveyed (AIC§0 #5; REV§9).
3. "No result" is mapped to success in two mainstream CI paths (REV§0 #1). This is the failure the UNKNOWN invariant exists to prevent.
4. Approval friction is answered by removing the human (classifier, `auto_review`, Zed "allowed", Copilot approving reviews) in four products; the invariant runs the other way (AIC§2.1, 2.3; DEV§2.4; REV§0 #6).
5. Design tools that expose MCP write access rely on advice or per-call consent (Penpot, Sketch) or grant broad writes (`use_figma`, `run_code`) (MOK§2.1-2.3).
6. Undo is stated with a coverage boundary in three products and stated as irreversible in one (AIC§2.1, 2.9, 2.4).

## 3. What to steal, what to avoid

### 3.1 Steal (with the EIJA form)

| # | Pattern | Origin | Source | EIJA form |
|---|---|---|---|---|
| S1 | Operation requests validated server-side; picture regenerated from the accepted model | GLSP, Sirius Web | DGM§2.9, DGM§3.1 | Drag and connect emit typed transactions; the kernel accepts or refuses and the refusal reason shows at the drop target |
| S2 | Position stored apart from meaning | Structurizr; draw.io failure case | DGM§2.8, 2.1 | Layout file keyed by stable element id; new elements only are auto-placed; one explicit undoable Tidy |
| S3 | Stable id on every rendered thing | Lovable Visual Edits | ADC§2.7 | Tree row, diagram box, journey step and evidence row share the model id used by selection, comment and ask-AI |
| S4 | Two labelled edit lanes | Lovable, v0 | ADC§2.6-2.7 | Direct edits through the kernel (no provider); a prompt lane marked as a provider call |
| S5 | Tree as spine with per-row status glyph and footer roll-up | Storybook, Jama Trace View, Notion filter | REQ§2.3, 2.2 | Language tree, APG keyboard model, depth budget 4, three-mode filter, click a count to filter |
| S6 | Trace lane with an explicit gap mark | Jama Trace View | REQ§2.2 | Requirement, state, journey, test, persona, evidence; a missing required link is drawn as a gap glyph |
| S7 | Suspect from meaning-bearing fields only, shown with the causing diff | DOORS Next, Jama Compare Versions | REQ§2.2 | Kernel hashes meaning-bearing fields; cleared only by a logged owner decision; no Clear All |
| S8 | Chaptered review: core, consequences, glue | Linear Guided Reviews | REQ§2.2 | Chapters generated from the model diff, labelled ADDED / MODIFIED / REMOVED (OpenSpec vocabulary) per element |
| S9 | Agent as delegate, human as assignee | Linear | V5 | Attention set shows kernel running, owner deciding, AI proposing; AI never occupies an approving slot |
| S10 | Bound inside every verdict; assumed and not-covered slots | Quint, Alloy, GNATprove, Lean | REV§5, REV§6, REV§9 | Four-slot coverage row: claim, covered, assumed, NOT covered; last slot never empty |
| S11 | Quiet success, loud unknown; stale and in-progress distinct | Dafny | REV§6 | PASS is the least conspicuous mark; UNKNOWN, CONFLICT, STALE visible without scrolling |
| S12 | Counterexample as rows of changed variables with a jump to the action | TLA+ Toolbox, Quint, Storybook Interactions | REV§5, MOK§2.9 | Table generated from the model; minimal or not-minimised label; replay token; step, rewind, pause |
| S13 | Two review modes: side drawer and blocking decision surface | Stripe ContextView / FocusView | DEV§2.8 | Drawer shows a proposal beside affected models; the blocking surface shows the exact revision and every UNKNOWN before the action is enabled |
| S14 | One palette acting on the selection, showing shortcuts, prefixes, synonyms, pinned | Linear, Superhuman, JetBrains, Obsidian | DEV§2.1, 2.10, 2.5, 2.11 | Every command shows enabled, blocked-with-reason or AI-proposal; contains no approve or apply |
| S15 | Grounding rule as a checker | v0, Figma Make kits | ADC§2.6, 2.3 | A proposal may cite only entities and tokens resolvable in the model or token files; anything else is an explicit new item |
| S16 | Undo that states what it does not restore | Claude Code, Bolt | AIC§2.1, 2.9 | Each undo control names external state, data and other models it leaves unchanged |
| S17 | Deterministic autonomy policy | Factory | AIC§2.10 | Risk class versus level as kernel policy, block wins; never a model judgement |
| S18 | Role-named token steps generated from few inputs | Linear, Geist, Radix | DEV§2.1, 2.7; VIS§2.5 | DTCG 2025.10 tokens (OKLCH plus hex fallback); tokens.css regenerated and diffed in a test |
| S19 | Read-only consistency checker separate from generator | Spec Kit `analyze` | REQ§2.1 | Kernel checks stay read-only relative to what they judge |
| S20 | Concept-to-code mapping as checked data | Figma Code Connect | MOK§2.1 | Mapping table with last check result and drift |

### 3.2 Avoid

| # | Pattern | Where it appears | Source | Why avoided |
|---|---|---|---|---|
| A1 | A model that approves: classifier auto mode, `auto_review`, "allowed" tool mode, approving Copilot review | Claude Code, Codex, Zed, Copilot | V2, AIC§2.3, DEV§2.4, REV§0 | Violates providers-never-approve. Vendor data: 93% of prompts approved; 17% false negative on n=52 overeager actions |
| A2 | LLM-authored grouping of a change presented as fact | Devin Review, CodeRabbit | AIC§2.7, REV§2 | Not checkable; EIJA groups from the model diff and labels any AI text "AI-estimated" |
| A3 | Skipped or missing evidence counted as success | GitHub, Codecov | REV§4 | Hides UNKNOWN |
| A4 | Two-state gates and one merged coverage percentage | SonarQube, coverage badges | REV§4, REV§6 | Cannot express UNKNOWN, NOT_RUN or the bound |
| A5 | Irreversible or uncovered revert | Windsurf, Bolt (database) | AIC§2.4, 2.9 | Undo must state its coverage |
| A6 | Agent write tools on a canvas | Figma `use_figma`, Sketch `run_code`, Penpot MCP write | MOK§2.1-2.3 | Agents propose only |
| A7 | Silent last-writer-wins on invariant-bearing properties; implicit set-override order | Figma multiplayer, Penpot token sets | MOK§2.1, 2.2 | Base-version transactions and a displayed order instead (MOK§5 #10 is an inference, not a vendor finding) |
| A8 | Free-form prose spec triplet as the review surface for small changes | Kiro, Spec Kit | REQ§0 #6, REQ§2.1 | One reported case turned a small bug into 4 stories and 16 criteria (n=1); use a size-proportional path |
| A9 | Regeneration that discards layout; locked generated layout | draw.io Mermaid, Lucid | DGM§2.1, 2.3 | Persist layout by id |
| A10 | Iframe embedding of provider markup | tldraw make-real | ADC§2.10 | Blocked by CSP and ADR-013 |
| A11 | Colour as the only carrier of meaning | Devin Review severity, many status UIs | AIC§2.7, REV§9 | WCAG 1.4.1; deutan separation of proved/unknown is 0.025 dE_OK (VIS§2.4) |
| A12 | More than 2 disclosure levels; 31 text styles; 6,000-shape libraries | Claude Code Desktop (3 modes), Geist, Miro | AIC§2.1, DEV§2.7, DGM§2.3 | V7; type budget of 6 sizes |
| A13 | Per-row status icons everywhere as default noise | DOORS Next (admins can switch off "to reduce clutter") | REQ§2.2 | One glyph per row, detail on selection |
| A14 | Hand-cleared suspect flags, Clear All | Jama, DOORS | REQ§2.2 | Trust erodes; no audit trail was described on the pages read |

## 4. The unmet need EIJA can own

**Statement.** An engineer who accepts AI-generated change to a business-rule model has no surveyed tool that answers, in one place and without trusting a model: what did this change mean, what else does it touch, what is proved and what is UNKNOWN, and am I the one who decides.

**Why the gap is plausible (evidence).**

| Component | Best existing precedent | What it lacks for EIJA's job |
|---|---|---|
| Review unit is a semantic operation | Linear chapters, OpenSpec deltas, SemanticDiff | Deltas hand-written or inferred from code; SemanticDiff cannot guarantee hidden edits are irrelevant (REV§7) |
| Ripple across several models | Nx affected, Backstage relations, Ilograph perspectives | Code and catalogue graphs, not states, journeys, personas, requirements of one executable model (REV§8, DGM§2.10) |
| Evidence with bound and UNKNOWN | Dafny, GNATprove, Quint, Stryker | Verification IDEs for proof authors, not review surfaces for agent-authored change (REV§6) |
| Human-only decision | Linear assignee, Spec Kit checklists | Not tied to exact evidence and revision |
| Agent output | Kiro properties, Codex review pane | Pass or fail without UNKNOWN; line-level (AIC§2.6, 2.3) |

**Why users might need it.** Perceived and measured effects of AI assistance diverge (METR 2025, Perry et al.); heavy delegation lowered a comprehension quiz score in one small RCT (n=52); in the 2025 Stack Overflow survey 66% chose "almost right, but not quite" and 45.2% said debugging AI code takes longer; only 3.1% highly trust accuracy (AIC§2.12, §3; self-report, medium). Understanding the change is the main review challenge; 14% of sampled review comments concerned defects (REV§2, Bacchelli and Bird).

**What this does not show.** No study shows that semantic review, ripple views or a visible UNKNOWN improve decisions (AIC§5, REV§12). The gap may exist because the feature has little value. The falsifiable test is the within-subject study in section 8: seeded-defect detection, UNKNOWN misread as PASS (target zero), time, calibration.

**Positioning (one sentence for the README, after the study).** EIJA Studio is where an owner reviews AI-generated change to an executable model by what it means, what it touches and what is proved, and decides.

## 5. Constraints from the repo that shape every option

| Constraint | Source | Design consequence |
|---|---|---|
| No build-time framework; untrusted text only through DOM text nodes | ADR-013 in `docs/adr/0000-poc-decision-log.md` | Tree, lane, palette, diagrams are plain DOM and SVG built with `createElementNS`; React SDKs (tldraw, Excalidraw, Radix) are out (DGM§2.12, DEV§3) |
| CSP `default-src 'none'`, `style-src 'self'`, no `font-src`, `/assets` allows two files, `no-store` everywhere | R2 | Fonts, icon files and extra scripts need an amended CSP and allowlist; `element.style.prop` is allowed, `setAttribute("style")` is not; SVG presentation attributes and same-origin workers are untested (DGM§2.12) |
| Frozen supported vocabulary; today two typed edits (enable recommendation; registrar rejection source) | ADR-003; README; R1 | Drag on a state diagram can only emit operations the kernel supports; every other drop is a visible refusal with a reason. The design must not imply general model editing |
| Single local owner, synthetic actors, loopback only | ADR-011 | Roles below are roles one person can hold; no multi-user claims. Multiplayer patterns from Figma are out of scope for v1 |
| AI proposal-only; provider egress needs flag and per-request consent | ADR-004; `AGENTS.md` | The prompt lane must be marked as egress; palette holds no approve or apply |
| Layout is a distinct subject dimension: layout change keeps domain evidence but invalidates exact-presentation approval | ADR-008; baseline "Layout-only change" text | Tidy and drag-to-reposition must show that they renew the presentation approval |
| Human understanding is UNKNOWN by construction; `field-use` blocked | ADR-010; README | The Studio must keep this visible; the baseline already does (a box reading "Human comprehension: UNKNOWN"). Keep it |

Baseline strengths worth keeping (R1): the UNKNOWN box, "Authorise only the exact revision you reviewed", aria-live status region, skip link, synthetic-domain disclosure.

## 6. Contradictions between sources and how each was resolved

| # | Contradiction | Sources | Resolution | Status |
|---|---|---|---|---|
| C1 | A "400 ms Doherty threshold" is cited as a finding by three dossiers; the transcription of Doherty and Thadani (1982) read by LAW contains no 400 ms figure | DGM§3.3, MOK§3, ADC§3 vs LAW§2.6 | Do not cite 400 ms as a finding. Use 0.1 s, 1 s, 10 s (V1). Doherty and Thadani is used only for "fast feedback has economic value" (3.0 s to 0.3 s: 180 to 371 transactions per hour in their data, blog transcription with one arithmetic error) | Resolved |
| C2 | Status vocabularies differ: REV proposes 7 (PASS, PARTIAL, NOT_RUN, UNKNOWN, CONFLICT, BLOCKED, STALE); VIS 5 visual roles; REQ 4 glyphs; AIC 3; DEV 4 with RUNNING. The kernel code returns PASS, FAIL, CONFLICT, STALE, UNKNOWN (R3), so REV's list omits FAIL and PARTIAL does not exist in the kernel | REV§11 #1, VIS§2.4, REQ§5 #2, AIC§4 #3, DEV§5 #4, R3 | Two layers. **Evidence status** (kernel words, closed): PASS, FAIL, CONFLICT, STALE, UNKNOWN, plus NOT_RUN (lane rule in `AGENTS.md`). **Eligibility** (not evidence): BLOCKED, ELIGIBLE_FOR_LOCAL_REVIEW. **Job state** (UI only, transient): RUNNING. **Visual roles** map onto these: proved = PASS, refuted = FAIL, unknown = UNKNOWN or NOT_RUN, stale = STALE, plus AI-proposed (provenance, not evidence). CONFLICT needs its own glyph. PARTIAL is not adopted until a kernel ADR defines it | Resolved for design; kernel ADR needed for PARTIAL |
| C3 | Baseline counts differ: SLP reports 14 font sizes and 397 words; VIS and DEV report 13 and about 404 | SLP§3.3, VIS§2.7, DEV§1 | I re-measured with a script on `app.css` and `index.html`: 13 distinct `font-size` values (12 fixed plus one `clamp()`), 7 weights (450 to 750), 19 hex colours, 6 distinct non-zero border-radius values, 0 gradients, 0 shadows, 0 blur, 0 `prefers-*` rules, 10 `eyebrow`, 6 `.panel`, 3 `<pre>`, 404 words in `index.html` after removing scripts and `<pre>`. SLP's 14 and 397 are not reproduced. Static count; dynamic text from `app.js` is not included | Resolved (measured) |
| C4 | Hick's law is applied three ways: log2(n+1) ratios (AIC), 1.9x for 64 versus 8 commands (MOK), and "log for practised users, linear for novices, not for search" (LAW) | AIC§3, MOK§3, LAW§2.3 | Follow LAW: Hick-Hyman only for stable-position command sets and sibling order; novice search is linear (Cockburn et al.: 0.30 + 0.08 n s); never for typed search. Quote earlier ratios as lower bounds only | Resolved |
| C5 | Palette speed: MOK predicts about 40% saving; DEV predicts the palette does not beat a visible control (2.75 s versus 2.55 s); DGM 4.35 s versus 6.55 s for adding a node | MOK§3, DEV§2.12, DGM§4 | Different comparators and typed-length assumptions. Claim only: a palette beats hidden or deep targets (MOK's 3.2 s versus 5.4 s bands of plus or minus 21% do not overlap) and does not beat a visible control. All are KLM PREDICTIONs for expert, error-free users who know the name (LAW§2.4) | Resolved with limits |
| C6 | Disclosure depth: Claude Code Desktop offers three transcript modes; NN/g says beyond 2 levels typically hurts | AIC§2.1 vs V7 | At most 2 levels; a third needs an HCI-ADR. NN/g is a 2006 practitioner rule (REQ§4 rates it medium) | Resolved |
| C7 | Approval automation is common in products (classifier, `auto_review`, "allowed", approving reviews) and forbidden by the invariant | AIC§2.1, 2.3; DEV§2.4; REV§0 | The invariant wins. Supporting data: 93% approval (V2) suggests reflex approval; classifier false-negative 17% on n=52 (vendor-reported, small n). A secondary claim of 97% was not confirmed and is not used (AIC§5) | Resolved |
| C8 | Linear's design lead advises not leaning on data; the project rule is evidence first | DEV§2.1 vs task rules | Take Linear's mechanisms as hypotheses; do not adopt the stance | Resolved |
| C9 | Layout policy: Ilograph forbids manual layout; Structurizr auto-places then allows manual; draw.io loses layout on regeneration | DGM§2.1, 2.8, 2.10 | Keep layout as secondary notation keyed by id (Green and Petre, via LAW§2.7 and DGM§3.2) | Resolved |
| C10 | Contrast: WCAG 2.2 ratio accepts text at 4.5:1 on the dark surface, which scores about Lc 35 in APCA versus guidance of Lc 60 to 75; APCA is unratified with a restricted reference-code licence | VIS§2.2, 2.4 | Gate on WCAG 2.2; report APCA Lc as advisory; vendor no APCA code; any lift of dark-mode lightness needs an HCI-ADR, a user test and legal review | Open (needs study) |
| C11 | Spec workflows: Kiro and Spec Kit gate phases; OpenSpec calls artifacts "enablers, not gates"; one practitioner found Kiro heavy for a small bug (n=1); Spec Kit has 139,274 stars | REQ§2.1 | Size-proportional path (one line and one criterion versus full chain). Both directions rest on weak evidence; measure in the study | Open |
| C12 | Working memory: 7 plus or minus 2 (Miller), 3 to 5 chunks (Cowan), and a folk rule of 7 menu items | LAW§2.5 | Budget 4 chunks held in mind with a stated 3 to 5 range; the limit does not cap visible item counts | Resolved |
| C13 | METR 2025: 19% slower (n=16); METR 2026: -18% (n=10) and -4% (n=47), intervals include zero and the authors call the signal unreliable; DORA reports over 80% self-reported productivity gain | AIC§2.12 | Make no direction claim. Design for calibrated trust; measure our own decision quality | Open |
| C14 | DGM says the DTCG Color module page says "do not implement"; VIS and MOK say 2025.10 is stable and supports `oklch` | DGM§4, DGM§6 vs VIS§2.11, MOK§4 | I opened `/tr/2025.10/color/` (V4) and `/tr/2025.10/format/` (V3): both are Final Community Group Reports of 28 October 2025, "intended for implementation", not W3C Standards. DGM cited the `/tr/drafts/color/` page. Pin `2025.10`; ignore `/drafts/` | Resolved (verified) |
| C15 | CSP behaviour is uncertain: MDN contradicts itself on `style.cssText`; SVG presentation attributes, same-origin workers and Lit adoptedStyleSheets are untested | DEV§1, DGM§2.12, DEV§3 | No ADR may rely on these until a CSP smoke test passes in the real Studio; run one Chromium only | Open (spike) |
| C16 | "Generic slate plus Inter" is a tell in the rubric; Linear uses Inter; VIS measured Inter as strong (tnum, opsz, zero) but 88 KB Latin | SLP§0 #2, VIS§2.6 | Do not ban by name; require a recorded type rationale; shortlist Public Sans, Atkinson Hyperlegible Next, Geist for a bake-off | Resolved |
| C17 | Atkinson Hyperlegible licence: vendor page points to an EULA, `google/fonts` carries OFL | VIS§2.6 | Reconcile before adoption | Open |
| C18 | Aesthetic research shows low complexity and high prototypicality rate best (Tuch et al. 2012), which favours generic layouts, while the rubric bans generic layouts | SLP§0 #4 | Our case against generic layout is scanning cost, honest evidence display and differentiation, not that generic looks worse to everyone. Keep the first screen calm and never trade evidence for appearance | Resolved |

## 7. What we still do not know

| Gap | Effect | Owner of the fix |
|---|---|---|
| No interview or observation of real users of this Studio; personas are literature-derived | Personas are hypotheses (`docs/hci/personas-and-jtbd.md`) | Study lane |
| No product was run by any dossier author | Interaction costs are model predictions from documentation | Prototype measurement |
| Study evidence for semantic review, ripple views, visible UNKNOWN, four-slot coverage row (H1) | Central claim untested | Study protocol in `docs/hci/design/` |
| Drag-and-drop UML editing has no headless OSS library found; elkjs is EPL-2.0 (GPL-3.0 secondary from 0.12.0) against an Apache-2.0 project | Build own SVG editor; licence review | Diagrams lane; `docs/oss/REGISTER.md` |
| Accessibility of canvas content to the slop-budget script (canvas is blind to DOM metrics) | Diagram needs a DOM or ARIA layer | Prototype |
| Fitts, KLM and Hick constants are population and device specific | Use a stated profile and bands | LAW§2.1 |
| Many WebFetch-derived numbers are `medium`; several 2026 arXiv papers were read at abstract level | Re-read on the source page before an ADR cites them | ADR author |

## 8. From synthesis to work

**Candidate HCI-ADR topics** (the integrator assigns numbers in 0057-0088; ordering follows the ranking in `PRINCIPLES.md`):

1. Status vocabulary, glyphs and the CONFLICT and STALE marks (C2). 2. Review unit: semantic transaction list and chapters. 3. Ripple lane and tiers (kernel-derived, heuristic, unknown). 4. Four-slot coverage row and the bound in every verdict. 5. Owner decision surface and rubber-stamp study arm. 6. Tree spine, depth budget, three-mode filter. 7. Drag as typed operation and refusal at drop target. 8. Layout persistence and Tidy. 9. Command palette contents and the no-approve rule. 10. Latency classes and job states. 11. Token source, DTCG pin, generation test. 12. Contrast gate (WCAG 2.2 gate, APCA advisory). 13. Type pair and font hosting (CSP amendment). 14. Asset allowlist and caching (server change). 15. Grounding checker for AI proposals. 16. Undo coverage labels. 17. Density and slop budget hooks (`data-eija-*`). 18. First-run onboarding path.

**Study (design only, nothing run).** Within-subject, baseline Studio versus proposed, engineers, excursion-workflow tasks: seeded-defect detection, UNKNOWN misread as PASS (target zero), time on task, calibration (confidence versus correctness), per-task SEQ, SUS and Raw TLX with intervals; include a keyboard-only cohort; a 12 or more participant floor follows REQ§6 and VIS§5; formative rounds of about 5 find problems but do not estimate prevalence (LAW§2.10). Add a first-impression arm at 50 ms and 500 ms (SLP§4.4). Watch for rubber-stamping: time from opening the decision surface to approval, and whether UNKNOWN items were opened.

## 9. Files and sources read for this synthesis

All ten dossiers in this folder; `README.md`; `AGENTS.md`; `docs/architecture/ARCHITECTURE.md`; `docs/adr/README.md`, `template.md`, `0000-poc-decision-log.md`; `docs/oss/REGISTER.md`; baseline `index.html`, `app.css`, `app.js` (line counts and the counts in C3); `src/eija_studio/interfaces/http.py` (CSP); `src/eija_studio/domain/evidence.py` (status words). Pages V1 to V7 were opened on 2026-09-29.
