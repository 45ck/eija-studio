# AI-generated UI "slop": tells, evidence and computable metrics

Research dossier `ai-slop-metrics`, lane `lane/ux-research`. Access date for every URL: 2026-09-29. Status: draft for the HCI-ADR block 0057-0088. Anything labelled PREDICTION is a model output, not a measurement. Anything labelled UNVERIFIED was not confirmed by a page opened in this session and is not built on.

## 0. Decisions first

1. **Adopt a machine-checkable "slop budget"** measured on rendered DOM/CSS per viewport (section 3). Three tiers: HARD (standard- or invariant-derived, must be 0 / pass), BAND (starting hypotheses, calibrated), DIAGNOSTIC (reported, never gating).
2. **Do not ban Inter or any font by name.** Linear, a reference-quality product, documents Inter and Inter Display in its own redesign write-up. The tell is an unexamined default stack, so we gate on family count and on a recorded rationale, not on a typeface.
3. **Evidence quality for "slop" is weak.** Nearly all tell catalogues are practitioner opinion; the two quantitative bodies of work (first-impression research; accessibility of LLM output) measure something adjacent. No study we could open shows that removing the tells improves outcomes for software engineers. That claim needs our own study (section 4.6).
4. **A tension we must state openly:** first-impression research finds low visual complexity *and high prototypicality* score best on aesthetic appeal. Generic layouts are prototypical. Our case against slop rests on expert scanning cost, honest evidence display and differentiation, not on "generic looks worse to everyone".
5. **Calibrate against public reference pages, then report distributions, not a pass/fail score.** With about 10 pages we can only detect very large metric-outcome correlations (section 4.5).

## 1. Scope and method

- **Queries run:** about 30 WebSearch queries (AI-UI slop tells, Wathan/Tailwind indigo, Anthropic frontend-aesthetics guidance, Lindgaard/Reinecke/Tuch/Miniukovich/Fogg/Tractinsky, NN/g on glassmorphism/icons/cards/reading, Linear redesign, homogenisation of LLM-built sites, target-size and contrast standards). The session's WebSearch budget (200) ran out before a planned check of the UI-Bench leaderboard.
- **Pages opened:** listed in the appendix. Where a publisher blocked the fetch (ACM, Taylor & Francis, MDPI, X, web.archive.org all refused), I say so per claim and mark confidence lower. Abstracts seen only in a search-result excerpt are labelled "excerpt".
- **Not done:** no browser was launched; no calibration measurements exist yet. The only measurement in this file is a static regex count of our own baseline CSS/HTML (section 3.3), not a rendered measurement.
- **Untrusted content:** all fetched pages were treated as data. Pages that told readers to do things (install a skill, run a command) were not followed.

## 2. Topics, patterns and verdicts

### 2.1 Practitioner and first-party catalogues of the tells

What it is today: a 2025-2026 genre of blog posts and agent "skills" naming the default look of LLM-generated UIs. Sources are opinion; some say so themselves.

| Tell | Who names it | Evidence quality |
|---|---|---|
| Indigo/purple accent, blue-purple gradient | Wathan post (Aug 2025, via secondary write-up because X returned HTTP 402); 925studios; SmoothUI; Anthropic cookbook | Anecdote. The secondary source states it gives no prevalence measurement. Causal story (Tailwind UI defaults became training data) is plausible, unmeasured. |
| Inter as default face | 925studios; Anthropic cookbook and blog | Anecdote. Contradicted as a *tell in itself* by Linear's use of Inter. |
| Three rounded cards in a row; icon, heading, two lines | 925studios; SmoothUI ("six identical cards"); Hallmark article | Anecdote. |
| Uniform 16px radius and 24px padding everywhere; uniform card heights | mania.design (author says the diagnosis is experiential) | Anecdote, but the only source giving concrete values. |
| Missing empty, loading, error states; everything visible at once | mania.design | Anecdote; overlaps NN/g progressive disclosure. |
| Generic headline copy | mania.design | Anecdote. |
| ALL-CAPS eyebrow above every heading, middle-dot metadata, arrow suffixes, repetitive rounded cards with uniform shadows | Anthropic `frontend-design` SKILL.md (first-party guidance, no evidence attached) | Guidance without data. Our baseline has 10 eyebrow elements in `index.html`. |
| Glassmorphism with neon glow | SmoothUI; NN/g (contrast and readability problems) | NN/g is authoritative on the readability mechanism; nothing shows glass is AI-specific. |

Patterns and why they work as *diagnoses* (not as proven harms):

- **Statistical-centre output ("distributional convergence").** Anthropic's blog and cookbook say models sample the high-probability centre, and that explicit steering improves output. Neither gives metrics; the cookbook shows before/after images only. Verdict **adapt**: use the mechanism as a hypothesis for why *our* AI-authored UI code needs a machine gate, since prompts alone are unmeasured.
- **Decoration without meaning.** Ties to the coherence principle / seductive-details effect: interesting but irrelevant material impairs recall in learning tasks (2023 online replication, n=248, recall only, not transfer; effect is in learning materials, not software UIs, so this is an analogy). Verdict **adapt**.
- **Containers that do not encode grouping.** NN/g on common region: borders and fills are a strong grouping cue, and unnecessary ones "increase complexity without improving clarity"; NN/g on cards: avoid for search, comparison and homogeneous content. Baymard's dashboard testing found cards hard to navigate when styling was inconsistent. Verdict **adopt** as the principle behind the container budget; the number 12 is still ours.
- **Decorative or unlabelled icons.** NN/g icon usability: universal icons are rare, a visible text label should accompany the icon, hover-only labels raise interaction cost. Verdict **adopt**.
- **Anti-slop tools with hidden gates.** The Hallmark write-up claims 65 binary gates but lists none and offers no evaluation; the tool itself was not opened. Verdict **avoid** as a source; **adapt** the idea (binary pre-emit checks) with published, versioned rules.

### 2.2 Benchmarks and studies specific to AI-built UIs

| Item | What it is | Finding relevant to us | Limits |
|---|---|---|---|
| UI-Bench (arXiv 2508.20410) | 10 AI text-to-app tools, 30 prompts, 300 sites, 4,000+ expert pairwise judgments, TrueSkill-derived ranking | Visual quality of AI output is measurable by expert pairwise comparison with confidence intervals; prompts, framework and leaderboard released | Abstract only; generated-site dataset "to be released soon" at posting; no tell-level analysis |
| Shin et al., "Interrogating Design Homogenization in Web Vibe Coding" (arXiv 2603.13036; Reinecke is a co-author) | Sociotechnical risk analysis | Frictionless generation can worsen homogenisation; proposes "productive friction" | No quantitative results in the abstract; states it is unclear how homogenisation extends to structural design |
| A11YN (arXiv 2510.13914) | Aligns LLMs for accessible UI code | Frontier models still produce inaccessible markup (reported inaccessibility rates 0.27 GPT-4.1, 0.29 Claude Sonnet 4; missing landmarks, weak contrast, unlabelled links); axe-core-based | Automated axe only; definition of "rate" not confirmed from the page I read; synthetic training data |
| DeGenTWeb (arXiv 2605.00087) | Detects LLM-dominant *content* sites | Shows LLM-dominant sites are prevalent and growing | About text, not visual design; detectors weak at low false-positive rates |

Verdict: **adopt** UI-Bench's method (expert pairwise + interval estimates) as the external criterion for validating our metrics (section 4.4), if the rated sites are actually released (UNVERIFIED). **Adopt** accessibility metrics as HARD gates because they are the best-evidenced failure of LLM UI output.

### 2.3 Aesthetics, trust and first impressions

What it is: a 25-year literature on how fast and how strongly appearance shapes judgement. All of it studies general-population reactions to websites or ATM-like systems, not engineers using a workspace over hours.

| Study | Design | Result | Why it matters / limit |
|---|---|---|---|
| Lindgaard et al. 2006 (excerpt only; publisher 403) | 3 studies, homepages shown 50 ms and 500 ms | Appeal ratings at 50 ms correlate highly with 500 ms | Judgements form before reading; says nothing about *which* features. |
| Tuch et al. 2012 (Google Research page) | 119 screenshots varying visual complexity (VC) and prototypicality (PT); 17 ms to 1000 ms | VC affects aesthetics even at 17 ms; PT effect weaker and later; low VC + high PT rated highest | Supports a complexity budget. Also implies generic (prototypical) can be liked: the tension in section 0. |
| Reinecke et al. 2013 (Harvard DASH abstract) | 548 volunteers rated 450 sites | Complexity and colorfulness models plus demographics explain about half the variance in 500 ms appeal | Direct precedent for computed complexity/colorfulness features. |
| Miniukovich & De Angeli 2015 (excerpt only; ACM 403) | 8 automatic metrics on 62 webpages and 53 iPhone apps, 150 ms and 4 s | Best regression explained up to R2 .49 (pages), .32 (apps); one metric alone far weaker (R2 .11) | Metrics work only in combination; exploratory; no thresholds. |
| Fogg et al. 2003, figures via Wikipedia summary | 2,684 people, 100 sites, 10 categories | 46.1% of comments cited visual appeal | Self-reported comments on credibility, not behaviour; 2002 sites. |
| Tractinsky et al. 2000 (OUP abstract) | ATM surrogate, before/after use | Aesthetics changed post-use perceived usability; actual usability did not | Halo effect; lab task; caution: it can mask problems (NN/g). |
| Kurosu & Kashimura 1995 via NN/g | 26 ATM UI variants, 252 participants | Appeal correlated more with perceived than actual ease of use | Second-hand via NN/g. |
| NN/g "How little do users read" (2008; data from 2005) | 45,237 page views after cleaning | At most 28% of words read on an average page, 20% more likely; about 50% on pages of 111 words or fewer; about 4.4 s per 100 added words | University-employee sample; not eyetracking; general web, not workspaces. |

Patterns and why: (1) appearance is judged before reading (Lindgaard, Tuch) so first-screen structure matters more than copy; (2) complexity is the earliest-acting factor (Tuch) so a container/type/colour budget is a reasonable proxy; (3) reading is scarce (NN/g) so prose on the primary screen is expensive; (4) beauty can hide defects (NN/g aesthetic-usability, Tractinsky), which for a *verification* tool is a hazard: a polished UI must not make UNKNOWN look like PASS. Verdict: **adopt** (1)-(3) as rationale for budgets, **adopt** (4) as a design constraint.

### 2.4 Reference-quality products and design systems (calibration candidates)

| Product | Verified today | Pattern | Verdict |
|---|---|---|---|
| Linear (`linear.app/now/how-we-redesigned-the-linear-ui`, 2024-03-28) | Page opened | LCH theme generation; theme variables cut from 98 to 3 (base, accent, contrast); Inter Display for headings, Inter for body; work on alignment of labels, icons, buttons; reduced noise in sidebar, tabs, headers, panels | **Adopt**: three-input theme model and alignment discipline; no claim of measured benefit |
| GitHub Primer typography | Page opened | Tokens bundle size, family, weight, line-height; line-height on a 4px grid; lines around 80 characters or fewer | **Adopt** the 4px rhythm as an alignment check |
| Material 3 type scale (`material-web` tokens file) | Tokens file opened | 5 roles x 3 sizes = 15 size tokens | **Adapt**: a whole system may define many sizes; the budget applies per viewport, not per system |
| Aalto Interface Metrics (MIT) | GitHub README opened | Selenium/Chrome screenshot pipeline, verified aesthetics/usability metrics | **Adapt**: metric names and validation precedent; we compute from DOM instead of pixels where possible |
| axe-core (MPL-2.0) | README opened | WCAG rule engine; `color-contrast` unsupported in JSDOM | **Adopt** in a real browser; whether it has a 2.5.8 target-size rule is UNVERIFIED from the README |

### 2.5 Standards used as HARD gates

WCAG 2.2: text contrast at least 4.5:1 (3:1 large); UI components and graphics at least 3:1; colour not the only means of conveying information; target size minimum 24 by 24 CSS px with a spacing exception (a 24 px circle centred on each undersized target must not intersect another target); enhanced size 44 by 44. WebAIM Million 2026: 95.9% of home pages had detected WCAG 2 failures, 56.1 errors per page, low-contrast text on 83.9% of pages. Verdict: **adopt**.

## 3. From tell to metric

### 3.1 Measurement contract

Playwright (or any single Chromium) at 1440x900, DPR 1, plus 1280x720; fonts settled; injected read-only script; `getComputedStyle` and `getBoundingClientRect`. "Visible in the primary viewport" means the box intersects the viewport, is not `display:none`, `visibility:hidden`, `hidden`, closed `<details>` or clipped to zero, and opacity above 0. Markup hooks needed from the Studio: `data-eija-source` (artifact id a value came from), `data-eija-state` (state a chip encodes), `data-eija-model` (text that is model content, not chrome). Untrusted text stays in DOM text nodes (ADR-013), so word counts read `textContent`.

### 3.2 Metric table

Tier: H = HARD, B = BAND (starting hypothesis, calibrated), D = diagnostic. Thresholds are hypotheses unless marked.

| # | Tell | Metric (computed) | Threshold | Tier | Justification and source | Evidence quality |
|---|---|---|---|---|---|---|
| M1 | Over-explaining copy, low density of meaning | Visible chrome words (excluding `data-eija-model`) per viewport; prose words = words in text nodes of 8 or more words | chrome at most 120; prose at most 30 | B | NN/g 20-28% read; 111-word pages about 50% read. Task starting target 120. Prose cap is ours. | Medium for scarcity; low for numbers |
| M2 | Card mania, box-around-everything | Containers per viewport: element with border on 2 or more sides, or fill differing from nearest opaque ancestor, or shadow; area at least 2,500 px2; at least 2 child elements. Excludes controls and single-side rules | at most 12 | B | NN/g common region and cards; Miniukovich clutter as combined-metric precedent | Medium principle; number ours |
| M3 | Card in card | Max nesting depth of containers; count of containers whose nearest container ancestor is also a container with radius above 0 | depth at most 3; nested cards 0 | B / H | NN/g common region ("decoration increases complexity"); Baymard | Medium |
| M4 | Type sprawl | Distinct computed font sizes (0.5 px buckets), weights, families, text colours (ΔE00 below 2 merged) per viewport | sizes at most 6; weights at most 3; families at most 2 sans/serif plus 1 mono; text colours at most 5 including status | B | Tuch/Reinecke: complexity matters early; Material's 15 tokens show system size is not the per-screen size | Low-medium |
| M5 | Colour sprawl, default palette | Accent hue clusters (OKLCH chroma at least 0.04, status hues excluded); accent hue window flag | 1 accent hue; advisory flag when accent hue is in 270-295 degrees with chroma at least 0.20 | B / D | Window anchored to Tailwind v4.3 indigo-500 `oklch(58.5% 0.233 277.117)` and violet-500 `oklch(60.6% 0.25 292.717)`; window itself is a heuristic | Low |
| M6 | Decorative gradients | Count of computed `background-image` containing `gradient(`, plus `background-clip:text` | 0 (data visualisations marked `data-eija-viz` exempt) | H | Rubric; no study of harm | Low (rule, not finding) |
| M7 | Glassmorphism | Count of `backdrop-filter`, `filter: blur`, and text over a background with alpha below 1 | 0 | H | NN/g: readability and contrast failures on translucent layers | Medium |
| M8 | Elevation sprawl | Distinct `box-shadow` values on visible elements | at most 2 | B | Task rubric; Material/Primer levels to be read in calibration | Low |
| M9 | Uniform radius/padding | Distinct radii and padding values; share of containers with radius 12 px or more | diagnostic only | D | mania.design gives values but no evidence; uniformity, not size, is the claimed tell | Low |
| M10 | Icon-per-bullet, decorative icons | Decorative icons (aria-hidden or no action) per text block; runs of 3 or more consecutive sibling items each with a leading icon or emoji; emoji code points in visible text; icon-only controls without visible label | runs 0; emoji 0; unlabelled icon-only controls 0 unless on an allow-list of universal icons; decorative icons per text block at most 0.15 | H / B | NN/g icon usability (labels visible, universal icons rare); seductive-details analogy | Medium (labels), low (ratio) |
| M11 | Centred hero + three-feature grid | Share of chrome words in `text-align:center`; count of rows of 3-6 sibling containers equal in width and height (within 2 px) each holding icon + heading + at most 2 lines | centred share at most 20%; equal-sibling rows 0 in workspace views | B | Practitioner catalogues; NN/g cards ("when not to use") | Low |
| M12 | Gratuitous badges and eyebrows | Chips (height under 32 px, at most 3 words, pill radius) lacking `data-eija-state`; uppercase or letter-spaced label elements | unbound chips 0; eyebrows at most 1 | H / B | Chips must encode state (invariant: nothing decorative). Eyebrow limit from Anthropic SKILL.md guidance | Low |
| M13 | Fake or placeholder data | Numbers, dates and names in visible text lacking a `data-eija-source` ancestor; regex hits on lorem, "John Doe", "Acme", `example.com`, round-number claims | 0 unsourced; 0 hits | H | EIJA invariant (view generated from or checked against code); practitioner note on placeholder stats | Invariant-derived |
| M14 | Generic marketing copy | Blocklist hits (e.g. "all-in-one", "without limits") | 0 | D | mania.design gives two examples only; a blocklist is a weak proxy | Low |
| M15 | Contrast | axe `color-contrast` and own compositor; incomplete results listed | 4.5:1 text, 3:1 large text and UI; **incomplete counts as UNKNOWN, never pass** | H | WCAG 1.4.3, 1.4.11; WebAIM 83.9% low-contrast base rate | High |
| M16 | Colour as sole carrier | Elements coloured by a status token with no text, glyph or shape difference | 0 | H | WCAG 1.4.1 | High |
| M17 | Target size | Interactive boxes under 24x24 not excused by spacing; primary actions under 32 px height | 0; primary at least 32 | H / B | WCAG 2.5.8 (24 px) opened; 32 px is ours. Fitts PREDICTION below | High (24), low (32) |
| M18 | Alignment and rhythm | Distinct left edges (1 px tolerance) of text blocks; share on the 6 most common edges; share of margins, paddings, gaps that are multiples of 4 px | on-edge share at least 0.85; 4 px share at least 0.9 | B | Miniukovich grid quality (excerpt); Ngo alignment measures (excerpt); Primer 4px grid. Tree indentation legitimately adds edges, so measure per pane | Low-medium |
| M19 | Whitespace / ink | Share of viewport area covered by text, glyph and control boxes; share of pixels differing from the modal background | no fixed threshold; band = calibrated P10-P90 | B | Miniukovich white-space metric (excerpt). Two-sided: too low is the low-density tell, too high is clutter | Low |
| M20 | Visual clutter, colorfulness | Screenshot-based edge density or feature congestion; Hasler-Süsstrunk colourfulness | reported vs reference distribution | D | Rosenholtz 2007 (excerpt); Reinecke 2013; colourfulness formula per PyImageSearch summary of Hasler & Süsstrunk 2003 | Medium (validated on photos or web pages, not workspaces) |
| M21 | UNKNOWN visibility | Count of UNKNOWN items in the model versus count rendered with an explicit UNKNOWN label and non-colour cue | equal | H | EIJA invariant | Invariant-derived |

Fitts PREDICTION (relative pointing difficulty only; Shannon form `MT = a + b log2(A/W + 1)`, MacKenzie 1992; `a`, `b` are device-specific and not supplied here). At amplitude A = 400 px, ID = 3.34 bits for W = 44, 3.76 for 32, 4.14 for 24, 4.70 for 16. Going from 32 to 16 px adds 0.95 bit, about a 25% rise in ID. Validity: one-dimensional pointing, W along the movement axis, mouse; touch, 2D targets and keyboard-first work are outside it. Verdict: 24 px is a floor, not a comfort target.

### 3.3 Worked example: the current baseline (static count, not rendered)

Regex count over `app.css` and `index.html` in this worktree, 2026-09-29. It shows the metrics discriminate, and that the baseline's problem is not the gradient tell.

| Measure | Baseline value (whole file, all tabs) |
|---|---|
| Distinct font-size declarations | 14 (13 fixed values 10 to 36 px plus one `clamp(38px,4vw,58px)`) |
| Distinct font weights / letter-spacing values | 7 / 7 |
| Distinct hex colours | 19 |
| Gradients, shadows, blur | 0 / 0 / 0 |
| Distinct radii | 6 (7, 8, 10, 12, 30 px and a 14 px variable) |
| Eyebrow-labelled elements | 10 |
| `.panel` sections | 6 |
| Words in static body text (scripts and `<pre>` removed, hidden tabs included) | 397 |

Reading: gradient/glass gates would pass; M1, M4, M12 would fail. Viewport-scoped numbers need a rendered run.

## 4. Calibration protocol

### 4.1 Sample

Pre-register, before measuring, a list of at least 10 public, login-free pages in two strata, plus controls.

- **Documentation/marketing (comparable to first screens):** candidates whose `robots.txt` I opened today and which permit generic crawlers on public pages: Linear public pages, MDN, Stripe docs. GitHub's `robots.txt` allows marketing pages and blocks `/tree/` and similar repo paths for crawlers; a single human-speed load of a repository root is ordinary browsing but must be recorded as a judgement call.
- **App-like public tools (closest to a workspace):** candidates not yet verified: Compiler Explorer, diagrams.net app, Excalidraw, Mermaid Live Editor, regex101, TypeScript Playground. Each needs a `robots.txt` and terms check before use. UNVERIFIED.
- **Controls:** (a) our baseline Studio; (b) 5 synthetic "default-prompt" fixture pages we author, labelled synthetic (tests discriminative ability only, and is circular by construction).

"Reference quality" is an assumption based on first-party design write-ups, not an independent quality rating. State it as such.

### 4.2 Procedure

One Chromium at a time; one page at a time; a single navigation and settle wait, no login, no form input, no scrolling beyond the first viewport; light and dark scheme if the page honours `prefers-color-scheme`. Record URL, UTC time, browser version, viewport, DPR, HTML byte hash, banner state. Run each page twice to measure test-retest drift. Store **only numbers and metadata** in the repo, not screenshots or copied markup of third-party pages.

### 4.3 Reporting

Publish per-page values and distributions (min, P10, median, P90, max), never a single "score". A threshold is accepted when at least 80% of references comply (a rule we propose, not from the literature); otherwise we either move the threshold or record the deviation as an HCI-ADR. Report failures to measure (blocked, banner-occluded, canvas-only pages where DOM metrics are blind) as NOT_RUN, not as passes. Version the metric script and the sample list; a change in either resets the calibration.

### 4.4 Validity checks, in increasing cost

1. **Discriminative:** synthetic fixtures must trip the intended metrics (circular; catches implementation bugs only).
2. **Convergent:** if UI-Bench's rated sites and judgements are released, test whether a composite of M1-M20 tracks expert pairwise rank. UNVERIFIED that the data is available.
3. **Human:** 50 ms and 500 ms appeal ratings plus 5-task engineer sessions on baseline versus proposed, following the Lindgaard and Tuch paradigms; task time, error and comprehension measures; UNKNOWN-reading accuracy as an EIJA-specific outcome. Protocol only; no results exist.

### 4.5 What the sample can and cannot show (arithmetic PREDICTION)

Correlating a metric with a rating across pages needs pages as the unit of analysis. Using the Fisher-z approximation with alpha .05 and power .80: 10 pages detect only |r| of about 0.79 or larger; detecting r = 0.3 needs about 85 pages. So a 10-page calibration yields **descriptive bands only**, not evidence that the metrics predict quality.

### 4.6 Study design for the user-benefit claim

Within-subject, counterbalanced baseline and proposed Studio, engineers as participants, excursion-workflow tasks, pre-registered outcomes (time on task, wrong-decision rate on UNKNOWN items, 500 ms appeal, SUS-style usability). No benefit is claimed until it runs.

## 5. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| Users read at most 28% of words on an average page, 20% more likely; about 50% on pages of 111 words or fewer | NN/g "How little do users read" (2008; 45,237 page views; 2005 data) | High for the study, medium for transfer to workspaces |
| About 4.4 s of extra visit time per 100 words added | same | Medium |
| 46.1% of 2,684 participants' credibility comments cited visual appeal (finance 54.6%, health 41.8%) | Wikipedia summary of Stanford study; ACM original 403 | Medium |
| 548 raters, 450 sites; complexity + colorfulness + demographics explain about half of variance in 500 ms appeal | Reinecke et al. 2013, Harvard DASH | High |
| 119 screenshots; complexity effect at 17 ms; low complexity + high prototypicality highest appeal | Tuch et al. 2012, Google Research page | High |
| 8 metrics, 62 webpages, 53 apps; R2 up to .49 (pages), .32 (apps); single metric R2 .11 | Miniukovich & De Angeli 2015, search excerpt | Medium |
| UI-Bench: 10 tools, 30 prompts, 300 sites, 4,000+ expert judgments | arXiv 2508.20410 abstract | High for the abstract |
| 95.9% of home pages had WCAG 2 failures; 56.1 errors per page; low contrast 83.9% | WebAIM Million 2026 | High |
| Frontier LLM inaccessibility rates 0.27 (GPT-4.1) and 0.29 (Claude Sonnet 4) | A11YN, arXiv 2510.13914 | Medium (metric definition unread) |
| Tailwind v4.3 indigo-500 = oklch(58.5% 0.233 277.117); violet-500 = oklch(60.6% 0.25 292.717) | tailwindcss.com/docs/colors | High |
| Linear cut theme variables from 98 to 3 | linear.app/now/how-we-redesigned-the-linear-ui | High |
| Material 3 type scale defines 15 size tokens (5 x 3) | material-web tokens file | Medium (distinct px values unread) |
| WCAG 2.2: 24x24 CSS px minimum target; 4.5:1 text; 3:1 non-text | W3C WCAG 2.2 and Understanding pages | High |
| 252 participants, 26 ATM variants: appeal tracked perceived more than actual ease of use | Kurosu & Kashimura via NN/g | Medium (second-hand) |
| Seductive-details replication n=248; recall harmed, transfer not | PMC10176302 | High for the study, low for UI transfer |

## 6. Implications for EIJA

1. Ship a `slop-budget` script (DOM/CSS, read-only) and run it on every Studio screen at 1440x900 and 1280x720. HARD metrics fail the gate; BAND metrics print the reference distribution beside our value.
2. Add three markup hooks to the Studio (`data-eija-source`, `data-eija-state`, `data-eija-model`). They turn the "no fake data, no decorative chip, UNKNOWN visible" invariants into checkable rules (M12, M13, M21).
3. Treat gradient, blur and glass as absent by construction (M6, M7): a zero-count rule is cheaper than a debate, and NN/g documents the contrast risk.
4. Replace the baseline's 10 eyebrows, 14 font sizes and 7 weights with one type scale; the largest measured baseline problems are text volume and type/container sprawl, not gradients.
5. Label icon-only controls and never use icons as bullets; keep a short allow-list of universal glyphs.
6. Do not let polish mask uncertainty: the aesthetic-usability effect can hide defects, so UNKNOWN needs a non-colour, high-contrast cue that passes M15 and M16.
7. Record a rationale for type choice in an HCI-ADR instead of banning Inter. Use Linear's three-input theme model (base, accent, contrast) as a token-design precedent.
8. Run the calibration, but publish it as bands. Do not claim the metrics predict quality until a study with enough pages or participants exists.
9. Ask for hooks where the metric is blind: canvas-rendered UML must expose an accessible tree or a data-attribute layer, otherwise M1-M12 read zero on the most important surface.
10. Plan the 50 ms / 500 ms and task study early; the first-impression literature says appearance is judged before reading, so the study must include the first screen.

## 7. Gaps and unverified items

- **No AI-specific evidence of harm.** No opened source measures that the tells reduce trust, speed or accuracy for developers. Prevalence of indigo, Inter or three-card grids in AI output is unmeasured in the sources I opened.
- **UNVERIFIED (blocked or excerpt-only):** Lindgaard 2006 correlation values; Miniukovich 2015 body text and thresholds; Ngo et al. 2003 measures; Rosenholtz 2007 details; Fogg 2003 original; Harp & Mayer 1998 original; Tuch et al. 2023 prototypicality-trust paper; MDPI paper on visual complexity of generative-AI-designed UIs; Wathan's post (secondary only); NN/g 1997 scanning figures.
- **Claims seen in search summaries and not used:** an NN/g "2026 State of UX" statement about glass effects (not on the NN/g glassmorphism page I opened); "1.7x issues, 2.74x vulnerabilities" for AI code (SmoothUI; source not checked); Hallmark's 65 gates (product not opened).
- **Not opened:** Hallmark tool, Anthropic frontend-design skill repository listing beyond SKILL.md, UI-Bench leaderboard, any Cursor/Lovable/v0/Bolt product pages (out of scope for this dossier; covered by other dossiers if assigned).
- **Population mismatch:** public pages are marketing/docs; the Studio is an authenticated workspace. App-like public tools narrow the gap but do not close it.
- **Metric blind spots:** canvas content, images of text, third-party iframes, and text in shadow DOM require explicit handling; axe's `color-contrast` limits on JSDOM mean we must use a real browser.
- **Open question:** whether to weight M1-M20 into a composite. Recommendation: no, until validity check 2 or 3 exists.

## Appendix: URLs opened (access date 2026-09-29)

Opened and read: claude.com/blog/improving-frontend-design-through-skills; platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics; raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md; arxiv.org/abs/2508.20410; arxiv.org/abs/2609.03918; arxiv.org/abs/2603.13036; arxiv.org/abs/2605.00087; arxiv.org/html/2510.13914v1; dash.harvard.edu/entities/publication/73120378-cc85-6bd4-e053-0100007fdf3b; research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/; academic.oup.com/iwc/article-abstract/13/2/127/898608; en.wikipedia.org/wiki/Stanford_Web_Credibility_Project; nngroup.com/articles/{how-little-do-users-read, glassmorphism, icon-usability, cards-component, common-region, aesthetic-usability-effect}; nngroup.com/videos/managing-visual-complexity; linear.app/now/how-we-redesigned-the-linear-ui; mania.design (spot-the-slop post); 925studios.co/blog/ai-slop-design-tells; smoothui.dev/blog/ai-design-slop; dev.to/rams901 Hallmark post; prg.sh Purple Gradient post; w3.org/TR/WCAG22; w3.org/WAI/WCAG22/Understanding/target-size-minimum.html; webaim.org/projects/million; baymard.com/blog/cards-dashboard-layout; pyimagesearch.com colorfulness post; github.com/aalto-ui/aim; github.com/dequelabs/axe-core; primer.style/foundations/typography; raw.githubusercontent.com/material-components/material-web/main/tokens/_md-sys-typescale.scss; pmc.ncbi.nlm.nih.gov/articles/PMC10176302; ixdf.org/literature/topics/glassmorphism; tailwindcss.com/docs/colors; yorku.ca/mack/hci1992.html; robots.txt of linear.app, developer.mozilla.org, docs.stripe.com, github.com.

Refused or empty (claims from these are excerpt-only or UNVERIFIED): x.com (402), tandfonline.com (403), dl.acm.org (403), academia.edu (403), mdpi.com (403), web.archive.org (blocked), persci.mit.edu (expired certificate), m3.material.io and semanticscholar.org (no content), cris.bgu.ac.il (404), dev.to/alanwest (404).
