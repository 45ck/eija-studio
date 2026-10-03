# HCI laws and quantitative models for EIJA Studio

Status: research dossier, lane `ux`. Access date for every URL: 2026-09-29. Author: research agent (not a user study).
Scope: which laws and instruments we may use to justify Studio layout, interaction cost, latency, colour and visual density; their formulas, validity limits, how to make each an executable model, and a unit-test oracle for each.

Read this first:

- Everything computed from these laws is a **PREDICTION**. None of it is a measurement of a human and none of it shows that developers will find the Studio pleasant. "Feels good" is not a quantity these laws predict. It is measured only by the study protocol (SUS, SEQ, NASA-TLX, section 2.10), which this dossier does not run.
- Constants (a, b, K, M, P) are device-, task- and population-specific. Oracles below test the **formula**, given stated constants. They do not certify the constants.
- Anything marked UNVERIFIED was not read in a primary or authoritative form this session and must not be built on.

## 1. Scope and method

**Evidence levels used in the tables.**

| Code | Meaning |
|---|---|
| P | Primary paper text read this session (PDF converted locally with `pdftotext`; the KLM paper is a scan, so its OCR is partly garbled and only clearly legible numbers are used) |
| A | Authoritative summary or official documentation page fetched (NN/g, W3C, Design Tokens CG, NASA, author's own site) |
| S | Secondary page fetched (Wikipedia, blog transcription). Used for formulas that agree with a P source or as a lead only |
| M | Bibliographic record only (Semantic Scholar API: title, year, venue, and abstract where the publisher exposes it). The paper body was not read |
| U | UNVERIFIED |

**Method.** About 12 WebSearch queries (the shared session budget of 200 was then exhausted by other agents), then WebFetch and `curl` on the pages in section 7. WebFetch returns a small-model summary of a page, not the page. So any number that matters here was cross-checked against a locally converted PDF where one existed (Cockburn, Soukoreff and MacKenzie, Accot and Zhai, Card et al., Horvitz, Green and Blackwell). Numbers that rest only on a summary are marked "medium".

**Not accessible** (403, 404, certificate error, or a bot wall): Fitts 1954 and Hyman 1953 (APA), Lindgaard 2006 (T&F, body), Sweller 1988 (Wiley), Reinecke 2013 PDF (AWS WAF), Miniukovich and De Angeli 2015 (ACM 403; abstract via API), John and Kieras 1996 (ACM), Green and Petre 1996 (PDF 404; the Green and Blackwell 1998 tutorial was read instead), NASA-TLX site (fetch failed; Wikipedia used), the IBM copy of Doherty and Thadani (certificate error; a blog transcription was read), MacKenzie 2013 HCI book chapters (404), and web.archive.org (blocked in this tool). Pirolli and Card 1999 was not readable (not found by DOI); NN/g's summary was used.

## 2. Laws, formulas, limits, oracles

### 2.1 Fitts's law (pointing)

| Item | Content | Source, level |
|---|---|---|
| Original | ID = log2(2D/W); IP = ID/MT. D = distance to target centre, W = target width along the movement axis | Fitts 1954 (M); formula via S1 (S) |
| Shannon form (use this one) | MT = a + b*ID, ID = log2(D/W + 1), MT in s, ID in bits, b in s/bit. Never negative. Original form goes negative when D < W/2 | MacKenzie 1992 (A: author site) |
| Welford 1968 | MT = a + b1*log2(D) + b2*log2(W) | S1 (S) |
| Effective width | We = 4.133 * SDx (SD of end-point coordinates on the approach axis); IDe = log2(D/We + 1); throughput TP = IDe/MT in bits/s | Soukoreff and MacKenzie 2004 (P) |
| Constants seen | Card et al. 1978 mouse, Welford form: a = 1030 ms, b = 96 ms/bit, IP about 10.4 bits/s (medium, via summary). Cockburn et al. 2007 menu pointing, 8 participants, mouse: MT = 0.37 + 0.13*ID s, R2 = 0.93 | S2 (A, medium); S4 (P) |

**Validity limits and misuse.**

- Fit is good for ID roughly 2 to 8 bits; predictions must stay inside the IDe range that was tested, and the intercept is not "time for a zero-distance move" (Soukoreff and MacKenzie recommendations II, V, VI, P).
- Nominal W misleads. Use effective width when comparing conditions (recommendations III and IV, P). The 4.133 factor equals 2*z(98.06 %) and corresponds to about 4 % of end-points outside the target (checked: 3.88 %).
- 1-D law. For rectangles we must choose W. Assumption (ours, not from a paper we read): use the smaller of w and h, which is conservative. Flag as an assumption in every layout run.
- Says nothing about visual search, choice or reading. Do not use it for those.

**Executable.** `fitts_mt(D, W, a, b) -> s` on layout geometry: D is centre-to-centre pixel distance between `from` and `to` elements in `design/layouts/*.json`. Ship constants as an explicit `profile` (mouse, 96 dpi) and report `ID` next to `MT`.

**Oracles (computed, exact).** ID(D=W) = 1.000 bit; ID(D=7W) = 3.000; ID(D=15W) = 4.000; Fitts original at D = W/4 gives -1.000 (the defect the Shannon form removes). With Cockburn constants MT(D=7W) = 0.37 + 0.13*3 = 0.760 s. Effective width: SDx = 2 px gives We = 8.266 px; D = 200 px gives IDe = 4.655 bits; MT = 0.9 s gives TP = 5.17 bits/s.

**Verdict: adopt** (Shannon form, effective-width TP only if we ever measure).

### 2.2 Steering law (Accot and Zhai 1997)

T = a + b * integral over path C of ds/W(s); for a straight tunnel of length A and constant width W, T = a + b*A/W. Derived by recursion from Fitts goal-passing: ID_N = N*log2(A/(N*W) + 1), which tends to A/(W*ln2) as N grows, so difficulty becomes linear in A/W, not logarithmic (P: S8). Experimental fits report r2 of 0.97 to 0.99, and the paper says errors were much higher than in Fitts tasks (P). The sign of the reported intercepts is garbled in the extracted text, so we use no constants. NN/g derives menu advice: shorter menus, no cascades beyond two levels, wider padding, a triangular hover buffer (A: S10).

Limits: applies to constrained path steering only (cascading menus, sliders, scrubbers, dragging a connector through a channel); the constants are pen-tablet constants from 1997.

Executable: `steering_id(A, W_of_s)` by numeric integration. **Oracle:** for A/W = 10, ID_N = 3.459 (N=1), 5.170 (N=2), 10.000 (N=10), 13.750 (N=100), limit 14.427 = 10/ln 2. Property test: doubling W halves the linear ID.

**Verdict: adapt**, only for connector drag routes in the UML canvas and any cascading menu. We avoid cascades instead.

### 2.3 Hick-Hyman law (choice)

T = a + b*H, with H = log2(1/p) per alternative; for C equiprobable alternatives T = a + b*log2(C); the common "+1" form is T = b*log2(n+1) (P: S4; S: S7). Hyman 1953 varied number, proportion and sequential probability of alternatives (M; abstract via search snippet only).

Constants (P: S4): expert, stable familiar menus, 2 to 12 items, 8 participants: T = 0.24 + 0.08*log2(n) s, R2 = 0.98. Novice or randomised menus: visual search T = 0.30 + 0.08*n s, R2 = 0.99.

**Validity limits, from Cockburn et al. (P).** The law holds when items are **stable in position** and the user is practised; before that, search time is linear in n. Hick and Hyman timed decisions to clear stimuli, not visual search; models that applied it to visual search failed (Sears et al., Soukoreff and MacKenzie, as reported in S4). Seow (2005, M) is the review of why Hick-Hyman gained less traction than Fitts. Verbal and saccade responses violate it (S7, S). "Fewer choices is always faster" is a misuse: it is logarithmic for experts and linear for novices, and grouping (chunking) changes n.

Executable: `hick_time(n_or_probs, a=0.24, b=0.08)` and `search_time(n)`, blended by an expertise weight e in [0,1] as Cockburn does (the blend equation itself was not reproduced here). **Oracle:** n=8 gives 0.480 s; n=12 gives 0.527 s; novice n=12 gives 1.260 s; probabilities (0.5, 0.25, 0.125, 0.125) give H = 1.75 bits.

**Verdict: adapt.** Use only for stable-position command sets and the ordering of tree siblings. Never for search boxes (typing narrows the set).

### 2.4 KLM and GOMS (task time)

KLM (Card, Moran and Newell 1980, P): T = sum of operators. Legible values in the paper's operator table: K 0.08 s (best typist, 135 wpm), 0.12 (90 wpm), 0.20 (average skilled, 55 wpm), 0.28 (40 wpm), 0.50 (random letters), 0.75 (complex codes), 1.20 (worst); P (point with mouse) 1.1 s average; H (home) 0.40 s; M (mental preparation) 1.35 s, fitted from their data (R2 = .84, SD of M about 1.1 s); D = 0.9*nD + 0.16*lD s (S6, agrees with the paper's form). B (button press) 0.10 s is the later refinement (S6, S; the 1980 paper folds it into a K-like term, OCR ambiguous). Placement rules 0 to 4 for M are in the paper (S5, S6).

Accuracy stated by the authors (P): RMS prediction error 21 % for individual unit tasks with the paper's own M fit, and about 5 to 6 % when predicting the total of several tasks. Cockburn et al. call the 1.35 s M "crude" (P: S4).

GOMS variants: KLM, CMN-GOMS, NGOMSL, CPM-GOMS; applies to **skilled, error-free** performance only, not learning, errors, fatigue (S42, S). CPM-GOMS predicted a 3 % productivity decrease at a telephone-operator workstation; the observed decrease was 4 % (S42, S: medium). John and Kieras 1996 (M) is the comparison paper. CogTool (CMU, LGPL-2.1, generates a KLM-style ACT-R prediction from a storyboard) exists but its GitHub repo showed 15 commits, moved 2013, so treat it as unmaintained reference, not a dependency (A: S41).

**Misuse.** Reporting a single total as a fact; ignoring that M count is a judgement; applying to novices or to review tasks where time is dominated by reading and deciding.

Executable: interpret `design/tasks/*.json` op by op: M 1.35, K 0.20 per key (a chord "cmd+k" is 2 K unless flagged), T `chars`*0.20, P from Fitts when `layout` is given else 1.1, B 0.10, H 0.40, R as stated, D via Fitts+B or the D formula (flag). Output a point estimate **and** a band of plus or minus 21 % labelled PREDICTION.

**Oracle (ours, from the table values):** M + P + B + H + 24 K (typing 24 chars at 0.20) = 1.35 + 1.10 + 0.10 + 0.40 + 4.80 = **7.75 s**. Property tests: inserting an R of x ms adds exactly x ms; removing an M (Rule 1, fully anticipated) lowers T by 1.35 s.

**Verdict: adopt** for current-vs-proposed flow comparison of expert, frequent tasks (daily and weekly). Do not use for first-run or review-quality claims.

### 2.5 Working memory: Miller and Cowan

Miller 1956 (P: S11): absolute judgment on one dimension is about 2.5 bits (about 6 categories); memory span is about 7 items and depends on chunks, not bits; recoding into chunks is the lever. Miller himself judged the recurrence of seven as coincidence. Cowan 2001 (abstract via M): the capacity is about 3 to 5 chunks when rehearsal and chunking are prevented; the "7 plus or minus 2" was "a rough estimate and a rhetorical device". The PMC review agrees (A/S: S12: 3 to 5 chunks; conditions: brief array, blocked rehearsal).

**Misuse.** "Menus and navigation may have at most 7 items". That confuses a memory-span limit with a display limit; visible items need not be remembered. The limit applies to what must be **held in mind** while comparing.

Executable: `wm_demand(task) -> int`: the number of independent chunks a reviewer must hold to decide (for example old rule, new rule, affected state, affected test). Budget default 4, with a stated uncertainty of 3 to 5. **Oracle:** 2^2.5 = 5.66 categories; log2(7) = 2.81 bits.

**Verdict: adapt** as a design budget for the "review by meaning" summary (at most 4 top-level chunks per change), not as a count of visible items.

### 2.6 Response time: Nielsen, Miller, Doherty and Thadani

NN/g (A: S13): 0.1 s feels instantaneous (direct manipulation feedback needs nothing more); 1 s keeps the flow of thought (show that work is happening in the 0.1 to 1 s range); 10 s is the limit of attention (needs percent-done and a way to interrupt). Cited origins: Miller 1968, Card et al. 1991 (primary not opened).

Doherty and Thadani 1982 (S: blog transcription of the IBM text): system response time (SRT) is the span from entering a command to the complete response. Programmer throughput from Thadani's data: 3.0 s SRT gives 180 transactions/hour, 2.0 s gives 208, 1.0 s gives 252, 0.6 s gives 279, 0.3 s gives 371 (+106 % from 3.0 to 0.3). The authors reject the old "2 s is acceptable" model because people hold a sequence of actions in a short-term buffer that slow responses disrupt. **In the text read, no 400 ms threshold appears**; the "400 ms Doherty threshold" is a later popularisation (attached by secondary sites, U as a finding of the paper). Transcription also has an internal inconsistency: the 0.6 s row lists 37.7 min task time, but 180 tasks at 279/h is 38.7 min.

Limits: 1980s terminal transactions by programmers; not generalisable to AI agents whose latency is seconds to minutes.

Executable: `latency_band(ms) -> {instant, flow, attention, abandon}` with thresholds 100, 1000, 10000 ms. Every UI action declares a budget class; a browser probe (one browser only) records p95 per action. **Oracle:** 99 ms instant; 100 to 999 flow; 1000 to 9999 attention; 10000 and above abandon (boundary convention is ours). Data oracle: think time = 3600/tph - SRT gives 17.00, 15.31, 13.29, 12.30, 9.40 s for the five rows.

**Verdict: adopt** the 0.1/1/10 classes; **avoid** quoting "400 ms" as a finding.

### 2.7 Cognitive Dimensions of Notations (Green and Petre)

Framework for evaluating notations and environments by trade-offs (Green and Petre 1996, M; Green and Blackwell 1998 tutorial, P/A: S15). Dimensions (tutorial one-line definitions): abstraction (types and availability of abstraction mechanisms), hidden dependencies (important links not visible), premature commitment (constraints on order of doing things), secondary notation (extra information outside formal syntax), viscosity (resistance to change), visibility (ability to view components easily), closeness of mapping, consistency, diffuseness, error-proneness, hard mental operations, progressive evaluation, provisionality, role-expressiveness. Viscosity has two kinds: repetition (one goal needs many repeated actions) and knock-on (one change forces further actions to restore consistency). The tutorial's examples: changing US to UK spelling throughout a document (repetition); inserting a figure that forces renumbering of later figures (knock-on).

Limits: qualitative and broad-brush; the tutorial itself lists trade-offs (reducing viscosity by adding abstractions raises the need for lookahead). No constants exist.

Executable (our operationalisation, a PREDICTION about effort, not a validated metric): **knock-on viscosity = number of manual edits needed to restore consistency after one conceptual change**. **Oracle:** a figure inserted before 5 manually numbered figures gives 5; with automatic numbering gives 0. For EIJA: rename a ubiquitous-language term; count artefacts that are not auto-updated (state, journey, test, persona, requirement) and require the owner to touch them. Target: 0 unreviewed silent changes, and every knock-on shown in a ripple list.

**Verdict: adopt** as the review vocabulary for the whole Studio: hidden dependencies (the ripple view), viscosity (rename and refactor), provisionality (an AI proposal is visibly provisional), visibility (UNKNOWN stays visible), premature commitment (do not force the owner to approve in a fixed order).

### 2.8 Information foraging (Pirolli and Card 1999)

Users maximise rate of gain = information value / cost of obtaining it; information scent (titles, labels, cues) lets them estimate value before committing (A: S17; S: S18). The compact form R = G/(T_B + T_W) (gain per between-patch plus within-patch time) is from the primary paper and was **not** read this session (U); NN/g gives only the ratio.

Limits: a descriptive optimisation model, not a calibrated predictor for a specific UI. Scent quality is measured by human judgement or text similarity, not by a law.

Executable: `scent(label, goal) -> [0,1]` as a token-overlap heuristic on tree-node and tab labels against the task goal, used only to rank designs in a review, and validated by a first-click study. **Oracle:** ratio form only: value 6, cost 3 s gives 2 per s; halving cost doubles rate.

**Verdict: adapt.** Tree nodes and change chips carry a count and kind of downstream impact as scent ("2 states, 1 journey, 3 tests"), so the reviewer decides where to look without opening each.

### 2.9 Cognitive load theory (Sweller 1988 onward)

Intrinsic (task), extraneous (presentation) and germane (schema building) load; effects: worked example, split attention, expertise reversal (S19, S; Sweller 1988 M, abstract elided by publisher). Whether the three types add is debated, and load is hard to measure (S19).

Executable proxies only: element interactivity count per screen (number of items that must be related to decide), and a split-attention check (are the picture and the code that explain each other adjacent and linked by highlight?). Measure workload with NASA-TLX in the study (2.10). **Oracle:** none numeric from the source; use the TLX arithmetic in 2.10.

**Verdict: adapt.** Split attention argues for UML picture and source model in one linked view; expertise reversal argues that explanations must collapse for experts (a text budget, not deletion).

### 2.10 Usability instruments and sample size

| Instrument | Scoring and numbers | Caveats | Source |
|---|---|---|---|
| SUS | 10 items, 1 to 5; odd items contribute (x - 1), even items (5 - x); sum times 2.5 gives 0 to 100. Average 68 over 500 evaluations. Oracle: all-3 answers give 50.0; best possible answers give 100.0 | Not diagnostic; correlation with task performance about r = .24; report confidence intervals | MeasuringU (A/S) |
| SEQ | One 7-point item after each task ("how difficult or easy"); mean about 5.5 over 400+ tasks; r about .5 with time and completion (Sauro and Dumas 2009, M) | About 14 % rate failed tasks as easy; ask why when below 5 | MeasuringU (S) |
| NASA-TLX | Six subscales (mental, physical, temporal, performance, effort, frustration) rated 0 to 100 in steps of 5; weighted score = sum(w_i*s_i)/15 with weights from 15 pairwise comparisons; Raw TLX = mean of subscales (Hart and Staveland 1988; Hart 2006, M). Oracle: s = (70,10,40,30,60,20), w = (5,0,2,3,4,1) gives 52.0; Raw gives 38.33 | Raw TLX is common and may be as valid; scores are relative, not absolute | Wikipedia (S) |
| Problems found | Found = N*(1 - (1 - L)^n), L about 0.31 mean (Nielsen and Landauer 1993, M). Oracle: n=1 gives 0.310, 3 gives 0.671, 5 gives 0.844, 10 gives 0.976, 15 gives 0.996 | L varies by product and user group; NN/g advises several rounds of about 5 and 20 users for quantitative measures | NN/g (A) |

Misuse: treating 5 users as 85 % of all problems in a complex product, using SUS as a diagnostic, comparing SUS to the 68 benchmark from a tiny sample without an interval, and reporting weighted TLX without recording weights.

**Verdict: adopt** SUS plus per-task SEQ plus Raw TLX for the study; report intervals; state that formative sessions find problems and do not estimate prevalence. The protocol itself is out of scope here.

### 2.11 Frameworks and principles

| Topic | What is verified | Limits and misuse | Verdict |
|---|---|---|---|
| Norman gulfs of execution and evaluation | Execution: turning intent into system actions; evaluation: interpreting system state to see if goals are met; successful execution usually depends on correct evaluation (A: S20, attributed to Hutchins, Hollan and Norman 1985/86; Norman) | Qualitative | adopt: every verification state must be interpretable at a glance; count steps M+P+B from intent to seeing the evidence |
| Shneiderman direct manipulation and 8 golden rules | Continuous representation; physical actions; rapid, incremental, reversible operations with immediate feedback (S23, S). Rules: consistency, universal usability, informative feedback, closure, prevent errors, easy reversal, user in control, reduce short-term memory load (A: S22) | Rule set is a checklist, not evidence | adopt: UML drag edits update the executable model with undo and immediate feedback |
| Nielsen 10 heuristics | Visibility of status; match to real world; control and freedom; consistency; error prevention; recognition over recall; flexibility; minimalist design; error recovery; help (A: S21; Nielsen 1994 refinement of 249 problems) | Heuristic evaluation finds problems, not user benefit | adopt as expert-review checklist |
| Horvitz mixed initiative | 12 principles (P: S24), notably: value-added automation; consider uncertainty about goals; timing with attention; dialog to resolve uncertainty; efficient direct invocation and termination; minimise cost of poor guesses; scope precision to uncertainty ("doing less"); efficient collaboration to refine results. Expected utility: eu(A) = p*u(A,G) + (1-p)*u(A,notG); act if p > p*, where p* = (u(notA,notG) - u(A,notG)) / ((u(A,G) - u(notA,G)) + (u(notA,notG) - u(A,notG))) (p* derived by us from eqs. 2 and 3 in the paper) | Utilities are unknowable a priori; the paper's agent may act, ours may **not** approve or apply | adapt: use only to decide whether AI shows a suggestion, asks a question or stays silent. Oracle: u(A,G)=1, u(A,notG)=-0.5, others 0 gives p* = 0.333 |
| Jakob's law | Users prefer your product to work like the ones they already know (A: S31) | Only as good as the choice of reference products | adopt: standard undo, command palette, tree and inspector conventions; reference set to be verified in the products dossier |
| Tesler's law | Complexity is conserved and moved: absorb it in the machine rather than in each user; Tognazzini's counter-argument that users take on harder tasks (S32, S) | Quote is from the Wikipedia summary; original interview (Saffer 2010) not read | adopt: the kernel absorbs synchronisation; the owner never hand-syncs picture and model |

### 2.12 Perception, visual complexity and first impressions

| Topic | Verified content | Limits | Verdict |
|---|---|---|---|
| Gestalt | Wertheimer 1923 factors: proximity, similarity, common fate, good continuation, closure, objective set, past experience (A: S26) | Descriptive, no thresholds. Any proximity ratio we set is a hypothesis to test | adopt: encode grouping by proximity and alignment before borders, matching the "container only when it encodes grouping or state" rule |
| Tufte | Data-ink ratio, chartjunk, lie factor (0.95 to 1.05 acceptable), small multiples (S27, S: Wikipedia; Tufte's own text not read, so wording is U). Lie factor = size of effect shown / size of effect in data. Oracle: a bar drawn twice as long for a value 1.5 times larger gives (1.0)/(0.5) = 2.0 | Studies cited on the Chartjunk page find embellishment can raise memorability, and minimalism is not objective (S28) | adopt: never truncate an evidence bar; small multiples for per-model evidence rows; UNKNOWN is a first-class mark, not empty space |
| Reinecke et al. 2013 | 450 websites, 548 volunteers; models of perceived visual complexity and colorfulness plus age and education explain about half the variance in 500 ms aesthetic ratings (M: abstract) | Websites, not developer tools; about half the variance is unexplained. Model formulas not read | adapt: compute proxy metrics as regression guards, not pass/fail |
| Miniukovich and De Angeli 2015 | Eight automatic GUI aesthetics metrics, webpages N=62 and iPhone apps N=53, 150 ms and 4 s exposures; up to 49 % of variance (web), up to 32 % (apps) (M: abstract) | Exploratory; the metric list was not read | adapt, as above |
| Lindgaard et al. 2006 | Visual-appeal ratings after 50 ms and 500 ms exposure are highly correlated (M plus search snippet; the coefficient is UNVERIFIED) | First impression of appeal is not usability or efficiency | adapt: keep the first screen calm, but never trade evidence for looks |
| WCAG 2.2 contrast (1.4.3) | ratio = (L1 + 0.05)/(L2 + 0.05); L = 0.2126 R + 0.7152 G + 0.0722 B after sRGB linearisation (0.04045, 12.92, ((c + 0.055)/1.055)^2.4); text 4.5:1, large text 3:1; do not round (A: S36). Oracle: white on black 21.00; #767676 on white 4.542 (pass); #777777 on white 4.478 (fail) | Contrast does not cover colour-blind separability; never the only carrier of meaning | adopt in the token linter |
| Design Tokens Format | Final Community Group Report 2025.10 (2025-10-28), "intended for implementation"; a colour `$value` is an object with `colorSpace`, `components`, optional `alpha` and `hex` (A: S43); not a W3C Standard | Older tool exports use plain hex strings | adopt for `design/tokens/*.tokens.json` |

**Density budgets.** The starting targets in the task (about 120 words and 12 containers per viewport, nesting 3, 6 font sizes, 2 elevations) have no source in the papers above. They are hypotheses, to be calibrated on reference products, each deviation needing an HCI-ADR. The metrics we can compute from DOM and layout JSON are exact counts (words, boxes, font sizes, depth), which is why we prefer them to perceptual models whose published fit is 30 to 50 % of variance.

## 3. Law to EIJA decision

| Law or instrument | EIJA decision it supports | Prediction it yields | Do not use it for |
|---|---|---|---|
| Fitts (Shannon, We) | Size and spacing of tree rows, tabs and canvas handles; place review-critical controls near the evidence they act on | MT per `P` op from `design/layouts`; ID in bits | Justifying a faster **Approve**: approval is deliberate; we optimise time to reach evidence, not time to approve |
| Steering | Connector drag corridors; forbid cascading menus | ID = A/W-style difficulty | Anything that is not a constrained path |
| Hick-Hyman | Stable command and sibling order; group commands into chunks | 0.24 + 0.08*log2(n) s for practised users | Search results, first-time use |
| KLM/GOMS | Current-vs-proposed flows for daily and weekly tasks (`design/tasks`) | Total with a plus or minus 21 % band | Learning, error handling, review quality |
| Miller/Cowan | Change summary of at most 4 chunks; ripple list grouped by model kind | Chunks held in mind per decision | Counting visible items |
| Nielsen 0.1/1/10 | Action latency classes; agent runs show progress and cancel | Band per action from a probe | Quoting a 400 ms threshold |
| Doherty and Thadani | Argument that fast local feedback is worth engineering effort | 3 s to 0.3 s: 180 to 371 transactions/hour in their data | Generalising to AI latency |
| Cognitive Dimensions | Review vocabulary; viscosity, hidden dependencies, provisionality, visibility as explicit design checks | Manual edits per conceptual change | A numeric quality score |
| Foraging | Scent on nodes: counts and kinds of downstream impact | First-click success in the study | Predicting time without data |
| CLT | Picture and model in one linked view; collapse text for experts | Split-attention check; TLX in the study | A numeric load metric |
| Norman gulfs | State glyph plus text for PASS, FAIL, UNKNOWN, RUNNING; steps from intent to evidence | Steps M+P+B to evidence | Colour-only status |
| Shneiderman | Reversible, incremental, immediate drag edits on generated UML | Latency band 0.1 s | Approving without review |
| Horvitz | AI may suggest, ask or stay silent; it never approves or applies | p* threshold from stated utilities | Any AI authority |
| Jakob, Tesler | Conventional shortcuts; kernel absorbs sync effort | Shortcut parity table | Skipping user study |
| Gestalt, Tufte | Grouping without boxes; honest evidence marks; small multiples | Container count, lie factor | Decorative charts |
| Reinecke, Miniukovich, Lindgaard | Regression guards on density and colour; calm first screen | Proxy metric drift | Pass/fail on beauty |
| WCAG contrast, DTCG | Token linter; colour never sole carrier | Contrast ratio per pair | Colour-blind checks (separate) |
| SUS, SEQ, TLX, n formula | Study protocol | Scores with intervals | Claims without a study |

## 4. Quantitative facts

| Fact | Source | Confidence |
|---|---|---|
| Shannon ID = log2(D/W + 1); original log2(2D/W) can be negative when D < W/2 | MacKenzie 1992 (S2); Soukoreff and MacKenzie 2004 (S3) | high |
| We = 4.133 * SDx; IDe = log2(D/We + 1); TP = IDe/MT in bits/s | Soukoreff and MacKenzie 2004 (P) | high |
| Fitts range for valid models: ID about 2 to 8 bits; the intercept is not a zero-distance time | Soukoreff and MacKenzie 2004, recommendations II, V, VI (P) | high |
| Menu pointing: MT = 0.37 + 0.13*ID s (R2 0.93, 8 participants, mouse) | Cockburn et al. 2007 (P) | high |
| Expert menu decision: T = 0.24 + 0.08*log2(n) s (R2 0.98); novice search T = 0.30 + 0.08*n s (R2 0.99) | Cockburn et al. 2007 (P) | high |
| Hick-Hyman fails when applied to visual search; requires stable item positions | Cockburn et al. 2007 (P) | high |
| Card et al. 1978 mouse: 1030 ms + 96 ms/bit, IP 10.4 bits/s | MacKenzie 1992 via summary (S2) | medium |
| KLM: K 0.08 to 1.20 s by skill (0.20 average), P 1.1 s, H 0.40 s, M 1.35 s | Card, Moran and Newell 1980 (P, scan OCR) | high |
| KLM error: 21 % RMS for single unit tasks, about 5 to 6 % for summed tasks | Card, Moran and Newell 1980 (P) | high |
| B = 0.10 s; D = 0.9nD + 0.16lD | Wikipedia KLM (S6) | medium |
| Steering: T = a + b*A/W (constant width); ID_N tends to A/(W ln 2); r2 0.97 to 0.99 | Accot and Zhai 1997 (P) | high (constants: not used) |
| Absolute judgment about 2.5 bits (about 6 categories); span about 7 chunks | Miller 1956 (S11) | high |
| Working memory about 3 to 5 chunks | Cowan 2001 abstract (M); PMC review (S12) | high |
| 0.1, 1, 10 s response-time limits | NN/g (S13) | high (attribution to Miller 1968, Card 1991 not opened) |
| 3.0 s to 0.3 s SRT: 180 to 371 transactions/hour (+106 %) | Doherty and Thadani transcription (S14) | medium (blog copy, one internal table error) |
| "400 ms Doherty threshold" is not stated in the text read | S14 | medium |
| CD dimensions list, two kinds of viscosity | Green and Blackwell 1998 (P) | high |
| Horvitz 12 principles; act if p > p* | Horvitz 1999 (P) | high |
| 10 usability heuristics; 249-problem factor analysis for the 1994 set | NN/g (S21) | high |
| Aesthetics models explain about 50 % (Reinecke), 49 % web and 32 % apps (Miniukovich) of variance | Abstracts (M) | high for the statement, low for transfer to Studio |
| WCAG 4.5:1 and 3:1; luminance constants | W3C Understanding 1.4.3 (A) | high |
| DTCG 2025.10 is a Final Community Group Report | designtokens.org (A) | high |
| SUS average 68 (500 evaluations); SEQ mean about 5.5; r about .24 (SUS vs performance) | MeasuringU (S38, S39) | medium |
| L = 31 %, 5 users about 85 % (formula gives 84.4 %) | NN/g (S37) | medium (L varies) |

## 5. Implications for EIJA

1. **Build the model, not a rule of thumb.** Implement `fitts_mt`, `hick_time`, `klm_time`, `latency_band`, `contrast_ratio`, `sus_score`, `tlx`, `p_star` as pure functions with the oracles above as unit tests, and read `design/tasks` and `design/layouts` with them. Every output carries the label PREDICTION and the constants profile used.
2. **Report bands, not points.** KLM predictions carry plus or minus 21 % and the M-count is logged; a decision that flips inside the band is not a decision.
3. **Do not minimise approval time.** Fitts and KLM would favour a bigger, nearer Approve. Our invariant says owner decisions are deliberate. Optimise the path to evidence and keep approval one deliberate step. This deviation needs its own HCI-ADR and a study arm that watches for rubber-stamping.
4. **Latency classes per action.** Drag feedback is 0.1 s; view switches 1 s; verification and agent runs get progress, cancel and a visible RUNNING or UNKNOWN state, never PASS by default.
5. **Semantic review is a chunking problem.** Summarise a change in at most 4 chunks (for example: term, rule, state, test), each expandable. Cap simultaneous cross-references at about 4, with a stated 3 to 5 range.
6. **Make hidden dependencies visible.** Use the Cognitive Dimensions vocabulary in the ADRs. Ripple count per change is the scent and the viscosity check; zero silent knock-on edits is the invariant.
7. **Let the picture be generated, and make edits reversible.** Direct manipulation, immediate feedback and undo (Shneiderman) plus Tesler (kernel absorbs sync) together justify UML drag edits that write to the executable model. Latency target is the 0.1 s class.
8. **AI has three moves: suggest, ask, stay silent.** Use Horvitz principles and p* only to choose among these. The utilities are unknown; record them as assumptions and test with the study.
9. **Density budgets are hypotheses with exact metrics.** Count words, containers, font sizes and nesting from the DOM; treat perceptual aesthetics models as regression guards only (they explain up to about half the variance).
10. **Tokens and contrast are machine-checkable now.** Use DTCG 2025.10 colour objects and a WCAG contrast linter in the token pipeline; never rely on colour alone for PASS, FAIL and UNKNOWN.
11. **No user-benefit claim without the study.** Use SUS, per-task SEQ and Raw TLX with intervals; formative rounds of about 5 find problems and do not estimate prevalence.

## 6. Gaps and unverified items

- Not read: Fitts 1954, Hyman 1953, Hick 1952, Seow 2005, Green and Petre 1996, Sweller 1988, Pirolli and Card 1999 (so R = G/(T_B + T_W) is UNVERIFIED), John and Kieras 1996, Lindgaard 2006 body (the 50 ms/500 ms correlation coefficient is UNVERIFIED), Reinecke 2013 and Miniukovich 2015 bodies (metric formulas), Tufte's books (data-ink definition wording is UNVERIFIED), Wertheimer beyond the summary, Nielsen and Landauer 1993 body, Hart and Staveland 1988.
- Not covered: Accot and Zhai 2003 rectangular-target Fitts extension (our "smaller side" rule is an assumption); CVD simulation and APCA; visual-search laws for dense diagrams; reading-time models (needed for review tasks, which KLM cannot predict); eye-tracking or saliency models for first-impression checks.
- Constants are from mouse studies on desktop; touch and trackpad need their own profile. Card 1978 constants (medium confidence) are inconsistent with Cockburn's (intercept 1.03 s vs 0.37 s), which shows how setup-dependent they are; pick one profile and state it.
- The Doherty and Thadani text read is a transcription; the 0.6 s row disagrees with its own arithmetic (37.7 vs 38.7 min).
- No verification yet of which conventions developers already know (Jakob's law needs a reference-product list); that belongs to the products dossier.
- The 21 % KLM error is for the 1980 experiment's tasks and users; there is no evidence it holds for AI-assisted or review tasks.

## 7. Source log (all opened 2026-09-29)

| ID | URL | Level |
|---|---|---|
| S1 | https://en.wikipedia.org/wiki/Fitts%27s_law | S |
| S2 | https://www.yorku.ca/mack/hci1992.html | A |
| S3 | https://www.yorku.ca/mack/ijhcs2004.pdf | P |
| S4 | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf | P |
| S5 | http://iihm.imag.fr/blanch/ens/2010-2011/M1/EIHM/cours/1980-Card-KLM.pdf | P (scan) |
| S6 | https://en.wikipedia.org/wiki/Keystroke-level_model | S |
| S7 | https://en.wikipedia.org/wiki/Hick%27s_law | S |
| S8 | https://research.cs.vt.edu/ns/cs5724papers/2.humanperf.fitts.accot.beyondfitts.pdf | P |
| S9 | https://en.wikipedia.org/wiki/Steering_law | S |
| S10 | https://www.nngroup.com/articles/steering-law/ | A |
| S11 | https://psychclassics.yorku.ca/Miller/ | A |
| S12 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2864034/ | A/S |
| S13 | https://www.nngroup.com/articles/response-times-3-important-limits/ | A |
| S14 | https://jlelliotton.blogspot.com/p/the-economic-value-of-rapid-response.html | S |
| S15 | https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf ; index https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/ | P/A |
| S17 | https://www.nngroup.com/articles/information-foraging/ | A |
| S18 | https://en.wikipedia.org/wiki/Information_foraging | S |
| S19 | https://en.wikipedia.org/wiki/Cognitive_load | S |
| S20 | https://www.nngroup.com/articles/two-ux-gulfs-evaluation-execution/ | A |
| S21 | https://www.nngroup.com/articles/ten-usability-heuristics/ | A |
| S22 | https://www.cs.umd.edu/users/ben/goldenrules.html | A |
| S23 | https://en.wikipedia.org/wiki/Direct_manipulation_interface | S |
| S24 | https://erichorvitz.com/chi99horvitz.pdf | P |
| S25 | Semantic Scholar Graph API records for DOIs 10.1207/s15516709cog1202_4, 10.1080/01449290500330448, 10.1037/h0055392, 10.1145/2702123.2702575, 10.1006/jvlc.1996.0009, 10.1145/2470654.2481281, 10.1037/h0056940, 10.1145/235833.236054, 10.1145/1240624.1240723, 10.1017/S0140525X01003922, 10.1207/s15327051hci2003_3, 10.1207/s15327051hci0701_3, 10.1145/358886.358895, 10.1145/169059.169166, 10.1145/302979.303030, 10.1145/1518701.1518946, 10.1207/s15327051hci0104_2, 10.1177/154193120605000909 (via https://api.semanticscholar.org/graph/v1/paper/DOI:...) | M |
| S26 | https://psychclassics.yorku.ca/Wertheimer/Forms/forms.htm | A |
| S27 | https://en.wikipedia.org/wiki/The_Visual_Display_of_Quantitative_Information | S |
| S28 | https://en.wikipedia.org/wiki/Chartjunk (fetched as data-ink page redirect) | S |
| S30 | https://en.wikipedia.org/wiki/Gestalt_psychology | S |
| S31 | https://lawsofux.com/jakobs-law/ | S |
| S32 | https://en.wikipedia.org/wiki/Law_of_conservation_of_complexity | S |
| S33 | https://dash.harvard.edu/entities/publication/73120378-cc85-6bd4-e053-0100007fdf3b | A |
| S36 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | A |
| S37 | https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/ | A |
| S38 | https://measuringu.com/sus/ | S |
| S39 | https://measuringu.com/seq10/ | S |
| S40 | https://en.wikipedia.org/wiki/NASA-TLX | S |
| S41 | https://github.com/cogtool/cogtool | A |
| S42 | https://en.wikipedia.org/wiki/GOMS | S |
| S43 | https://www.designtokens.org/TR/2025.10/format/ (and the /drafts/format/ page) | A |
| S45 | Repo: `AGENTS.md`, ADR-013 in `docs/adr/0000-poc-decision-log.md`, CSP in `src/eija_studio/interfaces/http.py` | P |

Opened but not used: https://www.edwardtufte.com/books/ (catalogue only, no content on data-ink).
