# Design system architecture

Lane `lane/ux-research`, aspect `design-system-architecture`. Date 2026-09-29. Status: proposed. Decision record: [HCI-ADR-0068](../../adr/0068-hci-design-system-architecture.md). Token files: [index.tokens.json](../../../design/tokens/index.tokens.json), [spacing.tokens.json](../../../design/tokens/spacing.tokens.json). Other aspects' token files this design consumes: [motion](../../../design/tokens/motion.tokens.json) (ADR-0066), [color](../../../design/tokens/color.tokens.json) (ADR-0059), [typography](../../../design/tokens/typography.tokens.json) and [fonts.lock.json](../../../design/fonts.lock.json) (ADR-0060). Source ids `AIC`, `VIS`, `DEV`, `DGM`, `SLP`, `LAW`, `V1` and so on are defined in [../research/SYNTHESIS.md](../research/SYNTHESIS.md) section 1.

Labels. **MEASURED** = a script or command I ran on 2026-09-29 (environment in section 1). **PREDICTION** = model output with constants and a range, not a user result. **ESTIMATED** = a number with no source. **UNVERIFIED** = not opened or not confirmable; nothing is built on it. No user study has been run and no claim of user benefit is made.

## 0. Decisions first

| # | Decision | Confidence | Evidence |
|---|---|---|---|
| D1 | Tokens are DTCG 2025.10 files in `design/tokens/`. A stdlib-only Python generator (about 140 code lines) writes one committed `tokens.css`, loaded through `@import ... layer(tokens)` and including the `@font-face` rules from `design/fonts.lock.json`. A test regenerates it and compares bytes. Every token is validated before the emit filter: an unknown type, unit, colour space, alias, unclassified root group, or a hex that disagrees with its OKLCH source fails the build. Terrazzo is an optional cross-check, not a gate. | Medium: fitted on the 5 real token files; one Windows machine | 4.2, M8, M13 |
| D2 | CSS is layered: `legacy, reset, tokens, base, components, overrides`. Custom properties have three tiers, but a tier exists only where a value changes across it. Theme output follows the colour aspect (three blocks, hex values) except that `color-scheme` is scoped to `:root[data-ui="next"]` until S8 (a global one changed the unmodified legacy page under a dark OS, M12); density is `data-density` on any region. No unlayered author CSS. The `reset` layer reverts every legacy declaration inside a new component (`all: revert`), component roots set inherited type and colour again in `base`, and new layers use `!important` only in one reset rule for `[hidden]` (5.2). | Medium: one Chromium | 5, M10, M12, M13, M15 |
| D3 | Components are native elements first, then vanilla ES-module builder functions with APG patterns and `data-*` state. No shadow DOM, no custom elements, no Lit, Zag or Web Awesome in v1. A vendored Preact core passed the CSP in a spike and is the recorded fallback (7.1). | Medium: measured on Chromium 151 only | 7, M3 to M5, M9, M14 |
| D4 | The inventory is 15 primitives (78 named states) and 8 recipes. A primitive must serve at least 2 of the 14 top tasks. Adding, removing or splitting one needs an HCI-ADR. Not in v1: tooltip, toast, anchored popover positioning, an icon set. | Low to medium: the task lists are my analysis | 8 |
| D5 | A static gallery is generated from the inventory and from real excursion-workflow fixtures, served under the Studio's exact CSP. It reports its own coverage with the Studio's words: a state with no check is NOT_RUN, never PASS. | Medium | 9 |
| D6 | Gates: ARIA snapshot, computed-style and geometry snapshot, and axe with `target-size` enabled. Pixel snapshots are advisory and exist for the reference platform only. Sixteen named tests DS-01 to DS-16. | Medium: pixel output was byte-identical in 18 runs on one machine; other machines untested | 10, M5, M6 |
| D7 | Budgets are bytes of unminified source (JS 120,000; CSS 40,000; `tokens.css` 18,000; one file 24,000), lines of at most 100 characters (generated files included: the generator wraps long values), at most 30 first-render requests, import depth at most 3, and a cold-load ready p95 of at most 200 ms (warn) and 1,000 ms (fail). | Low: a two-point fit whose range straddles 200 ms | 6 |
| D8 | Spacing is 8 steps on a 4 px base, in rem. Density numbers are the layout aspect's (control and row 28 px, typed field 32 px, compact 24 px), stored as tokens with two radii and a 24 px floor. The accepted pointing cost of 28 px against the baseline's 44 px is +0.078 s per pointing act (PREDICTION). | Low: density belongs to the layout aspect | 5.1 |
| D9 | Migration is a strangler plan in nine phases, S0 to S8. The legacy CSS is imported unmodified into `@layer legacy`. New CSS is scoped to `[data-ui="next"]`, an attribute on `<html>`, until S8. The owner decision surface moves last. Any file change under `resources/web` changes the implementation fingerprint, so phases ship as batched releases. | Medium | 11, M11 |
| D10 | Every UI change cites an accepted HCI-ADR in a commit trailer. A fast local check enforces it. Only the owner accepts an ADR; agents draft. | Medium for the mechanism; untested in practice | 12 |

## 1. Scope, method and limits

**Question.** How should the Studio's design system be built so that a developer-facing product can grow from three files into a coherent interface, under ADR-013 (no build-time framework; untrusted text through DOM text nodes only) and the strict CSP, without becoming the kind of UI the anti-slop rubric rejects?

**What I read.** Every dossier in `docs/hci/research/`, `personas-and-jtbd.md`, `design/brief.json`, `AGENTS.md`, `ARCHITECTURE.md`, `interfaces/http.py`, `adapters/identity.py`, `domain/evidence.py`, the three baseline web files, and the `hci` lane's `pyproject.toml` and `quality/sessions/hci.py`. Late in the session the other aspects published token files and design documents; I read the parts that constrain this aspect (the five token files and `fonts.lock.json` in full; the colour, typography, layout, accessibility, content and canvas documents by section and search, not page by page). Where they conflict with each other or with this document, section 14 lists it.

**What I measured.** Fifteen measurements M1 to M15 (section 15); M12 to M14 were added after the first audit and M15 after the second. Environment: Windows 11, 12 logical CPUs shared with other agents, Python 3.12.10, Node 22.22.0, Playwright 1.58.0 driving Chromium 151.0.7922.34 through `executable_path`, headless, device pixel ratio 1, one browser at a time. The Studio ran from this worktree with the `hci` lane's virtual environment (FastAPI 0.128.2, uvicorn 0.48.0), offline provider, loopback. All temporary files are in `.tmp/dsa/` (gitignored). Timings are from a loaded machine and are wide.

**What I did not do.** No Firefox or Safari. No real component code exists, so every component figure is a specification or a spike, not a result. No cross-platform screenshot comparison. No user study. No hosted or CDN measurement. WebFetch returns model-written summaries; where a claim depends on exact wording I say "per fetch summary".

## 2. Interfaces and assumptions

Nothing here is guessed silently. Each row is an assumption another aspect or the kernel must confirm.

| Id | Assumption | Owner | If it is false |
|---|---|---|---|
| I-COL | Colour tokens are sibling groups `color.light.*` and `color.dark.*` (142 tokens, OKLCH with hex, 40 aliases). The colour aspect wants `tokens.css` as three blocks with hex values, not `light-dark()` (color-system.md section 10, C9). The generator follows it, with one deviation: `color-scheme` is written on `:root[data-ui="next"]` until S8, not on `:root` (5.4, M12). | Colour aspect (ADR-0059) | A different theme layout is one generator option; the scope is one parameter. |
| I-TYP | Type tokens are 5 sizes, 2 weights, 2 families and 9 `text.*` composites; three WOFF2 files, 40,904 B; `@font-face` rules are generated by this aspect (typography.md section 8). Composites become one custom property per member. | Type aspect (ADR-0060) | Without fonts the system stack stays; no font bytes. |
| I-MOT | `motion.tokens.json` (ADR-0066) is the motion source. Its `budget` group is test-only and is not emitted. | Motion aspect | Nothing changes here. |
| I-STA | Ten status marks (six evidence words, BLOCKED, ELIGIBLE_FOR_LOCAL_REVIEW, RUNNING, AI_PROPOSED) have a shape, a word and a colour. | Status aspect | The `status-mark` primitive renders words only (`ai-interaction.md` A2 fallback). |
| I-SEC1 | `/assets/{name}` serves flat URL names from an allowlist with an extension-to-MIME map (woff2 included). Today it serves exactly `app.js` and `app.css`, and other lanes' documents assume all client code stays in those two files. | Security-boundary aspect | Fallbacks F1 (JS) and F1c (CSS) in 7.3; S1 ships without fonts. |
| I-SEC2 | `font-src 'self'` is added. It is now required, because fonts exist (typography.md MEASURED that Chromium 151 refuses them without it). | Security-boundary aspect | No custom fonts. |
| I-SEC3 | The CSP string is one exported constant. Today it is an inline literal in `http.py`. | Security-boundary aspect | DS-11 reads the string from `http.py` source with a regular expression. |
| I-KERN1 | `identity.implementation_files()` hashes every file under `resources/web`, so any UI file change changes the implementation fingerprint (11.1). A kernel ADR may hash browser assets as a separate dimension. | Kernel lane | Every UI release makes stored technical receipts STALE and the release fixture untrusted until the owner stamps; phases are batched (D9). |
| I-LAY | Density is the layout aspect's: chrome control and row 28 (compact 24), typed-answer field 32 (28), chip 24 (20, non-interactive only), gutter 12 to 16 (8) (layout-model.md section 3.5). Row-count figures in 5.1 assume an 800 px tree column. | Layout aspect (ADR-0058) | Row counts are recomputed; token names stay. |
| I-CAN | The canvas aspect builds `canvas.js` from SVG and HTML nodes and reads the `canvas.*` colour roles that now exist. | Canvas aspect (ADR-0061) | Canvas stays inside `app.js`. |
| I-A11Y | The accessibility aspect (ADR-0067) owns the complete test plan: axe 4.13.0 with `target-size` enabled, scripted keyboard, focus, reflow, forced-colour and text-spacing tests, manual screen-reader passes. It found 1 of 5 baseline failures with axe alone. DS-07 and DS-08 are the design-system slice of that plan, not a replacement. | Accessibility aspect | Sessions report NOT_RUN without Playwright or Chromium (`AGENTS.md`). |
| I-HCI | The `hci` lane owns the extra `hci = ["playwright==1.63.0", "axe-playwright-python==0.1.8"]` and the nox session `hci` (read from its worktree). This aspect adds sessions in its own module `quality/sessions/design_system.py` and reuses the extra. This environment has Playwright 1.58.0, not 1.63.0. | HCI lane | See 14. |
| I-CONT | Every UI string carries `data-eija-source` with one of chrome, model, ai, provider, user, and a vocabulary lint runs on `chrome` strings (content-and-onboarding.md D7, ADR-0065). | Content aspect | DS-15 still checks the attribute exists. |
| I-GOV | Only the owner moves an HCI-ADR from proposed to accepted. | Owner | Governance (12) has no authority source. |

## 3. Baseline (MEASURED, 2026-09-29)

Files: `src/eija_studio/resources/web/{index.html,app.css,app.js}`. Method: `wc -c`, and a Python regular-expression script over the three files (M1). Static count; text produced by `app.js` at run time is not included.

| Measure | Value |
|---|---|
| Bytes | `app.js` 10,561; `app.css` 7,156; `index.html` 7,561; total 25,278 |
| Lines | `app.js` 32 (longest 1,585 characters; 18 lines over 200); `app.css` 1 line of 7,155 characters; `index.html` 17 lines (longest 1,446) |
| Coupling | 55 element ids in `index.html`; 50 distinct ids read by `app.js` through `$()`; 18 `onclick` or `onsubmit` assignments; 2 module-level `let` variables |
| Tokens | 10 custom properties in `:root`; 19 distinct hex colours, 10 of them written as literals outside `:root` |
| Type and shape | 13 distinct `font-size` values in 32 declarations; 6 distinct border radii (7, 8, 10, 12, 14 through `var(--radius)`, 30 px) |
| Spacing | 87 non-zero px lengths in `padding`, `margin` and `gap`; 30 distinct values from 4 to 50 px; 38 of 87 (43.7%) are multiples of 4 px |
| Controls | Buttons have `min-height: 44px` |
| Modes | 0 `prefers-color-scheme`, 0 `prefers-reduced-motion`, 2 `@media` |
| Layers and structure | No `@layer`, no component boundary: state is two module variables and every view is rebuilt by one `render()` function on line 18 |
| Static request | `GET /assets/app.js` p50 2.17 ms, p95 2.78 ms (keep-alive, n = 110); `app.css` p50 2.13 ms; new connection p50 2.5 ms; uvicorn 0.48.0 `FileResponse`, `no-store` |
| Cold load | DOMContentLoaded p50 89.6 ms, p95 132.8 ms; load p50 94.4 ms; ready (connection chip shows the provider) p50 114.3 ms, p95 159.1 ms, max 170.1 ms; n = 22 after 3 discarded of 25 |
| Identity | `implementation_files()` hashes 26 files; 3 are under `resources/web` (M11) |

Reading. The baseline is partly tokenised already: the accent is one variable used 14 times, so changing the accent is one edit. The gaps are spacing (30 values), type (13 sizes), radius (6), dark mode (none), and structure: a reviewer or an AI agent sees a 7,155-character line as one change. `test_browser_never_interprets_provider_html` in `tests/test_http_and_architecture.py` checks only `innerHTML` and `eval(`.

## 4. Token pipeline

### 4.1 Requirements

| # | Requirement | Type | Source |
|---|---|---|---|
| R1 | Source is DTCG 2025.10, pinned; `/tr/drafts/` is ignored | hard | S1, S2 |
| R2 | The pipeline runs from a clean checkout with `pip install -e .[dev]`; dependencies live in a pyproject extra, pinned `==` | hard | `AGENTS.md`, `pyproject.toml` |
| R3 | Output is deterministic and diffable, so a test can compare bytes (invariant I2 applied to the design system) | hard | ADR-0019, `AGENTS.md` |
| R4 | Unknown type, colour space or alias fails the build (invariant I3 applied to tokens: never round up) | hard | ADR-010 |
| R5 | Types in use today: colour (OKLCH with hex), dimension, duration, cubicBezier, number, fontFamily, fontWeight, transition, typography composite | hard | the five token files |
| R6 | Output shape the other aspects asked for: hex values and three theme blocks (colour C9), density blocks (layout), `@font-face` from `fonts.lock.json` (typography section 8) | hard | I-COL, I-TYP, I-LAY |
| R7 | No new Node dependency for a token edit beyond what the repository's hooks already need | soft | R2; ADR-0017 (see 4.2) |
| R8 | Small surface to audit and to keep patched | soft | supply chain (below) |

### 4.2 Options and measurements

Input for every measurement: the five real token files (`index`, `spacing`, `motion`, `color`, `typography`; 243 tokens) and `design/fonts.lock.json` (M8).

| Option | What it is and who does it | Measured result | Drawbacks | Verdict |
|---|---|---|---|---|
| A: hand-written custom properties | The baseline: 10 properties in `:root`, everything else literal | 30 spacing values, 13 font sizes, 6 radii, 10 literal hex colours | No dark mode, no lint, no single source | Rejected as the end state |
| B: Style Dictionary 5.5.5 (Apache-2.0) | Node build tool, `usesDtcg: true`, `css` transform group. S3, S4, S5 | Install: 106 packages, 55 MB, 44 s; Node `>=22.0.0` (registry). On the 5 real files **30 of 235 declarations rendered `[object Object]`**: every `duration` value (motion 10, budget 18, load 2). Colours came out as hex, dimensions correct, typography composites as `font` shorthand. The docs say the 2025.10 format "does not have full support yet" (per fetch summary of S3; that page does not mention a `usesDtcg` option, which comes from my own configuration `sd/build3.mjs`) | Custom transforms for duration and transition; a custom format for three theme blocks and density; Node toolchain; its 5.5.4 and 5.5.5 release notes list a transitive-dependency fix and a prototype-pollution advisory (per fetch summary of S4) | Rejected as default |
| C: Terrazzo 2.7.1 (MIT) | Node CLI plus `@terrazzo/plugin-css`. S5, S6, S7 | Install: 68 packages, 61 MB, 89 s; dependencies include `vite`, `vite-node` and the native `lightningcss` binary for Windows. **With default lint it stopped with 28 errors** (plus 12 warnings; re-run 2026-09-29), all `core/valid-color` (hue range), on the colour aspect's OKLCH values whose hue is the DTCG keyword `none`. With that rule off it built 243 tokens (47,205 B on the re-run, 47,029 B on the first run before other aspects edited their files; comments and separate light and dark names included). Density through `$extensions.mode` worked. Re-compared on 2026-09-29: 106 non-colour custom-property names exist in both outputs; 104 have identical values and 2 (`--font-family-sans`, `--font-family-mono`) differ only in that Terrazzo quotes every family in the fallback stack (equivalent CSS) | Node plus Vite outside the pinned Python extras; a default lint that rejects a value the DTCG Color Module allows (hue `none`, S34); mode shape is a Terrazzo extension; no theme roles. Its own documentation page calls it "the only tool that supports the full DTCG format" (S6, re-read 2026-09-29), which is counter-evidence to the claim that Style Dictionary or a custom tool is enough, and says resolver support is "coming in 2.0" although 2.7.1 is installed, so that page is stale on at least that point | Optional cross-check; fallback if the owner accepts Node |
| D: minimal Python generator | About 140 code lines (137 non-blank, non-comment, non-docstring, counted by script; Appendix A), stdlib only; one `tokens.css` | 243 tokens read; 16,087 B: 14,538 B of custom properties and `color-scheme` rules and 1,549 B of `@font-face`; 379 lines, none over 100 characters; gzip 2,653 B (M8). The first version wrote 15,974 B with 5 lines of 118 to 473 characters (font stacks, `unicode-range`), found by the audit; the generator now wraps values after commas. In-process build p50 1.1 ms (n = 30, first version, not re-timed). Refused 15 of 15 negative cases with the named reason (M8, `test_gen5.py`): shadow type under an emitted and under a non-emitted root, gradient type under a non-emitted root, a token with no type, dangling alias (emitted and non-emitted root), cyclic alias, duplicate token, non-OKLCH colour space, dimension without unit, unit `em`, duration without unit under a non-emitted root, hex that disagrees with OKLCH, colour without hex, a root group listed in neither `emit` nor `emit-not`; 2 positive fixtures build | We own it: colour spaces other than OKLCH, gamut mapping and alpha are ours to write when needed; a reviewer must read it | **Chosen** |
| E: tokens read at run time | The browser fetches JSON and sets properties with `style.setProperty` | CSSOM writes pass the CSP (M3) | Unstyled first paint; one more request before render; JavaScript required for layout | Rejected |

Constraint that decides between B, C and D. R2 is hard: the repository has no `package.json`, and `AGENTS.md` sends dependencies to pinned pyproject extras. B and C fail R2 unless the owner adopts Node for the repository.

Node is not absent from the contributor toolchain (correction after audit). The first draft called the repository Python-only. ADR-0017 names noslop (https://github.com/45ck/noslop, package `@45ck/noslop` 1.0.0, MIT, TypeScript, `engines.node >= 22.0.0`; its `package.json` read through the GitHub API on 2026-09-29, S32) as the hook and guardrail enforcer, so Node 22 or later is needed wherever those hooks are installed. Whether it is installed on a given machine is UNVERIFIED: no noslop configuration, hook file or `package.json` is tracked in this repository (`git ls-files`). The npm package named `noslop` (0.2.0, `engines.node >= 18`) belongs to another repository and is not evidence. R7 is therefore weaker than the first draft claimed and is not what decides the choice. The decision rests on R2 (a second dependency graph of 55 to 61 MB with native binaries, outside the pinned pyproject extras), on the measured defects of B and C with default settings, and on R8. Promoting the Terrazzo cross-check to a gate on machines that have Node 22 is possible, but a gate whose result is PASS on one machine and NOT_RUN on another is a weaker gate; the owner decides. B additionally fails R5 as shipped, and C fails R5 with its default lint. D passes R1 to R6 and R8 by construction, and the tokens stay tool-neutral, so switching to C later is one config file. This deviates from ADR-0016 (OSS first); the `docs/oss/REGISTER.md` row is in 4.6.

What the cross-check is worth. My first reference implementation rounded numbers to four decimals; the Terrazzo comparison showed three line heights changed (1.4286 for 1.428571). Regenerating and diffing (DS-01) cannot see that, because the generator is consistent with itself. The corrected reference writes numbers as given, DS-02 has a round-trip case for it, and the cross-check stays because it catches this class of defect. It runs only where Node exists.

Argument against. C works with no custom code and is an existing tool; D moves maintenance to this project. Triggers to revisit are in the ADR: the generator exceeds about 300 code lines, the colour aspect needs gamut mapping or wide-gamut fallbacks, or the owner adopts Node for another reason.

### 4.3 Token files and ownership

| File | Owner | Holds | State on 2026-09-29 |
|---|---|---|---|
| `index.tokens.json` | this aspect | manifest, `density.*` role tokens (6), `bundle.*` and `load.*` budgets, component inventory | written |
| `spacing.tokens.json` | this aspect | `space`, `size`, `border`, `focus`, `radius` | written |
| `motion.tokens.json` | motion aspect (ADR-0066) | `motion`, `budget` | present |
| `color.tokens.json` | colour aspect (ADR-0059) | 142 colour tokens, sibling groups | present |
| `typography.tokens.json` | type aspect (ADR-0060) | families, weights, 5 sizes, 9 `text.*` composites | present |
| `fonts.lock.json` | type aspect | 3 font files, unicode ranges, `@font-face` parameters | present |

`index.tokens.json` is a valid DTCG file whose root `$extensions` carry the manifest. DTCG requires tools to preserve extension data they do not understand (per fetch summary of S1). A DTCG resolver document (S2, `.resolver.json`, sets, modifiers, `resolutionOrder`) would express the same composition and theme modifiers in a standard way. It is not used because I did not test resolver support in either tool (Terrazzo's documentation says resolver support is coming in 2.0 although 2.7.1 is installed, so that page is stale; S6), and the specification excerpt I read does not say whether a token file may alias into another file without a resolver; my generator merges files by path and Terrazzo did the same on these files. Revisit when a tool documents and passes a resolver test on these files.

### 4.4 What the tokens must not contain

Token types the generator refuses on purpose: `shadow`, `gradient`, `border`, `strokeStyle`. The rubric bans decorative gradients and shadow-only elevation, and dark-mode shadows reach only 1.025 to 1.08 contrast against the surface (`VIS` 2.5, MEASURED there). Elevation is a colour surface step plus `border.hairline` (the colour aspect defines four surface steps). A shadow token needs its own HCI-ADR.

### 4.5 Build plan

| Step | Action | Files | Gate |
|---|---|---|---|
| 1 | Add `scripts/build_tokens.py` from Appendix A (it reads `emit` and `emit-not` from `index.tokens.json`) and `tests/test_tokens.py` with the 15 negative fixtures, the two positive fixtures and the number round trip | `scripts/`, `tests/` (outside `resources/web`, so the implementation fingerprint does not change) | DS-01, DS-02 in `nox -t fast` |
| 2 | Generate `src/eija_studio/resources/web/tokens.css`; commit it | `resources/web/` (changes the fingerprint; ships in phase S1) | DS-01 |
| 3 | Add `quality/sessions/design_system.py` with sessions `ds_static` (tag `fast`) and `ds_browser` (tags `full`, `release`); the second reports NOT_RUN without Playwright or Chromium | `quality/sessions/` | `AGENTS.md` lane rules |
| 4 | Add the optional cross-check `scripts/check_tokens_terrazzo.mjs`, run only when `node` is on the path, with `core/valid-color` off and a comment saying why; result NOT_RUN otherwise | `scripts/` | never a gate |
| 5 | When a token file changes, regenerate and commit both; the owning aspect's ADR authorises the value | `design/tokens/`, `resources/web/tokens.css` | DS-01, DS-16 |

Contributor flow for one token edit: edit the JSON, run `python scripts/build_tokens.py`, commit both files with an `HCI-ADR` trailer (section 12). A hand edit of `tokens.css` fails DS-01.

Failure modes and their answers:

| Failure | Consequence | Answer |
|---|---|---|
| Two files define the same path | ambiguous value | duplicate token stops the build |
| A token type the generator does not support sits under a root that is not emitted (for example `bundle`) | it would pass unseen if only emitted roots were checked | every token is validated before the emit filter; a root in neither list stops the build |
| Alias to a token that does not exist | a component reads nothing | dangling alias stops the build; DS-04 stops the component |
| A colour role has a light value and no dark value | half-themed UI | DS-06 |
| Hex and OKLCH disagree | the picture and the contrast lint differ | the build stops (102 of 102 agree today, MEASURED) |
| Generator and Terrazzo disagree | one of them is wrong | the cross-check prints the token; the owner decides |

### 4.6 Register row for `docs/oss/REGISTER.md`

| Capability | OSS adopted | Alternatives checked | EIJA custom glue | Why custom was needed / replacement path |
|---|---|---|---|---|
| Design tokens to CSS | none for the generator; DTCG 2025.10 as the format; Terrazzo 2.7.1 as an optional cross-check | Style Dictionary 5.5.5 (30 of 235 declarations wrong with the default transforms), Terrazzo 2.7.1 (works with one lint rule off; adds Vite and a native binary and an `npm` dependency graph outside `pyproject.toml`). A Python DTCG library: not found. Seven guessed PyPI package names returned 404 and the web-search budget was exhausted, so this alternative is UNVERIFIED | `scripts/build_tokens.py`, about 140 code lines | Dependencies are pinned as extras in `pyproject.toml` (Node is needed only where the noslop hooks are installed, 4.2). Replacement: Terrazzo with a `terrazzo.config.mjs` once the owner accepts a Node toolchain; token files do not change |

## 5. CSS architecture

### 5.1 Spacing and rhythm: baseline against proposal

| Measure | Baseline (MEASURED, section 3) | Proposal | Basis |
|---|---|---|---|
| Distinct spacing values | 30 (4 to 50 px) | 8 steps: 4, 8, 12, 16, 24, 32, 48, 64 px | by construction, `spacing.tokens.json` |
| Values that already lie on the proposed scale | 25 of 87 (28.7%) | 100% by DS-05 | MEASURED count, script M1 |
| Multiples of 4 px | 43.7% | 100% | SLP metric M18 asks for at least 90% (a hypothesis, `SLP` 3.2) |
| Distinct radii | 6 | 2: 4 px controls, 8 px floating surfaces | by construction |
| Control and row height | 44 px buttons; no rows | 28 px default, 24 px compact | layout aspect, `layout-model.md` 3.5 |
| Typed-answer field height | not measured | 32 px default, 28 px compact | layout aspect |
| Pointer-target floor | none stated | 24 px (WCAG 2.2 SC 2.5.8, Level AA; S21) | standard |

Cost of the smaller control height (PREDICTION). Fitts's law in the Shannon form, `MT = a + b * log2(D/W + 1)`, with the calibration of Cockburn, Gutwin and Greenberg (CHI 2007, mouse, 8 participants, R2 = 0.93): a = 0.37 s, b = 0.13 s/bit (S28, PDF read). Distance D = 400 px, the narrow side taken as W (an assumption of `LAW` 2.1, conservative).

| W | ID = log2(400/W + 1) | MT = 0.37 + 0.13 * ID | Difference from 44 px |
|---|---|---|---|
| 44 px (baseline button) | 3.335 bits | 0.804 s | none |
| 32 px (typed field) | 3.755 bits | 0.858 s | +0.055 s |
| 28 px (control and row, chosen) | 3.934 bits | 0.881 s | +0.078 s |
| 24 px (compact) | 4.143 bits | 0.909 s | +0.105 s |

The layout document reaches the same order: about 0.03 s per 4 px step (`layout-model.md` 3.5). Rows visible in an 800 px column: 44 px gives 18, 32 px gives 25, 28 px gives 28, 24 px gives 33; the gain matters only when the list is longer than the window.

Validity limits: Fitts fits IDs of about 2 to 8 bits; the constants come from one menu-pointing study; the law is one-dimensional pointing and says nothing about keyboard use, visual search or reading. The 0.078 s difference (exactly 0.13 x (3.934 - 3.335) = 0.0779 s; the table's rounded times differ by 0.077) is smaller than one KLM band (plus or minus 21% of a multi-second task, `LAW` 2.4), so it is not evidence either way. It is a cost the design accepts for density; it is not a benefit claim. The approval control is not sized by this model (P2, `LAW` section 3). SLP metric M17 asks primary actions to be at least 32 px; chrome controls are 28 px here, so whether dialog primary buttons use the 32 px field height is a layout decision recorded in section 14.

### 5.2 Layers

```css
@layer legacy, reset, tokens, base, components, overrides;
@import url("/assets/app.css") layer(legacy);
@import url("/assets/tokens.css") layer(tokens);
```

The first line is the first line of the first stylesheet the page loads (the entry sheet, `studio.css`). Exact wiring: `tokens.css` contains no `@layer` of its own; the `layer(tokens)` on the import is the only place the layer is named. A named `@layer` block inside a file imported with `layer(tokens)` would create a nested layer (`tokens.tokens` by the layer-nesting rule; I did not open a source on nesting, so this is reasoning, not a citation), which is why the generator does not write one. `@import` may follow only `@charset` and `@layer` statements (S19). Rules:

| Rule | Reason | Test |
|---|---|---|
| No author CSS outside a layer, except `@layer` statements and `@import ... layer()` in the entry sheet; every other CSS file is reached only through such an import (`@font-face` inside `tokens.css` is therefore inside the `tokens` layer) | "Styles that are not defined in a layer always override styles declared in named and anonymous layers" (S13, per fetch summary). One unlayered rule beats every component | DS-03 |
| `legacy` is the lowest layer | The baseline `app.css` is imported unmodified with `layer(legacy)` (S19). New layers outrank it without specificity fights; the file is deleted when nothing depends on it | DS-03 |
| `overrides` is empty in shipped CSS | Reserved for the gallery and tests | DS-03 |
| One file per concern | `tokens.css`, `reset.css`, `base.css`, one CSS file per component, imported by the entry sheet | DS-13 |
| `reset` is exactly the two rules below and nothing else | Legacy type selectors leak into new components (next paragraph) | DS-03, DS-09 |
| No `!important` in `tokens`, `base`, `components` or `overrides`; the single allowed one is the `[hidden]` rule in `reset` | Important declarations reverse layer order: the first declared layer wins (S13), so an important rule in a low layer cannot be undone by a later layer | DS-03 |

**Legacy leaks into new components.** Scoping new CSS under `[data-ui="next"]` stops new rules reaching legacy markup. It does not stop the reverse: the baseline `app.css` has type selectors (`*`, `body`, `button`, `input`, `textarea`, `select`, `label`, `table`, `th`, `td`, `h2`, `h3`, `details`, `summary`, `header`, `aside`, `main`, `footer`, `pre`) that apply to every element of those types in `@layer legacy`, including the ones a new component renders. A component rule overrides only the properties it names; the rest (for example the legacy button's green background, border radius and `cursor`) survive. The reset layer removes them:

```css
/* reset.css, imported with layer(reset) */
[data-ui="next"] [data-eija-component],
[data-ui="next"] [data-eija-component] * { all: revert; }
[data-ui="next"] [hidden]:not([hidden="until-found"]) { display: none !important; }
```

```css
/* in base.css: inherited properties come from tokens, not from the legacy body */
[data-ui="next"] [data-eija-component] {
  box-sizing: border-box;
  font: var(--text-ui-font-weight) var(--text-ui-font-size) / var(--text-ui-line-height)
    var(--text-ui-font-family);
  letter-spacing: var(--text-ui-letter-spacing);
  color: var(--color-text-primary);
}
```

Why each part (sources opened 2026-09-29):

| Part | Reason | Source |
|---|---|---|
| `all: revert` | In an author style sheet, `revert` rolls a property back to the user or user-agent value, "as if no author-level rules were specified"; this skips every author layer, legacy included. `revert-layer` would only go back to the previous layer, which is `legacy`, so it is not used | S35, S36 |
| Custom properties survive | `all` resets every property except `direction`, `unicode-bidi` and custom properties, so tokens stay readable inside the component | S35 |
| Component roots set font and colour in `base` | Reverting an inherited property falls back to inheritance, so a component still inherits the legacy `body` font (15 px, line height 1.65) and ink colour unless its root sets them (M15) | M15 |
| `box-sizing` in `base` | The legacy `*{box-sizing:border-box}` is reverted by the reset; components that relied on it must set it | M15 |
| `[hidden]` rule, `!important` | Author `display` on an element overrides the `hidden` attribute (S37). Today the legacy `[hidden]{display:none!important}` hides such elements, and because it is important in the first layer it beats every later layer (S13). When `legacy` is deleted at S8, a component that sets `display` on an element it toggles with `hidden` would show it. The reset rule keeps today's behaviour after S8 | S13, S37, M15 |
| `:not([hidden="until-found"])` | Browsers typically render `hidden="until-found"` with `content-visibility: hidden`; `display: none` stops find-in-page from revealing it (S37). The legacy rule has no such exclusion, so until S8 any `until-found` element inside the Studio is hidden by `legacy` and cannot be found. No v1 primitive uses `until-found`; a component that needs it waits for S8 or an HCI-ADR | S37 |

MEASURED (M15, Chromium 151, the Studio's CSP string, 2026-09-29). A component subtree of 14 elements (button, label, input, table, details, summary, h2, pre, a hidden span with component `display: inline-flex`) compared on 18 computed properties with the legacy layer loaded and not loaded. Without the reset: 111 differing property values on all 14 elements (for example the component button kept the legacy green background, 8 px radius and pointer cursor). With the reset and the `base` root rule: 0 differences in type, colour, spacing, border, display or cursor; the only difference left was the width of 5 block elements (1,280 against 1,264 px), caused by the legacy `body{margin:0}` outside the component. The hidden span was `display: none` in both cases. The legacy button kept its 44 px `min-height` in both. No console errors. One browser and one fixture; the test that holds this is DS-09.

MEASURED (M10, Chromium 151, the Studio's CSP string): `@import url() layer(legacy)` loaded the unmodified baseline `app.css`; a legacy button kept 44 px and a new `button.ds` in `@layer components` got 32 px; the console reported no violation. MEASURED (M13, the same CSP plus `font-src 'self'`): the entry sheet above, importing the generator's real `tokens.css` (no inner `@layer`) with `layer(tokens)`, reported the two import rules with `layerName` legacy and tokens; `EIJA Sans` loaded from the `@font-face` inside the layered import (`document.fonts.check` true, status loaded; the font file was the type aspect's rebuilt WOFF2, not a shipped file); `--space-4` resolved to 1rem; a rule in `@layer components` using `var(--space-4)` gave 16 px padding; the console reported no error. One browser and one selector; the precedence rule itself is from S13.

### 5.3 Custom-property tiers

| Tier | What | Who writes it | Example |
|---|---|---|---|
| T1 | Scale and palette values, one per value | generated | `--space-4: 1rem`, `--size-control-compact: var(--size-hit-min)` |
| T2 | Roles that change with theme or density | generated (theme from sibling groups, density from `$extensions.mode`) | `--color-text-primary`, `--density-control-height`, `--density-gutter` |
| T3 | Component-private variables, prefix `--_` | by hand, in the component's rule, assigned from T1 or T2 | `--_row-indent: var(--space-3)` |

A tier exists only where a value changes across it. Spacing has one T2 role, `--density-gutter`; every other gap reads the scale directly. Primer has three token tiers and nine themes; Linear replaced 98 theme variables with 3 inputs (`VIS` 2.5, `DEV` 2.1): the shared lesson is fewer named layers with clear roles, not more. Component tokens are not put in JSON: that would multiply files and tokens for values nothing varies. Test DS-04: a component may read only names the generator emitted and its own `--_` names.

### 5.4 Themes and density

| Axis | Mechanism | MEASURED (M10, Chromium 151) |
|---|---|---|
| Theme | As the colour aspect specifies, with one change: `:root` holds the light values; a `prefers-color-scheme: dark` block on `:root:not([data-theme="light"])` and `:root[data-theme="dark"]` hold the dark values; hex values. `color-scheme` is written on `:root[data-ui="next"]` (and its `[data-theme]` variants) until S8, then on `:root`. Custom properties are inert for the legacy CSS, which reads none of them; `color-scheme` is not inert | M12, unmodified legacy `index.html` and `app.css`, 174 elements, 1280 x 720: under emulated dark, a global `:root{color-scheme: light dark}` changed the full-page screenshot hash and 895 computed values (color, background, border, outline, caret, `color-scheme`) on 86 elements; the scoped form changed 0 values and the screenshot hash was identical. Under emulated light the global form changed only the `color-scheme` value itself (174 values) and the screenshot was identical. The `light-dark()` alternative resolved to the dark value under an emulated dark scheme with no extra rule (M10). |
| Density | Compact values live in `[data-density="compact"]`; custom properties inherit, so any region can be compact | A button in a compact region measured 24 px, in the root 32 px (spike values, not the final density tokens). |
| Interactive chips | `--density-chip-height` (24 / 20 px) is for non-interactive chips only. An interactive chip (a filter, a removable term) reads `--size-chip-default` (24 px in both densities), which is the floor. No separate density token: a value that does not change across modes is not a T2 role (5.3) | DS-04 fails a component whose manifest entry is interactive and whose CSS reads `--density-chip-height`; DS-07 checks the rendered height |
| Inset next to a seam | `--density-gutter` (12 / 8 px) is the general pane gutter. Content on either side of a seam is inset with `--space-3` (12 px) from the seam centre line in both densities, because the layout aspect's seam relies on the SC 2.5.8 spacing exception: a 24 px circle on the seam's 8 px hit area must meet no other target (`layout-model.md` section 3.4, seam hit-area note; S21). The compact 8 px gutter is therefore not used next to a seam. No separate token, for the same reason as chips | DS-07 runs the 24 px circle test on every seam in both densities |
| Nested theme region | Not supported in v1 (the colour aspect defines root-level themes). A region with its own theme would have to re-apply `background` and `color`, because `color` inherits as a computed value | A `data-theme="dark"` div under a light page kept the light text colour until the rule was re-applied (with the `light-dark()` form). |

Bytes (M8). The three-block output for 71 roles is 14,538 B with the `color-scheme` rules (14,461 B in the first version). One `light-dark()` per role measured 10,302 B against 14,386 B in the first version of the generator, about 4,100 B or 28% smaller raw (gzip difference is small: 2,221 against 2,085 B); those two figures were not re-measured after the wrapping and scoping changes. The colour aspect declined to rely on `light-dark()` because MDN lists it as newly available since May 2024 (S18). Baseline calls a feature widely available 30 months after it became newly available (S31), so `light-dark()` reaches that status about November 2026 (MDN gives the month, not the day); the colour aspect's stated reason lapses then, and the question goes back to it (revisit list in the ADR). The reference generator no longer carries the `light-dark()` option; the first version did.

## 6. Bundle and performance budgets

### 6.1 What the budget is for

On this hardware bytes barely move load time (6.2), so the byte budgets exist for two other reasons: the client ships unminified and is meant to stay small and inspectable (ADR-013), and every file under `resources/web` enters the implementation fingerprint (11.1) and the `/assets` allowlist. The load budget is the user-visible one.

### 6.2 Model (PREDICTION)

Form: `T = a + w * RTT + s * KB`, with `w` the number of sequential request waves, `RTT` the per-request cost, `KB` the bytes in thousands.

Inputs (M2, M7). RTT = 2.17 ms (p50, keep-alive `app.js`). Two real graphs loaded into a blank page under the Studio's CSP through uvicorn, fresh context each time, n = 20:

| Graph | Bytes | Waves | p50 | p95 |
|---|---|---|---|---|
| Lit 3.3.3, five deduplicated jsDelivr modules | 17,639 | 3 | 33.8 ms | 53.1 ms |
| `axe.min.js` 4.13.0, one file | 580,491 | 1 | 82.7 ms | 202.3 ms |

Solving the two equations: `82.7 - 33.8 = 2.17 * (1 - 3) + s * (580.49 - 17.64)` gives `s = 53.24 / 562.85 = 0.0946 ms/KB`, and `a = 82.7 - 2.17 - 0.0946 * 580.49 = 25.6 ms`. Check on the Lit graph: `25.6 + 6.51 + 1.67 = 33.8`. A note on method: the first attempt used Python's `http.server`, which gave 188.6 ms for the same Lit graph; that was the test server's connection handling, not the graph. The numbers above use uvicorn, the Studio's server.

Prediction of cold-load ready p95 (baseline 159.1 ms, 17.7 KB of JS and CSS). The additional time is `s * (KB - 17.7) + 2.17 * extra waves`, plus `a` if the 25.6 ms module overhead applies to a module graph loaded from HTML (unknown, so both ends are shown):

| Client | KB | Extra waves | Added time without / with a | Ready p95 |
|---|---|---|---|---|
| Baseline | 17.7 | 0 | 0 | 159.1 ms (MEASURED) |
| Budget (JS 120 + CSS 40) | 160 | 2 (depth 3) | 17.8 / 43.4 ms | 176.9 to 202.5 ms |
| Lit graph added to the baseline | 35.3 | 2 | 6.0 / 31.6 ms | 165.1 to 190.7 ms |
| Web Awesome tree, tree-item, dialog, button closure (M9) added to the baseline | 277.7 | 5 | 35.4 / 61.0 ms | 194.5 to 220.2 ms |

Result. The 160 KB figure was set at the size where the upper end of the range meets the 200 ms target, so the prediction straddles the target: **the decision flips inside the range**, and the budget is a hypothesis that DS-14 must measure on real code. Validity limits: two data points, n = 20 each, so the fit has zero degrees of freedom; a slope and intercept fitted on two p50 values are added to a p95 baseline, which assumes the increment is the same at every percentile (untested); the two points mix a classic 580 KB minified script (axe) with a 5-file ES-module graph (Lit), so parse and execute cost is confounded with transfer cost in `s`; machine loaded by other agents, headless Chromium, minified third-party code as the source of the byte cost (unminified source may differ), no execution or layout cost of real components, fonts excluded. A third point (for example a 100 KB module graph) would separate the two effects; until then 160 KB is a placeholder. Nothing here says users will notice any of it: 200 ms is our target and 1,000 ms is the Nielsen limit for keeping the flow of thought (S27).

### 6.3 Generated `tokens.css` (MEASURED, M8)

For the five real token files and `fonts.lock.json` (M8, `gen5.py`): 243 tokens read, 16,087 B: 14,538 B of custom properties (325 declarations across the light, dark, dark-attribute and compact blocks) and `color-scheme` rules, and 1,549 B of `@font-face`; 379 lines, 0 over 100 characters; gzip 2,653 B. The first version wrote 15,974 B and 5 lines over 100 characters (audit finding); wrapping them cost 113 B. This replaces the 3 to 6 KB guess I made before the colour and type files existed; the 12,000 B budget in my first draft would have failed. The budget is 18,000 B, which leaves 11.9% over the measured size.

### 6.4 Budget table

All values are tokens in `index.tokens.json` (`bundle.*`, `load.*`) and are DESIGN_TARGET hypotheses.

| Budget | Value | Derivation | Test |
|---|---|---|---|
| JS at first render, all modules | 120,000 B | 160 KB total minus CSS; includes `canvas.js`, ESTIMATED by the canvas aspect at 25 to 45 KB (no source) | DS-13 |
| CSS at first render | 40,000 B | includes `tokens.css` (16,087 B), the legacy layer (7,156 B) while it exists, base and component files | DS-13 |
| `tokens.css` | 18,000 B | 6.3 | DS-13 |
| One JS or CSS file | 24,000 B | reviewability of one file; not derived | DS-13 |
| Line length | 100 characters, generated files included (the generator wraps after commas) | baseline lines of 1,585, 7,155 and 1,446 characters (3) | DS-12 |
| Requests before first API call | 30 | about 15 JS files (120,000 B at about 8,000 B), 6 CSS files, 1 HTML file, 3 fonts is 25, plus 20% margin; each about 2.2 ms (RTT above); the limit protects the allowlist, and time is governed by depth | DS-13 |
| Import depth | 3 | each level is one request wave | DS-13 |
| WOFF2 for first paint | 100,000 B | type aspect ceiling; shipped 40,904 B in 3 files (`fonts.lock.json`) | DS-13 |
| Ready p95, cold load | 200 ms warn, 1,000 ms fail | motion `budget.view` target; Nielsen 1 s (S27) | DS-14 |

Not budgeted here: interaction latency and frame time (ADR-0066 owns them).

## 7. Component technology

### 7.1 Options and measurements

All spikes ran in `.tmp/dsa/spike` with the Studio's exact CSP header, in Chromium 151 (M3, M4, M5, M9).

| Option | What it is and who does it | Measured | Drawbacks | Verdict |
|---|---|---|---|---|
| A: baseline | One `app.js` of builder helpers and ids | 10,561 B, 50 ids coupled to `index.html`, one `render()` rebuilding all views | No component boundary; a change to one view is a change to line 18 | Rejected as the end state |
| B: native elements plus vanilla ES-module builders (chosen) | `create(props)` returns a DOM element; text through `textContent`; state in `data-*`; ARIA per APG (S25) | Light-DOM custom element and plain DOM styled by global layers: no violation. `<dialog>` `showModal()` and the `popover` attribute: no violation, `:modal` and `:popover-open` matched. Relative-path modules are the only kind the CSP allows (M4) | We write and test the tree, palette, menu, seam and tabs keyboard code ourselves | **Chosen** |
| C: hand-written shadow-DOM custom elements | Web components with `attachShadow` | `adoptedStyleSheets` (Baseline widely available since March 2023, S16): applied, no violation. `<link rel=stylesheet>` inside the shadow root: applied, no violation. A `<style>` element inside the shadow root: blocked (`style-src-elem`). **axe 4.13.0 reported a critical `label` violation** for an `<input>` inside a shadow root labelled by a `<label for>` in the light DOM; the same markup in the light DOM passed | Ids do not resolve across a shadow boundary, so `label for`, `aria-labelledby` and `aria-controls` break unless every pair lives in one root; global layers do not reach inside, so styles are adopted per root; the slop-budget script needs a shadow-piercing walker (`SLP` section 6) | Not in v1 |
| D: Lit 3.3.3 (BSD-3-Clause, S8) | Reactive web components; `static styles = css`; `html` templates | The vendored closure worked with no violation and applied its styles. The jsDelivr `+esm` closure was 7 files with two copies of `lit-html` (3.3.1 and 3.3.2) and of `@lit/reactive-element` (2.1.1 and 2.1.2); deduplicated by hand it is 5 files, 17,639 B. The npm package itself is multi-file ESM whose `index.js` imports `@lit/reactive-element`, `lit-html` and `lit-element/lit-element.js` by bare specifier (tarball, S5) | No official single-file no-build artefact; vendoring depends on a third party's re-bundling and needs manual deduplication; shadow DOM by default; ADR-013 amendment | Not in v1 |
| E: Zag.js 1.44.0 machines (MIT) | Framework-agnostic state machines with a vanilla adapter | `@zag-js/tree-view` imports 6 bare-specifier packages and `@zag-js/vanilla` imports 4 (tarballs, S12). Import maps must be inline (S17), and an inline import map is blocked by the CSP (M4), so bare specifiers fail: `Failed to resolve module specifier` | Needs a bundler | Reference for keyboard and state design only |
| F: Web Awesome 3.14.0 (MIT, S9 to S11) | Lit-based component library | Unpacked 17,507,552 B. The closure of `tree`, `tree-item`, `dialog` and `button` in `dist-cdn` is 65 files, 260,061 B, import depth 6 (M9). Issue 1937 (four components wrote inline `style` attributes) was closed on 2026-02-03 by a merged pull request that switched to `styleMap` | 260 KB for four components exceeds the whole-client budget; the `/assets/{name}` route serves one path segment while the closure is nested; every file joins the implementation fingerprint; shadow-DOM labelling as in C; its theme is not our tokens; its status marks, tree with status glyphs and palette do not exist, so most of our components stay custom | Not in v1 |
| G: Preact 10.29.8 (MIT, S33), vendored as single files | Runtime virtual-DOM library, no build step; elements from `h()` calls | `dist/preact.module.js` is 11,693 B with no imports; `hooks/dist/hooks.module.js` is 3,647 B and imports the bare specifier `"preact"`, so one line must be changed to a relative path. Spike (M14): a three-row tree with `useState`, an `onClick` handler and a `style` object rendered under the Studio's CSP in Chromium 151 with no violation, in the light DOM; the click updated the row text | The vendored source contains `innerHTML` (3 occurrences) and `cssText` (2) for its `dangerouslySetInnerHTML` and string-style paths, so DS-12 and a scan of a concatenated `app.js` (F1) would flag it unless that file is exempted or edited (an edit loses upgradability); a second programming model (re-render and diff) beside APG keyboard and focus code; its maintenance cost against hand-written builders was not measured; `htm` and JSX not evaluated | Not in v1; the recorded fallback |

Correction to the research record. `developer-tool-craft-benchmarks.md` says the Web Awesome CSP issue was "still open when read". It is closed, with the fix merged on 2026-02-02 (S9, S10). This changes the reason for not adopting it: the CSP blocker is gone; size, routing, fingerprint and shadow-DOM labelling remain.

Closes an open item elsewhere. `content-and-onboarding.md` A7 and Q5 list "`popover` under the strict CSP" as untested. In Chromium 151 a `popovertarget` button opened a `popover` element (`:popover-open` matched) with no violation under the Studio's CSP (M3). Firefox and Safari are not tested.

ADR-013 ("no build-time framework dependency") does not by itself exclude a vendored runtime library such as G; the first draft did not say so. G is not chosen because of the DS-12 conflict, one more third-party file in the implementation fingerprint and `/assets` allowlist, and two programming models; none of these is a measured cost, so the choice between B and G is a judgement. Revisit G when three or more components need `update()` logic that diffs children (the trigger in the ADR).

Arguments against the choice. Custom components cost maintenance: keyboard handling, hit testing and screen-reader behaviour become ours (`DGM` says the same for the canvas and does not estimate the cost). Web Awesome and Lit have wider browser and assistive-technology exposure than our code will. The choice rests on the measured constraints in this repository, not on those libraries being poor.

### 7.2 Component contract

| Rule | Reason |
|---|---|
| One module per primitive, flat file names, relative imports only (`./status-mark.js`) | `/assets/{name}` takes one segment; import maps are blocked (M4) |
| Export `create(props) -> Element` and, where state changes, `update(el, props)`; keyboard behaviour attached inside `create` | one way to build and test any component |
| Text only through `textContent` or `Text` nodes; SVG through `createElementNS`; no `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`, `setAttribute("style", ...)`, `.cssText =` | ADR-013 and the CSP; DS-12 extends the existing two-string test |
| State is `data-eija-state`; variants are `data-variant`; every component root carries `data-eija-component="<id>"` | styling API for the layers, and the gallery can find every instance |
| Every string a component renders carries `data-eija-source` (chrome, model, ai, provider, user); model text sits under `data-eija-model` | the hooks the slop-budget metrics and the content lint need (`SLP` M12, M13, M21; ADR-0065 D7) |
| Roles and names come from the APG pattern named in the inventory; the closed catalogue is tree, tabs, dialog, combobox, toolbar, menu button, disclosure, window splitter (ADR-0067 D2, layout D6) | a11y contract |
| A component reads only tokens the generator emitted and its own `--_` variables | DS-04 |
| No custom elements and no shadow DOM in v1 | 7.1 |

Autonomous light-DOM custom elements passed the CSP test too (option B row). They are allowed by a later ADR if a component needs per-instance lifecycle that builders cannot give. Revisit when three or more components need cleanup that leaks in tests.

### 7.3 Serving modules until I-SEC1 lands

Other lanes' documents assume the client stays in `app.js` and `app.css`; today `/assets/{name}` serves exactly those two. Three fallbacks keep this design usable:

| Fallback | How | Cost |
|---|---|---|
| F1 | A stdlib script assembles `app.js` from module sources and writes it, committed and byte-compared, exactly like `tokens.css`; DS-13 budgets apply to the sources | one more generated file; two places to read the code |
| F1c | A stdlib script writes `app.css` as the layer-order line, `@layer legacy { <legacy source verbatim> }`, `@layer tokens { <tokens content> }` and the later layers (an `@import` inside a layer block is not valid, so everything is inlined). The legacy source moves outside `resources/web` (for example `quality/legacy/app.css`; it has no `@import` or `@charset`, checked). Committed and byte-compared like `tokens.css` | fonts cannot be served (only two files are), so no custom fonts until I-SEC1 and I-SEC2; one more generated file; the legacy bytes are unchanged but sit inside a block |
| F2 | Hand-maintained single `app.js` with section markers; per-section byte budgets | the file-size budget loses meaning; reviewers see one large file |

F1 is preferred because it keeps the source in reviewable modules and the shipped file inspectable. None is needed once the allowlist admits flat module names. S1 is blocked for fonts and for separate files until I-SEC1 to I-SEC3 are accepted; S1 without fonts can ship with F1 and F1c (11.3).

## 8. Component inventory

Source of truth: `index.tokens.json`, `$extensions.io.github.45ck.eija-studio.components`. Task ids are T01 to T14 of `design/brief.json`.

### 8.1 Primitives (15)

| Primitive | Class | Base | Pattern | Tasks served (of 14) | Named states | JS |
|---|---|---|---|---|---|---|
| button | native | `button` | APG button | 11 | 8 | no |
| field | native | `input`, `select`, `textarea`, `label` | native | 6 | 8 | no |
| table | native | `table` | native | 8 | 5 | no |
| disclosure | native | `details`, or a button with `aria-expanded` in a row | APG disclosure | 5 | 3 | yes |
| progress | native | `progress` | native | 2 | 3 | no |
| popover | native | `popovertarget` button and `popover` element | Popover API, Baseline 2025 (S15); term definitions and reasons | 4 | 3 | no |
| status-mark | mark | span, inline SVG glyph, word | text plus shape (WCAG 1.4.1) | 14 | 11 | yes |
| rollup | mark | `role=toolbar` of count buttons | APG toolbar; counts by state, never a percentage alone | 5 | 4 | yes |
| tree | behaviour | `ul role=tree` | APG tree (S25) | 5 | 7 | yes |
| dialog | behaviour | `dialog` with `showModal()`; palette is a combobox inside | native dialog (S14); APG combobox | 2 | 5 | yes |
| tabs | behaviour | `role=tablist` | APG tabs | 4 | 4 | yes |
| menu | behaviour | button with `aria-haspopup`, `role=menu` | APG menu button | 2 | 4 | yes |
| seam | behaviour | `role=separator` | APG window splitter | 2 | 4 | yes |
| notice | behaviour | `role=status` or `role=alert` | WCAG 4.1.3 | 5 | 3 | yes |
| canvas-node | behaviour | SVG group | canvas aspect | 2 | 6 | yes |

Totals (computed from the manifest by script): 15 primitives, 78 named states, 10 with script. Every one of the 14 tasks is served by 3 to 8 primitives; the smallest task coverage of a primitive is 2 (progress, dialog, menu, seam, canvas-node). The seam is a dragging control, so it needs a non-dragging path (WCAG 2.5.7, V6); the layout aspect provides keys and palette commands for it (layout D6).

### 8.2 Recipes (8)

A recipe composes primitives and adds layout classes only. It has no colour, type or state CSS.

| Recipe | Made of | Tasks |
|---|---|---|
| review-chapter | table, status-mark, disclosure | T02, T11 |
| ripple-lane | rollup, table, tabs | T03, T14 |
| coverage-row (claim, covered, assumed, NOT covered) | table, status-mark | T06, T14 |
| trace-table | table, button | T07 |
| decision-surface | dialog, rollup, field, button | T08 |
| job-row | status-mark, progress, button | T06, T13 |
| proposal-row | status-mark, disclosure, button | T01, T13 |
| concept-code-table | table, status-mark | T12 |

### 8.3 Why it is small

Rules (hypotheses): a primitive serves at least 2 top tasks (DS-15 recomputes this from the manifest); native elements first; a state is named only if the gallery renders it. Not built in v1, each with a reason:

| Not built | Reason | Comes back through |
|---|---|---|
| Tooltip | The content aspect bans it for essential information (content-and-onboarding.md, "Tooltip: none"); reasons and definitions use `popover` and level-0 text | none planned |
| Toast | A `notice` region replaces it; the AI aspect says no toast takes focus | none planned |
| Popover positioning by anchor | CSS anchor positioning: the MDN page read shows no Baseline data, so UNVERIFIED (S20). The `popover` primitive itself is in; without anchoring it uses the user-agent placement, and JavaScript placement through CSSOM `style` writes is allowed by the CSP (M3) | an ADR after Baseline status is verified |
| Icon set | Generic glyphs from Lucide (ISC), status and model glyphs drawn in-house on the same grid, per `VIS` 2.10; the choice belongs to the iconography aspect | iconography ADR |
| OSS splitter | The layout aspect lists OSS splitters as not evaluated (O7). This aspect did not evaluate them either: UNVERIFIED. ADR-0016 needs that check and a REGISTER row before `seam` is written | layout aspect |

The count is not compared with other systems: no source I opened gives a comparable count for a comparable product, and Web Awesome's "50+ components" (`DEV`) is a library, not a tool.

## 9. Component gallery

**What it is.** A static site under `reports/gallery/` (gitignored, not shipped, not under `resources/web`), generated by `quality/gallery/build_gallery.py` from the inventory and from fixtures in `quality/gallery/fixtures/`. One page per primitive; `?theme=dark&density=compact` selects a mode. It loads the real `resources/web` files, not copies, through the same entry sheet as the Studio, so the `legacy` layer is present in the gallery exactly as in the app until S8; DS-09 also renders every state without it to prove the reset holds (5.2). A small local server serves it with the Studio's exact CSP string (I-SEC3), so a component that needs an inline style fails in the gallery.

**Content rules.**

| Rule | Reason |
|---|---|
| Fixture text is the excursion workflow: states Draft, Submitted, Recommended, Approved, Rejected; actions Submit, Recommend, Approve, Reject, Revise; the kernel's status words; values from `examples/excursion-candidate.json` | rubric: no placeholder or lorem data |
| Every named state in the manifest has a fixture; a state without one is listed as NOT_RUN | Storybook lists untested states in a coverage widget (`MOK` 2.9); here the gap uses the product's own vocabulary |
| The gallery's summary page shows counts by status per check (PASS, FAIL, NOT_RUN, UNKNOWN) and never one percentage | P1 applied to the design system |
| Each page shows the component's token reads (from DS-04) | design and code stay one thing |

**Size (PREDICTION).** 78 states x 2 themes x 2 densities = 312 renders. Per render on a tiny DOM (M5, n = 35, p50): attribute switch 3.3 ms, `axe.run` 24.7 ms, `aria_snapshot` 12.0 ms, style and geometry dump 4.8 ms, together 44.8 ms. So the browser tier takes about `312 * 44.8 = 14.0 s` of checks plus browser start-up. Real component DOM is larger; axe cost grows with nodes, so allow up to three times, about 42 s. Both are PREDICTIONS from a 20-node page; DS-07 to DS-09 belong to the `full` tier, not `fast`.

## 10. Testing: visual regression, axe, static checks

### 10.1 What the evidence says

| Finding | Value | Source |
|---|---|---|
| Playwright for Python has no screenshot-comparison assertion; its page assertions are title, url and `to_match_aria_snapshot` | per fetch summary of the API page | S24 |
| Screenshot output varies with OS, version, hardware, power source and headless mode; keep baselines from the same environment; names carry platform and browser | per fetch summary | S23 |
| Pixel determinism on this machine | 18 screenshots (3 launches x 6 fresh contexts) of the same page gave 1 distinct SHA-256 (M6) | MEASURED |
| `aria_snapshot` and `to_match_aria_snapshot` work in Playwright 1.58.0 against a CSP page | passed on a tree fixture (M5) | MEASURED |
| axe-core disables `target-size` by default: 3 adjacent 16 px buttons gave 0 violations with default rules and 1 rule with 3 nodes once enabled | axe 4.13.0 (M5); the wheel's bundled 4.12.1 carries `id:"target-size"`, `enabled:!1`, `minSize:24` | MEASURED; S22 |
| axe alone is not enough: on the baseline it found 1 of 5 known failures | `accessibility.md` B1 (measured there) | repository |
| `wait_for_function` with a string predicate raised an `EvalError` under `script-src 'self'` in this browser; `evaluate` with an expression string worked | M3 harness note | MEASURED |
| `axe-playwright-python` 0.1.8 requires `playwright >= 1.36.0` and bundles axe-core 4.12.1; its PyPI metadata has no licence field, and the MIT licence rests on my reading of the wheel's `LICENSE` file | wheel metadata (M5, S29) | MEASURED |
| Hosted visual-review services need upload and CI; GitHub Actions is unavailable for these repositories (owner note, 2026-09-27) | repository policy | not adopted |

### 10.2 Tests

| Id | Test | Tier | Pass criterion (fixed before running) |
|---|---|---|---|
| DS-01 | `tokens.css` equals regeneration | fast | byte-equal |
| DS-02 | Generator refuses bad input | fast | all 15 negative fixtures (4.2) raise `ValueError` with the named reason (a `KeyError` or other accidental exception fails the test); a number such as 1.428571 is written unchanged; no generated line exceeds 100 characters |
| DS-03 | Layers | fast, static | the entry sheet holds only the `@layer` order line and `@import ... layer()` rules; every other shipped CSS file is imported that way and nothing else loads it; `tokens.css` contains no `@layer`; every selector in `reset`, `base` and `components` starts with `[data-ui="next"]` until S8; `reset.css` equals the two rules in 5.2; 0 `!important` in shipped CSS outside `reset.css` and the unmodified legacy file (the legacy file's one, `[hidden]{display:none!important}`, is listed as known); `overrides` empty |
| DS-04 | Token references | fast, static | every `var(--x)` in component CSS is an emitted token or a `--_` name declared in the same rule; no palette (T1 colour) names in `components`; a component whose manifest entry is interactive does not read `--density-chip-height` (interactive chips read `--size-chip-default`, 5.4) |
| DS-05 | Spacing scale | fast, static | every padding, margin or gap length in shipped CSS is `0` or `var(--space-*)`; 0 px literals |
| DS-06 | Mode contract and colour agreement | fast | default and compact groups have equal key sets; every colour role has a light and a dark value; every hex equals its OKLCH components within 1 unit per 8-bit channel |
| DS-07 | Target size and text spacing | full | computed `min(width, height)` at least 24 px for every interactive element in every gallery state, both densities; the seam is the only element allowed the SC 2.5.8 spacing exception (`data-eija-exempt="spacing"`), and for it a 24 px circle on its centre meets no other target in both densities (content next to a seam is inset `--space-3` from its centre line, 5.4); a link inside running text may use the SC 2.5.8 Inline exception (`data-eija-exempt="inline"`, allowed only on an `a` element whose nearest block ancestor also contains non-link text nodes, checked by the test), because term and source links in prose would otherwise fail or need padding that breaks line spacing (S21); with the SC 1.4.12 overrides applied (line height 1.5, paragraph spacing 2, letter spacing 0.12, word spacing 0.16, in units of the font size; S30) no text is clipped (`scrollWidth` at most `clientWidth`) |
| DS-08 | axe | full | 0 violations across `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`, `best-practice` with `target-size` enabled, for every state x theme x density; every `incomplete` result needs a written triage, otherwise the state is UNKNOWN, never pass (same criterion as ADR-0067) |
| DS-09 | Structural snapshots | full | `to_match_aria_snapshot` per state; computed style and geometry JSON per state, geometry tolerance 1 px, snapshots named by platform and browser. Legacy isolation (S1 to S7): each gallery state rendered with and without the `legacy` layer gives equal computed-style JSON for the component subtree (geometry compared relative to the component root, because the page body's margin comes from the legacy file), as M15 measured on one fixture; a toggled `hidden` element is `display: none` in both. Legacy invariance (S1 to S7): the unmodified legacy views, without `?ui=next`, have computed-style JSON and a screenshot hash equal to the pre-S1 record under emulated light and emulated dark (M12 shows a global `color-scheme` fails this in dark) |
| DS-10 | Pixel snapshots | release, advisory | on the reference platform, byte-equal to the committed PNG (M6 measured 0 variation there); on other platforms not run |
| DS-11 | CSP smoke | full | zero `securitypolicyviolation` events and zero CSP console errors while all gallery pages load; CSP string imported, not copied |
| DS-12 | Source rules | fast, static | no forbidden API (7.2) in shipped JS (a vendored third-party file needs its own ADR and an exemption listed by path); no line over 100 characters in JS, CSS, HTML, generated files included |
| DS-13 | Bundle budget | fast, static | bytes, requests and import depth within `bundle.*` |
| DS-14 | Load probe | full | one Chromium, at least 30 cold loads, ready p95 at most 200 ms (warn) and 1,000 ms (fail) |
| DS-15 | Inventory integrity | fast | every `data-eija-component` in shipped code is in the manifest and vice versa; every primitive has at least 2 tasks; every state has a fixture or is listed NOT_RUN; every rendered string has `data-eija-source` |
| DS-16 | Governance | fast | see section 12 |

Harness rules. Use `evaluate`, locators and polling, not `wait_for_function` with strings, against pages served with the real CSP. Do not use `bypass_csp` for DS-11. Enable axe `target-size` explicitly. One browser process at a time (`AGENTS.md`; 16 GB machine).

Pixel snapshots are advisory because the only evidence of determinism is one machine. If a second platform shows differences, they stay advisory; the structural snapshots are the gate.

## 11. Migration: strangler plan

Pattern. Fowler describes a strangler fig application as new behaviour built beside the old system and the old one replaced piece by piece, and notes that teams often resist the transitional architecture (S26). Here the transitional architecture is small: a cascade layer, a scope attribute and a URL flag.

### 11.1 Constraint that shapes the schedule

`adapters/identity.py` computes `implementation_files()` from every `*.py` under the package and every file under `resources/web` (`rglob("*")`). `domain/evidence.py` returns STALE for a receipt when any of `semantic`, `implementation`, `policy`, `environment`, `harness` differs. `trusted_build.json` lists exactly the three web files. So (M11):

| Change | Effect |
|---|---|
| Edit any file under `resources/web` | new implementation fingerprint; stored technical receipts become STALE; the release fixture is untrusted (`SOURCE_REVIEW_REQUIRED`) until the owner stamps (`AGENTS.md`: agents never stamp) |
| Add a file under `resources/web` (`tokens.css`, a font, a module) | same effect (what-if computed in memory: the equality with the trusted manifest fails) |
| Change `scripts/`, `tests/`, `quality/`, `design/`, `docs/` | no effect on the fingerprint |

In this worktree `trusted_fixture` is already false (26 files hashed and 26 trusted, but not equal), so the state should be read as "needs stamping" already. Consequence: phases that touch `resources/web` are batched into releases, each followed by one verification run and one owner stamp, and the phases that add no browser file ship first. A kernel ADR that hashes browser assets as their own dimension (I-KERN1) would remove the coupling; it is not proposed here.

### 11.2 Mechanism

| Element | Choice |
|---|---|
| Coexistence | Legacy CSS stays byte-identical in `@layer legacy` (5.2). New views mount in the same page. |
| Scope | New `base` and `components` CSS is written under `[data-ui="next"]`, set on `<html>` by the flag (not on `body`, so that `color-scheme` can be scoped to the same attribute, 5.4), so restyling native controls does not leak into legacy views while the flag is off. With the flag on, legacy views are still on the page; that is a preview state until S8 and DS-09's legacy invariance is checked with the flag off. The scope is removed at S8, and `color-scheme` moves to `:root`. |
| Switch | `?ui=next` on the launch link enables new views per phase; the default stays legacy until S8. The flag is read by JavaScript; no server route is added. |
| API | Old and new views call the same `/api` routes with the same payloads. No new endpoint is introduced by the design system. |
| Authority | The approve and apply request keeps `subject_hash` and `acknowledge_unknowns` exactly as `Approval` in `http.py` requires. |

### 11.3 Phases

| Phase | Adds | Replaces | Exit gates (fixed in advance) | Touches `resources/web` |
|---|---|---|---|---|
| S0 | tokens, generator, tests, gallery, this manifest | nothing | DS-01, DS-02, DS-05, DS-06 on fixtures; baseline numbers in section 3 recorded | no |
| S1 | `tokens.css`, `studio.css` with the `@layer` order and two `@import ... layer()` rules; fonts only after I-SEC1 to I-SEC3 (otherwise F1, F1c and no fonts) | nothing visible | DS-03; DS-09 legacy invariance in light and dark; DS-13 within budget; DS-14 p95 at most 200 ms (the baseline is 159 ms) | yes |
| S2 | status-mark, rollup, notice | `.evidence-card` grid and the notice line on the Evidence tab | DS-04, DS-08, DS-11; the rendered UNKNOWN count equals the model's (SLP M21) | yes |
| S3 | tree, tabs, seam, popover, selection bus, ripple-lane | tabs 01 to 03 in stages, Impact first | DS-07; the tree passes its APG keyboard table; chrome words at most 120 (SLP M1) | yes |
| S4 | review-chapter, menu (needs kernel typed operations, interface A3 of `ai-interaction.md`) | the line and JSON dump in Impact | DS-09; hidden-edit counter present | yes |
| S5 | canvas-node and `canvas.js` | `.state-flow` cards and the numeric layout fields | canvas frame budgets (ADR-0066); every drag has a non-drag path | yes |
| S6 | palette (dialog and combobox) | nothing (new) | no approve or apply command registered (P2); DS-08 | yes |
| S7 | decision-surface | the legacy approve and apply buttons | DS-08; the study's rubber-stamp arm protocol exists; the legacy path is kept until this passes | yes |
| S8 | delete `legacy` layer, `app.js`, old ids, the `[data-ui]` scope | all legacy | 0 bytes left in `legacy`; DS-13 | yes |

Rollback per phase: remove the flag and delete the phase's module; the legacy layer still styles the page. A phase that breaks a gate is reverted, not patched forward.

Order rationale. S2 first because status marks carry invariants P1 and P6 and are stateless; S7 last because approval is the highest authority risk and the legacy path already satisfies it. This order is a judgement; the study can reorder it.

## 12. Governance

### 12.1 Rule

Any change to what a user sees or operates needs an HCI-ADR. It is met by citing an accepted ADR that authorises the class of change, not by writing a new ADR per commit.

| UI change | Authorised by | Needs a new or superseding ADR when |
|---|---|---|
| A token value | the aspect ADR that owns the file (spacing and index: 0068; motion: 0066; colour: 0059; type: 0060) | the change is outside the value's stated range or breaks a budget |
| A new component, variant or named state; removing one | 0068 plus the aspect ADR that specifies it | always, because the inventory changes |
| A budget number | 0068 | always |
| Chrome copy | the content ADR (0065) and its vocabulary lint | the word budget or the copy rules change |
| A layout or interaction change | the layout (0058) or interaction ADR | always for a new pattern |
| Regeneration of `tokens.css` from unchanged tokens | exempt: DS-01 shows byte-equal | never |
| A revert of a change | exempt | never |

There are no other exemptions.

Supersession is per decision. HCI-ADR-0068 bundles ten decisions (D1 to D10). A later record may supersede one of them (for example a budget number, D7) and name it by id; the other nine stay in force, and the later record links back. The first draft bundled the ten decisions in one file because they share one measurement environment and one migration order; splitting the budgets and governance into their own records was considered and not done, to save numbers from a block that the audit and 12.3 both call scarce. The owner may still split them.

### 12.2 Mechanism

| Item | Rule |
|---|---|
| Trailer | Commits that touch `src/eija_studio/resources/web/`, `design/tokens/`, `design/fonts.lock.json` or `quality/gallery/` carry `HCI-ADR: 00NN` (one or more ids), or `HCI-ADR: exempt regenerate` or `exempt revert` |
| Check | `scripts/check_hci_governance.py` (proposed) runs in `nox -t fast` and in the noslop pre-commit hook (ADR-0017): the id exists in `docs/adr/`, the file is an HCI-ADR, and its status is proposed (allowed on a lane branch) or accepted (required to merge to `main`) |
| Acceptance | Only the owner moves an ADR to accepted. An agent may draft, and may not accept, approve or apply: the same authority rule as the product (I1, I4) |
| No bypass | `--no-verify` is blocked by noslop (ADR-0017); hosted CI is unavailable, so the local gate is the gate |
| Audit | The check writes `reports/governance.json` listing each UI commit and its ADR |

### 12.3 Capacity of the number block (PREDICTION)

The HCI block is 0057 to 0088: 32 numbers. On 2026-09-29 the tree holds HCI ADR files for 0057 to 0068 (12 numbers). `SYNTHESIS` section 8 lists 18 candidate topics; demand is about 18 to 21 numbers, leaving 11 to 14 for supersessions. Because a record is never rewritten after acceptance, each change to an accepted decision consumes a number. If the class table above is applied strictly, the spare numbers may run out; the integrator should reserve a second block before the block is 80% used (26 numbers).

## 13. Validation plan

| Item | What | Pass criterion |
|---|---|---|
| Prototype measurements | DS-01 to DS-16 on a first implementation of S0 to S2, one Chromium, 1440x900 and 1280x720 | all thresholds in section 10.2 |
| Load budget | DS-14 on the real client at S1 and after every phase | p95 at most 200 ms warn, 1,000 ms fail |
| Fitts cost | measured pointing time for the default and compact heights on the reference PC | not a gate; recorded beside the PREDICTION |
| Contributor study (formative) | 5 contributors, 3 tasks (add a spacing token; add a named state to status-mark; add a variant to button), recording time, failed gates and questions asked | findings only; no benefit claim; about 5 participants finds problems but does not estimate prevalence (`LAW` 2.10) |
| End-user study | the within-subject study in `SYNTHESIS` section 8; this aspect contributes the first-impression arm at 50 ms and 500 ms and the SUS, SEQ and Raw TLX measures | protocol is owned by the study lane; not present on 2026-09-29 |

Stop criteria. Stop and revisit if DS-08 shows a violation class that the inventory cannot avoid without shadow DOM; if DS-14 exceeds 1,000 ms; or if three or more phases each need a budget deviation.

## 14. Open items and conflicts between aspects

| Item | State |
|---|---|
| Density: accessibility D5 says "default density 32"; layout D7 says chrome controls and rows 28, typed fields 32 | Tokens follow the layout aspect, which owns density. The 24 px minimum holds in both. Accessibility should align its wording |
| SLP metric M17 asks primary actions to be at least 32 px; chrome controls are 28 px | Open for the layout aspect: size dialog primary buttons with `--density-field-height` or record a deviation |
| Colour C9 asks for three blocks and hex, with `color-scheme` on `:root`; `light-dark()` saves about 4,100 B | Generator follows the colour aspect except that `color-scheme` is scoped to `[data-ui="next"]` until S8 (M12); the colour aspect should accept that. Re-ask about `light-dark()` from about November 2026 (5.4) |
| Node 22 is needed wherever the noslop hooks are installed (ADR-0017); whether they are installed is UNVERIFIED | 4.2; the owner decides whether Terrazzo becomes a gate |
| A vendored Preact-class runtime is a viable fallback to hand-written builders | 7.1; revisit on the ADR trigger |
| A Python DTCG token library | Not found, UNVERIFIED (search budget exhausted) |
| Measurement scripts live in `.tmp/dsa/` (gitignored) | Section 15: the integrator should copy them into the repository; this aspect does not own a path for them |
| Nested theme regions | Not supported in v1; needs a re-apply rule if a region ever has its own theme |
| Terrazzo default lint rejects hue `none`, which the DTCG Color Module allows ("The `none` keyword MAY be used in the `components` array", S34) | Cross-check turns the rule off; the colour aspect keeps `none` |
| Legacy `[hidden]{display:none!important}` also matches `hidden="until-found"` | Until S8 no new component may rely on `until-found` (find-in-page cannot reveal it); after S8 the reset rule excludes it (5.2) |
| Legacy isolation measured on one fixture only (M15) | DS-09 holds it per gallery state; Firefox and Safari UNKNOWN |
| Seam inset in compact density | This design insets content 12 px from a seam centre in both densities; the layout aspect should confirm this against its compact 8 px gutter |
| Contradiction C15 (CSP behaviour) | Narrowed for Chromium 151: shadow DOM with adopted stylesheets, a `<link>` inside a shadow root, Lit, `<dialog>` and `popover` raise no violation; a shadow `<style>` element and an inline import map are blocked. Firefox and Safari are UNKNOWN |
| Fonts URL shape | `fonts.lock.json` proposes `resources/web/fonts/...`; the route serves one segment. This design uses flat URL names and lets the allowlist map them (I-SEC1); the generator emits the file name only |
| Web Awesome status in `developer-tool-craft-benchmarks.md` | Stale: issue 1937 is closed (7.1) |
| CSS anchor positioning Baseline status | UNVERIFIED (S20) |
| OSS splitters | Not evaluated by any aspect (layout O7) |
| Cross-platform screenshot behaviour | UNKNOWN; one machine measured |
| Generator support for colour spaces other than OKLCH and for alpha | Not implemented; refused; ADR needed when the colour aspect requires it |
| I-KERN1 fingerprint coupling | Kernel ADR proposal, not made here |
| Playwright in this environment is 1.58.0; the `hci` extra pins 1.63.0 | Confirm before implementing DS-08 |
| The direct users of the design system (contributors, coding agents) are not a persona | Gap in `personas-and-jtbd.md` |

## 15. Measurements and how to repeat them

All scripts are in `.tmp/dsa/` (gitignored), each under 170 lines; run with the environment in section 1. Because that folder is not committed, a reviewer cannot rerun M2 to M7 and M9 to M15 from the repository alone. Reproducible from the committed tree: M1 (counts over the three web files), M8 (Appendix A plus the token files gives 243 tokens and 16,087 B) and the 15 negative fixtures, which DS-02 will hold. The integrator should copy `gen5.py`, `test_gen5.py`, `scheme_leak.py`, `measure_baseline.py`, `measure_js_cost.py`, `axe_targets.py` and the `spike*` folders (without `node_modules`) to a tracked path such as `docs/hci/measurements/dsa/`; that path is outside this aspect's files, so it is deferred.

| Id | What | Command or file |
|---|---|---|
| M1 | Baseline counts | `wc -c`; Python regular-expression script over the three files |
| M2 | Static request latency and cold load | `measure_baseline.py` (http.client loop; Playwright with a `MutationObserver` init script; 25 loads, 3 discarded) against `python -m eija_studio serve` |
| M3 | CSP spike: light DOM, shadow DOM (adopted, link, style), Lit, dialog, popover, axe | `spike/server_uv.py`, `spike/run_isolate.py`, `spike/run_spike.py` |
| M4 | Inline import map | `spike/importmap.html` |
| M5 | axe `target-size`, `aria_snapshot`, per-state cost | `axe_targets.py`, inline timing script |
| M6 | Pixel determinism | 3 launches x 6 fresh contexts, SHA-256 of `page.screenshot()` |
| M7 | JavaScript load cost | `measure_js_cost.py` |
| M8 | Pipeline fit on the five real files | `sd/build3.mjs`; `tz/tz4.config.mjs` and `tz5.config.mjs` (`npx terrazzo build --config ...` in `tz/`); `python gen5.py OUT.css design/tokens/{index,spacing,motion,color,typography}.tokens.json` from the repository root; `python test_gen5.py` (15 negative and 2 positive cases); Terrazzo comparison by regular expression over the two outputs. `gen4.py` is the first version |
| M9 | Web Awesome closure | `npm pack @awesome.me/webawesome@3.14.0`, import-graph walk of `dist-cdn` |
| M10 | Layers, `light-dark()`, density, `@import layer()` | `spike/arch.html`, `spike/strangle.html` |
| M11 | Fingerprint what-if | in-memory dictionary comparison against `trusted_build.json` using `identity.py` |
| M12 | Does a global `color-scheme` change the legacy page? | `python scheme_leak.py`: unmodified `index.html` and `app.css`, Playwright 1.58.0 with Chromium 151, emulated light and dark, three variants (none, global, scoped); compares computed color properties of all 174 elements and a full-page screenshot hash |
| M13 | Layered import of `tokens.css` with `@font-face`, under the Studio's CSP plus `font-src 'self'` | `python spike2/run.py` (entry sheet, `gen5.py` output, legacy `app.css`, type aspect's rebuilt WOFF2 from `.tmp/audit_rebuilt/`) |
| M14 | Vendored Preact 10.29.8 under the Studio's CSP | `python spike3/run.py`; `npm pack preact@10.29.8`, `dist/preact.module.js` and `hooks/dist/hooks.module.js` with one specifier changed |
| M15 | Legacy layer leaks into new components, and the reset that removes them | `python spike4/run.py`: unmodified baseline `app.css` in `@layer legacy`, a 14-element component fixture, 18 computed properties, pages with and without the legacy layer and with and without `reset.css`, the Studio's CSP string, one Chromium process |

## 16. Sources

All URLs were opened on 2026-09-29. "Fetch summary" means WebFetch returned a model-written summary.

| Id | URL | Used for |
|---|---|---|
| S1 | https://www.designtokens.org/tr/2025.10/format/ | DTCG 2025.10 status, dimension, aliases, `$type` inheritance, `$extensions`, file extension |
| S2 | https://www.designtokens.org/tr/2025.10/resolver/ | Resolver module: sets, modifiers, `resolutionOrder`, `.resolver.json` |
| S3 | https://styledictionary.com/info/dtcg/ | Style Dictionary 2025.10 support statement (the page has no `usesDtcg` option) |
| S4 | https://github.com/style-dictionary/style-dictionary/releases | 5.5.3 to 5.5.5 release notes |
| S5 | https://registry.npmjs.org/style-dictionary/latest (and the same path for `@terrazzo/cli`, `@terrazzo/parser`, `@terrazzo/plugin-css`, `lit`, `@zag-js/vanilla`, `@zag-js/tree-view`, `@awesome.me/webawesome`, `axe-core`, `@playwright/test`); the `lit@3.3.3` tarball | versions, licences, dependency counts, unpacked sizes, Node engines, Lit imports |
| S6 | https://terrazzo.app/docs/ | Terrazzo DTCG statement: "the only tool that supports the full DTCG format"; resolver support "coming in 2.0" (stale against 2.7.1) |
| S7 | https://github.com/terrazzoapp/terrazzo | licence, activity |
| S8 | https://lit.dev/docs/components/styles/ | Lit styling; no CSP statement |
| S9 | https://github.com/shoelace-style/webawesome/issues/1937 | Web Awesome inline-style issue, closed 2026-02-03 |
| S10 | https://github.com/shoelace-style/webawesome/pull/1980 | fix merged 2026-02-02 |
| S11 | https://webawesome.com/docs/ | install, autoloader, base path |
| S12 | https://registry.npmjs.org/@zag-js/tree-view/-/tree-view-1.44.0.tgz and https://registry.npmjs.org/@zag-js/vanilla/-/vanilla-1.44.0.tgz | tarballs unpacked: `package.json` dependencies and the imports in `dist/*.mjs` |
| S13 | https://developer.mozilla.org/en-US/docs/Web/CSS/@layer | Baseline widely available since March 2022; unlayered outranks layered; `!important` reverses the layer order (re-opened 2026-09-29 for this revision) |
| S14 | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog | `showModal()` behaviour |
| S15 | https://developer.mozilla.org/en-US/docs/Web/API/Popover_API | Baseline 2025, newly available since January 2025 |
| S16 | https://developer.mozilla.org/en-US/docs/Web/API/Document/adoptedStyleSheets | widely available since March 2023; no CSP statement |
| S17 | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script/type/importmap | import maps are inline only |
| S18 | https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark | Baseline 2024, newly available since May 2024; requires `color-scheme` |
| S19 | https://developer.mozilla.org/en-US/docs/Web/CSS/@import | `layer()` syntax; placement rule |
| S20 | https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_anchor_positioning | page read shows no Baseline data (UNVERIFIED) |
| S21 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | SC 2.5.8 text and exceptions |
| S22 | https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md | `target-size` disabled by default |
| S23 | https://playwright.dev/docs/test-snapshots | screenshot variation across environments |
| S24 | https://playwright.dev/python/docs/api/class-pageassertions | Python page assertions |
| S25 | https://www.w3.org/WAI/ARIA/apg/patterns/treeview/ | tree keyboard model and roles |
| S26 | https://martinfowler.com/bliki/StranglerFigApplication.html | strangler fig pattern, 22 August 2024 |
| S27 | https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1 s, 1 s, 10 s limits |
| S28 | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf | Fitts calibration `T = 0.37 + 0.13 ID`, R2 = 0.93 (PDF text read) |
| S29 | https://pypi.org/pypi/axe-playwright-python/json and the 0.1.8 wheel | MIT licence, bundled axe-core 4.12.1 |
| S30 | https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html | SC 1.4.12 values, Level AA |
| S31 | https://web.dev/baseline | Baseline: widely available is 30 months after newly available |
| S32 | https://github.com/45ck/noslop (`package.json` through the GitHub API) | `@45ck/noslop` 1.0.0, MIT, `engines.node >= 22.0.0` |
| S33 | `npm view preact version license dist.unpackedSize` and the `preact@10.29.8` tarball | Preact 10.29.8, MIT, file sizes, bare specifier and `innerHTML` occurrences |
| S34 | https://www.designtokens.org/tr/2025.10/color/ | DTCG Color Module 2025.10 (Final Community Group Report, 28 October 2025): "The `none` keyword MAY be used in the `components` array" |
| S35 | https://developer.mozilla.org/en-US/docs/Web/CSS/all | `all` excludes `direction`, `unicode-bidi` and custom properties; Baseline widely available (per fetch summary) |
| S36 | https://developer.mozilla.org/en-US/docs/Web/CSS/revert | `revert` in author styles rolls back to user or user-agent styles; differs from `revert-layer` (per fetch summary) |
| S37 | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/hidden | author `display` overrides `hidden`; `until-found` typically uses `content-visibility: hidden` and is not revealed when `display` is `none` (per fetch summary) |
| V6 | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | SC 2.5.7 (opened by the synthesis author; not re-opened) |

Repository files read: `src/eija_studio/resources/web/*`, `interfaces/http.py`, `adapters/identity.py`, `domain/evidence.py`, `resources/trusted_build.json`, `tests/test_http_and_architecture.py`, `AGENTS.md`, `docs/architecture/ARCHITECTURE.md`, `docs/adr/0017-local-quality-gates.md`, `docs/oss/REGISTER.md`, `examples/excursion-candidate.json`, `design/tokens/*.tokens.json`, `design/fonts.lock.json`, `docs/hci/design/{color-system,typography,layout-model,accessibility,content-and-onboarding,canvas-uml-interaction,ai-interaction,motion-and-performance}.md` (by section and search), and, read-only from another worktree, `hci/pyproject.toml` and `hci/quality/sessions/hci.py`.

## Appendix A. Generator reference (the spike that section 4 measured)

This is the algorithm behind the section 4 numbers. It is not the shipped file; the implementer writes `scripts/build_tokens.py` from it and adds the tests in DS-01 and DS-02. It reads the five DTCG files and `fonts.lock.json`, merges token paths, folds sibling `color.light` and `color.dark` groups into roles, resolves aliases to `var()`, and writes one layered stylesheet followed by `@font-face` rules. It has 137 code lines (non-blank, non-comment, non-docstring, counted by script) in 167 lines. It differs from the first version (15,974 B) in five ways found by the audit or by M12: it validates every token before the emit filter, reads `emit` and `emit-not` from `index.tokens.json` and stops on a root in neither list, raises an explicit error for a missing or unknown unit, wraps long values after commas so no generated line exceeds 100 characters, and writes no inner `@layer` (the import supplies it, 5.2) and scopes `color-scheme`.

```python
"""DTCG 2025.10 -> CSS custom properties and @font-face. Standard library only. Fails closed."""
import json, math, re, sys
from pathlib import Path

REF = re.compile(r"^\{([^{}]+)\}$")
THEMES = ("light", "dark")
UNITS = {"dimension": ("px", "rem"), "duration": ("ms", "s")}
LINE_MAX = 100
KEBAB = lambda s: re.sub("[A-Z]", lambda m: "-" + m.group().lower(), s)


def walk(node, path=(), inherited=None, out=None):
    out = {} if out is None else out
    kind = node.get("$type", inherited)
    if "$value" in node:
        out[".".join(path)] = {"type": kind, "value": node["$value"], "modes": node.get("$extensions", {}).get("mode", {})}
        return out
    for key, child in node.items():
        if not key.startswith("$"):
            walk(child, path + (key,), kind, out)
    return out


def role(name):
    """color.light.accent.fg -> (color.accent.fg, 'light'); any other name -> (name, None)."""
    p = name.split(".")
    return (".".join(p[:1] + p[2:]), p[1]) if p[0] == "color" and len(p) > 2 and p[1] in THEMES else (name, None)


def css_name(path):
    return "--" + KEBAB(path.replace(".", "-"))


def oklch_to_rgb8(l, c, h):
    hue = math.radians(0 if h == "none" else h)
    a, b = c * math.cos(hue), c * math.sin(hue)
    l_, m_, s_ = l + 0.3963377774 * a + 0.2158037573 * b, l - 0.1055613458 * a - 0.0638541728 * b, l - 0.0894841775 * a - 1.2914855480 * b
    r, g, bl = (4.0767416621 * l_ ** 3 - 3.3077115913 * m_ ** 3 + 0.2309699292 * s_ ** 3,
                -1.2684380046 * l_ ** 3 + 2.6097574011 * m_ ** 3 - 0.3413193965 * s_ ** 3,
                -0.0041960863 * l_ ** 3 - 0.7034186147 * m_ ** 3 + 1.7076147010 * s_ ** 3)
    gamma = lambda x: 12.92 * max(0, min(1, x)) if x <= 0.0031308 else 1.055 * min(1, x) ** (1 / 2.4) - 0.055
    return [round(gamma(v) * 255) for v in (r, g, bl)]


def render(kind, value, tokens):
    if isinstance(value, str):
        m = REF.match(value)
        if m:
            if m.group(1) not in tokens:
                raise ValueError("dangling alias " + value)
            return "var(%s)" % css_name(role(m.group(1))[0])
    if kind == "color":
        if value["colorSpace"] != "oklch" or "hex" not in value or value.get("alpha", 1) != 1:
            raise ValueError("colour needs oklch source, a hex fallback and alpha 1")
        got = [int(value["hex"][i:i + 2], 16) for i in (1, 3, 5)]
        if max(abs(x - y) for x, y in zip(got, oklch_to_rgb8(*value["components"]))) > 1:
            raise ValueError("hex and oklch disagree: " + value["hex"])
        return value["hex"].lower()
    if kind in UNITS:
        if not isinstance(value, dict) or "value" not in value or value.get("unit") not in UNITS[kind]:
            raise ValueError("%s needs a value and a unit in %s" % (kind, UNITS[kind]))
        return str(value["value"]) + value["unit"]
    if kind == "cubicBezier":
        return "cubic-bezier(%s)" % ", ".join(map(str, value))
    if kind in ("number", "fontWeight"):
        return str(value)
    if kind == "fontFamily":
        return ", ".join(('"%s"' % f if " " in f else f) for f in ([value] if isinstance(value, str) else value))
    if kind == "transition":
        return " ".join(render(t, value[k], tokens) for k, t in (("duration", "duration"), ("delay", "duration"), ("timingFunction", "cubicBezier")))
    raise ValueError("unsupported type %r" % kind)


def expand(name, tok, tokens):
    """One token -> [(css name, css value)]; a typography composite gives one property per member."""
    base = role(name)[0]
    if tok["type"] != "typography":
        return [(css_name(base), render(tok["type"], tok["value"], tokens))]
    types = {"fontFamily": "fontFamily", "fontSize": "dimension", "fontWeight": "fontWeight", "letterSpacing": "dimension", "lineHeight": "number"}
    return [(css_name(base + "." + k), render(types[k], v, tokens)) for k, v in tok["value"].items()]


def check_cycles(tokens):
    def follow(name, seen):
        m = isinstance(tokens[name]["value"], str) and REF.match(tokens[name]["value"])
        if m and m.group(1) in tokens:
            if m.group(1) in seen:
                raise ValueError("cyclic alias at " + name)
            follow(m.group(1), seen | {name})
    for n in tokens:
        follow(n, {n})


def wrap(line):
    """Break a declaration longer than LINE_MAX after commas, four spaces in."""
    if len(line) <= LINE_MAX or ", " not in line:
        return line
    head, val = line.split(": ", 1)
    items = val.rstrip(";").split(", ")
    out, cur = [], head + ":"
    for i, item in enumerate(items):
        piece = " " + item + ("," if i < len(items) - 1 else ";")
        if len(cur + piece) > LINE_MAX and not cur.endswith(":"):
            out.append(cur)
            cur = "   " + piece
        else:
            cur += piece
    return "\n".join(out + [cur])


def font_face(lock_path):
    lock = json.loads(Path(lock_path).read_text(encoding="utf-8"))
    rules = []
    for face in lock["faces"]:
        weight = lock["font_face_rules"]["font-weight"][face["id"]]
        head = '@font-face {\n  font-family: "%s";\n  src: url("%s") format("woff2");\n' % (face["css_family"], face["shipped"]["file"])
        tail = "  font-weight: %s;\n  font-style: normal;\n  font-display: swap;\n" % weight
        rules.append(head + tail + wrap("  unicode-range: %s;" % face["shipped"]["unicode_range"]) + "\n}\n")
    return "".join(rules)


def load(files):
    tokens, pipeline = {}, {}
    for f in files:
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pipeline.update(doc.get("$extensions", {}).get("io.github.45ck.eija-studio", {}).get("pipeline", {}))
        for name, tok in walk(doc).items():
            if name in tokens:
                raise ValueError("duplicate token " + name)
            tokens[name] = tok
    return tokens, pipeline


def build(files, fonts=None, scope=':root[data-ui="next"]'):
    """Return (css, token count). scope carries color-scheme until S8; None means :root."""
    tokens, pipeline = load(files)
    emit, emit_not = pipeline["emit"], pipeline["emit-not"]
    check_cycles(tokens)
    for name, tok in tokens.items():  # every token is validated before the emit filter
        if name.split(".")[0] not in emit + emit_not:
            raise ValueError("root group %r is in neither emit nor emit-not" % name.split(".")[0])
        expand(name, tok, tokens)
        for v in tok["modes"].values():
            render(tok["type"], v, tokens)
    light, dark, compact = [], [], []
    for name in sorted(tokens):
        tok = tokens[name]
        if name.split(".")[0] in emit:
            for css, value in expand(name, tok, tokens):
                (dark if role(name)[1] == "dark" else light).append((css, value))
                compact += [(css, render(tok["type"], v, tokens)) for m, v in tok["modes"].items() if m == "compact"]
    fmt = lambda items: "\n".join(wrap("  %s: %s;" % i) for i in items)
    sc = scope or ":root"
    body = ":root {\n%s\n}\n" % fmt(light)
    body += '@media (prefers-color-scheme: dark) {\n:root:not([data-theme="light"]) {\n%s\n}\n}\n' % fmt(dark)
    body += ':root[data-theme="dark"] {\n%s\n}\n' % fmt(dark)
    body += '[data-density="compact"] {\n%s\n}\n' % fmt(compact) if compact else ""
    body += "%s {\n  color-scheme: light dark;\n}\n" % sc
    body += '%s[data-theme="light"] {\n  color-scheme: light;\n}\n' % sc
    body += '%s[data-theme="dark"] {\n  color-scheme: dark;\n}\n' % sc
    return body + (font_face(fonts) if fonts else ""), len(tokens)


if __name__ == "__main__":
    css, n = build(sys.argv[2:], fonts="design/fonts.lock.json")
    Path(sys.argv[1]).write_text(css, encoding="utf-8", newline="\n")
    print(n, "tokens read,", len(css.encode()), "bytes")
```

Known gaps of this reference, all deliberate: no colour space except OKLCH with a hex, no alpha other than 1, no `$root`, `$extends` or `$ref`, no gamut fallbacks, no `light-dark()` option (the first version had one), no comments in the output, dimension units limited to `px` and `rem` (the two units DTCG 2025.10 allows, S1) and duration units to `ms` and `s` (the two units DTCG 2025.10 allows, S1; the token files use `ms`), and the Python source itself has lines over 100 characters (DS-12 covers shipped JS, CSS and HTML, not the generator).
