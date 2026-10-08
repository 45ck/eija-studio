# Math oracles: worked examples with hand-verified answers

Lane: weave. Date: 2026-09-29. Companion to [docs/weave/design/impact-ranking-and-confidence.md](../../docs/weave/design/impact-ranking-and-confidence.md) and [ADR-0097](../../docs/adr/0097-weave-impact-ranking-math.md).

**How to use.** Each oracle is a tiny input, the definition it exercises, the derivation by hand, and the exact expected output. `eijagraph` must reproduce every value byte for byte. The same values are asserted by [tests/graph/test_impact_math_oracles.py](../../tests/graph/test_impact_math_oracles.py) against the stdlib reference [graph/bench/impact_math_reference.py](../bench/impact_math_reference.py) (43 tests, reproduced 2026-09-29: `python -m pytest tests/graph/test_impact_math_oracles.py`). A production implementation is differential-tested against that reference; the reference is tested against the kernel (`impact.closure`, `aggregate_status`), brute force, exact rationals and, when installed, networkx.

**Labels.** HAND = derived on paper here and then confirmed by the reference. EXHAUSTIVE = the test enumerates the whole stated domain. SEEDED = the test samples with a fixed seed (evidence, not proof). A value with no label is an input.

**What an oracle does not show.** Passing an oracle shows the code matches the definition on that input. It does not show the definition is the right thing to compute. That question is answered (or left open) in the design document.

---

## O1. Typed impact closure: tiers, distances, witnesses, budget, deleted links

**Definitions used.** A link `(src, type, dst)` yields impact arcs by its type's declared flow: `F` gives `src -> dst` (a change at `src` affects `dst`), `R` gives `dst -> src`. A type has a soundness class 0 (must), 1 (may) or 2 (heuristic). `I_c` is the arc set of classes `<= c`. `Impact(C, c)` is the least fixed point of `X -> C U succ_{I_c}(X)`. `tier(v)` is the least `c` with `v` in `Impact(C, c)`. `distance(v)` is the BFS distance in `I_tier(v)`. The witness is the lexicographically smallest shortest path from any root (sorted roots, sorted successors).

**Input.**

| Link type | flow | class |
|---|---|---|
| depends_on | R | 1 (may) |
| satisfies | FR | 0 (must) |
| verifies | FR | 0 (must) |
| calls | R | 2 (heuristic) |

Links (`src type dst`): `S2 depends_on S1`, `S3 depends_on S2`, `S1 depends_on S3`, `S2 satisfies R1`, `T1 verifies R1`, `S4 calls S3`, `T2 verifies R2`, `S4 satisfies R2`. Isolated node `D1`. Change set `C = {S1}`.

**Arcs by class (HAND).** `depends_on` has flow R, so `S2 depends_on S1` gives arc `S1 -> S2`; likewise `S2 -> S3` and `S3 -> S1` (class 1). `satisfies` and `verifies` give both directions (class 0): `S2 <-> R1`, `T1 <-> R1`, `T2 <-> R2`, `S4 <-> R2`. `calls` (R) gives `S3 -> S4` (class 2).

**Derivation (HAND).**
- Class 0 arcs only: `S1` has no outgoing class-0 arc, so `Impact(C,0) = {S1}`.
- Add class 1: `S1 -> S2 -> S3 -> S1` cycle, `S2 -> R1`, `R1 -> T1`, `R1 -> S2`. `Impact(C,1) = {S1, S2, S3, R1, T1}`.
- Add class 2: `S3 -> S4`, `S4 -> R2`, `R2 -> T2`. `Impact(C,2) = {S1, S2, S3, S4, R1, R2, T1, T2}`. `D1` is never reached.

**Expected output (EXHAUSTIVE over the 8 nodes).**

| node | tier | distance | witness |
|---|---|---|---|
| S1 | 0 | 0 | S1 |
| S2 | 1 | 1 | S1 S2 |
| S3 | 1 | 2 | S1 S2 S3 |
| R1 | 1 | 2 | S1 S2 R1 |
| T1 | 1 | 3 | S1 S2 R1 T1 |
| S4 | 2 | 3 | S1 S2 S3 S4 |
| R2 | 2 | 4 | S1 S2 S3 S4 R2 |
| T2 | 2 | 5 | S1 S2 S3 S4 R2 T2 |

Note the witness of a tier-1 node uses no class-2 arc. That is the point of tiers: a reader can trust a tier-1 explanation without believing any heuristic edge.

**Budget (HAND).** On the class-2 arc set with `budget = 4`: BFS visits `S1`, `S2`, then `S2`'s successors in sorted order `R1, S3` (visit order `S1 S2 R1 S3`), then stops with 4 visited. Discovered but unvisited: `S4` (from `S3`) and `T1` (from `R1`). Expected: `affected = [R1, S1, S2, S3]`, `complete = false`, `frontier = [S4, T1]`. The kernel returns the same three fields. With `budget = 0`: `affected = []`, `frontier = [S1]`, `complete = false`.

**Deleted link (HAND).** Base has `T2 verifies R2` and `S4 satisfies R2`; the change deletes the `verifies` link. Change `S4`. Base-only closure (class 0): `{R2, S4, T2}`. Head-only: `{R2, S4}`. Closure over base union head: `{R2, S4, T2}`. The rule: impact runs over the union of base and head arcs, so a dependent that lost its link is still reported.

**SQL form (must agree, tested at tiers 0, 1, 2).** Written against the store aspect's `edge` table (`docs/weave/design/storage-and-query.md` section 4.2, which stores `soundness` as text per edge) plus a small `flow(type, f, r)` table generated from the metamodel's `affects` and `anchor_ends`:

```sql
CREATE VIEW arc AS
SELECT e.src AS src, e.dst AS dst,
       CASE e.soundness WHEN 'must' THEN 0 WHEN 'may' THEN 1 ELSE 2 END AS cls
  FROM edge e JOIN flow x ON x.type = e.type WHERE x.f = 1
UNION
SELECT e.dst, e.src,
       CASE e.soundness WHEN 'must' THEN 0 WHEN 'may' THEN 1 ELSE 2 END
  FROM edge e JOIN flow x ON x.type = e.type WHERE x.r = 1;

WITH RECURSIVE reach(node) AS (
  SELECT node FROM root
  UNION
  SELECT a.dst FROM arc a JOIN reach r ON a.src = r.node WHERE a.cls <= :tier
) SELECT node FROM reach ORDER BY node;
```

The class comes from the edge row, not from its kind, so an extractor may downgrade a single edge (a `calls` edge resolved by a tool can be `may`, an unresolved one `heuristic`) without touching the metamodel.

**Property checks behind O1.** SEEDED (300 graphs, budgets None/0/1/3/7): closure, `complete` and `frontier` equal the kernel. EXHAUSTIVE (60 graphs of at most 7 nodes, all `2^n` subsets): `closure = F(closure)` and `closure` is contained in every `S` with `F(S)` contained in `S`. SEEDED (100 graphs): monotone in roots and in arcs, invariant under arc and adjacency reordering. SEEDED (100 graphs, exhaustive path enumeration): the witness equals the lexicographically smallest shortest path. SEEDED (600 random typed graphs; at least 20 satisfy the lint): when every link type's flow includes the direction away from its anchored endpoint, the far ends of suspect links lie inside the impact set; a negative control finds counterexamples when the lint is dropped.

---

## O2. SCC condensation, lexicographic topological order, reach and exposure counts

**Definitions.** `label(v)` = minimum member id of `v`'s strongly connected component. The condensation DAG has one node per label and a sorted arc `label(u) -> label(v)` for each arc `u -> v` with different labels. The topological order is the lexicographically smallest one (repeatedly take the smallest available label). `reach(v) = |closure({v})|` including `v`. `exposure(v)` = number of nodes whose closure contains `v`, including `v`.

**Input.** Nodes `a b c d e f g h`. Arcs: `a->b`, `b->c`, `b->f`, `c->a`, `c->d`, `d->e`, `e->d`, `g->a`. `h` isolated.

**Derivation (HAND).** Cycles: `a->b->c->a` gives `{a,b,c}` (label `a`); `d<->e` gives `{d,e}` (label `d`). `f`, `g`, `h` are singletons. Condensation arcs: `b->f` gives `a->f`; `c->d` gives `a->d`; `g->a` gives `g->a`. In-degrees: `g` 0, `h` 0, `a` 1, `d` 1, `f` 1. Kahn with a min-heap: available `{g,h}`; take `g`, which frees `a`; available `{a,h}`; take `a`, which frees `d` and `f`; available `{d,f,h}`; take `d`, `f`, `h`.

| quantity | expected |
|---|---|
| labels | a,b,c -> a; d,e -> d; f -> f; g -> g; h -> h |
| condensation | a: [d, f]; d: []; f: []; g: [a]; h: [] |
| topological order | g, a, d, f, h |
| reach | a 6, b 6, c 6, d 2, e 2, f 1, g 7, h 1 |
| exposure | a 4, b 4, c 4, d 6, e 6, f 5, g 1, h 1 |

Reach of `a` is `{a,b,c,d,e,f}` = 6; reach of `g` is those plus `g` = 7. Exposure of `d` counts `{a,b,c,d,e,g}` = 6; exposure of `f` counts `{a,b,c,f,g}` = 5 (HAND).

**Property checks.** SEEDED (150 graphs): labels equal mutual reachability classes, each label is the minimum member, labels are identical under shuffled node and arc order, reach counts equal brute-force closure sizes. SEEDED (60 DAGs of at most 6 nodes, all permutations): the order equals the minimum over all topological orders. SEEDED (100 graphs, skipped as NOT_RUN without networkx): the partition equals `nx.strongly_connected_components`.

---

## O3. Personalised PageRank in bit-exact integers

**Definitions.** Seeds carry integer weights; `s` is the normalised seed distribution. Arc weights are non-negative integers; `P(u,v) = w(u,v) / W_u`; a node with `W_u = 0` (dangling) returns to `s`. Teleport probability `alpha = a/b`, continue probability `beta = 1 - alpha`. The target is the exact vector `pi = alpha s + beta pi P` (row vector, sums to 1). The algorithm works on integer vectors of total mass `SCALE = 2^40`: from state `x`, each node `u` with `x_u > 0` sends `cont_u = floor(x_u (b-a) / b)` along its arcs (proportional split by floor, the remainder units going one each to the first targets in sorted id order) and the rest `x_u - cont_u` (plus all of `cont_u` for a dangling node) to the seed distribution by the same split rule. Iteration count `K` = the least integer with `2 beta^K <= 2^(-bits)`, decided in integers as `2^(bits+1) (b-a)^K <= b^K`. Total mass is `SCALE` after every iteration, exactly.

**Error bound (derived in the design document, section 5.3).** `|| x_K - SCALE*pi ||_1 <= 2 SCALE beta^K + (arcs + 2 nodes + seeds) / alpha` units. Consequence: if `x_u - x_v > 2 * bound` the order of `u` and `v` agrees with the exact `pi`.

### O3a. Three nodes, one seed, no dangling node

Arcs `A->B`, `A->C`, `B->C`, `C->A`, all weight 1. Seed `A` with weight 1. `alpha = 1/5`, `beta = 4/5`.

**Derivation (HAND).** `P(A,B) = P(A,C) = 1/2`, `P(B,C) = 1`, `P(C,A) = 1`. The equations:
- `pi_B = beta * pi_A / 2 = (2/5) pi_A`
- `pi_C = beta * (pi_A/2 + pi_B) = (4/5) * (1/2 + 2/5) pi_A = (4/5)(9/10) pi_A = (18/25) pi_A`
- `pi_A = alpha + beta * pi_C = 1/5 + (4/5)(18/25) pi_A = 1/5 + (72/125) pi_A`, so `pi_A (53/125) = 1/5` and `pi_A = 25/53`.
- Then `pi_B = 10/53`, `pi_C = 18/53`; the sum is `53/53 = 1` (check).

**Iteration count (HAND).** With `bits = 24` we need `(5/4)^K >= 2^25`, so `K >= 25 ln2 / ln 1.25 = 17.329 / 0.22314 = 77.66`, hence `K = 78` (and `K = 66` for `bits = 20`).

**Expected output (EXHAUSTIVE, one input).** `K = 78`; scores sum to exactly `2^40`; parts per million `A 471698, B 188679, C 339623` (true values 471698.11, 188679.25, 339622.64; sum 1000000); ranking `A, C, B`; every score within `err_bound_units` of `pi * 2^40` (the bound printed by the reference is 60764 units, about 0.055 ppm; the observed error is below one unit).

### O3b. Dangling node

Arcs `A->B` only; seed `A`; `alpha = 1/5`. `B` has no out-arc, so its continue mass returns to `A`.

**Derivation (HAND).** `pi_B = beta pi_A = (4/5) pi_A`. `pi_A = alpha + beta pi_B = 1/5 + (16/25) pi_A`, so `pi_A (9/25) = 1/5`, `pi_A = 5/9`, `pi_B = 4/9`. Expected ppm `A 555556, B 444444`.

**Property checks.** SEEDED (40 random weighted graphs with dangling nodes, several `alpha`, 1 to 2 seeds): mass conserved and L1 error within the printed bound against the exact rational solution (Gaussian elimination in `Fraction`). SEEDED (5 shuffles of node list, arc dict and seed dict order; plus 4 `PYTHONHASHSEED` values in subprocesses): scores byte-identical. SEEDED (skipped as NOT_RUN without networkx): agrees with `nx.pagerank(alpha=0.8, personalization=s, dangling=s)` within 1e-6 on a 25-node graph.

---

## O4. Context selection under a byte budget

**Definitions.** Pinned nodes (the seeds) are always included; if their cost alone exceeds the budget the result is `BUDGET_TOO_SMALL` with the cost needed, and nothing is truncated. Candidates `(score, cost)` with `0 < cost <= room` and `score > 0` form the pool, sorted by `score/cost` descending (compared by cross-multiplication), ties by id. Take each that fits (skipping those that do not). Then compare the value of that set with the single best pool candidate and keep the larger. Every candidate that is not chosen is listed in `omitted` with a reason in `omitted_reasons`: `NOT_SELECTED_BUDGET` (in the pool, lost), `TOO_LARGE_FOR_ROOM` (`cost > room`), `NON_POSITIVE_SCORE`, `NON_POSITIVE_COST`. Chosen and omitted partition the candidates.

**Input O4a.** Pinned `seed` cost 40; budget 100; room 60; candidates `a (90, 30)`, `b (60, 10)`, `c (50, 25)`, `d (10, 5)`.

**Derivation (HAND).** Densities: `b` 6.0, `a` 3.0, `c` 2.0, `d` 2.0. Sorted: `b, a, c, d` (tie `c` before `d` by id, but `c` will not fit). Take `b` (room 50), `a` (room 20), skip `c` (25 > 20), take `d` (room 15). Chosen `{a, b, d}`, value 160, cost 45, total with seed 85. The best single candidate is `a` (90), less than 160, so the greedy set stays. Exhaustive optimum for room 60 is also 160 (`a+b+d`; `a+c` 140; `b+c+d` 120).

**Expected.** `chosen = [a, b, d]`, `cost = 85`, `value = 160`, `omitted = [c]`, `omitted_reasons = {c: NOT_SELECTED_BUDGET}`.

**Input O4b (why the safeguard exists).** No pinned nodes; budget 100; candidates `p (2, 1)`, `q (100, 100)`. Density order `p` (2.0) then `q` (1.0): greedy takes `p`, then `q` does not fit; value 2. The best single candidate is `q` with value 100 > 2. Expected `chosen = [q]`, `omitted = [p]` (`NOT_SELECTED_BUDGET`). Without the safeguard the answer would be 2 against an optimum of 100.

**Input O4c.** Pinned `seed` cost 40, budget 30. Expected `{status: BUDGET_TOO_SMALL, needed: 40, chosen: [], omitted: [], omitted_reasons: {}}`.

**Input O4d (nothing dropped silently).** Pinned `seed` cost 40; budget 100; room 60; candidates `big (1000, 70)`, `a (10, 5)`, `zero (0, 5)`, `free (7, 0)`.

**Derivation (HAND).** `big` costs 70 > 60: it can never fit, whatever its score, so it is excluded from the pool but must be reported, because it is the most relevant candidate and the budget is why it is missing. `zero` has no score to gain; `free` has no defined density. Pool `{a}`; chosen `[a]`. Expected `omitted = [big, free, zero]` (excluded ones by id) with reasons `TOO_LARGE_FOR_ROOM`, `NON_POSITIVE_COST`, `NON_POSITIVE_SCORE`. A reader can therefore tell that a larger budget would bring `big` in.

**Property checks.** SEEDED (200 instances, exhaustive optimum by subset enumeration): value is at least half of the optimum, cost never exceeds the budget. SEEDED (200 instances with negative and zero scores and costs): `chosen` and `omitted` partition the candidates and `omitted_reasons` has exactly the omitted ids.

---

## O5. Weighted set cover (test and evidence selection)

**Definitions.** Universe `U`, sets `S_i` with cost `c_i`. Greedy: repeatedly choose the set minimising `c_i / |S_i ∩ uncovered|` (exact `Fraction`), ties by more newly covered, then smaller id. Elements in no set are returned as `unreachable`, never dropped. `d = max |S_i|`, `H(d) = 1 + 1/2 + ... + 1/d`.

### O5a. Greedy is not optimal

Elements: `a1 a2` (set `S1`, cost 1); `b1..b4` (`S2`, cost 1); `c1..c8` (`S3`, cost 1). Two further sets each hold half of every block: `A = {a1, b1, b2, c1, c2, c3, c4}` and `B = {a2, b3, b4, c5, c6, c7, c8}`, cost 1 each. `|U| = 14`, `d = 8`.

**Derivation (HAND).** Optimum: `A` and `B` cover all 14, cost 2; one set cannot (largest is 8). Greedy, all costs 1, so it takes the set with most newly covered: `S3` (8). Remaining uncovered `a1 a2 b1..b4`: `S2` covers 4, `A` covers `a1 b1 b2` = 3, `B` covers 3, `S1` covers 2. Take `S2`. Remaining `a1 a2`: `S1` covers 2, `A` covers 1, `B` covers 1. Take `S1`. Greedy = `{S3, S2, S1}`, cost 3. Ratio 3/2 = 1.5, within `H(8) = 761/280 = 2.718`.

**Expected.** `chosen = [S3, S2, S1]`, `cost = 3`, optimum 2.

### O5b. The cost-aware rule

Elements `1..7`. `X = {1..6}` cost 12; `Y = {1,2,3}` cost 3; `Z = {4,5,6}` cost 3. Element `7` is in no set.

**Derivation (HAND).** Ratios: `X` 12/6 = 2; `Y` 3/3 = 1; `Z` 1. Take `Y` (tie with `Z` on ratio and on newly covered, smaller id `Y`), then `Z`. Cost 6 = optimum for `{1..6}`; a rule that maximised coverage alone would pick `X` for 12. `7` is reported as `unreachable`, which in the product is a finding ("impacted obligation with no observing test"), not a silent omission.

**Expected.** `chosen = [Y, Z]`, `cost = 6`, `unreachable = [7]`.

**Property checks.** SEEDED (300 instances of at most 8 elements and 7 sets, exhaustive optimum): `optimum <= greedy <= H(d) * optimum`; result identical under shuffled set order.

---

## O6. Evidence redundancy: vertex-disjoint paths and the canonical minimum cut

**Definitions.** Between a requirement `R` and an evidence sink `E` (not adjacent), `k` = the maximum number of internally vertex-disjoint paths = the minimum vertex cut (Menger). The canonical minimum cut is the set of internal vertices whose in-copy is reachable from `R` in the residual graph of a maximum flow (unit vertex capacities by node splitting) and whose out-copy is not. It is the source-side minimal minimum cut and does not depend on which maximum flow was found.

| Case | Arcs | k | canonical cut | Reading (HAND) |
|---|---|---|---|---|
| Diamond into one hub | R->x, R->y, x->z, y->z, z->E | 1 | {z} | `z` is a single point of evidence; removing it severs everything |
| Two independent routes | R->x, R->y, x->E, y->E | 2 | {x, y} | Removing any one vertex leaves a path; the cut needs both |
| Chain | R->u, u->v, v->E | 1 | {u} | `{u}` and `{v}` are both minimum cuts; the canonical choice is the one nearest the source |
| Three routes, capped at 2 | R->a, R->b, R->c, a->E, b->E, c->E | at least 2 | none reported | The cap stops augmenting at 2; the report says "at least 2" |

**Property check.** SEEDED (200 random graphs of at most 7 nodes, at least 20 usable): `k` equals the brute-force minimum cut size, the canonical cut is one of the minimum cuts, and its source side is contained in the source side of every other minimum cut.

---

## O7. Status algebra: two operators, never mixed

**Operator A, replication join (several observations of one check).** Carrier `{UNKNOWN, STALE, PASS, FAIL, CONFLICT}` (the kernel's five; `NOT_RUN` is refused with an error, it is not a receipt status; the empty fold is `UNKNOWN`, equal to the kernel's `aggregate_status([])`); order `UNKNOWN < STALE < PASS < CONFLICT` and `STALE < FAIL < CONFLICT` (PASS and FAIL incomparable). `join_a` is the least upper bound.

| join | UNKNOWN | STALE | PASS | FAIL | CONFLICT |
|---|---|---|---|---|---|
| **UNKNOWN** | UNKNOWN | STALE | PASS | FAIL | CONFLICT |
| **STALE** | STALE | STALE | PASS | FAIL | CONFLICT |
| **PASS** | PASS | PASS | PASS | CONFLICT | CONFLICT |
| **FAIL** | FAIL | FAIL | CONFLICT | FAIL | CONFLICT |
| **CONFLICT** | CONFLICT | CONFLICT | CONFLICT | CONFLICT | CONFLICT |

EXHAUSTIVE over the 125 triples: commutative, associative, idempotent; `UNKNOWN` is the identity; `CONFLICT` is absorbing. EXHAUSTIVE over all sequences of length 1 to 6 over `{PASS, FAIL, STALE, UNKNOWN}` (5460 sequences): `fold_a` equals the kernel `aggregate_status` (the kernel's `assess_receipt` patched to return the given status), and folding any split point in two halves then joining equals the flat fold.

**Non-associativity of the kernel's rule under roll-up (HAND, reproduced by test; a hazard for reuse, the kernel does not roll up today).** Flat: `agg([PASS, FAIL, FAIL])` = `CONFLICT`. Rolled up through the kernel: `agg([agg([PASS, FAIL]), FAIL])` = `agg([CONFLICT, FAIL])`; the kernel does not recognise `CONFLICT` as an input status, so only `FAIL` is current and the result is `FAIL`. With `join_a`: `join_a(join_a(PASS, FAIL), FAIL) = join_a(CONFLICT, FAIL) = CONFLICT`. This lane implements and tests the algebra; changing the kernel needs its own ADR. The kernel's only caller folds a flat receipt list, and the unpatched `assess_receipt` cannot return `CONFLICT`, so the counterexample needs the patched assessment the test uses.

**Operator B, conjunction over distinct checks.** Carrier adds `NOT_RUN`. Default chain, worst first: `FAIL < CONFLICT < STALE < NOT_RUN < UNKNOWN < PASS`. `meet_b` is the chain minimum.

| claim slots | result (HAND) | why |
|---|---|---|
| PASS, STALE, PASS | STALE | one stale slot keeps the claim from PASS |
| PASS, NOT_RUN | NOT_RUN | NOT_RUN absorbs PASS |
| FAIL, NOT_RUN | FAIL | a known failure outranks a missing run in the default chain |
| UNKNOWN, STALE | STALE | the chain reports the worse of two non-PASS values |
| (no slots) | NOT_RUN | the empty conjunction would be PASS (the top); a gate that requires nothing has proved nothing |

EXHAUSTIVE: for every one of the 120 total orders of the five non-PASS values placed below `PASS`, `meet_b` is commutative and associative over all 216 triples, and a fold of 1 to 3 slots is `PASS` if and only if every slot is `PASS`. So the only owner decision that changes any verdict is where `PASS` sits (it must be on top); the order among the non-PASS values changes only which non-PASS word is printed (SYNTHESIS open question 1).

**Deviation from the formal aspect's reference (tested, section 10.3 of the design).** `graph/formal/eijaref/status.py` puts `NOT_RUN` at the bottom of its join (six-valued carrier) and returns `NOT_RUN` for the empty join. This oracle file keeps the kernel-exact join. On every value they share, both give the same table above; they differ only when `NOT_RUN` is fed to a join and on the empty join (`UNKNOWN` here, `NOT_RUN` there). The empty meet is `NOT_RUN` in both.

**Link status lift (DESIGN, from brief.json).** COVERED to PASS, SUSPECT to STALE, ORPHANED to FAIL, AMBIGUOUS to CONFLICT, UNRESOLVED to NOT_RUN. UNWANTED is a defect on the covering side, not a coverage status.

---

## O8. Counting statistics: what may be printed instead of a confidence percentage

All values are exact rationals or closed forms; no simulation.

### O8a. `pass^k` (repeat-trial reliability)

`pass_hat_k(n, c, k) = C(c,k) / C(n,k)`: the probability that `k` distinct trials drawn without replacement from `n` recorded trials with `c` passes are all passes.

**Input.** `n = 5`, `c = 3`. **Expected (HAND).** `k=1`: `3/5`; `k=2`: `C(3,2)/C(5,2) = 3/10`; `k=3`: `1/C(5,3) = 1/10`; `k=4`: `0`.

**Unbiasedness (HAND).** If the `n` trials are independent with pass probability `p`, then `E[C(c,k)/C(n,k)] = p^k`. Check for `n = 3`, `p = 1/2`, `k = 2`: `c` is Binomial(3, 1/2); `P(c=2) = 3/8` gives `C(2,2)/C(3,2) = 1/3`; `P(c=3) = 1/8` gives `C(3,2)/C(3,2) = 1`; `E = 3/8 * 1/3 + 1/8 * 1 = 1/8 + 1/8 = 1/4 = p^2`. EXHAUSTIVE in exact `Fraction`: `n = 2..6`, `p` in `{1/2, 1/3, 9/10}`, every `k`.

### O8b. Failure-free trials, and what "n passes" does and does not say

- One-sided 95% upper bound on the per-trial failure probability after `n` independent failure-free trials: `p* = 1 - 0.05^(1/n)`. `n = 5`: `1 - 0.05^0.2 = 0.4507`. `n = 100`: `0.02951` (the rule of three says `3/n = 0.03`, slightly conservative). `n = 300`: `0.00994`. Five green runs say almost nothing: the failure rate could still be 45%.
- A generator with failure-region mass `m` misses that region in `n` draws with probability `(1-m)^n`. `m = 1/1000`, `n = 1000`: `(0.999)^1000 = 0.3677`, so a thousand passing draws still miss a one-in-a-thousand region 37% of the time. If the generator gives the region mass 0 (a blind spot), the miss probability is exactly 1 for every `n`, and an agent that wrote both the code and the generator can share the blind spot.

### O8c. Three conventional "uninformative" priors, one dataset

Five successes, no failures. Posterior mean of the success probability under `Beta(a, a)`: uniform `a = 1`: `(5+1)/(5+2) = 6/7 = 0.857`; Jeffreys `a = 1/2`: `(5+1/2)/(5+1) = 11/12 = 0.917`; Haldane `a = 0`: `5/5 = 1`. The implied failure probabilities are `1/7`, `1/12` and `0`: the "confidence" is the prior. Subjective-logic projection with `W = 2` and base rate `1/2` (`alpha = r + aW = 6`, `beta = s + (1-a)W = 1`) gives `6/7`, the uniform-prior value: `b + a*u = 5/7 + (1/2)(2/7) = 6/7`.

### O8d. Why conjunction bounds collapse (Frechet, no independence assumption)

`P(A1 and ... and An) >= max(0, sum P(Ai) - (n-1))`. `n = 20`, each `0.99`: `20 * 0.99 - 19 = 0.8` exactly (`4/5`); independence would say `0.99^20 = 0.8179`. `n = 200`: the bound is `0` while independence says `0.99^200 = 0.134`. So a numeric confidence for a big claim is either unjustified (independence) or vacuous (Frechet), and every leaf number is itself an unmeasured input.

---

## O9. Change-risk vector: a partial order with a canonical linear extension

**Fields (integers, in priority order).** `protected_paths_touched`, `pinned_statements_changed`, `impacted_obligations_without_observer`, `suspect_links`, `tier0_size`, `tier1_size`, `tier2_size`, `changed_nodes`. `a` dominates `b` when every field of `a` is at least that of `b` and one is larger. The review order is the lexicographic order on the field tuple, larger first; it never places a dominated change above the change that dominates it.

**Input.** `X = (0,0,2,3,1,4,3,1)`, `Y = (0,0,0,5,1,10,20,1)`, `Z = (0,0,2,2,1,4,3,1)`.

**Derivation (HAND).** `X` versus `Y`: `X` is larger in field 3 (2 > 0), `Y` larger in fields 4, 6, 7, so neither dominates: the order is partial and no total order is implied. `X` versus `Z`: equal except field 4 (3 > 2), so `X` dominates `Z`. Lexicographic order: `X` (0,0,2,...) beats `Y` (0,0,0,...) at field 3, and `Z` (0,0,2,2,...) beats `Y` at field 3 and loses to `X` at field 4. Expected review order `X, Z, Y`: the change that leaves two impacted obligations with no observing test outranks the change that merely reaches more nodes. SEEDED (2000 random pairs): `dominates(a, b)` implies `key(a) > key(b)`.

---

## O10. Integration checks against sibling aspects (tests only, no new definitions)

These are differential tests. They pass when the sibling file exists and skip as NOT_RUN when it does not.

| Check | Sibling artefact | What must hold |
|---|---|---|
| Closure certificate | `graph/formal/eijaref/closure.py` | For 200 seeded graphs, the closure's `(distance, parent)` maps are accepted by `check_certificate`; the closure equals its naive Kleene iteration and its Warshall closure; `check_unreachable` accepts every unaffected node; a forged parent is rejected |
| SCC and order | `graph/formal/eijaref/order.py` | Labels equal `scc_labels` and pass `check_scc_labels`; the lexicographic topological order of the condensation equals `lexicographic_topological_order` and passes its checker |
| Status | `graph/formal/eijaref/status.py` | Same join on the five kernel values, same chain, same `LIFT`, same meet, `PASS` iff all `PASS` for all 120 chains; the two documented deviations are asserted so that drift in either file fails |
| Flow from the metamodel | `graph/schema/metamodel.json` | `flow_from_metamodel(affects, anchor_ends)` covers every anchored end for every link kind; `affects` values outside `to_source, to_target, both, none` raise |

---

## O11. Changeset overlap: pre-merge conflict prediction between two agents

**Definitions.** For change sets `A` and `B`: `direct` = nodes both edit; `a_reaches_b` = nodes `B` edits that `A`'s change reaches, with the tier of that reach; `b_reaches_a` likewise; `shared` = nodes both changes reach, at tier `max(tier_a, tier_b)`, the weakest soundness class needed for both to touch the node. Tier 0 means over `must` arcs only.

**Input.** The links of O1.

**Case 1, `A = {S1}`, `B = {S4}` (HAND).** `Impact(B, 2)` follows `S4 <-> R2` and `R2 <-> T2` (class 0) and finds no outgoing may or heuristic arc from `S4` (the `calls` arc `S3 -> S4` points into `S4`), so it is `{S4, R2, T2}`. `A` reaches `S4` only through the heuristic `calls` link (O1: tier 2). Expected `direct = []`, `a_reaches_b = {S4: 2}`, `b_reaches_a = {}`, `shared = {R2: 2, S4: 2, T2: 2}`. Reading: a possible collision that exists only through a heuristic edge; the report says which edge class it rests on.

**Case 2, `A = {S2}`, `B = {R1}` (HAND).** `S2 satisfies R1` gives arcs both ways at class 0, so each side's change reaches the other side's edited node at tier 0: `a_reaches_b = {R1: 0}`, `b_reaches_a = {S2: 0}`. `shared` adds what both reach through the may arcs: `S1` and `S3` at tier 1, `T1` at tier 0 (via `R1`), and `S4`, `R2`, `T2` at tier 2, plus the two edited nodes at tier 0. Reading: a certain interaction over encoded sound arcs.

**Property checks.** SEEDED (120 random typed graphs): the result is symmetric under swapping `A` and `B`, `shared` is exactly the intersection of the two tiered impact sets and its tier is the maximum of the two.

**Not shown.** That two changes which overlap in the encoded graph conflict in behaviour, or that changes with no overlap are safe: the graph has only the encoded arcs. The consistency aspect's post-merge check (findings of the merged tree minus the union of the sides' findings) catches what actually emerged; this prediction is the cheap, earlier signal.

---

## Coverage of this file

| Oracle | Design section | Test module names in `test_impact_math_oracles.py` |
|---|---|---|
| O1 | 2, 3 | `test_o1_*`, `test_closure_*`, `test_witness_*` |
| O2 | 4 | `test_o2_*`, `test_scc_*`, `test_lexicographic_*` |
| O3 | 5 | `test_o3_*`, `test_ppr_*`, `test_choose_iterations_*` |
| O4 | 6 | `test_o4_*`, `test_context_selection_*` |
| O5 | 7 | `test_o5_*`, `test_greedy_cover_*` |
| O6 | 8 | `test_o6_*`, `test_vertex_connectivity_*` |
| O7 | 10 | `test_o7_*` |
| O8 | 11 | `test_o8_*` |
| O9 | 9 | `test_o9_*`, `test_risk_key_*` |
| O11 | 3.1 | `test_o11_*`, `test_changeset_overlap_*` |
| O10 | 2, 10.3, 13 | `test_closure_result_is_a_certificate_*`, `test_scc_labels_and_topological_order_*`, `test_status_algebra_agrees_*`, `test_flow_derived_from_the_metamodel_*` |
