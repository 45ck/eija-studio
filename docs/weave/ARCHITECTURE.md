# Weave architecture: a deterministic, typed graph and compiler over everything

Lane: weave. Date: 2026-09-29. Status: proposed architecture, input to ADR block 0089-0112 (allocation in section 11). Nothing here is built yet except the benchmarks under `graph/bench/`. Evidence, sources and rejected alternatives are in [research/SYNTHESIS.md](research/SYNTHESIS.md); dossier keys ([trace], [math], ...) are defined there. Machine-readable node types, link types and rule ideas: [../../graph/brief.json](../../graph/brief.json).

## 1. What the graph is

**The graph is a derived, rebuildable index of git-tracked sources.** Given a git tree, the pinned extractors and the declared-link files, the graph (facts, edges, findings, root hash) is a pure function of those inputs. Delete the index and rebuild it and you get the same bytes. The graph is never edited, never the place a fact is decided, and never authoritative except for two kinds of input that are themselves in git: declared links (authored) and the human decision ledger (appended by a person).

What would change this statement (revisit triggers, all measurable): a rebuild that exceeds an agreed time budget on the reference PC; an index above about 10^7 edges; a required query class beyond joins and recursion (weighted paths, community detection); a need for concurrent multi-user editing. None holds today ([gdb] section 5, [bx] section 5.9).

What the graph is not: a proof of correctness, a second source of truth for rules, states or journeys (AGENTS.md forbids parallel sources), a graph database deployment, or a claim that humans understand the software better. A hash proves change, not truth.

## 2. Layers

```text
 L0  Sources in git                code, tests, contracts, JSON Schema, OpenAPI, UI assets, OKF pages,
     (the only truth)              ADRs, requirements (acceptance matrix), term registry, formal models,
                                   declared links (graph/links/*.jsonl), decision ledger (graph/ledger.jsonl)
      |
 L1  Extractors (UNTRUSTED)        one Extractor protocol; each returns sorted typed base facts with a
                                   provenance label; pinned tool + grammar versions recorded; NOT_RUN if absent
      |
 L2  Canonical typed graph         base facts (immutable, content-addressed) + declared links
                                   nodes: repo:// URI ids; edges: many-sorted signature + soundness class
                                   canonical form: RFC 8785 subset, sorted; Merkle root per view
      |
 L3  Derivation                    rules produce derived facts (rule id + premises recorded);
                                   closure = least fixed point; SQLite recursive CTE, reference = impact.closure
      |
 L4  Constraint checker            violation queries and file-local rules (the "compiler and linters"),
     (SMALL, TRUSTED)              stratified, each finding with a re-checkable witness; link_status();
                                   assess_link() over link certificates
      |
 L5  Diagnostics                   Finding model -> SARIF 2.1.0 (canonical) -> rdjson, LSP JSON, text
      |
 L6  Projections (get-only)        OKF pages | diagrams (Mermaid/PlantUML/DOT, SysML v2 text) | UI sidecar checks
                                   agent query tools (MCP, read-only) | exports (SCIP, Cypher/CSV, Soufflé, SKOS)

 Decision plane (beside the stack)  human ledger: ack of SUSPECT links, owner-approved statement digests,
                                    baseline decisions. Agents and providers never write here.
```

Storage and index: `graph/.index/graph.sqlite` (gitignored, disposable) holds `node(id, type, content_hash)`, `edge(src, type, dst, origin, method, digest)` and rule outputs. Only `graph/links/*.jsonl`, `graph/ledger.jsonl` and `graph/manifest.json` (schema version, extractor pins, root hash) are committed. A derived snapshot is committed only when a gate proves it equals a rebuild.

## 3. Data model

### 3.1 Truth classes

| Class | Examples | Authority | Rebuilt? | May satisfy a gate? |
|---|---|---|---|---|
| Declared | authored links, term bindings, requirement ids, ADR references, OKF pages' human parts | Source of truth (text in git), kernel-checked | No | Yes |
| Derived | imports, symbol references, test-to-symbol coverage, generated diagrams, closure | Recomputed by pinned extractors and rules | Every build | Yes, with its soundness class stated |
| Inferred | LLM or IR link recovery, Graphify edges, GraphRAG communities | Proposal only, label `inferred`, tool, model, version, confidence | Optional | No, never (ProofMap GAP-024) |
| Evidence | receipts, model-check outputs, link certificates | Recomputed by a checker from raw observations; graph stores digests, not verdicts | n/a | Only via `assess_*` |
| Decision | ledger entries | A human, exact subject digest | No | Yes, as the only clearing act |

### 3.2 Identity

- Node id = okf lane URI `repo://<repo-relative POSIX path>[#<fragment>]`. Path grammar and safety checks are `quality.okf.codelink.parse_uri`. The language is an attribute, not part of the id. An id is never derived from a display label.
- The fragment grammar is registered per node type (Python dotted symbol, CSV first column, term slug, table-cell slug, HTML `data-eija-key`, workflow element id). The fragment is interpreted together with the file type and hash method, which is how the okf lane resolves it today.
- Renames are explicit records `{old_id, new_id}` produced by a codemod, never inferred by similarity. A change that removes an id with no map entry is a finding.
- Identity is a name; integrity is a hash. They are stored in separate fields.
- Ids exported to other systems (SysML v2 `@id`) are UUIDv5 over the URI in a fixed namespace, so an export and an OKF page name the same thing.

### 3.3 Nodes and links

Full tables are in `brief.json`. Summary:

- 37 node types across code, contracts, workflow, language, requirements and decisions, verification, UI, views and knowledge. They start from ProofMap Lite's 20 node kinds (`app, component, script, entity, table, service, route, api, api_contract, code_surface, rule, prompt, intent, requirement, design, uml, plan, proof, test, doc`) and are pruned and renamed; each cites a SysML v2 term or says EIJA-specific.
- 27 link types (ProofMap had 16). Every link type fixes allowed (source type, target type) pairs, an origin class (declared, derived, inferred), a soundness class (`must`, `may`, `heuristic`) and, for declared links to mutable targets, a hash-method policy. Ill-typed and dangling links are errors, not warnings.
- The typed schema is `graph/schema/`; the schema itself is generated and hash-checked so an agent cannot widen an edge signature to make a link pass.

### 3.4 Link record and status

```text
Link = { id, kind, from: repo://..., to: repo://..., method, digest, baseline_decision }
baseline_decision = { ledger_seq, actor }        # no wall-clock in the artefact; receipts hold times
link_status(link, current_digest, ledger) -> COVERED | SUSPECT | ORPHANED | AMBIGUOUS | UNWANTED | UNRESOLVED
```

`link_status` is pure. `UNRESOLVED` reports NOT_RUN when a resolver or parser is missing, never PASS. `SUSPECT` means the normalised target digest changed since the baseline, not that the link is false. Early cutoff: suspicion propagates only when a target's normalised digest changed, so a comment-only edit stops at the first hop. Aggregation uses the closure with direct and transitive defects reported separately (OpenFastTrace vocabulary, own implementation; OpenFastTrace itself runs only as an optional process and its report is imported as evidence).

Hash method per link kind (policy, to be re-measured on EIJA history): requirement to symbol `ast-sig-v1` or `ast-v1`; requirement to test `ast-v1` on the test function; term to code `ast-api-v1`; whole file `lf-sha256-v1` only where the file is the artefact. Measurement backing the choice: two Python repositories, per-change stale rate 99.9 to 100% raw bytes, 88.7 to 98.3% whole-file AST, 7.2 to 9.4% symbol AST, 1.5 to 1.8% signature ([trace] section 4). These are sensitivity numbers, not a false-link rate.

### 3.5 Provenance labels on facts

`exact` (stdlib parse, no ambiguity), `syntactic` (tree-sitter or regex-free structural read), `candidate(n)` (n possible resolutions, e.g. conditional imports: LibCST gave two candidates for `toml.loads`), `tool-resolved` (SCIP indexer output, decoded and sorted by us), `unresolved`, plus `partial` for facts from an error-recovered tree (tree-sitter lost `f` and `g` in a broken file; MEASUREMENT [code] M2). No gate may PASS on a partial extraction.

## 4. Compiler and linters

A rule is a named check with an id, a version, a stratum, declared input relations, a severity and a message template.

| Kind | Form | Cache unit | Example |
|---|---|---|---|
| File-local | Python function from one file's facts to findings | file content hash | forbidden term form at a declaration site |
| Graph-global | SQL violation query over declared relations; zero rows = pass | Merkle hash of the read relations | requirement with no `verifies` link |

- One file per rule. A loader reads the declared reads and strata, builds the rule dependency graph and **rejects negation inside a recursive stratum at load time**. Recursion uses `UNION` (dedupes rows so cycles terminate) with an explicit `LIMIT` guard; every result query ends in a total `ORDER BY`.
- Each violation row has a stable id (hash of rule id, subject ids, canonical arguments; no line numbers) and a witness: for reachability-based findings the lexicographically first shortest path over sorted neighbours; for absence findings the declared closed-world scope that was searched (what links were looked at). A witness is re-checkable: re-run the closure on the witness subgraph alone and recover the fact.
- `Finding = {rule_id, level, message_id, args, locations[repo://...], witness[], fingerprint, fix?}`. Messages are standalone, carry a stable code and a long-form explanation URL; structured `args` mean an agent never parses prose. Suppressions live in one ledger keyed by fingerprint with a justification and an evidence path that resolves; a suppression that matches nothing is itself a finding; baselines may shrink, never grow; no expiry dates (expire by ADR or commit reference).
- Fixes are proposals: byte-range edits plus `applicability` and a `precondition_sha256` per file. Applying to a changed file fails closed. The kernel path never applies edits.
- Every rule ships: annotated fixtures (positive, negative, todo), a deliberately broken negative-oracle fixture, golden SARIF with a bless command, `.fixed` goldens where a fix exists, fix idempotence, and a differential test that incremental output equals clean output.
- Initial rule ideas are in `brief.json` (`rule_ideas`): 47 rules (WV-001 to WV-047) across link integrity, traceability, language, architecture, views, UI, assurance and hygiene.

Algebra used: many-sorted edge signatures (types), stratified negation (Datalog-lite), least fixed points (closure), SCC condensation with minimum-member relabelling, lexicographic topological order, dominators and transitive reduction for evidence-path lints, greedy set cover for test selection. Each has a stated oracle in [SYNTHESIS.md](research/SYNTHESIS.md) section 3.

## 5. Diagnostics and status algebra

- SARIF 2.1.0 is canonical. Profile: sorted results, rules and artifacts; `uriBaseId` for paths; explicit `columnKind`; no GUIDs, timestamps or absolute paths; `primaryLocationLineHash` also emitted for GitHub. rdjson, LSP-shaped JSON and text are generated views.
- NOT_RUN is first-class: `executionSuccessful=false` plus a tool notification. NOT_RUN absorbs PASS in aggregation, so order, threads and sharding cannot turn a skipped gate green.
- Two operators, never mixed: **join** for several pieces of evidence about one claim (information order; agrees with the kernel `aggregate_status` on every flat input up to length 6, MEASUREMENT reproduced) and **chain minimum** for conjunction across independent claims. The kernel's `aggregate_status` is order-independent but not associative (flat CONFLICT, rolled-up FAIL). The lattice is implemented and tested in `graph/`; the kernel defect goes to a separate ADR.
- Link status lifts to evidence status by a fixed map (DESIGN): COVERED to PASS, SUSPECT to STALE, ORPHANED to FAIL, AMBIGUOUS to CONFLICT, UNRESOLVED to NOT_RUN. UNWANTED is a reported defect on the covering side.
- No probabilities in gates. Confidence displays, if any, are labelled PREDICTION.

## 6. Trust model

Principle: **untrusted producers, small trusted checker, human decision.** AI proposes, the deterministic kernel checks, the owner decides.

| Actor | May | May not | Enforced by |
|---|---|---|---|
| Extractors (parsers, SCIP indexers, LLM link recovery) | Emit facts with provenance labels | Decide status, clear a suspect link, satisfy a gate with an inferred fact | Schema (inferred class cannot appear in coverage numerators); checker recomputes |
| Agents and providers | Read the graph via bounded query tools; propose links, fixes, renames, witnesses, edit translations | Approve, apply, clear SUSPECT, edit ledger, change protected policy, mint receipts | Absence of tools (MCP surface has no such tool, ADR-0041), schema with `enum` of live node ids, kernel authority checks, file-diff gate on ledger and policy paths |
| Checker (`link_status`, `assess_link`, rule runner) | Recompute everything from raw inputs and pinned tools | Trust a supplied `status`, a self-reported green, an mtime | Recompute-on-read; contract tests against `assess_receipt` semantics |
| Human owner | Append ledger entries (`ack LINK --reason`, approve statement digests), decide policy | n/a | Kernel local-decision capability; ledger is append-only |
| External tools (TLC, Bend, cvc5, OpenFastTrace) | Produce witnesses or reports | Be believed without an exact sentinel plus exit code and a pinned sha256 | Checker registry, subprocess runner |

**Trusted computing base is per link kind** (DESIGN, [assure] 2.2). Kernel floor for every kind: Python, stdlib `json` and `hashlib`, pydantic, `assess_link`, the checker registry (id, pinned version, sha256, licence, sentinel; modelled on the tla lane's `TOOLS.lock`), the subprocess runner, the status fold. Each kind adds exactly the checker it names:

| Link kind | Untrusted witness | Trusted checker | Label |
|---|---|---|---|
| generated | generator pin and output digest | kernel re-runs generator and byte-compares | GENERATED |
| model-proof | proof file | second kernel (`bend --verdict` or `leanchecker`), statement digest, assumption ledger | PROVED_IN_MODEL |
| model-check | spec and cfg | pinned TLC jar re-run | CHECKED_BOUNDED |
| solver-unsat | SMT file, optional Alethe proof | Carcara with cvc5 proof; Z3 alone is solver-trusted | PROVED_MODULO_SOLVER or SOLVER_TRUSTED |
| conformance | recorded observations or traces | kernel re-executes the real runtime and compares through the abstraction | CONFORMS_BOUNDED |
| contract or property | contracts, tests, seed | pytest or Hypothesis re-run with recorded seed | TESTED |
| human decision | sealed decision receipt | existing HMAC seal check | DECIDED |

Every PASS prints its TCB, bounds and label. A model proof is never worded as code correctness; conformance is its own link with its own status. Statements are pinned: the owner-approved digest over raw bytes lives in protected policy, agents may only add witnesses; for Bend hash each law block, for TLA+ hash property definitions and cfg. A per-proof assumption ledger (Bend `@unsafe` and foreign code, Lean `sorryAx`, Dafny `{:axiom}`, cvc5 `hole`, TLA+ `ASSUME`) is diffed against a committed report; an unlisted item is FAIL, a listed one makes the PASS say "with assumptions". Every model link needs a negative control and a reachability witness. `assess_link` mirrors `assess_receipt` (five subject dimensions: semantic, implementation, policy, environment, harness; statuses PASS, FAIL, STALE, UNKNOWN, CONFLICT, plus NOT_RUN) and never trusts a supplied status.

Honest limits: none of this is a sandbox against an agent with the owner's OS permissions (AGENTS.md); a local HMAC seal is an integrity seal, not institutional identity; the ledger's `actor` is declared, and its integrity rests on git history. See SYNTHESIS open question 2.

## 7. Determinism doctrine as testable rules

Each rule has an oracle. A permutation harness runs the pipeline over the whole matrix and requires one distinct output.

| ID | Rule | Oracle |
|---|---|---|
| D-01 | Every iteration that reaches output is sorted by a total key; every SQL result ends in a total `ORDER BY` | Shuffled insertion order gives 1 distinct output |
| D-02 | Committed graph artefacts use the RFC 8785 subset: strings, safe integers, booleans, null; no floats; keys checked | Round-trip `canonical()` equals JCS on the subset; RFC test vectors; JCS conformance test on the fact schema |
| D-03 | All I/O is explicit UTF-8, LF (`newline="\n"`); console encoding set by the CLI | Windows cp1252 console run byte-equals POSIX run |
| D-04 | No wall clock, time zone, `uuid4`, `random`, hostname or absolute path in an artefact. Any `now` is an explicit recorded input | Grep gate plus TZ matrix |
| D-05 | Paths are repo-relative POSIX; backslashes and `..` rejected | `ruff analyze graph` style key normalisation test |
| D-06 | CRLF folded to LF before hashing or parsing; identities never use raw byte offsets | CRLF and LF checkouts give one output; non-BMP character on the line |
| D-07 | Output independent of `PYTHONHASHSEED`; no `set` iteration reaches output | Seed matrix 0, 1, 2, random |
| D-08 | Locale-independent: no `locale`, no `casefold` on code-facing forms (ASCII-only forms) | `LC_ALL` matrix |
| D-09 | Ban library-default orders: `nx.condensation` labels (24 forms in 200 shuffles), `graphlib` order (5), `os.listdir`, unsorted `glob`; use `eijagraph.order` (minimum-member SCC labels, lexicographic topological order) | Lint gate and shuffle test |
| D-10 | No unrounded floats in committed files; ranking uses integer or `Fraction` fixed-iteration arithmetic then quantises, ties by id | Shuffle test; raw float hash differed 40 of 40 shuffles in the dossier sample |
| D-11 | Tool, grammar, Python minor version and rule fingerprint are in the extractor record and every cache key | Changing a pin changes the key |
| D-12 | Hashes use a domain-separation tag and length-safe encoding (no field concatenation without separator) | Collision test for `("a","bc")` vs `("ab","c")` |
| D-13 | Hash methods are versioned; a normalisation change is a new method name plus re-baseline, never a silent edit | Registry test shared with the okf lane |
| D-14 | A partial extraction is labelled partial and cannot PASS a gate | `has_error` fixture |
| D-15 | Missing prerequisite reports NOT_RUN and absorbs PASS; never a skipped-green | Missing-tool fixtures |
| D-16 | Every external-process adapter sorts its output, accepts only exact sentinel plus exit code, pins version and sha256 | Adapter contract tests with shuffled tool output |
| D-17 | Rebuild twice from a clean checkout: root hashes equal | Release gate |
| D-18 | Incremental output equals clean output after random edit sequences | Differential test (property lane strategies) |
| D-19 | Permutation harness: file order, rule order, hash seed, TZ, `LC_ALL`, CWD, CRLF, threads, non-BMP; SARIF byte-identical | Harness |
| D-20 | Windows and POSIX produce byte-identical committed goldens | Cross-platform compare (only Windows measured so far; POSIX is NOT_RUN) |
| D-21 | Temp files stay inside `.tmp/` with `TMP` and `TEMP` set | Session wrapper |
| D-22 | SARIF has no GUIDs, timestamps or absolute paths; explicit `columnKind` | Schema plus grep test |
| D-23 | Identity by id, never by label; renames are explicit records | Rename fixture |
| D-24 | Derived facts are not committed unless a gate proves rebuild equality | Manifest gate |

## 8. Incremental engine and freshness

Correctness is the Build Systems a la Carte definition: the stored result equals a clean recomputation. Cache key = SHA-256 of (rule fingerprint, sorted input content hashes) in SQLite; early cutoff when a rule's output hash is unchanged. One Merkle root per view (SCCs hashed as a unit). The cache is off by default until `graph/bench` shows a warm-run gain that justifies its bug surface (PREDICTION: on a repo this size the gain may be seconds). The release tier always does a full rebuild and compares. mtime is never a key.

## 9. Integration with each lane

Weave defines interfaces; lanes keep ownership. Nothing here edits another lane's files.

| Lane (worktree) | What weave consumes | What weave provides | Interface |
|---|---|---|---|
| okf | `repo://` grammar, `parse_uri`, `digest(root, ref, method)`, hash methods, STALE semantics, OKF pages | Typed declared-link file; generated `links` blocks; a strict profile (typed edges, broken link = error, times excluded from identity); proposed method `workflow-semantic-v1` hashing `Workflow.semantic_hash` | A `HashMethodRegistry` Protocol plus a fixture test both sides run; one shared CRLF-fold helper |
| visual | Neutral `Graph`, `Sequence`, `ClassModel` in `application/diagrams.py`; diagram provenance comment with `semantic_hash` | Lens laws suite, view mapping totality, SysML v2 emitter in the same neutral-model pattern, diagram-hash drift rule | `get(Workflow) -> ViewModel`; `translate(ViewModel, Edit) -> Accepted(...) or Rejected(code, reason)` |
| agents | MCP server (`mcp==2.2.0`), `AgentSurface`, redaction, consent rules | Query set with `outputSchema`: `node`, `neighbors`, `impact`, `context(budget)`, `explain`, `violations`, `link_status`, `ui_links`, `language.lookup`, `language.check`; proposal-only `translate`; per-session JSON Schema with `enum` of live ids | Every result bounded, sorted, hash-carrying, with `complete` and `frontier`; no free-form query by default |
| quality | ruff, mypy strict, import-linter layers, grimp import graph, complexity ratchet, nox plugin pattern | `quality/sessions/graph.py` (tags `fast`, `full`, `release`); intended-architecture reflexion (agree, differ, missing) against the import graph; adapters turning their output into `Finding` | Sessions use `python=False`; missing tools NOT_RUN |
| metrics | Budgets and ratchet conventions, `eija.metrics.v1` document | Graph metrics (coverage ratios, impact size, redundancy k, H and S counts) as a new section, labelled MEASUREMENT | Deterministic sections vs timing sections separated |
| tla | `TOOLS.lock` pattern, `ExcursionTrace`, abstraction and conformance harness | Link certificate `conformance` and `model-check` witness schema; statement pin over property definitions and cfg | Witness `{kind, subject digests, artefact, tool pin, raw observations}` |
| bend | `bend_runner.classify` sentinel rule, negative controls, drift check | `model-proof` witness schema; statement pin over each `law` block; assumption ledger extractor | Same witness shape; `--verdict` second check or NOT_RUN |
| smt-bmc | Z3 soundness and bounded model checking outputs | Policy: try cvc5 Alethe plus Carcara for supported theories before calling unsat proved; `hole` steps rejected or ledgered | Same witness shape |
| property | Hypothesis strategies and reference model | Law tests (GetPut, PutGet mod layout, conditional PutPut), incremental-equals-clean generator | Reuse strategies; results labelled MEASUREMENT on the tested alphabet |
| mutation | cosmic-ray sessions and scores | Attaches mutation score to `covers` and `verifies` edges as calibration | Edge attribute `fault_detection` with tool pin |
| hci | Playwright pin, axe results, journey | Sidecar UI model, `data-eija-key` contract, UIL-001 to 008; rendered tier reuses their browser one at a time | Results attached to UI keys; NOT_RUN without Chrome |
| kernel (`src/`) | `impact.closure`, `aggregate_status`, `assess_receipt`, `Workflow.semantic_hash`, `canonical()` as reference oracles in tests | Nothing. Kernel changes are separate ADRs and PRs: JCS, status lattice, explicit `operation_id`, server-computed available actions | `eijagraph` runtime never imports `eija_studio` |

## 10. Rollout, gates and exit criteria

| Phase | Scope | Exit criterion (measurable) |
|---|---|---|
| P1 core | Canonical writer, `eijagraph.order`, fact schema, SQLite index, closure tested against `impact.closure`, `link_status`, link record and declared-link file, Python, JSON, Markdown and HTML extractors, 8 first rules, SARIF writer, permutation harness | Rebuild twice gives one root hash; harness gives 1 distinct output on Windows; incremental equals clean; negative-oracle fixture per rule fails as designed |
| P2 views and language | Term registry and bijection checks, UI static tier (UIL-001, 002, 006, 007, 008), lens laws, mapping totality, SysML v2 emitter with golden, intended-architecture reflexion | Golden files stable; static tier runs Python-only in the `fast` tier; SysML validator run or NOT_RUN |
| P3 assurance and agents | `assess_link`, checker registry, statement pinning, assumption ledgers, tla and bend witness adapters, MCP query set, transcripts, pass^k harness, UI rendered tier (one browser, serial), tree-sitter and LibCST adapters | Every proof link prints its TCB and label; a weakened pinned statement gives FAIL in a seeded test |
| P4 measurement | Re-measure hash-method choice on EIJA history; hci and eval study with and without graph context and semantic diff | Numbers with n, model id, date; PREDICTION labels removed only by data |

Nox sessions in `quality/sessions/graph.py`: `fast` = static rules over the repo, determinism unit tests; `full` = permutation harness, differential incremental test, rendered UI tier (NOT_RUN without Chrome); `release` = double rebuild, external-tool validators, POSIX golden compare. Heavy work runs serially on the shared 16 GB PC; temp data in `.tmp/`.

## 11. ADR allocation for block 0089-0112

This table supersedes the numbers proposed inside individual dossiers (SYNTHESIS R12). Files are `docs/adr/00NN-weave-<slug>.md` from `docs/adr/template.md` including its OSS-check table.

| ADR | Decision | Dossier origin |
|---|---|---|
| 0089 | The graph is a derived, rebuildable index; truth classes; manifest and rebuild gate | [gdb] |
| 0090 | Node identity: `repo://` ids, fragment registry, rename maps | [code], [trace] |
| 0091 | Canonical serialisation and hashing: RFC 8785 subset, domain tags, length-safe encoding | [math], [bx] |
| 0092 | Typed schema: node and edge signatures, SysML v2 term mapping, ProofMap pruning | [mde] |
| 0093 | Link record, hash method per link kind, `link_status`, early cutoff | [trace] |
| 0094 | Human ledger, `ack`, agent boundary on clearing and policy | [trace], [assure] |
| 0095 | Extractor protocol, ladder and provenance labels; optional SCIP adapters | [code] |
| 0096 | Storage and query semantics: SQLite, total ORDER BY, closure as reference | [gdb] |
| 0097 | Rule model: strata, violation queries, witnesses, load-time negation check | [math], [gdb] |
| 0098 | Finding model, SARIF profile, suppression ledger | [incr] |
| 0099 | Determinism doctrine D-01 to D-24 and the permutation harness | [math], [incr] |
| 0100 | Incremental engine: verifying traces, early cutoff, cache off by default | [incr] |
| 0101 | Status lattice (weave side) and the kernel ADR request for `aggregate_status` | [math] |
| 0102 | Link certificates, `assess_link`, claim-relative TCB, checker registry | [assure] |
| 0103 | Statement pinning and assumption ledgers | [assure] |
| 0104 | Claim graph lint (no claim-to-claim edge, acyclic, defeaters) and GSN export | [assure] |
| 0105 | View lenses: laws, edit translators, SysML v2 emitter, reflexion vs intended architecture | [bx], [mde] |
| 0106 | Ubiquitous-language registry, bijection checks, generated exports | [lang] |
| 0107 | UI sidecar model, `data-eija-key`, UIL rules, static and rendered tiers | [ui] |
| 0108 | Agent query set, per-session schemas, transcript record and replay, pass^k harness | [agent] |
| 0109 | Export adapters: SCIP, Cypher/CSV, Soufflé facts, SKOS, Contextive, Vale, cspell | [gdb], [lang] |
| 0110 | Codemods and fix proposals with precondition hashes | [incr], [code] |
| 0111 | Benchmarks and the evidence ledger (`graph/bench`), label policy | all |
| 0112 | Reserved: index of kernel change requests raised by this lane | all |

Every ADR that adds a custom module carries the OSS-check table and a row in `docs/oss/REGISTER.md`. Extra `graph` pins `==`.

## 12. Answers to the owner's questions in one place

- Is Neo4j used? As an optional one-way export, run by a user as a separate process; never in the trust path. Reasons: GPL-3.0 server, second stateful store, no speed benefit at our scale, undefined row order.
- Is OKF used? Yes: as the readable, generated projection and the prose authoring surface (okf lane), with typed hash-anchored links in a sidecar and a strict profile.
- What maths do we use? Those in SYNTHESIS section 3 that change a measured number or remove a measured failure: fixed points, SCC and lexicographic order, stratified rules, Merkle roots and early cutoff, canonical forms, keyed diff, set cover, lens laws as tests, certifying checkers. Category theory, sheaves, information theory and probabilistic confidence are theory-only.
- What makes it deterministic? Section 7, with a harness that requires byte-identical output.
- What makes humans understand more? Unmeasured. The design gives them witnesses, SUSPECT lists and semantic diffs; the claim stays a PREDICTION until the hci and eval lanes measure it.
