# Typography system

Lane `lane/ux-research`. Date 2026-09-29. Status: proposed (revised after audit, 2026-09-29; changes listed in section 13). Aspect: typography. Decision record: [HCI-ADR 0060](../../adr/0060-hci-typography.md). Machine-readable: [typography.tokens.json](../../../design/tokens/typography.tokens.json) (W3C Design Tokens Community Group format, 2025.10) and [fonts.lock.json](../../../design/fonts.lock.json) (family, licence, source URL, sha256, glyph coverage).

Labels used below. **MEASURED**: computed by a script I ran on 2026-09-29 (tool, browser and date named). **PREDICTION**: model output with its assumptions; not a measurement of any person. **UNVERIFIED**: not confirmed this session; nothing is built on it. Source ids `S1` to `S35` are in section 12; every URL was opened on 2026-09-29. No user study has been run, so **no claim of user benefit is made**.

## 0. Decisions first

| # | Decision | Value | Basis | Confidence |
|---|---|---|---|---|
| 1 | UI sans | **Noto Sans**, self-hosted subset, wght 400 to 600 only, css family `EIJA Sans`, 16,736 bytes | Section 4: passes the hard filters; digits tabular by default without a font feature or a build step; smallest Latin subset of the candidates that pass them (16,736 bytes shipped, against 20,288 for Inter with `ss02` and `tnum` baked in); same design family as the symbol fallback. It does not have the highest x-height: Inter is 1.8% higher (0.546 against 0.536). MEASURED on the font files | Low to medium: Noto Sans, Public Sans, Atkinson Hyperlegible Next and Inter with a baked disambiguation feature are inside the noise of my unvalidated proxy; a bake-off with all four and a system-stack control is registered (section 10) |
| 2 | Mono | **Fira Code**, self-hosted subset, ligature tables removed at build time, wght 400 to 600, css family `EIJA Mono`, 19,832 bytes | 72 of 84 needed notation glyphs native, all on the same 0.6 em cell (MEASURED); JetBrains Mono has 58; Noto Sans Mono has 72 but 6 of them are off the cell | Medium |
| 3 | Notation fallback | **Noto Sans Math** subset, 4,336 bytes, css family `EIJA Symbols`, never first in a stack | Mono stack: 84 of 84 anticipated codepoints covered, 72 of 84 on the cell; the 12 that come from this face in a mono context are off the cell, including ⇒, ⇔, ↦, ⟦ ⟧ and ∘ (MEASURED). Sans stack: all 65 codepoints a sans context may use (74 of 84 overall; the 10 missing are keyboard and box-drawing glyphs, mono-only by rule). The 84 are a design assumption: 8 are attested in the repository today (section 4.4) | Medium |
| 4 | Scale | 5 sizes: 12, 14, 16, 20, 24 px (0.75, 0.875, 1, 1.25, 1.5 rem); line boxes 16, 20, 24, 28, 32 px on a 4 px grid; one slot left unused under the budget of 6 | Baseline declares 14 sizes (MEASURED). Sizes 12/16, 14/20, 20/28 also appear in the Windows type ramp (S18) | Medium for the scale; the 14 px default is a convention (section 3.2) |
| 5 | Weights | 400 and 600 only. 600 never below 14 px. No italic file, `font-synthesis: none` | Baseline uses 7 weights (MEASURED). Windows guidance: minimum 14 px Semibold, 12 px Regular (S18) | Medium |
| 6 | Letter-spacing | 0 everywhere, stored as one token `font.letterSpacing.none` that every text role references; no all-caps transform | Design rule: the baseline has 7 values from -2.8 to 1.8 px (MEASURED) and kernel enum values are shown as stored. The token format is not the reason: the 2025.10 typography type requires a `letterSpacing` dimension (S1, section 9.8), so the tokens set it explicitly to 0 px | Medium |
| 7 | Monospace rule | Mono means: a **literal token** (compare or copy exactly), code, formal notation, or column-aligned text. Everything a person reads as language is sans | Section 6 | Medium |
| 8 | Measure | Prose 56 ch (about 68 characters); source and trace views 100 ch; tables and trees unlimited | PREDICTION by arithmetic on repository text; sources disagree (WCAG AAA at most 80 characters, Microsoft 50 to 60 letters and not more than 60 characters). 56 ch is 68 characters with spaces, so it is a hypothesis at the upper edge of one source's range (section 5.3) | Low |
| 9 | Delivery | 3 files, 40,904 bytes; `font-src 'self'`; `font-display: swap`; preload the sans and mono files | MEASURED: the current Studio CSP blocks all three; with `font-src 'self'` they load; loopback fetch median 6.7 ms | High for the CSP finding |
| 10 | Type never carries authority | No typeface, italic or size distinguishes AI-authored from kernel-derived text; provenance is a badge and an outline (P9) | Invariants I1 and I4 | High (design rule) |

Size of the change against the baseline (MEASURED, static parse of `app.css`): sizes 14 to 5, weights 7 to 2, letter-spacing values 7 to 1, smallest text 10 px to 12 px, font bytes 0 to 40,904.

**What this does not show.** No study shows that these choices help anyone. The legibility numbers are proxies. The x-height model is a psychophysics floor for continuous text, not a model of scanning short labels. Section 11 lists what is unknown.

## 1. Method and limits

- Baseline read from `src/eija_studio/resources/web/app.css`, `index.html` and the CSP in `src/eija_studio/interfaces/http.py` (S31).
- 19 font files downloaded from `google/fonts` at commit `23e54b51ddffbc7713c583748e3bd86f62b1fa4a` (S29), hashed, and measured with fontTools 4.56.0: cmap coverage of 84 needed codepoints, GSUB features, x-height from glyph outlines, digit advances, subset size.
- A glyph-confusion **proxy** (section 4.2): 1 minus the soft intersection-over-union of two glyph bitmaps at 14 px, for I/l, I/1, l/1 and 0/O and six more pairs. It measures shape distance, not human confusion, and is not validated.
- One headless Chromium (Chrome for Testing 151.0.7922.34, device scale factor 1, Windows 11) served a synthetic page through the Studio CSP with and without `font-src`. It reported which platform font drew each glyph (Chrome DevTools Protocol) and measured widths.
- WebSearch was unavailable (session budget exhausted); sources came from direct fetches, the GitHub API and Crossref. Two papers I wanted were not readable: Beier and Larson 2010 on misrecognised letters (publisher returned 403) and Bigelow 2019 on typeface features (bibliographic record only). Neither is used.
- Audit revision (2026-09-29): I re-downloaded the DTCG 2025.10 spec, the Geist typography page, the MDN font-display page, the NN/g response-time article, the WCAG target-size page, the OFL FAQ, the Microsoft typography page, both Primer pages and the MDN preload page, and checked each claim against the text. I also measured Inter with `cv08`, `ss02` and `ss04` baked into the cmap (one extra subset, one proxy run; script `.tmp/fonts/inter_feat.py`, not shipped).
- Audit round 2 (2026-09-29): re-read the raw Fira Code README and the MDN `font-variant-ligatures`, `font-display` and `size-adjust` pages; recomputed the equal x-height widths from unrounded values; re-measured the 12 off-cell advances, the average term advance and system-font coverage with fontTools on the rebuilt subsets and the installed Windows fonts (script `.tmp/audit2/verify.py`, not shipped); scanned tracked files for non-ASCII characters.
- Not measured: macOS and Linux rendering, high-DPI, a slow disk, hinted rendering, dark mode perception, any real user.

## 2. Baseline (MEASURED)

Static parse of `app.css` (7,156 bytes) with `.tmp/baseline_type.py`; computed styles in a browser were not measured.

| Property | Baseline | Note |
|---|---|---|
| Distinct `font-size` values | 13 (10, 11, 12, 13, 17, 19, 20, 21, 22, 23, 25, 36 px and one `clamp(38px,4vw,58px)`) | 14 if the `font:15px/1.65 ...` shorthand on `body` is counted. This reconciles the dossiers: VIS and DEV report 13, SLP reports 14 |
| Font weights | 7 (450, 500, 600, 620, 650, 700, 750) | |
| Letter-spacing values | 7 (-2.8, -1.8, -1, -0.55, 1.2, 1.5, 1.8 px) | Negative tracking on headings, positive on labels |
| Line-height values | 4 (1.08, 1.3, 1.6, 1.65) | |
| Families | 2 stacks, both system: `ui-sans-serif, system-ui, ...` and `ui-monospace, SFMono-Regular, Consolas, monospace` | No font files. On this PC they resolve to Segoe UI and Consolas (browser fallback observed in Chromium); other systems: UNVERIFIED |
| Smallest text | 10 px (eyebrow, `header small`, `.option small`) | |
| Text in `pre` | 12 px mono; 3 `<pre>` elements in `index.html` (MEASURED count) | Raw JSON |
| Words in `index.html` outside scripts and `pre` | 404 | Not a typography number; it is the pressure on prose styling |

Worth keeping: one system stack costs zero bytes and needs no CSP change (section 4.6, first row).

## 3. Quantitative model

Full arithmetic with constants is in [HCI-ADR 0060](../../adr/0060-hci-typography.md). Summary here.

### 3.1 Type sprawl (counts)

| Metric | Baseline (MEASURED) | Proposed | Label |
|---|---|---|---|
| Distinct font sizes declared | 14 | 5 (budget 6) | Baseline MEASURED; proposed by construction, PREDICTION for any real viewport until a lint and the slop-budget script run |
| Weights | 7 | 2 | same |
| Letter-spacing values | 7 | 1 (zero) | same |
| Line-height values | 4 | 4 distinct ratios (4/3 is used twice); 5 px values on a 4 px grid | same |
| Text families in the first position | 2 | 2 (plus one glyph-fallback face) | same |
| Font bytes | 0 | 40,904 | MEASURED (file sizes) |

### 3.2 Angular x-height against the fluent-reading range (PREDICTION)

Model. Angular x-height of a lower-case letter is `2 atan(h / 2D)` with `h = x_ratio * size_px * 0.2646 mm` (1 CSS px is 1/96 in, S17) and viewing distance D. Legge and Bigelow report that text can be read at maximum speed over about 0.2 to 2 degrees of x-height (S16). Distances: 500 and 600 mm are my assumptions for a desktop monitor (UNVERIFIED, no source opened); 710 mm is the CSS reference distance (28 in, S17).

| Text | x-height ratio (MEASURED) | x-height px | Degrees at 500 mm | at 600 mm | at 710 mm |
|---|---|---|---|---|---|
| Baseline 10 px eyebrow (Segoe UI) | 0.500 | 5.00 | 0.152 | 0.126 | 0.107 |
| Baseline 13 px table (Segoe UI) | 0.500 | 6.50 | 0.197 | 0.164 | 0.139 |
| Baseline 15 px body (Segoe UI) | 0.500 | 7.50 | 0.227 | 0.189 | 0.160 |
| Baseline 12 px `pre` (Consolas) | 0.490 | 5.88 | 0.178 | 0.149 | 0.126 |
| Proposed `caption` 12 px | 0.536 | 6.43 | 0.195 | 0.163 | 0.137 |
| Proposed `ui` 14 px | 0.536 | 7.50 | 0.228 | 0.190 | 0.160 |
| Proposed `prose` 16 px | 0.536 | 8.58 | 0.260 | 0.217 | 0.183 |
| Proposed `code` 14 px | 0.527 | 7.37 | 0.224 | 0.186 | 0.157 |

Reading. (a) Relative to the baseline the proposal is larger in x-height everywhere it is smaller in nominal size or equal: smallest text +29% (12 px against 10 px), table text +15% (14 against 13), body-equivalent text +0% (14 against 15) and reading text +14% (16 against 15), mono +25% (14 against Consolas 12). These ratios do not depend on viewing distance, so the ordering cannot flip inside the distance band. (b) The size that reaches 0.2 degrees is 12.3, 14.8 and 17.5 px for EIJA Sans at 500, 600 and 710 mm. So 14 px `ui` text is predicted to reach the floor at 500 mm and to fall about 5% short at 600 mm; 12 px is predicted about 19% short by size at 600 mm (18.8% by angle). Whether 14 reaches the floor flips inside the distance band, so the model does **not** decide between 14 and 15 px. The same holds for 16 px `prose`: it reaches the floor at 500 and 600 mm and is 8.5% short by angle at 710 mm (0.183 degrees), so the floor is not evidence for 16 px either. The 14 px and 16 px defaults follow convention (Windows body 14/20, S18; Primer body 14 px and body large 16 px, S19) and the study tests 14 against 15 (section 10). Fira Code x-height in the table is the shipped subset (0.5265, rounded 0.527); the candidate table in section 4.3 lists 0.525, the upstream default instance at wght 300.

Validity. The floor comes from continuous text read at speed. It says nothing about recognising a status word, comparing two hashes or scanning a tree. It assumes normal vision, adequate contrast and CSS px equal to 1/96 in on the user's display. Users can scale text (rem sizes, browser zoom to 200%, S12).

### 3.3 Width and density (MEASURED in Chromium 151)

| Text at 14 px | EIJA font | System stack on this PC | Ratio |
|---|---|---|---|
| 11 domain terms in one line (sans) | 615.9 px | 578.9 px (Segoe UI) | +6.4% |
| 10 digits | 80.1 px | 75.5 px | +6.1% |
| 12 mono characters | 100.8 px | 92.4 px (Consolas) | +9.1% |

At equal x-height the difference nearly vanishes (PREDICTION by linear scaling, one method: system size = 14 x x_EIJA / x_system, unrounded widths from `fonts.lock.json` `verification.equal_x_height_comparison`): Segoe UI at 15.01 px would set the same terms 0.75% wider than EIJA Sans at 14 px; Consolas at 15.04 px would be 1.6% narrower than EIJA Mono at 14 px (at exactly 15.0 px: +0.7% and -1.8%). The 11-term string is stored as `verification.sans_terms_string`. So text is wider at the same nominal size, not at the same legibility model. Any pane width measured with system fonts does not transfer; measure layouts with the shipped fonts (section 9).

### 3.4 Bytes and latency

Shipped: 16,736 + 19,832 + 4,336 = 40,904 bytes (39.9 KiB), inside the 100,000-byte hypothesis of the dossier (S32, VIS section 4 item 5; not a standard). MEASURED loopback fetch of all three files with `Cache-Control: no-store`, Python client, n = 60: median 6.7 ms sequential, p95 17.9 ms, maximum 76.2 ms. This is 7% of the 0.1 s class for direct actions at the median (S33). A browser p95 has not been measured. In the smoke page the layout-shift observer recorded 0 shifts with `font-display: swap`; the fetch takes a few milliseconds, so this says nothing about a slow disk or remote host.

### 3.5 What the model cannot say

Reading speed on this typeface, error rates for I/l/1/0/O, whether 12 px status words are misread, whether weight 400 versus 600 is perceived equally in dark mode. Those are the study arms in section 10.

## 4. Choosing the families

### 4.1 Hard filters

| Filter | Why | Source |
|---|---|---|
| Open licence that allows self-hosting and subsetting | Files ship in an Apache-2.0 repository under `font-src 'self'` | S15 items 2.1, 2.5, 2.6 |
| No Reserved Font Name, or use the whole file unmodified | Subsetting is a modification; a declared RFN then forces a rename (FAQ 2.6; the rule that a rename is needed only when an RFN is declared is FAQ 3.8). WOFF2 conversion without renaming is allowed only if the data is unchanged apart from compression (2.2.1) | S15 (items 2.6, 3.8, 2.2.1); RFN lines checked in each `OFL.txt` (MEASURED) |
| Tabular figures available | Counts, versions, scores align without layout shift | S4, S28 |
| Subset at most about 25 KB per face, 100 KB in total | The 100 KB total is the dossier's hypothesis (S32); 25 KB per face is my starting value | S32 |
| Basic Latin and Latin-1 | English UI; other text falls back to the system | repository |

Reserved Font Names declared (MEASURED in the licence files): IBM Plex Sans and Mono ("Plex"), Source Sans 3 and Source Code Pro ("Source"), Cascadia Mono ("Cascadia Code"). Their whole files are 229,852, 169,416, 39,176 (Regular only), 89,484 and 210,224 bytes as WOFF2 (MEASURED), so they fail the size filter or need renaming. They are rejected on that ground, not on design.

### 4.2 UI sans candidates (MEASURED unless stated)

Confusable pairs are the proxy distance at 14 px (0 means identical bitmaps): I/l, I/1, l/1, 0/O. Subset bytes use the same Latin set for every family, wght 400 to 600. Digit advance is in em for tabular figures.

| Family (version in file) | x-height | I/l, I/1, l/1, 0/O | Min | Tabular digit em | Subset bytes | Notes |
|---|---|---|---|---|---|---|
| **Noto Sans** (2.015) | 0.536 | 0.41, 0.44, 0.57, 0.67 | 0.41 | 0.572, and it is the default | 16,348 | Chosen |
| Public Sans (2.001) | 0.517 | 0.55, 0.56, 0.80, 0.51 | 0.51 | 0.700 (needs `tnum`) | 19,424 | Repository says unmaintained since v2.001, 2022-05-11 (S23, S30) |
| Atkinson Hyperlegible Next (2.001) | 0.496 | 0.44, 0.69, 0.78, 0.47 | 0.44 | 0.632 (needs `tnum`) | 17,724 | Designed for low-vision legibility (S25); lowest x-height; no evidence of effect opened |
| Geist (1.800 in file) | 0.530 | 0.11, 0.71, 0.67, 0.36 | 0.11 | 0.600 (needs `tnum`) | 16,584 | I and l nearly identical; I found no documented fix for this on Geist's own page (S22) |
| Inter (4.001) | 0.546 | 0.00, 0.72, 0.72, 0.52 | 0.00 | 0.648 (needs `tnum`) | 21,588 | Capital I and lower-case l are identical bitmaps by default (0.00). Inter's site documents `cv08`, `ss02` and `ss04` for this (S26). With `ss02` baked in the proxy gives I/l 0.49, l/1 0.79, min 0.49; subset 20,288 bytes with `ss02` and `tnum` baked in (MEASURED, audit revision; the 21,588 in this column used another feature list). Used by Linear (S21) |
| IBM Plex Sans (3.201) | 0.516 | 0.49, 0.44, 0.68, 0.54 | 0.44 | default tabular | whole file 229,852 | Reserved Font Name |
| Source Sans 3 (3.052) | 0.478 | 0.14, 0.48, 0.49, 0.64 | 0.14 | default tabular | whole file 169,416 | Reserved Font Name; I and l near-identical |
| Segoe UI Variable (system, 2.03) | 0.500 | 0.16, 0.59, 0.54, 0.73 | 0.16 | 0.539 | not shipped | This PC only; proprietary; the baseline's font on Windows |

Reading the table without inventing a score. (1) A pair distance at or below about 0.16 means two glyph bitmaps that are nearly the same: Inter (0.00), Geist (0.11), Source Sans 3 (0.14) and Segoe UI Variable (0.16) fail for any text that shows identifiers, unless a disambiguation feature is switched on. The 0.16 threshold was fixed after I had seen the distances, so it is a post hoc exclusion, not a pre-registered one. Inter has documented features for this (S26), and I measured them in the audit revision: with `ss02` or `ss04` baked into the cmap the I/l distance is 0.49 (`cv08` alone: 0.39), which passes the threshold and is above Noto Sans (0.41) on the proxy. Inter was therefore not shown to be unfit; it is a fourth arm in study A. (2) Among the rest, Public Sans (0.51), Atkinson (0.44) and Noto Sans (0.41) differ by 0.1, which I treat as noise for an unvalidated proxy. (3) On the remaining measurable properties Noto Sans is ahead of Public Sans and Atkinson: higher x-height (+3.7% against Public Sans, +8.1% against Atkinson), tabular figures without a font-feature dependency and the narrowest tabular digit (0.572 em against 0.632 and 0.700), the smallest subset, and the same design family as the symbol fallback. Against Inter with `ss02` and `tnum` baked in it is behind on x-height (0.536 against 0.546, -1.8%) and on the proxy minimum (0.41 against 0.49, noise-level), and ahead on size (16,736 against 20,288 bytes, -17%), on needing no build-time feature freeze (the baked Inter needs a cmap remap step that departs from the plain subset recipe, and my naive freeze left the slashed zero 0.631 em wide against 0.648 em for the other digits) and on the symbol-fallback family. (4) Public Sans beats it only on the proxy and on visual character; Atkinson only on recency and on a stated design purpose. This is a tie on the evidence I have, resolved by the properties above, which is why the ADR registers a bake-off and a reversal rule. Noto Sans is a provisional default, not a finding.

An earlier draft weighted these criteria into one score. It gave different winners under different weightings (Geist won 55% of random weightings because it maximises recency and x-height while losing on I/l), so I dropped the composite and kept the table.

### 4.3 Mono candidates (MEASURED)

"Native" is how many of the 84 needed codepoints (section 4.4) the font has. "Off cell" is how many of those native glyphs have an advance different from the 0 glyph.

| Family (version in file) | x-height | Native of 84 | Off cell | I/l, I/1, l/1, 0/O | Min | Subset bytes |
|---|---|---|---|---|---|---|
| **Fira Code** (5.002; upstream latest 6.2, 2021-12-06, S24, S30) | 0.525 (wght 300 default instance; 0.527 in the shipped subset) | 72 | 0 | 0.67, 0.37, 0.77, 0.41 | 0.37 | 19,832 (ligature tables removed) |
| JetBrains Mono (2.211 in file; upstream v2.304, 2023-01-14, S27, S30) | 0.550 | 58 | 0 | 0.54, 0.48, 0.73, 0.20 | 0.20 | 14,524 |
| Noto Sans Mono (2.014) | 0.536 | 72 | 6 (U+21A6, 21D0, 21D2, 21D4, 2205, 25C7) | 0.37, 0.48, 0.40, 0.31 | 0.31 | 16,700 |
| Geist Mono (1.701) | 0.530 | 46 | 0 | 0.28, 0.47, 0.35, 0.31 | 0.28 | 14,164 |
| Red Hat Mono (1.030) | 0.488 | 22 | n/a | 0.35, 0.42, 0.49, 0.24 | 0.24 | 14,152 |
| Atkinson Hyperlegible Mono (2.001) | 0.496 | 21 | n/a | 0.57, 0.27, 0.58, 0.27 | 0.27 | 14,872 |
| IBM Plex Mono (2.3) | 0.516 | 39 | n/a | 0.20, 0.45, 0.46, 0.10 | 0.10 | whole file 39,176; Reserved Font Name |
| Source Code Pro (1.026) | 0.478 | 50 | n/a | 0.43, 0.37, 0.53, 0.30 | 0.30 | whole file 89,484; Reserved Font Name |
| Cascadia Mono (2407.024) | 0.518 | 45 | n/a | 0.54, 0.28, 0.61, 0.28 | 0.28 | whole file 210,224; Reserved Font Name |

Why Fira Code. It ties with Noto Sans Mono on native coverage (72) but every one of its notation glyphs sits on the 0.6 em cell (Noto Sans Mono has six that do not, which breaks column alignment in traces and source views), it carries 8 of the 9 keyboard glyphs and all 10 box-drawing glyphs natively (Geist Mono 5 and 10, JetBrains Mono 4 and 10, Noto Sans Mono 0 and 10), its shipped x-height (0.527) is within 2% of the sans (0.536), and it has the best minimum of the confusable-pair proxy (0.37). JetBrains Mono is smaller and has the highest x-height, but 26 needed glyphs would come from a foreign face, including the core logic symbols. The proxy gives JetBrains Mono the weakest 0/O distance of the leading mono candidates (0.20), which the study checks. The "unmaintained" concern applies to Fira Code as much as to Public Sans: the last upstream release is 2021-12-06. Both are pinned files, so the risk is missing fixes, not breakage.

No peer-reviewed comparison of code typefaces or of monospace against proportional text for identifiers was found this session: **UNVERIFIED**. The choice rests on coverage, cell alignment and the proxy, and the bake-off in section 10 exists for that reason.

Ligatures. Fira Code carries programming ligatures. Notation must show what was written (`->` must not fuse), so the `calt`, `liga` and `clig` tables are removed when the subset is built (verified: the shipped GSUB has only `locl` and `zero`), rather than relying on CSS alone; `font-variant-ligatures: none`, which disables all ligatures and contextual forms (S35), is also set as a second guard.

### 4.4 Symbols EIJA needs

**Headline: 84 of 84 covered in mono, 72 of 84 on the cell; 74 of 84 in sans (all 65 sans-usable).**

The set is mostly a **design assumption**, not observed use. MEASURED (audit round 2, `git ls-files` outside `docs/hci`, UTF-8 files): tracked files contain 9 distinct non-ASCII characters, 8 of them in the 84 (U+00B7, U+00D7, U+2013, U+2014, U+201C, U+201D, U+2026, U+2192; the ninth is U+FF0B fullwidth plus in `index.html`). The other 76 are anticipated from the formal techniques named in ADR-0018 (TLA+, property tests, mutation; S31) and interface needs (key labels, tree text views). The system faces on this PC cover all 8 attested characters; Segoe UI Variable covers 44 of 84 and 34 of the 65 sans-usable, Segoe UI 34 and 34, Consolas 44 and 34 (fontTools cmap; the browser may fall back per glyph to Segoe UI Symbol, which has 84 of 84, not rendered, UNVERIFIED). Figures in `fonts.lock.json` under `verification.system_font_coverage_of_symbol_sets`; the 84 with names under `symbol_sets`.

| Set | Codepoints | Sans stack | Mono stack |
|---|---|---|---|
| arrows (10) | U+2190-2194, U+21A6, U+21B3, U+21D0, U+21D2, U+21D4 | 10 (Symbols) | 10 (6 Fira, 4 Symbols) |
| logic (11) | negation, conjunction, disjunction, turnstile, double turnstile, up and down tack, for all, exists, not exists, identical to | 11 | 11 |
| temporal (3) | U+25A1, U+25C7, U+25CB | 3 | 3 |
| sets (12) | membership, subset, union, intersection, empty set, set minus, N, Z, R, ring operator | 12 | 12 |
| relations (8) | at most, at least, not equal, approximately, plus-minus, times, division, minus | 8 | 8 |
| brackets (7) | angle and white square brackets, double bar, lambda, end of proof | 7 | 7 |
| typographic (14) | ellipsis, middle dot, bullet, dashes, quotes, primes, degree, section, no-break space | 14 | 14 |
| keyboard (9) | Command, Option, Shift, Control, Return, Delete, Escape, Tab, return arrow | 4 of 9 (U+21B5, 21E5, 21E7, 23CE from Symbols; the other 5 missing) | 9 |
| box drawing (10) | U+2500, 2502, 250C, 2510, 2514, 2518, 251C, 252C, 2534, 253C | 5 of 10 | 10 |
| **Total** | 84 | **74 of 84** | **84 of 84** |

Rule from the table: keyboard and box-drawing glyphs are used only in a mono context (`kbd`, text views). A sans context must not depend on them. In a mono context 12 glyphs come from the fallback face and none is on the cell: U+2032, 2033, 21A6, 21B5, 21D0, 21D2, 21D4, 220E, 2216, 2218, 27E6, 27E7 (advances 0.23 to 1.26 em against the 0.6 em cell, MEASURED). MEASURED in Chromium: `P ⇒ Q` in the mono style was 47.8 px against 42.0 px for five cells. Do not put those 12 inside column-aligned text; a markup lint should list them. That is 14% of the set and includes core logic and relation notation (⇒, ⇔, ↦, ⟦ ⟧, ∘), exactly what trace and guard views show. An on-cell `EIJA Symbols` was considered and not built: 7 of the 12 are narrower than the cell and could be padded to 0.6 em, 4 (0.72 to 1.01 em) could be padded to two cells, and U+21D4 (1.26 em) would need about 5% horizontal compression to fit two cells. It is an OFL-permitted modification (no Reserved Font Name) but changes the rebuild recipe and the hashes; deferred until the lint shows these glyphs in real column-aligned text.

Status glyphs (proved, refuted, unknown, stale, conflict) are drawn as SVG by the iconography aspect, not taken from any font (VIS§4 item 2, S32). Fonts are not relied on for meaning.

### 4.5 Font stacks

- Sans: `"EIJA Sans", "EIJA Symbols", system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.
- Mono: `"EIJA Mono", "EIJA Symbols", ui-monospace, "Cascadia Mono", Consolas, SFMono-Regular, Menlo, monospace`.
- The system tail is only for a failed font load. It is not metric-matched (`size-adjust` and `ascent-override`, S10, are not used because the tail differs per operating system and I could measure only Windows), so a failed load changes widths by about 6% to 9% (section 3.3).
- `font-display` compared (S3, S10). `swap` (extremely small block period, infinite swap period) always ends in the EIJA faces but reflows once on a slow load by that 6% to 9%. `optional` (extremely small block period, no swap period) never reflows but can leave a session in the system tail, which defeats reproducible widths and notation coverage. A `size-adjust` fallback face would shrink the reflow but can be tuned only for the one operating system measured. `swap` with preload is kept; the synthetic 0-shift result does not settle it, so validation item 4 runs on the slow HDD and names the switch condition.

### 4.6 What each rejected option costs (one line each)

| Option | Reason it is not chosen |
|---|---|
| Keep the system stack | Zero bytes and no CSP change, and it covers all 8 notation characters attested today; but no `tnum` guarantee on every system, 44 of the 84 anticipated codepoints on this PC's Segoe UI Variable and Consolas (34 of the 65 sans-usable), widths differ per operating system so layout geometry cannot be reproduced. The rejection rests on anticipated notation and reproducible widths. Kept as the study A control. See ADR option A |
| Hybrid: system sans, ship only mono and symbols | 24,168 bytes and two files; keeps mono cell alignment and 84 of 84 mono coverage; but sans widths (most of the UI) stay operating-system dependent. First fallback if study A's system-stack control is not worse (ADR option H) |
| Inter plus JetBrains Mono | I = l by default; the documented fix (`ss02`, S26) has to be baked in at build time, which I measured only in the audit revision (20,288 bytes, I/l 0.49). It is not rejected on evidence of unfitness: it is a study A arm. Linear uses Inter for its own product (S21), a reason to look, not a reason to copy. JetBrains Mono has 58 of 84 notation glyphs, so 26 would come from a foreign face |
| Public Sans plus Fira Code | Strongest on the proxy and distinctive, but wider tabular digits (0.700 em), a font-feature dependency for tabular figures, unmaintained upstream, and the symbol fallback comes from a different design family |
| Atkinson Hyperlegible Next plus Fira Code | Lowest x-height of the candidates, so the smallest predicted angular size at any nominal size; purpose-built for low vision, but no evidence of effect was opened |
| Geist plus Geist Mono | I/l distance 0.11; Geist Mono covers 46 of 84; no disambiguation feature found |
| IBM Plex, Source Sans and Code Pro, Cascadia | Reserved Font Names force a rename to subset, or 39 KB to 230 KB whole files |
| One family, all monospace | A 0.6 em cell is 13% wider than the average character of the domain terms in EIJA Sans (0.529 em, MEASURED from advances over the 19-term list stored in `fonts.lock.json` `verification.average_domain_term_character_em`, internal spaces of the two multi-word terms included, no spaces between terms; the figure depends on the sample, a 3-term sample gave 0.508 em); Windows guidance recommends one UI font (S18); prose reading would lose (PREDICTION from width; no reading test) |

## 5. Scale, weights, line height, measure

### 5.1 The scale

| Token | px (rem) | Line box | Weight | x-height px | Used for | Reference |
|---|---|---|---|---|---|---|
| `font.size.xs` | 12 (0.75) | 16 | 400 | 6.4 | caption, dense status words | Windows caption 12/16, Primer caption 12 px (S18, S19) |
| `font.size.sm` | 14 (0.875) | 20 | 400 or 600 | 7.5 | default UI, code | Windows body 14/20, Primer body medium 14 px (S18, S19) |
| `font.size.md` | 16 (1) | 24 | 400 | 8.6 | reading text | Primer body large 16 px, title small 16 px (S19) |
| `font.size.lg` | 20 (1.25) | 28 | 600 | 10.7 | headings, roll-up counts | Windows subtitle 20/28, Primer title medium 20 px (S18, S19) |
| `font.size.xl` | 24 (1.5) | 32 | 600 | 12.9 | view title | none exactly (Windows 28/36, Primer 32) |

Steps are 1.17, 1.14, 1.25 and 1.2 apart. The dossier's starting hypothesis was ratio 1.2 from 13 px (VIS§2.7); I moved the base to 12 px and rounded to whole pixels so every line box is a multiple of 4 px (Primer's foundations page says its unitless line heights align to a 4 px grid, S20; I did not confirm that its own body medium at 0.875rem sits on it, so this is a loose precedent). Whole pixels avoid fractional glyph positions at 1x; that is a rendering expectation I did not test.

Exact line boxes. 1.3333 x 12 px is 15.9996 px, not 16, and 1.4286 x 14 px is 20.0004 px. The token build therefore emits the exact ratios `calc(4 / 3)` and `calc(10 / 7)` (the tokens carry a six-decimal number and the exact form in `$extensions`), and validation item 1 checks computed line boxes in the browser. A browser may still round to its layout unit; I did not measure that (UNVERIFIED).

Density modes. A compact mode uses the same tokens with a 24 px row (16 px line box plus 8 px padding) and needs no extra size. Rows are 28 px comfortable (20 plus 8), both at least the 24 px target minimum of WCAG 2.5.8 (S34, dossier VIS Q2). PREDICTION, Fitts index of difficulty at D = 400 px: 4.14 bits at 24 px, 3.93 at 28, 3.75 at 32 (Shannon form; one-dimensional, mouse; not applied to the Approve control, P2). The layout aspect owns this model.

### 5.2 Rules

| Rule | Value | Basis |
|---|---|---|
| Units | rem for size, unitless for line height | Resizable text (S12); Primer uses rem tokens (S20) |
| Weights | 400 and 600; 600 only from 14 px | S18 |
| Italic | none shipped, none used; `font-synthesis: none` | S18 (italics excluded from the Windows ramp); S6 |
| Tracking | 0 (token `font.letterSpacing.none`, 0 px); no `text-transform` | Design rule from the baseline count (7 values, MEASURED); the token format requires the property, so it is set to 0 explicitly (S1 section 9.8) |
| Caption | at most about 5 words; never a status, count, refusal reason or UNKNOWN; never weight 600 | Windows minimum 12 px Regular (S18) |
| Truncation | end ellipsis only; the full string is the accessible name and shows on selection; never truncate a status word or a count | Design rule. Microsoft's page contradicts itself (a summary table says use ellipses in most cases; a later section recommends clipping and says not to use ellipses to avoid clutter unless containers are not well-defined), so it is not cited as support (S18) |
| Long identifiers | `overflow-wrap: anywhere` inside cells; never break a status word | baseline already does this for output |
| Numerals | `font-variant-numeric: tabular-nums` (a no-op in EIJA Sans, MEASURED, so a fallback font also aligns) | S4 |
| Zero | mono uses `font-feature-settings: "zero" 1` | S28 |
| Ligatures | none in mono (removed at build); `font-variant-ligatures: none` also set | S35 |
| Contrast class | `title` and `heading` (20 px at 600 is above 18.5 px bold) may meet 3:1; every other role needs 4.5:1 | S14 |
| Prose amount | at most about 30 words of `prose` per primary viewport | anti-slop rubric target |

### 5.3 Measure

Text sample: 931 words of repository prose (README, sentences of 8 or more words). In EIJA Sans the average advance is 0.472 em including spaces and `0` is 0.572 em, so 1 ch holds 1.211 characters (MEASURED). 56 ch is therefore 68 characters (58 non-space) at 16 px, 513 px wide (PREDICTION by arithmetic). Sources: WCAG 1.4.8 (AAA) at most 80 characters (S13); Microsoft 50 to 60 letters per line and not more than 60 (S18); Primer around 80 or fewer (S20); the dossier notes Dyson 2004 found the optimum task-dependent (VIS§2.7, not re-opened by me). 56 ch does not sit inside every source. It is inside WCAG 1.4.8 and Primer (about 68 characters against about 80). Against Microsoft it depends on what "letters" means: 58 non-space characters fit 50 to 60, but 68 characters with spaces exceed "not more than 60 characters". I therefore treat 56 ch as a hypothesis at the upper edge of one source's range, not as a value the sources support; 50 ch (about 61 characters) would sit at that limit, and study B can test both. For source, JSON and trace views 100 ch, where 1 ch is exactly one cell.

## 6. When to use monospace

One rule: **mono marks text that must be compared or copied exactly, or that is code or notation.** Sans marks language. Mono is not an emphasis style, not a "machine-generated" style and not an authority style.

| Text (real excursion-workflow examples) | Face | Reason |
|---|---|---|
| Ubiquitous-language terms: Excursion, Registrar, Submitted | sans `ui` | Words; read as language, not compared character by character |
| Transition ids: TR-SUBMIT, TR-REJECT | mono `code` | Literal, case-sensitive, copied into commands |
| Guard names: actor_active, operation_binding | mono `code` | Literal identifiers |
| Effect names: Audit:ExcursionRejected, PaymentCaptured | mono `code` | Literal, contain punctuation |
| Evidence status words: PASS, UNKNOWN, STALE, NOT_RUN | mono `code-strong` (non-PASS states, the status aspect decides) or `code-small` in dense rows | Closed kernel vocabulary shown exactly as stored (no `text-transform`) |
| Revision hash, seed, replay token | mono `code` | Compared character by character; the value is never invented in mockups: mark it as a placeholder |
| Formal notation: actor_active ∧ role_current ∧ state_equals | mono `code` | Symbols on one cell (MEASURED); no ligatures |
| Source, JSON, counterexample trace rows | mono `code`, measure 100 ch | Column alignment |
| Key labels: Ctrl, K, ⌘, ⇧ | mono in `kbd` | Literal key names; the four Mac modifier glyphs are native in EIJA Mono |
| Counts and versions in a table column | sans tabular | Numbers, not tokens. Exception: inside a roll-up such as "3 UNKNOWN" the count uses the status face so digits and word align |
| Explanations, AI rationale, refusal reasons, onboarding | sans `prose` | Language. Not italic; provenance is shown by badge and outline, not by face (P9) |
| Buttons, tabs, menu items, palette result names | sans `ui` or `ui-strong` | Language; the Approve label is not larger than sibling actions (P2) |

Counter-evidence. I looked for a product that sets tabular data in a mono face and found none in the sources opened. Vercel's Geist typography page lists tabular numerals as a modifier of a sans label style (Label 13, "with Strong, and Tabular (123)") and describes its mono styles as pairing with other sizes or for inline code (S22, re-read in the audit revision), which agrees with this design. Mono for counts inside a roll-up ("3 UNKNOWN") is our own choice with no source either way; study C therefore includes a counts task in both faces as an open question, not as a response to counter-evidence.

## 7. Roles

Nine text tokens, all in `typography.tokens.json` under `text.*`.

| Token | Face, size/line, weight | Where (task ids from `design/brief.json`) |
|---|---|---|
| `text.title` | sans 24/32, 600 | View title, one per view (T02, T06) |
| `text.heading` | sans 20/28, 600 | Chapter and section headings; roll-up counts at level 0 (T02, T03, T06, T08) |
| `text.prose` | sans 16/24, 400 | AI rationale, refusal reason, help, first-run (T10, T13) |
| `text.ui` | sans 14/20, 400 | Tree rows, table cells, buttons, inputs, palette results (T03, T05, T09, T11) |
| `text.ui-strong` | sans 14/20, 600 | Column headers, selected row, decision button label (T08) |
| `text.caption` | sans 12/16, 400 | Timestamps, "n of m" position, secondary metadata (T05, T12) |
| `text.code` | mono 14/20, 400 | Ids, hashes, paths, guards, effects, notation, source and trace (T06, T07, T12) |
| `text.code-strong` | mono 14/20, 600 | Status words and counts on summaries and the decision surface (T06, T08, T14) |
| `text.code-small` | mono 12/16, 400 | Status words in dense rows, hash prefixes in tables (T05, T14) |

Invariant links. UNKNOWN is never set smaller than PASS in the same context and never uses `caption` (P1). The Approve control uses `ui-strong` like its siblings; type never makes it larger or more prominent (P2). Untrusted text reaches the page only through DOM text nodes (ADR-013); this aspect adds fonts and CSS, not a rendering path, so no untrusted markup is introduced. Text outside the subset (other scripts, emoji) falls back to system fonts; that changes appearance only.

## 8. Delivery, security and licences

Requirements on other lanes (this aspect states them and does not implement them):

| Requirement | Evidence | Owner |
|---|---|---|
| Add `font-src 'self'` to the CSP | MEASURED: with the current CSP Chromium 151 refused all three files and logged a `default-src` violation; with `font-src 'self'` all loaded. MDN: a missing `font-src` falls back to `default-src` (S2) | Security boundary and assets aspect (`http.py`) |
| Allow the three `.woff2` files and three licence texts on `/assets/` with `Content-Type: font/woff2` and `nosniff` | `http.py` serves only `app.js` and `app.css` today (S31). Python's MIME table may not know woff2, so set it explicitly | same |
| Keep `Cache-Control: no-store` for now | MEASURED loopback median 6.7 ms for the three files; revisit if the Studio is served remotely | same |
| `<link rel="preload" as="font" type="font/woff2" crossorigin>` for the sans and mono files | `crossorigin` is required even for same-origin fonts; preload follows CSP (S7) | Studio HTML |
| `@font-face` with `font-display: swap`, weight range `400 600`, `unicode-range` per file (Appendix B) | S3, S5, S8; the exact CSS was run in the smoke test | Tokens aspect (generation) |
| Ship `OFL.txt` for each family and the three copyright lines; replace the sentence in `NOTICE.md` that says no font files are bundled | OFL FAQ 1.10 (S15); NOTICE.md (S31) | Integrator |
| Add three rows to `docs/oss/REGISTER.md` (text in `fonts.lock.json`, `register_rows_needed`) | ADR-0016 (S31) | Integrator |
| Regenerate `MANIFEST.json`; `package-data` already includes `resources/**/*` | `pyproject.toml` (S31) | Integrator |

Licences (MEASURED from the files at the pinned commit): Noto Sans "Copyright 2022 The Noto Project Authors", Fira Code "Copyright 2014-2020 The Fira Code Project Authors", Noto Sans Math "Copyright 2022 The Noto Project Authors"; all SIL Open Font License 1.1; none declares a Reserved Font Name, so subsetting does not require a rename (S15 items 2.6 and 3.8). The name table is left unchanged; the CSS family names `EIJA Sans`, `EIJA Mono` and `EIJA Symbols` are CSS aliases only. A Chromium platform-font query reports the upstream names ("Fira Code Light" for the mono file, because its name table was not edited; harmless).

Reproducibility. Appendix A rebuilds the three files from `fonts.lock.json`: it downloads each source, checks the source sha256, rebuilds and compares. MEASURED 2026-09-29: 3 of 3 sha256 matched after a fresh download (fontTools 4.56.0, Python 3.12.10). Another fontTools or brotli version may change bytes without changing glyphs.

## 9. Interfaces and assumptions

| Aspect | Typography assumes or provides | Status |
|---|---|---|
| Colour | Provides contrast classes per role (`title` and `heading` may use 3:1; all others 4.5:1). Assumes no weight or size change between light and dark. Colour must report an APCA Lc for `caption` and `code-small` as advisory (APCA is unratified, C10) | Assumption; contrast itself UNKNOWN here |
| Layout | Provides line boxes (16, 20, 24, 28, 32) and row heights 24 and 28. Requires that layout geometry be measured with the shipped fonts, not system fonts (section 3.3). Mono `ch` is one cell; prose `ch` is not average width | Stated interface |
| Status and evidence | Provides two weights and two mono sizes. Requires: UNKNOWN never smaller than PASS; no status word in `caption`; the status aspect chooses which states use `code-strong` | Stated interface |
| Iconography | Status glyphs are SVG, not font glyphs. Key labels are `kbd` in mono | Stated interface |
| Content | `caption` at most about 5 words; `prose` at most about 30 words per primary viewport | Stated interface |
| Motion | Font swap is not animated and carries no meaning | Stated interface |
| Security boundary | Needs the CSP, allowlist and cache decisions in section 8 | Open dependency: no font renders until done |
| Tokens | This file is DTCG 2025.10; colour tokens use `colorSpace`, `components`, `hex` (S1). Typography tokens set all five required properties, including `letterSpacing` as 0 px. `ch` is not a DTCG unit, so `font.measure.*` are numbers with the unit in `$extensions` | Stated interface |

## 10. Validation plan and study arms

Fixed before running. Prototype measurements (one browser at a time, 1440x900 and 1280x720, device scale factor 1):

| # | Measurement | Pass criterion |
|---|---|---|
| 1 | Token lint on generated CSS, plus computed line boxes in the browser | at most 5 distinct font sizes, 2 weights, 1 letter-spacing value, 0 italic, 0 `text-transform`; every token has the five DTCG typography properties; computed line box of each role within 0.01 px of 16, 20, 24, 28, 32 |
| 2 | Slop-budget script, computed styles per viewport | at most 5 distinct sizes (rubric limit 6), 2 text families in the first position, no text below 12 px, no weight 600 below 14 px |
| 3 | Font smoke test in the real Studio (CDP `getPlatformFontsForNode`) | 0 CSP font violations; all 3 faces `loaded`; every text node drawn by an EIJA face except listed fallback glyphs |
| 4 | Load probe in the browser, 30 or more cold-cache loads of the real Studio served from the checkout on the reference PC's slow HDD (D:, `AGENTS.md`) | p95 of the three font requests at most 50 ms (half the 0.1 s class); layout shift at most 0.01 on load; if shift exceeds 0.01, compare `optional` and a size-adjusted fallback before release |
| 5 | Residual-glyph lint | 0 of the 12 off-cell codepoints inside column-aligned text |
| 6 | WCAG 1.4.12 override (line height 1.5, letter 0.12 em, word 0.16 em, paragraph 2 em) and 200% zoom and 320 px reflow | no clipped or overlapping text, no lost function |
| 7 | Rendering check at 100% and 125% scaling, Windows, one screenshot per role | visual inspection only; not a legibility measure |

User-study arms (the study protocol is owned by another lane; typography contributes these):

- Design. Within-subject, counterbalanced (Latin square over conditions). Study A: sans family at 14 px, five conditions: EIJA Sans (Noto Sans), Public Sans, Atkinson Hyperlegible Next, Inter with `ss02` and `tnum` baked in, and the system sans stack that the baseline resolves to (control; it answers whether the whole change is worth 40,904 bytes and a CSP change, which no other arm can). Study B: default UI size 14 against 15 px in the chosen family, and prose measure 50 ch against 56 ch. Study C: mono (Fira Code, JetBrains Mono, Noto Sans Mono) and, separately, counts in a roll-up set in sans against set in mono. Study D: status words at 12 px `code-small` against 14 px `code-strong`.
- Participants and trials. At least 12 engineers per study is the dossier floor (VIS§5), not a computed sample size: no power calculation was done because no pilot variance exists. After a pilot of about 5 (formative; finds problems, cannot compare conditions) the sample size is computed from the pilot variance of the primary measure and this file is amended before the study runs. Proposed 8 trials per task per condition, so an identifier task with 12 items per trial gives many item-level errors per participant; the unit of analysis is the participant mean or proportion. Include participants who use corrective lenses, since the model assumes normal vision.
- Tasks (excursion domain). Find the one odd identifier in a list of 12 that mixes I, l, 1, 0 and O; decide whether two 12-character hash strings are equal; count UNKNOWN rows in a 20-row evidence list; transcribe `actor_active ∧ role_current ∧ state_equals`; read a table of counts with mixed digit widths.
- Measures. Errors, time on task, UNKNOWN items misread as PASS (target zero), raw NASA-TLX, preference rank.
- Analysis and multiplicity. Paired differences with confidence intervals. One primary contrast per study, fixed beforehand: A, chosen face against the system stack on identifier-task error rate (95% interval); B, 14 against 15 px on time on task (95%); C, Fira Code against JetBrains Mono on identifier-task error rate (95%); D, 12 px against 14 px on UNKNOWN misreads. Replacement of the chosen face in A: each of the three alternative faces is compared with the chosen face on identifier-task error rate as one family of three, with Bonferroni-adjusted 98.3% intervals; a face replaces the choice only if its interval excludes 0 and the difference is at least 5 percentage points (a hypothesis, not an established effect size), or its time difference is at least 10%. All other measures and contrasts (time, NASA-TLX, preference, secondary tasks) are exploratory, reported with unadjusted 95% intervals and labelled exploratory. Four arms and several measures inflate false positives; that is why only the stated contrasts can change a decision.
- Stop criteria. Stop and raise all status words to 14 px if any participant misreads UNKNOWN as PASS in the 12 px arm. Redesign the mono choice if the identifier error rate exceeds 10% in any mono condition.

Status of results: none. **No user-benefit claim is made until results exist.**

## 11. Open questions and UNVERIFIED items

| Item | Effect | How to close |
|---|---|---|
| Viewing distances 500 and 600 mm are assumed | Whether 14 px reaches the 0.2 degree floor | Measure with the study cohort or cite a source |
| Proxy distance is not validated against human confusion | Noto Sans vs Public Sans vs Atkinson is a tie | Study A |
| No source opened on code typefaces or mono against proportional for identifiers | Fira Code choice rests on coverage and cell alignment | Study C; find a source |
| Beier and Larson 2010 (misrecognised letters) and Bigelow 2019 not read | No claim built on them | Read them |
| macOS, Linux, high-DPI, hinted rendering not measured | Unhinted 12 and 14 px rendering quality unknown outside Windows and Chromium 151 headless | Validation item 7 on more systems |
| Dark-mode weight perception | Whether 400 looks too thin on dark | Colour aspect study |
| Public Sans, Atkinson and Fira Code are not updated upstream (2022-05, 2024-11, 2021-12) | Missing fixes only; files are pinned | Recheck before release |
| Fira Code in the pinned file is 5.002; upstream 6.2 exists | Coverage may differ | Re-measure before bumping |
| Noto Sans release date and maintenance not opened | Recency cannot be scored | Open the Noto repository |
| Browser p95 font load | Only a Python loopback client was measured | Validation item 4 |
| Behaviour of `font-display: swap` on a slow disk (reference PC has an HDD, `AGENTS.md`) | Possible visible swap | Validation item 4 on the HDD |
| Flip of the 14 versus 15 px default, and of the 16 px prose default, inside the distance band | Convention decides | Study B |
| Inter with `ss02` and `tnum` baked in was measured with a naive cmap freeze; the slashed zero came out 0.631 em wide against 0.648 em | A real build needs the tabular form of the zero; size 20,288 bytes may change slightly | Build it properly if it enters study A |
| The Chromium layout unit may round line boxes such as 15.9996 px | Computed line boxes may differ from 16, 20 px; the `calc()` form removes the cause but was not run | Validation item 1 |
| Microsoft's 50 to 60 "letters" per line: does it count spaces? | Whether 56 ch (68 characters) is inside its range | Study B measure arm |
| 76 of the 84 notation codepoints are anticipated, not attested | The coverage argument against the system stack rests on future use | Re-scan when formal views ship; study A system-stack control |
| Does Chromium fall back per glyph to Segoe UI Symbol (84 of 84) for the system stack? | Rendered coverage of option A and H may be higher than the named-face counts | Render the 84 in the system stack with `getPlatformFontsForNode` |
| 12 off-cell glyphs in mono (14%), including ⇒ ⇔ ↦ ⟦ ⟧ ∘ | Traces and guards using them cannot be column-aligned | Residual-glyph lint; build an on-cell `EIJA Symbols` if the lint finds real use |

## 12. Sources (all opened 2026-09-29)

| Id | URL | Type | Used for | Confidence |
|---|---|---|---|---|
| S1 | https://www.designtokens.org/tr/2025.10/format/ | Standard (Community Group Report, not a W3C Standard) | section 9.8: the typography value must contain fontFamily, fontSize, fontWeight, letterSpacing (a dimension) and lineHeight (a number); dimension units px and rem; groups; `$extensions`. My first read (a truncated fetch summary) wrongly reported no letterSpacing; the audit and my re-read of the downloaded spec corrected it | High |
| S2 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/font-src | Official docs | `font-src` falls back to `default-src` | High |
| S3 | https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display | Official docs | `swap` definition (extremely small block period, infinite swap period); the page contains no advice on avoiding `block` | High |
| S4 | https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant-numeric | Official docs | `tabular-nums`, `slashed-zero` and OpenType mapping | High |
| S5 | https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/unicode-range | Official docs | `unicode-range` behaviour | High |
| S6 | https://developer.mozilla.org/en-US/docs/Web/CSS/font-synthesis | Official docs | `font-synthesis: none` | High |
| S7 | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/preload | Official docs | `crossorigin` needed for font preload; `as` lets the browser apply the correct content security policy to the resource | High |
| S8 | https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_fonts/Variable_fonts_guide | Official docs | `wght` axis and `font-weight` range | High |
| S9 | https://developer.mozilla.org/en-US/docs/Web/CSS/font-size-adjust | Official docs | considered, not used (x-heights within 2%) | High |
| S10 | https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/size-adjust | Official docs | considered, not used | High |
| S11 | https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html | Standard (Understanding) | SC 1.4.12 values | High |
| S12 | https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html | Standard (Understanding) | SC 1.4.4, 200% | High |
| S13 | https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html | Standard (Understanding) | SC 1.4.8 at most 80 characters, space-and-a-half | High |
| S14 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | Standard (Understanding) | large text is 18 pt or 14 pt bold, about 24 and 18.5 px | High |
| S15 | https://openfontlicense.org/ofl-faq/ | Licence FAQ | subsetting is modification (2.6); rename needed only if RFNs are declared (3.8); unmodified WOFF2 (2.2.1); webfont use (2.1) | High |
| S16 | https://doi.org/10.1167/11.5.8 (abstract read from Europe PMC record PMC3428264 via https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1167/11.5.8&format=json&resultType=core; the journal page returned 403) | Peer-reviewed review, Journal of Vision 2011 | fluent range 0.2 to 2 degrees of x-height | High for the abstract; full text not read |
| S17 | https://www.w3.org/TR/css-values-4/#reference-pixel | Standard | 1 px = 1/96 in, reference pixel 0.0213 degrees at 28 in | High |
| S18 | https://learn.microsoft.com/en-us/windows/apps/design/style/typography | Official docs | Windows type ramp, minimums, one font, no italics, 50 to 60 letters per line and not more than 60 characters. The page contradicts itself on ellipses, so it is not used for that | High |
| S19 | https://primer.style/product/primitives/typography/ | Official docs | Primer sizes in rem and roles; weights (base scale 300 to 600, roles use 400 to 600); stacks. The body line-height value is not confirmed | High for sizes and weights |
| S20 | https://primer.style/foundations/typography | Official docs | rem, 4 px line-height grid, about 80 characters | High |
| S21 | https://linear.app/now/how-we-redesigned-the-linear-ui | First-party blog | Linear uses Inter and Inter Display | Medium |
| S22 | https://vercel.com/geist/typography | Official docs | tabular numerals as a modifier of sans label styles; mono styles for pairing and inline code | High |
| S23 | https://github.com/uswds/public-sans | Repository | OFL, v2.001, unmaintained | Medium (page summary) |
| S24 | https://github.com/tonsky/FiraCode | Repository | OFL, 6.2 (2021-12-06), variable font. Its README describes enabling `calt` (IE 10+, Edge Legacy) and `font-variant-ligatures: contextual` (CodeMirror); it does not describe disabling ligatures, so it is not cited for that (raw README re-read in audit round 2) | High for version, date and licence |
| S25 | https://github.com/googlefonts/atkinson-hyperlegible-next | Repository | OFL, design goal, v2.001 (2024-11-20) | Medium (page summary) |
| S26 | https://rsms.me/inter/ | First-party site | `ss02` disambiguation, `tnum`, `zero` | Medium |
| S27 | https://github.com/JetBrains/JetBrainsMono | Repository | OFL, x-height goal, NL variant | Medium |
| S28 | https://learn.microsoft.com/en-us/typography/opentype/spec/features_pt | Standard | `tnum` definition | High |
| S29 | https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl | Font source (OFL files and licence texts, pinned commit) | all font files measured | High |
| S30 | GitHub API `repos/{tonsky/FiraCode, uswds/public-sans, JetBrains/JetBrainsMono, rsms/inter, vercel/geist-font}/releases/latest` via `gh api` | First-party API | release tags and dates: Fira Code 6.2 2021-12-06, Public Sans v2.001 2022-05-11, JetBrains Mono v2.304 2023-01-14, Inter v4.1 2024-11-16, Geist v1.7.2 2026-06-01 | High |
| S31 | Repository files: `src/eija_studio/resources/web/app.css`, `index.html`, `src/eija_studio/interfaces/http.py`, `NOTICE.md`, `pyproject.toml`, `docs/oss/REGISTER.md`, `docs/adr/0000-poc-decision-log.md`, `docs/adr/0018-formal-vv-portfolio.md`, `examples/excursion-baseline.json` | Primary | baseline, CSP, constraints, real domain strings | High |
| S32 | `docs/hci/research/visual-design-foundations.md`, `SYNTHESIS.md`, `PRINCIPLES.md` | Research dossiers (this lane) | budgets, principles, baseline counts | Medium |
| S33 | https://www.nngroup.com/articles/response-times-3-important-limits/ (opened 2026-09-29, audit revision) | Practitioner | 0.1 s, 1 s, 10 s limits | High for the wording; medium as evidence for this decision |
| S34 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html (opened 2026-09-29, audit revision) | Standard | 24 by 24 CSS px target | High |
| S35 | https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant-ligatures (opened 2026-09-29, audit round 2) | Official docs | `none` disables all ligatures and contextual forms | High |
| M1 | `design/fonts.lock.json` and the scripts in Appendix A | MEASURED by me | font metrics, coverage, sizes, browser smoke, loopback | Medium (single machine) |

## 13. Changes after the audit (2026-09-29)

| # | Finding | Result | Change |
|---|---|---|---|
| 1 | DTCG 2025.10 typography type has no letterSpacing | Confirmed wrong (spec section 9.8 requires it, its example uses it) | Claim removed everywhere; `font.letterSpacing.none` added; all nine `text.*` tokens set it; letter-spacing 0 is now justified only by the baseline count and a design rule |
| 2 | Geist sets tabular data in mono | Confirmed wrong (tabular is a modifier of a sans label style; 29 style class names by my regex, not 28) | Counter-evidence rewritten; option E drawback removed; class count dropped; study C counts arm re-justified as an open question |
| 3 | MDN advises avoiding `block` | Confirmed: no such text on the page | Attribution deleted; `swap` definition kept |
| 4 | NN/g and target-size not re-opened | Confirmed | Both opened; source rows updated |
| 5 | Inter dismissed unfairly | Confirmed; Inter with `ss02` or `ss04` baked in has I/l 0.49 | Measured; Inter is a study A arm; the claims "highest x-height" and "passes every hard filter" were removed; Noto Sans is provisional |
| 6 | 16 px prose "reaches" 0.2 degrees | Confirmed: 8.5% short at 710 mm | Rationale rewritten; the floor is not evidence for 16 px |
| 7 | 56 ch inside the union of sources | Confirmed loose (68 characters against Microsoft's 60) | Stated as a hypothesis at the upper edge |
| 8 | Study rule thin | Confirmed | Trials, sample-size status, multiplicity, system-stack control added |
| 9 | Line-height decimals | Confirmed arithmetic (15.9996, 20.0004) | Exact `calc()` ratios; browser check added; browser rounding UNVERIFIED |
| 10 | Fira Code x-height 0.525; 18% short | Confirmed: shipped 0.5265; 18.9% by size, 18.8% by angle | Values updated, basis stated |
| 11 | ADR template sections missing | Confirmed | Licence check, Revisit when and Definition of ready added to the ADR |
| 12 | OFL item numbers; Primer weights; Microsoft ellipsis contradiction; preload wording | Confirmed | Corrected in the source table and rules |

Audit round 2 (2026-09-29). Each finding re-checked by me before changing anything.

| # | Finding | My check | Change |
|---|---|---|---|
| R1 | Equal x-height figures mixed two methods (1.9%, 0.8%) | Confirmed: exact x-height scaling gives +0.75% and -1.58%; exactly 15.0 px gives +0.70% and -1.82% | One method stated (exact x-height); 0.75% and 1.6% in section 3.3 and the ADR, 15.0 px values in brackets; unrounded inputs in `fonts.lock.json` |
| R2 | Fira Code README does not describe disabling ligatures | Confirmed from the raw README: it describes enabling `calt` and `contextual` only | Sentence deleted; MDN `font-variant-ligatures` (S35) cited for `none`; S24 row rewritten |
| R3 | ADR Definition of ready box unticked; rubric row shortened | Confirmed | Box ticked; full template wording restored with the gradient half marked not applicable |
| R4 | 84-codepoint set mostly anticipated; hybrid never listed | Confirmed: 9 distinct non-ASCII characters in tracked files, 8 in the 84; system faces cover all 8, and 34 of 65 sans-usable | Stated as a design assumption; system coverage reported; hybrid added as ADR option H and first fallback |
| R5 | "84 of 84" headline hides 12 off-cell glyphs | Confirmed: 12 advances 0.232 to 1.262 em re-measured on the rebuilt files | Headline now "84 covered, 72 on cell"; on-cell symbol face considered, sized and deferred with a trigger |
| R6 | `swap` chosen without comparing alternatives; HDD untested | Confirmed | `swap`, `optional` and `size-adjust` compared (MDN S3, S10); load probe on the HDD is now a pass criterion |
| R7 | 11-term string and 0.529 em term list not stored | Confirmed the string and list are now in `fonts.lock.json`; recomputed 0.5291 em from the shipped subset over 158 characters | Doc points to the stored list; the earlier "spaces excluded" wording was wrong (internal spaces are included) and is corrected |
| R8 | Decision summaries T-3, T-4, T-5 stale | Not a file in this lane. Checked: tokens file has 26 tokens (2 fontFamily, 2 fontWeight, 6 dimension, 7 number, 9 typography); letterSpacing and Geist statements in the files are correct | No file change; the integrator should regenerate summaries from the files |
| R9 | `residual_glyphs_off_cell` was `[12, 12]` | Confirmed fixed: it is the integer 12 | none needed |

## Appendix A. Rebuild the shipped fonts from the lock file

Requires `pip install fonttools brotli`. Verified 2026-09-29: prints three lines ending `sha256 match`.

```python
"""python rebuild_from_lock.py design/fonts.lock.json OUTDIR"""
import hashlib, io, json, os, sys, urllib.request
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

def parse_ranges(text):
    cps = set()
    for part in text.split(","):
        part = part.strip()[2:]
        if "-" in part:
            a, b = part.split("-"); cps.update(range(int(a, 16), int(b, 16) + 1))
        else:
            cps.add(int(part, 16))
    return sorted(cps)

def build(ttf_bytes, cps, features, wght):
    font = TTFont(io.BytesIO(ttf_bytes), recalcTimestamp=False)
    if "fvar" in font:
        limits = {}
        for axis in font["fvar"].axes:
            if axis.axisTag == "wght":
                if wght:
                    limits["wght"] = tuple(wght)
            else:
                limits[axis.axisTag] = axis.defaultValue
        font = instancer.instantiateVariableFont(font, limits, inplace=False)
        buf = io.BytesIO(); font.save(buf); buf.seek(0)
        font = TTFont(buf, recalcTimestamp=False)
    opts = subset.Options()
    opts.layout_features = features
    opts.flavor = "woff2"
    opts.hinting = False
    opts.notdef_outline = True
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17]
    opts.drop_tables += ["DSIG"]
    opts.glyph_names = False
    opts.legacy_kern = False
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=cps)
    sub.subset(font)
    out = io.BytesIO(); font.flavor = "woff2"; font.save(out)
    return out.getvalue()

lock = json.load(open(sys.argv[1], encoding="utf-8"))
outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
ok = True
for face in lock["faces"]:
    up, sh = face["upstream"], face["shipped"]
    src = urllib.request.urlopen(up["source_url"]).read()
    assert hashlib.sha256(src).hexdigest() == up["source_sha256"], "source changed: " + face["id"]
    wght = (400, 600) if face["id"] in ("sans", "mono") else None
    data = build(src, parse_ranges(sh["unicode_range"]), lock["reproduce"]["features_kept"][face["id"]], wght)
    open(os.path.join(outdir, sh["file"]), "wb").write(data)
    same = hashlib.sha256(data).hexdigest() == sh["sha256"]
    ok &= same
    print(face["id"], sh["file"], len(data), "sha256 match" if same else "sha256 DIFFERENT")
sys.exit(0 if ok else 1)
```

## Appendix B. Font CSS used in the smoke test

Generated from the tokens by the tokens aspect in the real build; this hand-written form ran in Chromium 151 with the earlier decimal line heights 1.3333 and 1.4286; the `calc` forms below are the audit revision and were not re-run under the Studio CSP plus `font-src 'self'`. The `unicode-range` values are in `fonts.lock.json`.

```css
@font-face{font-family:"EIJA Sans";src:url("fonts/EIJA-NotoSans-latin-400-600.woff2") format("woff2");
  font-weight:400 600;font-style:normal;font-display:swap;unicode-range:/* faces[0].shipped.unicode_range */}
@font-face{font-family:"EIJA Mono";src:url("fonts/EIJA-FiraCode-latin-notation-400-600.woff2") format("woff2");
  font-weight:400 600;font-style:normal;font-display:swap;unicode-range:/* faces[1].shipped.unicode_range */}
@font-face{font-family:"EIJA Symbols";src:url("fonts/EIJA-NotoSansMath-symbols-400.woff2") format("woff2");
  font-weight:400;font-style:normal;font-display:swap;unicode-range:/* faces[2].shipped.unicode_range */}
body{font-synthesis:none}
.sans{font-family:"EIJA Sans","EIJA Symbols",system-ui,"Segoe UI",sans-serif}
.mono{font-family:"EIJA Mono","EIJA Symbols",ui-monospace,Consolas,monospace;
  font-feature-settings:"zero" 1,"calt" 0,"liga" 0;font-variant-ligatures:none}
.t12{font-size:.75rem;line-height:calc(4 / 3)}.t14{font-size:.875rem;line-height:calc(10 / 7)}
.t16{font-size:1rem;line-height:1.5}.t20{font-size:1.25rem;line-height:1.4}.t24{font-size:1.5rem;line-height:calc(4 / 3)}
```

MEASURED results of that run are in `fonts.lock.json` under `verification`: without `font-src` all three faces ended in `error` and the console named a `default-src` violation; with it all three were `loaded`, the sans terms drew from Noto Sans, `→ ⊨ ≤ ∅ ∀` in a sans line drew from Noto Sans (24 glyphs) and Noto Sans Math (5 glyphs), and in a mono line `∀ ∈ · ⊨ ∧ ¬` drew from Fira Code with only `⇒` from Noto Sans Math.
