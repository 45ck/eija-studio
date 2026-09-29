# Research dossier: mockup and prototyping tools

Lane: `lane/ux-research`. Access date for every URL below: 2026-09-29. Status: research input, not a decision. Decisions go in HCI-ADRs (0057-0088).

Question: which interaction patterns from Figma, Penpot, Sketch, Framer, Balsamiq, Axure RP, ProtoPie, Uizard, Storybook (and Adobe XD's status) transfer to a model editor whose "shapes" are domain concepts with invariants, under the EIJA invariants (AI proposes, kernel checks, owner decides; UNKNOWN stays visible; agents never approve or apply)?

## 0. Decisions first

| # | Recommendation | Verdict | Main evidence |
|---|---|---|---|
| 1 | Inspector shows invariants and evidence status first, attributes second; selection-driven, at most two disclosure levels | adapt | Figma UI3 puts component controls above attributes; NN/g two-level limit |
| 2 | Command palette (Ctrl/Cmd+K) as the universal entry point; each command shows kernel-derived enabled/disabled state and an "AI proposes" marker | adapt | Figma actions menu, Axure Quick Actions; KLM PREDICTION in section 3 |
| 3 | Tree (layers) panel is a projection of the executable model; drag-drop emits a typed transaction that the kernel accepts or rejects, never a raw reparent | adapt | Figma doc is a tree and its server rejects cycles |
| 4 | Explicit, checked mapping model concept to code symbol, with drift shown | adopt | Figma Code Connect, Storybook CSF |
| 5 | Every state of a concept is a named, declarative "story"; counterexample and journey traces replay with step, rewind, pause | adopt | Storybook Interactions panel; Framer variants; ProtoPie scenes |
| 6 | Agent write access through MCP only as proposals; no direct canvas writes | avoid (as shipped by others) | Figma `use_figma`, Penpot MCP write ops, Sketch `run_code` |
| 7 | Tokens in DTCG 2025.10 with `colorSpace` objects; no implicit override order for domain rules | adopt / avoid | designtokens.org; Penpot set cascade |
| 8 | Proposed (unapproved) elements render in a visibly provisional style, as Balsamiq does for "not final" | adapt | Balsamiq rationale |
| 9 | Comments anchor to model elements and to a change, and never carry approval | adapt | Figma comment mode, Axure Cloud |
| 10 | Multiplayer: no silent last-writer-wins on invariant-bearing properties; conflicts surface as a diff against a base version | avoid LWW | Figma multiplayer write-up |

## 1. Scope and method

- Tools: WebSearch (US-only) then WebFetch. WebFetch returns a model-written summary of the page, not raw text. Quotes below are therefore limited to a few words and every number is rated `medium` unless the page text made it unambiguous.
- Queries (about 30): per product official-docs queries (Figma Dev Mode, variables, auto layout, prototyping, comments, actions menu, MCP, Code Connect, UI3; Penpot tokens, MCP, layers; Sketch changelog and MCP; ProtoPie triggers/responses; Framer components and homepage; Balsamiq rationale and desktop sunset; Axure RP 11; Uizard AI; Storybook testing and CSF; Adobe XD maintenance mode) plus law sources (Fitts, Hick, KLM, Nielsen response times, Doherty, progressive disclosure) and DTCG status.
- Not accessible: `helpx.adobe.com` (HTTP 403, twice); Figma help URLs for keyboard shortcuts and quick actions returned the wrong article, and the components and one prototyping URL returned 404 (so Figma components and variants are covered only via Schema 2025 and UI3 sources); Axure quick-actions doc 404. Where a first-party page was not opened the claim is marked UNVERIFIED in section 5.
- Web content was treated as data. No code from any page was run. No screenshots or assets were copied.
- Repo context read: `AGENTS.md`, `docs/adr/0000-poc-decision-log.md` (ADR-013), CSP in `src/eija_studio/interfaces/http.py` (`default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:`). Consequence: no CDN fonts, no inline scripts or styles, no framework build. Every pattern below must be implementable in plain DOM with untrusted text as text nodes.

### URLs opened (all 2026-09-29)

Figma: help.figma.com/hc/en-us/articles/{15023124644247 (Dev Mode), 15339657135383 (variables), 360040451373 (auto layout), 23570416033943 (actions menu), 360040314193 (prototyping), 15253220891799 (conditionals), 360039825314 (comments), 360039832014 (design panel), 15343816063383 (modes), 35794667554839 (Schema 2025)}; figma.com/blog/how-figmas-multiplayer-technology-works/; figma.com/blog/behind-our-redesign-ui3/; developers.figma.com/docs/figma-mcp-server/tools-and-prompts/; developers.figma.com/docs/code-connect/.
Penpot: github.com/penpot/penpot; help.penpot.app/user-guide/, /user-guide/design-systems/design-tokens/, /user-guide/designing/layers/, /mcp/.
Others: sketch.com/changelog/mac/, sketch.com/docs/mcp-server/; protopie.io/learn/docs/interactions-triggers, /interactions-responses; framer.com/, framer.com/academy/lessons/framer-animations-component-interactions; balsamiq.com/, balsamiq.com/learn/the-future-of-balsamiq-for-desktop/; axure.com/, axure.com/upgrade-to-11, docs.axure.com/axure-rp/reference/environment/; support.uizard.io/en/collections/7738636-ai-features; storybook.js.org/docs/{writing-tests, api/csf, writing-tests/interaction-testing}; community.adobe.com/questions-525/xd-is-in-maintenance-mode-does-that-mean-adobe-is-discontinuing-the-app-1545659.
Standards and laws: designtokens.org/, designtokens.org/tr/2025.10/format/; nngroup.com/articles/response-times-3-important-limits/, /progressive-disclosure/; lawsofux.com/doherty-threshold/; en.wikipedia.org/wiki/{Fitts's_law, Hick's_law, Keystroke-level_model}.

## 2. Products and topics

### 2.1 Figma (Design, Dev Mode, Make)

Today: the dominant collaborative design tool; Dev Mode is a separate inspect-and-handoff mode; an official MCP server exposes design context to coding agents and, now, write tools.

| Pattern | Why it works (law/principle) | Source |
|---|---|---|
| Properties panel is contextual: no selection shows file-level styles and variables; a selection shows only that layer's controls; view-only users get a reduced panel | Progressive disclosure: novices see few options, experts avoid scanning; NN/g caps useful depth at two levels | help.figma.com/.../360039832014; nngroup.com/articles/progressive-disclosure/ |
| UI3 ordering decisions: component controls placed above colour and size; width, height and auto layout merged; X/Y kept above W/H because testing showed inversion "disrupted muscle memory"; condensed alignment grid reverted for the same reason | Stable spatial layout supports expert routine performance (KLM presumes routine expert execution); ordering by task frequency (Hick: fewer visible choices, faster choice) | figma.com/blog/behind-our-redesign-ui3/ |
| Toggleable property labels | Serves recognition for novices without costing experts space or time (progressive disclosure) | same; help.figma.com/.../360039832014 |
| Auto layout as three primitives: direction, gap, padding, plus hug/fill/fixed sizing; add with Shift+A, remove with Alt+Shift+A | Few orthogonal controls with direct-manipulation equivalents lower mental preparation (KLM M) | help.figma.com/.../360040451373 |
| Layers panel: nested tree of the document; drag to reparent or reorder | Direct manipulation of the structure the user thinks in; the document is "a tree of objects", and the server rejects reparenting that would create a cycle | figma.com/blog/how-figmas-multiplayer-technology-works/ |
| Actions menu: Ctrl/Cmd+K opens a search over AI tools, productivity actions, assets and plugins; content adapts to permissions | Recognition plus keyboard path avoids menu traversal (KLM P and B operators removed); large command sets stay usable because search replaces browsing (Hick applies to browsing, not to typed search) | help.figma.com/.../23570416033943 |
| Comment mode (key C): pins on canvas, mentions, resolve; canvas is not editable in comment mode | Mode separation prevents accidental edits while reviewing (error prevention); comments need only view access | help.figma.com/.../360039825314 |
| Dev Mode: "Compare changes" against previous versions and against the main component; "Ready for dev" status; Focus view shows one ready design at a time; annotations | Diff at the point of decision reduces recall load; a status marks what needs attention | help.figma.com/.../15023124644247 |
| Code Connect: maps a design component to the real code component with `.figma.ts` template files or a UI with GitHub integration; mapping is served to Dev Mode and to MCP | Removes guesswork between two representations; the mapping is data, so it can be checked | developers.figma.com/docs/code-connect/ |
| Variables: collections, modes, aliasing, scoping; Professional up to 10 and Organization up to 20 modes per collection | Scoping limits the choices offered per property (Hick) | help.figma.com/.../15339657135383; .../35794667554839 |
| Prototype logic: trigger plus action; variables and if/else conditionals; actions run top to bottom so order changes outcomes; invalid conditionals outlined in red | Immediate visible error at the point of authoring (feedback under 0.1-1 s, section 3); the order dependence is a hidden-state hazard | help.figma.com/.../15253220891799 |
| Multiplayer: client/server, last-writer-wins per property, tree with fractional indexing, offline edits reapplied on reconnect | Simple and fast; conflicts are resolved silently at property granularity | figma.com/blog/how-figmas-multiplayer-technology-works/ |
| MCP server: read tools (`get_design_context`, `get_variable_defs`, `get_code_connect_map`) and write tools (`use_figma`, `generate_figma_design`) | Gives agents structured context instead of screenshots | developers.figma.com/docs/figma-mcp-server/tools-and-prompts/ |

Verdict for EIJA:
- Adopt: contextual inspector, property-label toggle, Code Connect-style explicit mapping, comment-mode separation, compare-changes at the decision point.
- Adapt: layers as the DDD tree; palette; "Ready for dev" (in EIJA readiness is computed by the kernel and decided by the owner, never a designer-set flag); variables and modes (modes become scenarios or personas, with the mode set shown in full).
- Avoid: agent write tools on the canvas; silent last-writer-wins; order-dependent action lists without an explicit sequence diagram.

### 2.2 Penpot (open source)

Today: MPL-2.0 open-source design platform, Clojure and ClojureScript, self-hostable, with flex and CSS grid layouts, components and variants, native design tokens, plugins and an MCP server. The GitHub page showed 60.5k stars (medium confidence, counts change daily).

| Pattern | Why it works | Source |
|---|---|---|
| Tokens in DTCG format: 13 token categories, sets, themes, aliases in braces, formulas (+ - * / % ^ and functions), JSON import and export | One open format lets kernel and tool share the same file; formulas are computed, not typed | help.penpot.app/user-guide/design-systems/design-tokens/ |
| Token sets cascade: for identical names the later set overrides the earlier | Familiar from CSS, but the override order is hidden state | same |
| Themes as multidimensional selections over sets, grouped into theme groups | Avoids a combinatorial explosion of named themes | same |
| Layers panel with boards, group and ungroup, lock and hide icons, deep select | Standard tree affordances; no search or filter was documented in the fetched page | help.penpot.app/user-guide/designing/layers/ |
| MCP server has read and write access; a browser plugin bridges the open file; the docs advise read-only first, asking the agent to describe intended changes before applying, and small reversible steps | Vendor itself recommends a describe-then-apply discipline; there is no approval mechanism, only user prompting | help.penpot.app/mcp/ |

Verdict: adopt DTCG and its theme grouping idea; adapt "describe before apply" into a enforced kernel-side dry run rather than advice; avoid ordered set-override for domain rules. Penpot is the only tool here with public source, but MPL-2.0 file-level copyleft needs a licence review before any code reuse (not assessed; see section 6).

### 2.3 Sketch

Today: macOS-native design tool; latest Mac release seen was 2026.3.1 (14 Sep 2026) with a built-in, opt-in local MCP server.

| Pattern | Why it works | Source |
|---|---|---|
| MCP server is off by default, local-only, operates on the open document; the host client can be set to ask before each tool call; write path is `run_code` over the full SketchAPI | Consent default is off (secure defaults); but `run_code` gives an agent arbitrary write power | sketch.com/docs/mcp-server/ |
| Colour variables extended (gradients, eyedropper); Display P3 in prototype player | Wide-gamut correctness needs colour-space-aware tokens, matching DTCG `colorSpace` | sketch.com/changelog/mac/ |

Verdict: adopt "off by default, per-call consent" for any agent bridge; avoid a generic `run_code` style tool. Confidence in the changelog details is medium (summarised page).

### 2.4 Framer

Today: site builder with a canvas-native design agent, CMS agent and code agent, hosting, analytics and A/B testing (framer.com homepage).

| Pattern | Why it works | Source |
|---|---|---|
| Component variants as named states; a transition connects two variants; layer names and structure must align across variants so the tool can interpolate | A declared state set with explicit transitions is a state machine in all but name; aligned structure makes diffs computable | framer.com/academy/lessons/framer-animations-component-interactions |
| Triggers (hover, press) map to variant switches | Small trigger vocabulary lowers choice cost (Hick) | same |
| Agents "generate and refine in place" | Fast, but the edit lands in the document without a review boundary | framer.com |

Verdict: adopt variants-as-states, and the naming-alignment rule as a kernel check (same state names across a concept and its journeys); avoid in-place agent edits.

### 2.5 ProtoPie

Today: sensor and logic-rich prototyping.

| Pattern | Why it works | Source |
|---|---|---|
| Trigger, Response, Object model; 30+ response types; trigger families: touch, conditional (Chain, Range, Start, Detect), mouse, key, input, sensor | A uniform three-part grammar makes each interaction inspectable as data | protopie.io/learn/docs/interactions-triggers; .../interactions-responses |
| Conditions with operators (>, >=, <, <=, =, !=); `Assign` sets variables; `Reset` clears state | Explicit, testable predicates; reset makes state initial-condition visible | protopie.io/learn/docs/interactions-responses |
| Variables scoped to all scenes or to one scene, shown by solid or outlined icon | Scope is encoded in a glyph, not colour alone | protopie.io/blog/quick-start-using-protopie-in-3-steps (search result only, UNVERIFIED as page; see section 5) |
| Send/Receive messages between scenes and devices | Decouples parts; also creates untyped coupling | protopie.io/learn/docs/interactions-responses |

Verdict: adapt the trigger, condition, response grammar for journey and state editors, but with typed guards and effects executed by the kernel, and with negative cases (what does NOT fire) shown. Avoid untyped message passing.

### 2.6 Balsamiq

Today: low-fidelity wireframing; the vendor is retiring the Desktop product (sales end 31 Dec 2026, support end 31 Dec 2027) in favour of Cloud, adds an AI prototype generator and an MCP server (balsamiq.com).

| Pattern | Why it works | Source |
|---|---|---|
| Deliberately low fidelity: "stop debating colors" and focus on structure | Fidelity sets what feedback is invited; low fidelity directs review to structure. This is vendor rationale, not measured evidence here | balsamiq.com/ |
| Real-time commenting alongside wireframes | Feedback lives where the object is | balsamiq.com/ |

Verdict: adapt for provisional state: AI-proposed elements and UNKNOWN evidence use a distinct, non-colour-only style (pattern plus label) so nobody mistakes them for accepted model. A user study is needed before claiming this improves review quality.

### 2.7 Axure RP

Today: Axure RP 11 (per the vendor site), conditions and variables, dynamic panels with multiple states, adaptive views, notes for specifications, developer inspect with automated redlines, publish to Axure Cloud. No AI features were found on the fetched pages.

| Pattern | Why it works | Source |
|---|---|---|
| Docked panes (Pages, Outline, Libraries, Components, inspector panes) that can float or dock to hot zones; toolbar fully customisable | Expert control over layout at the cost of setup time | docs.axure.com/axure-rp/reference/environment/ |
| Outline is a searchable and sortable list of every widget | Search over the tree replaces scrolling | same |
| Quick Actions on `/` to insert widgets, navigate pages and apply styles (RP 11) | Keyboard-first entry point | axure.com/upgrade-to-11 |
| Notes attached to widgets carry requirements and specifications | Requirement sits next to the object that realises it (traceability) | axure.com/ |
| Dynamic panel = one widget with several states, switched by events | Same state-set idea as Framer variants | search result on docs.axure.com (page not opened; UNVERIFIED as page) |

Verdict: adapt notes-on-objects as requirement links; avoid free-floating panes as default (setup cost with no kernel benefit).

### 2.8 Uizard

Today: AI-first mockup tool. Help centre lists Autodesigner, Theme Generator, Image Generator, Text Assistant, Screenshot Scanner, Wireframe Scanner and Design Review. Acquisition by Miro is UNVERIFIED (search result only).

Patterns: generate a whole multi-screen project from a prompt; convert screenshots to editable mockups. Why it is instructive: it shows the failure mode EIJA must avoid, a large unreviewed generated diff. Verdict: avoid whole-project generation; adapt "Design Review" as AI critique that only emits findings (propose-only), and screenshot-to-model as a proposal with a per-element diff. Source: support.uizard.io/en/collections/7738636-ai-features.

### 2.9 Storybook

Today: workshop for UI components; the closest tool in this set to executable specification.

| Pattern | Why it works | Source |
|---|---|---|
| A story is one named state of a component; "a declarative list of states" | Enumerated states are reviewable, testable and diffable | storybook.js.org/docs/api/csf |
| Play function simulates user steps and asserts; the Interactions panel offers pause, resume, rewind and step; failures are pinned to the step; `step` groups actions into collapsible groups | Replayable trace with a located failure is exactly what a counterexample viewer needs | storybook.js.org/docs/writing-tests/interaction-testing |
| Stories double as tests (Vitest addon, Playwright, a11y addon, visual tests, a coverage widget listing untested states) | One artefact, several checks; untested states are shown, not hidden | storybook.js.org/docs/writing-tests |

Verdict: adopt. Model concept states are stories; journey and counterexample traces use the step-through panel pattern; the coverage widget maps to "untested or UNKNOWN states listed".

### 2.10 Adobe XD

Status: in maintenance mode, no new features, no longer sold as a standalone app (multiple secondary sources, and an Adobe community thread that discusses "maintenance mode"). I could not open an Adobe first-party page (403), so the status and dates are UNVERIFIED against a first-party source. Do not build on any date. Verdict for EIJA: no patterns taken; treat as evidence that tool lock-in risk is real, which supports open formats (DTCG, JSON layouts).

## 3. Cross-cutting evidence and laws

| Law or principle | Use here | Validity limits |
|---|---|---|
| Fitts (Shannon form ID = log2(D/W + 1)) | Size and place drag handles, tree rows and palette targets | Breaks down when D and W both vary widely; 1-D model; edge targets act as infinite width; not for saccades (Wikipedia) |
| Hick-Hyman (T = b log2(n+1)) | Limits visible choices per level | Equal probability, practised users, ordered menus; typed search is not covered; `b` must be fitted (Wikipedia) |
| KLM (Card, Moran, Newell 1980) | Compare task flows | Expert, error-free, routine tasks, time only; RMS error about 21% (Wikipedia) |
| Nielsen response times (0.1, 1, 10 s) | Feedback for kernel checks | Guidelines from 1993 with rounded values (nngroup.com) |
| Doherty threshold (400 ms) | Target for palette and inspector updates | IBM 1982 mainframe context; treat as a design target only (lawsofux.com) |
| Progressive disclosure | Inspector and evidence panels | More than two levels typically hurts usability; staged disclosure fails when steps interdepend (nngroup.com) |

PREDICTION (KLM, expert who knows the command name, assumptions: K = 0.2 s, P = 1.1 s, B = 0.1 s, M = 1.35 s, H = 0.4 s per Wikipedia KLM table):

| Path | Operators | Predicted time |
|---|---|---|
| Palette: M, chord (2 K), 6 typed chars, Enter | 1.35 + 0.4 + 1.2 + 0.2 | about 3.2 s |
| Three-level menu with mouse: M, 3 x (P + B), then H back to keyboard | 1.35 + 3 x 1.2 + 0.4 | about 5.4 s |

Predicted saving about 2.2 s (about 40%) per command, with an error band of about 21% RMS. It says nothing about novices, discoverability or learning. The task-flow JSON (`design/tasks/`) should encode both paths so the executable model can recompute this with real layout geometry.

PREDICTION (Hick): a flat list of 64 commands versus 8 gives log2(65)/log2(9) = 6.02/3.17, about 1.9 times the choice time for browsing. Relative only; `b` is not known for our users. Search-first access sidesteps this, which is why the palette lists recents and context-relevant commands first.

## 4. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| DTCG Format Module 2025.10 is a Final Community Group Report dated 2025-10-28, "not a W3C Standard" | designtokens.org/tr/2025.10/format/ | high |
| DTCG colour is an object: `colorSpace`, `components`, optional `alpha`, optional `hex`; aliases use `{group.token}` or `$ref` JSON Pointer; groups can `$extends` | same | high |
| Figma variable modes per collection: Professional up to 10, Organization up to 20 | help.figma.com/.../35794667554839 | medium |
| Figma multiplayer: last-writer-wins per property; document is Map of object ID to Map of property to value; server rejects cycle-creating reparents | figma.com/blog/how-figmas-multiplayer-technology-works/ | high (first-party engineering post; age unknown) |
| Figma Dev Mode "Completed" status needs Organization or Enterprise; Ready for dev is on paid plans; Code Connect needs Dev or Full seat on Organization or Enterprise | help.figma.com/.../15023124644247; developers.figma.com/docs/code-connect/ | medium |
| Figma actions menu opens with Ctrl/Cmd+K; some AI tools in it labelled limited beta | help.figma.com/.../23570416033943 | medium |
| Figma prototype animation duration range 1 to 10,000 ms; Shift+E toggles Design and Prototype tabs | help.figma.com/.../360040314193 | medium |
| Penpot has 13 token categories; sets cascade by order | help.penpot.app/user-guide/design-systems/design-tokens/ | medium |
| Penpot repository: MPL-2.0, about 60.5k stars | github.com/penpot/penpot | medium |
| ProtoPie: 30+ response types; up to 5 fingers in multi-touch | protopie.io/learn/docs/interactions-responses; .../interactions-triggers | medium |
| Balsamiq Desktop: sales end 2026-12-31, support end 2027-12-31 | balsamiq.com/learn/the-future-of-balsamiq-for-desktop/ | high |
| Sketch Mac 2026.3.1 released 2026-09-14; MCP server local-only, off by default | sketch.com/changelog/mac/; sketch.com/docs/mcp-server/ | medium |
| Storybook Vitest addon turns stories into Vitest tests | storybook.js.org/docs/writing-tests | high |
| KLM times: K 0.2 s (average typist), P 1.1 s, H 0.4 s, M 1.35 s, B 0.1 s; prediction error about 21% RMS | en.wikipedia.org/wiki/Keystroke-level_model (secondary; original is Card, Moran, Newell, CACM 1980) | medium |
| Nielsen limits 0.1 s, 1 s, 10 s | nngroup.com/articles/response-times-3-important-limits/ | high |
| Doherty and Thadani, IBM Systems Journal 1982, 400 ms | lawsofux.com/doherty-threshold/ (secondary) | medium |
| Progressive disclosure: two levels typically fine, three or more confuse (NN/g, 2006) | nngroup.com/articles/progressive-disclosure/ | high |

## 5. Implications for EIJA

1. Inspector order for a selected concept: (a) kernel verdict and UNKNOWN count, (b) invariants, (c) attributes, (d) links (states, journeys, tests, personas, requirements). Follows Figma UI3's "controls before attributes" and NN/g's two-level cap. Study needed to confirm.
2. One palette on Ctrl/Cmd+K (Figma) with `/` as an alias for insert-and-navigate (Axure). Every entry carries a glyph and text for kernel-enabled, kernel-blocked with reason, or AI-proposal. Disabled commands stay listed with the reason, so nothing is silently hidden.
3. Tree panel is generated from the model. Drag-and-drop dispatches a typed transaction; the kernel accepts or refuses (Figma's cycle rejection is the precedent) and the refusal reason shows at the drop target. Picture and tree can never diverge because both are projections.
4. Ship a concept-to-code mapping table modelled on Code Connect: concept, code symbol, last check result, drift. Mapping is data, so the kernel checks it.
5. Represent each concept's states as Storybook-style stories, and render model-check counterexamples and journey traces in a step, rewind, pause panel that pins the failing step.
6. Agents: read-only context tools plus propose-only tools. Copy Sketch's "off by default, per-call consent"; do not copy Figma `use_figma` or Sketch `run_code`. Turn Penpot's "describe before applying" advice into a kernel dry run whose output is the semantic diff (the "compare changes" view).
7. Tokens: DTCG 2025.10 with `colorSpace`/`components`, no implicit set-override order for domain rules; any ordering is an explicit, displayed list.
8. Provisional style: AI-proposed and UNKNOWN items get a shape or pattern plus text label (Balsamiq's low-fidelity idea, ProtoPie's solid versus outlined scope icon), never colour alone.
9. Comments attach to model element IDs and change IDs; Figma-style comment mode separation (read-only while commenting) applies. A comment or "ready" flag is never an approval; approval is a separate owner action outside agent reach.
10. Multiplayer: do not adopt property-level last-writer-wins for invariant-bearing fields. Use base-version transactions and show conflicts as a diff. This is an inference from the kernel invariants, not from a vendor.
11. ADR-013 and the CSP constrain the implementation: plain DOM, self-hosted OFL fonts, no inline styles. Verify each pattern is achievable before writing an ADR.

## 6. Gaps and unverified items

- UNVERIFIED (first-party page not opened): Adobe XD maintenance-mode dates and wording; Uizard acquisition by Miro; ProtoPie variable-scope icon (search snippet only); Axure dynamic panel states (search snippet of docs.axure.com only); Figma multi-page keyboard shortcut list and exact quick-actions history (older Ctrl+/ appears in forum results, current help says Ctrl/Cmd+K).
- Not covered: Framer variables and CMS internals, Figma Make, Penpot multiplayer and comments, Sketch Inspector layout, ProtoPie Studio state features beyond scenes, Axure adaptive views geometry, and any published usability study of these tools.
- No user-benefit claim here is supported by a study. Section 3 predictions are models. Study protocol belongs in `docs/hci/design`.
- WebFetch summaries can paraphrase or omit; numbers rated `medium` should be re-read on the source page before an ADR cites them.
- MPL-2.0 (Penpot) and Apache-2.0 (EIJA) compatibility for any code reuse is not assessed; nothing was copied.
- Font and icon licences: none selected in this dossier; to be handled in the tokens and type dossier.
