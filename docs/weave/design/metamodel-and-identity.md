# Metamodel, identity, canonical form and hashing for the weave graph

Lane: weave. Aspect: metamodel-identity. Date: 2026-09-29. Status: DESIGN feeding [ADR-0089](../../adr/0089-weave-metamodel-identity.md). Machine-readable form: [graph/schema/](../../../graph/schema/README.md) (metamodel version 1.0.0). Reproduce every MEASUREMENT here with the commands in section 12.

Labels: MEASUREMENT (a script ran, domain stated), PREDICTION (reasoned, not run), DESIGN (a proposal of this lane), UNVERIFIED (not opened or not confirmable; nothing is built on it). Sources marked [S..] are listed in section 13 and were opened on 2026-09-29; keys [mde], [math], [trace], [lang], [code], [gdb], [assure] are the lane's research dossiers in `docs/weave/research/`, cited where I rely on what their authors opened.

## 0. Decisions first

| # | Decision | Confidence | Evidence |
|---|---|---|---|
| D1 | The graph is a **typed multigraph over stable identities**: a set of nodes, each with one of 42 types, and a set of edges keyed `(kind, from, to, qualifier)`, each kind having a many-sorted signature (45 rows) over an order-sorted type hierarchy. A document is well formed iff it is a graph homomorphism into the schema graph plus degree bounds and acyclicity (section 2). | High | 45 signature rows; `graph/schema/typecheck.py` and 38 passing tests |
| D2 | **42 node types and 29 link kinds** (the brief had 37 and 27). Changes are additive except one split, and each has evidence (section 3.3). | Medium: needs sibling-aspect review | dogfood on this repo, okf bundle mapping |
| D3 | **Identity is a name, integrity is a digest, provenance is a file.** Node id = canonical `repo://<path>[#<fragment>]`; digest = `sha256:` plus the output of a versioned hash method; `asserted_in` = the file whose bytes assert a fact. Ids are ASCII, canonical (one spelling), never derived from a label; renames are explicit records (section 5). | High | 106 of 106 tracked paths fit the grammar; 173 of 180 okf resources already conform |
| D4 | **Canonical form is an RFC 8785 subset** (strings, safe integers, booleans, null; no floats; keys ASCII by schema), written by an own writer of about 60 lines. `rfc8785==0.1.4` is a test oracle, not a runtime dependency. Absent means default: no `null`, no empty containers. | High | 0 differences in 4000 documents against `rfc8785`; kernel `canonical()` equals it on every ASCII-key document (section 6.1) |
| D5 | **Graph hash = sorted records, domain-separated, two-level over source-file shards. No canonical labelling.** Record hash `H(tag, NUL, JCS(record))`; shard hash over the sorted record rows of one file (comparator specified in section 6.2); root over sorted `[path, shard hash]`; view roots filter by the view's link kinds. | High | 1 root over 200 shuffles versus 200 for three naive forms; label-free hashing conflates distinct claims (section 6.3); view roots and the comparator are tested |
| D6 | **A node's dependency closure is fingerprinted on demand** (hash of the sorted node records **and** the edge records induced on the closure), not by a per-node Merkle hash over children. Equal semantics under cycles, no SCC handling. | Medium | 60 random cyclic graphs, five mutation kinds (node record; edge class, qualifier, anchors, kind): 0 differences from the kernel `closure()`; the node-only form misses all 48 edge mutations |
| D7 | **Links anchor both ends** where both are content-addressable: `anchors` holds one entry per anchored end. A changed digest at either end makes the link SUSPECT and says which end. Hash method is per (end, node type, fragment presence). This generalises the brief's single `method`/`digest`. | Medium: link aspect must accept | Doorstop stores only the parent digest [trace]; 20 of 29 kinds are anchored |
| D8 | **Two kinds of cardinality.** Structural bounds (`max_in`, `max_out`, acyclic, no self-loop, typing) hold in every well-formed graph. Obligations (`min`, tied to a rule id) are completeness claims checked at named gates. | High | 13 signature rows carry a structural bound, 6 carry an obligation; all six rule ids exist in `graph/rules/catalogue.json` |
| D9 | **Propagation is declared per kind** as `affects` (`to_source`, `to_target`, `both`, `none`) with `cover_role` and `rank_weight`, so impact is a pure function of the schema. | Medium | fan-out measurement: `both` on `verifies` (the one of the four `both` kinds present) makes closures 4.5 times larger (section 4.4) |
| D10 | **Schema evolution is semver.** MINOR is additive and must not change any existing record hash; MAJOR needs a migration function and changes every root on purpose (the domain tag carries the major). Schemas are closed (`additionalProperties: false`), generated from one table. | High | tests: generated files current, tag registry, closed records |
| D11 | **Interchange is projection, not truth.** OKF pages, SysML v2 text, Structurizr/LikeC4 JSON, ArchiMate exchange XML, SCIP, Cypher/CSV are get-only exports or narrow, untrusted imports. Exported ids are UUIDv5 over the `repo://` id in a fixed namespace. | High for OKF and SysML v2; UNVERIFIED for LikeC4 JSON and ArchiMate element mapping | section 8 |
| D12 | **Graph technology, restated for identity.** Neo4j receives our ids as an application property under a uniqueness constraint (available in Community), never its internal ids; OKF carries our ids in `resource` and our digests in the okf lane's extension keys `sources[].hash_method` and `sources[].sha256` (not OKF fields). Neither holds the truth. | High | [S12], [S13], [S1] |

## 1. What the owner asked, for this aspect

The owner asked how graphs (Neo4j, OKF) are used, and which mathematics makes the process efficient, effective and deterministic. For identity and hashing the answer is:

| Question | Answer | Benefit named | Mechanism | Cost | Evidence |
|---|---|---|---|---|---|
| Is Neo4j the store? | No. Optional one-way export. Node property `eija_id` = our id, uniqueness constraint on it | No second stateful truth; ids survive delete and reload | Cypher/CSV projection generated from the canonical document | An export adapter and a golden test | Neo4j reuses internal ids after deletes and gives no guarantee about the id-to-element mapping outside one transaction [S12]; uniqueness constraints exist in Community, existence constraints only in Enterprise [S13] |
| Is OKF the graph? | No. A generated, readable projection and the prose surface. `resource` carries our id, the okf lane's extension keys in `sources[]` our anchors | Humans and agents read pages; staleness is by digest | Frontmatter mapping (section 8.1) | 7 of 180 pages have non-canonical fragments today | OKF links are untyped and broken links must be tolerated; `stale_after` reads the clock [S1] |
| Which mathematics? | Typed graphs and signatures (typing), sets and keys (identity), JCS (bytes), sorted records under a domain-separated hash (permutation invariance), fixed points (closure fingerprint), deterministic rewriting with a named strategy (renames) | Ill-typed links fail at build; one root for any input order; renames resolve to one normal form | Sections 2 and 6 | Table upkeep; hash cost linear in records | Sections 6 and 9 |
| Which mathematics is rejected here? | Canonical labelling, Weisfeiler-Leman hashing as identity, category-theoretic migration, probabilistic confidence | None implementable | Section 6.3 | n/a | C4 |

## 2. Mathematical basis (definitions, then what they buy)

**Definitions.** Let `T` be the finite set of 42 node types with a subsort order `<=` given by four supertypes (`workflow_element`, `ui_node`, `verifier`, `model_concept`). An order-sorted signature lets a rule name a supertype and stand for all its subtypes [S15]; here it only shortens tables, and the generator expands it. Let `K` be the 29 link kinds, and for each `k` a set of signature rows `Sigma_k` of `(from sorts, to sorts, max_out, max_in, qualifiers, obligations)`.

A **graph document** is `G = (V, E, tau)`: `V` a finite set of canonical ids, `tau : V -> T` total, and `E` a finite **set** of tuples `(k, s, t, q)` with `k` in `K`, `s, t` ids, `q` a qualifier or empty. Because `E` is a set keyed by its content, an edge needs no separate identity: `eid = H(tag, [k, s, t, q])`. Equivalently `G` is a family of relations `R_k` over `V x V x Q`. This is the usual notion of a typed multigraph: parallel edges of one kind are allowed only when their qualifiers differ.

**Well formed** means the following five conditions. Each is a scan of the nodes and edges with hash-table lookups, so the definition is linear in `|V| + |E|` (expected time, times the number `R` of signature rows of one kind, at most 8 in this metamodel); the reference implementation additionally sorts adjacency lists for a deterministic cycle report, so it is `O(R * |E| + |E| log |E|)` (signature rows are expanded once per kind, tested):

1. every `t` is in `V`, and every `s` is in `V` unless `k` is `renamed_to` (a tombstone start);
2. `(tau(s), tau(t))` matches some row of `Sigma_k`, and `q` is allowed by that row (this is a homomorphism into the **schema graph** whose nodes are types and whose arcs are rows; I take it as a definition, not a theorem);
3. degree bounds: for each row and each node, the number of matching edges is at most `max_out` (resp. `max_in`);
4. for the five acyclic kinds (`contains`, `derived_from`, `refines`, `renamed_to`, `supersedes`), the relation has no directed cycle;
5. no self-loops and no duplicate `(k, s, t, q)`.

`typecheck.py` implements 1 to 5, plus the composite rename check of section 5.3, in about 170 lines; the tests exercise each defect class. JSON Schema cannot express a join, so records are validated alone by schema and the document by this reference; the rule lane's implementation must agree with it on the fixtures.

**What each piece of mathematics earns here** (only where it changes a number or removes a failure):

| School | Mechanism in this aspect | Benefit (named) | Cost | Evidence | Verdict |
|---|---|---|---|---|---|
| Type theory: many-sorted and order-sorted signatures | Edge typing as a row lookup; supertypes shorten rows | An agent or a person cannot write `requirement satisfies symbol`; 45 rows instead of a per-pair list | Table upkeep; generated checks | Reference checker names all defect classes (tests) | adopt |
| Relational algebra: keys, sets | `E` is a set keyed by content; records addressed by id | No duplicate links; edge ids are a pure function of the key; keyed diff is exact | none | Duplicate-edge finding | adopt |
| Content addressing, Merkle structure | Record hash, shard hash, root (section 6) | One comparison decides "did anything change"; the changed shard names the file | Detects change, not truth (AGENTS.md) | C3, C5 | adopt |
| Order theory: least fixed points | Dependency-closure fingerprint over the kernel closure | Cache key and staleness for derived results | Recomputed per query | C6: 60 trials, 0 differences | adopt |
| Deterministic rewriting (strategy: id-level rule first, else path-level) | Rename records as rules `old -> new` | One normal form for any id, independent of record order | Records must be functional; termination is checked on the lifted system, not on the relation alone (section 5.3) | C7: 3000 resolutions, 0 order dependence; the mixed-level counterexample is caught | adopt |
| Canonical forms (JCS) | Byte-identical serialisation | Same hash on any platform or language | No floats in artefacts | C1 | adopt |
| Graph canonical labelling (RDFC-1.0, nauty), Weisfeiler-Leman | Would hash graphs up to isomorphism | None: nodes have identities, and isomorphism invariance is a defect here | Worst-case blow-up | C4 | reject (section 6.3) |
| Category theory | The schema graph and the typing homomorphism as vocabulary; mapping totality is the views aspect's check | Vocabulary only | none | n/a | theory-only |
| Information theory, probability | None for identity | none | none | n/a | not used |

## 3. Node types

### 3.1 Summary by layer (full table with id grammar, methods and examples: [README](../../../graph/schema/README.md))

| Layer | Types | Truth class | Default digest method |
|---|---|---|---|
| code | `module`, `symbol`, `contract`, `api_operation` | derived | `ast-api-v1`, `ast-v2`/`ast-sig-v1`, `lf-sha256-v1`, `json-key-v1` |
| workflow | `workflow`, `state`, `transition`, `role`, `guard`, `effect` | declared | `workflow-semantic-v1`, `workflow-element-v1` |
| language | `bounded_context`, `term`, `invariant` | declared | `md-table-row-v1`, `md-bold-term-v1` |
| requirements | `requirement`, `adr`, `persona`, `journey` | declared (journey derived) | `csv-row-v1`, `lf-sha256-v1`, `md-table-row-v1` |
| knowledge and views | `document`, `okf_page`, `diagram`, `diagram_element`, `component` | mixed | `lf-sha256-v1`, `json-key-v1` |
| process | `lane`, `gate` | declared, derived | `md-table-row-v1`, `ast-v2` |
| verification | `test`, `property`, `formal_model`, `formal_law`, `witness`, `tool`, `evidence`, `link_certificate`, `claim` | derived, declared, evidence | `ast-v2`, `lf-sha256-v1`, `law-block-v1`, `json-key-v1` |
| governance | `decision`, `agent_run` | declared, evidence | `json-key-v1`, `lf-sha256-v1` |
| ui | `ui_view`, `ui_region`, `ui_control`, `ui_field`, `ui_status`, `ui_table`, `design_token` | declared | `html-key-v1`, `json-key-v1` |

Counts by truth class: declared 27, derived 11, evidence 4 (MEASUREMENT of `metamodel.json`).

### 3.2 The owner's vocabulary, mapped

| Owner term | Schema term | How | Why not a new type |
|---|---|---|---|
| term, context | `term`, `bounded_context` | direct | n/a |
| aggregate | `term` with `attrs.ddd_role = aggregate` | attribute | An aggregate is a language concept first; obligations key on the attribute (`WV-054`: an aggregate term needs a realising symbol) and the enum also names entity, value object, domain event, domain service, policy. One type keeps signatures small |
| requirement, ADR, persona | `requirement`, `adr`, `persona` | direct | n/a |
| state, transition | `state`, `transition` | direct (split from the brief's `workflow_element`) | Typed `flows_to` and `depends_on` rows need distinct sorts |
| diagram element | `diagram_element` | direct | n/a |
| UI screen, UI element | `ui_view`; `ui_region`, `ui_control`, `ui_field`, `ui_status`, `ui_table` | direct | n/a |
| code symbol | `symbol` (attr `kind`: function, class, method, constant, type_alias) | direct | The okf lane's five symbol page types map onto `kind` one to one |
| test | `test`, `property` | direct | n/a |
| law, proof, model check | `formal_law`, `witness`, `formal_model` | a law states, a witness proves, a model is what is checked | Keeps the statement pin (law) apart from the artefact that supports it (witness) |
| evidence | `evidence`, `link_certificate` | direct | n/a |
| task | `lane` (and `agent_run` for an execution) | a work unit that exists in git | A `task` type needs a git-tracked source; none exists. Adding one is a MINOR change once a source does |
| implements (link) | `satisfies` (to a requirement), `realises` (to a concept), `exposes` (to an API operation) | by target type | One word for three relations hid which claim was made |
| tests (link) | `verifies` (declared) and `covers` (derived) | by origin class | Verifying and executing are different claims |
| renders (link) | `derived_from` (generated view), `realises` (UI element realising a concept) | by artefact | The generator re-run check applies only to the first |
| traces-to (link) | not an edge: the transitive relation over the `trace` view (`realises`, `satisfies`, `verifies`, `refines`, `models`, `formalises`) | view | A stored transitive edge would be a second source of truth |
| refines, depends-on, derives-from, documents, supersedes, realises, verifies | `refines`, `depends_on`, `derived_from`, `documents`, `supersedes`, `realises`, `verifies` | direct | n/a |

### 3.3 Changes from `graph/brief.json`, each with its reason

| Change | Brief | Now | Reason and evidence |
|---|---|---|---|
| Workflow split | one `workflow_element` | `workflow` plus `state`, `transition`, `role`, `guard`, `effect` (`workflow_element` kept as a supertype) | The kernel `Transition` has `from_state`, `to_state`, `role`, `guards`, `required_effects`, `forbidden_effects`; without typed edges a dangling state is invisible to the graph. Per-element hashing (`workflow-element-v1`) means editing one transition does not stale links to the other three |
| New kind `flows_to` | none | state to transition to state, degree bounds 1 | Same. Kernel validation already rejects dangling transition states |
| `depends_on` rows | code only | plus transition to role, guard, effect (qualifier `required` or `forbidden`) | Same |
| New kind `refines` | none | requirement, term (SKOS broader), formal model, invariant | Owner's vocabulary; requirement decomposition; the language dossier's `broader` [lang] |
| `test` at file level | function only | fragment optional; without it the method is `lf-sha256-v1` | MEASUREMENT: of 44 evidence references in the acceptance matrix, 40 name an existing test or smoke file, 0 name a function (section 9) |
| `adr` sub-decision | file only | optional fragment `adr-NNN` with `md-table-row-v1` | The okf bundle has 14 pages for decisions inside `0000-poc-decision-log.md` |
| `decision` id | `graph/ledger.jsonl#<seq>` | `graph/ledger[/shard].jsonl#<64 hex entry id>` | The consistency aspect measured duplicate sequence numbers under union merge in 200 of 200 trials; entry ids are content addressed |
| Anchors | one `method`, one `digest` | `anchors[]`, one entry per anchored end | D7 |
| Flow attributes | `soundness` only | plus `affects`, `cover_role`, `rank_weight` on every kind | The impact-ranking aspect requires them, no defaults |
| Hash-method registry | 7 registered, 4 proposed | 8 registered (adds `ast-v2`), 6 proposed (adds `workflow-element-v1`, `okf-human-v1`) | `ast-v2` is in use in the okf worktree (63 source entries across the 180 pages); the other two are proposals |
| Kept as brief | the dropped ProofMap node kinds and merged link kinds (`node_types_dropped_from_proofmap`, `link_types_dropped_from_proofmap` in the brief) | unchanged | n/a |

## 4. Link kinds

### 4.1 Kinds by group (rows abbreviated; the full signature table with cardinalities is generated into the README)

| Group | Kind | Class | Sound. | Affects | Anchored ends | SysML v2 term [S8] | Structural | Obligation |
|---|---|---|---|---|---|---|---|---|
| structure | `contains` | derived, declared | must | to_source | none | composition (PREDICTION) | acyclic; in<=1 on 7 of 8 rows | `WV-053` term in a context |
| | `depends_on` | derived, declared | may | to_source | none | none | none | none |
| | `flows_to` | derived | must | to_target | none | none | in<=1 (source state), out<=1 (target state) | none |
| | `calls` | derived, declared | heuristic | to_source | none | none | none | none |
| | `exposes` | derived | may | to_target | none | none | in<=1 | none |
| semantic | `realises` | declared | must | both | from, to | none | none | `WV-054`, `WV-031` |
| | `satisfies` | declared | must | both | from, to | `satisfy` | none | `WV-011` |
| | `verifies` | declared | must | both | from, to | `verify` | none | `WV-010` |
| | `covers` | derived | may | to_source | none | none | none | none |
| | `names` | declared | must | both | from, to | none | qualifier = surface | none |
| | `documents` | declared | must | to_source | to | `doc` | none | none |
| | `refines` | declared | must | to_source | to | none | acyclic; in<=1 for requirements | none |
| | `serves` | declared | must | to_source | to | none | none | none |
| decision records | `motivates` | declared | must | none | from | none | none | none |
| | `supersedes` | declared | must | none | none | none | acyclic; in<=1 | none |
| | `renamed_to` | declared | must | none | none | none | acyclic; out<=1, in<=1; same node type; start may be absent | none |
| generation and models | `derived_from` | derived | must | to_source | from, to | none | acyclic | none |
| | `models`, `formalises` | declared | must | to_source | from, to | none | none | none |
| | `conforms_to` | declared | may | to_source | from, to | none | none | none |
| | `exercised_by` | declared, derived | may | to_target | to | none | none | `WV-037` |
| | `styled_by` | derived | may | to_source | to | none | none | none |
| assurance | `proves`, `attests`, `checked_by` | evidence | must | to_source | see README | none | none | none |
| | `supports`, `defeats` | declared | must | to_target | from or none | none | none | none |
| | `decides` | declared | must | to_source | to | none | none | none |
| proposals | `proposes` | inferred | heuristic | none | from | none | attrs `tool`, `version` required | none |

Counts (MEASUREMENT of `metamodel.json`): soundness must 21, may 6, heuristic 2; `affects` to_source 16, to_target 5, both 4, none 4; anchored ends: none 9, from 4, to 7, both 9; 45 signature rows, 12 with `max_in`, 2 with `max_out`, 6 obligations. Classes: every kind also admits `inferred`, which requires `attrs.tool` and `attrs.version` and can never satisfy a gate (WV-007).

### 4.2 Cardinality semantics

A **structural** bound is a safety property: it holds in every well-formed document, so the compiler reports a violation as an error the moment a link is written (`WV-055` link-cardinality-exceeded, `WV-056` acyclic-link-cycle). An **obligation** is a completeness claim, `min >= 1` on a side, tied to a rule id; it is checked at named gates because a fresh graph is legitimately incomplete (28 requirements exist before their tests do). The two are stored in one table so a person can read "what may I write" and "what must eventually exist" together. No obligation is a metamodel default that makes a build red by itself: severity and gate live in the rule catalogue.

### 4.3 Anchors and hash methods

An `anchor` is `{end: from|to, method, digest}`; `anchors` has one entry per anchored end of the kind, ordered `from` before `to` (the schema enforces order and count with `prefixItems`). Allowed methods are the node type's methods, further split by fragment presence where a type admits both (`test`, `contract`, `adr`, `document`). Semantics owned by the link aspect: a link is SUSPECT when either stored digest differs from the digest recomputed by the okf lane's `digest(root, ref, method)`, and the report names the changed end. Anchoring both ends is the reason for the D7 generalisation: Doorstop stores only the parent's fingerprint, so a change in the child is never suspect [trace]. Cost: more SUSPECT events. Mitigation: methods are chosen per end to be low-noise (per change, a symbol signature was stale in 1.5 to 1.8 percent of cases, a symbol AST in 7.2 to 9.4 percent and whole-file bytes in 99.9 to 100 percent, on the Doorstop and StrictDoc Python source histories [trace]; sensitivity, not a false-link rate).

### 4.4 Propagation (`affects`) and its tension with anchors

`affects` maps one-to-one onto the impact aspect's flow set: `to_target` = {F} (a change at `from` affects `to`), `to_source` = {R}, `both` = {F, R}, `none` = {}. I set it by asking who depends on whom: a container depends on its parts, an implementation on its requirement, a document on what it describes; four trace kinds (`realises`, `satisfies`, `verifies`, `names`) are `both`, because a change on either side puts the other side's status in question.

Two measurements on the dogfood graph of section 9 (kernel `closure()`, every node as one root):

| Variant | Arcs | Sum of closure sizes | Largest closure |
|---|---|---|---|
| metamodel `affects` (four kinds `both`) | 148 | 1304 | 33 |
| the same four kinds `to_source` only (only `verifies` occurs in this graph) | 108 | 288 | 10 |

The whole difference comes from the 40 `verifies` edges: of the four `both` kinds (`realises`, `satisfies`, `verifies`, `names`) only `verifies` occurs in this 83-node graph, at file-level test granularity, so 40 edges become 80 arcs and the sum of closure sizes grows 4.5 times (MEASUREMENT, one graph, it will move as files are added; the other three kinds are untested here). The impact aspect's proposed lint says every anchored end needs the flow that leaves it. Nine kinds fail it by design (`attests`, `conforms_to`, `derived_from`, `exercised_by`, `formalises`, `models`, `motivates`, `proposes`, `proves`): a hand edit of a generated diagram makes the `derived_from` link suspect, but does not affect the workflow it was drawn from. **A suspect link is computed from anchors, whatever `affects` says; `affects` only governs which other nodes a change reaches.** I recommend the lint be narrowed accordingly (open question 3).

## 5. Identity

### 5.1 The scheme

```text
id        = "repo://" path [ "#" fragment ]
path      = segment *( "/" segment )            ; segment = 1*( ALPHA / DIGIT / "." / "_" / "-" ), not "." or ".."
fragment  = fsegment *( "/" fsegment )
fsegment  = 1*( unreserved / ":" / pct-encoded ) ; unreserved per RFC 3986; pct-encoded = "%" 2*UPHEXDIG
```

Rules (each checked; `is_canonical_id` in the bench and the generated schema patterns):

1. **One spelling.** Every non-unreserved byte of a fragment segment is `%XX` with uppercase hex; an unreserved byte is never encoded. RFC 3986 treats the two hex cases as equivalent [S11]; we choose uppercase so a string comparison is an identity comparison. A colon stays literal because real names contain it (`Audit:ExcursionSubmitted` in the baseline workflow).
2. **ASCII only, repo-relative POSIX.** No backslash, no `..`, no leading slash, no empty segment, no percent sign in a path. MEASUREMENT: 106 of 106 tracked paths of this worktree fit; a path that does not is a finding, not a silent skip.
3. **Never derived from a label.** A display title is an attribute.
4. **Per-type fragment grammar** (the "registry"): part of the type table. Examples: symbol = dotted Python name; requirement = the first CSV column; term and bounded context = the okf `slug()` of the name; workflow element = `<kind>/<name>`; UI node = `<kind>/<data-eija-key>`.
5. **Fragments resolve to exactly one thing.** Two matches is an ambiguity finding (the okf `md-table-row-v1` addresses a row by the slug of any cell).
6. **Canonical slug form.** The okf resolver accepts `#bend_proof` for the slug `bend-proof` because it compares slugs. Ours accepts only the slug. MEASUREMENT: 7 of 180 okf resources (all `Verification Technique`, from ADR-0018) are non-canonical under this rule.

### 5.2 Alternatives considered

| Option | Stable across edits | Stable across moves | Human readable | Works for code symbols | Verdict |
|---|---|---|---|---|---|
| A. `repo://path#fragment` (okf lane) | yes | no, needs rename records | yes | yes | **chosen**: it is the okf link target already, and already 173 of 180 conforming |
| B. Opaque UUID stored in the artefact (Doorstop UIDs) | yes | yes | no | no: an id in every function is source pollution an agent must allocate | reject for code; requirement ids (`AC01`) already are intrinsic keys |
| C. Content hash as id (git blob, SWHID) | no: changes on every edit | no | no | no | reject as id; keep as digest and alias |
| D. SCIP symbol string | yes | partly | fair | yes, for languages with an indexer | alias for non-Python symbols in a later MINOR version [S14] |
| E. Label-derived slug | no | no | yes | no | reject (D-23) |

Moves are a known cost of A. Indicative size: after 100 commits, 20.6 percent of the symbols of the Doorstop source repository and 3.3 percent of those of StrictDoc were no longer present at their original path and name (`target_symbol_missing_rate` in `graph/bench/results/traceability-staleness-{doorstop,strictdoc}.json` [trace]). That measure counts every absence, deletions included; it does not separate moves and renames from deletions and involves no Doorstop anchor, so it bounds neither the rename rate nor the orphan rate of our ids. Mitigation below.

### 5.3 Renames

A rename is an edge `renamed_to` from the old id to the new id, emitted by a codemod, never inferred by similarity. The start id may be absent from the graph (a tombstone); the end must exist; both have the same node type. Two forms: an **id-level** record (the end carries a fragment) and a **path-level** record (two file ids without fragments) that moves every fragment of a file in one record.

**Rewriting system and strategy.** Let `R_id` be the id-level records and `R_path` the path-level ones, each read as a rule `old -> new`. The path-level rule is lifted to fragments: `p -> q` also rewrites `p#x` to `q#x`. Both may apply to one id (`repo://a.py#f` matches the path rule for `a.py` and possibly an id rule for `a.py#f`), so the system is not deterministic by itself. `resolve(id)` fixes the strategy: apply the id-level rule if one matches the whole id, otherwise the path-level rule for its file part, and repeat until neither applies.

**What holds.** Assume the records are functional (no two records share a left side, `out<=1`). Then `resolve` is a deterministic function of the record set: it does not depend on record order (C7: 100 seeded chains, 10 shuffles, 3 probes each, 0 order-dependent results; the maps are built from sorted records, so even a rejected non-functional set gives one answer). The set of ids reachable from any start is finite, so `resolve(x)` terminates iff its trajectory does not revisit an id, and then its result is the unique normal form under that strategy. Termination is a property of the **lifted** system with the priority strategy, not of the relation `renamed_to` alone: the kind is declared acyclic, functional and injective, and that is not sufficient. Counterexample (a test, and C7): the records `repo://a.py -> repo://b.py` (module) and `repo://b.py#f -> repo://a.py#f` (symbol) are each well typed and the relation has no cycle, yet `resolve("repo://a.py#f")` sends `a.py#f` to `b.py#f` by the path rule and back by the id rule, forever. An earlier revision of this section claimed termination iff the single relation is acyclic; that was wrong.

**Check.** A cycle of the lifted system contains a step taken at some id where a rule applies by its left side (an id-level step at a left side, or a path-level step at a file id or at that file id extended by a fragment; a path-level-only cycle also cycles the fragment-less file ids). So walking `resolve` from every left side of every record finds every non-terminating trajectory: `typecheck.check_document` reports `rename-cycle` (candidate rule: WV-056 family) and `identity_checks.check_renames` reports `composite-cycle`. Two independent implementations agree with each other and with a brute-force search over all probe ids on 400 seeded random systems of 1 to 5 records over 4 files (test seed 20260929; 54 of the 400 contain a loop; the pool of probe ids is every file, alone and with fragments `f`, `g`, `h`). This is an exhaustive check on a small domain plus a proof sketch, not a machine-checked proof; the formal lane may take it as an obligation. Alternative not taken: forbid mixing the two levels over one file. The check is cheaper than the restriction and keeps the useful "move the file, then rename one function" record pair.

### 5.4 Aliases and exports

| Alias | Definition | Use | Note |
|---|---|---|---|
| UUIDv5 | `uuid5(EIJA_NS, id)`, `EIJA_NS = uuid5(NAMESPACE_URL, "urn:eija:weave:id-namespace:1")` = `504a1617-fcab-5ac4-80d6-bd272560936e` | SysML v2 `@id`, Cypher/CSV keys | RFC 9562: UUIDv5 hashes namespace plus name with SHA-1, equal inputs give equal UUIDs [S10]. MEASUREMENT: a hand implementation equals the standard library on 2000 ids, 0 collisions. Not a security claim |
| xs:ID | `"eija-" + uuid` | ArchiMate exchange XML | The Archi copy of the exchange XSD types `identifier` as `xs:ID` [S6]; a UUID may start with a digit, hence the letter prefix. That `xs:ID` needs an NCName start is UNVERIFIED here (the W3C page returned no text) |
| SWHID `cnt` | `swh:1:cnt:` + SHA-1 of `blob <len> NUL bytes` | optional file alias on file-level nodes | Intrinsic, no metadata such as a name [S9]. MEASUREMENT: equals `git hash-object` for `LICENSE`. **Not a freshness anchor**: it changes with line endings (a two-line file differs between LF and CRLF; `lf-sha256-v1` does not), and SHA-1 |
| SCIP symbol | `<scheme> ' ' <package> ' ' (<descriptor>)+` | non-Python symbols, later | Grammar quoted from `scip.proto` [S14] |
| Neo4j | node property `eija_id` under `CREATE CONSTRAINT ... FOR (n:Label) REQUIRE n.eija_id IS UNIQUE` | export | Never `id()` or `elementId()` [S12], [S13] |

## 6. Canonical form and hashing

### 6.1 Serialisation

**Decision.** RFC 8785 restricted to strings, integers with absolute value at most 2^53-1, booleans, null, arrays and objects. The writer sorts object keys by UTF-16 code units, escapes exactly `"` `\` and control characters (short forms for `\b \t \n \f \r`, `\u00xx` lowercase otherwise), leaves `/` and non-ASCII characters literal, and rejects lone surrogates, floats and out-of-range integers [S2]. The restriction removes the only hard part of JCS, ECMAScript number formatting.

| Option | Byte-identical across platforms and languages | Dependency | Kernel-compatible | Verdict |
|---|---|---|---|---|
| A. Kernel `canonical()` (`json.dumps(sort_keys=True, ensure_ascii=False)`) | No: differs on floats, `-0.0`, integers above 2^53 and key order for supplementary versus U+E000 to U+FFFF characters | none | it is the kernel | reject for new artefacts; leave the kernel alone |
| B. `rfc8785==0.1.4` as runtime dependency (Apache-2.0, pure Python) | Yes | one small package | no | acceptable; not chosen: the verifier's trusted base should be smaller than the check that tests it |
| C. Own subset writer, `rfc8785` as differential test oracle | Yes on the subset | none at runtime | agrees on ASCII keys | **chosen** |
| D. CBOR or protobuf deterministic encoding | Depends on the library | a library | no | not evaluated; a `sysml-toolkit` claim of deterministic CBOR is unrun [mde] |

Evidence (C1): 4000 seeded documents, half with ASCII-only keys, half with keys from a pool that includes U+E000, U+FFFF, U+10000, U+10FFFF and control characters. The own writer equals `rfc8785` 0.1.4 on all 4000. The kernel's `canonical()` equals it on all 2000 ASCII-key documents and differs on 45 of 2000 others, all 45 explained by key order. C1b: code-point order and UTF-16 order disagree exactly for a supplementary character against a character in U+E000 to U+FFFF (18 of 156 ordered pairs of 13 distinct representatives, all of that form). Since every key in a weave record is an ASCII schema name, the kernel's `canonical()` and JCS coincide on every weave record; a test asserts it (D-02). Eight out-of-subset inputs (float, NaN, 2^53, -2^60, lone surrogate, bytes, set, integer key) are rejected.

**Minimal-encoding principle.** An optional field has one encoding, its absence. `null`, `{}`, `[]` and `""` in an optional position are rejected by the schema (`qualifier` has `minLength 1`, `attrs` has `minProperties 1`). Without this, two byte strings would mean one record and the hash would separate equal facts.

### 6.2 Hash structure

```text
dhash(tag, v)    = "sha256:" + hex( SHA-256( ASCII(tag) || 0x00 || JCS(v) ) )       tag = eija.weave.<name>.v<N>
record hash      = dhash("eija.weave.node.v1", node)   |  dhash("eija.weave.edge.v1", edge)
edge id (eid)    = dhash("eija.weave.edge-id.v1", [kind, from, to, qualifier])
shard hash(F)    = dhash("eija.weave.shard.v1", sorted([ ["n", id, rh] .. ] ++ [ ["e", kind, from, to, q, rh] .. ]))    all records asserted by file F
root             = dhash("eija.weave.root.v1", { metamodel_major, shards: sorted([path, shard hash]) [, view] })
closure fp(n)    = dhash("eija.weave.closure.v2", { nodes: sorted([ [id, node rh] for id in C(n) ]),
                                                     edges: sorted([ [kind, from, to, q, edge rh] for edges with both ends in C(n) ]) })      C(n) = dependency closure of n
```

**Row comparator (normative for every implementation).** `sorted(...)` above orders lists of rows, and a row is a list of strings. Compare two rows element by element from the first element; the first differing element decides, and a row that is a proper prefix of another sorts first; two strings compare by their UTF-8 bytes. Every element that is ever sorted is ASCII by schema (ids, kinds, qualifiers matching `[a-z][a-z0-9_]{0,31}`, `sha256:` digests, the tags `n` and `e`, file paths), so byte, code-point and UTF-16 order coincide and no non-ASCII case exists; a test asserts that qualifiers and kinds are ASCII and that non-ASCII ids are non-canonical. Consequence: within a shard every `["e", ...]` row precedes every `["n", ...]` row (`"e" < "n"`), and the shard array is one JSON array of both. The root sorts `[path, shard hash]` pairs the same way. A second implementation checks itself against `identity-vectors.json` key `shard_rows`, which holds one shard with node and edge rows mixed, the shard hashes, the full root and two view roots.

Argument for injectivity (assuming SHA-256 collision resistance, which is an assumption and not proved here): a tag contains no NUL and JCS text contains no raw NUL (control characters are escaped), so the first NUL splits tag from value unambiguously, and `(tag, v)` maps injectively to the hashed bytes. One value is hashed, never a concatenation of fields, so the Doorstop-style ambiguity cannot arise. MEASUREMENT (C2): concatenating `("a","bc")` and `("ab","c")` collides; the JCS-array form does not; the same record under two tags does not. The tag registry in `metamodel.json` (`domain_tags`) prevents two aspects from reusing a tag; two tags are reserved for the ledger and the link certificates.

A **shard** is the set of records asserted by one repository file: a node belongs to the shard of its id's path, an edge to `asserted_in` (the file whose bytes assert it: the link file for declared links, the file the extractor read for derived ones). The root is therefore a two-level Merkle structure with a wide first level; it differs from RFC 6962's binary tree with its 0x00 and 0x01 prefixes [S3] because we need no inclusion proofs (a verifier always has the whole repository) and want localisation by file. A **view root** hashes the records of one named view (`structure`, `trace`, `language`, `assurance`, `ui`, `governance`; the kinds of each are the `views` table of `metamodel.json`): the edges whose kind is in the view plus the node records of their endpoints (a tombstone endpoint has none), grouped in shards as above, with the view name in the root input under the ordinary root tag. Implemented as `view_records` and `graph_root(view=...)`; tests: a change outside the view (an unrelated node, an edge of another kind) leaves the view root unchanged, a change to an in-view edge or an endpoint changes it, an unknown view is an error.

Properties, all MEASUREMENTS on seeded graphs unless marked:

| Property | Result | Check |
|---|---|---|
| Order independence | 200 shuffles of records, key order and list order of a 300-node, 900-edge graph: 1 distinct root. The same shuffles give 200 distinct hashes for `json.dumps` in insertion order, 200 for `sort_keys` with unsorted lists, 200 for networkx `node_link_data` | C3 |
| Localisation | In a graph of 20 shards, changing one node digest changes exactly that shard; adding an edge asserted in a new file adds exactly that shard; reversing both lists changes nothing | C5 |
| Closure fingerprint | 60 random cyclic graphs (40 nodes, 90 edges), one record mutated per trial, five mutations in rotation (12 trials each): a node record, and an edge's class, qualifier, anchors or kind. The set of changed fingerprints equals the kernel `closure()` of the mutated node (or of the edge's source) in all 60. The first revision hashed node records only: it missed all 48 edge mutations, so a declared edge replaced by an inferred one left every fingerprint unchanged | C6 |
| Byte stability | The whole report is byte-identical under `PYTHONHASHSEED` 0 and 12345 (test), and under 1 and 2 (manual) | test |
| Cost of a root | 100,000 nodes and 400,000 edges: root in 16.92 s with the pure-Python writer, 6.55 s with `json.dumps(sort_keys=True, separators, ensure_ascii=False)`, same root; one run, Python 3.12.10, Windows 11, Intel Family 6 Model 167; committed as `graph/bench/results/identity-timing.json` (non-deterministic, kept apart from the byte-stable `identity-checks.json`; rerun `identity_checks.py --write --timing`). An earlier run of the same command gave 18.95 s and 8.21 s (11 and 20 percent higher), so treat these as one-run figures on a shared machine. PREDICTION by linear extrapolation: 10^4 records in about 0.4 s | C11 |
| Cost of closure fingerprints | For one node: a traversal of its closure plus a sort, `O(|C| + |E_C| log |E_C|)`, where `E_C` are the edges induced on `C`. For every node: the sum of closure sizes, up to `O(|V| * (|V| + |E|))` in the worst case (PREDICTION). MEASUREMENT: on the 83-node dogfood graph the sum of closure sizes is 1304 under the metamodel's `affects` (the total is the same whichever direction is followed, section 4.4). Fingerprints are computed on demand for the nodes a query touches, never for the whole graph on every build | C6, section 9 |

The C encoder is admissible only for documents already validated against the schema (it would print `1.0` for a float and accept lone surrogates); the differential test in C1 is the guard.

### 6.3 Simple canonical serialisation versus canonical labelling

**Decision: sort records and hash them. Do not compute a canonical labelling.**

Canonical labelling (nauty; RDFC-1.0 for RDF datasets) assigns labels to nodes that have none so that two graphs receive the same output iff they are isomorphic. RDFC-1.0 states exactly that guarantee and also that some datasets are built to keep the algorithm from terminating in reasonable time [S4]. Graph isomorphism has a quasipolynomial algorithm [S5], and no polynomial one is claimed. That trade is right when nodes are anonymous. Ours are not:

1. **Every node has an intrinsic identity** (the id). Labelling is the identity map, and sorting by id is the canonical form. Derived facts that seem anonymous (an n-ary certificate) receive ids from content (`eid`, `entry_id`); no blank nodes exist, so no labelling problem exists.
2. **Isomorphism invariance is a defect here.** C4: the graph `S1 satisfies R1, S2 satisfies R2` and the graph `S1 satisfies R2, S2 satisfies R1` are isomorphic. A label-free hash gives them one value; an assurance graph must give two, because they assert different claims. Our root differs.
3. **Label-free hashes are not even reliable identifiers.** C4: networkx's Weisfeiler-Leman hash is equal for a 6-cycle and two disjoint triangles, which are not isomorphic. The dossier's plan to use WL as a fast negative filter [math] is unnecessary: the sorted-record root is already O(n log n).
4. **Cost and determinism.** Sorting and hashing is linear after the sort; a labelling has a worst case we would have to guard against with limits, and its output for symmetric inputs depends on tie-breaking.

Revisit trigger: an import format with anonymous nodes (for example a hand-drawn diagram without ids). Then RDFC-1.0 or nauty is used to *derive ids for the import proposal only*, with a step limit, and the result is a proposal the owner accepts, never a hash of the graph.

### 6.4 What the hash does not say

A digest says the normalised slice changed or did not. It does not say the link is true, the code correct or the proof about the code (AGENTS.md, ARCHITECTURE section 3.4). The normaliser can hide a change that mattered (a comment stating an invariant, a callee's behaviour); `ast-v2` reduces one such gap by including same-module private helpers, and each method has a version so a change of normalisation is a new name plus a re-baseline (D-13).

## 7. Schema evolution

| Rule | Mechanism | Check |
|---|---|---|
| One source | `metamodel.json` is edited; three schemas and the README tables are generated; `build_schemas.py --check` fails if a committed file is stale | test |
| Version | `metamodel_version` follows semantic versioning: MAJOR incompatible, MINOR backward-compatible additions, PATCH fixes [S16]. The public API here is the metamodel, the id grammar and the hash methods | doc |
| MINOR | New type, kind, optional attribute, enum value, hash method or signature row. It must not change the record hash of any existing record: hashes depend on records only, and an absent optional attribute is absent from the bytes | property of D4 |
| MAJOR | Removal or rename of a type, kind or field, or a tightened signature. Needs a pure function `migrate(doc_vN) -> doc_vN+1` with a golden test. The root tag carries the major (`metamodel_major` in the root input), so every root changes on purpose | design |
| Closed schemas | `additionalProperties: false` at every record, so an unknown field is an error rather than data an agent can smuggle | tests |
| Hash-method names | Immutable. `ast-v2` was added beside `ast-v1`, not over it | okf lane |
| Deprecation | A deprecated type or kind stays valid for one MINOR series with a `note`, then goes in a MAJOR | design |
| Agents | The schemas are protected paths: an agent may not widen a signature to make a link pass (the agent aspect's `PROTECTED_PATH` set includes `graph/schema/**`) | mcp-tools.md |

Cost: a closed enum means a new value is a MINOR bump that older validators reject. Accepted because the graph, schema and validator live in one repository and move together. Considered and not adopted: open extension bags (an escape hatch that erases the closed-world checks), and schema-to-schema functors (category-theoretic migration [math]: no implementable benefit over a migration function with a golden test).

## 8. Interchange with existing standards

Rule of thumb from the MDE dossier [mde]: narrow, textual, generated projections survive; whole-model round-trips do not. So: every export is get-only and golden-tested; every import is a proposal the kernel checks and the owner decides; an unsupported input is refused with a stable code.

### 8.1 OKF v0.2 (the okf lane owns generation)

| OKF field or rule [S1], or okf-lane extension (marked) | Weave | Direction | Note |
|---|---|---|---|
| `type` (required) | node type via a table | both | 13 okf types map to 9 weave types; 0 of 180 pages have an unmapped type (MEASUREMENT, section 9) |
| `title`, `description` | `attrs.title` (200 chars) | export | description is not stored |
| `resource` | node `id` | both | must match the id pattern of the mapped type: 173 of 180 do today |
| `sources[].resource` | `documents` or `derived_from` edge target | both | OKF entries also carry `id`, `title`, `author`, `usage_count` and `last_modified`; weave uses none of them |
| **okf-lane extension, not OKF:** `sources[].hash_method`, `sources[].sha256` | `to` anchor of that edge: method name and digest `sha256:` plus hex | both | The OKF v0.2 SPEC defines no hash fields; the okf lane adds them as extension keys, which the SPEC's extensions rule permits (unknown keys MAY be included; ADR-0045 and ADR-0046 of the okf lane). The digest function is the okf lane's; weave stores the result |
| `generated.by` | ignored | n/a | |
| `generated.at`, `verified[].at`, `stale_after` | excluded from identity and from every verdict | n/a | they read or record a clock; freshness is by digest |
| `verified[].by` | a ledger `decision` proposal | import | never clears a link |
| `status` (draft, stable, deprecated) | `attrs.okf_status` | both | |
| Body links | not imported | n/a | OKF: "The specific kind ... is conveyed by the surrounding prose, not by the link itself" and consumers must tolerate broken links [S1]. Typed links live in the sidecar; a generated `links` block lists them |
| `index.md`, `log.md`, `okf_version` | not nodes | n/a | `okf_version` goes in the manifest |

The okf lane's hash methods in use, from the bundle, counted as `sources[]` entries: `ast-v2` 63, `md-table-row-v1` 38, `csv-row-v1` 28, `ast-api-v1` 17, `ast-sig-v1` 17, `md-bold-term-v1` 10, `lf-sha256-v1` 9. All seven are in the weave registry.

### 8.2 SysML v2 (first export, emit-only)

Verified against the release repository's training files and the API schema [S8]: `requirement def <'1'> Name { doc /* text */ }`; `satisfy vehicleSpecification by vehicle_design;`; `verification def V { objective { verify R; } }`; `state ... accept ... then ...;` and `first start then normal;`; `metadata def X;` with `metadata X about Y;`; the API JSON schema types `@id` as a UUID string and offers `aliasIds` (array of strings), `declaredShortName` and `qualifiedName`.

| Weave | SysML v2 | Status |
|---|---|---|
| `requirement` | `requirement def <'AC01'> ... { doc /* title */ }` | mapping verified against syntax; emitter not built |
| `satisfies` | `satisfy R by X;` | same |
| `verifies`, `test` | `verification def T { objective { verify R; } }` | same |
| `workflow`, `state`, `transition` | `state def` / `state`; `accept <trigger> ... then <state>;` | syntax verified; guard and effect mapping is a PREDICTION |
| `role`, `guard`, `effect` | `metadata def` plus `metadata X about Y;` | syntax verified; fit is a PREDICTION |
| id | `@id` = UUIDv5 of the `repo://` id; `aliasIds` = `[repo:// id]` | schema-compatible (a UUID string) |

Validation is optional and reports NOT_RUN without a validator. A passing syntax check is not a conformance claim to the standard, and a check of the model is not a check of the code.

### 8.3 Structurizr and LikeC4 (intended architecture, read-only)

Opened: a Structurizr workspace JSON in the repository's tests has top-level `id`, `name`, `lastModifiedDate`, `lastModifiedAgent`, `model`, `views`; element ids are small counter-like strings (`"2"`, `"3"`); elements carry `properties` maps [S7]. So the exported `id` is not an identity, and the modification fields are wall-clock. Mapping (DESIGN): `component` id is `repo://<architecture json>#<slug of the qualified name>`, taken from a `properties` entry the human sets; `id`, `lastModified*` are dropped before hashing. LikeC4's CLI page documents `export json` without describing the structure [S7b]: field mapping is UNVERIFIED and the choice between the two tools stays with the determinism test the MDE dossier proposes.

### 8.4 ArchiMate exchange format (on demand, PREDICTION)

The Open Group page describes a tool-to-tool exchange format for ArchiMate 3.1 and 3.2, not a persistent format; the XSD ships with the standard and free registration is required; XSD licence terms are not stated on the page [S6]. The Archi repository carries an XSD dated 2019, version 3.1, status Preliminary, whose element enumeration includes `ApplicationComponent`, `Requirement`, `Stakeholder`, `Constraint`, `WorkPackage` and whose relationship enumeration includes `Composition`, `Realization`, `Serving`, `Flow`, `Association`; `identifier` is `xs:ID` and references are `IDREF` (opened, [S6]). Candidate mapping, unbuilt and unreviewed: `component` to `ApplicationComponent`, `requirement` to `Requirement`, `persona` to `Stakeholder`, `contains` to `Composition`, `realises` to `Realization`. The direction of `Serving` versus `depends_on` is reversed and needs care. We do not vendor the XSD.

### 8.5 Other targets

| Target | Mapping | Note |
|---|---|---|
| Neo4j (CSV then Cypher `LOAD CSV`) | one label per node type, one relationship type per kind, `eija_id` property with a uniqueness constraint, `qualifier`, `class`, `asserted_in` as properties | GPL-3.0 server: separate user-run process only [S12] |
| SKOS | `term` to `skos:Concept`, `refines` to `skos:broader` | language aspect owns the export |
| SCIP | alias for non-Python symbols (later) | [S14] |
| SARIF | finding locations use `repo://` ids | rules aspect |

## 9. Applied to this repository

`graph/bench/metamodel_dogfood.py` builds a graph from real artefacts with stdlib parsers: the excursion workflow, the acceptance matrix, the ubiquitous-language terms of `ARCHITECTURE.md`, the ADR files and two Python functions. It is a prototype, not the extractor lane's product. Results (MEASUREMENT, committed in `graph/bench/results/metamodel-dogfood.json`; counts move as files are added, rerun to refresh):

| Check | Result |
|---|---|
| Graph | 83 nodes, 108 edges (`contains` 23, `depends_on` 37, `flows_to` 8, `verifies` 40), 25 shards |
| Schema validation (`graph.schema.json`) | 0 errors |
| Reference checker (typing, cardinality, cycles, dangling) | 0 findings |
| Ids | 0 non-canonical |
| Determinism | root equal after a second clean extraction and when extraction order is shuffled |
| `workflow-semantic-v1` reimplemented from JSON | equals the kernel `Workflow.semantic_hash` |
| `csv-row-v1`, `lf-sha256-v1`, `md-bold-term-v1` | equal to the okf lane's `digest()` on every node checked |
| okf bundle | 180 concept pages, 13 okf types, all mapped; 173 resources match the id pattern of their mapped type, 7 do not (non-canonical fragments such as `bend_proof`) |
| Acceptance matrix | 28 requirements, 44 evidence references: 40 name an existing test or smoke file (7 distinct files), **0 name a function**, 2 name `docs/verification/VERIFICATION.md` (a document, not a verifier), 2 name `application/verifier.py`, which does not exist as written (the path lacks `src/eija_studio/`); two requirements (AC26, AC28) end with no `verifies` link. AC09 and AC12 each cite the unresolved `application/verifier.py` beside existing test files (`tests/test_domain.py`, `tests/test_http_and_architecture.py`; `tests/test_application.py`), so both do get `verifies` links to those files; AC26 and AC28 cite only `docs/verification/VERIFICATION.md` and are the two with none (an audit note that AC12 also lacks a link is wrong: its evidence names `tests/test_application.py`, which exists) |

What this says: the metamodel fits the artefacts that exist, the hash methods interoperate with the okf lane and the kernel, and the traceability that exists today is at file granularity, so the migration path is file-level `test` nodes first and function-level nodes as links are written. It does not say the acceptance matrix is right; it says which of its references resolve.

## 10. Interfaces to other aspects and lanes

| To | What weave-metamodel provides | What it needs | Status |
|---|---|---|---|
| okf lane | id grammar and canonical fragment rule; registry of 14 methods (8 registered, 6 proposed); edge anchor shape; `okf_bundle` mapping test | `digest(root, ref, method)`, `parse_uri`; register `workflow-semantic-v1`, `workflow-element-v1`, `json-key-v1`, `html-key-v1`, `law-block-v1`, `okf-human-v1`; regenerate 7 pages with canonical fragments; add `ast-v2` to ADR-0046 | proposed |
| links and ledger aspect | `anchors[]`, `eid`, decision ids as entry ids, `renamed_to` records | accept `anchors[]` over single `method`/`digest`; `entry_id` over `ledger_seq` (consistency-sync F3); use tag `eija.weave.ledger-entry.v1` | proposed |
| storage aspect | record, shard and root definitions; edge key `(kind, from, to, qualifier)` | implement the root as specified (their flat streamed dump equals a one-shard tree at small size; beyond about 10^5 edges they already propose partitions); add `qualifier` to the edge primary key | proposed |
| rules aspect | `edge_signature` relation (`metamodel.json`), `typecheck.py` as executable definition; obligations by rule id | agree with `typecheck.py` on the fixtures; number three candidate rules: non-canonical id, invalid rename record, duplicate or self-loop edge | proposed |
| impact-ranking aspect | `affects`, `cover_role`, `rank_weight`, `soundness` on every kind | narrow the anchor lint (section 4.4); `render_bytes` and test `cost` are not in the metamodel: they are derived, so store them nowhere and compute at query time, or add optional attributes in a MINOR version | open |
| human-views aspect | `layer`, `truth`, `ddd_role`, `trace`, obligations | none | consistent (their tests pass against this file) |
| agent aspect | `NodeId` pattern is looser than the schema; the schema is the authority; `graph/schema/**` protected | tighten `NodeId` to the schema pattern | proposed |
| kernel | reference oracles in tests only: `Workflow.semantic_hash`, `closure()`, `canonical()` | nothing; a kernel move to JCS would need its own ADR | none needed |
| quality lane | `quality/sessions/graph.py` runs `build_schemas.py --check` and the tests; the `graph` extra pins `jsonschema==4.26.0` and `rfc8785==0.1.4`; the 38 tests pass on both the locally installed jsonschema 4.25.1 (37 without the hash-seed test) and on 4.26.0 (all 38, one run with `rfc8785` 0.1.4 present) | nox session | not written by this aspect | |

## 11. Risks and limits

| Risk | Consequence | Mitigation | Label |
|---|---|---|---|
| A normaliser hides a meaningful change | False fresh link | Versioned methods; `ast-v2`; per-kind policy; human ack for SUSPECT | limit |
| Path moves break ids | Loud ORPHANED links | Rename records, path-level form; a removed id without a record is a finding (WV-008) | measured elsewhere [trace] |
| Both-end anchors raise SUSPECT volume | Review fatigue | Method choice per end; measure on EIJA history before enforcing (phase 4) | PREDICTION |
| `both` flow inflates closures | Noisy impact | Tiers by soundness; narrow the lint; witness paths | MEASURED 4.5 times on 83 nodes |
| Closed enums slow evolution | PR per new value | Accepted; one repository | design |
| Reference checker and rule lane diverge | Two definitions of well formed | Fixture agreement test; the formal lane's independent instance checker (`graph/formal/eijaref/metamodel.py`) has nothing rename-specific, so it can differ from `typecheck.py` on mixed-level rename sets (PREDICTION: not run on such sets) | open |
| Mixed-level renames loop although each record is valid | `resolve` does not terminate on some id | Composite check from every left side (section 5.3), test with the counterexample; candidate WV-056 family rule | fixed in this revision |
| Hash cost at large scale | Slow rebuild | C encoder after validation; shard cache keyed by file content hash | MEASURED 6.6 to 16.9 s at 500k records (one run, `identity-timing.json`) |
| SHA-256 collision | Undetected change | Assumed infeasible; algorithm named in the digest string (`sha256:`) for agility | assumption |
| POSIX byte identity | Untested | Only Windows was run | NOT_RUN |
| Benefit to agents or humans | Unproven | Measurement is the hci and eval lanes' job | UNMEASURED |

## 12. Reproduce

```text
python graph/schema/build_schemas.py --check                 # generated files current, tables coherent
python graph/bench/identity_checks.py                        # C1 to C10, canonical JSON, byte-identical between runs
python graph/bench/identity_checks.py --timing               # adds C11 (not deterministic)
python graph/bench/identity_checks.py --write --timing       # also writes results/identity-timing.json (machine and Python recorded)
python graph/bench/metamodel_dogfood.py                      # section 9
python -m pytest tests/graph/test_metamodel_identity.py      # 38 tests; a missing optional package is a skip (NOT_RUN)
```

Optional oracles used for one session and not committed: `rfc8785==0.1.4` installed under `.tmp/site` (source read before running), `networkx` 3.5. Without them the affected checks report NOT_RUN.

## 13. Open questions

1. Will the okf lane register the proposed methods and regenerate the 7 non-canonical pages? Until then the pages and this metamodel disagree.
2. Does the link aspect accept two anchors per link instead of one? If not, `satisfies` and `verifies` lose their requirement-side anchor and requirement edits stop making links suspect.
3. Should the impact aspect's anchored-end lint be split, so that "the link is suspect" (always, from anchors) and "the far node is affected" (per `affects`) are separate? Nine kinds hinge on it.
4. Where is `render_bytes` computed, and is it stored? Stored numbers derived from rendering would change record hashes on every format change; I recommend computing it at query time.
5. Should `technique` (a kind of verification evidence, seven okf pages from ADR-0018) be a node type? Today it maps to `document`.
6. Which validator, if any, runs against exported SysML v2 text? Not chosen; NOT_RUN by default.
7. POSIX: one run of the bench on Linux or WSL and a committed golden.

## 14. Sources (opened 2026-09-29)

| Key | URL | Used for |
|---|---|---|
| S1 | https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md | OKF v0.2 fields (`type`, `resource`, `sources[]` with `resource`, `id`, `title`, `author`, `usage_count`, `last_modified`; `generated`, `verified`, `stale_after`, `status`); untyped links; broken links tolerated; extra keys allowed. No hash fields |
| S2 | https://www.rfc-editor.org/rfc/rfc8785 | JCS: string escaping, UTF-16 key order, no NaN or Infinity, lone surrogates, Informational status |
| S3 | https://www.rfc-editor.org/rfc/rfc6962 | Merkle tree hash with 0x00 leaf and 0x01 node prefixes, second-preimage rationale |
| S4 | https://www.w3.org/TR/rdf-canon/ | RDFC-1.0: isomorphic iff same output; poison graphs; Recommendation 2024-05-21 |
| S5 | https://arxiv.org/abs/1512.03547 | Babai: graph isomorphism in quasipolynomial time |
| S6 | https://www.opengroup.org/open-group-archimate-model-exchange-file-format ; https://github.com/archimatetool/archi (file `org.opengroup.archimate.xmlexchange/xsd/archimate3_Model.xsd`) | ArchiMate exchange: purpose, versions; XSD `xs:ID`, element and relationship enumerations |
| S7 | https://github.com/structurizr/structurizr (file `structurizr-dsl/src/test/resources/dsl/spring-petclinic/workspace.json`) ; S7b https://likec4.dev/tooling/cli/ | Structurizr JSON shape; LikeC4 `export json` undocumented structure |
| S8 | https://github.com/Systems-Modeling/SysML-v2-Release (training files 25, 32, 34, 39) ; https://github.com/Systems-Modeling/SysML-v2-API-Services (`conf/json/schema/metamodel/Unioning.json`) | SysML v2 textual forms; `@id` UUID, `aliasIds` |
| S9 | https://www.swhid.org/specification/v1.2/5.Core_identifiers/ | SWHID syntax and `cnt` computation |
| S10 | https://www.rfc-editor.org/rfc/rfc9562 | UUIDv5 definition and determinism |
| S11 | https://www.rfc-editor.org/rfc/rfc3986 | unreserved characters; hex case equivalence; fragment ABNF |
| S12 | https://neo4j.com/docs/cypher-manual/current/functions/scalar/ | `id()` and `elementId()` stability and reuse |
| S13 | https://neo4j.com/docs/cypher-manual/current/constraints/managing-constraints/ | uniqueness constraint syntax and edition |
| S14 | https://github.com/scip-code/scip/blob/main/scip.proto | SCIP symbol grammar |
| S15 | https://en.wikipedia.org/wiki/Order-sorted_logic | order-sorted signature definition (secondary source) |
| S16 | https://semver.org/ | MAJOR, MINOR, PATCH rules |
| S17 | https://json-schema.org/draft/2020-12/json-schema-core | `$defs`; `$ref` with sibling keywords |
| local | `graph/bench/identity_checks.py`, `graph/bench/metamodel_dogfood.py`, `graph/bench/results/*.json`, `tests/graph/test_metamodel_identity.py`; sibling worktree `okf` (`quality/okf/codelink.py`, `okf/` bundle), read-only | all MEASUREMENTs |

Not opened or not confirmable: W3C XML Schema datatypes (ID and NCName), the ArchiMate specification pages (behind a login), Goguen and Meseguer's original order-sorted algebra paper, nauty's licence page. Nothing is built on them.
