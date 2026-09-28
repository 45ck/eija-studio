# ADR-0039: Apply HCI laws to the Studio UI with Playwright, axe-core and pure formula modules

* Status: accepted
* Date: 2026-09-28
* Lane: hci

## Context and problem statement

The Studio UI is the owner's only instrument for reviewing an AI-proposed change, yet its usability claims are unmeasured. We want reproducible, quantitative checks grounded in established HCI models (Fitts, Hick-Hyman, KLM-GOMS, Doherty, WCAG 2.2, Miller/Cowan) that a later wave of UI work can be held to, without pretending to measure real users.

## Decision drivers

* ADR-0016: adopt open source; write only EIJA-specific glue.
* Honest evidence: models predict, they do not measure people; a missing browser is NOT_RUN, never PASS.
* The UI files belong to the visual lane, so this lane may measure but not edit them.
* The Studio serves a strict CSP (`script-src 'self'`) that must stay untouched by the instrumentation.
* Reproducibility on a shared 16 GB Windows PC (one browser at a time, temp inside the checkout).

## Considered options

* Playwright for Python driving the installed Chrome + axe-core through axe-playwright-python, with pure-Python law modules and an in-page observer script (chosen).
* Lighthouse CI or pa11y: audit-oriented, no journey model, no Fitts/KLM/Hick, would still need custom glue for the journey.
* Selenium / WebDriver + axe-selenium: heavier setup, weaker CDP init-script support (CSP-safe injection).
* Manual heuristic review only (the hci-review-skill pack): valuable but not reproducible or quantitative; kept as the qualitative complement.

## Decision outcome

Chosen option: Playwright + axe-playwright-python, because both are mature, permissively licensed, cross-platform, drive real Chrome via `channel="chrome"` without a browser download, and the injection of the observer as a CDP init script leaves the Studio's CSP intact.

* `quality/hci/laws.py` and `wcag.py` are pure, cited, configurable formulas (no I/O).
* `quality/hci/probe.js` only observes (geometry, choice counts, focus, click -> DOM-update timing); a unit test forbids mutating calls in it.
* `quality/hci/journey.py` holds the canonical owner journey as data plus one driver for pointer and keyboard-only runs. The pointer moves to and clicks the exact landing point that Fitts's D is computed from, after verifying nothing covers it.
* `analysis.py`, `recommend.py`, `report.py` turn traces into metrics, deterministic ranked recommendations, a canonical `report.json` and a `REPORT.md` that is a pure function of that JSON.
* Fitts constants are MacKenzie & Buxton (1992) mouse, smaller-of, Shannon (`230 + 166 * ID` ms), verified against the paper's text; Hick `b = 0.150 s/bit` and KLM operator times are Card, Moran & Newell. All are labelled population averages.
* The working-memory figure is explicitly a visibility proxy, not a memory measurement.

### Consequences

* Good: every claim in REPORT.md is traceable to a formula, a constant with a citation, and a recorded observation; drift between the committed report and its snapshot is a fast, browser-free check.
* Good: the journey-as-data can be replayed headed for demos.
* Bad: geometry depends on the Chrome version and installed fonts; the snapshot names its platform and Chrome build.
* Bad: timings are wall-clock on a shared PC; budgets for them are generous ratchets.
* Revisit when: the visual lane changes the UI (refresh the snapshot, tighten budgets), or when human study data exists to replace the population constants with locally fitted ones.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Playwright (Apache-2.0), axe-core (MPL-2.0) via axe-playwright-python (MIT) | Adopted as-is | n/a |
| Lighthouse, pa11y | Audit tools without a task model; no Fitts, Hick, KLM or click-latency instrumentation | Could feed extra a11y findings later |
| Existing Fitts/KLM calculators (web apps, `cogtool`-style tools) | GUI tools with manual input; no headless API against a live DOM | Replace `laws.py` if a maintained Python library appears |
| `quality/hci/*` (custom) | The journey, the geometry capture, the budgets and the report are EIJA-specific glue | Formulas are 5-line pure functions; the driver is the only real code |
