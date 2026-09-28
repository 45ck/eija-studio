# HCI-law instrumentation

Quantitative, reproducible HCI checks of the Studio UI. **This is prediction plus instrumented measurement on synthetic data. It is not a usability study, and it says nothing about real users' speed, comprehension or satisfaction.** The latest results are in [REPORT.md](REPORT.md) (rendered from [report.snapshot.json](report.snapshot.json)). Decisions: [ADR-0039](../adr/0039-hci-law-instrumentation.md), [ADR-0040](../adr/0040-hci-budgets-as-ratchets-and-harness-identity.md).

## Run it

```bash
pip install -e ".[dev,hci]"              # playwright==1.63.0, axe-playwright-python==0.1.8 (no browser download)
python -m quality.hci prereq             # READY, or NOT_RUN: <reason> (exit 3)
python -m quality.hci run                # writes reports/hci/{report.json,REPORT.md,trace.json}
python -m quality.hci run --publish-docs --date 2026-09-28   # also refresh docs/hci/ (commit these)
python -m quality.hci check              # drift check, no browser
pytest -m hci                            # budgets as tests (opt-in; skipped => NOT_RUN if Chrome is missing)
nox -s hci                               # the same, as a gate (tags: full, release); nox -s hci_docs is the fast drift check
```

Requirements: Google Chrome installed (Playwright `channel="chrome"`; nothing is downloaded), Python 3.11+. The run starts its own `eija serve`-equivalent on an ephemeral loopback port with a workspace under `.tmp/hci/` (offline provider, synthetic data), one fresh server per journey. Without Chrome, Playwright or axe every entry point reports `NOT_RUN` and never `PASS`.

## What is measured

The canonical owner journey (20 modelled actions): type the request, create the case, ask for interpretations, select `recommend_only`, open Try, reset, Submit and Recommend as teacher-assigned, Approve as registrar, attempt Recommend as teacher-unassigned (the kernel must deny it), open Evidence, run verification, type the three review answers, acknowledge, approve the exact revision, apply. It runs three times with the pointer (timing repeats; the first run also does the audits) and once keyboard-only.

`quality/hci/probe.js` is injected as a Playwright init script (so the Studio's `script-src 'self'` CSP stays intact). It only observes.

### Fitts's law (pointing)

Shannon formulation (MacKenzie 1992): `ID = log2(D / W + 1)` bits, predicted `MT = a + b * ID`.

* `D`: distance in CSS px between the landing point of the previous and of the current pointer target. The landing point is the centre of the target's effective clickable box, and the driver clicks exactly there (it verifies with `elementFromPoint` that nothing covers it). The first pointer target has no preceding position and no `ID`.
* `W = min(width, height)` of the effective box (MacKenzie & Buxton 1992, "smaller-of"). A checkbox and its `<label>` are one target because the label activates the control; the raw input box is reported alongside.
* `a = 0.230 s`, `b = 0.166 s/bit`: MacKenzie & Buxton (1992) mouse regression on the smaller-of model, `MT = 230 + 166 * ID` ms, r = .9501 (Macintosh II, laboratory pointing). Population average; swap `laws.FittsModel` for locally fitted values.
* Flags: `ID > 4` bits, and `W < 24 px` (WCAG 2.2 SC 2.5.8 Target Size (Minimum)).
* Own WCAG 2.5.8 audit over every visible enabled control of every audited view: pass (>= 24x24), `pass-spacing` (undersized but a 24 px circle around its centre touches no other target and no other undersized target's circle) or fail. The inline, user-agent-controlled, equivalent and essential exceptions are not evaluated.

### Hick-Hyman law (choice)

`T = b * log2(n + 1)` with `b = 0.150 s/bit` (Hick 1952, Hyman 1953; constant from Card, Moran & Newell 1983). At each decision point the journey declares the group of alternatives that compete for one intent (interpretation cards, work-area tabs, lifecycle actions, acting roles) and the probe counts the enabled ones (`n`); it also counts every enabled control in the viewport (`screen_controls`, an upper bound). Flag: `n > 7`. Hyman's point stands: time follows uncertainty, so the value is an upper bound for an expert who already knows the answer.

### KLM-GOMS (expert task time)

Card, Moran & Newell (1980): `K` 0.28 s (average non-secretary typist), `P` 1.10 s, `B` 0.10 s per press or release, `H` 0.40 s, `M` 1.35 s. Operators are recorded from what the driver really does: a click is `P B B`; every mouse/keyboard switch adds `H`; typing adds one `K` per character plus one per Shift; `Ctrl+A` is two `K`; a `<select>` is modelled as open (`P B B`) and choose (`P B B`) because native popups are not observable. `M` operators are placed by hand, once per real decision or reading moment, with the reason recorded in `journey.py`. Three totals: standard, **Fitts-refined** (each `P` replaced by its Fitts `MT`), and the keyboard-only journey built from the actual Tab/Enter/Space/arrow presses. Scrolling and system response `R` are excluded from the standard total; the measured wait is reported separately.

### Doherty threshold (responsiveness)

Doherty & Thadani (1982): about 400 ms. In the page, a capture-phase `click` listener timestamps each interaction (mouse or Enter/Space activation) and a `MutationObserver` timestamps DOM updates. Reported per interaction: **first feedback** (first DOM mutation; here the synchronous "Working..." notice) and **settled** (last mutation before the page was quiet for 150 ms with no `aria-busy`). Percentiles are nearest-rank (deterministic; with few samples p95 is the maximum). Native controls that change no DOM (the acknowledge checkbox) are listed and excluded. Timings exclude input-device and OS latency and are wall-clock on a possibly busy PC: budgets use generous ratchets.

### WCAG 2.2 AA

axe-core (bundled with axe-playwright-python) restricted to tags `wcag2a wcag2aa wcag21a wcag21aa wcag22aa`, run on every checkpoint view (start, create, options, selected, Impact, Try x3, Evidence x2, applied). Aggregated by rule and impact, plus axe's `incomplete` (needs manual review). Also: a reflow check at 390x844 and 320x568 (WCAG 1.4.10), a supplementary non-axe check for state conveyed only by a CSS class, and the keyboard traversal below. axe finds only part of the WCAG failures; clean is not conformant.

### Keyboard-only traversal

The whole journey again with Tab, Enter, Space and arrow keys only. Recorded: Tab presses per target, every focus stop, whether each has a visible indicator (computed outline or box-shadow), whether activation dropped focus to `<body>` once the DOM settled, and focus moves against reading order (heuristic: upward moves over 8 px, ignoring a wrap to the page top and a jump to the next grid column).

### Working memory (heuristic proxy)

Miller (1956) 7 +/- 2, Cowan (2001) about 4. These limits concern chunks a person *holds*, not pixels on screen, so the number here is only a **visibility proxy**: `chunks = visible operable controls + groups of visible static text/heading atoms that share a parent element`, measured in the first viewport and on the whole page for each view. Flags: more than 9 (Miller upper bound); more than 4 is shown for reference.

## Budgets

`quality/hci/budgets.json`: each budget has a `target` (the law's threshold) and a `limit` (the ratchet, the worst the current UI may be). `PASS` <= target; `GAP` between target and limit (pytest reports **xfail**, never pass); `FAIL` above the limit (regression); `NOT_RUN` when unmeasurable. The visual lane tightens limits toward targets as it applies REPORT.md recommendations; a change to a limit is a reviewed diff.

## Determinism and drift

Geometry, operators, axe results and all derived numbers are deterministic for the same UI bytes, Chrome and fonts (a browser test asserts that target boxes and operator sequences repeat across journeys). Timings are measured and vary. `report.json` is canonical (sorted keys, LF); `REPORT.md` is a pure function of the JSON, so `python -m quality.hci check` (fast tier) re-renders the committed snapshot and compares bytes. A snapshot older than the current UI bytes is reported as informational, not as failure; rerun `nox -s hci` and `--publish-docs` to refresh it. No timestamp is written unless `--date` is given.

## Reuse for demos

The journey is data (`quality/hci/journey.py`: `Step`, `Ref`, `Expect`, `Decision`) executed by one driver, so a live, visible demo (headed Chrome, cursor, typing) can replay the same steps with `--headed`. Recording and narration are out of scope for this lane.

## Human study (NOT_RUN)

None of this replaces observing people. A minimal protocol: 5-8 participants per persona, think-aloud, the same journey as a scenario, success/time/error counts and a satisfaction scale, results labelled with N and recruitment. The owner's [hci-review-skill](https://github.com/45ck/hci-review-skill) (MIT; consulted, not a dependency) has planners for that (`usability-test-planner`, `error-and-time-metrics-analyzer`, `cognitive-walkthrough`).

## References

* Card, S. K., Moran, T. P., Newell, A. (1980). The keystroke-level model for user performance time with interactive systems. *CACM* 23(7), 396-410.
* Card, S. K., Moran, T. P., Newell, A. (1983). *The Psychology of Human-Computer Interaction*. Erlbaum.
* Cowan, N. (2001). The magical number 4 in short-term memory. *Behavioral and Brain Sciences* 24(1), 87-114.
* Doherty, W. J., Thadani, A. J. (1982). The economic value of rapid response time. IBM.
* Hick, W. E. (1952). On the rate of gain of information. *Q. J. Exp. Psychol.* 4, 11-26. Hyman, R. (1953). Stimulus information as a determinant of reaction time. *J. Exp. Psychol.* 45, 188-196.
* MacKenzie, I. S. (1992). Movement time prediction in human-computer interfaces. *Proc. Graphics Interface '92*, 140-150.
* MacKenzie, I. S., Buxton, W. (1992). Extending Fitts' law to two-dimensional tasks. *Proc. CHI '92*, 219-226.
* Miller, G. A. (1956). The magical number seven, plus or minus two. *Psychological Review* 63, 81-97.
* W3C. WCAG 2.2, SC 2.5.8 Target Size (Minimum), 1.4.10 Reflow, 2.4.3 Focus Order, 2.4.7 Focus Visible, 4.1.2 Name, Role, Value.
