# Human views of the weave graph: comprehension-first projections

Lane: weave. Aspect: human-views. Date: 2026-09-29 (revised after audit). Status: proposal feeding [ADR-0105](../../adr/0105-weave-human-views.md). Requirements only: the HCI lane implements the UI. The machine-readable definition is [graph/schema/views.md](../../../graph/schema/views.md); the checks are `graph/bench/human_views_reference.py`, `graph/bench/human_views_budgets.py` and `tests/graph/test_human_views.py` (30 passed on 2026-09-29, revised after audit).

Labels: MEASUREMENT (a script ran; domain stated), PREDICTION (reasoned, not run), HYPOTHESIS (a starting value to calibrate), DESIGN (a proposal of this lane), UNVERIFIED (not opened or not confirmable; nothing is built on it). Source keys: dossiers `[trace] [math] [gdb] [bx] [mde] [lang] [ui] [assure] [incr] [code] [agent] [thesis]` are defined in `docs/weave/research/SYNTHESIS.md`; `[S]` is that synthesis. HCI-lane items are `P1`-`P12` (principles), `I1`-`I10` (invariants), `T01`-`T14` (tasks) from `ux/docs/hci/`. Sources I opened for this document are `H1`-`H33` in section 13.

## 0. Decisions first

| # | Decision | Confidence | Basis |
|---|---|---|---|
| D1 | Every human view is a get-only projection `view(snapshot, params) -> document` defined by a question, a slice, a projection and a budget (graph/schema/views.md). Eight views: change digest, ripple, trace matrix, coverage map, language tree, diagnostics, explain, neighbourhood. Each ships as canonical JSON plus a lossless text form; the HCI lane renders. No view stores or edits anything. | High | [S] decision 1; HCI P3; this document section 3 |
| D2 | The default form follows the question, not fashion: outline for hierarchy, roll-ups and gaps; matrix for requirement-by-evidence enumeration; ordered list for findings; witness chain for "why"; node-link only for a bounded neighbourhood or a path question. The evidence is task-dependent and offers no universal winner. | High that no winner exists; medium on the mapping | H1, H2, H4, H6; section 2 |
| D3 | Hairballs are prevented by budgets and aggregation, not by layout. Every view has hard budgets; overflow becomes exact counts plus "N more", never silent loss; a whole-graph node-link diagram is never a view. | Medium (numbers are HYPOTHESES) | H1, H2, H7; ProofMap history (section 2.3); section 4 |
| D4 | Semantic zoom is a fold over the containment hierarchy of a commutative monoid of status-count vectors. A container badge is `fold_b`, the chain minimum (PASS if and only if every item is PASS; empty is NOT_RUN), taken over the statuses present in the counts of the leaves. The weave join is NOT a badge operator: it is for repeated observations of one claim, and `join(PASS, NOT_RUN)` is PASS. MEASUREMENT (exhaustive, 9,330 sequences of length 1 to 5): `fold_b` had 0 violations of "PASS iff all PASS", the join 996 (first: `[PASS, STALE]` gives PASS). The kernel `aggregate_status` re-applied to its own output is kept as a NEGATIVE CONTROL for a hypothetical hierarchical re-aggregation (12,504 of 25,488 splits differ, 3,720 to PASS); the kernel does not do that, so it is not a failure that occurs in EIJA. | High | section 8; ADR-0097 IR-8; `graph/formal/eijaref/status.py` |
| D5 | Non-PASS states are visible at level 0 of every view with a count; filters report hidden non-PASS counts; NOT_RUN and UNKNOWN are never drawn as PASS or as "unaffected"; an empty tier says what was searched. | High (invariant) | HCI P1, I3; H26 |
| D6 | "Why is this here?" is one canonical witness (a selected cause) plus a contrast with the baseline plus limits, from provenance; the question is a closed set (`why_affected`, `why_not_affected`, `why_status`, `why_link`, `why_finding`); no probabilities. | Medium-high | H25 (contrastive, selected explanations); H21-H23 (questions as menu, debugging domain) |
| D7 | Ripple separates sound reach, over-approximate reach, heuristic reach and not-analysed, as nested closures whose tiers equal a maximin path oracle; direct and transitive are counted apart. On this repo the sound tier is empty and 22 of 28 requirements are reached only through import-derived edges, which is exactly why the tiers must be shown. | High for mechanism; MEASUREMENT for the repo | section 8 |
| D8 | The change digest is the entry point. Operations are grouped in at most 4 chunks; a null edit (raw file digest differs, normalised digest equal) is counted under its hash method, never listed silently and never hidden without the counter. | Medium | HCI P4; `[trace]` section 4 |
| D9 | Determinism: outputs are RFC 8785 subset documents; integers only, no percentages, no timestamps; identity by id; the order that decides a badge label or which rows survive a cap is data (`chain_worst_first`, hashed into `definition_digest`), display order is only applied after the cut; no force-directed layout in any artefact (the neighbourhood carries an integer `(rank, slot)` grid; drags are a layout complement keyed by id). | High | D-01 to D-24 |
| D10 | No benefit is claimed. Every comprehension effect is a PREDICTION until the HCI lane's study runs; what is measured here is slice sizes. | High | HCI I10, P12; `[agent]` section 5 |

## 1. Scope, method and limits

**Question.** What should a person see so that they understand exactly what a change did, using the typed graph, and what does the evidence say about the forms (node-link, matrix, outline, list) at scale?

**Read.** All twelve dossiers, `docs/weave/ARCHITECTURE.md`, `graph/brief.json`, `graph/schema/metamodel.json` (the newer typed metamodel: 42 node types, 29 link types with `affects`, `soundness`, `obligations`), the sibling aspects' bench files in this worktree, the HCI lane's principles, personas, language-tree design and review dossier (`/c/Dev/eija-wt/ux/docs/hci/`), the okf, visual and agents lane docs, and the owner's ProofMap Lite gap register (private repo, read with the owner's `gh` login).

**Opened for this document.** Full texts: Okoe et al. (H2), Kobsa (H4), Shneiderman (H5), Miller (H25; abstract-level in the audit), Sadowski et al. (H26). Wettel et al. (H17) was listed as read in full in the first pass, but the audit could not reopen it (OpenAlex returns only the opening sentences, the publisher page is not readable): its figures are UNVERIFIED. Abstracts only, through the OpenAlex API and DOIs: the rest of section 13, marked "abstract". Two PDFs behind bot walls (Ghoniem et al. full text, Lee et al. full text) were not readable.

**Limits, stated once.**
- The web-search budget was exhausted (200 of 200), so discovery used DOIs, OpenAlex and direct URLs. Studies I did not think to look for are missing. "I found no study of X" means "not found with these means".
- No study of typed assurance graphs, trace-link matrices versus graphs, or graph views consumed by AI agents was found. The visualisation evidence below comes from generic network tasks, tree browsing and software-comprehension experiments, and transfers by analogy only.
- The sibling aspects were being written in the same worktree while I worked. I read the decisions table and flow declarations of `impact-ranking-and-confidence.md`, section 9.5 of `agent-interface-and-context-packs.md`, and `graph/schema/mcp-tools.md` (envelope, tool index, `graph_why`, `graph_impact`, `snapshot_diff`); I only searched `consistency-and-sync.md` and `rules.md`; `storage-and-query.md` did not exist. The interfaces below track their state at that time and may drift: UNVERIFIED that they will match after merge.
- Licences of rendering libraries come from GitHub SPDX metadata (H32), not from LICENSE texts.

## 2. What the evidence says about node-link, matrix and outline at scale

### 2.1 Studies

| # | Study | Design | Result as reported | Limits | Key |
|---|---|---|---|---|---|
| 1 | Ghoniem, Fekete, Castagliola, Information Visualization 2005 | Controlled experiment, node-link vs matrix, 7 generic graph tasks. Per Okoe et al.'s description: synthetic graphs of 20, 50 and 100 nodes at densities 0.2, 0.4, 0.6 | "when graphs are bigger than twenty vertices, the matrix-based visualization outperforms node-link diagrams on most tasks. Only path finding is consistently in favor of node-link diagrams" (abstract). Per Okoe: small sparse graphs favoured node-link for connectivity; large dense graphs favoured matrices on all tasks | Abstract only; random dense graphs; software graphs are sparser | H1 |
| 2 | Okoe, Jianu, Kobourov, TVCG 2019 | 864 crowd participants, between-subjects, 14 tasks, interactive node-link (NL) and adjacency matrix (AM), two real scale-free networks: 258 nodes and 1090 edges (density 0.032 as printed, 2E/V^2; 4.22 edges per node), 332 nodes and 2126 edges (density 0.039 in the paper's Table 1; its prose says 0.019, a typo, since 2E/(V(V-1)) gives 0.0387; 6.40 edges per node) | Of 10 topology tasks, NL was more accurate in 5 and less accurate in 3; AM better in 2 of 4 group/cluster tasks; NL a slight edge in 1 of 2 memorability tasks. AM costs: labels barely visible when zoomed out, neighbours far from the label axis were found less accurately (one repeat: accuracy .5 far vs .79 near), zoom and pan felt tedious; NL costs: occlusion and ambiguity where edges pass through nodes | Crowdsourcing; two datasets; sparse graphs; interaction implementations not identical; authors say generalisation to larger or denser graphs is unclear | H2 |
| 3 | Keller, Eckert, Clarkson, Information Visualization 2006 | User experiments on directed product-model graphs, node-link vs matrix | Abstract states the experiments "identify key factors on the readability of graph visualisations" and confirm earlier comparisons; results not read | Abstract only | H3 |
| 4 | Kobsa, InfoVis 2004 | 48 students, between-subjects, 5 tree visualisations plus Windows Explorer (indented outline) as baseline, 15 tasks | Task time per task: Explorer 101.2 s and Treemap 106.5 s (fastest), BeamTrees 188.4 s (slowest). Correct answers: Treemap 73.3% highest, BeamTrees 40.8% and Tree Viewer 41.7% lowest. Conclusion: none of the visualisations "showed benefits for users that went significantly beyond" the Explorer baseline | File-directory trees; subjects were skilled with Explorer; students | H4 |
| 5 | Wettel, Lanza, Robbes, ICSE 2011 | 41 participants (UNVERIFIED), 4 sites, CodeCity (3D city metaphor) vs Eclipse plus Excel, Java systems, whole-system comprehension tasks | UNVERIFIED (not re-openable in the audit): the first pass recorded +24.26% correctness and -12.01% completion time for CodeCity overall; nothing here rests on these figures | A tool comparison, not a representation comparison; text tools as baseline; 3D | H17 |
| 6 | Ware, Purchase, Colpoys, McGill, Information Visualization 2002 | Cognitive cost of graph aesthetics on shortest-path finding in spring layouts | "after the length of the path the two most important factors are continuity and edge crossings"; the number of branches leaving path nodes also matters | Abstract; synthetic graphs | H7 |
| 7 | Larkin and Simon, Cognitive Science 1987 | Theory: informationally equivalent representations differ in computational efficiency because operators for search and pattern recognition differ | "When two representations are informationally equivalent, their computational efficiency depends on the information-processing operators that act on them" | Paper-and-pencil physics and mathematics problems | H6 |
| 8 | Ko, Myers, Coblenz, Aung, TSE 2006 | Developers, unfamiliar program, 5 tasks, 70 minutes | Developers spent on average 35% of their time on the mechanics of navigation within and between files; they lost track of collected code | Eclipse of that date; small program | H18 |
| 9 | Ko and Myers (Whyline): CHI 2004, ICSE 2008, CHI 2009 | Debugging tools that let a person pick a "why did" or "why didn't" question about program output | 2004 (Alice): debugging time down "by nearly a factor of 8", 40% more tasks completed. 2008: novices with the Whyline "twice as fast as expert programmers without it" on one task. 2009 (Java): about 3 times as successful and about 2 times as fast against a breakpoint debugger | Runtime debugging, small tasks, authors' own tool; numbers as reported in abstracts | H21-H23 |
| 10 | LaToza and Myers, 2010; Sillito, Murphy, De Volder, FSE 2006 | Surveys and observation of what developers ask | 179 respondents listed 371 hard-to-answer questions (21 categories; the abstract's "94 distinct categories" reads garbled, so no question count is used); the most frequent categories concern intent and rationale ("why was it done this way"); Sillito catalogued 44 kinds of questions during change tasks | Self-report; abstracts | H19, H20 |
| 11 | Miller, Artificial Intelligence 2019 | Review of the social-science literature on explanation | Four findings: explanations are contrastive (why P rather than Q), selected (one or two causes, biased), probabilities matter little compared with causes, and social | A review, not an experiment on software | H25 |
| 12 | Sadowski, Soederberg, Church, Sipko, Bacchelli, ICSE-SEIP 2018 | Google code review: 12 interviews, 44 survey respondents, 9 million reviewed changes | Cites earlier work as "compelling evidence" that "understanding code to review is a major hurdle"; median change 24 lines | The hurdle claim is quoted from earlier work | H26 |
| 13 | Johnson, Song, Murphy-Hill, Bowdidge, ICSE 2013 | 20 developer interviews on static analysis tools | False positives and the way warnings are presented are barriers to use | Interviews; abstract | H27 |
| 14 | Cuddeback, Dekhtyar, Hayes, RE 2010 | 26 participants vetting candidate requirements traceability matrices | Analysts move a candidate matrix toward the line where recall equals precision; those given low-recall, low-precision matrices "drastically improved both". The abstract calls the RTM the artefact behind impact analysis, reverse engineering, reuse and regression testing | Java formatter program | H28 |
| 15 | von Mayrhauser and Vans, IEEE Computer 1995 | Survey of six program-comprehension models | The general models "may not always apply to specialized tasks that more efficiently employ strategies geared toward partial understanding"; results from small programs may not scale | Survey | H33 |

### 2.2 Reading, sceptically

1. **There is no universal winner; the task decides.** Node-link keeps winning path-finding and, with interaction, many topology tasks even at 258 to 332 sparse nodes (H1, H2). Matrices win group, density and counting tasks and remove occlusion (H2). Outlines held their ground against four novel tree displays (H4). A rule of the form "graphs are hairballs, use matrices" is not supported; nor is "node-link is intuitive".
2. **Threshold evidence is thin and pulls in two directions.** "More than twenty vertices" (H1) comes from dense synthetic graphs; H2's sparse graphs of 258 and 332 nodes were workable for topology tasks with highlight and selection. Our default of 20 nodes for an unassisted node-link view is therefore a HYPOTHESIS placed between them, with an explicit expansion step to 50 and a hard stop at 100.
3. **Representation efficiency depends on the operation** (H6). That is the theoretical reason to define each view by its question. It is a principle, not a measurement of our views.
4. **Path-following cost has known drivers**: path length, continuity, crossings and branching (H7). This is why the neighbourhood view bounds out-degree shown and never draws the whole graph.
5. **Navigation overhead is large in practice** (H18: 35% of time). A view that answers a question in place saves navigation; that saving is a PREDICTION for our views.
6. **People ask "why" and "why not" questions and answer them slowly by hand** (H19-H23). Tools that turn such questions into a menu with a computed answer were much faster in debugging experiments. The transfer to link explanations is by analogy and is a PREDICTION.
7. **Explanations should be short and contrastive** (H25). One selected cause, a foil, no probabilities.
8. **Comprehension is often partial and task-specific** (H33), so views answer questions; they do not try to hold the whole model.
9. **Task vocabularies exist.** Graph-task taxonomies (H15) and lists of low-level analytic tasks (H16) name what people do with a network. The eight views are phrased as questions; no claim of covering either taxonomy is made.
10. **Slices are a natural unit.** Programmers were observed to break programs into non-contiguous pieces related by data flow when debugging (H24). The ripple and the neighbourhood are slices over typed links.
11. **Hybrids exist.** NodeTrix shows node-link for global structure and matrices for dense communities (H11, abstract). Node-link and matrix stay separate views here; a hybrid is a possible later view if the study shows people need both at once.
12. **Ways to separate overview and detail are catalogued** as overview+detail, zooming, focus+context and cue-based techniques, with the empirical evidence summarised (H13; I read only the abstract). L0 and L1 are overview+detail, the container fold is zooming, and no distortion is used.

### 2.3 What the evidence does not say, and our own history

- Nothing found compares matrix, outline and node-link for **typed assurance graphs** (requirements, tests, proofs) or for **agent** consumption. Everything above transfers by analogy.
- The owner's ProofMap Lite history is a measurement of what happens when completeness is chased with diagrams. Its gap register has 68 rows; 40 of them match `visual|visible|diagram|draw.io|model view` (a regex count, MEASUREMENT of the file, not a judgement; the first pass said 41 and the audit recounted 40). Rows GAP-051 to GAP-058 escalate coverage into pictures: "one source-file node per covered file", "one inferred row and deterministic visual id per Graphify manifest symbol", each because the previous summary "+N more" left agents opening JSON. GAP-068 records that the dashboard's page became the scroll container. Read: every time completeness was made visible as a diagram, the next gap was that the diagram was too big to read, and a new diagram was added. Its sidebar lists 20 model views (`Language`, `Use Cases`, ... `Verification`); I found no budget for their number in the register or the README (my reading, H31).

### 2.4 Consequence: form by question class

| Question class | Default form | Alternatives | Why | Key |
|---|---|---|---|---|
| What changed | Grouped outline of operations | keyed diff JSON, line diff at level 2 | Understanding the change is the hurdle; operations, not lines; HCI P4 | H26, H33 |
| What does it touch | Outline by tier and type with counts | bounded neighbourhood | Counts and tiers before pictures; over-approximation must be visible | H6, D7 |
| Is each requirement satisfied and verified | Matrix, rows requirements, columns evidence kinds (at most 7) | outline with chips | Exhaustive two-set enumeration; the traceability matrix is the established artefact; no occlusion | H2, H28 |
| Where are the gaps | Outline of containers with counts vectors | matrix; treemap deferred | Roll-ups compose; outline was not beaten by novel tree displays; a spatial overview reportedly beat text tools in one 3D study (H17, figures UNVERIFIED) but against a different baseline | H4, H17 |
| What does this term mean and where is it bound | Tree (HCI D1) with inspector | matrix term by surface | Hierarchy with drill-down | H4, HCI |
| What is wrong | Grouped list with witness one click away | SARIF, text | Presentation is a documented barrier to using analyser output | H27 |
| Why is this here | One witness chain, a contrast, limits | reproduce command | Contrastive, selected explanations; "why" questions as a menu | H25, H21-H23 |
| How do these connect | Bounded node-link, integer grid | edge table | Path and neighbour tasks favour node-link; bound the size | H1, H2, H7 |

## 3. The eight views

Definitions, slices, projections, orders and budgets are in [graph/schema/views.md](../../../graph/schema/views.md) sections 6 to 8. This section says what each is for, what a person sees, and what the HCI lane must do or must not do.

| Id | Question (HCI tasks) | L0: always visible | L1: one step | L2: source |
|---|---|---|---|---|
| HV-01 change-digest | What did this change do? (T02) | Operation counts per chapter (core, consequences, glue), the hidden null-edit counter with its hash method, one line of the impact aspect's change-risk vector (exact counts, no score), `bounds.complete`, `snapshot.dirty` | One operation: before and after in the model's terms, cause, chapter | Keyed diff JSON, line diff, digests |
| HV-02 ripple | What does it touch and how sure are we? (T03, T05, T12) | Counts per tier (sound, over-approximate, heuristic, not analysed), direct vs transitive, what was searched | One node: canonical witness summary, tier, distance | Full witness, closure certificate |
| HV-03 trace-matrix | Satisfied and verified by what? (T14, T06, T12) | Counts by status, gap count, `not_applicable` count, page and column headers | One cell: links, tiers, evidence, SUSPECT cause, redundancy | Link records, digests, ledger entries |
| HV-04 coverage-map | Where are the gaps? (T14, T12) | Counts vector and badge per container at default expansion (2 levels, at most 15 rows) | One container: counts by obligation, first gaps | Item list with statuses |
| HV-05 language-tree | What does the language mean and where is it bound? (T05, T09) | Tree to depth 4, own status per row, change marks | Inspector: definition, forms, bindings with tier, ripple summary | Registry record, hash diff |
| HV-06 diagnostics | What is wrong or unproven? (T11, T12, T14, T06) | Counts by error, warning, note, not run; new since base | One finding: message, location, witness summary, fix proposal preview | Finding JSON, SARIF |
| HV-07 explain | Why is this here, or why not? (T03, T05, T11, T12) | The sentence, at most 4 witness segments, the contrast | Hops list (at most 12) | Reproduce command with the snapshot root hash |
| HV-08 neighbourhood | How do these connect? (T03, T12) | At most 20 nodes on an integer grid, or the edge table | Expand to 50 on request | Node and link records |

### 3.1 Worked example with real numbers (MEASUREMENT on this repo, typed graph derived from imports and the acceptance matrix)

The repo has no declared `satisfies` links and no term registry, so this is a proxy: `depends_on` and `covers` come from `ast` imports (derived, soundness `may`), `verifies` from the evidence column of `ACCEPTANCE_MATRIX.csv` (declared, `must`). Arcs are the directions in which a change flows: from a changed module to its dependents and to the tests that cover it, and from a test to the requirement it verifies (the impact aspect declares `verifies` as flowing both ways; only this direction is used here). Change `src/eija_studio/domain/impact.py`:

```text
HV-02 ripple   changed: repo://src/eija_studio/domain/impact.py (1 node)   complete: true
  sound (must)              0   searched: 0 declared satisfies links exist; the first hop (module to covering test) is import-derived (may), so it bounds every path at may
  over-approximate (may)   30   5 modules, 3 tests, 22 requirements   (3 direct, 27 transitive)
  heuristic                 0
  not analysed              0   extractors not run: none reported
```

The empty sound tier is honest and must be said: the 22 requirements are reached only through import-derived hops. Declaring `satisfies` links would not by itself fill the sound tier for a code change, because every module-to-requirement path crosses a `covers` hop (may) even though `verifies` is declared (must). Ask `why_affected` for AC16 (area Impact):

```text
HV-07 explain  why_affected  req AC16   tier over-approximate (may)   1 path, rank 1
  1. impact.py  ~>  tests/test_domain.py    link: test covers module          (derived, may; import proxy)
  2. tests/test_domain.py  ~>  AC16         link: test verifies requirement   (declared, must; CSV row AC16)
  (~> is the direction in which a change flows)
  contrast: at base_root AC16 was <status>; impact.py digest <d0> is now <d1>        (values come from the snapshots)
  limits: hop 1 is an import proxy, not measured coverage
  actions (owner, proposals only): review AC16; re-run tests/test_domain.py; no ack is offered (no SUSPECT link)
```

The witness has 2 hops and 2 segments (`covers`, `verifies`), inside the budget of 4 segments. Over all 262 (module, requirement) witnesses on this repo, hops are 2 to 4 (median 3) and segments 2 to 3 (median 3).

### 3.2 Per-view requirements for the HCI lane

- **HV-01.** Chapters are computed (layer, truth class, `derived_from`), not summarised by a model. `RENAMED` is one row. The null-edit counter is a permanent element, names the method, and reveals the edits on request. A "Viewed" mark persisting across revisions and clearing when an operation's digest changes is the HCI lane's (P4); the view supplies the digest.
- **HV-02.** Show tiers as four chunks. An empty tier shows what was searched. "Analysed, not affected" is never drawn as a state; `why_not_affected` gives the searched scope, or UNKNOWN with the frontier count when `complete` is false. The optional `verification_cover` block says covers is not fault detection.
- **HV-03.** Cells carry status word plus glyph plus (optional) colour (P6). Distinguish four empty conditions: `gap` (required link absent), `not_applicable` (policy), NOT_RUN (extractor or prerequisite missing), and an unrequired blank. Totals row and column are counts vectors. Rows sorted by `(area, id)`; a group header only for an area of two or more rows.
- **HV-04.** Row = container with counts vector and the two denominators as `n of m`; badge from the fold, not from children. Order structural. Bars, if drawn, are redundant to counts.
- **HV-05.** The HCI lane's language-tree design (D1-D10) stands; the view supplies rows, kind letters from `ddd_role`, tiers, and the four ripple tiers of its rename sheet (regenerated = must `derived_from`; suspect = digest mismatch on a declared link; text match = heuristic derived `names`; not analysed = frontier or NOT_RUN).
- **HV-06.** Findings are never scored. New since base first. A finding's fix is a preview; the view offers no apply (I4). NOT_RUN records are findings of level `not run`, listed with the missing tool and pin.
- **HV-07.** The sentence is a template id with structured args, expanded by the renderer; no model writes it. "Another path" walks `path_rank`. Actions are text for the owner.
- **HV-08.** Consume the `(rank, slot)` grid; do not run a force-directed layout for anything saved, exported or compared. A user's drag is a layout complement keyed by id.

## 4. Scale strategy

### 4.1 Budgets

Every budget is a HYPOTHESIS with a stated basis (views.md section 8). The tuple is: chunks at the top level, disclosure levels after L0, tree depth, rows per screen, rows before "N more", matrix rows per page and columns, neighbourhood nodes (default, expanded, hard stop), out-degree shown, witness segments and hops, closure node budget, and a latency target. Values: 4, 2, 4, 25, 5, 25 and 7, 20 / 50 / 100, 7, 4 and 12, 2000, 1000 ms.

Arithmetic:

- Matrix cells per page: rows times columns, at most 25 x 7 = 175. This repo: 28 rows x 4 evidence kinds = 112 cells whole (MEASUREMENT); 28 exceeds 25 rows, so 2 pages; the first page has 25 x 4 = 100 cells.
- Whole-graph node-link: 23 modules exceed the default 20; the matrix would be 23 x 23 = 529 cells. Neither is a view; the neighbourhood is.
- Closed 1-hop ego size (node plus neighbours): max 16, median 4; 0 of 23 modules exceed 20. The best-first selection at budget 20 returned at most 19 nodes, because the largest connected component has 19 nodes: on this repo the node budget never binds (MEASUREMENT). Unit tests exercise it with smaller budgets.
- Witness segments to a requirement: at most 3 (budget 4).
- Ripple lists: for 15 of 23 modules the requirement or test group exceeds 5 rows (max 25 requirements, 6 tests), so priority-then-cap with "N more" is needed on this repo.

### 4.2 Semantic zoom is a monoid fold

Let `H` be the containment hierarchy (`contains`, acyclic in the metamodel) and `c(I)` the counts vector of a set of items `I` (six statuses, plus a gap count and a not-applicable count). Then `c(A union B) = c(A) + c(B)` for disjoint sets: `c` is a homomorphism from (multisets, union) to (vectors, addition), a commutative monoid. Consequences: any zoom level is the fold of the level below; the result is independent of grouping and order (so byte-stable); no status can disappear when a container is collapsed (law C2). The container badge is `fold_b` (chain minimum with PASS on top; empty is NOT_RUN) over the statuses present (the support of `c`). Because `fold_b` is idempotent, commutative and associative, this equals the fold over all leaves. It is PASS if and only if every leaf is PASS, for every chain with PASS on top (checked over all 120 chains, sequences up to length 3). Two operators exist in the status algebra and they are not interchangeable: the join (least upper bound in the information order) is for repeated observations of ONE claim by one check, and it masks a non-PASS item among distinct items (`join(PASS, NOT_RUN)`, `join(PASS, UNKNOWN)` and `join(PASS, STALE)` are all PASS); `fold_b` is for distinct items and cross-claim roll-ups (ADR-0097 IR-8, `eijaref.status`). The first version of this document measured "0 mismatches" for the join under splits; that only shows the join is idempotent and associative, so it says nothing about which operator a badge needs, and it is dropped as evidence. The counts, not child badges, are the input so that an empty child container (NOT_RUN) does not lower a non-empty sibling. Laws C1, C2, C4 and C5 are executable in `tests/graph/test_human_views.py` on the reference definitions, including the property "badge is PASS iff every leaf is PASS" with the join as a negative control; C3 and C6 need the implemented views (NOT_RUN); a second negative control is the kernel aggregate re-applied to its own output (section 8), which the kernel does not do.

### 4.3 Progressive disclosure

L0 is the counts and body at default expansion; L1 is an inspector; L2 is source (views.md section 4). It follows the visual information-seeking mantra, "Overview first, zoom and filter, then details-on-demand" (H5, read in full): overview is L0, zoom is the containment fold, filter is the facets with hidden counters, details-on-demand are L1 and L2, relate is HV-07 and HV-08, extract is the text form, and history is the contrast with the base snapshot (there is no per-session history). This mirrors the HCI lane's decision D3 (inspector level 1, source level 2) and the two-level rule of thumb (H30, which states no evidence base). UNKNOWN, NOT_RUN, STALE, FAIL, CONFLICT and `not_run` reasons are L0. The chunk limit of about 4 top-level groups per change follows P4 and the working-memory range of 3 to 5 items under controlled conditions (H29).

### 4.4 Overflow, filters and the hidden counter

Priority-then-cap orders a long list by `(severity rank, distance, id)` before cutting, so the shown rows are the worst. The severity rank is `chain_worst_first` of the definition block: data, hashed into `definition_digest`, because it decides which rows are shown and which are hidden. The HCI lane may reorder or restyle the shown rows, never choose the cut (test: documents are byte-equal for two display orders, and a different rank changes the cut); `overflow` carries `hidden` and `hidden_by_status`. Property test: shown plus hidden equals total, and a PASS is never shown while a non-PASS is hidden; the negative control (cut by id alone) hides a FAIL behind two PASS rows. Trees and matrices do not cap. Any filter reports the counts by status of the non-PASS rows it hides (HCI D7).

### 4.5 Neighbourhood by degree of interest

The literature offers a way to keep a large graph readable without drawing all of it: show the neighbourhood of a focus chosen by a degree-of-interest function (Furnas' fisheye views, adapted from trees to graphs by van Ham and Perer: H8, H9). Our version is an integer best-first expansion `DOI(x | f) = API(x) - D(f, x)`, with `D` the shortest-path distance from the focus (breadth-first distances computed first; the first draft used the depth at which the expansion happened to reach a node, which can be longer, and the audit found a case; a differential test against an independent oracle now covers it), with a bonus so non-PASS nodes are not crowded out, connected by construction, `O(E log V)`. The weights are this lane's HYPOTHESIS. Hierarchical aggregation (H10) is the general guideline behind the outline roll-ups: aggregate to make displays "less cluttered", with the aggregation rule explicit.

### 4.6 Growth (PREDICTION, arithmetic on stated assumptions)

At the measured 1.913 edges per node, a code graph of N modules has about `E = 1.913 N` edges, density `2E / (N (N - 1))`, and `N^2` matrix cells.

| N (modules) | E | density | matrix cells | whole node-link within default 20? | 1-hop ego (max degree grows) |
|---|---|---|---|---|---|
| 23 (measured) | 44 | 0.174 | 529 | no (23 > 20) | 16 (measured) |
| 100 | about 191 | about 0.039 | 10,000 | no | PREDICTION: hubs keep it near or above 20 |
| 230 | about 440 | about 0.017 | 52,900 | no | same |
| 1000 | about 1913 | about 0.004 | 1,000,000 | no | same |

H2's two networks have density 0.032 and 0.039 (Table 1; the prose typo 0.019 is not used) and 4.22 and 6.40 edges per node. A 100-module graph at 1.913 edges per node has a similar density (about 0.039) but far fewer edges per node, and density alone is a misleading comparator because it falls as the graph grows while edges per node stay constant: the code graph is sparser per node than H2's networks at every N. So H2's finding (node-link with interaction was not worse for topology tasks at 258 to 332 nodes) transfers only weakly. The graph is still far too big to draw whole, so the bounded neighbourhood remains necessary and its budget stays a calibration question, not a settled number.

Latency (PREDICTION). Tiers need three closures done naively. The graph-database dossier measured plain BFS at 56 ms for 10^5 edges and 848 ms for 10^6 (`[gdb]` section 2, synthetic). Three closures is arithmetic on those two numbers: about 170 ms and about 2.5 s. This is probably pessimistic: the three nested closures can be computed in one bucketed maximin pass (a single traversal keyed by tier), which is not built or timed here. Against the 1 s target for a view document, 10^5 edges fits and 10^6 edges does not; there the view is a job with progress (HCI P7) or uses the closure node budget (2000, the maximum of `graph_impact.max_nodes` in the agent contract) and reports `bounds.complete: false` with the frontier.

## 5. Explanations from provenance ("why is this link here")

**What exists to explain from** (truth classes, `[S]` decision 1): declared links carry the declaring file location, hash method, baseline digest and ledger sequence; derived facts carry rule id and premises (canonical minimal derivation, `[math]` section 2.3); inferred links carry tool, model, version and the run; evidence carries digests and the checker; findings carry the violation query rows or the closed-world scope searched.

**Answer shape** (views.md section 7.4). The base is the agent contract's `graph_why` result (`holds`, `rule_id`, `premises`, `witness` steps, `searched_scope`, `rechecked`); the human document adds `sentence_id` and `args`, `truth_class` and `soundness`, the witness grouped into at most 4 segments of equal `(link kind, origin, tier)`, a contrast with the baseline, limits, the reproduce command with the snapshot root, and owner actions as text.

**Why this shape.** Explanations that people find satisfying are contrastive, select one or two causes and do not lean on probabilities (H25). So: one canonical witness (lexicographically first shortest path, checked against a brute-force oracle on 200 random graphs), an integer count of other shortest paths and a `path_rank` to ask for the next; a foil (the baseline); no confidence. Selection is biased by nature (H25), so `n_paths` and "another path" keep the choice inspectable. Questions are a closed menu generated from the graph (H21-H23), and the most common hard questions are about rationale (H20), which is what `motivates`, `supersedes` and ADR links answer for a requirement.

**Absence.** "Why is R not affected" and "why is there no verifier" have no derivation (a semiring explanation exists only for the positive fragment: `[math]` section 2.3). The answer is the closed-world scope: which relations were searched, how many nodes, whether `complete`. If the closure stopped at the budget the answer is UNKNOWN with the frontier, never "no".

**Trust.** The witness is untrusted output that a small checker re-verifies: every node exists at `snapshot.graph_root`, every hop is a link (`check_certificate`, `check_unreachable` of the formal aspect). A view whose witness has not been checked says so.

## 6. Mapping to the HCI lane

| HCI item | Requirement on the views | Check |
|---|---|---|
| P1 UNKNOWN visible, counted, never rolled into PASS | L0 counts by all six statuses; `gap`; badge from the fold; hidden counter on filters | laws C2, C4; negative control (kernel re-aggregation) |
| P2 owner decides; no approve or apply reachable | No view carries an approve, apply, clear or edit action; explain actions are text with `applies: false` | `test_no_view_offers_an_owner_operation` with a negative control; agents lane test for the tool surface |
| P3 what you see is generated; edits are typed requests | Documents are pure functions of a root; layout is a complement keyed by id | determinism test; `definition_digest` |
| P4 the unit of review is a semantic operation | HV-01 operations, at most 4 chunks, null-edit counter | X6 partition test |
| P5 every change shows its ripple, no silent knock-on | HV-02 tiers; "not analysed" never drawn as "unaffected" | X4 nested tiers; maximin oracle |
| P6 status never by colour alone; contrast computed | Data carries the status word; colour is presentation | HCI lane |
| P7 latency classes | Document target 1 s; slower is a job; previous verdict stays visible as STALE | PREDICTION (section 4.6); HCI probe |
| P8 keyboard first; drag has a path | Grid and tables are addressable by id; no drag-only information | HCI lane |
| P9 AI proposals grounded and provisional | `proposes` links appear only as proposals; sentences never model-written | schema |
| P10 restraint: chunks, levels, words | Budgets (section 4.1); L0 to L2 | budget tests; HCI slop budget |
| P11 undo states what it does not restore | Not applicable (views do not edit) | not applicable, with reason |
| P12 predictions labelled | This document; `label` in the definition block | review |
| I3 UNKNOWN never hidden; human understanding UNKNOWN until measured | D5 and D10 (sections 0 and 12) | laws C2, C4 |
| I4 providers and agents never approve or apply | as P2 | as P2 |

Task mapping: T02 HV-01; T03 HV-02, HV-07, HV-08; T05 HV-05, HV-02, HV-07; T06 HV-03, HV-06; T09 HV-05; T11 HV-06, HV-07; T12 HV-03, HV-04, HV-07, HV-08; T14 HV-03, HV-04, HV-06. T01, T04, T07, T08, T10, T13 are outside these views (approval, canvas editing, counterexample stepping, onboarding and AI prompts belong to other HCI aspects).

**What the HCI lane decides**: display order of statuses, glyphs, colours, geometry, motion, keyboard maps, the wording that fills sentence templates, and the calibration of every budget. **What it must not do**: recompute roll-ups from child badges; drop counts when filtering; draw NOT_RUN or UNKNOWN as PASS or "unaffected"; add approve, apply, clear or edit to a view; run its own layout for anything saved or compared.

## 7. Mathematics and computer science: what earns a place

Each row names a concrete benefit and a cost; rows without one are theory-only.

| School | Mechanism in the views | Benefit (number or failure removed) | Cost and limit | Verdict | Source |
|---|---|---|---|---|---|
| Algebra: monoid homomorphism, chain minimum | Counts vectors; badge = `fold_b` over the support of the counts | Composable zoom and a badge that cannot show PASS over a non-PASS item. MEASUREMENT: `fold_b` 0 violations of "PASS iff all PASS" in 9,330 sequences, the join 996 (negative control). NEGATIVE CONTROL: kernel `aggregate_status` re-applied to its own output differs from flat in 12,504 of 25,488 splits (3,720 to PASS); the kernel does not do this | None; the kernel function is not changed (own ADR) | adopt | section 8; ADR-0097 IR-8 |
| Order theory: lattices, maximin paths | Tiers as nested closures `R_0 <= R_1 <= R_2`; tier = best path's weakest link | A miss or an over-count traces to a heuristic edge; equals a brute-force path oracle on 150 random graphs | Three closures (PREDICTION 170 ms at 10^5 edges; a one-pass bucketed maximin traversal should be cheaper, not built) | adopt | `[math]` 2.2; tests |
| Graph theory: BFS order, SCCs, topological order | Canonical witness (lexicographically first shortest path); HV-01 dependency order over the condensation with minimum-member labels | One witness, same on every platform; cycles listed together; equals brute force on 200 graphs. `nx.condensation` labels took 24 forms over 200 shuffles (`[S]` section 7) | Own ~100 lines | adopt | tests; `[math]` 2.1 |
| Provenance (positive fragment) | Witness = one canonical derivation; premises stored | "Why" is a lookup and re-checkable | No semiring explanation for absence: scope searched instead | adapt | `[math]` 2.3 (not opened by me) |
| Content addressing, keyed diff | Method-versioned digests; null edits = raw digest differs, normalised equal | Review lists exclude formatting noise with a counter. Raw-byte digests were stale on 99.9 to 100% of file-touching commits in two repos, symbol ASTs on 7 to 9% (`[trace]` section 4, MEASUREMENT) | A normaliser can hide a meaningful edit: the counter names the method | adopt | `[trace]` 4 |
| Best-first search with a degree-of-interest score | HV-08 selection, integers, connected | Bounded, deterministic neighbourhood; problems not crowded out | Weights are heuristic; on this repo the budget never binds | adopt (labelled heuristic) | H8, H9 |
| Combinatorial optimisation | Greedy weighted set cover for `verification_cover` | A small verifier set covering the impacted obligations (greedy set cover, within a factor H(n) of the minimum; minimum set cover is NP-hard, so the set is not claimed to be minimal) | Covers is a link, not fault detection | adopt (optional block) | `[math]` 2.8 |
| Graph connectivity | Vertex-disjoint evidence paths, capped at 3 | Single point of evidence as a count | Flow per requirement | adapt (report only) | `[math]` 2.1 |
| Relational algebra, Datalog | A view slice is a named query over relations; gaps come from stratified negation (WV-010) computed once by the rules, not by the view | Order-independent; views cannot disagree with the compiler | None | adopt (lite) | `[gdb]` 4 |
| Type theory | Closed sums for statuses, question kinds, sentence ids | An agent or renderer never parses prose | Schema upkeep | adopt | `[math]` 2.9 |
| Category theory, sheaves (checks only) | Mapping totality (every node and link type is shown or `not_shown`); overlap agreement X1-X6 | A new type cannot silently vanish from the views; two views cannot disagree about a shared id | Tests only | adopt as tests | `[bx]` 4 |
| Cognitive science: informational vs computational equivalence | Choose the projection by the question | Reason for eight views instead of one graph | A principle, not a measurement | adopt as design rule | H6 |
| Graph drawing: force-directed layout | none in artefacts | Removes floats and seeds from artefacts (D-10) | Users lose organic layout; an integer grid is plainer | reject for artefacts; UI may drag as a complement | D-10 |
| Matrix seriation | none by default | A declared canonical order is deterministic; the survey lists many heuristics (H14) | Clusters are not made visible by order alone | reject as default; user sort with a total tie-break | H14 |
| Space-filling maps (treemap) | deferred | Kobsa found no significant gain over an outline (H4); Wettel's reported overview gain (UNVERIFIED) was against text tools (H17) | Needs a study | defer; test in the HCI study | H4, H17 |
| Edge bundling | none | The literature claims less clutter (H12) | Curves hide provenance; floats | reject | H12 |
| Probabilistic confidence | none | Explanations rely on causes, not probabilities (H25); `[S]` decision on no percentages in gates | none | reject | H25 |

## 8. Measurements (MEASUREMENT unless stated)

Command: `python graph/bench/human_views_budgets.py --out graph/bench/results/human-views-budgets.json`. Domain: `src/eija_studio/**/*.py`, `tests/test_*.py`, `docs/adr` records numbered below 0089 (outside the weave block), `ARCHITECTURE.md`, `ACCEPTANCE_MATRIX.csv`, `examples/excursion-*.json` and `graph/schema/views.md`, LF-folded; the input root is in the result file. Two runs give byte-identical output. Windows only; POSIX is NOT_RUN (D-20).

| Fact | Value | Section of result |
|---|---|---|
| Import graph | 23 modules, 44 directed edges (no mutual imports, 23 SCCs), 1.913 edges per node, density 0.174, max degree 15, largest connected component 19, closed 1-hop ego size max 16 median 4 | `import_graph` |
| Acceptance matrix | 28 rows, 22 areas (5 with two or more rows, 17 singletons), 4 evidence kinds (doc, other, script, test), 112 cells, 34 filled by kind, 9 distinct evidence files; statuses PASS_LOCAL 17, PARTIAL 9, NOT_RUN 2 | `requirements` |
| Language | 10 glossary terms, 5 contexts; baseline workflow 4 states, 4 transitions, 2 roles; tree depth NOT_RUN (no registry with `ddd_role`) | `language` |
| ADR references | 7 ADR files, 0 cross-reference edges | `adrs` |
| Typed ripple | 23 modules, 6 test files, 28 requirements; 44 depends_on, 16 covers, 34 verifies; affected tests per changed module 0 to 6 (median 2), requirements 0 to 25 (median 16); 15 of 23 modules need overflow at 5 rows; 7 of 23 modules touched by no test file; 3 requirements (AC15, AC26, AC28) with no test file; tier 0 reach is 0 everywhere | `typed_ripple` |
| Witnesses | 262 (module, requirement) witnesses: hops 2 to 4 (median 3), segments 2 to 3 (median 3); all within 4 | `typed_ripple` |
| Kernel ripple | 3 changed actions (Approve, Recommend, Reject) reach 20 nodes: 3 each of rule, runtime, state-view, journey, obligation, receipt, plus 1 review-packet, 1 local-decision; one edge kind, so one segment of up to 7 hops | `kernel_ripple` |
| Roll-up laws | counts vector C1, C2 and badge C4 (`fold_b` over the support): 0 mismatches in 500 seeded trees, and 0 violations of "badge PASS iff every leaf PASS"; exhaustive over 9,330 sequences of length 1 to 5: `fold_b` 0 violations, join 996 (negative control; first `[PASS, STALE]` gives PASS); split composition of non-empty parts: `fold_b` 0 and join 0 of 35,460 (both compose, so this does not choose the badge operator); NEGATIVE CONTROL kernel `aggregate_status` re-applied to its own output: 12,504 of 25,488 differ, 3,720 with PASS above a non-PASS flat result, first example `[PASS, PASS, FAIL]` split after the first: flat CONFLICT, rolled-up PASS | `rollup` |
| Budgets | of 15 checks: 8 within, 4 over (expected: the overflow rule applies: tests and requirements per changed module, whole table rows, whole-graph nodes), 3 NOT_RUN (change digest, language tree depth, diagnostics: nothing built yet). The check "best-first selection size <= budget" was removed: it is true by construction because the selector stops at the budget. It is replaced by the largest connected component (19 <= 20), which is why the node budget never binds on this repo | `budgets` |

The kernel result is a negative control, not a bug in kernel use: the kernel aggregates a flat receipt list and never re-aggregates its own output; the harness patches `assess_receipt` to identity so that statuses can be fed back as receipts. It shows what a hierarchical roll-up built by re-aggregating statuses would do, and it is why the badge is computed with `fold_b` from counts. NOT_RUN items stay NOT_RUN until the metamodel, rules and store exist.

Tests: `tests/graph/test_human_views.py`, 30 passed: definition consistency and no floats; mapping totality against `metamodel.json` with a negative control; no owner operation in any view, with a negative control; counts laws; badge is `fold_b` from counts and PASS iff every leaf is PASS (all 120 chains), with the join as a negative control; kernel re-aggregation as a negative control (skips as NOT_RUN if the kernel is not importable); priority-then-cap with a negative control; documents byte-equal for two display orders and `definition_digest` covering the cut order; neighbourhood selection equal to an independent DOI oracle and a shortest-distance-versus-expansion-depth case; tiers equal a maximin oracle and are nested and order independent; canonical witness equals brute force; segments; neighbourhood bounded, connected, order independent and preferring a problem node; grid unique cells and order independent; operations and null edits partition a keyed diff; chapters; dependency order topological, deterministic, cycles adjacent; bench output deterministic with no floats, absolute paths or timestamps.

## 9. Determinism and testing of the views

Rules D-01 to D-24 apply (views.md section 10). Specific to views: sentence text is a template id plus args, never generated prose; shares are `n of m`; status counts are integers; the order that decides a badge label or a cut (`chain_worst_first`) is data and is part of `definition_digest`, while the HCI display order is applied only after the cut and never changes a byte; `definition_digest` pins budgets, mappings and that chain; `snapshot.graph_root` pins the snapshot. Permutation harness (D-19) inputs for views: file order, link insertion order, rule order, hash seed, CRLF, non-BMP labels; the expected result is one distinct document per snapshot. The tests above already shuffle link and adjacency order. A golden text rendering per view belongs to the implementing lane.

## 10. Interfaces to other aspects and lanes

Human views reuse the agent tool contract's envelope (`snapshot`, `bounds`, `Finding`, `Step`, `Text`; `graph/schema/mcp-tools.md`) and are computed by the same server-side functions with human budgets. Per-view providers and gaps are in views.md section 12; the summary:

| Interface | Provider to consumer | Shape | If missing or different |
|---|---|---|---|
| View documents | weave to hci | The envelope and payloads of views.md; JCS subset; untrusted prose only inside `Text` | HCI cannot render; nothing else changes |
| Keyed diff with null edits | store and agent-interface aspect to HV-01 | `snapshot_diff` plus file-level digests | Null edits are invisible in the current result; **request**: `null_edits_by_method` |
| Impact with distance | impact aspect (ADR-0097) to HV-02, HV-07 | `tiered_impact -> {node: {tier, distance, witness}}`; `graph_impact.by_soundness`; risk vector (IR-7) as one L0 line | Direct vs transitive not shown; NOT_RUN |
| Witness with origin and soundness per hop | agent-interface aspect (ADR-0099) to HV-07 | `graph_why.witness` is `Step {from, edge, to}`; segments need `origin`, `soundness` | The view builder joins them from the store; **request** to extend `Step` if agents want segments |
| Status algebra | status aspect (`graph/formal/eijaref/status.py`) to views | `fold_b` (chain minimum) for every badge, `fold_a` (join) only for evidence on one claim, `LIFT`, chain (proposal of the allocation's status ADR) | Views refuse to print a badge; counts still print |
| Empty-slot status | status aspect to views | What `fold` returns for a required slot with no links: `eijaref.status` gives NOT_RUN (bottom), the kernel gives UNKNOWN for no receipts, the HCI design expects UNKNOWN for an absent link | Views carry `gap: true` so any reading can be shown; open question 2 |
| Obligations, propagation, layers | metamodel (`graph/schema/metamodel.json`) to views | `signatures[].obligations[]`, `affects`, `soundness`, `layer`, `truth`, `trace`, `ddd_role` | No required slots (`no obligation applies`); the totality test fails and names the type |
| Findings | rules (`graph/schema/rules.md`) to HV-06 | `Finding` with `baseline_state`, witness, fingerprint | HV-06 NOT_RUN |
| Links and ledger | links aspect to HV-03, HV-06 | `link_status`, ledger sequence | SUSPECT and STALE cannot be shown |
| Term registry | language aspect to HV-05 | forms, `ddd_role`, bindings | Only derived workflow nodes; says so |
| Certificate checker | formal aspect (`eijaref/closure.py`) to HV-07 | `check_certificate`, `check_unreachable` | Witness marked unchecked |
| Run report | agent-interface aspect (section 9.5 of its design) | Defined there; follows this file's envelope, budgets, counting laws | Not duplicated |
| OKF | weave to okf lane | The L1 card of a row (a requirement's HV-03 row, a term's HV-05 record) as text inside the generated `facts` or `links` block of that node's page; typed edges stay in the sidecar | Pages stay as they are; no loss |
| Visual | weave to visual lane | HV-08 exports through the visual lane's neutral `Graph` model (Mermaid, DOT) for static pages; HV-02 as the existing `impact` diagram | Static export only |
| Quality | weave to quality lane | Proposed: the tests in a `graph` session tagged `fast`, the bench in `full`; this aspect did not create `quality/sessions/graph.py` because the file is shared across the aspects | Run by hand: `python -m pytest tests/graph/test_human_views.py` |
| Metrics | weave to metrics lane | Counts vectors and the bench numbers as a MEASUREMENT section | Not surfaced |
| HCI study | hci lane to weave | Section 11 protocol; fixtures | Views stay unvalidated |

**Graph technology, in the human context.** A person who wants free-form exploration can load the Cypher or CSV export into Neo4j Browser (GPL-3.0: the server by the LICENSE text opened in `[S]`, the browser repository by GitHub SPDX) or Gephi (GPL-3.0 SPDX): an optional, user-run, non-authoritative surface, outside the trust path and outside our determinism contract (layout determinism of those tools is UNVERIFIED). It is where hairballs are most likely, so it is not one of the views. Rendering libraries for HV-08 (React Flow/xyflow MIT, Cytoscape.js MIT, vis-network Apache-2.0, sigma.js MIT, D3 ISC, Mermaid MIT by SPDX) are the HCI lane's choice; the contract is that they draw the supplied `(rank, slot)` grid. OKF is the reader's projection (per-node text cards, sections above) and the prose surface; it is not a view of relations, because its links are untyped. SARIF (HV-06's export) can be read in the Microsoft SARIF Viewer extension for VS Code (MIT by SPDX) by people who live in an editor. GraphRAG-style narrated summaries are not a source of any view (not checkable, not deterministic); the agents lane may show an AI-labelled summary beside a view.

## 11. Evaluation plan (protocol only; NOT_RUN)

Nothing above shows that these views help a person. To test it, reuse the HCI lane's method (pre-registered hypotheses, seeded items, intervals, stop criteria; `template-hci.md`) with these additions.

| Id | Task on the excursion workflow fixtures | Condition A (views) | Condition B (baseline: `git diff` plus text search) | Measures |
|---|---|---|---|---|
| E1 | List the requirements affected by a seeded change and say which are only over-approximated | HV-01, HV-02 | line diff, grep | correct set, false and missed items, time, UNKNOWN misread as PASS (target 0) |
| E2 | Explain why a seeded SUSPECT link is flagged | HV-06, HV-07 | files and hashes by hand | correct cause, time |
| E3 | Find the requirements with no verifier | HV-03 or HV-04 | matrix CSV plus text search | time, misses |
| E4 | Decide whether a formatting-only edit changes meaning | HV-01 with counter | line diff | correct verdict, confidence calibration |
| E5 | Trace a concept from a term to code, UI and tests | HV-05, HV-08 | grep | time, correct chain |

Pre-registered comparisons, participants (formative 5 to 8; quantitative about 20 or more, per the HCI lane), a keyboard-only cohort, and stop rules (stop if any participant approves with an unread UNKNOWN on a seeded item) come from the HCI protocol. The agent-side evaluation (pass^k with and without graph context) belongs to the agents lane. The budgets of section 4.1 become ratchets (target and limit, like the HCI lane's ADR-0040) only after a first calibration run.

## 12. Risks, open questions, gaps

| Risk or counter-evidence | Evidence | Mitigation |
|---|---|---|
| Budget numbers are guesses | No study fixes 20, 25, 5 or 7 for typed graphs | Marked HYPOTHESIS; recorded basis; calibrated by the HCI lane |
| 20 nodes may be too strict for node-link on sparse graphs | H2: workable at 258 to 332 sparse nodes with interaction | Expand step to 50; hard stop 100; revisit after calibration |
| An outline may not beat the baseline | H4: no display significantly beat Explorer | Outline is chosen for compositional counts and low cost, not for speed; the study measures it |
| Outlines hide non-hierarchical links | Structure of the form | Inspector cards, HV-02, HV-08 show cross-links |
| Counts everywhere may overwhelm | HCI risk list (alarm fatigue, UNVERIFIED) | Chunks limited to 4 at L0; study measures |
| One witness is a biased selection | H25 | `n_paths`, `path_rank`, scope shown |
| The null-edit counter can hide a meaningful edit | `[trace]` section 2 (false fresh) | Counter names the method and reveals on request |
| Cold start: no declared links, so tier 0 is empty | Measured (tier 0 reach 0) | Every empty tier states the scope searched; completeness views (HV-04) show the missing links first |
| Sizes here are tiny (23 modules) | Measured | Section 4.6 growth is PREDICTION; re-run the bench as the graph grows |
| The metamodel is moving | 42 types now vs 37 in the brief | Totality test fails loudly and names the type |

**Open questions.**
1. **Which order is "worst first"?** The data chain `chain_worst_first` (badge label and cap rank) is the weave chain FAIL, CONFLICT, STALE, NOT_RUN, UNKNOWN, PASS, a proposal equal to `eijaref.status` `DEFAULT_CHAIN`. The HCI lane proposes CONFLICT, FAIL, STALE, UNKNOWN, NOT_RUN, PASS for display. The HCI order may reorder rows after the cut; it may not choose the cut or the badge label. One owner decision (the status ADR) should fix the chain; that a badge is PASS only if all items are PASS does not depend on it.
2. **What is the status of a required slot with no link?** `eijaref.status` (empty join = NOT_RUN), the kernel (no receipts = UNKNOWN) and the HCI design (absent link = UNKNOWN) differ. Recommendation: UNKNOWN for "no evidence exists", NOT_RUN for "a check exists and its prerequisite was absent". This needs the status ADR; views carry `gap` meanwhile.
3. **ADR number.** The assigned file name was `00101-...` (five digits). At integration it was renumbered to 0105, the slot the allocation table gives to view lenses and views; the register row, this document, views.md and the ADR links were updated. RESOLVED.
4. **Grouping key for the trace matrix.** In this repo 17 of 22 `area` values are singletons. Group by lane or context from `contains` once a registry exists, or leave rows ungrouped.
5. **Chapters.** Is the deterministic rule (layer, truth class, `derived_from`) what a reviewer expects as "core, consequences, glue"? The study can compare with reviewers' own grouping.
6. **Treemap.** Worth a study arm against the outline for HV-04? Evidence is mixed (H4, H17).

**Gaps and UNVERIFIED.** Full texts not read: Ghoniem et al., Keller et al., Cockburn et al. (abstract only), Ko and Myers papers, Sillito et al., LaToza and Myers, Weiser, Storey (no abstract available), Brooks. Whyline numbers are the authors' reports on their own tools. Kobsa's participants were students familiar with Explorer. Wettel's baseline was Eclipse plus Excel. The ProofMap counts are regex counts. Neo4j Browser and Gephi layout determinism, Neo4j Bloom's licence and the wording of the SARIF viewer's features are UNVERIFIED. The sibling interfaces track the state of their files at the time of writing. POSIX byte identity of the bench is NOT_RUN. Human benefit is UNMEASURED.

## 13. Sources

All opened on 2026-09-29. "Full" = full text read; "abstract" = abstract read through the OpenAlex API (`api.openalex.org/works/doi:<doi>`) or the publisher DOI record.

| Key | Source | Access |
|---|---|---|
| H1 | Ghoniem, Fekete, Castagliola. On the readability of graphs using node-link and matrix-based representations. Information Visualization 4(2), 2005. https://doi.org/10.1057/palgrave.ivs.9500092 | abstract |
| H2 | Okoe, Jianu, Kobourov. Node-link or adjacency matrices: old question, new insights. IEEE TVCG 2019. https://doi.org/10.1109/TVCG.2018.2865940 ; text: https://openaccess.city.ac.uk/id/eprint/20159/ | full (submitted version) |
| H3 | Keller, Eckert, Clarkson. Matrices or node-link diagrams. Information Visualization 5(1), 2006. https://doi.org/10.1057/palgrave.ivs.9500116 | abstract |
| H4 | Kobsa. User experiments with tree visualization systems. InfoVis 2004. https://www.ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf | full |
| H5 | Shneiderman. The eyes have it. IEEE Symposium on Visual Languages 1996. https://doi.org/10.1109/VL.1996.545307 ; text: https://drum.lib.umd.edu/ (report CS-TR-3665) | full |
| H6 | Larkin, Simon. Why a diagram is (sometimes) worth ten thousand words. Cognitive Science 1987. https://doi.org/10.1111/j.1551-6708.1987.tb00863.x | abstract |
| H7 | Ware, Purchase, Colpoys, McGill. Cognitive measurements of graph aesthetics. Information Visualization 2002. https://doi.org/10.1057/palgrave.ivs.9500013 | abstract |
| H8 | Furnas. Generalized fisheye views. ACM SIGCHI Bulletin 1986. https://doi.org/10.1145/22339.22342 | abstract |
| H9 | van Ham, Perer. "Search, show context, expand on demand". IEEE TVCG 2009. https://doi.org/10.1109/TVCG.2009.108 | abstract |
| H10 | Elmqvist, Fekete. Hierarchical aggregation for information visualization. IEEE TVCG (OpenAlex year 2009). https://doi.org/10.1109/TVCG.2009.84 | abstract |
| H11 | Henry, Fekete, McGuffin. NodeTrix: a hybrid visualization of social networks. IEEE TVCG 2007. https://doi.org/10.1109/TVCG.2007.70582 | abstract |
| H12 | Holten. Hierarchical edge bundles. IEEE TVCG 2006. https://doi.org/10.1109/TVCG.2006.147 | abstract |
| H13 | Cockburn, Karlson, Bederson. A review of overview+detail, zooming, and focus+context interfaces. ACM Computing Surveys 2009. https://doi.org/10.1145/1456650.1456652 | abstract |
| H14 | Behrisch et al. Matrix reordering methods for table and network visualization. Computer Graphics Forum 2016. https://doi.org/10.1111/cgf.12935 | abstract |
| H15 | Lee, Plaisant, Parr, Fekete, Henry. Task taxonomy for graph visualization. BELIV 2006. https://doi.org/10.1145/1168149.1168168 | abstract |
| H16 | Amar, Eagan, Stasko. Low-level components of analytic activity in information visualization. InfoVis 2005. https://doi.org/10.1109/INFOVIS.2005.24 | abstract |
| H17 | Wettel, Lanza, Robbes. Software systems as cities: a controlled experiment. ICSE 2011. https://doi.org/10.1145/1985793.1985868 | first sentences of the abstract only (audit, 2026-09-29); figures UNVERIFIED |
| H18 | Ko, Myers, Coblenz, Aung. An exploratory study of how developers seek, relate, and collect relevant information during software maintenance tasks. IEEE TSE 2006. https://doi.org/10.1109/TSE.2006.116 | abstract |
| H19 | Sillito, Murphy, De Volder. Questions programmers ask during software evolution tasks. FSE 2006. https://doi.org/10.1145/1181775.1181779 | abstract |
| H20 | LaToza, Myers. Hard-to-answer questions about code. PLATEAU 2010. https://doi.org/10.1145/1937117.1937125 | abstract |
| H21 | Ko, Myers. Designing the Whyline. CHI 2004. https://doi.org/10.1145/985692.985712 | abstract |
| H22 | Ko, Myers. Debugging reinvented. ICSE 2008. https://doi.org/10.1145/1368088.1368130 | abstract |
| H23 | Ko, Myers. Finding causes of program output with the Java Whyline. CHI 2009. https://doi.org/10.1145/1518701.1518942 | abstract |
| H24 | Weiser. Programmers use slices when debugging. CACM 1982. https://doi.org/10.1145/358557.358577 | abstract |
| H25 | Miller. Explanation in artificial intelligence: insights from the social sciences. Artificial Intelligence 2019. https://arxiv.org/abs/1706.07269 | full (section 1.2, four findings) |
| H26 | Sadowski, Soederberg, Church, Sipko, Bacchelli. Modern code review: a case study at Google. ICSE-SEIP 2018. https://doi.org/10.1145/3183519.3183525 ; text: https://sback.it/publications/icse2018seip.pdf | full |
| H27 | Johnson, Song, Murphy-Hill, Bowdidge. Why don't software developers use static analysis tools to find bugs? ICSE 2013. https://doi.org/10.1109/ICSE.2013.6606613 | abstract |
| H28 | Cuddeback, Dekhtyar, Hayes. Automated requirements traceability: the study of human analysts. RE 2010. https://doi.org/10.1109/RE.2010.35 | abstract |
| H29 | Cowan, 2010: working-memory storage capacity limited to 3 to 5 meaningful items in young adults (PMC article PMC2864034; the fetch returned the abstract, not the title or venue). https://pmc.ncbi.nlm.nih.gov/articles/PMC2864034/ | abstract |
| H30 | Nielsen Norman Group. Progressive disclosure. 2006-12-03. https://www.nngroup.com/articles/progressive-disclosure/ | page (states no cited evidence for the two-level rule) |
| H31 | 45ck/proofmap-lite `docs/gap-audit.md` and `README.md` (private repository, read with the owner's `gh` login); regex counts computed here (audit recount: 40 rows) | file |
| H32 | GitHub REST metadata (`license.spdx_id`, `archived`, `pushed_at`) for cytoscape/cytoscape.js, xyflow/xyflow, mermaid-js/mermaid, d3/d3, gephi/gephi, visjs/vis-network, jacomyal/sigma.js, neo4j/neo4j-browser, microsoft/sarif-vscode-extension | API |
| H33 | von Mayrhauser, Vans. Program comprehension during software maintenance and evolution. IEEE Computer 1995. https://doi.org/10.1109/2.402076 | abstract |

Internal sources: `docs/weave/research/*.md` (12 dossiers), `docs/weave/ARCHITECTURE.md`, `graph/brief.json`, `graph/schema/metamodel.json`, `graph/bench/impact_math_reference.py`, `graph/formal/eijaref/status.py`, the HCI lane files under `/c/Dev/eija-wt/ux/docs/hci/` (`research/PRINCIPLES.md`, `personas-and-jtbd.md`, `design/language-and-ddd-tree.md`, `research/review-diff-and-assurance-uis.md`, `design/brief.json`, `docs/adr/template-hci.md`), the okf lane `docs/knowledge-base.md`, the visual lane `docs/visual.md`, the agents lane `docs/agents/contract.md`, `src/eija_studio/domain/impact.py`, `src/eija_studio/domain/evidence.py`.
