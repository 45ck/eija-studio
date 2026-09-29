# Math and CS foundations for the weave graph

Research dossier, lane `weave`, ADR block 0089-0112. Accessed 2026-09-29. Author: research agent. Status: input to ADRs, not a decision record.

## 0. Decisions first

| # | Decision | Why (one line) | Evidence |
|---|---|---|---|
| D1 | The trust path uses no graph database. Canonical store is sorted JSON Canonicalization Scheme (JCS) JSONL; SQLite (stdlib) is a rebuildable query index. Neo4j and similar are export targets only. | Licence, footprint and result-order risks; SQLite already gives least-fixed-point queries (`WITH RECURSIVE ... UNION`) and matched the kernel closure on 300 random graphs. | S27, S2, M5 |
| D2 | Rules are stratified Datalog-lite (SQL views in stratum order plus a small stratification checker). No external Datalog engine in the default path. | Datalog terminates and is PTIME in data; the checks we need are positive reachability plus stratified negation. | S20, S27 |
| D3 | Add a status lattice in `graph/eijagraph` and propose a kernel ADR: the kernel `aggregate_status` is order-independent on flat receipt lists but does not compose when re-applied to its own output. | Measured counterexample: flat `CONFLICT`, rolled-up `FAIL`. | M4 |
| D4 | Ban library-default ordering in artefacts. Use min-member SCC labels, lexicographic topological order, quantised ranks with ID tie-break, JCS for new graph files. | Measured: `nx.condensation` labels took 24 forms over 200 insertion orders; `graphlib` order 5; PageRank floats 40 of 40 different. | M1-M3 |
| D5 | Incremental rebuild is a small custom verifying-trace rebuilder with early cutoff over Merkle hashes. Salsa, differential dataflow and DBSP are inspiration, not dependencies. | Build Systems a la Carte gives the correctness and minimality definitions; nothing off the shelf targets Python plus Windows plus our artefacts. | S15, S14 |
| D6 | Every reported violation carries a re-checkable witness (a derivation path), not prose. | Provenance-semiring idea, restricted to the positive fragment where the theory applies. | S10 |
| D7 | Probabilistic confidence (conservative Bayesian, subjective logic) is display-only and labelled PREDICTION. Never a gate. | Their hypotheses (operational profile, independence) do not hold for agent-written property tests. | S26 |
| D8 | Category theory, CRDT libraries, treewidth, double-pushout tooling: theory-only. One named check is adapted from each where it yields a test. | No implementable benefit beyond a law or a vocabulary. | Section 2 |

Measurements M1-M5 come from `graph/bench/foundations_checks.py` (committed, deterministic, Windows 11, Python 3.12.10, networkx 3.5, SQLite 3.49.1) and `tests/graph/test_foundations_checks.py`. They are exhaustive over a small domain or seeded samples; none is a proof for all inputs.

## 1. Scope and method

* Read: `src/eija_studio/domain/{impact,models,evidence}.py`, `AGENTS.md`, `docs/adr/README.md`, `docs/oss/REGISTER.md`, `docs/architecture/ARCHITECTURE.md`. Read-only look at sibling lanes: `okf` (`quality/okf/codelink.py`: `repo://path#fragment` URIs plus named hash methods `ast-v1`, `ast-api-v1`, `lf-sha256-v1`, `csv-row-v1`, `md-bold-term-v1`, `md-table-row-v1`), `quality` (ADR-0035: import-linter layers, grimp import graph), `metrics` (grimp module graph, "hash is not proof" honesty conventions), `visual` and `agents` (existing artefacts only).
* ProofMap Lite is a private repo; I read its README and `docs/gap-audit.md` through `gh`. Lessons are in section 2.9.
* Web: the shared WebSearch budget (200 of 200) was already spent by other agents, so **no search queries were possible**. Every source is a direct fetch of a URL I already knew (papers, specs, repo pages, docs). Licences, archive flags and push dates were taken from the GitHub API record and the LICENSE file (`gh api repos/<o>/<r>[/license]`), because page summaries proved unreliable (a summary said Joern 2.0.1 while the API says v4.0.640).
* Inaccessible: ACM DL (403), Project Euclid (Tarski: metadata only), Inria HAL and lip6 (CRDT paper), Stanford ilpubs (PageRank report), Brandes PDF (404), Wikipedia "Self-adjusting computation" (404), Jane Street `incremental` (404), nauty site (TLS error; licence read from the COPYRIGHT bundled in the pynauty repo). The Green et al. and Cooper et al. PDFs were opened and text-extracted locally. The Cousot 1977 PDF is a scanned image, so nothing is stated from it.
* Web pages are treated as data; no fetched code was run. `rfc8785==0.1.4` (pure Python, no dependencies) was installed into `.tmp/site` for one optional check.

## 2. Schools of thought: what is implementable

Format per card: **Result** (hypotheses) - **EIJA use** - **Oracle** - **Cost** - **Verdict**.

### 2.1 Graph theory

**Strongly connected components and condensation.** Result: Tarjan's algorithm is O(V+E) and emits components in reverse topological order of the condensation (S30). Hypotheses: finite directed graph. EIJA use: cycles are real in our graph (rule to journey to obligation loops); collapse each SCC into one node before any DAG algorithm, and report every cycle deterministically. Note `graphlib.TopologicalSorter` reports "only one undefined choice" among several cycles (S6). Oracle: SCCs equal mutual-reachability classes computed by brute-force closure; output identical under 200 shuffled insertion orders after relabelling each SCC by its minimum member ID (M2). Cost: trivial. Verdict: **adopt** with the relabel wrapper.

**Topological order.** Result: not unique; `graphlib` states order "may depend on the specific order in which the items were inserted" (S6). Recipe: lexicographically smallest topological order (`nx.lexicographical_topological_sort`), 1 distinct output versus 5 for `graphlib` over 200 shuffles (M2). Verdict: **adopt**.

**Dominators.** Result: Cooper-Harvey-Kennedy iterative algorithm is a dataflow fixed point, O(N^2) worst case, faster than Lengauer-Tarjan until about 30,000 nodes in their experiments (S30a). Hypotheses: a single entry node. EIJA use: "single point of failure" in evidence paths: node d dominates evidence e for requirement R if every path R to e passes d. Oracle: d dominates n iff deleting d makes n unreachable (brute force on random DAGs). Cost: low. Verdict: **adopt** (networkx `immediate_dominators`, S8).

**Transitive reduction.** Result: unique for a DAG and a subgraph of it; not unique with cycles (S30b); networkx requires a DAG and drops attributes (S8). EIJA use: flag redundant links (requirement linked both directly and via a design element) and draw readable diagrams. Run on the condensation. Oracle: reachability preserved; every removed edge has an alternate path. Verdict: **adopt**.

**Min-cut and vertex capacities.** Result: max-flow equals min-cut; vertex capacities by node splitting (S30c). Blast radius is the closure, not a cut. The cut answers the inverse question: the smallest set of nodes whose loss severs all evidence for a requirement (redundancy k). Min cuts are not unique, so canonicalise (for example the source-side minimal cut) and verify it by brute force on small graphs. Cost: flow per requirement. Verdict: **adapt** (report only).

**PageRank and personalised PageRank.** Result: aider ranks a file dependency graph and weights files in the chat; budget default 1k tokens (S7). networkx exposes `personalization` and warns "no guarantee of convergence" (S8); my run hit `PowerIterationFailedConvergence` at tol 1e-12 with the default 100 iterations. Floats differed bitwise in 40 of 40 insertion orders on a 300-node graph; rounding to 1e-10 collapsed them to one result and one top-20 order (M3; boundary straddling not excluded). EIJA use: `relevant(node, k)` for the agents lane to pack context. Design (PREDICTION, not built): fixed-iteration integer or `Fraction` power iteration, so results are bit-identical on any platform, then quantise and break ties by ID. Oracle: shuffled-insertion invariance plus a seeded sanity test that the seed node ranks first. Verdict: **adapt**. Relevance is a heuristic, never evidence.

**Betweenness.** Brandes' algorithm (networkx cites it); sampling with `k` is non-deterministic unless seeded (S8). Use exact only; report as a hub metric. Brandes' paper was not opened (complexity unverified). Verdict: **adapt** (metric only).

**Treewidth.** NP-complete in general, fixed-parameter tractable, Courcelle's theorem for bounded width (S30d). At our sizes (workflow at most 64 transitions, graphs in the thousands) nothing needs it. Verdict: **theory-only**.

### 2.2 Order theory, lattices, fixed points

**Knaster-Tarski and Kleene.** Result: a monotone map on a complete lattice has a lattice of fixed points; if it preserves limits of ascending chains, the least fixed point is the limit of f^n(bottom) (S11). Hypotheses: monotone on a complete lattice; iteration terminates when the lattice has finite height. EIJA use: `impact.closure` is the least fixed point of X to roots union successors(X) on the powerset of a finite node set. Make that explicit and reuse one worklist solver for closure, dominators and rule strata. Oracles: (a) F(closure) equals closure; (b) any S with F(S) subset of S contains closure; (c) monotone in roots and in edges; (d) already measured: closure equals `networkx.descendants` and SQLite recursive CTE on 300 random graphs, 0 mismatches (M5); 20k nodes and 60k edges took 0.057 s once on this PC. Verdict: **adopt**.

**Galois connections and abstract interpretation.** Result: a monotone Galois connection F(a) <= b iff a <= G(b) supports sound approximation (S12). The Cousot 1977 paper is the origin (URL opened, text not readable). EIJA use: the `envelope` string in `model_impact` admits its graph is an abstraction. Make it structural: every edge carries a soundness class `must`, `may` (over-approximation), or `heuristic` (may miss; for example grimp does not see dynamic imports, S32). Impact reports separate reach through sound edges from reach that needs heuristic edges. Oracle: seeded fault injection: change a real dependency and check the impact set contains it; misses must trace to a `heuristic` edge. Verdict: **adapt** (discipline, no abstract domain library).

**Status lattice.** Result (my construction, verified by enumeration): the order UNKNOWN < STALE < {PASS, FAIL} < CONFLICT is a bounded lattice whose join equals the kernel `aggregate_status` on every flat multiset of length up to 6 over {PASS, FAIL, STALE, UNKNOWN}, satisfies commutativity, associativity and idempotence, and composes under roll-up (M4). The kernel function is order-independent but is not associative on its range: `CONFLICT` is not absorbing, so `agg([agg([PASS,FAIL]), FAIL])` returns FAIL while the flat call returns CONFLICT. This is Belnap's four-valued shape (true, false, both, neither as an information lattice, S26d) with STALE added as partial information. Gating is a second, different operation (conjunction over independent claims: FAIL, CONFLICT, STALE, UNKNOWN, PASS as a chain minimum), so keep two operators and never mix them. Oracle: exhaustive law tests on 5 values. Cost: kernel change needs its own ADR; meanwhile implement in `graph/` and test agreement on flat inputs. Verdict: **adopt**.

### 2.3 Datalog, relational algebra, provenance

**Datalog evaluation.** Result: bottom-up naive and semi-naive evaluation reach the minimal model; evaluation always terminates (finite Herbrand base), data complexity is P-complete; stratified negation forbids negation through recursion; safety needs head variables in the body (S20). EIJA use: link rules such as `uncovered(R) :- requirement(R), not verified(R)` become the "linter": each head is a named diagnostic. Implement strata as ordered SQL views, plus a checker that rejects negation inside a recursive stratum. SQLite `WITH RECURSIVE` with `UNION` discards repeated rows, so cyclic graphs terminate; without `ORDER BY` extraction order is undefined and recursive selects cannot use aggregates (S27). Oracle: naive versus semi-naive equality; permutation invariance of the sorted result. Cost: small; the checker is ours. Verdict: **adopt** (Datalog-lite); Souffle and Nemo remain optional processes (section 3).

**Provenance semirings.** Result (Green, Karvounarakis, Tannen, PODS 2007; text-extracted locally): annotating tuples with elements of a commutative semiring K generalises positive relational algebra; Proposition 3.5: a map h between semirings commutes with every positive-algebra query iff h is a semiring homomorphism; polynomial annotations are the most general and every other annotation factors through them; recursion needs semirings with fixed points, and provenance of recursive queries can be infinite (formal power series). Hypotheses: **positive** relational algebra and Datalog; no negation in that paper. EIJA use: do not store polynomials. Store one canonical minimal derivation per fact (shortest path, ties broken by sorted edge IDs). Answers "why is this link here / why is this requirement affected" as a path of base edges. Missing-evidence findings have no semiring explanation; their witness is the declared closed-world scope (which links were searched). Oracle: re-run closure on the witness subgraph only and recover the fact; delete any witness edge and the fact must vanish for a minimal witness. Cost: one parent pointer per fact. Verdict: **adapt**.

### 2.4 Rewriting and bidirectional transformation

**Double-pushout graph rewriting.** Result: rule L <- K -> R, deletion by pushout complement then addition by pushout, dangling-edge condition, applications potentially non-deterministic, termination undecidable (S20). Tools (GROOVE, Henshin) are Java modelling tools; GROOVE explores state spaces and model-checks (S20). EIJA use: none for the kernel. Adapt one theorem for **normalisers** (ID canonicalisation, wiki link rewriting): Newman's lemma, terminating plus locally confluent gives a unique normal form (S20b). Oracle: apply rules in 100 random orders, expect one normal form. Verdict: **theory-only**, with the confluence test **adapted**.

**Lenses.** Result: `get`/`put` with GetPut and PutGet (and PutPut for very well-behaved lenses) (S20c). EIJA use: visual lane generates diagrams (get); human edits in draw.io are proposals (put) that produce a change bundle, never an applied change. Oracles: `get(put(s, v)) == v` and `put(s, get(s)) == s` on generated models. ProofMap Lite hit exactly these problems (GAP-010, GAP-030). Verdict: **adapt**.

### 2.5 Semantic diff, canonical forms, hashing

**Tree and graph edit distance.** GumTree (Falleri et al., ASE 2014; LGPL-3.0, see section 3) and APTED (O(n^3) time, O(mn) space, MIT; known issue above 40k nodes, S17). With stable node IDs a keyed diff (set difference plus per-node semantic hash) is O(n) and exact, so edit distance is only needed for artefacts without IDs (draw.io XML, DOM). Oracle: `apply(diff(a, b), a) == b`; `diff(a, a)` empty. Verdict: **adapt** (keyed diff); GumTree as an optional process.

**Canonical serialisation versus graph canonical labelling.** The kernel `canonical()` is `json.dumps(sort_keys=True, separators, ensure_ascii=False)`. Against RFC 8785 (JCS, Informational; sorts keys by UTF-16 code units, ECMAScript number rules, integers beyond 2^53 as strings; S13) it differs on `1.0`, `1e-07`, `-0.0`, integers above 2^53 (JCS refuses them) and key order for astral versus BMP characters (M1). Same-platform Python hashing is unaffected. Decision: JCS for **new** graph artefacts, floats forbidden (integers and strings only); do not change kernel hashes without an ADR. Canonical labelling (nauty, RDFC-1.0) is needed only for nodes without stable IDs. RDFC-1.0 (W3C Recommendation 2024-05-21) guarantees identical output iff datasets are isomorphic and warns some inputs will not terminate in reasonable time (S19). Graph isomorphism is quasipolynomial (Babai, S18) but hard in practice. Weisfeiler-Leman hashes: equal for isomorphic graphs, collisions possible (S8). So WL is a fast-negative bucket filter, never an identity. Verdict: JCS **adopt**; labelling **adapt** only for ID-less imports; WL **adapt** as filter.

### 2.6 Merkle structures and hash-consing

Result: a Merkle DAG makes a parent hash cover its children (git: a commit hash transitively covers tree and parents, S21); leaf and internal nodes need distinct prefixes to block second-preimage confusion (S21b). Hash-consing shares structurally equal values, giving O(1) equality (S21a). EIJA use: node hash = H(domain tag, kind, JCS fields, sorted child hashes); one root per view; SCCs hashed as a unit (design, my reasoning: Merkle needs a DAG). Freshness becomes "root changed, list which subtrees". This is the general form of what the okf lane does per link. AGENTS.md rule stands: a hash identifies content, it does not prove correctness. Oracle: change one leaf, exactly its ancestors change; permute input order, same root. Verdict: **adopt**; hash-consing **adapt** (interning table only in long-running processes).

### 2.7 Incremental computation and build systems

Result: Build Systems a la Carte separates scheduler from rebuilder and defines minimality ("executes tasks at most once per build and only if they transitively depend on inputs that changed") and correctness (S15). Salsa memoises queries with durability and early cutoff (S14a); differential dataflow and DBSP maintain views under input changes (S14b-d). EIJA use: our derived artefacts (link index, closure, diagrams, wiki staleness) are tasks; implement a suspending scheduler with verifying traces keyed on Merkle hashes, and early cutoff when a task's output hash is unchanged. Oracles: incremental output equals from-scratch output after random edit sequences (differential test); a counter shows no task ran whose input hashes were unchanged. Risk: an undeclared dependency yields stale-but-trusted output, so the release tier does a full rebuild and compares. Self-adjusting computation and Adapton: sources not opened, **UNVERIFIED**. Verdict: **adapt** (about 200 lines, ours); engines **inspiration**.

### 2.8 Convergent merge, selection, information, concepts

**CRDTs.** State-based merge must be commutative, associative and idempotent (join semilattice); operation-based needs causal delivery; metadata can grow (S22). EIJA has one owner, but many agents and worktrees append receipts. Content-addressed records merged by set union form a grow-only set, so merges never conflict; contradictions surface as `CONFLICT` in the status lattice, not as merge failures. Oracle: merge commutative, associative, idempotent (property tests). Verdict: **adapt** (idea only), no CRDT library.

**Submodular optimisation and set cover.** Set coverage is monotone submodular; greedy gets (1 - 1/e) for maximum coverage under a cardinality budget (Nemhauser-Wolsey-Fisher) and about ln n for set cover, essentially optimal unless P = NP (Dinur-Steurer) (S23). EIJA use: choose the fewest tests that cover the impacted obligations for the fast tier; ties broken by (cost, ID). Oracle: covers every coverable target; within H(n) of a brute-force optimum on small instances; permutation-invariant. Honest limit: "covers" means covered by declared links; whether those tests would detect faults is a PREDICTION, which mutation results can calibrate. Verdict: **adopt**.

**MDL and information theory.** Two-part codes L(H) + L(D|H); Kolmogorov complexity is uncomputable, so MDL only ranks candidates under a chosen code (S24a). Use: compressed size of canonical model versus generated pages as a trend metric for redundancy. It says nothing about truth. Verdict: **theory-only**, trend metric at most.

**Formal concept analysis.** A formal context (G, M, I) yields a concept lattice through a Galois connection (S24b). Use: offline analysis of requirements-by-tests or modules-by-terms to expose duplicate tests and unlinked concepts. The size bound was not verified. `concepts` (MIT) exists. Verdict: **theory-only** with an optional offline report.

### 2.9 Types, categories, confidence

**Type theory and refinement types.** Refinement types attach predicates to types (Freeman-Pfenning 1991; Liquid Haskell, S25a). In Python the useful part is a many-sorted signature for edges (`verifies: Test -> Requirement`, `realises: Component -> Requirement`) checked by the linter, plus NewType IDs under the quality lane's mypy strict. Predicate-level proofs belong to the smt-bmc lane. Oracle: each seeded ill-typed edge is rejected. Verdict: **adapt** (edge signatures); refinement types **theory-only**.

**Category theory.** Spivak: a schema is a small category, an instance a set-valued functor, and three migration functors translate data between schemas (S25b). Tools: Catlab.jl (MIT, Julia, pushed 2026-07-02) and CQL (AGPL-3.0, last push 2023-04-14). Practical value for EIJA: (1) vocabulary; (2) one checkable law: a view mapping is a graph homomorphism, so a path in the model must map to a path in the view (test on generated diagrams). Pushouts for merge and functorial migration: no implementable benefit found. Verdict: **theory-only**; the homomorphism test **adapted**; CQL **reject** (AGPL, stale).

**Conservative Bayesian inference, subjective logic.** CBI (Zhao, Salako, Strigini, Robu, Flynn) needs a prior confidence bound and tests representative of operation (S26a); Salako and Zhao relax independence but stay Bayesian (S26b). Rule of three: n independent failure-free trials give upper bound 3/n at 95% (S26c). Subjective opinions carry (belief, disbelief, uncertainty, base rate) and keep uncertainty explicit (S26d). Our tests are not drawn from an operational profile, so a failure probability would be pseudo-precision. Keep `UNKNOWN` as explicit unknown mass instead of a probability. Verdict: **theory-only**; if shown, a labelled PREDICTION.

**Lessons from ProofMap Lite (S32).** Its gap register lists what breaks in a draw.io to graph to change-bundle to OpenFastTrace chain: stale generated artefacts (GAP-002), timestamp churn (GAP-003), browser-local drafts mistaken for evidence (GAP-010), docs-only edits suppressing a code-change warning (GAP-027), model views with no typed trace to the canonical graph (GAP-030), and freshness that proves nothing about correctness. Mapping: Merkle freshness (2.6), no timestamps (D4), typed edge signatures (2.9), evidence-kind separation (implication 8).

## 3. Options table

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| NetworkX | BSD-3-Clause | active, 3.7 on 2026-09-21 | dependency (optional extra, pinned) | SCC, dominators, reduction, flow, PageRank; wrap for determinism (M2, M3). Local install is 3.5, pin after ADR | S8, gh API |
| rustworkx | Apache-2.0 | active, 0.18.1 on 2026-07-29 | inspiration | Same algorithms in Rust; only if scale demands (20k nodes closure was 0.057 s) | S9, gh API |
| SQLite | public domain | active | dependency (stdlib) | Recursive CTE = least fixed point; index store | S27 |
| Datalog engine Soufflé | UPL-1.0 | 2.5 on 2025-03-24, active | optional process | C++ compile, provenance (TOPLAS'20 named on its page); Windows build cost UNVERIFIED | S5, gh API |
| Nemo | Apache-2.0 | active | inspiration | Datalog engine in Rust; capabilities UNVERIFIED | gh API |
| CozoDB | MPL-2.0 | last release v0.7.6 2023-12-11, last push 2024-12-04 | reject | Embedded Datalog, but release cadence stalled | S4, gh API |
| Neo4j Community | GPL-3.0 (Enterprise: commercial, closed) | active | export target | Great for ad-hoc exploration; server, JVM, GPL, not in trust path | S2, gh API |
| Kuzu | MIT | archived 2025-10-10 | reject | Frozen; only inspiration | S3 |
| Memgraph | BSL 1.1 / Memgraph Enterprise Licence | active | reject | Not OSI-open | gh API |
| FalkorDB | SSPL-1 | active | reject | SSPL | gh API |
| ArcadeDB, Apache AGE, TerminusDB, Oxigraph, Jena | Apache-2.0 | active | export target | Licence verified; capabilities UNVERIFIED | gh API |
| Salsa | Apache-2.0 or MIT | active | inspiration | Early cutoff, durability; Rust | S14a |
| Differential dataflow | MIT | active | inspiration | Incremental fixpoints; Rust | S14b |
| Feldera (DBSP) | MIT open edition; Enterprise code not MIT | active | inspiration | Needs Docker or a large toolchain; DBSP paper arXiv 2203.16684 | S14c-d, gh API |
| DDlog | MIT | archived 2023-07-07 | reject | Archived | gh API |
| Joern | Apache-2.0 | active, v4.0.640 | export target | Code property graph; JDK 21; code-intelligence dossier owns detail | S16, gh API |
| SCIP | Apache-2.0 | active | export target | Symbol index format; `scip-python` listed | S16 |
| Glean | BSD | active | inspiration | Haskell and C++ fact store; Windows support UNVERIFIED | S16, gh API |
| OpenFastTrace | GPL-3.0 | 4.10.0 on 2026-09-20 | optional process | Invoke as separate Java process only; do not link or bundle; legal review UNVERIFIED | S28, gh API |
| GumTree | LGPL-3.0 (LICENSE file; a page summary saying Apache-2.0 was wrong) | active | optional process | AST diff; Java; run as separate process | S17, gh API |
| difftastic | MIT | active | inspiration | Output "intended for human consumption" | S17 |
| APTED (Python) | MIT | last push 2017-11 | reject | Stale; keyed diff suffices | S17, gh API |
| nauty | Apache-2.0 (bundled COPYRIGHT) | current version listed 2.9.3 | optional process | Canonical labelling via CLI only | S18 |
| pynauty | GPL-3.0-or-later | pushed 2024-09; Linux and macOS wheels only | reject | GPL wrapper, no Windows wheel | S18 |
| rfc8785 | Apache-2.0 | 0.1.4 (2024-09-27), repo active | dependency | JCS, pure Python, no dependencies | S13 |
| RDFC-1.0 | W3C Software and Document Licence | Recommendation 2024-05-21 | inspiration | Algorithm reference for ID-less nodes | S19, gh API |
| SHACL, pySHACL | W3C spec; Apache-2.0 | Recommendation 2017-07-20 | export target | Only if an RDF export exists | S29, gh API |
| GQL, SQL/PGQ | ISO standards | GQL ISO/IEC 39075:2024 | inspiration | Query vocabulary reference | S29 |
| GROOVE, Henshin | UNVERIFIED | Henshin last push 2025-06-26 | inspiration | Graph rewriting tools; no licence file found by API | S20 |
| concepts (FCA) | MIT | active | optional process | Offline analysis | gh API |
| Catlab.jl / CQL | MIT / AGPL-3.0 | active / last push 2023-04-14 | inspiration / reject | Julia; AGPL and stale | gh API |

## 4. Mechanisms table

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Graph theory | SCC condensation, min-member labels | Deterministic cycle reports, DAG algorithms usable | O(V+E) | adopt | S30, M2 |
| Graph theory | Lexicographic topological order | One order for any insertion order | Slightly slower than plain Kahn | adopt | S6, M2 |
| Graph theory | Dominators | Single points of failure in evidence paths | O(N^2) worst case | adopt | S30a |
| Graph theory | Transitive reduction | Redundant-link lint, readable diagrams | Closure cost | adopt | S30b |
| Graph theory | Vertex min-cut | Evidence redundancy number | Flow per requirement | adapt | S30c |
| Graph theory | PageRank and personalised PageRank | Context ranking for agents | Non-deterministic floats unless fixed | adapt | S7, M3 |
| Graph theory | Betweenness / treewidth | Hub metric / none | Seeded sampling / NP-complete | adapt / theory-only | S8, S30d |
| Order theory | Least fixed point, worklist | One solver; closure semantics explicit | none | adopt | S11, M5 |
| Order theory | Galois connection, edge soundness classes | Honest over/under-approximation in impact | Extractors must declare class | adapt | S12 |
| Order theory | Status lattice with join and conjunction | Hierarchical roll-up that composes | Kernel ADR to align | adopt | M4 |
| Datalog | Stratified rules as SQL views | Linter with named diagnostics | Own stratification checker | adopt | S20, S27 |
| Provenance | Minimal derivation witness | Verifiable "why" | One pointer per fact; no negation | adapt | S10 |
| Rewriting | DPO rules | Refactor vocabulary | Undecidable termination | theory-only | S20 |
| Rewriting | Confluence test for normalisers | Unique normal form | Randomised tests | adapt | S20b |
| Bx | Lens laws GetPut/PutGet | Oracle for view generators | Property tests | adapt | S20c |
| Diff | Keyed diff, optional GumTree | Semantic diff, exact with IDs | Edit distance O(n^3) only for ID-less | adapt | S17 |
| Canonical forms | JCS for new artefacts | Cross-platform, cross-language bytes | Forbid floats; kernel differs (M1) | adopt | S13, M1 |
| Canonical forms | nauty / RDFC-1.0 labelling; WL filter | ID-less matching; fast negatives | Hard worst case; collisions | adapt | S18, S19, S8 |
| Merkle | Merkle DAG with domain tags | Precise freshness | SCCs hashed as a unit | adopt | S21 |
| Incremental | Verifying traces plus early cutoff | Minimal recomputation | Undeclared deps; full rebuild at release | adapt | S15, S14 |
| CRDT | Grow-only content-addressed evidence set | Conflict-free multi-agent merge | Semantic conflicts remain | adapt | S22 |
| Optimisation | Greedy set cover, deterministic ties | Small fast test set | Coverage is not fault detection | adopt | S23 |
| Information | MDL or compression trend | Redundancy trend | Not a truth measure | theory-only | S24a |
| FCA | Concept lattice | Duplicate and unlinked groups | Size unverified | theory-only | S24b |
| Types | Many-sorted edge signatures | Ill-typed links rejected | Signature upkeep | adapt | S25a |
| Category theory | Homomorphism test for views | Views preserve paths | Minimal | theory-only (test adapted) | S25b |
| Probability | CBI, rule of three, subjective logic | Uncertainty display | Hypotheses unmet | theory-only | S26 |

## 5. Implications for EIJA

1. **Store and query.** Nodes have stable IDs (OKF `repo://path#fragment` plus the codelink hash method as node content hash); typed edges live in sorted JCS JSONL under `graph/`; SQLite is a disposable index. Edge kinds carry a many-sorted signature and a soundness class.
2. **Compiler diagnostics.** Stratified rule heads are the diagnostics; each has an ID, a severity and a witness derivation. Rules reject negation inside a recursive stratum at load time.
3. **Status algebra.** Ship `StatusLattice` (join for evidence about one claim; chain minimum for conjunction across claims). Test agreement with `aggregate_status` on flat inputs; file a kernel ADR for the composition defect (M4). Do not touch `src/` from this lane.
4. **Determinism package.** `eijagraph.order` provides SCC relabelling, lexicographic topological order, quantised ranking and JCS writing. CI-equivalent local test: shuffled insertion, `PYTHONHASHSEED` matrix, Windows plus POSIX, byte-compare outputs. Ban `nx.condensation` labels, raw `graphlib` order, unrounded floats and timestamps in committed files.
5. **Freshness.** One Merkle root per view; verifying-trace rebuilder with early cutoff; differential test versus scratch rebuild; release tier always rebuilds fully.
6. **Agents.** MCP lane consumes `relevant(node, k)` (deterministic personalised ranking, labelled heuristic) and `explain(finding)` (witness path). Agents propose edges; only the kernel-side verifier promotes them.
7. **Selection.** Fast tier runs the greedy cover of impacted obligations; property and mutation lanes supply the cost and fault-detection calibration.
8. **Models versus code.** Formal lanes (tla, smt-bmc, bend) emit receipts on `model_check` claims whose subject is the model hash; a separate `conforms` claim links model to code with its own status. A mocked or missing run is `NOT_RUN`, never `PASS`.
9. **Quantities to report** (each labelled MEASUREMENT computed from the graph, or PREDICTION): link coverage per requirement, evidence redundancy k, single-point dominators, impact size, staleness by changed subtree, cover size. No confidence percentages.
10. **Graph databases.** Ship `export-neo4j` (CSV) and RDF/SCIP exporters later as adapters; register them in `docs/oss/REGISTER.md`. OKF stays the human-facing projection: its links are untyped and the spec defines no hashing or validation (S1), so typed edges and hashes live in the sidecar, not in prose.

## 6. Gaps and unverified

* No search queries possible (budget spent by other agents); coverage of tools I did not already know is therefore limited. Codemod engines (ast-grep, LibCST, Comby, OpenRewrite), Adapton, Jane Street Incremental, Acar's self-adjusting computation, Datomic, DuckDB with PGQ, Graphify: **not verified**.
* Theorem statements taken from Wikipedia (Knaster-Tarski/Kleene, Galois connection, Newman, max-flow, submodular, set cover, treewidth, Merkle, hash-consing, CRDT, FCA, MDL, refinement types, four-valued logic, subjective logic, rule of three) are secondary sources; the original papers (Tarski 1955, Nemhauser-Wolsey-Fisher 1978, Shapiro et al., Rondon et al., Belnap 1977, Jøsang, Bishop et al.) were not opened.
* Not opened: Brandes 2001, PageRank technical report (only networkx and aider docs), Tarjan 1972, Aho-Garey-Ullman 1972, Menger's theorem, Bodlaender.
* Licences UNVERIFIED: GROOVE, Henshin. GPL-3.0 tools (OpenFastTrace) as a separate process: legal position not reviewed.
* Feldera page summary claimed a very heavy build; checked only that Enterprise code is not MIT. Soufflé semi-naive evaluation and Windows build not verified.
* Design items not yet built or measured: fixed-iteration deterministic PageRank, canonical min-cut, witness re-check, verifying-trace rebuilder, edge soundness classes, stratification checker. All are proposals.
* My measurements use small seeded samples on one Windows machine; POSIX runs are pending. The nx versions differ (3.5 local, 3.7 current).
* Kuzu: only "archived" verified, not the successor project.

## Sources (opened 2026-09-29)

| Id | URL |
|---|---|
| S1 | https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md (repo licence Apache-2.0 via GitHub API) |
| S2 | https://github.com/neo4j/neo4j |
| S3 | https://github.com/kuzudb/kuzu |
| S4 | https://github.com/cozodb/cozo |
| S5 | https://github.com/souffle-lang/souffle |
| S6 | https://docs.python.org/3/library/graphlib.html |
| S7 | https://aider.chat/docs/repomap.html ; https://aider.chat/2023/10/22/repomap.html |
| S8 | https://github.com/networkx/networkx ; docs pages for transitive_reduction, immediate_dominators, condensation, weisfeiler_lehman_graph_hash, betweenness_centrality, pagerank under https://networkx.org/documentation/stable/reference/algorithms/ |
| S9 | https://github.com/Qiskit/rustworkx |
| S10 | https://web.cs.ucdavis.edu/~green/papers/pods07.pdf |
| S11 | https://en.wikipedia.org/wiki/Knaster%E2%80%93Tarski_theorem ; Tarski metadata https://projecteuclid.org/journals/pacific-journal-of-mathematics/volume-5/issue-2/A-lattice-theoretical-fixpoint-theorem-and-its-applications/pjm/1103044538.full |
| S12 | https://en.wikipedia.org/wiki/Galois_connection ; https://www.di.ens.fr/~cousot/COUSOTpapers/publications.www/CousotCousot-POPL-77-ACM-p238--252-1977.pdf (scanned) |
| S13 | https://www.rfc-editor.org/rfc/rfc8785 ; https://github.com/trailofbits/rfc8785.py ; https://pypi.org/pypi/rfc8785/json |
| S14 | a https://github.com/salsa-rs/salsa ; b https://github.com/TimelyDataflow/differential-dataflow ; c https://github.com/feldera/feldera ; d https://arxiv.org/abs/2203.16684 |
| S15 | https://www.microsoft.com/en-us/research/uploads/prod/2018/03/build-systems.pdf |
| S16 | https://github.com/joernio/joern ; https://github.com/scip-code/scip ; https://github.com/facebookincubator/glean |
| S17 | https://github.com/GumTreeDiff/gumtree ; https://github.com/JoaoFelipe/apted ; https://tree-edit-distance.dbresearch.uni-salzburg.at/ ; https://github.com/Wilfred/difftastic |
| S18 | https://github.com/pdobsan/pynauty (incl. bundled nauty COPYRIGHT) ; https://users.cecs.anu.edu.au/~bdm/nauty/ ; https://arxiv.org/abs/1512.03547 |
| S19 | https://www.w3.org/TR/rdf-canon/ |
| S20 | https://en.wikipedia.org/wiki/Datalog ; https://en.wikipedia.org/wiki/Graph_rewriting ; b https://en.wikipedia.org/wiki/Confluence_(abstract_rewriting) ; c https://en.wikipedia.org/wiki/Bidirectional_transformation ; https://en.wikipedia.org/wiki/Double_pushout_graph_rewriting ; https://groove.cs.utwente.nl/ |
| S21 | a https://en.wikipedia.org/wiki/Hash_consing ; b https://en.wikipedia.org/wiki/Merkle_tree ; https://git-scm.com/docs/hash-function-transition |
| S22 | https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type |
| S23 | https://en.wikipedia.org/wiki/Submodular_set_function ; https://en.wikipedia.org/wiki/Set_cover_problem |
| S24 | a https://en.wikipedia.org/wiki/Minimum_description_length ; b https://en.wikipedia.org/wiki/Formal_concept_analysis |
| S25 | a https://en.wikipedia.org/wiki/Refinement_type ; b https://arxiv.org/abs/1009.1166 |
| S26 | a https://arxiv.org/abs/2008.09510 ; b https://arxiv.org/abs/2208.00462 ; c https://en.wikipedia.org/wiki/Rule_of_three_(statistics) ; d https://en.wikipedia.org/wiki/Subjective_logic ; https://en.wikipedia.org/wiki/Four-valued_logic |
| S27 | https://www.sqlite.org/lang_with.html ; https://www.sqlite.org/copyright.html |
| S28 | https://github.com/itsallcode/openfasttrace |
| S29 | https://www.w3.org/TR/shacl/ ; https://en.wikipedia.org/wiki/Graph_Query_Language |
| S30 | https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm ; a https://www.cs.tufts.edu/comp/150FP/archive/keith-cooper/dom14.pdf ; b https://en.wikipedia.org/wiki/Transitive_reduction ; c https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem ; d https://en.wikipedia.org/wiki/Treewidth |
| S31 | GitHub API licence and metadata records: `gh api repos/<owner>/<repo>` and `/license` for every repo named in section 3 (the "gh API" source) |
| S32 | https://github.com/45ck/proofmap-lite (private; README and docs/gap-audit.md read via `gh`); local quality/metrics lane files |
| M1-M5 | `graph/bench/foundations_checks.py`: M1 = C1 JCS vs kernel, M2 = C2 order sensitivity, M3 = C3 PageRank, M4 = C4 status lattice, M5 = C5 closure vs recursive CTE |
