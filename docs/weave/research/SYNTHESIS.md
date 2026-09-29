# Weave synthesis: one deterministic, typed, checkable graph over everything

Lane: weave. Date: 2026-09-29. Status: research synthesis feeding ADR block 0089-0112. It is not a decision record. Evidence labels: MEASUREMENT (a script ran, numbers are real, domain stated), PREDICTION (reasoned, not run), DESIGN (a proposal of this lane), UNVERIFIED (not opened or not confirmable; nothing is built on it).

Source keys used below. Dossiers (all in this folder): [mde] mde-metamodels-and-standards, [bx] multi-view-consistency-and-bx, [trace] traceability-and-requirements-graphs, [code] code-intelligence-and-analysis, [gdb] graph-databases-and-knowledge-graphs, [math] math-and-cs-foundations, [assure] assurance-and-proof-linking, [incr] incremental-builds-and-diagnostics, [agent] agent-reliability-and-context, [lang] ubiquitous-language-ontology-and-dsls, [ui] ui-to-model-linking, [thesis] 00-PRODUCT-THESIS. Sources I opened myself this session (2026-09-29): [V1] OKF v0.2 SPEC (`GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md`), [V2] RFC 8785 (rfc-editor.org), [V3] GitHub REST metadata and LICENSE heads for 22 repositories (`gh api repos/<r>`), [V4] PyPI JSON for rfc8785, networkx, libcst, rustworkx, jsonschema, markdown-it-py, [V5] the sibling lanes' files under `/c/Dev/eija-wt/*`, [V6] a re-run of `tests/graph` and `graph/bench/foundations_checks.py` in this worktree (5 passed, 1 skipped as NOT_RUN because `rfc8785` is not installed).

The dossier authors reported that the WebSearch budget was exhausted before they started, and it was still exhausted when I tried (200 of 200). So every "no tool does X" claim below means "not found with the means available", never "does not exist".

## 0. Decisions first

| # | Decision | Confidence | Basis |
|---|---|---|---|
| 1 | The graph is a **derived, rebuildable index of git-tracked sources**, never a source of truth. Declared links are authoritative, derived links are recomputed, inferred links are proposals that cannot satisfy a gate. | High | [gdb] section 2, [ui] GAP-024, ProofMap gaps GAP-002/003/033 |
| 2 | **No graph database in the trust path.** Store = canonical typed facts, SQLite (stdlib) as a disposable query index. Neo4j and other graph DBs are optional export targets only. | High for scale (MEASUREMENT: 10^6-edge closure in 0.85 s pure Python, 1.3 s SQLite), High for licence | [gdb] section 2, [V3] |
| 3 | **OKF v0.2 is the human/agent-readable projection and the authoring surface for declared prose links, not the graph.** Its links are untyped, broken links must be tolerated, staleness is wall-clock. EIJA adds a strict profile: typed edges, broken link = error, hash-based freshness, timestamps excluded from identity. | High | [V1], [gdb], [trace] 3.3 |
| 4 | **The compiler is a set of named violation rules over typed relations.** Zero rows means pass. Every finding carries a stable id, a deterministic witness, and exports to SARIF 2.1.0. A missing prerequisite is NOT_RUN and absorbs PASS. | High | [gdb] D6, [math] D2/D6, [incr] |
| 5 | **Links are anchored to method-versioned digests of normalised target slices, chosen per link kind by measurement.** A changed digest means SUSPECT, never "false". Only a human ledger entry clears it. | High | [trace] section 4 (MEASUREMENT on 2 repos) |
| 6 | **Adopt the mathematics that changes a concrete number or removes a concrete failure**: least fixed points (already in the kernel), SCC condensation with a canonical relabelling, lexicographic topological order, stratified rules, content-addressed Merkle roots, early cutoff, keyed diff, greedy set cover, JCS. Everything else is theory-only with at most one adopted check. | High | section 3 |
| 7 | **Custom code is limited to the EIJA-specific glue**: fact schema and canonical writer, link status function, rule runner and Finding model, SARIF profile writer, determinism harness, link certificates (`assess_link`), UI sidecar checker, term registry checker. Everything else is an adapter over an existing tool. | High | section 2 |
| 8 | **A model proof is never a code proof.** Each link kind states its trusted computing base and label (PROVED_IN_MODEL, CHECKED_BOUNDED, CONFORMS_BOUNDED, TESTED, GENERATED, DECIDED). Statements are pinned by owner-approved digest. | High | [assure] |
| 9 | **The graph does not make abstractions correct and no benefit to agents or humans is claimed until measured.** Agent and human effects are UNMEASURED; the eval design uses pass^k and pre-registered tasks. | High that the gap is real | [agent] section 5, [thesis] |
| 10 | **Two extractors first, the rest by trigger.** Phase 1 uses stdlib `ast`, `json`, `html.parser` plus the okf lane's already-pinned `markdown-it-py`; tree-sitter, LibCST and SCIP indexers arrive when a TS/JS/CSS surface or a rename codemod needs them. | Medium | section 2, [code] M4 (167 of 167 definitions agree between `ast` and tree-sitter) |

## 1. The owner's question: graphs, Neo4j, OKF, and what we use them for

"Graph" names three separate things in this design. Keeping them apart is most of the answer.

| Role | What it is | Technology chosen | What is not chosen, and why | Source |
|---|---|---|---|---|
| A. Data model | Typed nodes and typed, hash-anchored edges over code, UI, diagrams, language, requirements, tests, proofs, evidence, ADRs, personas | Canonical JSON facts (RFC 8785 subset), many-sorted edge signatures in JSON Schema | Neo4j property graph, RDF/OWL: open-world or server semantics add nothing to a closed, curated, checked model | [math] 2.9, [lang] 2.3 |
| B. Query and check engine | Reachability, impact, violation queries, witnesses | SQLite recursive CTE with `UNION`, reference semantics = `impact.closure` | Neo4j (GPL-3.0 server, JVM, row order undefined without ORDER BY), Memgraph (BSL), FalkorDB (SSPL), Kuzu (archived), TypeDB (server) | [gdb] 3.1; [V3] Neo4j `LICENSE.txt` head read: "GNU GENERAL PUBLIC LICENSE Version 3" |
| C. Knowledge surface | Files a person or agent reads, links, and edits | OKF v0.2 bundle at `okf/` (okf lane), generated pages plus human notes | A wiki that is edited as truth; GraphRAG summaries (LLM-extracted, not evidence) | [V1], [gdb] 3.7 |

**How Neo4j fits.** It is an export target: one-way Cypher/CSV projection for a person who wants ad-hoc exploration in the Neo4j browser, run by that person as a separate process. Reasons: (1) GPL-3.0 server; an Apache-2.0 package must not bundle or link it (licence text opened, [V3]); (2) a second stateful store outside git can drift from git, the failure class ProofMap Lite recorded (GAP-002, 003, 025, 033); (3) no speed gain at our scale (MEASUREMENT [gdb]: SQLite closure 88 ms at 10^5 edges, 1.3 s at 10^6, dominated by nothing an engine fixes); (4) determinism: Cypher row order is undefined without `ORDER BY`. Its useful ideas (typed patterns, GQL/SQL-PGQ vocabulary) come free from our violation-query files. Revisit triggers, all measurable: index above about 10^7 edges; rebuild over an agreed budget; needs beyond joins and recursion (weighted paths, community detection) that a library cannot cover [gdb] section 5.10.

**How OKF fits.**
- *Projection.* Every concept (term, module, symbol, ADR, requirement, gate, lane) has a generated OKF page with `resource: repo://path#fragment` and `sources[].sha256` + `hash_method`; the okf lane owns generation and the STALE gate (ADR-0045/0046 in the okf worktree, [V5]).
- *Authoring of declared links.* Prose links between pages are declared links, but OKF says "The specific kind ... is conveyed by the surrounding prose, not by the link itself" and "Consumers MUST tolerate broken links" ([V1], read verbatim). So typed edges cannot live in OKF prose. They live in a sidecar declared-link file under `graph/` (weave), and OKF pages get a generated `links` block derived from it.
- *Freshness.* OKF `stale_after` is "An absolute instant. A concept is stale when `now >= stale_after`" and no hash field exists ([V1]). Time-based staleness reads the wall clock, which the determinism doctrine bans from verdicts. We decide freshness by digest; if `stale_after` is ever used, `now` is an explicit recorded input.
- *Strict profile.* The okf lane already made broken links a defect for its own bundle (ADR-0045). Weave generalises: typed edges, broken link = error, `generated.at`, `verified.at`, `stale_after` excluded from identity hashes.
- *Attested computation.* OKF's deterministic no-LLM attester is the natural slot for `assess_link` ([assure] section 3).

**What we use graphs for, concretely** (each is a rule or a projection, none is a dashboard): impact of a change with a witness path; SUSPECT link lists after a code change; uncovered requirements and unlinked symbols; language drift (term in code, UI, diagram, test, doc); layer and architecture reflexion (intended vs actual); view totality (every semantic type is drawn or explicitly not shown); enabled-set equality between UI and kernel guards; proof-statement pinning and assumption ledgers; bounded agent context and proposal validation.

## 2. Adopt-versus-build matrix

Rule: ADR-0016. "Adopt" means a dependency in extra `graph` (pinned `==`) or stdlib. "Process" means a separate optional process whose output is data and whose absence is NOT_RUN. "Export" means one-way generated projection with a golden test. Licence roles are in section 8.

| Capability | Adopt (dependency) | Optional process / export | Build (custom, justified) | Why custom | Source |
|---|---|---|---|---|---|
| Extraction, Python | stdlib `ast`, `symtable`; okf `codelink` normalisers | LibCST (qualified names, codemods) when a rename map is needed; scip-python (heavy, licence partly UNVERIFIED) | `Extractor` protocol returning sorted typed facts with provenance label (`exact`, `syntactic`, `candidate(n)`, `tool-resolved`, `unresolved`) | No tool emits EIJA fact schema; sorted, labelled output must be ours | [code] 2, 5 |
| Extraction, JS/TS/CSS/HTML/MD/JSON | stdlib `json`, `html.parser`; `markdown-it-py` (okf pin) now; tree-sitter and six grammars in phase 2 | scip-typescript (Node 22/24), ast-grep (structural rules), ruff `analyze graph` (normalise backslash paths) | Same protocol; identity grammar; partial-parse flag (`has_error` means partial, never PASS) | tree-sitter grammar ABIs differ (14 vs 15), CRLF changes byte ranges (MEASUREMENT) | [code] M1, M2, M5 |
| Identity | okf `repo://path#fragment` grammar and hash methods (`ast-v1`, `ast-sig-v1`, `ast-api-v1`, `lf-sha256-v1`, `csv-row-v1`, `md-bold-term-v1`, `md-table-row-v1`) | SWHID alias for file snapshots (about ten lines, do not depend on GPL `swh-model`); UUIDv5 for exported ids (RFC 9562) | Fragment-grammar registry per node type; rename map (old id, new id); domain-separated node hash | okf owns hashing; weave owns the registry of which method a link kind uses | [trace] 3.4, [mde] D7, ADR-0046 |
| Canonical serialisation | `rfc8785==0.1.4` (Apache-2.0) or an own writer validated against RFC vectors | RFC 6902 only for export diffs | Restricted payload subset (strings, safe integers, booleans, null) and conformance test; never compare with kernel `fingerprint()` | Kernel `canonical()` is not JCS for floats and astral key order (MEASUREMENT); kernel change needs its own ADR | [math] C1, [V2] |
| Storage | stdlib `sqlite3` | Dolt for a cross-run evidence ledger if the owner wants it (Apache-2.0, owner already runs it); DuckDB for analytics later | Node/edge tables, total ORDER BY on every query, root Merkle hash, manifest | Store must be disposable and byte-comparable | [gdb] D2 |
| Query | SQLite `WITH RECURSIVE ... UNION`; `impact.closure` as reference | Soufflé (UPL-1.0) export of `.facts` for Linux/WSL users | Named parameterised queries: `node`, `neighbors`, `impact`, `why`, `violations`, `context(budget)` | Agents get bounded typed answers, not free-form Cypher (Text2Cypher errs) | [gdb] D7, [agent] |
| Constraints and rules | jsonschema (edge signatures, sidecar schemas) | pySHACL as optional cross-check of an exported SKOS graph | Rule loader with stratification check; one file per rule; witness derivation | No tool implements per-context bijection with declared bindings and witnesses | [math] D2, [lang] 5 |
| Diagnostics | ruff, import-linter, mypy (existing quality lane); `jsonschema` to validate SARIF | reviewdog (rdjson), sarif-sdk (.NET validator), GitHub code scanning via REST only (Actions unavailable, owner decision) | `Finding` model, SARIF 2.1.0 profile writer (sorted, no GUID/time/abs path, `columnKind`), suppression ledger, permutation harness | `sarif-om` stale since 2019; determinism profile is ours | [incr] 2.3, 5 |
| Codemods | LibCST (Python), byte-range edits (Markdown, YAML, OKF) | ast-grep `fix` (JS/TS/CSS/HTML) | Fix proposal record `{edits, applicability, precondition_sha256}`; rename map emission | Kernel path never applies edits (agents and providers never apply) | [incr] 2.6, [code] 6.7 |
| Views | `rfc8785`; SysML v2 text as first export; Mermaid/PlantUML/DOT already emitted by visual lane | LikeC4 or Structurizr (decided by byte-equality test), sysml-toolkit or Pilot as optional validator, draw.io as import/export surface only | Lens law suite (GetPut, PutGet mod layout, conditional PutPut), edit translator protocol, mapping totality check, one SysML emitter | No compatible-licence Python lens library (PyPI `lenses` GPLv3+, Boomerang stale LGPL) | [bx] 3, [mde] 2.2 |
| Agents | MCP Python SDK (agents lane, `mcp==2.2.0`) | Outlines, XGrammar, llguidance as inspiration only | Query set definition, per-session JSON Schema with `enum` of live node ids, hash-keyed transcript record/replay, pass^k harness | Providers are CLI agents, so decoding cannot be embedded; validate on receipt | [agent] 2.4, 6 |
| Formal | Existing lanes' pinned tools (TLC via `TOOLS.lock`, Bend, Z3) | Lean `leanchecker`, cvc5 Alethe + Carcara, Dafny audit as second checkers, gsn2x for GSN | `assess_link`, checker registry, statement pinning, assumption ledger diff, negative-control requirement | Mirrors `assess_receipt`; each lane emits witnesses, weave supplies schema and fold | [assure] 7 |
| Traceability | (none as source of truth) | OpenFastTrace (GPL-3.0, separate JVM process, report imported as evidence), StrictDoc/ReqIF export | Link record, pure `link_status` function using OFT names, ledgered `ack`, completeness gate | No surveyed tool has a content-digest link with a code normaliser plus a ledger | [trace] 3, 7 |
| Language | `ast`, `markdown-it-py` | Contextive, Vale, cspell, SKOS Turtle, Context Mapper CML as generated exports | Term registry schema, splitter, bijection checker | No tool implements per-context bijection with bindings | [lang] 5 |
| UI | Playwright (hci pin), axe (hci lane), DTCG token format | oasdiff, Spectral, Style Dictionary (deferred), Storybook (deferred) | Sidecar UI model schema, `data-eija-key` contract, UIL-001..008 | Vanilla 49-line UI, no component model | [ui] 6 |

## 3. Schools of thought: mechanism, benefit, cost, verdict

Only rows with an implementable benefit. Benefit column names the number or failure it changes. "Theory-only" rows keep at most one adopted check.

| School | Mechanism (concrete) | Benefit and evidence | Cost and limit | Verdict | Source |
|---|---|---|---|---|---|
| Order theory, fixed points | Impact = least fixed point of `X -> roots U succ(X)` on the powerset of a finite node set; one worklist solver reused for closure, dominators, rule strata | Result independent of visit order; terminates on cycles. MEASUREMENT: closure equals `nx.descendants` and SQLite CTE on 300 random graphs, 0 mismatches, reproduced [V6] | Only monotone rules; "no test covers X" is negation and needs stratification | adopt | [math] 2.2, [gdb] 4 |
| Order theory, lattices | `StatusLattice`: join for evidence on one claim; chain minimum for conjunction across claims | MEASUREMENT: kernel `aggregate_status` is order-independent but not associative; hierarchical counterexample flat CONFLICT vs rolled-up FAIL; lattice join equals kernel on all flat inputs up to length 6 (reproduced [V6]) | Kernel fix needs its own ADR; this lane implements and tests agreement only | adopt (in `graph/`) | [math] 2.2 |
| Order theory, Galois/soundness | Edge soundness class `must`, `may`, `heuristic`; impact reports reach through sound edges apart from reach that needs heuristic edges | Honest over-approximation; a miss traces to a heuristic edge (seeded fault injection test) | Extractors must declare a class | adapt | [math] 2.2 |
| Graph theory | SCC condensation relabelled by minimum member; lexicographically smallest topological order; dominators; transitive reduction on the condensation | MEASUREMENT: `nx.condensation` labels took 24 forms over 200 insertion orders, `graphlib` 5, sorted-SCC tuples and lexicographic topo sort 1 (reproduced [V6]). Redundant-link lint, single-point-of-evidence lint | Own ~100 lines of stdlib Tarjan and Kahn avoids a dependency; networkx stays a test oracle | adopt | [math] 2.1 |
| Graph theory | Personalised PageRank for `context(budget)` | MEASUREMENT: raw float hashes differed in 40 of 40 shuffled insertions; rounding at 1e-10 gave one result on that 300-node sample (a sample, not a proof). Design: fixed-iteration `Fraction`/integer power iteration | Relevance is a heuristic and labelled so; effect on agent success is unmeasured (RepoGraph +2 to +2.7 pp on SWE-bench Lite, Python, GPT-4 series) | adapt, advisory | [math] 2.1, [agent] 2.2 |
| Graph theory | Vertex min-cut, betweenness | Evidence redundancy `k`; hub metric | Flow per requirement; min cuts are not unique so canonicalise | adapt, report only | [math] 2.1 |
| Relational algebra, Datalog | Rules as named queries over relations; stratified negation; recursion via `UNION` CTE; loader rejects negation inside a recursive stratum | Declarative, diffable, order-independent; each violation row has a stable id and witness. Datalog terminates and is polynomial in data size (Wikipedia-level source, [math]) | No Datalog engine in the default path; revisit above about 30 rules or when negation-through-recursion is needed | adopt (lite), engine theory-only | [gdb] 4, [math] 2.3, [agent] 4 |
| Provenance | One canonical minimal derivation (lexicographically first shortest path) per derived fact; rule id and premise ids stored | "Why is this affected/covered/red" is a lookup and re-checkable. Provenance semiring theory (Green, Karvounarakis, Tannen, PODS 2007) applies to the positive fragment only, per the text [math] extracted | Missing-evidence findings have no semiring explanation; their witness is the searched scope. Full polynomials theory-only | adapt | [math] 2.3, [trace] 6 |
| Content-addressed Merkle | Node hash = H(domain tag, kind, JCS fields, sorted child hashes); one root per view; SCCs hashed as a unit | Freshness is a hash comparison; a leaf change changes exactly its ancestors; rebuild-twice root comparison is the determinism gate | Detects change, not truth; encoding must be exact and length-safe (Doorstop's digest concatenates fields without a separator, MEASURED collision for two inputs) | adopt | [math] 2.6, [trace] 3.2 |
| Canonical forms | Normalise before hashing (AST without positions, LF fold); version the method | MEASUREMENT on Doorstop and StrictDoc history: raw bytes stale on 99.9 to 100% of file-touching commits, whole-file AST 88.7 to 98.3%, symbol AST 7.4 to 9.4%, signature only 1.5 to 1.8% | Two Python repos; sensitivity, not ground truth; the normaliser can hide a change that mattered | adopt | [trace] 4 |
| Canonical serialisation | RFC 8785 subset for graph artefacts; no floats | Byte-identical across platforms and languages. MEASUREMENT: kernel `canonical()` differs on `1.0`, `-0.0`, integers above 2^53 and astral-vs-BMP key order | `rfc8785` 0.1.4 (Apache-2.0, requires Python >= 3.8 [V4]) is a small dependency or an own writer with RFC vectors | adopt | [math] C1, [V2] |
| Incremental computation | Verifying-trace rebuilder: key = SHA-256(rule fingerprint, sorted input hashes); early cutoff when an output hash is unchanged | Comment-only edits stop at the first hop; correctness oracle is "incremental equals clean" (Build Systems a la Carte, Definition 3.1, read directly) | An undeclared input yields stale-but-trusted output; cache off by default until `graph/bench` shows a gain (repo is small, gain may be seconds: PREDICTION) | adapt | [incr] 4, [trace] 6 |
| Incremental computation | Z-set diff of findings (new +1, absent -1) for baselines | Deterministic new/unchanged/absent classification (SARIF `baselineState`) | DBSP joins not needed | adapt | [incr] 2.1 |
| Type theory | Many-sorted edge signatures `(source type, edge type, target type)`; closed sum types for verdicts; NewType ids under mypy strict | Ill-typed link fails at build; `NOT_RUN` is not a `bool` | Signature upkeep; refinement types theory-only | adapt | [math] 2.9, [mde] 5 |
| Bidirectional transformations | Views as asymmetric lenses: `get` pure projection, canvas edit translated to `Accepted(...)` or typed `Rejected(code, reason)`, `apply_transaction` the only `put` | MEASUREMENT (exhaustive, 3 transactions x 2 bases): `enable` idempotent; `set` before `enable` refused with `MEANING_REQUIRED`; order matters, so translator orders by dependency | Laws hold only modulo definedness; a complement holds layout | adapt as tests, no library | [bx] 3.8, 4 |
| Bidirectional transformations | Generated exports are get-only lenses; hand edits to generated views are rejected, not merged | Removes round-trip conflicts (ProofMap GAP-010, GAP-030) | None | adopt | [lang] 4, [bx] 2.8 |
| Term and graph rewriting | LibCST codemods as the only write-back; rename emits (old, new); confluence test for normalisers (100 random orders give one normal form) | Deterministic reviewable refactors; ids survive by explicit map; a change that removes an id without a map entry is a lint error | Syntactic renames only; DPO rewriting and critical-pair tools theory-only | adopt | [code] 6, [math] 2.4 |
| Combinatorial optimisation | Greedy set cover over impacted obligations, ties by (cost, id) | Smallest fast-tier test set that covers impacted obligations; within H(n) of optimum on small instances | "Covers" is by declared link, not fault detection (mutation lane calibrates) | adopt | [math] 2.8 |
| Certifying computation | Link certificate = witness + pinned statement digest + assumption ledger; a small checker recomputes acceptance | Untrusted producers, small trusted checker; TCB stated per link kind. LEDA: matching module 280 LoC, checker 26 LoC (reported by the source) | One checker per kind; checker must be simple | adopt (pattern), DESIGN (schema) | [assure] 2 |
| Refinement, trace validation | Abstraction map alpha; per-step comparison; TLC trace validation | Conformance link with printed bounds; the tla lane already does it | Safety only; bounded; incomplete traces accepted (source warns) | adapt | [assure] 3 |
| Test-suite analysis | Mutation score and property tests attached to link kinds | Fault-detection calibration of `covers` edges | Fault model stated | adopt via lanes | [math] 5.7 |
| CRDT-style merge | Content-addressed grow-only evidence set merged by union | Multi-agent, multi-worktree merges never conflict; contradictions surface as CONFLICT | Semantic conflicts remain; no library | adapt (idea only) | [math] 2.8 |
| Information theory, MDL | Compressed size of canonical model vs generated pages | Redundancy trend only | Says nothing about truth | theory-only | [math], [incr] |
| Category theory | Two checks only: mapping totality (every semantic type is drawn or `not_shown`) and view-as-homomorphism (a model path maps to a view path) | New semantic types cannot silently vanish from views | Functorial migration, CQL, institutions, pushouts: no implementable benefit found | theory-only + 2 adopted tests | [bx] 4, [math] 2.9 |
| Sheaf-style consistency | Overlap join: views sharing ids must agree on shared facts; disagreement is a located finding | Pinpoints which two views disagree on which id | Cohomology adds nothing for discrete typed records | adapt (join), rest theory-only | [bx] 2.7 |
| Probabilistic assurance | pass^k over n recorded trials for agents; plain ratios for coverage | Exposes agent inconsistency: pass^8 below 25% for a >60% pass@1 agent (tau-bench, GPT-4o retail) | Conservative Bayesian and subjective-logic hypotheses do not hold for agent-written tests; no confidence percentages in gates | adopt pass^k; rest theory-only, PREDICTION label | [agent] 2.7, [math] 2.9 |
| Structural diff | Keyed diff (set difference plus per-node semantic hash), O(n) with stable ids; GumTree only for id-less artefacts | Exact semantic diff for review packets | GumTree is LGPL-3.0 and Java (process only) | adapt | [math] 2.5 |
| Formal languages | Longest-match tokenisation of names over a sorted term-form table; regular, linear time | Deterministic term extraction from identifiers, labels, prose; unsplittable names report UNKNOWN, never a guess | Same-case identifiers need a dictionary | adopt | [lang] 4 |
| Formal terminology | Per-context name/concept relation must be a bijection on preferred names (Deissenboeck and Pizka): homonym = one name, two concepts; synonym = two preferred names, one concept | Two exact set checks with counts H and S; no NLP. MEASUREMENT: only 3 of 10 glossary terms appear as contiguous identifier words in `src/`, so bindings must be declared, not inferred | Curation; accepted-form escape hatch | adopt | [lang] 2.2, 3 |
| Treewidth, DPO tools, FCA, CQL, Hets | none implementable here | none | Heavy or non-OSS | theory-only | [math], [bx] |

## 4. Quantities we can compute, and their labels

| Quantity | Formula or mechanism | Label | Not to be read as |
|---|---|---|---|
| Link coverage per requirement, symbol coverage per requirement | `linked / total`, plain ratio | MEASUREMENT of the graph | Test adequacy |
| Stale-link rate by hash method | share of links whose digest no longer matches after H commits | MEASUREMENT (re-runnable: `graph/bench/traceability_staleness.py`) | "Link is false" |
| Impact size, frontier | `closure(...)` with `complete`, `frontier` | MEASUREMENT of encoded edges | Every real-world consequence (the kernel says so in `envelope`) |
| Evidence redundancy `k` | minimum vertex cut between a requirement and its evidence | MEASUREMENT | Fault tolerance |
| Single points of evidence | dominators on requirement-to-evidence paths | MEASUREMENT | Risk score |
| Homonym count H, synonym count S | per-context bijection violations | MEASUREMENT | Naming quality |
| Enabled-set difference | symmetric difference of UI-enabled controls and kernel-allowed transitions per (state, actor) | MEASUREMENT over the enumerated pairs | UI correctness |
| Cover size | greedy set cover of impacted obligations | MEASUREMENT | Fault detection |
| Determinism distinct-output counts | outputs over N permutations (must be 1) | MEASUREMENT | Determinism for all inputs |
| Agent reliability | `pass^k = E[C(c,k)/C(n,k)]`, report n, c, model id, CLI version, date | MEASUREMENT with n stated | Anything extrapolated (PREDICTION) |
| Any confidence percentage, "risk" or "trust" score | none | not computed | do not ship |

## 5. Contradictions between sources and how they are resolved

| # | Contradiction | Resolution | Confidence |
|---|---|---|---|
| R1 | [math] stores typed edges as committed sorted JSONL under `graph/`; [gdb] says the graph is derived and only a manifest is committed | Two classes. Declared links (`graph/links/*.jsonl`, sorted, JCS) are authored source and committed. Derived and inferred facts and the SQLite index are not committed. A committed manifest holds schema version, extractor pins and the root hash; a gate rebuilds twice and compares. A derived snapshot may be committed only if a gate verifies rebuild equality (churn and untracked-file bypass are ProofMap GAP-003, GAP-033) | High |
| R2 | Rule form: [incr] Python `Rule` functions; [math] SQL views; [gdb] one violation-query file per rule; [agent] Datalog theory-only | Two kinds, one output. File-local rules are Python functions over one file's facts. Graph-global rules are SQL violation queries with declared read relations and a stratum. Both emit `Finding`. No Datalog engine until about 30 rules or a recursion-with-negation need | Medium |
| R3 | Graph library: [gdb] rustworkx in extra, networkx oracle; [math] networkx dependency, rustworkx inspiration; [code] own Tarjan or networkx | Core ordering code is stdlib-only (about 100 lines) so determinism is ours. networkx is a test oracle, pinned below 3.7 because 3.7 requires Python >= 3.12 while EIJA supports >= 3.11 ([V4]; the dossier measured 3.5). rustworkx deferred: 10^6-edge closure is not the bottleneck | High |
| R4 | Node id: [code] `<lang>:<path>#<qualified name>`; okf `repo://path#fragment`; [ui] `ui:<view>/<control>` | Canonical id is the okf `repo://` URI. Language is an attribute, not part of the id. Non-file concepts get fragments with an explicit selector registered per node type; the id is never derived from a label. Note the okf fragment is interpreted by the hash method and file type (Python symbol, CSV first column, term slug, table cell slug), so the registry pairs fragment grammar with method | Medium; needs agreement with okf lane |
| R5 | Canonical JSON: [code] restrict payloads so `canonical()` and JCS coincide; [math], [gdb], [bx] use JCS | Both: restricted subset (no floats, safe integers, strings, booleans, null) serialised by a JCS writer, plus a test that `canonical()` output equals JCS on that subset. Kernel untouched | High |
| R6 | Two status vocabularies: kernel/assure evidence set PASS, FAIL, STALE, UNKNOWN, CONFLICT (+ NOT_RUN); [trace] link set COVERED, SUSPECT, ORPHANED, AMBIGUOUS, UNWANTED, UNRESOLVED; [incr] wants NOT_RUN to absorb PASS; [math] lattice omits NOT_RUN | Keep two sorts. Link status is per link; a fixed map lifts it to evidence status for aggregation (DESIGN: COVERED to PASS, SUSPECT to STALE, ORPHANED to FAIL, AMBIGUOUS to CONFLICT, UNRESOLVED to NOT_RUN; UNWANTED is a reported defect, not a status of coverage). Where NOT_RUN sits in the chain is an open question (section 9) with default: below PASS, above FAIL, absorbing PASS | Medium |
| R7 | CQL licence: [bx] README says BSD-3 for non-commercial and evaluative use, no LICENSE file; [math] says AGPL-3.0, last push 2023-04-14 | GitHub reports no SPDX for `CategoricalData/CQL`, last push 2026-07-26 ([V3]). [math] probably read a different repository. Either way CQL is not a dependency. UNVERIFIED which repository the AGPL claim refers to | Low on detail, High on verdict |
| R8 | OKF spec location: [gdb], [trace], [assure] cite `knowledge-catalog/okf/SPEC.md`; the okf lane says it moved to `open-knowledge-format` | Both repositories exist and are Apache-2.0 ([V3]). I read the `open-knowledge-format` SPEC ([V1]): version 0.2. The okf lane recorded byte-identical copies (SHA-256 `26aa5da0...`) on 2026-09-28; I did not re-hash. Cite the canonical repo | High |
| R9 | [code] "no imports from `src/`" vs [math] bench imports `eija_studio.domain` | `eijagraph` runtime never imports `eija_studio` (it must index other repos and must not couple to the kernel). Tests and benches may import the kernel as a reference oracle (`impact.closure`, `aggregate_status`, `assess_receipt`) | High |
| R10 | Hash granularity: okf `ast-v1` includes docstrings; [trace] proposes signature or symbol AST per link kind | Reuse okf methods; the link-kind-to-method policy is a weave table, not a new method. Requirement to symbol: `ast-sig-v1` or `ast-v1`; requirement to test: `ast-v1` on the test function; term to code: `ast-api-v1`; file artefacts: `lf-sha256-v1`. Re-measure on EIJA history (too short today) | Medium |
| R11 | Extras bloat: tree-sitter plus six grammars, libcst, playwright, networkx, rustworkx, jsonschema, rfc8785 all proposed for `graph` | Extra `graph` carries only what the compiler needs in phase 1 (`rfc8785`, `jsonschema`); tree-sitter and libcst enter when their trigger fires; Playwright reuses the hci pin; oracles are optional and skip as NOT_RUN. Splitting extras is an owner/lane-lead question | Medium |
| R12 | ADR numbering: [assure] proposes 0089 link certificates, 0090 statement pinning, 0091 claim graph; [lang] proposes 0089 registry; [incr] proposes 0089-0092 engine | One allocation table (ARCHITECTURE.md section 11) supersedes all dossier numbers | High |
| R13 | Proof policy: [agent] proofs advisory unless SMT-backed and pinned; [assure] a PASS with TCB label | Compatible. Proof-kind links produce labelled evidence; whether a label blocks a gate is owner-protected policy per link kind, defaulting to non-blocking except for pinned, second-checked laws | Medium |
| R14 | UI dossier proposes `labels` edge; language dossier binds forms to surfaces; ProofMap had no such edge | One edge type `names` (surface to term) with a `surface` attribute; UIL-004 compares the browser's accessible name with the term's registered forms | Medium |
| R15 | GitHub code scanning proposed in [incr]; memory: GitHub Actions unavailable (owner owes GitHub, 2026-09-27) | SARIF is produced locally; upload is REST only and an owner decision, not built | High |
| R16 | ProofMap Lite: dossiers call it private and licence-less | Confirmed by API: private, no SPDX ([V3]). Lessons only; copy no code | High |
| R17 | Tool availability claims: [mde] `sysml-toolkit` "three weeks old"; API shows pushed 2026-09-24, Apache-2.0 | Consistent. Still a watch item, never a dependency; its feature claims are unrun | High |

## 6. What is genuinely novel, and what is not

Every ingredient below exists elsewhere; the source is given. The claim of novelty is about the combination and its discipline. I could not run a broad prior-art search (budget exhausted), so treat "not found" as unverified.

| Not novel (reuse, cite) | Source |
|---|---|
| Suspect links via stored fingerprints and explicit clear | Doorstop |
| Coverage-state vocabulary (covered, predated, outdated, ambiguous, orphaned, unwanted) and direct vs transitive defects | OpenFastTrace |
| Symbol grammars and per-file immutable facts | SCIP, Kythe, Glean |
| Early cutoff and verifying traces | Build Systems a la Carte, Salsa |
| Certifying algorithms, witness plus small checker | Mehlhorn et al., Leroy |
| Assurance-case structural lint rules | Assurance 2.0 (Bloomfield and Rushby) |
| Lens laws | Foster et al. |
| Reflexion models | Murphy, Notkin, Sullivan |

| Novel in combination (claim to test, not to assert) | Why it matters | How it would be falsified |
|---|---|---|
| One closed, typed, content-addressed graph spanning code, UI, diagrams, ubiquitous language, requirements, tests, proofs, evidence, ADRs and agent runs, whose only authoritative parts are declared links and a human ledger | Most surveyed tools cover one or two of these; none read here spans all with a determinism contract | A surveyed tool found to do the same with a byte-identical, permutation-tested contract |
| Link status that is a pure function of (link, current digest, ledger) with method chosen per link kind by measurement, where a human ack is the only clearing act and agents may only propose | Turns "did the code drift from the requirement" into a hash comparison with a stated false-stale rate | The measured stale rates on EIJA history make SUSPECT noise unusable (signature-only 1.5 to 1.8% per change on two other repos; EIJA history is too short to say) |
| Claim-relative TCB and owner-pinned statement digests, so a green proof states what it stands on and cannot silently prove a weaker statement | Targets the weakened-postcondition attack seen in the vericoding study | An agent successfully weakens a pinned statement without a FAIL |
| UI enabled-set equality against kernel guards over enumerated (state, actor) pairs | Catches the measured drift today: UI hard-codes 5 actions, baseline example has 4, button enabledness ignores guards | UIL-005 reports clean while a browser test shows a mismatch |
| Determinism as a tested contract for a whole assurance graph: permutation harness (file order, hash seed, TZ, locale, CWD, CRLF, threads, non-BMP, Windows and POSIX) with byte-identical SARIF | Lets humans and agents trust that a re-run means the same thing | Any permutation that changes a byte |
| NOT_RUN as an absorbing verdict carried through SARIF (`executionSuccessful=false` plus notification) into gates | A skipped gate cannot look green | A gate that passes with a missing prerequisite |

What the graph does not do: prove code correct, prove that a link is semantically true, establish that people understand the software, or replace tests. A hash proves change, not correctness (AGENTS.md).

## 7. Measurement ledger

| Fact | Value | Label | Where |
|---|---|---|---|
| Closure, 10^3 / 10^5 / 10^6 edges, plain BFS | 0.3 ms / 56 ms / 848 ms | MEASUREMENT, synthetic, one machine | [gdb] 2 |
| Closure, SQLite CTE | 0.7 ms / 88 ms / 1312 ms | same | [gdb] 2 |
| Closure equality across BFS, CTE, networkx, 300 random graphs | 0 mismatches | MEASUREMENT (reproduced [V6]) | [math] M5 |
| Ordering: distinct outputs over 200 shuffles | `nx.condensation` 24, `graphlib` 5, sorted SCC 1, lexicographic topo 1 | MEASUREMENT (reproduced [V6]) | [math] C2 |
| PageRank float hashes over 40 shuffles | 40 distinct; 1 after rounding | MEASUREMENT (reproduced [V6]) | [math] C3 |
| Status aggregate | flat CONFLICT, rolled-up FAIL | MEASUREMENT (reproduced [V6]) | [math] C4 |
| Stale rate per file-touching commit, raw bytes / whole-file AST / symbol AST / signature | Doorstop 99.9 / 88.7 / 8.1 to 9.4 / 1.5 percent; StrictDoc 100 / 98.3 / 7.2 to 7.4 / 1.8 percent | MEASUREMENT, two Python repos | [trace] 4 |
| `ast` vs tree-sitter definitions in `src/` | 167 vs 167, no file differs | MEASUREMENT | [code] M4 |
| Broken Python under tree-sitter | classes recovered, `f` and `g` lost | MEASUREMENT | [code] M2 |
| Kernel `canonical()` vs JCS | differs on float text, `-0.0`, >2^53, astral key order | MEASUREMENT | [math] C1, [bx], [code] M6 |
| Glossary terms as identifier words in `src/` | 3 of 10 | MEASUREMENT, one repo, one commit | [lang] 5.3 |
| UI hard-coded actions | 5 literal vs 4 in baseline example | MEASUREMENT (static read) | [ui] 1 |
| Lens partiality | `set` before `enable` gives `MEANING_REQUIRED` | MEASUREMENT, 3 x 2 | [bx] 3.8 |
| Licence, archive and push metadata for 22 repositories | see section 8 | MEASUREMENT via GitHub API, 2026-09-29 | [V3] |
| POSIX byte-identity | not run; only Windows measured | NOT_RUN | all dossiers |
| Agent or human benefit of the graph | not measured | UNMEASURED | [agent], [thesis] |

## 8. Licence roles (exact where I read the text)

"Text" means a LICENSE file head or spec text opened by me or by the dossier author (stated in the dossier). "SPDX" means GitHub metadata only. Engineering reading, not legal advice; the owner must decide before shipping any GPL, LGPL, EPL or MPL component even as a separate process.

| Tool | Licence (basis) | Role for an Apache-2.0 package |
|---|---|---|
| stdlib `sqlite3`, `ast`, `json`, `html.parser` | public domain / PSF | dependency |
| `rfc8785` 0.1.4 | Apache-2.0 (SPDX [V3]) | dependency |
| `jsonschema` 4.26.0 | MIT ([V4]) | dependency (tests and schema checks) |
| `markdown-it-py` 4.2.0 | MIT ([lang], okf pin) | dependency (via okf extra) |
| tree-sitter core and grammars | MIT (SPDX [V3]; grammars per [code]) | dependency, phase 2 |
| LibCST 1.9.0 | MIT with PSF-derived files ([code] read LICENSE; GitHub reports NOASSERTION [V3]) | dependency, phase 2 |
| networkx | BSD-3-Clause ([V4]); 3.7 needs Python >= 3.12 | test oracle only, pin below 3.7 |
| rustworkx 0.18.1 | Apache-2.0 ([V4]) | deferred |
| Playwright, axe-core | Apache-2.0, MPL-2.0 ([ui]) | hci lane pin; unmodified MPL use |
| Hypothesis | MPL-2.0 (text [assure]) | test dependency (property lane) |
| Neo4j Community | GPL-3.0 (text [V3]) | export target, separate user-run process |
| OpenFastTrace | GPL-3.0 (text [V3]) | optional separate JVM process, report imported as data |
| TRLC | GPL-3.0 (SPDX [V3]) | inspiration only |
| LOBSTER | AGPL-3.0 ([trace]) | reject as dependency |
| Ladybug | MIT (SPDX [V3], Windows wheels per [gdb]) | export target, pinned; young fork of archived Kuzu |
| Kuzu | MIT, archived 2025-10-10 ([V3]) | reject |
| Memgraph, FalkorDB | BSL 1.1 plus enterprise licence; SSPL-1 ([gdb], text read) | reject |
| TypeDB | MPL-2.0 ([gdb]) | inspiration |
| Soufflé | UPL-1.0 (SPDX [V3]) | export target, optional process on Linux/macOS/WSL |
| SCIP | Apache-2.0 (SPDX [V3]) | export/input format; decode by protobuf codegen |
| Semgrep engine / community rules | LGPL-2.1 / Semgrep Rules License v1.0 ([code], summary read) | engine as process; do not vendor rules |
| CodeQL CLI | GitHub CodeQL Terms (text [code]) | reject |
| OpenRewrite (Py/TS) | Moderne Source Available ([code]) | reject |
| LikeC4 / Structurizr | MIT / Apache-2.0 (SPDX [V3]) | export target, chosen by determinism test |
| sysml-toolkit | Apache-2.0 (SPDX [V3]), 3 weeks old | optional validator, watch |
| SysML v2 Pilot | EPL-2.0 ([mde]) | optional process, never vendored |
| PlantUML | GPL-3.0-or-later default, variants listed in `LICENSES.md` ([mde]) | export target, existing visual-lane process |
| Vitruv, Sirius, Xtext, Papyrus | EPL-1.0 / EPL-2.0 ([bx], [mde]) | inspiration |
| eMoflon IBeX, Hets, Modelio | GPL-3.0, GPL-2.0-or-later, GPL-3.0 | inspiration only |
| PyPI `lenses` | GPLv3+ ([bx]) | reject |
| CQL | no SPDX; README non-commercial terms ([V3], [bx]) | reject |
| Doorstop / StrictDoc | LGPL-3.0 / Apache-2.0 (dossier read LICENSE; GitHub NOASSERTION [V3]) | inspiration, export (StrictDoc) |
| ProofMap Lite | private, no licence file ([V3]) | lessons only, copy no code |
| SARIF 2.1.0 | OASIS standard; schema reuse terms UNVERIFIED | write the profile; vendor schema only after owner clears terms |
| OKF v0.2 spec | Apache-2.0 repo ([V3], [V1]) | format dependency (okf lane) |

## 9. Open questions

1. Position of NOT_RUN and UNKNOWN in the conjunction chain (default proposed: FAIL < CONFLICT < STALE < NOT_RUN < UNKNOWN < PASS; owner or kernel-ADR decision, tested exhaustively).
2. Where the human ledger lives and how it is authenticated. A git-tracked append-only file gives history but a local HMAC seal is an integrity seal, not institutional identity (kernel doc). An agent with OS write access can edit any file; the honest statement is the one in AGENTS.md (not a sandbox).
3. Whether `graph` should be one extra or several, and whether tree-sitter is needed before a JS/CSS surface is checked.
4. Whether the okf lane accepts a shared hash-method registry and a `workflow-semantic-v1` method hashing `Workflow.semantic_hash`.
5. Kernel changes that the graph reports but must not make: canonical JSON (JCS), status lattice, explicit `operation_id` on routes, server-computed available actions for the UI. Each needs its own ADR and PR outside this lane.
6. Whether GitHub SARIF upload is wanted (REST only; owner token and egress decision).
7. Measurement plan for the human and agent benefit (hci and eval lanes): pre-registered tasks, pass^k, with and without graph context and semantic diff.
8. Determinism on POSIX: no measurement exists; needs one run on Linux or WSL and a committed golden.

## 10. Sources

Dossiers: the twelve files named in the key at the top, in `docs/weave/research/`. Primary and vendor sources are listed at the end of each dossier and were opened on 2026-09-29 by their authors; this synthesis relies on them where marked with the dossier key. Sources I opened for this synthesis:

- https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md (links untyped; broken links tolerated; `stale_after`; no hash field; version 0.2)
- https://www.rfc-editor.org/rfc/rfc8785 (Informational status; UTF-16 code unit ordering; ECMAScript number serialisation)
- https://api.github.com/repos/{neo4j/neo4j, LadybugDB/ladybug, kuzudb/kuzu, CategoricalData/CQL, itsallcode/openfasttrace, trailofbits/rfc8785.py, Instagram/LibCST, tree-sitter/tree-sitter, GoogleCloudPlatform/knowledge-catalog, GoogleCloudPlatform/open-knowledge-format, 45ck/proofmap-lite, Open-MBEE/sysml-toolkit, likec4/likec4, structurizr/structurizr, Qiskit/rustworkx, networkx/networkx, doorstop-dev/doorstop, strictdoc-project/strictdoc, souffle-lang/souffle, scip-code/scip, bmw-software-engineering/trlc} (licence, archived, pushed_at, visibility) and the `LICENSE.txt` heads of neo4j and openfasttrace (both "GNU GENERAL PUBLIC LICENSE Version 3")
- https://pypi.org/pypi/{rfc8785,networkx,libcst,rustworkx,jsonschema,markdown-it-py}/json (versions, `requires_python`)
- Sibling worktrees `/c/Dev/eija-wt/{okf,visual,agents,quality,metrics,tla,bend,property,mutation,hci}` (read-only): okf ADR-0045/0046 and `quality/okf/codelink.py`, visual ADR-0023 and `application/diagrams.py`, agents ADR-0041, quality ADR-0035, tla ADR-0028 and `TOOLS.lock`, bend ADR-0026, metrics ADR-0037, hci ADR-0039, mutation ADR-0033.
- Owner repo `45ck/proofmap-lite` README and `docs/label-conventions.md` (20 node types, 16 edge types), read with the owner's `gh` login.
