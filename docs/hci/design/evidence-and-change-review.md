# Evidence, semantic diff and ripple: reviewing an agent's change

Lane `lane/ux-research`, aspect `evidence-change-review`. Date 2026-09-29. Status: proposed design. Decision record: [HCI-ADR-0063](../../adr/0063-hci-evidence-change-review.md). Task flows: [design/tasks/review-flows.json](../../../design/tasks/review-flows.json). Source ids (`REV§4`, `LAW§2.7`, `V2`) are defined in [../research/SYNTHESIS.md](../research/SYNTHESIS.md) section 1; ids `S1` to `S40` (plus `S15b` and `S24b`) are pages and files I opened myself and are listed in section 8.

Every number is labelled **MEASURED** (I or another lane ran a tool; method stated), **PREDICTION** (a model output, not a human result) or **UNVERIFIED** (not confirmed, not built on). No user study has been run. Nothing here claims that developers will prefer or decide better with this screen; the study in ADR-0063 is the test.

## 0. Decisions first

| # | Decision | Evidence basis | Confidence |
|---|---|---|---|
| D1 | The review unit is a **typed semantic operation** computed by the kernel from the model diff, grouped into chapters (Core, Follows from core, Other), each labelled ADDED, MODIFIED or REMOVED. The JSON diff is one level down. MEASURED: the excursion change "recommendation only" is 4 operations in 2 chapters. | Understanding the change is the main review challenge (S15). Linear groups core parts first (S9). OpenSpec uses the ADDED, MODIFIED, REMOVED vocabulary (S10); its page says agents draft artifacts under human direction, so those deltas are agent-drafted, whereas here they are kernel-derived. CodeRabbit's page says it generates Mermaid sequence diagrams (S11) and does not say how it groups changes; an AI-written grouping would in any case be excluded by the invariants. | Medium. None of the review products I opened derives operations from an executable model; model-driven-engineering diff tools (EMF Compare, S40) compare models and were not checked for typed operations (UNVERIFIED); untested with users |
| D2 | One operation is read as **changed fields only** ("from Submitted → Recommended"). Unchanged fields and non-semantic edits sit behind counters. The before and after pictures share one layout. | The TLA+ Toolbox trace hides unchanged variables (S20). GitHub un-marks a Viewed file when it changes (S14). MEASURED: a full reversal of states, transitions and guards changes 49 of 75 JSON leaf values and 0 operations (an upper-end example; a single swap changes far fewer). | Medium |
| D3 | The ripple is a **strip of model kinds with counts**, not a graph. A kind with no model shows `?` and one sentence. "0" and "?" never look alike. | Nx marks every project affected when the lock file changes (S18). Jama draws a gap mark where a required link is missing (S19). Cognitive Dimensions: hidden dependencies (S27). MEASURED: 20 nodes of 8 kernel node types, shown as 6 cells; personas and requirements are not modelled. | Medium |
| D4 | The **evidence rail** shows counts by state, never a percentage. Every claim row carries the status glyph, the status word, the bound and the first NOT covered items at level 0. UNKNOWN sorts first and is as loud as FAIL in position. | GitHub counts a skipped required check as success (S1). Codecov defaults `if_not_found` to success (S2). Stryker publishes two denominators (S3). Quint says verified is always for a bound (S5). | High for the failure prevented; untested for user benefit (H1) |
| D5 | **"Covers X, not Y"** is a four-slot row: claim, covered, assumed, NOT covered. The last slot is never empty; when the kernel supplies nothing it reads UNKNOWN. | GNATprove separates Justified from Unproved (S4). The verifier already lists 5 limits that no UI shows (S34). Kiro says property tests are evidence, not proof (S21). | Medium; hypothesis H1 |
| D6 | **Status is glyph plus word plus colour role.** Six evidence statuses (PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN) and one job state (RUNNING). PARTIAL is not used. PASS is the quietest mark and still shows its bound. | WCAG 1.4.1 (S23). Dafny marks obsolete (not yet re-verified) and verifying states distinctly and asks for shapes as well as colours for colour-blind users (S6). CVD data from the visual dossier (VIS§2.4). | High for the rule; glyph shapes untested |
| D7 | A **counterexample** replaces the diff in the change pane (level 1): rows of variables that differ, expected against actual, a minimal or not-minimised label, a replay token, Step, Play, Back, and a jump to the rule. | TLA+ Toolbox (S20); Kiro shrinks to the smallest failing input (S21); the verifier cell fields (S34). | Medium |
| D8 | **The owner decides.** A three-slot attention set (AI, Kernel, Owner) is read-only. The rail holds one entry, "Decide", that opens the decision surface. No control on this screen or in the palette approves or applies. | Users approve 93% of Claude Code permission prompts (S13, vendor-reported). Linear keeps the human as assignee (S16). Copilot can submit approving reviews when enabled (S17). Complacency is not overcome by simple practice and automation bias is not prevented by training or instructions (S24). | High as an invariant; rubber-stamp risk is medium |
| D9 | **Time is not the claim.** PREDICTION: the four flows need less or equal motor and response time in the proposed screen, but total time flips inside plausible reading-effort assumptions in 3 of 4 flows. | KLM model in ADR-0063; LAW§2.4. | High that the model cannot decide this |
| D10 | Seven **kernel additions** are needed (section 1.3). Today the kernel already fills 6 of the 8 ripple cells (Personas and Requirements are `?`); without K1 to K7 there is no operation list or chapter (K1, K2), no typed coverage slots (K3), no NOT_RUN registry (K4), no STALE reason (K5) and no authority delta (K7). Each needs a kernel ADR; none is made here. | Repo files read (S34). | High |

## 1. Scope, interfaces and assumptions

### 1.1 What this document settles

The core review screen: meaning summary, before and after diff, ripple strip, evidence rail, counterexample stepper, status system, four-slot coverage row and how it is used in the study. It does not settle the language tree, the diagram editor, the palette contents beyond this screen, the owner decision surface, tokens, type, or the AI prompt lane. Where I depend on them I state an interface, below, and keep it explicit.

### 1.2 Interfaces to other aspects (assumptions, not decisions)

| Id | I assume | Owner aspect | If it changes |
|---|---|---|---|
| A1 | A shell with a 40 px top bar and a 48 px navigation rail. The language tree is reachable from the rail and is not shown on this screen. Selecting a model element elsewhere opens this screen filtered to operations that touch it. | shell and tree | Column widths move by the same amount; nothing else |
| A2 | Colour is delivered as role tokens: `status.pass`, `status.fail`, `status.conflict`, `status.stale`, `status.unknown`, `status.not_run`, `status.running`, `provenance.ai`, plus surface and text roles. UNKNOWN is a neutral hue, never tinted like PASS. Contrast is computed per pair; a pair that is not computed is reported UNKNOWN. | colour and tokens | This screen has no hue-only meaning, so a palette change cannot break meaning; contrast rows in ADR-0063 stay UNKNOWN until computed |
| A3 | Type has at most 6 sizes and tabular numerals. This screen uses 5 named steps: caption (bounds, ids, mono), small, base, title, case title. Pixel values are not fixed here. | type | Layout heights in Appendix A are 20 px lines on a 13 px base; other sizes need the layout JSON regenerated |
| A4 | The diagram renderer draws the two state pictures from the model at one layout keyed by element id and marks ADDED, MODIFIED and REMOVED elements with a dashed, heavy or dotted outline plus a text label. Pictures are read-only on this screen; drag editing is not offered here. | diagrams | If pictures are not ready, the fields table alone carries D2 |
| A5 | The decision surface (T08) opens from "Decide", shows the exact revision and every non-PASS claim, and keeps the existing acknowledgement and typed answers of the baseline. This screen never enables Approve. | owner decision | The rail entry stays the same |
| A6 | The AI prompt lane is elsewhere. On this screen AI text, if the owner asks for it, appears in a separate region labelled "AI-written, unchecked" with a dashed outline, and never replaces or edits the operation list, counts or evidence. | AI assist | None |

### 1.3 Kernel additions this design needs (proposals; each needs a kernel ADR and regression tests, `AGENTS.md`)

| Id | Need | What exists today (read in the repo) |
|---|---|---|
| K1 | `semantic_diff(before, after)`: operations with a stable id, verb, kind, element id, changed fields (name, before, after), a per-operation hash, and the count of raw differences that normalise away | `model_impact` returns only changed action names (`domain/impact.py`). `Workflow.semantic_hash` already treats definition order as non-semantic (`domain/models.py`) |
| K2 | Chapter rule: Core = ADDED or REMOVED elements. Follows from core = MODIFIED elements that reference a core element (a transition whose from or to state is ADDED). Other = the rest | Nothing |
| K3 | Typed coverage on every claim: claim text, covered (count, declared, unit, depth, method), `assumed[]`, `not_covered[]` | The matrix receipt has `expected_cells`, `matrix`, `protocol` and five `limitations` strings, all in the API payload and never rendered (`application/verifier.py`, `app.js`). The packet has 4 `limitations` |
| K4 | A registry of evidence kinds, so that a registered kind with no receipt reports NOT_RUN | With no receipts `aggregate_status` returns UNKNOWN (`domain/evidence.py`). `AGENTS.md` says missing prerequisites report NOT_RUN |
| K5 | The reason for STALE: which of the 5 subject dimensions differ | `assess_receipt` returns STALE when any of semantic, implementation, policy, environment or harness differ, without saying which |
| K6 | Roles touched by the diff; impact roots for states | The impact graph is keyed by action only, so an ADDED state has no root of its own |
| K7 | Optional baseline observation (verify the baseline model too, about 2.7 s), enabling an authority delta: who could act before and who can act now | Only the candidate is verified today. MEASURED by running `verify_runtime` on both models: accepted cells 6 before, 7 after; 3 added, 2 removed |

### 1.4 Other lanes' files seen after drafting (read only, not edited)

I finished the layouts in Appendix A before other lanes' files appeared in the shared worktree, then read them (S39). They reach similar ideas with a different composition; the integrator decides.

| Source | What it says | Effect here |
|---|---|---|
| `design/layouts/proposed-review.json`, `proposed-evidence.json` (layout lane) | A 40 px top bar with case switcher, four tabs (Language, Review, Diagram, Evidence), global PASS, UNKNOWN and NOT_RUN chips and a palette trigger; a 276 px tree; a 708 px centre; a 456 px rail; a 32 px bottom strip with Kernel, AI and Owner chips and a prompt lane. Review tab: chaptered operations with per-operation state, journey and test counts, before and after diagrams, the ripple in the rail with a "kernel" tier, an Unknown group, a "Review decision" button. Evidence tab: claim table with status and bound; the four slots in the rail; every ADR-0018 kind as a NOT_RUN row | Same intent as D1 to D8. Differences: (a) the attention set is a bottom strip there and header chips here; D8 needs only that the three slots are always visible, so adopt the strip if the shell has it. (b) Evidence sits on its own tab there and beside the change here. My reason, that the bound and NOT covered must be in view while the change is judged, is hypothesis H1; the study can compare both. (c) They list unbuilt ADR-0018 kinds as NOT_RUN; I list only registered kinds (K4), because a NOT_RUN row for a tool that does not exist implies it could be run. (d) They show per-operation ripple counts; I show one whole-change strip because the kernel groups by action (O7). (e) Rail 456 px there, 360 px here |
| `language-and-ddd-tree.md` (D2 and section 1) | Top bar 48 px, rail 400 px, status bar 32 px; the tree marks operations A, M and + from `change.operations[]` | A1 pixel values move; the tree and this screen consume the same operation list (K1) |
| `ai-interaction.md` (D2, D11) | Whose turn it is shows as the proposal state word rather than a separate widget; the palette holds read, propose and job commands only | Consistent with A6 and section 2.13; the attention chips may reduce to state words |
| `__pointer` element in the layout files | A virtual pointer rest position at (720, 450) | Adopted: the first P of every flow starts there |

## 2. The screen

### 2.1 Default state at 1440 by 900 (wireframe)

Legend: `[#]` PASS, `[x]` FAIL, `<?>` UNKNOWN, `[ ]` Viewed toggle. The eight ripple chips are one row of eight in the real layout; the wireframe wraps them for width. Coordinates for every element are in Appendix A.

```
+---+-------------------------------------------------------------------------------------+---------------------------------+
|nav|Teacher recommends; registrar decides     AI proposed  Kernel checked  Owner deciding|                                 |
|   |4 operations - 2 ADDED - 2 MODIFIED - 0 REMOVED           0 non-semantic edits hidden|Evidence 7f3a91c2  [Verify]      |
|   |                              |                                                      |<?> 1 UNKNOWN   [#] 3 PASS       |
+---+------------------------------+------------------------------------------------------+---------------------------------+
|   |Core                          |Before                      After                     |<?> UNKNOWN Human understanding  |
|   |+ ADDED    state Recommended  |+------------------+      +-------------------+       |    none measured                |
|   |  [ ]                         || 4 states, 4 rules|      | 5 states, 5 rules |       |    not covered: any real        |
|   |+ ADDED    rule  Recommend    || picture from the |      | + Recommended     |       |    reviewer                     |
|   |  [ ]                         || model, same      |      |   (dashed, ADDED) |       |[#] PASS Runtime matrix          |
|   |Follows from core             |+------------------+      +-------------------+       |    125 of 125 cells, 1 step     |
|   |~ MODIFIED rule  Approve      |MODIFIED rule Approve                                 |    not covered: sequences,      |
|   |  [ ]  <- selected            |  from  Submitted -> Recommended                      |    identity, durability         |
|   |~ MODIFIED rule  Reject       |  6 unchanged fields    JSON diff                     |[#] PASS Protected policy        |
|   |  [ ]                         |                                                      |    5 of 5 rules                 |
|   |0 of 4 viewed                 |Ripple, per changed action                            |    not covered: UNKNOWN         |
|   |                              |[Rules 3][State views 3][Journeys 3][Runtime rows 3]  |[#] PASS Impact closure          |
|   |                              |[Evidence 6][Decision 2][Personas ?][Requirements ?]  |    20 nodes, declared mapping   |
|   |                              |Not analysed: personas, requirements have             |    not covered: effects         |
|   |                              |no model here                                         |    outside mapping              |
|   |                              |                                                      |                                 |
|   |                              |                                                      |                                 |
+---+------------------------------+------------------------------------------------------+---------------------------------+
|   |                              |                                                      |[Decide]  Reviewable             |
|   |                              |                                                      |         1 UNKNOWN open          |
+---+-------------------------------------------------------------------------------------+---------------------------------+
```

### 2.2 Regions

| Region | Box (px) | Contents | Disclosure level |
|---|---|---|---|
| Header | 64,48 to 1064,76 | Case title (the canonical meaning label), attention set | 0 |
| Summary line | 64,100 to 960,124 | Operation counts by verb, the hidden-edit counter | 0 |
| Operation list | 56,140 to 376,392 | Chapters, operation rows, Viewed toggles, progress | 0 |
| Change pane | 392,140 to 1064,540 | Before and after pictures, changed fields of the selected operation, ripple strip, not-analysed line | 0; JSON diff, ripple list and unchanged fields at level 1 |
| Evidence rail | 1080,40 to 1440,900 (surface); first content at y = 96 | Subject id, Verify, roll-up chips, claim rows, decision bar | 0; coverage detail, receipts at level 1; receipt JSON at level 2 |

Disclosure never exceeds two levels below level 0 (NN/g: beyond 2 levels users often get lost, a 2006 practitioner rule, S26). UNKNOWN, status, bound and NOT covered are all at level 0.

### 2.3 Meaning summary and the operation list

- The summary line is generated, never written: `4 operations - 2 ADDED - 2 MODIFIED - 0 REMOVED`. The case title is the canonical meaning label the server already owns (`CANONICAL_OPTIONS`), not provider text.
- Chapters: **Core** holds ADDED and REMOVED elements. **Follows from core** holds MODIFIED elements that reference a core element. **Other** holds the rest (K2). For the example: Core = ADDED state Recommended, ADDED rule Recommend; Follows from core = MODIFIED rule Approve, MODIFIED rule Reject. A change with a single operation shows no chapter heading.
- Working-memory budget: at most 4 top-level chunks, stated range 3 to 5 (Miller S28, Cowan S29). The limit applies to what must be held in mind, not to visible rows (SYNTHESIS C12). If a change has more than 4 chapters the list collapses to chapter rows with counts.
- Row anatomy: verb glyph and word (+ ADDED, ~ MODIFIED, - REMOVED), kind word (state, rule), element name, a 24 by 24 Viewed toggle. Row height 40 px. An operation proposed by an agent carries the text "AI-proposed" and a dashed left edge; a kernel-derived or owner-made operation carries neither (P9).
- The list is an APG tree (S30): Down and Up move focus and selection, Home and End jump, Space toggles Viewed. No single-character shortcut exists, so WCAG 2.1.4 (S25) is not triggered.
- **Viewed** persists per operation hash and clears when the hash changes, as GitHub does for a file (S14). It is stored in the browser's `localStorage` inside try and catch (a convenience, absent in private windows), is never sent to the server, and is never an input to eligibility or approval. The text "0 of 4 viewed" names the toggles, so there is no icon-only control.
- Not-analysable change: a change the kernel cannot express as typed operations shows one row "NOT ANALYSED" with the raw diff below it. Today the frozen vocabulary means the kernel refuses such a change with a reason instead (ADR-003, `policy.py`).

### 2.4 Before and after semantic diff

- For the selected operation the pane shows only the fields that differ, as `field  before → after`. MODIFIED rule Approve: `from  Submitted → Recommended`, with "6 unchanged fields" as a counter (a transition has 8 fields; the id is the key and one field changed).
- ADDED rule Recommend shows all its fields with an empty before, because nothing can be hidden: Teacher, Submitted → Recommended, 6 guards including `actor_assigned`, effects `Audit:ExcursionRecommended` and `Notification:RegistrarQueued`. ADDED state Recommended shows "referenced by 3 rules", derived from the transitions that name it.
- The two pictures are one diagram at one layout, rendered twice, so the only differences are the added node and the changed edges (Tufte's small multiples: same scale and axes, S22). Elements keep their position by id; the ADDED node is placed by the layout aspect.
- The counter "N non-semantic edits hidden" is permanent and opens the list of raw differences that normalised away. MEASURED: a full reversal of the order of states, transitions and each transition's guards in the candidate gives the same semantic hash, 49 of 75 raw JSON leaf differences and 0 operations. This is an upper-end example, not a typical noise level: a single swap changes far fewer leaves. SemanticDiff hides syntax-only edits by language rules (S12); I could not confirm its own statement about the limits of hiding, so the counter is there to let the owner check.
- Level 2 ("JSON diff") shows the canonical, sorted JSON of both models. Raw JSON never appears at level 0 (baseline: 3 `pre` blocks).

### 2.5 Ripple strip

One row, eight cells of 84 by 56 px: Rules, State views, Journeys, Runtime rows, Evidence, Decision, Personas, Requirements. Each cell is a name and a tabular count, or `?`. Each cell is named for the kernel object it counts, not for a reviewer's notion of it: the kernel's impact graph has one chain of nodes per changed action, so a count is a number of nodes of that kind, one per changed action, and not a number of states added or tests written. In the example the change adds 1 state and the model goes from 4 to 5 states, while "State views 3" is the three per-action state views of Approve, Recommend and Reject. The strip title carries the unit at level 0 ("Ripple, per changed action"); the kernel's "declared mapping" sentence appears when a cell is expanded.

| Cell | Kernel source today (node prefix in `model_impact`) | Unit | Example count (MEASURED) |
|---|---|---|---|
| Rules | `rule:*` | changed rules (one per changed action) | 3 |
| State views | `state-view:*` | per-action state views | 3 |
| Journeys | `journey:*` | per-action journey lines | 3 |
| Runtime rows | `runtime:*` | per-action rows of the runtime matrix | 3 |
| Evidence | `obligation:*` and `receipt:*` | obligations plus receipts | 6 |
| Decision | `review-packet` and `local-decision` | fixed pair | 2 |
| Personas | no model | not analysed | `?` |
| Requirements | no model | not analysed | `?` |

- MEASURED (kernel domain code run on 2026-09-29, section 3): 3 changed actions (Approve, Recommend, Reject), 20 affected nodes of 8 node types (the six cells above plus `review-packet` and `local-decision` in one cell), closure complete. For the second typed edit (registrar rejection source only) it is 1 changed action and 8 nodes.
- Tiers. A count is kernel-derived unless the cell carries `H` (heuristic edge, none exist today) or `?` (not analysed). The kernel's own sentence, "All dependencies encoded by this projection mapping; not every real-world consequence", appears when a cell is expanded, and the expanded cell repeats that the mapping is declared.
- `?` is a hollow diamond with a question mark and the word in the sentence below the strip: "Not analysed: personas, requirements have no model here". A cell that was analysed and found nothing shows `0` with no diamond, so absence and ignorance cannot be confused (Nx marks every project affected on a lock-file change, S18, and the dossier calls that a deliberate over-approximation; the design goes further and never draws "not analysed" as "unaffected").
- Level 1: a cell opens the list of affected element ids, for example the three journey lines the kernel already generates. Expanding Personas shows what is known (roles touched by the diff: Teacher, Registrar, K6) and what is not (persona goals).
- No graph in v1. A graph would be an extra picture to check and would need its own hierarchy; the strip answers "what else does this touch" and "what is not known" in one row. Deferred, not rejected (open question O2).

### 2.6 Evidence rail

- Header: `Evidence 7f3a91c2` (first 8 characters of the subject hash) and a `Verify` button.
- Roll-up chips: one per state present, in severity order FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN, RUNNING, PASS. A chip is a counter and a filter (click a count to filter the rows, as Storybook does, REQ§2.3). There is no percentage and no "all clear" state: any UNKNOWN or NOT_RUN caps the roll-up, and the screen reader label reads "Evidence: 3 PASS, 1 UNKNOWN".
- Rows: sorted by severity, then kernel order. Row height 68 px, three lines: glyph, status word, claim name; the bound; NOT covered.
- Decision bar: a short status word mapped from the kernel's eligibility code and the number of open non-PASS claims. Mapping: `ELIGIBLE_FOR_LOCAL_REVIEW` shows "Reviewable"; `BLOCKED` shows "Blocked" plus a short reason (`RUNTIME_EVIDENCE_FAIL` shows "runtime FAIL"). The raw kernel code and blocker codes appear at level 1, beside the word, unchanged. The map is a UI string table, not a kernel change; the full table for every blocker code is owed by the content aspect. "Reviewable" was chosen because "Eligible" and "Approved" both read as a go-ahead to me (analyst judgement, untested; the study reads it back). Eligibility is not evidence and is not approval (ADR-010).
- Claims on the excursion example today (kernel keys in brackets): Human understanding (`human_understanding`, UNKNOWN by construction), Runtime matrix (`runtime_matrix`), Protected policy (`schema_policy`), Impact closure (`modelled_impact_closure`).

### 2.7 "This proof covers X but not Y": the four-slot row

The verified precedents each cover one part: a Justified column apart from Unproved (GNATprove, S4), a bound printed with the verdict (Quint, Alloy, S5, S7), two denominators and a No coverage state (Stryker, S3), a dependency listing (Lean, REV§6, not opened by me). No page I opened shows the combination, so this composite is a hypothesis (H1: showing the fourth slot reduces approvals that overlook an unknown). It is tested in the study.

Level-1 form, filled from the real runtime matrix receipt:

```
[#] PASS   Runtime matrix
    claim        every one of the cells behaves as the oracle states
    covered      125 of 125 declared cells (5 actors x 5 states x 5 actions), 1 step each
                 7 accepted, 118 denied; 25 cells are new (state Recommended)
    assumed      oracle written by the same author as the policy; synthetic actors stand for real roles
    NOT covered  action sequences; real identity; crash durability; human understanding
    receipts     1 current PASS   0 STALE      [Receipt JSON]
```

Rules:

1. Four slots in fixed order. `covered` gives counts with denominators and units, the depth (1 step) and the method id. Counts, not percentages.
2. `NOT covered` is never empty. If the kernel supplies nothing the slot reads `UNKNOWN (kernel supplied no limits)`. Today that is the case for Protected policy, and the wireframe shows it.
3. `assumed` lists what the verdict relies on being true. "None declared" is a legal value and is not the same as "none".
4. Level 0 shows the covered line and the first three NOT covered items followed by "+n" when there are more. The assumed slot is level 1.
5. A PASS row never omits its bound. Dafny makes success the quiet default because its design treats verified as the expected result (S6); EIJA borrows the visual weight only, because a bound-less green is what GitHub and Codecov show (S1, S2).

How the five limits the verifier already writes map to slots. The verifier emits them as one flat list; the classification is mine and the kernel should emit it typed (K3):

| Verifier limitation (source `application/verifier.py`) | Slot |
|---|---|
| Synthetic fixture directory; no real SSO | assumed (actors stand for roles) and NOT covered (real identity) |
| No human-outcome measurement | NOT covered |
| One-step state and action matrix, not exhaustive arbitrary sequences | NOT covered |
| Same-author oracle, not an independent holdout | assumed |
| Disposable non-durable sandbox: observes transaction semantics, not crash durability | NOT covered |

How other evidence kinds from ADR-0018 would fill the slots (design proposal; none of these kinds is built and none was tested with users):

| Kind | covered | assumed | NOT covered |
|---|---|---|---|
| Machine-checked proof | the theorem and the model it is about | every axiom it depends on, and any unfinished proof (Lean lists axioms; Dafny has `assume`, REV§6) | the code, unless conformance is a separate receipt |
| Model check | states explored, depth bound (Quint `--max-steps` defaults to 10, S5; Alloy scope defaults to 3 per signature, S7) | the model matches the runtime | anything beyond the bound |
| Property test | examples run, seed | the generator reaches the interesting cases | unsampled inputs; label "evidence, not proof" (Kiro, S21) |
| Mutation score | detected over valid, and detected over covered (S3) | the mutants represent real faults | mutants with No coverage |

### 2.8 Counterexample stepper (level 1, replaces the diff)

Seeded fixture, not a kernel result: no failing cell exists today (MEASURED: 0 mismatches in 125). The example is a hypothetical cell where an unassigned teacher's Recommend was accepted.

```
+---+-------------------------------------------------------------------------------------+---------------------------------+
|nav|Teacher recommends; registrar decides     AI proposed  Kernel checked  Owner deciding|                                 |
|   |4 operations - 2 ADDED - 2 MODIFIED - 0 REMOVED           0 non-semantic edits hidden|Evidence 7f3a91c2  [Verify]      |
|   |                              |                                                      |[x] 1 FAIL <?> 1 UNKNOWN         |
+---+------------------------------+------------------------------------------------------+---------------------------------+
|   |Core                          |[Back to change]                                      |[x] FAIL Runtime matrix          |
|   |+ ADDED    state Recommended  |FAIL teacher-unassigned Submitted Recommend           |    124 of 125 cells match       |
|   |+ ADDED    rule  Recommend    |1 step, minimal. Replay runtime_matrix:               |    not covered: sequences,      |
|   |Follows from core             |teacher-unassigned/Submitted/Recommend                |    identity, durability         |
|   |~ MODIFIED rule  Approve      |                                                      |<?> UNKNOWN Human                |
|   |~ MODIFIED rule  Reject       |variable    expected     actual                       |    understanding                |
|   |                              |accepted    false        true                         |[#] PASS Protected policy        |
|   |                              |state       Submitted    Recommended                  |[#] PASS Impact closure          |
|   |                              |version     0            1                            |                                 |
|   |                              |audit       0            1                            |                                 |
|   |                              |outbox      0            1                            |                                 |
|   |                              |operations  0            1                            |                                 |
|   |                              |                                                      |                                 |
|   |                              |[Step back] [Step] [Play]  Step 1 of 1                |                                 |
|   |                              |[Jump to rule TR-RECOMMEND]                           |                                 |
|   |                              |                                                      |                                 |
+---+------------------------------+------------------------------------------------------+---------------------------------+
|   |                              |                                                      |[Decide]  Blocked                |
|   |                              |                                                      |         runtime FAIL            |
+---+-------------------------------------------------------------------------------------+---------------------------------+
```

- Rows are only the variables that differ, expected against actual, using the real cell fields (`accepted`, `state`, `version`, `audit`, `outbox`, `operations`). The TLA+ Toolbox highlights changed variables and can hide the unchanged ones (S20).
- The label says `minimal` only when the producing tool states it; otherwise `not minimised`. Kiro shrinks failing inputs to the smallest that reproduces (S21). I could not confirm any minimality claim for model checkers on the Quint page (S5), so that is UNVERIFIED and not built on.
- Replay token: a deterministic key (`runtime_matrix:actor/state/action`) that is copyable. A multi-step trace gets Step, Step back and Play with Space; state changes are announced in a live region and motion carries no meaning.
- Play toggles to Pause while it runs (the button keeps its place, so no extra target is added); Play advances one step per interval and stops at the last step.
- "Jump to rule" selects the rule in the change pane. The expression column of the Toolbox is deferred because the kernel has no evaluator.
- "Back to change" restores the diff. FAIL blocks eligibility through the existing blocker `RUNTIME_EVIDENCE_FAIL`.

### 2.9 Status system

| Status | Kernel source | Glyph (16 px grid, 1.5 px stroke) | Word | Weight | When |
|---|---|---|---|---|---|
| FAIL | `assess_receipt` returns FAIL; aggregate FAIL | filled square with a cut-out cross | FAIL | loudest | an authenticated receipt whose expected and actual differ, or a malformed artifact |
| CONFLICT | aggregate: a current PASS and a current FAIL | square split on the diagonal, half filled | CONFLICT | loud | evidence disagrees; never averaged |
| STALE | receipt subject differs from the current subject | square with a dashed outline | STALE plus reason (K5) | medium | evidence for an earlier revision, kept per ADR-012 |
| UNKNOWN | kernel has no authority for the claim, or none exists | hollow diamond containing `?` | UNKNOWN | loud in position | human understanding by construction; claims with no receipt of a recognised kind |
| NOT_RUN | registered kind, no receipt (design rule K4; the kernel returns UNKNOWN today) | dotted circle | NOT_RUN | medium | prerequisite missing or not requested |
| RUNNING | UI job state | open ring with a gap | RUNNING plus elapsed seconds | medium | a verification job; the previous verdict stays visible as STALE |
| PASS | receipt recomputed as PASS | small filled square (10 px) | PASS | quietest | matrix and policy hold within their stated bound |
| AI-proposed (provenance) | operation source is an agent | dashed outline | AI-proposed | medium | never evidence, never a status |

Rules: the word is always present and always in the same place; the same glyph is used in rail rows, roll-up chips, the ripple `?` and the decision bar; the glyph silhouettes differ by fill and outline so they survive greyscale; hue comes from A2 and carries nothing alone. MEASURED by the visual dossier (own script, Machado 2009 severity 1.0, not re-run by me): the baseline green and red differ by 0.204 dE_OK normally and about 0.08 for protan and deutan against one just-noticeable difference of 0.02, and proved against unknown, refuted against stale differ by 0.025 and 0.016 for deutan, which is 1.25 and 0.8 times the dossier's 0.02 threshold: marginal to below. The threshold is a just-noticeable difference, not a criterion for telling small marks apart, and its origin is UNVERIFIED here, so the numbers only support the rule WCAG 1.4.1 already states: hue is not relied on (VIS§2.4). Whether the glyph shapes are distinguishable at 12 to 16 px is untested.

PARTIAL is not adopted: the kernel has no such state, and adding one needs a kernel ADR (SYNTHESIS C2).

### 2.10 Attention set and the human-only decision

- Three read-only chips: AI (`AI proposed`, `AI idle`), Kernel (`Kernel checked`, `Kernel RUNNING`, `Kernel not run`), Owner (`Owner deciding`, `Owner waiting for evidence`, `Owner decided`). Gerrit's attention set shows whose turn it is with an arrow before the name (S15b).
- The AI chip has no menu and no button. An agent is a delegate and the human stays responsible (Linear, S16). No palette command reachable from an agent or provider maps to Decide, approve or apply (I4).
- "Decide" is a plain button of 140 by 40 px. It is deliberately not the largest or the nearest target on the screen: Fitts and KLM would favour making it so, and the invariant that approval is deliberate wins (P2, LAW§3). Approve itself lives on the decision surface (A5).
- Rubber-stamp guard: 93% of prompts approved in one vendor's data (S13); cognitive forcing functions reduced overreliance in an experiment but participants rated them least favourably (S31); explanations reduce overreliance only when they are cheap to use (S32). The four-slot row is meant to be cheap; the study measures whether it is.

### 2.11 Small multiples

Three uses, all with the same axes and scale across panels and zero-based counts:

1. The before and after state pictures (level 0).
2. The ripple cells: eight cells of one design, so a reader compares by position.
3. The authority matrix (level 1, needs K7): five actors, each a 5 by 5 grid of states by actions, cells 20 px, one mark for accepted and a quiet mark for denied, shared row and column labels, before and after side by side. MEASURED: 6 accepted before, 7 after; added (registrar, Recommended, Approve), (registrar, Recommended, Reject), (teacher-assigned, Submitted, Recommend); removed (registrar, Submitted, Approve), (registrar, Submitted, Reject). Cells are graphics with a text alternative (a table); the interactive path is the list of accepted cells, each row at least 24 px high.

No bar encodes a value in v1, so no scale can be truncated. I did not open Tufte's own text; the description of small multiples rests on a secondary page (S22), and any wording of his rules is UNVERIFIED.

### 2.12 States

| State | Behaviour |
|---|---|
| No candidate | Rail rows show NOT_RUN; change pane says "No candidate. Select a meaning first." (6 words) |
| Verify pressed | Within 100 ms the row changes to RUNNING with elapsed seconds. The previous verdict stays and is marked STALE. MEASURED in three environments: the 125-cell run took 1.0 s (audit run), 1.9 s (audit run) and 2.7 s (my first run, slow HDD); a later run of mine gave 1.4 to 1.5 s (three warm runs in one process). All sit in the 1 to 10 s class: NN/g asks for a working indication there and for percent-done plus a way to interrupt only beyond 10 s (S8); the cancel control is added for jobs that can pass 10 s |
| Verification result | Rows update in place; a live region announces the roll-up once ("Evidence: 3 PASS, 1 UNKNOWN") |
| Evidence stale | STALE with reason and the current subject; rows keep their old bound |
| Kernel unavailable | "Kernel unavailable. Evidence is UNKNOWN." All rows UNKNOWN. Nothing is inferred |
| Hash changed under a Viewed mark | The mark clears and the row shows "changed since viewed" |
| Empty ripple kind | `0`, analysed |

### 2.13 Keyboard and palette

Focus order: operation list, change pane, rail. In the operation list Space toggles Viewed and Enter is not needed because selection follows focus. The ripple cells form a toolbar with arrow keys. Rail rows are a second tree (APG, S30): Down and Up, Space opens the level-1 coverage detail. The palette (owned elsewhere) contributes only navigation and evidence commands for this screen: Go to next unviewed operation, Go to next non-PASS claim, Show JSON diff, Verify. It has no Decide, approve or apply command. Every interactive target is at least 24 by 24 CSS px (SC 2.5.8, S24b); the smallest are the Viewed toggles at exactly 24.

## 3. What the kernel says today (MEASURED)

Method: I imported the kernel domain and application modules directly (no server, no browser) on 2026-09-29 and ran the baseline and candidate models. Windows 11, Python 3.12.10, pydantic 2.12.5 (the project pins 2.13.4; domain logic is not expected to differ, UNVERIFIED). Snippet in Appendix B. The counts come from a single run (they are deterministic); the verification time was sampled several times (row below) and is a range, not a constant.

| Fact | Value |
|---|---|
| Semantic operations for `enable_recommendation` | 4: ADDED state Recommended; ADDED transition TR-RECOMMEND; MODIFIED TR-APPROVE (`from_state` Submitted → Recommended); MODIFIED TR-REJECT (`from_state` Submitted → Recommended) |
| Operations for `set_rejection_source` to Submitted (on the candidate) | 1: MODIFIED TR-REJECT (`from_state` Recommended → Submitted) |
| Changed actions and affected nodes, first edit | 3 (Approve, Recommend, Reject); 20 nodes: rule 3, runtime 3, state-view 3, journey 3, obligation 3, receipt 3, review-packet 1, local-decision 1; closure complete |
| Second edit | 1 changed action; 8 nodes |
| Matrix cells | candidate 125 of 125 (5 x 5 x 5); baseline 100 (5 x 4 x 5); status PASS; 0 expected and actual mismatches |
| Accepted cells | candidate 7 (of 125); baseline 6 (of 100) |
| Verification time | Candidate matrix, timed inside `verify_runtime`; excludes HTTP and rendering. Samples: 2.73 s (my first run, workspace inside the checkout on the D: HDD); 1.88 s and 1.01 s (two audit runs, reported by the audit, not re-run by me, workspace on other disks); 1.41 to 1.52 s (three warm runs of mine on 2026-09-29, one process, `.tmp/` workspace). Machine and disk dependence is large, so the time is a range of about 1.0 to 2.7 s, not a constant. The flows use 2.73 s as a conservative upper value; it sits in both arms and cancels in the comparison but inflates absolute T06 totals |
| Non-semantic edit | fully reversing states, transitions and guards leaves the semantic hash equal; 49 of 75 raw JSON leaf values differ; 0 operations (the audit reproduced 75 leaves and 49 differing) |

The baseline UI (MEASURED by the layout lane's Chromium run, not re-run by me; section 5) never renders receipts, although the API payload carries them, and its packet shows 4 limitation strings, not the verifier's 5.

Mapping from kernel fields to the screen:

| Screen element | Kernel field |
|---|---|
| Operation list, summary line | K1 (new); `case.baseline`, `case.candidate` |
| Ripple cells | `packet.impact.affected`, `changed_actions`, `graph`, `complete`, `envelope` |
| Claim rows | `packet.technical_claims`, `packet.human_understanding` |
| Bound and covered | `case.receipts[].artifact.{expected_cells, matrix, protocol}` |
| Limits | `case.receipts[].artifact.limitations`, `packet.limitations` (typed by K3) |
| STALE and PASS per receipt | `packet.receipt_applicability[]` |
| Decision bar | `packet.status`, `packet.blockers`, `packet.eligible` |
| Subject id | `packet.subject_hash` |
| Counterexample rows | `case.receipts[].artifact.cells[]` where expected differs from actual |

## 4. Applying the research

### 4.1 Tufte

| Idea (source S22, secondary) | Application | Check |
|---|---|---|
| Data-ink: remove ink that carries no information | No boxes around groups; hairlines and alignment; 3 filled regions specified in the default state (rail, decision bar, selected row); chip and row treatment is not specified | Container count from the layout (section 5) |
| Small multiples | Section 2.11 | Identical scale across panels |
| Graphical integrity, lie factor | Counts are numerals; no bar in v1; any later bar starts at zero | Design rule |
| Mark the unknown, do not leave a gap | `?` cells, UNKNOWN chip, NOT covered slot | UNKNOWN count rendered equals model count (SLP M21) |

### 4.2 Cognitive Dimensions (Green and Blackwell, S27). Ratings are analyst judgement, not measurement

| Dimension | Baseline | Proposed | Why |
|---|---|---|---|
| Hidden dependencies | high | low | Ripple strip beside the change; JSON graph moves to level 2 |
| Visibility | low: UNKNOWN box below the fold (y 949 to 1042 at 900 px high) | high | UNKNOWN, bound and NOT covered at level 0 |
| Viscosity, knock-on | medium | medium | Reviewing does not change the model; a rename elsewhere still ripples, but now with a list |
| Premature commitment | low | low | Operations can be viewed in any order; decision is separate |
| Provisionality | medium | high | AI-proposed marks, dashed outlines, STALE kept visible |
| Role-expressiveness | low | medium | Verb, kind and chapter name the role of each operation |
| Error-proneness | high: a PASS card with no bound | medium | Bound and NOT covered beside PASS; UNKNOWN cannot roll into PASS |
| Secondary notation | n/a | layout by id, chapters | Owned by the diagram aspect |

### 4.3 Review and assurance tools

| Product pattern (source) | Verdict here |
|---|---|
| GitHub Viewed checkbox, progress, un-mark on change (S14) | Adopt; keyed by operation hash |
| Gerrit six statuses including NOT_APPLICABLE, OVERRIDDEN (S33) and attention set (S15b) | Adopt the idea of statuses that are not pass or fail and of a "whose turn" strip |
| Linear guided review: core first, supporting grouped apart (S9); the page did not describe ordering or Viewed | Adapt; chapters come from the model, not from a model |
| OpenSpec ADDED, MODIFIED, REMOVED (S10) | Adopt the words; here the deltas are kernel-derived, while the OpenSpec page describes agents drafting artifacts under human direction |
| CodeRabbit generates Mermaid walkthrough sequence diagrams (S11; the page does not say how changes are grouped) | Avoid model-written summaries as the review surface |
| EMF Compare compares and merges models at model level with any metamodel (S40); the page does not list difference kinds (UNVERIFIED) | Closest precedent for a model-derived diff; not opened deeply enough to adopt or rule out its difference kinds. Study the user guide before the kernel ADR for K1 |
| SemanticDiff hides syntax-only edits (S12) | Adapt with a hidden-edit counter |
| Nx affected (S18) | Adopt the conservative direction (mark more, not less); add the not-analysed kind |
| Jama Trace View gap mark (S19) | Adopt for `?` |
| TLA+ Toolbox trace (S20) | Adopt changed-only rows, jump to action |
| Dafny gutter (S6), GNATprove (S4), Stryker (S3), Quint and Alloy bounds (S5, S7) | Adopt per section 2.7 |
| GitHub skipped equals success (S1), Codecov default success (S2) | Avoid; the design exists to prevent this |
| Copilot approving review when enabled (S17), classifier auto mode (S13) | Avoid |

## 5. Numbers (budgets, geometry, predictions)

### 5.1 Screen budgets

Baseline figures are MEASURED by another lane's script (`.tmp/measure_current.py`, Playwright, one headless Chromium, the shipped assets, viewport 1440 by 900, an existing case opened, no notice box). I read `.tmp/current_measure.json` (gitignored) and, later, the same geometry as `design/layouts/current-evidence.json` and `current-impact.json` in the shared worktree (not yet committed). I did not re-run the measurement. Proposed figures come from the layout JSON in Appendix A and are a design specification, not a rendering.

| Metric | Baseline, evidence tab | Baseline, impact tab | Proposed, default state |
|---|---|---|---|
| Visible words, all | 134 | 156 | 164 |
| Visible chrome words (excluding model and kernel-supplied text) | 83 | 88 | 77 by my reconstruction (164 minus 46 claim words, 12 operation words, 18 picture words, 4 case title, 7 field-row words); different rule from the baseline, so UNKNOWN as a comparison |
| Distinct font sizes in the viewport | 12 | 12 | 5 by specification |
| Containers (border or fill, at least 2 children) | 7 | 9 | UNKNOWN: 3 specified fills plus 17 chips and rows with no specified border or fill, so 3 to 20 |
| Nesting depth | 2 | 2 | at most 3 |
| UNKNOWN items visible without scrolling | 0 of 1 (the box starts at y 949; fold at 900) | none on the tab | 2 of 2 (claim and not-analysed kinds) |
| Claims whose bound is visible | 0 of 3 | n/a | 3 of 3 |
| Claims whose NOT covered slot is visible | 0 of 4 | n/a | 4 of 4 |
| Interactive targets under 24 px | 0 | 0 | 0 (layout JSON check) |

Two states of the baseline matter. Right after a verification a notice box appears and pushes everything down by about 79 px (my estimate from the repo screenshot); the three PASS labels then sit at y of about 903 (read from the repo screenshot `evidence/studio-evidence.png`), just below the fold, and the word UNKNOWN is visible only in that transient notice. The proposed screen has 30 more visible words than the baseline evidence tab in total (164 against 134, both above the starting target of about 120; the two counts use different methods, so 30 is approximate). Three of the 30 are unit words added after the audit ("State views", "Runtime rows", "per changed action"), and they buy a label that names what the kernel counts. The extra words are evidence content, and P1 outranks P10 at level 0; this deviation is recorded in ADR-0063. No claim is made that chrome words fall: the 83 and 77 come from different counting rules.

Word rule: a token counts if it contains a letter or a digit. The layout lane treats the notice, blockers and boundary text as model content; I treat kernel-supplied claim rows, operation rows and diagram text as model content. The two rules differ, so the chrome-only figures are not compared; the prototype must re-count both screens with one rule.

### 5.2 Geometry

Current geometry is the layout lane's measurement. The task flows reference it as `current-evidence` and `current-impact` in `design/layouts/`. My own CSS-only estimate, made before I found that measurement, agreed with it within 8 px on the tabs, the verify button, the claim cards and the UNKNOWN box. Proposed geometry is a target. It exists only in Appendix A (`review-proposed`, `review-proposed-trace`) because my instructions restrict me to three files; the integrator should extract those two blocks to `design/layouts/` or grant the files. Until then the four proposed pointing operators in the task flows cannot be resolved by a reader of the repository alone, and the four Fitts times (0.588, 0.992, 0.790, 0.892 s; recomputed from Appendix A by the audit) are not reproducible from `design/layouts/`. The layout lane's `proposed-review.json` has different element ids and does not substitute.

### 5.3 Task-flow predictions

Computed by a script over `design/tasks/review-flows.json` and the layouts (kept in `.tmp/review/`, gitignored, so not reproducible from the repository). Full arithmetic is in ADR-0063, so every total can be checked by hand. The executable model lane can recompute the current flows from `design/layouts/` today and the proposed pointing operators once the two Appendix A blocks are extracted. B is 0.1 s per button press or release (S37), so each click is two B operators in the flows. **PREDICTION**, expert error-free users, KLM plus or minus 21 percent.

| Task | Current | Proposed | Motor plus response (current, proposed) | Total flips if current M is cut to 6, 4, 4, 5 and proposed M is doubled? |
|---|---|---|---|---|
| T02 Review by meaning | 14.78 s | 8.45 s | 2.63 s, 1.70 s | yes: 10.73 s against 15.20 s |
| T03 See the ripple | 10.73 s | 4.94 s | 2.63 s, 0.89 s | yes: 8.03 s against 8.99 s |
| T06 Run and read evidence | 14.99 s | 9.42 s | 6.89 s, 4.02 s | yes: 12.29 s against 14.82 s |
| T07 Inspect a counterexample | 17.65 s | 7.68 s | 8.20 s, 2.28 s | no: 14.95 s against 13.08 s |

The current flows answer weaker questions (no before state, no bound, no trace view), so the comparison is a lower bound for the current UI and not a like-for-like race. The claim is only that the proposed screen does not add pointing or typing. The current flows use the 1.1 s default for four off-screen pointing operators while the proposed flows use Fitts times of 0.59 to 0.99 s; with 1.1 s for the proposed operators too, proposed motor plus response rises by 0.1 to 0.5 s per task and stays below current in all four. Reading effort, which dominates, is not modelled by KLM.

Sensitivity to the Fitts profile (arbitrary alternative, not a sourced constant: a = 0.10 s, b = 0.20 s per bit, a slower slope and a shorter intercept; the values are my choice and are not taken from a source, so they test sensitivity only). Recomputed from Appendix A and the layout lane's geometry: current pointing operators become 0.659, 0.473 and 0.839 s (was 0.733, 0.613, 0.851); proposed become 0.436, 1.056, 0.745 and 0.904 s (was 0.588, 0.992, 0.790, 0.892). Motor plus response (current, proposed) becomes T02 2.56 and 1.70 s, T03 2.56 and 0.74 s, T06 6.74 and 4.09 s, T07 8.20 and 2.25 s: still lower or equal in the proposed flows in all four, and no comparison of totals changes sign. K, M, B, P and H constants rest on a secondary source (Wikipedia, S37); the primary (Card, Moran and Newell 1980) was not opened, so the constants are medium confidence.

## 6. Study support

The protocol is in ADR-0063 (Validation plan). Seeded cases for this aspect, all on the excursion domain; SD1 to SD3 use only the kernel's two supported edits:

| Id | Seeded condition | What a correct reviewer notices | Executable today |
|---|---|---|---|
| SD1 | `set_rejection_source` to Submitted after enabling recommendation | A registrar can reject before any recommendation | yes |
| SD2 | Verify, then edit the rejection source | The evidence is STALE; the decision needs a fresh run | yes |
| SD3 | Verified candidate, free-text question "what is proved?" | Human understanding is UNKNOWN; the matrix is one step and same-author | yes |
| SD4 | Reordering-only edit | Nothing meaningful changed; 0 operations | yes (needs an import path for a reordered file) |
| SD5 | A failing cell where an unassigned teacher can Recommend | Locate the missing guard from the trace | needs a sealed seeded receipt; not executable in the kernel |
| SD6 | Authority delta hidden inside a valid change | Registrar loses Submitted entry, gains Recommended entry | needs K7 |

Study arms. Three conditions, so that the kernel-free part of the change can be separated from the kernel-dependent part: **A** the baseline; **A+** the baseline with the receipts and the verifier's five limitations rendered and the UNKNOWN box moved above the fold, with no kernel change and no new payload field; **D** the proposed screen. A to A+ estimates what rendering data that already exists is worth (the baseline's two measured defects). A+ to D estimates what typed operations, the ripple strip and the typed four-slot row add on top. The study does not separate typed operations from the ripple strip or from the four-slot row inside D; that would need further arms, which I do not propose before A+ has been compared. A+ is also a candidate first release, because it needs no kernel ADR. In A+ the limitations appear as the verifier's flat list, so H1 (the typed fourth slot lowers overlooked UNKNOWN or NOT covered items) is tested as A+ against D, not as A against D.

Measures specific to this screen: UNKNOWN items misread as PASS (target zero), seeded conditions noticed, time from opening the decision surface to approval, share of UNKNOWN and NOT covered items opened before approval, "Not useful" marks if any AI text is shown, and the confidence-against-correctness calibration.

## 7. Risks, contradictions and what I could not verify

| # | Item | State |
|---|---|---|
| O1 | Whether four slots at level 0 are read or ignored | Untested. If participants skip NOT covered, move it to the decision surface and re-test |
| O2 | A ripple graph as an optional level-2 view | Deferred; needs the diagram aspect |
| O3 | Glyph legibility at 12 to 16 px and under CVD | Untested; needs a simulation and a discrimination test |
| O4 | Contrast of every status pair in light and dark | Not computed (colour aspect): UNKNOWN in the accessibility table |
| O5 | Reflow below 1280 px: three columns need about 1232 px after the rail | UNKNOWN; a bottom drawer for the rail is one option |
| O6 | Chapter rule K2 on changes the frozen vocabulary cannot yet produce | Untested beyond two transactions |
| O7 | Per-operation ripple (which nodes come from which operation) | The kernel groups by action; K1 and K6 would enable it |
| O8 | Whether a hash-keyed Viewed mark helps or hides new risk | Untested; the study logs Viewed-then-changed cases |
| O9 | The dashed outline marks both a STALE glyph and an AI-proposed operation edge, in different places | Confusion risk untested; if it shows, give AI-proposed a distinct edge treatment |
| O10 | Whether A+ alone removes most overlooked UNKNOWN items, which would make D's kernel additions (K1 to K7) a smaller win than they look | Untested; the three-arm study is designed to show it |
| C-a | Linear guided review: the dossier says core, consequences, glue; the page I opened says only core first and supporting grouped separately | Chapters are EIJA's own rule; Linear is precedent for core first only |
| C-b | SemanticDiff "cannot guarantee" wording in the dossier | Not confirmed by the pages I opened; UNVERIFIED |
| C-c | Reviewable per-revision marks (dossier) | Not confirmed; GitHub cited instead |
| C-d | Quint counterexample minimality (dossier) | Not on the page I opened; UNVERIFIED |
| C-e | Nx "over-approximates" | The page does not use the word; it describes lock-file and widely-used-project cases; the reading is mine |
| C-f | Small multiples originate in Envisioning Information (1990) per the secondary page, not the book the dossier names | Secondary source only |

## 8. Sources opened on 2026-09-29

| Id | URL | What I confirmed |
|---|---|---|
| S1 | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks | A skipped job reports Success and does not block a required check; conclusion values listed |
| S2 | https://docs.codecov.com/docs/commit-status | `if_not_found` defaults to success; `informational` passes regardless of coverage |
| S3 | https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ | Eight mutant states; two score denominators (valid, covered) |
| S4 | https://docs.adacore.com/spark2014-docs/html/ug/en/source/how_to_view_gnatprove_output.html | Columns Total, Flow, Provers, Justified, Unproved; Unproved is neither proved nor justified |
| S5 | https://quint.sh/docs/model-checkers | Apalache `--max-steps` defaults to 10; verified is always for a bound; no minimality statement found |
| S6 | https://dafny.org/blog/2023/04/19/making-verification-compelling-visual-verification-feedback-for-dafny/ | Quiet green bar for verified; obsolete (dimmed) and verifying (animated) states; shapes as well as colours for colour-blind users; optimistic default rationale |
| S7 | https://alloy.readthedocs.io/en/latest/language/commands.html | Default scope up to 3 per top-level signature; all Alloy models are bounded |
| S8 | https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1 s, 1 s, 10 s limits and the feedback each needs |
| S9 | https://linear.app/docs/diffs and https://linear.app/now/reviewing-code-in-the-agent-era | Guided review groups core parts first and supporting changes apart; chunks that read like a story; ordering and Viewed not described |
| S10 | https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md (read via raw.githubusercontent.com, github.com returned 503) and https://github.com/Fission-AI/OpenSpec | ADDED, MODIFIED, REMOVED delta sections merged on archive; the page says humans explore and agents draft artifacts; MIT licence |
| S11 | https://docs.coderabbit.ai/pr-reviews/walkthroughs | The page says CodeRabbit generates Mermaid sequence diagrams for pull requests with component interactions; it does not state how grouping or file summaries are produced |
| S12 | https://semanticdiff.com/docs/what-is-semanticdiff/ | Hides whitespace, optional commas, redundant parentheses; needs per-language rules |
| S13 | https://anthropic.com/engineering/claude-code-auto-mode | 93% of permission prompts approved; classifier false positive 0.4% (n=10,000), false negative 17% (n=52); vendor-reported |
| S14 | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request | Viewed checkbox, progress bar, un-marked when the file changes |
| S15 | https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf (Bacchelli and Bird, ICSE 2013; read as text) | Understanding is the reviewers' main challenge; 78 (14%) of sampled comments concerned defects |
| S15b | https://gerrit-review.googlesource.com/Documentation/user-attention-set.html | Attention set marks whose turn it is with an arrow before the name |
| S16 | https://linear.app/docs/assigning-issues | An agent cannot be the primary assignee; the human remains responsible |
| S17 | https://docs.github.com/en/copilot/concepts/agents/code-review | Copilot can submit an approving review that satisfies required approval when enabled; not guaranteed to spot all problems |
| S18 | https://nx.dev/docs/features/ci-features/affected | Affected from git, project graph and dependency tracing; lock-file change marks everything |
| S19 | https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/trace-view.html | Columns by level with counts; red exclamation mark for a missing required relationship |
| S20 | https://learntla.com/topics/toolbox.html | Error trace: expandable step rows, changed variables in red, hide unchanged, double-click to the action |
| S21 | https://kiro.dev/docs/specs/correctness/ | Property tests are evidence, not proof; failures shrink to the smallest input |
| S22 | https://en.wikipedia.org/wiki/Small_multiple (secondary) and https://www.edwardtufte.com/books/ (catalogue only) | Same scales and axes across repeated panels; Tufte's own text not opened |
| S23 | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | SC 1.4.1, Level A |
| S24 | https://pubmed.ncbi.nlm.nih.gov/21077562/ read through NCBI E-utilities (Parasuraman and Manzey, Human Factors 2010) | Abstract (re-read 2026-09-29): complacency and automation bias occur in naive and expert participants; complacency cannot be overcome with simple practice; bias cannot be prevented by training or instructions |
| S24b | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | SC 2.5.8, Level AA, 24 by 24 CSS px and five exceptions |
| S25 | https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html | SC 2.1.4, Level A: turn off, remap or active only on focus |
| S26 | https://www.nngroup.com/articles/progressive-disclosure/ | Beyond 2 disclosure levels usability is typically low (2006) |
| S27 | https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf | Definitions of the dimensions used |
| S28 | https://psychclassics.yorku.ca/Miller/ | Span about seven chunks; recoding into chunks is the lever |
| S29 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2864034/ | About 3 to 5 chunks when rehearsal and grouping are prevented |
| S30 | https://www.w3.org/WAI/ARIA/apg/patterns/treeview/ | Tree keyboard model and aria attributes |
| S31 | https://arxiv.org/abs/2102.09692 | Cognitive forcing functions reduced overreliance; least favourable ratings for the best designs |
| S32 | https://arxiv.org/abs/2212.06823 | Explanations reduce overreliance when the effort to use them is low relative to the benefit |
| S33 | https://gerrit-review.googlesource.com/Documentation/config-submit-requirements.html | Six submit requirement statuses, each inspectable |
| S34 | Repo files read: `src/eija_studio/domain/{evidence,impact,models,policy}.py`, `application/{compiler,verifier,service}.py`, `resources/web/{index.html,app.css,app.js}`, `README.md`, `docs/architecture/ARCHITECTURE.md`, `docs/adr/0018-formal-vv-portfolio.md`, `AGENTS.md` | Kernel behaviour and baseline UI as described |
| S35 | https://sback.it/publications/icse2018seip.pdf (Sadowski et al., ICSE-SEIP 2018; read as text) | Median 24 lines changed; analysis results carry a "Not useful" button and analyzers with high rates are fixed or disabled |
| S36 | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html and https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | 3:1 for graphical objects and components; 4.5:1 text; values are not rounded |
| S37 | https://en.wikipedia.org/wiki/Keystroke-level_model (secondary) | K 0.08 to 1.20 s, P 1.1, H 0.4, M 1.35, B 0.1 per button press or release (a click is 2 B), RMS error 21% |
| S38 | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf (Cockburn, Gutwin, Greenberg, CHI 2007; local text copy) | Pointing MT = 0.37 + 0.13 ID s; expert menu choice 0.24 + 0.08 log2 n |
| S39 | `design/layouts/{current-evidence,current-impact,proposed-review,proposed-evidence}.json`, `docs/hci/design/{language-and-ddd-tree,ai-interaction}.md`, `.tmp/current_measure.json`, all in the shared worktree, read on 2026-09-29 | Baseline geometry and other lanes' proposals (section 1.4) |
| S40 | https://eclipse.dev/emfcompare/ (index page and documentation index) | EMF Compare brings model comparison to the EMF framework, generic for any metamodel, compare and merge; the pages I opened do not list difference kinds (UNVERIFIED) |

## Appendix A. Proposed layout geometry (extract each block to `design/layouts/<stem>.json`)

Viewport 1440 by 900, CSS px, page coordinates. Both layouts are design targets, not measurements. `words` follows the token rule in section 5.1. The baseline layouts are the layout lane's `current-evidence.json` and `current-impact.json`. `__pointer` is the virtual pointer rest position used by the flows.

### `design/layouts/review-proposed.json`

Proposed review screen, default state. Design target.

```json
{"schema":"eija.layout.v1","ui":"proposed","screen":"review","viewport":{"w":1440,"h":900},"elements":[
 {"id":"topbar","role":"panel","x":0,"y":0,"w":1440,"h":40,"label":"shell top bar (owned by shell aspect)","importance":0.0,"words":0},
 {"id":"palette-trigger","role":"input","x":1000,"y":8,"w":240,"h":24,"label":"Search Ctrl+K","importance":0.6,"words":2},
 {"id":"navrail","role":"panel","x":0,"y":40,"w":48,"h":860,"label":"shell navigation rail (owned by shell aspect)","importance":0.0,"words":0},
 {"id":"case-title","role":"text","x":64,"y":48,"w":620,"h":24,"label":"Teacher recommends; registrar decides","importance":0.9,"words":4},
 {"id":"attention-ai","role":"chip","x":690,"y":52,"w":110,"h":24,"label":"AI proposed","importance":0.5,"words":2},
 {"id":"attention-kernel","role":"chip","x":808,"y":52,"w":120,"h":24,"label":"Kernel checked","importance":0.5,"words":2},
 {"id":"attention-owner","role":"chip","x":936,"y":52,"w":128,"h":24,"label":"Owner deciding","importance":0.5,"words":2},
 {"id":"summary","role":"text","x":64,"y":100,"w":600,"h":24,"label":"4 operations 2 ADDED 2 MODIFIED 0 REMOVED","importance":0.9,"words":8},
 {"id":"hidden-counter","role":"button","x":700,"y":100,"w":260,"h":24,"label":"0 non-semantic edits hidden","importance":0.5,"words":4},
 {"id":"chapter-core","role":"text","x":64,"y":140,"w":200,"h":20,"label":"Core","importance":0.6,"words":1},
 {"id":"op-1","role":"tree-item","x":56,"y":164,"w":320,"h":40,"label":"ADDED state Recommended","importance":0.8,"words":3},
 {"id":"op-1-viewed","role":"button","x":340,"y":172,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"op-2","role":"tree-item","x":56,"y":204,"w":320,"h":40,"label":"ADDED rule Recommend","importance":0.8,"words":3},
 {"id":"op-2-viewed","role":"button","x":340,"y":212,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"chapter-follow","role":"text","x":64,"y":256,"w":200,"h":20,"label":"Follows from core","importance":0.6,"words":3},
 {"id":"op-3","role":"tree-item","x":56,"y":280,"w":320,"h":40,"label":"MODIFIED rule Approve","importance":0.8,"words":3},
 {"id":"op-3-viewed","role":"button","x":340,"y":288,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"op-4","role":"tree-item","x":56,"y":320,"w":320,"h":40,"label":"MODIFIED rule Reject","importance":0.8,"words":3},
 {"id":"op-4-viewed","role":"button","x":340,"y":328,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"ops-progress","role":"text","x":64,"y":372,"w":300,"h":20,"label":"0 of 4 viewed","importance":0.3,"words":4},
 {"id":"caption-before","role":"text","x":392,"y":140,"w":320,"h":20,"label":"Before","importance":0.4,"words":1},
 {"id":"caption-after","role":"text","x":744,"y":140,"w":320,"h":20,"label":"After","importance":0.4,"words":1},
 {"id":"graph-before","role":"canvas","x":392,"y":164,"w":320,"h":140,"label":"state picture before: 4 states, 4 rules","importance":0.8,"words":8},
 {"id":"graph-after","role":"canvas","x":744,"y":164,"w":320,"h":140,"label":"state picture after: 5 states, 5 rules","importance":0.8,"words":10},
 {"id":"field-title","role":"text","x":392,"y":324,"w":672,"h":24,"label":"MODIFIED rule Approve","importance":0.8,"words":3},
 {"id":"field-row-1","role":"text","x":392,"y":352,"w":672,"h":28,"label":"from Submitted to Recommended","importance":0.9,"words":4},
 {"id":"fields-hidden","role":"button","x":392,"y":384,"w":200,"h":24,"label":"6 unchanged fields","importance":0.4,"words":3},
 {"id":"source-toggle","role":"button","x":600,"y":384,"w":120,"h":24,"label":"JSON diff","importance":0.3,"words":2},
 {"id":"ripple-title","role":"text","x":392,"y":432,"w":672,"h":20,"label":"Ripple, per changed action","importance":0.7,"words":4},
 {"id":"ripple-rules","role":"chip","x":392,"y":456,"w":84,"h":56,"label":"Rules 3","importance":0.7,"words":2},
 {"id":"ripple-states","role":"chip","x":476,"y":456,"w":84,"h":56,"label":"State views 3","importance":0.7,"words":3},
 {"id":"ripple-journeys","role":"chip","x":560,"y":456,"w":84,"h":56,"label":"Journeys 3","importance":0.7,"words":2},
 {"id":"ripple-tests","role":"chip","x":644,"y":456,"w":84,"h":56,"label":"Runtime rows 3","importance":0.7,"words":3},
 {"id":"ripple-evidence","role":"chip","x":728,"y":456,"w":84,"h":56,"label":"Evidence 6","importance":0.7,"words":2},
 {"id":"ripple-decision","role":"chip","x":812,"y":456,"w":84,"h":56,"label":"Decision 2","importance":0.7,"words":2},
 {"id":"ripple-personas","role":"chip","x":896,"y":456,"w":84,"h":56,"label":"Personas ?","importance":0.9,"words":2},
 {"id":"ripple-requirements","role":"chip","x":980,"y":456,"w":84,"h":56,"label":"Requirements ?","importance":0.9,"words":2},
 {"id":"ripple-unknown-line","role":"text","x":392,"y":520,"w":672,"h":20,"label":"Not analysed: personas, requirements have no model here","importance":0.9,"words":8},
 {"id":"rail","role":"panel","x":1080,"y":40,"w":360,"h":860,"label":"evidence rail","importance":0.0,"words":0},
 {"id":"rail-title","role":"text","x":1096,"y":100,"w":232,"h":20,"label":"Evidence 7f3a91c2","importance":0.6,"words":2},
 {"id":"verify-button","role":"button","x":1336,"y":96,"w":88,"h":28,"label":"Verify","importance":0.8,"words":1},
 {"id":"rollup-unknown","role":"chip","x":1096,"y":132,"w":112,"h":28,"label":"1 UNKNOWN","importance":1.0,"words":2},
 {"id":"rollup-pass","role":"chip","x":1216,"y":132,"w":88,"h":28,"label":"3 PASS","importance":0.5,"words":2},
 {"id":"claim-human","role":"tree-item","x":1080,"y":168,"w":360,"h":68,"label":"UNKNOWN Human understanding / none measured / not covered: any real reviewer","importance":1.0,"words":10},
 {"id":"claim-matrix","role":"tree-item","x":1080,"y":236,"w":360,"h":68,"label":"PASS Runtime matrix / 125 of 125 cells, 1 step / not covered: sequences, identity, durability","importance":0.9,"words":14},
 {"id":"claim-policy","role":"tree-item","x":1080,"y":304,"w":360,"h":68,"label":"PASS Protected policy / 5 of 5 rules / not covered: UNKNOWN","importance":0.8,"words":10},
 {"id":"claim-closure","role":"tree-item","x":1080,"y":372,"w":360,"h":68,"label":"PASS Impact closure / 20 nodes, declared mapping / not covered: effects outside mapping","importance":0.8,"words":12},
 {"id":"decision-bar","role":"panel","x":1080,"y":820,"w":360,"h":80,"label":"decision entry bar","importance":0.0,"words":0},
 {"id":"decide-button","role":"button","x":1096,"y":836,"w":140,"h":40,"label":"Decide","importance":0.9,"words":1},
 {"id":"decide-status","role":"text","x":1244,"y":836,"w":180,"h":40,"label":"Reviewable 1 UNKNOWN open","importance":0.7,"words":4},
 {"id":"__pointer","role":"text","x":720,"y":450,"w":1,"h":1,"label":"pointer rest position (virtual, not a UI element)","importance":0.0,"words":0}
]}
```

### `design/layouts/review-proposed-trace.json`

Proposed review screen with the counterexample stepper open (seeded fixture). Design target.

```json
{"schema":"eija.layout.v1","ui":"proposed","screen":"review-trace","viewport":{"w":1440,"h":900},"elements":[
 {"id":"topbar","role":"panel","x":0,"y":0,"w":1440,"h":40,"label":"shell top bar (owned by shell aspect)","importance":0.0,"words":0},
 {"id":"palette-trigger","role":"input","x":1000,"y":8,"w":240,"h":24,"label":"Search Ctrl+K","importance":0.6,"words":2},
 {"id":"navrail","role":"panel","x":0,"y":40,"w":48,"h":860,"label":"shell navigation rail (owned by shell aspect)","importance":0.0,"words":0},
 {"id":"case-title","role":"text","x":64,"y":48,"w":620,"h":24,"label":"Teacher recommends; registrar decides","importance":0.9,"words":4},
 {"id":"attention-ai","role":"chip","x":690,"y":52,"w":110,"h":24,"label":"AI proposed","importance":0.5,"words":2},
 {"id":"attention-kernel","role":"chip","x":808,"y":52,"w":120,"h":24,"label":"Kernel checked","importance":0.5,"words":2},
 {"id":"attention-owner","role":"chip","x":936,"y":52,"w":128,"h":24,"label":"Owner deciding","importance":0.5,"words":2},
 {"id":"summary","role":"text","x":64,"y":100,"w":600,"h":24,"label":"4 operations 2 ADDED 2 MODIFIED 0 REMOVED","importance":0.9,"words":8},
 {"id":"hidden-counter","role":"button","x":700,"y":100,"w":260,"h":24,"label":"0 non-semantic edits hidden","importance":0.5,"words":4},
 {"id":"chapter-core","role":"text","x":64,"y":140,"w":200,"h":20,"label":"Core","importance":0.6,"words":1},
 {"id":"op-1","role":"tree-item","x":56,"y":164,"w":320,"h":40,"label":"ADDED state Recommended","importance":0.8,"words":3},
 {"id":"op-1-viewed","role":"button","x":340,"y":172,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"op-2","role":"tree-item","x":56,"y":204,"w":320,"h":40,"label":"ADDED rule Recommend","importance":0.8,"words":3},
 {"id":"op-2-viewed","role":"button","x":340,"y":212,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"chapter-follow","role":"text","x":64,"y":256,"w":200,"h":20,"label":"Follows from core","importance":0.6,"words":3},
 {"id":"op-3","role":"tree-item","x":56,"y":280,"w":320,"h":40,"label":"MODIFIED rule Approve","importance":0.8,"words":3},
 {"id":"op-3-viewed","role":"button","x":340,"y":288,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"op-4","role":"tree-item","x":56,"y":320,"w":320,"h":40,"label":"MODIFIED rule Reject","importance":0.8,"words":3},
 {"id":"op-4-viewed","role":"button","x":340,"y":328,"w":24,"h":24,"label":"Viewed","importance":0.4,"words":0},
 {"id":"ops-progress","role":"text","x":64,"y":372,"w":300,"h":20,"label":"0 of 4 viewed","importance":0.3,"words":4},
 {"id":"rail","role":"panel","x":1080,"y":40,"w":360,"h":860,"label":"evidence rail","importance":0.0,"words":0},
 {"id":"rail-title","role":"text","x":1096,"y":100,"w":232,"h":20,"label":"Evidence 7f3a91c2","importance":0.6,"words":2},
 {"id":"verify-button","role":"button","x":1336,"y":96,"w":88,"h":28,"label":"Verify","importance":0.8,"words":1},
 {"id":"claim-human","role":"tree-item","x":1080,"y":168,"w":360,"h":68,"label":"UNKNOWN Human understanding / none measured / not covered: any real reviewer","importance":1.0,"words":10},
 {"id":"claim-policy","role":"tree-item","x":1080,"y":304,"w":360,"h":68,"label":"PASS Protected policy / 5 of 5 rules / not covered: UNKNOWN","importance":0.8,"words":10},
 {"id":"claim-closure","role":"tree-item","x":1080,"y":372,"w":360,"h":68,"label":"PASS Impact closure / 20 nodes, declared mapping / not covered: effects outside mapping","importance":0.8,"words":12},
 {"id":"decision-bar","role":"panel","x":1080,"y":820,"w":360,"h":80,"label":"decision entry bar","importance":0.0,"words":0},
 {"id":"decide-button","role":"button","x":1096,"y":836,"w":140,"h":40,"label":"Decide","importance":0.9,"words":1},
 {"id":"rollup-fail","role":"chip","x":1096,"y":132,"w":72,"h":28,"label":"1 FAIL","importance":1.0,"words":2},
 {"id":"rollup-unknown","role":"chip","x":1176,"y":132,"w":112,"h":28,"label":"1 UNKNOWN","importance":1.0,"words":2},
 {"id":"rollup-pass","role":"chip","x":1296,"y":132,"w":88,"h":28,"label":"2 PASS","importance":0.5,"words":2},
 {"id":"claim-matrix","role":"tree-item","x":1080,"y":236,"w":360,"h":68,"label":"FAIL Runtime matrix / 124 of 125 cells match / not covered: sequences, identity, durability","importance":1.0,"words":13},
 {"id":"decide-status","role":"text","x":1244,"y":836,"w":180,"h":40,"label":"Blocked runtime FAIL","importance":0.7,"words":3},
 {"id":"trace-back","role":"button","x":392,"y":140,"w":136,"h":24,"label":"Back to change","importance":0.5,"words":3},
 {"id":"trace-title","role":"text","x":392,"y":172,"w":672,"h":24,"label":"FAIL teacher-unassigned Submitted Recommend","importance":0.9,"words":4},
 {"id":"trace-label","role":"text","x":392,"y":200,"w":672,"h":20,"label":"1 step, minimal. Replay runtime_matrix:teacher-unassigned/Submitted/Recommend","importance":0.6,"words":6},
 {"id":"trace-table","role":"panel","x":392,"y":232,"w":672,"h":200,"label":"variables that differ: expected vs actual (6 rows)","importance":1.0,"words":30},
 {"id":"step-back","role":"button","x":392,"y":448,"w":96,"h":32,"label":"Step back","importance":0.5,"words":2},
 {"id":"step-next","role":"button","x":496,"y":448,"w":96,"h":32,"label":"Step","importance":0.5,"words":1},
 {"id":"step-play","role":"button","x":600,"y":448,"w":96,"h":32,"label":"Play","importance":0.3,"words":1},
 {"id":"step-jump","role":"button","x":704,"y":448,"w":220,"h":32,"label":"Jump to rule TR-RECOMMEND","importance":0.7,"words":4},
 {"id":"step-position","role":"text","x":932,"y":448,"w":132,"h":32,"label":"Step 1 of 1","importance":0.3,"words":4},
 {"id":"__pointer","role":"text","x":720,"y":450,"w":1,"h":1,"label":"pointer rest position (virtual, not a UI element)","importance":0.0,"words":0}
]}
```

## Appendix B. Reproducing the kernel facts

```python
import sys; sys.path.insert(0, "src")
from pathlib import Path
from eija_studio.domain.policy import baseline, apply_transaction
from eija_studio.domain.models import SemanticTransaction
from eija_studio.domain.impact import model_impact
from eija_studio.adapters.sqlite_store import sandbox_factory
from eija_studio.application.verifier import verify_runtime

before = baseline()
after = apply_transaction(before, SemanticTransaction(kind="enable_recommendation"))
impact = model_impact(before, after)          # changed 3, affected 20, complete True
ws = Path(".tmp/ws"); ws.mkdir(parents=True, exist_ok=True)
subject = {"semantic": after.semantic_hash, "implementation": "x", "policy": "x", "environment": "x", "harness": "x", "presentation": "x"}
receipt = verify_runtime(after, subject, sandbox_factory(ws))   # 125 cells, 7 accepted
```

Operations come from comparing states and transitions by id and field. Reversing `states`, `transitions` and `guards` leaves `semantic_hash` unchanged.
