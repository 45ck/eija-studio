# Code intelligence and analysis: extracting a symbol graph with stable identities

Lane: weave. Dossier: code-intelligence. Date: 2026-09-29 (all sources accessed 2026-09-29). Status: research input to ADR-0089..0112, not a decision.

## Decisions first

1. **Build a small, layered fact extractor; do not adopt a code-intelligence server.** Every tool that gives *semantic* cross-references (SCIP indexers, Kythe, Glean, CodeQL, Joern) needs Node, JVM, Bazel or a proprietary licence, and none gives byte-stable output without our own canonicalisation. The reusable parts are the *formats and ideas* (SCIP's symbol grammar, Glean's immutable fact DAG, Soufflé's proof trees), not the engines.
2. **Extractor ladder, each fact labelled with how it was obtained.** L0 file digests; L1 syntactic symbols (Python: stdlib `ast`; TS/JS/HTML/CSS/JSON/Markdown: pinned tree-sitter grammars); L2 name resolution (Python: LibCST for imports and qualified names; TS/Python semantic resolution only through an optional SCIP indexer process); L3 derived relations (Datalog-style rules over the facts). A fact records `source` (exact / syntactic / candidate-set / tool-resolved), tool and version. Missing tool means NOT_RUN, never an empty PASS.
3. **Identity is a name, integrity is a hash, and they are separate.** Symbol id = `<lang>:<repo-relative POSIX path>#<qualified name>` (aligned with the okf lane's `repo://path#fragment`); the content hash (okf `ast-v1`, `ast-sig-v1`, `ast-api-v1`) says whether the thing changed. A rename is an explicit record (old id, new id), produced by a LibCST codemod, never inferred by similarity.
4. **Dependencies (extra `graph`, pinned `==`)**: `tree-sitter` plus grammar wheels (MIT), `libcst` (MIT, PSF parts). **Optional processes**: scip-typescript, scip-python (Node), Soufflé (Linux/macOS; source build on Windows), Semgrep or Opengrep (LGPL, rules licence caveat), universal-ctags (GPL, process boundary only). **Rejected**: CodeQL (licence), OpenRewrite for Python/TS (source-available), stack-graphs and DDlog (archived), LSIF (superseded).
5. **Derived facts come from rules with recorded derivations.** Generalise `domain/impact.py` (least fixed point) to a tiny semi-naive rule evaluator or SQLite `WITH RECURSIVE`; store the rule id and premises of every derived edge (proof tree). Soufflé is an optional accelerator, not the semantics.

## 1. Scope and method

**Question.** What is the best deterministic way to extract a symbol graph, with stable identities, from Python, TypeScript/JS, HTML/CSS, Markdown and JSON, and which tools are dependencies versus optional processes?

**Method.** For each tool: repository metadata (licence, archived flag, last push) from the GitHub API on 2026-09-29; latest release from the GitHub releases API or PyPI JSON; README and licence text opened; specifications (RFC 8785, RFC 6901, SCIP proto, LSP) opened. Four **local measurements** on this PC (Windows 11, Python 3.12.10; probes in `docs/weave/research/code-intelligence-probes/`). Lessons from ProofMap Lite read from its README, `docs/gap-audit.md`, `docs/source-review.md`.

**Limits.** The WebSearch budget for the session was exhausted (200 of 200), so discovery was by direct fetch of known primary pages, not by open search; tools I did not think of are missing. Page content was read through a summarising fetcher; where a licence or status claim matters I re-read the raw file (`gh api .../contents`) and say so. No fetched page's instructions were followed and no fetched code was run. See section 6 for unverified items.

**Measurements** (label: MEASUREMENT, not general claims):

| ID | What | Result |
|---|---|---|
| M1 | tree-sitter 0.26.0 with six grammars: parse a sample per language twice, hash node type and byte range per node; repeat with CRLF | Identical hash across runs for all 8 grammars; **CRLF changes every byte range** (hash differs), so identities must not use raw offsets and text must be LF-folded first. Grammar ABIs differ (14 for TS, HTML, JSON; 15 for Python, JS, CSS, Markdown). |
| M2 | tree-sitter on broken Python (unclosed parameter list) | `has_error` true; only class `A` recovered, **`f` and `g` lost**. stdlib `ast.parse` raises `SyntaxError`. Error-recovered trees are partial, so a fact set from one must be marked partial, not complete. |
| M3 | LibCST 1.9.0 `FullyQualifiedNameProvider` on a sample with a relative import, a `try/except` import pair, `self.f()` and `x.f()` | `W()` resolved to `eija_studio.domain.models.Workflow`; `toml.loads` gave **two candidates** (`tomllib.loads`, `tomli.loads`); `self.f()` became `A.g.<locals>.self.f` and `x.f()` `h.<locals>.x.f`: **no attribute or type resolution**. On Windows `FullRepoManager` needed absolute paths. |
| M4 | `ast` versus tree-sitter-python definition extraction over `src/**/*.py` (23 files) | 167 definitions each, no file differs; 44 ms (`ast`) versus 28 ms (tree-sitter) for the whole tree. Speed is irrelevant at this scale; agreement is the useful result. |
| M5 | `ruff analyze graph src` (ruff 0.15.7) three runs, two `PYTHONHASHSEED` values | Byte-identical output; stderr says the command "is experimental and may change without warning"; **keys use backslash paths on Windows**. |
| M6 | Kernel `canonical()` (`sort_keys`) versus RFC 8785 | Key order differs for a non-BMP key versus a BMP key above U+E000 (code point order versus UTF-16 code-unit order); Python emits `1.0` and unbounded integers, JCS requires ECMAScript number form and IEEE 754 range. `canonical()` is **not** JCS. |

## 2. Tools and schools, one by one

### 2.1 Parsing and structure

**tree-sitter** (MIT; core v0.27.0, 2026-08-30; active). Incremental parser with error recovery, C11 runtime, no dependencies ([S1]). Official grammars for Python, JS, TS, HTML, CSS, JSON are MIT with Windows wheels on PyPI; Markdown is `tree-sitter-grammars/tree-sitter-markdown` (MIT) ([S58], [S59]). Gives: uniform concrete syntax trees and a `tags` query convention for definitions and references (role and kind captures) ([S2]). Does not give: name resolution (tags identify entities and locations; resolution is our inference from the docs' scope, M3 shows the syntactic ceiling for the analogous Python case). Cost: pin grammar versions (they are separate packages with separate ABIs, M1), fold CRLF, treat `has_error` as partial (M2). **Verdict: dependency** (extra `graph`).

**Python stdlib `ast` and `symtable`**. The grammar "might change with each Python release"; `col_offset` is a UTF-8 byte offset; `ast.unparse` does not round-trip source ([S49]). `symtable` classifies scopes (local, free, global, nonlocal) but cannot see `exec`/`eval` ([S50]). Gives: exact syntax and scope facts with no dependency; the okf lane already hashes via `ast`. Cost: must record the Python minor version in provenance. **Verdict: dependency (stdlib) for Python L1**, cross-checked against tree-sitter (M4).

**LibCST** (MIT; PSF-dual parts listed in its LICENSE; v1.9.0, 2026-08-11). Lossless CST that "keeps all formatting details", plus a codemod framework ([S34], [S36]). Metadata providers give scopes and qualified names, explicitly without type inference and with multiple candidate names for conditional imports ([S35]; matches M3). Gives: deterministic rename and rewrite with formatting preserved (the write-back half of a bidirectional transformation). Cost: native wheel; API friction on Windows paths (M3). **Verdict: dependency** for L2 Python imports/qualified names and for codemods.

**Language Server Protocol** (spec CC-BY-4.0 repo). JSON-RPC with `definition`, `references`, `documentSymbol`; positions default to UTF-16 code units unless negotiated; responses only "roughly" in request order ([S10]). Gives: universal editor interface. Does not give: a persistent, canonical graph; results depend on server state. **Verdict: inspiration** (position-encoding lesson: store UTF-8 byte offsets and convert at the edge).

**ctags** (Universal Ctags, GPL-2.0; v6.2.1 2025-10-25). Fast syntactic tags for Python, JS, TS, HTML, CSS, JSON, Markdown; JSON output needs libjansson; default sort by tag name ([S19], [S20]). Gives: nothing tree-sitter does not, with a copyleft binary. **Verdict: optional process, not recommended** (only as a fallback for languages with no grammar).

**Doxygen** (GPL-2.0; output declared not covered by the licence; Python among supported languages; XML output for tools) ([S47], [S48]). Documents C++-first; Python support is docstring-oriented. **Verdict: inspiration** (its XML-as-interchange idea); not used.

### 2.2 Code-intelligence formats and systems

**SCIP** (Apache-2.0; repo now under `scip-code`, v0.10.0 2026-09-03). Protobuf schema; symbols are human-readable strings `scheme package descriptors` ([S4]); design goals: file-level incrementality, parallel indexing, limited blast radius of wrong data; explicitly a producer-oriented transmission format, not storage or consumer convenience ([S5]). The proto states only the `metadata` field order; "other field values may appear in any order" ([S4]), so **a SCIP file is not canonical**: EIJA must sort on decode. Bindings exist for Go, Rust, Java, Kotlin, .NET, Haskell, TypeScript; **none for Python** ([S3] listing), so decode via protobuf codegen from `scip.proto` (the PyPI package named `scip` is an unrelated project). The `scip` CLI has `print`, `lint`, `snapshot`, `stats`, `test` ([S6]). Vendor claims that SCIP is 4-8x smaller than LSIF are Sourcegraph's and Meta's own statements ([S7]). **Verdict: export target and optional input.** Adopt the symbol *grammar* for our ids; consume `index.scip` from optional indexers.

**scip-typescript** (Apache-2.0; needs Node 22 or 24; `--infer-tsconfig` for JS) ([S60]). Uses the TypeScript compiler (Apache-2.0) for real resolution. **Verdict: optional process** for TS/JS L2.

**scip-python** (a Sourcegraph fork of pyright; `LICENSE.txt` opens with Pyright's MIT notice; the remainder of the file was not read; Node 16+, Python 3.10+, may need 8 GB heap) ([S61]). **Verdict: optional process**, heavy, UNVERIFIED licence in full.

**LSIF** (spec 0.6.0 still marked "under construction"; `lsif-py` and `lsif-node` archived, last pushes 2022) ([S8], [S9], [S59]). Numeric ids and dynamic graph shape were the stated reasons SCIP replaced it ([S7]). **Verdict: reject.**

**Kythe** (Google; Apache-2.0; pushed 2026-09-18; Bazel build; indexers for C++, Go, Java) ([S11]). Identity is a five-field VName (signature, corpus, root, path, language) ([S12]). **Verdict: inspiration**: adopt the idea that identity is a tuple with a corpus/root, so a monorepo path move is one field change.

**Glean** (Meta; BSD-style licence, raw LICENSE read; pushed 2026-09-28). Facts are immutable typed terms forming a DAG, stored content-deduplicated in RocksDB, stacked databases for incrementality, Angle query language "similar to Datalog", can ingest SCIP/LSIF ([S13], [S14], [S15]). **Verdict: inspiration** for the fact model (immutable, typed, derived facts distinguished from base facts). Running Glean is out of proportion for this repo.

**stack-graphs** (GitHub; Apache-2.0 or MIT; **archived 2025-09-09**, "no longer supported or updated by GitHub") ([S16]). Name binding as path finding in a per-file graph built by a tree-sitter-graph DSL, no build needed ([S17], [S18]). **Verdict: inspiration only**; do not depend on an archived engine. The lesson is per-file isolation of facts, which SCIP also has.

### 2.3 Code property graphs, query engines, pattern tools

**Joern** (Apache-2.0; v4.0.640 2026-09-28; JVM). Code property graph (AST + control flow + program dependence) with a Scala query DSL; exports GraphML and Neo4j CSV ([S21], [S22]). The concept is from Yamaguchi et al., IEEE S&P 2014 ([S23]). **Verdict: optional process** for deep dataflow when a lane needs it; CPG concept is inspiration. The docs' language-maturity table looked dated; treat maturity as UNVERIFIED.

**CodeQL.** The queries and libraries repository is MIT ([S25]) but the CLI and engine are under GitHub CodeQL Terms: allowed for academic research, demonstrations, and analysis of an **Open Source Codebase**, including CI only when hosted on GitHub.com; **not** allowed to generate databases for automated analysis or CI otherwise, nor to use it with non-open-source code such as a private repo, unless the user has GitHub Advanced Security; no redistribution or hosting for others ([S24], [S26]). EIJA is an assurance tool for other people's (often closed) code. **Verdict: reject** as dependency and as optional process we ship; users with a licence may point us at SARIF they produce.

**Semgrep OSS** (engine LGPL-2.1; v1.178.0 2026-09-23; Windows wheel exists) ([S27], [S58]). The community **rules** repo is under the Semgrep Rules License v1.0, which (per the licence page summary; full text to be re-read before use) limits use to internal business purposes and forbids redistribution or offering as a service ([S28], [S29]) so we cannot vendor those rules into an Apache-2.0 repo. **Opengrep** is an LGPL-2.1 fork by a vendor consortium made after Semgrep moved features to a commercial licence (their statement), rule-compatible ([S30]). **Verdict: optional process** with our own rules; engine LGPL is acceptable across a process boundary.

**ast-grep** (MIT; 0.45.3 2026-08-31; tree-sitter based; `ast-grep-py`/`ast-grep-cli` wheels for win_amd64) ([S31], [S58]). YAML rules for structural search, lint and rewrite. No determinism statement in docs ([S31]); we make it deterministic by sorting results and pinning. **Verdict: dependency (optional extra)** for architecture and vocabulary lint rules across TS/HTML/CSS where LibCST does not apply. ProofMap Lite already uses it ([S64]).

**Comby** (Apache-2.0; latest release 1.8.1 on 2022-06-28 though the repo has 2026 pushes; OCaml, binaries documented for Homebrew and Ubuntu only) ([S32], [S59]). **Verdict: inspiration**; ast-grep covers the use with Windows wheels.

**OpenRewrite** (Apache-2.0 core and Java/Kotlin/XML/YAML modules; JS/TS, Python, C#, Go modules under the **Moderne Source Available License**: not to be commercialised or offered as a managed service) ([S33]). **Verdict: reject** for Python and TS; LibCST and ast-grep do the job under OSI licences.

### 2.4 Datalog and incremental evaluation

**Soufflé** (UPL-1.0; v2.5 2025-03-24; last push 2026-07-13). Datalog compiled to C++ or interpreted, semi-naive evaluation and magic sets, provenance/explain giving minimal-height proof trees (default depth 4; cannot explain non-existence automatically) ([S37], [S38]). Binaries for Ubuntu, Fedora, Oracle Linux, macOS; Windows needs a source build ([S39]). **Verdict: optional process** for large analyses on Linux/WSL; UPL is permissive. Output order is not documented as sorted: UNVERIFIED, so sort in our adapter.

**Doop** (UPL-1.0 with third-party components; Java bytecode and Android points-to; runs on Soufflé) ([S40]). **Verdict: inspiration** (points-to analyses as a rule library); not our languages.

**Ascent** (MIT; Rust macros; lattices, parallel; peer-reviewed CC 2022 and OOPSLA 2023 papers per its README) ([S41]). **Verdict: inspiration**; Rust toolchain out of proportion.

**DDlog** (MIT; **archived**, repo now `vmware-archive`, last push 2023-07-07; no successor named) ([S42]). **Verdict: reject.** **differential-dataflow** (MIT; active) is the Rust engine underneath ([S43]); **theory-only** until we need incremental recomputation beyond per-file caching.

**SQLite recursive CTEs** (stdlib `sqlite3`, already the kernel's store). `UNION` (not `UNION ALL`) discards repeated rows so cyclic graphs terminate; `ORDER BY` in the recursive select fixes the extraction order; no aggregates in the recursive part ([S53]). **Verdict: dependency (already present)** for transitive closure over stored edges.

### 2.5 Python to UML and dependency graphs

| Tool | Facts | Verdict |
|---|---|---|
| pyreverse (in pylint, GPL-2.0-or-later) | UML from Python code, dot/PlantUML/Mermaid output; docs do not describe limits ([S44], [S58]) | Reject: the visual lane already generates diagrams from the executable model; GPL only as a process |
| py2puml (MIT) | PlantUML classes from annotations and constructors only; never evaluates code; misses unannotated attributes ([S45]) | Inspiration (its "annotations only, no evaluation" stance) |
| pydeps (BSD-2) | Import graph from bytecode; needs Graphviz; only imports found by the import machinery ([S46]) | Reject; grimp (BSD-2, used by import-linter in the quality lane, [S58]) or `ast` imports are enough |
| `ruff analyze graph` (MIT) | JSON import map; experimental; backslash keys on Windows (M5) | Optional process; normalise paths |

### 2.6 Mathematical and CS schools

Covered in the mechanisms table (section 4): Datalog and least fixed points, provenance, content-addressed Merkle structures, incremental computation, graph theory (SCC condensation), name binding as graph search, term rewriting and bidirectional transformation, canonical serialisation.

### 2.7 Lessons from ProofMap Lite

From its `docs/gap-audit.md` ([S64]): (a) evidence carries an **inferred versus canonical** label, and Graphify output is scanned as *inferred* `code_graph` evidence; (b) generated timestamps caused churn (GAP-003), so regenerate byte-identically; (c) freshness by a **sha256 evidence snapshot**, not by mtime (GAP-015 and GAP-025); (d) drift warnings must map to a change bundle and a prompt, not prose (GAP-029); (e) untracked generated files bypassed a clean-tree gate (GAP-033). Graphify (Apache-2.0 or MIT) parses code with tree-sitter locally and uses an LLM for docs and images, tagging edges EXTRACTED or INFERRED ([S63]): its LLM half is non-deterministic by construction, so only its AST half is admissible as a deterministic source. **Verdict: inspiration and comparison baseline**, not a dependency.

## 3. Table of options

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| tree-sitter + grammars | MIT | active; core v0.27.0 | dependency | uniform syntax layer, Windows wheels | S1, S58, S59 |
| Python `ast`, `symtable` | stdlib (Python licence not checked) | stdlib | dependency | exact Python syntax and scopes, no install | S49, S50 |
| LibCST | MIT (+PSF-dual files) | v1.9.0, active | dependency | qualified names, lossless codemods | S34-S36 |
| ast-grep | MIT | 0.45.3, active | dependency (optional extra) | structural lint and rewrite, TS/HTML/CSS | S31, S58 |
| SQLite recursive CTE | stdlib module (SQLite licence not checked) | stdlib | dependency | closure with cycle safety | S53 |
| scip-typescript | Apache-2.0 | active | optional process | real TS/JS resolution; Node 22/24 | S60 |
| scip-python | MIT (pyright) + unread rest | active | optional process | semantic Python resolution; heavy | S61 |
| SCIP format | Apache-2.0 | v0.10.0, `scip-code` org | export target / input | symbol grammar, per-file docs; not canonical | S3-S7 |
| Soufflé | UPL-1.0 | v2.5; Linux/macOS binaries | optional process | fast Datalog, proof trees | S37-S39 |
| Joern | Apache-2.0 | v4.0.640, active | optional process | dataflow CPG, JVM | S21-S23 |
| Semgrep engine / Opengrep | LGPL-2.1 | active | optional process | pattern rules across a process boundary | S27, S30 |
| Semgrep community rules | Semgrep Rules License v1.0 | active | reject (do not vendor) | internal-use, no redistribution | S28, S29 |
| universal-ctags | GPL-2.0 | v6.2.1 | optional process (fallback) | syntactic tags only | S19, S20 |
| `ruff analyze graph` | MIT | experimental | optional process | import map; normalise paths | S62 (M5) |
| Graphify | Apache-2.0 / MIT | active | inspiration | AST half deterministic, LLM half not | S63 |
| Kythe | Apache-2.0 | active, Bazel | inspiration | VName identity tuple | S11, S12 |
| Glean | BSD-style | active | inspiration | immutable typed fact DAG | S13-S15 |
| stack-graphs, tree-sitter-graph | Apache-2.0 or MIT | stack-graphs **archived** 2025-09-09 | inspiration | per-file name-binding graph | S16-S18 |
| Doop, Ascent | UPL-1.0, MIT | active | inspiration | rule libraries, lattices | S40, S41 |
| differential-dataflow | MIT | active | inspiration | incremental joins, Rust | S43 |
| Doxygen | GPL-2.0 (output unaffected) | active | inspiration | XML interchange | S47, S48 |
| pyreverse, py2puml, pydeps | GPL-2.0+, MIT, BSD-2 | active | reject / inspiration | visual lane covers diagrams | S44-S46 |
| LSP / LSIF | CC-BY-4.0 spec / archived indexers | LSIF 0.6.0 unfinished | inspiration / reject | editor protocol; superseded format | S8-S10 |
| CodeQL | MIT queries; CLI under GitHub CodeQL Terms | active | reject | no closed-source or general CI use without GHAS | S24-S26 |
| OpenRewrite (Py/TS modules) | Moderne Source Available | active | reject | not OSI; Apache only for Java-family | S33 |
| DDlog | MIT | **archived** | reject | no maintainer, no successor named | S42 |
| Comby | Apache-2.0 | last release 2022 | inspiration | ast-grep replaces it | S32 |

## 4. Mechanisms (math and CS)

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Datalog / fixed points | Derived relations (calls-transitively, impact, trace-to-test) as rules over base facts, evaluated semi-naively | Result should not depend on evaluation order (positive rules); one mechanism for impact, layering and traceability; generalises `impact.closure` | Negation and aggregation need stratification; order-independence is textbook and UNVERIFIED this session, so it is tested by shuffle-invariance property tests | **adapt**: tiny in-repo evaluator or SQLite CTE; Soufflé optional | S37, S53 |
| Provenance | Each derived edge stores rule id and premise ids (a proof tree); "why is this affected?" is a lookup | Explainability for humans and agents; Soufflé does this with minimal-height trees | Storage; no explanation of non-existence | **adapt** (proof trees). Full semiring provenance (Green, Karvounarakis, Tannen, PODS 2007, exists per Crossref) is **theory-only**: no theorem is used here | S38, S56 |
| Content-addressed Merkle | Digest per normalised file, per symbol, per directory; Git's object model is the precedent | O(changed) recomputation; stale detection; identical inputs give identical ids | Normalisation choices define what "changed" means (formatting, CRLF); hash proves change, not truth | **adopt** (okf lane already implements symbol hashes) | S54 |
| Incremental computation | Cache by (tool id and version, grammar version, normalised content hash); per-file facts as in SCIP documents and stack-graphs | Cheap re-index; parallel; blast radius of a bad fact limited to a file | Cross-file facts need invalidation from the impact closure; DDlog archived | **adapt**: per-file caching only; differential-dataflow **theory-only** | S5, S17, S42, S43 |
| Graph theory | SCC condensation of import/call graphs; cycle reports; layered order | Explicit cycle handling; DAG for layering checks; deterministic topological order after sorting | Adds `networkx` (BSD-3) or ~30 lines of own Tarjan | **adopt** (decide in ADR; own code is small) | S55 |
| Name binding as graph search | Resolution as path finding (stack graphs); candidate sets when ambiguous | Honest "resolved / candidate(n) / unresolved" status instead of guesses (M3) | Engine archived; full binding needs a compiler | **adapt**: the status vocabulary; **theory-only**: the engine | S16, S17, S35 |
| Term rewriting / bidirectional transformation | LibCST codemods and ast-grep rewrites as the only sanctioned write-back; rename emits an (old, new) map | Deterministic, reviewable refactors; ids survive by explicit mapping | Covers syntactic renames, not semantic equivalence | **adopt** | S31, S34 |
| Canonical serialisation | RFC 8785 JCS for any hash computed in more than one language | Cross-language byte identity | Kernel `canonical()` is not JCS (M6); JCS forbids duplicate keys and non-IEEE numbers | **adapt**: fact schema allows only strings, safe integers, booleans, null, ASCII identifier keys, where `canonical()` and JCS coincide; add a conformance test against JCS | S51, M6 |
| JSON Pointer | Address JSON values by RFC 6901 pointer | Stable under object key reorder | **Not** stable under array insertion or reorder | **adapt**: pointer plus key-field addressing (`id`, `name`) where the schema declares one | S52 |

## 5. Extraction by language: identity and dependency choice

| Language | L1 (dependency) | L2 (optional) | Identity | Hazards |
|---|---|---|---|---|
| Python | `ast` (definitions, imports, scopes via `symtable`); LibCST for qualified names | scip-python | `py:src/eija_studio/domain/impact.py#closure`, methods `#Cls.meth`; duplicates get `~2` by source order and are flagged unstable | conditional imports give candidate sets; `self.x` unresolved (M3); Python-version-dependent AST |
| TS / JS | tree-sitter typescript, javascript (ABI 14 and 15) | scip-typescript (TS compiler) | `ts:path#Export.member`; SCIP descriptor string in `scip:` field when available | overloads, declaration merging, re-exports need L2; dynamic `require` |
| HTML | tree-sitter html | none | `html:path#id=app`, else `data-testid`, else tag-path with ordinal (flagged positional) | templating languages are not HTML; attribute order must be sorted |
| CSS | tree-sitter css | none | `css:path#<normalised selector>@<at-rule chain>` | cascade and specificity are not computed; duplicates by ordinal |
| Markdown | tree-sitter markdown (or a CommonMark parser) | none | `md:path#<heading slug path>`; terms and table rows as in okf `md-bold-term-v1`, `md-table-row-v1` | duplicate headings; slug rules must be pinned |
| JSON | stdlib `json` with duplicate-key rejection | none | `json:path#/pointer`, plus key-field addressing | array index instability (RFC 6901); numbers beyond 2^53 |

Common determinism rules: repo-relative POSIX paths (M5 shows why); files read as bytes, decoded UTF-8, CRLF folded to LF before hashing or parsing (M1); every collection sorted by a total key; tool and grammar versions in an `extractor` record and in the cache key; no wall-clock in any artefact (ProofMap GAP-003); sorted-output adapter for every external process; `NOT_RUN` when a prerequisite is absent.

## 6. Implications for EIJA

1. **ADR: symbol id grammar and extractor ladder.** Adopt the id form in section 5, align with okf `repo://` URIs, and reuse its hash methods instead of new ones; provenance labels `exact | syntactic | candidate(n) | tool-resolved | unresolved`.
2. **Package `graph/eijagraph/extract/`**: `ast`, tree-sitter and LibCST adapters behind one `Extractor` protocol returning sorted, typed facts; extra `graph` pins tree-sitter, six grammars and libcst with `==`. No import from `src/`.
3. **Conformance tests, not trust.** Cross-check `ast` versus tree-sitter definitions on the repo (M4 already agrees at 167); CRLF and reformat invariance; shuffle-invariance of file order and rule order; byte-identical output on Windows and POSIX; a JCS conformance test on the fact schema (M6).
4. **Facts versus derived facts, as in Glean.** Base facts are immutable and content-addressed; derived edges carry rule id and premises. Rules start as `impact.closure` generalised; SQLite recursive CTE for stored graphs.
5. **Optional processes are adapters with pinned versions and NOT_RUN.** scip-typescript and scip-python produce `index.scip`; we decode with protobuf codegen from `scip.proto`, sort every repeated field, and label results tool-resolved. Soufflé only behind the same rules format, Linux/WSL.
6. **Licence hygiene in the OSS register.** Do not vendor Semgrep community rules; never ship or require CodeQL; universal-ctags, pylint and Doxygen only as user-installed processes if at all; record each row with licence text location in `docs/oss/REGISTER.md`.
7. **Rename and refactor path.** LibCST codemods emit the rename map; the graph compiler rejects a change that removes an id without a map entry (drift as a lint error, consistent with the product thesis).
8. **Partial parses are partial facts.** A file with `has_error` yields facts marked partial and a diagnostic; no gate may PASS on a partial extraction (M2).
9. **Do not adopt Graphify or ProofMap's TypeScript code as a runtime.** Reuse its lessons: sha256 freshness snapshot, inferred-versus-canonical label, no timestamps, drift tied to change bundles.
10. **Export, do not host.** Emit SCIP for external navigation tools and GraphML or CSV for graph databases in the graph-database dossier; Neo4j, Kuzu and others are decided there, not here.

## 7. Gaps and unverified items

- **UNVERIFIED**: order-independence of positive Datalog (textbook, not opened); Soufflé output ordering; Glean and Kythe Windows buildability; Joern current language maturity (docs table looked stale); CodeQL supported languages; scip-python full licence text beyond its first lines; Semgrep Rules License full text (read only as a summary); DDlog archive date (page says 2026-07-13, API says archived with last push 2023); parse5 status (GitHub shows archived, not investigated); pyreverse limits (docs silent); grimp API and its determinism (only PyPI metadata read); whether `tree-sitter-language-pack` (MIT, 371 grammars) downloads or bundles parsers at install time (not opened).
- **Not tested**: scip-typescript and scip-python end to end (Node not exercised, no measurement of index determinism); tree-sitter grammar upgrades changing tree shape (0.23.6 versus 0.25.0 Python grammars gave the same tree on one small sample: not a proof); Markdown and HTML identity collisions on real repositories; Windows versus POSIX byte identity (only Windows was run).
- **Not covered**: graph databases (Neo4j GPL-3.0 per GitHub API, Kuzu archived 2025-10) are the graph dossier's topic; UML/MDE round-trip tools; formal-method tool integration; mutation and property tools.
- **Search**: no open web search was possible; tools not named in the brief may exist (for example Python call-graph analysers).

## Sources (all accessed 2026-09-29)

S1 https://tree-sitter.github.io/tree-sitter/ · S2 https://tree-sitter.github.io/tree-sitter/4-code-navigation.html · S3 https://github.com/scip-code/scip · S4 https://raw.githubusercontent.com/scip-code/scip/main/scip.proto · S5 https://github.com/scip-code/scip/blob/main/docs/DESIGN.md · S6 https://github.com/scip-code/scip/blob/main/docs/CLI.md · S7 https://sourcegraph.com/blog/announcing-scip · S8 https://microsoft.github.io/language-server-protocol/overviews/lsif/overview/ · S9 https://github.com/microsoft/language-server-protocol/blob/gh-pages/_specifications/lsif/0.6.0/specification.md · S10 https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/ · S11 https://github.com/kythe/kythe · S12 https://kythe.io/docs/kythe-storage.html · S13 https://github.com/facebookincubator/Glean · S14 https://glean.software/docs/introduction/ · S15 https://github.com/facebookincubator/Glean/blob/main/LICENSE · S16 https://github.com/github/stack-graphs · S17 https://github.blog/open-source/introducing-stack-graphs/ · S18 https://github.com/tree-sitter/tree-sitter-graph · S19 https://docs.ctags.io/en/latest/man/ctags.1.html · S20 https://github.com/universal-ctags/ctags · S21 https://docs.joern.io/ · S22 https://github.com/joernio/joern · S23 https://www.ieee-security.org/TC/SP2014/papers/ModelingandDiscoveringVulnerabilitieswithCodePropertyGraphs.pdf · S24 https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md · S25 https://github.com/github/codeql · S26 https://docs.github.com/en/code-security/codeql-cli/getting-started-with-the-codeql-cli/about-the-codeql-cli · S27 https://github.com/semgrep/semgrep · S28 https://semgrep.dev/legal/rules-license · S29 https://github.com/semgrep/semgrep-rules · S30 https://github.com/opengrep/opengrep · S31 https://github.com/ast-grep/ast-grep · S32 https://github.com/comby-tools/comby · S33 https://docs.openrewrite.org/licensing/openrewrite-licensing · S34 https://github.com/Instagram/LibCST · S35 https://libcst.readthedocs.io/en/latest/metadata.html · S36 https://github.com/Instagram/LibCST/blob/main/LICENSE · S37 https://souffle-lang.github.io/ · S38 https://souffle-lang.github.io/provenance · S39 https://souffle-lang.github.io/install · S40 https://github.com/plast-lab/doop (and its LICENSE) · S41 https://github.com/s-arash/ascent · S42 https://github.com/vmware-archive/differential-datalog · S43 https://github.com/TimelyDataflow/differential-dataflow · S44 https://pylint.readthedocs.io/en/stable/additional_tools/pyreverse/index.html · S45 https://github.com/lucsorel/py2puml · S46 https://github.com/thebjorn/pydeps · S47 https://www.doxygen.nl/manual/index.html · S48 https://www.doxygen.nl/manual/features.html · S49 https://docs.python.org/3/library/ast.html · S50 https://docs.python.org/3/library/symtable.html · S51 https://www.rfc-editor.org/rfc/rfc8785 · S52 https://www.rfc-editor.org/rfc/rfc6901 · S53 https://www.sqlite.org/lang_with.html · S54 https://git-scm.com/book/en/v2/Git-Internals-Git-Objects · S55 https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.condensation.html · S56 https://api.crossref.org/works/10.1145/1265530.1265535 · S57 Soufflé CAV 2016, DOI 10.1007/978-3-319-41540-6_23 (Crossref metadata only) · S58 PyPI JSON, `https://pypi.org/pypi/<package>/json` for tree-sitter-*, libcst, ast-grep-py, semgrep, pylint, pydeps, py2puml, grimp, import-linter, networkx, markdown-it-py, tinycss2 · S59 GitHub REST API `https://api.github.com/repos/<owner>/<repo>` (licence, archived, pushed_at) and `/releases/latest` for each repository named · S60 https://github.com/sourcegraph/scip-typescript · S61 https://github.com/sourcegraph/scip-python (and its LICENSE.txt) · S62 local `ruff analyze graph --help` and run (M5) · S63 https://github.com/safishamsi/graphify · S64 https://github.com/45ck/proofmap-lite (README, `docs/gap-audit.md`, `docs/source-review.md`, `.proofmap/specgraph.project.yaml`) · Other lanes read: `/c/Dev/eija-wt/okf/quality/okf/codelink.py`, `/c/Dev/eija-wt/visual/docs/adr/0023-generated-uml-and-visual-diff.md`, `/c/Dev/eija-wt/quality/docs/adr/0035-static-analysis-and-architecture-fitness-functions.md`, `/c/Dev/eija-wt/tla/docs/adr/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md`.
