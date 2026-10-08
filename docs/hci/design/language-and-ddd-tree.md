# Language and DDD tree: design for the ubiquitous-language spine

Aspect `language-ddd-tree`. Lane `lane/ux-research`. Date 2026-09-29. Status: proposed; the decision record is [HCI-ADR-0062](../../adr/0062-hci-language-ddd-tree.md). Nothing here measures an EIJA user. Numbers are labelled PREDICTION (a model output), MEASURED (a command run on this repository at commit `ddc43b9`) or DESIGN COUNT (counted from the layout in Appendix B or from a stated rule, not from a built page). This is revision 3, written after audits of revisions 1 and 2; section 10 lists what changed.

Source ids: `AIC`, `ADC`, `DGM`, `REQ`, `MOK`, `REV`, `LAW`, `VIS`, `DEV`, `SLP`, `V1`-`V7`, `R1`-`R3` are defined in [SYNTHESIS.md](../research/SYNTHESIS.md) section 1. `L1` to `L29` are pages and files I opened myself on 2026-09-29 (Appendix A). Where a row says "dossier only", I did not re-open the page.

## 0. Decisions first

| # | Decision | Main evidence | Confidence |
|---|---|---|---|
| D1 | One `role="tree"` in the shell's 296 px sidebar is the spine: context, aggregate, then entity, value object, invariant and term. Depth at most 4, enforced by the kernel. One focus stop per row, roving tabindex. | APG tree pattern (L1); APG treegrid needs every cell focusable (L2); Productboard depth advice (L14); sample tree has depth 4 and 43 nodes (MEASURED, section 4.1) | Medium |
| D2 | Row anatomy at level 0: kind letter, name, one status shape (subtree-worst when collapsed, own when expanded), change mark A, M or +, homonym mark. The status word is not drawn in the rail (recorded deviation, 4.1a); it is in the header, the footer counts and the accessible name. PASS from a scoped record reads "PASS local". No trace counts on unselected rows. | DOORS Next admins can hide per-link icons "to reduce the clutter" (L10); Storybook status per row plus footer roll-up (L12); DESIGN COUNT: 122 chrome words against 198 for per-row counts | Medium |
| D3 | Selection drives an inspector (level 1): definition, binding, four trace chips (code, requirements, tests, wiki), ripple summary, AI verbs. Raw source is level 2. Nothing deeper. | Jama Trace View: source item, counts per level, gap mark (L9); NN/g two-level rule (L20, medium) | Medium |
| D4 | Every edit is a typed request. Operation-level unavailability is shown at gesture start, instance-level refusal at the drop or edit target, always with a reason. A confirm sheet appears only when the ripple has a non-generated edge. Today 1 of 10 tree gestures executes; the rest are refusals, shown with their reason and not hidden (hypothesis H3, 4.5). | LSP change annotation `needsConfirmation` (L8); VS Code refactor preview (L6); ADR-003 (repo) | Medium |
| D5 | Rename changes a label and keeps the stable id. Kernel-bound identifiers (states, roles, actions) refuse rename and offer an alias. Ripple is four tiers: regenerated, suspect, text match, not analysed. Prose is never edited automatically. | Green and Blackwell knock-on viscosity (L23); DOORS Next default validity attributes (L10); OpenFastTrace revision in the id (L11); MEASURED text tier for one term: 19 files | Medium |
| D6 | Drag re-parents with a client-side legal-parent matrix, a 2 px drop line and a refusal reason on the target. The non-drag path is Move to (a tree picker in a modal) and the palette. Both emit the same operation. | WCAG 2.5.7 (L4); Atlassian move menu for trees (L15); Structurizr: re-parenting is hard in a UI (L16, vendor) | Medium |
| D7 | Visible filter field, three modes (Highlight, Path, Flat) plus a fuzzy toggle, facet tokens, sidebar-footer counts that filter on click, and a counter that always reports hidden UNKNOWN, NOT_RUN, STALE, FAIL and CONFLICT rows. | VS Code highlight and filter modes with a badge on folders (L5); Notion scope modes (L13, differs: see 3); Storybook click-count-to-filter (L12) | Medium |
| D8 | Trace chips show count, worst check status and tier (kernel-derived, text match, not analysed). A missing required link is a gap mark. Wiki and requirement tracing are interfaces to other lanes. | Jama gap mark (L9); OKF v0.2 links are untyped (L17); OpenFastTrace needs and covers (L11); Code Connect describes no maintenance of the mapping (L18) | Medium |
| D9 | AI verbs at a term: propose a definition, list duplicate or homonym candidates, propose a name for an unnamed concept, explain a homonym. Output is provisional and grounded; AI never renames, moves, adopts or approves. | ADR-004; P9; I4; I8 | High for the invariant, medium for the verbs |
| D10 | Structure rules: same label in two contexts is a homonym shown on both rows (example: Approve); sibling order is declared for contexts, lifecycle for states and actions, otherwise kind then label; no reorder gesture in v1. | Fowler on polysemes (L21); repo: `Approve` in Execution and in Governance | Medium |

What this design does not claim: that developers will like it or decide better. The study in the ADR is the test.

## 1. Scope and stated interfaces

I own the tree, its inspector, editing, filter and chips. I depend on other aspects and I state each assumption instead of guessing.

| Aspect | What I assume | What breaks if wrong |
|---|---|---|
| Status and colour | Closed evidence words PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN (C2). One shape per word, PASS least conspicuous. A PASS whose record limits its scope carries the qualifier: "PASS local" (4.1). Display severity order CONFLICT, FAIL, STALE, UNKNOWN, NOT_RUN, PASS (mine, proposed). Tokens `status.*`, `accent`, `surface.rail` (one elevation step), `focus`. HCI-ADR-0063 wants glyph plus word wherever a status is shown; the rail deviates (4.1a). | Row needs 16 px for the shape; a wider glyph shrinks the name; if the status lane requires the word in the rail, names lose 60 px |
| Type | HCI-ADR-0060 roles: caption 12, ui 14, prose 16, code 14, code-small 12 px; row names in ui 14 px; the average sans character is 0.529 em, 7.4 px at 14 px (typography.md section 3.3, MEASURED there). One sans and one mono; mono for ids, kind letters, paths. | Names truncate earlier or later; the truncation count in 4.2 moves |
| Palette | Prefix `t` for terms; commands Rename, Move to, Add term, Add alias, Retire term, Ask AI to propose; each shows enabled, blocked with reason, or AI-proposal; no approve or apply; workflow action names qualified (see D10) | Move to and Add term lose their keyboard path |
| Review and ripple | The tree receives `change.operations[]` with `element_id` and verb ADDED, MODIFIED or REMOVED and shows marks. Chapters and the full ripple lane live elsewhere. | Marks show nothing |
| Shell | `design/layouts/proposed-language.json` (layout lane): top bar 40 px, sidebar 296 px with 272 px of content, inspector 392 px with 360 px of content, status bar 28 px at 1440 by 900; HCI-ADR-0057 gives the content widths 272 and 360. Six lens tabs (Language, States, Journeys, Requirements, Tests, Personas) sit in the main region. At 1024 by 768 the layout lane's sidebar is a 40 px rail, so the tree would be a drawer (ASSUMPTION, 4.2). Revision 1 assumed a 400 px rail and a 48 px top bar: that was wrong | Names truncate (9 to 11 of 43 at 296 px, 11 to 13 at 272 px); budgets need a re-count; the tree is hidden at 1024 unless the IA lane opens it |
| Diagrams | Selection is shared by stable id. Layout is stored by the diagram aspect; the tree stores none. | Two selections that drift |
| Kernel and API | A language catalogue, typed language operations, bindings with tiers, suspect and drift checks. Section 4.12 lists what needs a kernel ADR. | Only stage 1 (read-only tree) is deliverable |
| Knowledge base (OKF lane) | A resolver from term id to wiki pages with `status`, `stale_after` and link tier | Wiki chip stays "not analysed" |
| Study lane | Protocol file under `docs/hci/design/` | The ADR carries an inline protocol |

## 2. Job, personas, tasks

Personas and frequencies are hypotheses from [personas-and-jtbd.md](../personas-and-jtbd.md).

| Task | Persona | Frequency | What the tree must let them do |
|---|---|---|---|
| T05 Edit the language tree | P2 primary, P3 reads | weekly | Rename, add, move a term; see the ripple before accepting |
| T09 Find anything | P1 | daily | Reach a term and read its definition, status and chips |
| T11 Resolve stale or suspect | P2 | weekly | See the causing diff; clear by a logged decision |
| T12 Map a concept to code | P1, P4 | weekly | Read the code chip: symbol, last check, drift or UNKNOWN |
| T13 Ask AI at a selected element | P3 | weekly | Ask, read a provisional proposal, adopt as an owner edit |
| T14 Find gaps | P4, P3 | weekly | One click from a gap count to the rows |

Jobs J4, J5, J6 (persona P2): see every dependent artefact when the language changes; keep tree, diagram and model in step without hand-syncing; see why something is suspect and clear it by a recorded decision.

## 3. Benchmarks: requirement-tool trees and IDE explorers

"Take" and "avoid" are my judgement. "Opened" means I read the page on 2026-09-29.

| Product or standard | Pattern | Take or avoid | Source (opened) |
|---|---|---|---|
| W3C ARIA APG tree | Enter activates; Up and Down move; Right opens or moves to the first child; Left closes or moves to the parent; Home, End; type-ahead; `*` expands siblings; `aria-level`, `aria-setsize`, `aria-posinset` when nodes load lazily; focus and selection are distinct. The page does not describe editing or drag and drop. | Take the keys. Add F2 and Move to myself | L1 |
| W3C ARIA APG treegrid | Rows and cells are focusable; arrows move between cells | Avoid: per-row chips would add tab stops and cells. Use `tree` | L2 |
| VS Code Explorer | Drag and drop to move files and folders; Ctrl+Alt+F opens Find with two modes, highlight and filter, and an exact or fuzzy toggle; in highlight mode folders that contain matches show a badge. The page says files and folders can be renamed in the Explorer but names no rename key (re-checked 2026-09-29; revision 1 credited F2 to this page in error) | Take both modes, the fuzzy toggle and the ancestor badge | L5 |
| VS Code refactoring | Rename Symbol is F2 in the editor; Refactor Preview lets you deselect changes before applying | Take preview then partial apply for the text tier. F2 on a tree row is my choice by analogy with Rename Symbol; the Explorer's file-rename key is UNVERIFIED here | L6 |
| JetBrains rename | Shift+F6; Preview lists usages; options for comments, strings and text occurrences | Take the separate text-occurrence tier | L7 |
| LSP 3.17 `ChangeAnnotation` | A server can flag grouped edits as needing user confirmation | Take: confirm only what is not generated | L8 |
| Jama Trace View | Columns by level from a source item, unique counts in each header, a red exclamation mark where a required link is missing, arrows upstream and downstream, inline edit in a slide-out panel | Take counts and gap mark; put them in the inspector, not on every row | L9 |
| Jama suspect clearing | Clear one or Clear All; the page names no permission, audit trail or reason | Avoid Clear All and reasonless clearing | L9b |
| DOORS Next link validity | Six default attributes affect validity (Artifact Format, Description, Diagram Content, Identifier, Primary Text, Title); State does not; a validity icon per link that admins can turn off "to reduce the clutter" | Take per-field validity; take one glyph per row, not a badge stack | L10 |
| OpenFastTrace | Item ids are `type~id~revision`; needs and covers lists; a link to an item with a higher revision is Outdated, to a lower one Predated (spec design document); licence GPL-3.0 (README) | Take the revision-in-id idea for suspect. Licence needs a decision in the tracing lane | L11, L11b |
| Storybook Vitest addon | A status indicator on each story and component; totals in a testing widget; press the failure count to filter (where the widget sits was not confirmed) | Take: status in the tree, count as filter; the roll-up at the foot of the tree is my placement | L12 |
| Notion sub-items | Filter scope: parents only, parents and sub-items, or sub-items only; display: nested or flattened | Take the idea of explicit scope. "Sub-items only" shows children without their parents, a precedent for a Flat-like mode; the page does not say whether ancestors stay visible in the other scopes, so Path (matches plus ancestors) is my own | L13 |
| Productboard | Five levels; drag and drop to re-parent; "avoid adding subcomponents to subcomponents" | Take a stated depth budget; ours is 4 | L14 |
| Atlassian design system | Every drag needs a non-drag route; for trees a Move menu item opens a modal with all movement outcomes; a drop indicator line | Take Move to and the drop line | L15 |
| Structurizr | Vendor argument: as models grow, elements are harder to find and "re-parenting" is not easy in a UI; supports automatic then manual layout | Counter-evidence for drag as the main route; keeps Move to and a confirm sheet | L16 |
| Figma Code Connect | Maps design components to repository components; the page says nothing about keeping the mapping current | Gap we can fill: checked mapping with a last-check result (absence in one page only) | L18 |
| DDD sources | Fowler: a bounded context divides a model; the same word can mean different things in different parts (utility "meter"); ubiquitous language is model-based and evolves; references from outside an aggregate go to its root | Take homonyms as a first-class case | L19, L21 |
| Archi (ArchiMate) | README does not describe its model tree | UNVERIFIED; not built on | L22 |
| Ilograph resource tree; Figma layers panel | dossier only (DGM§2.10, MOK§2.1) | Cited only as context | none |

## 4. The design

### 4.1 Content model

Six kinds. The letter is text in the mono face, not an icon. The kind word appears in the inspector, in the accessible name and in the tooltip. Whether users recognise the six letters is a study item.

| Letter | Kind | Legal parent | Required link (default, owner may change; DATA not code) | Note |
|---|---|---|---|---|
| C | Context (the repo says "bounded area") | root | none | 5 in the sample |
| A | Aggregate | C | code symbol | Only Change Case is declared an aggregate in code (`domain/change_case.py`); the other four are proposed classifications |
| E | Entity | A | none | none in the sample |
| V | Value object | A or E | none | |
| I | Invariant | C, A or E | test | each maps to an acceptance criterion in the sample |
| T | Term | C, A, E or V | bound model element runs under the runtime-matrix claim | states, actions, roles, other vocabulary |

Depth is at most 4: context, aggregate, value object, term. The kernel refuses a move or add that exceeds it (`DEPTH_BUDGET`). Productboard uses a five-level structure and advises against nesting subcomponents in subcomponents (L14); it gives no rationale for a particular depth, and the limit of 4 here comes from the brief. NN/g's two-level rule (L20) is about disclosure levels, not tree depth; I use it only for disclosure (D3).

Own status of a row: proposed rules R1 to R4. They need a kernel ADR; stage 1 approximates them from the catalogue and from repository records (declared, not kernel-computed, and labelled so).

| Rule | Situation | Row status |
|---|---|---|
| R1 | A required link is absent | UNKNOWN, never PASS |
| R2 | A required link exists and its check never ran | NOT_RUN |
| R3 | The check ran | PASS, FAIL, CONFLICT or STALE as the kernel computes. A PASS keeps the scope of its record (mapping below) |
| R4 | The row has several statuses (its own check and the requirement links of its chips) | The worst by display severity. A text-match link can only lower a status to UNKNOWN: it never raises one and never asserts FAIL, STALE or CONFLICT. A row with no required link and no claim shows no status; its chips still show theirs |

The repository's acceptance vocabulary is not the kernel's. `v0_2_status` in `docs/verification/ACCEPTANCE_MATRIX.csv` has 17 PASS_LOCAL, 9 PARTIAL, 2 NOT_RUN and no plain PASS (MEASURED by script, 2026-09-29). `docs/verification/VERIFICATION.md` says PASS_LOCAL "means only the declared synthetic/local portion was exercised". The mapping:

| Matrix word | Row status | Rendering |
|---|---|---|
| PASS_LOCAL | PASS with scope `local` | Written "PASS local" wherever a word is shown: inspector header, footer count, accessible name. The row's `v0_2_scope_note` is in the inspector. A bare PASS is drawn only for a record that declares no scope limit; the repository has none |
| PARTIAL | UNKNOWN | The inspector shows two lines, covered (PASS local) and not covered (UNKNOWN), from the scope note |
| NOT_RUN | NOT_RUN | Plain |

**Where the PASS of a state or action row comes from.** The ten term rows for the five states and the five actions bind to the model elements that the runtime-matrix claim enumerates. `assess_receipt(receipt, subject, "runtime_matrix", "integration_test")` in `domain/evidence.py` returns PASS only if the receipt's technical subject dimensions match the candidate, the producer is `eija-local-verifier`, the method is `bounded-runtime-matrix-v1`, the observed cells are exactly actors by states by actions (5 synthetic actors; the baseline states or the baseline plus Recommended; the 5 actions) and every cell's expected equals its actual. That is a kernel result. Its scope is one-step experiments on synthetic fixtures with an oracle written alongside the implementation (VERIFICATION.md), so it also reads "PASS local". The role terms Teacher and Registrar carry no status in stage 1: the matrix actors (teacher-assigned, teacher-unassigned, teacher-revoked, registrar, viewer) are fixtures, not roles, and no binding between them is recorded.

**Where an invariant's status comes from.** The required link of an invariant is a test. Stage 1 reads the acceptance row as a declared link (tier "declared", recorded by people, not computed by the kernel) and the files in its `v0_2_evidence` column as the test link, at file granularity. AC28 names only `docs/verification/VERIFICATION.md`, so it has no test link: R1 makes the row UNKNOWN (gap: test) although the criterion reads NOT_RUN, and UNKNOWN is the worse of the two.

**Worked example, Reject.** Its own claim, the matrix cell, is PASS local. Its requirements chip resolves by text match to AC12, which is PARTIAL because the oracle is same-author (VERIFICATION.md). By R4 the row reads UNKNOWN and the why-line in the header names the chip (4.2). The same rule turns 8 of the 10 state and action rows to UNKNOWN, because AC12 (the transition table) and AC15, both PARTIAL, name them. Text match over-approximates, so this errs in the safe direction (it never rounds up) and it is noise that recorded id links would remove. It cannot separate the homonym Approve: both Approve terms would receive AC08 and AC12 (the Governance Approve has no claim and shows no status).

Collapsed rows show the worst status in their subtree. Expanded rows show only their own status, because the children show theirs. The sidebar footer always counts every row.

**Sample tree (real excursion domain).** Names come from `docs/architecture/ARCHITECTURE.md`, `domain/policy.py` and `docs/verification/ACCEPTANCE_MATRIX.csv`. Kind classification is proposed by this document. Statuses are derived by R1 to R4 and the mapping above (AC ids shown); the Studio produces none of them for language items today. Bracket = worst status in subtree; "own" = the row's own status.

```
C Authoring   [subtree UNKNOWN]
  A Change Case   [own UNKNOWN]
    V Meaning Selection   [no status]
    V Proposal   [no status]
    V Semantic Transaction   [no status]
      T enable_recommendation   [no status]
      T set_rejection_source   [no status]
    I Layout keeps domain evidence   [own UNKNOWN]  AC03 PARTIAL
    I Provider never selects meaning   [own PASS local]  AC07
C Execution   [subtree UNKNOWN]
  A Preview Instance   [own UNKNOWN]
  A Workflow Definition   [own UNKNOWN]
    V Role   [no status]
      T Registrar   [no status]
      T Teacher   [no status]
    V State   [subtree UNKNOWN]
      T Draft   [own PASS local]
      T Submitted   [own UNKNOWN]  AC12 text match
      T Recommended   [own UNKNOWN]  ADDED; AC12, AC15 text match
      T Approved   [own UNKNOWN]  AC15 text match
      T Rejected   [own PASS local]
    V Transition   [subtree UNKNOWN]
      T Submit   [own UNKNOWN]  AC12 text match
      T Recommend   [own UNKNOWN]  ADDED; AC12 text match
      T Approve   [own UNKNOWN]  MODIFIED, homonym x2; AC08, AC12 text match
      T Reject   [own UNKNOWN]  MODIFIED; AC12 text match
      T Revise   [own UNKNOWN]  AC12 text match
    I No teacher final approval   [own PASS local]  AC09
    I Recommend is not approval   [own UNKNOWN]  AC21 PARTIAL
    I Recommend needs assignment   [own PASS local]  AC10
    I Reject prerequisite state   [own UNKNOWN]  AC12 PARTIAL, MODIFIED
C Assurance   [subtree UNKNOWN]
  A Evidence Receipt   [own UNKNOWN]
  I Impact reports frontier   [own PASS local]  AC16
  T Review Packet   [no status]
C Governance   [subtree UNKNOWN]
  A Local Decision   [own UNKNOWN]
    T Apply   [no status]
    T Approve   [no status]  homonym x2
  I Human understanding UNKNOWN   [own UNKNOWN, gap: test]  AC28 NOT_RUN
  T Authority   [no status]
C Provider integration   [no status]
  T Proposal Provider   [no status]
```

Counts (DESIGN COUNT: R1 to R4 applied to this list and to the matrix rows; revision 2): 43 nodes; per level 5, 10, 14, 14; largest sibling group 7 (children of Workflow Definition); 8 invariants; 23 rows carry an own status: 6 PASS local, 17 UNKNOWN, 0 NOT_RUN, 0 FAIL, 0 STALE, 0 CONFLICT; 1 gap: test. Revision 1 reported 14 PASS, 8 UNKNOWN and 1 NOT_RUN: that rounded PASS_LOCAL up to PASS and ignored the PARTIAL criteria that the rows link to (section 10). Sibling order: contexts keep the declared context-map order (`ARCHITECTURE.md`); states and actions follow the lifecycle (first reachability from the initial state); everything else is by kind (aggregate, entity, value object, invariant, term) then label. There is no reorder gesture in v1.

**4.1a Status in the rail: a recorded deviation.** Revision 1 drew a 60 px status word beside every non-PASS row. The shell's sidebar is 296 px wide, not 400 (section 1). With the word column the name gets 116 px at level 1 down to 68 px at level 4, about 15 to 9 characters at 7.4 px per character; without it 176 to 128 px (about 24 to 17 characters). HCI-ADR-0063 wants a glyph and a word wherever a status is shown. In the rail this design draws the glyph only. The word is in the inspector header, in the footer counts (each count carries its word), in the accessible name of the row and in the tooltip. The cost is that six glyphs must be told apart by shape alone (colour-vision simulation UNKNOWN; the status lane owns the shapes) and the study measures it (section 8). If the shell offered a sidebar of about 400 px the word column would return.

### 4.2 Primary viewport (1440 by 900, Reject selected in a verified candidate)

Geometry is the shell's (section 1): sidebar 296 px holds the tree, the main region holds the Language lens for the selected term, the inspector column holds the ripple and the AI verb. Appendix B has the coordinates.

```
EIJA Studio  Let teachers sign off excursions. rev 3  Changes Model Evidence     [ Search or run  Ctrl K ]   offline local
+----------------------------+------------------------------------------------------+---------------------------+
| [ Filter                  ]| Language States Journeys Requirements Tests Personas |                           |
| Highlight Path Flat  Fuzzy | Reject  UNKNOWN MODIFIED         Move Rename Add term| Ripple 8 nodes            |
| > C Authoring            u | Term in Workflow Definition, Transition              | rule 1 state 1 journey 1  |
| v C Execution              | The Registrar rejects an excursion from Recommended. | runtime 1  obligation 1   |
|   > A Preview Instance   u | Before this case: from Submitted.                    | receipt 1 packet 1        |
|   v A Workflow Definition u| Model element TR-REJECT, kernel-derived      Source  | decision 1                |
|     > V Role               | Worst chip: requirements, AC12 PARTIAL (text match)  |                           |
|     > V State          + u | [code 5] [requirements 1] [tests 1] [wiki 0]         | Not analysed              |
|     v V Transition       u | code, tier: text match (heuristic)                   | wiki bundle, outside      |
|         T Submit         u |   policy.py                                          | mapping                   |
|         T Recommend    A u |   verifier.py                                        |                           |
|         T Approve  x2  M u |   evidence.py                                        | [ Ask AI to propose ]     |
|[        T Reject       M u]|   app.js                                             |   provider call           |
|         T Revise         u |   index.html                                         |                           |
|       I No teacher fina… p |                                                      |                           |
|       I Recommend is no… u |                                                      |                           |
|       I Recommend needs… p |                                                      |                           |
|       I Reject prerequi… M u|                                                     |                           |
| > C Assurance            u |                                                      |                           |
| > C Governance           u |                                                      |                           |
| > C Provider integration   |                                                      |                           |
| 6 PASS local   17 UNKNOWN  |                                                      |                           |
| 0 NOT_RUN  0 FAIL  1 gap: test                                                    |                           |
+----------------------------+------------------------------------------------------+---------------------------+
1 UNKNOWN  0 FAIL  0 CONFLICT  0 STALE  6 NOT_RUN  3 PASS  0 need you 0 running                      VERIFIED
```

The wireframe is schematic. `>` is a collapsed parent, `v` an expanded parent, the selected row is in square brackets (the design uses a filled row), `+` is the contains-changes mark, `u` and `p` stand in for the glyphs of UNKNOWN and PASS local (the status lane owns the real shapes), and the chip list is compressed. `…` marks a truncated name (design count below). The shell's status bar is drawn with the layout lane's sample values, not this tree's: it counts claims for the whole case, while the sidebar footer counts the rows of this tree. The words differ as well as the denominators: the footer says "PASS local" for scoped rows, while the status-bar sample says "PASS" (the layout lane's label; whether the status bar should also say "PASS local" is a question for the status lane). The footer count filters the tree only and the two positions are not interchangeable; whether people confuse them is a study item.

The header reads UNKNOWN because of R4 (4.1), and the why-line under the binding names the chip that sets it. The numbers on the Reject row are MEASURED with `git grep` at `ddc43b9` (Appendix C): 5 files in `src` contain `Reject` as a word, 1 test file, 1 acceptance criterion (AC12), 0 wiki pages because no OKF bundle exists in the repo. The ripple strip shows the kernel's own closure for a changed `Reject` action: `model_impact` in `domain/impact.py` chains 8 nodes (rule, runtime, state-view, journey, obligation, receipt, review-packet, local-decision), and the three lines add up to those 8. Revision 2 also showed "test cells 25" in the strip; that number is not a kernel output (it is 5 actors by 5 states for action Reject, derived from the 125-cell matrix in `docs/verification/VERIFICATION.md`), so revision 3 removes it from the strip. The cell count belongs to the ripple lane's detail for the runtime node, labelled as derived from the matrix.

**Truncation at the shell width (DESIGN COUNT, estimate).** Row anatomy: 8 px padding, 16 px indent per level, a 24 px chevron slot, the kind letter with its gap (20 px), then the name, then a 4 px gap, the status glyph (16 px), the change mark (16 px plus 4 px gap), the homonym mark (20 px) and 8 px padding. That leaves a name width of 176, 160, 144 and 128 px at levels 1 to 4. At 7.4 px per character (average sans advance 0.529 em at 14 px, from the ADR-0060 measurement; a rough figure) 11 of the 43 names truncate when spaces are counted as characters: all 8 invariants, `Semantic Transaction`, `enable_recommendation` and `set_rejection_source`. Counting only non-space characters gives 9, all 8 invariants still among them. The estimate is therefore 9 to 11 at 296 px, 11 to 13 at a 272 px sidebar, none at 400 px, and 1 to 3 at 400 px with a 60 px status-word column (option G in the ADR). The full name is in the inspector title, the tooltip and the accessible name. The invariant labels are sentences, so the loss falls on the rows people scan for meaning. Two responses are recorded, neither tested: a naming lint that warns when a label exceeds the row budget (hypothesis H4: short label, full statement in the definition), and a request to the IA lane for a resizable sidebar (a drag splitter needs a non-drag alternative under WCAG 2.5.7, and a persisted width). At 1024 by 768 the layout lane's sidebar is a 40 px rail; this design then opens the tree as a 296 px drawer over the main region with the selection kept. That is an ASSUMPTION for the IA lane, and no budget is counted for 1024.

Two honest properties of this sample: every chip is "text match" because the repo has no binding data yet, and "Not analysed" is never drawn as zero impact.

### 4.3 Inspector (level 1) and source (level 2)

| Block | Content | Rule |
|---|---|---|
| Header (main region) | Name, kind, worst status word ("PASS local" where scoped), change verb | The word is visible here for every status; in the rail it is only a glyph (4.1a) |
| Why-line | The chip or check that sets the status, for example "Worst chip: requirements, AC12 PARTIAL (text match)" | Required whenever the header status is worse than the row's own claim (R4) |
| Definition | One sentence, editable inline if the operation is available | Empty definition is a gap, not a PASS |
| Binding | Model element id and how it was derived | "kernel-derived" or "declared" |
| Chips | code, requirements, tests, wiki | Each: count, worst check status, tier; a required link that is absent is drawn as a gap mark with the word "no test" |
| Chip list | Items of the selected chip, at most 5 rows before a scroll | Path and one status each; tier once in the list header |
| Ripple summary (shell inspector column) | Counts per model from the kernel closure plus "Not analysed" | Detail belongs to the ripple lane |
| Homonym pair | When the label exists in two contexts, both definitions side by side | See D10 |
| AI (shell inspector column) | "Ask AI to propose" marked "provider call" | Needs per-request consent (I8). While an edit is pending, the confirm sheet takes this place |
| Source | Raw JSON or catalogue text and the hash diff | Level 2, reached by "Source" |

### 4.4 Keyboard and ARIA

Container `role="tree"` with an accessible name; rows `role="treeitem"`; children in `role="group"`; `aria-expanded` on parents; `aria-selected` on the selected row; `aria-level`, `aria-setsize`, `aria-posinset` on every row (computed, not only when lazy). Roving tabindex, one tab stop. Selection follows focus and drives the inspector. Untrusted strings are set as text nodes and referenced with `aria-labelledby`, never through `setAttribute` (ADR-013). Results of kernel requests go to one polite live region.

| Key | Action | Source |
|---|---|---|
| Up, Down | Previous or next visible row | L1 |
| Right | Expand, or move to first child | L1 |
| Left | Collapse, or move to parent | L1 |
| Home, End | First or last visible row | L1 |
| Printable characters | Type-ahead to the next name that starts with them | L1 |
| `*` | Expand all siblings | L1 |
| Enter | Move focus to the inspector | L1 says Enter activates; the default action here is open the inspector |
| F2 | Rename in place if available; otherwise an anchored reason | By analogy with Rename Symbol in VS Code (L6); no APG standard |
| Delete | Opens the Retire sheet; never deletes at once | mine |
| Escape | Cancel edit, close sheet, clear filter, in that order | mine |
| Menu key or Shift+F10 | Context menu: Rename, Move to, Add term, Add alias, Retire, Ask AI | mine |
| Ctrl+K | Palette (owned by the palette aspect) | DEV§2.1 |
| Ctrl+Z | Undo the last candidate edit and state what it does not restore | P11 |

No single-letter shortcut exists because type-ahead uses them. A filter chord is deferred to the keyboard-map aspect; the filter field is a visible control and the first tab stop before the tree.

**What Ctrl+Z says it does not restore:** evidence receipts that the edit made inapplicable (retained, ADR-012), the decision that the edit cleared (retained in audit), code, tests, requirement text and wiki pages, and provider spend.

### 4.5 Operations: what executes today

Typed requests. "Today" means the frozen vocabulary of ADR-003 in v0.2 (`SemanticTransaction.kind` accepts only `enable_recommendation` and `set_rejection_source`).

| Gesture | Typed request | Today | Refusal shown |
|---|---|---|---|
| Choose the Reject prerequisite (two values) in the inspector of the invariant | `set_rejection_source` | executes | none |
| F2 on a term label | `rename_label` | refused | `NOT_IN_FROZEN_VOCABULARY` at gesture start |
| F2 on a state, action or role | `rename_label` | refused always | `KERNEL_BOUND`: the identifier is part of the semantic hash; offer Add alias |
| Edit definition | `set_definition` | refused | `NOT_IN_FROZEN_VOCABULARY` |
| Add term | `add_term` | refused | same |
| Drag, or Move to | `move_element` | refused | same |
| Change kind | `set_kind` | refused | same |
| Add alias | `add_alias` | refused | same |
| Retire | `retire_term` | refused | same |
| Clear a suspect link | `clear_suspect` | refused | `NO_SUSPECT_DATA`: no suspect state or decision record type exists |

That is 1 executable gesture of 10. `enable_recommendation` also executes but is triggered by selecting a meaning, not by a tree gesture; the tree shows the resulting ADDED rows.

Two refusal classes. Class A (operation unavailable) is shown when the gesture starts, so no effort is wasted. Class B (operation available, this instance illegal) is shown on the target with a code from this set: `ROLE_MISMATCH`, `DEPTH_BUDGET`, `CYCLE`, `DUPLICATE_NAME_IN_PARENT`, `KERNEL_BOUND`, `STALE_REVISION` (the base version moved). Codes are stable strings like the kernel's `DomainError` codes.

**Show or hide unavailable operations.** Options: (A) hide an operation until the kernel supports it, so the tree offers only what works today; (B) show it and answer with a coded reason (chosen). A removes dead ends and the repeated refusals that B causes (9 of 10 gestures in stage 1). B keeps the operation vocabulary discoverable, gives the palette and the context menu the same enabled or blocked-with-reason rule that the palette aspect assumes, and makes the stage-2 gap visible instead of implying a rename cannot exist. I found no source that compares the two for developer tools: UNVERIFIED, so this is hypothesis H3. The study counts attempts on refused operations, the time to the next successful action and SEQ after a refusal (section 8); if refusals are read as defects, switch to A for the operations that have no stage-2 date.

Every accepted request edits the candidate of a Change Case, never the baseline. Approve and apply stay on the decision surface. Language edits are assumed to change a new subject dimension (`language`) and therefore to clear an exact-presentation approval, as layout does under ADR-008; that needs the kernel ADR in 4.12.

### 4.6 Rename and its ripple

Identity, label and identifier are three different things.

| Layer | Example | Rename behaviour |
|---|---|---|
| Stable id | `term:semantic-transaction` | Never changes |
| Label and aliases | Semantic Transaction | Rename changes the label; the old label is kept as an alias unless the owner removes it |
| Kernel identifier | state `Recommended`, role `Registrar`, action `Reject` | Not renameable in v0.2; a label that differs from the identifier would make the language disagree with the code, so only aliases are allowed |

Ripple tiers shown in the confirm sheet, at most four chunks. Cowan reports about 3 to 5 chunks in young adults when rehearsal and chunking are blocked (L24); reading a sheet is not that task, so the cap of 4 is hypothesis H2, not derived from it. The study asks participants to state the tiers after reading the sheet (section 8):

| Tier | Meaning | Action |
|---|---|---|
| Regenerated | Views generated from the model (tree, inspector, palette, diagrams, journeys, rule table) | Automatic, listed by count only |
| Suspect | Id-bound links whose meaning-bearing fields changed | Owner clears each by a logged decision, or edits the linked item |
| Text match | Occurrences of the old label in files, found by search | Listed with file and count; never edited automatically. Files that must not be hand-edited are marked: retained (accepted ADRs, which docs/adr/README.md says are never rewritten) or generated (a generator header, for example the coverage.py report) |
| Not analysed | Sources the kernel has not indexed (no wiki bundle, other repositories) | Listed separately; never counted as zero |

Meaning-bearing fields (default, schema property per field, following DOORS Next's list in spirit, L10): label, definition, kind, parent context, bound model element. Not meaning-bearing: aliases, notes.

**Worked example (MEASURED).** Rename the term Semantic Transaction. `git grep -l -i -E 'semantic transaction|SemanticTransaction|semantic_transaction'` at `ddc43b9`, excluding `docs/hci` and `design`:

| Tier | Count |
|---|---|
| Regenerated | not counted here (no views consume the label yet) |
| Suspect | 0, because the repo has no id-bound links |
| Text match | 19 files, 34 lines (`src` 6, `tests` 2, `docs` 5, contracts, evidence and provenance 5, changelog 1) |
| of which do not hand-edit | 2: `docs/adr/0016-oss-first-adapters-not-engines.md` (accepted ADR, retained) and `evidence/coverage.json` (generated: its header names coverage.py 7.13.3) |
| of which unclassified | 17, including `CHANGELOG.md` and `contracts/*.json`; whether the contracts are generated is not declared anywhere |
| Not analysed | 1: no OKF wiki bundle configured |

Consequence for viscosity: the text tier is not smaller with the tree. Prose still needs up to 17 manual edits. What changes is that the owner sees all 19 files, 2 marked do-not-hand-edit and 1 unanalysed source before accepting, instead of learning about them later (Cognitive Dimensions: hidden dependencies). Rename of the kernel-bound role `Registrar` is a refusal; its text tier would be 22 files (MEASURED, regex `registrar`, case-insensitive).

The text tier is heuristic and over-approximates: the loose regex `receipt` for the term Evidence Receipt matches 40 files while the strict phrase forms match 3 (MEASURED). The confirm sheet therefore shows the pattern used and lets the owner narrow it.

### 4.7 Drag to re-parent, and Move to

Legal-parent matrix, precomputed on the client from the kernel's kind table, so hover feedback is local.

| Moving kind | Legal new parent |
|---|---|
| Context | root only (reordering is not offered) |
| Aggregate | Context |
| Entity | Aggregate |
| Value object | Aggregate or Entity |
| Invariant | Context, Aggregate or Entity |
| Term | Context, Aggregate, Entity or Value object |

Behaviour: pointer events, not HTML drag and drop. On pointer down on a row body (not the chevron) and movement past a small threshold (set by the prototype, not chosen here), a ghost row follows the pointer and illegal targets dim with their code on hover. A legal target shows a 2 px drop line (Atlassian, L15) and the words "Move here". Drop opens the confirm sheet if the ripple has a non-generated edge, otherwise applies to the candidate and offers Undo. Escape cancels. The ghost is positioned with `element.style.setProperty`; no inline style attribute (ADR-013). Whether that passes the CSP is a smoke-test item (SYNTHESIS C15).

Non-drag path: "Move to" from the context menu, the palette or the menu key opens a modal with a tree picker that lists only legal parents, type-ahead inside it, and the same confirm sheet. This satisfies WCAG 2.2 SC 2.5.7 (L4) and follows the Atlassian tree guidance (L15). Both paths emit `move_element`.

Moving an aggregate member across aggregates changes an invariant boundary. Fowler describes an aggregate as a consistency boundary with outside references going to its root (L21), so the confirm sheet for such a move states "invariant boundary changes" and lists the invariants of the old and new parent. This is a design rule I derived from the definition, not a documented product behaviour.

### 4.8 Search and filter

| Element | Behaviour |
|---|---|
| Filter field | Visible, first tab stop before the tree. Matches name, aliases, definition, id, code symbol. Client-side. |
| Modes | Highlight (whole tree, matches marked, ancestors carry a match badge; VS Code, L5). Path (matches and ancestors; default). Flat (matches only, with a breadcrumb). |
| Fuzzy | Toggle between exact and fuzzy, as VS Code (L5) |
| Facets | `status:unknown`, `kind:invariant`, `gap:test`, `changed:modified`, `source:ai` as tokens typed in the field |
| Sidebar footer | Counts of this tree's rows by evidence word ("PASS local" for scoped PASS); pressing a count applies its facet (Storybook shows totals in a testing widget and filters on press, L12; the footer position is mine). It counts rows, the shell status bar counts claims: same words, different denominators |
| Hidden counter | While a filter is active a line under the field reports hidden rows that are UNKNOWN, NOT_RUN, STALE, FAIL or CONFLICT. Example (DESIGN COUNT on the sample, rules R1 to R4): filter `reject` matches 4 rows, shows 11 with ancestors, hides 32; of the 17 UNKNOWN rows 13 are hidden and no other non-PASS status exists, so the line reads "Filter hides 13 UNKNOWN". |
| Empty result | Names what is missing and gives one verb: "No term matches. Filter hides 17 UNKNOWN. Clear filter." (Primer empty-state rule: purpose first, next step; dossier DEV§2.6) |
| Palette | Jump to a term with prefix `t`; palette selects the row and opens the inspector. Not a filter. |

The hidden counter exists because a filter is a silent way to lose UNKNOWN. It is the tree-level version of the hidden-null-edit counter in P4.

### 4.9 Trace chips

| Chip | Resolves to | Tier sources | Status of a link |
|---|---|---|---|
| code | Symbol path and file | kernel-derived when a recorded mapping exists (checked data); text match otherwise | Mapping check: symbol exists at the commit, name agrees with the term. No such check exists today: NOT_RUN |
| requirements | Acceptance criteria (`AC..`), later tracing items | Recorded id link, else text match | Criterion status from the matrix; PARTIAL split as in 4.1 |
| tests | Test ids | Recorded id link, else text match | Last run result bound to the commit |
| wiki | OKF pages | `resource` field naming the term id (needs agreement with the KB lane), else untyped markdown link (text match) | `status`, `stale_after` and `verified` fields of the page; past `stale_after` is STALE |

Precedents: Jama counts and gap mark (L9); OpenFastTrace revision ids and outdated detection (L11, licence GPL-3.0, so the tracing lane decides how it is used); Code Connect keeps the mapping as data but its page says nothing about keeping it current (L18); OKF v0.2 has typed `status` and `stale_after` but untyped links (L17). A chip with zero items and a required-link rule is a gap. A chip with zero items and no rule is plain.

### 4.10 AI at the tree

| Verb | Output | Grounding |
|---|---|---|
| Propose a definition | Inspector text with dashed outline and a text badge "AI-proposed" | Cites only existing ids; a new concept is labelled NEW |
| Find duplicate or homonym candidates | A list of rows | Existing ids only |
| Propose a name for an unnamed concept in a change | A provisional row in place | NEW label |
| Explain the difference between two homonyms | Inspector text | Existing ids only |

Rules: the prompt lane is marked "provider call" and needs the startup flag and per-request consent (I8). AI output never modifies the tree. The owner presses "Adopt as edit" and that is a typed request through the kernel like any other; AI has no accept control (P9, I4). An unresolved reference is rejected with a reason. Every AI string carries `data-eija-source`. A "Not useful" action is logged per source.

### 4.11 States

| State | Display |
|---|---|
| No catalogue declared (stage 1) | The tree shows only derived nodes (Workflow Definition with states, transitions, roles) under one row "Contexts not declared", status UNKNOWN. Not an empty pane. |
| Loading | Rows from the last payload stay; facets that need the kernel show RUNNING; never a spinner implying PASS |
| Kernel unreachable | Rows stay, marked STALE with the time of the last payload |
| Long job (text tier) | RUNNING, progress, cancel; previous ripple stays visible as STALE (P7) |
| Refusal | Class A or B as in 4.5, with a code and one sentence |
| Base version moved | `STALE_REVISION`: the sheet shows the difference and does not apply |

### 4.12 Delivery in two stages, and what needs a kernel ADR

Stage 1 is deliverable without kernel change: a read-only tree generated from the `Workflow` (states, transitions, roles, guards, effects), a catalogue file for what cannot be derived (contexts, classifications, definitions, aliases, bindings), and one editable gesture (`set_rejection_source`). "Derive what you can, declare only the rest, check the declared against the derived." The catalogue must not restate states, transitions or roles (AGENTS.md: no parallel sources).

Stage 2 needs a kernel ADR, in the lane rule form (executable semantics, missing-resolver rejection, projection rules, identity effects, a negative oracle, an evidence policy): a `language` subject dimension; the typed operations in 4.5; bindings with tiers; suspect computation; a drift check; PARTIAL handling (C2); and the per-cell applicability question below.

Proposed payload (interface, not an API design):

```
{"schema":"eija.language.v1","revision":4,
 "nodes":[{"id":"term:reject","kind":"T","label":"Reject","parent":"vo:transition",
   "definition":"...","definition_source":"owner|ai_proposed","meaning_hash":"...",
   "change":"MODIFIED","own_status":"PASS",
   "bindings":[{"kind":"model|code|requirement|test|wiki","target":"...",
                "tier":"kernel|text|unknown","check":{"status":"UNKNOWN","at":"ddc43b9","bound":"..."}}]}],
 "legal_parents":{"A":["C"]},"ops":{"rename_label":{"available":false,"reason":"NOT_IN_FROZEN_VOCABULARY"}}}
```

One kernel behaviour to note: a runtime receipt is inapplicable as a whole when the semantic hash changes (`assess_receipt` compares subject dimensions), so after any candidate edit every matrix-bound term is STALE, not only the changed one. The tree cannot be finer than the kernel; per-cell applicability would need a kernel change.

## 5. Quantitative model (PREDICTION unless marked)

Full arithmetic is in [HCI-ADR-0062](../../adr/0062-hci-language-ddd-tree.md). Flows are in [language-flows.json](../../../design/tasks/language-flows.json). Revision 2 charges a click as two B operators (press and release), which is how the KLM source defines B (L25, re-checked 2026-09-29: 0.1 s per press or release); a drag carries two B because it is a press and a release.

| Model | Inputs | Result |
|---|---|---|
| KLM, expert, error-free (Card, Moran and Newell 1980, L30) | K 0.20, P 1.10, H 0.40, M 1.35 s and the 21% RMS error from L30; B 0.10 per press or release from L25 (the 1980 paper charges a button press as one K, 0.20 s, the same as two B per click); band plus or minus 21% (an RMS error, not a confidence interval) | Table 5.1 |
| Fitts, Shannon form, ID = log2(D/W + 1) (L26) | Cockburn et al.: MT = 0.37 + 0.13 ID s, 8 participants, mouse, menu items 22 px high, calibration over items 1 to 16 of one menu, roughly 1 to 4 bits by my arithmetic (L26); higher IDs are extrapolations | Row height 24, 28, 32 px differs by 0.049 s at D = 280 px: inside the band, no decision |
| Hick-Hyman, expert, stable order (L26) | T = 0.24 + 0.08 log2(n), 2 to 12 items | n = 7 siblings: 0.46 s (0.4646 before rounding; 0.48 s if n + 1 is used); novice linear 0.86 s |
| Keystroke count for navigation, DESIGN COUNT under a stated policy | Sample tree, 43 nodes. Policy: start on the first row; walk down the ancestor chain of the target with Down or Up presses, pressing Right to expand a collapsed ancestor; no Left, Home, End or type-ahead | Arrow-only mean 7.3 keys (all collapsed; median 7, max 14); with contexts expanded mean 8.5 (median 9, max 14). Palette: 2 chord keys, the shortest unique label prefix (mean 4.7 characters, duplicates and prefixes of other labels counted at full length) and Enter: mean 7.7, max 14 |
| Layout budgets | Appendix B | 122 chrome words (shell 37), 60 content words, 182 total, 11 containers (12 with a rename in progress), 19 rows of 24 that fit, no target under 24 px, 9 to 11 of 43 names truncated at 296 px |

The keystroke policy is a choice. A shortest-path policy that may use Left, Home and End gives smaller values (an independent breadth-first check in the audit found about 7.7 for contexts expanded and 6.9 for all collapsed with Home and End), so neither route is shown to be faster, and no parity is claimed beyond this 43-node tree. The scripts are not in the repository (Appendix C), so these are labelled DESIGN COUNT and not MEASURED.

### 5.1 KLM by task (PREDICTION, seconds; band plus or minus 21%)

The "current" column is a workaround in an editor and shell because the baseline Studio has no language surface (grep of `index.html`, `app.js`, `app.css` for `role="tree"`, `treeitem`, `glossary`, `ubiquitous`, `draggable`, `aria-expanded`: 0 matches each, MEASURED). Reading time of long output is not modelled, which favours the workaround. The outputs are not equivalent: the workaround yields no kernel ripple, status or UNKNOWN.

| Task | Current | Proposed | Ratio | Bands overlap | Reading |
|---|---|---|---|---|---|
| T05 rename | 14.20 | 8.20 | 0.58 | no | Proposed adds one kernel dry run of 1 s (design budget) |
| T05 move by drag | 6.05 | 5.40 | 0.89 | yes | Parity; no time claim |
| T05 move without drag | 6.05 | 9.15 | 1.51 | yes | Slower by design: the WCAG 2.5.7 path; ratio 1.51 sits at the edge of the flip band (upper limit 1.53). With a dedicated 2-key chord it would be 8.15 (ratio 1.35) |
| T05 add term | 19.85 | 22.80 | 1.15 | yes | Typing dominates; the proposal adds checks |
| T09 find term | 8.70 | 4.90 | 0.56 | no | Palette against opening a file and searching |
| T11 clear 3 suspect links | 27.30 | 17.10 | 0.63 | no | Workaround leaves no record |
| T12 code drift | 11.85 | 4.90 | not comparable | n/a | The drift check does not exist in the kernel; the workaround is a grep and a judgement. No ratio is claimed |
| T13 AI definition | 19.80 | 9.70 | 0.49 | no | Consent and adopt are kept; provider latency not modelled |
| T14 gaps, 8 invariants | 71.20 | 4.00 | not comparable | n/a | Eight manual greps against one click on a facet whose required-link rule data must first be authored (setup not modelled). No ratio is claimed |

Sensitivity over K in {0.12, 0.20, 0.28}, P in {0.83, 1.10}, M in {0.6, 1.35} (12 cells). The flip band [0.653, 1.532] is the range in which two plus or minus 21% bands overlap; it is a heuristic, not a statistical test. T09 and T13 stay outside it in all 12 cells; T05 rename is inside it in 2 of 12, T11 in 5 of 12, T05 move without drag in 7 of 12; T05 move by drag and T05 add are inside in 12 of 12. Nothing here is a benefit claim.

Hand switching. The flows omit H, and the omission is asymmetric: the current move and T13 workarounds switch between mouse and keyboard several times, the proposed rename switches once. With H 0.40 s at every switch (strict; a two-handed user needs none, so the truth lies between) the totals are rename 14.20 against 8.60 (0.61), move by drag 7.25 against 5.80 (0.80), move without drag 7.25 against 9.55 (1.32), add 20.25 against 23.20 (1.15), T13 21.40 against 10.50 (0.49); T09 and T11 have no switch. On a 24-cell grid (the 12 cells above, with H 0 and with strict H) T09 and T13 never enter the flip band; rename enters it in 6, T11 in 10, move without drag in 18, move by drag in 22, add in 24. No decision changes.

Response overlap. The 1980 paper (L30) does not count a system response that an M follows unless it exceeds 1.35 s. The proposed rename, move and add flows count R before an M, which favours the current flows; without it the totals are rename 7.20, move by drag 5.30, move without drag 8.15 and add 21.80. The tables keep R counted.

Fitts variant. Where a P operator has a layout stem (design/layouts/proposed-language.json rows as stand-ins, or the inline states in Appendix B), its time can be taken from geometry, 0.37 + 0.13 ID, instead of 1.10. The proposed totals then become T05 rename 8.05, move by drag 4.97, move without drag 9.00, add 22.67, T11 14.27, T13 8.57, T14 3.90; T09 and T12 have no P operator. The stand-in rows differ from this aspect's own tree, so these are approximate PREDICTIONS and no decision changes.

Two predictions cut against the design: T05 add term and T05 move without drag are not faster (both inside the band). They are kept because checked structure and the non-drag path are requirements, not speed features.

## 6. Anti-slop budget for the primary viewport

DESIGN COUNT from Appendix B at 1440 by 900, at the shell's geometry. A built page must be re-counted with the slop-budget script at 1440 by 900 and 1280 by 720. Counting rules: a word is a whitespace-separated token of a visible label; glyph-only elements count 0 words (their words are in the accessible name); "content" words are row names, the term title, the kind line, the definition and the chip-list items; every other visible word is chrome, including the shell's (37 words: top bar and status bar, counted from the layout lane's labels).

| Item | Target | Design value |
|---|---|---|
| Chrome words | at most about 120 | 122 (shell 37, this design 85): at the limit |
| All visible words | HCI-ADR-0063 uses at most 180 | 182 (content 60): 2 over. Recorded deviation: 60 words are the tree's row names and the term's definition, the material the screen exists to show; this design's own chrome is 85 words (revision 3 dropped the derived "test cells 25" from the ripple strip). Revision 1 reported 88 chrome words on a 400 px rail that the shell does not provide; the count is not comparable |
| Containers (bordered or filled, plus the selected-row fill) | at most about 12 | 11: sidebar surface, filter field, palette trigger, provider chip, scope button, 4 trace chips, AI button, selected row. This assumes 13 text buttons without border or fill (Move, Rename, Add term, Source, the four mode links, the five footer counts) and an unfilled shell stage chip `st-stage`; each drawn bordered or filled adds one, and a filled `st-stage` alone gives 12, and 13 in the confirm state, over the target. Pending rename (Appendix B, state `language-tree-confirm`): the AI button gives way to the confirm sheet, whose only bordered control is Confirm, and the rename field is added: 12 (DESIGN COUNT; the sheet's tiers are hairline-separated rows, Cancel is a text button) |
| Nesting depth | at most 3 | 2 in the primary state; 3 with the rename field (sidebar, selected row, field) |
| Distinct font sizes | at most 6 | 3 by the ADR-0060 roles (12 caption and code-small, 14 ui and code, 16 prose); sizes owned by the type aspect |
| Elevations | at most 2 | 1 (sidebar surface step); no shadows |
| Prose blocks of 8 or more words | about 30 words in total | 12 (definition); the ripple lines are label-number pairs |
| Interactive targets under 24 by 24 px | 0 | 0 (rows 28 px, chevrons 24 px, chips 28 px, counts 24 px) |
| Eyebrows | at most 1 | 0 |
| Alternative: per-row trace counts (option E) | | 198 chrome words (122 + 4 counts on each of 19 rows): fails |
| Alternative: a 60 px status word column in the rail (revision 1) | | Adds 1 word per non-PASS row (13 in this viewport) and cuts the name width to 116 to 68 px |

Rows visible: 19 of 24 that fit at 28 px (696 px between the filter block and the footer); 24 px rows fit 29, 32 px rows fit 21. The sample tree fully expanded is 43 rows, so it scrolls; with contexts expanded one level it is 15 rows.

## 7. Risks and counter-evidence

| Risk | Evidence | Mitigation |
|---|---|---|
| Users may prefer searching, browsing or tracing in different mixes; some find traceability of little use | Borg, Alegroth and Runeson 2017 (L27) | Tree, filter, palette and chips all exist; study measures which route is used |
| Visual re-parenting does not scale | Structurizr vendor argument (L16) | Confirm sheet, legal-parent matrix, Move to |
| Only 1 of 10 gestures executes today | ADR-003; 4.5 | Stage 1 is read-only plus one edit; refusals are explicit and early |
| The tree is a wall of UNKNOWN if bindings are never recorded | Sample: 17 of 23 own statuses are UNKNOWN under rules R1 to R4 (4.1) | This is the honest state; the sidebar footer and the gap facet make it actionable; the study checks it does not cause alarm fatigue (UNVERIFIED as a risk) |
| Reasonless or bulk clearing erodes trust | Jama page names no audit or reason (L9b) | Closed reason list of 3, one record per link; scoped clear only within one cause, not offered in v1 |
| Letters as kind glyphs may not be recognised | No evidence found | Recognition test in the study |
| Text-match tier over-approximates | MEASURED: 40 files loose against 3 strict. It also lowers row status (R4): 8 of the 10 state and action rows read UNKNOWN because AC12 and AC15 name them | Pattern shown and editable; the why-line names the chip; recorded id links replace text match. Whether text match should lower status at all is open (section 9) |
| Names truncate at the shell width | 9 to 11 of 43 at 296 px, all 8 invariants (4.2); DESIGN COUNT with an estimated character width | Full name in inspector, tooltip and accessible name; naming lint (H4); resizable sidebar request to the IA lane (option G1 in the ADR: 0 truncated at 400 px) |
| Six glyphs alone must carry the status in the rail | No colour-vision simulation; no recognition test | Words in header, footer and accessible name; study measure (section 8) |
| Two UNKNOWN counts (shell status bar, sidebar footer) | Different denominators | Footer filters the tree only; study checks confusion |

## 8. Study tasks for this aspect

Protocol, measures and stop criteria are in the ADR. Seeded items on the excursion workflow: (S1) a linked criterion that became suspect after a definition change; (S2) the homonym Approve; (S3) the PARTIAL criterion AC12 that must read UNKNOWN, not PASS; (S4) an illegal drop (an invariant under a term); (S5) a rename whose text tier includes an accepted ADR; (S6) a PASS_LOCAL invariant (AC07, AC09, AC10 or AC16) that must be read as "PASS local", scoped, and not as unqualified proof, and the Reject term that reads UNKNOWN although its own matrix claim is PASS local. Additional measures for revision 2: shape-only recognition of the six status glyphs in the rail against the same rows with words; scoped-PASS misread as unscoped PASS (target zero); ability to state all confirm-sheet tiers after reading it (H2); attempts on refused operations and SEQ after a refusal (H3); name-truncation effect on finding an invariant (H4).

## 9. Gaps, UNVERIFIED items, open questions

- UNVERIFIED: Archi tree behaviour (L22); screen-reader behaviour of `tree` against `treegrid` (no test data); Figma layers and Ilograph (dossier only); whether `contracts/*.json` are generated.
- Not measured: any human behaviour; any latency; any built page. The reference PC keeps `D:` on an HDD (AGENTS.md), which matters for kernel dry runs.
- Open: which word is ubiquitous, "bounded area" (repo) or "context" (DDD literature)? The tree shows "Context" with "bounded area" as an alias; the owner should decide.
- Open: display severity order between UNKNOWN and NOT_RUN (status aspect).
- Open: OpenFastTrace is GPL-3.0; how the tracing lane uses it is not decided here.
- Open: per-cell receipt applicability in the kernel (4.12).
- Open: whether editing the language should clear an exact-presentation approval (assumed yes, by analogy with layout under ADR-008).
- Layout files: this aspect wrote none under `design/layouts/`. Appendix B holds the primary state and three inspector states (`language-tree-suspect`, `language-tree-ai`, `language-tree-confirm`); the integrator should extract them into `design/layouts/`. Task-flow `P` operators use the layout lane's `proposed-language` stem where an equivalent element exists (row ids there are stand-ins, because its sample tree differs), the inline states otherwise, and none for steps outside the Studio.
- Open for the IA lane: sidebar width (a resizable tree sidebar, 272 versus 296 px) and how the tree opens at 1024 by 768, where the layout lane draws a 40 px rail.
- Open for the status lane: whether the rail may show a glyph without a word (4.1a); how to render a scoped PASS.
- Open: should a text-match link lower a row's status (R4)? It errs safe but adds noise until id links exist.
- Not verified by me: the Explorer's rename key in VS Code (L5 says files and folders can be renamed but names no key).
- UNVERIFIED and not used in any decision: Tuch et al. 2012 on visual complexity and prototypicality (publisher pages returned 403).
- Layout stems `language-tree-suspect` and `language-tree-ai` used by 12 P operators in T11 and T13 exist only as inline blocks in Appendix B, so a `klm_time` or `fitts_mt` run on those flows fails until the integrator extracts them into `design/layouts/` and re-checks that every `from` and `to` id resolves.

## 10. Changes in revisions 2 and 3

| Audit finding | Verified | What changed |
|---|---|---|
| PASS rendered where the repository says PASS_LOCAL; the 10 state and action rows and the Reject header unexplained; counts rounded up | Yes: `PASS_LOCAL` was absent from both documents; AC07, AC09, AC10, AC16 are PASS_LOCAL; AC12 is PARTIAL | Mapping table and rules R1 to R4 (4.1); the source of the state and action PASS named (`assess_receipt` on `runtime_matrix`); Reject now reads UNKNOWN with a why-line; counts recomputed (6 PASS local, 17 UNKNOWN, 0 NOT_RUN, 1 gap); filter and empty-state examples recomputed; seed S6 added |
| Rail 400 px and top bar 48 px contradict the shell (296 px sidebar, 40 px top bar) | Yes: `design/layouts/proposed-language.json` and HCI-ADR-0057 | Appendix B re-laid at shell geometry; words, containers and truncation recounted; the status word column dropped from the rail as a recorded deviation (4.1a); 1024 case and sidebar width stated as open items for the IA lane |
| KLM click counted as one B | Yes: the source defines B as press or release; re-fetched 2026-09-29 | Every click is two B; flows and tables regenerated (T05 rename 8.20, move without drag 9.15, add 22.80, T11 17.10, T13 9.70, T14 4.00; current flows also change) |
| Hick-Hyman for 7 items quoted as 0.47 s | Yes: 0.4646 | 0.46 s, with the n + 1 variant 0.48 s |
| Navigation key counts not reproducible; "parity" | Partly: the figures reproduce under the stated policy (walk the ancestor chain, no Left, Home, End); a shortest-path policy gives lower values | Policy documented, relabelled DESIGN COUNT, 8.5 kept with its policy, parity claim dropped |
| Two citation misattributions; Notion understated | Yes: VS Code page names no F2 (it does say files can be renamed; wording corrected in revision 3); OpenFastTrace README has no id format (found in the spec design document); Notion "sub-items only" is a Flat-like precedent | Rows re-pointed (L5, L6, L11, L11b, L13) |
| 88 words called a pass against a 120 target while 149 words were visible; 12 containers unbacked | Yes | Total and chrome both reported (123 chrome, 183 total), the deviation recorded; the confirm state has its own layout (12 containers) |
| Task-flow file: 10 P operators without from and to, no layout stem | Yes | All P operators carry from and to; stems added where geometry exists; documented reasons elsewhere |
| T12 and T14 ratios not comparable; 21% is an RMS error | Yes | Ratios dropped for both; the overlap test is labelled a heuristic |
| No option for hiding unavailable operations; cap of 4 tiers not evidence | Yes | Option added with hypothesis H3; the cap of 4 is hypothesis H2 |

Revision 3, after the audit of revision 2 (each finding re-checked by me before changing anything):

| Audit finding | Verified | What changed |
|---|---|---|
| The designer's reported decision summary carried revision-1 numbers | Yes: the summary is not in these files; the files hold revision 2 | Files are canonical; the summary returned with this revision is regenerated from them |
| Ripple strip "8 modelled" while its lines add up to 32; the 25 test cells are not a kernel output | Yes: `model_impact` chains 8 nodes; 25 is derived from the matrix | Strip reads "Ripple 8 nodes"; "test cells 25" removed and assigned to the ripple lane's detail; words 183 to 182, chrome 123 to 122 |
| Truncation said "spaces excluded" but counted spaces | Yes: 11 with spaces, 9 without | Stated as a range 9 to 11 (272 px: 11 to 13) |
| Footer and status bar said to use "the same words" | Yes: "PASS local" against "PASS" | Text corrected; container count states which buttons are assumed borderless, and the effect of `st-stage` |
| H omitted asymmetrically | Yes: 3 H in the current move flows, 1 in proposed rename | H variant and a 24-cell grid added; no decision changes |
| Load-bearing claims without an opened URL | Yes | Card, Moran and Newell 1980 opened (L30): K, P, H, M and 21% confirmed; B stays tertiary and equals one 1980 K per click. Fitts range of 2 to 8 bits withdrawn; the calibration range (about 1 to 4 bits) stated. Nielsen and Landauer replaced by L31. Tuch 2012 marked UNVERIFIED |
| Decision said C is the only option keeping containment; D and E keep it too | Yes | Wording changed; D called complementary; E rejected on the word budget only |
| No option for a wider tree | Yes | Option G (resizable sidebar or tree in the main region) added to the ADR with truncation counts |
| VS Code page "does not mention rename" | Yes: it says files and folders can be renamed | "names no rename key" |
| Productboard said to limit depth "for the same reason" | Yes | Reworded (4.1) |
| Storybook widget "at the bottom of the sidebar" | Not confirmed by me either | Position removed from the claim |
| Cognitive Dimensions tutorial unreachable for the auditor | No: I re-fetched the PDF on 2026-09-29 and found the knock-on viscosity definition in the text | Kept |
| Response overlap (not raised by the audit) | Found while reading L30 | Reported as a variant; tables unchanged (conservative) |

Hypotheses introduced or relabelled in revision 2: H2 (four ripple tiers are readable), H3 (show unavailable operations with a reason), H4 (a naming lint helps truncated labels). None is supported by evidence yet.

## Appendix A. Pages opened by me on 2026-09-29

| Id | URL | Used for |
|---|---|---|
| L1 | https://www.w3.org/WAI/ARIA/apg/patterns/treeview/ | Tree keys and ARIA |
| L2 | https://www.w3.org/WAI/ARIA/apg/patterns/treegrid/ | Treegrid focus rule |
| L3 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | 24 by 24 CSS px and exceptions |
| L4 | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | SC 2.5.7 |
| L5 | https://code.visualstudio.com/docs/getstarted/userinterface | Explorer: drag to move, rename files and folders (no key named), filter modes, badge, fuzzy toggle (re-read 2026-09-29) |
| L6 | https://code.visualstudio.com/docs/editing/refactoring | Rename and Refactor Preview |
| L7 | https://www.jetbrains.com/help/idea/rename-refactorings.html | Rename, preview, text occurrences |
| L8 | https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/ | `needsConfirmation` |
| L9 | https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/trace-view.html | Trace View |
| L9b | https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/relationships/clear-suspect-links.html | Clearing suspect links |
| L10 | https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors-next/7.1.0?topic=projects-link-validity | Link validity attributes and icon |
| L11 | https://github.com/itsallcode/openfasttrace | Licence GPL-3.0 (README) |
| L11b | https://github.com/itsallcode/openfasttrace/blob/main/doc/spec/design.md (read raw) | Item id format, needs and covers lists, Outdated and Predated link status |
| L12 | https://storybook.js.org/docs/writing-tests/integrations/vitest-addon | Status in tree, count as filter |
| L13 | https://www.notion.com/help/tasks-and-dependencies | Sub-item filter scopes (parents only, parents and sub-items, sub-items only) |
| L14 | https://support.productboard.com/hc/en-us/articles/360058212253-Build-your-product-hierarchy | Hierarchy, depth advice, drag |
| L15 | https://atlassian.design/components/pragmatic-drag-and-drop/design-guidelines | Move menu for trees, drop line |
| L16 | https://docs.structurizr.com/as-code | Vendor argument on UI re-parenting |
| L17 | https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md | OKF v0.2 fields and links |
| L18 | https://developers.figma.com/docs/code-connect/ | Mapping as data, no maintenance statement |
| L19 | https://martinfowler.com/bliki/UbiquitousLanguage.html | Ubiquitous language |
| L20 | https://www.nngroup.com/articles/progressive-disclosure/ | Two disclosure levels (2006, rule of thumb) |
| L21 | https://martinfowler.com/bliki/BoundedContext.html and https://martinfowler.com/bliki/DDD_Aggregate.html | Bounded context; aggregate root |
| L22 | https://github.com/archimatetool/archi | Archi README (no tree description) |
| L23 | Green and Blackwell 1998, Cognitive Dimensions of Information Artefacts: a tutorial (PDF at https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf; re-fetched 2026-09-29 and read by text extraction) | Repetition and knock-on viscosity |
| L24 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2864034/ | Cowan 2010: 3 to 5 chunks |
| L25 | https://en.wikipedia.org/wiki/Keystroke-level_model | KLM operator values, B as press or release (a click is two B), and 21% RMS error (tertiary; Card, Moran and Newell 1980 not opened by me; re-read 2026-09-29) |
| L26 | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf | Cockburn, Gutwin and Greenberg, A Predictive Model of Menu Performance: Fitts and Hick-Hyman constants and limits (text extracted with pdftotext) |
| L27 | https://arxiv.org/abs/1703.01897 | Borg, Alegroth and Runeson 2017 |
| L30 | http://iihm.imag.fr/blanch/ens/2010-2011/M1/EIHM/cours/1980-Card-KLM.pdf (Card, Moran and Newell 1980, CACM 23(7); DOI https://dl.acm.org/doi/10.1145/358886.358895) | KLM operators, button press as K, 21% RMS error, response-overlap rule (scan read by text extraction) |
| L31 | https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/ | About 5 users for qualitative tests, about 20 for quantitative (Nielsen 2000) |
| L28 | https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1, 1, 10 s |
| L29 | Repo at `ddc43b9`: `README.md`, `AGENTS.md`, `docs/architecture/ARCHITECTURE.md`, `docs/adr/0000-poc-decision-log.md`, `docs/verification/ACCEPTANCE_MATRIX.csv`, `src/eija_studio/domain/{models,policy,impact,evidence}.py`, `src/eija_studio/application/compiler.py`, `src/eija_studio/interfaces/http.py`, web assets | Domain names, kernel behaviour, CSP |

The APG treegrid and tree pages were read through WebFetch, which returns a model-written summary, so key names and property names are paraphrase-checked, not character-checked.

## Appendix B. Layouts (schema `eija.layout.v1`, proposed, 1440 by 900)

Revision 2 draws the tree at the shell's geometry (design/layouts/proposed-language.json: sidebar 296 px, main region 296 to 1048 px, inspector 1048 to 1440 px). Shell elements (top bar, status bar) use the layout lane's labels and positions and are counted as shell chrome. Counting rules: `words` is the number of whitespace-separated tokens in `label`, 0 for glyph-only elements and the virtual pointer. Ids starting with `row.`, `insp.title`, `insp.kind`, `insp.definition` and `item.` count as content words. Containers (bordered or filled): `frame.sidebar`, `input.*`, `palette-trigger`, `provider`, `scope`, `chip.code`, `chip.req`, `chip.test`, `chip.wiki`, `btn.ai`, plus the selected-row fill. `importance` is my judgement. Text buttons without border or fill, not counted as containers: `term-move`, `term-rename`, `term-add`, `insp.source`, `link.mode.*`, `status.*`; the shell's `st-*` elements, including the `st-stage` chip, are assumed unfilled (the layout lane owns their styling). The primary state has 108 elements, 182 words and 11 containers (DESIGN COUNT). The three further states are the inspector-column states that the task flows use; the integrator should extract the four blocks into `design/layouts/`.

State `language-tree` (Reject selected):

```
{"schema":"eija.layout.v1","ui":"proposed","screen":"language-tree","viewport":{"w":1440,"h":900},"elements":[
 {"id":"brand","role":"text","x":16,"y":8,"w":88,"h":24,"label":"EIJA Studio","importance":0.3,"words":2},
 {"id":"scope","role":"button","x":112,"y":4,"w":296,"h":32,"label":"Let teachers sign off excursions. rev 3","importance":0.4,"words":7},
 {"id":"tab-changes","role":"tab","x":424,"y":0,"w":88,"h":40,"label":"Changes","importance":0.5,"words":1},
 {"id":"tab-model","role":"tab","x":512,"y":0,"w":72,"h":40,"label":"Model","importance":0.6,"words":1},
 {"id":"tab-evidence","role":"tab","x":584,"y":0,"w":96,"h":40,"label":"Evidence","importance":0.5,"words":1},
 {"id":"palette-trigger","role":"button","x":976,"y":4,"w":320,"h":32,"label":"Search or run Ctrl K","importance":0.6,"words":5},
 {"id":"provider","role":"chip","x":1304,"y":6,"w":120,"h":28,"label":"offline local","importance":0.2,"words":2},
 {"id":"frame.sidebar","role":"panel","x":0,"y":40,"w":296,"h":832,"label":"","importance":0.0,"words":0},
 {"id":"input.filter","role":"input","x":12,"y":48,"w":272,"h":32,"label":"Filter","importance":0.6,"words":1},
 {"id":"link.mode.highlight","role":"button","x":12,"y":84,"w":64,"h":24,"label":"Highlight","importance":0.3,"words":1},
 {"id":"link.mode.path","role":"button","x":80,"y":84,"w":40,"h":24,"label":"Path","importance":0.3,"words":1},
 {"id":"link.mode.flat","role":"button","x":124,"y":84,"w":36,"h":24,"label":"Flat","importance":0.3,"words":1},
 {"id":"link.mode.fuzzy","role":"button","x":228,"y":84,"w":56,"h":24,"label":"Fuzzy","importance":0.3,"words":1},
 {"id":"row.authoring","role":"tree-item","x":0,"y":116,"w":296,"h":28,"label":"Authoring","importance":0.5,"words":1},
 {"id":"chevron.authoring","role":"button","x":8,"y":118,"w":24,"h":24,"label":"expand","importance":0.2,"words":0},
 {"id":"rowstatus.authoring","role":"text","x":232,"y":122,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.execution","role":"tree-item","x":0,"y":144,"w":296,"h":28,"label":"Execution","importance":0.5,"words":1},
 {"id":"chevron.execution","role":"button","x":8,"y":146,"w":24,"h":24,"label":"collapse","importance":0.2,"words":0},
 {"id":"row.preview-instance","role":"tree-item","x":0,"y":172,"w":296,"h":28,"label":"Preview Instance","importance":0.5,"words":2},
 {"id":"chevron.preview-instance","role":"button","x":24,"y":174,"w":24,"h":24,"label":"expand","importance":0.2,"words":0},
 {"id":"rowstatus.preview-instance","role":"text","x":232,"y":178,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.workflow-definition","role":"tree-item","x":0,"y":200,"w":296,"h":28,"label":"Workflow Definition","importance":0.5,"words":2},
 {"id":"chevron.workflow-definition","role":"button","x":24,"y":202,"w":24,"h":24,"label":"collapse","importance":0.2,"words":0},
 {"id":"rowstatus.workflow-definition","role":"text","x":232,"y":206,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.role","role":"tree-item","x":0,"y":228,"w":296,"h":28,"label":"Role","importance":0.5,"words":1},
 {"id":"chevron.role","role":"button","x":40,"y":230,"w":24,"h":24,"label":"expand","importance":0.2,"words":0},
 {"id":"row.state","role":"tree-item","x":0,"y":256,"w":296,"h":28,"label":"State","importance":0.5,"words":1},
 {"id":"chevron.state","role":"button","x":40,"y":258,"w":24,"h":24,"label":"expand","importance":0.2,"words":0},
 {"id":"rowstatus.state","role":"text","x":232,"y":262,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.transition","role":"tree-item","x":0,"y":284,"w":296,"h":28,"label":"Transition","importance":0.5,"words":1},
 {"id":"chevron.transition","role":"button","x":40,"y":286,"w":24,"h":24,"label":"collapse","importance":0.2,"words":0},
 {"id":"row.submit","role":"tree-item","x":0,"y":312,"w":296,"h":28,"label":"Submit","importance":0.5,"words":1},
 {"id":"rowstatus.submit","role":"text","x":232,"y":318,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.recommend","role":"tree-item","x":0,"y":340,"w":296,"h":28,"label":"Recommend","importance":0.5,"words":1},
 {"id":"rowstatus.recommend","role":"text","x":232,"y":346,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"rowmark.recommend","role":"text","x":252,"y":344,"w":16,"h":20,"label":"A","importance":0.6,"words":1},
 {"id":"row.approve","role":"tree-item","x":0,"y":368,"w":296,"h":28,"label":"Approve","importance":0.5,"words":1},
 {"id":"rowstatus.approve","role":"text","x":232,"y":374,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"rowmark.approve","role":"text","x":252,"y":372,"w":16,"h":20,"label":"M","importance":0.6,"words":1},
 {"id":"rowmark.approve.homonym","role":"text","x":268,"y":372,"w":20,"h":20,"label":"x2","importance":0.5,"words":1},
 {"id":"row.reject","role":"tree-item","x":0,"y":396,"w":296,"h":28,"label":"Reject","importance":0.9,"words":1},
 {"id":"rowstatus.reject","role":"text","x":232,"y":402,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"rowmark.reject","role":"text","x":252,"y":400,"w":16,"h":20,"label":"M","importance":0.6,"words":1},
 {"id":"row.revise","role":"tree-item","x":0,"y":424,"w":296,"h":28,"label":"Revise","importance":0.5,"words":1},
 {"id":"rowstatus.revise","role":"text","x":232,"y":430,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.inv-teacher","role":"tree-item","x":0,"y":452,"w":296,"h":28,"label":"No teacher final approval","importance":0.5,"words":4},
 {"id":"rowstatus.inv-teacher","role":"text","x":232,"y":458,"w":16,"h":16,"label":"status glyph PASS local","importance":0.7,"words":0},
 {"id":"row.inv-labels","role":"tree-item","x":0,"y":480,"w":296,"h":28,"label":"Recommend is not approval","importance":0.5,"words":4},
 {"id":"rowstatus.inv-labels","role":"text","x":232,"y":486,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.inv-recommend","role":"tree-item","x":0,"y":508,"w":296,"h":28,"label":"Recommend needs assignment","importance":0.5,"words":3},
 {"id":"rowstatus.inv-recommend","role":"text","x":232,"y":514,"w":16,"h":16,"label":"status glyph PASS local","importance":0.7,"words":0},
 {"id":"row.inv-reject-start","role":"tree-item","x":0,"y":536,"w":296,"h":28,"label":"Reject prerequisite state","importance":0.5,"words":3},
 {"id":"rowstatus.inv-reject-start","role":"text","x":232,"y":542,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"rowmark.inv-reject-start","role":"text","x":252,"y":540,"w":16,"h":20,"label":"M","importance":0.6,"words":1},
 {"id":"row.assurance","role":"tree-item","x":0,"y":564,"w":296,"h":28,"label":"Assurance","importance":0.5,"words":1},
 {"id":"chevron.assurance","role":"button","x":8,"y":566,"w":24,"h":24,"label":"expand","importance":0.2,"words":0},
 {"id":"rowstatus.assurance","role":"text","x":232,"y":570,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.governance","role":"tree-item","x":0,"y":592,"w":296,"h":28,"label":"Governance","importance":0.5,"words":1},
 {"id":"chevron.governance","role":"button","x":8,"y":594,"w":24,"h":24,"label":"expand","importance":0.2,"words":0},
 {"id":"rowstatus.governance","role":"text","x":232,"y":598,"w":16,"h":16,"label":"status glyph UNKNOWN","importance":0.7,"words":0},
 {"id":"row.provider-integration","role":"tree-item","x":0,"y":620,"w":296,"h":28,"label":"Provider integration","importance":0.5,"words":2},
 {"id":"chevron.provider-integration","role":"button","x":8,"y":622,"w":24,"h":24,"label":"expand","importance":0.2,"words":0},
 {"id":"status.pass","role":"button","x":12,"y":816,"w":96,"h":24,"label":"6 PASS local","importance":0.7,"words":3},
 {"id":"status.unknown","role":"button","x":112,"y":816,"w":100,"h":24,"label":"17 UNKNOWN","importance":0.7,"words":2},
 {"id":"status.notrun","role":"button","x":12,"y":844,"w":84,"h":24,"label":"0 NOT_RUN","importance":0.7,"words":2},
 {"id":"status.fail","role":"button","x":100,"y":844,"w":56,"h":24,"label":"0 FAIL","importance":0.7,"words":2},
 {"id":"status.gap-test","role":"button","x":160,"y":844,"w":96,"h":24,"label":"1 gap: test","importance":0.7,"words":3},
 {"id":"lens-language","role":"tab","x":312,"y":44,"w":80,"h":32,"label":"Language","importance":0.4,"words":1},
 {"id":"lens-states","role":"tab","x":396,"y":44,"w":64,"h":32,"label":"States","importance":0.4,"words":1},
 {"id":"lens-journeys","role":"tab","x":464,"y":44,"w":80,"h":32,"label":"Journeys","importance":0.4,"words":1},
 {"id":"lens-requirements","role":"tab","x":548,"y":44,"w":112,"h":32,"label":"Requirements","importance":0.4,"words":1},
 {"id":"lens-tests","role":"tab","x":664,"y":44,"w":64,"h":32,"label":"Tests","importance":0.4,"words":1},
 {"id":"lens-personas","role":"tab","x":732,"y":44,"w":80,"h":32,"label":"Personas","importance":0.4,"words":1},
 {"id":"insp.title","role":"text","x":312,"y":88,"w":160,"h":24,"label":"Reject","importance":1.0,"words":1},
 {"id":"insp.status","role":"text","x":480,"y":88,"w":200,"h":24,"label":"UNKNOWN MODIFIED","importance":0.8,"words":2},
 {"id":"term-move","role":"button","x":776,"y":86,"w":72,"h":28,"label":"Move","importance":0.3,"words":1},
 {"id":"term-rename","role":"button","x":856,"y":86,"w":80,"h":28,"label":"Rename","importance":0.3,"words":1},
 {"id":"term-add","role":"button","x":944,"y":86,"w":88,"h":28,"label":"Add term","importance":0.3,"words":2},
 {"id":"insp.kind","role":"text","x":312,"y":116,"w":480,"h":20,"label":"Term in Workflow Definition, Transition","importance":0.4,"words":5},
 {"id":"insp.definition","role":"text","x":312,"y":144,"w":720,"h":48,"label":"The Registrar rejects an excursion from Recommended. Before this case: from Submitted.","importance":0.8,"words":12},
 {"id":"insp.binding","role":"text","x":312,"y":200,"w":640,"h":24,"label":"Model element TR-REJECT, kernel-derived","importance":0.5,"words":4},
 {"id":"insp.source","role":"button","x":976,"y":200,"w":56,"h":24,"label":"Source","importance":0.2,"words":1},
 {"id":"insp.why","role":"text","x":312,"y":232,"w":720,"h":24,"label":"Worst chip: requirements, AC12 PARTIAL (text match)","importance":0.7,"words":7},
 {"id":"chip.code","role":"chip","x":312,"y":264,"w":96,"h":28,"label":"code 5","importance":0.6,"words":2},
 {"id":"chip.req","role":"chip","x":416,"y":264,"w":152,"h":28,"label":"requirements 1","importance":0.6,"words":2},
 {"id":"chip.test","role":"chip","x":576,"y":264,"w":96,"h":28,"label":"tests 1","importance":0.6,"words":2},
 {"id":"chip.wiki","role":"chip","x":680,"y":264,"w":88,"h":28,"label":"wiki 0","importance":0.6,"words":2},
 {"id":"item.header","role":"text","x":312,"y":304,"w":720,"h":20,"label":"code, tier: text match (heuristic)","importance":0.3,"words":5},
 {"id":"item.0","role":"text","x":312,"y":328,"w":720,"h":28,"label":"policy.py","importance":0.4,"words":1},
 {"id":"item.1","role":"text","x":312,"y":356,"w":720,"h":28,"label":"verifier.py","importance":0.4,"words":1},
 {"id":"item.2","role":"text","x":312,"y":384,"w":720,"h":28,"label":"evidence.py","importance":0.4,"words":1},
 {"id":"item.3","role":"text","x":312,"y":412,"w":720,"h":28,"label":"app.js","importance":0.4,"words":1},
 {"id":"item.4","role":"text","x":312,"y":440,"w":720,"h":28,"label":"index.html","importance":0.4,"words":1},
 {"id":"ripple.0","role":"text","x":1064,"y":56,"w":360,"h":24,"label":"Ripple 8 nodes","importance":0.8,"words":3},
 {"id":"ripple.1","role":"text","x":1064,"y":80,"w":360,"h":24,"label":"rule 1  state 1  journey 1","importance":0.8,"words":6},
 {"id":"ripple.2","role":"text","x":1064,"y":104,"w":360,"h":24,"label":"runtime 1  obligation 1","importance":0.8,"words":4},
 {"id":"ripple.3","role":"text","x":1064,"y":128,"w":360,"h":24,"label":"receipt 1  packet 1  decision 1","importance":0.8,"words":6},
 {"id":"ripple.notanalysed","role":"text","x":1064,"y":168,"w":360,"h":40,"label":"Not analysed  wiki bundle, outside mapping","importance":0.6,"words":6},
 {"id":"btn.ai","role":"button","x":1064,"y":224,"w":168,"h":28,"label":"Ask AI to propose","importance":0.4,"words":4},
 {"id":"text.provider","role":"text","x":1240,"y":228,"w":120,"h":20,"label":"provider call","importance":0.3,"words":2},
 {"id":"st-unknown","role":"button","x":12,"y":872,"w":104,"h":28,"label":"1 UNKNOWN","importance":0.7,"words":2},
 {"id":"st-fail","role":"button","x":120,"y":872,"w":72,"h":28,"label":"0 FAIL","importance":0.7,"words":2},
 {"id":"st-conflict","role":"button","x":196,"y":872,"w":104,"h":28,"label":"0 CONFLICT","importance":0.7,"words":2},
 {"id":"st-stale","role":"button","x":304,"y":872,"w":80,"h":28,"label":"0 STALE","importance":0.7,"words":2},
 {"id":"st-not-run","role":"button","x":388,"y":872,"w":96,"h":28,"label":"6 NOT_RUN","importance":0.7,"words":2},
 {"id":"st-pass","role":"button","x":488,"y":872,"w":72,"h":28,"label":"3 PASS","importance":0.7,"words":2},
 {"id":"st-attention","role":"button","x":580,"y":872,"w":176,"h":28,"label":"0 need you 0 running","importance":0.7,"words":5},
 {"id":"st-stage","role":"chip","x":1332,"y":874,"w":96,"h":24,"label":"VERIFIED","importance":0.4,"words":1}
]}
```

State `language-tree-suspect` (a suspect chip list is open; `btn.clear` and the reason menu are in the inspector column):

```
{"schema":"eija.layout.v1","ui":"proposed","screen":"language-tree-suspect","viewport":{"w":1440,"h":900},"elements":[
 {"id":"__pointer","role":"text","x":720,"y":450,"w":1,"h":1,"label":"pointer rest position (virtual, not a UI element)","importance":0.5,"words":0},
 {"id":"item.suspect.0","role":"tree-item","x":312,"y":328,"w":720,"h":28,"label":"policy.py","importance":0.5,"words":1},
 {"id":"item.suspect.1","role":"tree-item","x":312,"y":356,"w":720,"h":28,"label":"verifier.py","importance":0.5,"words":1},
 {"id":"item.suspect.2","role":"tree-item","x":312,"y":384,"w":720,"h":28,"label":"evidence.py","importance":0.5,"words":1},
 {"id":"btn.clear","role":"button","x":1064,"y":216,"w":96,"h":28,"label":"Clear","importance":0.5,"words":1},
 {"id":"menu.reason","role":"button","x":1064,"y":248,"w":240,"h":32,"label":"reason 1 of 3","importance":0.5,"words":4},
 {"id":"menu.reason.1","role":"button","x":1064,"y":280,"w":240,"h":32,"label":"reason 2 of 3","importance":0.5,"words":4},
 {"id":"menu.reason.2","role":"button","x":1064,"y":312,"w":240,"h":32,"label":"reason 3 of 3","importance":0.5,"words":4}
]}
```

State `language-tree-ai` (consent, send and adopt in the inspector column; the proposal sits between `btn.send` and `btn.adopt`):

```
{"schema":"eija.layout.v1","ui":"proposed","screen":"language-tree-ai","viewport":{"w":1440,"h":900},"elements":[
 {"id":"__pointer","role":"text","x":720,"y":450,"w":1,"h":1,"label":"pointer rest position (virtual, not a UI element)","importance":0.5,"words":0},
 {"id":"btn.consent","role":"button","x":1064,"y":264,"w":136,"h":28,"label":"Allow egress","importance":0.5,"words":2},
 {"id":"btn.send","role":"button","x":1208,"y":264,"w":72,"h":28,"label":"Send","importance":0.5,"words":1},
 {"id":"btn.adopt","role":"button","x":1064,"y":400,"w":120,"h":28,"label":"Adopt as edit","importance":0.5,"words":3}
]}
```

State `language-tree-confirm` (rename pending; the confirm sheet replaces the ripple and AI block, the rename field replaces the row label). Containers: the 11 of the primary state, minus `btn.ai`, plus `input.rename` and `btn.confirm` = 12. Chrome words about 122 (122, minus the 31 words of the ripple block, the not-analysed line, the AI button and its badge, plus the 31 words of the sheet; the main region is left as in the primary state, so this is an estimate). Nesting depth 3 (sidebar, selected row, field):

```
{"schema":"eija.layout.v1","ui":"proposed","screen":"language-tree-confirm","viewport":{"w":1440,"h":900},"elements":[
 {"id":"row.transaction","role":"tree-item","x":0,"y":172,"w":296,"h":28,"label":"Change Transaction","importance":0.5,"words":2},
 {"id":"input.rename","role":"input","x":60,"y":174,"w":168,"h":24,"label":"Change Transaction","importance":0.5,"words":2},
 {"id":"sheet.title","role":"text","x":1064,"y":56,"w":360,"h":24,"label":"Rename Semantic Transaction","importance":0.5,"words":3},
 {"id":"sheet.tier.0","role":"text","x":1064,"y":88,"w":360,"h":24,"label":"Regenerated  tree, inspector, palette","importance":0.5,"words":4},
 {"id":"sheet.tier.1","role":"text","x":1064,"y":116,"w":360,"h":24,"label":"Suspect  0","importance":0.5,"words":2},
 {"id":"sheet.tier.2","role":"text","x":1064,"y":144,"w":360,"h":40,"label":"Text match  19 files, 2 do not hand-edit","importance":0.5,"words":8},
 {"id":"sheet.tier.3","role":"text","x":1064,"y":192,"w":360,"h":24,"label":"Not analysed  1 source","importance":0.5,"words":4},
 {"id":"sheet.pattern","role":"text","x":1064,"y":224,"w":360,"h":40,"label":"Pattern  semantic transaction, SemanticTransaction, semantic_transaction","importance":0.5,"words":5},
 {"id":"btn.confirm","role":"button","x":1064,"y":280,"w":200,"h":32,"label":"Confirm as candidate edit","importance":0.5,"words":4},
 {"id":"btn.cancel","role":"button","x":1272,"y":280,"w":72,"h":32,"label":"Cancel","importance":0.5,"words":1}
]}
```

## Appendix C. Reproduction

```
# text tier for a term (MEASURED at ddc43b9)
git grep -l -i -E 'semantic transaction|SemanticTransaction|semantic_transaction' -- . ':!docs/hci' ':!design'
# chips for the selected term Reject
git grep -c -E '\bReject\b' -- src ; git grep -c -E '\bReject\b' -- tests
git grep -n -E '\bReject\b' -- docs/verification/ACCEPTANCE_MATRIX.csv
# baseline has no language surface
grep -c -i -E 'role="tree|treeitem|glossary|ubiquitous|draggable|aria-expanded' src/eija_studio/resources/web/index.html src/eija_studio/resources/web/app.js src/eija_studio/resources/web/app.css
```

Reproducibility. The KLM tables follow from the operators in `design/tasks/language-flows.json` and the constants in section 5 by addition. Word, container and target counts follow from Appendix B and the counting rules stated there. The sample-tree statuses follow from rules R1 to R4, the mapping table and `docs/verification/ACCEPTANCE_MATRIX.csv` in 4.1. The keystroke counts follow from the policy stated in section 5. The Python scripts that computed them (revision 3: `.tmp/lang-rev3/klm_h.py` for the H and grid variants, `.tmp/lang-rev3/trunc.py` for truncation and word counts) were kept in the gitignored `.tmp/` and are not part of the repository, so no number in this document is claimed as reproducible by a repository command, except the `git grep` and `grep` lines above (MEASURED).
