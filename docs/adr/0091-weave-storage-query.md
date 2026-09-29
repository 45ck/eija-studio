# ADR-0091: Storage and query: git files are the truth, a disposable SQLite index answers named queries

* Status: proposed
* Date: 2026-09-29 (revised after audit the same day)
* Lane: weave (aspect storage-query)

## Context and problem statement

Weave ties code, UI, diagrams, language, requirements, tests, proofs, evidence and decisions into one typed graph checked by a compiler-like rule set. The graph needs a store and a query surface for three audiences: rule authors, agents (through MCP) and humans. The choice is between files in git as the source of truth with a rebuildable embedded index, and a graph database (Neo4j or another) as the store. The kernel doctrine is that identical inputs give byte-identical outputs, that a missing prerequisite is `NOT_RUN` and never `PASS`, and that agents propose while the kernel checks and the owner decides. Design and evidence: [storage-and-query.md](../weave/design/storage-and-query.md). Benchmark method: [graph/bench/PLAN.md](../../graph/bench/PLAN.md).

Numbering note: `docs/weave/ARCHITECTURE.md` section 11 allocates 0091 to canonical serialisation and 0096 to storage and query semantics. This record was assigned 0091 by the aspect brief. The integrator must reconcile the two tables; the content of the ARCHITECTURE 0091 (RFC 8785 subset and hashing) is a dependency of this record, not part of it. Other numeric cross-references in the ARCHITECTURE table (0090, 0092, 0095, 0097, 0099, 0109) do not match the files present in `docs/adr/` (for example 0095 is lint-compile-rules and 0099 is agent-interface), so this record refers to aspects by name and file path until the numbers are frozen.

## Decision drivers

* Determinism: a rebuild from a clean checkout must give equal root hashes; result order must not depend on insertion order, engine internals or platform.
* Trust path: no second stateful store outside git that can drift from the sources (the failure class recorded by the owner's ProofMap Lite experiments).
* Scale: measured, not assumed. About 10^4 edges is the predicted size of this repository (from counts); 10^6 is headroom.
* Operational cost for OSS adopters on Windows, macOS and Linux with 16 GB machines: install size, memory behaviour, runtime prerequisites.
* Licence: EIJA is Apache-2.0; a GPL, SSPL or BSL component must not be bundled or linked.
* Agent reliability: an agent must not be able to produce a silently wrong verdict from a mis-written query.
* OSS first (ADR-0016): adopt, and write only EIJA-specific glue.

## Considered options

Storage:

* A. Files in git as truth plus a disposable stdlib SQLite index, named by its root hash (chosen).
* B. Neo4j (Community) as the graph store, git as export.
* C. An embedded graph engine (Ladybug, successor of the archived Kuzu) as the index.
* D. DuckDB (with or without the DuckPGQ extension) as the index.
* E. Server graph or Datalog stores (Memgraph, FalkorDB, TypeDB, Apache AGE, Dolt) as the store.
* F. In-memory Python only (dicts, or rustworkx or networkx), no database. Measured head-to-head in the design, Section 2.1b.

Query language for rules and agents:

* Q1. SQL violation queries for rules; named parameterised queries for agents; Cypher/GQL export only (chosen).
* Q2. Cypher or GQL as the input language for agents and rules.
* Q3. SQL/PGQ (`GRAPH_TABLE`) as the input language.
* Q4. A Datalog engine (Soufflé, Cozo) as the rule engine.
* Q5. Free-form SQL for agents.

Provenance:

* P1. One canonical witness per fact plus rule id and premises; semirings as specification (chosen).
* P2. Full provenance polynomials N[X] per derived fact.
* P3. No provenance.

## Decision outcome

Chosen: A with Q1 and P1.

1. **Truth and index.** Committed inputs are the sources, `graph/links/*.jsonl`, `graph/ledger.jsonl` and an attestation `graph/manifest.json`. The index is `graph/.index/graph-<root12>-<key12>.sqlite3` (gitignored by the existing `*.sqlite3*` pattern; `graph/.index/` to be added), built in sorted order, opened read-only, garbage-collected. The graph's identity is the root, the SHA-256 of a canonical sorted dump of `node` and `edge`. The file also holds findings, provenance and proposals, which depend on the rule set, schema, engine and extractor pins that the root does not cover, so the file is named and reused by an **index key** = SHA-256 of (root, rule-set hash, schema version, engine version, extractor-pins hash); the root and the key inputs are stored in a `meta` table and a mismatch refuses the file. A changed rule with an unchanged graph gives a new key and recomputed findings. The file's bytes are never compared.
2. **Query surface.** Rules are SQL files with a declared stratum and reads; the loader rejects negation inside a recursive stratum; recursion selects only the node column with `UNION`; every result query ends in a total `ORDER BY`; `LIKE` is banned. Agents get named, parameterised, bounded, sorted queries with typed results carrying the root hash, the index key, `complete` and `frontier`. Budgeted `impact` (and its `frontier`) is computed by the Python BFS that copies `impact.closure`, because the budget truncates in FIFO visit order and a recursive CTE has no defined order (a SQL `LIMIT` differed from the kernel's truncated set in 33 of 300 random graphs on SQLite 3.49.1); SQL computes only the unbounded set closure (0 mismatches against the kernel in 300 random graphs) and joins. A free-form `sql(text)` exists only behind an owner flag with read-only open, `query_only`, an authorizer, a progress handler and a row cap. Cypher and GQL appear only as an export dialect.
3. **Provenance.** One canonical witness per fact (lexicographically smallest shortest path, which the existing sorted FIFO closure already produces when parents are recorded), plus rule id and premises for derived facts. The Boolean and tropical semirings are used; polynomials are not stored. Missing-evidence findings carry the searched scope, not a derivation.
4. **Neo4j and Cypher.** An optional one-way export (sorted CSV, load script, golden test) run by a person as a separate process. The only import is a differential check that an engine loaded from the export reproduces the SQLite closure; absence reports `NOT_RUN`. No data flows back.
5. **OKF.** OKF pages are a get-only projection. The graph excludes generated blocks from a page's hash (proposed method `okf-human-v1`, needs the okf lane's agreement) so the projection cannot feed its own source. Typed links live in the sidecar; the okf `links` block is generated from it.

### Why the alternatives lose (evidence, all MEASUREMENT on Windows 11, Python 3.12.10, SQLite 3.49.1 unless labelled)

* **Speed does not justify an engine, and it does not justify SQLite over plain Python either.** On a synthetic typed graph (two full runs, same machine, narrow tables) the slowest query at 10^6 edges (impacted-and-untested, recursion then negation) took 3.8 to 4.4 s; every query at 10^4 edges took at most 22 ms; the closure of 5 roots took 2.5 to 3.6 s at 10^6 with text ids and 1.1 to 1.7 s with integer-interned ids. The same queries in dicts and sets, with no database, took 0.75 s (closure), 0.75 s (stratified violation) and 0.0055 s (anti-join) at 10^6, with answers asserted equal to SQLite's (design 2.1b): 3 to 10 times faster. **The choice of SQLite over option F therefore rests on authoring and inspection, not speed:** one declarative, diffable statement per rule, any SQL tool for a human, a rule language that is not agent-writable Python code. That benefit is a DESIGN judgement and is unmeasured (PLAN H16); if it does not survive the rule-authoring evaluation, the fallback is Python rules with SQLite kept as the exploration export. Width caveat: the timing runs used 3 and 4 column tables; at the specified 5 and 7 columns with 64-hex digests the file is about 1.7 times larger (300 MB at 10^6 edges), the build 20 s and the dump plus root hash 12.6 s at 10^6 (design 2.1c). Run-to-run spread on the shared PC was up to 1.7 times for query timings and 5.4 times for file builds, so only larger differences count. DuckDB is faster for scans (0.44 to 0.63 s bulk load, 43 to 83 ms anti-join at 10^6) but is a wheel of up to 32.8 MB with about 190 ms extra import time, for no needed gain.
* **The file is not the identity.** Six builds of one 2,000-edge graph in five insertion orders gave five distinct SQLite file hashes and one canonical-dump hash. Hence: identity by dump.
* **Order must be explicit.** An unindexed scan on rowid tables gave 8 distinct orders over 8 shuffled loads; the SQLite documentation says extraction order without `ORDER BY` is undefined; the Neo4j documentation says "Unless ORDER BY is used, Neo4j does not guarantee the row order of a query result".
* **Recursion must select only the node column.** `UNION` over the node column stopped by itself on a cycle (4 rows); `UNION` carrying a path or depth column, and `UNION ALL`, ran to the 1,000-row guard. Witnesses are therefore computed outside SQL.
* **An embedded graph engine offers an easy way to a wrong answer, and needs caps.** All on Ladybug 0.20.4 (PyPI has 0.21.0 since 2026-09-28; not re-run). Under explicit caps (128 MB pool, 1 thread, 1 GB max db size, 500 MB RSS watchdog; graphs of 100, 1,000 and 2,000 edges): the default variable-length pattern with bound 30 failed on 1,000 and 2,000 edges with "Buffer manager exception: Unable to allocate memory! The buffer pool is full and no memory could be freed!" (peak RSS 165 to 169 MB, which is the 50 MB baseline of every successful query plus a full 128 MB pool, so the cap held and the failure was clean); bound 3 returned an incomplete set without error (88 of 217 and 366 of 462 reference nodes missing); the exact bound worked but took 0.60 s at 2,000 edges; the `* SHORTEST 1..N` form equalled the reference closure in 8 to 24 ms at 50 MB. The internal cause is UNVERIFIED. An unrecorded, non-reproducible anecdote reported by the coordinator (an uncapped 10,000-edge run at 8.4 GB resident) motivated the caps; it is NOT evidence and no decision rests on it. Conclusion: an export target only, with the caps and the `SHORTEST` form documented; not a default dependency, because the reproducible items (silent truncation, path enumeration, failure at bound 30) make a natural-looking query wrong or slow.
* **Neo4j.** Community is GPL-3.0 (LICENSE.txt: "GNU GENERAL PUBLIC LICENSE Version 3"); needs Java SE 21 or 25; Windows 11 is "personal use and development only"; a stateful store outside git. Full `neo4j-admin database import` requires a "non-existent or empty" offline database.
* **Language reliability has no comparative evidence.** Text2Cypher (arXiv 2412.10064) and the BIRD text-to-SQL leaderboard (best 78.10 dev, 82.39 test, human 92.96) use different metrics and schemas and cannot be compared. The claim that SQL is more reliable than Cypher for LLMs is UNVERIFIED and is not used. The decision rests on determinism and on removing free-form query text from the agent path.
* **Semirings.** Green, Karvounarakis and Tannen (PODS 2007), read as text: polynomials are the most general provenance for positive relational algebra (Theorem 4.3), Datalog needs omega-continuous semirings and can have infinitely many derivations, and negation is listed as future work. Our cyclic graphs and our negation-based findings are exactly the cases outside that theory. Witness correctness: 600 random graphs, 3,373 paths, 0 mismatches against a brute-force oracle and under shuffled edge order.

### Consequences

* Good: zero new runtime dependencies for the core; Windows-native; rebuild equals clean is testable; agents cannot mis-write a query; humans can open the index in any SQL tool; Neo4j users are served without trust-path cost.
* Good: every finding is re-checkable from its witness.
* Bad: no native graph pattern language for humans (mitigated by the CLI, OKF pages and the export). Rule authors write recursive SQL, which is awkward beyond the positive fragment.
* Bad: the root hash is Python-bound above about 10^5 edges (8.5 to 10.8 s at 10^6 with narrow tables, 12.6 s at the specified width); it must become a Merkle tree over partitions before then. Extrapolation, PREDICTION: closure of 5 roots would take about 40 to 78 s at 10^7 edges (the cause of the slope above 1 between 10^5 and 10^6 is unmeasured), which is why that size is the revisit trigger.
* Bad: identity by dump hash means readers cannot rely on file equality; tools must not diff the SQLite file.
* Bad: POSIX and macOS behaviour, older SQLite versions, and the real graph size are not measured (NOT_RUN or PREDICTION). No index-key test exists yet because `eijagraph.store` does not (NOT_RUN).
* Revisit when (all measurable): index above about 10^7 edges; full rebuild over the budget in PLAN.md on the reference PC; a required query class beyond joins and recursion; an embedded graph engine shown to stay under 256 MB at 10^5 edges with the `SHORTEST` form and a measured benefit; SQL/PGQ available in a Windows-capable pure-wheel engine.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| SQLite via stdlib `sqlite3` (public domain) | Adopted as the store and recursive-CTE engine. Only the node and edge DDL, the load order, the canonical dump and the rule loader are custom. | Replaceable behind `eijagraph.store`; DuckDB is the measured alternative for analytics |
| Neo4j Community (GPL-3.0), Neo4j Python driver (Apache-2.0 AND Python-2.0) | GPL server, JVM, second stateful store, undefined order; used only for the optional export check | Export CSV and Cypher script; nothing to replace |
| Ladybug (MIT), Kuzu (MIT, archived) | Measured on 0.20.4 only (0.21.0 exists, not re-run): default variable-length pattern silently truncates below the true depth, enumerates paths (0.60 s against 24 ms at 2,000 edges) and fails at bound 30 under a 128 MB pool; the 8.4 GB uncapped figure is an unrecorded anecdote and is not used as a reason; export target only, with caps and the `SHORTEST` form | Pin and cap in the export README; drop if unmaintained |
| DuckDB (MIT), DuckPGQ (MIT, "research project") | Faster scans, but 32.8 MB wheel and no needed gain; PGQ extension needs an install-time download and is research-stage | Optional analytics extra later |
| Memgraph (BSL 1.1), FalkorDB (SSPL), Apache AGE, TypeDB (MPL-2.0), Cozo (MPL-2.0, stale), DDlog (archived) | Licence, server architecture or maintenance status | none |
| Soufflé (UPL-1.0) | No Windows in its install page; a second rule syntax | Optional differential oracle on Linux, macOS, WSL, phase 3 |
| rustworkx (Apache-2.0), networkx (BSD-3), plain Python dicts (option F) | Plain Python was measured faster than SQLite (design 2.1b) and is used for budgeted closure and witnesses; not used as the sole store for authoring and inspection reasons (DESIGN, unmeasured); networkx 3.7 needs Python 3.12 or later; import 1.4 to 4 s | Test oracle only for the libraries, pinned below 3.7 |
| Provenance semiring libraries | None adopted; the theory is used to specify witnesses | Own witness code (about 40 lines, tested against a brute-force oracle) |
| EIJA-specific: `eijagraph.store` (schema, load, dump, root hash), `eijagraph.rules` loader (stratification, lint), query catalogue, Cypher/CSV exporter | No OSS tool provides a byte-deterministic typed store with per-rule witnesses and an agent-safe query set | Remains custom; the store engine is not |
