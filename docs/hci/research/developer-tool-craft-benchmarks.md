# Developer-tool craft benchmarks

Research dossier "devtool-craft" for the EIJA Studio UX lane. Access date for every URL: 2026-09-29.
Status: research input, not a decision. Decisions go to HCI-ADRs (0057-0088). Predictions are labelled PREDICTION and are not measurements.

## Decisions first

| # | Recommendation | Basis |
|---|---|---|
| 1 | Build a small set of vanilla-JS primitives (command palette, tree, tabs, split pane, dialog, diff/review list) as explicit state machines; do not adopt a component library wholesale. | Every full library checked is React-only, needs a build, or has an open `style-src 'self'` bug (section 3). |
| 2 | Treat Lit (BSD-3-Clause, about 5 KB) as the only framework-like dependency worth a spike, behind a CSP test and an ADR-013 amendment. | Section 3. |
| 3 | Use Zag.js machines and Primer `@primer/behaviors` as behavioural references or vendored candidates, not as the UI. | Section 3. |
| 4 | One universal command palette that acts on the current selection, shows the shortcut beside each command, has entity prefixes, and contains no approve/apply command. | Linear, Superhuman, VS Code, Warp (section 2). |
| 5 | Theme from three inputs (base, accent, contrast) in a perceptual colour space; semantic status hues are separate. | Linear, Stripe, Geist (section 2). |
| 6 | Record a CSP decision on fonts: the current CSP has no `font-src`, so under `default-src 'none'` any web font, even self-hosted, is blocked. | `src/eija_studio/interfaces/http.py` line 63. |

## 1. Scope and method

Goal: find what makes developer tools feel world-class, so EIJA Studio can copy the mechanisms (not the look) under the anti-slop rubric and the invariants (AI proposes, kernel checks, owner decides; UNKNOWN never hidden).

Method: WebSearch to find pages, then WebFetch on the primary or official page. WebFetch returns a model-made summary of the page, not raw text. Every quantitative fact below was therefore read from a summary and carries a confidence rating, and no quotation was checked character by character. Search results alone were never used as a source unless the row says so.

Accessible: official docs and blogs for Linear, Zed, VS Code, JetBrains, GitHub Primer, Vercel Geist, Stripe, Raycast, Warp, Obsidian, Superhuman (First Round Review, Superhuman blog); GitHub repos; MDN; W3C; NN/g.

Not accessible or not useful this session: Superhuman help centre (403); Linear "part I" redesign post (404); Linear keyboard-shortcuts docs (404); JetBrains 2022 new-UI announcement (404); `nngroup.com/articles/hicks-law` (404); web.archive.org (blocked by the tool). The shared WebSearch budget (200 calls) ran out before all follow-ups were done, so several claims stay UNVERIFIED (section 6).

Baseline measured from the repo (my count, simple regex, static HTML only, dynamic content excluded):

| Baseline metric | Value | Rubric target |
|---|---|---|
| Visible words in `index.html` after stripping tags | about 404 | about 120 per viewport (the baseline is one document, so not directly comparable) |
| `<pre>` blocks | 3 | raw JSON should be 0 in a primary view |
| Distinct `font-size` declarations in `app.css` | 13 (one is a `clamp`) | at most 6 |
| Distinct hex colours in `app.css` | 19 | one accent hue plus status hues |
| `.panel` sections in `index.html` | 6 | containers only where they encode grouping or state |

Current CSP: `default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'`. That means no inline `<style>`, no inline `style=""` attributes, no inline scripts, no fonts.

CSP fact from MDN: `el.style.display = "none"` is allowed; `setAttribute("style", ...)` is blocked. The same MDN page contradicts itself on `style.cssText =` (listed as blocked in one place, allowed in another). Test in the Studio before relying on either.

## 2. Products and topics

Each block: what it is today, patterns with the HCI reason, verdict for EIJA. Law abbreviations: NIELSEN-RT = response-time limits 0.1 s / 1 s / 10 s; FITTS = movement time grows with distance and shrinks with target size; HICK = decision time grows with number and complexity of choices; SCENT = information scent; PD = progressive disclosure; KLM = keystroke-level model.

### 2.1 Linear

Issue tracker, positioned around speed and craft. Command menu, search and shortcuts are first-class.

| Pattern | Why it works | Source |
|---|---|---|
| Command menu on Cmd/Ctrl+K acts on the current selection or view, and can be scoped with prefixes (`i` issues, `p` projects, `u` users, `l` labels, `d` documents). | Recognition over recall; prefixes cut the candidate set, so fewer choices to scan (HICK); scent stays high because results are typed by entity. | https://linear.app/docs/search |
| `/` quick search, `G` then a letter for navigation, `?` opens a searchable shortcut sheet (added 2021-03-25). | Shortcuts are learnable in place; making the sheet searchable is a discoverability move (SCENT). | https://linear.app/docs/search ; https://linear.app/changelog/2021-03-25-keyboard-shortcuts-help |
| Search ranks unstarted and in-progress issues before completed, cancelled, archived. | Ranking by likely relevance to the user's current job. | https://linear.app/docs/search |
| Theme generated from three variables (base, accent, contrast) in LCH, replacing 98 theme variables. | Perceptual lightness is comparable across hues; one contrast input yields high-contrast themes. | https://linear.app/now/how-we-redesigned-the-linear-ui |
| Redesign aimed at less visual noise and stronger hierarchy in sidebar, tabs, headers, panels; density explored "from very condensed to more spacious"; six weeks from direction to general availability; internal feature-flag dogfooding. | Restraint plus dogfooding; density tuned instead of assumed. | https://linear.app/now/how-we-redesigned-the-linear-ui |
| Method principles: "Simple first, then powerful", "Aim for clarity" (plain terminology, no invented jargon), "Say no to busy work". | Matches EIJA's ubiquitous-language goal. | https://linear.app/method/introduction |

Caution: Saarinen's ten rules include "don't lean on data as a crutch" (Figma blog summary). That is a practitioner belief, not evidence, and conflicts with our evidence-first rule. Treat Linear's look as hypotheses to test, not proof. https://www.figma.com/blog/karri-saarinens-10-rules-for-crafting-products-that-stand-out/

Verdict: adopt the palette model (selection-aware, prefixes, searchable `?` sheet); adapt the three-input theme; avoid copying the visual style or the anti-data stance.

### 2.2 Raycast

Keyboard launcher and extension platform: "apps, files, extensions, AI, and dictation one keystroke away".

| Pattern | Why it works | Source |
|---|---|---|
| List with right-side accessories (text, dates, tags) and an optional detail pane for the selected item. | Metadata beside the label raises scent without opening the item; one list plus one detail avoids navigation depth (PD). | https://developers.raycast.com/api-reference/user-interface/list |
| Built-in fuzzy matching on titles and keywords; loading bar under the search field. | Forgiving input plus visible system status. | same |
| Empty view is a first-class component (title, description, icon, actions). Store guidelines forbid flickering empty states: show loading before data. | Prevents a false "nothing here" (status visibility). | same ; https://developers.raycast.com/basics/prepare-an-extension-for-store |
| Naming rules: commands are `<verb> <noun>` or `<noun>`, Title Case actions, an ellipsis for actions that open a submenu. | Consistent labels are scannable (SCENT). | https://developers.raycast.com/basics/prepare-an-extension-for-store |

Verdict: adapt list + accessories + detail pane for the "changes by meaning" list. The manual page suggested an opening hotkey, but that conflicts with my prior knowledge, so the hotkey is UNVERIFIED and not used.

### 2.3 VS Code

Editor with named surfaces and a strict contribution model.

| Pattern | Why it works | Source |
|---|---|---|
| Named surfaces with usage guidance: Activity Bar, Primary and Secondary Sidebar, Editor, Panel, Status Bar. Command Palette for named discoverable actions; Quick Pick for focused input; Notifications for time-sensitive alerts; Settings for persistent preferences. | One purpose per surface lowers decision cost (HICK) and gives users a stable map. | https://code.visualstudio.com/api/ux-guidelines/overview |
| Palette prefixes (`?` lists them) and separate quick-open, symbol and go-to-line keys. | Mode by prefix keeps one entry point. | https://code.visualstudio.com/docs/getstarted/userinterface |
| Command titles: clear names, category prefixes, no emoji, shortcuts for frequent commands. | Same. | https://code.visualstudio.com/api/ux-guidelines/command-palette |
| Walkthrough guidance: avoid many steps; every step gets an action, "use verbs where possible". | Onboarding by doing, not reading (PD). | https://code.visualstudio.com/api/ux-guidelines/walkthroughs |
| Settings: a search UI over a JSON file; workspace settings override user settings. | Two interfaces to one store; project-level sharing. | https://code.visualstudio.com/docs/getstarted/userinterface |
| Agent edits reviewed as diffs, with Keep or Undo per change or for all pending edits, plus snapshot checkpoints before each request. | Reversibility cuts the cost of trusting proposals. | https://code.visualstudio.com/docs/agents/run/review-code-edits |

Verdict: adopt the surface map and the reversibility model; adapt the palette. Review is at diff level, which EIJA must exceed (by meaning).

### 2.4 Zed

Rust editor with a custom GPU UI framework (GPUI) and an agent panel.

| Pattern | Why it works | Source |
|---|---|---|
| Explicit frame budget: at 120 Hz there are 8.33 ms per frame; team says the only way to meet it was its own UI framework. | Sub-100 ms interaction (NIELSEN-RT) is the floor; frame budgets make it testable. | https://zed.dev/blog/videogame |
| Metal-pipeline post reports frame times consistently under 4 ms on M1 and M2 in its tests. | Vendor measurement on Apple hardware only. | https://zed.dev/blog/120fps |
| Palette lists the key binding beside every command; keymap is JSON with context expressions, plus a graphical keymap editor; selectable base keymaps (VS Code, JetBrains, Vim, Emacs, others). | Recognition teaches recall; familiar keymaps lower switching cost. | https://zed.dev/docs/command-palette ; https://zed.dev/docs/key-bindings |
| Agent review: one multi-buffer tab with every change; accept or reject each hunk or the whole set; follow mode; tool permissions "allowed, denied, or confirmed"; Restore Checkpoint after each edit. | Review is a single list, so no hunting across files. | https://zed.dev/docs/ai/agent-panel |
| Settings UI and `settings.json`, with `.zed/settings.json` per project; defaults are chosen per language. | Good defaults so few settings are needed. | https://zed.dev/docs/configuring-zed |

Verdict: adopt the review-list idea and per-item accept/reject vocabulary; avoid the "allowed" auto-approval mode for anything that approves or applies in EIJA (kernel-level invariant); the GPU stack is irrelevant, but budgets are not.

### 2.5 JetBrains (new UI)

New UI, default in 2024.2 (2024-07-08). Stated goals: reduce visual complexity, easy access to essentials, progressively disclose complexity. https://blog.jetbrains.com/blog/2024/07/08/the-new-ui-becomes-the-default-in-2024-2/ ; https://www.jetbrains.com/help/idea/new-ui.html

| Pattern | Why it works | Source |
|---|---|---|
| Work began 2021; more than 10 UX studies; preview and beta; more than 2,000 bugs fixed after launch; a compact mode was added. | Studies plus a density switch admit users differ (HICK, PD). | JetBrains blog above |
| Removed the prominent blue Run button; customisable toolbar; breakpoints shown over line numbers; fold icons on hover. | Hides rarely needed chrome until hover or need (PD, restraint). | same ; help page |
| Search Everywhere: Shift twice opens one box for classes, files, symbols, actions, settings; synonyms are recognised ("toggle presentation mode" finds "Enter Presentation Mode"); Tab switches scope. | Synonyms and scope tabs raise scent. | https://www.jetbrains.com/help/idea/searching-everywhere.html |
| Classic UI kept as a plugin for a stated minimum period; JetBrains reports 87 percent of users had switched. | Migration off-ramp for trust. | JetBrains blog above |

Verdict: adapt (synonym aliases in the palette; compact mode; hover-reveal for secondary actions). NN/g limits disclosure to two levels: https://www.nngroup.com/articles/progressive-disclosure/. For EIJA, UNKNOWN must stay at level 0 (always visible as a count), with detail at level 1.

### 2.6 GitHub Primer

GitHub's design system: React components, Rails components, CSS utilities, design tokens, UI patterns, and an "MCP server". https://primer.style/product/getting-started/

| Pattern | Why it works | Source |
|---|---|---|
| Empty states in three kinds (feature unused, temporarily empty, error) with rules: purpose first, brief next step, no playful art for errors, no vague "There was a problem". | Status visibility and error recovery. | https://primer.style/product/ui-patterns/empty-states/ |
| Tokens in JSON compiled with Style Dictionary; 9 colour themes including high-contrast, tritanopia and colour-blind variants; MIT. | A tested theme matrix, not one light and one dark. | https://github.com/primer/primitives |
| `@primer/behaviors`: framework-agnostic focus trap, focus zone, anchored position, scroll into view; MIT. | Small behaviours instead of a component set. | https://github.com/primer/behaviors |
| `primer/view_components` (Rails) ships no custom elements; the page says it entered maintenance mode in February 2026. | Not an option for a Python app. | https://github.com/primer/view_components |

Verdict: adopt the empty-state taxonomy; adapt the theme matrix (colour-vision variants) as an input to tokens; evaluate `@primer/behaviors` in a spike; avoid the React and Rails components. Primer React is MIT and React-only (https://github.com/primer/react). I found no general Primer web-component library (UNVERIFIED).

### 2.7 Vercel (Geist)

Design system and open-source fonts. https://vercel.com/geist/introduction

| Pattern | Why it works | Source |
|---|---|---|
| Ten colour scales, ten steps each, each step with a role: 1-3 component backgrounds, 4-6 borders, 7-8 high-contrast backgrounds, 9-10 text and icons; a two-value backgrounds scale. | Role-named steps make UI states derivable and auditable (a token per role, not per use). | https://vercel.com/geist/colors |
| 31 typography classes, each pre-setting size, line height, letter spacing and weight; mono variants for code and tabular data. | Fewer decisions per screen; but 31 styles exceeds our budget of 6 sizes. | https://vercel.com/geist/typography |
| Geist Sans, Geist Mono and Geist Pixel under SIL OFL-1.1. | Licence fits our rule. | https://github.com/vercel/geist-font |

Verdict: adapt the step-role scheme with far fewer scales (one neutral, one accent, status hues); avoid 31 text styles. The components are React (`@vercel/geistcn`, per the intro page) and their licence is UNVERIFIED.

### 2.8 Stripe Dashboard

| Pattern | Why it works | Source |
|---|---|---|
| Accessible colour system built in CIELAB: 4.5:1 for small text, 3:1 for large text and icons; the article says any two colours five levels apart meet 4.5:1 (for their palette). | Perceptual uniformity gives predictable contrast. | https://stripe.com/blog/accessible-color-systems |
| Stripe Apps split: ContextView (drawer next to the Stripe page, the default) versus FocusView (blocking backdrop for start-to-finish tasks). | Side-by-side context for review; a blocking mode for a consequential task (fewer accidental actions). | https://docs.stripe.com/stripe-apps/design |
| Custom styling of extension UI is intentionally limited to keep consistency and contrast. | Constraint as accessibility guarantee. | same |
| `?` lists shortcuts; a Shortcuts section shows pinned and recent pages; Home overview is customisable by widgets; settings are grouped Personal, Account, Product. | Recent and pinned items reduce lookup cost (FITTS/HICK in navigation). | https://docs.stripe.com/dashboard/basics |
| Pattern catalogue includes empty state, loading, progress stepping, demo content. | Complete state coverage. | https://docs.stripe.com/stripe-apps/patterns |

Verdict: adopt the ContextView/FocusView split for "AI proposal beside affected models" versus "owner decision"; adapt the contrast method (validate computationally against WCAG ratios, since WCAG uses relative luminance, not CIELAB).

### 2.9 Warp

Terminal, now described as an open-source "Agentic Development Environment". https://docs.warp.dev/

| Pattern | Why it works | Source |
|---|---|---|
| Blocks pair a command and its output as one atomic unit, with per-block copy, share, bookmark, filter and search. | A meaningful unit of work replaces a scrolling stream; actions bind to the unit (chunking). | https://docs.warp.dev/terminal/blocks |
| Palette (Ctrl+Shift+P on Windows) with filter prefixes `w:`, `p:`, `n:`, `actions:`, `files:`, `sessions:` and clickable filter buttons. | Prefix or click, same result set. | https://docs.warp.dev/terminal/command-palette |
| Same agent reachable in app, CLI and cloud. | One capability, several surfaces. | https://docs.warp.dev/ |

Verdict: adapt blocks as the model for a Semantic Transaction card (one atomic reviewable unit with its own actions). Warp's agent features are not examined for approval authority; UNVERIFIED.

### 2.10 Superhuman

Email client built around speed and keyboard use; product-market-fit method published at First Round.

| Pattern | Why it works | Source |
|---|---|---|
| Speed targets: initially 100 ms UI response, later under 50 ms (per the First Round summary). | 0.1 s is the "instantaneous" limit (NIELSEN-RT); staying well below it leaves margin for variance. | https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/ |
| Palette principles: same shortcut everywhere; every action reachable; forgiving fuzzy search with synonyms; ranking by importance, frequency and context; contextual filtering; show the shortcut in results so users "learn the shortcut for next time". | Palette doubles as a trainer; recognition converts to recall. | https://blog.superhuman.com/how-to-build-a-remarkable-command-palette/ |
| Method: survey "very disappointed" share; 22 percent at start, 58 percent three quarters later; roadmap split 50/50 between strengthening loved features and fixing friction. | Measured, not aesthetic, feedback loop; the Sean Ellis 40 percent threshold. | First Round link above |

Verdict: adopt the palette principles and the "show the shortcut" trainer; adapt the PMF survey into the EIJA user-study protocol (the question would be about the change-review task, not the product overall). A 50-60 ms internal target appeared only in a search summary of an unopened blog: UNVERIFIED.

### 2.11 Obsidian

Local-first note app with plugins. https://obsidian.md/help/ (the page describes local storage, Sync, Publish, a CLI and a Web Clipper; graph view and Canvas were not confirmed).

| Pattern | Why it works | Source |
|---|---|---|
| Command palette opens with Ctrl/Cmd+P; fuzzy matching ("scf" finds Save Current File); user-pinned commands at the top; per-command hotkeys as the faster alternative. | Fuzzy match lowers typing cost; pinning personalises without clutter. | https://obsidian.md/help/plugins/command-palette |
| Extensibility by core and community plugins, themes and CSS. | Not applicable: EIJA cannot let plugins approve or apply. | https://obsidian.md/help/ |

Verdict: adapt pinning; avoid open plugin extensibility in v1.

### 2.12 Cross-cutting topics

Speed budgets. NN/g restates 0.1 s (feels instantaneous), 1 s (flow of thought uninterrupted), 10 s (attention stays), citing Miller 1968 and Card et al. 1991; the article is dated 1993. https://www.nngroup.com/articles/response-times-3-important-limits/. Limits: perceptual thresholds for interactive dialogue, not for batch jobs. EIJA implication: local UI actions under 100 ms; kernel checks (model check, mutation) often exceed 10 s, so they must run as visible asynchronous jobs with an honest RUNNING or UNKNOWN state, never a spinner that implies a pass.

Keyboard-first and KLM. KLM operator times (Wikipedia summary of Card, Moran and Newell 1980): H 0.4 s, P 1.1 s, M 1.35 s, B 0.1 s, K 0.08 to 1.20 s by typist; valid only for expert, error-free, short routine tasks, with about 21 percent RMS error. https://en.wikipedia.org/wiki/Keystroke-level_model. The original CACM paper was not opened, so treat these as MEDIUM.

PREDICTION (KLM, assuming K = 0.2 s, my assumption): reach a visible control with the mouse = M + P + B = 1.35 + 1.1 + 0.1 = 2.55 s. Reach the same command through a palette = M + 2K (chord) + 4K (typed characters) + K (Enter) = 1.35 + 1.4 = 2.75 s. Reach a control three levels deep by mouse = M + 3(P + B) = 4.95 s. Reading: the palette does not beat a visible control, it beats hidden or deep ones, and it wins outright when hands are already on the keyboard (mouse route then adds H, 0.4 s). Do not present these as measured.

Information scent and density. Scent is the user's estimate of value from a link's representation, strengthened by clear labels, accompanying content, page context and prior knowledge (Budiu, NN/g, 2020-02-02). https://www.nngroup.com/articles/information-scent/. Design consequence: dense rows with a label plus two or three metadata accessories (Raycast) beat paragraphs.

Empty states and onboarding. NN/g: communicate status, give learning cues in place, give a direct path to the key task (Kaplan, 2021-09-19). https://www.nngroup.com/articles/empty-state-interface-design/. With Primer, Raycast and VS Code: an empty EIJA panel names what is missing (for example "No journey covers this transition") and offers one verb-first action. Use the real excursion domain, not lorem.

Settings. Patterns seen: search UI over a file (VS Code, Zed); layered overrides (user, project); base keymaps; grouped by owner (Stripe). Recommendation: few settings, sensible defaults, density and colour-vision variant as the two visible ones.

Fitts. T = a + b log2(2D/w); valid for pointing with mouse, trackpad and finger on non-edge targets; screen edges act as "infinite targets" for mouse but not for touch edges (NN/g). https://www.nngroup.com/articles/fitts-law/. Not valid for keyboard routes.

Hick. Decision time increases with the number and complexity of choices (Hick 1952, Hyman 1953); caution against oversimplifying to abstraction (Laws of UX summary). https://lawsofux.com/hicks-law/. Not applied to searchable palettes, where filtering, not scanning, dominates. The formula was not opened this session.

## 3. Open-source components and design systems for a no-build, strict-CSP app

ADR-013 requires no build-time framework and untrusted text only through DOM text nodes. The CSP forbids inline styles and any font.

| Candidate | Licence | Size / form | CSP and no-build evidence | Accessibility evidence | Verdict |
|---|---|---|---|---|---|
| Lit | BSD-3-Clause (docs CC-BY-3.0) | about 5 KB min+gzip; "virtually tool-free" | `css` tag rejects non-`css` expressions; `unsafeCSS` exists for trusted only. Lit uses adoptedStyleSheets in modern browsers and `<style>` elements elsewhere; a nonce request (lit-element #867) is marked done. That adoptedStyleSheets escape `style-src` is UNVERIFIED from a primary source (MDN page silent; only search summaries) | n/a (base class) | adapt: spike, then ADR |
| Web Awesome (successor of Shoelace) | MIT (repo) | 50+ free components, Lit-based, CDN or npm, autoloader needs a base path | Issue #1937 (opened 2026-01-12, still open when read) says animated-image, carousel, progress-ring and slider emit inline `style` attributes, blocking `style-src 'self'`; components using Lit `styleMap` are fine | "Accessibility Built In" (marketing); no audit found | avoid for v1; Shoelace itself is sunset |
| Spectrum Web Components | Apache-2.0 | Lit-based monorepo; 1.5k stars | No CDN or CSP statement found | a11y test config in repo; claims screen reader and keyboard support | avoid (Adobe visual identity; UNVERIFIED CSP) |
| Zag.js | MIT | Machines for React, Vue, Solid, Svelte and Vanilla; 5.2k stars | Vanilla adapter exists (`@zag-js/vanilla`), but a maintainer thread says the vanilla examples broke on 1.0 and exit animations are tricky; CSP not addressed | Modelled on WAI-ARIA authoring practices; Playwright tests (repo claim) | adapt: reference for machines; possible vendoring after a spike |
| Ark UI | not confirmed | 45+ components; React, Solid, Vue, Svelte only | needs a framework | claims WAI-ARIA and keyboard | avoid |
| Radix Primitives | MIT | React only | needs React and a build | follows WAI-ARIA authoring practices, tested in "a wide selection" of assistive technologies (no method stated) | avoid; use its accessibility page as a checklist |
| Primer behaviors | MIT | small TS package; 39 stars | framework-agnostic; needs a built copy | focus trap and focus zone | adapt: spike |
| Primer primitives | MIT | JSON tokens compiled to CSS files; 9 colour themes | plain CSS output | tritanopia and colour-blind themes | adapt: reference or consume CSS |
| Open Props | MIT | 500+ props, 4.0 kB Brotli; CDN import | CSS custom properties only, no inline styles | n/a | adapt for scales (space, easing); its wide palette conflicts with one accent |

Sources: https://lit.dev/docs/ ; https://lit.dev/docs/components/styles/ ; https://github.com/lit/lit-element/issues/867 ; https://developer.mozilla.org/en-US/docs/Web/API/Document/adoptedStyleSheets ; https://shoelace.style/ ; https://webawesome.com/ ; https://webawesome.com/docs/ ; https://github.com/shoelace-style/webawesome ; https://github.com/shoelace-style/webawesome/issues/1937 ; https://github.com/adobe/spectrum-web-components ; https://opensource.adobe.com/spectrum-web-components/ ; https://zagjs.com/ ; https://github.com/chakra-ui/zag ; https://github.com/chakra-ui/zag/discussions/2309 ; https://zagjs.com/overview/faq ; https://ark-ui.com/ ; https://www.radix-ui.com/primitives/docs/overview/accessibility ; https://github.com/radix-ui/primitives ; https://github.com/primer/behaviors ; https://github.com/primer/primitives ; https://open-props.style/.

Adopt versus build, on the evidence:

1. No fully styled library passes all three filters (no framework at build time, `style-src 'self'`, licence). Web Awesome comes closest but has an open CSP bug; fixing it locally means forking.
2. The components EIJA needs most (command palette, tree, split pane, review list, tab set, dialog) are few and central to the product's feel. Owning them lets each be specified as a state machine and tested, which suits a tool whose theme is executable models.
3. Drag-and-drop UML editing is not covered by any headless library found here; it needs its own dossier.
4. Vendoring a prebuilt Lit or Zag file adds a third-party artefact under `resources/web`. That needs a `docs/oss/REGISTER.md` row, a pinned version and hash, and an ADR-013 amendment.
5. Cost of "build" is not measured: no LOC or effort estimate exists yet. Do a one-day spike per candidate before ruling anything in or out.

Fonts and icons (open licences, source URLs):

| Asset | Licence | Source |
|---|---|---|
| Geist Sans, Geist Mono | SIL OFL-1.1 | https://github.com/vercel/geist-font |
| JetBrains Mono | OFL-1.1 (font), Apache-2.0 (source); 8 weights; ligatures optional | https://github.com/JetBrains/JetBrainsMono |
| Inter | OFL-1.1; variable font, tabular numbers, slashed zero | https://github.com/rsms/inter |
| Lucide icons | ISC (parts MIT); 1,600+ SVG | https://github.com/lucide-icons/lucide |
| Codicons | CC BY 4.0 (icons, attribution needed), MIT (code); 1,200+ | https://github.com/microsoft/vscode-codicons |

Rubric note: Inter as a default is on the anti-slop list, so choose a type pair by a decision record, not by default. A system font stack needs no CSP change and no font bytes; a web font needs `font-src 'self'`.

## 4. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| 0.1 s / 1 s / 10 s response-time limits (Miller 1968, Card 1991 cited; 1993 article) | https://www.nngroup.com/articles/response-times-3-important-limits/ | high |
| 120 Hz frame budget is 8.33 ms | https://zed.dev/blog/videogame | high |
| Zed frame times consistently under 4 ms on M1 and M2 in its tests | https://zed.dev/blog/120fps | medium (vendor, Apple only) |
| Superhuman UI target 100 ms, later under 50 ms | https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/ | medium |
| Superhuman "very disappointed" score 22 percent to 58 percent; 40 percent benchmark | same | medium |
| Linear theme variables reduced from 98 to 3 (base, accent, contrast) | https://linear.app/now/how-we-redesigned-the-linear-ui | high |
| Linear redesign took 6 weeks | same | high |
| JetBrains new UI: more than 10 UX studies, more than 2,000 bugs fixed, 87 percent switched | https://blog.jetbrains.com/blog/2024/07/08/the-new-ui-becomes-the-default-in-2024-2/ | medium |
| Geist: 10 colour scales x 10 steps; 31 typography classes; headings 14-72 px | https://vercel.com/geist/colors ; https://vercel.com/geist/typography | medium |
| Stripe: 4.5:1 small text, 3:1 large; five levels apart guarantees 4.5:1 | https://stripe.com/blog/accessible-color-systems | medium |
| WCAG 2.2 1.4.3: 4.5:1 normal text, 3:1 large text (18 pt, or 14 pt bold) | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | high |
| Primer primitives: 9 colour themes | https://github.com/primer/primitives | medium |
| KLM: H 0.4 s, P 1.1 s, M 1.35 s, B 0.1 s; about 21 percent RMS error | https://en.wikipedia.org/wiki/Keystroke-level_model | medium (tertiary) |
| Lit about 5 KB min+gzip | https://lit.dev/docs/ | high |
| Open Props 4.0 kB Brotli, 500+ props | https://open-props.style/ | medium |
| Web Awesome issue #1937 (4 components, inline style, opened 2026-01-12) | https://github.com/shoelace-style/webawesome/issues/1937 | medium (state may have changed) |
| Progressive disclosure: no more than 2 levels | https://www.nngroup.com/articles/progressive-disclosure/ | high |
| Baseline: about 404 words, 3 `<pre>`, 13 font-size values, 19 hex colours | own count of `src/eija_studio/resources/web` | medium (regex) |

## 5. Implications for EIJA

1. Command palette (hypothesis for an HCI-ADR). One key, everywhere. Acts on the current selection; prefixes per entity (term, aggregate, state, journey, test, requirement); shortcut shown beside each result; synonym aliases; user-pinned commands. AI verbs read "Ask AI to propose..." and only create proposals. The palette contains no command that approves or applies; those commands exist only on the owner decision surface. Sources: Linear, Superhuman, JetBrains, Obsidian, Warp.
2. Two review modes, borrowed from Stripe: a side-by-side context drawer (AI proposal next to affected states, journeys, tests, personas, requirements) and a blocking focus surface for the owner decision. The blocking surface shows the exact revision and every UNKNOWN before the action becomes available.
3. Review by meaning as a list of atomic units. Combine Zed's multi-buffer list, Warp's blocks and Raycast's accessories: each Semantic Transaction is one row with a meaning label, a ripple count per model type and a status glyph; the detail pane shows the ripple. Per-unit accept and reject exist as owner actions only; no "always allow" mode for approval or apply, unlike Zed's tool-permission "allowed" setting for tool calls.
4. Speed budgets as tests. Local interactions under 100 ms (PREDICTION target, to be verified by measurement); anything above 1 s shows progress; above 10 s runs as a job with RUNNING then a real outcome. UNKNOWN is a first-class result state next to PASS and FAIL, and it is counted in every summary.
5. Progressive disclosure with a floor. At most two levels; UNKNOWN counts, proof status and blocked reasons stay at level 0. Raw JSON moves behind an explicit "source" view and off the primary screen.
6. Tokens. Generate the theme from base, accent and contrast in a perceptual space, with semantic status hues separate; use role-named steps (Geist style) with far fewer scales; validate WCAG ratios by computation and test against colour-vision variants (Primer ships tritanopia and colour-blind themes). The rubric's "colour is never the only carrier" means every status has a glyph and a word.
7. CSP first. Decide fonts before typography (system stack versus `font-src 'self'`). Move dynamic positions (drag and drop) through `el.style.setProperty` or SVG attributes and test them under the real CSP. Ban inline `style=""` and any `innerHTML` or `unsafeHTML`-style API for untrusted text.
8. Empty states as instruction. Use Primer's three kinds; each names the missing thing in domain words and offers one verb-first action; never flash an empty state before loading (Raycast).
9. Onboarding by doing. A walkthrough of at most a few steps, each with an action; keep the excursion workflow as the sample (VS Code guidance).
10. Learning cost. Palette, `?` shortcut sheet (searchable) and per-command shortcuts are cheap to add; measure discovery in the first user study (Superhuman-style survey question adapted to the change-review task; no results exist yet).

## 6. Gaps and unverified items

- No user study exists; nothing here shows benefit for EIJA users. All KLM numbers are PREDICTION.
- UNVERIFIED: Raycast default hotkey (page text conflicted with prior knowledge); Superhuman internal 50-60 ms target; Zed "2 ms latency" and "0.12 s startup" (appear only in secondary write-ups); Obsidian graph view and Canvas; "Zen of GitHub" list (one summary said 14 aphorisms, a second fetch showed none); Warp agent approval behaviour; Stripe Dashboard shortcuts beyond `?`; Linear list density values.
- Not read: Linear redesign part I, Linear keyboard docs (404), Superhuman help centre (403), JetBrains 2022 announcement (404), WAI-ARIA Authoring Practices, the CACM KLM paper, Fitts 1954, Hick 1952 and the Hick-Hyman formula.
- Web Awesome: bundle size and current state of issue #1937 unverified after the read; free versus Pro boundary not checked in detail.
- Lit and Zag: whether adoptedStyleSheets and positioning code pass `style-src 'self'` needs a test in the real CSP, not documents.
- No search was possible after the shared web-search budget ran out, so competitors outside the named list (Cursor, Figma, Storybook, Mermaid tools) were not examined; UML drag-and-drop and formal-evidence display need separate dossiers.
- Product claims change quickly. Treat each row as of 2026-09-29.

## 7. URLs opened this session (access date 2026-09-29)

Linear: linear.app/now/how-we-redesigned-the-linear-ui ; linear.app/method/introduction ; linear.app/docs/conceptual-model (no relevant content) ; linear.app/docs/search ; linear.app/changelog/2021-03-25-keyboard-shortcuts-help ; figma.com/blog/karri-saarinens-10-rules-for-crafting-products-that-stand-out/
Zed: zed.dev/blog/120fps ; zed.dev/blog/videogame ; zed.dev/docs/command-palette ; zed.dev/docs/key-bindings ; zed.dev/docs/configuring-zed ; zed.dev/docs/ai/agent-panel ; zed.dev/
VS Code: code.visualstudio.com/api/ux-guidelines/{overview,command-palette,walkthroughs} ; code.visualstudio.com/docs/getstarted/userinterface ; code.visualstudio.com/docs/copilot/chat/chat-agent-mode ; code.visualstudio.com/docs/agents/run/review-code-edits
JetBrains: blog.jetbrains.com/blog/2024/07/08/the-new-ui-becomes-the-default-in-2024-2/ ; jetbrains.com/help/idea/new-ui.html ; jetbrains.com/help/idea/searching-everywhere.html
Primer: primer.style/product/getting-started/ ; primer.style/product/getting-started/principles/ and /design-principles/ (no aphorisms) ; primer.style/product/ui-patterns/empty-states/ ; github.com/primer/{primitives,view_components,behaviors,react}
Vercel: vercel.com/geist/{introduction,colors,typography} ; github.com/vercel/geist-font
Stripe: stripe.com/blog/accessible-color-systems ; docs.stripe.com/stripe-apps/{design,patterns} ; docs.stripe.com/dashboard/basics
Raycast: manual.raycast.com ; developers.raycast.com/basics/prepare-an-extension-for-store ; developers.raycast.com/api-reference/user-interface/{list,actions}
Warp: docs.warp.dev/ ; docs.warp.dev/terminal/{blocks,command-palette}
Obsidian: obsidian.md/help/ ; obsidian.md/help/plugins/command-palette
Superhuman: review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/ ; blog.superhuman.com/ ; blog.superhuman.com/how-to-build-a-remarkable-command-palette/
HCI and standards: nngroup.com/articles/{response-times-3-important-limits,information-scent,empty-state-interface-design,fitts-law,progressive-disclosure}/ ; lawsofux.com/hicks-law/ ; en.wikipedia.org/wiki/Keystroke-level_model ; w3.org/WAI/WCAG22/Understanding/contrast-minimum.html ; developer.mozilla.org (style-src; Document/adoptedStyleSheets)
Libraries: lit.dev/docs/ ; lit.dev/docs/components/styles/ ; github.com/lit/lit-element/issues/867 ; shoelace.style ; webawesome.com and /docs/ ; github.com/shoelace-style/webawesome and issues/1937 ; github.com/adobe/spectrum-web-components ; opensource.adobe.com/spectrum-web-components/ ; zagjs.com and /overview/faq ; github.com/chakra-ui/zag and discussions/2309 ; ark-ui.com ; radix-ui.com/primitives/docs/overview/accessibility ; github.com/radix-ui/primitives ; open-props.style
Fonts and icons: github.com/{lucide-icons/lucide, microsoft/vscode-codicons, JetBrains/JetBrainsMono, rsms/inter}
Repo files read: `src/eija_studio/interfaces/http.py` (CSP), `src/eija_studio/resources/web/*`, `AGENTS.md`, `docs/architecture/ARCHITECTURE.md`, `docs/adr/0000-poc-decision-log.md` (ADR-013).
