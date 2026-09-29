# Formal verification of the weave: what is proved, what is checked, what is trusted

Lane: weave. Aspect: formal-verification-of-weave. Date: 2026-09-29. Status: DESIGN for [ADR-0103](../../adr/00103-weave-formal-verification-of-weave.md), with the measurements below run on the reference PC (Windows 11, Python 3.12.10, SQLite 3.49.1, Temurin 17.0.19; POSIX not run). Obligation list with status and commands: [graph/formal/OBLIGATIONS.md](../../../graph/formal/OBLIGATIONS.md). Benchmark check ids F1 to F9 refer to `graph/bench/formal_checks.py`; test ids to `tests/graph/formal/`. Nothing in `eijagraph` exists yet; every result below is about the independent references in `graph/formal/eijaref`, the sibling lanes' reference files, and the metamodel and catalogue data as they stood today.

Labels: MEASUREMENT (a script ran; domain stated), PREDICTION (reasoned, not run), DESIGN (a proposal), PROVED ON PAPER (proof in this document, hypotheses stated, not machine-checked), UNVERIFIED (not opened or not confirmable; nothing is built on it), NOT_RUN (a prerequisite is absent). A proof about a model is not a proof about the code: conformance is a separate claim with its own label.

Source keys. Opened this session (2026-09-29): [RFC] rfc-editor.org/rfc/rfc8785 (page and .txt); [PYJSON] docs.python.org/3/library/json.html; [PYCLI] docs.python.org/3/using/cmdline.html (`PYTHONHASHSEED`); [SQLITE] sqlite.org/lang_with.html; [FOSTER] Foster, Greenwald, Moore, Pierce, Schmitt, TOPLAS 2007 (cis.upenn.edu/~bcpierce/papers/lenses-toplas-final.pdf, text extracted); [CERT] McConnell, Mehlhorn, Naher, Schweitzer, "Certifying algorithms" (people.mpi-inf.mpg.de/~mehlhorn/ftp/CertifyingAlgorithms.pdf, text extracted); [ALLOY] github.com/AlloyTools/org.alloytools.alloy (README, LICENSE, releases through `gh api`), alloytools.org/alloy6.html, alloytools.org/about.html, alloy.readthedocs.io/en/latest/language/commands.html, and the jar's own `--help`; [CLINGO] potassco.org/clingo and github.com/potassco/clingo (LICENSE.md head, releases); [Z3] github.com/Z3Prover/z3 (LICENSE.txt head, releases) and PyPI `z3-solver` 5.1.0.0; [HYP] hypothesis.readthedocs.io (settings, `derandomize`) and PyPI metadata plus LICENSE head; [DL] en.wikipedia.org/wiki/Datalog; [NIST] csrc.nist.gov/pubs/sp/800/185/final (abstract only); [GH] GitHub API records (`gh api repos/...`: licence, archived, pushed). In-repo: the kernel (`src/eija_studio/domain/{impact,evidence,models}.py`), the twelve dossiers ([assure], [math], [bx], [trace], ...), `docs/weave/ARCHITECTURE.md`, and the sibling aspects' ADRs 0089, 0091, 0093, 0095, 0097, 0099, 00101 with their reference files (read-only). Sibling worktrees `tla`, `bend`, `smt-bmc`, `property`, `okf` (read-only).

## 0. Decisions first

| # | Decision | Confidence | Basis |
|---|---|---|---|
| 1 | Verify the weave with a **ladder**, cheapest rung that closes each property: schema, then exhaustive enumeration of a small domain (zero extra trust), then a certificate plus a small checker, then Alloy for bounded relational statements, then property tests and differential runs against an independent implementation. Machine-checked proofs (Lean, Bend) are deferred behind a measurable trigger. | High | Sections 2 to 8; every rung was exercised |
| 2 | **The trusted kernel is about 200 statement lines of stdlib Python plus one hash-method registry**, listed in section 3.3. Everything else, extractors, SQLite queries, networkx, tree-sitter, agents, providers, Alloy, clingo, Neo4j, OKF pages, is untrusted and either recomputed by the kernel or cross-checked. Reference sizes are measured: closure checker 22 lines, SCC checker 41, topological-order checker 16, status algebra 12, canonical writer 41, rule stratifier plus evaluator 73 (205 in all). The production kernel is a PREDICTION of the same order plus `link_status`, the reader and the ledger check. | Medium (size), High (list) | Check F7 of `graph/bench/formal_checks.py`; [CERT] section 6 (LEDA: matching module 280 lines, checker 26) |
| 3 | **Certificates where the producer is complicated, N-version where it is not certifiable.** Closure, SCC and topological order get certificates (path or closed set; partition; order). Rule evaluation gets two evaluators that must agree on the release tier. Extractor fidelity is not certifiable and is labelled TESTED with provenance classes. | High | Section 3.4 |
| 4 | **Alloy 6 is the bounded-statement checker; Z3 is not used in phase 1; clingo is a test-time bridge for rule fixtures.** Alloy checked the certificate theorems and their five mutants (11 commands, 15.8 s to 23.6 s with Glucose, 216 s to 230 s with SAT4J). The metamodel needs no solver today: a constructive instance with 42 nodes and 6 edges is accepted by two independent checkers. | High for the choice today, Medium as a permanent choice | Sections 5.3 and 7.1 |
| 5 | **Determinism is argued compositionally and tested twice.** Four small theorems (writer, injectivity, framing, root) cover the last steps; a permutation harness covers the rest; the harness is itself tested for sensitivity (a seeded set-iteration defect gave 8 distinct outputs over 8 hash seeds, the sorted variant 1). | High | Section 4 |
| 6 | **The gate predicate does not depend on the owner's choice of chain.** For all 120 orders of the five non-PASS values below PASS, a fold is PASS iff every input is PASS; an empty gate and a required check without evidence are never PASS. Only the printed label depends on the chain. | High (exhaustive) | Section 6 |
| 7 | **Drift between a model and its code is guarded by five mechanisms and never by a claim.** Regeneration byte-compare for generated models; a named-condition parity between Alloy and Python; differential runs on exhaustive small scope; digest-pinned `conforms_to` links in the weave itself; bilateral mutation controls. The label stays CONFORMS_BOUNDED. | High | Section 9 |
| 8 | **Independent re-verification of sibling lanes found five concrete items** (section 11): a NOT_RUN acceptance flag that an agent can set, a canonical writer that accepts tuples, a hash method that crashes on a lone-surrogate literal, two representational differences in the status join, and stricter key domains that are safe but undocumented. No false-PASS was found. | High | Section 11 |
| 9 | **A stage-0 self-check** (`graph/formal/selfcheck.py`, 0.5 s) reports on the kernel without using the machinery it judges. A suite that accepts a wrong implementation is itself a FAIL. | High | Section 3.6 |
| 10 | Not claimed: correctness of extractors, that a rule expresses its intent, that a hash method's normal form is the right one, POSIX byte identity, any benefit to agents or humans. | High | Section 12 |

## 1. What "verified" means here

A gate has one dangerous error: a **false PASS**. A false FAIL costs time, a false PASS lets a defect through. So the question for every component is "can a bug in this code produce PASS when the input violates a rule?". NOT_RUN absorbing PASS removes the missing-prerequisite route; the rest is the trusted kernel.

| Label | Meaning | What it is worth |
|---|---|---|
| PROVED ON PAPER | A proof with hypotheses stated in this document | A statement about the model of the checker, only as reliable as the proof reading |
| EXHAUSTIVE(domain) | Every element of a stated finite domain was checked | A proof for that domain; a proof for all sizes only when a finite reduction is argued (sections 5, 6, 8) |
| CHECKED_BOUNDED(scope) | Alloy found no counterexample within a stated scope | No counterexample up to the scope, [ALLOY]: "All alloy models are bounded" |
| DIFFERENTIAL | Two independently written implementations agree on a stated set | Catches a slip in either; blind to a shared misreading of the specification |
| TESTED | Property tests (Hypothesis with `derandomize=True`: "every run will test the same set of test cases until you update Hypothesis, Python, or the test function" [HYP]) or seeded samples | A sample |
| GENERATED | A generated file equals a fresh regeneration byte for byte | Freshness, not truth |
| NOT_RUN | A prerequisite is absent | Never PASS |

Two rules apply to every claim below. First, a bounded or sampled result is never worded as a proof. Second, every check that can fail has a **negative control**: a deliberately wrong implementation the check must catch. Section 10 lists them; a suite that cannot fail proves nothing.

## 2. The properties and the technique for each

Full list with ids, commands and status: [OBLIGATIONS.md](../../../graph/formal/OBLIGATIONS.md) (47 obligations, seven groups). The groups, the technique and why that rung:

| Group | Property (short) | Technique | Tool (licence) | Scope and label | Why not a higher or lower rung |
|---|---|---|---|---|---|
| D determinism | Canonical writer is a function of the value; injective; RFC 8785 on the subset; framing injective; root depends on the record set; stage-wise and end-to-end permutation invariance; snapshot consistency; rebuild-twice and incremental-equals-clean; hash-method invariance and sensitivity | Four paper theorems, exhaustive pools, Hypothesis, differential against `rfc8785`, permutation and seed harness | stdlib, Hypothesis (MPL-2.0), rfc8785 0.1.4 (Apache-2.0) | Pool of 282 hostile values, 24 orders, 20,000 random values: EXHAUSTIVE and DIFFERENTIAL; the rest TESTED | The value space is infinite (strings): enumeration cannot close it, so the injectivity proof is on paper and enumeration checks it |
| G graph | Closure is the least fixed point; a witness is re-checkable; SCC labels canonical; topological order canonical; budgeted closure is a prefix; SQL closure equals the reference | Certificate plus checker; exhaustive over all digraphs on 4 nodes; Alloy to scope 7 | stdlib, Alloy 6.2.0 (MIT per LICENSE header) | 1,048,576 cases: EXHAUSTIVE; Alloy CHECKED_BOUNDED | 2^49 graphs on 7 nodes cannot be enumerated (5.6 x 10^14); SAT can |
| S status | Join lattice laws; gate is PASS iff all PASS for every chain; two-level claim status; agreement with the kernel; `link_status` laws; lift map; ledger monotone | Finite reduction plus exhaustive enumeration | stdlib | 6 values, 216 triples, 120 chains, 266,304 combinations: EXHAUSTIVE | The domain is finite: a solver would add trust and nothing else |
| M metamodel and rules | Table lemmas; a constructive satisfying instance; strata recomputed; catalogue stratifiable; rule non-vacuity; two-evaluator agreement; termination and the LIMIT guard; verdict guard | Set operations, constructive witness, SCC stratifier, clingo and Alloy pilots, differential SQLite against the reference evaluator | stdlib, clingo 5.8.2 (MIT), Alloy | Metamodel 42 types, 29 kinds, 6 obligations; 97 rules: EXHAUSTIVE on the tables, DIFFERENTIAL on instances | Obligations do not interact deeply yet (one chain of depth 2); a solver is warranted only past a stated trigger (7.1) |
| L lenses | The partial-lens law checker is valid; each view lens satisfies GetPut, PutGet (modulo layout) and conditional PutPut on its alphabet; get-only projections are total and deterministic; keyed merge laws | Checker validated on the paper's own counterexamples; exhaustive alphabets; finite reduction for `merge3` | stdlib | 3 of 3 paper controls; 256 cases for `merge3` | Views are owned by the consistency aspect; this lane supplies the checker |
| T trust | Verdict is independent of agent-supplied fields; checker reads the original bytes; kernel imports only the stdlib and stays under a size budget; external tools are accepted only on exact sentinel plus exit code plus pinned digest; any exception fails closed | Metamorphic tests, import contract, adapter contract tests, fault injection | import-linter (quality lane), stdlib | Runner contract MEASURED; the rest DESIGN | Needs `eijagraph`, which does not exist |
| X drift | Models stay in step with the code they describe | Section 9 | Alloy, pins, mutation | CONFORMS_BOUNDED at best | A proof about a model is not a proof about the code |

## 3. The trusted-kernel boundary

### 3.1 Actors

| Actor | Trusted? | May | May not | How it is held to that |
|---|---|---|---|---|
| Extractors (ast, tree-sitter, LibCST, SCIP, LLM link recovery) | No | Emit facts with a provenance label | Decide a status, clear a link, satisfy a gate | The kernel recomputes every digest a verdict depends on from the raw bytes; `partial` cannot PASS (D-14) |
| SQLite index and rule SQL | No (checked) | Answer queries | Be believed on absence | Closure by certificate; rule results by a second evaluator on the release tier; total `ORDER BY`; LIMIT truncation is a finding |
| Agents and providers | No | Read through bounded tools, propose | Approve, apply, write the ledger or policy, mint receipts | No tool exists for it (ADR-0099); verdict independence tested by metamorphic test (PO-T1) |
| networkx, rustworkx, tree-sitter, LibCST | No | Serve as test oracles or phase-2 adapters | Enter a verdict without a check | Oracle role only in this lane (`networkx` 3.5 measured to give 5 labellings over 60 orders) |
| Alloy, clingo, Z3, TLC, Bend | No | Verify the design, produce witnesses | Sit in the path of a verdict | Sentinel, exit code, pinned sha256; a missing tool is NOT_RUN |
| Neo4j, OKF pages, SARIF views, diagrams | No | Present | Feed back | Get-only projections; Neo4j only as an optional export and a differential closure check (ADR-0091) |
| The kernel (section 3.3), the reader, the protected policy | Yes | Decide | Nothing else | This section |
| The owner | Yes | Append ledger entries, approve statement digests, decide policy | n/a | Kernel capability; ledger is a grow-only set (ADR-0093) |

### 3.2 How a false PASS can arise and what stops each route

| # | Route | Example | Guard | Residual (label) |
|---|---|---|---|---|
| R-1 | A wrong fact | The parser drops a function, so a link to it looks fine | Provenance labels; `partial` never PASSes; a second extractor on a sample (ast versus tree-sitter agreed on 167 of 167 definitions [code]) | Fidelity is not certifiable: TESTED |
| R-2 | A wrong derivation | The CTE misses a node | Closure certificate; the same closure from a second engine; total `ORDER BY`; the LIMIT probe (section 5.4) | EXHAUSTIVE on 4 nodes, CHECKED_BOUNDED on 7 |
| R-3 | A wrong rule | The query does not express the intent | Fixture matrix (fire, repair, benign), rule-source mutation, templates generated from the metamodel | Intent is a human reading: owner-protected policy |
| R-4 | A wrong fold | A skipped check lets the gate pass | Section 6: PASS iff all PASS, empty gate is NOT_RUN, required check without evidence is not PASS | EXHAUSTIVE |
| R-5 | A wrong hash or serialisation | Two records share bytes; a change is invisible | Theorems T1 to T4; hash-method metamorphic tests | PROVED ON PAPER plus EXHAUSTIVE; the normal form's adequacy is a choice |
| R-6 | An accepted NOT_RUN | An environment flag turns NOT_RUN into exit 0 | See section 11, item 1: acceptance must be a ledger entry, never an environment variable, and never on the release tier | DESIGN (open) |
| R-7 | A stale or forged input | The checker reads a cache the producer wrote | The checker reads the original bytes itself ([CERT] 6.2: "in order to check the output of a sorting algorithm, it does not suffice to verify that the output list is sorted"; the checker must see the unmanipulated input); double read against the snapshot root | DESIGN |
| R-8 | An exception | A hash method raises and the run is treated as clean | Fail closed: any exception in an extractor, hash method or rule is NOT_RUN or FAIL, never silence; fault injection per stage | DESIGN; a live case exists (section 11, item 3) |
| R-9 | A weakened rule, policy or ledger | An agent edits a rule until it passes | Protected policy pinned by owner-approved digest; ledger grow-only; file-diff gate | OS-level tampering is out of scope (AGENTS.md: not a sandbox) |
| R-10 | A tool answer believed | A solver or checker output is trusted | Exact sentinel plus exit code plus pinned sha256; second checker for proofs; negative control per model link | Solver soundness stays in the residual |

Assumptions the argument rests on (each is a residual, not a guard): A-SHA SHA-256 is collision resistant; A-PY CPython, `hashlib`, `json`, `sqlite3` behave as documented; A-GIT reads from the git object store return the committed bytes; A-POLICY the owner-approved policy digests are the owner's; A-OS no adversary has OS write access to the kernel files; A-SPEC the catalogue expresses the intent; A-EXTRACT extractors are right within their provenance label.

### 3.3 The kernel list and its measured size

| Component | Role | Reference (statement lines, MEASUREMENT F7) | Verified by |
|---|---|---|---|
| Reader | Bytes from the git object store, LF fold, repo-relative POSIX paths | not built | PO-T3, PO-D7 |
| Canonical writer and framing | RFC 8785 subset; length-safe, domain-separated digests | 41 | T1 to T4, sections 4.1 to 4.4 |
| Hash-method registry (okf lane) | What a change is: `ast-v1`, `ast-sig-v1`, `ast-api-v1`, `lf-sha256-v1`, table and term methods | not measured | PO-D10 (metamorphic) |
| `link_status`, lift, ledger check | The only clearing act is a human ledger entry for the exact digest | about 10 (PREDICTION) | PO-S5, PO-S6, PO-S7 |
| Status fold | join, meet, claim | 12 | Section 6 |
| Closure and witness checker | Positive path or closed set | 22 | Section 5 |
| SCC and order checkers | Canonical labels and order | 41 + 16 | Section 5 |
| Rule evaluation | Stratifier, verdict fold, second evaluator | 73 (reference evaluator) | Section 7 |
| Total | | 205 measured, plus about 100 to 150 unbuilt | |

The size is what matters for review: [CERT] argues that a checker "should be so simple that the question of having a correct checking program is not really an issue" and reports LEDA checkers of 26, 35 and 95 lines; ours are the same order.

Enforcement (DESIGN, interface to the quality lane): the kernel modules live in one package that may import only the stdlib and itself (an import-linter contract); a line budget on that package is a ratchet in the metrics lane; a change to it needs an ADR.

### 3.4 Certificates and re-checks

A certificate is a witness that a small checker verifies without redoing the work ([CERT]: "the checker accepts the triple (x, y, w) if and only if w is a valid witness for the equality y = f(x)").

| Kind | Claim | Witness | Checker accepts iff | Theorem | Status |
|---|---|---|---|---|---|
| closure-path | C is the closure of R in E | C, rank on C, parent on C minus R | (a) R in C, (b) each parent is a member, an edge, of smaller rank, (c) C is forward-closed | C = lfp (5.1) | MEASURED |
| closure-cut | t is not affected | The closed set C | R in C, C forward-closed, t not in C | t not in lfp | MEASURED |
| scc-partition | label is the canonical SCC labelling | label | total, minimum-member, each class strongly connected inside itself, quotient acyclic | classes = SCCs (5.2) | MEASURED |
| topological-order | order is the lexicographically smallest | the order | permutation, edges forward, each element the minimum available | unique canonical order | MEASURED |
| finding-derivation | A finding follows from declared facts | rule id, premises, path | premises exist, each hop is a link | re-run on the witness subgraph | DESIGN (rules aspect) |
| solver-witness | A model or proof exists | file, sentinel | second checker or negative control | per link kind (assurance aspect) | DESIGN |

Absence findings (a requirement with no verifier) had "the searched scope" as their witness. The closure-cut is stronger: the forward-closed set from the requirement, hashed, is a witness a person or a program can check in linear time. This is a proposal to the rules and views aspects (section 13).

What a certificate does not cover: the input. A closure certificate proves C is the closure of the edges it was given. Whether those edges are the true dependencies of the code is extractor fidelity (R-1), which no certificate reaches.

### 3.5 Where each check runs

| Tier | What | Measured cost |
|---|---|---|
| fast | `selfcheck.py`, certificate checkers on the real graph, status and link laws | 0.5 s (selfcheck) |
| full | The whole `tests/graph/formal` suite, the exhaustive benchmarks, the Alloy models (Glucose) | 140 passed, 8 NOT_RUN (production bindings) and 1 expected failure (a documented finding) in 46 s to 76 s depending on machine load, of which about 19 s Alloy, 15 s status enumeration, 7 s SCC enumeration. Without Hypothesis, clingo and `rfc8785`: 128 passed, 11 NOT_RUN, 32 s |
| release | Everything, Alloy with a second SAT backend (SAT4J), two-evaluator agreement, POSIX golden | SAT4J adds about 4 minutes; POSIX NOT_RUN |

Solver diversity for Alloy is free: Glucose (native, JNI) and SAT4J (pure Java) agreed on all 11 verdicts. A disagreement would be a FAIL.

### 3.6 Bootstrapping

The weave will verify its own links (`conforms_to`, `proves`). A checker that only reports through the machinery it checks can hide its own failure. So `graph/formal/selfcheck.py` imports only `eijaref`, reports through its own JSON and exit code (0, 1, 2), and treats a suite that passes a wrong implementation as FAIL. It does not remove the need to trust the reference; it removes the circularity. The reference is itself trusted by the five means in section 1 plus human review of about 200 lines.

## 4. Determinism

### 4.1 The value domain and the writer

The committed-artefact domain V: null, booleans, integers with absolute value at most 2^53 - 1, strings of Unicode scalar values (no lone surrogates), lists of V, objects from strings to V. Everything else is refused. The writer W is RFC 8785 restricted to V: no whitespace; strings escaped as [RFC] 3.2.2.2 (controls U+0000 to U+001F as `\b \t \n \f \r` or lowercase `\u00xx`; `"` and `\` escaped; everything else literal); integers as decimal digits; members sorted by the UTF-16 code-unit sequence of the raw key ([RFC] 3.2.3); UTF-8.

| Theorem | Statement | Proof (PROVED ON PAPER) | Evidence |
|---|---|---|---|
| T1 determinism | W(x) depends only on the abstract value | Keys are distinct; the sort is by a total order on distinct strings (the map from a string to its UTF-16 code units is injective), so the member sequence is unique; the rest is structural recursion | 24 orders of a 4-key object gave 1 output; 300 seeded random dicts (up to 30 orders each) and 300 Hypothesis examples |
| T2 injectivity | W(x) = W(y) implies x = y | Define a strict decoder D. Each value starts with a distinct byte class (`n t f - 0-9 " [ {`), JSON is unambiguous, the string escape is injective and inverted by unescape, integers are canonical decimals, and object members are recovered as a set. So D(W(x)) = x | 282 hostile values, 0 collisions, 0 round-trip failures including type; Hypothesis round trip |
| T3 framing | frame(tag, f1..fn) determines (tag, f1..fn) | The 8-byte big-endian length of every field precedes it and the arity is stated; the code is prefix-free, so parsing is unique. Assumption: every length is below 2^64 | ("a","bc") and ("ab","c") collide under plain concatenation (MEASURED) and differ under `frame`; 800 tuples gave 800 distinct frames. Same idea as NIST TupleHash, "designed to hash tuples of input strings unambiguously" ([NIST], abstract only; not used, we frame SHA-256 ourselves) |
| T4 root | The root depends only on the SET of leaves and sees every leaf | Leaves are sorted and deduplicated (duplicates refused); leaf and interior nodes use different domain tags; by T3 the pre-image chain determines the leaf bytes. Modulo A-SHA | 24 orders gave 1 root; changing any of 4 leaves changed the root |

Conformance to the RFC on V is a separate claim (T5). Evidence: the two vectors printed in the RFC (the string sample of 3.2.2 and the sorting sample of 3.2.3) reproduce; 20,000 seeded random members of V gave 0 mismatches against `rfc8785` 0.1.4 (Apache-2.0, LICENSE head opened; [GH]: pushed 2026-09-28). For integers the RFC defers to ECMAScript number serialisation (ECMA-262, not opened); the agreement on random safe integers is the evidence and is labelled DIFFERENTIAL.

One point the RFC makes and this lane keeps: "For the purpose of obtaining a deterministic property order, sorting of data encoded in UTF-8 or UTF-32 would also work, but the outcome for JSON data like above would differ and thus be incompatible with this specification" ([RFC] 3.2.3). Determinism alone does not need UTF-16 order; interoperability with any JCS implementation does. The RFC's own vector shows the difference: the emoji (a surrogate pair, first unit D83D) sorts between U+20AC and U+FB33 in UTF-16 order and last in code-point order. The kernel's `canonical()` sorts by code point, so it differs from JCS on the object with keys U+10000 and U+FFFF (MEASUREMENT).

### 4.2 What the kernel's `canonical()` does outside V (MEASUREMENT F3b)

It is right for its own typed inputs. It must not be reused for committed graph artefacts on unvalidated data:

| Input | Behaviour |
|---|---|
| `{1: "a"}` and `{"1": "a"}` | Same text, so distinct values share a fingerprint ([PYJSON]: "all the keys of the dictionary are converted to strings ... `loads(dumps(x)) != x` if x has non-string keys") |
| `{1: "a", "1": "b"}` | `TypeError` (sort of mixed keys) |
| `(1, 2)` and `[1, 2]` | Same text |
| `1.0`, `-0.0` | `1.0`, `-0.0`; JCS prints `1` and `0` |
| `{10: 1, 9: 2}` | `{"9":2,"10":1}`: numeric keys sort by value ([PYJSON]: "numeric keys are sorted by value, not by their string representation") |
| lone surrogate string | `UnicodeEncodeError` in `fingerprint` |
| integer above 2^53 | Kept exact (JCS refuses it) |

### 4.3 The compositional argument and the harness

Pipeline = Read, Extract, Load, Derive, Check, Serialise. If every stage is a function of its input taken as a set or a path-to-bytes mapping, the pipeline is a function of the tree. Hidden order channels are the only way to break this, and there are eight:

| Channel | Example | Detection | Evidence |
|---|---|---|---|
| Container iteration | `set` of strings reaching output | Seed matrix; lint (rules aspect WV-085) | Toy pipeline: 8 distinct outputs over 8 `PYTHONHASHSEED` values, 1 when sorted (F8); [PYCLI]: str and bytes hashes are salted unless the seed is fixed |
| File-system order | `os.listdir`, unsorted `glob` | Shuffle, lint | D-09 |
| Library defaults | `nx.condensation` numbering | Shuffle, replaced by min-member labels | 5 labellings over 60 insertion orders; every raw labelling rejected by the canonical checker as non-canonical, and accepted after a min-member relabel (F4b) |
| Query order | SQLite without `ORDER BY` | Total `ORDER BY` in every result query | [SQLITE]: without `ORDER BY` "the order in which rows are extracted is undefined" |
| Floats | PageRank | Integer or `Fraction` arithmetic | 40 of 40 shuffles gave different float hashes [math] |
| Encoding | CRLF, non-BMP characters | CRLF fold, UTF-8 everywhere | RFC vectors; hash-method tests |
| Environment | locale, time zone, cwd, threads | Permutation harness | D-19 |
| External tools | Sorted or unsorted output | Adapter sorts, exact sentinel | D-16 |

Stage-wise permutation tests (cheap, strong) plus one end-to-end harness (few, real) is the plan. The harness is worthless if it cannot see a defect, so it has a negative control: the seeded set-iteration pipeline above. What none of this shows: determinism for inputs nobody permuted, on POSIX (NOT_RUN), or across Python and SQLite versions (pinned in every cache key, D-11).

### 4.4 Snapshot consistency

A build that reads a moving working tree is nondeterministic by construction. The reader (PO-D7) takes the tree from the git object store, or hashes every file on first read and re-checks the snapshot root at the end; a mismatch is NOT_RUN. DESIGN; nothing to measure until the reader exists.

## 5. Graph computations

### 5.1 Closure is the least fixed point, and a certificate proves it

Definition. For a digraph (V, E) and roots R, F(X) = R union { v : (u, v) in E, u in X } and lfp = the union over k of F^k(empty set). This is the kernel's `impact.closure` (edges mean "source affects target"). F distributes over unions, so the Kleene union is the least fixed point with no finiteness assumption.

Theorem C (certificate soundness), PROVED ON PAPER. Let C, rank, parent satisfy (a) R is a subset of C; (b) for each c in C minus R, (parent[c], c) is in E, parent[c] is in C and rank[parent[c]] < rank[c]; (c) u in C and (u, v) in E imply v in C. Then C = lfp.
Proof. C is a subset of lfp by induction on rank: a root is in F(empty); any other c has a parent of smaller rank, which is in lfp by hypothesis, and lfp is closed under F. lfp is a subset of C: F^0(empty) is empty; F^(k+1)(empty) = R union E[F^k(empty)], which is a subset of R union E[C], which is a subset of C by (a) and (c). QED.
Corollary. If (a) and (c) hold and t is not in C, then t is not in lfp: a forward-closed set is the negative witness.

Each hypothesis is necessary, checked two ways: five mutants of the checker, each dropping one of (a), (b1 edge exists), (b2 parent in C), (b3 rank decreases), (c), have a counterexample in Python (all digraphs on 3 nodes) and in Alloy (scope 7).

| Check | Domain | Result (MEASUREMENT) |
|---|---|---|
| Kernel `closure` equals naive Kleene iteration and Warshall closure | all 2^16 digraphs with self-loops on 4 nodes x all 16 root sets = 1,048,576 cases | 0 mismatches |
| BFS certificate accepted, negative witnesses accepted | same | 0 rejections |
| SQLite `WITH RECURSIVE ... UNION` equals the reference | all 512 digraphs on 3 nodes x 8 root sets = 4,096 | 0 mismatches |
| Impact aspect's `closure` and its `(distance, parent)` maps | all 3-node graphs; accepted by this lane's checker | 0 failures |
| Kernel budgeted closure: `affected` is inside the closure, `complete` implies equality, `frontier` is inside the closure | 512 x 8 x 5 budgets = 20,480 | 0 violations |
| Real checker accepts only true closures | exhaustive over 2-node graphs, roots and every (C, parent, rank): 5,184 candidates, 480 accepted; 60,000 seeded one-field perturbations of correct certificates on 3 to 6 nodes: 34,540 accepted | 0 accepted with C different from the closure |

Honest reading. For reachability the certificate checker is no simpler than the algorithm it checks. Its value is elsewhere: it validates a witness path a human is shown, it checks an answer from the SQL engine or a Neo4j export without trusting either, and its negative form (the closed set) is a witness for absence.

### 5.2 SCC labelling and topological order

Facts: the SCC partition of a digraph is unique; the condensation is acyclic; the lexicographically smallest topological order is unique (at each step the available set is determined by the prefix, and taking the minimum is forced).

Theorem S (partition certificate), PROVED ON PAPER. Let every node carry a label; classes are label-equal sets; each class's label is its minimum member; (2) inside each class, forward and backward search from the minimum member using only edges inside the class reaches the whole class; (3) the quotient graph (classes, edges between different classes) is acyclic. Then the classes are exactly the SCCs.
Proof. By (2) each class lies in one SCC. If two distinct classes A and B lay in one SCC there would be paths a to b and b to a; collapsing consecutive nodes of one class turns them into a closed walk through A and B in the quotient, a cycle, contradicting (3). QED. (2) alone accepts all singletons; (3) alone accepts one class holding every node, so both are needed. The checker has no lowlink and no stack; it is not Tarjan.

| Check | Domain | Result |
|---|---|---|
| Producer (Tarjan, minimum-member labels) accepted by the checker and equal to the mutual-reachability definition | all 65,536 digraphs on 4 nodes | 0 differences |
| The checker accepts exactly the canonical labelling | all 27 labelings x 512 digraphs on 3 nodes = 13,824 | 0 disagreements |
| Lexicographic topological order equals the brute-force minimum over all permutations; accepted by the order checker | all 4,096 loopless digraphs on 4 nodes, 543 of them acyclic | 0 differences |
| Impact aspect's `scc_labels` and `lex_topological_order` | all 3-node graphs; accepted by these checkers | 0 failures |
| Alloy: `scc_soundness` for scope 6; mutants without (2) or (3) | | UNSAT for the theorem, SAT for both mutants |

### 5.3 What Alloy adds, exactly

`graph/formal/alloy/certificates.als` (56 lines) models the acceptance conditions of both checkers and asserts the two theorems and the negative-witness corollary; five closure mutants and two SCC mutants must each have a counterexample; one `run` shows a non-vacuous accepted certificate. Result: 11 of 11 as expected. What that means: no counterexample with at most 7 nodes (6 for SCC) and integers in -8..7. The integer bound does not restrict the conclusion, because any accepted certificate can be re-ranked by parent depth, at most 6 for 7 nodes. It is a check on the statements (each condition is necessary; nothing else is missing within scope), not on the Python code; the Python code has its own exhaustive tests, and section 9 ties the two.

### 5.4 SQLite recursion and the LIMIT trap

[SQLITE]: with `UNION` "repeated rows are discarded before being added to the queue", which makes cyclic graphs terminate; the LIMIT clause "determines the maximum number of rows that will ever be added to the recursive table ... Once the limit is reached, the recursion stops". So a guard implemented as a LIMIT inside the recursive select silently returns a partial closure. MEASUREMENT: a 51-node chain, LIMIT 10 inside the recursive select returned 10 rows. The guard must ask for LIMIT + 1 and turn a full result into a finding; a bare LIMIT is a false-PASS route for absence findings. (The design in ARCHITECTURE layer L3, `WITH RECURSIVE` over `UNION` plus a `LIMIT` guard, needs this rule stated; ADR-0091 restricts recursion to the node column with `UNION`.)

## 6. Status and link algebras

Two sorts exist and must not be mixed: **evidence status** PASS, FAIL, STALE, UNKNOWN, CONFLICT (the kernel's five) plus NOT_RUN; **rule verdict** PASS, FAIL, NOT_RUN (ADR-0095, chain minimum FAIL < NOT_RUN < PASS). Link status COVERED, SUSPECT, ORPHANED, AMBIGUOUS, UNRESOLVED lifts to evidence status by a fixed map.

### 6.1 Join for repeated observations of one check

Information order NOT_RUN < UNKNOWN < STALE < {PASS, FAIL} < CONFLICT; join = least upper bound (computed by search over the order, not by a hand table). Laws: commutative, associative, idempotent, identity NOT_RUN: checked over all 36 pairs and 216 triples. **Finite reduction**: a commutative, associative, idempotent operation folds a list to a function of its set, so the 216 triples close the claim for every list length; this is stronger than sampling lengths. On the kernel's five values the join equals `aggregate_status` on all 5,460 flat sequences of length 1 to 6 over {PASS, FAIL, STALE, UNKNOWN} (MEASUREMENT, kernel present). The kernel is not compositional: `agg([PASS, FAIL, FAIL])` is CONFLICT but `agg([agg([PASS, FAIL]), FAIL])` is FAIL (reproduced); the join composes. The kernel fix is a separate ADR and PR.

### 6.2 Meet across required checks; the gate predicate

Meet is the minimum in a chain with PASS on top. **Theorem G** (PROVED ON PAPER): for every total order of the six values with PASS at the top, the fold is PASS if and only if the list is non-empty and every element is PASS. Proof: PASS is the maximum, so the minimum is PASS only if no element is smaller. EXHAUSTIVE: 120 chains x multisets of size 1 to 4, 0 violations. Consequence: where NOT_RUN and UNKNOWN sit is cosmetic for gating; it decides only which word prints. SYNTHESIS open question 1 therefore has no effect on any verdict, only on messaging.

Two negative controls the suite catches: a fold seeded with PASS (`reduce(..., PASS)`) makes the empty gate pass; a fold that skips NOT_RUN lets `[PASS, NOT_RUN]` pass. Both fail `suite_status`.

### 6.3 Two levels, and why a required check must use the meet

Claim status = meet over required checks of (join over the evidence of that check). `join([PASS, NOT_RUN])` is PASS, which is right for two independent pieces of evidence for the same check and wrong for two required checks. So the split between "required" and "alternative" is a schema fact: the certificate names its required checks (the two-check rule for proofs: the producer toolchain and the independent kernel are two required checks). EXHAUSTIVE: for 1 to 3 required checks with evidence as any subset of the six values (64 + 64^2 + 64^3 = 266,304 combinations), the claim is PASS iff every check's join is PASS, 0 violations; a claim with no required checks and a required check with no evidence are never PASS.

### 6.4 Reconciliation with the impact aspect

The impact aspect wrote its own fold (`fold_a`, `fold_b`) and tests two differences against this lane's `eijaref.status`: its join refuses NOT_RUN and returns UNKNOWN for the empty list (the kernel's behaviour); ours puts NOT_RUN at the bottom and returns NOT_RUN. Both satisfy every property in 6.1 to 6.3; the law suite is written to accept either (join only on the kernel's five values; empty join not PASS). Recommendation of this lane: the production `eijagraph.status` follows the impact aspect (kernel-exact join, NOT_RUN only in the meet), because one word then means "ran, nothing decidable" everywhere. `eijaref.status` stays as it is: two sibling tests pin its behaviour.

### 6.5 `link_status`

Signature (adapter form used by the suite): `link_status(baseline, observation, acks, link_id)` with observation one of UNRESOLVED, ABSENT, AMBIGUOUS, DIGEST(d). The precedence among the three non-digest cases is the link-record ADR's choice; the laws below do not depend on it:

| Law | Statement | Negative control that must fail |
|---|---|---|
| LS1 total, deterministic | Exactly one of the five statuses; the same inputs give the same answer; the result does not depend on the ack set's representation | |
| LS2 COVERED soundness | COVERED only if an observation exists with digest equal to the baseline, or an ack for exactly (link, current digest) | ack matched on digest alone, ignoring the link |
| LS3 ack locality | An ack for another digest, or another link, changes nothing | same |
| LS4 ack clears SUSPECT only | An ack never turns ORPHANED, AMBIGUOUS or UNRESOLVED into COVERED | ack clears ORPHANED |
| LS5 monotone in the ledger | Adding an ack changes at most SUSPECT to COVERED | |
| LS6 unresolved is never covered | A missing resolver reports UNRESOLVED, which lifts to NOT_RUN | UNRESOLVED reported COVERED |

Exhaustive over 5 observations x 16 ack subsets x 4 possible extra acks. The lift map sends only COVERED to PASS (EXHAUSTIVE over all chains and pairs).

### 6.6 The ledger

ADR-0093 makes the ledger a grow-only set of content-addressed entries merged by union. The obligation (PO-S7) is set monotonicity: for a base ref and head, entries(base) is a subset of entries(head); an ack binds the exact subject digest so an ack on one branch cannot hide a change on another. Union is commutative, associative and idempotent, so multi-worktree merges cannot conflict; a semantic conflict shows up as CONFLICT in the join, never as a merge failure.

## 7. Metamodel and rules

### 7.1 The metamodel (files: `graph/schema/metamodel.json`, owned by the metamodel aspect)

The task asked for "Alloy 6 or Z3" for consistency and satisfiability. Measured answer: neither is needed today.

| Check | Method | Result (MEASUREMENT F9) |
|---|---|---|
| Table lemmas MM-002 to MM-004 and MM-020 to MM-025: no unknown or empty signature side, no isolated node type, no obligation that cannot be met (scope type not on the obligation's side), no minimum above a maximum, every obligation names a rule that exists in the catalogue, no supertype clash, unique domain tags | Set operations, an independent reading of `graph/schema/README.md` | 0 findings on 42 node types, 29 link kinds, 6 minimum obligations |
| The same lemmas on `graph/brief.json` (the prose brief the schema replaced) | | 17 findings: 13 link types with free-text hash policy, 2 node types (`gate`, `lane`) in no link type, 2 compound classes. All are gone from `metamodel.json`; the check found real defects |
| Constructive instance: one node per type (ids from the metamodel's own examples), one edge per minimum obligation | Deterministic construction | 42 nodes, 6 edges; accepted with 0 findings, including the minimum obligations, by this lane's checker and by the aspect's `check_document` |
| Differential: this lane's instance checker against `graph/schema/typecheck.check_document` (the file was named `reference.py` until the metamodel aspect renamed it during this work) | 600 seeded random edge sets over 2 nodes per type, 70% signature-guided, 0 to 24 edges; 540 had findings; 6 finding codes exercised | 0 mismatches |
| Demand chains among obligations | Static | One chain of depth 2: a transition needs a `realises` link from a UI control (WV-031), and a UI control needs an `exercised_by` link to a test or journey (WV-037). The constructive instance meets it |

Solver trigger (measurable): revisit when any of these holds, and then use Alloy (relational, `^` closure built in) or clingo (below): a demand chain of depth 3 or more; a minimum obligation whose only satisfying far type has a maximum that the minimum can exceed; a metamodel change that adds disjunctive obligations ("either a test or a formal model"); or a constructive instance that the reference rejects.

| Option | Fit for these statements | Footprint | Measured here | Verdict |
|---|---|---|---|---|
| Plain Python (exhaustive, constructive) | Finite tables, small graphs | none | 1,048,576 closure cases in 49 s; all 65,536 4-node digraphs in 6 s | First choice whenever the domain is enumerable |
| Alloy 6.2.0 [ALLOY] | Relational logic with transitive closure, cardinality, bounded; the certificate theorems | 21,062,377-byte jar, Java 17 (already needed by TLC), licence MIT per the LICENSE header (Apache text marked "NOT VALID YET"), bundled SAT solvers UNVERIFIED | 11 commands: 15.8 s and 23.6 s (Glucose), 216 s and 229.6 s (SAT4J); pilot rule model 2.2 s including JVM start | Chosen for bounded statements the enumeration cannot reach |
| clingo 5.8.2 [CLINGO] | Stratified Datalog is close to ASP syntax; fixture synthesis by minimisation | 1,621,287-byte wheel, MIT (LICENSE.md head) | Four pilot programs: 400 differential evaluations, 4 minimal fixtures and a dead-rule control in 0.56 s | Test-time bridge only |
| Z3 5.1.0.0 [Z3] | Arithmetic, bit-vectors; used by the smt-bmc lane for the policy proof | 17,040,097-byte wheel, MIT (LICENSE.txt head) | Not used. Reachability needs bounded unrolling or a fixed-point engine: UNVERIFIED, not tried | Not adopted for weave-internal properties in phase 1 |
| TLA+ / TLC (tla lane pin, MIT) | Behaviour over time, interleavings | Java, jar pinned in `TOOLS.lock` | Not used | Reserve for a multi-writer incremental cache (trigger in ADR) |

Timing caveat: single machine, other agents running, load not controlled; the ratio (about 10x) is indicative.

### 7.2 Rules

The rules aspect chose SQL violation queries as the source (ADR-0095), 97 rules in the catalogue, 50 with negative reads (36 before the ADR-0095 polarity audit added 14), 15 generated from metamodel constraints. What can and cannot be verified:

| Item | Method | Result |
|---|---|---|
| Declared strata equal the formula `max(0, positive reads, negative reads + 1)`, and each negative read is over a strictly lower stratum | Independent recomputation from `reads` | 97 rules, 0 problems |
| The catalogue as a program is stratifiable (no negation through recursion) | Feed the dependency graph to the SCC-based stratifier | Yes, under one stated assumption: stratum-3 rules (WV-045 reads `finding` negatively) feed `finding3`, which nothing reads. If WV-045 fed `finding` the program would be unstratifiable (control, tested) |
| Loader rejects negation in recursion, unsafe variables | Reference IR; safety is the "range restriction" and evaluation "always terminates" for Datalog ([DL]) | 4 of 4 malformed programs rejected |
| Closed-world verdict guard (`rule_verdict`, revised after the ADR-0095 audit): a finding is FAIL on partial input only when the finding set is monotone in the incomplete relations (`none` or `monotone` read effect); a rule that reads an incomplete relation negatively or through a derived relation, or lacks a prerequisite, is NOT_RUN whatever it found; no finding with an incomplete positive read is NOT_RUN; PASS otherwise | Exhaustive over 3 x 2 x 3 combinations (finding count, prerequisite, read effect) | Correct against the revised table |
| Verdict fold: PASS iff all PASS; NOT_RUN never hides a FAIL; the empty run is NOT_RUN | Exhaustive over 3-valued multisets of size 1 to 4 | Correct |
| Reference evaluator equals SQLite | 4 pilot programs (uncovered; reach and cycle; orphan and ill-typed; stratified two-level) x 200 seeded fact sets; the final head was non-empty in 110 to 140 of 200 | 0 mismatches |
| clingo equals the reference; every solver fixture replays in the reference and SQLite; a contradictory rule has no fixture | 4 programs x 100 sets; 4 fixtures of 1 fact each | 0 mismatches; replays succeed; dead-rule control returns none |
| Monotone rules are monotone; negation is not | Property over 200 random graphs; a two-fact example | Adding facts never removes a positive consequence; a requirement's violation disappears when a verifier is added |

Not verified and why. Whether a rule's SQL text expresses its intent (R-3) is a human reading plus the fixture matrix (378 minimum cases, ADR-0095) and rule-source mutation. Polarity is declared and tested, not proved. The catalogue's `statement` field is prose, not an IR, so no automatic translation to Alloy or clingo exists; building one is warranted only if the rules aspect moves to an IR, or if more than about 30 rules need recursion with negation (the ADR's own trigger). Until then the solver bridge is a pilot on the fragment that has an IR.

Recommendation to the rules aspect (section 13): rules that are templates (15, generated from metamodel constraints) get an automatic independent evaluator from this lane's instance checker; rules over `scc.*`, `affected` and `component*` get a certificate check on their derived relations; the rest rely on fixtures and mutation.

## 8. Lenses, views and merges

Definitions ([FOSTER] section 3): GetPut `put(get c, c) = c`; PutGet `get(put(a, c)) = a`; PutPut `put(a', put(a, c)) = put(a', c)`; well-behaved is the first two, very well-behaved adds PutPut; the paper states the laws "if both operations are defined" and does not require PutPut because `map`, `flatten`, `merge` and conditionals fail it "for reasons that seem pragmatically unavoidable". EIJA's `put` can refuse (`Rejected`), so the checker makes definedness explicit: GetPut demands acceptance of the no-op edit; PutGet and PutPut are checked only where `put` accepts; the view comparison may ignore layout.

The checker (85 lines) is validated on the paper's three counterexamples, each of which must trip exactly the law the paper says: a put with a side effect fails GetPut only; a put that drops view information fails PutGet only; a put that bumps a version number fails PutPut only. 3 of 3 agree. The per-view law suites (GetPut, PutGet modulo layout, conditional PutPut on the `SemanticTransaction` alphabet) belong to the consistency aspect (ADR-0093 reports four seeded broken translators caught); this lane supplies the checker and asks that those suites run through it (PO-L2). Get-only lenses (OKF pages, diagrams, SysML text, SARIF and exports) have weaker obligations: total, deterministic, and mapping-total (every semantic type is drawn or `not_shown`).

### 8.1 Keyed three-way merge

**Keyed three-way merge** (ADR-0093 claims symmetry, identity, idempotence and associativity-when-defined, measured on 3,000 seeded trials). `merge3` decides each key from four values (base, ours, theirs, a third replica). Four symbols (absent, a, b, c) realise every equality pattern among four slots, so **256 single-key cases stand for every alphabet and every number of keys**, provided merge is key-wise, which a second test confirms on 400 random 5-key records. EXHAUSTIVE result: all four laws hold, and the merge is defined iff at most one distinct value differs from the base, 0 violations. This turns a sample into a finite-reduction result.

### 8.2 Every transformation, every law class

ADR-0093 defines eleven transformation cards (`graph/schema/transformations.md`) and a law catalogue (GEN G1 to G7, PROP L1 to L10, EXT E1 to E5, complement C1 to C4, MRG M1 to M8, REN R1 to R4, ACK A1 to A5). This lane does not re-own those laws. For each card it says which formal obligation applies, which rung closes it and what is measured here:

| Card | Class | Laws (ADR-0093) | Formal obligation and technique | Status here |
|---|---|---|---|---|
| T1 model to diagram | GEN (get-only) | G1 to G7 | Determinism and permutation invariance PO-D6; mapping totality and homomorphism PO-L3 (an independent reader `rho` recovers the shown part); byte identity of committed output PO-D1 | PENDING (visual lane owns the generators) |
| T2 diagram edit to transaction | PROP (lens with partial put) | L1 to L10 | Run through `check_lens_laws` (PO-L2): GetPut needs acceptance of the no-op edit; PutGet only where accepted; conditional PutPut only on the slots claimed. Exhaustive on the alphabet; Hypothesis beyond | NOT_RUN here; checker validated (PO-L1) |
| T3 model to SysML v2 text | GEN | G1 to G7 | Same as T1 plus an independent parse of the emitted text | PENDING |
| T4 model to code obligations | GEN plus create-once scaffold | G1 to G7, E4 | Regeneration byte-compare (X1); round trip generate then extract (E4) | PENDING |
| T5 model to UI projection and checks | GEN and CHK | G, E | Enabled-set equality is a set comparison over enumerated (state, actor) pairs: EXHAUSTIVE by construction | PENDING |
| T6 graph to OKF pages | GEN with complement | C1 to C4 | Complement laws are GetPut and PutGet with a complement; the aspect already found that C1 fails on three or more consecutive newlines, which is exactly the kind of counterexample the law checker is for | PENDING |
| T7 code to facts, reflexion | EXT and CHK | E1 to E5 | E1 permutation harness (PO-D6); E2 locality is a metamorphic relation; E3 label honesty (PO-T2); E5 "seeded lie" is PO-T1 and PO-T3: an extractor that reports a fact the file does not contain must be caught by the kernel's recomputation | PENDING |
| T8 rename | REN | R1 to R4 | R3 inverse and R4 commutation are exhaustive on a small file alphabet; R2 needs a name-erased normaliser (DESIGN) | PENDING |
| T9 merge and post-merge compile | MRG | M1 to M8 | M1 to M5: 256 single-key cases stand for every alphabet (8.1); M6 determinism; M7 differential against `git merge-file`; M8 needs the finding model | M1 to M5 MEASURED (this lane); rest owned |
| T10 ack | ACK | A1 to A5 | A1 subject-bound and A3 order independence are properties of `link_status` (LS2, LS3, and the ack set is a set); A4 append-only is PO-S7; A5 forks are visible needs the ledger design | LS1 to LS6 MEASURED on the reference |
| T11 graph to exports | GEN | G1 to G7 | Determinism and goldens; a differential closure check between the SQLite index and an engine loaded from the Neo4j export (ADR-0091), NOT_RUN when absent | PENDING |

The pattern: a get-only card needs determinism, totality and byte identity, all closed by permutation tests and goldens; a card with a put needs the partial-lens laws and a typed rejection for every undefined input; a merge or ack card needs set laws, which reduce to a finite check. None needs a solver.

## 9. Drift between a model and its code

A proof about a model is not a proof about the code. Five mechanisms, in decreasing strength:

| # | Mechanism | Guards | Residual |
|---|---|---|---|
| X1 | **Regeneration byte-compare** for models generated from a source of truth (schemas from `metamodel.json`: `build_schemas.py --check`) | The model is a function of its source | The generator; label GENERATED |
| X2 | **Named-condition parity** between a hand-written model and its implementation: each Alloy predicate is named after the Python condition it mirrors (a, b1, b2, b3, c; s2, s3), and a test fails when a name, a mutant or an error token exists on one side only | Silent addition or removal of a condition | Semantics of a name |
| X3 | **Differential runs** on exhaustive small scope and Hypothesis: the model's decision and the code's agree | A behavioural slip | Bounded (CONFORMS_BOUNDED, bounds printed) |
| X4 | **Digest-pinned links in the weave itself**: a `conforms_to` link from the implementation symbol (`ast-v1`) to the model file, a `proves` link with the statement pinned by `law-block-v1`; either digest changing makes the link SUSPECT until a human acks or the run is repeated | Silent edit of either side | Needs `eijagraph`; DESIGN |
| X5 | **Bilateral mutation controls**: a model mutant (drop a condition) must produce a counterexample in the solver, and the matching code mutant must fail the tests | A vacuous model or a toothless test | Mutant set is chosen by us |

Solver-synthesised fixtures are a sixth, useful bridge: a fixture found by clingo or Alloy is committed as data and replayed through the implementation (here: the reference evaluator and SQLite); the solver is not in the gate, so its version cannot change a verdict. Solver output order is not guaranteed stable across versions, so fixtures are regenerated only on purpose.

Labels on every model link (assurance aspect): PROVED_IN_MODEL or CHECKED_BOUNDED for the model, CONFORMS_BOUNDED for the link to code, with the bound printed. TLA+ and Bend links keep their own lanes' harnesses (state-graph comparison, trace validation, differential runtime matrix); the weave contributes statement pinning, the assumption ledger and the negative-control requirement.

## 10. Negative controls (a check that cannot fail proves nothing)

| Check | Wrong implementation it must catch | Caught |
|---|---|---|
| Closure suite | One-hop closure | yes |
| Certificate checker | five mutants, each missing one condition | yes, Python and Alloy |
| SCC and order suite | Insertion-order labelling (the `nx.condensation` behaviour) | yes |
| Canonical writer suite | `json.dumps(sort_keys=True, ensure_ascii=False)` | yes |
| Status suite | Vacuous meet (`reduce(..., PASS)`); meet that skips NOT_RUN | yes |
| `link_status` suite | ack matched on digest only; UNRESOLVED reported COVERED; ack clears ORPHANED | yes, 3 of 3 |
| Lens law checker | the paper's three lenses | yes |
| Metamodel table check | Synthetic metamodel with an isolated type, an unmeetable obligation, min above max, a missing rule id, duplicate tag | yes |
| Instance checker | Empty edge set breaks the minimum obligations; a self-loop; a two-cycle on an acyclic kind | yes |
| Catalogue strata | A wrong declared stratum; stratum-3 output fed to `finding` | yes |
| Determinism harness | Set-iteration pipeline | yes, 8 distinct outputs |
| Alloy runner | Missing or wrong jar (NOT_RUN); no `expect` clause (FAIL); wrong expectation (FAIL) | yes |

## 11. Findings on sibling lanes' artefacts

None is a false PASS. Each is stated with evidence and a proposed owner action; this lane changes no sibling file.

| # | Finding | Evidence | Proposal |
|---|---|---|---|
| 1 | `exit_code(NOT_RUN, not_run_accepted=True)` returns 0, and the acceptance is driven by an environment variable in the quality lane's audit session (`EIJA_ALLOW_NOT_RUN=1`, per the rules reference). An agent that can set an environment variable can turn a skipped gate into exit 0 | `graph/rules/reference.py`, tested | Acceptance is a ledger entry bound to the report digest, not an environment variable; the release tier never accepts NOT_RUN |
| 2 | `identity_checks.jcs_dumps` accepts tuples and serialises them as arrays, so `(1, 2)` and `[1, 2]` share bytes. Deterministic, but a collision class; the formal writer refuses tuples | test in `test_formal_crosscheck.py` | Refuse tuples in artefact writers, or document that artefact inputs come from parsed JSON only |
| 3 | The okf lane's `codelink.digest` raises `UnicodeEncodeError` on a Python source containing a string literal with a lone-surrogate escape (`"\ud800"`), instead of `Unresolved` or a digest. A link check would abort | `xfail(strict=True)` test `test_po_d10_a_lone_surrogate_...` | Catch and report as unresolved; obligation PO-T7 makes "any exception fails closed" a tested rule |
| 4 | Status join: two representational differences (empty join, NOT_RUN in the join) between `eijaref.status` and the impact aspect's fold | section 6.4 | Follow the impact aspect in production |
| 5 | Rules aspect `canonical_json` restricts keys to ASCII identifiers; safe (equal bytes inside the domain, refusal outside), stricter than the metamodel aspect's writer | test | Document the domain per writer |

Independent confirmations (no finding): the kernel's `closure` on 1,048,576 cases; the metamodel's `check_document` on 600 instances; the rules aspect's strata on 97 rules; `merge3` laws on 256 reduced cases; the impact aspect's closure, SCC, order and folds; the identity aspect's graph root (permutation of nodes, edges and key order over 60 shuffles; a change to any single node or edge of a 40-node, 90-edge graph changes the root) and its writer against the formal writer on the hostile pool and 2,000 random values.

## 12. What is not verified

| Not verified | Why | What would change that |
|---|---|---|
| The production code (`eijagraph`) | It does not exist; the suites run against references and skip the eight production bindings as NOT_RUN | Build it; `graph/formal/binding.json` names where each suite attaches |
| Extractor fidelity | Not certifiable | A second extractor per language on a sample; conformance against tool-resolved output |
| That a rule, an invariant or a formal statement says what the owner means | Human reading | Owner-approved statement digests; review |
| That a hash method's normal form is the right notion of change | A design choice, measured for sensitivity only on two other repositories | Re-measure on EIJA history |
| POSIX byte identity | Not run | One run on Linux or WSL and a committed golden |
| Alloy results beyond scope 7 (6 for SCC) | Bounded | Paper proofs cover all sizes for both theorems; a machine-checked proof is deferred |
| The bundled SAT solvers' correctness and licences | Not read | Second SAT backend on the release tier; licences read before any redistribution (the jar is never redistributed) |
| Machine-checked proofs | Not built | Trigger: a certificate kind whose soundness proof is not a short induction, or an owner request; then Lean (`leanchecker` exists; the older standalone `lean4checker` is archived [GH]) or Bend via the bend lane |
| Any benefit to agents or humans | Unmeasured | The hci and eval lanes |

## 13. Interfaces to other aspects

| Aspect | This lane consumes | This lane provides | Requests |
|---|---|---|---|
| Metamodel and identity (ADR-0089) | `metamodel.json`, `typecheck.py` (formerly `reference.py`), `identity_checks.py` | Table-lemma checker MM-002 to MM-004 and MM-020 to MM-025 and an independent instance checker (differential, 0 mismatches); constructive instance | Structured obligation scope (`scope_type` plus `where`) instead of prose such as "term with ddd_role aggregate"; make MM-020 to MM-022 part of `check_metamodel`; decide tuples in the writer |
| Storage and query (ADR-0091) | The closure query design | Certificate checker for any closure the SQL returns; the LIMIT + 1 rule | State the truncation guard rule in the query contract |
| Consistency and sync (ADR-0093) | `merge3`, the translator laws | Partial-lens law checker; exhaustive reduction of the `merge3` laws | Run the per-view suites through `check_lens_laws`; state ledger monotonicity as a subset check against the base ref |
| Rules (ADR-0095) | Catalogue, `rule_verdict`, `fold_verdicts`, `exit_code` | Strata recomputation; verdict laws; witness checkers (`check_unreachable` for absence findings); template evaluator | Environment-variable NOT_RUN acceptance (finding 1); an optional IR for the fragment that has one; polarity property tests as a fixture class |
| Impact and ranking (ADR-0097) | `impact_math_reference.py` | Second checker for closure certificates, SCC and order; status law suite | Adopt the kernel-exact join in production |
| Agent interface (ADR-0099) | Tool list (read-only, proposal-only) | PO-T1 metamorphic non-interference test; certifying-style checker for proposals uses the same certificate protocol | Verdict must not read any agent-supplied field; tool results carry the root hash |
| Human views (ADR-00101) | Witness re-check need (HV-07) | `check_certificate`, `check_unreachable` (stable signatures) | Mark a witness unchecked when the checker is absent (already done) |
| okf | `codelink.digest`, hash methods | Metamorphic invariance and sensitivity tests (PO-D10), one finding | Fix the lone-surrogate crash; a fail-closed wrapper |
| tla, bend, smt-bmc | `TOOLS.lock` pattern, sentinel rule | `graph/formal/TOOLS.lock` and `run_alloy.py` in the same pattern | Witness schema for link certificates (assurance aspect) |
| quality | Sessions, import-linter | Sessions `graph_formal` (fast: selfcheck plus the light tests, 12 s by hand), `graph_formal_full` (whole suite plus Alloy) and `graph_formal_release` (benchmarks plus the SAT4J backend) appended to `quality/sessions/graph.py`. nox is not installed on this PC, so the sessions themselves are NOT_RUN; their commands were run by hand | Import contract for the kernel package; ratchet on its size |
| property | Hypothesis pin `6.168.3` | Derandomised profile `formal` (`derandomize=True`, `database=None`); extra `graph-formal` in `pyproject.toml` pins `hypothesis==6.168.3` and `clingo==5.8.2` (both optional; absence is NOT_RUN) | Reuse strategies when the lane lands |
| Kernel (`src/`) | `closure`, `aggregate_status`, `canonical` as oracles | Nothing; change requests only | JCS for new hashes; `aggregate_status` composition; both need their own ADR |

## 14. Open questions

1. Where NOT_RUN sits in the chain: cosmetic for gating (Theorem G); an owner choice for messaging.
2. Whether the production join follows the impact aspect (kernel-exact) or the formal reference (NOT_RUN at the bottom). Recommendation in 6.4.
3. Whether NOT_RUN acceptance moves from an environment variable to a ledger entry (finding 1).
4. Whether the rules aspect wants an IR for the checkable fragment (the trigger is in 7.2).
5. Whether the Alloy jar is fetched by a documented command or vendored under `graph/formal/tools/` (size 21 MB; licence of bundled solvers unread).
6. Whether Lean is worth its toolchain for the two certificate theorems (this lane says no until a trigger fires).
7. Numbering: the allocation table in `ARCHITECTURE.md` section 11 gives 0103 to statement pinning; this record was assigned the number 00103 by the brief (the sibling record for human views is 00101). The integrator reconciles.

## 15. Sources

Opened this session: see the keys at the top. Also read: the kernel files, `docs/weave/research/SYNTHESIS.md` and the dossiers [math] and [assure] in full, [bx] section 2 and 3.8, `docs/weave/ARCHITECTURE.md`, `graph/brief.json`, `graph/schema/{metamodel.json,typecheck.py,build_schemas.py,README.md}`, `graph/rules/{catalogue.json,reference.py,check_catalogue.py}`, ADR-0089, 0091, 0093, 0095, 0097, 0099, 00101 (summaries), `graph/bench/{impact_math_reference,identity_checks,consistency_checks}.py`, `/c/Dev/eija-wt/{tla,bend,smt-bmc,property,okf}` (TOOLS.lock, ADR-0028, ADR-0029, `bend_runner.py`, `quality/okf/codelink.py`). Not opened and therefore not relied on: the small-scope hypothesis literature, Apt-Blair-Walker stratification, verified-Tarjan formalisations, ECMA-262, the SAT solvers' licences, the Z3 fixed-point engine. The web-search budget was exhausted (200 of 200), so "no tool does X" means not found with the means available.

### Reproduce

```text
python graph/formal/selfcheck.py                     # 0.5 s, exit 0 PASS / 1 FAIL / 2 NOT_RUN
python graph/formal/selfcheck.py --alloy             # + Alloy certificate models (needs Java 17 and the pinned jar)
python graph/bench/formal_checks.py --timing         # all measurements above, 75 s
python -m pytest tests/graph/formal -q               # 140 passed, 8 NOT_RUN, 1 xfail on the reference PC (Hypothesis, clingo, rfc8785 installed)
```
