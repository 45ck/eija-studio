# Graph databases and knowledge graphs for EIJA

Dossier: `graph-databases` | Lane: weave | Written 2026-09-29 | All URLs opened 2026-09-29 unless marked UNVERIFIED.
Labels: MEASUREMENT = run in this session, reproducible with the named script. PREDICTION = reasoning, not run.

## 0. Decisions first

| # | Decision | Confidence |
|---|---|---|
| D1 | The graph is a **derived, rebuildable index**. It is never a source of truth. Truth stays in git-tracked text (code, OKF pages, contracts, ADRs, declared links) and in receipts. | High |
| D2 | **Core engine = Python stdlib `sqlite3` plus the existing least-fixed-point `closure`.** Zero new dependencies, Windows-safe, public domain. | High (MEASUREMENT, section 2) |
| D3 | Optional pinned extra `graph`: **rustworkx** (SCC, topological order, transitive reduction). NetworkX only as a differential-test oracle. | Medium |
| D4 | **Neo4j is excluded as a runtime dependency.** At most an optional export target (Cypher script), built only on demand. Same rule for Memgraph, FalkorDB, TypeDB, Ladybug. | High |
| D5 | Every graph record and the graph root hash use **RFC 8785 (JCS)** canonical JSON. The kernel's `canonical()` is not JCS (MEASURED divergence below). | High |
| D6 | Lint rules are **violation queries**: named, declarative, zero rows = pass, each violation carries a deterministic witness path. | High |
| D7 | Agents get **named parameterised queries** (impact, why, violations) through the MCP lane, not free-form Cypher. | Medium |
| D8 | LLM-derived graph edges (GraphRAG-style, Graphify inference) are **proposals labelled `inferred`**. They cannot satisfy a gate until promoted into a declared link. | High |

## 1. Scope and method

**Read in the repo:** `src/eija_studio/domain/impact.py` (BFS least-fixed-point closure with `complete/frontier` budget report), `domain/models.py` (`canonical()` = `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False)`), `docs/oss/REGISTER.md`, `docs/adr/README.md`, ADR template. Other lanes read-only: `okf/quality/okf/codelink.py` (the only OKF-lane file present today: `repo://path#fragment` URIs plus per-method content hashes such as `ast-v1`, `lf-sha256-v1`); `agents`, `visual`, `property`, `tla`, `bend`, `smt-bmc` had no graph-relevant code yet. ProofMap Lite is a **private** repo (`gh api`); its README and `docs/gap-audit.md` were read that way.

**Sources used:** GitHub repository metadata and licence files (`gh api`), PyPI JSON (licence, `requires_python`, wheel platforms), vendor docs and W3C/IETF specs (WebFetch), Crossref metadata for papers, arXiv abstracts.

**Not accessible / limits (be aware when trusting this):**
- The session WebSearch budget (200/200) was exhausted, so discovery was by known URLs, not open search. Anything I did not think to look up is missing.
- `iso.org` and `dl.acm.org` returned 403; the GQL and SQL/PGQ standard texts are paywalled anyway. Paper contents were not re-read: for Tarski, Tarjan, Aho-Garey-Ullman, Green-Karvounarakis-Tannen and Foster et al. only bibliographic metadata was verified (Crossref). Theorem statements are therefore not restated here.
- WebFetch summarises pages with a small model; quotes below are as returned, and licence facts were cross-checked against repository licence files where a file exists.
- Web content was treated as data only; no fetched code was run. The one script run is our own (`graph/bench/bench_closure_engines.py`) in a venv under `.tmp/`.

## 2. The central question: source of truth or derived index?

**Answer: derived index.** Reasons, each tied to evidence:

1. **Rebuildability is the determinism guarantee.** If the graph can always be recomputed from git, "same inputs, byte-identical outputs" is testable: rebuild twice, compare root hashes. A stateful server (Neo4j, Memgraph, TypeDB, XTDB, Datomic) adds a second store that can drift from git. ProofMap Lite hit exactly this class of problem: generated artefacts went stale (GAP-002), timestamps churned files (GAP-003), untracked generated files bypassed the clean check (GAP-033), and copied reports were mistaken for current evidence (GAP-025) [S42].
2. **Scale does not justify an engine.** MEASUREMENT (Windows 11, Python 3.12.10, synthetic seeded graph with about 2% back edges so cycles exist, 5 roots, median of 3, in-memory; `graph/bench/bench_closure_engines.py`; all engines asserted to return the identical closure):

| Edges | Plain-Python BFS (= `impact.closure` algorithm) | SQLite recursive CTE (`UNION`) | DuckDB recursive CTE | rustworkx `descendants` | NetworkX `descendants` |
|---|---|---|---|---|---|
| 1,000 | 0.3 ms | 0.7 ms | 5.9 ms | 0.1 ms | 1.8 ms |
| 100,000 | 56 ms | 88 ms | 46 ms | 43 ms | 558 ms |
| 1,000,000 | 848 ms | 1,312 ms | 528 ms | 720 ms | not run (memory) |

   Load times (SQLite `executemany` 2.0 s vs DuckDB CSV read 0.26 s at 10^6) are not like-for-like. Caveats: synthetic graph, one machine, wall-clock noise. Conclusion: for 10^3 to 10^6 edges the closure query is not the bottleneck; extraction (parsing code and docs) will be. **A graph database buys no speed at our scale.**
3. **What a graph DB does add** is a pattern language (Cypher, GQL, SQL/PGQ). That is a convenience for agents and humans, obtainable as an export without making the DB authoritative.
4. **Where truth actually lives** (proposed, matches the OKF lane's `repo://` + hash design):

| Layer | Examples | Authority | Rebuilt? |
|---|---|---|---|
| Declared links | OKF frontmatter and links, requirement tags in tests, ADR references, `repo://` URIs | Source of truth (text in git, human/agent-authored, kernel-checked) | No |
| Derived links | imports, symbol references, test-to-symbol coverage, generated diagrams | Recomputed by pinned extractors | Yes, every build |
| Inferred links | LLM entity extraction, GraphRAG communities, Graphify inference | Proposal only, label `inferred` | Optional |
| Evidence | receipts, model-check outputs | Kernel-recomputed; graph stores receipt hashes, not verdicts | n/a |

Pipeline: `sources -> per-file extraction (cached by content hash) -> canonical facts (JCS, sorted) -> Merkle root -> SQLite index [+ rustworkx] [+ exports]`. Commit only a manifest (schema version, extractor versions, root hash) into receipts; do not commit the full fact dump unless a gate verifies rebuild equality.

## 3. Per tool and school

Verdicts use: dependency / optional process / export target / inspiration / reject. Licence "usable as" reasoning is mine, not legal advice.

### 3.1 Property-graph databases

**Neo4j.** Community Edition: GPL v3 (repo `LICENSE.txt` is plain GPLv3; no Commons Clause string found; licensing page confirms "GPL v3") [S1, S2]. Enterprise: commercial "Neo4j Software Agreement" (not read) [S2]. Community lacks clustering, online backup, multiple databases and RBAC [S3]. Runtime: Java SE 21/25 for 2026.09; Windows 11 is listed for development only, Windows Server 2022/2025 for production [S4]. Python driver 6.3.1 is Apache-2.0 AND Python-2.0 [S5]. Order is not guaranteed without `ORDER BY` [S6]; unbounded variable-length patterns can be slow [S7]. Gives EIJA: mature Cypher, visual browser. Costs: a JVM server process, a stateful store outside git, GPLv3 server (fine as a separate process a user runs, not something to bundle or link into an Apache-2.0 distribution), nondeterministic row order unless every query sorts. **Verdict: excluded as runtime dependency; optional export target (Cypher script); driver only inside an opt-in adapter.**

**openCypher and GQL.** ISO/IEC 39075:2024 GQL was published April 2024 (openCypher says April 11, gqlstandards.org says April 17; the ISO page was inaccessible). Its graph pattern matching is "essentially identical" to SQL/PGQ, which is Part 16 of SQL:2023 [S8, S9, S10, S11]. openCypher is Apache-2.0 and active, evolving toward GQL conformance [S9]. Use: name the query dialect we export (Cypher today, GQL when tools support it). No product to adopt.

**Memgraph.** Repo licence = Business Source License 1.1 plus Memgraph Enterprise License. The Additional Use Grant allows internal production use but forbids embedding or distributing to third parties and DBaaS; change date stated as "2030-14-09" (malformed as printed) to Apache-2.0 [S12]. Not open source by its own text. **Reject as dependency; user-run optional process only.**

**Kuzu (status verified).** `kuzudb/kuzu` is **archived** on GitHub; README says the project is being archived; last release v0.11.3 (2025-10-10); MIT [S13]. Successor **Ladybug** (`LadybugDB/ladybug`, README: "formerly known as Kuzu"), MIT, active, v0.20.4 (2026-09-10), `pip install ladybug`, Windows amd64/arm64 wheels, Python `>=3.10,<3.15` [S14]. Embedded, columnar, Cypher, serialisable ACID. Costs: young fork under a different team; fast version cadence (v0.20.4 within a year of Kuzu's last v0.11.3); a Kuzu acquisition story is UNVERIFIED. **Verdict: best embedded Cypher option, but only as an optional export/query adapter (pinned), never core.**

**FalkorDB.** Server is SSPLv1; section 13 requires offering "Service Source Code" if the functionality is made available to third parties as a service [S15]. FalkorDBLite (embedded) is BSD per its README but PyPI ships only Linux and macOS wheels (cp312-314), no Windows [S15]. **Reject** (licence and Windows).

**TypeDB.** MPL-2.0 (file-level copyleft), v3.13.6 (2026-09-22), frequent releases, Windows x86_64 CE supported, Apache-2.0 driver with win_amd64 wheel [S16]. Strongly typed schema (entities, relations with roles, inheritance) is the closest match to "typed edges with constraints". Costs: server process, TypeQL is unfamiliar to LLMs (UNVERIFIED), stateful. **Verdict: inspiration (typed relations with roles); optional export only if demanded.**

### 3.2 Relational engines with graph queries

**SQLite** (public domain [S19]). Recursive CTEs: `UNION` deduplicates so cyclic graphs terminate; `UNION ALL` needs `LIMIT` or a `WHERE` guard; without `ORDER BY` extraction order is undefined (FIFO in the current implementation) [S19]. Already EIJA's store (ADR-0000/REGISTER). **Dependency (already present).** Rule: every result query ends in a total `ORDER BY`.

**DuckDB** (MIT; 1.5.6; Windows wheels) with `WITH RECURSIVE`, `USING KEY`, path-in-list cycle checks [S17]. Faster load and closure at 10^6 (section 2). **Verdict: optional extra for analytics over evidence and metrics tables when SQLite is too slow; not needed for the graph today.**

**DuckPGQ** (MIT, CWI): implements SQL:2023 SQL/PGQ `GRAPH_TABLE`, path finding, some algorithms; README calls it "a research project and a work in progress"; installed with `INSTALL duckpgq FROM community` (a network fetch at install time; pinning and offline mirroring needed; Windows support UNVERIFIED) [S18]. **Inspiration / experiment; reject for core.**

### 3.3 Versioned and temporal stores

**Dolt** (Apache-2.0, v2.3.5, 2026-09-16; Windows install documented). Prolly trees are history-independent (same content, same tree regardless of operation order), content-addressed, and diff in time proportional to the change [S20]. Owner already uses Dolt for beads. Gives: versioned tables with diff, a good fit for a cross-run evidence/metrics ledger. Costs: Go binary plus MySQL-protocol server, a second VCS beside git. **Optional process for ledgers; inspiration for our Merkle root; not for the graph.**

**XTDB 2** (MPL-2.0, JVM, v2.2.0-beta3 on 2026-09-28: still beta) bitemporal SQL [S21]. **Datomic** (docs: all editions free, binaries Apache-2.0; source availability UNVERIFIED; Nubank-maintained; JVM) [S22]. **Datascript** (EPL-1.0, in-memory Datalog for Clojure/JS) [S23]. All JVM/Clojure. **Inspiration only**: the useful idea is two time axes. We adapt it without wall-clock: "valid" = subject content hash, "recorded" = evidence content hash and git tree.

### 3.4 In-memory graph libraries

**rustworkx** (Apache-2.0, 0.18.1, Windows wheels; `strongly_connected_components`, `transitive_reduction`, `lexicographical_topological_sort`, `ancestors`, `descendants`, `condensation` present) [S24]. **NetworkX** (BSD-3-Clause; 3.7 requires Python >=3.12 while EIJA supports 3.11, so pin below 3.7 or keep dev-only; pure Python, about 13x slower than rustworkx at 10^5 in our run) [S24]. **Verdicts: rustworkx = optional dependency (extra `graph`, `==` pinned); NetworkX = test oracle.** Our benchmark asserted all engines return identical closures, which is the differential-testing pattern we want in `tests/graph/`.

### 3.5 RDF, OWL, SHACL

**Standards:** SHACL is a W3C Recommendation (2017-07-20) for validating RDF graphs against shapes; recursive-shape semantics are explicitly left to implementations; SHACL-SPARQL is optional [S27]. **RDFC-1.0** (W3C Rec, 2024-05-21): isomorphic datasets yield identical canonical output; can be slow on adversarial "poison" datasets [S28]. **Tools:** Apache Jena (Apache-2.0, Java), RDF4J (BSD-3-Clause per GitHub, Java) [S25], **Oxigraph** (MIT OR Apache-2.0, Rust, `pyoxigraph` 0.5.11 with Windows wheels, includes RDFC; README: SPARQL evaluation "not been optimized yet") [S26], rdflib (BSD-3) and **pySHACL** (Apache-2.0, pure Python) [S27].
What it gives: declarative, standards-based constraint language; canonical N-Quads. Costs: an RDF mapping layer, IRIs for everything, heavier reasoning semantics (OWL open-world) than an assurance kernel wants, pySHACL scale at 10^6 triples unmeasured. **Verdicts: SHACL = optional export-and-validate (extra, later); Jena/RDF4J = reject (JVM); Oxigraph/rdflib = export target if RDF is requested. Avoid blank nodes so RDFC is never needed.**

### 3.6 Datalog and code-intelligence systems

**Soufflé** (UPL-1.0; docs list Linux and macOS only, no Windows) [S30]. **Cozo** (MPL-2.0, embedded Datalog; no pushes since 2024-12-04) [S31]. **Glean** (BSD per its LICENSE file; not evaluated further). **SCIP** (Apache-2.0) and **tree-sitter** (MIT) are candidate derivation sources for symbol edges [S38]. **Verdicts:** Soufflé = export target (`.facts` + rules, run by users on Linux/macOS/WSL); Cozo = reject (stale); SCIP/tree-sitter = derivation inputs for the agents/quality lanes, not this dossier.

### 3.7 GraphRAG and file-based knowledge

**GraphRAG** (MIT; paper: LLM builds an entity graph, precomputes community summaries; claims better comprehensiveness and diversity than baseline RAG for global questions over corpora around 1M tokens [S32]). **CodexGraph** (agents query a code-graph database interface; DB unspecified in the abstract) [S34]. **Text2Cypher** (44,387-instance dataset; abstract states LLMs "typically produce incomplete or incorrect outputs" without fine-tuning) [S33]. **Graphify** (Apache-2.0, moved to `Graphify-Labs/graphify`; vendor says local deterministic AST parsing with every edge explained: vendor claim, not tested by us) [S35], already used by ProofMap Lite [S42]. Verdict: GraphRAG = **reject for the assurance graph** (LLM extraction is neither deterministic nor evidence), inspiration for navigating human prose. Graphify = optional input, labelled `inferred` unless its edges come from an AST pass we can reproduce.

**OKF v0.2** [S37]: a directory of Markdown files with YAML frontmatter; only `type` is required; bundles may be a git repo. Fields for provenance (`sources`), trust (`generated`, `verified`, tiers), lifecycle (`status`, `stale_after`) and Attested Computations (deterministic, no-LLM attester). What EIJA must add, because OKF is deliberately loose:
- Links are **untyped** directed edges and **broken links are tolerated** (sections 6.1, 11). EIJA needs a stricter profile: typed edges, broken link = error.
- `stale_after` is decided by `now >= stale_after` (wall-clock), and `generated.at`/`verified.at` are timestamps. Determinism doctrine: keep them out of identity hashes, and decide freshness by content hash (the okf lane's `repo://` + hash method) rather than the clock.
OKF is the authoring format for declared links, not a graph store.

**OpenFastTrace** (GPL-3.0 per GitHub) is what ProofMap used for tracing; usable only as a separately spawned Java process, never linked [S36].

### 3.8 Options table

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| SQLite (`sqlite3`) | Public domain | Stable, stdlib | dependency | Already the store; cycle-safe recursive CTE; closure 1.3 s at 10^6 edges | S19, S44 |
| rustworkx | Apache-2.0 | 0.18.1, active | dependency (extra `graph`) | SCC, topo order, reduction; Windows wheels | S24 |
| NetworkX | BSD-3-Clause | 3.7 (needs Py>=3.12) | optional process | Test oracle only; about 13x slower | S24, S44 |
| DuckDB | MIT | 1.5.6, active | optional process | Analytics on ledgers; faster at 10^6 | S17, S44 |
| DuckPGQ | MIT | "research project" | inspiration | SQL/PGQ preview; install-time network fetch | S18 |
| Neo4j Community | GPL-3.0 | Active | export-target | JVM server, GPL server, no gain at our scale | S1-S4, S6 |
| Neo4j Enterprise | Commercial agreement | Active | reject | Terms not open; not needed | S2, S3 |
| neo4j Python driver | Apache-2.0 + PSF | 6.3.1 | export-target | Only inside an opt-in adapter | S5 |
| Memgraph | BSL 1.1 + MEL | Active | reject | Grant forbids embedding/distribution | S12 |
| Kuzu | MIT | Archived, last 0.11.3 | reject | Archived upstream | S13 |
| Ladybug | MIT | 0.20.4, active, Windows wheels | export-target | Embedded Cypher; young fork, pin | S14 |
| FalkorDB / FalkorDBLite | SSPLv1 / BSD wrapper | Active | reject | SSPL section 13; no Windows wheels | S15 |
| TypeDB | MPL-2.0 | 3.13.x, active | inspiration | Typed relations; server; TypeQL learnability UNVERIFIED | S16 |
| Dolt | Apache-2.0 | 2.3.5, active | optional process | Versioned evidence ledger; owner already runs it | S20 |
| XTDB 2 | MPL-2.0 | beta | inspiration | Bitemporal model; JVM | S21 |
| Datomic | Apache-2.0 binaries | Active | inspiration | Immutable facts; closed source status UNVERIFIED | S22 |
| Datascript | EPL-1.0 | Active | inspiration | Clojure/JS only | S23 |
| Apache Jena / RDF4J | Apache-2.0 / BSD-3 | Active | reject | JVM; no need | S25 |
| Oxigraph / pyoxigraph | MIT OR Apache-2.0 | 0.5.11 | export-target | RDF + RDFC, Windows wheels | S26 |
| rdflib + pySHACL | BSD-3 / Apache-2.0 | Active | export-target | SHACL validation of exported RDF | S27 |
| Soufflé | UPL-1.0 | Active; no Windows docs | export-target | Datalog `.facts` export for Linux/WSL users | S30 |
| Cozo | MPL-2.0 | No push since 2024-12 | reject | Stale | S31 |
| GraphRAG | MIT | Active | reject | LLM-extracted edges are not evidence | S32 |
| Graphify | Apache-2.0 | Active | optional process | Inferred edges only | S35 |
| OpenFastTrace | GPL-3.0 | Active | optional process | Spawned jar only | S36 |
| OKF v0.2 | Apache-2.0 (repo) | v0.2 spec | dependency (format) | Authoring format for declared links; needs strict profile | S37 |
| SCIP / tree-sitter | Apache-2.0 / MIT | Active | inspiration | Derivation inputs, other lanes | S38 |

## 4. Mathematical and computer-science mechanisms

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Order theory, fixed points | Impact closure as least fixed point of a monotone step function (already `impact.py`); per-edge-type propagation rules | Result independent of visit order; termination on finite graphs (visited set only grows) | Only monotone rules; "no test covers X" is negation and needs stratification | adopt | S43, S41 (Tarski, metadata only) |
| Graph theory | SCC condensation to a DAG; lexicographic topological order; transitive reduction for diagram edges | Cycles become explicit components; stable ordering for reports and diagrams | Reduction is only meaningful on the condensed DAG | adopt | S24, S41 (Tarjan, Aho-Garey-Ullman, metadata only) |
| Relational algebra, Datalog | Each lint rule = named query that must return zero rows; recursion via `WITH RECURSIVE` | Declarative, diffable, human-readable rules | Non-linear recursion and negation awkward in CTEs; Soufflé needed for full Datalog | adopt | S19, S30 |
| Provenance semirings | Annotate derived facts with how they were derived | "Why is this impacted / why does the claim hold?" | Full polynomials can explode | adapt: keep one canonical witness path per derived fact (BFS parent pointers over sorted neighbours) | S41 (Green et al., metadata only) |
| Content-addressed Merkle structures | Root hash over sorted canonical records; per-file extraction cache keyed by content hash | Graph identity for receipts; cheap change detection; history independence shown by Dolt prolly trees | Encoding must be exact | adopt | S20, S43 |
| Canonical serialisation | RFC 8785 for records; avoid blank nodes so RDFC-1.0 is unnecessary | Byte-identical across platforms | I-JSON limits: IEEE-754 numbers, no duplicate keys, no Unicode normalisation | adopt (JCS), theory-only (RDFC) | S29, S28 |
| Category theory | Schema graph as a category; a data graph is well typed iff every edge maps into an allowed (source type, edge type, target type); commuting-path checks (Requirement to Test to Evidence equals derived Requirement to Evidence) | Ill-typed or inconsistent links fail at build | CQL has no licence file (GitHub reports none): treat as inspiration; only the typing check is implementable cheaply | adapt (typing + path equalities), theory-only (functorial migration) | S40 |
| Incremental computation | Per-file memoisation now; DBSP-style incremental view maintenance later | Rebuild only what changed | DBSP-level machinery is heavy; full closure at 10^6 edges is about 1 s already | adapt (memoisation), theory-only (DBSP) | S39, S44 |
| Bitemporal data | Two axes: subject content hash vs evidence content hash and git tree | Answers "was this proof about this code?" without wall-clock | Needs an explicit as-of key per receipt | adapt | S21, S22 |
| Bidirectional transformations (lenses) | Round-trip laws for diagram-model edits | Would let humans edit diagrams safely | Belongs to the visual lane; not needed for a read-only index | theory-only | S41 (Foster et al., metadata only) |
| Graph rewriting, information theory, probabilistic assurance | Not assessed for graph storage | n/a | n/a | theory-only | none |

**Measured finding on canonical JSON (S43, S29).** Python `canonical({"\U0001F600":1,"～":2})` orders `～` first (code-point order); RFC 8785 sorts by UTF-16 code units, which places the emoji (D83D) first. Python also emits `1.0` and `1e-07` for floats; RFC 8785 uses ECMAScript number serialisation, so these are expected to differ (exact JCS output for these values UNVERIFIED: pull the RFC test vectors). Today's models use strings and integers, so risk is low, but a graph of arbitrary identifiers should not depend on it. Kernel change needs its own ADR; the graph package should ship its own JCS encoder plus RFC vectors, and forbid floats.

## 5. Implications for EIJA

1. **ADR "graph is a derived index"** (block 0089-0112): declared, derived and inferred layers as in section 2; only declared links are authoritative; a gate rebuilds twice and compares the root hash.
2. **Implement `graph/eijagraph` on `sqlite3` first.** Tables `node(id, type, content_hash)` and `edge(src, type, dst, origin)`; every query ends with a total `ORDER BY`; recursive CTEs use `UNION` plus an explicit `LIMIT` guard. Keep `impact.closure` semantics (`complete`, `frontier`) as the reference; test the SQL against it.
3. **Node IDs are the okf lane's `repo://path#fragment` URIs**, edge records carry the hash method (`ast-v1` etc.) so staleness is a hash comparison, never a clock read.
4. **Typed edge schema** in `graph/schema/`: allowed (source type, edge type, target type), plus commuting-path rules. OKF profile for EIJA: typed edges, broken link = error, `generated.at`/`verified.at`/`stale_after` excluded from hashes.
5. **Violation queries as the linter.** One file per rule, zero rows = pass, each row a stable id plus witness path. This is the "compiler and linters over the whole set" and it is human-readable.
6. **Deterministic explanations.** Every reachability fact carries the lexicographically first shortest witness path; the review packet can print "why".
7. **Agent interface:** MCP tools `impact(node)`, `why(node)`, `violations(rule)`; free-form read-only SQL only behind a flag with row and time limits. Do not rely on LLM-written Cypher (S33).
8. **Optional extra `graph`** (pinned `==`): rustworkx for SCC/topological order; NetworkX dev-only oracle with a Python-version pin decision. Add REGISTER rows for each. Exports (Cypher script, N-Quads plus SHACL, Soufflé facts, Ladybug) only when a user asks; each is a one-way, non-authoritative projection with its own contract test.
9. **Ledger, not graph, goes in Dolt** (if the owner wants cross-run history); keep git as the authority for the graph inputs.
10. **Revisit triggers for a graph DB:** index above about 10^7 edges, rebuild exceeding an agreed budget on CI-equivalent hardware, or needs beyond joins and recursion (weighted paths, community detection) that rustworkx cannot cover.

## 6. Gaps and unverified items

- UNVERIFIED: Kuzu acquisition or company change; only the archive notice and fork are verified.
- UNVERIFIED: Neo4j Enterprise agreement terms; whether the Neo4j GPLv3 tree carries additional terms beyond the LICENSE header (none found by string search).
- Legal reading of Apache-2.0 plus GPLv3/SSPL/BSL interaction is my engineering reading, not legal advice.
- UNVERIFIED: DuckPGQ on Windows and its offline install; TypeDB LLM-authoring reliability; Datomic source availability; XTDB Windows; SHACL and pySHACL performance at 10^6 triples.
- UNVERIFIED: any claim that SQL is more reliable than Cypher for LLM authors. No comparative evidence found (Text2Cypher shows only that Cypher generation errs).
- GQL standard text and exact publication date (April 11 vs 17 per two sources) not confirmed from ISO.
- Benchmark is synthetic and single-machine; it says nothing about extraction cost, which is the likely bottleneck and is not yet measured.
- Paper theorem statements were not re-read (metadata only); the fixed-point termination argument in section 4 is my own elementary reasoning about `impact.py`.
- OKF and agents lanes are in flux; interfaces here assume `codelink.py`'s URI and hash-method design and may need updating.
- Graphify determinism is a vendor claim.

## 7. Sources (accessed 2026-09-29)

| Id | URL |
|---|---|
| S1 | https://github.com/neo4j/neo4j (LICENSE.txt, repo metadata via API) |
| S2 | https://neo4j.com/licensing/ |
| S3 | https://neo4j.com/docs/operations-manual/current/introduction/ |
| S4 | https://neo4j.com/docs/operations-manual/current/installation/requirements/ |
| S5 | https://github.com/neo4j/neo4j-python-driver , https://pypi.org/project/neo4j/ |
| S6 | https://neo4j.com/docs/cypher-manual/current/clauses/order-by/ |
| S7 | https://neo4j.com/docs/cypher-manual/current/patterns/variable-length-patterns/ |
| S8 | https://www.gqlstandards.org/ |
| S9 | https://opencypher.org/ , https://github.com/opencypher/openCypher |
| S10 | https://arxiv.org/abs/2112.06217 |
| S11 | https://en.wikipedia.org/wiki/SQL:2023 |
| S12 | https://github.com/memgraph/memgraph (LICENSE, licenses/BSL.txt) |
| S13 | https://github.com/kuzudb/kuzu |
| S14 | https://github.com/LadybugDB/ladybug , https://pypi.org/project/ladybug/ |
| S15 | https://github.com/FalkorDB/FalkorDB (LICENSE), https://github.com/FalkorDB/falkordblite , https://pypi.org/project/falkordblite/ |
| S16 | https://github.com/typedb/typedb , https://typedb.com/docs/home/install/ce |
| S17 | https://github.com/duckdb/duckdb , https://duckdb.org/docs/current/sql/query_syntax/with.html , https://pypi.org/project/duckdb/ |
| S18 | https://github.com/cwida/duckpgq-extension , https://duckdb.org/community_extensions/extensions/duckpgq.html |
| S19 | https://www.sqlite.org/lang_with.html , https://www.sqlite.org/copyright.html |
| S20 | https://github.com/dolthub/dolt , https://www.dolthub.com/docs/architecture/storage-engine/prolly-tree |
| S21 | https://github.com/xtdb/xtdb , https://docs.xtdb.com/ |
| S22 | https://docs.datomic.com/datomic-overview.html |
| S23 | https://github.com/tonsky/datascript |
| S24 | https://github.com/Qiskit/rustworkx , https://www.rustworkx.org/api/index.html , https://pypi.org/project/rustworkx/ , https://github.com/networkx/networkx , https://pypi.org/project/networkx/ |
| S25 | https://github.com/apache/jena , https://github.com/eclipse-rdf4j/rdf4j |
| S26 | https://github.com/oxigraph/oxigraph , https://pypi.org/project/pyoxigraph/ |
| S27 | https://www.w3.org/TR/shacl/ , https://github.com/RDFLib/pySHACL , https://pypi.org/project/rdflib/ |
| S28 | https://www.w3.org/TR/rdf-canon/ |
| S29 | https://www.rfc-editor.org/rfc/rfc8785 |
| S30 | https://github.com/souffle-lang/souffle , https://souffle-lang.github.io/install |
| S31 | https://github.com/cozodb/cozo |
| S32 | https://arxiv.org/abs/2404.16130 , https://github.com/microsoft/graphrag |
| S33 | https://arxiv.org/abs/2412.10064 |
| S34 | https://arxiv.org/abs/2408.03910 |
| S35 | https://github.com/Graphify-Labs/graphify |
| S36 | https://github.com/itsallcode/openfasttrace |
| S37 | https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md |
| S38 | https://github.com/scip-code/scip , https://github.com/tree-sitter/tree-sitter |
| S39 | https://arxiv.org/abs/2203.16684 |
| S40 | https://arxiv.org/abs/1009.1166 , https://github.com/CategoricalData/CQL |
| S41 | Crossref metadata: https://api.crossref.org/works/10.1145/1265530.1265535 (semirings), /10.1137/0201010 (Tarjan), /10.1137/0201008 (Aho-Garey-Ullman), /10.2140/pjm.1955.5.285 (Tarski), /10.1145/1232420.1232424 (lenses) |
| S42 | https://github.com/45ck/proofmap-lite (private; README and docs/gap-audit.md read via `gh api`) |
| S43 | In-repo: `src/eija_studio/domain/impact.py`, `domain/models.py`; `/c/Dev/eija-wt/okf/quality/okf/codelink.py` |
| S44 | `graph/bench/bench_closure_engines.py` (MEASUREMENT, Python 3.12.10, Windows 11) |
