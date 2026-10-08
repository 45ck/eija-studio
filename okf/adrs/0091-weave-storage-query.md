---
type: Architecture Decision Record
title: 'ADR-0091: Storage and query: git files are the truth, a disposable SQLite index answers named queries'
description: Weave ties code, UI, diagrams, language, requirements, tests, proofs, evidence and decisions into one typed graph checked by a compiler-like rule set.
resource: repo://docs/adr/0091-weave-storage-query.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0091-weave-storage-query.md
  title: 0091-weave-storage-query.md
  hash_method: lf-sha256-v1
  sha256: 344815fb627e5009e461256d919e8b9ce7500dc3aef593d28a53b4436ee34254
notes_baseline: 4898e1883c187d448262d511ea230318dab5cd148598f8c953c9726862436a2e
---

# ADR-0091: Storage and query: git files are the truth, a disposable SQLite index answers named queries

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 (revised after audit the same day) |
| Lane | weave (aspect storage-query) |
| Source | `repo://docs/adr/0091-weave-storage-query.md` |

## Decision outcome (verbatim)

> Chosen: A with Q1 and P1.
>
> 1. **Truth and index.** Committed inputs are the sources, `graph/links/*.jsonl`, `graph/ledger.jsonl` and an attestation `graph/manifest.json`. The index is `graph/.index/graph-<root12>-<key12>.sqlite3` (gitignored by the existing `*.sqlite3*` pattern; `graph/.index/` to be added), built in sorted order, opened read-only, garbage-collected. The graph's identity is the root, the SHA-256 of a canonical sorted dump of `node` and `edge`. The file also holds findings, provenance and proposals, which depend on the rule set, schema, engine and extractor pins that the root does not cover, so the file is named and reused by an **index key** = SHA-256 of (root, rule-set hash, schema version, engine version, extractor-pins hash); the root and the key inputs are stored in a `meta` table and a mismatch refuses the file. A changed rule with an unchanged graph gives a new key and recomputed findings. The file's bytes are never compared.
> 2. **Query surface.** Rules are SQL files with a declared stratum and reads; the loader rejects negation inside a recursive stratum; recursion selects only the node column with `UNION`; every result query ends in a total `ORDER BY`; `LIKE` is banned. Agents get named, parameterised, bounded, sorted queries with typed results carrying the root hash, the index key, `complete` and `frontier`. Budgeted `impact` (and its `frontier`) is computed by the Python BFS that copies `impact.closure`, because the budget truncates in FIFO visit order and a recursive CTE has no defined order (a SQL `LIMIT` differed from the kernel's truncated set in 33 of 300 random graphs on SQLite 3.49.1); SQL computes only the unbounded set closure (0 mismatches against the kernel in 300 random graphs) and joins. A free-form `sql(text)` exists only behind an owner flag with read-only open, `query_only`, an authorizer, a progress handler and a row cap. Cypher and GQL appear only as an export dialect.
> 3. **Provenance.** One canonical witness per fact (lexicographically smallest shortest path, which the existing sorted FIFO closure already produces when parents are recorded), plus rule id and premises for derived facts. The Boolean and tropical semirings are used; polynomials are not stored. Missing-evidence findings carry the searched scope, not a derivation.
> 4. **Neo4j and Cypher.** An optional one-way export (sorted CSV, load script, golden test) run by a person as a separate process. The only import is a differential check that an engine loaded from the export reproduces the SQLite closure; absence reports `NOT_RUN`. No data flows back.
> 5. **OKF.** OKF pages are a get-only projection. The graph excludes generated blocks from a page's hash (proposed method `okf-human-v1`, needs the okf lane's agreement) so the projection cannot feed its own source. Typed links live in the sidecar; the okf `links` block is generated from it.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/weave/ARCHITECTURE.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.

## Referenced by

* [ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing](/adrs/0089-weave-metamodel-identity.md) - EIJA Studio wants deterministic, machine-checkable links between code, UI, diagrams, ubiquitous language, requirements, tests, formal results, evidence, ADRs a…
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
