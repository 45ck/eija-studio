# Proof obligations of the weave

Lane: weave. Aspect: formal-verification-of-weave ([design](../../docs/weave/design/formal-verification-of-weave.md), [ADR-0103](../../docs/adr/00103-weave-formal-verification-of-weave.md)). Date: 2026-09-29. This file is the flat, checkable list. Each row is a property of the weave that must hold, the technique that closes it, its honest scope, and where it stands today. Nothing here says the production code is correct: `eijagraph` does not exist yet, so every "MEASURED" below is about a reference in `graph/formal/eijaref`, a sibling lane's reference file, or data files as they stood on this date.

## How to read a row

| Column | Meaning |
|---|---|
| Statement | What must be true, with hypotheses when a theorem is involved |
| Technique | The rung of the ladder: SCHEMA, ENUM (exhaustive, stated domain), CERT (certificate plus small checker), PAPER (proof in the design document), ALLOY (bounded), PROP (Hypothesis, derandomised), DIFF (two independent implementations), FAULT (fault injection), META (metamorphic relation) |
| Scope and label | The domain and the strength of the result: EXHAUSTIVE, CHECKED_BOUNDED, DIFFERENTIAL, TESTED, PROVED ON PAPER, GENERATED, DESIGN |
| Status today | MEASURED (a script ran, on the stated subject), NOT_RUN (a prerequisite is absent; never a pass), PENDING (needs `eijagraph` or another lane), DESIGN (specified, nothing to run) |
| Reproduce | A test or command; `T:` is a file under `tests/graph/formal/`, `B:` a check in `graph/bench/formal_checks.py` |

Status vocabulary for the whole file: an obligation is **discharged for an implementation** only when its suite ran on that implementation. Suites run on the references now. The production binding table ([binding.json](binding.json)) lists where each suite attaches; while a target module is absent its test reports NOT_RUN, not PASS.

Negative controls: every suite is also run against at least one deliberately wrong implementation and must fail (design section 10). A suite that accepts a wrong implementation is a FAIL of the suite (`graph/formal/selfcheck.py`).

## D: determinism

| ID | Statement | Technique | Scope and label | Status today | Reproduce |
|---|---|---|---|---|---|
| PO-D1 | The canonical writer is a function of the abstract value: dict insertion order is not observable (theorem T1) | PAPER, ENUM, PROP | 24 orders of a 4-key object; 300 seeded random dicts; Hypothesis: TESTED, PROVED ON PAPER | MEASURED on reference; metamodel aspect's `jcs_dumps` cross-checked on the pool and 2,000 random values; `eijagraph.canon` PENDING | T: `test_formal_canon.py`, `test_formal_properties.py`, `test_formal_crosscheck.py`; B: F3 |
| PO-D2 | The writer is injective on V (null, bool, integers within 2^53 - 1, scalar-value strings, lists, string-keyed objects) and refuses everything else (T2) | PAPER, ENUM, PROP | 282 hostile values, 0 collisions, 0 round-trip failures; 10 out-of-domain values refused; Hypothesis round trip: PROVED ON PAPER | MEASURED on reference; the kernel's `canonical()` collapses `{1:"a"}` and `{"1":"a"}` and `(1,2)` and `[1,2]` (why it is not reused) | T: `test_formal_canon.py`; B: F3, F3b |
| PO-D3 | On V the writer equals RFC 8785: the two RFC vectors reproduce and a second implementation agrees | ENUM, DIFF | RFC 3.2.2 string vector and 3.2.3 sort vector; 20,000 seeded random members of V against `rfc8785` 0.1.4: DIFFERENTIAL | MEASURED (needs `rfc8785`; otherwise NOT_RUN) | T: `test_formal_canon.py`; B: F3 |
| PO-D4 | Digests use a domain tag and a length-safe frame: `frame(tag, fields)` determines its arguments (T3) | PAPER, ENUM, PROP | 800 tuples, 800 distinct frames; plain concatenation collides on ("a","bc") and ("ab","c") | MEASURED on reference | T: `test_formal_canon.py`, `test_formal_properties.py` |
| PO-D5 | A root hash depends only on the set of records and sees every record (T4) | PAPER, ENUM, PROP, DIFF | Reference Merkle: 24 orders, 4 leaf changes; metamodel aspect's `graph_root`: 60 shuffles incl. key order, every node and edge of a 40-node, 90-edge graph | MEASURED on both; production PENDING | T: `test_formal_canon.py`, `test_formal_crosscheck.py` |
| PO-D6 | Stage-wise and end-to-end permutation invariance (file order, rule order, hash seed, TZ, locale, cwd, CRLF, threads, non-BMP) yields one output; the harness itself detects a seeded defect | PROP, META | Sensitivity control: 8 distinct outputs for a set-iteration pipeline over 8 `PYTHONHASHSEED` values, 1 for the sorted pipeline | Harness sensitivity MEASURED; the real harness (`eijagraph.harness`) PENDING | T: `test_formal_rules_lens_metamodel.py`; B: F8 |
| PO-D7 | Snapshot consistency: a build reads the git object store (or hashes on first read and re-checks the snapshot root); a moving tree gives NOT_RUN | FAULT | Edit a file mid-run and expect NOT_RUN | DESIGN | none yet |
| PO-D8 | Rebuilding twice from a clean checkout gives equal roots; incremental output equals clean output after random edit sequences | DIFF, PROP | Property lane strategies | PENDING (owned by the harness and incremental aspects) | none yet |
| PO-D9 | No wall clock, time zone, GUID, host name or absolute path in a committed artefact; no unsorted iteration or library-default order reaches output | ENUM (positive controls) | Rules WV-043, WV-044, WV-083, WV-085 (rules aspect) own the scan; this lane supplies seeded positive controls | PENDING | none yet |
| PO-D10 | Each hash method is invariant under edits that do not change the notion of "changed" (comments, CRLF, spacing, blank lines) and sensitive to edits that do (operator, rename, docstring, constant, default argument; signature for `ast-sig-v1`; any byte for `lf-sha256-v1`) | META | okf lane's `codelink.digest`, 5 invariance and 5 sensitivity relations plus signature and file relations | MEASURED (skipped as NOT_RUN if `codelink.py` is absent); one FINDING: a lone-surrogate string literal raises `UnicodeEncodeError` (`xfail(strict=True)`) | T: `test_formal_hash_methods.py` |

## G: graph computations

| ID | Statement | Technique | Scope and label | Status today | Reproduce |
|---|---|---|---|---|---|
| PO-G1 | The impact closure is the least fixed point of `X -> R union succ(X)`. A closure certificate (C, rank, parent) that passes (a) R in C, (b) parent edge exists, parent in C, rank decreases, (c) C forward-closed, proves C = lfp (Theorem C) | PAPER, ENUM, ALLOY | All 2^16 digraphs with self-loops on 4 nodes x 16 root sets = 1,048,576 cases: kernel, Kleene, Warshall, BFS certificate: EXHAUSTIVE; Alloy scope 7: CHECKED_BOUNDED | MEASURED: 0 mismatches; impact aspect's `closure` also passes | T: `test_formal_closure.py`, `test_formal_crosscheck.py`; B: F1; Alloy: `alloy/certificates.als` |
| PO-G2 | A closure witness is re-checkable without redoing the closure: a path (positive) and a forward-closed set (negative). Each condition of the checker is necessary | CERT, ENUM, ALLOY | Real checker: 5,184 candidates exhaustive on 2 nodes, 60,000 perturbations; 5 of 5 mutants have a counterexample in Python (3 nodes) and Alloy (7) | MEASURED | T: `test_formal_closure.py`, `test_formal_tools_and_drift.py`; B: F1c |
| PO-G3 | SCC labels are the canonical partition: minimum-member labels, classes strongly connected inside, acyclic quotient (Theorem S); the checker accepts exactly that labelling | PAPER, CERT, ENUM, ALLOY | 65,536 digraphs on 4 nodes; 13,824 labelings on 3 nodes; Alloy scope 6 with two mutants; library default (`nx.condensation`) gave 5 labellings over 60 orders, all rejected as non-canonical | MEASURED; impact aspect's `scc_labels` passes | T: `test_formal_order_and_status.py`, `test_formal_crosscheck.py`; B: F4, F4b |
| PO-G4 | The lexicographically smallest topological order is unique; the checker accepts exactly it | CERT, ENUM | All 4,096 loopless digraphs on 4 nodes (543 acyclic) against the brute-force minimum over permutations | MEASURED | T: `test_formal_order_and_status.py`; B: F4 |
| PO-G5 | The kernel's budgeted closure returns a subset of the true closure, `complete` implies equality, `frontier` lies in the closure | ENUM | 20,480 cases (3-node graphs x root sets x budgets 0 to 4) | MEASURED, 0 violations | T: `test_formal_closure.py`; B: F1b |
| PO-G6 | A SQLite recursive CTE with `UNION` equals the reference closure, and a truncating LIMIT is detected (ask for LIMIT + 1), never returned as a shorter answer | ENUM, FAULT | 4,096 cases; a 51-node chain with LIMIT 10 inside the recursive select returned 10 rows | MEASURED; production query PENDING (`eijagraph.store:closure` binding) | T: `test_formal_closure.py`; B: F1, F5 |

## S: status and link algebras

| ID | Statement | Technique | Scope and label | Status today | Reproduce |
|---|---|---|---|---|---|
| PO-S1 | The join of evidence for one check is commutative, associative, idempotent with identity NOT_RUN, so it is a function of the set for every list length | ENUM (finite reduction), PAPER | 36 pairs, 216 triples: EXHAUSTIVE; extended to all lengths by the reduction | MEASURED | T: `test_formal_order_and_status.py`; B: F2 |
| PO-S2 | A gate (meet across required checks) is PASS iff it is non-empty and every input is PASS, for every chain with PASS on top; NOT_RUN absorbs PASS; the empty gate is NOT_RUN (Theorem G) | PAPER, ENUM | 120 chains x multisets of size 1 to 4: EXHAUSTIVE, 0 violations | MEASURED; impact aspect's `fold_b` and rules aspect's `fold_verdicts` pass the same predicate | T: same, `test_formal_crosscheck.py` |
| PO-S3 | Claim status = meet over required checks of the join over each check's evidence; a required check without evidence, and a claim with no required checks, are never PASS | ENUM | 64 + 64^2 + 64^3 = 266,304 combinations | MEASURED, 0 violations | B: F2 |
| PO-S4 | The join equals the kernel's `aggregate_status` on every flat list; the kernel does not compose (flat CONFLICT, rolled-up FAIL) | ENUM, DIFF | 5,460 flat sequences of length 1 to 6 over 4 statuses (kernel present) | MEASURED; kernel fix needs its own ADR | T: `test_formal_order_and_status.py` |
| PO-S5 | `link_status` laws LS1 to LS6: total and deterministic; COVERED only with a matching digest or an ack for exactly (link, digest); acks are local; an ack clears SUSPECT only; monotone in the ledger; UNRESOLVED is never COVERED | ENUM, META | 5 observations x 16 ack sets x 4 extra acks; 3 wrong implementations caught | MEASURED on the reference decision table; production PENDING (`eijagraph.links` binding) | T: `test_formal_order_and_status.py`, `test_formal_tools_and_drift.py` |
| PO-S6 | The lift map sends only COVERED to PASS: a link fold is PASS iff every link is COVERED | ENUM | All 120 chains x pairs of link statuses | MEASURED | T: `test_formal_order_and_status.py` |
| PO-S7 | The ledger is grow-only: entries(base) is a subset of entries(head); merges are set unions; an ack binds the exact subject digest | ENUM, DIFF | Set laws are trivial; the git check is a diff gate | DESIGN (ADR-0093 defines the ledger); PENDING | none yet |

## M: metamodel and rules

| ID | Statement | Technique | Scope and label | Status today | Reproduce |
|---|---|---|---|---|---|
| PO-M1 | Table lemmas hold: no unknown or empty signature side (MM-002, MM-003), no isolated node type (MM-004), no obligation whose scope is not on its side (MM-020), no minimum above a maximum (MM-021), every obligation's rule exists in the catalogue (MM-022), no supertype clash or unknown member (MM-023, MM-024), unique domain tags (MM-025) | ENUM | `graph/schema/metamodel.json`: 42 node types, 29 link kinds, 6 minimum obligations: 0 findings; the prose brief (37 and 27) gave 17 findings, all gone | MEASURED | T: `test_formal_rules_lens_metamodel.py`; B: F9 |
| PO-M2 | The metamodel is satisfiable and not vacuous: an instance with every node type inhabited and every minimum obligation met exists | CERT (constructive witness), DIFF | 42 nodes, 6 edges, accepted by two independent checkers; one demand chain of depth 2 (WV-031 then WV-037) | MEASURED; a solver is required only past the trigger in the design (7.1) | T: same; B: F9 |
| PO-M3 | Rule strata equal the catalogue's formula; negative reads are over strictly lower strata; the catalogue is stratifiable (no negation through recursion), assuming stratum-3 output feeds `finding3` | ENUM, DIFF | 97 rules, 0 problems; two controls (a wrong stratum; stratum-3 output fed to `finding`) caught | MEASURED | T: same; B: F9 |
| PO-M4 | Each rule can fire and can be silent (non-vacuity), and the rule set is jointly satisfiable, on the fragment that has an IR; every solver fixture replays in the implementation | ALLOY, DIFF (clingo bridge) | 4 pilot programs, 4 minimal fixtures of 1 fact, dead-rule control; Alloy pilot 3 of 3 | PILOT MEASURED; catalogue-level PENDING (fire, repair, benign matrix is the rules aspect's: 378 minimum cases) | T: same; B: F5b; Alloy: `alloy/rule_uncovered.als` |
| PO-M5 | Two evaluators agree: the production rule engine and the reference IR evaluator return the same findings (release tier); disagreement is FAIL | DIFF | Pilot: reference against SQLite, 4 programs x 200 seeded fact sets, 0 mismatches; against clingo, 4 x 100, 0 mismatches | PILOT MEASURED; production PENDING | B: F5, F5b |
| PO-M6 | Stratified evaluation terminates; monotone rules are monotone; negation is not, so negative reads need the closed-world guard | ENUM, PROP | 200 random graphs; a two-fact example | MEASURED | T: same |
| PO-M7 | The metamodel aspect's `check_document` equals an independent instance checker on signature typing, qualifiers, self-loops, dangling ends, duplicates, `max_in`, `max_out` and acyclicity | DIFF | 600 seeded random edge sets, 540 with findings, 6 codes exercised | MEASURED, 0 mismatches | B: F9 |
| PO-M8 | The rules aspect's verdict guard (revised by that aspect during this work) is correct: a finding on partial input is FAIL only when the rule's finding set is monotone in the incomplete relations; a rule that reads an incomplete relation anti-monotonically (negation, anti-join, count below a minimum) or lacks a prerequisite is NOT_RUN whatever it found; PASS only with no finding, every prerequisite and no incomplete read; the verdict fold is PASS iff all PASS and NOT_RUN never hides FAIL; the empty run is NOT_RUN | ENUM | 3 finding counts x 2 prerequisite states x 3 read effects = 18 guard combinations; 3-valued multisets up to size 4 | MEASURED. FINDING: `exit_code(NOT_RUN, not_run_accepted=True)` is 0 and the flag comes from an environment variable | T: `test_formal_crosscheck.py` |

## L: lenses, views, merges

| ID | Statement | Technique | Scope and label | Status today | Reproduce |
|---|---|---|---|---|---|
| PO-L1 | The partial-lens law checker (GetPut requires acceptance of the no-op edit; PutGet and PutPut only where `put` accepts; view comparison may ignore layout) is valid: it reproduces the paper's three counterexamples | ENUM | 3 of 3, each tripping exactly the expected law | MEASURED | T: `test_formal_rules_lens_metamodel.py`; B: F6 |
| PO-L2 | Every view lens (transformation card T2, laws L1 to L10 of ADR-0093) satisfies GetPut, PutGet modulo layout and declared amendments, and conditional PutPut on its alphabet | ENUM, PROP | Owned by the consistency aspect (ADR-0093); to be run through `check_lens_laws` | NOT_RUN here | none yet |
| PO-L3 | Get-only projections (cards T1, T3, T4, T5, T6, T11: OKF pages, diagrams, SysML text, UI projection, exports; laws G1 to G7, C1 to C4) are total and deterministic; every semantic type is drawn or `not_shown`; a model path maps to a view path | PROP, ENUM | Golden per projection; mapping totality | PENDING | none yet |
| PO-L4 | The keyed three-way merge is symmetric, has identity and idempotence, is associative where defined, and is defined iff at most one distinct value differs from the base | ENUM (finite reduction), DIFF | 256 single-key cases stand for every alphabet and key count; key-wise independence tested on 400 random 5-key records | MEASURED on the consistency aspect's `merge3`, 0 violations | T: `test_formal_crosscheck.py` |

## T: trust boundary

| ID | Statement | Technique | Scope and label | Status today | Reproduce |
|---|---|---|---|---|---|
| PO-T1 | Non-interference: a verdict does not depend on any agent-supplied field (proposals, transcripts, self-reported status, tool descriptions) | META | Mutate agent-only fields arbitrarily; require identical verdicts | PENDING | none yet |
| PO-T2 | `partial`, `candidate(n)` and `unresolved` facts cannot satisfy a gate; a second extractor agrees on a sample | FAULT, DIFF | `has_error` fixture; ast against tree-sitter (167 of 167 definitions [code]) | PENDING; the 167 of 167 is the code dossier's measurement | none yet |
| PO-T3 | The checker reads the original bytes itself, not the producer's cache ([CERT] 6.2) | FAULT | Tamper the cache; expect FAIL or NOT_RUN | DESIGN | none yet |
| PO-T4 | The kernel package imports only the standard library and itself, and stays inside a line budget | SCHEMA (import contract), ratchet | Reference package: stdlib only, no `eijagraph` or `eija_studio` import, no wall clock, no randomness: tested; sizes 205 statement lines in six components | MEASURED for `eijaref`; production PENDING (quality and metrics lanes) | T: `test_formal_tools_and_drift.py`; B: F7 |
| PO-T5 | External tools are accepted only on an exact sentinel plus exit code plus pinned sha256; a missing or wrong tool is NOT_RUN; a model without `expect` clauses cannot pass | FAULT | Runner: missing jar, wrong digest, no expect, wrong expectation, right expectation | MEASURED | T: `test_formal_tools_and_drift.py` |
| PO-T6 | The stage-0 self-check reports without the machinery it judges, and fails a suite that accepts a wrong implementation | FAULT | 5 suites, 7 wrong implementations | MEASURED (0.5 s) | `python graph/formal/selfcheck.py` |
| PO-T7 | Any exception in an extractor, hash method or rule fails closed: NOT_RUN or FAIL, never PASS and never silence | FAULT | Inject a raise in each stage | DESIGN; a live case: PO-D10 finding | none yet |

## X: drift between models and code

| ID | Statement | Technique | Scope and label | Status today | Reproduce |
|---|---|---|---|---|---|
| PO-X1 | A generated model or schema equals a fresh regeneration | GENERATED | Metamodel aspect's `build_schemas.py --check` | Not this lane's file; consumed | `python graph/schema/build_schemas.py --check` |
| PO-X2 | Behavioural agreement between a model and the code it describes on exhaustive small scope | DIFF | Reference against kernel, SQLite, sibling references (see G, S, M rows) | MEASURED where a reference exists | see rows |
| PO-X3 | A `conforms_to` link (implementation `ast-v1` digest plus model digest) and a `proves` link (statement pinned by `law-block-v1`) in the weave itself flip to SUSPECT when either side changes | DESIGN | Dogfooding, needs `eijagraph.links` | DESIGN | none yet |
| PO-X4 | Named-condition parity: Alloy predicates and mutants and Python condition tokens and mutants coincide | ENUM (name parity) | 5 closure conditions, 5 mutants, 2 SCC conditions | MEASURED | T: `test_formal_tools_and_drift.py` |
| PO-X5 | Formal tools are pinned by sha256 and size; NOT_RUN semantics hold | SCHEMA | `TOOLS.lock` (Alloy 6.2.0, clingo 5.8.2, Hypothesis 6.168.3) | MEASURED | T: `test_formal_tools_and_drift.py` |

## Production bindings

[binding.json](binding.json) maps eight law suites to the functions they must run against once `eijagraph` exists. Signatures are the adapter forms documented in `eijaref/suites.py`. All eight report NOT_RUN today. The rows that must go green first, in this order: canonical writer, closure, SCC and order, status fold, `link_status`.

## Claims made by sibling lanes that this lane did not re-verify

| Claim | Owner | Why not |
|---|---|---|
| Personalised PageRank error bound and ordering certification; greedy set cover ratio; context selection at least half the optimum | Impact aspect (ADR-0097), oracle file `math-oracles.md` | Rational-arithmetic oracles exist there; no independent second implementation was written |
| Lens law suite catches four seeded broken translators | Consistency aspect (ADR-0093) | The per-view suites are theirs (PO-L2) |
| Rule precision, fixture matrix of 378 minimum cases, SARIF profile validity | Rules aspect (ADR-0095) | Catalogue-level dynamic checks need the rule engine |
| Hash-method stale rates (1.5 to 9.4% per change on two repositories) | Traceability dossier | Sensitivity measured elsewhere, not re-run on EIJA |

## Adding an obligation

1. State it as a property with hypotheses; say which failure it prevents (a false PASS route from design section 3.2, or a determinism channel).
2. Choose the cheapest rung that closes it (design section 1): schema, enumeration, certificate, Alloy, property test, differential; a machine-checked proof only past the trigger.
3. Write the suite so it takes the implementation as a parameter, run it on a wrong implementation, and bind it in `binding.json`.
4. Give it a status honestly: a suite that ran on a reference is MEASURED on that reference, not discharged for the product.
5. If a model is involved, add its drift guard (design section 9) in the same change.
