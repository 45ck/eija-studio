# ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing

* Status: proposed
* Date: 2026-09-29
* Lane: weave (aspect metamodel-identity). Design, evidence and arithmetic: [docs/weave/design/metamodel-and-identity.md](../weave/design/metamodel-and-identity.md). Machine-readable metamodel and schemas: [graph/schema/README.md](../../graph/schema/README.md). Reproducible checks: `graph/bench/identity_checks.py`, `graph/bench/metamodel_dogfood.py`, `tests/graph/test_metamodel_identity.py`.
* Numbering note for the integrator: `docs/weave/ARCHITECTURE.md` section 11 allocates 0089 to "the graph is a derived, rebuildable index", 0090 to node identity, 0091 to canonical serialisation and hashing, and 0092 to the typed schema. This record is the single decision record for all four (the lane assignment gave this aspect one file, 0089). Sibling documents that cite ADR-0090, ADR-0091 or ADR-0092 in the section 11 sense mean sections D3 (identity), D4 and D5 (canonical form and hashing) and D1, D2 and D7 to D9 (typed schema) below. Some siblings were assigned other numbers (the storage aspect's record is also called ADR-0091 in `docs/oss/REGISTER.md`), so the integrator must reconcile the block before merge. The integrator may also split this record; nothing else needs to change.

## Context and problem statement

EIJA Studio wants deterministic, machine-checkable links between code, UI, diagrams, ubiquitous language, requirements, tests, formal results, evidence, ADRs and personas, with a compiler and linters over the whole set, so that agents work reliably and humans see what is happening. The synthesis fixed the shape: the graph is a derived, rebuildable index of git-tracked sources; only declared links and a human ledger are authoritative; extractors and agents are untrusted; a small trusted checker recomputes every verdict; the owner decides. That shape needs four things pinned before any extractor, rule or query can be written: a typed metamodel (what nodes and links may exist and where), an identity scheme (what a node is called and how it is told from what it contains), a canonical serialisation (the bytes that are hashed and committed) and a graph hash (how one value stands for a whole graph, and for one file's contribution to it). Without them two lanes will disagree on a spelling, a hash will differ between Windows and POSIX, an agent will widen a signature to make a link pass, and "did anything change" will have no cheap answer.

## Decision drivers

* Determinism doctrine D-01 to D-24 (ARCHITECTURE section 7): same inputs give byte-identical outputs, independent of file order, locale, time zone, clock, hash seed, threads and platform; no wall clock, floats or absolute paths in artefacts.
* Identity is a name, integrity is a hash; an id is never derived from a label (D-23).
* An ill-typed or dangling link must fail at build, and an agent must not be able to widen a signature (AGENTS.md: agents propose, the kernel checks, the owner decides).
* Reuse before build (ADR-0016): adopt the okf lane's `repo://` grammar and hash methods, JSON Schema, stdlib; build only what is EIJA-specific and say why.
* Cheapest correct mechanism at this scale (about 10^2 to 10^5 records on a shared 16 GB PC).
* A proof about a model is not a proof about code; a hash proves change, not truth; missing prerequisites are NOT_RUN.
* No benefit to agents or humans is claimed until measured.

## Considered options

Metamodel source (D1, D2, D7 to D10):

* M1. Pydantic models as the metamodel with emitted JSON Schema, as the kernel does for its own contracts. Handles records; cannot express signatures across records, cardinality, propagation or hash-method policy without further tables.
* M2. OWL or SHACL (open-world reasoners; pySHACL, Apache-2.0). Rejected in the dossiers: open-world semantics and a JVM or RDF stack for a closed, curated model; SHACL stays an optional cross-check of an exported SKOS graph.
* M3. LinkML (Apache-2.0) generating JSON Schema, SHACL and Pydantic from one YAML model. Closest in spirit; heavy dependency set, and the parts we need most (many-sorted signatures with cardinality, propagation, anchored ends, per-type hash methods) are not its schema language.
* M4. SysML v2, UML or MOF as the internal metamodel. Rejected: ambiguous or heavyweight, no maintained Python stack, lossy interchange (MDE dossier); SysML v2 is an export target only.
* M5. One maintained JSON table (`metamodel.json`) of node types, link kinds and signature rows, from which closed JSON Schemas and README tables are generated, plus a small executable reference for the join-level checks (chosen).

Identity (D3): opaque UUIDs stored in artefacts (Doorstop-style); content hash as id (git blob, SWHID); SCIP symbol strings; label-derived slugs; canonical `repo://path#fragment` URIs with explicit rename records (chosen). Comparison table in design section 5.2.

Canonical serialisation (D4): the kernel's `canonical()`; the `rfc8785` package as a runtime dependency; an own RFC 8785 subset writer with `rfc8785` as a differential test oracle (chosen); deterministic CBOR or protobuf (not evaluated). Comparison in design section 6.1.

Graph hashing (D5, D6): sorted records under a domain-separated hash, two-level over source-file shards (chosen); a binary Merkle tree as in RFC 6962; a canonical labelling of the graph (RDFC-1.0, nauty) or a Weisfeiler-Leman hash. Evidence in design section 6.3.

## Decision outcome

Chosen option: M5 for the metamodel, canonical `repo://` ids for identity, an RFC 8785 subset for bytes, and sorted-record two-level hashing for the graph, because each is the cheapest mechanism that gives a tested determinism or typing guarantee, and each reuses an existing standard or lane convention.

**D1. A typed multigraph.** A graph document is `(V, E, tau)`: canonical ids, a total type map into 42 node types (order-sorted by four supertypes), and a set of edges keyed `(kind, from, to, qualifier)` over 29 link kinds with 45 signature rows. Well formed means: endpoints exist (a rename's start may be a tombstone), each edge matches a signature row and qualifier, degree bounds hold, five kinds are acyclic, the lifted rename system terminates, no self-loops, no duplicate keys. Records are validated by generated closed JSON Schemas (Draft 2020-12, `additionalProperties: false`); joins by `graph/schema/typecheck.py`. An agent proposal is an `inferred` edge that carries `attrs.tool` and `attrs.version` and can never satisfy a gate.

**D2. Node types and link kinds.** 42 and 29 (the brief had 37 and 27): `workflow_element` becomes `workflow` plus `state`, `transition`, `role`, `guard`, `effect`; new kinds `flows_to` and `refines`; file-level `test` nodes, `adr` sub-decisions, content-addressed `decision` ids. The owner's vocabulary maps onto them (design section 3.2): `aggregate` is a `term` with `ddd_role = aggregate`; `task` is a `lane`; `implements` is `satisfies`, `realises` or `exposes` by target; `tests` is `verifies` or `covers`; `renders` is `derived_from` or `realises`; `traces-to` is the transitive relation over the `trace` view, not an edge.

**D3. Identity.** `id = repo://<path>[#<fragment>]`; path ASCII repo-relative POSIX; fragment segments RFC 3986 unreserved characters plus a literal colon, everything else uppercase `%XX`; one spelling per identity; fragment grammar per node type; a fragment resolves to exactly one thing; the okf `slug()` form is the only accepted form for slug-addressed types. Renames are `renamed_to` records (id-level and path-level), functional and acyclic, resolved by a deterministic rewriting (id-level rule first, else the path-level rule for the file part) to a unique normal form. Termination is a property of the lifted system, not of the relation: an id-level and a path-level record in opposite directions can loop although each record and the relation are valid, so the checker walks the strategy from every left side and reports `rename-cycle`. Aliases, never identities: UUIDv5 over the id in a fixed namespace for exports, SWHID for file snapshots, SCIP symbols for non-Python code, and for Neo4j an application property `eija_id` under a uniqueness constraint.

**D4. Canonical form.** RFC 8785 restricted to strings, integers within +-(2^53-1), booleans, null, arrays and objects; keys ASCII by schema so the kernel's `canonical()` coincides on every weave record; no floats; absent means default (no `null`, no empty container); UTF-8, LF. An own writer of about 60 lines; `rfc8785==0.1.4` is a differential test oracle in the `graph` extra, skipped as NOT_RUN when absent.

**D5. Hashing.** `dhash(tag, v) = sha256(ASCII(tag) || 0x00 || JCS(v))` with tags from a registry in `metamodel.json`; record hashes for nodes and edges; shard hashes over the sorted record rows asserted by one file (rows compared element by element, strings by UTF-8 bytes; all sorted elements are ASCII by schema); a root over sorted `[path, shard hash]` with the metamodel major in its input; view roots over the edges of a named view (kinds from `metamodel.json`) and the records of their endpoints; no canonical labelling, because every node has an identity and isomorphism invariance would conflate distinct claims.

**D6. Closure fingerprint.** A node's dependency closure is fingerprinted on demand as a hash of its sorted node records and of the edge records induced on the closure (tag `eija.weave.closure.v2`), not by a Merkle hash over children, so cycles need no special handling. A node-only form was measured to miss every edge-record change (class, qualifier, anchors, kind). Cost: one traversal per queried node; for every node at once up to `O(V(V+E))` in the worst case.

**D7. Anchors.** A declared link stores one `{end, method, digest}` per anchored end (20 of 29 kinds are anchored, 9 at both ends); either end changing makes it SUSPECT and names the end. Methods are the node type's, split by fragment presence where a type has both forms. Link status semantics belong to the link aspect.

**D8. Cardinality.** Structural bounds (`max_in`, `max_out`, acyclic, typing) hold in every well-formed graph; obligations (`min` with a rule id) are completeness claims checked at named gates.

**D9. Propagation.** Every kind declares `affects` (`to_source`, `to_target`, `both`, `none`), `cover_role` and `rank_weight`; a suspect link is computed from anchors regardless of `affects`.

**D10. Evolution.** Semantic versioning of the metamodel; MINOR additive and hash-neutral for existing records; MAJOR with a migration function and an intentional root change; closed schemas; immutable hash-method names; the schemas are protected paths.

**D11. Interchange.** OKF, SysML v2 text, Structurizr and LikeC4 JSON, ArchiMate exchange XML, SCIP and Cypher/CSV are get-only exports or narrow untrusted imports; OKF `generated.at`, `verified[].at` and `stale_after` are excluded from identity and verdicts.

**D12. Graph technology.** Neo4j is an optional export target run by a person as a separate process; OKF is the readable projection. Neither is in the trust path.

### Consequences

* Good: a link of the wrong shape, a dangling end, an over-full cardinality or a cycle in an acyclic kind is a named, located finding before anything else runs. MEASUREMENT: applied to this repository the metamodel produced an 83 node, 108 edge graph with 0 schema errors and 0 reference findings.
* Good: one root for any input order. MEASUREMENT: 200 shuffles of a 300-node, 900-edge graph give 1 root; three naive serialisations give 200 distinct hashes each. A changed file names its shard, so "what changed" costs a comparison of shard hashes.
* Good: bytes agree with RFC 8785 and with the kernel where they should. MEASUREMENT: 0 differences from `rfc8785` 0.1.4 in 4000 documents; the kernel's `canonical()` equals it on all ASCII-key documents and differs only in the key order of supplementary versus U+E000 to U+FFFF characters.
* Good: the digest methods interoperate with the okf lane and the kernel. MEASUREMENT: `csv-row-v1`, `lf-sha256-v1` and `md-bold-term-v1` equal the okf `digest()` on every node checked; `workflow-semantic-v1` reimplemented from JSON equals `Workflow.semantic_hash`.
* Good: it exposes real gaps. MEASUREMENT: the acceptance matrix cites evidence at file granularity (0 of 44 references name a function, 2 do not resolve as written); 7 of 180 okf resources use non-canonical fragments.
* Bad: table upkeep, and a closed schema means every new enum value is a reviewed change.
* Bad: anchoring both ends of trace kinds raises SUSPECT volume (PREDICTION: needs a measurement on EIJA history), and `both` flow on those kinds makes impact closures about 4.5 times larger on the dogfood graph (MEASUREMENT, one graph).
* Bad: paths in ids mean file moves need rename records; the okf lane must regenerate 7 pages and register 6 proposed hash methods; the link aspect must accept two anchors per link; the storage aspect must implement this root and add `qualifier` to the edge key.
* Bad: hashing 500,000 records took 6.6 to 16.9 seconds in Python (one run, committed as `graph/bench/results/identity-timing.json`; an earlier run gave 8.2 to 19.0); fine at repository scale (PREDICTION: under a second at 10^4 records), a shard cache keyed by file content hash is the mitigation.
* Bad: only Windows was measured; POSIX byte identity is NOT_RUN.
* Revisit when: a graph exceeds about 10^6 records or a full root takes longer than the agreed rebuild budget (add per-shard caching, then a compiled writer); an import format brings anonymous nodes (use RDFC-1.0 or nauty to derive ids for the proposal only); the measured SUSPECT rate on EIJA history makes both-end anchors unusable (fall back to one anchor per kind); SHA-256 is weakened (the `sha256:` prefix lets digests change algorithm under a MAJOR version); the kernel adopts JCS (then the own writer becomes a wrapper).

## OSS check (required for any custom module)

Custom modules: `graph/schema/build_schemas.py` and `metamodel.json` (metamodel and schema generator), `graph/schema/typecheck.py` (join-level checks), the canonical writer and hash functions (reference in `graph/bench/identity_checks.py`; production `eijagraph.canon`), and the id and rename functions.

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| [rfc8785](https://github.com/trailofbits/rfc8785.py) 0.1.4, Apache-2.0 (wheel LICENSE read; pure Python, no dependencies; rejects lone surrogates and integers beyond 2^53-1) | Correct and small. Adopted as the differential test oracle. Not a runtime dependency: the checker's trusted base should be smaller than the tests that guard it, and the subset writer is about 60 lines because floats are excluded | If the own writer is ever dropped, depend on it at the same pin |
| [jsonschema](https://github.com/python-jsonschema/jsonschema) 4.26.0 (the `graph` extra pin) and 4.25.1, MIT; the 38 identity tests passed on both | Adopted for record validation (Draft 2020-12). Cannot express joins, cardinality or acyclicity | none needed |
| [LinkML](https://github.com/linkml/linkml), Apache-2.0 | Generates JSON Schema, SHACL, OWL and Pydantic from one model, but adds a large dependency set and has no native many-sorted signatures with cardinality, propagation direction or hash-method policy | Optional one-off exporter from `metamodel.json` |
| [pySHACL](https://github.com/RDFLib/pySHACL), Apache-2.0, and OWL reasoners | Open-world or RDF stack for a closed curated model | Optional cross-check of an exported SKOS graph |
| RDFC-1.0 (W3C Recommendation), nauty, networkx Weisfeiler-Leman hash | Solve labelling of anonymous nodes; our nodes are named, isomorphism invariance conflates distinct claims (measured), and RDFC-1.0 warns of inputs that do not terminate in reasonable time | RDFC-1.0 to derive ids for an anonymous import proposal, with a step limit |
| [networkx](https://github.com/networkx/networkx) 3.5 (BSD by classifier, BSD-3-Clause per the dossier; pin below 3.7) | Library defaults are order dependent (dossier measurement); used only as a test oracle for hashing comparisons | `graph` extra, skipped as NOT_RUN when absent |
| [swh-model](https://github.com/softwareheritage/swh-model), GPL-3.0 | GPL; a `cnt` identifier is ten lines of `hashlib` | Own ten lines; SWHID is an optional alias only |
| SysML v2 Pilot and API Services (EPL-2.0), `sysml-toolkit` | JVM or a three-week-old Rust tool whose claims I did not run; only text is emitted | Optional validator as a separate process; NOT_RUN when absent |
| [Structurizr](https://github.com/structurizr/structurizr) (Apache-2.0), [LikeC4](https://github.com/likec4/likec4) (MIT) | Their JSON exports carry counter-like ids and modification times (Structurizr, measured) or an undocumented structure (LikeC4) | Read-only import of a human-written intended architecture, ids from a property |
| [Archi](https://github.com/archimatetool/archi) (MIT) and the ArchiMate exchange XSD | XSD licence terms are not stated on the standard's page; not vendored | Export on demand |
| [Neo4j](https://github.com/neo4j/neo4j) Community, GPL-3.0 | GPL server outside git; internal ids are reused after deletes | Export target, separate user-run process |
| OKF v0.2 (Apache-2.0) and the okf lane's `codelink.py` | Adopted: `repo://` grammar and hash methods (the `sources[].hash_method` and `sources[].sha256` keys are the okf lane's extension keys; the OKF v0.2 SPEC defines no hash fields). Its resolver accepts non-canonical slug spellings, so weave adds a canonical-form rule | Shared registry and fixture test with the okf lane |
| EIJA-specific: metamodel table, schema generator, reference checker, canonical writer, ids and renames | No tool provides typed, hash-anchored links with per-kind signatures, cardinality, propagation and a determinism contract over these artefacts | Each part is small and replaceable behind the schema files |

Licence roles for an Apache-2.0 package (engineering reading, not legal advice): dependencies are stdlib `json`, `hashlib`, `re`, `uuid`, `sqlite3` and, in extra `graph`, `jsonschema` (MIT); test-only oracles are `rfc8785` (Apache-2.0) and `networkx` (BSD); export targets or separate processes are Neo4j (GPL-3.0), SysML v2 Pilot (EPL-2.0), PlantUML-family tools and any GPL, LGPL, EPL or MPL tool; inspiration only are Doorstop, LinkML and RDFC-1.0. The extra `graph` in `pyproject.toml` pins `jsonschema==4.26.0` (added by the rules aspect; the identity tests were run on 4.26.0 and on 4.25.1) and `rfc8785==0.1.4`; `networkx` 3.5 is an oracle installed by hand and skipped as NOT_RUN when absent.
