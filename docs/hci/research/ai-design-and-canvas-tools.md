# Research dossier: AI design and canvas tools

Lane: `lane/ux-research`. Access date for every URL below: 2026-09-29. Scope: what AI design, prototyping and canvas products do today, which interaction patterns transfer to the EIJA Studio, and which do not.

## Decisions first

| # | Decision for EIJA | Verdict | Main evidence |
|---|---|---|---|
| 1 | Two edit lanes: a deterministic direct-edit lane (no provider call, target feedback under 0.1 s) and a prompt lane for intent | adopt | Lovable Visual Edits (no LLM); NN/G response limits |
| 2 | Every on-screen element carries a stable ID that resolves to a model entity; comments, drags and "ask AI about this" attach to that ID | adopt | Lovable stable JSX IDs; NN/G "apple picking" |
| 3 | AI may author tweak controls, but as a data proposal that the kernel validates against registered parameters | adapt | Claude Design tweaks panel |
| 4 | Grounding rule: a proposal may only reference language terms, tokens and components the model can verify; anything new is declared as new | adopt | v0 design-system docs; Figma Make kits |
| 5 | Design-system import must list what was not extracted (UNKNOWN stays visible) | adopt | Figma Make kits limitation |
| 6 | Token file: adapt the DESIGN.md idea (tokens plus rationale, lint, diff), export to W3C DTCG; do not depend on it while it is alpha | adapt | google-labs-code/design.md |
| 7 | Review by meaning with "last turn" and per-change accept/reject; no provider-side apply | adapt | Codex app review pane |
| 8 | Do not embed provider-generated HTML or iframes | avoid | tldraw make-real; ADR-013; Studio CSP |

## 1. Scope and method

**Queries run (WebSearch, US-only):** Claude Design launch; Figma Make docs; Google Stitch; Claude Design help centre; DESIGN.md; v0 design mode and registry; Claude Artifacts; Figma Make kits; Figma AI First Draft; tldraw make real; Uizard Autodesigner; Galileo AI and Stitch; Magic Patterns; Subframe; Lovable visual edits; Framer Wireframer; Codex app review; Codex app launch; "distributional convergence" frontend slop; NN/G generative UI; HCI foundations (Horvitz, Amershi, Shneiderman, KLM, Doherty, Hick, Fitts).

**Method:** search, then open the primary page (vendor docs, changelogs, first-party blogs, papers). Fetches went through a summarising model, so figures were taken from those summaries and are listed as such. One summary mislabelled the Codex review docs as another product; a re-fetch asked for the product name and returned "Codex".

**Not accessible:** `openai.com/index/introducing-the-codex-app/` (HTTP 403); `docs.subframe.com/concepts/design-to-code` (404); Subframe help-centre export article (redirects to docs root); Framer academy and dictionary pages (404); Anthropic's frontend-aesthetics cookbook notebook (opened, content not retrievable); Shneiderman 1983 PDF (unreadable). `web.archive.org` is blocked in this tool. Stitch's `docs/design-md/overview` page opened but returned only a title.

**Seen only in search results, not opened (treat as UNVERIFIED):** Galileo AI sunset details; Uizard Autodesigner 2.0 status in 2026; Figma "Make Designs" copycat incident press coverage; Framer keyboard shortcuts; Subframe "components synced, pages exported" wording; Codex app Windows availability.

PREDICTION labels below follow the dossier rule: model output, not measurement.

## 2. Products and topics

### 2.1 Claude Design (Anthropic Labs): verified, exists as described

**Today:** a research-preview workspace with its own canvas for prototypes, slides and one-pagers, launched 2026-04-17, powered by Claude Opus 4.7, for Pro, Max, Team and Enterprise (Enterprise off by default). Sources: [Anthropic announcement](https://www.anthropic.com/news/claude-design-anthropic-labs), [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design), [product page](https://claude.com/product/design).

| Pattern | Why it works (law or principle) | Sources |
|---|---|---|
| Four refinement channels on one canvas: chat, inline comment on an element, direct edit (drag, resize, align, edit text), and sliders | Direct manipulation: continuous representation, rapid reversible incremental actions (Shneiderman); mixed initiative couples automation with direct manipulation (Horvitz) | Get started; [Horvitz 1999](https://www.microsoft.com/en-us/research/publication/principles-mixed-initiative-user-interfaces/); [Direct manipulation](https://en.wikipedia.org/wiki/Direct_manipulation_interface) |
| Tweaks panel: Claude generates sliders and toggles for spacing, colour, layout; the user can ask for more controls | Converts an open-ended prompt into a bounded choice set, which lowers decision cost (Hick-Hyman) and gives sub-second feedback (Doherty) | Get started; [Laws of UX: Hick](https://lawsofux.com/hicks-law/), [Doherty](https://lawsofux.com/doherty-threshold/) |
| Design system extracted from codebase, decks and design files, tested with sample projects, then a "Published" toggle makes it org-wide | Human gate between AI proposal and authoritative state; matches Amershi guideline 16 "convey the consequences of user actions" | [Set up your design system](https://support.claude.com/en/articles/14604397-set-up-your-design-system-in-claude-design); [Amershi 2019 guidelines](https://www.microsoft.com/en-us/research/blog/guidelines-for-human-ai-interaction-design/) |
| Output is checked against the design system and self-corrected; admins can lock a team to one system | Constraint by grounding, not by adjectives in prompts (see 2.13) | Product page |
| "Save what we have and try a completely different approach"; ask for 2-3 alternative layouts | Bounded variant count keeps comparison cost low (Hick-Hyman) | Get started |
| Handoff to Claude Code via `/design-sync` and `/design`; exports to PDF, PPTX, HTML, ZIP and named partners | Explicit handoff artefact instead of implicit copy | Get started; product page |

**Limits:** research preview; shares subscription usage limits; large codebases consume more usage (Get started). The docs do not say how sliders bind to code, so the mechanism is UNVERIFIED.

**Verdict: adapt.** Keep the four-channel model and the publish gate. Change: sliders bind only to parameters registered in the executable model; "Published" is the owner's decision, never the provider's.

### 2.2 Claude Artifacts

**Today:** a side panel where Claude builds documents, code and small apps; templates Docs, Slides, Design; private by default; publish by link; 20 MB text-only storage per artifact; "Try fixing with Claude" on errors. Source: [Artifacts help](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them).

- Side panel next to the conversation keeps the artefact stable while the chat scrolls. Principle: visibility of the object of interest (Shneiderman).
- Several edit requests can be queued across files and sent as one batch. Principle: reduces round trips, addresses NN/G "accordion editing" ([NN/G](https://www.nngroup.com/articles/accordion-editing-apple-picking/)).
- Error diagnostics with a one-click repair request. Principle: efficient correction (Amershi guideline 9).

**Verdict: adapt** batching and the side-panel arrangement; **avoid** the private-to-published-link model (EIJA is local, 127.0.0.1 only).

### 2.3 Figma Make and Figma AI

**Today:** Make is a prompt-to-app tool inside Figma with a Figma-style properties panel, draw and annotation tools, code view, version history and publishing. First Draft (2024) was folded into a Figma agent from 2026-05-20. Sources: [Explore Figma Make](https://help.figma.com/hc/en-us/articles/31304412302231-Explore-Figma-Make), [Introducing Make](https://www.figma.com/blog/introducing-figma-make/), [First Draft help](https://help.figma.com/hc/en-us/articles/23955143044247-Use-First-Draft-with-Figma-AI).

| Pattern | Why it works | Sources |
|---|---|---|
| Point at an element, then describe the change | Removes the reference-typing cost NN/G calls "apple picking" | Introducing Make; NN/G |
| Properties panel and code view beside the prompt | Three abstraction levels (intent, property, code) on one object | Explore Figma Make |
| Make kits = npm packages + library variables and styles + written guidelines that teach usage | Guidelines carry rationale that tokens cannot | [Get started with Make kits](https://help.figma.com/hc/en-us/articles/39241689698839-Get-started-with-Make-kits); [Make kits blog, 2026-04-02](https://www.figma.com/blog/introducing-make-kits-and-make-attachments/) |
| Documented loss: kits "currently don't support full extraction of design tokens"; a subset becomes a global CSS file of raw values | An honest limitation statement; users can see what the tool cannot know | Get started with Make kits |
| Curated libraries at four fidelities (wireframe to high fidelity) rather than open generation; the earlier "Make Designs" was disabled after outputs "too closely resembled existing apps" | A generic-output failure handled by narrowing the palette, not by better prompts | [First Draft blog, 2024-09-24](https://www.figma.com/blog/figma-ai-first-draft/) |

**Verdict: adapt.** Adopt the "guidelines beside tokens" pair and the honest-loss disclosure. First Draft could not use an org's own design system at launch (First Draft help); that gap is what Make kits, Magic Patterns and v0 later filled.

### 2.4 Google Stitch (successor of Galileo AI, per secondary sources)

**Today:** a Google Labs tool. 2025-05-20: prompt or image to UI with multi-variant generation, theme selectors and export to Figma or front-end code, on Gemini 2.5 Pro ([Google Developers Blog](https://developers.googleblog.com/stitch-a-new-way-to-design-uis/)). 2026-03-18: AI-native infinite canvas, design agent, agent manager for parallel ideas, voice critique, "Play" to preview linked screens, DESIGN.md, export via MCP and SDK ([Google blog](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/)). 2026-05-19: streaming to the canvas and steering iterations mid-run ([Stitch updates](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-updates/)).

| Pattern | Why it works | Sources |
|---|---|---|
| Streaming output to the canvas while the agent works | Progress visibility during waits over 1 s ([NN/G limits](https://www.nngroup.com/articles/response-times-3-important-limits/)) | Stitch updates |
| Agent manager: several ideas in parallel, kept organised | Parallel lanes need a status overview; same problem as EIJA lanes | Google blog 2026-03-18 |
| Screens linked and previewed with "Play"; agent proposes next screens | Prototype as a runnable check | Google blog 2026-03-18 |
| DESIGN.md portable design rules | See 2.5 | [Stitch DESIGN.md post, 2026-04-21](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/) |

**Verdict: adapt** the agent manager and the streaming-progress pattern; **avoid** voice as a primary channel (no evidence it helps engineers editing formal models). The Galileo-to-Stitch lineage and the 2025-06-20 sunset date come from secondary sources only: UNVERIFIED. `galileo.ai` now shows an unrelated observability product.

### 2.5 DESIGN.md (Google Labs, open specification)

Source: [github.com/google-labs-code/design.md](https://github.com/google-labs-code/design.md).

- Two layers: YAML front matter with tokens (colour, typography, spacing, rounded, components, `{path.to.token}` references) and a Markdown body with rationale.
- CLI: `lint` (11 rules including broken references and WCAG AA contrast), `diff` (token regressions), `export` (Tailwind v3/v4, DTCG), `spec` (text for agent prompts). Licence Apache-2.0. Status: alpha.
- Why it works: tokens are checkable, rationale is readable, and an agent can "know exactly what a color is for" ([Google post](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/)). This is the same shape as EIJA's "generated or checked against the code" invariant.

**Verdict: adapt.** Take the token-plus-rationale split, the lint and diff idea, and the DTCG export. Do not take a runtime dependency while alpha; the token lane owns the DTCG choice.

### 2.6 v0 (Vercel)

**Today:** prompt-to-app with Design Mode (2025-06-12) and Design Systems 2.0. Sources: [Design Systems 2.0 docs](https://v0.app/docs/design-systems-2), [Design Mode announcement](https://community.vercel.com/t/introducing-design-mode-on-v0/13225), [Vercel blog, 2025-08-22](https://vercel.com/blog/ai-powered-prototyping-with-design-systems).

| Pattern | Why it works | Sources |
|---|---|---|
| Design Mode edits copy, type, layout and colour "without editing code or spending any credits"; Tailwind UIs only | Direct manipulation without a model round trip; the LLM is reserved for intent | Announcement |
| Import from GitHub, Figma nodes, Storybook links, `.tgz` packages and manual notes; result saved as a reusable skill with a starter app and up to three reference repos in `v0.json` | Grounding source is inspectable and versioned | Design Systems 2.0 |
| Stated rule: if a component, prop or token "cannot be verified from the sources, v0 should not use it" | Converts "do not hallucinate components" into a checkable constraint | Design Systems 2.0 |
| Updating the design system does not rewrite existing projects | Predictability (no surprise ripple); mirrors EIJA's explicit apply | Design Systems 2.0 |

**Caveat:** a data-loss bug after heavy Design Mode edits was reported 2025-06-21 and reported fixed by 2025-06-24 (community post). Direct-edit lanes need durable versioning.

**Verdict: adopt** the verifiability rule and the no-model direct-edit lane.

### 2.7 Lovable (Visual Edits, preview toolbar)

**Today:** the preview toolbar has four modes: select elements, edit text inline, draw annotation, add comment. Sources: [docs](https://docs.lovable.dev/features/design), [Introducing Visual Edits, 2025-02-12](https://lovable.dev/blog/introducing-visual-edits), [How we built Visual Edits](https://lovable.dev/blog/visual-edits).

| Pattern | Why it works | Sources |
|---|---|---|
| Each generated JSX component gets a unique stable ID via a Vite plugin, so a DOM click maps to source | Identity between picture and code is what makes selection trustworthy | How we built |
| Code held client-side as an AST (Babel, SWC); Tailwind changes applied optimistically, then HMR | Feedback inside the 0.1 s "direct manipulation" limit ([NN/G](https://www.nngroup.com/articles/response-times-3-important-limits/)) | How we built |
| Explicit non-LLM path: precise changes "without requiring AI intervention" to save cost and wait | Separates deterministic from probabilistic edits, the same split as EIJA's kernel versus provider | How we built |
| Multi-select with Ctrl or Cmd, then one prompt for all selected elements | Batching reduces prompts (NN/G accordion editing) | Docs |
| Metering: 100 free inline text edits per account, refilling after 24 h; 2,000 per workspace per 24 h; other modes consume credits | Users see which actions cost model spend | Docs |

**Verdict: adopt** stable-ID mapping and the labelled two-lane cost model. Docs do not describe design-system use in this section (UNVERIFIED for Lovable).

### 2.8 Magic Patterns

**Today:** AI prototyping with a code-based design-system representation. Sources: [Design systems page](https://www.magicpatterns.com/product/design-systems), [Design System Agent, 2026-06-10](https://www.magicpatterns.com/blog/introducing-design-system-agent).

- Imports from GitHub, local folders, live URLs and npm; reads tokens, components and brand standards. Vendor claim: output "matches your system pixel-for-pixel" (marketing; UNVERIFIED as measured).
- The Design System Agent scans sources and proposes discovered components, styles and rules; users then edit one, many or system-wide (for example, colour tokens).
- Why it works: propose-then-review keeps a human between extraction and use (Amershi guidelines 9 and 16).

**Verdict: adapt** the "agent proposes what it found, human curates" import flow.

### 2.9 Subframe

**Today:** landing page claims a canvas "1:1 with code", components with props, slots and variants synced from the codebase, an agent that builds in the repo, and MCP for external agents; FAQ says it works best with React ([subframe.com](https://www.subframe.com/)). The docs pages I tried were not available, so the "components synced, pages exported" mechanism seen in search is UNVERIFIED.

**Verdict: avoid relying on it as evidence.** The concept (design components tied to code components) is already covered by v0 and Magic Patterns; "1:1 with code" is a marketing claim with no mechanism verified.

### 2.10 tldraw make-real

**Today:** an open-source experiment: sketch on a canvas, select, click Make Real, and the model's HTML appears as a live iframe shape beside the sketch. The GitHub repository is archived (2026-02-20 per repository page). Sources: [repo](https://github.com/tldraw/make-real), [story so far, 2023-11-18](https://tldraw.substack.com/p/make-real-the-story-so-far).

| Pattern | Why it works | Sources |
|---|---|---|
| Annotate the generated result on the same canvas, then send it back as the next prompt | Feedback is spatial, not textual; removes "apple picking" | Story so far; NN/G |
| Result and sketch share one canvas; embedding the live site beat popups | Proximity of cause and effect | Story so far |
| Previous HTML is supplied to the model so it can "fill in" annotated regions | Iteration by context, not restart | Story so far |

**Verdict: adapt** annotation-as-input; **avoid** the iframe mechanism. Studio CSP is `default-src 'none'` with no frame source, and ADR-013 forbids provider HTML, so generated markup cannot be embedded.

### 2.11 Framer AI (Wireframer and the AI canvas agent)

**Today:** an agent that "creates editable pages, sections, copy, and visuals" and lets the user "take over on the canvas at any point"; branching and review workflows before publishing. Source: [framer.com/wireframer](https://www.framer.com/wireframer/). Wireframer-specific docs and shortcuts were not accessible: UNVERIFIED.

- Output is editable layers, not a locked template: the AI result lands in the same object model as hand work.
- Review and publish are separate steps from generation (matches the propose/decide split).

**Verdict: adapt** "AI output lands in the editable model" and separate review before publish.

### 2.12 OpenAI Codex desktop app (UI)

**Today:** a desktop app with project sidebar, threads, review panel; launched on macOS 2026-02-02 per a third-party review ([Verdent](https://www.verdent.ai/guides/codex-app-first-impressions-2026)); the official launch post returned HTTP 403. Review docs: [Codex code review](https://learn.chatgpt.com/docs/code-review?surface=app) (redirect target of `developers.openai.com/codex/app/review`).

| Pattern | Why it works | Sources |
|---|---|---|
| Diff scopes: unstaged, staged, commit, branch, and **last turn** (the assistant's latest edits) | Answers "what did the agent just change" with one selector; low Hick-Hyman cost (5 options) | Codex code review |
| Stage or revert at three levels: whole diff, file, single hunk | Granular reversibility (Shneiderman); efficient correction (Amershi 9) | Codex code review |
| Inline comment on a diff line becomes guidance to the agent | Point-then-say, attached to a stable location | Codex code review |
| A worktree per thread isolates parallel agents | Prevents cross-lane interference; user merges manually | Verdent |
| Gap noted by a reviewer: no built-in editor loop, so small fixes leave the app | Review without edit forces context switches | Verdent (third-party, single source) |

**Verdict: adapt.** The diff is textual; EIJA needs the same three levels over semantic changes: whole change set, per model, per single semantic change. The reviewer-noted editor gap is a reason to keep direct edit inside the review surface.

### 2.13 Why outputs feel generic, and what mitigates it

| Finding | Source |
|---|---|
| Anthropic names "distributional convergence": "safe design choices" dominate web training data, so unguided models sample from that centre; steer with direct prompting, design skills, or richer tooling | [Improving frontend design through Skills, 2025-11-12](https://claude.com/blog/improving-frontend-design-through-skills) |
| Figma's first generator produced mocks resembling existing apps; the fix was curated component libraries and assembly examples | [First Draft blog](https://www.figma.com/blog/figma-ai-first-draft/) |
| Grounding in the real design system is now the common mitigation: Claude Design (extraction plus self-check), Figma Make kits, v0 skills, Magic Patterns, Stitch DESIGN.md | Sections 2.1, 2.3, 2.5, 2.6, 2.8 |
| Prompt-only control has an articulation barrier (users struggle to state intent with enough specificity) | Search-result summary of NN/G and Nielsen writing only; page not opened: UNVERIFIED. The opened NN/G study shows related friction (accordion editing, apple picking) |
| Academic framing: Norman's gulfs applied to UI generation; a CHI 2026 paper proposes semantic guidance | [Park et al., arXiv 2601.19171](https://arxiv.org/pdf/2601.19171) (numbers not extracted; UNVERIFIED) |

**Reading for EIJA:** the anti-slop rubric (no default gradients, generic hero, placeholder data) is a design-time rule. For the product, slop is prevented structurally: the picture is generated from the model, so there is nothing generic to sample. Where AI proposes text or layout, it must be grounded in the ubiquitous language and tokens.

### 2.14 Uizard

**Today:** AI features per the help centre: Autodesigner, Theme Generator, Image Generator, Text Assistant, Screenshot Scanner, Wireframe Scanner, Design Review ([help collection](https://support.uizard.io/en/collections/7738636-ai-features)). Acquired by Miro, announced 2024-05-27 ([Uizard blog](https://uizard.io/blog/uizard-joins-miro/)). Current development status in 2026 is UNVERIFIED (no primary source found).

- Scanner patterns (sketch or screenshot to editable screens) are import features, not review features.

**Verdict: avoid** as a design reference; nothing verified beyond what tools above already show.

## 3. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| Claude Design launched 2026-04-17 as a research preview on Claude Opus 4.7 | [Anthropic](https://www.anthropic.com/news/claude-design-anthropic-labs) | high |
| Claude Design counts against shared subscription usage limits | [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) | high |
| Claude Artifacts: 20 MB per artifact, text-only storage | [Artifacts help](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them) | high |
| Lovable: 100 free inline text edits per account (refill 24 h), 2,000 per workspace per 24 h | [Lovable docs](https://docs.lovable.dev/features/design) | high |
| v0 Design Mode launched 2025-06-12; no credits; Tailwind only | [Vercel community](https://community.vercel.com/t/introducing-design-mode-on-v0/13225) | medium (forum announcement) |
| v0 design-system skill: up to 3 reference GitHub sources | [v0 docs](https://v0.app/docs/design-systems-2) | high |
| Figma Make kits announced 2026-04-02; token extraction is partial, output is raw-value CSS | [Figma blog](https://www.figma.com/blog/introducing-make-kits-and-make-attachments/), [help](https://help.figma.com/hc/en-us/articles/39241689698839-Get-started-with-Make-kits) | high |
| Figma First Draft: 4 libraries; agent became entry point 2026-05-20 | [First Draft help](https://help.figma.com/hc/en-us/articles/23955143044247-Use-First-Draft-with-Figma-AI) | high |
| DESIGN.md: 11 lint rules, alpha, Apache-2.0, exports Tailwind and DTCG | [GitHub](https://github.com/google-labs-code/design.md) | high |
| Stitch: 2025-05-20 launch on Gemini 2.5 Pro; 2026-03-18 canvas and agent; 2026-05-19 streaming agent rollout | Google blogs (section 2.4) | high |
| Codex review pane: 5 diff scopes; stage or revert at 3 levels | [Codex code review](https://learn.chatgpt.com/docs/code-review?surface=app) | high |
| Response-time limits: 0.1 s feels instantaneous, 1 s keeps flow, 10 s holds attention (Miller 1968; Card et al. 1991) | [NN/G](https://www.nngroup.com/articles/response-times-3-important-limits/) | high |
| Doherty threshold 400 ms (Doherty and Thadani, IBM Systems Journal, 1982) | [Laws of UX](https://lawsofux.com/doherty-threshold/) | medium (secondary summary of a primary) |
| KLM operators: P 1.1 s, H 0.4 s, M 1.35 s, B 0.1 s, K 0.20 s (55 wpm) to 0.28 s (40 wpm); RMS error 21%; expert, error-free, routine tasks only | [Keystroke-level model](https://en.wikipedia.org/wiki/Keystroke-level_model) | medium (secondary; original Card, Moran and Newell not opened) |
| NN/G accordion editing and apple picking: 8 participants, 90-minute sessions, ChatGPT-3.5, 2023 | [NN/G](https://www.nngroup.com/articles/accordion-editing-apple-picking/) | high for the study; low external validity (n=8, text tasks) |
| Amershi et al.: 18 guidelines in four phases | [Microsoft Research](https://www.microsoft.com/en-us/research/blog/guidelines-for-human-ai-interaction-design/) | high |

**Worked model (PREDICTION, not a measurement).** Task: change one guard on a state transition to a value picked from an enumerated list.

- Prompt path: M 1.35 + P 1.1 + B 0.1 (select target) + H 0.4 + 40 characters at K 0.20 (8.0) + Enter 0.2 = 11.15 s, plus provider wait (unmodelled; over 1 s by assumption, so a progress indicator is needed).
- Direct path: M 1.35 + P 1.1 + B 0.1 (select) + P 1.1 + B 0.1 (choose value) = 3.75 s, plus an assumed 0.1 s response.
- Predicted ratio about 3 to 1 for this task. Validity: KLM covers expert, error-free, routine execution only, error 21% RMS; it says nothing about tasks where the user does not know the target value, where a prompt may be better. The study in section 4 tests that boundary.

## 4. Implications for EIJA

1. **Element-to-model identity.** Every rendered node (tree item, diagram box, journey step, evidence row) carries a stable model ID. Selection, comment, drag and "ask AI" all resolve through it. Rationale: Lovable's stable IDs; NN/G apple picking.
2. **Two lanes, labelled.** Direct edits (rename term, move state, change enumerated guard) run through the kernel with no provider and give feedback under 0.1 s (PREDICTION target from NN/G limits). Prompted work shows a streaming or progress state past 1 s and is marked as calling a provider, which also supports the existing egress-consent rule in AGENTS.md.
3. **AI-authored tweak controls are proposals.** A tweaks panel spec is JSON validated by the kernel: each control names a registered parameter and range. A control that binds to nothing is rejected and shown as rejected. Applying a value is an owner action.
4. **Grounding rule for proposals.** Adopt the v0 rule as a checker: a proposal may cite only entities, tokens and components resolvable in the model or token files; anything else must appear as an explicitly new item awaiting the owner. This blocks generic output structurally rather than by prompt wording.
5. **Import shows what it could not extract.** Follow Figma Make kits' disclosed loss: any import (design files, existing tokens) ends with a list of unmapped items, rendered as UNKNOWN, never dropped.
6. **Token file.** Evaluate a DESIGN.md-shaped pair (tokens plus rationale) with `lint` and `diff` semantics and DTCG export. Record the choice in an HCI-ADR in the 0057-0088 block; no dependency on an alpha tool.
7. **Review by meaning with Codex-style scopes.** Scope selector: last agent turn, this proposal, whole branch. Accept or reject at three levels: change set, model, single semantic change. Inline comment attaches to a model ID and is sent to the provider as guidance. Provider cannot apply.
8. **Parallel lanes in one overview.** Borrow the Stitch agent-manager and Codex worktree-per-thread idea for proposal branches: one row per proposal with status, verification state and UNKNOWN count.
9. **No embedded provider markup.** Pictures (UML, journeys) are SVG generated by the kernel from the model and injected through DOM text and attribute nodes only, consistent with ADR-013. A make-real style iframe is not available under the current CSP; any change needs its own ADR.
10. **Study protocol (design only, no results claimed).** Within-subject comparison of direct versus prompt path for 8 task types across two levels of task clarity (target known, target unknown); measures: time on task, error count, reference-typing events, self-reported control (agreed scale to be chosen). Hypothesis H1: direct is faster when the target is known; H2: prompt wins when unknown. Sample size and analysis plan belong to the study document.

## 5. Gaps and unverified items

| Item | Status |
|---|---|
| Claude Design slider-to-code binding mechanism | UNVERIFIED (not documented) |
| Galileo AI sunset date and Stitch lineage | UNVERIFIED (secondary sources only) |
| Uizard Autodesigner 2026 status | UNVERIFIED |
| Subframe docs (design-to-code, sync semantics) | UNVERIFIED; docs unreachable, landing page only |
| Framer Wireframer specifics (variants, shortcuts) | UNVERIFIED; docs unreachable |
| Codex app official launch post and platform matrix | UNVERIFIED (403); launch date from a third-party review |
| Anthropic frontend-aesthetics cookbook content | UNVERIFIED (notebook not retrievable); the blog post was used instead |
| Park et al. 2026 (arXiv 2601.19171) results and sample size | UNVERIFIED; only the framing was extracted |
| Vendor claims ("pixel-for-pixel", "1:1 with code", "production ready") | Marketing; no measurement seen |
| Any evidence that these interaction patterns help software engineers building formal models | None found; all products target designers or app builders. A user study is required |
| Not researched here | Figma Design agent internals; Adobe, Canva, Miro and other Claude Design export partners; accessibility behaviour of any product |

## 6. URLs opened (access date 2026-09-29)

Anthropic: https://www.anthropic.com/news/claude-design-anthropic-labs ; https://support.claude.com/en/articles/14604416-get-started-with-claude-design ; https://support.claude.com/en/articles/14604397-set-up-your-design-system-in-claude-design ; https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them ; https://claude.com/product/design ; https://claude.com/blog/improving-frontend-design-through-skills

Figma: https://help.figma.com/hc/en-us/articles/31304412302231-Explore-Figma-Make ; https://help.figma.com/hc/en-us/articles/39241689698839-Get-started-with-Make-kits ; https://www.figma.com/blog/introducing-make-kits-and-make-attachments/ ; https://help.figma.com/hc/en-us/articles/23955143044247-Use-First-Draft-with-Figma-AI ; https://www.figma.com/blog/figma-ai-first-draft/ ; https://www.figma.com/blog/introducing-figma-make/

Google: https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-updates/ ; https://developers.googleblog.com/stitch-a-new-way-to-design-uis/ ; https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/ ; https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/ ; https://github.com/google-labs-code/design.md ; https://stitch.withgoogle.com/docs/design-md/overview (title only)

Others: https://v0.app/docs/design-systems-2 ; https://community.vercel.com/t/introducing-design-mode-on-v0/13225 ; https://vercel.com/blog/ai-powered-prototyping-with-design-systems ; https://uizard.io/blog/uizard-joins-miro/ ; https://support.uizard.io/en/collections/7738636-ai-features ; https://www.magicpatterns.com/blog/introducing-design-system-agent ; https://www.magicpatterns.com/product/design-systems ; https://www.subframe.com/ ; https://github.com/tldraw/make-real ; https://tldraw.substack.com/p/make-real-the-story-so-far ; https://docs.lovable.dev/features/design ; https://lovable.dev/blog/visual-edits ; https://lovable.dev/blog/introducing-visual-edits ; https://www.framer.com/wireframer/ ; https://learn.chatgpt.com/docs/code-review?surface=app ; https://www.verdent.ai/guides/codex-app-first-impressions-2026 ; https://galileo.ai

HCI: https://www.nngroup.com/articles/response-times-3-important-limits/ ; https://www.nngroup.com/articles/accordion-editing-apple-picking/ ; https://arxiv.org/pdf/2601.19171 ; https://www.microsoft.com/en-us/research/publication/principles-mixed-initiative-user-interfaces/ ; https://www.microsoft.com/en-us/research/blog/guidelines-for-human-ai-interaction-design/ ; https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/ ; https://en.wikipedia.org/wiki/Direct_manipulation_interface ; https://en.wikipedia.org/wiki/Keystroke-level_model ; https://lawsofux.com/doherty-threshold/ ; https://lawsofux.com/hicks-law/ ; https://lawsofux.com/fittss-law/
