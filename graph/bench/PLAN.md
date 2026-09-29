# Benchmark plan: storage and query (aspect storage-query)

Lane: weave. Date: 2026-09-29 (revised after audit). Decision record: [ADR-0091](../../docs/adr/0091-weave-storage-query.md). Design and prior measurements: [storage-and-query.md](../../docs/weave/design/storage-and-query.md).
Labels: MEASUREMENT (ran, result file named), PREDICTION (pre-registered, not run), NOT_RUN (prerequisite missing or deliberately deferred; never a pass).

## 0. Ground rules

1. **Correctness before timing.** Every engine's answer is compared with the reference (`impact.closure` semantics, or the seeded expected set) before its time is recorded. A mismatch is a defect, not a data point.
2. **Deterministic block and timing block are separate.** Counts, hashes and booleans go in `deterministic` and must be byte-identical across runs (checked by hash); wall-clock goes in `timing` and is never compared byte-for-byte. Example: `storage_query_probe.py` prints `deterministic_sha256`.
3. **Report the environment**: OS, Python, SQLite version, engine versions, CPU count, RAM, disk type of the scratch directory, whether other agents were running. One machine is one sample, not a distribution.
4. **Repeat and report spread.** At least 5 repetitions after 1 warm-up; report median, minimum and maximum. The runs so far used medians of 3 (2 at 10^6) and are labelled accordingly.
5. **Resource safety on the shared 16 GB PC (owner and coordinator rule).** Run serially, one engine at a time. Scratch under `.tmp/` only, with `TMP` and `TEMP` set. Every engine that has a memory setting gets an explicit cap of at most 256 MB and an in-process or wrapper RSS watchdog that aborts the process above 500 MB (see `ladybug_probe.py`, which refuses larger limits). Start at 100 edges and grow by 10 times only while the previous size peaked under 40% of the limit. Nothing above 2,000 edges for a graph engine, and nothing above 10^6 edges for SQLite or DuckDB, runs on the shared PC. **Larger or uncapped runs belong to a dedicated build stage on a machine with nothing else running.** Prefer cited documentation over running heavy engines at design time.
6. **Pre-registration.** Thresholds below were written before the runs they govern. A threshold is changed only by a dated edit that names the reason; the old value stays visible.

## 1. What has already been measured (MEASUREMENT, this session)

Scripts: `storage_query_probe.py` (stdlib; DuckDB optional; modes: default, `--skip-timing`, `--python-baseline`), `ladybug_probe.py` (capped, watchdog). Results: `results/storage-query-probe.json` (final full run; `timing_script_sha256` is the script that produced the timing block, `script_sha256` and the deterministic block were regenerated after the audit), `results/python-baseline-and-wide-ddl.json` (pure-Python head-to-head and specified-DDL width), `results/storage-query-probe-run-b-timing.json` (an earlier full run, kept as a second sample), `results/ladybug-capped-probe-{100,1000,2000}-edges.json`. Older: `bench_closure_engines.py`, `foundations_checks.py`, `traceability_staleness.py`.

| Quantity (final run; earlier run B in brackets where recorded) | Result | Where |
|---|---|---|
| Closure, 10^4 / 10^5 / 10^6 edges, SQLite CTE, text ids (s) | 0.020 / 0.158 / 2.5 (0.028 / 0.163 / 3.57) | design section 2.1 |
| Same, integer-interned ids (s) | 0.008 / 0.098 / 1.1 (0.006 / 0.090 / 1.69) | same |
| Stratified violation (recursion then negation) (s) | 0.022 / 0.18 / 3.8 (0.013 / 0.23 / 4.43) | same |
| Anti-join violation (s) | 0.0006 / 0.006 / 0.067 | same |
| Canonical dump plus root hash (s) | 0.069 / 0.89 / 8.5 (0.095 / 1.01 / 10.8) | same |
| File build, default pragmas vs journal and sync off, 10^4 / 10^5 / 10^6 (s) | 0.67 vs 0.05 / 0.80 vs 0.54 / 9.6 vs 5.7 (0.12 vs 0.08 / 0.87 vs 0.71 / 12.5 vs 10.8) | same |
| Observed run-to-run spread, same machine | query timings up to 1.7 times (closure up to 1.4); in-memory build 2 to 4 times; default-pragma file build 5.4 times (10^4); p99 6.6 times (10^5) | design section 2.1 |
| SQLite file hashes over 5 insertion orders / dump hashes | 5 / 1 | design section 2.2 |
| Witness vs brute-force oracle | 0 mismatches in 600 graphs, 3,373 paths | design section 2.3 |
| Unbounded SQL closure vs kernel closure; budgeted Python closure under shuffled insertion order | 0 mismatches in 300 graphs each (195 truncated by budget); SQL `LIMIT` differed from the kernel's truncated set in 33 of 300 (SQLite 3.49.1, outside the hash) | design section 2.2 |
| Pure Python vs SQLite, 10^4 / 10^5 / 10^6 (closure s; stratified violation s) | Python 0.0034 / 0.054 / 0.75; 0.0039 / 0.081 / 0.75 against SQL 0.020 / 0.158 / 2.5; 0.022 / 0.18 / 3.8; answers equal | design section 2.1b |
| Specified DDL width (5 node, 7 edge columns), 10^4 / 10^5 / 10^6 | file 2.8 / 28.9 / 299.5 MB; build 0.08 / 1.65 / 20.2 s; dump plus root hash 0.147 / 1.34 / 12.6 s | design section 2.1c |
| Ladybug default, 10^4 edges | ANECDOTE, not evidence: 8.4 GB resident reported by the coordinator, unrecorded and not reproducible | design section 2.4 |
| Ladybug 0.20.4 capped (128 MB pool, 500 MB RSS watchdog), 1,000 and 2,000 edges (0.21.0 published 2026-09-28, not re-run) | default pattern bound 30: buffer pool exhausted, clean failure (165 to 169 MB peak RSS = 50 MB baseline plus the pool); bound 3: silently incomplete; exact bound: correct, 0.60 s at 2,000 edges; `SHORTEST`: correct, 8 to 24 ms, 50 MB | same |
| Size of this repository (okf worktree, head `cdc4f37321de`) | 465 defs, 276 imports, 1,141 md links, 687 `repo://` | design section 2.1 |
| Extrapolation to 10^7 edges | closure 40 to 78 s, root hash 85 to 108 s narrow, 126 s wide (PREDICTION, arithmetic in design section 2.1a; cause of slope above 1 unmeasured) | same |

## 2. Hypotheses, thresholds and falsifiers

Each row: claim, metric, PREDICTION threshold (pre-registered), and what would falsify the design decision.

| ID | Hypothesis | Metric and method | Threshold | If falsified |
|---|---|---|---|---|
| H1 | At the real graph size (built once P1 extractors exist), SQLite answers every catalogue query fast enough for interactive use | p50 and p99 of each named query over 1,000 random arguments; real graph plus a 10 times synthetic scale-up | p99 at most 100 ms for `node`, `neighbors`, `why`; at most 1 s for `impact` with budget 5,000; at most 2 s for any `violations` rule | Add integer interning; then DuckDB for scans; only then reconsider an engine (ADR-0091 revisit trigger) |
| H2 | Full rebuild fits a budget for the reference PC | Wall-clock of extract, load, dump, root hash, from a clean checkout, 5 runs | at most 5 s at the real size (DESIGN budget, owner may change); cache stays off while this holds | Enable the verifying-trace cache (ADR-0100) and re-measure |
| H3 | Root hash cost stays under the budget until a Merkle partition is needed | Same dump at 10^4, 10^5, 10^6 | at most 0.2 s at 10^4; if over 2 s at the real size, partition by view | Implement per-view roots |
| H4 | The store is deterministic under permutation | Permutation harness (ADR-0099): file order, rule order, hash seed, TZ, `LC_ALL`, CWD, CRLF, threads, non-BMP paths; root hash and SARIF bytes | 1 distinct output over at least 200 permutations; POSIX golden equal (NOT_RUN until a Linux or WSL run exists) | Any second output is a release blocker |
| H5 | Incremental rebuild equals clean rebuild | Random edit sequences (Hypothesis strategies from the property lane), 200 sequences of up to 20 edits | 0 differences | Cache stays off; fix or delete |
| H6 | Every catalogue query result is byte-stable for a fixed root | Run each query 20 times across processes with different hash seeds | 1 distinct output per query and argument set | Fix ordering; lint gap |
| H7a | Unbounded SQL closure (recursive CTE over the node column) equals `impact.closure` as a set | 300 random graphs with cycles, oracle from `src/eija_studio/domain/impact.py` (test-only import); probe result: 0 mismatches. To repeat over `eijagraph.store` output | 0 mismatches | Defect in `eijagraph.store` |
| H7b | Budgeted closure (affected set, `complete`, `frontier`) is computed by the Python BFS, equals `impact.closure`, and is unchanged when edge insertion order is shuffled | 300 random graphs with cycles and random budgets, including truncated cases (probe: 195 truncated, 0 mismatches vs the kernel copy and under shuffle); repeat over `eijagraph.store` output with the real kernel import | 0 mismatches; at least 100 truncated cases | Defect in the BFS or the store. Do NOT move budgets into SQL: a SQL `LIMIT` differed in 33 of 300 |
| H8 | Witness re-check recovers the fact, and deleting any witness edge removes it (minimality) | Every finding in the fixture and real graph; closure on the witness subgraph alone | 100% recovered; 100% of single-edge deletions remove the fact | Fix witness code |
| H9 | An embedded graph engine offers a benefit worth its operational cost | Ladybug (or its successor) with caps of 256 MB and 1 thread on the export of the real graph; same catalogue queries expressed in Cypher, reachability in the `* SHORTEST 1..N` form with N at least the longest chain | Peak RSS at most 256 MB at 10^5 edges, results equal SQLite for all queries, and at least 3 times faster than SQLite on some query class the rules need. All three must hold. | Stay an export target only (current position). NOT_RUN above 2,000 edges (rule in section 0.5); at 2,000 edges the peak was 50 MB and `SHORTEST` matched the reference, which says nothing about 10^5. |
| H10 | The Neo4j export loads and reproduces the reference closure | Owner-run only: `load.cypher` into Community edition with a stated heap cap; closure of 5 roots with an exact bound; compare with SQLite | Result set equal; row order documented as undefined without `ORDER BY` | Fix exporter; NOT_RUN in this session (no Neo4j, deliberately) |
| H11 | Integer interning is safe | Root hash and every query result identical with interning on and off, 200 permutations | 0 differences; speedup at least 1.5 times at 10^6 (measured 2.1 times for closure) | Do not ship interning |
| H12 | Named queries beat free-form query text for agent reliability | See section 3 | See section 3 | Agent surface keeps named queries regardless (determinism reason), but the reliability claim is withdrawn |
| H13 | The scale curve stays inside budget up to the revisit trigger | Closure of 5 roots, anti-join, stratified violation and root hash at 10^4, 10^5, 10^6 edges on the reference PC; slope s = log10(t at 10^6 / t at 10^5); 5 runs each | Closure at most 10 s and root hash at most 30 s at 10^6; slope at most 1.4 (measured 1.2 and 1.34 in two runs). Predicted breach of the closure budget at 10^7 (40 to 78 s), which is the stated trigger | Above budget at 10^6: add integer interning (measured 1.6 to 2.2 times), then Merkle partition of the root hash, then DuckDB for scans; only then reconsider an engine |
| H15 | The index file cannot be stale: its key covers the root, the rule-set hash, the schema version, the engine version and the extractor pins | Key function test: change exactly one input at a time with the same graph, expect a different key and recomputed findings; change nothing, expect the same key and a no-op rebuild; open a file whose `meta` disagrees with its name, expect refusal | 100% of single-input changes change the key; 0 stale reuses | Defect in the key; NOT_RUN until `eijagraph.store` exists |
| H16 | SQL rule files give a real authoring or inspection benefit over Python rules (the reason SQLite is chosen over plain Python, since Python was measured 3 to 10 times faster) | With the rule-language aspect and the hci lane: the same 10 rules written as SQL and as Python by different authors (human or agent), then reviewed by second reviewers who must state what each rule flags; measure authoring errors caught by the loader lint, review time and disagreement rate | Pre-register at the time of the run; no threshold is claimed today | Fall back to Python rules over the same files, SQLite kept as the exploration export. NOT_RUN; the benefit is a DESIGN judgement |
| H14 | Recursive rule text is reproducibly terminating | Lint plus the W2 workload: every recursive rule selects only the node column with `UNION`; a rule that carries a path or depth column must be rejected by the loader (measured: such a form ran to the 1,000-row guard on a 3-node cycle) | 0 accepted rules with extra recursive columns; 100% of seeded bad rules rejected | Loader defect |

## 3. Agent and human evaluation of the query interface (NOT_RUN; design only)

The claim "agents do better with named queries than with free-form SQL or Cypher" has no evidence today (design section 5.2). It is measured by the eval lane, not asserted.

| Item | Design |
|---|---|
| Tasks | 40 pre-registered questions over a frozen fixture graph of the real repository at a fixed root hash: 10 impact, 10 coverage and missing-evidence, 10 suspect-link and why, 10 cross-type joins (for example "which acceptance rows are verified only by tests that cover no changed symbol"). Ground truth by hand-written reference SQL, reviewed by a second person or agent, results stored in the repo. |
| Arms | (a) named queries only; (b) free-form SQL with the schema in the prompt; (c) free-form Cypher against an exported Ladybug or Neo4j instance with the schema in the prompt. Same model and CLI version per arm; record model id, CLI version and date. |
| Trials | n = 8 runs per task per arm at temperature settings the CLI allows; record and replay transcripts by hash so replays are deterministic (agents lane harness). |
| Metrics | Exact set equality of the returned ids with ground truth; execution error rate; count of identifiers not present in the graph (hallucinations); tool calls; tokens; pass^k with k = 1, 4, 8 defined as the mean over tasks of C(c, k) / C(n, k) where c of n runs passed. Report n and c, not only the ratio. |
| Analysis | Report raw counts per arm per task class. Arithmetic for what 40 tasks can resolve, two independent arms, task as the unit, pass rate near 0.5: standard error of the difference sqrt(2 x 0.25 / 40) = 0.112, so 80% power at a two-sided 5% level needs a true difference of about (1.96 + 0.84) x 0.112 = 0.31, i.e. 31 percentage points. To resolve 0.6 against 0.8 needs n = ((1.96 sqrt(2 x 0.7 x 0.3) + 0.84 sqrt(0.6 x 0.4 + 0.8 x 0.2)) / 0.2)^2 = ((1.270 + 0.531) / 0.2)^2 = 81.1, so 82 tasks per arm. A paired analysis on the same tasks should do better and is not costed here. Repeats within a task do not add independent tasks; they measure consistency (pass^k). Failures are read and classified (wrong join, wrong filter, ordering, hallucinated id, timeout). |
| Labels | Results are MEASUREMENT for that model, CLI, fixture and date; anything else is PREDICTION. |
| Human arm | With the hci lane: reviewers answer 10 of the same questions using (a) CLI plus OKF pages, (b) SQLite browser, (c) none of the graph (grep and reading). Time and correctness, at least 5 participants; whether such participants are available is an owner question, so this is NOT_RUN and the human benefit stays UNMEASURED. |

## 4. Engine matrix and how each is run

| Engine | Role in the bench | Run on the shared PC? | Cap and guard |
|---|---|---|---|
| SQLite (stdlib) | Baseline and chosen store | Yes, serially, up to 10^6 edges | scratch in `.tmp`, journal off |
| DuckDB | Analytics comparator | Yes, up to 10^6 edges (0.63 s load measured) | `SET memory_limit` (name UNVERIFIED, check docs before use) or process RSS watchdog |
| Ladybug | Export target check | Only capped, at most 2,000 edges (enforced by the probe, which refuses larger values and has no RSS probe fallback: on an unsupported platform it reports NOT_RUN) | `buffer_pool_size` at most 256 MB (default 128), `max_num_threads` 1, `max_db_size` 1 GB, in-process watchdog abort at 500 MB, each query variant in its own child with a wall-clock limit, the `SHORTEST` form for reachability |
| Neo4j Community | Export check | No. Owner-run on a machine chosen by the owner | Explicit heap and page-cache limits per its operations manual (not read this session); documented in the export README |
| Soufflé | Datalog differential oracle | No (Windows not supported per install page); Linux, macOS or WSL in the dedicated stage | timeout |
| networkx, rustworkx | Test oracles for closure and SCC | Yes, small graphs only (networkx import costs 1.4 to 4 s) | pin networkx below 3.7 |

## 5. Workloads

| Workload | Purpose | Generator |
|---|---|---|
| W1 synthetic typed graph | Scaling curves | `make_graph(n_edges, seed=11)`; symbols 20%, requirements 5%, tests 10% of the edge count; 2% back edges in `depends_on`; 8% of requirements without `verifies` |
| W2 adversarial cycles | Termination and witness stress | Dense strongly connected components, self-loops removed, long chains; also a graph where `UNION` with a carried column would not terminate |
| W3 real graph | The only workload that supports a claim about EIJA | Built from the repository by the P1 extractors at a recorded commit; frozen as a fixture with its root hash |
| W4 OKF-rich | Projection independence | W3 plus all generated OKF blocks; root hash must equal W3 without them |
| W5 Unicode | Order and identity | Ids with BMP, astral, combining and mixed-case characters; CRLF and LF checkouts of the same content |
| W6 rename storm | Rename maps | 10% of ids renamed via explicit records; graph equality modulo the map |

## 6. Procedure and reporting

1. `python graph/bench/storage_query_probe.py --skip-timing` twice; the two `deterministic_sha256` values must be equal (done: equal in this session).
2. Timing run per size, serial; results written to `graph/bench/results/<name>.json` with the environment block; the deterministic sub-block hash recorded in the design doc.
3. Regenerate the tables in the design doc by script from the result files, not by hand (to do when the bench moves under `tests/graph/`).
4. A benchmark result never changes a decision by itself; the ADR names the trigger, and a change is a new ADR that supersedes 0091.

## 7. Known limitations of the current bench (be aware when reading the numbers)

* Synthetic graph, one machine, shared with other agents, scratch on a slow HDD; the memory build was slower than the file build at 10^5 (1.14 s against 0.87 s), which is noise, not a finding.
* Only Windows 11 and Python 3.12.10 with SQLite 3.49.1. No POSIX, no macOS, no older SQLite.
* `sizing` counts come from the okf worktree at the time of the run and change as that lane commits; the count (not the timing) is the reproducible part, and the result file records the counts of the run.
* The Ladybug 8.4 GB figure is an anecdote reported by the coordinator; the run that produced it was killed, is in no result file and is not reproducible from the repository, so no conclusion rests on it. The capped reruns cover graphs of at most 2,000 edges and Ladybug 0.20.4 only (0.21.0, uploaded 2026-09-28T23:25Z, was not re-run). Before the caps existed the author of this plan also ran an uncapped earlier version of the probe (2,000 and 10,000 edges, no memory instrumentation); see design section 2.4, Disclosure. That was outside the rule in section 0.5 and is not repeated.
* `timing_script_sha256` in the result file is the hash of `storage_query_probe.py` when the timing block was produced. The script was edited afterwards: `TMP`/`TEMP` moved into `main()`, and (audit revision) `budgeted_closure_checks`, `kernel_closure`, `--python-baseline`, `python_baseline` and `wide_ddl` were added. No previously measured code changed. The deterministic block and `script_sha256` were regenerated with the current script; the timing block was not re-run. `python-baseline-and-wide-ddl.json` carries the hash of the current script.
* The main timing tables use 3 and 4 column tables; the specified DDL is 5 and 7 columns. Only size, build, dump and closure were re-measured at the specified width (design 2.1c), one run per size.
* The pure-Python baseline excludes file reading and peak memory, so it is an upper bound on Python's advantage for this graph shape. It is synthetic.
* Run-to-run spread on this machine is large (section 1), and the file builds are dominated by fsync on an HDD. The two full timing runs on record are the whole sample; a threshold change needs the 5-repetition protocol of section 0.4.
* The DuckDB memory limit setting name is UNVERIFIED and must be read from its documentation before use.
