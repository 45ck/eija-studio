# Motion, feedback and performance budgets

Lane `lane/ux-research`, aspect `motion-performance`. Date 2026-09-29. Status: proposed. Decision record: [HCI-ADR-0066](../../adr/0066-hci-motion-performance.md). Tokens: [design/tokens/motion.tokens.json](../../../design/tokens/motion.tokens.json). Task-flow slices: [design/tasks/motion-performance.json](../../../design/tasks/motion-performance.json).

Source ids `E1` to `E34` are defined in section 12; every URL was opened on 2026-09-29. Revised after an independent audit (2026-09-29): the elapsed-time ticker is withdrawn (section 9), the frame budget has a tolerance and a display-rate check (section 8), token kinds distinguish literature limits from anchored values (section 10), and KLM clicks are charged as two B (section 2 of the ADR). Research-dossier ids (`REV§6`, `LAW§2.6`, `P7`) are defined in [SYNTHESIS.md](../research/SYNTHESIS.md). Numbers are labelled MEASURED (tool, date, conditions), LITERATURE (a threshold as published), ANCHORED (a published point whose p95 fail rule is ours), DERIVED (arithmetic or a nominal value), TARGET (our hypothesis) or PREDICTION (model output with band). Nothing here shows that developers will find the Studio pleasant; that needs the study in section 11.

## 0. Decisions first

| # | Decision | Test | Evidence |
|---|---|---|---|
| D1 | Every action declares one of four response classes: direct, view, commit, job. Each has a literature limit (fail) and a design target (warn), tested as p95. | MB-01 to MB-05 | E1, E8, E12, E23 |
| D2 | Feedback ladder. At most 100 ms: the acting element changes state. Under 1 s: no spinner, skeleton or busy text. From 1 s: a static start-time text, written once (no ticking count: WCAG 2.2.2 has no five-second exception for auto-updating information, E6). Determinate progress only when the kernel reports it. Never a skeleton or spinner over a status or evidence region. | MB-04 to MB-06 | E1, E2, E6, E16 |
| D3 | Slow work is a job. The previous verdict stays visible and marked STALE while it runs. The outcome is a real evidence status. Cancel or abandon states what it does not undo. Two phases: Phase 0 needs no kernel change and can only say "pending" and, after the 1 s indicator delay, offer "abandon wait"; Phase 1 needs a kernel job endpoint (its own ADR) and can say RUNNING, progress and cancel. | MB-06 to MB-08 | E1, E18, E20 |
| D4 | Authority honesty. Status words (PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN, RUNNING, APPROVED, APPLIED) are written to the screen only from a kernel response or job event, never predicted. Optimism is allowed for view state and layout position only, marked "pending" until acknowledged. Approve, apply, select, save, discard and typed edits are never optimistic. | MB-16, MB-17, MB-21 | E17, ADR-004, ADR-008 |
| D5 | Motion has four purposes only: feedback, enter-exit, continuity, progress. Durations come from {100, 150, 240, 400} ms. Only opacity and transform are animated. Every animation is interruptible. No success animation on approve. | MB-13, MB-19 | E3, E11 |
| D6 | Diff and relayout transitions keep object identity by stable element id (FLIP with the Web Animations API, 240 ms, 400 ms cap). Removed items stay listed with the word REMOVED; nothing vanishes. No highlight flash. The View Transition API is not used yet: it is Baseline Newly available since 2025-10-14 (E34), so the deferral rests on untested CSP behaviour, reduced-motion handling and the default cross-fade; a smoke test is in the probe. | MB-11, MB-15 | E13, E14, E15, E22, E29, E34 |
| D7 | Canvas drag is client-only during the gesture (one frame loop, SVG transform attribute, incident edges only) and issues exactly one commit at drop. Budget: 60 Hz (display rate measured first), main gate p95 script at most 10 ms per move, p95 frame interval at most 20 ms with at most 5 percent of frames over 25 ms, zero long animation frames. 120 Hz is not promised. | MB-09, MB-10 | E9, E10, E25 |
| D8 | Reduced motion: under `prefers-reduced-motion: reduce` no transform, scale or translate animation runs; opacity fades of at most 100 ms are kept; indeterminate progress is drawn static. Meaning never depends on motion: the screen with animations finished equals the screen with motion disabled. | MB-14, MB-15 | E4, E5 |
| D9 | Every budget is a token and a test id, so a browser probe can fail the build. Baselines in section 3 are MEASURED server-side only; browser-side and frame numbers are UNKNOWN until measured in a visible Chromium. | section 10 | E23 |
| D10 | Finding for the kernel lane, not a decision here: verification time is dominated by SQLite commits, and a batching change might move it from the 1 to 10 s class into the 0.1 to 1 s class. Unmeasured. | section 3.3 | E31 |

## 1. What the baseline does

Read from `src/eija_studio/resources/web/{app.css,app.js,index.html}` and `src/eija_studio/interfaces/http.py` on 2026-09-29 (E32). MEASURED means counted by `grep` on the files.

| Fact | Value | Consequence |
|---|---|---|
| `transition`, `animation`, `@keyframes`, `prefers-reduced-motion` in `app.css` | 0 of each | No motion exists, so there is nothing to make reduced. The only hover effect is `filter: brightness(.95)`, unanimated. |
| `task()` in `app.js` | `if(busy)return;` then sets `aria-busy` on `body` and writes a text notice | A second click during any request is dropped without a message. One request at a time locks the whole page. |
| Feedback for verification | The text "Executing the synthetic state / actor / action matrix…" in `#notice` (`role="status"`, `aria-live="polite"`), written synchronously in the click handler | Text only; no elapsed time, progress, cancel or STALE prior verdict. |
| API shape | Every command is one synchronous `fetch` that returns the whole case (12 to 46 KB) | No progress events and no cancel exist in the kernel interface. |
| Browser requests | No `AbortController` | An abandoned wait would not stop the kernel; see section 5. |
| Optimism | None found in `app.js`: views are rendered from the response after `await load(id)` | The baseline is already authority-honest; the design must keep that while adding local feedback. |

## 2. Response classes and Doherty per interaction type

Nielsen's three limits (E1): about 0.1 s feels instantaneous and needs no feedback beyond the result; about 1 s keeps the flow of thought (no special feedback is needed between 0.1 and 1 s); about 10 s is the limit of attention and needs percent-done and a way to interrupt. The article gives no p95 fail threshold, so our "limit" values below are ANCHORED to these points and the p95 fail rule is our own choice. The article is from 1993 with a 2014 update and cites Miller (1968) and Card et al. (1991); I did not open those. Validity: perceptual limits for interactive dialogue, not for batch jobs.

Doherty and Thadani (E12, a blog transcription of the IBM text): programmer throughput in transactions per hour was 180 at 3.0 s system response time, 208 at 2.0 s, 252 at 1.0 s, 279 at 0.6 s and 371 at 0.3 s. The text read contains no 400 ms threshold, so the popular "Doherty threshold" is not used. Validity: 1980s terminal transactions by programmers, one table in a transcription with an internal arithmetic slip reported by the dossier `LAW§2.6`; it says fast feedback has value and says nothing about AI latency. We use the 0.3 s row only to place our view and commit targets below the 1 s limit; we do not predict a throughput gain.

Limit = fail threshold (ANCHORED to the Nielsen point named, rule ours), target = warn threshold (TARGET), both p95 of at least 30 trials (MB ids in section 10). INP (E8) is assessed at p75; our p95 is the stricter tail.

| Class | Interaction types in the Studio | Limit | Target | Feedback | Doherty row used |
|---|---|---|---|---|---|
| direct | pointer down, drag frame, selection, focus, hover, palette open, keystroke echo in palette | 100 ms (E1) | 50 ms (TARGET) | The acting element changes; no indicator | 0.3 s row; target lies inside it |
| view | tree selection updates the facet lane; chapter open; perspective switch; palette results after a keystroke | 1000 ms (E1) | 200 ms (TARGET; same number as the INP good boundary, E8, but INP is p75 and ours p95) | Selection changes at once; content updates in place; nothing else before 1 s | 0.3 s row |
| commit | select meaning, typed edit, layout drop, save, approve, apply, discard | 1000 ms | 300 ms (TARGET) | Pending marker on the acting element at once; result from the kernel response | 0.3 s row; measured server p95 26 to 214 ms (E23) |
| job | verify, model check, mutation run, provider proposal, agent run | none for completion; accept in 100 ms | accept in 50 ms | RUNNING (or pending in Phase 0) at once; static start-time text from 1 s; determinate progress only if the kernel reports it; interrupt control from the start; above 10 s a percentage or the words "no progress signal" | not applicable (seconds to minutes) |

INP (E8): good at or below 200 ms, poor above 500 ms, assessed at the 75th percentile, covers click, tap and key press but not hover, zoom or scroll. It is a field metric for pages; here it only supplies the 200 ms reference for the view target.

## 3. Baseline measurements

### 3.1 Server-side latency (MEASURED)

Tool: `.tmp/latency/probe.py` (Python 3.12.10 `http.client`, keep-alive, real HTTP to uvicorn 0.48 on 127.0.0.1, FastAPI app from `create_app`, offline provider, worktree files, identity flag forced to trusted only to allow `verify`; the file hashing cost stays). 2026-09-29, Windows 11, workspace on C:, n = 20 full change-case cycles, 12 logical CPUs shared with about a dozen other agents, so the tail is inflated. Latency is request to full response body read. It excludes browser scheduling, JSON parse, DOM update and paint.

| Endpoint | p50 ms | p95 ms | max ms | Response bytes | Band at p50 / p95 (thresholds 100, 1000, 10000 ms) |
|---|---|---|---|---|---|
| GET status | 21.0 | 74.2 | 665.4 | 1957 | instant / instant |
| GET cases (list) | 11.7 | 111.2 | 379.5 | 3136 | instant / flow |
| POST create case | 19.4 | 89.5 | 877.7 | 2097 | instant / instant |
| POST propose (offline provider) | 43.1 | 109.8 | 121.2 | 3008 | instant / flow |
| POST select meaning | 24.2 | 57.9 | 122.3 | 4834 | instant / instant |
| GET case view | 23.1 | 37.6 | 48.1 | 12103 | instant / instant |
| POST layout (one drag drop) | 18.3 | 25.8 | 31.5 | 4857 | instant / instant |
| POST preview | 17.2 | 33.4 | 116.8 | 194 | instant / instant |
| POST execute (one action) | 17.7 | 32.2 | 35.4 | 285 | instant / instant |
| POST edit (typed transaction) | 19.1 | 25.5 | 43.0 | 4922 | instant / instant |
| **POST verify (125 cells)** | **2095.8** | **2971.3** | **4165.3** | 38403 | **attention / attention** |
| GET case view after verify | 36.8 | 73.6 | 121.7 | 46439 | instant / instant |
| POST approve | 75.3 | 214.1 | 1370.4 | 38868 | instant / flow |
| POST apply | 51.5 | 158.6 | 1859.1 | 38867 | instant / flow |

Reading it. Only verification is in the 1 to 10 s class. Every commit is inside the target at p50 and p95 except that the tails reach 1.4 to 1.9 s once in 20 runs on a loaded machine, so the 1 s limit is not safe at the maximum and MB-05 (elapsed text at 1 s) applies to commits as well. The p95 of n = 20 is the interpolated value near the second-largest sample and is weak; the probe must run with n of at least 30 and three repetitions before a limit is enforced. Raw output: `.tmp/latency/result.json` (gitignored).

Live provider latency: UNKNOWN. `evidence/live-provider-status.json` reports both live providers NOT_RUN. The offline provider answered in 43 ms; the code records `elapsed_seconds` per run, and another lane's task file `design/tasks/ai-flows.json` notes timeouts of 60 s (OpenRouter) and 120 s (Codex); I did not verify them in code.

### 3.2 Browser-side latency and frame rate: UNKNOWN

I ran the baseline UI in one Chrome 154 tab and drove it with a script. `document.visibilityState` was `hidden` and `hasFocus()` false, so `requestAnimationFrame` did not run and timers and network tasks were throttled: the same status fetch took p50 66 ms in the page against 21 ms in Python (max 3.6 s), and the create-case round trip took p50 502 ms against 19 ms. Those numbers are 1.8 to 26 times the server values and are discarded as a baseline. What survives is qualitative: the notice text for verification appears in the same task as the click (before any response). Browser-side p95 per action, frame intervals and paint times need a visible Chromium (headless, or a foreground window) and remain UNKNOWN. The closing test MB-01 to MB-03 and MB-09 are written for that probe.

### 3.3 Where verification time goes (MEASURED, in process)

Same tooling, no HTTP: `verify_runtime` on the selected candidate took 1801, 2011, 2300, 2551 and 2342 ms in five runs. The matrix is 5 actors x 5 states x 5 actions = 125 cells, about 16.8 ms per cell at the HTTP p50. Under `cProfile` (which inflates wall time to 9.2 s) 376 SQLite connections were opened and 257 commits took 6.70 s of 9.21 s, or 73 percent of profiled time. `identity()` (hashes every `.py` and web resource) took 41.7 ms per call (mean of 10) and runs in view, verify, approve and apply.

Finding for the kernel lane, labelled HYPOTHESIS: if commits were batched per cell or per run, verification might fall below 1 s and change class from attention to flow. That would remove the need for a progress display on this job but not for the job lane, because model checks and mutation runs will be slower. Kernel changes need an ADR and a regression test (`AGENTS.md`); this document does not propose the change, only that the number is known.

## 4. Feedback: skeleton, spinner, status word, progress

| Pattern | Use in the Studio | Reason | Source |
|---|---|---|---|
| Skeleton screen | Not used | Data is local (measured GET p95 under 115 ms), so the 2 to 10 s range where NN/g recommends skeletons is not reached; NN/g says skip skeletons and spinners under 1 s. A placeholder bar can be read as content or as a status (P1 risk). | E2 |
| Spinner | Only as the indeterminate glyph inside a RUNNING or pending label; it moves at most 5 s, then it is static; the start-time text does not change | Never alone: the word RUNNING or pending accompanies it (colour and motion are never the only carrier). A spinner never implies PASS. | E2, E6, P7 |
| Start-time text | From 1 s after acceptance, written once (for example "since 14:03:12"), never updated | The reader can compute the age without a fabricated estimate. A ticking count was dropped: it is auto-updating information shown beside the STALE verdict and WCAG 2.2.2 gives it no five-second exception (E6). Risk: a static text may read as a frozen job after the glyph stops; measured in the study. Fallback if it does: a ticking count with a visible "Hide elapsed" button | E1, E6 |
| Determinate progress | Only when the kernel reports done and total (Phase 1); the value never exceeds the reported fraction and never shows 100 percent before the terminal outcome | An invented bar is a false status; see the counter-evidence row below | E19 |
| Native `<progress>` | Determinate: `<progress value max>`; indeterminate: no `value` attribute. Set with DOM properties, not a `style` attribute | MDN recommends the native element over the ARIA role; a width set by `style=""` is blocked by the CSP | E19, E24 |
| Estimated time remaining | Not shown | No source supports an honest estimate for a job kind with no history; an ETA would be a claim the kernel did not make | none |
| Perceived-duration tricks | Rejected | One progress-bar augmentation shortened perceived duration by 11 percent in one experiment (E16; baseline not stated in the abstract read), which is the reason to refuse them: the display must describe the job, not manage the reader | E16 |
| Message queue while busy | Not in v1. Input during a job either takes effect or shows why it is blocked within 100 ms | Two interruption speeds exist elsewhere (Cursor: Enter queues, Cmd+Enter steers) but the Studio has one owner and one job at a time | E21 |

## 5. Jobs

### 5.1 States and honesty rules

A job row is a state word plus, where relevant, a count and a start time. States: `pending` (client sent a request, kernel state unknown), `RUNNING` (kernel confirmed a job), then exactly one terminal state from the evidence vocabulary: PASS, FAIL, CONFLICT, UNKNOWN or NOT_RUN. STALE describes the previous verdict, never the new one.

| Rule | Detail | Test |
|---|---|---|
| Prior verdict stays | While a job runs, the previous result for the same subject remains on screen with the word STALE. Dafny does the same: the previous results stay visible while verifying, and obsolete results are shown dimmed (E18). Dimming is never the only cue: the word STALE and a shape are present | MB-07 |
| No PASS by default | Nothing shows PASS, or a count that could be read as PASS, until a terminal outcome arrives. A roll-up with any UNKNOWN never reads PASS (P1) | MB-16 |
| Cancel is not undo | Cancel or abandon shows what it does not restore. VS Code documents that stopping an agent does not undo completed actions or external changes (E20). Cancelled jobs end NOT_RUN with the counts, for example "87 of 125 cells run, no result" | MB-08 |
| Interrupt from the start | Nielsen requires interruption above 10 s (E1). Phase 1 offers Cancel from the start because it costs one control and a job may run for minutes. Phase 0 offers Abandon wait only after the 1 s indicator delay: it leaves the kernel outcome unknown, so it is not shown for a job that finishes in under 1 s | MB-08 |
| Announce sparingly | Start, at most once per 10 s, terminal. Never per progress tick. `role="status"` for progress and results, `alert` only for errors (WCAG 2.2 SC 4.1.3, Level AA, E7) | MB-18 |

### 5.2 Phases

| Phase | Kernel change | What the user sees | What it cannot honestly say |
|---|---|---|---|
| 0 | none | `pending` at once; static start-time text and control "Abandon wait" from 1 s | RUNNING, progress and cancel. The baseline endpoint is one synchronous request. `fetch` abort ends the browser's wait but the kernel continues and commits the receipt (`Studio.verify` runs to completion). So the control must say "The kernel may still finish and record a result" and the case view must be reloaded to show it |
| 1 | needs a kernel-lane ADR: `POST verify` returns 202 with a job id; a job resource reports state and done and total; cancel is a request the kernel honours between cells | RUNNING at accept; determinate progress polled every 250 ms; cancel; NOT_RUN with counts on cancel | PREDICTION: at the p50 of 2096 ms and a 250 ms poll the bar moves about 8 times by about 15 cells each; steps of about 12 percent are visible and are honest |

Interface assumption I-JOB, stated so the kernel lane can accept or refuse it: job state and counts come only from the kernel; the UI never derives progress from elapsed time. Phase 1 polled progress is auto-updating information; whether it needs a pause, stop or hide control under SC 2.2.2 is UNVERIFIED and goes to the Phase 1 ADR.

Recommended order of work: run the D10 commit-batching experiment (kernel lane) before building the Phase 0 UI. If verify drops under 1 s, Phase 0 pending and Abandon wait are unnecessary for it (they stay for slower jobs).

## 6. Authority honesty: what may be optimistic

Optimistic UI shows the expected result while a request is pending and reverts on failure (React `useOptimistic`, E17). That is a valid pattern for view state. It is not valid for anything that stands for the kernel's or the owner's decision, because a reverting "APPROVED" is a false statement about authority (I1, I3, I4).

| Class | Examples | Local prediction allowed | Marker while pending | On refusal or error |
|---|---|---|---|---|
| O0 view state | selection, expansion, filter, palette query, scroll, viewed-mark toggle | yes, applied at once | none | not applicable (no server call). A viewed mark is a reading aid; it never counts as evidence of understanding (ADR-010) |
| O1 presentation | layout drop of a node (`POST layout`) | yes: the node stays at the drop position | dashed outline plus the word "pending" (never colour alone) | node returns to the last committed position over 240 ms; the kernel's reason is shown at the drop target. After a successful commit the UI must also show, from the response, that exact-presentation approval was cleared (ADR-008: the kernel writes `DecisionInvalidated` and returns `decision: null`) |
| O2 typed semantic edit | connector retarget, rename, reparent that maps to a kernel transaction | no: the picture is generated from the model (P3). A ghost of the gesture may follow the pointer; the model view does not change until the response | ghost with "pending" | ghost dissolves in 100 ms; the refusal reason is shown at the target |
| O3 authority and lifecycle | select meaning, save, verify, approve, apply, discard | never | the control shows pending with the exact revision hash it will send | the control returns to its prior state; the error code and message are shown |

Rules that make this testable:

1. The words PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN, RUNNING, APPROVED and APPLIED are written into the DOM only in the handler of a kernel response or job event (MB-16). A mock kernel that delays every commit by 3 s must show no such word before the response.
2. The pending marker is not a status. It has its own glyph and the word "pending", and it is removed by the response (MB-21).
3. Approve enters pending with the subject hash the owner saw. The result is accepted only if the returned decision carries the same subject hash; otherwise the UI shows the kernel's `SUBJECT_CHANGED` refusal.
4. No artificial delay, cooldown or confetti is added to approval. A delay has no supporting evidence here and would shift effort from reading to waiting. Rubber-stamping is measured in the study, not prevented by latency (`PRINCIPLES.md` P2).
5. Rule 1 is the strict form of an asymmetric principle: a client may at most move toward less authority, never toward more. We go further and let the client predict no status at all.

## 7. Motion

### 7.1 Purposes and vocabulary

Motion exists for four purposes and nothing else. Any other motion is a defect.

| Purpose | Used for | Duration token | Properties | Easing |
|---|---|---|---|---|
| feedback | press, selection, focus and hover state change | feedback 100 ms | opacity | enter (ease-out) |
| enter-exit | palette, popover, drawer, tooltip | transient 150 ms, same both ways | opacity, transform (translate at most 8 CSS px) | enter to appear, exit to leave |
| continuity | reflow after expand or collapse; node settle after relayout; return of a refused drop | continuity 240 ms, cap 400 ms for the longest travel | transform | move (ease-in-out) |
| progress | indeterminate glyph while a job has no progress signal | linear, at most 5 s, then static | transform | linear (the only permitted linear, because it does not move an object) |

Values: durations {100, 150, 240, 400} ms follow NN/g, which gives about 100 ms for simple feedback, 200 to 300 ms for substantial changes and up to 400 ms for large movements, and says animations are far more often too long than too short (E3). Curves are the CSS keyword curves: ease-out `[0, 0, 0.58, 1]`, ease-in `[0.42, 0, 1, 1]`, ease-in-out `[0.42, 0, 0.58, 1]` (E28). Only `transform` and `opacity` are animated because they can run on the compositor without layout or paint (E11).

Forbidden: animating `width`, `height`, `top`, `left`, `filter`, `backdrop-filter`; looping motion after 5 s; stagger delays; bounce or overshoot; entrance animation on first load; any motion whose only effect is decoration; a success animation on Approve or Apply.

### 7.2 Diff transitions and object constancy

Object constancy means the reviewer can keep tracking the same thing across two states. Evidence for animation here is indirect (E13 to E15) and every study read was on visualisations, not on review lists, so the design keeps motion small and switchable.

| Situation | Behaviour | Why |
|---|---|---|
| Next revision replaces the current one | Items are matched by stable operation id. Matched items keep their place; changed items keep their place and change their marks; ADDED items appear with no motion beyond a 100 ms opacity fade; REMOVED items remain in the list with the word REMOVED and a shape (nothing vanishes) | The word and glyph carry the change (P4, P6). Motion never carries meaning |
| Chapter or ripple row expands | Sibling rows below move by FLIP: measure First, apply the change, measure Last, Invert with a transform, Play over 240 ms (E22). Content fades in over 100 ms | Compositor-only; siblings keep their identity |
| Kernel-generated relayout after a typed edit | Nodes whose generated position differs move together over 240 ms, one group, no stagger. Travel longer than 240 ms of normal speed is capped at 400 ms | Bederson and Boltman found animated viewpoint transitions helped users rebuild a spatial mental map without slowing tasks (E13, abstract-level, spatial data viewpoint changes, 1999). Heer and Robertson found animated transitions improved graphical perception in statistical graphics and staged them (E14, abstract-level). Chevalier et al. list maintaining context as one of six roles of animation (E15). No source tested this design |
| A drop is refused | Node returns to the last committed position over 240 ms; the reason appears at the drop target | Shows where it went back to |
| A viewed mark clears because the operation hash changed | Instant change of the mark and its word; no pulse | The state is persistent, so a missed animation loses nothing |

Not used: highlight flashes, attention pulses, view-transition cross-fades. The View Transition API can assign persistent identity with `view-transition-name` and cross-fades by default (E29). Its support is no longer the obstacle: the web-features explorer lists same-document view transitions as Baseline Newly available since 2025-10-14 (Chrome 111, Edge 111, Firefox 144, Safari 18; E34). FLIP with the Web Animations API is a hand-written substitute for something the browser now offers. The deferral stands on three points not yet tested: behaviour under the strict CSP, reduced-motion handling (the MDN pages read do not mention it), and the default cross-fade against our rule of no flashes and no decoration. A smoke test for these goes into the probe; if it passes, replace FLIP for sibling reflow and record a new ADR.

### 7.3 Interruptibility

No animation blocks input. Pointer events are never disabled during a transition. A new gesture cancels or finishes the running animation to its end state (`Animation.finish()` or `cancel()` in the Web Animations API) and starts from the resulting layout. Test MB-19 dispatches a click 50 ms into a 240 ms transition and requires the effect within 100 ms.

### 7.4 Under the strict CSP

The Studio serves `style-src 'self'` and `script-src 'self'` with no inline script or style (E32, `http.py`). MEASURED 2026-09-29 in Chrome 154 on Windows with the baseline CSP (E24):

| Technique | Result |
|---|---|
| `element.setAttribute('style', ...)` | blocked; one `style-src-attr` violation reported, computed style unchanged |
| `element.style.color = ...`, `element.style.setProperty('--x', ...)` (CSSOM) | works, no violation |
| `element.animate(...)` (Web Animations API) | creates and reports `running`; frames not observed (hidden tab) |
| SVG `transform` attribute on a `<g>` | works; `transform.baseVal` reads it back |
| `CSSStyleSheet.replaceSync` plus `adoptedStyleSheets` | works, no violation |

Consequences: all motion is CSS in the shipped stylesheet or the Web Animations API; per-element values go through CSSOM custom properties; canvas nodes move with the SVG `transform` attribute; progress uses `<progress>`. Not tested: a same-origin Web Worker for layout (`worker-src` falls back to `script-src`; open contradiction C15 in `SYNTHESIS.md`), and playback of animations in a visible tab. Both go in the probe.

## 8. Canvas drag budget

The canvas is a projection of the executable model (P3). During the gesture nothing in the model changes; only the picture of one node moves.

| Item | Rule |
|---|---|
| Pipeline | `pointermove` handlers only record the latest pointer position. One `requestAnimationFrame` callback per frame writes the SVG `transform` of the dragged node and updates the path data of its incident edges. No layout engine call, no `fetch`, no model read in the frame loop |
| Cost model | Work per frame is proportional to one node plus its incident edges, not to the graph. No constant for milliseconds per edge is available (not measured), so this document offers no per-frame prediction; the budget is a test, not a forecast |
| Budget (60 Hz reference) | Main gate: p95 main-thread work per move frame at most 10 ms (DERIVED: RAIL says the browser needs about 6 ms of a 16 ms frame, so 10 ms is left, E9; RAIL is a legacy page). Frame interval: nominal period 16.7 ms (DERIVED, not a limit); fail if p95 interval exceeds 20 ms or more than 5 percent of frames exceed 25 ms (1.5 periods); both tolerances are TARGET hypotheses to calibrate, because a healthy vsync-locked run jitters around 16.7 ms and a hard 16.7 ms p95 would fail or pass by chance. Zero long animation frames (over 50 ms, E25) during a drag; pointerdown to first response at most 50 ms target and 100 ms limit |
| Refresh rates | The probe measures the display rate first (median `requestAnimationFrame` interval over 1 s idle) and reports MB-09 only between 55 and 65 Hz; on 120 or 144 Hz the frame rows are reported not comparable, so a fast display cannot pass the 60 Hz test trivially. The reference PC's own display rate is UNKNOWN until the probe runs. Zed states 8.33 ms per frame at 120 FPS and built its own GPU UI framework to meet it (E10, vendor); we do not claim that for an SVG DOM |
| Scale | Budget defined up to 100 nodes and 200 edges. Above that the canvas shows a visible cap message; it does not degrade silently (precedent in `diagramming-and-uml-tools.md` section 5 item 9). The excursion model has 5 states, so the measured range is trivially inside |
| Drop | One `POST` per drop. The node stays at the drop position with the pending marker (class O1). Commit ack per MB-03; refusal return per MB-11 |
| Layout engine | Automatic layout (elkjs in a same-origin worker, a proposal of the diagram lane) runs off the main thread on request, never per frame. Regeneration after a typed edit: target 400 ms on the excursion model (hypothesis from the diagram dossier, unmeasured) |
| Not used | `PointerEvent.getCoalescedEvents()`: MDN lists limited availability and a secure-context requirement (E30) |

## 9. Reduced motion

`prefers-reduced-motion` takes `no-preference` or `reduce`; it has been widely available since January 2020 (E4). Reduce means the user asked for less motion, not none, and scaling or panning of large objects is the trigger MDN names for vestibular disorders (E4).

| Under `reduce` | Behaviour | WCAG |
|---|---|---|
| feedback | unchanged (opacity, 100 ms) | opacity and colour changes fall outside the SC 2.3.3 definition of motion animation (E5) |
| enter-exit | opacity only, 100 ms; no translate | E5 |
| continuity | instant; the reasons and marks are already in text | E5 |
| progress | no moving glyph; static glyph plus the word and the start-time text | E6 |
| refused drop | node jumps back; the reason is shown | E5 |

SC 2.3.3 is Level AAA; we conform anyway because the cost is one media query and the token file. SC 2.2.2 (Level A) requires a way to pause, stop or hide moving content that starts automatically and lasts more than five seconds; the 5 s cap on indeterminate motion meets that for the glyph (E6, which also has a preloader exception for content not shown in parallel with other content). It does not cover auto-updating information: the same page says there is no five-second exception for it. A once-per-second elapsed ticker shown beside the STALE verdict would therefore need a pause, stop or hide control unless essential, so the ticker is withdrawn and a start time is written once. Phase 1 polled progress is still open (UNVERIFIED). Earlier drafts marked SC 2.2.2 as a pass by specification for the whole job row; that was wrong for the ticker. SC 2.3.1 (no more than three flashes in any one second, Level A, E33) is met by having no flashing element; nothing here flashes.

Motion-free equivalence (MB-15): capture the DOM text and state attributes after calling `finish()` on every running animation; capture it again with all motion disabled; they must be identical. That is what "motion never carries meaning" means as a test.

## 10. Budgets as tests

Threshold is the fail value (a literature limit or a hard rule); target is the warn value. All latency values are p95 over at least 30 trials in a visible Chromium on the reference PC, three repetitions, worst run reported, at 1440x900 and 1280x720. Status column: nothing is implemented, so every row is UNKNOWN until its probe runs.

| Id | What | Fail | Warn (target) | Method | Basis | Status |
|---|---|---|---|---|---|---|
| MB-01 | direct: input to next paint (proxy: `event.timeStamp` to the first `requestAnimationFrame` followed by a `MessageChannel` message) | over 100 ms | over 50 ms | probe with synthetic pointer and key events | E1 TARGET | UNKNOWN |
| MB-02 | view: click on a tree row to the facet lane updated | over 1000 ms | over 200 ms | probe | E1, E8, E12 | UNKNOWN |
| MB-03 | commit: press to kernel response applied to the DOM | over 1000 ms | over 300 ms | probe against the real kernel | E1, E12, E23 | server side MEASURED (p95 26 to 214 ms); browser UNKNOWN |
| MB-04 | job accept and direct feedback: press to pending or RUNNING visible | over 100 ms | over 50 ms | probe | E1 | UNKNOWN |
| MB-05 | no spinner, skeleton, start-time text or Abandon wait control before 1000 ms; start-time text (and, in Phase 0, Abandon wait) present by 1100 ms and unchanged afterwards (no auto-updating text node in the job row) | any earlier, none by 1100 ms, or any later text mutation | none | probe with a mock kernel delayed 500 ms, 1500 ms; MutationObserver on the job row | E1, E2, E6 | UNKNOWN |
| MB-06 | determinate progress only from kernel data; poll age at most 250 ms; no 100 percent before the terminal outcome; above 10 s a percentage or the words "no progress signal" | any breach | none | mock job with scripted progress | E1, E19 | UNKNOWN (Phase 1) |
| MB-07 | prior verdict remains with the word STALE while RUNNING | missing | none | DOM assertion during a 3 s mock job | E18 | UNKNOWN |
| MB-08 | cancel or abandon control present from RUNNING; its press changes state within 100 ms; end state NOT_RUN with counts and a not-restored string | any breach | none | mock job | E1, E20 | UNKNOWN |
| MB-09 | drag frames at a measured 55 to 65 Hz display, N of 100 nodes: p95 script per move at most 10 ms (main gate); p95 frame interval at most 20 ms; share of frames over 25 ms at most 5 percent; long animation frames (over 50 ms) equal 0. Outside 55 to 65 Hz: reported not comparable | any breach | none | probe with scripted pointer path, `PerformanceObserver` for `long-animation-frame` (MDN says feature detection is needed, E25) | E9, E25 | UNKNOWN |
| MB-10 | above 100 nodes or 200 edges a visible cap message appears; frame budget not silently missed | silent | none | synthetic graph of 120 nodes | DGM | UNKNOWN |
| MB-11 | refused drop returns in at most 240 ms with a reason at the drop target | any breach | none | mock kernel returning 409 | this doc | UNKNOWN |
| MB-12 | typed edit drop to regenerated picture | none | over 400 ms | probe on the excursion model | DGM | UNKNOWN |
| MB-13 | animation durations within {100, 150, 240, 400} ms; none over 400; only `opacity` and `transform`; no `filter` or `backdrop-filter` | any breach | none | static scan of the stylesheet and `getAnimations()` at runtime | E3, E11 | token file checked by script: animation durations are exactly 100, 150, 240 and 400 ms; the fifth duration token (5000 ms) caps indeterminate motion and is not an animation duration; transition recipes list only opacity and transform. Runtime check UNKNOWN |
| MB-14 | under emulated `reduce`: `getAnimations()` returns none with a non-opacity property; opacity animations at most 100 ms | any breach | none | Chromium media emulation | E4, E5 | UNKNOWN |
| MB-15 | motion-free equivalence of DOM text and state | any difference | none | snapshot compare | this doc | UNKNOWN |
| MB-16 | status and authority words appear only after a kernel response: with a 3 s delayed mock, none before the response; after a 409, none | any breach | none | mock kernel | ADR-004, ADR-008, E17 | UNKNOWN |
| MB-17 | any input during a job yields its effect or a visible reason within 100 ms; no silent drop | any silent drop | none | scripted clicks during a job (the baseline fails this by construction: `if(busy)return;`) | E32 | baseline FAIL by source reading; proposed UNKNOWN |
| MB-18 | live-region announcements: start, at most one per 10 s, terminal; none per tick | any breach | none | live-region mutation log | E7 | UNKNOWN |
| MB-19 | click 50 ms into a 240 ms transition takes effect within 100 ms; no `pointer-events: none` during transitions | any breach | none | probe | E3 | UNKNOWN |
| MB-20 | indeterminate motion stops at 5 s | over 5100 ms | none | probe | E6 | UNKNOWN |
| MB-22 | View Transition smoke test (not a gate for shipping): same-document `startViewTransition` raises no CSP violation, honours emulated `reduce`, and the default cross-fade can be disabled or made instant | any breach means the API stays deferred | none | probe in one Chromium | E29, E34 | UNKNOWN |
| MB-21 | every pending marker has the word "pending" and a glyph, and is removed by the response | any breach | none | DOM assertion | this doc | UNKNOWN |

Pass criteria fixed before running: every row above, and any FAIL blocks merge of the code that owns the action. WARN rows are recorded and shown in the report next to the reference value, not hidden.

## 11. User-study slice

Protocol owner: the study lane. This slice states what motion and performance add, without claiming a benefit.

| Item | Proposal |
|---|---|
| Design | Within-subject, tween layer on (ADR option C) versus tween layer off (option D, durations set to 0), counterbalanced order, on the excursion workflow; baseline Studio as a third reference for T06 and T08 |
| Tasks | T02 open chapters, T04 move a node and see the relayout, T06 verify and read the outcome, T08 approve with a deliberately delayed commit, T11 resolve a stale item |
| Participants | About 5 per formative round; about 20 or more for a quantitative comparison; a cohort with reduced motion enabled (LAW§2.10, `SYNTHESIS` sample-size notes) |
| Measures | Time on task; errors; recall of where each node was before a relayout (mental-map check); UNKNOWN or STALE read as PASS during and after a job (target zero); a static start time read as a frozen job (count, asked after a job over 5 s); report of "approved" before the kernel response in the seeded delayed-commit trial (target zero); SEQ per task; Raw NASA-TLX; SUS at the end with an interval |
| Stop criteria | Stop and redesign if any participant reports an authority state that the kernel had not committed; default the tween layer to off if the on condition is slower by more than a pre-registered margin with a confidence interval that excludes zero (the margin is set before the study; 10 percent is our placeholder, no source) |
| Status | No results. No claim of user benefit is made. |

## 12. Sources and open items

MEASURED by this lane: E23 latency probe, E24 CSP test, E31 kernel profile, E32 source reading.

| Id | Source | URL | Type | Confidence |
|---|---|---|---|---|
| E1 | NN/g, response time limits (1993, updated 2014) | https://www.nngroup.com/articles/response-times-3-important-limits/ | practitioner research | high |
| E2 | NN/g, skeleton screens (2023-06-04) | https://www.nngroup.com/articles/skeleton-screens/ | practitioner research | medium |
| E3 | NN/g, animation duration (2020-02-09) | https://www.nngroup.com/articles/animation-duration/ | practitioner research | medium |
| E4 | MDN, `prefers-reduced-motion` | https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion | official documentation | high |
| E5 | WCAG 2.2 Understanding SC 2.3.3, Level AAA (errata: blur no longer excluded from the definition) | https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html | standard | high |
| E6 | WCAG 2.2 Understanding SC 2.2.2, Level A (5 s applies to moving content; auto-updating has no 5 s exception) | https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html | standard | high |
| E7 | WCAG 2.2 Understanding SC 4.1.3, Level AA | https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html | standard | high |
| E8 | web.dev, Interaction to Next Paint | https://web.dev/articles/inp | official documentation | high |
| E9 | web.dev, RAIL (legacy, points to Core Web Vitals) | https://web.dev/articles/rail | official documentation | medium |
| E10 | Zed blog, GPUI frame budget | https://zed.dev/blog/videogame | first-party blog | medium (vendor) |
| E11 | web.dev, high-performance CSS animations | https://web.dev/articles/animations-guide | official documentation | high |
| E12 | Doherty and Thadani table, transcription | https://jlelliotton.blogspot.com/p/the-economic-value-of-rapid-response.html | secondary transcription | medium |
| E13 | Bederson and Boltman 1999, InfoVis'99, DOI 10.1109/infvis.1999.801854 (abstract via OpenAlex) | https://api.openalex.org/works?search=Does%20animation%20help%20users%20build%20mental%20maps%20of%20spatial%20information | peer-reviewed, abstract only | medium |
| E14 | Heer and Robertson 2007, IEEE TVCG, DOI 10.1109/tvcg.2007.70539 (abstract via OpenAlex) | https://api.openalex.org/works?search=Animated%20transitions%20in%20statistical%20data%20graphics | peer-reviewed, abstract only | medium |
| E15 | Chevalier et al. 2016, AVI, DOI 10.1145/2909132.2909255 (abstract via OpenAlex) | https://api.openalex.org/works?search=Animations%2025%20years%20later | peer-reviewed, abstract only | medium |
| E16 | Harrison et al. 2010, CHI, "Faster progress bars", DOI 10.1145/1753326.1753556 (abstract via OpenAlex) | https://api.openalex.org/works?search=Faster%20progress%20bars%20manipulating%20perceived%20duration%20with%20visual%20augmentations | peer-reviewed, abstract only | medium |
| E17 | React docs, `useOptimistic` | https://react.dev/reference/react/useOptimistic | official documentation | high |
| E18 | Dafny blog, verification feedback (2023-04-19) | https://dafny.org/blog/2023/04/19/making-verification-compelling-visual-verification-feedback-for-dafny/ | first-party blog | medium |
| E19 | MDN, ARIA `progressbar` role | https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/progressbar_role | official documentation | high |
| E20 | VS Code docs, agent sessions | https://code.visualstudio.com/docs/copilot/agents/overview | official documentation | medium |
| E21 | Cursor docs, agent overview | https://cursor.com/docs/agent/overview | official documentation | medium |
| E22 | Lewis, FLIP your animations | https://aerotwist.com/blog/flip-your-animations/ | practitioner write-up | medium |
| E23 | MEASURED server latency probe (section 3.1) | `.tmp/latency/probe.py`, `result.json` | own measurement | medium (n = 20, shared PC) |
| E24 | MEASURED CSP behaviour of style APIs (section 7.4) | http://127.0.0.1:8792 during the session | own measurement | medium (hidden tab, one browser) |
| E25 | MDN, Long Animation Frame timing | https://developer.mozilla.org/en-US/docs/Web/API/Performance_API/Long_animation_frame_timing | official documentation | medium |
| E26 | Design Tokens Format Module 2025.10 | https://www.designtokens.org/tr/2025.10/format/ | community group report | high |
| E27 | KLM operator times (B is per button press or release; a click is 2B) | https://en.wikipedia.org/wiki/Keystroke-level_model | secondary | medium |
| E28 | MDN, `<easing-function>` | https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function | official documentation | high |
| E29 | MDN, View Transition API and Using guide | https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API | official documentation | medium |
| E30 | MDN, `PointerEvent.getCoalescedEvents()` | https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/getCoalescedEvents | official documentation | medium |
| E31 | MEASURED verification profile (section 3.3) | `.tmp/latency/prof.py` | own measurement | medium |
| E33 | WCAG 2.2 Understanding SC 2.3.1, Level A | https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html | standard | high |
| E32 | Baseline source reading | `src/eija_studio/resources/web/*`, `src/eija_studio/interfaces/http.py` | primary | high |
| E34 | web-features explorer, view transitions (Baseline Newly available since 2025-10-14) | https://web-platform-dx.github.io/web-features-explorer/features/view-transitions/ | official (WebDX community group) | medium |

Argues against parts of this design: E16 (a progress augmentation shortened perceived duration by 11 percent in one experiment; we refuse it on honesty grounds, so we forgo that effect), E17 (optimistic UI is the mainstream pattern for perceived speed; we restrict it), E10 (fast UIs are built by making the work faster, not by explaining the wait; D10 records that the largest win may be a kernel change).

UNVERIFIED or not opened, and not built on:

- Origins of the 0.1, 1 and 10 s limits (Miller 1968, Card et al. 1991).
- Any "400 ms Doherty threshold" (not in the text read).
- Carbon and Material motion tokens: the Carbon pages returned 404 or truncated content; the dossier values (`visual-design-foundations.md` section 2.9) were not re-opened, so durations here are justified by NN/g only.
- Superhuman's 100 ms target (`developer-tool-craft-benchmarks.md`, not re-opened).
- View Transition API behaviour under this CSP and under reduced motion (Baseline status is now verified, E34); Web Worker under this CSP (C15); animation playback in a visible tab; Event Timing API details; whether Phase 1 kernel-polled progress needs a pause, stop or hide control under SC 2.2.2 (the ticker question is settled: it does, so it is withdrawn); the reference PC's display refresh rate.
- Live provider and long-job durations (model check, mutation, TLC); browser-side latency and frame intervals.
- Bederson and Boltman, Heer and Robertson, Chevalier and Harrison: only abstracts were read through OpenAlex; results are not quoted beyond the abstract.

Interfaces to other aspects (assumptions, not decisions):

| Aspect | Assumption |
|---|---|
| colour | pending, RUNNING, STALE and NOT_RUN each have a shape and word; contrast of these marks is theirs to compute (UNKNOWN here) |
| layout and canvas | the canvas is SVG DOM with stable node ids; keyboard move commands provide the non-dragging path (WCAG 2.5.7); the pending marker fits in a row without a new container |
| interaction and palette | no palette command reaches approve or apply; palette open is a direct-class action |
| kernel | Phase 1 job endpoint and cancel are proposals for the kernel lane's ADR; nothing here edits the kernel |
| slop budget | the job row adds at most 8 words ("RUNNING 3 s, Cancel" style) and no container |
