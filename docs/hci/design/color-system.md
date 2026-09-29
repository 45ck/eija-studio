# Colour system: OKLCH role tokens, redundant status coding, diff and categorical colour

Lane `lane/ux-research`, aspect `color-system`. Date 2026-09-29. Status: proposed. Decision record: [HCI-ADR-0059](../../adr/0059-hci-color-system.md). Machine-readable: [color.tokens.json](../../../design/tokens/color.tokens.json) (W3C Design Tokens Community Group format 2025.10).

Labels. **MEASURED**: computed by a script I ran on repository files or on the tokens in this change, 2026-09-29. **PREDICTION**: model output; not a measurement of people. **UNVERIFIED**: not confirmed this session; nothing is built on it. No user study has been run; no claim of user benefit is made. Source ids `S1` to `S28` are in section 14; every URL there was opened on 2026-09-29. Research dossiers in `docs/hci/research/` are cited as `VIS`, `REV`, `SYN` and are not re-opened unless a row says so.

## 0. Decisions first

| # | Decision | Confidence | Evidence |
|---|---|---|---|
| C1 | **Tokens are OKLCH components plus a 6-digit sRGB hex fallback in DTCG 2025.10**, light and dark as sibling groups with identical paths (71 tokens each, 51 literal and 20 aliases). Gates run on the hex. The generated CSS emits the hex, so what is rendered is what was checked. No P3 or wide-gamut tokens. | High for the format; medium for the delivery | S4, S5, S6, section 10 |
| C2 | **One accent hue (OKLCH 250, blue) plus four chromatic status hues (pass 165, fail 30, stale 85, conflict 350) anchored to the Okabe-Ito hues within 20 degrees.** UNKNOWN, NOT_RUN and BLOCKED are neutral (chroma exactly 0). AI-proposed and RUNNING reuse the accent hue and differ by shape and word. | Medium: anchors are documented; hue choice among blues is not decisive (section 7.4) | S9, S11, S12 |
| C3 | **Colour grammar.** Status hue lives on the glyph only; every status word is set in `text.primary`; a status wash may fill at most one region per viewport; the UNKNOWN count is shown even when it is zero. Diff colour lives on a 3 px rail, a sign and a row wash; category colour lives on a mark with a label. Each family has its own form, so hue overlap between families never decides meaning (section 3). | High for WCAG 1.4.1; medium for the grammar | S1, S16, sibling doc `evidence-and-change-review.md` 2.9 |
| C4 | **Lightness is assigned by a constrained search, not by a conspicuity ladder.** Under WCAG 4.5:1 and an APCA advisory floor, the search maximised the worst-case colour-vision-deficiency (CVD) separation. PREDICTION: worst pair of the 8 statuses is 0.061 dE_OK in light and 0.046 in dark (3.1 and 2.3 times the 0.02 just-noticeable difference), against about 0.02 to 0.03 for the ladder built first (hex in 7.3; the chosen palette was optimised for this metric and the ladder was not). Hue is still never the only carrier. | Medium: the model is a simulation; small marks are not covered by the 0.02 figure | S6, S9, S10; section 7 |
| C5 | **Diff colours are three dedicated hues (added 207, removed 300, changed 125), at least 39 degrees from every status and accent hue, never green and red.** Added, removed and changed also carry a sign (+, -, ~), a word and a strike-through on removed text. | Low to medium: dedicated hues have no precedent found; Primer's CVD themes use blue and orange (S13) | S13, section 8 |
| C6 | **Categorical palette: 8 marks, hues 45 degrees apart, lightness retuned per theme, opt-in ("colour by") and always paired with a label.** PREDICTION: minimum CAM02-UCS distance 13.06 (light) and 13.66 (dark) over normal vision and all severities of the three deficiencies, both simulation conventions; every mark at least 3.3:1 against every surface. Below the 18 that Petroff reports for 8 colours without a contrast rule (S10). | Medium | S10, S12; section 9 |
| C7 | **Gates and advisories are testable requirements COL-01 to COL-14** (section 6): WCAG 2.2 contrast computed on the hex, APCA Lc advisory, CVD separation, glyph-silhouette distance, hue gaps, parity of light and dark, token-file validity. A value that cannot be computed is UNKNOWN and fails the build. | High for the WCAG gates; the CVD and glyph thresholds are our hypotheses | S1, S2, S3, S14 |
| C8 | **Dark theme: elevation by surface step plus a border, no shadow; status glyph colours lifted to an APCA floor of Lc 45 (NOT_RUN 30) and `text.secondary` to Lc 60.** This departs from "lowest lightness that reaches 4.5:1" (SYN C10) and needs the dark-contrast study in section 12. | Low: APCA is unratified | S14, S15 |
| C9 | **Delivery:** `tokens.css` is generated from the token file with two blocks (`prefers-color-scheme` and a `data-theme` override), not `light-dark()`; a forced-colours mapping to system colours is proposed (section 10). | Medium | S7, S6 (system colours) |

Not settled here: glyph geometry (status-display aspect; section 1), type sizes, layout, and the token build script.

## 1. Interfaces and assumptions

| Aspect | This document assumes or provides | Status |
|---|---|---|
| Status display (`evidence-and-change-review.md` 2.9) | Assumes its glyph table: FAIL filled square with cross, CONFLICT square split on the diagonal, STALE dashed square, UNKNOWN hollow diamond with `?`, NOT_RUN dotted circle, RUNNING open ring, PASS small filled square. It gives no glyph for BLOCKED; I test a provisional filled diamond with a bar. AI-proposed is a dashed outline treatment, not a glyph. Provides one `fg` hue per status and a word rule. | Assumption; glyph geometry untested at 12 to 16 px (its open item O3) |
| Accessibility (`accessibility.md` D8, D6, 9.1) | Provides `focus.ring` at 4.56 or more on every surface and 4.44 or more on the selection wash; four surface steps; status words in the ink colour; every text and fill pair computed on every surface it can sit on. Proposes the forced-colours mapping in section 10. | Provided; forced-colours mapping is a proposal |
| Typography (`typography.md` 9) | Asks colour to report APCA Lc for caption and code-small as advisory. Provided (minimum over four surfaces, W3 reference implementation, see section 6): `text.secondary` 74.6 (light) and 60.7 (dark); `text.primary` 92.4 and 93.3. Status words in dense rows use `text.primary`. | Provided; APCA thresholds by size and weight not read (UNVERIFIED) |
| Canvas (`canvas-uml-interaction.md` 5.4) | Provides the `canvas.*` roles as aliases (11 per theme). LAYOUT is neutral, MEANING is accent, a refused drop uses the BLOCKED ink, not the FAIL hue. | Provided |
| Motion (`motion-and-performance.md`) | Pending and RUNNING use `status.running` (accent) with the word; colour never carries motion. | Provided |
| Layout | Two elevations: `raised` (grouping) and `overlay` (palette, menus). `sunken` is a recess, not an elevation. Zero shadows. In light, `overlay` and `raised` have the same fill (`#FFFFFF`), so the second elevation exists only through a 1 px `border.control` edge (3.13:1 or more on every light surface); in dark it is a lighter step plus the same edge. No token defines the edge separately. | Assumption; overlay edge in light is a proposal (O5) |
| Tokens and CSP | Tokens are data; CSS is an external file under `style-src 'self'`; no `style` attribute; `setAttribute("data-theme")` is not a style write. The `/assets` allowlist must serve `tokens.css` (server change owned by the security-boundary aspect). | Assumption |
| Language tree and evidence rail | The display order of statuses (their proposals differ) is not decided here. This document only guarantees that every pair is separable by glyph and word. | Not settled here |

## 2. Baseline (MEASURED)

Method: I parsed `src/eija_studio/resources/web/app.css` and enumerated 22 foreground and background pairs the stylesheet defines (text, control borders, focus ring, selected states) and computed WCAG 2.2 ratios from the hex values. Dynamic text set by `app.js` is not included.

| Fact | Value |
|---|---|
| Distinct hex colours | 19 (SYN C3) |
| Themes | Light only; no `prefers-color-scheme`, `forced-colors` or `prefers-reduced-motion` rule (SYN C3) |
| Text pairs (16 of 22) | All pass 4.5:1; lowest is muted text on the pale runtime-state wash, 5.10 |
| Non-text pairs (6 of 22, strict reading of SC 1.4.11) | 3 fail 3:1: secondary-button border 1.68, input border 1.74, state-node border 1.56. Whether an input border counts depends on whether another cue identifies the control; I count it |
| Disabled button | White on the green at `opacity: .5` is 2.27:1; inactive components are exempt from SC 1.4.3 |
| Focus ring | `#bf7400`, 3.41 to 3.68 against paper and white |
| UNKNOWN box | Tint `#fff3d9` on paper differs by 0.032 dE_OK (normal vision), 1.6 times the 0.02 just-noticeable difference; the box relies on its text |
| Only status pair | Green `#236755` vs danger `#9f382b`: 0.204 dE_OK normally; worst case over protan, deutan and tritan at severity 50 and 100, both simulation conventions, 0.068 |
| Status carriers | Colour of a number, one tinted box; no shape system |

The baseline text contrast is sound. Its gaps are: no dark theme, control borders below 3:1, one weak tint carrying UNKNOWN, and no status vocabulary beyond three tones.

## 3. Colour grammar

Colour is assigned by form, so that two families that share a hue are still told apart by where and how they appear (WCAG 1.4.1: colour is not the only means, S1).

| Family | Form | Allowed places | Never |
|---|---|---|---|
| Neutral | Surfaces, text, borders | Everything else | Carrying a status |
| Accent (hue 250) | Link text, selection edge (2 px) and wash, focus ring, the one primary button per view, AI-proposed and RUNNING marks, canvas MEANING outline and legal-target outline | Interaction and provenance | Evidence status, diff, decoration, chart series |
| Status | Glyph (16 px grid, 12 px in dense rows) in the `fg` hue; the word beside it in `text.primary`; at most one `tint` wash per viewport | Rows, roll-up chips, decision bar | A rail, a fill behind a whole row, coloured words |
| Diff | 3 px leading rail, sign, row wash (`tint`), word-level highlight (`strong`), strike-through on removed text | Review chapters, source view, diagram overlay | A glyph slot, a roll-up, a tree row status |
| Category | 10 px square mark or 4 px bar plus the category name | Only when the owner enables "colour by"; at most 8 in use | A glyph shape, a status or diff surface |
| Forced colours | All families collapse to system colours; shape, word and sign remain | Section 10 | Relying on hue |

Budgets (PREDICTION, by construction; the slop-budget script owns the measurement): the default viewport uses neutrals, the accent and at most four chromatic status hues; a review viewport adds the three diff hues; category hues appear only when enabled. Distinct text colours per viewport: `text.primary`, `text.secondary`, `accent.fg` for links, `text.disabled`, so at most four (target 5 in SLP M4).

Rules for status marks: PASS is the quietest mark by size (evidence aspect), not by colour; FAIL, CONFLICT, UNKNOWN and BLOCKED are the loud ones; the roll-up always lists all six evidence counts, including zeros, so UNKNOWN 0 is visible as a real count (P1). A neutral grey never stands for "fine": UNKNOWN is a dark neutral in light (9.24:1) and a mid-light neutral in dark (5.93:1), with a hollow diamond and its word.

## 4. OKLCH rules (lightness and chroma)

| # | Rule | Applied values | Basis |
|---|---|---|---|
| R1 | Neutrals have OKLCH chroma at most 0.010 (measured maximum 0.0058) around a warm hue target of 80; hex rounding moves the realised hue at this chroma. Status neutrals have chroma exactly 0. | Light surfaces L 0.974, 1.000, 0.950; dark 0.192, 0.227, 0.265, 0.155 | Near-neutral ground so status hues are not shifted; Linear describes a more neutral direction (S17, intent only) |
| R2 | `text.primary` at least 13:1 and Lc 90; `text.secondary` at least 6:1 and Lc 60; on all four surfaces. `text.disabled` is exempt and never carries information. | Light 13.36 and 6.12; dark 13.10 and 7.65 | S2; S14 advisory |
| R3 | `border.control` at least 3.1:1 on all surfaces; `border.subtle` is decorative (1.13 to 1.44). | 3.13 to 3.63 light; 3.14 to 4.01 dark | S3 |
| R4 | One accent hue, 250. `accent.fg` is also the button fill and the focus ring, so one value serves all three. At least 4.5:1 on every surface. | Light L 0.530 C 0.150; dark L 0.759 C 0.128 | S6; sweep in 7.4 |
| R5 | Chromatic status hues stay within 20 degrees of an Okabe-Ito anchor (bluish green 165.5, vermilion 47.5, orange 76.8, reddish purple 346.3, blue 244.0; MEASURED from the hex in S12). Fail is 17.5 degrees redder than vermilion: at 7.9:1 hue 30 stays red where hue 40 turns brown (`#901308` against `#852B00`). | 165, 30, 85, 350, 250 | S11, S12 |
| R6 | Chromatic `fg` chroma is at least 0.10 and at most 0.16. Lightness is chosen by search: contrast at least 4.5:1 on all four surfaces and below a per-role ceiling so that no glyph is near-black (light: pass 6, fail 8, stale 6, conflict 7, accent 6.5; dark 9), Lc at least 45 in dark (the search used 45.5 from a scratch APCA port; the realised minimum with the W3 reference implementation is 45.8), objective = maximise the worst pair of dE_OK over normal, protan, deutan and tritan at severity 50 and 100, both simulation conventions. Sequential search (chromatic five, then the three neutrals, then diff), so not a joint optimum. | Section 5 tables | S9, S10 |
| R7 | NOT_RUN is the lowest-emphasis mark: at least 3.15:1 rather than 4.5:1, still above the 3:1 gate. | 3.32 light, 4.44 dark | S3 |
| R8 | Washes (`tint`): L 0.94, C 0.035 to 0.040 in light (neutral washes L 0.925, C 0); L 0.27, C 0.05 in dark (neutral washes L 0.27, C 0); `text.primary` at least 9:1 and `text.secondary` at least 4.5:1 on every wash. Each `fg` is at least 3:1 on its own wash. | Min primary on wash 10.59 light, 9.06 dark | S2, S3 |
| R9 | Diff: hues 207, 300, 125; `fg` at least 4.5:1 (search over 4.53 to 9.5); `strong` L 0.88 light, 0.36 dark. | Section 5 | Section 8 |
| R10 | Categories: hues 25 + 45k degrees; chroma at least 0.075; retuned lightness per theme; at least 3.15:1 on every surface. | Section 9 | S10 |
| R11 | Dark elevation by a lighter step (delta L at least 0.03) plus a 1 px border, never by shadow. | 0.035 and 0.038 | Shadow contrast on dark 1.025 to 1.08 (VIS 2.5, MEASURED there) |
| R12 | sRGB only; hex is authoritative for gates; hover and pressed reuse `accent.tint`, `surface.sunken` and `border.control`, so no state-derived colour tokens exist. | 0 derived tokens | Delivery risk of relative colour syntax (CSS Color 5 is a Working Draft, VIS 2.1) |

## 5. Token inventory

Values are OKLCH (L, C, hue degrees) with the hex fallback. The file is authoritative; these tables are generated from it.

### 5.1 Surfaces, text, borders, accent

| Token | Light hex | Light L C H | Dark hex | Dark L C H |
|---|---|---|---|---|
| `surface.canvas` | #F8F6F4 | 0.974 0.003 68 | #151412 | 0.192 0.004 85 |
| `surface.raised` | #FFFFFF | 1.000 0.000 - | #1D1C1A | 0.227 0.004 85 |
| `surface.overlay` | #FFFFFF | 1.000 0.000 - | #262523 | 0.265 0.004 85 |
| `surface.sunken` | #F0EEEB | 0.950 0.005 78 | #0D0C0A | 0.155 0.004 85 |
| `text.primary` | #262422 | 0.262 0.005 68 | #EFEDE9 | 0.947 0.006 85 |
| `text.secondary` | #5A5855 | 0.461 0.005 78 | #B9B7B4 | 0.780 0.005 78 |
| `text.disabled` | #A6A4A1 | 0.719 0.005 78 | #575552 | 0.450 0.005 78 |
| `border.subtle` | #E0DEDA | 0.901 0.006 85 | #2F2E2B | 0.301 0.005 92 |
| `border.control` | #888683 | 0.621 0.005 78 | #72716E | 0.549 0.005 91 |
| `accent.fg` | #006EBE | 0.530 0.150 250 | #6EB6FF | 0.759 0.128 250 |
| `accent.tint` | #DDEDFF | 0.940 0.030 251 | #142A41 | 0.279 0.051 251 |
| `accent.on-solid` | #FFFFFF | 1.000 0.000 - | #151412 | 0.192 0.004 85 |

`focus.ring` and `accent.solid` are aliases of `accent.fg`; `selection.wash` is an alias of `accent.tint`.

### 5.2 Status

| Token | Light hex | Light L C H | Dark hex | Dark L C H |
|---|---|---|---|---|
| `status.pass.fg` | #006F4F | 0.480 0.101 165 | #00B07F | 0.671 0.141 165 |
| `status.fail.fg` | #901308 | 0.419 0.160 30 | #F57663 | 0.711 0.160 30 |
| `status.unknown.fg` | #3E3E3E | 0.364 0.000 - | #A1A1A1 | 0.709 0.000 - |
| `status.stale.fg` | #7E5E00 | 0.501 0.103 85 | #F3BA25 | 0.819 0.160 85 |
| `status.conflict.fg` | #AF3E7C | 0.541 0.161 350 | #FF8BC5 | 0.779 0.154 350 |
| `status.not-run.fg` | #828282 | 0.607 0.000 - | #8A8A8A | 0.633 0.000 - |
| `status.blocked.fg` | #2E2E2E | 0.301 0.000 - | #C7C7C7 | 0.830 0.000 - |

Washes:

| Token | Light hex | Dark hex |
|---|---|---|
| `status.pass.tint` | #D4F4E5 | #072E20 |
| `status.fail.tint` | #FFE4DF | #3B1C17 |
| `status.unknown.tint` | #E6E6E6 | #262626 |
| `status.stale.tint` | #F8EACE | #322405 |
| `status.conflict.tint` | #FFE2EE | #381C2A |
| `status.not-run.tint` | #F0EEEB | #262626 |
| `status.blocked.tint` | #E6E6E6 | #262626 |

`status.proposed` and `status.running` are aliases of the accent (`fg` and `tint`). The `not-run.tint` in light is the `sunken` surface, because a separate wash would have put the glyph below 3:1.

### 5.3 Diff

| Token | Light hex | Light L C H | Dark hex | Dark L C H |
|---|---|---|---|---|
| `diff.added.fg` | #00717C | 0.501 0.086 207 | #6CD7E5 | 0.821 0.100 207 |
| `diff.added.tint` | #CDF3F9 | 0.939 0.040 208 | #002D32 | 0.271 0.046 206 |
| `diff.added.strong` | #A0E5EF | 0.880 0.070 207 | #00464D | 0.360 0.062 206 |
| `diff.removed.fg` | #4E2C7C | 0.380 0.130 300 | #B7A0E4 | 0.750 0.099 300 |
| `diff.removed.tint` | #EEE7FF | 0.941 0.033 299 | #2A203B | 0.269 0.050 300 |
| `diff.removed.strong` | #DECEFF | 0.880 0.069 300 | #443261 | 0.360 0.081 300 |
| `diff.changed.fg` | #3B5000 | 0.399 0.100 125 | #A2BC75 | 0.759 0.099 125 |
| `diff.changed.tint` | #E5F0D4 | 0.939 0.039 125 | #212B0D | 0.271 0.051 125 |
| `diff.changed.strong` | #CDE0AE | 0.880 0.070 125 | #34440D | 0.360 0.080 125 |

### 5.4 Categories (use in this order)

| Token (use in this order) | OKLCH hue | Light hex | Light L C | Dark hex | Dark L C |
|---|---|---|---|---|---|
| `category.1.mark` | 206 | #2B8F9A | 0.60 0.090 | #89DAE3 | 0.84 0.080 |
| `category.2.mark` | 70 | #7E541B | 0.48 0.090 | #D8953D | 0.72 0.130 |
| `category.3.mark` | 295 | #462281 | 0.36 0.149 | #B7A0FB | 0.76 0.130 |
| `category.4.mark` | 25 | #B06A65 | 0.60 0.091 | #BD615B | 0.60 0.119 |
| `category.5.mark` | 115 | #7E8814 | 0.60 0.130 | #C8D386 | 0.84 0.100 |
| `category.6.mark` | 160 | #004A2E | 0.36 0.082 | #77B493 | 0.72 0.080 |
| `category.7.mark` | 250 | #246099 | 0.48 0.111 | #3A84CA | 0.60 0.130 |
| `category.8.mark` | 340 | #612D51 | 0.38 0.090 | #A16D8F | 0.60 0.081 |

`category.N.tint`: L 0.94, C 0.035 (light) and L 0.27, C 0.05 (dark) at the mark's hue. `category.unassigned` aliases `text.secondary` and `surface.sunken`: unassigned items are neutral, never a hue.

## 6. Testable requirements

Every rule reads `design/tokens/color.tokens.json`, resolves aliases, evaluates on the `hex`, and reports UNKNOWN (and fails) if a token is missing, an alias dangles or a value cannot be computed. The same list is in the file under `$extensions.io.github.45ck.eija-studio.requirements`, with a `measured` snapshot.

Pair set behind "pairs checked" (COL-01 to COL-05, per theme): COL-01 8 (2 text tokens x 4 surfaces); COL-02 44 (2 x 22 literal washes); COL-03 80 (20 literal subjects x 4 surfaces: 7 status, 3 diff, accent, `border.control`, 8 categories); COL-04 13 (7 status glyphs on their tint, 3 diff glyphs on tint and on strong); COL-05 2. Total 147, or 167 if the aliases (`focus.ring`, `status.proposed`, `status.running`) are counted as their own pairs. An earlier draft said 160 without defining the set.

COL-06 method. Values are the minimum over the four surfaces of the absolute Lc, text on background, computed with the W3 reference implementation `apca-w3` 0.1.9 (Somers, revision 2022-07-03) run on the token hexes. It reproduces the published oracles: black on white 106.04, white on black -107.88, `#262422` on `#F8F6F4` 97.21. An earlier draft of this table used a scratch port that did not reproduce the reference (it gave 90.2, 71.5, 63.4, 53.3 and 91.6, 60.5, 45.5, 37.4); the audit caught it. Status glyph set: pass, fail, unknown, stale, conflict, blocked, proposed and running (NOT_RUN listed separately). The conclusions are unchanged: light `text.secondary` at 74.6 is still just below the 75 body minimum; dark status glyphs are at or above 45 (lowest 45.8, pass); dark NOT_RUN at 36.7 is above its 30 floor.

| Id | Requirement | Threshold | Type | Light | Dark |
|---|---|---|---|---|---|
| COL-01 | `text.primary`, `text.secondary` on every surface | at least 4.5:1 (SC 1.4.3) | gate | min 6.12 | min 7.65 |
| COL-02 | Both text tokens on every wash (`tint`, `strong`, 22 of them) | at least 4.5:1 | gate | 4.85 (secondary on `diff.removed.strong`); primary 10.59 | 5.29; 9.06 |
| COL-03 | Status, diff, accent, focus, `border.control`, category marks on every surface | at least 3:1 (SC 1.4.11) | gate | min 3.13 (`border.control` on `sunken`) | min 3.14 |
| COL-04 | Status and diff `fg` on its own wash | at least 3:1 | gate | min 3.32 | min 4.38 |
| COL-05 | `accent.on-solid` on `accent.solid`; `focus.ring` on `accent.tint` | 4.5:1; 3:1 | gate | 5.28; 4.44 | 8.59; 6.82 |
| COL-06 | APCA Lc, absolute value | primary 90, secondary 60, status glyph 45 (not-run 30) | advisory | 92.4; 74.6; 65.6; 56.0 | 93.3; 60.7; 45.8; 36.7 |
| COL-07 | Worst-case dE_OK between any two of 8 colours (pass, fail, unknown, stale, conflict, not-run, blocked, proposed; RUNNING shares the accent hex with proposed), conditions in 7.1 | at least 0.04 (2 x JND) | hypothesis | 0.061 (pass, proposed; tritan 100) | 0.046 (pass, not-run; deutan 100); 0.0448 at severities 10 to 100 step 10 (deutan 90) |
| COL-08 | Glyph silhouette distance (1 minus weighted IoU of greyscale renders) between any two of 8 glyphs (pass, fail, conflict, stale, unknown, not-run, running, provisional blocked; AI-proposed is a dashed outline, not a glyph), at 12 px | at least 0.25 | hypothesis | 0.313 (unknown, blocked) at 12 px; 0.334 at 16 px | same (colour-free) |
| COL-09 | Diff hue gap to every status and accent hue; worst-case dE_OK diff to status, accent and each other | at least 35 degrees; at least 0.02 | hypothesis | 39.7 degrees; 0.028 | 39.7 degrees; 0.040 |
| COL-10 | 8 category marks: CAM02-UCS distance over conditions; contrast; chroma | at least 12; 3:1; 0.075 | hypothesis | 13.06; 3.30; 0.082 | 13.66; 3.66; 0.080 |
| COL-11 | Dark elevation steps (`overlay` minus `raised`, `raised` minus `canvas`) | delta L at least 0.03 | hypothesis | not applicable (overlay equals raised) | 0.038; 0.035 |
| COL-12 | Chroma of surfaces, text, borders; status neutrals | at most 0.010; exactly 0 | hypothesis | 0.0058; 0 | 0.0058; 0 |
| COL-13 | Token validity: `colorSpace` oklch, `components` [L, C, H or none], `alpha` 1, 6-digit hex equal to the sRGB conversion of the components within 1/255, `$description` present | structural | gate | 142 leaves, 0 errors; max delta 0 of 255 | same |
| COL-14 | Light and dark parity: identical token paths | structural | gate | 71 and 71, identical | |

Regression floors. Every threshold typed "hypothesis" (COL-07 to COL-12) was chosen at or just below the value the first accepted palette reached, so it detects regressions in the token lint; it does not validate the design. COL-07 was first written as 0.05 (2.5 x JND). The first palette passed 0.05 under one simulation convention and fell to 0.010 in dark (pass against not-run) under the other; I fixed the palette and, because the corrected dark result is 0.046, restated the threshold as 2 x JND = 0.04 before recording it. That is a hypothesis moved after seeing data; the study in section 12 is the test, not this number.

## 7. Colour-vision-deficiency criteria and results

### 7.1 Criteria

- **Simulation.** Machado, Oliveira and Fernandes 2009 matrices (S9) for protanopia, deuteranopia and tritanopia at severity 100 (dichromacy) and 50 (anomalous trichromacy). I checked the six severity-50 and severity-100 matrices against the `colorspacious` 1.1.2 package to six decimals (scratch use only; not a dependency).
- **Convention.** The authors' page does not say whether the matrices act on linear or gamma-encoded sRGB; Petroff notes that the paper's figures used gamma-encoded values while later work applies them to linear values (S10, footnote 4). Every criterion takes the worse of both.
- **Metric.** dE_OK, Euclidean distance in Oklab (S6, S8); one just-noticeable difference is 0.02 (CSS Color 4 gamut mapping constant). For categorical sets, CAM02-UCS distance with sRGB viewing conditions, as Petroff (S10); my implementation agrees with `colorspacious` within 0.02 units on six test colours.
- **Redundancy is the requirement, hue separation is the floor.** Every status has a word and a glyph (COL-08, C3). Hue separation is required only to stay above 2 x JND (COL-07) so that hue adds a channel; it is not asked to carry the meaning.

### 7.2 Worst status pairs (PREDICTION)

| Theme | Rank | Pair | Worst-case dE_OK | Condition |
|---|---|---|---|---|
| light | 1 | pass vs proposed | 0.061 | tritan 100 |
| light | 2 | pass vs unknown | 0.062 | deutan 100 |
| light | 3 | conflict vs not-run | 0.063 | deutan 100 |
| light | 4 | unknown vs blocked | 0.063 | deutan 100 |
| light | 5 | fail vs blocked | 0.068 | protan 100 |
| dark | 1 | pass vs not-run | 0.046 | deutan 100 |
| dark | 2 | pass vs unknown | 0.048 | deutan 100 |
| dark | 3 | conflict vs blocked | 0.048 | deutan 100 |
| dark | 4 | unknown vs conflict | 0.053 | deutan 100 |
| dark | 5 | fail vs not-run | 0.054 | protan 100 |

Sets. The COL-07 set is the 8 colours above; the COL-08 glyph set has RUNNING and no AI-proposed, so the two floors are not measured on the same 8. RUNNING and AI-proposed share the accent hex, so RUNNING has the same colour distances as AI-proposed and 0 to it: those two are told apart by form (open ring against dashed outline) and word only. UNKNOWN, NOT_RUN and BLOCKED are neutral (chroma 0): they are told apart from each other by glyph, word and lightness, not hue. Re-run COL-07 and COL-08 on one agreed set once the status-display aspect fixes its glyphs.

The same 8 colours in CAM02-UCS (the metric used for categories, section 9), over normal vision and severities 10 to 100 step 10, both conventions (PREDICTION, my computation): minimum 6.95 in light (unknown against blocked, protan 40) and 6.60 in dark (pass against not-run, deutan 100); for the five chromatic colours 9.23 (light) and 8.19 (dark). These are well below the 13.06 reached by the categories and Petroff's 18 (S10). Status is redundantly coded, so a lower floor is defensible, but the two floors are on different scales and must not be compared as if they were the same. In the light theme UNKNOWN (`#3E3E3E`) and BLOCKED (`#2E2E2E`) are near-ink, BLOCKED is 0.04 dE_OK from `text.primary`, and the pair is separated by silhouette alone (0.313, on shapes drawn from a text description, floor chosen after the first render). This is the weakest spot for the invariant that UNKNOWN is loud; it is parked with study CS1.

Chromatic-only worst pair (pass, fail, stale, conflict, proposed): 0.061 in light (pass against proposed, tritan) and 0.061 in dark (stale against conflict, tritan). The three neutrals are the tight part: in dark, pass and conflict sit next to not-run, unknown and blocked under deutan because their lightness is similar.

### 7.3 Contrast ladder against the chosen search

I built the ladder first: contrast tiers by conspicuity (fail 7.0, conflict 6.0, unknown 8.0, blocked 11.0, accent 5.6, pass 4.55, stale 4.6, not-run 4.6 on all surfaces; hues 165, 40, 85, 350, 250; chroma caps 0.13 to 0.16). It reads well as an attention scheme and separates poorly. Its hexes, so the figure can be checked (also in the token file under `$extensions...option_c_ladder_hex`): light pass `#007A57`, fail `#8E2E00`, stale `#886500`, conflict `#99316A`, proposed `#005EA4`, unknown `#464646`, not-run `#6A6A6A`, blocked `#323232`; dark pass `#0CA175`, fail `#FF946E`, stale `#B3870D`, conflict `#EE7FB7`, proposed `#52A2F0`, unknown `#BCBCBC`, not-run `#8E8E8E`, blocked `#DBDBDB`.

Bias. The chosen palette was optimised for exactly the metric it is scored on; the ladder was not, so the comparison favours the chosen palette by construction. An independent rebuild from the tiers above (the audit) gave worst pairs of about 0.022 to 0.024 in light and 0.025 to 0.028 in dark. Read the ladder figure as about 0.02 to 0.03, roughly 1.1 to 1.5 times the just-noticeable difference.

| Palette | Theme | Worst pair over 28, sev 50 and 100, linear and gamma | dE_OK | Multiple of JND 0.02 |
|---|---|---|---|---|
| D chosen | light | pass vs proposed | 0.061 | 3.1 |
| D chosen | dark | pass vs not-run | 0.046 | 2.3 |
| C contrast ladder | light | pass vs not-run | 0.024 (0.030 under the gamma convention) | 1.2 to 1.5 |
| C contrast ladder | dark | fail vs conflict | 0.021 (0.022 under the gamma convention) | 1.1 |

The chosen palette is better in both themes under every combination I tried (severity 100 only or 50 and 100; linear, gamma or both). Decision flips inside the band: no. Note the earlier failure mode: an intermediate dark palette scored 0.010 for pass against not-run under the gamma convention; the shipped one does not.

### 7.4 What hue can and cannot do

- Raw Okabe-Ito hexes used as the five chromatic roles reach 0.076 worst pair, better than our 0.061, but 3 of the 5 fail 3:1 on at least one light surface (minimum over the four surfaces: stale 1.94, conflict 2.64, pass 2.95; on the canvas `#F8F6F4` alone only stale 2.09 and conflict 2.84 fail, pass is 3.17 and fails on `sunken`) and the accent blue is 2.95 on the dark `overlay` (S12 hex, computed by me). Retuning lightness to pass contrast costs 0.015 of worst-pair separation (20%) in this measure. PREDICTION.
- Accent hue sweep, the seven other statuses fixed, lightness and chroma fixed at the accent's, worst dE_OK to any status over both conventions. Light: 200 gives 0.030, 210 0.043, 220 0.059, 230 0.062, 240 0.062, **250 0.061**, 260 0.049, 270 0.054, 280 0.060, 290 0.084, 300 0.080. Dark: 200 0.036, 210 0.054, 220 0.073, 230 0.084, 240 0.082, **250 0.080**, 260 0.080, 270 0.078, 280 0.059, 290 0.046, 300 0.047. Hue 250 is within 0.023 of the best value in light (290) and 0.004 in dark (230); only cyan and teal (200 to 210) are clearly worse, and violet is not consistently better. So 250 is chosen by the Okabe-Ito blue anchor (244, S12), by not choosing violet, and by staying clear of the cyan diff hue, not by a CVD win. That is a rubric choice, not evidence.
- Hue-only separation at 4.5:1 and free lightness could reach 0.081 in light and 0.100 in dark in an earlier search (linear convention only, five chromatic roles), using very dark or very light members that stop looking like red or amber (for example `#6B2100` for fail). I chose recognisable hues over the last 0.02.

### 7.5 Glyph silhouettes (COL-08)

I rasterised the evidence aspect's glyph descriptions at 12 and 16 px (8x supersampling, greyscale ink coverage), approximating the dashes and the `?`, and added a provisional BLOCKED glyph. Distance = 1 minus the weighted intersection over union of two renders. Closest pairs at 12 px: unknown against blocked 0.313, fail against conflict 0.330, pass against blocked 0.428; at 16 px: fail against conflict 0.334, unknown against blocked 0.349. All 28 pairs are at least 0.313; the 0.25 floor was chosen after the first render, so it is a regression floor and not an independent test. PREDICTION about shapes I drew from a text description; the real glyph geometry belongs to the status-display aspect, and the test must be rerun on it.

### 7.6 Existing OSS colour systems (considered, not adopted, not benchmarked)

The repository is OSS-first (ADR-016). I opened the pages below on 2026-09-29. Features are as those pages state; anything else is UNVERIFIED.

| System | What the source says | Licence (source) | Why not adopted here | Source |
|---|---|---|---|---|
| Radix Colors | 12-step scales per hue; steps 11 and 12 are documented as text, "guaranteed to Lc 60 and Lc 90 APCA contrast" on a step 2 background of the same scale; the page has no colour-vision-deficiency guidance | MIT (repository) | Contrast is by construction per hue, but no cross-hue CVD separation, no neutral UNKNOWN role and no diff or category grammar is stated; it would still need our COL-07 to COL-10 lint (UNVERIFIED that its hues pass) | S23, S24 |
| Primer primitives | Tokens as JSON compiled with Style Dictionary, said to follow the W3C design token specs (which draft or version: UNVERIFIED); light and dark themes plus high-contrast, tritanopia and colour-blind variants | MIT (repository) | Status and diff are green and red by default (S13); its CVD themes swap diff to blue and orange; that is diff options G and H in section 8, kept as study arms. Its source tokens are the closest precedent for our file | S13, S25 |
| Adobe Leonardo | Generator of colour scales from a target contrast ratio; npm package and web app; built on D3 colour | Apache-2.0 (repository) | A generator for surfaces and text ramps, not a status or CVD system. Could produce the neutral ramp in a later revision; not evaluated (whether it supports APCA: UNVERIFIED) | S26 |
| Material colour utilities (HCT) | HCT space (hue, chroma, tone) based on CAM16 and L*, tonal palettes, a contrast component | Apache-2.0 (repository) | The page does not state a tone-difference contrast guarantee that I could read, so I build nothing on it (UNVERIFIED). HCT is a candidate replacement for the OKLCH search, and a study arm for the palette | S27 |
| Carbon | Repository licence only was verified; the colour documentation page did not load | Apache-2.0 (repository) | Colour behaviour UNVERIFIED; not evaluated | S28 |

None of these was measured against COL-01 to COL-12. The rejection is therefore a scope decision (no system found that states a neutral UNKNOWN role, a CVD floor across status hues and parity with our token format), not a measured comparison. Deferred as O13.

## 8. Diff colour

Why dedicated hues. A diff shows added and removed content beside evidence status. If added were green and removed red, a row could show a green wash and a PASS glyph, or a red wash and a FAIL glyph, for unrelated reasons.

| Option | Statement | Confusion with status or accent |
|---|---|---|
| G | Green and red washes, the common convention. Primer's default diff uses its success and danger washes (S13) | Identical tokens to PASS and FAIL by construction |
| H | Blue and orange. Primer's protanopia-deuteranopia themes swap additions to blue and deletions to orange (S13) | Blue is the accent; orange sits next to fail and stale |
| I (chosen) | Added 207, removed 300, changed 125, on rail, sign and wash; never a glyph | Hue gap at least 39.7 degrees to every status and accent hue; worst-case dE_OK to a status, accent or other diff colour 0.028 (light) and 0.040 (dark), so under CVD hue can coincide and the form (rail, sign, wash against glyph) decides |
| J | Neutral washes with signs and strike-through only | None, but loses fast scanning; kept as a study arm |

The chosen hues fill the three gaps left between the status and accent hues (85 to 165, 165 to 250, 250 to 350). Learnability of removed as violet is untested; the sign, the word and the strike-through carry the meaning. The dedicated-hue design has no precedent found in the sources read.

## 9. Categorical palette

Use. Only when the owner enables "colour by" (bounded context, kind, persona). Every use has the category name or a glyph beside the mark. At most 8 at once; use the first n in the order below, which was chosen so any prefix keeps the best separation I could get.

| Categories in use | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| Light min dE' (CAM02-UCS) | 35.6 | 27.9 | 14.9 | 14.4 | 13.9 | 13.5 | 13.1 |
| Dark min dE' | 38.6 | 14.0 | 13.9 | 13.9 | 13.9 | 13.9 | 13.7 |

Comparison (PREDICTION, CAM02-UCS distance over normal vision and severities 10 to 100 for the three deficiencies, both conventions):

| Palette | Minimum distance | Marks below 3:1 on at least one light surface |
|---|---|---|
| Okabe-Ito 8 including black, unmodified (S12) | 10.97 (orange against reddish purple, tritan) | 5 of 8 (1.14 to 2.95) |
| Chosen | 13.06 light, 13.66 dark | 0 |
| Petroff 2021, 8 colours, generated without a 3:1 rule | 18 required; best sets 19.6 to 20.2 (S10) | not stated |
| My search, light, minimum contrast relaxed (linear convention only, wide lightness band, chroma 0.06 to 0.15) | 17.3 at 3.15:1; 21.8 at 2:1; 22.5 at 1.5:1 | by definition |

So a 3:1 rule for marks costs about 5 CAM02-UCS units at 8 colours in my search, which is not a proven optimum. Because every mark carries a label, WCAG does not require 3:1 for it (S3 exempts a graphic when text conveys the same information; its worked example is a chart, and it lists status icons without associated text as needing 3:1, so applying the exemption to a glyph beside its word is my inference); I keep 3:1 for legibility of small marks and record that as a choice.

## 10. Delivery

- `tokens.css` is generated from the token file by a Python script owned by the tokens aspect: `:root` (light), `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { ... } }` and `:root[data-theme="dark"] { ... }`, with `color-scheme` set. `light-dark()` is Baseline "newly available" since May 2024 (S7), so it is not relied on. Values are the hex fallbacks. A test regenerates the file and diffs it (invariant: what you see is generated from the model; here, from the tokens).
- Under the CSP (`style-src 'self'`, `default-src 'none'`), the CSS is an external file; no `style` attribute; toggling `data-theme` uses `setAttribute`, which is not a style write (repository: `src/eija_studio/interfaces/http.py` line 63).
- Forced colours (proposal for the accessibility aspect, which measured that hex `fill` and `stroke` are not overridden in Chromium 154 and `currentColor` is):

| Token family | System colour (S6) |
|---|---|
| `surface.*` | `Canvas` |
| `text.primary`, `text.secondary`, `border.*`, `status.*.fg`, `diff.*.fg` (rail), `category.*.mark` | `CanvasText` (via `currentColor`) |
| `text.disabled` | `GrayText` |
| `accent.fg` for links | `LinkText` |
| Selection, focus ring | `Highlight` (border and outline; no fill) |
| Washes (`tint`, `strong`) | none (dropped) |

In forced colours hue is lost by design; every state must survive as glyph, word, sign, dash or strike-through. This is a sibling test: two states that differ only by computed background colour must also differ in border, shape or text.

## 11. Worked arithmetic and oracles

WCAG 2.2 relative luminance and ratio (S2): channel c in 0..1; linear = c / 12.92 if c at most 0.04045, else ((c + 0.055) / 1.055) ^ 2.4; Y = 0.2126 R + 0.7152 G + 0.0722 B; ratio = (Y_lighter + 0.05) / (Y_darker + 0.05); no rounding before comparison (4.499 fails).

Example. `text.primary` `#262422` = (38, 36, 34): linear (0.01938, 0.01764, 0.01600), Y = 0.01789. `surface.canvas` `#F8F6F4` = (248, 246, 244): linear (0.93869, 0.92158, 0.90466), Y = 0.92400. Ratio = (0.92400 + 0.05) / (0.01789 + 0.05) = 14.346.

Oracles a test can use: black on white 21.000; `#767676` on white 4.542 (passes); `#777777` on white 4.478 (fails); dE_OK black to white 1.000; Machado deuteranopia severity 100 on linear (1, 0, 0) gives (0.367322, 0.280085, 0) which is `#A39000`; CAM02-UCS J' of white 100.0 by construction.

Search procedure (reproducible from this description; the scratch scripts are in gitignored `.tmp/` and are not part of the change): candidate colours on a lightness grid of 0.01 at the hue, chroma the smaller of the cap and the sRGB gamut maximum; keep those whose minimum ratio over the four surfaces lies in the band (and Lc at least 45.5 in dark); take the exhaustive product over roles and keep the maximum of the minimum pairwise dE_OK; repeat for the neutrals (grey ramp, chroma 0) against the chromatic five, then for diff `fg`. Categories: simulated annealing over 8 slots with fixed hues, chroma from a short list and lightness on a 0.02 grid, objective the minimum CAM02-UCS distance; then a greedy farthest-point order.

APCA numbers are advisory and were computed by my scratch implementation of the published formula (constants as read in `VIS`, checked on black and white). No APCA code is added to the repository; whether implementing the formula needs legal review is open (SYN C10).

## 12. Study protocols (nothing run)

| Id | Question | Design | Sample | Measures | Stop criteria |
|---|---|---|---|---|---|
| CS1 | Are statuses read correctly by people with and without CVD? | Within-subject on the excursion evidence rail at 12 and 16 px; conditions: glyph, word and hue (proposed); glyph and word only; hue and word only (diagnostic). Counterbalanced. Screened with a standard colour-vision test | At least 12 with protan or deutan CVD and 12 with normal vision; recruitment may cap this, in which case results are formative | Accuracy per status; UNKNOWN read as PASS (target 0); time; SEQ | Stop and redesign if any participant reads UNKNOWN as PASS in the proposed condition; report effect sizes with intervals. Add a confusion measure: AI-proposed items read as owner-selected (one accent hue carries selection and AI-proposed, so only dashed against solid edge and the word separate them); stop criterion: any AI-proposed item read as owner-selected in the proposed condition |
| CS2 | Does lifting dark text to Lc 60 and above help? | `text.secondary` at 4.5:1 against Lc 60 against Lc 75 on the same reading and lookup tasks, dark theme | At least 20 | Reading errors, time, preference, Raw TLX | Keep the current value unless the interval excludes zero difference in errors |
| CS3 | Do dedicated diff hues confuse or help? | Options G, H, I, J on a change review; add a cross-check: point to the FAIL rows among diff washes | At least 20; keyboard-only cohort separate | Time to count added and removed operations; wrong-family errors (target 0); comprehension after a legend | Stop I if it produces more wrong-family errors than G; also count AI-proposed against selected confusions on the review chapters |
| CS4 | Are 8 categories usable with labels? | Identify and group items with and without labels, 4, 6 and 8 categories | At least 12 | Accuracy, time | Cap the number of categories at the largest n with no error increase |
| CS5 | First impression | 50 ms and 500 ms ratings of the default view in light and dark (SYN arm) | At least 20 | Appeal ratings with intervals | None; informative only |

## 13. Open questions and contradictions

| # | Item | State |
|---|---|---|
| O1 | WCAG 2.2 ratio against APCA for dark (SYN C10) | Open. The two disagree for status glyphs in dark (ratio at least 4.4, Lc 36.7 to 69.8). I lifted dark glyphs to Lc 45 and secondary text to Lc 60 at no extra tokens; CS2 tests it. APCA is unratified and WCAG 3 has no contrast algorithm yet (S14, S15) |
| O2 | CVD simulation convention | Unresolved by the sources (S9, S10). Every criterion uses the worse of both. An earlier draft flipped under the other convention (section 7.3) |
| O3 | The 0.02 just-noticeable difference applies to large uniform patches (gamut-mapping constant, S6), not to 12 px glyphs | COL-07 is a floor, not evidence of discriminability; CS1 measures it |
| O4 | Glyph geometry, BLOCKED glyph, and the dashed outline shared by STALE and AI-proposed (evidence aspect O9) | Hue helps (stale against the accent is not among the five closest pairs in either theme, so it is above 0.068 in light and above 0.054 in dark) but is not a test. Owned by the status-display aspect |
| O5 | Overlay edge in light theme: `overlay` equals `raised`; a shadow is invisible in dark | Decision in this revision: 1 px `border.control` edge and no shadow (the token descriptions now say so; an earlier token draft said "one shadow"). Rubric reading: 2 elevations, of which the light second one is an edge, not a fill. Visibility of a light shadow not measured |
| O6 | The status display order proposals differ between aspects | Not decided here |
| O7 | Category hue overlap with status and diff hues (every status hue is within 22.5 degrees of a category hue by construction) | Mitigated by form and opt-in; CS3 and CS4 |
| O8 | Neutral hue target 80; realised hue drifts at chroma below 0.006 | Cosmetic; chroma is the rule |
| O9 | CVD prevalence figures are from an author page (8, 5 and 4 percent of males by ancestry, S11) and not from an epidemiological paper | Medium |
| O10 | Machado severities 50 and 100 only in the criteria; Petroff checks 1 to 100 | Categories use 10 to 100 step 10; statuses use 50 and 100. Checked at 10 to 100 step 10 after the audit: worst status pair 0.0612 (light) and 0.0448 (dark, deutan 90, gamma convention), so the 0.04 floor still holds but 0.046 is not the minimum over all severities |
| O11 | PARTIAL status | Not adopted; needs a kernel ADR (SYN C2) |
| O12 | One accent (hue 250) carries link, selection, focus ring, primary button, AI-proposed, RUNNING and canvas MEANING, so P9 (AI-proposed distinct from selection) rests on form (dashed against solid edge) and word only | Disclosed; measured in CS1 and CS3 as an AI-proposed against selected confusion rate |
| O13 | Existing OSS colour systems (Radix Colors, Primer primitives, Leonardo, Material colour utilities, Carbon) were not run through COL-01 to COL-12 | Deferred: benchmark their status and diff tokens with the same lint (section 7.6) before the palette is frozen |

## 14. Sources

Access date for every URL: 2026-09-29. Confidence: high (standard, primary source or first-party file), medium (author page, preprint, single source), low (secondary).

| Id | URL or file | Type | Used for | Conf. |
|---|---|---|---|---|
| S1 | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | standard (Understanding) | SC 1.4.1 | high |
| S2 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | standard | SC 1.4.3, formula, no rounding | high |
| S3 | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | standard | SC 1.4.11 | high |
| S4 | https://www.designtokens.org/tr/2025.10/color/ | community group report | colour value structure, `none`, hex | high |
| S5 | https://www.designtokens.org/tr/2025.10/format/ | community group report | groups, `$type`, aliases, `$extensions`, no modes | high |
| S6 | https://www.w3.org/TR/css-color-4/ | candidate recommendation draft, 2026-09-26 | oklch, JND 0.02, system colours | high |
| S7 | https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark | official docs | `light-dark()` newly available since May 2024 | high |
| S8 | https://bottosson.github.io/posts/oklab/ | primary (author) | Oklab design; D65 and normal well-lit viewing assumption | high |
| S9 | https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html | primary (authors' page, IEEE TVCG 15(6), 2009) | matrices | high; paper PDF not read |
| S10 | https://arxiv.org/abs/2107.02270 (PDF read) | preprint (Petroff, 2021) | thresholds 18 for 8 colours, CAM02-UCS, linear application | medium |
| S11 | https://jfly.uni-koeln.de/color/ | author page (Okabe and Ito) | prevalence, redundancy advice, vermilion | medium |
| S12 | https://siegal.bio.nyu.edu/color-palette/ | secondary | Okabe-Ito hex values | medium |
| S13 | https://raw.githubusercontent.com/primer/primitives/main/src/tokens/component/diffBlob.json5 (last commit for that path 2025-07-02) | first-party source file | diff colours by theme | high |
| S14 | https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html | author documentation | Lc guidance; unratified | medium |
| S15 | https://www.w3.org/TR/wcag-3.0/ | working draft, 2026-09-10 | contrast algorithm undecided | high |
| S16 | https://dafny.org/blog/2023/04/19/making-verification-compelling-visual-verification-feedback-for-dafny/ | first-party blog | quiet success, stale dimmed, shapes for colour-blind users | high |
| S17 | https://linear.app/now/how-we-redesigned-the-linear-ui | first-party blog | LCH themes, three inputs, more neutral | medium |
| S18 | https://docs.github.com/en/get-started/accessibility/managing-your-theme-settings | official docs | light and dark colourblind themes exist | high |
| S19 | `src/eija_studio/resources/web/app.css` | repository | baseline colours | high |
| S20 | `src/eija_studio/interfaces/http.py` line 63 | repository | CSP | high |
| S21 | `src/eija_studio/domain/evidence.py` | repository | kernel words PASS, FAIL, CONFLICT, STALE, UNKNOWN | high |
| S22 | `docs/hci/design/{evidence-and-change-review,accessibility,typography,canvas-uml-interaction,motion-and-performance}.md` | repository (sibling aspects, same lane) | interfaces in section 1 | medium |
| S23 | https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale | official docs | Radix scale steps and APCA statement | high |
| S24 | https://github.com/radix-ui/colors | first-party repository | MIT licence | high |
| S25 | https://github.com/primer/primitives | first-party repository | MIT licence, themes, token format | high |
| S26 | https://github.com/adobe/leonardo | first-party repository | purpose, Apache-2.0 | high (purpose); contrast methods not confirmed |
| S27 | https://github.com/material-foundation/material-color-utilities | first-party repository | HCT, Apache-2.0 | high (existence); contrast claims not confirmed |
| S28 | https://github.com/carbon-design-system/carbon | first-party repository | Apache-2.0 only | high |

Cross-check tool, not a source: `colorspacious` 1.1.2 (MIT) installed with pip into gitignored `.tmp/`; used to confirm Machado matrices and my CAM02-UCS implementation; not added to the repository.
