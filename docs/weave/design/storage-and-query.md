# Weave design: storage and query

Lane: weave. Aspect: storage-query. Date: 2026-09-29 (revised after audit the same day). Status: proposed; decision record is [ADR-0091](../../adr/0091-weave-storage-query.md); benchmark method is [graph/bench/PLAN.md](../../../graph/bench/PLAN.md).
Labels: MEASUREMENT (a script ran in this session; script and result file named), PREDICTION (reasoned, not run), DESIGN (a proposal), UNVERIFIED (not opened or not confirmable; nothing is built on it). All URLs were opened on 2026-09-29 unless marked otherwise. Licence readings are engineering readings, not legal advice.

## 0. Decisions first

| # | Decision | Confidence | Evidence |
|---|---|---|---|
| S1 | **Git-tracked files are the source of truth. The graph is a derived, disposable index.** Stored as a SQLite file (stdlib `sqlite3`), named by an index key (the root plus the rule-set hash, schema version, engine version and extractor pins, Section 4.3), never committed, never edited. Only `graph/links/*.jsonl`, `graph/ledger.jsonl` and `graph/manifest.json` are committed inputs or attestations. | High | Section 2 (scale), section 4 (determinism), ARCHITECTURE section 1 |
| S2 | **The index file's bytes are not the identity.** The identity of the graph is the SHA-256 of a canonical sorted dump of `node` and `edge` (the root hash); the identity of the index file, which also holds findings and proposals, is the index key. MEASUREMENT: the same 2,000-edge graph built in 5 different insertion orders gave 5 different SQLite file hashes and 1 dump hash. | High | Section 2.3 |
| S3 | **No graph database in the trust path**: not Neo4j, Ladybug, Memgraph, FalkorDB, TypeDB, Kuzu. At the sizes we can reach (about 10^4 edges today, PREDICTION; 10^6 edges is 100 times more) SQLite answers every query class we need in under 5 s, most in under 30 ms. Speed is not the reason to prefer SQLite over plain in-memory Python, which was measured 3 to 10 times faster on the same queries (Section 2.1b); the reasons are declarative, diffable rule files and ad hoc human exploration (Section 3, option F). | High | Sections 2.1, 3 |
| S4 | **Query language, three audiences.** Rule authors write SQL violation queries (one file per rule, stratified, declared reads). Agents call **named, parameterised, bounded queries** with typed results, never free-form query text. Humans use the CLI (`why`, `impact`), generated OKF pages and diagrams, and may open the SQLite file in any SQL tool. Cypher/GQL is an **export vocabulary**, not an input language. | High for agents (evidence in 5.2); Medium for the SQL choice (no comparative LLM evidence exists, see 5.2) | Sections 5, 7 |
| S5 | **Datalog is a discipline, not an engine.** Rules are stratified; the loader rejects negation inside a recursive stratum; recursion is `WITH RECURSIVE ... UNION` over the node column only. Soufflé is an optional differential oracle on Linux and macOS, later. | High | Section 5.3, MEASUREMENT of CTE termination |
| S6 | **Provenance semirings: adopt the idea, not the algebra.** Store one canonical witness (lexicographically smallest shortest path, plus rule id and premises for derived facts) per fact. The Boolean semiring and the tropical semiring are what we actually use. Polynomials N[X] are not stored. | High | Section 6, the PODS 2007 text read this session |
| S7 | **Neo4j: optional one-way export, run by a person as a separate process, never a runtime requirement.** The export is sorted CSV plus a Cypher load script, with a golden test. "Import" means only a differential check that an engine loaded from the export reproduces the reference closure (NOT_RUN without an engine). No import of engine data back into the graph. | High | Section 7 |
| S8 | **OKF pages are a get-only projection.** The graph never reads the machine-generated parts of a page (otherwise the projection feeds its own source and the root hash has no fixed point). Typed, hash-anchored links live in `graph/links/*.jsonl`; the okf lane's `links` block is generated from them. | High | Section 8 |
| S9 | **Ladybug (Kuzu's successor) is an export target only, and only with caps and the `SHORTEST` pattern.** Reproducible evidence, all measured on 0.20.4 (PyPI has 0.21.0, published 2026-09-28, not re-run): under a 128 MB buffer-pool cap and an RSS watchdog, the default variable-length pattern with bound 30 fails cleanly on 1,000 and 2,000 edges (buffer pool exhausted), a smaller bound silently returns an incomplete set, an exact bound costs 0.60 s at 2,000 edges where the `* SHORTEST` form returns exactly the reference closure in 8 to 24 ms at 50 MB (Section 2.4). A separate, unrecorded anecdote (8.4 GB resident in an uncapped 10,000-edge run, reported by the coordinator, not reproducible) motivated the caps and is NOT evidence. | High that the default pattern is unsafe to hand to agents or authors; the internal cause is UNVERIFIED | Section 2.4 |

## 1. Scope, and what this aspect depends on

This aspect answers: is the graph a source of truth or a derived index; which store and query language; whether provenance semirings pay; how Neo4j is supported; how OKF relates; operational cost and licences for adopters. It does not decide node or link types (aspect: typed schema), the rule model beyond its storage needs (rule-model aspect, [0095-weave-lint-compile-rules.md](../../adr/0095-weave-lint-compile-rules.md)), or the agent tool list (agents lane).

Read for this design: all files in `docs/weave/research/` (SYNTHESIS, `graph-databases-and-knowledge-graphs`, `math-and-cs-foundations`, `traceability-and-requirements-graphs`, `code-intelligence-and-analysis`, `agent-reliability-and-context`, others skimmed), `docs/weave/ARCHITECTURE.md`, `graph/brief.json`, `src/eija_studio/domain/impact.py`, the okf worktree (`docs/adr/0045`, `0046`, `quality/okf/codelink.py`, a generated page), the agents worktree ADR-0041, `docs/adr/template.md`, `docs/oss/REGISTER.md`.

### 1.1 Interfaces (each dependency on another aspect or lane, stated once)

| Depends on | What this design needs from it | What this design provides | Status |
|---|---|---|---|
| okf lane | `repo://` grammar (`parse_uri`), hash methods, `digest(root, ref, method)`; pages with `okf:generated` blocks; STALE gate | Generated `links` block content; the rule that the graph excludes generated blocks (Section 8) | Interface proposed; okf lane owns page generation |
| agents lane | MCP server, `AgentSurface` | Named query catalogue (Section 5.4) with JSON-Schema results; query safety contract | Proposed; agents lane owns transport |
| typed-schema aspect (metamodel; ARCHITECTURE section 11 allocates 0092, and [0089-weave-metamodel-identity.md](../../adr/0089-weave-metamodel-identity.md) covers metamodel and identity) | Node and edge types, signatures | Table DDL that stores any type set; signature check is a load-time step | Independent of the exact type list |
| identity aspect (same file, [0089-weave-metamodel-identity.md](../../adr/0089-weave-metamodel-identity.md); ARCHITECTURE section 11 allocates 0090) | Fragment grammar per node type | `node.id` is an opaque `repo://` string here | Independent |
| canonical serialisation (ARCHITECTURE section 11 allocates 0091; the metamodel-identity record above also covers hashing) | JCS-subset writer and length-safe hashing | Uses it for the canonical dump | Numbers are not frozen: this record was assigned 0091 by its brief. References here use the aspect name and file path; the integrator reconciles the numbers |
| determinism aspect (ARCHITECTURE section 11 allocates 0099 to determinism, but the file 0099-weave-agent-interface.md in the tree is the agent-interface aspect, so the numbers conflict) | Permutation harness | Store-specific determinism tests (Section 4.4) | Proposed |
| quality lane | nox session pattern | `quality/sessions/graph.py` tags `fast`, `full`, `release` | Proposed |
| kernel | `impact.closure` | Used as the reference oracle in tests only; `eijagraph` never imports `eija_studio` | Existing |

## 2. Evidence

### 2.1 Scale: how big is the graph, and how fast is a query

**Size of EIJA itself (MEASUREMENT, `graph/bench/storage_query_probe.py --sizing`, block `repository_counts` of `graph/bench/results/storage-query-probe.json`).** The okf worktree at commit `cdc4f37321de` (the full repo plus the OKF wiki, no modified tracked files), counted with stdlib `ast` and regexes. The counts move as the okf lane commits; the result file records the head it counted.

| Fact | Count |
|---|---|
| Tracked files | 331 (234 `.md`, 53 `.py`, 22 `.json`) |
| Python `def` and `class` nodes | 465 |
| Python import statements | 276 |
| Markdown relative links | 1,141 |
| `repo://` occurrences | 687 |
| Markdown files under `okf/` | 210 (includes `index.md`) |

Direct edges countable today: at most 1,141 + 687 + 276 = 2,104 (occurrences, not deduplicated; the three kinds overlap). PREDICTION: adding tests, requirements, ADRs, term bindings, UI keys and evidence links gives a graph of order 10^3 to 10^4 edges, so 10^4 is a generous ceiling for this repository and 10^6 is the headroom for an adopter monorepo. Not tested against a built graph; no extractor exists yet.

**Synthetic typed graph (MEASUREMENT, Windows 11, Python 3.12.10, SQLite 3.49.1, one shared 16 GB machine, scratch on a slow D: HDD, median of 3 (2 at 10^6), wall-clock; not deterministic).** Generator: `make_graph` in `storage_query_probe.py`, seed 11; symbols, requirements and tests, typed edges `depends_on` (2% back edges so cycles exist), `satisfies`, `verifies`, `covers`; 8% of requirements seeded with no `verifies` edge. Closure roots: 5 symbols; propagating edge types `depends_on` and `satisfies`. Every query result was asserted equal to the seeded or reference answer before it was timed. The table is the final full run (timing script hash `4f44a11a0685...`, field `timing_script_sha256` in the result file). Width caveat: this benchmark used a 3-column node table and a 4-column edge table, whereas the specified DDL (Section 4.2) has 5 and 7 columns including 64-hex digests; Section 2.1c re-measures size and dump time at the specified width. The index-file-size, build and canonical-dump rows below are therefore understated by about 1.5 to 2 times. The second column of each cell is an earlier full run of the same machine and script family (`storage-query-probe-run-b-timing.json`), shown because the spread between runs is itself a result.

| Metric (final run / earlier run B) | 10^4 edges | 10^5 edges | 10^6 edges |
|---|---|---|---|
| Nodes | 3,500 | 35,000 | 350,000 |
| Build, in-memory, text ids, with reverse index (s) | 0.028 / 0.11 | 0.54 / 1.14 | 5.2 / 5.9 |
| Build, file, default pragmas (s) | 0.67 / 0.12 | 0.80 / 0.87 | 9.6 / 12.5 |
| Build, file, `journal_mode=OFF`, `synchronous=OFF` (s) | 0.05 / 0.08 | 0.54 / 0.71 | 5.7 / 10.8 |
| Build, in-memory, integer-interned edges only (s) | 0.022 / 0.068 | 0.19 / 0.20 | 1.9 / 2.4 |
| Index file size, journal off (MB) | 1.6 | 17.0 | 178.8 |
| Closure of 5 roots, recursive CTE, text ids (s) | 0.020 / 0.028 | 0.158 / 0.163 | 2.5 / 3.6 |
| Closure, same, integer-interned ids (s) | 0.008 / 0.006 | 0.098 / 0.090 | 1.1 / 1.7 |
| Closure size (nodes) | 2,346 | 23,290 | 232,499 |
| Closure plus witness map in Python (s) | 0.019 / 0.013 | 0.173 / 0.183 | 2.2 / 2.7 |
| Violation: requirements with no `verifies` (anti-join) (s) | 0.0006 / 0.0006 | 0.006 / 0.008 | 0.067 / 0.066 |
| Violation: impacted and untested (stratified: recursion, then negation) (s) | 0.022 / 0.013 | 0.18 / 0.23 | 3.8 / 4.4 |
| Neighbours in and out of one node, p50 (ms) | 0.011 / 0.011 | 0.013 / 0.011 | 0.013 / 0.014 |
| Neighbours in and out of one node, p99 (ms) | 0.045 / 0.036 | 0.16 / 0.025 | 0.038 / 0.048 |
| Canonical dump plus root hash (s) | 0.069 / 0.095 | 0.89 / 1.01 | 8.5 / 10.8 |
| DuckDB bulk CSV load of edges (s) | 0.078 / 0.12 | 0.17 / 0.30 | 0.44 / 0.63 |
| DuckDB anti-join violation (s) | 0.006 / 0.007 | 0.013 / 0.012 | 0.043 / 0.083 |

Reading, with limits:
- **Spread.** Two full runs on the same machine differ by up to 1.7 times for query timings (closure up to 1.4 times; the stratified violation at 10^4 edges 1.66 times: 0.0218 s against 0.0131 s), 2 to 4 times for in-memory builds at 10^4 and 10^5 edges, and 5.4 times for the file build with default pragmas at 10^4 edges (0.67 s against 0.12 s: fsync on the HDD). Tail latency (p99) moved 6.6 times at 10^5 (0.1635 ms against 0.0247 ms). Differences below about 1.5 times are not findings; file-build timings on this machine are not reliable to better than a factor of five. `journal_mode=OFF` with `synchronous=OFF` was faster than default pragmas in all six recorded pairs (1.2 to 13 times), which is consistent with fsync cost on an HDD but is not a controlled comparison.
- At 10^4 edges every query is at most 22 ms (narrow tables). At 10^6 (100 times the predicted ceiling) the slowest query is 3.8 to 4.4 s. No engine is needed for speed.
- Integer interning shortens closure time by 1.6 to 2.2 times at 10^5 and 10^6 in both runs. It is safe for determinism only because the integer is the node's rank in the sorted list of ids, so `ORDER BY rank` equals `ORDER BY id` by construction (SQLite's default text order is byte order; MEASUREMENT: Python `sorted` equals SQLite `ORDER BY` on a mixed BMP and astral test set). It is a phase-2 optimisation, not needed at 10^4.
- The canonical dump and root hash is Python-bound (8.5 to 10.8 s at 10^6). Beyond about 10^5 edges the root must be a Merkle tree over per-view or per-file partitions, not one flat hash. At 10^4 it is 0.07 to 0.1 s (narrow) and 0.15 s at the specified width (Section 2.1c).
- DuckDB is faster to bulk load and to run large scans (0.44 to 0.63 s and 43 to 83 ms at 10^6). It is a candidate for analytics over the evidence ledger, not for the graph. Cold `python -c "import X"` wall time, median of 5, final run: `sqlite3` 88 ms, `duckdb` 280 ms, `networkx` 503 ms (bare interpreter start 55 ms). Other runs this session (not kept) gave up to 162, 482 and 3,964 ms, so cold-start cost depends mostly on the OS file cache.
- Extraction, not querying, is the likely bottleneck: reading and `ast.parse`-ing all 53 Python files and reading all 234 Markdown files of the okf worktree took 0.115 s median of 5 (weave worktree: 0.058 s). This is stdlib only; tree-sitter and SCIP indexers will cost more and are not measured here.
- Earlier dossier figures (SQLite closure 88 ms at 10^5 and 1.3 s at 10^6, [gdb] section 2) used a different synthetic graph without an edge-type join and integer ids; they are not comparable and neither is a claim about real repositories.
- Not measured: POSIX and macOS; SQLite versions older than 3.49.1; warm versus cold OS cache; concurrent readers; peak process memory of the SQLite build; the real graph (no extractor yet).

### 2.1a Extrapolation to the revisit trigger (PREDICTION, arithmetic shown)

Closure of 5 roots with text ids, seconds, from the table: final run 0.0195 (10^4), 0.1578 (10^5), 2.5058 (10^6); run B 0.0279, 0.1633, 3.5684. Log-log slope between adjacent sizes is log10(t2/t1): final run log10(0.1578/0.0195) = 0.91 and log10(2.5058/0.1578) = 1.20; run B 0.77 and 1.34. The slope rises above 1 at 10^6; the cause is unmeasured. The closure share of the graph is constant (2,346 of 3,500 nodes, 23,290 of 35,000 and 232,499 of 350,000, about 66 to 67% each), so a growing share does not explain it; leaving the CPU cache is a hypothesis, not tested. Extending the last slope by one decade gives 2.5058 x 10^1.20 = 39.7 s (final run) and 3.5684 x 10^1.34 = 78 s (run B) at 10^7 edges, against the 10 s budget for closure in PLAN.md. Root hash grows about linearly (8.5 s to 8.5 x 10 = 85 s at 10^7; run B 108 s; narrow tables, so a floor: the specified width gave 12.6 s at 10^6 and 126 s by the same arithmetic). So the 10^7-edge revisit trigger is where the measured curve leaves the budget, by a factor of 4 to 8. Nothing at 10^7 was run: an in-memory Python build of that size was judged unsafe on the shared 16 GB PC, so this stays a PREDICTION.

### 2.1b Option F head-to-head: the same queries in plain Python, no database (MEASUREMENT)

`storage_query_probe.py --python-baseline`, result `graph/bench/results/python-baseline-and-wide-ddl.json` (script hash in the file; same machine and conditions as 2.1, median of 3, 2 at 10^6). The Python side builds two dicts from the edge rows, then runs a verbatim copy of `impact.closure` (`kernel_closure`), the lexicographically smallest witness map, the anti-join as a set difference, and the stratified violation as closure then set difference. Every answer was asserted equal to the SQLite answer for the same graph before its time was kept. Not included: reading from a file, extraction, peak memory (not measured).

| Query (s) | 10^4 Python / SQL | 10^5 Python / SQL | 10^6 Python / SQL |
|---|---|---|---|
| Build (dicts / in-memory tables with reverse index) | 0.002 / 0.028 | 0.051 / 0.54 | 0.654 / 5.2 |
| Closure of 5 roots (kernel copy / text-id CTE) | 0.0034 / 0.020 | 0.054 / 0.158 | 0.75 / 2.5 |
| Closure plus lexmin witness (Python only) | 0.0022 | 0.049 | 0.89 |
| Anti-join violation | 0.00002 / 0.0006 | 0.0003 / 0.006 | 0.0055 / 0.067 |
| Stratified violation (impacted and untested) | 0.0039 / 0.022 | 0.081 / 0.18 | 0.75 / 3.8 |

Reading. Plain Python was faster than SQLite on every row (3 to 10 times on closure and stratified queries at 10^6; more on build), so **speed justifies neither a database nor SQLite over Python**. Closure plus witness in Python totals about the same as the closure alone: the witness is not an extra cost. What SQLite buys is not measured here and is a DESIGN judgement: rules as one declarative statement per file that a person can read, diff and run in any SQL tool; a persistent, read-only-openable index with an authorizer for the owner-only ad hoc escape hatch; and a rule language that is not Python code an agent could make impure. The cost is recursive SQL that is awkward beyond the positive fragment and two implementations of closure (SQL for sets, Python for budgets and witnesses). If the rule-authoring evaluation (PLAN H16) shows no authoring or inspection benefit, the fallback is Python rules over the same files with SQLite kept as the exploration export.

### 2.1c Size and dump time at the specified DDL width (MEASUREMENT)

Same script and result file. `node` has 5 columns and `edge` 7 (Section 4.2), digests are full-width fake SHA-256 hex, journal off, file on the HDD scratch. Closure here runs on the file-backed database (the 2.1 closure ran in memory), so its times are not comparable to 2.1.

| Metric | 10^4 edges | 10^5 edges | 10^6 edges | Narrow tables (2.1) |
|---|---|---|---|---|
| Index file size (MB) | 2.8 | 28.9 | 299.5 | 1.6 / 17.0 / 178.8 |
| Build, file, journal off (s) | 0.08 | 1.65 | 20.2 | 0.05 / 0.54 / 5.7 |
| Canonical dump plus root hash (s) | 0.147 | 1.34 | 12.6 | 0.069 / 0.89 / 8.5 |
| Closure of 5 roots, file-backed CTE (s) | 0.014 | 0.40 | 4.35 | in memory: 0.020 / 0.158 / 2.5 |

The wider rows grow files about 1.7 times and the dump 1.5 to 2 times. One run per size on a shared HDD; the spread noted in 2.1 applies.

### 2.2 Determinism of the store itself

All rows: MEASUREMENT from `storage_query_probe.py`, deterministic block, hash `f771bce3...76aa` in the result file (regenerated 2026-09-29 after the audit added the closure-budget sub-block; the previous hash `fb6a7d96...16c0` covered the same sub-blocks without it, and every other sub-block is byte-identical) (the counts of the repository trees are outside this hash because they move with every commit). Running the deterministic block again with `PYTHONHASHSEED=5` and with `PYTHONHASHSEED=9` gave the same hash; earlier revisions of the script, run with `PYTHONHASHSEED=random`, gave byte-identical JSON twice.

| Question | Result | Consequence |
|---|---|---|
| Is the SQLite file deterministic? 2,000 edges, 6 builds (5 distinct insertion orders, one repeated) | 5 distinct file hashes for both table layouts; the repeated order gave equal bytes. `VACUUM INTO` normalised the `WITHOUT ROWID` layout to 1 distinct hash but left the rowid layout at 5. The canonical dump hash was 1 in all cases. | Never hash or compare the file. The identity is the dump hash. Load in sorted order anyway (D-01). |
| Is result order defined without `ORDER BY`? 8 shuffled insertion orders | An unindexed filtered scan on rowid tables gave 8 distinct orders; on `WITHOUT ROWID` tables 1 (primary-key order). The recursive closure gave 1 in both. The SQLite docs say extraction order is undefined without `ORDER BY` (FIFO in the current implementation) | The 1s are implementation accidents. Rule D-01 stands: every result query ends in a total `ORDER BY`, lint-checked. |
| Does `UNION` terminate on cycles? Cycle a, b, c plus tail d, `LIMIT 1000` guard | `UNION` on the node column alone: 4 rows, terminated by itself. `UNION` carrying a path column, or a depth column: ran to the 1,000-row guard. `UNION ALL`: ran to the guard. | Recursive rules select only the node column. Paths and depths are not carried in SQL; witnesses are computed outside (Section 6). The `LIMIT` guard is a backstop, and a result of exactly the guard size is a finding, not an answer. |
| Does SQLite `ORDER BY` match Python `sorted`? Set of `z`, fullwidth tilde, emoji, `a`, `B`, `e-acute` | Yes (both code point order). RFC 8785 key order (UTF-16 code units) differs: it places the emoji before the fullwidth tilde. | Use JCS order only for keys inside serialised objects; use binary order for record order; test both. Do not ask SQL to sort in JCS order. |
| Are `LIKE` and `GLOB` safe? | `'A' LIKE 'a'` is true (ASCII case-insensitive); `'A' GLOB 'a'` is false | Rule queries use `=`, `GLOB` or `substr`, never `LIKE`. |
| Does a SQL closure equal the kernel closure, and is the kernel's budgeted truncation stable? 300 random graphs with cycles (`budgeted_closure_checks`); 195 of the 300 budgets truncated | The unbounded recursive CTE equals the kernel closure as a set in all 300 (0 mismatches); the budgeted `impact.closure` result (affected set, `complete`, `frontier`) was identical under shuffled edge insertion order in all 300 (0 mismatches); the probe's copy equals the real `impact.closure` on all 300 cases | Sets: SQL is allowed. Budgets: computed by the Python BFS, next row |
| Could SQL implement the budget? `SELECT ... FROM r LIMIT budget` on the same 300 graphs (SQLite 3.49.1; observation outside the determinism hash) | The SQL result differed from the kernel's truncated set in 33 of 300 graphs (queue order is undefined without `ORDER BY`; the edge index yields neighbours by type then destination, not by destination) | Not used. Budget and `frontier` follow `impact.closure`'s FIFO visit order, so they are computed by the Python BFS with parent pointers. SQL computes only the unbounded set closure and joins |
| Do the SQL violation queries return the intended set? 20,000 edges, 92 seeded uncovered requirements | Rows equal the seeded set exactly | Positive control for the "zero rows means pass" contract. |

### 2.3 Witnesses

MEASUREMENT (`witness_checks`, 600 random graphs, 1 to 2 roots, 3 to 13 nodes, 3,373 paths): the lexicographically smallest shortest path (by node-id sequence) from a root computed by rank propagation equals a brute-force oracle that enumerates every shortest path (0 mismatches), and is unchanged under shuffled edge order (0 mismatches). The naive alternative, FIFO breadth-first search over sorted neighbour lists recording the first discoverer as parent, gave the same witness in all 600 graphs (0 differences). That is the algorithm already in `impact.closure` (sorted roots, sorted neighbours, FIFO). So recording one parent pointer per visited node in that loop gives the canonical witness at no measurable extra cost (Section 2.1b). Sample, not proof; the argument is by induction on levels: the queue order at each level is the order by (parent rank, node id).

### 2.4 Operational cost of one embedded graph engine (Ladybug, measured on 0.20.4)

Version note (PyPI JSON, checked 2026-09-29): `ladybug` 0.21.0 was uploaded 2026-09-28T23:25Z, about 20 hours before this document's date; the GitHub releases page still lists v0.20.4 as latest. Every measurement below is for 0.20.4 and was not re-run on 0.21.0, so the conclusions about the default pattern are dated and version-specific. The 5.9 MB wheel figure is the 0.20.4 Windows amd64 wheel (5.87 MB); the 0.21.0 Windows wheel is 5.64 MB and Linux musl wheels are 9.3 MB (0.20.4) to 10.6 MB (0.21.0).

Sources: row 1, an anecdote reported by the coordinator, who said they observed and killed the process; it is in no result file and is not evidence. Rows 2 to 6, MEASUREMENT, `graph/bench/ladybug_probe.py`, results `graph/bench/results/ladybug-capped-probe-{100,1000,2000}-edges.json`. Every Ladybug process in the probe starts an in-process RSS watchdog (10 ms sampling, abort above 500 MB), uses a 128 MB buffer pool, one thread and `max_db_size` 1 GB, runs each query variant in its own child process with a 30 s limit, and refuses graphs above 2,000 edges. The probe compares each result with the SQLite closure of the same graph (roots added back, because a variable-length pattern of length at least 1 returns a root only if a path reaches it).

| Run | Settings | Result |
|---|---|---|
| 1. ANECDOTE, not evidence: 10,000-edge load then variable-length reachability, first bound 30 | Defaults (its docstring: buffer pool "~80% of system memory"; 8 TB address-space reservation unless `max_db_size` is set) | Reported: 8.4 GB resident, the shared 16 GB Windows PC fell to about 500 MB free and 97% commit, the coordinator killed it. Unrecorded and not reproducible; no decision rests on it. |
| 2. Default pattern `-[:Prop* 1..30]->`, 1,000 and 2,000 edges | Capped | **Failed on both, cleanly**: "Buffer manager exception: Unable to allocate memory! The buffer pool is full and no memory could be freed!" Peak RSS was 165 MB (1,000 edges) and 169 MB (2,000 edges); every successful query child sat at about 50 MB (46 to 50 MB), so 165 to 169 minus 50 is 115 to 119 MB, under the 128 MB pool: the data are consistent with the cap holding (pool full plus process baseline). |
| 3. Default pattern with a small bound (3), 1,000 and 2,000 edges | Capped | **Silently incomplete**: 88 of 217 and 366 of 462 reference nodes missing, no error. |
| 4. Default pattern with the exact bound (true depth + 1: 7 and 11) | Capped | Equals the reference. 26 ms at 1,000 edges; **0.60 s at 2,000 edges (76 MB)**, where the `SHORTEST` form below takes 24 ms. |
| 5. `-[:Prop* SHORTEST 1..30]->`, 1,000 and 2,000 edges, also with the exact bound | Capped | **Equals the reference in every case**; 8 to 24 ms; peak RSS 50 MB. 100 edges: also equal (4 ms). |
| 6. Plain edge scan without `ORDER BY`, 3 shuffled loads | Capped | 3 distinct row orders (100, 1,000 and 2,000 edges alike). |

Reading. (a) For Ladybug the safe reachability query is the `SHORTEST` form with a bound at least as large as the longest chain; a smaller bound truncates silently, and the default form enumerates paths (its cost grows with the bound: bound 11 took 0.60 s where `SHORTEST` took 24 ms on the same 462-node closure). The SQLite recursive CTE has no bound to choose and returned the reference closure of a 10^4-edge graph in 20 ms (Section 2.1). This is direct evidence for the choice in Section 5: a natural-looking Cypher query that an agent or a person writes can be slow, exhaust memory or return a wrong-looking short answer, whereas the SQL rule has one form that terminates. (b) With the cap, the failing query stopped with an error and RSS stayed near baseline plus pool, so in this probe the cap held. What the cap does not do is make the default pattern return an answer: at bound 30 it fails, and at a smaller bound it returns a silently incomplete set. Whether the uncapped default would exhaust memory on a 10,000-edge graph is NOT established here (the only report is the row 1 anecdote). (c) The internal cause of the blow-up is UNVERIFIED; I did not read the engine's path semantics. It is consistent with default variable-length patterns enumerating paths rather than nodes, which the timing difference against `SHORTEST` supports but does not prove. (d) Not measured: any graph above 2,000 edges, the memory of `SHORTEST` at scale, and macOS or Linux.

Disclosure (who observed what). The 8.4 GB figure in row 1 was reported by the coordinator; this author did not observe it and no result file holds it. Before the caps existed, this author ran earlier versions of this probe with default settings. The first run (10,000 edges, default pattern with bound 30 first, no per-query limit) produced no output within an outer 300 s limit. Two later runs at 2,000 and 10,000 edges put each query in a child with a 30 s limit: the default pattern at bound 30 hit the limit at both sizes, and the `SHORTEST` form equalled the reference at 10,000 edges (0.23 to 0.44 s). None of these runs measured memory, they ran outside the shared-PC rule that now applies, they are consistent with the coordinator's report in row 1 (a 30 s limit was hit at bound 30), and they are not reproducible from the repository (the script was replaced by the capped version and its result files were removed). They are mentioned for completeness and are not used as evidence.

Verdict: a strike against Ladybug 0.20.4 as a default dependency, resting on the reproducible items only: the default variable-length pattern silently truncates below the true depth, enumerates paths (0.60 s against 24 ms at 2,000 edges), and fails outright at bound 30 under a 128 MB pool at 1,000 edges. Recorded as an export target only, with the caps and the `SHORTEST` pattern in the export README; re-run the 100 and 1,000-edge probes on the current release before any change of role. A safe configuration was demonstrated only for graphs of at most 2,000 edges; it is not demonstrated for realistic ones.

### 2.5 Provenance semirings: what the paper says (opened as text)

Source: Green, Karvounarakis, Tannen, "Provenance Semirings", PODS 2007, `https://www.cs.ucdavis.edu/~green/papers/pods07.pdf`, read as extracted text.
- Definition 3.1: a K-relation over attributes U is a function from U-tuples to K with finite support (Definition 3.2 gives the positive-algebra operations). In the Section 3 text, a commutative semiring is (K, +, ., 0, 1) with (K,+,0) and (K,.,1) commutative monoids, . distributing over +, and a . 0 = 0 . a = 0.
- Proposition 3.5: for commutative semirings K and K', a map h from K to K' commutes with every positive relational algebra (RA+) query on one argument iff h is a semiring homomorphism.
- Proposition 4.2 and Theorem 4.3: polynomials N[X] are the most general provenance semiring; for any commutative semiring K, evaluating the N[X] result under a valuation gives the K result, for any RA+ query.
- Section 5: Datalog on K-relations needs omega-continuous semirings (least upper bounds of chains), and the tag of an answer is the sum over all derivation trees of the product of leaf tags. Examples given include the Boolean semiring, (N with infinity, +, ., 0, 1), PosBool(B) for finite B, and the tropical semiring (N with infinity, min, +, infinity, 0).
- Proposition 5.4: for a Datalog query q and B-relation R (B as printed in the text; read as the Boolean semiring), supp(q(R)) equals q applied to supp(R). Nothing more general is claimed here.
- Conclusion: the authors "would like to extend Definition 3.2 to include negation, which seems to require axiomatizing an additional operation akin to 'proper subtraction'". So the theory here covers the positive fragment only.
- The authors write that Algorithm All-Trees "does not immediately give an effective way to evaluate datalog over the tropical semiring but we conjecture that such a procedure exists". So the paper supplies no procedure for the tropical case; our shortest-witness computation (Section 6) is an elementary breadth-first search plus a brute-force check, not an application of the paper's algorithm.
- In (N with infinity) a tuple can have infinitely many derivation trees (their example x = ax + b has solution a* b where 1* = infinity in N-infinity); the paper introduces formal power series for that. This is exactly our cyclic dependency graphs.

## 3. Options considered for storage

Verdict vocabulary: dependency, optional process, export target, inspiration, reject. "Status" is from the GitHub API or PyPI on 2026-09-29.

| Option | Licence (basis) | Status 2026-09-29 | Windows / macOS / Linux for OSS adopters | Role | Why | Source |
|---|---|---|---|---|---|---|
| Files in git plus stdlib `sqlite3` index | SQLite: public domain; `sqlite3` module: PSF | SQLite 3.49.1 measured here; CTE support since release 3.8.3, 2014-02-03 | Bundled with CPython on all three | **dependency (chosen)** | Zero install, deterministic when used with total `ORDER BY`, measured in Section 2 | [sqlite.org/lang_with](https://www.sqlite.org/lang_with.html), [release 3.8.3](https://www.sqlite.org/releaselog/3_8_3.html), [copyright](https://www.sqlite.org/copyright.html) (dossier, [gdb] S19) |
| In-memory Python only (dicts; option F) | Python licence | n/a | Any Python | **rejected as the only store; kept as the algorithm for budgets and witnesses** | Measured 3 to 10 times faster than SQLite on the same queries (Section 2.1b), so speed is not the argument against it. Against it: rules would be Python code rather than declarative statements, and a human has nothing to open and query. That benefit is a DESIGN judgement, unmeasured (PLAN H16) | Section 2.1b; `python-baseline-and-wide-ddl.json` |
| DuckDB | MIT (GitHub SPDX; PyPI metadata empty) | 1.5.6, published 2026-09-28; pushed 2026-09-28 | Wheels for win, macOS, Linux; wheel up to 32.8 MB | optional process (later): analytics over ledgers | Faster at 10^6 for scans (Section 2.1) but adds up to 32.8 MB and about 190 ms of import time (280 ms against 88 ms in the final run) for no needed gain. Its docs list `USING KEY` and list-based cycle checks and mention no `CYCLE` clause. | [duckdb.org WITH](https://duckdb.org/docs/current/sql/query_syntax/with.html); `gh api repos/duckdb/duckdb`; PyPI JSON |
| DuckPGQ (SQL/PGQ in DuckDB) | MIT | pushed 2026-09-17; README: "a research project and a work in progress"; `INSTALL duckpgq FROM community` | Windows support not stated on the page | inspiration | Install-time network fetch; research status | [github.com/cwida/duckpgq-extension](https://github.com/cwida/duckpgq-extension) |
| Ladybug (Kuzu successor) | MIT | Measured on 0.20.4 (2026-09-10). PyPI has 0.21.0 (uploaded 2026-09-28T23:25Z), not re-run; GitHub releases still show v0.20.4; pushed 2026-09-28; README: "formerly known as Kuzu"; Cypher | Wheels win amd64/arm64, macOS, Linux; Windows amd64 wheel 5.87 MB (0.20.4), 5.64 MB (0.21.0); Linux musl up to 9.3 / 10.6 MB | **export target only** | Section 2.4: under a 128 MB cap the default recursive pattern failed at bound 30, truncated silently at bound 3 and took 0.60 s at the exact bound, while the `SHORTEST` pattern matched the reference in 24 ms (graphs up to 2,000 edges, 0.20.4 only) | [github.com/LadybugDB/ladybug](https://github.com/LadybugDB/ladybug), PyPI JSON |
| Kuzu | MIT | Archived on GitHub, last push 2025-10-10, last PyPI 0.11.3 | n/a | reject | Archived upstream | `gh api repos/kuzudb/kuzu` |
| Neo4j Community | GPL-3.0 (`LICENSE.txt` opened: "GNU GENERAL PUBLIC LICENSE Version 3"; licensing page lists "Neo4j Community Edition (GPL v3)") | pushed 2026-09-22 | Server on JVM: "Java SE 21 and Java SE 25" for 2025.10; Windows 11 "personal use and development only", Windows Server 2022/2025 for production; dev systems "2GB minimum, 16GB or more recommended" | **export target, run by a person as a separate process** | GPL server and JVM; second stateful store; "Unless ORDER BY is used, Neo4j does not guarantee the row order of a query result" | [LICENSE.txt](https://github.com/neo4j/neo4j), [licensing](https://neo4j.com/licensing/), [requirements](https://neo4j.com/docs/operations-manual/current/installation/requirements/), [ORDER BY](https://neo4j.com/docs/cypher-manual/current/clauses/order-by/) |
| Neo4j Enterprise | "Neo4j Software Agreement", terms not read | n/a | n/a | reject | Terms not open; not needed | [licensing](https://neo4j.com/licensing/) |
| neo4j Python driver | Apache-2.0 AND Python-2.0 (PyPI) | 6.3.1, 2026-09-15 | pure Python | export target (inside an opt-in adapter only) | Only for the optional differential check | PyPI JSON |
| Memgraph | Business Source License 1.1 plus Enterprise licence (dossier read the text); GitHub SPDX NOASSERTION | pushed 2026-09-28 | server | reject | Additional Use Grant forbids embedding or distributing (per dossier [gdb] S12; not re-read this session) | dossier [gdb] |
| FalkorDB | SSPLv1 (dossier read the text); GitHub NOASSERTION | pushed 2026-09-28 | server; embedded variant has no Windows wheels per dossier | reject | SSPL section 13 | dossier [gdb] |
| Apache AGE | Apache-2.0 (GitHub SPDX) | pushed 2026-09-19 | Architecture not opened; that it needs a PostgreSQL server is UNVERIFIED | reject (not evaluated further) | Server-side; adds a database for no gain at our scale | `gh api repos/apache/age` |
| TypeDB | MPL-2.0 (SPDX) | pushed 2026-09-28 | server | inspiration | Typed relations with roles; server; TypeQL learnability UNVERIFIED | `gh api repos/typedb/typedb`, dossier |
| Dolt | Apache-2.0 (SPDX) | pushed 2026-09-28 | Go binary plus MySQL protocol server | optional process for a cross-run evidence ledger | Not for the graph; the owner already runs it | `gh api repos/dolthub/dolt`, dossier |
| Cozo | MPL-2.0 | last push 2024-12-04 | embedded | reject | Stale | `gh api repos/cozodb/cozo` |
| Differential Datalog (DDlog) | MIT | archived, last push 2023-07-07 | n/a | reject | Archived | `gh api repos/vmware-archive/differential-datalog` |
| Soufflé | UPL-1.0 | pushed 2026-07-13 | Install page lists Ubuntu, Fedora, Oracle Linux 8, macOS and source builds; Windows is not mentioned | optional differential oracle (Linux, macOS, WSL) | Datalog semantics cross-check; not for Windows-native users | [souffle-lang.github.io/install](https://souffle-lang.github.io/install) |
| Glean | GitHub SPDX NOASSERTION; dossier read BSD-style | pushed 2026-09-28 | heavy | inspiration | Base versus derived facts, immutable typed facts | dossier [code] |
| rustworkx | Apache-2.0 | 0.18.1, 2026-07-30 | wheels win, macOS, Linux | deferred | Closure is not the bottleneck | PyPI JSON |
| networkx | BSD-3-Clause | 3.7 requires Python >= 3.12 (PyPI); EIJA supports >= 3.11 | pure Python | test oracle only, pin below 3.7 | Import cost 1.4 to 4 s | PyPI JSON |

The alternative "graph database as source of truth, git as export" is rejected for the reason recorded in the dossier from the owner's own ProofMap Lite experience: a second store drifted from git (its gap records GAP-002, 003, 025, 033; the repository is private, and I rely on the dossier's reading).

## 4. Store design (DESIGN unless labelled)

### 4.1 Layers and truth

Follow ARCHITECTURE section 2. This aspect owns L2 storage and the query surface of L3 to L4.

| Artefact | Location | Committed? | Authority |
|---|---|---|---|
| Declared links | `graph/links/*.jsonl` (sorted, JCS subset) | yes | source of truth |
| Decision ledger | `graph/ledger.jsonl` (append-only) | yes | source of truth (human) |
| Manifest | `graph/manifest.json`: schema version, extractor pins, rule-set hash, root hash | yes | attestation only; a gate rebuilds and compares |
| Index | `graph/.index/graph-<root12>-<key12>.sqlite3` | **no** | none; disposable |
| Findings, SARIF | generated | only as goldens | derived |

Gitignore note: the repo's `.gitignore` already contains `*.sqlite3*` but not `*.sqlite`. ARCHITECTURE section 2 names `graph/.index/graph.sqlite`, which that pattern would not ignore. Use the `.sqlite3` suffix, and add `graph/.index/` to `.gitignore` when the integrator commits (root `.gitignore` is not owned by this lane).

### 4.2 Schema

```sql
-- application_id and user_version are set to fixed constants; page_size is set explicitly to 4096.
CREATE TABLE node(id TEXT PRIMARY KEY, type TEXT NOT NULL, content_hash TEXT NOT NULL,
                  method TEXT NOT NULL, label TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE edge(src TEXT NOT NULL, type TEXT NOT NULL, dst TEXT NOT NULL, origin TEXT NOT NULL,
                  soundness TEXT NOT NULL, method TEXT NOT NULL, digest TEXT NOT NULL,
                  PRIMARY KEY(src, type, dst)) WITHOUT ROWID;
CREATE INDEX edge_rev ON edge(dst, type, src);
CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT NOT NULL) WITHOUT ROWID;  -- root, index key and its inputs
CREATE TABLE fact_prov(kind TEXT, subject TEXT, rule_id TEXT, premises TEXT, PRIMARY KEY(kind, subject, rule_id));
CREATE TABLE finding(fingerprint TEXT PRIMARY KEY, rule_id TEXT NOT NULL, ...) WITHOUT ROWID;
```

The main benchmark (2.1) used the first two tables with three and four columns; Section 2.1c re-measured file size, build, dump and closure at this width. `WITHOUT ROWID` gives primary-key scan order; the rowid layout gave 8 distinct scan orders, so it is banned, not because order would be relied on but so accidents are less likely. Origin classes and soundness classes are those of `graph/brief.json`; `inferred` rows sit in a separate `proposal` table so a coverage query cannot count them by forgetting a filter (DESIGN; the check is that no rule query reads `proposal`, enforced at load time).

### 4.3 Build, snapshot, replace

1. Extract to sorted facts (extractor protocol aspect; number not frozen).
2. Insert in sorted order into a new temporary file, with `journal_mode=OFF` and `synchronous=OFF`, in one transaction. Measured faster than default pragmas in all six recorded pairs (1.2 to 13 times, Section 2.1) on this HDD, so it is the default for the build, not for readers. The SQLite pragma documentation warns that with `journal_mode=OFF` "the database file will very likely go corrupt" if the application crashes mid-transaction, and calls `synchronous=OFF` "a good option when creating a new database from scratch, in a scenario where the process of creating the database can be repeated". That is our case only if a half-written file can never be mistaken for an index: the build writes to a temporary name, computes the root, and only then renames to `graph-<root12>.sqlite3` (step 4); a crashed build leaves a temporary file that `graph gc` removes. If a later measurement on a non-HDD disk shows no gain, drop the pragmas and keep the rename.
3. Compute the root hash as the SHA-256 of the canonical dump, streamed: for each row of `node ORDER BY id`, then `edge ORDER BY src, type, dst`, one JCS-subset array per line, LF-terminated, preceded by a domain tag and lengths (D-12). At 10^4 edges this costs 0.1 s.
4. Compute the **index key** and name the file `graph-<root12>-<key12>.sqlite3` (first 12 hex characters of the root and of the key). `key = SHA-256(domain tag "eija.weave.index.v1" and length-prefixed fields: root hash, rule-set hash, schema version, eijagraph version, extractor-pins hash)`, where the rule-set hash is the SHA-256 of the sorted list of (rule id, SHA-256 of the rule file bytes, declared stratum). Reason: the file also holds `finding`, `fact_prov` and `proposal`, which are functions of the rules, the schema, the engine and the extractors, and none of those enter the root (the root covers `node` and `edge` only). Naming by the root alone would reuse a stale file, with old findings, after a rule edit. The root and every key input are stored in `meta`, and a reader that finds a mismatch between the file name and `meta` refuses the file. Readers write `PRAGMA query_only=ON` on open.

Why file-per-root: an agent server holding a connection would block replacing `graph.sqlite3` on Windows (PREDICTION: an open file cannot be replaced on Windows; not tested here); a new snapshot per root removes the case, and old snapshots are garbage-collected by a `graph gc` command that keeps the newest N (default 3). The unchanged-input rebuild is a no-op: same index key, same file name. A changed rule with an unchanged graph gives the same root and a different key, hence a new file with recomputed findings.

### 4.4 Determinism tests owned by this aspect

| Test | Oracle | Rule |
|---|---|---|
| Rebuild twice from a clean checkout: equal root hashes | root hash | D-17 |
| Shuffle insertion order: equal root hashes; different file bytes are allowed and documented | root hash | D-01, S2 |
| Every SQL text ends in a total `ORDER BY`; no `LIKE`; no `UNION ALL` without a guard; no recursive select with extra columns | lint over `graph/rules/*.sql` (parsed, not regex) | D-01, D-09 |
| Unbounded closure via SQL equals `impact.closure` as a set on 300 random graphs including cycles (measured: 0 mismatches, Section 2.2) | kernel oracle | reference semantics |
| Budgeted closure (affected set, `complete`, `frontier`) computed by the Python BFS equals `impact.closure` and is unchanged by shuffled edge insertion order (measured on the probe's copy: 0 mismatches in 300; the test over `eijagraph.store` output is still to be written) | kernel oracle, permutation | reference semantics, D-01 |
| Index key changes when one rule, the schema version, the engine version or an extractor pin changes with the same graph, and is unchanged when none does; a stale file is never returned (NOT_RUN: `eijagraph.store` does not exist yet) | key function test | Section 4.3 |
| Witness equals brute-force lexicographically smallest shortest path; re-checking a witness on its own subgraph recovers the fact | brute-force oracle | Section 6 |
| Projection independence: deleting all generated OKF blocks does not change the root hash | root hash | S8 |
| Windows and POSIX golden equality | goldens | D-20 (POSIX NOT_RUN until measured) |
| Incremental output equals clean output after random edit sequences | differential test | D-18 |

## 5. Query layer

### 5.1 The audiences and what each needs

| Audience | Needs | Interface | Determinism contract |
|---|---|---|---|
| Rule author (human or agent proposing a rule) | Declarative, diffable, testable | One `.sql` file per rule with declared `reads` and `stratum`; zero rows means pass | Total order, witness columns, stable finding id |
| Agent (through MCP) | Bounded, typed, verifiable answers; no chance to invent identifiers or run expensive queries | Named queries with a JSON Schema result, `complete` and `frontier`, root hash in every answer | Sorted, size-capped; same root hash and arguments give same bytes |
| Human reviewer | Understand what changed and why | `why`, `impact`, `suspect` CLI; SARIF in an editor; OKF pages; diagrams | Same as above; every line carries a `repo://` id |
| Human explorer | Ad hoc questions | SQLite CLI or any SQL browser on the index; optional Cypher export | Read-only file; export is one-way |

### 5.2 Which language: evidence and honest limits

Evidence gathered:
- Text2Cypher (arXiv 2412.10064, opened): a dataset of 44,387 instances (39,554 train, 4,833 test) assembled because LLMs "often struggle" to produce Cypher; fine-tuned models improved Google-BLEU and exact match over their baselines. The improvement in exact match for GPT-4o was about 0.01 and for Llama 3.1 8B about 0.11 (values as returned by a summarising fetch tool, treat as approximate).
- Text-to-SQL, BIRD leaderboard (opened, values as returned): top execution accuracy 78.10 on the dev set (2026-08-22) and 82.39 on the test set (date not confirmed on a leaderboard row), human 92.96.
- These two are not comparable: different benchmarks, different metrics (exact match and BLEU versus execution accuracy), different schemas. **I found no study comparing LLM reliability on SQL against Cypher or GQL for the same task. The claim "SQL is more reliable for LLMs than Cypher" is UNVERIFIED and is not used.** The dossier reached the same conclusion.
- What the two do show, jointly: even the best current systems on a public benchmark are wrong on roughly one query in five, on schemas with database values and evidence hints they were given. A wrong query in an assurance graph is a silently wrong verdict.

Therefore the decision does not rest on which language models write better. It rests on determinism and on removing free-form query text from the agent path:

| Criterion | SQL (SQLite) | Cypher / GQL | SQL/PGQ | Datalog |
|---|---|---|---|---|
| Zero-install on Windows, macOS, Linux | yes (stdlib) | no (engine) | not in SQLite; DuckPGQ is a research extension | Soufflé: no Windows page |
| Row order defined | only with `ORDER BY` (docs) | only with `ORDER BY` (Neo4j docs) | inherits SQL | set semantics |
| Recursion that terminates on cycles | `UNION` over node column, measured (Section 2.2) | Ladybug, measured (Section 2.4): the default variable-length pattern needs a bound, silently truncates below the true depth, enumerates paths and exhausted a 128 MB pool at bound 30 on 1,000 edges; the `SHORTEST` form matched the reference. Neo4j not run | engine-specific | native |
| Negation | `NOT EXISTS`, stratify by convention | `WHERE NOT` patterns | inherits SQL | stratified, checked by engine |
| Standard | SQL:2023 | ISO/IEC 39075:2024 published April 2024 per gqlstandards.org | SQL:2023 Part 16 per the same site, graph pattern matching "technically stable since mid 2022" | none |
| Already in the repo | yes (ADR-0000) | no | no | no |

### 5.3 Decision

1. **Rules are SQL files** with a stratum, declared `reads`, and a witness column. The loader (rule-model aspect; see [0095-weave-lint-compile-rules.md](../../adr/0095-weave-lint-compile-rules.md)) rejects negation in a recursive stratum. This is Datalog-lite: semantics of stratified Datalog (as described in the dossier, from Wikipedia-level sources, not re-read here) with a SQL syntax.
2. **Cypher/GQL is never an input.** It is a target dialect of the export (Section 7). GQL Part on pattern matching being aligned with SQL/PGQ means that if SQLite or a future stdlib gains SQL/PGQ, the named queries can be re-expressed without changing their contract. PostgreSQL's SQL/PGQ status is UNVERIFIED (the documentation URL I tried returned 404 and the web-search budget is exhausted).
3. **Soufflé differential oracle (optional, phase 3, Linux, macOS, WSL):** export the positive fragment (`edge` facts, closure, coverage rules) as `.facts` and `.dl`, run, and compare result sets with the SQLite results. Benefit: an independently implemented fixed-point check on the closure semantics that would otherwise only be checked against our own `impact.closure`. Cost: a second rule syntax to keep in step, limited to the positive fragment plus stratified negation. Not built now; revisit at about 30 rules or on the first disagreement between rule authors and rule behaviour.

### 5.4 Agent query catalogue (this lane defines; agents lane serves)

Every query is parameterised, read-only, bounded, sorted, and returns `{root, index_key, complete, frontier, rows}`. `frontier` and `complete` follow `impact.closure`. **Implementation split:** `impact` with a budget is computed by the Python BFS (the `impact.closure` algorithm with a parent pointer per node), because the budget truncates in FIFO visit order and a recursive CTE has no defined order (Section 2.2: 33 of 300 graphs differed). SQL computes only the unbounded set closure and joins.

| Query | Arguments | Result | Bound |
|---|---|---|---|
| `node` | `id` | node, hash, method, outgoing and incoming counts by type | one row |
| `neighbors` | `id`, `direction`, `types[]`, `limit` | sorted edges | `limit` <= 200 |
| `impact` | `roots[]`, `edge_types[]`, `budget` | affected ids, frontier, one witness path per affected id (Python BFS) | `budget` <= 5,000 |
| `why` | `id` | canonical witness plus rule id and premises | one path |
| `violations` | `rule_id`, `scope` | rows with finding id, subject, witness | `limit` <= 500 |
| `link_status` | `link_id` or `subject` | status with digests | one row |
| `context` | `id`, `budget_tokens` | ranked neighbourhood (heuristic, labelled) | budget |

An escape hatch `sql(text)` exists only behind an owner flag and applies, in order: `mode=ro` URI open (stdlib docs: `sqlite3.connect("file:...?mode=ro", uri=True)`); `PRAGMA query_only=ON` (SQLite docs: prevents data changes, though the database is "not truly read-only"); an authorizer callback that denies everything except reads of `node`, `edge`, `finding` (`set_authorizer`, stdlib docs); a progress handler that aborts after a fixed instruction count (`set_progress_handler`: "a non-zero value ... will terminate the currently executing query"); and a row cap. It is off by default because a free-form query is exactly the failure Section 5.2 documents. The safety stack is composed from documented APIs; I did not run an attack against it, so it is DESIGN, not a security claim, and it is not a sandbox against an agent with the owner's OS permissions (AGENTS.md).

## 6. Provenance: are semirings worth it?

**Answer: use the theory to specify what a witness is; implement only the two semirings we need; do not store polynomials.**

| Semiring | Where it appears in EIJA | Implementation | Benefit | Cost |
|---|---|---|---|---|
| Boolean (B, or, and) | Reachability, coverage, "is affected" | `impact.closure`, recursive CTE | Already the kernel semantics. Every gate question is "does a derivation exist", which is a Boolean question; the paper's Prop. 5.4 (Datalog over B-relations is standard Datalog on the support) is the sanity check that the Boolean reading is the ordinary one | none |
| Tropical (N with infinity, min, +) | Shortest witness length (depth of impact): the tropical tag of a node is the minimum over derivations of the sum of edge tags, with every base edge tagged 1 (paper Definition 5.1 with K = tropical) | BFS level | The "distance" shown next to an affected node; the canonical witness is a shortest one. The paper gives no evaluation procedure for the tropical case (Section 2.5), so this is computed by BFS and checked against brute force, not derived from the paper | none |
| Why-provenance, P(X) with union and intersection | "Which base facts support this derived fact" | one canonical witness plus, for coverage, the list of covering edges | Every finding is re-checkable: re-run the closure on the witness subgraph alone and recover the fact (test) | one parent pointer per visited node (measured: closure plus witness in Python totals 0.019 s at 10^4 edges and 0.17 s at 10^5 in the SQL-run script, and 0.002 s and 0.049 s in the Python baseline, Section 2.1b; the increment over the closure alone is about zero) |
| N[X] polynomials, formal power series | "How many independent derivations", full how-provenance | not stored | None that a gate uses. The one quantity that looks like it is redundancy of evidence, which is a minimum vertex cut between requirement and evidence, not a derivation count (aspect graph-metrics) | Infinite in cyclic graphs (the paper's own example); needs omega-continuity; blows up |

Limits, stated exactly: the paper's results are for positive relational algebra and positive Datalog; negation is listed by the authors as future work. Missing-evidence findings (`requirement with no verifying test`) are negation, so a semiring has no explanation for them. Their witness is the closed-world scope that was searched: the rule id, the set of `verifies` links examined, and the root hash. That is a statement about what was looked at, not a derivation.

## 7. Neo4j and Cypher: how supported

**Position.** An optional one-way generated projection for people who want to explore in a graph browser. Never in the trust path, never a runtime requirement, never a dependency of any extra.

**Why not more.** GPL-3.0 server (an Apache-2.0 package must not bundle or link it); JVM (Java SE 21 or 25); on Windows the Community-relevant statement is "Windows 11" for personal use and development only; a stateful store outside git; row order undefined without `ORDER BY`; no speed gain at our scale (Section 2.1).

**Contract of the export (`eijagraph export cypher`; export-adapters aspect, number not frozen):**

| Item | Rule |
|---|---|
| Files | `nodes.csv`, `edges.csv` (one file per link type if the engine needs typed relationship tables), `load.cypher`, `README.md` with resource caps |
| Content | Sorted by the same total keys as the canonical dump; UTF-8, LF; header row fixed; ids are the `repo://` strings; the root hash is recorded in `README.md` and as a graph property |
| Determinism | Byte-identical for a given root hash; golden test on a fixture graph; a change in the exporter version is a new file header |
| Load path for Neo4j | `LOAD CSV` in a generated Cypher script, one statement block per link type in sorted order (the syntax `LOAD CSV [WITH HEADERS] FROM url [AS alias] [FIELDTERMINATOR char]` is from the Neo4j getting-started page; the uniqueness-constraint and relationship-creation statements are UNVERIFIED until the export test runs against a pinned Neo4j, NOT_RUN today). The operations manual says full `neo4j-admin database import` is "used to import data into a non-existent or empty database" and needs the database offline with direct server access; its CSV header conventions were not on the pages I could read, so that path is UNVERIFIED and not used |
| Load path for an embedded engine | Ladybug `COPY Node FROM 'nodes.csv' (header=false)` and `COPY Prop FROM ...` loaded 100, 1,000 and 2,000-edge graphs in 0.15 to 0.2 s under the caps of Section 2.4 (MEASUREMENT); a single relationship table `Prop` was used in the probe, the exporter would create one per link type |
| Query hygiene | README gives the Ladybug reachability query in its `* SHORTEST 1..N` form with N at least the longest chain (the default form truncates silently below the true depth and exhausted the pool at bound 30, Section 2.4), a `LIMIT`, and states that without `ORDER BY` row order is undefined (3 distinct orders over 3 shuffled loads, and the Neo4j manual says the same) |
| Import | **None.** The only "import" is a differential check: load the export into an engine, run the reference closure, compare with the SQLite result. Missing engine gives NOT_RUN. Data flowing back from an engine into `graph/links` would make the engine a source of truth and is refused |

Revisit triggers (from ARCHITECTURE section 1, all measurable): index above about 10^7 edges; rebuild over an agreed time budget on the reference PC; a query class beyond joins and recursion (weighted paths, community detection) that a library cannot cover; concurrent multi-user editing.

## 8. OKF pages and the graph

Facts (OKF v0.2 SPEC, opened): "The specific kind (parent/child, references, joins-with, depends-on) is conveyed by the surrounding prose, not by the link itself." "Consumers MUST tolerate broken links." `stale_after` is "An absolute instant. A concept is stale when `now >= stale_after`." Only `type` is required. The spec says nothing about hashes or determinism. The okf lane's ADR-0045 already makes broken links a defect for its own generated bundle, and ADR-0046 fixes hash methods and STALE semantics by digest.

| Question | Decision |
|---|---|
| Is an OKF page a graph node? | Yes, type `okf_page`. Its identity is `repo://okf/...md`. |
| What does its `content_hash` cover? | **Only the human-owned parts** (frontmatter keys the generator does not write, and text outside `okf:generated` blocks), by a proposed method `okf-human-v1` (DESIGN; needs okf lane agreement). Generated blocks and `sources[].sha256` are projections of other nodes; hashing them would make the page depend on the graph that projects it. Test: deleting every generated block leaves the root hash unchanged. |
| Which edges come from a page? | `documents` from the frontmatter `resource` and `sources[].resource` (derived, exact, generated by the okf lane and re-derived by us from the same fields). Prose links between pages are **not** edges (untyped); the okf gate already checks they resolve. Typed relations among concepts are authored in `graph/links/*.jsonl`. |
| How do typed links reach a reader? | The okf lane already emits an `okf:generated:begin links` block per page (currently `_No generated cross-references._`). Weave supplies, for a node id, sorted lines of the form: `- <link type>: [<title>](<relative path to page>) <code>repo://...</code> sha256:<12>`. Where the target has no page (a test or a line-range), the URI appears in a code span, which the okf link checker does not treat as a link. Ordering, wording and paths are pure functions of the graph. |
| Time | `generated.at`, `verified.at`, `stale_after` are excluded from every hash; freshness is by digest; if `stale_after` is ever used, `now` is an explicit recorded input, not read from the clock. |
| Who owns what | okf lane: page generation, STALE gate, `sync`. Weave: typed link sidecar, link status, the `links` block content, the projection-independence test. Neither edits the other's files. |

Two points on the rule above (DESIGN, not measured).
1. **Why the exclusion is needed, and how much of it.** The feedback loop is only through the `links` block: its text is a function of graph edges, so if it entered the page's own hash, a new link would change the page hash, which is an input to link status. The `facts` block is generated from sources, not from the graph, so excluding it is not needed for termination; it is excluded here for simplicity, at the price that a hand edit inside a generated block is invisible to the graph. The okf gate's `drift` check (ADR-0045) catches that case. A narrower method (exclude only graph-derived blocks) is an option for the okf lane to choose.
2. **Open question for the okf and link-status aspects.** okf `sync` re-baselines `sources[].sha256` and drops `verified` (ADR-0046), which is a machine re-baseline. The link-status design says that only a human ledger entry clears SUSPECT. For links from a page to its generated sources both hold if `documents` edges from `sources[]` are marked origin `derived` (recomputed by `sync`), and the human-ack rule applies to declared links only. That split is not yet agreed with the okf lane.

## 9. Operational cost and licence compatibility for OSS adopters

| Concern | Chosen design | Cost for an adopter | Alternative cost (for comparison) |
|---|---|---|---|
| Install | Python 3.11+ only; `sqlite3` is in the standard library on all three platforms | none | Ladybug: 5.9 MB wheel; DuckDB: up to 32.8 MB wheel; Neo4j: a JVM and a server |
| Memory | Index 2.8 MB at 10^4 edges and 300 MB on disk at 10^6 at the specified width (Section 2.1c); process footprint not measured for SQLite or the Python baseline | tiny at the expected size | Ladybug 0.20.4: about 50 MB baseline plus a pool the caller must cap; the effect of the default pool was reported only as an unrecorded anecdote (Section 2.4) |
| Disk | Snapshots named by root hash, `graph gc` keeps 3 | up to 3 files | Neo4j: 10 GB minimum for development systems per its requirements page |
| Windows | stdlib; no native build; the whole measurement in this document ran on Windows 11 | none | Neo4j Community: Windows 11 development only; Soufflé: Windows not mentioned |
| macOS, Linux | stdlib | none, but **POSIX byte-identity is NOT_RUN** (D-20) | n/a |
| Rebuild time | 10^4 edges: build 0.03 to 0.7 s narrow (0.08 s at the specified width, journal off) plus root hash 0.07 to 0.15 s plus extraction 0.06 to 0.12 s (stdlib); PREDICTION total under 1.5 s for this repo. 10^6 edges: build 5 to 12.5 s narrow and 20 s wide, plus root hash 8.5 to 10.8 s narrow and 12.6 s wide | fine | n/a |
| Licence of the package | Apache-2.0; every dependency is stdlib or in the `graph` extra (`rfc8785` Apache-2.0 per SPDX, `jsonschema` MIT per PyPI) | none | GPL, SSPL, BSL servers cannot be bundled; GPL server is acceptable only as a separate process a user starts |
| Reproducibility for adopters | Snapshot is rebuildable from git; manifest pins extractor versions | none | A Neo4j data directory is not rebuildable from git without a loader |

## 10. Risks, unverified items and revisit triggers

Unverified or not measured:
- Real graph size (no extractor yet); the 10^4 figure is a PREDICTION from counts.
- SQLite behaviour on macOS and Linux, and on SQLite versions below 3.49.1. The queries use only recursive CTEs (3.8.3), `WITHOUT ROWID` (SQLite 3.8.2, 2013-12-06 or later, per [withoutrowid.html](https://www.sqlite.org/withoutrowid.html), opened 2026-09-29), `VACUUM INTO` in the probe only (not needed by the design). A minimum-version test on the oldest SQLite that supported Python versions ship is NOT_RUN.
- Ladybug on the current release 0.21.0 (measurements are for 0.20.4); Ladybug memory cause and the path semantics of its variable-length patterns; the 8.4 GB anecdote; Ladybug on any graph above 2,000 edges; the memory of its `SHORTEST` form at scale; anything about Neo4j (not run, by design; the export script syntax for Neo4j is unverified).
- The 10^7-edge extrapolation in Section 2.1a (PREDICTION), the cause of the slope above 1, and the peak process memory of the SQLite and Python-baseline builds at 10^6 (not measured).
- Whether SQL rule files improve authoring or inspection over Python rules (DESIGN judgement; PLAN H16).
- Whether an open reader blocks replacing an index file on Windows (Section 4.3; the design avoids the case).
- LLM reliability difference between SQL and Cypher (no comparative study found; the pre-registered comparison is in PLAN.md and is NOT_RUN).
- PostgreSQL SQL/PGQ status (documentation URL 404; web-search budget exhausted); Apache AGE architecture.
- The reading of licences is engineering judgement; the owner decides before shipping any GPL, LGPL, EPL or MPL component, even as a separate process.

Revisit triggers: index above about 10^7 edges; full rebuild over the budget in PLAN.md on the reference PC; a needed query class beyond joins and recursion; a demonstrated safe memory cap and a measured benefit for an embedded graph engine at realistic size; an SQL/PGQ implementation in a stdlib-bundled or pure-wheel engine with Windows support.

## 11. Sources (accessed 2026-09-29)

| Topic | URL | Used for |
|---|---|---|
| SQLite recursive CTE | https://www.sqlite.org/lang_with.html | `UNION` dedupe and cycles; undefined order without `ORDER BY` (FIFO in the current implementation); no aggregates or window functions in the recursive select; `LIMIT` semantics |
| SQLite WITHOUT ROWID | https://www.sqlite.org/withoutrowid.html | "SQLite version 3.8.2 (2013-12-06) or later is necessary" |
| SQLite release 3.8.3 | https://www.sqlite.org/releaselog/3_8_3.html | CTE support added, dated 2014-02-03 |
| SQLite aggregate functions | https://www.sqlite.org/lang_aggfunc.html | "The order of the concatenated elements is arbitrary unless an ORDER BY argument is included" |
| SQLite pragmas | https://www.sqlite.org/pragma.html | `query_only`, `trusted_schema`, `max_page_count` |
| Python sqlite3 | https://docs.python.org/3/library/sqlite3.html | `set_authorizer`, `set_progress_handler`, `mode=ro` URI, `serialize` |
| DuckDB WITH | https://duckdb.org/docs/current/sql/query_syntax/with.html | `USING KEY`; list-based cycle checks; no `CYCLE` mention |
| DuckPGQ | https://github.com/cwida/duckpgq-extension | "a research project and a work in progress"; install from community |
| Ladybug | https://github.com/LadybugDB/ladybug ; PyPI JSON `ladybug` | MIT; formerly Kuzu; measured on v0.20.4; PyPI 0.21.0 uploaded 2026-09-28; wheel sizes |
| Kuzu | `gh api repos/kuzudb/kuzu` | archived, last push 2025-10-10 |
| Neo4j | https://github.com/neo4j/neo4j (LICENSE.txt head) ; https://neo4j.com/licensing/ ; https://neo4j.com/docs/operations-manual/current/installation/requirements/ ; https://neo4j.com/docs/cypher-manual/current/clauses/order-by/ ; https://neo4j.com/docs/operations-manual/current/import/ | Licence, JVM and Windows statements, no row-order guarantee, import prerequisites |
| GQL | https://www.gqlstandards.org/ | publication 2024-04-17; alignment with SQL/PGQ |
| Text2Cypher | https://arxiv.org/abs/2412.10064 ; https://arxiv.org/html/2412.10064 | dataset and fine-tuning results |
| BIRD | https://bird-bench.github.io/ | leaderboard figures as returned |
| Provenance semirings | https://www.cs.ucdavis.edu/~green/papers/pods07.pdf | Definitions and propositions in Sections 2.5 and 6 |
| OKF v0.2 | https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md | link and staleness statements |
| Soufflé install | https://souffle-lang.github.io/install | platforms listed |
| Repositories (licence, archived, pushed) | `gh api repos/<owner>/<repo>` for neo4j/neo4j, LadybugDB/ladybug, kuzudb/kuzu, duckdb/duckdb, cwida/duckpgq-extension, apache/age, souffle-lang/souffle, memgraph/memgraph, FalkorDB/FalkorDB, facebookincubator/Glean, cozodb/cozo, dolthub/dolt, typedb/typedb, vmware-archive/differential-datalog, Qiskit/rustworkx | Licence SPDX, archived flag, last push |
| Packages | https://pypi.org/pypi/{ladybug,duckdb,neo4j,rustworkx,networkx,rfc8785,jsonschema,pyoxigraph,kuzu}/json | Versions, licence metadata, `requires_python`, wheel platforms and sizes |
| Neo4j LOAD CSV | https://neo4j.com/docs/getting-started/data-import/csv-import/ ; https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/ | `LOAD CSV` syntax; full import needs a "non-existent or empty" database; header conventions not visible on either page |
| In-repo | `src/eija_studio/domain/impact.py`; okf worktree ADR-0045, ADR-0046, `quality/okf/codelink.py`; agents worktree ADR-0041; `graph/bench/storage_query_probe.py`; `graph/bench/ladybug_probe.py`; results `graph/bench/results/storage-query-probe.json`, `python-baseline-and-wide-ddl.json`, `storage-query-probe-run-b-timing.json`, `ladybug-capped-probe-{100,1000,2000}-edges.json` | Measurements and interfaces |
| Dossiers | `docs/weave/research/*.md` | Prior measurements and licence readings cited as "dossier" |
