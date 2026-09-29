# Compiler and lint rules for the weave graph

Lane weave, aspect `lint-compile-rules`. Date 2026-09-29. Status: DESIGN feeding [ADR-0095](../../adr/0095-weave-lint-compile-rules.md); nothing is implemented in `eijagraph`. What exists and runs today: the catalogue [graph/rules/catalogue.json](../../../graph/rules/catalogue.json), its validator, the reference semantics [graph/rules/reference.py](../../../graph/rules/reference.py), the schema [graph/schema/rules.md](../../../graph/schema/rules.md), one benchmark and their tests. Labels: **MEASUREMENT** (a script ran, domain stated), **PREDICTION** (reasoned, not run), **DESIGN** (proposal of this lane), **UNVERIFIED** (not confirmed, nothing is built on it).

Source keys. Dossiers in [../research/](../research/) (keys as in [SYNTHESIS.md](../research/SYNTHESIS.md)): [gdb] [math] [trace] [lang] [ui] [bx] [assure] [incr] [agent] [code] [mde]. Sources I opened on 2026-09-29: [S1] OASIS SARIF 2.1.0 Errata 01 full text, read raw (docs.oasis-open.org); [S2] OASIS `sarif-schema-2.1.0.json` (raw.githubusercontent.com, `oasis-tcs/sarif-spec`); [S3] SQLite `WITH` clause documentation (sqlite.org/lang_with.html), read raw; [S4] W3C SHACL Recommendation, Soufflé "rules" and "install" pages, ruff `TID251` and FAQ pages, import-linter contract types, Semgrep rule-testing docs, rustc dev guide diagnostics (all via the fetch tool, so summaries; quoted phrases are as returned); [S5] PyPI JSON for pyshacl, rdflib, jsonschema, ruff, import-linter, cosmic-ray and GitHub API metadata for pySHACL, Soufflé, ruff, import-linter, Semgrep, ast-grep, cosmic-ray; [S6] `45ck/proofmap-lite` `docs/gap-audit.md` (private, read with the owner's `gh` login); [S7] sibling files: quality ADR-0035 and `quality/sessions/quality.py`, okf ADR-0045 and ADR-0046, mutation ADR-0033, and `graph/schema/metamodel.json` with `build_schemas.py` from the metamodel aspect in this worktree. My runs: [B1] `graph/bench/rule_language_bench.py` (results in `graph/bench/results/rule-language.json`), [B2] `python graph/rules/check_catalogue.py --stats`, [B3] `tests/graph/test_rules_*.py` and `test_rule_language_bench.py`, [B4] ruff probes, run on the local 0.15.7 and re-run on the quality lane's pin 0.16.9 (installed under `.tmp/`; identical results on both), [B5] validation of the SARIF example against [S2] (jsonschema 4.25.1 first, re-run under the pinned 4.26.0 with the same result), [B6] the audit-driven checks: `test_polarity_claim_over_all_small_worlds` and the validator's duplicate-parameter, negation and promotion-gate checks.

## 0. Decisions first

| # | Decision | Basis |
|---|---|---|
| 1 | The compiler is a seven-stage pipeline (extract, canonicalise and type-check, derive, check, diagnose, propose fixes, project). Rules in the **compile class** (14) check the well-formedness of the graph itself; a failure marks the run `malformed` and blocks every projection (OKF sync, diagram regeneration, exports). Lint-class rules (83) never block projections. | section 1; a stale OKF page must stay regenerable, so SUSPECT links are lint, not compile |
| 2 | **Rule language: SQL violation queries** for relational graph-global rules (64 of 97), **Python** for file-local rules and graph algorithms (31), **generated templates** from the metamodel for cardinality and acyclicity (15, counted in the SQL or Python totals by their implementation), and **tool-backed** rules (2). Datalog, SHACL and Cypher are export targets and optional cross-checks, not runtime. | [B1]: four engines return identical results on four rules at every size run; pySHACL takes 140.6 s for one rule at 2,000 nodes; Soufflé documents no Windows install; SQLite authorizer enforces declared reads |
| 3 | Every rule declares the relations it reads with polarity; the loader **enforces** the declaration and **computes** the stratum. There is no negation inside a recursive stratum. Closed-world guard by polarity: a finding that is monotone in an incomplete relation is real (FAIL stands, silence is NOT_RUN); a rule that reads an incomplete relation negatively, or through a derived relation, reports NOT_RUN whatever it found, because its findings can be artefacts of the missing facts. | [S3], [B1] authorizer probe, `reference.read_effect` and `rule_verdict`, [B6] |
| 4 | **Verdicts are PASS, FAIL, NOT_RUN**, folded by the chain minimum `FAIL < NOT_RUN < PASS`. NOT_RUN absorbs PASS and never absorbs FAIL. | exhaustive law tests [B3] |
| 5 | **97 rules in 12 categories**, all `proposed`, each with a stable id, one message per distinct situation, a witness kind, a fixture matrix and an ADR-lite entry. One defect has exactly one rule: three ideas from the brief were merged into others (WV-021, 030, 035, ids retired) and one was generalised (WV-022, now the acyclicity template); WV-031 and WV-063 are distinct defects (a transition with no UI control, a transition with no code) and are separated by the template parameter `peer`, and the validator rejects any two template rules with identical parameters. | [B2]; section 3 |
| 6 | **Diagnostics are SARIF 2.1.0** in a determinism profile. Finding identity is `eija.finding.v1`, a domain-separated, length-prefixed SHA-256 over rule id, subject ids and identity arguments (no line, no text, no time). The canonical file carries no baseline state; the baseline comparison is a separate view. | [S1] F.2 to F.7, 3.27.16; example validated against [S2] [B5] |
| 7 | **Suppressions expire without a clock**: by ledger sequence, release tag, subject digest, or an explicit `--as-of` input; an unevaluable expiry fails closed. No inline pragmas. Baselines may shrink, never grow. Severity, maturity and exemptions are protected policy. | [S6] GAP-017; quality-lane ratchet; WV-045, 046, 091, 098 |
| 8 | **Incremental evaluation is opt-in** and never a semantics: per-rule key over relation-slice hashes, early cutoff on unchanged output, `incremental == clean` as the oracle. A body edit of one Python function dirties 21 of 97 rules; a comment-only edit dirties none. Whole-catalogue evaluation is estimated from four stand-in rules at about 0.25 s at 10^3 nodes and 4.6 s at 10^4 (an estimate, not a bound: Python graph algorithms and template `GROUP BY` rules over real views were not timed). | [B2], [B1]; PREDICTION for wall time |
| 9 | **Fixes are proposals**: byte-range edits with `applicability` and a `precondition_sha256`; 14 rules carry one (4 machine-applicable). Clearing a SUSPECT link is never a fix: it is a human ledger act. | [S4] rustc applicability; ADR-0094 boundary |
| 10 | **Every rule is tested by a fire/repair/benign matrix** (389 minimum cases), golden SARIF, a polarity property test, the permutation harness, and rule-source mutation by the mutation lane's engine. | section 9 |
| 11 | **Governance**: adding a rule needs a catalogue entry, fixtures, a golden and an ADR-lite line in `decisions.jsonl`; `enforced` needs an owner ledger entry. A full ADR is needed only for a new relation, node or link type, extractor, dependency, kernel change or stage contract. Today 94 of the 97 ADR-lite entries are declared stubs (`alternatives_checked` false); a promotion gate in the validator refuses to promote a rule with a stub entry. | section 10 |
| 12 | **No benefit to agents or humans is claimed**; the design gives them structured arguments, a witness and a reproducible query, and the effect stays a PREDICTION until the hci and eval lanes measure it. | section 11 |

## 1. The pipeline

### 1.1 Stages as compiler phases

| Compiler phase | Stage | Input to output | Determinism contract | Failure and rule class | Reused |
|---|---|---|---|---|---|
| Lexing and parsing | S1 extract | source tree (sorted repo-relative POSIX paths, UTF-8, CRLF folded to LF) to `FactBatch` per file, sorted, provenance-labelled | per-file cache key is SHA-256 of content and extractor pin; a partial parse is labelled partial (D-14) | WV-006 (NOT_RUN), WV-009 (syntax error is `error`; tree-sitter recovery is NOT_RUN) | stdlib `ast`, `json`, `html.parser`; `markdown-it-py` (okf pin); tree-sitter and LibCST in phase 3 |
| Name resolution | S2 canonicalise | facts, declared links and ledger to the canonical typed graph; every link resolves to a node or gets status ORPHANED or AMBIGUOUS | RFC 8785 subset, sorted; Merkle root per view | compile class: WV-001, 003, 004, 008 | okf `repo://` grammar |
| Type checking | S2 | edge signatures, cardinality maxima, acyclicity, hash-method policy, canonical form of committed artefacts | signatures generated from `graph/schema/metamodel.json` | compile class: WV-002, 047, 055, 022, 043, 044, 082, 084 | jsonschema for sidecars |
| Semantic analysis | S3 derive | `link_status`, impact closure, SCCs, `component_of`, `component_edge`, `exposed_transition`, `live_motivated`, `evidence_verdict` | least fixed points; strata in order; SCC labels by minimum member | none: derivation emits no findings | `impact.closure` as test oracle |
| Lint | S4 check | rules by stratum 0 to 3 to findings and per-rule verdicts | every SQL result ends in a total `ORDER BY`; findings sorted | lint class (83 rules) | stdlib `sqlite3` |
| Diagnostics | S5 diagnose | findings, suppressions, baseline to SARIF and views | profile `eija-sarif/v1` | WV-090 checks the output | own writer (sarif-om is stale since 2019 [incr]) |
| Fix-its | S6 propose | findings to edit proposals | precondition hashes; disjoint sorted edits | none | LibCST (phase 3), byte-range edits |
| Code generation | S7 project (get-only) | OKF pages, diagrams, exports | byte-equal to a fresh run (WV-065) | blocked when the run is `malformed` | okf and visual lanes |

The analogy stops at one point: a compiler stops at the first phase that fails. This pipeline keeps evaluating every rule so a person or an agent sees all findings at once; only stage S7 is gated.

### 1.2 Run header and exit codes

A run's inputs are explicit and recorded, never ambient: tree identity (git tree hash, or the Merkle root of the working tree), baseline ref, `--as-of` (optional), tier, extractor pins, catalogue digest, profile id. Nothing reads the wall clock, the locale, the time zone or the environment (D-04, D-08). Exit codes: 0 PASS, 1 FAIL, 2 NOT_RUN unless accepted, 3 internal error (a rule that raises reports NOT_RUN with a notification and the run exits 3). The NOT_RUN policy is the quality lane's: its `audit` session fails with a NOT_RUN message unless `EIJA_ALLOW_NOT_RUN=1` records the gap as accepted [S7].

### 1.3 Tiers

| Tier | Contents | Rules | Runs |
|---|---|---|---|
| `fast` | stdlib Python only, static facts | 83 | every save and commit (quality ADR-0036 adapts noslop hooks to nox) |
| `full` | harness, second process, generators, browser (one, serial) | 13 | before a PR |
| `release` | double clean rebuild, POSIX golden compare | 1 (WV-087) | release |

### 1.4 Compile-class failures and projections

The run continues after a compile-class failure: every rule still evaluates, so a person or an agent sees all findings. But if any compile-class rule is FAIL or NOT_RUN the run is `malformed`: the Merkle root is still computed and printed, it cannot be written to `graph/manifest.json`, and stage S7 refuses to regenerate OKF pages, diagrams or exports and prints the compile findings instead. Reason: a projection of a graph with dangling ids or ill-typed links bakes the defect into generated files, the failure class ProofMap Lite recorded when generated artefacts drifted or were trusted stale (GAP-025 [S6]; GAP-002 and GAP-003 as summarised in [gdb]). Lint-class findings never block S7: a SUSPECT link (WV-005) exists because code changed, and the OKF sync that re-baselines the page must still be able to run.

## 2. The rule language

### 2.1 Candidates

| Form | Recursion and negation | Reads enforceable | Windows, no extra process | Licence | Verdict |
|---|---|---|---|---|---|
| Python predicates | any | by API only (a deny-by-default accessor) | yes | n/a | **use** for file-local rules and graph algorithms (SCC, dominators, min cut, transitive reduction) |
| SQL over SQLite | linear recursion; no aggregate inside the recursive select; `UNION` dedupes so cycles terminate; negation outside the recursion [S3] | **yes, at the engine** (authorizer), section 2.5 | yes (stdlib) | public domain | **use** for relational graph-global rules |
| Datalog (Soufflé) | stratified; "rules involving negation must be stratifiable" [S4] | by construction | Windows not mentioned on the install page [S4] | UPL-1.0 (GitHub API [S5]) | export target and Linux/WSL cross-check |
| SHACL Core and SHACL-SPARQL (pySHACL 0.40.1, rdflib 7.6.0) | "validation with recursive shapes is not defined in SHACL and is left to SHACL processor implementations" [S4]; recursion and negation need SPARQL | shapes are data | yes, pure Python | Apache-2.0, BSD-3-Clause [S5] | export target and small-graph cross-check; too slow as runtime in the one implementation measured (the slow case is SPARQL closure, not recursive shapes) |
| Pattern engines (Semgrep, ast-grep) | match source patterns, not typed graph relations | n/a | separate process | ast-grep MIT, Semgrep LGPL-2.1 [S5] | optional process for JS/TS/CSS source rules in phase 3, own rules only |
| Cypher on Neo4j Community | pattern matching with `EXISTS` subqueries | no | JVM server | GPL-3.0 [gdb] | export text for humans; never in the trust path |

### 2.2 Benchmark [B1]

Setup. Four rules that occur in the catalogue, each written in four ways and run on one seeded synthetic graph (seed 20260929; n requirements, 1.5n tests, n modules, n/2 terms): R1 requirement without verifier (anti-join, WV-010), R2 transitive suspect (positive recursion, WV-005), R3 requirement not covered through a refinement chain (recursion then negation, the stratified case of WV-010), R4 homonym in context (self-join and aggregate, WV-017). Engines: plain Python, SQLite 3.49.1, a **toy** semi-naive Datalog evaluator written for this measurement (it is not Soufflé), and pySHACL over rdflib (SHACL Core for R1, SHACL-SPARQL for R2 to R4, each in a child process with a 300 s budget). Windows 11, CPython 3.12.10, median of 3 (Datalog and SHACL: one run). Timings are one machine; the deterministic sections of the result file (agreement, line counts) are byte-stable.

Agreement. **All engines return identical sorted results for every rule at every size they ran**: python, sql and datalog at n = 200, 1,000, 2,000, 10,000 and 100,000; shacl at 200, 1,000 and 2,000. Violation counts at n = 1,000: R1 246, R2 371, R3 165, R4 10; at n = 100,000: 25,934, 99,942, 16,453 and 990. A rule that found nothing would agree everywhere, so `tests/graph/test_rule_language_bench.py` asserts every rule finds something and not everything.

Rule size (non-blank lines of the rule definition only):

| Rule | Python | SQL | Datalog | SHACL |
|---|---|---|---|---|
| R1 anti-join | 3 | 1 | 2 | 2 (Core) |
| R2 positive recursion | 13 | 6 | 3 | 4 (SPARQL) |
| R3 recursion then negation | 13 | 6 | 3 | 3 (SPARQL) |
| R4 self-join and aggregate | 5 | 2 | 2 | 3 (SPARQL) |

Time in milliseconds, `validate` only for SHACL (graph loading excluded):

| Rule | n | Python | SQL | toy Datalog | pySHACL |
|---|---|---|---|---|---|
| R1 | 1,000 | 0.18 | 0.57 | 7.1 | 123 |
| R1 | 10,000 | 1.96 | 6.56 | 71.9 | not run |
| R1 | 100,000 | 40.0 | 59.4 | 1,031 | not run |
| R2 | 200 | 0.07 | 0.06 | 1.5 | 2,544 |
| R2 | 1,000 | 0.66 | 1.24 | 5.5 | 28,913 |
| R2 | 2,000 | 2.39 | 7.00 | 30.9 | 140,614 |
| R2 | 10,000 | 18.8 | 47.8 | 273 | not run |
| R2 | 100,000 | 263 | 796 | 1,822 | not run |
| R3 | 10,000 | 10.0 | 31.9 | 161 | not run |
| R3 | 100,000 | 279 | 531 | 2,255 | not run |
| R4 | 2,000 | 0.37 | 0.67 | 9.6 | 10,070 |
| R4 | 100,000 | 57.4 | 33.9 | 1,269 | not run |

"Not run" above 2,000 nodes is a cut-off I chose (`--shacl-max`), reported as NOT_RUN, not a timeout.

Reading.
- Expressiveness is not the discriminator: all four forms express all four rules, and SQL and Datalog are the shortest. SHACL Core expressed only R1; the other three needed SPARQL inside SHACL, at which point SHACL is SPARQL with a wrapper.
- SHACL as a runtime is out on speed, in pySHACL over rdflib. R2 is a SPARQL property-path closure evaluated once per focus node inside an `sh:sparql` constraint; that is a statement about SHACL-SPARQL in one implementation, and it is a different matter from the Recommendation's silence on recursive shapes (quoted in 2.1), which is why recursion has to be written as SPARQL at all. R2 grows 5x in size and 11.4x in time from n = 200 to 1,000, and 2x in size and 4.9x in time from 1,000 to 2,000 (fitted exponent 2.28 over that step, close to quadratic). The same graph of 2,000 nodes takes 7 ms in SQL. Extrapolating to 3,000 nodes gives about 316 s with a quadratic fit and 354 s with the fitted exponent, past the budget either way (**PREDICTION**).
- At 10^5 nodes Python is 1.9 to 3x faster than SQL on the two recursive rules (263 versus 796 ms, 279 versus 531 ms) and slower on R4 (57 versus 34 ms). At the sizes this repository has (10^3 to 10^4 nodes) SQL is about 0.3 to 48 ms per rule (0.34 to 2.6 ms at 10^3, 3.5 to 47.8 ms at 10^4 over the four stand-ins). So speed does not decide between Python and SQL.
- The toy Datalog evaluator is 2 to 37x slower than SQL across the runs (it is closest on the recursive rules at 10^5 nodes); a compiled engine such as Soufflé would change that, and this run says nothing about it (Soufflé documents no Windows install, so it could not be run here).

Limits. Synthetic graph, four rules, one machine, one SQLite version. pySHACL is one SHACL processor; others (Jena and the like) were not measured (UNVERIFIED). The graph shape (locality of dependencies) affects R2 and R3.

### 2.3 Why SQL over Python for graph-global rules, and where it stops

The margin is small and the decision is about people, not speed. Python would also work, since a deny-by-default accessor can enforce reads there too. SQL wins on four points that matter for "humans can see what happened": the rule is 1 to 6 lines and its polarity is visible (`NOT EXISTS`, `GROUP BY`); a finding can be reproduced by anyone with the `sqlite3` shell on the disposable index, without our code; the engine, not our wrapper, enforces the declared reads; and a diff of a rule is a diff of a query. The cost is that SQLite restricts recursion [S3]: a recursive select must contain exactly one reference to the recursive table (linear recursion), must not use aggregate or window functions, and without `ORDER BY` the extraction order is undefined (a FIFO in the current implementation). So algorithms that need more (SCC, dominators, transitive reduction, min cut) are Python functions that write **derived relations** (`scc.<kind>`, `dominator`) into the index at stratum 1, and the violation query over them is again SQL. 64 rules are SQL, 31 Python, 2 tool-backed.

### 2.4 Datalog, SHACL and Cypher as exports, and where Neo4j and OKF meet the rules

The catalogue's `statement` field is a Datalog-style body, so an export is mechanical. Four renderings of WV-010 (requirement without a covered verifier); the first three were run in [B1]/[B3] in their simplified form, the fourth was not run (**UNVERIFIED**: Neo4j is not installed here and the syntax is from memory of Neo4j 5):

```sql
-- generated by the cardinality-min template (reference.cardinality_min_sql, tested)
SELECT n.id AS node, COUNT(c.link_id) AS count FROM node_requirement n
LEFT JOIN covered_verifies c ON c.dst = n.id GROUP BY n.id HAVING COUNT(c.link_id) < :min ORDER BY n.id
```
```text
% Datalog (benchmark form; the toy evaluator agrees with SQL)
covered(R) :- verifies(_, R).
out(R)     :- requirement(R), !covered(R).
```
```turtle
# SHACL Core (benchmark shape; pySHACL agrees with SQL at n = 200, 1,000, 2,000)
e:S a sh:NodeShape ; sh:targetClass e:Requirement ;
    sh:property [ sh:path [ sh:inversePath e:verifies ] ; sh:minCount 1 ] .
```
```cypher
// Cypher for a person exploring in Neo4j Browser (UNVERIFIED syntax, not run)
MATCH (r:Requirement)
WHERE NOT EXISTS { MATCH (:Verifier)-[l:VERIFIES]->(r) WHERE l.status = 'COVERED' }
RETURN r.id AS node ORDER BY node
```

How the three graph technologies the owner asked about relate to the rules:
- **SQLite index** is where rules run. It is disposable: rebuilt from git, never a source of truth.
- **Neo4j** receives a one-way Cypher/CSV export for exploration and, optionally, the rules rendered as Cypher for a person to run. A rule result from Neo4j is never a verdict: row order is undefined without `ORDER BY` [gdb], the server is GPL-3.0 and stateful, and the export can drift from git. The trust path recomputes.
- **SHACL and Datalog** exports let a second implementation cross-check a subset of rules on the fixture graphs (SHACL anywhere but slow; Soufflé on Linux or WSL). A disagreement is a bug in one of the two, found by a differential test, not a verdict.
- **OKF** is the readable projection. DESIGN, proposal to the okf lane: each catalogue rule gets a generated OKF page (`type: Rule`, `resource: repo://graph/rules/catalogue.json#WV-010`, `sources[].hash_method` `json-key-v1`), so the page that a SARIF `helpUri` points to goes STALE when the rule changes. Findings themselves are not OKF concepts: they are ephemeral and belong in SARIF. OKF links are untyped and broken links are tolerated [gdb], so WV-096 reports where prose links have no typed link behind them.

### 2.5 Enforcing declared reads and polarity

[B1] **MEASUREMENT.** Python's `sqlite3` `set_authorizer` reports exactly the base tables a statement reads: R1 `requirement, verifies`; R2 `changed, depends_on`; R3 `refines, requirement, verifies`; R4 `form_of`. A deny-by-default authorizer that allows only `requirement` and `verifies` rejects R3 with `access to refines.parent is prohibited`. So "declared reads equal actual reads" is a load-time check for SQL rules, and a rule can neither read an undeclared relation nor be cached on an incomplete key (the Buck2 lesson: undeclared inputs are errors [incr]). Python rules receive an accessor that exposes only declared relations.

Polarity (positive or negative read) is declared, not inferred: SQLite offers no parse tree. Two checks stand behind the declaration, and neither proves it. (1) **[B6] MEASUREMENT, exhaustive small worlds**: `test_polarity_claim_over_all_small_worlds` enumerates every pair of nested fact sets over four links and shows, for the generated `cardinality-min` query, that findings only shrink as facts arrive (anti-monotone: the test asserts that at least one finding present on a partial fact set is absent on the complete one, which is the spurious finding the guard exists for), and for a positive join that findings only grow. (2) A Hypothesis property test (property lane, not written here) is the planned check on random facts: with all other relations fixed, adding rows to a positively read relation can only add findings and adding rows to a negatively read relation can only remove them. A SQL parser that recovers polarity statically (sqlglot was not opened, **UNVERIFIED**) is a revisit option.

**A polarity audit found declaration errors.** The first catalogue worded a negation in the `statement` of 14 rules while declaring only positive reads (WV-014 and 016 "every path" and "min cut < k", WV-026, 028, 033, 036, 039, 040, 041, 042, 076, 092, 093, 099). That matters because the closed-world guard (2.6) trusts the declaration. They now declare the negative read; nine of them declare a relation in both polarities, either because the statement both joins and negates it or because it does not say which relation is negated (WV-014, 016, 026, 036, 039, 040, 042, 076, 092), and their strata moved (13 rules from 0 to 1, WV-026 from 1 to 2). The validator now fails a statement that words a negation (`not`, `no`, `without`, `lacks`, `missing`, `fewer`) unless some relation is read negatively or the rule is on the reviewed `ATTRIBUTE_ONLY_NEGATION` list (11 rules whose negation is over a field or a syntactic property of a row that is read positively). This is a word-level check; it cannot see a negation that the statement does not spell out, so a full audit against real queries remains for the phase-1 implementation (open item).

### 2.6 Strata and the closed-world guard

`stratum(rule) = max(0, max over positive reads, max over negative reads + 1)`. Stratum 0 reads base facts positively; 1 reads derived relations or negates base facts; 2 negates derived relations; 3 reads the findings of other rules (suppression hygiene, WV-045). Catalogue [B2]: 41 rules at stratum 0, 38 at 1, 17 at 2, 1 at 3 (after the polarity audit in 2.5; before it 54, 26, 16, 1). The brief's estimates differ for some rules (it gave WV-001 stratum 0); the formula is the definition and the validator recomputes it.

**The guard, stated by polarity.** Absence findings assume the input is complete (the closed-world assumption). Let `F(D)` be the findings of a rule over the facts `D`, and let some relation `X` in `D` be incomplete: an extractor for it did not run, or ran with status partial, so facts are missing but none are invented. Then:

| How the rule reads `X` | Effect of the missing facts | Verdict |
|---|---|---|
| not at all (`none`) | none | FAIL if a finding, else PASS |
| a base relation, positively and directly (`monotone`) | `F` can only lose findings: adding facts to `X` can only add findings, so every finding seen on partial input is also a finding on complete input | FAIL if a finding (sound); else **NOT_RUN**, silence proves nothing |
| negatively (`unsafe`): absence, anti-join, `count < min`, "every path" | `F` can gain findings that disappear when the facts arrive | **NOT_RUN whatever it found**, reason `incomplete-input` |
| through a derived relation (`unsafe`) | derivations such as `link_status` are not monotone in the ledger or in node digests, so the guard assumes the worst | **NOT_RUN whatever it found** |

The earlier wording of this design, "a seen violation is FAIL even on partial input", was true only for the second row and was stated for all rules; for a rule with negative reads it contradicted the rule that such a rule is evaluated only when its inputs are complete. `reference.read_effect(rule, incomplete, catalogue)` computes the effect from the declared reads and the catalogue's `derivations` table (union and typed views such as `node` and `node.symbol` overlap in both directions), and `reference.rule_verdict(findings, prerequisites_ok, effect)` applies the table. A rule that could not be evaluated at all (tool missing, crash, unevaluable suppression expiry) is NOT_RUN. So `PASS` means: no finding, every prerequisite present, and no incomplete relation among the reads. The limit is the same as in 2.5: the table is exactly as sound as the declared polarity, which is tested, not proved.

## 3. Rule anatomy, templates and ids

Fields are in [rules.md](../../../graph/schema/rules.md) section 2. Three points shape the catalogue.

**Templates from the metamodel.** The metamodel aspect declares cardinality obligations (`min`, `rule`, `scope`, `side`), functional maxima (`max_in`, `max_out`) and acyclic link kinds in `graph/schema/metamodel.json`. Each becomes a generated rule with no hand-written query: 13 `cardinality-min` rules (WV-010, 011, 031, 037, 050 to 054, 056, 059, 063, 100), one `cardinality-max` (WV-055) and one `acyclic` (WV-022, covering `contains`, `derived_from`, `refines`, `renamed_to` and `supersedes`). The template has an optional `peer` parameter, the node type at the other end of the link: without it, two obligations that differ only in that type generate one query (WV-031, a transition needs a UI control, and WV-063, a transition needs a symbol, did exactly that in the first catalogue, so every transition without a realiser was reported twice with two fingerprints). `reference.cardinality_min_sql(..., peer_view)` restricts the count to links whose other end is in the peer view; `test_peer_parameter_separates_rules_that_differ_only_in_the_other_end` shows the three queries return different rows on one fixture. A new obligation in the metamodel adds a rule for free, and an agent cannot weaken a rule without changing a generated, hash-checked file. `min` counts only links whose status is COVERED, so a requirement whose only verifier is SUSPECT is reported as not verified and the link rules say why.

**One defect, one rule.** Two rules that report the same defect double the noise and split suppressions. Merged: WV-021 (term binding to a missing term), WV-030 (UI dangling link) and WV-035 (call to a missing operation) into WV-001, whose argument `kind` says which link. Their ids are retired, never reused. Generalised: WV-022 was the brief's cyclic-`broader` check for terms; it is now the acyclicity template for every acyclic link kind (term and requirement `refines`, ADR `supersedes`, `contains`, `derived_from`, `renamed_to`), and the consistency aspect already cites WV-022 for acyclicity. WV-001 (never existed) and WV-004 (existed at the baseline) partition dangling links by cause, and WV-044 gave absolute paths to WV-082. The rule is now enforced, not only stated: the validator fails when two template rules have identical `(template, params)`, the failure mode that the audit found for WV-031 and WV-063 (`test_validator_rejects_two_template_rules_with_identical_params`). It cannot see two hand-written rules that report one defect; that stays a review item (section 10, step 5).

**Ids and messages are stable, wording is not.** A rule id's meaning never changes; a semantic change is a new id, like a hash method (D-13). Each message has an id and positional arguments, so a consumer reads `message.id` and `arguments`, not prose.

## 4. The catalogue

97 rules, 105 messages, 12 categories [B2]. Legend: **Level** is the level once `enforced` (effective level is capped at `note` until then, section 6); **Ph** is the delivery phase (section 14); **S** the stratum; **C** marks the compile class; `(sql)` and `(python)` give the implementation of graph-global and file-local rules. "Source" gives dossier keys, the metamodel, or another lane's ADR.

### 4.1 Dangling, stale, orphaned and ill-typed links (10 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-001 | dangling-link | error | fast | P1 | 1 | graph-global (sql) **C** | `link(L, K, F, T, _, _), (not node(F) or not node(T)), not node_before(missing endpoint)` | gdb, okf ADR-0045, ui, lang |
| WV-002 | ill-typed-edge | error | fast | P1 | 1 | graph-global (sql) **C** | `link(L, K, F, T), type(F)=TF, type(T)=TT, not signature(K, TF, TT)` | math, mde, metamodel |
| WV-003 | duplicate-id | error | fast | P1 | 0 | graph-global (sql) **C** | `node(I, T1, H1, S1), node(I, T2, H2, S2), S1 != S2` | trace |
| WV-004 | orphaned-link | error | fast | P1 | 1 | graph-global (sql) **C** | `link(L, K, F, T), node_before(T), not node(T), not rename_map(T, _)` | trace 4 |
| WV-005 | suspect-link | error/warning | fast | P1 | 1 | graph-global (sql) | `link_status(L, SUSPECT, Direct or Transitive)` | trace 4, trace 7 |
| WV-007 | inferred-link-satisfies-gate | error | fast | P2 | 0 | graph-global (sql) | `link(L, K, F, T, _, _, inferred), counts_toward_gate(K)` | ui GAP-024, gdb D8 |
| WV-008 | id-removed-without-rename-map | error | fast | P2 | 1 | graph-global (sql) **C** | `node_before(I), not node(I), not rename_map(I, _)` | code 6.7 |
| WV-022 | acyclic-link-cycle | error | fast | P2 | 1 | template **C** | `scc.K has a component of size > 1 (or a self loop) for a link kind K declared acyclic` | metamodel, math M2, lang SKOS |
| WV-047 | hash-method-unregistered-or-mismatched | error | fast | P2 | 1 | graph-global (sql) **C** | `link(L, K, _, _, M, _), (not hash_method(M) or not hash_method_policy(K, M))` | trace, okf ADR-0046 |
| WV-055 | link-cardinality-exceeded | error | fast | P2 | 1 | template **C** | `count(links of kind K on side S of node N) > max declared by the metamodel signature` | metamodel, math (many-sorted signatures) |

### 4.2 Extractor health (2 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-006 | unresolved-resolver | notrun | fast | P1 | 0 | graph-global (sql) **C** | `extractor_run(E, not_run, Reason)` | trace, incr |
| WV-009 | partial-extraction-gated | error/notrun | fast | P1 | 0 | file-local (python) **C** | `partial_fact(File, Position)` | code M2 |

### 4.3 Orphans and coverage (11 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-010 | requirement-without-verifier | error | fast | P1 | 2 | template | `node.requirement(N), count(covered_link of kind verifies, incoming, N) < 1` | trace, math, metamodel |
| WV-011 | requirement-without-satisfier | error | fast | P2 | 2 | template | `node.requirement(N), count(covered_link of kind satisfies, incoming, N) < 1` | trace, metamodel |
| WV-012 | symbol-without-requirement | note | fast | P2 | 2 | graph-global (sql) | `node.symbol(S), in_policy_scope(S), no covered satisfies or names link from S` | trace 5 |
| WV-013 | unwanted-coverage | warning | fast | P2 | 0 | graph-global (sql) | `link(L, K, F, T), target_needs_no_coverage(T, policy)` | trace |
| WV-014 | single-point-of-evidence | note | full | P3 | 1 | graph-global (python) | `d dominates every path from requirement R to its covered evidence` | math 2.1 |
| WV-015 | redundant-link | note | full | P3 | 0 | graph-global (python) | `link(L, K, F, T) is implied by a path F -> ... -> T of other links of kind K (transitive reduction on the condensation)` | math 2.1 |
| WV-016 | evidence-redundancy-below-k | note | full | P3 | 1 | graph-global (python) | `min vertex cut between requirement R and its covered evidence is < k` | math 2.1 |
| WV-051 | persona-without-journey | note | fast | P2 | 2 | template | `node.persona(N), count(covered_link of kind serves, incoming, N) < 1` | owner request |
| WV-052 | journey-without-persona | note | fast | P2 | 2 | template | `node.journey(N), count(covered_link of kind serves, outgoing, N) < 1` | owner request |
| WV-056 | term-without-binding | warning | fast | P2 | 2 | template | `node.term(N), count(covered_link of kind names, incoming, N) < 1` | lang, owner request |
| WV-100 | test-without-requirement | note | fast | P2 | 2 | template | `node.test(N), count(covered_link of kind verifies, outgoing, N) < 1` | trace, owner request |

### 4.4 Naming and vocabulary drift (11 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-017 | homonym-in-context | error | fast | P2 | 0 | file-local (python) | `term_form(T1, C, F, preferred), term_form(T2, C, F, preferred), T1 != T2` | lang 2.2 |
| WV-018 | synonym-two-preferred-forms | error | fast | P2 | 0 | file-local (python) | `term_form(T, C, F1, preferred), term_form(T, C, F2, preferred), F1 != F2` | lang 2.2 |
| WV-019 | form-shared-by-two-terms | error | fast | P2 | 0 | file-local (python) | `term_form(T1, C, F, K1), term_form(T2, C, F, K2), T1 != T2, not (K1 = preferred and K2 = preferred)` | lang 5 |
| WV-020 | forbidden-form-at-declaration | error | fast | P2 | 0 | file-local (python) | `identifier(Site, Words), term_form(T, C, F, forbidden, ReplacedBy), F is a contiguous word sequence of Words` | lang 4, lang 5 |
| WV-023 | deprecated-without-replaced-by | error | fast | P2 | 0 | file-local (python) | `term_meta(T, status=deprecated), no replaced_by` | lang |
| WV-024 | unbound-identifier-report | note | full | P2 | 1 | graph-global (sql) | `identifier(Site, Name, Freq), high frequency, not named by any names link` | lang 5.3 |
| WV-053 | term-without-bounded-context | error | fast | P2 | 2 | template | `node.term(N), count(covered_link of kind contains, incoming, N) < 1` | lang, metamodel |
| WV-054 | aggregate-term-without-realiser | warning | fast | P2 | 2 | template | `node.term(N), count(covered_link of kind realises, incoming, N) < 1` | lang, metamodel |
| WV-094 | forbidden-form-in-prose | error | fast | P2 | 0 | file-local (python) | `prose_token(Doc, Pos, Words), term_form(T, C, F, forbidden), F occurs in Words outside code` | lang 5, 3D-Linter SPEC |
| WV-095 | forbidden-form-in-ui-literal | warning | fast | P2 | 0 | file-local (python) | `ui_literal(File, Pos, Text), term_form(T, C, F, forbidden), F occurs in Text` | ui, lang |
| WV-099 | diagram-label-drift | warning | fast | P2 | 1 | graph-global (sql) | `view_fact(Diagram, Id, label, L), names(Id, T), L not in forms(T)` | lang, bx |

### 4.5 Layering and dependency (5 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-025 | import-cycle | warning | fast | P2 | 0 | graph-global (python) | `scc.depends_on has a component of size > 1` | math 2.1, code |
| WV-026 | architecture-reflexion | warning/note | fast | P2 | 2 | graph-global (sql) | `component_edge(A, B) not allowed by allow_decl (divergence), or allow_decl(A, B) with no component_edge (absence)` | mde, quality ADR-0035 |
| WV-057 | layer-inversion | error | fast | P2 | 1 | graph-global (sql) | `edge(A, B) in depends_on, calls, exposes with rank(component_of(A)) < rank(component_of(B))` | quality ADR-0035, mde |
| WV-058 | forbidden-component-dependency | error | fast | P2 | 1 | graph-global (sql) | `component_edge(A, B), forbid_decl(A, B)` | quality ADR-0035 |
| WV-059 | module-without-component | warning | fast | P2 | 2 | template | `node.module(N), count(covered_link of kind contains, incoming, N) < 1` | mde, quality ADR-0035 |

### 4.6 Diagram and view versus model (6 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-027 | diagram-semantic-hash-drift | error | fast | P2 | 0 | graph-global (sql) | `diagram_meta(D, Embedded), projection_hash(source(D)) != Embedded` | bx, visual ADR-0023 |
| WV-028 | view-mapping-totality | error | fast | P2 | 1 | graph-global (sql) | `semantic_type(T), not in view_mapping as drawn or not_shown` | bx 4 |
| WV-029 | lens-law-violation | error | full | P3 | 0 | test-level | `an edit sequence e on a view violates GetPut, PutGet (mod layout and declared amendments) or conditional PutPut` | bx 3.8 |
| WV-060 | diagram-element-unbound | error | fast | P2 | 1 | graph-global (sql) | `diagram_element(E), derived_from(E, S), not node(S)` | bx, mde |
| WV-061 | model-element-not-drawn | warning | fast | P2 | 1 | graph-global (sql) | `node.workflow_element(N), not drawn in view V, not declared not_shown in V` | bx |
| WV-062 | view-overlap-disagreement | error | fast | P2 | 0 | graph-global (sql) | `view_fact(V1, Id, P, X1), view_fact(V2, Id, P, X2), V1 != V2, X1 != X2` | bx 2.7 |

### 4.7 Model versus code (5 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-063 | workflow-element-without-realiser | warning | fast | P2 | 2 | template (`peer` symbol) | `node.transition(N), count(covered_link of kind realises, incoming from node.symbol, N) < 1` | mde, bx, owner request |
| WV-064 | transition-not-exposed | warning | fast | P2 | 2 | graph-global (sql) | `node.transition(T), not exposed_transition(T)` | ui, mde |
| WV-065 | generated-artefact-drift | error | full | P2 | 0 | adapter | `derived_from(A, S) generated, regenerated(A) != digest(A)` | assure 7, bx, lang 4 |
| WV-066 | model-without-conformance-link | note | fast | P3 | 1 | graph-global (sql) | `models(FM, W), no conforms_to(Code, FM)` | assure, agent |
| WV-067 | formal-law-without-formalises | warning | full | P3 | 1 | graph-global (sql) | `node.formal_law(L), no formalises(L, Invariant or Requirement)` | assure |

### 4.8 UI versus model, API, tokens and evidence (7 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-031 | uncovered-domain-action | error | fast | P2 | 2 | template (`peer` ui_control) | `node.transition(N), count(covered_link of kind realises, incoming from node.ui_control, N) < 1` | ui, metamodel |
| WV-032 | orphan-or-unkeyed-element | error | full | P3 | 1 | rendered | `rendered element with an interactive role, no data-eija-key, or a key that is not in the sidecar` | ui |
| WV-033 | label-drift | error | full | P3 | 1 | rendered | `rendered accessible name of a control that names term T is not a registered form of T` | ui, lang |
| WV-034 | enabledness-mismatch | error | full | P3 | 0 | rendered | `for (state, actor): enabled(UI) != allowed(kernel)` | ui |
| WV-036 | token-drift | warning/note | fast | P2 | 1 | file-local (python) | `css var(--x) with no token, unused token, or raw colour literal` | ui |
| WV-037 | ui-control-without-evidence | warning | fast | P2 | 2 | template | `node.ui_control(N), count(covered_link of kind exercised_by, outgoing, N) < 1` | ui, metamodel |
| WV-050 | ui-element-without-term | warning | fast | P2 | 2 | template | `node.ui_control(N), count(covered_link of kind names, outgoing, N) < 1` | ui, lang, owner request |

### 4.9 Evidence freshness and status lattice (12 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-038 | statement-digest-mismatch | error | fast | P3 | 0 | graph-global (sql) | `node.formal_law(L, D), approved_digest(L, A), D != A` | assure |
| WV-039 | assumption-ledger-diff | error | full | P3 | 1 | graph-global (sql) | `assumption in a witness report not listed in the committed ledger` | assure |
| WV-040 | proof-without-negative-control | error | full | P3 | 1 | graph-global (sql) | `models(FM, W) with proof evidence, no seeded-unsafe control that fails and no reachability witness` | assure |
| WV-041 | model-proof-worded-as-code | error | fast | P3 | 1 | graph-global (sql) | `claim about code supported only by a proof link with no conforms_to` | assure, AGENTS.md |
| WV-042 | claim-graph-structure | error | fast | P3 | 1 | graph-global (python) | `claim-to-claim support edge, a cycle among claims, or a defeater with no resolution` | assure |
| WV-068 | evidence-subject-stale | error | fast | P3 | 0 | graph-global (sql) | `evidence_subject(E, Dim, D1), current_subject(E, Dim, D2), D1 != D2` | assure, kernel assess_receipt |
| WV-069 | checker-not-pinned | error | fast | P3 | 1 | graph-global (sql) | `checked_by(E, Tool), not registered with a pinned version and sha256` | assure, tla ADR-0028 |
| WV-070 | supplied-status-mismatch | error | fast | P3 | 1 | graph-global (sql) | `supplied_status(E, S1), evidence_verdict(E, S2), S1 != S2` | assure, AGENTS.md |
| WV-071 | not-run-absorbed-as-pass | error | fast | P3 | 0 | graph-global (sql) | `aggregate_report(A, Inputs, Reported), NOT_RUN in Inputs, Reported = PASS` | incr, math C4, quality audit session |
| WV-072 | conflicting-evidence | error | fast | P3 | 1 | graph-global (sql) | `two evidence items on one claim with verdicts PASS and FAIL (join = CONFLICT)` | math C4 |
| WV-073 | pass-without-tcb-label | error | fast | P3 | 1 | graph-global (sql) | `evidence_verdict(E, PASS), label(E) missing or stronger than the checker kind allows` | assure 2.2 |
| WV-074 | mocked-evidence-labelled-live | error | fast | P3 | 0 | graph-global (sql) | `evidence_meta(E, mode=mocked or synthetic), claimed live` | AGENTS.md |

### 4.10 ADR supersession and record discipline (6 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-076 | adr-supersession-asymmetric | error | fast | P2 | 1 | graph-global (sql) | `adr_meta(A, superseded_by, B) without supersedes(B, A), or supersedes(B, A) without the header on A` | docs/adr/README.md |
| WV-077 | superseded-adr-still-live | warning | fast | P2 | 2 | graph-global (sql) | `motivates(A, T), all motivators of T are superseded, no live motivator` | docs/adr/README.md, trace |
| WV-078 | adr-status-invalid | error | fast | P2 | 0 | file-local (python) | `status not in {proposed, accepted, superseded by ADR-NNNN}` | docs/adr/template.md |
| WV-079 | adr-number-collision | error/warning | fast | P2 | 0 | graph-global (sql) | `two ADR files share a number, or a number lies outside the reserved block of its lane` | docs/adr/README.md |
| WV-080 | accepted-adr-rewritten | error | fast | P3 | 0 | graph-global (sql) | `accepted ADR whose body digest (adr-body-v1: everything but the Status line) differs from the digest recorded at acceptance` | docs/adr/README.md |
| WV-081 | adr-oss-check-missing | warning | fast | P2 | 0 | file-local (python) | `ADR lists a custom module but its OSS-check table has no filled row` | ADR-0016, docs/adr/template.md |

### 4.11 Determinism violations (11 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-043 | non-canonical-committed-artefact | error | fast | P1 | 0 | file-local (python) **C** | `committed_file(F, Bytes), canonical(parse(Bytes)) != Bytes` | math C1, code M6 |
| WV-044 | nondeterminism-token-in-artefact | error | fast | P2 | 0 | file-local (python) **C** | `committed_file contains a timestamp, GUID, hostname or random token` | incr, ProofMap GAP-003 |
| WV-082 | non-posix-or-absolute-path | error | fast | P2 | 0 | file-local (python) **C** | `id or path with a backslash, a drive letter, a leading slash or a .. segment` | code M5, okf codelink.parse_uri |
| WV-083 | nondeterministic-api-use | error | fast | P2 | 0 | adapter | `eijagraph code uses a banned nondeterministic API (wall clock, uuid4, random, hostname, locale, nx.condensation, graphlib order, os.listdir, glob.glob)` | incr 2.2, own measurement |
| WV-084 | unpinned-extractor-record | error | fast | P2 | 0 | graph-global (sql) **C** | `extractor_record(E) lacks tool, grammar, python minor or rule fingerprint` | code M1 |
| WV-085 | unsorted-iteration-in-emitter | error | fast | P2 | 0 | file-local (python) | `call to iterdir, glob, rglob, listdir, scandir or walk, or iteration over a set, not directly under sorted(...) in eijagraph code` | incr 2.2, math D-09, own measurement |
| WV-086 | missing-explicit-encoding-or-newline | error | fast | P2 | 0 | adapter | `open, read_text or write_text in eijagraph without encoding, or a text write without newline set to LF` | incr 2.2, lang 5.6, own measurement |
| WV-087 | rebuild-root-mismatch | error | release | P2 | 0 | harness | `root hash of build 1 != root hash of build 2 from a clean checkout` | incr 2.2 |
| WV-088 | permutation-output-diverged | error | full | P1 | 0 | harness | `SARIF bytes differ across file order, rule order, PYTHONHASHSEED, TZ, LC_ALL, CWD, CRLF, threads or non-BMP input` | incr 4 |
| WV-089 | hash-method-golden-drift | error | fast | P2 | 0 | graph-global (sql) | `golden vector of hash method M no longer reproduces, while the method name is unchanged` | okf ADR-0046 |
| WV-090 | sarif-profile-violation | error | fast | P1 | 0 | graph-global (python) | `SARIF output has a GUID, timestamp, absolute path, machine or account field, unsorted array or missing columnKind` | SARIF F.2 to F.4, incr |

### 4.12 Rules about rules (11 rules)

| ID | Rule | Level | Tier | Ph | S | Kind | Fires when | Source |
|---|---|---|---|---|---|---|---|---|
| WV-045 | suppression-without-evidence-or-matching-nothing | error | fast | P2 | 3 | graph-global (sql) | `suppression(S, Fp, Rule, Justification, Evidence), no evidence path that resolves, or no current finding with fingerprint Fp` | incr 5.6 |
| WV-046 | baseline-growth | error | fast | P2 | 1 | graph-global (sql) | `baseline(Fp), not baseline_before(Fp)` | incr |
| WV-048 | obligation-reduced | error | fast | P2 | 1 | graph-global (sql) | `obligation_before(O), not obligation(O), no ledger decision covering O` | agent-interface design 8.3, vericoding [assure], AGENTS.md |
| WV-049 | same-author-evidence | warning | fast | P3 | 1 | graph-global (sql) | `requirement R, verifier V and satisfier S all authored_in_run(Run), no owner-approved statement digest for R` | agent-interface design C6, assure statement pinning |
| WV-075 | ledger-entry-dangling | error | fast | P2 | 1 | graph-global (sql) | `ledger(Seq, Actor, Subject, Digest, Action), not node(Subject)` | trace 7 |
| WV-091 | suppression-expired | error/notrun | fast | P2 | 0 | graph-global (sql) | `suppression(S, Expiry), Expiry reached under the explicit as-of input, ledger sequence, release or digest` | user request, incr 5.6 |
| WV-092 | rule-without-fixtures | error | fast | P2 | 1 | meta | `catalogue_rule(R), fewer than the required positive, negative, mutation and golden fixtures` | quality ADR-0035, incr 5 |
| WV-093 | rule-without-decision-entry | error | fast | P2 | 1 | meta | `catalogue_rule(R), no decision_entry(R)` | user request |
| WV-096 | okf-link-untyped | note | fast | P2 | 1 | graph-global (sql) | `okf_link(Page1, Page2), no typed declared link between the two concepts` | okf SPEC, gdb 3.7 |
| WV-097 | ledger-actor-not-human | error | fast | P2 | 0 | graph-global (sql) | `ledger(Seq, Actor, ...), Actor is not a declared human actor` | AGENTS.md, trace 7, okf ADR-0046 |
| WV-098 | protected-policy-digest-mismatch | error | fast | P2 | 0 | graph-global (sql) | `protected_file(P, D), approved_digest(P, A), D != A` | AGENTS.md, assure statement pinning |

### 4.13 Where the requested categories land

| Requested | Rules |
|---|---|
| Dangling or stale links (hash mismatch) | WV-001, 004, 005, 008, 047, 068, 089 |
| Orphans: requirement without test | WV-010 (and 011, 012, 013) |
| Orphans: term without code | WV-056 |
| Orphans: UI element without domain term | WV-050 (and WV-037 for a control without a test) |
| Orphans: test without requirement | WV-100 |
| Layering and dependency | WV-025, 026, 057, 058, 059, 055 |
| Naming and vocabulary drift | WV-017 to 020, 023, 024, 033, 094, 095, 099 |
| Diagram versus model | WV-027, 028, 029, 060, 061, 062 |
| Model versus code | WV-034, 041, 063 to 067 |
| Evidence freshness and status lattice | WV-038 to 042, 068 to 074 |
| ADR supersession | WV-022 (cycles), 076, 077, 078, 079, 080, 081 |
| Determinism violations | WV-043, 044, 082 to 090 |
| Moved goalposts and self-verification (agents aspect) | WV-048, 049 |

## 5. Diagnostics

Full profile: [rules.md](../../../graph/schema/rules.md) sections 5 and 6. What each choice buys:

| Choice | Buys | Evidence |
|---|---|---|
| SARIF 2.1.0 canonical, other formats generated | one carrier for every lane; `kind: open` and `executionSuccessful` express NOT_RUN | [S1] 3.27.9, 3.20.14 |
| `partialFingerprints["eijaFinding/v1"]`, `fingerprints` left empty | stable identity across runs; the spec says "a direct SARIF producer SHOULD NOT populate" `fingerprints` | [S1] 3.27.16 |
| No `baselineState`, `guid`, times, machine, account, command line, absolute paths | byte-identical output; the spec lists these as non-deterministic (F.2) and adds that a baseline makes the file depend on an earlier file (F.7) | [S1] |
| `columnKind: unicodeCodePoints` always | explicit unit; the spec requires it when results are non-empty and text artifacts were processed, and LSP defaults to UTF-16 | [S1] 3.14.27 |
| `message.id` + `arguments` + `text` | agents read structure; every viewer can still show text | [S1] 3.11.2, 3.11.7 |
| `codeFlows` for the witness | an ordered path that "demonstrates the problem" | [S1] 3.37.6 |
| `properties.verdicts` for every evaluated rule | a passing rule leaves a record, so "PASS" is distinguishable from "not evaluated" | DESIGN |
| `kind: open` for NOT_RUN, not `kind: pass` for PASS | SARIF has a native `pass` kind ("evaluated, no problem found", 3.27.9), not used: one `pass` result per rule per run would add 97 results that every consumer treats as findings to skip, and they would carry no information that `properties.verdicts` does not. `open` is defined as "the tool concluded there was insufficient information", which is close to but not the same as NOT_RUN (not evaluated at all): the profile uses it for NOT_RUN on purpose (a consumer that knows nothing of EIJA still sees an unresolved item and not a pass), and the `toolExecutionNotifications` entry with `associatedRule` says which and why | [S1] 3.27.9, 3.20.14; DESIGN |

**MEASUREMENT [B5]**: the worked example (three findings and one NOT_RUN, 12,946 bytes) has zero errors against the OASIS schema [S2] and against the determinism-profile checker; a seeded bad `level` and a removed `executionSuccessful` each give one schema error. Run with jsonschema 4.25.1 first and re-run on 2026-09-29 under the pinned 4.26.0 (`Draft4Validator`, the schema's own draft): the same 0, 1 and 1 errors, and the schema's sha-256 is unchanged. Six orderings of three findings times six orderings of three artifacts (36 combinations) produce one byte string (`test_output_is_independent_of_finding_and_artifact_order`).

Two spellings, one identity: `eija.finding.v1` is the domain tag inside the hash preimage, `eijaFinding/v1` is the key in SARIF `partialFingerprints`, where the spec requires "a versioned hierarchical string" (3.27.17, 3.5.4.2; its example is `prohibitedWordHash/v3`, read raw 2026-09-29); the two version suffixes move together. Fingerprint golden vector (MEASUREMENT, pinned in the test): rule `WV-010`, subject `repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01`, identity `{"kind":"verifies","side":"in"}` gives `38354b0926aa0f7fdbd57c5e4a73bcf549b606018b0d958dd03ee9023ba34d91`. Moving the finding to another line leaves it unchanged; `("a","bc")` and `("ab","c")` differ.

Views generated from SARIF: text, `rdjson` for reviewdog, LSP-shaped JSON for the agents lane, and a GitHub code-scanning upload by REST only (Actions are unavailable to 45ck repos, owner decision, so that path is not built).

## 6. Severity, suppression, false positives

### 6.1 Levels, tiers and maturity

| Level | fast | full | release |
|---|---|---|---|
| `error` | blocks | blocks | blocks |
| `warning` | ratcheted: the baseline may shrink, never grow (WV-046) | ratcheted | blocks |
| `note` | report | report | report |
| `notrun` | blocks unless accepted (`EIJA_ALLOW_NOT_RUN=1`) | same | same, and the acceptance is recorded in the run |

While a rule is `proposed` or `experimental` its effective level is `min(severity, note)`: a new rule cannot block anyone until an owner ledger entry makes it `enforced`. All 97 rules are `proposed`, so today none blocks. The target severities are error 68, warning 18, note 10, notrun 1 [B2].

### 6.2 Suppressions and baselines

A suppression is `{id, rule, fingerprint, justification, evidence, expires}` in `graph/suppressions.json` (protected). Rules for it:

- `evidence` must resolve to a repo-local file (and anchor). ProofMap Lite recorded the reason: acceptances without evidence were an ignored warning in disguise, and GAP-017 fixed that by requiring `id`, `reason` and resolving `evidence` [S6]. WV-045 also reports a suppression that matches no finding (import-linter treats an unmatched ignore as an error by default [S4]).
- `expires` is one of four forms and none reads a clock: `ledger_seq`, `release`, `until_digest` with `subject`, or `as_of` compared with the explicit `--as-of` input. The last form exists because "expire on a date" is what people ask for; the date is an input recorded in the run, so the same inputs give the same verdict. **A suppression whose expiry cannot be evaluated does not suppress** (WV-091 reports NOT_RUN). Tested in `test_suppression_expiry_never_reads_a_clock`.
- No inline pragmas. A comment cannot carry a resolving evidence path, would be invisible in JSON, CSV and Markdown artefacts, and changes the file it sits in.
- The baseline is a ratchet (ArchUnit's freezing rules and the quality lane's complexity ratchet are the precedents [incr], [S7]). WV-046 fails if the baseline grew against the baseline ref.

### 6.3 False-positive policy

Each rule declares a soundness class: 87 `exact` (no false positive given correct facts), 8 `may` (over-approximate edges, a splitter or incomplete provenance) and 2 `heuristic` (WV-024, WV-085). The policy:

1. `may` and `heuristic` rules ship at `note` or `warning` and are promoted only after a human has reviewed **every** finding they produce on this repository; the review outcome (true positives, false positives) goes into the ADR-lite entry.
2. **Every false positive becomes a negative fixture** and either a rule change (a new version of the messages, or a new id if the meaning changes) or a declared exemption in a protected policy file. Never a silent suppression.
3. Both error directions are real. ProofMap Lite measured a rule that was too strict (GAP-019: a warning fired although related evidence existed because the rule required every related surface) and one too lenient (GAP-027: a docs-only edit cleared a code-change warning) [S6]. The catalogue therefore counts links of the right **evidence kind**: `verifies` counts only verifier nodes (test, property, formal model, witness), not documents, and templates use "at least one" where the policy says so.
4. Report precision as counts, `TP / (TP + FP)` over reviewed findings. No confidence percentage enters a gate. A promotion with zero false positives in n reviewed findings still leaves an upper bound: about 3/n at 95% (arithmetic: `1 - 0.05^(1/n)`, for n = 30 this is `1 - exp(ln 0.05 / 30) = 1 - exp(-0.0999) = 0.0950`). That number is an argument about sample size, not a threshold.
5. Static tiers say what they cannot see: UI static checks report "static-visible only"; WV-020 counts names the splitter could not split (`unknown_names`) instead of guessing (only 3 of 10 glossary terms appear as contiguous identifier words in `src/`, [lang] MEASUREMENT).

## 7. Incremental evaluation

**Semantics first.** Incremental evaluation is a cache, never a meaning. Correctness is the Build Systems a la Carte definition (stored result equals a clean recomputation, Definition 3.1, read in the paper by the incr dossier author) and the oracle is D-18: incremental output equals clean output after random edit sequences (Hypothesis strategies from the property lane).

**Key and cutoff.** `key(rule) = SHA-256(domain tag, rule fingerprint, sorted (relation, slice Merkle root))`, where the rule fingerprint covers rule id, catalogue entry digest, source hash and pinned tool versions (D-11). Two cutoffs: (1) a node whose normalised digest did not change dirties nothing, so a comment-only edit dirties no rule; (2) a rule whose output hash is unchanged lets the previous SARIF chunk be reused. Reads are enforced (section 2.5), so an undeclared input cannot make a cache hit wrong.

**Dirty sets, MEASUREMENT of the catalogue metadata [B2]** (which rules read a relation that a change class makes dirty, through the derivation table; not a timing):

| Change | Dirty rules of 97 | fast / full |
|---|---|---|
| comment-only edit of a Python function (digest unchanged) | 0 | 0 / 0 |
| body edit of a Python function or method | 21 | 19 / 2 |
| edit of a test function | 18 | 17 / 1 |
| add or remove one `verifies` link | 17 | 14 / 3 |
| edit one term in the registry | 28 | 26 / 2 |
| edit prose in a document or ADR | 21 | 20 / 1 |
| edit the UI html or js | 23 | 21 / 2 |
| edit the workflow json | 22 | 20 / 2 |
| append one ledger entry | 24 | 24 / 0 |
| edit eijagraph source (static determinism rules) | 22 | 21 / 1 |
| edit the catalogue or a fixture | 4 | 4 / 0 |

The derivation model is conservative: a ledger entry can move any link status, so it dirties every `link_status.<kind>`; a node edit dirties only kinds whose anchored ends include that node type (from the metamodel's `anchor_ends`).

**Cost model.** `T_full = sum over rules of c_r`; `T_incr = sum over dirty rules of c_r + T_hash`. From [B1] the slowest benchmark rule in SQL costs 2.55 ms at 10^3 nodes (R3) and 47.8 ms at 10^4 (R2). **PREDICTION**: if every rule cost as much as the slowest of the four stand-ins, 97 rules would take 97 x 2.55 ms = 0.25 s at 10^3 nodes and 97 x 47.8 ms = 4.6 s at 10^4. That is an estimate from stand-ins, not an upper bound: the anti-join stand-ins cost 3.5 to 6.6 ms at 10^4 (R4, R1), but Python graph algorithms (SCC, dominators, min cut) and template `GROUP BY` rules over real views were not timed and could be slower. Extraction, not checking, is the likely bottleneck ([gdb]). At those numbers the estimated best-case saving of a cache is 0.19 s at 10^3 nodes and about 3.6 s at 10^4 (78% of the estimate, the body-edit case: 76 of 97 rules clean), against extraction costs that are unmeasured, so **the cache is off by default** until `graph/bench` shows a warm-run gain that pays for its bug surface (same conclusion as [incr] and SYNTHESIS). The release tier always evaluates cleanly and compares.

## 8. Autofix

A fix is data: `{rule, fingerprint, applicability, edits: [{path, start, end, replacement}], precondition_sha256: {path: hash}}`. Byte-range edits over LF-folded text, sorted, disjoint. Rules:

1. **Proposals only.** The kernel path and the MCP surface never apply edits (AGENTS.md: agents and providers never approve or apply). `eija-graph fix --apply` is a user-invoked command outside the kernel; an agent may edit in its own checkout, and the checker recomputes anyway.
2. **Fail closed.** If a file's LF-folded SHA-256 differs from `precondition_sha256`, the fix is refused, not merged.
3. **Applicability** uses the rustc vocabulary [S4]: `machine_applicable` ("can be applied mechanically"), `maybe_incorrect`, `has_placeholders`, plus our `human_only` for acts that only a person may do.
4. **Overlap is a conflict**, reported, not resolved silently (ESLint leaves overlapping fixes for a later pass [incr]).
5. **Idempotent and convergent.** Applying a fix twice gives the same bytes and the rule's finding disappears (repair operator `RM-APPLY-FIX`). Passes are capped at 10; our fixes are disjoint by construction, so reaching the cap is a bug reported as an internal error (ESLint caps at 10 and ruff at 100 [incr]).

| Applicability | Rules |
|---|---|
| `machine_applicable` (4) | WV-027 regenerate a diagram, WV-043 canonicalise a file, WV-065 regenerate an artefact, WV-086 add explicit encoding and newline |
| `maybe_incorrect` (5) | WV-004 retarget a link, WV-018 demote a form, WV-020 rename (LibCST, phase 3), WV-085 wrap in `sorted`, WV-094 replace a form in prose |
| `has_placeholders` (1) | WV-008 rename map entry with the new id blank |
| `human_only` (4) | WV-005 (a review summary; clearing SUSPECT is a ledger act), WV-038 (re-approve a statement digest), WV-048 (a ledger decision covering a reduced obligation), WV-098 (re-approve protected policy) |

## 9. Testing the rules

### 9.1 Fixture matrix

For each rule, with `C` a clean graph fixture: a **fire** operator applied to `C` must yield at least one finding whose subjects include the mutated id; a **repair** operator applied to the fired fixture must give the same bytes as `C` (`RM-REVERT` always, plus the rule's own repairs); a **benign** operator applied to `C` must give the same bytes (comment edit, unrelated node, reformat, plus the global operators CRLF, file order, environment, non-BMP, threads). The operators are the catalogue's (26 fire, 16 repair, 5 benign, 5 global), so a rule author cannot write a rule and a fixture that agree by construction. [B2]: **389 minimum cases**, at most 6 per rule, mean 4.01; each message id needs at least one more positive case. This is the negative-oracle rule of AGENTS.md generalised: a check must fail when the thing it guards is broken. It resembles what the literature calls metamorphic testing; I did not open a source, so nothing is claimed from it.

### 9.2 Layers

| Layer | What it checks | Oracle |
|---|---|---|
| Fixtures with annotations | `ruleid:` positive, `ok:` negative, `todoruleid:` known gap, per message id | Semgrep's test convention [S4] |
| Fire/repair/benign matrix | the rule fires on the fault, stops when repaired, ignores noise | section 9.1 |
| Golden SARIF | exact bytes per fixture; regenerated only by `--bless` in a reviewed commit | byte equality |
| Polarity property test | declared polarity matches behaviour on random facts | section 2.5 |
| Differential | SQL rule equals its Python or Datalog form on fixtures; incremental equals clean | bench pattern |
| Permutation harness | SARIF identical under file order, rule order, hash seed, TZ, LC_ALL, CWD, CRLF, threads, non-BMP: 9 single-axis runs plus one all-axes run must equal the baseline | D-19 (determinism aspect owns it) |
| Rule-source mutation | run the mutation lane's engine (cosmic-ray 8.7.0, MIT [S5]) over `eijagraph.rules`, `eijagraph.sarif` and `graph/rules/reference.py` with the fixture suite as the killing suite; survivors are triaged; per-module ratchet | mutation ADR-0033 [S7] |
| Catalogue meta-checks | WV-092 every rule has fixtures, matrix and golden; WV-093 every rule has an ADR-lite entry | validator |

The mutation lane's engine runs natively on Windows in a scratch copy under `.tmp/mutation/` with at most two workers [S7]; the rule tests must therefore avoid grandchild processes where possible (cosmic-ray kills only the immediate process on a Windows timeout, per ADR-0033).

### 9.3 What is tested today [B3]

`tests/graph/test_rules_catalogue.py` (30 tests: the validator accepts the committed catalogue and rejects each of 14 seeded defects, including a wrong stratum, an unknown relation, a reused retired id, a metamodel disagreement, two template rules with identical parameters, a negation without a negative read and promotion of a stub decision entry); `test_rules_reference.py` (26: fingerprint golden vector and length safety, exhaustive verdict laws, the verdict truth table by read effect, `read_effect` on direct, negative and derived reads, the exhaustive small-world polarity check, the `peer` template, suppression expiry, byte-identical SARIF over 36 input orders, profile checker on eight seeded violations, the cardinality-min template on positive, negative and boundary cases, schema validation against the OASIS schema when present); `test_rule_language_bench.py` (12: engine agreement, guard, authorizer, hash-seed independence, committed result, pySHACL when installed). Run 2026-09-29: 67 passed, 1 skipped (pySHACL not installed: NOT_RUN); the whole `tests/graph` suite, including the formal aspect's cross-check of `rule_verdict`, gave 342 passed, 13 skipped, 1 xfailed. Skips are NOT_RUN: the SHACL cross-check skips when `pyshacl` is not importable, the schema check when the OASIS schema is not available offline.

## 10. Governance

**Adding a rule** needs, in one change: (1) a catalogue entry with `maturity: proposed`; (2) the query or function; (3) fixtures, the matrix and a golden; (4) a line in `graph/rules/decisions.jsonl` (ADR-lite: problem, evidence, alternatives with the existing tool checked first, cost, revisit trigger); (5) a check that the defect is not already reported by another rule (one defect, one rule). WV-092 and WV-093 enforce the presence of (3) and (4); the validator enforces the rest of the shape.

**What the ADR-lite entries are worth today (MEASUREMENT, `check_catalogue.py --stats`).** The 97 entries prove that every rule has a `problem` (97 distinct texts) and `evidence` keys, not that alternatives were compared per rule: before the audit the `alternatives` field was one of two boilerplate strings and `revisit` one string for all 97 entries, so the presence check passed on boilerplate. Now each entry carries `alternatives_checked`. Three are true (WV-083, 085 and 086, whose ruff probes ran on 0.15.7 and 0.16.9 and are written out in the entry); the other 94 are declared stubs (`alternatives` starts with `STUB`, `revisit` is labelled a default). The promotion gate in `check_catalogue.py` makes this binding where it matters: a rule whose maturity is beyond `proposed` fails validation unless its entry has `alternatives_checked` true and an `alternatives` text no other rule shares (`test_promotion_gate_rejects_a_stub_and_shared_alternatives`). Filling the 94 stubs is the price of promotion, paid rule by rule, not now.

**Lifecycle.** `proposed` (runs, effective level note) then `experimental` (fixtures and matrix pass) then `enforced` (an owner ledger entry approves the catalogue digest) then `deprecated` (`replaced_by`; the id stays). Agents and providers may add `proposed` rules and propose severity changes; they cannot make a rule `enforced`, change a severity, tier or exemption, edit `suppressions.json` or `baseline.json`, or append to the ledger. WV-098 detects that: each protected path has an owner-approved digest in the ledger, and a mismatch is an error. Honest limit: an agent with the owner's OS permissions can edit any file, including the ledger; the check reveals it in review and git history, and AGENTS.md says this is not a sandbox.

**ADR-lite versus ADR.** A full ADR is needed for a new relation, node type or link type, a new extractor or dependency, a kernel change, or a change to a stage contract. A rule, a message change or a promotion needs only a decision entry. A semantic change to a rule is a new id plus an entry, not an edit.

**Move checks left.** A lint rule that can never fire because the schema forbids the state should be deleted; a lint rule that keeps firing on a structural property should become a metamodel constraint and be generated. That is how WV-055 and WV-022 came about.

**Protected paths** (DESIGN): `graph/rules/catalogue.json` fields `severity`, `tier`, `maturity`, `params`; `graph/suppressions.json`; `graph/baseline.json`; `graph/ledger.jsonl`; the coverage, layer and exemption policy files; `graph/schema/metamodel.json`.

## 11. What humans and agents get

A text view of one finding (DESIGN; the numbers are the golden vector above):

```text
WV-010 requirement-without-verifier  fingerprint 38354b09...
  Requirement repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01 has 0 covered verifies links (needs 1).
  Scope searched: link.verifies into AC01: none.
  Why: every requirement needs a verifier (test, property, model check or witness); only COVERED links count.
  Re-check: template cardinality-min, reads node.requirement and covered_link.verifies, parameter min=1;
            run graph/rules/queries/WV-010.sql on graph/.index/graph.sqlite with the sqlite3 shell.
  Fix: add a verifies link from a verifier with a current digest. A SUSPECT link does not count until a human acknowledges it.
  Related: none.
```

For agents the same finding is the record in [rules.md](../../../graph/schema/rules.md) section 5 (structured `args`, `fingerprint`, `witness`, `fix`), exposed through the agents lane's read-only tools `violations(rule)`, `explain(finding)` and `link_status(link)`. Nothing is parsed from prose, and the fingerprint lets an agent see that a finding is the same one after it edited the file.

**What is claimed.** Nothing about effect size. Evidence that exists: in the SWE-agent ablation a linter guard on edits gave 18.0% versus 15.0% resolved on SWE-bench Lite (one paper, one benchmark, one model family [agent], fetch summary). Anything beyond that is a **PREDICTION**: that structured arguments and a re-checkable witness reduce misunderstood findings, and that a stable fingerprint reduces re-work. The measurement plan is the SYNTHESIS one: pre-registered tasks, pass^k, with and without diagnostics, run by the hci and eval lanes.

## 12. Schools of thought used here

| School | Mechanism in this design | Benefit | Cost and limit | Evidence and verdict |
|---|---|---|---|---|
| Stratified Datalog and relational algebra | violation queries; computed strata; no negation in recursion; closed-world guard by polarity (monotone findings survive missing facts, anti-monotone ones do not) | order-independent, terminating rules with declared polarity; a partial run cannot report a spurious absence | Datalog engine not used; polarity is declared and tested over exhaustive small worlds, not proved; the audit found 14 mis-declared rules, so a wrong declaration is a live risk | [B1], [B6], [S3], [S4]; **adopt (lite)** |
| Least fixed points | `affected`, `scc`, closure derivations; `impact.closure` as oracle | termination on cycles; result independent of visit order | monotone rules only; negation sits above | [math] M5 (0 mismatches over 300 graphs); **adopt** |
| Order theory (chain of verdicts) | `FAIL < NOT_RUN < PASS`, chain minimum | order-, thread- and shard-independent aggregation; skipped gates cannot look green | the position of NOT_RUN relative to UNKNOWN and STALE is an open owner question | exhaustive tests up to length 4 [B3]; **adopt** |
| Provenance and witnesses | every finding carries a witness (single, pair, path, scope, diff, counterexample) | "why" is a lookup and re-checkable | absence findings have no semiring explanation, their witness is the searched scope | [math] 2.3; **adapt** |
| Type theory | many-sorted edge signatures, closed sum types for level and verdict | ill-typed links fail at build; NOT_RUN is not a bool | signature upkeep, generated | [mde], metamodel; **adopt** |
| Content addressing and Merkle | relation-slice hashes as cache keys; domain-separated, length-prefixed fingerprint | change detection without clocks; boundary-safe identity | detects change, not truth | Doorstop collision [trace]; test vectors [B3]; **adopt** |
| Incremental computation (BSalC, Salsa) | per-rule key, early cutoff, `incremental == clean` | fewer re-runs when it matters | undeclared inputs; gain unmeasured at this size | [incr]; **adapt, off by default** |
| Group of differences (Z-sets) | baseline state as new/absent by fingerprint difference, in a view | deterministic new versus known classification | none at this size | [incr] 2.1; **adapt** |
| Term rewriting | fixes as disjoint rewrites; idempotence and bounded passes | deterministic multi-fix application | termination is not guaranteed in general, hence the cap | [incr]; **adapt** |
| Mutation and metamorphic-style testing | fire/repair/benign matrix and rule-source mutation | a rule that cannot fail is caught | fixtures are finite; killing power is a score, not a proof | ADR-0033, AGENTS.md; **adopt** |
| Category theory | only the two checks adopted elsewhere (view totality WV-028, overlap WV-062) | new types cannot vanish from views | nothing beyond those | [bx]; **theory-only** |
| Information theory, probabilistic assurance | none in the gates; precision reported as counts | avoids pseudo-precision | | [math] D7; **theory-only** |

## 13. Interfaces to other aspects and lanes

| Counterpart | I consume | I provide | Open |
|---|---|---|---|
| metamodel aspect (`graph/schema/metamodel.json`) | node and link types, supertypes, `max_in`, `max_out`, `acyclic`, `anchor_ends`, obligations with rule ids | the rule behind each obligation id: WV-010, 011, 031, 037, 053, 054 exist (a test checks it); template semantics | request: add obligations for WV-050, 051, 052, 056, 059, 063, 100; ids WV-053 (term without bounded context) and 054 (aggregate term without realiser) are taken as the metamodel uses them, WV-055 is the maximum template and WV-022 the acyclicity template |
| link and ledger aspects (allocation ADR-0093 and 0094) | `link_status(link, digest, ledger)`, ledger schema, actor grammar, approved digests | rules WV-005, 038, 075, 091, 097, 098 that need them | WV-080 and WV-097 wait on ADR-0094 |
| extractor aspect (allocation ADR-0095) | `extractor_run` (status, pins, produced relations), provenance labels | the closed-world guard and WV-006, 009, 084 | `ARCHITECTURE.md` section 11 allocates 0095 to the extractor protocol; this record was assigned the same number (open question 1) |
| store and query aspect (allocation ADR-0096) | SQLite schema, relation views, total `ORDER BY`, `finding` table | queries, the authorizer allow-list per rule | |
| determinism aspect (allocation ADR-0099) | permutation harness, D-01 to D-24, `harness_result` | WV-087, 088, 090 as consumers; the SARIF profile | |
| okf lane | `repo://` grammar, hash methods, STALE gate | request: `adr-body-v1` (WV-080), `json-key-v1` for rule pages, OKF pages of `type: Rule` | okf lane acceptance |
| quality lane | ruff pin and config, import-linter, `nox` tags, NOT_RUN convention, ratchet | `quality/sessions/graph.py`; banned-API list generated from `banned_apis` and checked, not written, into their `pyproject.toml`; import-linter and ruff findings ingested as separate SARIF runs, keeping their own rule ids | ruff pin is 0.16.9; the probes ran on 0.15.7 and were re-run on 0.16.9 with identical results |
| mutation lane | cosmic-ray engine, scratch copy, ratchet | target list and the killing suite | |
| property lane | Hypothesis strategies | polarity test, incremental-equals-clean generator | |
| visual lane | `semantic_hash` provenance comment, neutral models | WV-027, 060, 061, 062, 099 | |
| agents lane and agent-interface aspect | read-only MCP server; its proposal checker steps C1 to C8 | Finding schema, `violations`, `explain`; no write tool. Their C1 to C8 are rules here (C1 WV-002, C2 WV-001, C3 WV-047, C4 WV-007, C5 WV-048, C6 WV-049, C7 WV-098, C8 WV-006), so one implementation serves proposals and free-form edits. WV-048 and WV-049 are the two rule ideas that aspect asked for under exactly those ids | the agent-interface ADR calls this record 0097; see open question 1 |
| hci lane | Playwright and axe captures (one browser) | WV-032, 033, 034 | NOT_RUN without Chrome |
| tla, bend, smt-bmc | witness and checker registry | WV-038 to 041, 069 | |
| metrics lane | `eija.metrics.v1` | rule counts, precision counts, fixture cases | |
| kernel (`src/`) | nothing at runtime | nothing; `impact.closure`, `aggregate_status`, `assess_receipt` are test oracles only | |

## 14. Phases

| Phase | Rules | Exit criterion (measurable) |
|---|---|---|
| P1 (11) | WV-001 to 006, 009, 010, 043, 088, 090 | catalogue validates; the 11 rules pass their matrices; permutation harness gives one distinct output on Windows; `incremental == clean` on random edits; two clean rebuilds give one root |
| P2 (63) | link hygiene, coverage templates, language, architecture, views, static UI, ADR, static determinism, governance | goldens stable; every `may` rule has a reviewed precision count; suppression and baseline gates live |
| P3 (23) | assurance and evidence, rendered UI, dominators and redundancy, lens laws, WV-080 | every PASS prints its TCB label; a seeded weakened statement gives FAIL |
| P4 | promotion of rules to `enforced`; re-measure hash-method noise on EIJA history; benefit study with hci and eval | numbers with n, model id, date |

## 15. Limits, not measured, open questions

Not measured: precision of any rule (no labelled findings exist); the polarity of every rule against its real query (the audit in 2.5 was by reading statements, and the queries do not exist yet); per-rule alternatives (94 of 97 ADR-lite entries are stubs); rule cost on real EIJA data (the benchmark is synthetic); the wall-clock gain of the cache; POSIX byte-identity (only Windows run; WV-087 reports NOT_RUN for the POSIX comparison); effect on agents or humans; SHACL processors other than pySHACL; Soufflé (not runnable here); the Cypher text; the sqlglot polarity option.

Honest limits. A passing rule says "no violation found over the extracted facts", not that the software is right; a hash detects change, not truth; a proof about a model is not a proof about the code (WV-041, 066); the catalogue's `statement` fields are informational and are not the executed queries.

Open questions for the owner or the integrator:
1. **ADR numbers.** This record was assigned 0095, while `ARCHITECTURE.md` section 11 allocates 0095 to the extractor protocol and 0097 and 0098 to the rule model and the Finding/SARIF profile. Sibling aspects have meanwhile used 0093 (consistency and sync), 0097 (impact ranking and confidence, whose own note asks for a new number), 0099 (agent interface) a file first named 00101 (human views, now 0105) and a file first named 00103 (formal verification of the weave, now 0102), and the agent-interface design still calls the rules ADR 0097. ADR-0095 covers the rule model, the diagnostics and the rule governance (allocation 0097 and 0098); the integrator has to give every record a unique number in 0089 to 0112 and update the cross-references. Nothing in this design depends on the number.
2. Whether a `proposed` rule should be capped at `note` (this design) or be allowed to warn.
3. Whether unaccepted NOT_RUN should block the fast tier (the quality lane's audit session does).
4. Which suppression expiry kinds the owner accepts (all four are specified).
5. Whether the SARIF schema may be vendored (OASIS reuse terms UNVERIFIED); until then tests skip without it.
6. Which of the 7 proposed metamodel obligations the metamodel lane accepts.
7. Whether `WV-080` (accepted ADR rewritten) is worth a new hash method and an acceptance ledger entry.

Kernel change requests raised by this design: none. The `aggregate_status` non-associativity stays on the SYNTHESIS kernel-request list (open question 5 there); this design uses its own three-valued chain and does not depend on the fix.

## 16. Sources

| Key | URL or path | What I used |
|---|---|---|
| S1 | https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html | 3.4.4, 3.11, 3.14.27, 3.20.14, 3.27.9, 3.27.10, 3.27.16, 3.27.17, 3.27.23, 3.27.24, 3.35, 3.37.6, Appendix F |
| S2 | https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json | schema validation of the example (sha-256 c3b4bb2d...2682e; not vendored) |
| S3 | https://www.sqlite.org/lang_with.html | recursion restrictions, `UNION`, `LIMIT`, order |
| S4 | https://www.w3.org/TR/shacl/ ; https://souffle-lang.github.io/rules ; https://souffle-lang.github.io/install ; https://docs.astral.sh/ruff/rules/banned-api/ ; https://docs.astral.sh/ruff/faq/ ; https://import-linter.readthedocs.io/en/stable/contract_types/ ; https://docs.semgrep.dev/writing-rules/testing-rules ; https://rustc-dev-guide.rust-lang.org/diagnostics.html | statements quoted in sections 2, 6, 8, 9 (fetch summaries) |
| S5 | https://pypi.org/pypi/{pyshacl,rdflib,jsonschema,ruff,import-linter,cosmic-ray}/json ; GitHub API `repos/{RDFLib/pySHACL,souffle-lang/souffle,astral-sh/ruff,seddonym/import-linter,semgrep/semgrep,ast-grep/ast-grep,sixty-north/cosmic-ray}` | versions, licences, activity |
| S6 | https://github.com/45ck/proofmap-lite `docs/gap-audit.md` (private) | GAP-017, 018, 019, 027, 029 |
| S7 | `/c/Dev/eija-wt/{quality,okf,mutation}` ADRs and `quality/sessions/quality.py`; `graph/schema/metamodel.json`, `build_schemas.py` | conventions and interfaces |
