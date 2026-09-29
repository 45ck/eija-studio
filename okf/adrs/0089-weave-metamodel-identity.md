---
type: Architecture Decision Record
title: 'ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing'
description: EIJA Studio wants deterministic, machine-checkable links between code, UI, diagrams, ubiquitous language, requirements, tests, formal results, evidence, ADRs and personas, with a compiler and linters over the whole set,…
resource: repo://docs/adr/0089-weave-metamodel-identity.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0089-weave-metamodel-identity.md
  title: 0089-weave-metamodel-identity.md
  hash_method: lf-sha256-v1
  sha256: 5ad216e8e2f8a72c1d1c002aaa194df390a9551f9805b36f854011da20dcb290
notes_baseline: 2849f37f60c6d968df052e4170f2fe3eb0de30d40af0032b915e7b4f4104d626
---

# ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | weave (aspect metamodel-identity). Design, evidence and arithmetic: [docs/weave/design/metamodel-and-identity.md](repo://docs/weave/design/metamodel-and-identity.md). Machine-readable metamodel and schemas: [graph/schema/README.md](repo://graph/schema/README.md). Reproducible checks: `graph/bench/identity_checks.py`, `graph/bench/metamodel_dogfood.py`, `tests/graph/test_metamodel_identity.py`. |
| Source | `repo://docs/adr/0089-weave-metamodel-identity.md` |

## Decision outcome (verbatim)

> Chosen option: M5 for the metamodel, canonical `repo://` ids for identity, an RFC 8785 subset for bytes, and sorted-record two-level hashing for the graph, because each is the cheapest mechanism that gives a tested determinism or typing guarantee, and each reuses an existing standard or lane convention.
>
> **D1. A typed multigraph.** A graph document is `(V, E, tau)`: canonical ids, a total type map into 42 node types (order-sorted by four supertypes), and a set of edges keyed `(kind, from, to, qualifier)` over 29 link kinds with 45 signature rows. Well formed means: endpoints exist (a rename's start may be a tombstone), each edge matches a signature row and qualifier, degree bounds hold, five kinds are acyclic, the lifted rename system terminates, no self-loops, no duplicate keys. Records are validated by generated closed JSON Schemas (Draft 2020-12, `additionalProperties: false`); joins by `graph/schema/typecheck.py`. An agent proposal is an `inferred` edge that carries `attrs.tool` and `attrs.version` and can never satisfy a gate.
>
> **D2. Node types and link kinds.** 42 and 29 (the brief had 37 and 27): `workflow_element` becomes `workflow` plus `state`, `transition`, `role`, `guard`, `effect`; new kinds `flows_to` and `refines`; file-level `test` nodes, `adr` sub-decisions, content-addressed `decision` ids. The owner's vocabulary maps onto them (design section 3.2): `aggregate` is a `term` with `ddd_role = aggregate`; `task` is a `lane`; `implements` is `satisfies`, `realises` or `exposes` by target; `tests` is `verifies` or `covers`; `renders` is `derived_from` or `realises`; `traces-to` is the transitive relation over the `trace` view, not an edge.
>
> **D3. Identity.** `id = repo://<path>[#<fragment>]`; path ASCII repo-relative POSIX; fragment segments RFC 3986 unreserved characters plus a literal colon, everything else uppercase `%XX`; one spelling per identity; fragment grammar per node type; a fragment resolves to exactly one thing; the okf `slug()` form is the only accepted form for slug-addressed types. Renames are `renamed_to` records (id-level and path-level), functional and acyclic, resolved by a deterministic rewriting (id-level rule first, else the path-level rule for the file part) to a unique normal form. Termination is a property of the lifted system, not of the relation: an id-level and a path-level record in opposite directions can loop although each record and the relation are valid, so the checker walks the strategy from every left side and reports `rename-cycle`. Aliases, never identities: UUIDv5 over the id in a fixed namespace for exports, SWHID for file snapshots, SCIP symbols for non-Python code, and for Neo4j an application property `eija_id` under a uniqueness constraint.
>
> **D4. Canonical form.** RFC 8785 restricted to strings, integers within +-(2^53-1), booleans, null, arrays and objects; keys ASCII by schema so the kernel's `canonical()` coincides on every weave record; no floats; absent means default (no `null`, no empty container); UTF-8, LF. An own writer of about 60 lines; `rfc8785==0.1.4` is a differential test oracle in the `graph` extra, skipped as NOT_RUN when absent.
>
> **D5. Hashing.** `dhash(tag, v) = sha256(ASCII(tag) || 0x00 || JCS(v))` with tags from a registry in `metamodel.json`; record hashes for nodes and edges; shard hashes over the sorted record rows asserted by one file (rows compared element by element, strings by UTF-8 bytes; all sorted elements are ASCII by schema); a root over sorted `[path, shard hash]` with the metamodel major in its input; view roots over the edges of a named view (kinds from `metamodel.json`) and the records of their endpoints; no canonical labelling, because every node has an identity and isomorphism invariance would conflate distinct claims.
>
> **D6. Closure fingerprint.** A node's dependency closure is fingerprinted on demand as a hash of its sorted node records and of the edge records induced on the closure (tag `eija.weave.closure.v2`), not by a Merkle hash over children, so cycles need no special handling. A node-only form was measured to miss every edge-record change (class, qualifier, anchors, kind). Cost: one traversal per queried node; for every node at once up to `O(V(V+E))` in the worst case.
>
> **D7. Anchors.** A declared link stores one `{end, method, digest}` per anchored end (20 of 29 kinds are anchored, 9 at both ends); either end changing makes it SUSPECT and names the end. Methods are the node type's, split by fragment presence where a type has both forms. Link status semantics belong to the link aspect.
>
> **D8. Cardinality.** Structural bounds (`max_in`, `max_out`, acyclic, typing) hold in every well-formed graph; obligations (`min` with a rule id) are completeness claims checked at named gates.
>
> **D9. Propagation.** Every kind declares `affects` (`to_source`, `to_target`, `both`, `none`), `cover_role` and `rank_weight`; a suspect link is computed from anchors regardless of `affects`.
>

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/oss/REGISTER.md`
* `repo://docs/weave/ARCHITECTURE.md`
* `repo://graph/bench/identity_checks.py`
* `repo://graph/bench/metamodel_dogfood.py`
* `repo://graph/bench/results/identity-timing.json`
* `repo://graph/schema/build_schemas.py`
* `repo://graph/schema/typecheck.py`
* `repo://pyproject.toml`
* `repo://tests/graph/test_metamodel_identity.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0091: Storage and query: git files are the truth, a disposable SQLite index answers named queries](/adrs/0091-weave-storage-query.md) - Weave ties code, UI, diagrams, language, requirements, tests, proofs, evidence and decisions into one typed graph checked by a compiler-like rule set.

## Referenced by

* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
