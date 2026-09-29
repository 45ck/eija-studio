# Impact, ranking and evidence-confidence mathematics

Lane: weave. Aspect: impact-ranking-math. Date: 2026-09-29. Status: DESIGN for [ADR-0097](../../adr/0097-weave-impact-ranking-math.md). Nothing in `eijagraph` is built yet. Sibling aspects written in parallel were read on 2026-09-29 and this design is aligned to them (sections 2, 5.7, 10.3 and 13): the metamodel (`graph/schema/metamodel.json`, ADR-0089), the agent interface (`graph/schema/mcp-tools.md`, ADR-0099), the human views (`graph/schema/views.md`), consistency and sync (ADR-0093) and the formal reference (`graph/formal/eijaref`). What exists and runs today: a stdlib reference ([graph/bench/impact_math_reference.py](../../../graph/bench/impact_math_reference.py)), its oracle tests ([tests/graph/test_impact_math_oracles.py](../../../tests/graph/test_impact_math_oracles.py), 43 tests), worked examples with hand-verified answers ([graph/schema/math-oracles.md](../../../graph/schema/math-oracles.md), oracles O1 to O11), a co-change ranking measurement ([graph/bench/ranking_cochange_eval.py](../../../graph/bench/ranking_cochange_eval.py)) and a timing script ([graph/bench/impact_math_timing.py](../../../graph/bench/impact_math_timing.py)).

Labels: MEASUREMENT (a script ran, domain stated), PREDICTION (reasoned, not run), DESIGN (a proposal of this lane), UNVERIFIED (not opened or not confirmable; nothing is built on it), HAND (derived on paper in the oracle file, then confirmed by the reference), SEEDED (a test with fixed seeds over sampled inputs: evidence, not proof), EXHAUSTIVE (a test that enumerates the whole stated domain). Source keys: dossiers in `docs/weave/research/` as in SYNTHESIS ([math], [agent], [assure], [trace], [incr], [gdb]); sources I opened myself on 2026-09-29 are S1 to S24 in section 15.

## 0. Decisions first

| Id | Decision | Benefit (what it changes) | Mechanism | Cost and limit | Label |
|---|---|---|---|---|---|
| IR-1 | Impact is the least fixed point of `X -> C U succ(X)` over typed arcs, reported in three soundness tiers with a distance, a lexicographically smallest shortest-path witness, a budget and an honest frontier | A blast radius that is order-independent, terminates on cycles, and shows which part rests on heuristic edges | Kernel `impact.closure` generalised; SQL `WITH RECURSIVE ... UNION` as the store form; equality with the kernel tested on 300 seeded graphs, equality of the SQL form with the reference on the worked example and on 200 seeded typed graphs (networkx is not used for the closure) | Only as complete as the encoded arcs; flow is derived from the metamodel's `affects` and `anchor_ends` | HAND, SEEDED (equality with the kernel) |
| IR-2 | Impact (structural, over-approximate, for planning) and suspicion (digest-driven, for link status) are two different closures | Comment-only edits stop at the first hop for status, while planning still sees dependents | Impact runs from changed content hashes over base-union-head arcs; suspicion is `link_status`; the stale set is a subset of the impact set (by construction, tested) | The flow derivation must include the arc away from every anchored end; true by construction, checked by test | DESIGN |
| IR-3 | SCC condensation with minimum-member labels; reach and exposure counts by bitset DP on the condensation | Cycles reported deterministically; "if this changes, N things re-verify" for every node in one pass | Iterative Tarjan, Kahn with a min-heap, Python big-int bitsets | `O(E V / 64)` for all-node counts; nodes in one giant SCC are indistinguishable by reach | HAND, MEASUREMENT (library order dependence, from the dossier) |
| IR-4 | Relevance for `context(budget)` and for ordering inside a tier is personalised PageRank in **bit-exact fixed-point integers**, default `alpha = 1/5`, impact-direction weight 2 and reverse weight 1, no hub damping; advisory only | Fixes the measured float non-determinism (40 of 40 shuffles differ). On two Python repositories it beat hop distance at recall@10 with a paired 95% interval excluding 0, beat a path-prefix baseline on one and tied it on the other (section 5.6) | `2^40` integer mass, floor split with remainder to sorted targets, `K` from `alpha` by integer inequality, proven L1 error bound | Heuristic; PPR variants differ within noise and hub damping helped one repository and hurt the other; effect on agent success unmeasured | MEASUREMENT (offline proxy), PREDICTION (agent effect) |
| IR-5 | `context(budget)` = pinned seeds, then density greedy with a best-single-item safeguard, budget in **bytes**, with an explicit omitted list that also names candidates too large for the room | Bounded, replayable agent reads; every candidate not chosen is listed with a reason code | Knapsack greedy, at least half the optimum | Modular value: near-duplicate pages are not penalised | HAND, SEEDED |
| IR-6 | Test and evidence selection = a safe candidate pool from `covers` edges, then weighted greedy set cover of impacted obligations; uncoverable obligations become findings | Smallest fast-tier set over declared verifiers with a `H(d)` guarantee; the gap list is itself a diagnostic | Chvatal-style greedy on exact `Fraction` ratios | "Covers" is a declared or measured link, not fault detection; the fast tier is never a safety claim | HAND, SEEDED |
| IR-7 | Change risk is a vector of exact counts with a partial order and a canonical lexicographic review order. No scalar score; gates are boolean rules | Explains why a change is first in the queue; cannot be gamed by tuning weights; no fake calibration | Product order plus fixed field priority | Not a defect predictor; ordering among incomparable changes is a convention | DESIGN, HAND |
| IR-8 | Two status operators, never mixed: replication join `A` (several observations of one check) and conjunction `B` (distinct checks, chain minimum, `NOT_RUN` absorbs `PASS`); an empty conjunction is `NOT_RUN`, never `PASS` | Roll-ups compose; a missing tool cannot look green; the kernel's aggregation rule is not associative as a fold on statuses, so the roll-up algebra lives in `graph/` with tests (the kernel does not roll up today) | Lattice `UNKNOWN < STALE < {PASS, FAIL} < CONFLICT` and a verdict chain with `PASS` on top | Owner decides the order among non-`PASS` values; kernel change needs its own ADR | EXHAUSTIVE |
| IR-9 | **No confidence percentage anywhere in a gate or a default view.** Print counts, exhaustive-domain statements, generator-relative miss bounds (labelled conditional), mutation ratios with the fault model, and `pass^k` for agent trials | Removes pseudo-precision; the three "uninformative" priors give 0.857, 0.917 and 1.0 for the same data | Counts and exact rationals only | Less to show a manager; revisit trigger in section 11.6 | HAND |
| IR-10 | Evidence redundancy `k` (vertex-disjoint paths, capped) and the canonical minimum cut for single points of evidence, report only. Betweenness is not built | Names the one test, tool pin or person a claim rests on | Unit-capacity max flow with node splitting; source-side minimal cut | Needs the support graph to include `checked_by` arcs | HAND, SEEDED |
| IR-11 | Changeset overlap between two change sets (direct, reaches, shared, by tier) as pre-merge conflict prediction | Names the collisions between parallel agents before they land, with the arc class each rests on | Two closures and an intersection; symmetric | An early signal over encoded arcs, not a merge check | HAND, SEEDED |

Every function above is a pure function of the canonical graph, the recorded parameters and a change set. Nothing reads a clock, an environment variable, a random source or an unsorted container (rules D-01, D-04, D-07, D-10 of [ARCHITECTURE section 7](../ARCHITECTURE.md)).

## 1. Model and notation

A typed graph `G = (V, L)`: nodes `V` with content hashes, and links `L` of `(from, kind, to)` where `kind` is a link kind of the metamodel (metamodel version 1.0.0, read 2026-09-29: 42 node types, 29 link kinds). I write `src` for the `from` end and `dst` for the `to` end.

**This aspect adds no metamodel field.** It reads what the metamodel already declares per link kind: `soundness` (`must`, `may`, `heuristic`), `rank_weight` (a pair `(fwd, rev)`, section 5.3), `cover_role` (`none`, `observer`, `verifier`, section 7), `affects` (`to_source`: a change at the `to` end reaches the `from` end; `to_target`: the reverse; `both`; `none`) and `anchor_ends` (which endpoint digests the link stores). From these it derives the impact flow, a subset of `{F, R}`:

* `F` (arc `src -> dst`) if `affects` is `to_target` or `both`, or `from` is an anchored end;
* `R` (arc `dst -> src`) if `affects` is `to_source` or `both`, or `to` is an anchored end.

The anchored-end clause is the point: a changed anchored endpoint makes the link SUSPECT, so the other end needs re-checking, whatever `affects` says. With this rule the consistency lint of section 3 ("flow covers the anchored direction") holds by construction, and a test asserts it for every kind and fails loudly if the metamodel ever adds an `affects` value this aspect does not know. Derived flows for metamodel 1.0.0 (regenerate, do not hand-edit):

| Derived flow | Link kinds (soundness) |
|---|---|
| `FR` (both directions) | attests (must), conforms_to (may), derived_from (must), exercised_by (may), formalises (must), models (must), names (must), proves (must), realises (must), satisfies (must), verifies (must) |
| `R` only | calls (heuristic), checked_by (must), contains (must), covers (may), decides (must), depends_on (may), documents (must), refines (must), serves (must), styled_by (may) |
| `F` only | defeats (must), exposes (may), flows_to (must), motivates (must), proposes (heuristic), supports (must) |
| none | renamed_to (must), supersedes (must) |

`rank_weight` and `cover_role` are read from the metamodel, not hard-coded by kind name: `rank_weight_from_metamodel`, `cover_role_from_metamodel` and `relevance_weights` in the reference take them from the kind's spec, validate them (two non-negative integers, not both zero; one of the three roles) and raise on anything else. In metamodel 1.0.0 every kind declares `rank_weight = [2, 1]`, which is the ADR default, and only `verifies` (verifier) and `covers` (observer) have a `cover_role`; a test asserts both facts, so a metamodel change that moves a weight or a role fails loudly instead of silently disagreeing with a second copy. Inputs that are still policy, not metamodel: the test costs of section 7 (default table by test kind, per-node override if the metamodel aspect adds an optional `cost` attribute: open request) and the context cost (`render_bytes`, the okf page's byte length).

The impact digraph `I_c` has arc `src -> dst` for each link whose flow has `F` and whose soundness class is at most `c`, and arc `dst -> src` for each link whose flow has `R` and class at most `c`. `I_0 <= I_1 <= I_2` as arc sets. The kernel's `closure(graph, roots, budget)` already takes exactly this shape: "edges mean source affects target".

Change set `C` (the roots): nodes whose content hash under their registered hash method differs between base and head trees, nodes added or removed (a removal is a root in the base graph), nodes named by a rename record, and both endpoints of an added, removed or re-anchored link. Hash methods are the okf lane's and the metamodel's registry (`ast-v1`, `ast-sig-v1`, `ast-api-v1`, `lf-sha256-v1`, `json-key-v1`, ...); this aspect only consumes "changed or not".

### 1.1 Where graph technology sits in this aspect

The owner asked how Neo4j, OKF and similar tools are used. For the mathematics in this document:

| Tool or format | Role here | Not its role | Source |
|---|---|---|---|
| SQLite (stdlib) | Store form of the closure (`WITH RECURSIVE ... UNION`), of `arc`, and of ordered result sets; disposable index | A source of truth | oracle O1 SQL, tested at three tiers on the worked example and against the reference on 200 seeded typed graphs; timing in section 12 |
| Neo4j and Neo4j GDS | One-way export target for a person who wants to explore (Cypher, PageRank, shortest path) | Anything in a gate, any committed number, any dependency: GPL-3.0 server and library, float results, row order undefined without `ORDER BY` | [S3], SYNTHESIS section 1 |
| OKF v0.2 pages | The readable surface for what these functions return: `context` yields node ids that resolve to pages, and a page's byte length is the context cost; a generated `links` block can list an `impact` witness | Holder of typed links, hashes or rank scores (OKF links are untyped, broken links must be tolerated: SYNTHESIS section 1) | okf lane ADR-0045/0046 |
| Datalog engines (Soufflé) | Optional export of `.facts` for someone who wants to cross-check the closure with an independent engine | Default path; the closure is already the kernel's own fixed point | SYNTHESIS section 3 |
| networkx | Test oracle only (SCC partition, PageRank cross-check), skipped as NOT_RUN when absent | Producer of any artefact (library orders and floats are not deterministic) | tests |

## 2. Impact closure: a least fixed point with tiers

**Definition.** For a change set `C` and class `c`, `F_c(X) = C U succ_{I_c}(X)` on the powerset of `V` ordered by inclusion. `Impact(C, c) = lfp F_c`. The tier of a node is the least `c` with the node in `Impact(C, c)`; its distance is the BFS distance in `I_tier`; its witness is the lexicographically smallest shortest path from any root (sorted roots, sorted successors; the FIFO BFS realises this by induction on layers, and the test checks it against exhaustive path enumeration on 100 graphs).

**Why it is well defined (hypotheses stated).** Kleene's fixed-point theorem [S1]: on a directed-complete partial order with a least element, a Scott-continuous `f` has a least fixed point equal to the supremum of `bottom, f(bottom), f(f(bottom)), ...`. Here the order is the finite powerset lattice of `V`, `F_c` is monotone (more nodes give more successors), and every chain is finite, so `F_c` is continuous and the iteration stops after at most `|V|` rounds. This is my elementary reading of the theorem's hypotheses, not a quotation of the finite case. The three tiers nest: `Impact(C,0) <= Impact(C,1) <= Impact(C,2)`, because `F_c` is monotone in the arc set (SEEDED test).

**Algorithm.** BFS with a sorted queue, exactly the kernel loop plus parent and distance maps: `O(V_r + E_r)` over the reachable part, memory `O(V_r)`. The store form is the SQL in oracle O1, written against the store aspect's `edge` table (`storage-and-query.md` section 4.2, `soundness` stored as text on each edge) plus a small `flow` table generated from the metamodel; its `UNION` (not `UNION ALL`) removes repeated rows so cyclic graphs terminate; SQLite documents that recursive-select results need `ORDER BY` for a defined order [gdb]. Budget semantics are the kernel's: stop when `budget` nodes are visited; `frontier` is the discovered-but-unvisited set; `complete` is `frontier` empty. `budget = 0` gives `frontier = roots`. A negative budget is an error.

**Report shape (DESIGN; integers only).**

```json
{"schema": "eija.weave.impact.v1", "roots": ["repo://..."], "complete": true, "frontier": [],
 "params": {"max_tier": 2, "budget": null, "arc_set_sha256": "...", "flow_table_sha256": "..."},
 "partial_extraction": false, "counts": {"tier0": 1, "tier1": 4, "tier2": 3},
 "affected": [{"id": "repo://...", "tier": 1, "distance": 2, "score_ppm": 188679, "witness": ["...", "..."]}],
 "envelope": "Reach over encoded arcs only; not every real-world consequence."}
```

Sorted by `(tier, -score_ppm, distance, id)` (section 5.5). `partial_extraction` is true if any contributing extractor label is `partial`; a partial report can never be complete.

**Certificates and a second checker.** The `distance` and `parent` maps of a closure are exactly the `(rank, parent)` certificate that the formal aspect's small checker accepts (`graph/formal/eijaref/closure.py`: roots inside the set, every non-root has a parent arc from a lower rank inside the set, and the set is forward-closed; `check_unreachable` gives the negative witness). That checker has no queue and no iteration, so its acceptance independently confirms the positive and negative parts of a report. The oracle tests feed my closure output to it on 200 seeded graphs, compare with its naive Kleene iteration and its Warshall closure, and show that a forged parent is rejected.

**Failure modes.**

| Failure | Effect | Guard |
|---|---|---|
| A link kind has no flow (`affects` none and no anchored end) | No structural arc: a change never crosses it | Correct for `renamed_to` and `supersedes`; any other such kind is a metamodel review item; the derived-flow table above is the audit list |
| A wrong `affects` direction | Silent under-reach | Direction is declared by the metamodel and audited in the table above; anchored ends always add the arc away from the anchor, so every suspect link's far end is inside the impact set (tested as "stale set is a subset of impact set" on 600 seeded typed graphs with a negative control that finds counterexamples when the anchor clause is dropped) |
| Dynamic dispatch, reflection, generated code | Missing arcs | Soundness class `heuristic` for extracted `calls`; reach through them is tier 2 and labelled |
| Giant strongly connected component or a hub | Impact covers most of the graph | Report `counts` and `|affected| / |V|`; a report above an agreed saturation is labelled uninformative rather than sorted harder |
| Deleted or re-anchored links | Dependents dropped | Closure runs over the union of base and head arcs (oracle O1, "deleted link") |
| Partial extraction | Missing facts | `partial_extraction` flag; `complete` forced false |
| Budget exhausted | Truncated report | `frontier` lists what was not expanded; the caller may continue from it |

**What it does not prove.** It is the set of nodes reachable over the encoded arcs. It is not the set of nodes whose behaviour changes, and it says nothing about whether any change is correct. Datalog and provenance-semiring theory apply to this positive fragment only: the witness is one derivation (why-provenance), not a proof of absence [math]. "No test covers X" is negation and lives in a stratum above the closure.

## 3. Impact versus suspicion, and early cutoff

Two closures answer two questions and must not be merged.

| | Impact (section 2) | Suspicion (link aspect) |
|---|---|---|
| Question | What could be affected, so what should be re-checked, read or scheduled? | Which recorded links are no longer anchored to the content they were made against? |
| Input | Changed content hashes | Link digest versus current digest of the anchored endpoint |
| Propagation | Transitive over arcs of the tier | One hop: only links whose anchored endpoint's normalised digest changed; a node whose own digest did not change does not pass suspicion on (early cutoff) |
| Over- or under-approximation | Over-approximate on purpose | Exact for the anchored digest, silent about semantics |
| Failure it prevents | Missed dependent | Stale evidence that still reads as green |

Consistency rule: stale nodes are a subset of the impact set of the same change. The flow derivation in section 1 makes this true by construction; the test keeps it true if the derivation changes. Consequence for measurement: raw-byte anchors are suspect on 99.9 to 100% of file-touching commits, symbol AST on 7 to 9%, signature on 1.5 to 1.8% (MEASUREMENT on two Python repositories, [trace] section 4), so early cutoff is only worth its name when the anchor method is chosen per link kind; that choice belongs to the link aspect.

### 3.1 Changeset overlap: pre-merge conflict prediction

The product thesis names conflict prediction as a flagship: before anything lands, predict overlap between parallel changesets by file, symbol and abstraction, because two agents changing the same concept is a semantic conflict git cannot see ([thesis], `docs/weave/research/00-PRODUCT-THESIS.md`). The impact closure gives it almost for free. For change sets `A` and `B`: `direct` (both edit a node), `a_reaches_b` and `b_reaches_a` (a node one side edits that the other side's change reaches, with the tier of that reach), and `shared` (nodes both changes reach, at the tier of the weakest arc class either needs). Cost: two closures and a set intersection. Oracle O11 works two cases by hand.

What it is and is not. It is an early signal over encoded arcs, labelled by tier so a reader knows whether a predicted collision rests on sound arcs or on a heuristic edge. It is not a merge check: the consistency aspect's post-merge rule (findings of the merged tree minus the union of the two sides' findings, ADR-0093) finds what actually emerged, and the two are complementary. An empty overlap does not mean the changes are independent.

## 4. Condensation, topological order, reach and exposure

**Definition.** `label(v)` is the minimum member id of the strongly connected component of `v`. The condensation has one node per label and sorted, deduplicated arcs between labels. The topological order is the lexicographically smallest (Kahn with a min-heap). `reach(v) = |closure({v})|` and `exposure(v)` is the number of nodes whose closure contains `v`; both count `v`.

**Why.** Cycles are real in this graph (rule, journey, obligation loops). Library defaults are order-dependent: `nx.condensation` component numbering took 24 forms over 200 shuffled insertion orders, `graphlib` order 5, minimum-member labels and lexicographic topological order 1 (MEASUREMENT [math] C2, reproduced by the SYNTHESIS author). Tarjan is `O(V + E)` and emits components in reverse topological order [S2]. Reach and exposure answer "how far does a change to this node go" and "how many changes reach this node" for every node in one pass: bitset DP over the condensation, `mask(c) = members(c) | OR mask(succ(c))`, then `bit_count`.

**Complexity.** Tarjan `O(V + E)`; ordering `O((V + E) log V)`; all-node reach `O(E V / w)` word operations for word size `w` on the condensation (my bound; measured in section 12). Iterative Tarjan avoids Python's recursion limit.

**Failure modes.** A giant SCC makes reach counts equal for all its members (correct, and a signal). Memory for all-node masks is `O(C V / 8)` bytes; at `V = 10^5` that is up to 1.25 GB in the worst case, so all-node reach runs only up to about `10^4` nodes and otherwise per requested node (PREDICTION for the bound, the `10^4` figure is the measured range in section 12).

**What it does not prove.** Reach counts are structural. A node with `reach = 1` is not "safe"; it may just have no encoded dependents.

**Betweenness and other centralities are not built.** They change no decision that reach, exposure and the vertex cut in section 8 do not already change, Brandes-style exact betweenness costs `O(V E)` (complexity unverified, paper not opened [math]) and the sampled variant is non-deterministic unless seeded [math].

## 5. Relevance ranking: integer personalised PageRank

### 5.1 What it is for, and what it is not

Two uses, both advisory: (a) `context(seeds, budget)`, choosing what an agent or a person reads about a change; (b) ordering nodes inside a soundness tier of an impact report. It is never evidence, never a gate, and never a substitute for the closure. The closure says what is reachable and why; the ranking says what is probably worth looking at first.

### 5.2 Options

| Option | Determinism | Explains itself | Evidence read this session | Verdict |
|---|---|---|---|---|
| Hop distance (k-hop ego graph, as in RepoGraph) | exact, integer | yes (a path) | RepoGraph reports +2.0 to +2.66 pp on SWE-bench Lite for four agent frameworks, Python, GPT-4-series only ([agent], not re-opened by me) | keep as the distance field and as a measured baseline |
| Personalised PageRank, floats (networkx, scipy, Neo4j GDS) | float results differ bitwise across insertion orders: 40 of 40 shuffles (MEASUREMENT [math] C3, reproduced); networkx warns of no convergence guarantee [math]; GDS defaults `maxIterations 20`, `tolerance 1e-7`, `dampingFactor 0.85`, stops when scores change less than the tolerance [S3] | weak | Aider ranks a file graph this way [agent] | reject as an artefact producer. Neo4j itself stays an optional one-way export: a person may run GDS PageRank on the exported CSV to explore, and nothing computed there is committed or used by a gate (the GDS repository's LICENSE.txt head says GNU GPL version 3, so it is never linked into this Apache-2.0 package) |
| Personalised PageRank, integer fixed point (this design) | bit-exact, platform independent (section 5.3) | the path witness plus the score | this session: offline co-change study (section 5.6) | **adopt** |
| Forward-push approximate PPR (Andersen, Chung, Lang) | order-dependent unless the queue order is fixed | weak | not opened (fetch failed): UNVERIFIED | revisit only above about `10^6` arcs |
| Weighted shortest path, Katz, heat kernel | possible | partly | not evaluated | not built |

### 5.3 Definition and the integer algorithm

Relevance digraph `H` over the same nodes. For a link `(u, t, v)` the impact arc(s) of its type (section 1) get weight `fwd_t`, and the reversed arc of each impact arc gets weight `rev_t` (context flows back to what the changed node was built from); a link whose flow is `FR` has both directions as impact arcs, so each keeps `fwd_t`. The weight of `x -> y` in `H` is the sum over all links joining `x` and `y` of the applicable value; the default is `(fwd, rev) = (2, 1)`, chosen by the rule in 5.6. An optional hub-damped variant (off by default) multiplies the weight of every arc **into** node `y` by `65536 // (1 + deg(y))`, where `deg` counts distinct neighbours (integer division, no logarithm, no float). Seeds carry positive integer weights.

Let `alpha = a/b` be the teleport probability, `beta = 1 - alpha`, `s` the normalised seed distribution, `P(u,v) = w(u,v)/W_u` with `W_u` the weight sum of the out-arcs of `u`. A node with `W_u = 0` (dangling) returns to `s`. The target is `pi = alpha s + beta pi P` (row vector). For `0 < alpha < 1` the solution exists and is unique because `beta P` has spectral radius at most `beta < 1` (elementary; PageRank with damping and dangling handling is standard [S4]).

**Algorithm (bit-exact).** State `x` is an integer vector of total mass `SCALE = 2^40`. Start `x_0 = split(SCALE, seeds)`. Each iteration, for nodes in sorted id order with `x_u > 0`: `cont_u = floor(x_u (b - a) / b)`; send `cont_u` along the out-arcs by `split`; the remainder `x_u - cont_u` (and all of `cont_u` for a dangling node) goes to the seeds by `split`. `split(m, targets)` gives each target `floor(m w_i / W)` and hands the leftover units one each to the first targets in sorted id order. Every operation is exact integer arithmetic, so total mass is exactly `SCALE` after every iteration, and the result does not depend on hash seed, insertion order, platform or thread count. `K` is the least integer with `2^(bits+1) (b - a)^K <= b^K` (decided in integers; `alpha = 1/5, bits = 24` gives `K = 78`; `bits = 20` gives `K = 66`, HAND in O3).

**Error bound (derived here; checked against exact rational solutions on 40 seeded graphs).** Write `F(x) = beta xP~ + alpha (sum x) s`, where `P~` is `P` with dangling rows replaced by `s` (row-stochastic). For vectors of equal total mass, `F(x) - F(y) = beta (x - y) P~`, and `|| z P~ ||_1 <= || z ||_1` for row-stochastic `P~`, so `F` is a `beta`-contraction in `L1`. Each iteration's rounding perturbs the exact `F(x)` by at most `eps = arcs + 2 nodes + seeds` units in `L1` (each floor loses less than one unit; the `cont`/remainder pair contributes two per node). Because every iterate has mass exactly `SCALE` and so does `pi* = SCALE pi`, `|| x_{t+1} - pi* || <= beta || x_t - pi* || + eps`, hence

`|| x_K - pi* ||_1 <= 2 SCALE beta^K + eps / alpha` (units of `1/SCALE`).

Every coordinate is within that bound, so two nodes whose scores differ by more than twice the bound are ordered as the exact `pi` orders them. The printed `err_bound_units` accompanies every result. For the 3-node oracle the bound is 60764 units (0.055 ppm) and the observed error is below one unit.

**Output.** Scores as parts per million, rounded with integer arithmetic; ranking key `(-score, id)`. No float reaches an artefact (rule D-10).

**Complexity.** `O(K (arcs + nodes))` big-int operations on 41-bit values; memory `O(V + E)`. `K` depends only on `alpha` and `bits`, not on the graph.

### 5.4 Hypotheses and failure modes

| Failure | Effect | Guard |
|---|---|---|
| Hubs (a base type, a utility module) attract rank for every seed | Every context is the same few files | Optional hub damping, off by default because it helped `doorstop` (recall@10 0.530 against 0.468 undamped) and hurt `strictdoc` (0.380 against 0.426) on the test halves; report the top-degree nodes so a person can see the effect |
| Weights and `alpha` are heuristics | A misleading order | One global default pair, advisory label, per-type overrides only with a measurement; the report prints `alpha`, weights and `err_bound_units` |
| Seeds far from everything else | Mass returns to the seed, the ranking is the seed's neighbourhood | Correct behaviour; the context report still lists omitted candidates |
| Graph built from partial extraction | Missing arcs, wrong scores | `partial_extraction` propagates to the ranking report |
| A very long weighted arc list | `K` times arcs big-int operations is slow in Python | Section 12 timings; a native implementation is allowed if it reproduces oracle O3 byte for byte |

### 5.5 Blast-radius ordering

The set is the closure; the order is a reading aid: `(tier, -score_ppm, distance, id)`. Tier first because it separates what stands on sound arcs from what stands on heuristics; score inside a tier because PPR ordered co-changed files better than hop distance in the offline study (section 5.6, a proxy); distance and id make the order total and deterministic. The score is computed with the change set as seeds (weights equal).

### 5.6 MEASUREMENT: does structure predict which files change together?

Setup ([graph/bench/ranking_cochange_eval.py](../../../graph/bench/ranking_cochange_eval.py), results in [graph/bench/results/](../../../graph/bench/results/)). Static import graph of a Python repository at a pinned HEAD; every commit (no merges, newest first) with 2 to 25 changed `.py` files that exist at HEAD; up to 3 seed files per commit chosen by a hash of commit and path; target = the other files changed in the same commit; all other files are candidates. Rankers: `random` (hash order), `dir_proximity` (longest shared path prefix, needs no graph), `bfs_undirected` (hop distance), `impact_closure` (dependents first by hop distance, then undirected), and eight PPR configurations from the integer implementation. Metrics: mean recall@5, @10, @20 and reciprocal rank of the first target, averaged over seeds within a commit, then over commits, with a seeded bootstrap of 1000 resamples for 95% intervals. Parameters were chosen on the older half of the commits (by recall@10) and scored on the newer half.

Repositories: `doorstop` (pinned HEAD `789792ebef4f`, 94 modules, 370 import arcs, 192 usable commits, 479 seed-target pairs) and `strictdoc` (pinned HEAD `abf7be7daa2a`, package only, 299 modules, 1537 import arcs, 157 usable commits, 314 pairs). Test half = the newer half of the commits (96 and 78). Expected recall@10 of a random order is 0.107 and 0.034.

Test-half results (mean over commits; bootstrap intervals are in the JSON files). Every number was reproduced exactly by a second run of the same script, which is the determinism check for the harness itself:

| Ranker | doorstop r@5 | r@10 | r@20 | MRR | strictdoc r@5 | r@10 | r@20 | MRR |
|---|---|---|---|---|---|---|---|---|
| random (hash order) | 0.040 | 0.080 | 0.161 | 0.095 | 0.009 | 0.017 | 0.053 | 0.031 |
| path prefix (no graph) | 0.283 | 0.446 | 0.602 | 0.238 | 0.141 | 0.214 | 0.280 | 0.138 |
| hop distance (undirected) | 0.262 | 0.408 | 0.568 | 0.184 | 0.221 | 0.321 | 0.413 | 0.220 |
| dependents first, then hop distance | 0.291 | 0.413 | 0.586 | 0.254 | 0.212 | 0.332 | 0.391 | 0.266 |
| PPR alpha 1/10, weights 1:1 | 0.105 | 0.353 | 0.642 | 0.175 | 0.273 | 0.364 | 0.562 | 0.320 |
| PPR alpha 1/5, weights 1:1 | 0.129 | 0.468 | 0.693 | 0.183 | 0.291 | 0.426 | 0.563 | 0.317 |
| PPR alpha 1/3, weights 1:1 | 0.162 | 0.504 | 0.707 | 0.190 | 0.294 | 0.429 | 0.577 | 0.311 |
| PPR alpha 1/2, weights 1:1 | 0.180 | 0.517 | 0.745 | 0.198 | 0.298 | 0.433 | 0.574 | 0.290 |
| PPR alpha 3/20, weights 1:1, run to convergence | 0.114 | 0.419 | 0.675 | 0.182 | 0.283 | 0.406 | 0.556 | 0.320 |
| PPR alpha 3/20, weights 1:1, T = 30 (agent-interface spec) | 0.114 | 0.419 | 0.675 | 0.182 | 0.283 | 0.406 | 0.556 | 0.320 |
| **PPR alpha 1/5, impact:reverse 2:1 (default)** | 0.210 | 0.454 | 0.703 | 0.223 | 0.305 | 0.461 | 0.579 | 0.395 |
| PPR alpha 1/5, 1:1, hub damped | 0.364 | 0.530 | 0.696 | 0.310 | 0.184 | 0.380 | 0.483 | 0.259 |

Paired difference of the default configuration against two baselines, test half, mean and 95% bootstrap interval over commits:

| Default PPR minus baseline (test half) | doorstop recall@10 | doorstop MRR | strictdoc recall@10 | strictdoc MRR |
|---|---|---|---|---|
| hop distance | +0.046 [+0.004, +0.091] | +0.039 [+0.011, +0.071] | +0.141 [+0.060, +0.216] | +0.175 [+0.106, +0.248] |
| path prefix | +0.008 [-0.097, +0.108] | -0.014 [-0.058, +0.033] | +0.247 [+0.138, +0.350] | +0.257 [+0.168, +0.351] |

How the default was picked. Choosing per repository on the older half gave different winners (`ppr_a1/5_hubdamped` for `doorstop`, `ppr_a1/5_impact2x` for `strictdoc`), which is itself a finding: no variant dominates. I therefore fixed one pooled rule, "highest mean recall@10 over both older halves", which selects alpha 1/5 with 2:1 weights (0.460 pooled on the older halves; symmetric alpha 1/3 was 0.443). I stated the rule after seeing the older-half numbers of both repositories, so its result on the test halves is not an independent confirmation, and the test-half means of the top variants (0.447 to 0.475 pooled) are within noise of one another.

Reading, with the limits that apply:
- Co-change is a proxy. A bulk edit co-changes unrelated files; a truly impacted file may be untouched. Bulk commits above 25 files were dropped.
- The graph is built at HEAD and the commits are older; files renamed or deleted since are absent.
- Static imports only, one language, two repositories, and eight PPR configurations were compared, so any winner's margin is optimistic even with the split. The halves are not independent (same files, same authors).
- What the data supports: every PPR variant except `alpha = 1/10` had a higher mean recall@10 than hop distance on both repositories (intervals in the JSON files); the default's paired interval against hop distance excludes 0 on both; against the path-prefix baseline it is indistinguishable on `doorstop` (+0.008, interval spans 0) and clearly better on `strictdoc`. What it does not support: a claim that PPR is the best relevance measure, or that the default parameters are optimal.
- Nothing here measures agent success or human comprehension. That remains UNMEASURED (section 14).

### 5.7 Reconciliation with the agent-interface aspect's ranking

The agent-interface aspect ([agent-interface-and-context-packs.md](agent-interface-and-context-packs.md) sections 5.3 and 5.4, ADR-0099) specified, independently, a fixed-point integer personalised PageRank and the same knapsack selection. The two families coincide; the details differ, and one implementation should serve both.

| | IR-4 (this design) | Agent-interface section 5.3 |
|---|---|---|
| Graph | Directed relevance digraph: impact arcs weigh `fwd`, their reversals `rev`, from the metamodel's `affects` and anchors | Undirected weighted graph; weight `base(kind) * m(soundness)` with `m = 2` for must and may, 1 for heuristic, 0 for `proposes` |
| Continue probability | 0.8 (`alpha = 1/5`) | 0.85 (`alpha = 3/20`) |
| Iterations | `K` from `alpha` and `bits` by an integer inequality (66 or 78) | `T = 30` fixed; "no convergence claim" (`0.85^30 = 0.0076`) |
| Mass | Conserved exactly; dangling nodes return to the seeds | Floors lose mass (bounded by them); isolated nodes not addressed |
| Error | L1 bound printed with every result (section 5.3) | Arithmetic bound on lost mass only |
| Scale and output | `2^40`; parts per million of total mass | `10^12`; permille normalised by the maximum |
| Weights | Uniform `(2, 1)`; per-kind weights only with a measurement | Per-kind base weights 4/3/2/1 (their DESIGN, no ablation) |
| Knapsack | Density greedy plus best single item, at least half the optimum | The same algorithm, with its own proof by fractional relaxation, plus a heuristic level-upgrade step |

Measured with the same harness (section 5.6), their parameters (`alpha = 3/20`, `T = 30`, uniform undirected weights, which is their spec on an import graph where every edge has one kind) reach pooled test recall@10 of 0.413. That is above hop distance (0.364) and below the IR-4 default (0.458). Running the same `alpha = 3/20` to convergence gives the identical numbers on both repositories (recall@10 0.419 and 0.406, MRR 0.182 and 0.320), so stopping at `T = 30` costs nothing measurable here; the whole gap to the default is `alpha` and the weights (`alpha = 1/5` with uniform weights gives 0.447 pooled, the 2:1 weights add 0.011; not separated further, and the differences are within the noise stated above). The per-kind base weights cannot be tested on an import graph and remain unmeasured; their own offline plan (`pack_recall@B`, their section 5.8) is the right place to test them.

Recommendation (for the integrator; nothing in the other aspect's files was changed): one shared module, `eijagraph.rank.ppr_int`, with the pack policy carrying `alpha`, the iteration count (from the integer inequality, not a constant), the weights digest and `err_bound_units`; their slot logic, mandatory set and level upgrades stay theirs; their per-kind base weights become an optional weights policy adopted only if `pack_recall@B` shows a gain over uniform weights. The knapsack is one function (`eijagraph.select.knapsack`), tested by both.

## 6. Context selection under a budget

**Definition.** Inputs: a mandatory set `M` supplied by the caller, whose members are pinned with integer costs (for the agent interface `context_pack`, the seed, statement, verifier, term, finding and suspect slots of its section 5.2; for a plain query, the seeds); candidates with integer `(score_ppm, cost)`; a budget in **bytes** of rendered page text (the okf lane's page bytes, a deterministic quantity; provider token counts are not, and differ between models). If the pinned cost alone exceeds the budget the result is `BUDGET_TOO_SMALL` with the needed amount and nothing is truncated (the agent interface uses the same rule and error code). Otherwise take candidates by score per cost (cross-multiplied integers, ties by id), skipping any that do not fit; compare the value of that set with the single best candidate that fits and keep the larger. Report `chosen`, `cost`, `value` and `omitted`. `omitted` lists every candidate that was not chosen, each with a reason in `omitted_reasons`: `NOT_SELECTED_BUDGET` (it fit the room and lost, listed in density order), `TOO_LARGE_FOR_ROOM` (its cost exceeds the room left after the pinned nodes, so a larger budget would bring it in; it can be the most relevant candidate, and it is reported, not dropped), `NON_POSITIVE_SCORE`, `NON_POSITIVE_COST`. Chosen and omitted partition the candidates (SEEDED, 200 instances; oracle O4d). Excluding a too-large candidate from the selection does not change the half-optimum guarantee, because no feasible set contains it.

**Guarantee (hypotheses: additive values, every candidate cost at most the room).** The result is at least half the optimum. The classic argument takes the better of the greedy prefix and the first excluded item [S5]; my variant skips items that do not fit and adds the best single item, which is at least as good on both branches. Tested against exhaustive optimum on 200 seeded instances.

**Complexity.** Sorting `n` candidates is `O(n log n)` with exact integer cross-multiplication; the scan is `O(n)`; the best-single-item check is `O(n)`. Independent of graph size once the scores exist.

**Failure modes.** Modular value ignores redundancy (two near-identical pages both score high); a diversity term would make it submodular and is deferred. A wrong cost (stale byte count) mis-budgets; the cost is read from the same page digest the okf lane hashes, so a stale cost is a stale hash. Always-loaded context is the wrong default: a study (arXiv 2602.11988; the authors' affiliation was not verified) reports repository-level context files did not generally improve success and raised cost by over 20% ([agent], not re-opened by me), so `context` is an on-demand query, never a preamble.

**What it does not prove.** That the chosen pages are sufficient or that they help an agent (UNMEASURED).

## 7. Test and evidence selection

### 7.1 Two problems, kept apart

1. **Safe pool** `T_safe`: every test that could observe the change. `T_safe = { t : covers(t) meets Impact(C, c) }` where `covers` edges are derived from coverage data. Rothermel and Harrold proved a control-flow-graph technique "safe" (selects all tests capable of exposing faults) under stated conditions [S6]; here safety holds only modulo the completeness of the `covers` facts, and the report says so. Source of `covers` facts: coverage.py dynamic contexts, `dynamic_context = test_function` records which test ran each line in a SQLite data file [S7]; lines map to symbols by `ast` ranges. The metrics lane already runs coverage.py (ADR-0037). Without coverage data `T_safe` is `NOT_RUN`, never "all tests pass".
2. **Fast-tier subset**: the cheapest subset of the pool that gives every impacted obligation an observing verifier. This is weighted set cover.

### 7.2 Weighted set cover

**Definition.** Universe `U` = obligations (requirement, invariant, workflow element, claim) in `Impact(C, 1)` that need executable evidence. Sets: for each `t` in the pool, `S_t = { o in U : verifies(t, o) declared }`, cost `c_t` an integer (declared per test kind, default table unit 1, property 4, integration 16, browser 64, formal 64: PREDICTION defaults; a recorded-runtime file can replace them as an explicit input, never a clock read at gate time). Greedy: repeatedly take the set with the least `c_t / |S_t ∩ uncovered|` (exact `Fraction`), ties by more newly covered, then id. Elements in no set are returned as `unreachable`. Hypotheses: finite universe, positive integer costs, sets given explicitly, each set's elements from the universe.

**Complexity.** The reference loop is `O(iterations x |pool| x |S|)` (1.0 s at 2 000 elements and 1 000 sets, section 12); a lazy-evaluation greedy with a priority queue is `O(total set size x log |pool|)` (standard; DESIGN, to be tested equal to the reference including ties).

**Guarantee.** The greedy heuristic for set cover is an `H(d)` approximation with `d` the size of the largest set (Chvatal 1979 [S8]; the unweighted statement and the cost-per-new-element weighted generalisation are on [S9]); no polynomial algorithm does better than `(1 - o(1)) ln n`: Feige (1998) under the assumption that NP has no quasi-polynomial-time algorithms, and Dinur and Steurer (2013) unless P = NP (statement and both hypotheses as worded on [S9], opened 2026-09-29; the papers were not read, and the Dinur-Steurer abstract [S10] says only that it gives stronger inapproximability for Set-Cover). The tight family ratio grows like `log2(n)/2` [S9]. Oracle O5a shows greedy 3 against optimum 2 (`H(8) = 2.72`). Tested SEEDED: `opt <= greedy <= H(d) opt` on 300 small instances by exhaustive optimum. Exact optimisation (ILP) is deferred until the greedy gap matters; OR-tools is Apache-2.0 (SPDX [S11]) and would be an optional process.

**Diagnostics it produces.** `unreachable` obligations are findings ("impacted obligation with no test that observes the change"), the sharpest signal this section offers. `pool` empty for an impacted obligation means either no verifier or none that touches the change.

**Failure modes and honest limits.** (i) "Covers" is coverage, not fault detection: 100% line coverage with no assertion covers everything and detects nothing. Calibration: mutation score per `covers` or `verifies` edge (mutation lane, `fault_detection` attribute). Just et al. found a statistically significant correlation between mutant detection and real fault detection independent of code coverage on 357 real faults in 5 open-source applications, and "some inherent limitations" [S12]; that supports mutation ratios as a relative indicator and does not turn them into a probability. (ii) The fast tier is unsafe by design; the full tier runs `T_safe`, the release tier runs everything. (iii) Flaky tests corrupt cost and coverage; flake handling is the property and hygiene lanes'. (iv) Test-selection tools exist: pytest-testmon (MIT, last push 2025-12-01; README: it "automatically selects and re-executes only tests affected by recent changes" and saves its dependency database to `.testmondata`; testmon.org says it "collects dependencies between tests and all executed code (internally using Coverage.py)" and compares them against changes, tracks environment variables, the Python version and third-party package versions, and does not track static files; the blog post that details the comparison was not read, so the selection rule itself stays UNVERIFIED) [S13], and Ekstazi and static RTS studies (Gligoric et al. ISSTA 2015, Legunsen et al. FSE 2016; bibliographic records only, results not read: UNVERIFIED) [S14, S15]. Phase 4 compares them with this selector on the same change sets; until then no claim about selection quality or time saved is made (UNMEASURED).

**What it does not prove.** That the selected tests would catch a defect, or that the unselected ones would not.

## 8. Evidence redundancy and single points of evidence

**Definition.** Build the support graph from a claim to its evidence: arcs from the claim to each `PASS`-lifted link's evidence node, and from evidence to the `tool` node named by `checked_by`, and from tools to a super-sink `E*` joined from every leaf. `k` = the maximum number of internally vertex-disjoint paths from the claim to `E*`, capped at 3. By Menger's theorem `k` equals the minimum vertex cut for non-adjacent endpoints, also for directed graphs [S16]. Compute by augmenting paths with unit vertex capacities (node splitting), each augmentation a BFS over sorted neighbours: `O(k (V + E))`.

**Canonical cut.** Minimum cuts are not unique (a chain `R, u, v, E` has cuts `{u}` and `{v}`). Report the source-side minimal one: internal vertices whose in-copy is reachable from the claim in the residual graph of a maximum flow but whose out-copy is not. That residual set is a standard construction in the max-flow min-cut proof [S17]; that it does not depend on which maximum flow was found is Picard and Queyranne's result on the lattice of minimum cuts, which I did not open (UNVERIFIED as a citation); the test checks canonicity by brute force on seeded graphs (source side contained in that of every other minimum cut).

**Use.** `k = 1` names the one test, tool pin or person a claim rests on; two tests run by one pinned tool share that tool as a cut vertex (oracle O6, first row). Report only; no gate. A separate dominator algorithm is not needed: on `R -> E*` paths a vertex on every path is exactly a cut of size 1.

**Failure modes.** Missing `checked_by` arcs hide common causes; the direct arc `R -> E*` makes `k` unbounded (reported as none); the count is structural and says nothing about the independence of the evidence in fact.

## 9. Change-risk: a vector, not a score

**Definition.** Eight exact integers, in review-priority order: `protected_paths_touched`, `pinned_statements_changed`, `impacted_obligations_without_observer` (size of `unreachable` in section 7), `suspect_links`, `tier0_size`, `tier1_size`, `tier2_size` (per-tier increments), `changed_nodes`. The order `a >= b` is componentwise; `a` dominates `b` if it is at least `b` everywhere and larger somewhere. The review queue sorts by the field tuple lexicographically, larger first, which never puts a dominated change above its dominator (2000 seeded pairs). Two changes can be incomparable, and the design says so instead of inventing a total order (oracle O9).

**Complexity.** `O(|C| + |Impact| + |cover|)` once the closure and the cover exist; the vector and its comparison are `O(fields)`.

**Gates are rules, not thresholds.** `protected_paths_touched > 0` and `pinned_statements_changed > 0` require an owner decision under the trust model (ARCHITECTURE section 6: agents never write the ledger or protected policy paths; a file-diff gate enforces it); nothing else gates on a number.

**Why no weighted score.** (1) No ground truth: this repository has 7 commits (`git rev-list --count HEAD`, MEASUREMENT 2026-09-29), so any weight would be invented. (2) Literature models exist that predict defect density from relative code churn (Nagappan and Ball, ICSE 2005; bibliographic record only, results not read [S18]) but they need historical defect data to fit and are validated per project. (3) A scalar becomes an optimisation target for an agent that proposes changes; a vector with named fields keeps the reason visible. (2) and (3) are PREDICTION.

**What it does not prove.** Nothing about defect probability.

## 10. The status algebra

### 10.1 Two operators

| | A: replication join | B: conjunction |
|---|---|---|
| Folds | Several observations of **one** check on one subject (the kernel's receipts) | **Distinct** checks or links or child claims |
| Carrier | `UNKNOWN, STALE, PASS, FAIL, CONFLICT` (the kernel's five) | adds `NOT_RUN` |
| Order | `UNKNOWN < STALE < PASS < CONFLICT`, `STALE < FAIL < CONFLICT`; `PASS` and `FAIL` incomparable | total chain, default `FAIL < CONFLICT < STALE < NOT_RUN < UNKNOWN < PASS` |
| Operation | least upper bound | chain minimum |
| Identity | `UNKNOWN` (so the empty fold is `UNKNOWN`, as in the kernel) | `PASS` (the empty fold would be `PASS`, so it is returned as `NOT_RUN` instead) |
| Absorbing | `CONFLICT` | `FAIL` |
| Laws | commutative, associative, idempotent (EXHAUSTIVE, 125 triples) | same over every admissible chain (EXHAUSTIVE, 120 chains, 216 triples each) |

A join-semilattice is exactly an associative, commutative, idempotent operation, equivalently a poset with least upper bounds [S19]. The shape of `A` matches the four values `Neither, True, False, Both` of Belnap's four-valued logic with `STALE` inserted between `Neither` and the pair; the Wikipedia page I opened states the four values and the logical lattice but I could not confirm its information-order wording, so the resemblance is UNVERIFIED as a citation. Nothing depends on it: the laws are proved by enumeration.

`NOT_RUN` is not a receipt status. It is introduced by the claim assessment when a required prerequisite is missing (the checker registry knows whether a pinned tool is present), and it lives only in `B`; `fold_a` refuses it. With the prerequisite present and no receipt, the slot is `UNKNOWN`, which is what the kernel's `aggregate_status([])` returns.

**Complexity.** Linear in the number of statuses folded; the tables are 5 x 5 and 6 x 6 constants. Laws are checked by enumeration (125 and 216 triples, 120 chains), which closes the claim for every length because a commutative, associative, idempotent operation folds to a function of the set of its arguments.

### 10.2 Rules

1. Fold receipts with `A` inside a slot, fold slots and child claims with `B`. Roll-up through a claim hierarchy uses only `B`, which is associative, so a rolled-up result equals the flat one. The kernel's `aggregate_status` is `A` on flat inputs (equal on all 5460 sequences of length 1 to 6 over four statuses, with `assess_receipt` patched to return a given status) but its rule is not associative when its own output is fed back in: flat `agg([PASS, FAIL, FAIL])` is `CONFLICT`, rolled up `agg([agg([PASS, FAIL]), FAIL])` is `FAIL`, because the rule ignores `CONFLICT` as an input (MEASUREMENT under the same patch, reproduced; oracle O7). This is a hazard for reuse, not a defect that fires today: the kernel has one caller (`application/compiler.py`, line 25), which folds a flat receipt list and never feeds an aggregate back, and the unpatched `assess_receipt` cannot return `CONFLICT`. The graph roll-up will do exactly that (claims contain claims), so the case for a kernel change is prevention. This lane implements and tests the algebra; the kernel change is a separate ADR and PR (ARCHITECTURE section 11 reserves an index of kernel change requests; the integrator assigns the number).
2. A claim names its required slots. The empty conjunction would be `PASS` (the top of the chain), so a claim with no required slots would be vacuously green; `fold_b([])` therefore returns `NOT_RUN`: a gate that requires nothing has proved nothing. The formal aspect's reference returns the same.
3. `PASS` must be the top of the chain. That is the only property any verdict depends on: for all 120 orderings of the five non-`PASS` values below `PASS`, a fold is `PASS` if and only if every slot is `PASS` (EXHAUSTIVE). The order among non-`PASS` values only decides which non-`PASS` word is printed. That is SYNTHESIS open question 1 and stays an owner decision.
4. Link status lifts by the fixed map COVERED to `PASS`, SUSPECT to `STALE`, ORPHANED to `FAIL`, AMBIGUOUS to `CONFLICT`, UNRESOLVED to `NOT_RUN`; UNWANTED is a defect on the covering side.
5. `any_of` slots (alternative independent checks) would need the dual operator (chain maximum). It is not specified, default is `all_of`; an owner decision if ever needed.
6. A receipt made for an older subject is `STALE` whatever it said, and `A` lets a current `PASS` or `FAIL` outrank it (`STALE` below both). That is the kernel's behaviour and is kept: an old red result stops counting the moment the subject digest changes, which is the intent of digest freshness, and the same rule stops an old green result from counting.

### 10.3 Reconciliation with the formal aspect's `eijaref.status`

The formal aspect wrote its own reference (`graph/formal/eijaref/status.py`, "proposal of ADR-0101"). It was read and compared by test on 2026-09-29. Everything that decides a verdict is identical: the same two operators, the same default chain, the same `LIFT` map, `join` equal to this design's `A` on the kernel's five values, `PASS` iff all `PASS` for all 120 chains, and the empty meet is `NOT_RUN`. Two representational choices differ, and both are tested as documented deviations so a drift in either file fails a test:

| | This design | `eijaref.status` | Effect |
|---|---|---|---|
| Where `NOT_RUN` sits in the join | Outside it; `fold_a` refuses it | Bottom, below `UNKNOWN`: the join carrier has six values | A join fed a `NOT_RUN` receipt: mine errors, theirs ignores it |
| Empty join | `UNKNOWN` | `NOT_RUN` | The kernel's `aggregate_status([])` is `UNKNOWN`, so mine equals the kernel on every flat input including the empty list (MEASUREMENT, patched kernel); theirs differs on `[]` only |

Recommendation (an integrator or owner decision; either choice is a constants change): keep the kernel-exact join, so one word, `UNKNOWN`, means "the check could run and produced nothing decidable" in the kernel and in the graph, and reserve `NOT_RUN` for "a prerequisite was absent", which the checker registry can decide. The other choice is simpler to implement (one six-valued carrier) at the price of two words for the empty case. Presentation is a third matter: the human views use a display order (`CONFLICT, FAIL, STALE, UNKNOWN, NOT_RUN, PASS`) to sort badges; it is not the algebra's chain and changes no verdict.

**What it does not prove.** The algebra combines verdicts; it does not make any individual verdict true.

## 11. Confidence: what is computed and what deliberately is not

### 11.1 Decision

No number named confidence, probability of correctness, risk score or trust score appears in a gate, a default view, an agent tool result or an OKF page. Reasons are the hypotheses of the available methods (11.2) and three demonstrations (11.4). What we print instead is in 11.3.

### 11.2 Methods considered

| Method | Hypotheses as read | Why they fail here | Verdict |
|---|---|---|---|
| Rule of three | `n` independent Bernoulli trials, zero events; then `[0, 3/n]` is a 95% interval for the rate [S20] | Test inputs are not drawn from the operational profile; agent-written generators share the agent's blind spots | show only as a labelled, generator-relative statement (11.3 c) |
| Conservative Bayesian inference (Zhao, Salako, Strigini, Robu, Flynn) | The abstract: new theorems extending CBI let prior knowledge be used "without inducing dangerously optimistic biases", worked for operational testing of autonomous vehicles [S21]. The theorems' hypotheses beyond the abstract were not read: UNVERIFIED | Not evaluated: the theorem hypotheses were not read. From the abstract it works from operational-testing evidence and a prior, which EIJA does not have | not implemented; revisit trigger 11.6 |
| Subjective logic | Opinion `(b, d, u, a)` with `b + d + u = 1`, `P = b + a u`; observations `(r, s)` map through Beta parameters `alpha = r + a W`, `beta = s + (1 - a) W`, `W = 2`; cumulative fusion assumes independent sources [S22] | Base rate `a` is an input; independence fails for evidence from one agent and one tool; the number inherits both | store the counts `(r, s)` only; no opinions |
| Assurance 2.0 probabilistic valuation (Bloomfield and Rushby) | Probabilities apply only to sound cases; inputs are subjective ([assure], the authors' paper was opened by its dossier author) | Subjective leaves | not computed; the structural rules are linted by the assurance aspect |
| Frechet bounds | `P(A1 and ... and An) >= max(0, sum P(Ai) - (n - 1))`, no independence assumed [S23] | Leaf probabilities are unmeasured; the bound collapses | teaching example only |
| Bayesian updating with a named prior | prior | The prior decides the answer (11.4) | not computed |

### 11.3 What we do print

| Quantity | Exact definition | Label | Read as |
|---|---|---|---|
| a. Counts and ratios | `linked / total`, `covered obligations / impacted obligations`, with the numerator and denominator | MEASUREMENT of the graph | not adequacy |
| b. Exhaustive-domain statement | "all N enumerated cells matched" where the cells are a stated finite abstraction; for the runtime matrix the kernel enumerates `actors x states x actions` = 5 x 4 x 5 = 100 cells (125 with `Recommended`) (`evidence.py`) | proof by exhaustion **of the abstraction** | not a statement about all executions |
| c. Generator-relative bound | "n failure-free draws; any failure region with generator mass at least `m` was missed with probability at most `(1 - m)^n`" (`n = 1000`, `m = 1/1000`: 0.3677) | conditional on the generator; PREDICTION about the world | says nothing when the failing region has generator mass 0 |
| d. Mutation ratio | killed / total, fault model and tool pin named | MEASUREMENT over a stated fault model | relative indicator (S12); ratchet on it is a regression gate, not a confidence claim |
| e. `pass^k` for agent runs | `C(c,k) / C(n,k)`, unbiased for `p^k` when trials are independent (exact check in O8a); print `n`, `c`, model id, CLI version, date | MEASUREMENT with `n` stated | `n = 5, c = 5` says the failure rate could still be 45% (O8b) |
| f. Evidence summary | per claim: slots, statuses, TCB label, bounds, assumption ledger, unresolved defeaters, `k` | DESIGN | the honest replacement for a percentage |

### 11.4 Three demonstrations (all exact, oracle O8)

- Same data, three priors. Five successes, no failures: uniform Beta(1,1) gives 6/7 = 0.857, Jeffreys Beta(1/2,1/2) gives 11/12 = 0.917, Haldane Beta(0,0) gives 1, i.e. failure probability 1/7, 1/12 or 0. The subjective-logic projection with `W = 2` and base rate 1/2 reproduces 6/7. A confidence built on this is the prior.
- Blind spots. A generator with failure-region mass `m` misses it in `n` draws with probability `(1 - m)^n`; for `m = 0` that is exactly 1 for every `n`.
- Conjunction. Twenty conjuncts at 0.99 give a Frechet lower bound of exactly 0.8 against 0.8179 under independence; two hundred give 0 against 0.134. A number for a big claim is either unjustified (independence) or vacuous (Frechet).

### 11.5 What each printed quantity does not prove

(a) adequacy of tests; (b) anything outside the enumerated cells; (c) anything about real inputs; (d) detection of faults outside the mutation operators; (e) `pass^k` of the next run; (f) that the evidence is independent.

### 11.6 Revisit trigger (a proposal; the number is the owner's to set)

Reconsider a calibrated number only when there is data to calibrate against: a ledger of human decisions with recorded later outcomes large enough to score a forecast (for example a Brier score) and a stated operational profile for a deployed component. Until then the claim "this software is X% likely correct" is not made.

## 12. Complexity and measured cost

MEASUREMENT: the reference implementations ([graph/bench/impact_math_timing.py](../../../graph/bench/impact_math_timing.py)), Windows 11, CPython 3.12.10, seeded random graphs, best of 3 runs (one run where marked), milliseconds, on one shared 16 GB PC under other agents' load. The reference favours clarity; a production implementation should not be slower.

| Computation | Cost class | 1 000 nodes, 4 993 arcs | 10 000 nodes, 49 985 arcs | 100 000 nodes, 499 984 arcs |
|---|---|---|---|---|
| Closure from one root (reference BFS) | `O(V_r + E_r)` | 2.5 | 39.2 | 606.8 |
| Same closure, SQLite recursive CTE with an index | `O(V_r + E_r)` plus index lookups | 4.6 | 75.5 | 1114.6 |
| SCC labels (iterative Tarjan) | `O(V + E)` | 4.4 | 92.2 | 1524.3 (1 run) |
| Reach counts for every node (bitset DP) | `O(E V / w)` | 6.7 (1 run) | 171.8 (1 run) | NOT_RUN |
| Integer PPR, `K = 66` (`bits = 20`) | `O(K (V + E))` | 311.9 (1 run) | 3640.4 (1 run) | NOT_RUN |

Greedy set cover (reference, no lazy evaluation): 7.3 ms for 200 elements and 100 sets, 1016.7 ms for 2 000 elements and 1 000 sets (1 run).

Reading (PREDICTION where it goes beyond the table). The closure is cheap at any size this graph will plausibly reach: the synthesis measured 10^6 arcs at about 0.85 s for plain BFS and 1.3 s in SQLite, and this run agrees in order of magnitude. The integer PPR is the expensive one: 3.6 s at 50 000 arcs is fine for an on-demand `context` query and too slow to run for every node. Two controls, both DESIGN, to be checked by test when built: (a) restrict `H` to the nodes within `L` hops of the seeds, because the exact mass at hop distance beyond `L` is at most `beta^(L+1)` (a walk must continue `L + 1` times), which is about 0.001 for `alpha = 1/5, L = 30`; the truncation error must be verified against the full computation before it is trusted; (b) a lazy-evaluation greedy for set cover (a priority queue whose keys only worsen as coverage grows) with the same tie-breaks, tested equal to the reference. A native or vectorised integer PPR is allowed if it reproduces oracle O3 byte for byte. The store aspect measured closure of 5 roots through its typed `edge` table (with an edge-type join) at 10^6 edges in two runs, 2.5 s and 3.6 s with text ids and 1.1 s and 1.7 s with integer-interned ids (its table, read 2026-09-29; the final run and earlier run B; quoted as ranges because the runs differ), and 3.8 s and 4.4 s for the stratified "impacted and untested" violation; its graph and joins differ from the plain graph timed here, so the two tables are not comparable and neither says anything about a real repository. None of these numbers says anything about agents or people; they bound the cost of the computations only.

## 13. Interfaces to other aspects and lanes

Read on 2026-09-29 (parallel work, files may move): metamodel (`graph/schema/metamodel.json`, ADR-0089), consistency (ADR-0093), agent interface (`docs/weave/design/agent-interface-and-context-packs.md`, `graph/schema/mcp-tools.md`, ADR-0099), human views (`graph/schema/views.md`), formal reference (`graph/formal/eijaref`), rules catalogue (`graph/schema/rules.md`, `graph/brief.json`). ADR numbers of aspects whose records I have not seen are not cited.

| To | What this aspect needs or provides | Concrete interface |
|---|---|---|
| Metamodel aspect (ADR-0089) | Reads `soundness`, `affects`, `anchor_ends` per link kind and derives the impact flow (section 1); requests an optional `cost` attribute on verifier node types (a policy table is the fallback) | `flow_from_metamodel` in the reference; a test that fails on an unknown `affects` value or a kind whose derived flow misses an anchored end |
| Agent-interface aspect (ADR-0099) | **`graph_impact`** is IR-1: `by_soundness.must`, `.may`, `.heuristic_only` are tiers 0, 1 and 2 with the lower tiers removed; `max_nodes` is the kernel budget with `bounds.complete` and `bounds.frontier`; a witness is the lexicographically first shortest path. **`context_pack`** takes its mandatory set `M` as the pinned set of section 6 and its `ranked` tier from IR-4 and IR-5. Open: its own fixed-step PageRank spec differs from IR-4 (section 5.7) | Same closure and knapsack code behind both tools; the `params` block carries `alpha`, iteration count, weights digest and `err_bound_units` |
| Human-views aspect (ADR-0101, file currently `00101-weave-human-views.md`; `graph/schema/views.md`) | Consumes `tiered_impact(links, flow, soundness, roots) -> {node: {tier, distance, witness}}` (HV-02, HV-07), `fold_a`, `fold_b`, `LIFT`, the greedy cover for `verification_cover`, and the redundancy count for `evidence_redundancy` (HV-03) | Names and shapes are those of `graph/bench/impact_math_reference.py`; a missing function makes the view report NOT_RUN |
| Formal aspect (`graph/formal/eijaref`) | Second checker for closure certificates and SCC and topological-order results; a separate status reference | Differential tests in `test_impact_math_oracles.py` (closure certificate accepted, forged parent rejected, SCC labels and order equal, status agreement with two documented deviations, section 10.3) |
| Consistency aspect (ADR-0093) | Roots come from the keyed diff of two graph roots; closure runs over the union of base and head arcs | `changed` ids from the store's diff; no other coupling |
| Store aspect (ADR-0091, `storage-and-query.md`) | An `arc` view over its `edge(src, type, dst, origin, soundness, ...)` table joined to a generated `flow(type, f, r)` table; the closure query with `:tier`; every result ends in a total `ORDER BY`. Its named query `impact(roots, edge_types, budget)` returns affected ids, frontier and one witness; tiers add the class of the edge row (not of its kind), so an extractor can downgrade a single edge. Its `context(id, budget_tokens)` should read bytes, to agree with the agent interface's `budget_units` and IR-5 (tokenizers are model-specific) | SQL in oracle O1 tested against that schema; differential test against the reference |
| Link and ledger aspect | `link_status` results; hash-method registry; ledger. `link_status` lifts to evidence status by `LIFT`; "content hash changed" feeds the roots | `link_status -> {COVERED, SUSPECT, ...}` |
| Assurance aspect | `assess_link` outputs feed `A`; slots and claims feed `B`; `NOT_RUN` only from missing prerequisites | `fold_a`, `fold_b` semantics (section 10) |
| Rules aspect (ADR-0095, `compiler-and-lint-rules.md`, `graph/schema/rules.md`) | Existing rules this aspect feeds: WV-005 (suspect link), WV-010 (requirement without verifier), WV-014 (single point of evidence), WV-016 (evidence redundancy below k). New rule ideas, ids to be assigned by the rules aspect (the store aspect already measures an "impacted and untested" violation query; section 7's version is stricter, it needs a verifier that also observes the change): "impacted obligation with no observing test" (section 7), "claim with no required slot" (section 10), "stale set not within impact set" (section 3, a self-check) | Witness of each finding as in section 2 |
| okf lane (ADR-0045/0046) | Page byte length as `render_bytes`; `context` returns node ids that resolve to pages | Reads the digest the okf lane already computes |
| agents lane (ADR-0041) | The MCP server that hosts the tools; every result bounded, sorted, integer, with `complete`, `frontier` and `params` | No free-form query |
| metrics lane (ADR-0037) | A `graph_math` section: impact counts per tier, cover size, `H(d)`, risk fields, `pass^k`; deterministic part separate from timings; `not_measured` list | Same MEASURED / NOT_RUN vocabulary |
| mutation lane (ADR-0033) | Edge attribute `fault_detection` = `{killed, total, fault_model, tool_pin}` | Reported, never converted to a probability |
| property lane | Strategies for law tests (permutation invariance, `F(closure) = closure`, greedy ratio) | Reuse the oracle tests as properties |
| quality lane (ADR-0035/0036) | Two sessions appended to `quality/sessions/graph.py`: `graph_impact_math` (tags `fast`, `full`) runs the oracle tests (about 10 s); `graph_impact_math_bench` (tag `release`) runs the timing script. The co-change study needs external clones, is run by hand (section 16) and is NOT_RUN in the gates | `python=False`, tags |
| tla, bend, smt-bmc | Witnesses become `assess_link` results, hence `A` inputs; a missing tool is `NOT_RUN` | Assurance aspect owns the witness schema |
| kernel (`src/`) | Read-only oracles: `impact.closure`, `evidence.aggregate_status`; nothing changes here | `eijagraph` never imports `eija_studio`; tests may |

`impact`, `context`, `select_tests` and `risk` results carry `params` = the canonical JSON of the parameters plus the digests of the arc set and the flow table, so a result is replayable. None carries a float or a timestamp.

## 14. What the whole thing does not prove, and what is unmeasured

| Statement | Status |
|---|---|
| Any of these computations makes agents more reliable or humans faster | UNMEASURED. Offline retrieval proxy in 5.6 only. Design for the measurement: pre-registered tasks, `pass^k` with and without `context` and semantic diff (agents lane), a review-time study (hci lane). METR's randomised trial found experienced developers 19% slower with early-2025 AI tools while expecting a speed-up ([agent], arXiv 2507.09089, not re-opened by me), so measurement, not assumption, decides |
| Impact is complete | False by construction: encoded arcs only |
| A selected test set finds defects | UNMEASURED; mutation calibrates |
| PPR beats hop distance in general | Two Python repositories, co-change proxy, tuned on older commits: not shown in general |
| POSIX byte-identity of the ranking | NOT_RUN. Integer arithmetic makes it very likely; only Windows was run here (PREDICTION) |
| The kernel's `aggregate_status` rule composes under roll-up | No, and the kernel does not roll up today. The hazard is reported, the algebra is in `graph/`, a kernel ADR is pending |

## 15. Sources (opened 2026-09-29 unless marked)

| Id | Source | What it was used for |
|---|---|---|
| S1 | https://en.wikipedia.org/wiki/Kleene_fixed-point_theorem | Hypotheses and statement of Kleene's theorem (secondary) |
| S2 | https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm | `O(V+E)`, reverse topological emission |
| S3 | https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/ ; https://github.com/neo4j/graph-data-science (LICENSE.txt head: GNU GPL version 3 for the Neo4j Sweden AB software, NOTICE lists other licences) | GDS PageRank defaults and float convergence; licence |
| S4 | https://en.wikipedia.org/wiki/PageRank | Damping formula, dangling nodes, power iteration (secondary). Personalisation papers exist: Haveliwala, "Topic-sensitive PageRank", WWW 2002, and Jeh and Widom, "Scaling personalized web search", WWW 2003 (bibliographic records via Crossref only; not read) |
| S5 | https://en.wikipedia.org/wiki/Knapsack_problem | Density greedy and the 1/2 argument (secondary) |
| S6 | https://api.crossref.org/works/10.1145/248233.248262 | Rothermel and Harrold, TOSEM 1997, abstract quoted |
| S7 | https://coverage.readthedocs.io/en/latest/contexts.html ; https://github.com/coveragepy/coveragepy (Apache-2.0, pushed 2026-09-27, SPDX) | Dynamic contexts, licence |
| S8 | https://api.crossref.org/works/10.1287/moor.4.3.233 | Chvatal 1979, bibliographic record (paper not opened) |
| S9 | https://en.wikipedia.org/wiki/Set_cover_problem | `H(d)` greedy ratio, weighted rule, tight example, inapproximability (secondary) |
| S10 | https://arxiv.org/abs/1305.1979 | Dinur and Steurer, abstract: stronger inapproximability for Set-Cover (the `(1 - o(1)) ln n` figure is from S9) |
| S11 | GitHub API `repos/google/or-tools`: Apache-2.0, pushed 2026-09-28 | Optional exact solver licence |
| S12 | https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014.pdf (abstract read locally) | Just et al., FSE 2014 |
| S13 | https://github.com/tarpas/pytest-testmon ; https://testmon.org/ (both opened 2026-09-29); GitHub API (MIT, pushed 2025-12-01) | Test-selection tool status, licence, `.testmondata`, use of Coverage.py |
| S14 | https://api.crossref.org/works/10.1145/2771783.2771784 | Ekstazi paper, bibliographic record only |
| S15 | https://api.crossref.org/works/10.1145/2950290.2950361 | Static RTS study, bibliographic record only |
| S16 | https://en.wikipedia.org/wiki/Menger%27s_theorem | Vertex version, directed graphs |
| S17 | https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem | Residual reachability defines a minimum cut; the page shows several minimum cuts exist |
| S18 | https://api.crossref.org/works/10.1145/1062455.1062514 | Nagappan and Ball, ICSE 2005, bibliographic record only |
| S19 | https://en.wikipedia.org/wiki/Semilattice | Algebraic and order definitions |
| S20 | https://en.wikipedia.org/wiki/Rule_of_three_(statistics) | Rule of three statement and derivation |
| S21 | https://arxiv.org/abs/2008.09510 | Zhao et al. abstract (CBI) |
| S22 | https://en.wikipedia.org/wiki/Subjective_logic | Opinion definition, Beta mapping, fusion independence |
| S23 | https://en.wikipedia.org/wiki/Fr%C3%A9chet_inequalities | Conjunction bounds |
| S24 | https://en.wikipedia.org/wiki/Four-valued_logic | Belnap's four values (information order not confirmed) |
| Sib | Sibling aspects read on 2026-09-29: `graph/schema/metamodel.json`, `graph/schema/mcp-tools.md`, `graph/schema/views.md`, `graph/schema/rules.md`, `docs/weave/design/agent-interface-and-context-packs.md`, `docs/adr/0093-weave-consistency-sync.md`, `docs/adr/0099-weave-agent-interface.md`, `graph/formal/eijaref/{closure,order,status}.py` | Interfaces and reconciliation (sections 1, 5.7, 10.3, 13) |
| Local | `src/eija_studio/domain/impact.py`, `domain/evidence.py`; `graph/bench/foundations_checks.py`; `docs/weave/research/*`; `graph/brief.json` | Kernel oracles, measurements M1 to M5 reused |

Not opened, so nothing is built on them: the ACL local-partitioning paper (fetch failed with a certificate error), Brandes 2001, the original PageRank report, Picard and Queyranne 1980, Belnap 1977, Chvatal's paper text, Ekstazi and Legunsen results, CBI theorem statements, tau-bench and RepoGraph beyond the dossier extracts. Wikipedia pages are secondary sources; every theorem used is either checked by enumeration here or stated with its hypotheses and marked.

## 16. Reproduce

```bash
export TMP=$PWD/.tmp TEMP=$PWD/.tmp
python -m pytest tests/graph/test_impact_math_oracles.py -q          # 43 tests, about 5 to 10 s
python graph/bench/impact_math_timing.py                             # section 12, machine dependent
git clone https://github.com/doorstop-dev/doorstop.git .tmp/cochange/doorstop      # pinned HEAD in the result file
git clone https://github.com/strictdoc-project/strictdoc.git .tmp/cochange/strictdoc
python graph/bench/ranking_cochange_eval.py .tmp/cochange/doorstop --commits 1200 --max-seeds 3     --out graph/bench/results/ranking-cochange-doorstop.json         # section 5.6, about 12 minutes
python graph/bench/ranking_cochange_eval.py .tmp/cochange/strictdoc --commits 900 --max-seeds 2     --exclude tests --exclude docs --exclude developer --exclude tools     --out graph/bench/results/ranking-cochange-strictdoc.json        # about 7 minutes
```

The clones are read with `git show` and `git log` only; check out the pinned `repo_head` of each result file to reproduce a number exactly (the script reads files from `HEAD`).
