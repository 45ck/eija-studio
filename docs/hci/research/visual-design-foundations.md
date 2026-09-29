# Visual design foundations: colour, type, layout, motion, icons, tokens

Dossier: `visual-foundations`. Lane: `lane/ux-research`. Access date for every URL: 2026-09-29.
Status: research input for HCI-ADRs 0057-0088. Nothing here is a decision yet.

Labels used below: **MEASURED** = computed by a script I ran this session on the cited data or files. **PREDICTION** = model output, not a user result. **UNVERIFIED** = not opened or not confirmable this session; nothing is built on it. No user study has been run; no claim of user benefit is made.

## 1. Scope and method

**Question.** Which colour, type, spacing, motion, icon and token foundations let EIJA Studio look and feel like a serious engineering tool, under the anti-slop rubric and the existing constraints (no build framework, ADR-013; strict CSP)?

**What I did.**

- About 45 pages opened with WebFetch (W3C specs, MDN, GitHub repos and READMEs, design-system sources, vendor pages). Full list in section 7.
- Downloaded the variable/regular TTFs of 10 font candidates from `google/fonts` (OFL builds) into `.tmp/fonts/` and measured glyph coverage, features, and WOFF2 size with fontTools 4.56.0.
- Implemented WCAG 2.x contrast, APCA 0.0.98G (constants read from the `apca-w3@0.1.9` source on unpkg, then checked: black on white gives Lc 106.0 and white on black gives Lc -107.9, matching the published reference values), OKLab/OKLCH, and Machado 2009 CVD simulation (matrices checked against the authors' page). Scripts stay in `.tmp/` (gitignored); results are quoted here.
- Read the baseline `app.css`, `index.html` and the CSP in `interfaces/http.py`.

**Not accessible.**

- WebSearch budget for the session was exhausted at 200 calls, so I could not run further searches after the first pass.
- Material 3 and Carbon's own docs sites are client-rendered and returned no content; I read Carbon's source docs (`carbon-website` repo) and Material's token source (`material-web` repo) instead.
- Nature Methods (Wong 2011) redirected to a login handshake; PubMed gave a cookie wall; ScienceDirect returned 403.
- The NEI page has no prevalence numbers.

## 2. Findings by topic

Each block: what it is today, patterns and why they work, verdict for EIJA. Principle names (proximity, redundancy, Fitts, Nielsen limits) are standard HCI vocabulary; I did not open a primary source for the laws in this dossier except where a URL is given.

### 2.1 Colour spaces: OKLab/OKLCH, CSS Color 4/5

**Today.** Oklab (Ottosson) is a perceptual space with L, a, b; OKLCH is its polar form. CSS Color 4 is a Candidate Recommendation Draft dated 2026-09-26 and defines `oklch()`, `oklab()` and a gamut-mapping algorithm in OKLCH with a JND of 0.02 dE_OK. CSS Color 5 is a Working Draft (2026-09-13) with relative colour syntax, `color-mix()` (default space Oklab), `light-dark()`, and `contrast-color()`. MDN lists `oklch()` as Baseline widely available (since May 2023) and `light-dark()` as Baseline 2024 (May 2024).

| Pattern | Why it works | Source |
|---|---|---|
| Author every colour token in OKLCH; keep hue fixed, vary L for steps | L tracks perceived lightness, so equal L steps read as equal steps; contrast is predictable from L. Supports Gestalt similarity and redundancy without hue drift. | Ottosson; CSS Color 4 |
| Derive states (hover, pressed, muted) with relative colour or `color-mix()` in oklab | Fewer literal values, so fewer tokens to audit | CSS Color 5 |
| Gamut-map with the spec algorithm, never hard-clip | Keeps hue near-constant when P3 chroma is mapped to sRGB | CSS Color 4 |
| Pair every OKLCH token with a 6-digit hex fallback in the exported token file | DTCG allows an optional `hex` field | DTCG Color 2025.10 |

**Limits.** Ottosson states Oklab lightness and chroma predictions were fitted to CAM16 output, not to new experiments, so it is comparable to CAM16-UCS, not proven better. CSS Color 5 is still a Working Draft; features I rely on (`from`, `color-mix`) are shipping but the spec can change. `contrast-color()` detail was truncated in my fetch: UNVERIFIED.

**Verdict: adopt** OKLCH as the source of truth, ship hex fallbacks.

### 2.2 Contrast: WCAG 2.2, APCA, WCAG 3

**Today.** WCAG 2.2 is a W3C Recommendation (2024-12-12): text 4.5:1 (AA), 3:1 large text, 7:1 AAA; non-text 3:1; target size minimum 24x24 CSS px (2.5.8); colour must not be the only means of conveying information (1.4.1). WCAG 3.0 is a Working Draft (2026-09-10); its own text says the contrast algorithm is "yet to be determined" and it may be obsoleted at any time. APCA describes itself as a candidate for WCAG 3, is not adopted, and its reference code carries a restricted licence (`apca-w3` package licence field: "Limited W3 License"; the SAPC-APCA repo reports NOASSERTION on GitHub; the readme badge says Beta Non-Com).

| Pattern | Why it works | Source |
|---|---|---|
| Gate on WCAG 2.2 ratio (normative), report APCA Lc as advisory | WCAG 2.2 is the only citable conformance basis today | WCAG 2.2, WCAG 3 draft |
| Use APCA to catch dark-mode failures the ratio misses | The APCA authors argue 2.x overstates dark-colour contrast; my numbers agree in direction (see 2.4) | APCA in a Nutshell |
| Published APCA Lc guidance as design targets: Lc 75 minimum body, Lc 90 preferred, Lc 45 large, Lc 30 spot text, Lc 15 dividers | Gives a second, size/weight-aware check for small mono text | APCA in a Nutshell |
| Never shrink hit targets below 24x24 px; keep dense-mode targets at 24 and default at 32 | Fitts: index of difficulty falls as width grows; 2.5.8 sets the floor | WCAG 2.2 Understanding 2.5.8 |

**Limits.** APCA Lc values above are the authors' guidance, unratified. A licence review is needed before vendoring any APCA code; implementing the published formula from scratch still needs legal sign-off (UNVERIFIED: I did not read a licence text).

**Verdict: adopt** WCAG 2.2 as gate; **adapt** APCA as advisory metric without shipping its code until licensing is clear.

### 2.3 Colour vision deficiency and safe palettes

**Today.** Okabe-Ito (Color Universal Design, 2002) is an eight-colour palette designed to be distinguishable across CVD types. Hex codes read from a secondary page: #000000, #E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00, #CC79A7. The original Okabe-Ito page lists the hues (vermilion, yellow, orange, bluish green, sky blue, blue, reddish purple). Viridis is designed for perceptual uniformity, CVD legibility and greyscale printing (R package documentation). ColorBrewer provides sequential, diverging and qualitative schemes with a "colorblind safe" filter, 3 to 12 classes, © Cynthia Brewer, Mark Harrower, Penn State.

Prevalence: the Okabe-Ito authors state 8% of Caucasian, 5% of Asian, 4% of African males are red-green colour blind; Colour Blind Awareness states about 1 in 12 men (8%) and 1 in 200 women.

| Pattern | Why it works | Source |
|---|---|---|
| Seed hues from Okabe-Ito, then re-tune L per surface | Hues are separable for all three dichromat types at the palette level | Okabe-Ito page; hex list |
| Sequential data (coverage, mutation score) uses a viridis-like or ColorBrewer sequential ramp | Monotonic lightness lets value be read without hue | Viridis vignette; ColorBrewer |
| Every status has three redundant channels: hue, glyph shape, text label | Redundancy gain; WCAG 1.4.1 | WCAG 2.2 |
| Red/green pair is never the only difference | See measurement below | MEASURED |

**MEASURED (own script, Machado 2009 severity 1.0, dE_OK).** For the current baseline pair `--green #236755` vs `--danger #9f382b`: normal 0.204, protan 0.080, deutan 0.082, tritan 0.259. One JND is 0.02 (CSS Color 4), so the pair stays above JND but loses about 60% of separation for protan/deutan. That is a hue-only check; it does not model text reading or small-area effects.

**Verdict: adopt** Okabe-Ito seed hues plus mandatory glyph+label redundancy; **adapt** Viridis/ColorBrewer for sequential encodings only.

### 2.4 Semantic status palette (PREDICTION)

EIJA needs at least: PROVED/PASS, REFUTED/FAIL, UNKNOWN, STALE/PENDING, and AI-PROPOSED (accent). UNKNOWN must never look like a softened pass or fail. Candidate tokens, chroma held near the Okabe-Ito seed, L chosen as the lowest that reaches 4.5:1 against the surface. Surfaces: light #FAFAFA (oklch 0.985 0 0), dark #121417 (oklch 0.19 0.008 260).

| Role | Light text token | WCAG / APCA (light) | Dark text token | WCAG / APCA (dark) |
|---|---|---|---|---|
| proved | oklch(0.544 0.114 165) #00845F | 4.51 / Lc 66.5 | oklch(0.575 0.121 165) #008F67 | 4.50 / Lc -34.6 |
| refuted | oklch(0.572 0.156 48) #BE5400 | 4.51 / Lc 66.5 | oklch(0.607 0.165 48) #CE5C00 | 4.53 / Lc -34.8 |
| stale | oklch(0.562 0.118 77) #9B6A00 | 4.52 / Lc 66.6 | oklch(0.597 0.125 77) #A87400 | 4.54 / Lc -34.8 |
| accent | oklch(0.556 0.130 244) #1579B9 | 4.50 / Lc 66.5 | oklch(0.589 0.130 244) #2583C4 | 4.50 / Lc -34.6 |
| unknown | oklch(0.557 0 260) #737373 | 4.54 / Lc 66.7 | oklch(0.592 0 260) #7E7E7E | 4.54 / Lc -34.9 |

Two findings:

1. **Dark mode via ratio alone is misleading.** Colours that pass 4.5:1 on the dark surface score only about Lc 35 (magnitude), far below the Lc 60-75 guidance. If APCA guidance proves right, dark text tokens must be lighter than the ratio needs. PREDICTION only; no user data.
2. **Hue alone cannot separate these roles.** Deutan dE_OK: proved-vs-unknown 0.025, refuted-vs-stale 0.016 (below or near one JND of 0.02), proved-vs-refuted 0.109. So proved/unknown and refuted/stale are near-indistinguishable by colour for deuteranopes. Glyph and label are mandatory: for example filled square = proved, cross = refuted, hollow diamond with "?" = unknown, half-filled = stale. UNKNOWN keeps a neutral grey plus a distinct shape, never a tint of green.

**Verdict: adopt** roles and redundancy rule; the exact values are provisional until a rendering check on real screens.

### 2.5 Theming, elevation, borders versus shadows

**Today.** Radix Colors uses a 12-step scale with fixed semantics: steps 1-2 backgrounds, 3-5 component backgrounds (normal, hover, pressed), 6-8 borders, 9-10 solid, 11-12 text; steps 11 and 12 are guaranteed Lc 60 and Lc 90 on a step-2 background (Radix docs). GitHub Primer has three token tiers (base, functional, component), nine themes over light and dark plus high contrast, and semantic roles (success, danger, attention, accent, and item states open/closed/done), each with muted and emphasis variants. Linear's March 2026 refresh moved from a cool blue-ish grey to a warmer, less saturated grey, made borders and separators softer and lower contrast, dimmed the sidebar, and reduced icon use; its team used an internal tool exposing hue, chroma and lightness per token.

| Pattern | Why it works | Source |
|---|---|---|
| Role-numbered scale (background, component, border, solid, text) instead of ad-hoc greys | Predictable contrast per role; tokens read as intent | Radix docs |
| Functional token layer between raw colours and components | Theme swaps change one layer; audit is per role | Primer colour docs |
| Recede chrome (dim sidebar, soft separators) so content wins | Figure/ground; lowers container count (rubric) | Linear refresh |
| Light-dark via `color-scheme` plus `light-dark()` | One declaration per role; no duplicated blocks | MDN `light-dark()` |

**MEASURED (own script).** Adjacent surface steps are close: light #FAFAFA to #F2F3F5 to #E6E8EB gives 1.064 and 1.106:1; dark #121417 to #191C20 to #24272B gives 1.079 and 1.14:1. A border that reaches 3:1 (WCAG 1.4.11, for component boundaries that identify a control) needs about #8E9198 on light and #606369 on dark. A black shadow on the dark surface reaches only 1.025 (20% alpha), 1.053 (40%), 1.08 (60%) contrast against the surface. **PREDICTION:** in dark mode shadows are close to invisible, so elevation there must come from a lighter surface step plus a border, not a shadow. The rubric allows at most 2 elevations: use surface steps 0 and 1 with a 1px border, and reserve a single shadow for floating layers only if measured visible in light mode.

**Verdict: adopt** role-based scale and functional token tier; **adapt** Linear's "recede the chrome" as a container-budget technique; **avoid** shadow-only elevation.

### 2.6 Typography: open-licence families

All candidates are OFL 1.1 (copyright lines read from `google/fonts` OFL.txt; Inter, JetBrains Mono and Geist statements confirmed on their GitHub pages; Atkinson's own site describes an end-user licence agreement, while the `google/fonts` copy is OFL: reconcile before adopting).

**MEASURED** from the `google/fonts` `main` builds (may differ from upstream release builds). "Latin subset" = Basic Latin + Latin-1 + common punctuation + basic arrows/relations, all OpenType features kept, WOFF2. "Formal /38" = how many of 38 notation glyphs are present (arrows ->, <-, <->, =>, <=, <=>, |->; quantifiers; set and logic symbols; <=, >=, !=, ~=, ===, composition; box, diamond, angle brackets, lambda, times).

| Family (version source) | Axes | Full WOFF2 | Latin subset | Formal /38 | tnum | zero |
|---|---|---|---|---|---|---|
| Inter (v4.1, 2024-11-16) | opsz, wght | 341 KB | 88 KB | 16 | yes | yes |
| IBM Plex Sans (1.1.0, 2024-11-13) | wght, wdth | 224 KB | 64 KB | ~14/43 basic set | no | yes |
| IBM Plex Mono (regular only) | none | 38 KB | 13 KB | 9 | n/a | yes |
| JetBrains Mono (v2.304, 2023-01-14) | wght | 70 KB | 37 KB | 25 | n/a | yes |
| Source Sans 3 (3.052R, 2023-04-04) | wght | 165 KB | 43 KB | 19 | no | yes |
| Public Sans (v2.001, 2022-05-11) | wght | 41 KB | 23 KB | ~9/43 basic set | yes | no |
| Atkinson Hyperlegible Next | wght | 47 KB | 30 KB | ~8/43 basic set | yes | no |
| Atkinson Hyperlegible Mono | wght | 25 KB | 15 KB | ~8/43 basic set | n/a | yes |
| Geist (v1.7.2, 2026-06-01) | wght | 68 KB | 30 KB | ~14/43 basic set | yes | no |
| Geist Mono | wght | 70 KB | 31 KB | 10 | n/a | no |
| Noto Sans Math (fallback) | none | 336 KB | 5.9 KB for the 38 glyphs | 38 | n/a | n/a |

Where "/38" is given it is the exact count; the "~x/43" entries are from the first coverage pass over a slightly larger 43-character set and are rounded indicators, not comparable to the /38 column. The finding does not depend on the difference.

**Finding: no text family covers formal notation.** ∧ ∨ ⊢ ⊨ ⊥ ⊤ ∪ ∩ ℤ and ↦ are missing in every candidate; ∀ ∃ ∈ ⊆ are missing in Inter and Plex; JetBrains Mono is the best mono (missing ⇒ ⇐ ⇔ ↦ ∄ ∪ ∩ ∅ ℤ ⊢ ⊨ ⊥ ⊤). Noto Sans Math (OFL) covers all 38; subsetting to those glyphs gives about 6 KB WOFF2.

| Pattern | Why it works | Source |
|---|---|---|
| Two families only: one UI sans, one mono; formal notation always in mono with a subset math fallback | Meets rubric; consistent glyph set for every ∀/∃/⊨ | MEASURED coverage |
| Turn off programming ligatures in notation contexts | Ligatures fuse operators (`->`, `!=`); notation must show what was written. JetBrains Mono ships an NL build | JetBrains Mono README |
| Tabular numerals for counts, scores, versions | Aligned columns; no layout shift when evidence counts update (Doherty/Nielsen response feedback stays stable) | Inter README; MEASURED tnum |
| Slashed or dotted zero in mono | Disambiguates 0/O in ids and hashes | Inter README; MEASURED zero |
| Self-host WOFF2 | Required by CSP (see below) | MDN font-src; `http.py` |

**Repo constraints (read from `interfaces/http.py`).**

- CSP is `default-src 'none'` with no `font-src`; per MDN, a missing `font-src` falls back to `default-src`, so any `@font-face` is blocked today. Adding `font-src 'self'` is required.
- `/assets/{name}` only serves `app.js` and `app.css`; fonts and icon sprites need an extended allowlist and correct MIME types (plus `X-Content-Type-Options: nosniff` is already set).
- All responses carry `Cache-Control: no-store`, so fonts refetch each load. On localhost this is cheap; if Studio is ever served remotely, revisit.
- Baseline uses a system font stack (`ui-sans-serif, system-ui, ...`): zero font bytes, but no control over notation glyphs or numerals.

**Shortlist for a bake-off (not a decision).**

- UI sans: Public Sans (23 KB, tnum, neutral), Atkinson Hyperlegible Next (30 KB, tnum, designed for low vision character differentiation; licence to reconcile), Geist (30 KB, tnum). Inter is measurably strong (tnum, opsz, zero) but is flagged by the rubric as a default choice; only pick it with a recorded reason. IBM Plex Sans lacks a `tnum` feature in this build.
- Mono: JetBrains Mono (37 KB Latin, 25/38 notation glyphs, NL variant, variable); IBM Plex Mono (13 KB) has the weakest notation coverage; Atkinson Mono (15 KB) is the smallest but covers little notation.
- Fallback: Noto Sans Math subset, loaded via `unicode-range`. Risk to test: fallback glyphs are not fixed-width, so column alignment in mono grids may break.

**Verdict: adopt** self-hosted, subset, variable WOFF2 with `font-src 'self'`; **adapt** the family choice via a legibility test (protocol in section 5); **avoid** ligatures in notation and avoid remote font CDNs.

### 2.7 Type scale, line height, measure

**MEASURED (arithmetic).** From a 13 px base, ratios give: 1.125 -> 13.0, 14.6, 16.5, 18.5, 20.8; 1.2 -> 13.0, 15.6, 18.7, 22.5, 27.0; 1.25 -> 13.0, 16.2, 20.3, 25.4, 31.7. The rubric caps distinct sizes at 6. The baseline stylesheet declares 13 distinct `font-size` values (10, 11, 12, 13, 17, 19, 20, 21, 22, 23, 25, 36 px, plus a `clamp()`), MEASURED from `app.css`.

Evidence on measure: WCAG 1.4.8 (AAA) sets at most 80 characters per line and line spacing at least 1.5 within paragraphs; 1.4.12 requires content to tolerate line height 1.5, paragraph spacing 2x, letter spacing 0.12 em, word spacing 0.16 em without loss. Dyson's 2004 review (Behaviour and Information Technology 23(6)) identifies characters per line as the critical variable; its synthesis reports mixed findings: some studies read faster at about 100 characters, and one reports better comprehension at 55. So "45-75" is a convention, not a firm result, and screen tasks differ from prose reading.

| Pattern | Why it works | Source |
|---|---|---|
| Fixed 5-6 step scale on one ratio (1.2 is a starting hypothesis) | Fewer sizes lowers visual complexity; hierarchy by size and weight | rubric; MEASURED arithmetic |
| Prose measure 55-80 ch; code and tables may exceed it | Bounded by 1.4.8; Dyson shows the optimum is task-dependent | WCAG 1.4.8; Dyson 2004 |
| Never depend on tight line height; test 1.5 line height and text-spacing overrides | 1.4.12 | WCAG 2.2 |

**Verdict: adopt** a 6-step scale; **adapt** measure per surface (prose 55-80 ch, mono 80-100 ch, tables unlimited), to be tested rather than assumed.

### 2.8 Spacing, density, grids, container queries

**Today.** Primer's spacing scale is 4 px based: 2, 4, 6, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 64 ... 128; control heights XSmall 24, Small 28, Medium 32, Large 40, XLarge 48 px, with larger gaps for `pointer: coarse`. Carbon's spacing tokens: 2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 160 px (`$spacing-01` to `-13`). Container queries: size queries widely available since early 2023; container style queries reached Baseline newly available in May 2026 (web.dev digest; secondary summary said Firefox 151 shipped last). `@property` is Baseline newly available since July 2024.

| Pattern | Why it works | Source |
|---|---|---|
| One spacing scale, about 8 steps, shared by all components | Proximity encodes grouping without borders; fewer containers | Primer; Carbon |
| Two density modes via control-height tokens (default 32, compact 24) | Compact stays at the WCAG 24 px floor; default supports faster pointing | Primer control sizes; WCAG 2.5.8 |
| Component-level responsiveness with container queries | Same tree panel works in a sidebar or full width | MDN container queries |
| Register numeric tokens with `@property` when animation needs them | Typed, animatable custom properties | MDN `@property` |

**PREDICTION (Fitts index of difficulty, dimensionless, distance 400 px, Shannon form log2(D/W+1)):** target width 16 px: 4.70 bits; 24: 4.14; 32: 3.75; 40: 3.46; 44: 3.33; 48: 3.22. Moving 24 to 32 px cuts 0.39 bits (about 9%). Converting bits to milliseconds needs device coefficients that I did not source here; do not read this as a time. Validity: one-dimensional pointing at known distance; ignores homing, visual search and target density.

**Verdict: adopt** a 4-based scale with named steps and two density modes; **adapt** container queries for panels, keeping fallbacks for older engines.

### 2.9 Motion

**Today.** NN/g: 100 ms for simple feedback, 200-300 ms for moderate changes, general range 100-400 ms, and 500 ms+ "feels like a drag"; ease-out for entrances, ease-in for exits; avoid linear; respect reduced motion. Nielsen's limits (1993): 0.1 s feels instantaneous, 1 s keeps flow of thought, 10 s keeps attention. Material 3 duration tokens from `material-web` source (Apache-2.0, v0_192): short 50/100/150/200 ms, medium 250/300/350/400, long 450 to 600, extra-long 700 to 1000; `easing-standard` cubic-bezier(0.2, 0, 0, 1), emphasized-decelerate cubic-bezier(0.05, 0.7, 0.1, 1). Carbon (source docs): fast-01 70 ms, fast-02 110, moderate-01 150, moderate-02 240, slow-01 400, slow-02 700; productive standard cubic-bezier(0.2, 0, 0.38, 0.9); it reserves "expressive" motion for occasional important moments. MDN: `prefers-reduced-motion` is Baseline widely available (since January 2020), for users with vestibular disorders.

| Pattern | Why it works | Source |
|---|---|---|
| Productive-only motion: 70-150 ms for state feedback, 150-240 ms for panel and diff expansion, nothing over 400 ms in the main workflow | Stays within Nielsen's 0.1 s "instantaneous" band for feedback; long animations delay expert users | Carbon; NN/g; Nielsen 1993 |
| Ease-out entering, ease-in exiting, no linear | Matches perceived physics | NN/g |
| Motion never carries meaning; a state change also changes glyph/text | Redundancy; safe under reduce | MDN; WCAG 1.4.1 |
| Under `reduce`, replace transitions with instant state or a single-step fade | Vestibular safety | MDN |

Baseline `app.css` has no `prefers-reduced-motion` or `prefers-color-scheme` rule (MEASURED count 0) and no gradients or shadows (MEASURED count 0).

**Verdict: adopt** a 4-token duration scale (about 100, 150, 240, 400 ms) and one productive easing; **avoid** decorative or expressive motion.

### 2.10 Icons

| Set | Licence | Size and scope | Notes | Source |
|---|---|---|---|---|
| Lucide | ISC, with about 120 Feather-derived icons under MIT | 1,600+ icons (guide page), 24x24 grid, default stroke 2; latest release 1.48.0 (2026-09-24) | Attribution and licence text must ship; GitHub's licence detector reports NOASSERTION because of the dual licence | lucide.dev; GitHub API |
| Phosphor | MIT | Over 1,200 icons (derived from a type reference; medium confidence), six weights, SVG per weight; last release v2.0.8 (2024-02-01) | Weight axis helps dense vs relaxed density | GitHub `phosphor-icons/core` |
| Tabler | MIT | 6,220 icons (5,166 outline, 1,054 filled), 2 px default stroke; latest v3.48.0 (2026-09-22) | Largest coverage; stroke adjustable | GitHub `tabler/tabler-icons` |

None includes UML, state-machine or proof-status glyphs. Those (proved, refuted, unknown, stale, AI-proposed, model, journey, test) must be drawn in-house on the same grid and stroke so they carry meaning consistently. Constraint: inline `style` attributes are blocked by `style-src 'self'`; SVG presentation attributes and same-origin files still work, and ADR-013 permits DOM construction (`createElementNS`) with no framework.

**Verdict: adopt** Lucide (ISC) for generic actions, in-house glyphs for status and model semantics; **avoid** icon-per-bullet (rubric) and coloured icon backgrounds (Linear removed them).

### 2.11 Design tokens

**Today.** The DTCG format reached a stable version 2025.10 (Final Community Group Report, 2025-10-28; Format, Color and Resolver modules). It is not a W3C Standard or on the Standards Track. Colour tokens are objects: `colorSpace`, `components` (may include `"none"`), optional `alpha`, optional `hex` (6-digit fallback); 14 colour spaces including `oklch` (L 0-1, C 0-infinity, H 0-360) and `srgb`. Dimensions are `{value, unit}` with `px` or `rem`; types include colour, dimension, fontFamily, fontWeight, duration, cubicBezier, number, border, shadow, transition. References use `{group.token}`; extensions use `$extensions`. Note a second page at `/tr/drafts/format/` describes itself as a preview draft dated 2026-09-08: pin to 2025.10. Style Dictionary is Apache-2.0, latest release v5.5.5 (2026-09-20) per GitHub API, although its site still says "Version 4" (site lag; forward-compatible with DTCG).

| Pattern | Why it works | Source |
|---|---|---|
| Author `design/tokens/*.tokens.json` in DTCG 2025.10 with `oklch` components and `hex` fallback | Tool-neutral; the kernel and CI can lint contrast from the same file | DTCG Color 2025.10 |
| Generate `tokens.css` (custom properties) from tokens with a small Python script or Style Dictionary | Single source; no build framework needed if Python does it | DTCG; Style Dictionary |
| Register typed properties with `@property` only for values that animate or need type checks | Avoids overhead; supported since July 2024 | MDN |
| Add a check that tokens.css equals a regeneration | "What you see is generated" invariant applied to the design system | EIJA invariants |

**Verdict: adopt** DTCG 2025.10; **adapt** generation to the repo's Python-only toolchain (Style Dictionary is Node; adding it adds an install, which the lane forbids for now).

## 3. Quantitative facts

| # | Fact | Source | Confidence |
|---|---|---|---|
| Q1 | WCAG 2.2 is a W3C Recommendation, 2024-12-12; text contrast AA 4.5:1 (3:1 large), AAA 7:1 (4.5:1 large); non-text 3:1 | w3.org/TR/WCAG22 | high |
| Q2 | Target size minimum 24x24 CSS px, with a 24 px spacing-circle exception (2.5.8) | WCAG Understanding 2.5.8 | high |
| Q3 | WCAG 3.0 is a Working Draft (2026-09-10); contrast algorithm "yet to be determined" | w3.org/TR/wcag-3.0 | high |
| Q4 | APCA guidance: Lc 75 body minimum, 90 preferred, 45 large, 30 spot, 15 dividers; unratified | git.apcacontrast.com nutshell | medium |
| Q5 | CSS Color 4 gamut mapping JND = 0.02 dE_OK, epsilon 0.0001 | w3.org/TR/css-color-4 | high |
| Q6 | CSS Color 4 is a CR Draft (2026-09-26); Color 5 is a Working Draft (2026-09-13) | w3.org | high |
| Q7 | `oklch()` Baseline widely available since May 2023; `light-dark()` Baseline 2024 (May 2024); `@property` newly available since July 2024; `prefers-reduced-motion` widely available since January 2020 | MDN pages | high |
| Q8 | DTCG 2025.10 stable, 14 colour spaces including oklch, hex fallback is 6-digit | designtokens.org/tr/2025.10 | high |
| Q9 | 8% of males of European ancestry red-green colour blind (5% Asian, 4% African); about 1 in 200 women | jfly.uni-koeln.de; colourblindawareness.org | medium (secondary, not epidemiological papers) |
| Q10 | Okabe-Ito hex set #E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7 plus black | siegal.bio.nyu.edu (secondary) | medium |
| Q11 | Baseline pair #236755 vs #9f382b: dE_OK 0.204 normal, 0.080 protan, 0.082 deutan, 0.259 tritan | MEASURED, Machado 2009 matrices | medium (simulation) |
| Q12 | Baseline `app.css`: 13 distinct font-size declarations, 9 colour tokens, radius 14 px, 0 prefers-color-scheme/reduced-motion rules | MEASURED from repo | high |
| Q13 | Candidate text tokens at exactly 4.5:1 on dark surface score about Lc 35 (magnitude) | MEASURED (WCAG + APCA 0.0.98G) | medium (APCA unratified) |
| Q14 | Deutan dE_OK: proved vs unknown 0.025; refuted vs stale 0.016; proved vs refuted 0.109 | MEASURED | medium |
| Q15 | Shadow contrast on dark surface: 1.025 / 1.053 / 1.080 at 20 / 40 / 60% black | MEASURED | medium |
| Q16 | Latin WOFF2 subsets: Inter 88 KB, Plex Sans 64, Source Sans 3 43, JetBrains Mono 37, Geist 30, Atkinson Next 30, Public Sans 23, Plex Mono 13 | MEASURED on google/fonts builds | medium (upstream may differ) |
| Q17 | Formal-notation coverage of 38 glyphs: Noto Sans Math 38; JetBrains Mono 25; Source Sans 3 19; Inter 16; Geist Mono 10; Plex Mono 9. 38-glyph Noto subset = 5.9 KB WOFF2 | MEASURED | medium-high |
| Q18 | Fitts ID at D = 400 px: W 24 -> 4.14 bits; 32 -> 3.75; 40 -> 3.46 | computed (PREDICTION) | medium (validity limits in 2.8) |
| Q19 | Material 3 duration tokens 50-1000 ms; Carbon 70, 110, 150, 240, 400, 700 ms | material-web source; carbon-website source | high |
| Q20 | Nielsen response limits 0.1 s, 1 s, 10 s | nngroup.com (1993) | high |
| Q21 | NN/g animation guidance 100-400 ms range; 500 ms+ drags | nngroup.com | medium (practitioner) |
| Q22 | Icon licences: Lucide ISC (+MIT subset); Phosphor MIT; Tabler MIT (6,220 icons) | official pages, GitHub | high |
| Q23 | Latest tags: Inter v4.1, Geist v1.7.2, JetBrains Mono v2.304, Lucide 1.48.0, Tabler v3.48.0, Style Dictionary v5.5.5 | GitHub API | high |
| Q24 | Dyson 2004: characters per line is the critical line-length variable; results mixed (reading speed vs comprehension) | Dyson 2004 PDF (read) | high |
| Q25 | Baseline CSP lacks `font-src`; `/assets` allowlist has only app.js and app.css | `interfaces/http.py` | high |

## 4. Implications for EIJA

1. **Tokens first.** Create `design/tokens/*.tokens.json` in DTCG 2025.10 (OKLCH components with `hex` fallback) and generate `tokens.css` with a Python script in the repo; a test regenerates and diffs it. Records the source of truth for later ADRs.
2. **Status system.** Five roles (proved, refuted, unknown, stale, AI-proposed) each with hue + glyph + label; UNKNOWN is a neutral grey hollow diamond, never tinted like a pass. Deutan separation of proved/unknown (0.025) and refuted/stale (0.016) is below the point where hue can carry meaning.
3. **Two-metric contrast gate.** Gate builds on WCAG 2.2 ratios; report APCA Lc per token pair in the token lint output. Raise dark-mode text lightness above the 4.5:1 minimum until Lc 60+ if APCA guidance is adopted (needs an HCI-ADR and a legal check on APCA code). Do not vendor APCA code.
4. **Light and dark from day one** via `color-scheme` and `light-dark()`; baseline has neither. Elevation in dark mode by surface step plus 1 px border; no shadow-only elevation.
5. **Type.** Two families plus mono: pick a UI sans from the shortlist by legibility test; JetBrains Mono for code and notation with ligatures off; a 6 KB Noto Sans Math subset as the notation fallback via `unicode-range`. Total font budget target: under about 100 KB Latin WOFF2 for the first paint (Q16 sums: Public Sans 23 + JetBrains Mono 37 + math 6 = 66 KB, PREDICTION on budget).
6. **Server changes needed for fonts and icons** (owner: whoever owns `http.py`): add `font-src 'self'`, extend the `/assets` allowlist with MIME types, decide on caching (currently `no-store` on everything). Each is a security-relevant change and needs its own HCI-ADR or amendment to the CSP record.
7. **Scale discipline.** Six type sizes, one ratio (start 1.2 from 13 px), eight spacing steps on a 4 px base, two density modes (32 px default, 24 px compact); baseline has 13 font sizes to consolidate.
8. **Motion budget.** Four durations (about 100/150/240/400 ms), one productive easing, no motion that carries meaning, instant state under `prefers-reduced-motion`. Baseline has no reduced-motion rule.
9. **Icons.** Lucide for generic actions (ship its licence text); draw in-house glyphs for status and model semantics on the same 24 px grid and 2 px stroke; build SVG by DOM APIs only (ADR-013, CSP).
10. **Recede the chrome.** Follow Linear's direction (dim navigation, soft separators, fewer icons) as the concrete tactic for the container budget, and measure containers per viewport rather than trusting taste.

## 5. Study protocol sketches (nothing run)

- **Legibility bake-off (font).** Within-subject, 12+ developers, 3-4 sans candidates crossed with 2 mono candidates. Tasks: find the odd identifier in a list (0/O, 1/l/I), read a formula with ∀ ∃ ⊨, compare two hashes. Measures: error rate, time, subjective load (NASA-TLX). Success is decided before running, per HCI-ADR.
- **Status discrimination (CVD).** Show the five status roles at small size with hue only, then hue + glyph; measure identification accuracy for participants screened for CVD with a standard test plate. Pre-register a threshold.
- **Dark-mode contrast.** Compare text tokens at 4.5:1 vs Lc 60+ on the same tasks; measure reading errors and preference. This is the only way to settle the WCAG/APCA divergence for EIJA.

## 6. Gaps and unverified items

| Item | State |
|---|---|
| Nature Methods Wong 2011 paper; only confirmed indirectly (search listing, Okabe-Ito original, hex list). Not opened | UNVERIFIED as a primary read |
| CVD prevalence from an epidemiological paper; NEI page has none | UNVERIFIED (medium via advocacy and lab pages) |
| Material 3 elevation, Carbon typography and elevation, Primer shadow/motion pages: empty or client-rendered | UNVERIFIED; do not cite for elevation |
| Vercel Geist design-system colour guidance, Figma, Vercel v0, Cursor, Zed, VS Code theming, JetBrains theming | not opened; out of budget once search was exhausted |
| Primer colour-blind theme names and how diff colours are handled | UNVERIFIED (page says nine themes; details not confirmed) |
| Atkinson Hyperlegible licence: Braille Institute page points to an EULA; `google/fonts` carries OFL | reconcile before adoption |
| APCA code licence status for a from-scratch implementation | legal review needed |
| Font builds are `google/fonts` `main`; upstream release files may differ in features (Source Sans 3, Plex Sans show no `tnum` in these builds) | verify against upstream before ADR |
| IBM Plex Math coverage (npm package listed by IBM) not measured | UNVERIFIED |
| Doherty threshold (400 ms) and Fitts/Hick coefficients not sourced in this dossier | see HCI-laws dossier |
| Container query Baseline widely-available date for style queries; web.dev digest gave newly available May 2026 only | high for the digest, low for anything later |
| All predictions (status palette values, dark-mode Lc, Fitts bits, font budget) | PREDICTION; no user study |

## 7. URLs opened (access date 2026-09-29)

Colour and accessibility: bottosson.github.io/posts/oklab/ · w3.org/TR/css-color-4/ · w3.org/TR/css-color-5/ · w3.org/TR/WCAG22/ · w3.org/TR/wcag-3.0/ · w3.org/WAI/WCAG22/Understanding/{target-size-minimum, visual-presentation, text-spacing}.html · github.com/Myndex/SAPC-APCA · git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html · unpkg.com/apca-w3@0.1.9/src/apca-w3.js · registry.npmjs.org/apca-w3/latest · jfly.uni-koeln.de/color/ · siegal.bio.nyu.edu/color-palette/ · colourblindawareness.org/colour-blindness/ · nei.nih.gov (types of colour vision deficiency) · colorbrewer2.org · cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html · inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html

Typography: github.com/{rsms/inter, IBM/plex, vercel/geist-font, JetBrains/JetBrainsMono, adobe-fonts/source-sans} · raw.githubusercontent.com/google/fonts/main/ofl/{inter, ibmplexsans, ibmplexmono, jetbrainsmono, sourcesans3, publicsans, atkinsonhyperlegiblenext, atkinsonhyperlegiblemono, geist, geistmono, notosansmath}/ (TTF + OFL.txt) · brailleinstitute.org/freefont/ · stu.westga.edu/~ssynan1/literacy/Dyson.pdf (Dyson 2004)

CSS and platform: developer.mozilla.org/en-US/docs/Web/CSS/{@property, color_value/oklch, color_value/light-dark, @media/prefers-reduced-motion, CSS_containment/Container_queries} · developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/font-src · web.dev/blog/baseline-digest-may-2026

Design systems and tokens: primer.style/foundations/{color/overview, primitives/size} · primer.style/product/getting-started/accessibility/ · radix-ui.com/colors/docs/palette-composition/understanding-the-scale · linear.app/now/behind-the-latest-design-refresh · raw.githubusercontent.com/carbon-design-system/carbon-website/main/src/pages/elements/{motion,spacing}/overview.mdx · raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-motion.scss · nngroup.com/articles/{animation-duration, response-times-3-important-limits}/ · w3.org/community/design-tokens/ · designtokens.org/tr/2025.10/color/ · designtokens.org/tr/drafts/format/ · styledictionary.com

Icons and releases: lucide.dev/license · lucide.dev/guide/ · github.com/phosphor-icons/core · github.com/tabler/tabler-icons · api.github.com release/licence endpoints for the repos above

Opened but empty or blocked (no facts used): nature.com/articles/nmeth.1618 · pubmed.ncbi.nlm.nih.gov/21774112 · sciencedirect.com (Dyson and Haselgrove 2001) · m3.material.io (elevation, easing) · carbondesignsystem.com pages · primer.style shadow and motion pages
