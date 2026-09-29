# Incremental builds and diagnostics: research dossier

Lane: weave (ADR block 0089-0112). Date: 2026-09-29. Status: input to ADRs, not a decision.
All URLs were opened on 2026-09-29 unless marked UNVERIFIED. PREDICTION means not yet measured in this repo.

## 0. Decisions first

Build a small **diagnostics core** and reuse everything around it.

1. **One `Finding` model, many views.** A finding is pure data: rule id, structured message, `repo://` locations, witness facts, fingerprint, optional fix proposal. SARIF 2.1.0 is the primary export. rdjson (reviewdog), LSP-shaped JSON (agents lane) and text are generated views. None of them is a source of truth.
2. **Incrementality is a cache, never a semantics.** Correctness is the Build Systems a la Carte definition: the stored result equals a clean recomputation. Every incremental run is differential-tested against a clean run.
3. **Content addressing, no clocks.** Cache keys are SHA-256 of LF-normalised bytes plus a rule fingerprint. No mtime, timestamps or GUIDs in artefacts. Hashed JSON follows RFC 8785.
4. **Rules are pure functions with declared inputs**, tested by annotated fixtures, golden SARIF, fix goldens, an idempotence check and a permutation harness (Windows and POSIX).
5. **Fixes are proposals with content-hash preconditions.** The kernel path never applies edits. A human-invoked command or an agent inside its own sandbox applies them, then the checker re-runs.
6. **Adopt:** ruff, import-linter, ast-grep (structural rules), LibCST (Python codemods), reviewdog, `rfc8785`, `jsonschema`. **Build:** the Finding model, the SARIF profile writer, the red-green rule cache (about a page of Python over SQLite), the suppression ledger and the permutation harness.

## 1. Scope and method

Question: what is the best design for an incremental, deterministic, testable, SARIF-emitting rule engine over EIJA's link graph (code, docs, requirements, tests, evidence, ADRs)?

- **Repo read:** `src/eija_studio/domain/impact.py` (monotone least-fixed-point closure, sorted queue, no negation); `domain/models.py` (`canonical()` is `json.dumps(sort_keys=True, ensure_ascii=False)`, `fingerprint()` is SHA-256 of that); `docs/adr/README.md`; `docs/oss/REGISTER.md`; `AGENTS.md`.
- **Other lanes (read-only):** okf `quality/okf/codelink.py` (`repo://path#fragment` URIs, hash methods `ast-v1`, `lf-sha256-v1`, CRLF folded to LF) and `checks.py` (`Finding(check, code, path, message)`, code STALE); quality `docs/quality/gates.md` (ratchet rule, ruff 0.16.9, import-linter 2.15, gates print text, not SARIF).
- **Owner repo:** [45ck/proofmap-lite](https://github.com/45ck/proofmap-lite) README, `docs/gap-audit.md`, `docs/source-review.md`.
- **Tools:** WebFetch (returns a small-model summary, so quotes I did not confirm against raw text are marked); GitHub API via `gh` for status, licence file and tags (`https://api.github.com/repos/<owner>/<repo>`); PyPI JSON; Crossref for bibliographic checks; raw source (ruff, ESLint); `pdftotext` on two papers (DBSP and Build Systems a la Carte), which I read directly.
- **WebSearch:** the session budget (200/200) was exhausted before this task. Four queries (Nixpkgs reproducibility, Bazel hermeticity, Adapton, Nix content-addressed derivations) returned nothing, so discovery used known primary URLs. Coverage of unknown tools is lower than a search-led survey.
- **Inaccessible:** ACM DL (403), the Adapton PDF at a guessed URL (404), the Elm "Compiler Errors for Humans" post (client-rendered, empty), the abstract of Barik et al. (elided by the publisher), a GNU Make manual excerpt (lacked the up-to-date rule).

## 2. Tools and schools

### 2.1 Build systems and incremental computation

| Idea | What it is | Gives EIJA | Cost | Verdict |
|---|---|---|---|---|
| Build Systems a la Carte ([ICFP 2018](https://doi.org/10.1145/3236774), [JFP 2020](https://doi.org/10.1017/S0956796820000088)) | Scheduler plus rebuilder taxonomy. Read directly: Definition 3.1 calls a result correct if inputs are unchanged and every non-input key equals recomputing its task on the result store. Table 1 gives Make's persistent state as file modification times, minimal only if nobody `touch`es a file. | A test oracle for our cache (incremental equals clean) and the vocabulary of early cutoff. | None as a spec. Non-deterministic tasks need a separate model (paper section 6.3); we forbid them. | **Adopt as spec** |
| Salsa ([repo](https://github.com/salsa-rs/salsa), [book](https://salsa-rs.github.io/salsa/)) | Query memoisation: revision counter, each memo records the revisions of its dependencies, durability tiers, backdating (a re-run yielding an equal value is treated as unchanged). The overview says Salsa assumes the query is "a purely deterministic function of its inputs". ty uses it (`salsa 0.28.5` in `astral-sh/ruff` `Cargo.toml`). | Exact model: rule = tracked function, file content = input, rule set and tool versions = high durability. | Rust; no Python binding found. We re-implement the idea; purity is by convention plus the differential test. | **Adapt** |
| Adapton ([PLDI 2014](https://doi.org/10.1145/2594291.2594324), Crossref record only) | Demand-driven incremental computation; abstract not read. | Root of Salsa-style design. | - | Inspiration |
| Bazel ([hermeticity](https://bazel.build/basics/hermeticity)) | "given the same input source code and product configuration, a hermetic build system always returns the same output by isolating the build from changes to the host system". Non-hermetic causes: timestamps and build IDs, absolute paths, writes to the source tree. Suggests finding leaks by building in a container holding only sources and declared tools. | Checklist for our determinism harness. | Would replace nox and the Python toolchain. | Inspiration |
| Buck2 ([why](https://buck2.build/docs/about/why/)) | DICE incremental engine; with remote execution "it is required for a build rule to correctly declare all of its inputs" (README); Starlark is deterministic. | Undeclared inputs are errors, not warnings. | Pre-release, Rust. | Inspiration |
| Pants ([how it works](https://www.pantsbuild.org/stable/docs/introduction/how-does-pants-work)) | Rust engine, typed Python rules, fine-grained invalidation, sandboxed processes, Python dependency inference from imports. | Closest prior art to "Python rules over an invalidation engine". | Replaces nox; large. | Inspiration |
| Nix ([CA derivations](https://nix.dev/manual/nix/latest/store/derivation/outputs/content-address)) | Content-addressed store paths; floating content-addressed derivations still need the experimental `ca-derivations` feature. | Our keys are content-addressed, not input-addressed. | Not a dependency for a Windows-first Python kernel. | Inspiration |
| Make | File modification times (paper Table 1). Ruff's cache key is also mtime plus permissions (`crates/ruff/src/cache.rs`, `FileCacheKey`). | Negative example: mtime is unsound after `touch`, checkout or clock skew. Fine for a formatter, not for evidence. | - | **Reject mtime keys** |
| DBSP ([PVLDB 16(7) 2023](https://doi.org/10.14778/3587136.3587137)) | Incremental view maintenance on streams over a commutative group. Z-sets (rows with integer weights) make sets and bags a group. Incremental version is `D . Q . I`; chain rule; all results checked in Lean (paper's own claim). Theorem 5.4: for a Datalog program, if the input is a set the recursive circuit outputs the Datalog relation; on unbounded domains convergence is not guaranteed. | Z-sets model finding diffs (new = +1, absent = -1). Delta iteration equals semi-naive evaluation. | Feldera compiles SQL to Rust with a JVM front end; too heavy. No Python core. | **Adapt Z-set diff; rest theory-only** |

### 2.2 Sources of nondeterminism and their elimination

| Source | Evidence | Elimination in EIJA artefacts |
|---|---|---|
| Directory order | `os.listdir` "is in arbitrary order" ([docs](https://docs.python.org/3/library/os.html)) | Sort every listing by normalised POSIX path |
| Hash seed | Unset `PYTHONHASHSEED` means random `str` and `bytes` hashes; `0` disables ([docs](https://docs.python.org/3/using/cmdline.html)) | No `set` iteration reaches output; sort before emit; harness runs several seeds |
| Locale, timezone, paths, randomness, archive metadata | [Reproducible Builds docs](https://reproducible-builds.org/docs/) | No `locale`, no time, no absolute paths |
| Wall clock | `SOURCE_DATE_EPOCH` clamps embedded times ([spec](https://reproducible-builds.org/specs/source-date-epoch/)) | Stronger: omit time from artefacts entirely |
| String ordering | Python orders `str` by code point ([tutorial](https://docs.python.org/3/tutorial/datastructures.html)); JCS sorts keys by UTF-16 code units ([RFC 8785](https://www.rfc-editor.org/rfc/rfc8785)) | These differ for keys mixing supplementary characters with U+E000-U+FFFF, and JCS fixes number formatting, so `canonical()` is not JCS for exotic keys or floats (derived from the two sources, not tested). New artefacts use `rfc8785` with string, int and boolean payloads only |
| Column units | LSP defaults to UTF-16 code units, allows utf-8 and utf-32 ([3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#positionEncodingKind)); SARIF has `columnKind` | Store byte offsets; emit an explicit `columnKind`; test with a non-BMP character on the line |
| Line endings | okf already folds CRLF to LF before hashing | One shared helper (section 5, item 7) |
| SARIF | Appendix F "Producing deterministic SARIF log files" (summary only): no absolute paths (use `uriBaseId`), timestamps or GUIDs; sort results and artifacts | Adopt as the SARIF profile |

Reproducibility is hard even for disciplined ecosystems. [Malka, Zacchiroli, Zimmermann (MSR 2025)](https://arxiv.org/abs/2501.15919) report 69-91 percent bitwise reproducibility across 709,816 nixpkgs packages (2017-2023) and about 15 percent of failures from embedded build dates. So we test rather than assume (section 5, item 4). The [definition](https://reproducible-builds.org/docs/definition/) is our acceptance sentence: "given the same source code, build environment and build instructions, any party can recreate bit-by-bit identical copies of all specified artifacts", with the SARIF file and its hash as the artefacts.

### 2.3 Diagnostic formats and infrastructure

| Format | Facts | Gives EIJA | Cost |
|---|---|---|---|
| [SARIF 2.1.0 Errata 01](https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html) (OASIS Standard, 2023-08-28) | `fingerprints` and `partialFingerprints` (3.27.16-17); `baselineState` new, unchanged, updated, absent, renamed (3.27.24); `suppressions` (3.27.23); `fixes` with `artifactChanges`, `deletedRegion`, `insertedContent` (3.27.30, 3.55-3.57); rule metadata (3.49); invocations with `executionSuccessful` and `toolExecutionNotifications` (3.20); `automationDetails`; `originalUriBaseIds` | Carrier for every lane. `executionSuccessful=false` plus a notification is the honest encoding of NOT_RUN. | Verbose; pin a profile for stable bytes. |
| [GitHub code scanning](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) | Dedupe uses only `partialFingerprints.primaryLocationLineHash`. Limits: 10 MB gzipped, 25,000 results per run (top 5,000 shown), 25,000 rules, 20 tags (10 kept). [Upload](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github): Action, CodeQL CLI or REST API; missing fingerprints are computed by the upload action; free on public repos, private repos need Advanced Security. | PR annotations on the public repo. | Actions are unavailable to 45ck repos (memory note), so REST only; token and egress are an owner decision. |
| [LSP 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) `Diagnostic` | `range`, `severity`, `code`, `codeDescription.href`, `source`, `message`, `tags`, `relatedInformation`, `data` (preserved between `publishDiagnostics` and `codeAction`). Pull diagnostics: `resultId`, `interFileDependencies`. `CodeAction.edit`, `isPreferred`. | Shape for the MCP view; `data` carries fix preconditions. | Position-encoding trap. |
| [reviewdog](https://github.com/reviewdog/reviewdog) rdjson ([proto](https://raw.githubusercontent.com/reviewdog/reviewdog/master/proto/rdf/reviewdog.proto)) | `Diagnostic{message, location, severity, source, code{value,url}, suggestions[{range,text}], related_locations}`; reads SARIF (`-f=sarif`); diff filtering with `-filter-mode`. | Local PR-review bridge. | Go binary, optional. |
| Ruff output | Source on `main` has `sarif.rs` (SARIF 2.1.0, rules sorted by severity then id) and `rdjson.rs`. The settings page lists json, junit, github, gitlab, pylint, azure but not sarif, so docs lag source. | Quality lane can ingest ruff SARIF. | Result order and the CLI flag on pinned 0.16.9 unverified. |

### 2.4 Rule authoring and testing frameworks

| Tool | Mechanism to copy | Source |
|---|---|---|
| Semgrep | Inline `ruleid:` / `ok:` (and `todoruleid:`) annotations, `semgrep --test`, `rule.fixed.py` autofix goldens, `--validate` rule lint | [docs](https://docs.semgrep.dev/writing-rules/testing-rules) |
| Clippy | UI tests: `//~^` markers, `.stderr` golden, `.fixed` golden checked with rustfix, `cargo uibless` regenerates | [book](https://doc.rust-lang.org/clippy/development/adding_lints.html) |
| ESLint | `RuleTester` valid and invalid arrays, `output` for fixes, `messageId`. Source: overlapping fixes stay as problems, fixes sorted by range, `MAX_AUTOFIX_PASSES = 10`; suggestions are stand-alone, never multipass | [RuleTester](https://eslint.org/docs/latest/integrate/nodejs-api#ruletester), [custom rules](https://eslint.org/docs/latest/extend/custom-rules), `lib/linter/` |
| Ruff | Safe versus unsafe fixes ([docs](https://docs.astral.sh/ruff/linter/)). Source: fix loop capped at `MAX_ITERATIONS = 100`, then "Failed to converge" | `crates/ruff_linter/src/linter.rs` |
| ast-grep | `valid` / `invalid` arrays; outcomes reported, validated, noisy, missing; snapshots (`--update-all`); `scan --format sarif` | [tests](https://ast-grep.github.io/guide/test-rule.html), [scan](https://ast-grep.github.io/reference/cli/scan.html) |
| import-linter | Contracts forbidden, protected, layers, independence, acyclic siblings; `broken_contract_guidance`; `unmatched_ignore_imports_alerting` (stale ignore is an error by default) | [docs](https://import-linter.readthedocs.io/en/stable/contract_types/) |
| ArchUnit | `FreezingArchRule` records existing violations; later runs report only new ones (ratchet) | [guide](https://www.archunit.org/userguide/html/000_Index.html) |
| dependency-cruiser | `forbidden` / `allowed` / `required` rules with severity and `comment`; `--ignore-known`; reporters incl. json, mermaid, d2, dot; no SARIF reporter in `src/report` | [rules](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md) |
| Deptrac | Layers by collectors, rulesets, baseline (a `YamlBaselineMapper` is in source) | [docs](https://deptrac.github.io/deptrac/) |

### 2.5 Error-message quality

The evidence base is thin. [Becker et al. 2019](https://doi.org/10.1145/3344429.3372508) survey the field: compiler and interpreter messages "present substantial difficulty and could be more effective, particularly for novices". [Barik et al. ICSE 2017](https://doi.org/10.1109/ICSE.2017.59) exists but I could not read its findings. I found no controlled study of message wording for LLM consumers (UNVERIFIED that none exists).

Practice is better documented. The [rustc dev guide](https://rustc-dev-guide.rust-lang.org/diagnostics.html) prescribes a level, an error code with a long `--explain` text, a message understandable alone, primary and secondary labelled spans and sub-diagnostics. Suggestions carry an applicability: `MachineApplicable` ("can be applied mechanically"), `HasPlaceholders`, `MaybeIncorrect`, `Unspecified`. [RFC 1644](https://github.com/rust-lang/rfcs/blob/master/text/1644-default-and-expanded-rustc-errors.md) (2016-06-07) introduced the annotated-span format. Take: stable code, standalone message, labelled spans, explicit applicability, long explanation at a stable URL (`helpUri` in SARIF, `codeDescription.href` in LSP). For agents add structured `properties` (expected, actual, witness ids) so nothing is parsed from prose. Whether this raises agent fix rates is a **PREDICTION**; measure fix-applied-and-finding-gone rate per rule with the metrics lane.

### 2.6 Autofix and codemods

| Tool | Facts | Verdict |
|---|---|---|
| [LibCST](https://github.com/Instagram/LibCST) | MIT, with some PSF-derived files (dual MIT/PSF) and one Apache-2.0 file per its LICENSE. Lossless CST, `CodemodTest.assertCodemod`, `python -m libcst.tool codemod`. Docs state no determinism or idempotence guarantee, so we test them. | **Optional dependency** (`graph` extra) for Python fixes |
| [OpenRewrite](https://github.com/openrewrite/rewrite) | Apache-2.0 core and Java parsers; Python, C# and JS parsers under the Moderne Source Available License; some recipes proprietary (README, tiered licensing). | **Reject as dependency**; inspiration (typed LST, recipes as deterministic tool calls for agents) |
| ast-grep | MIT; rewrites with `fix`, applied by `--update-all` | **Optional process** |
| Byte-range text edits | Own code, tens of lines | For Markdown, YAML, OKF pages, ADR tables |

## 3. Options table

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| Salsa | Apache-2.0 or MIT | active, 0.28.5 (2026-09-24) | inspiration | Right model, Rust only | [repo](https://github.com/salsa-rs/salsa) |
| Bazel | Apache-2.0 | active, 9.2.0 (2026-07-13) | inspiration | Would replace nox | [repo](https://github.com/bazelbuild/bazel) |
| Buck2 | Apache-2.0 or MIT | active, no stable tag | inspiration | Rust, pre-release | [repo](https://github.com/facebook/buck2) |
| Pants | Apache-2.0 | active, 2.33.1 (2026-08-27) | inspiration | Inference idea; too large | [repo](https://github.com/pantsbuild/pants) |
| Nix | LGPL-2.1 | active, tag 2.35.2 | inspiration | CA idea; floating CA experimental | [repo](https://github.com/NixOS/nix) |
| GNU Make | UNVERIFIED | UNVERIFIED | reject (mtime keys) | Unsound key | [paper](https://doi.org/10.1145/3236774) |
| Feldera / DBSP | MIT (open edition); Enterprise files under Feldera terms | active, v0.357.0 (2026-09-27) | inspiration | Z-sets; JVM plus Rust weight | [LICENSE](https://github.com/feldera/feldera/blob/main/LICENSE) |
| differential-dataflow | MIT | active | inspiration | Rust, heavy | [repo](https://github.com/TimelyDataflow/differential-dataflow) |
| Soufflé | UPL-1.0 | active, 2.5 (2025-03-24) | optional process / export target | If Datalog rules are needed; Windows build UNVERIFIED | [repo](https://github.com/souffle-lang/souffle) |
| DDlog | MIT | archived 2023-07-07 | reject | Archived | [repo](https://github.com/vmware/differential-datalog) |
| Glean | BSD (LICENSE header) | active | inspiration | Code-fact store; heavy | [repo](https://github.com/facebookincubator/Glean) |
| CodeQL | queries MIT; CLI limited to OSI-licensed codebases on GitHub.com, research and demos, no redistribution | active | optional process, public repo only | Not a kernel dependency | [CLI licence](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md) |
| SARIF 2.1.0 | OASIS standard; repo under OASIS IPR (RF on RAND) | Errata 01, 2023-08-28 | export target | Implementing a spec is not redistribution; schema reuse terms UNVERIFIED | [spec](https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html) |
| sarif-sdk (.NET) | MIT | active | optional process | Validate and convert; needs .NET | [repo](https://github.com/microsoft/sarif-sdk) |
| sarif-om (Python) | MIT | last release 2019-10-05 | reject | Stale; emit a small profile by hand | [PyPI](https://pypi.org/project/sarif-om/) |
| LSP 3.17 | UNVERIFIED | stable | export target | Agent view | [spec](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) |
| reviewdog | MIT | active, v0.21.2 | export target / optional process | rdjson, diff filter | [repo](https://github.com/reviewdog/reviewdog) |
| GitHub code scanning | service; free on public repos | live | export target (owner decision) | REST upload needs no Actions | [docs](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github) |
| rfc8785 | Apache-2.0 | 0.1.4 (2024-09-27), repo active | dependency | Pure-Python JCS | [repo](https://github.com/trailofbits/rfc8785.py) |
| jsonschema | MIT | 4.26.0 | dependency (tests) | Validate SARIF | [PyPI](https://pypi.org/project/jsonschema/) |
| ruff | MIT | active, 0.16.9 | dependency (existing) | Emits SARIF, rdjson | [repo](https://github.com/astral-sh/ruff) |
| import-linter, grimp | BSD-2-Clause | 2.15, 3.17 | dependency (existing) | Text output; adapter to Finding | [repo](https://github.com/seddonym/import-linter) |
| Semgrep engine | LGPL-2.1 | active, v1.178.0 | optional process | Registry rules are internal-business-use only, no distribution ([licence](https://semgrep.dev/legal/rules-license/)); write own rules | [repo](https://github.com/semgrep/semgrep) |
| ast-grep | MIT | active, 0.45.3 (2026-08-31) | optional process | SARIF out, rule tests, fixes | [repo](https://github.com/ast-grep/ast-grep) |
| LibCST | MIT (plus PSF, Apache-2.0 files) | v1.9.0 (2026-07-29) | dependency (extra) | Lossless Python codemods | [repo](https://github.com/Instagram/LibCST) |
| OpenRewrite | Apache-2.0 core; Moderne SAL for Python parser | active, v8.92.11 | reject | Python parser licence | [repo](https://github.com/openrewrite/rewrite) |
| Clippy, ESLint | Apache-2.0, MIT | active | inspiration | Test conventions | section 2.4 |
| ArchUnit | Apache-2.0 | active, v1.5.1 | inspiration | Freezing rules | [repo](https://github.com/TNG/ArchUnit) |
| dependency-cruiser | MIT | active, v18.4.0 | inspiration | JS only | [repo](https://github.com/sverweij/dependency-cruiser) |
| Deptrac | MIT | active, 4.7.2 (an older fork is archived) | inspiration | PHP only | [repo](https://github.com/deptrac/deptrac) |
| ProofMap Lite | none detected by GitHub | pushed 2026-07-26 | inspiration | No licence file: lessons only, copy no code | [repo](https://github.com/45ck/proofmap-lite) |

## 4. Mechanisms from mathematics and computer science

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Build-system theory | Correctness = stored value equals clean recomputation; early cutoff; minimality | Testable meaning of "incremental is right"; fewer re-runs | Differential test only | **Adopt** | [ICFP 2018](https://doi.org/10.1145/3236774) Def. 3.1 |
| Incremental computation | Memo keyed by input hash; recorded dependencies; backdating; durability tiers | Agent-loop latency; unchanged evidence not recomputed | Python re-implementation; purity by convention. PREDICTION: repo is small, gain may be seconds, so **measure first** in `graph/bench/` | **Adapt** | [Salsa algorithm](https://salsa-rs.github.io/salsa/reference/algorithm.html) |
| Content-addressed Merkle structures | Per-file SHA-256, per-directory combined hash, run hash over sorted findings | Validity independent of mtime, machine and order; one hash goes into the receipt | Hash cost (PREDICTION: milliseconds here); CRLF and encoding normalisation shared with okf | **Adopt** | [Nix CA docs](https://nix.dev/manual/nix/latest/store/derivation/outputs/content-address); okf `codelink.py` |
| Groups of differences (Z-sets) | Findings as a Z-set; run diff = new minus old; classify by weight sign | Deterministic new / absent / unchanged for `baselineState` and baselines | Small; DBSP join incrementality not needed | **Adapt** | [PVLDB 2023](https://doi.org/10.14778/3587136.3587137) |
| Fixed points, Datalog | Semi-naive delta iteration for closure; stratified negation for "no test covers this requirement" | Terminating, sound impact and coverage rules. Negation is non-monotone, so it sits outside the monotone closure in `impact.py` and must be stratified | Two strata; unbounded domains may not converge (paper), so keep domains finite | **Adopt as constraint**; engine theory-only | DBSP Thm 5.4 and text |
| Order theory | Verdict aggregation as a join-semilattice with `NOT_RUN` absorbing `PASS` | Aggregate independent of order, threads, sharding; a missing prerequisite cannot become PASS | Property test: commutative, associative, idempotent | **Adopt** (own design, no external source) | test to be written |
| Provenance | Each finding lists the fact ids and hashes it depends on (why-provenance) | Human sees the witness chain; cache dependencies come free | Larger SARIF (`relatedLocations`, `codeFlows`) | **Adapt** witness sets; semiring algebra theory-only | [Green et al., PODS 2007](https://doi.org/10.1145/1265530.1265535) (bibliographic check only) |
| Term and graph rewriting | Fixes as rewrite rules; confluence and termination decide whether order matters | Deterministic multi-fix application | ESLint caps at 10 passes and ruff at 100 with a "failed to converge" error: termination is not guaranteed in practice. Critical-pair analysis theory-only | **Adapt**: sorted disjoint edits, bounded iteration, `NOT_CONVERGED` | ESLint `source-code-fixer.js`; ruff `linter.rs` |
| Type theory | Closed sum types for verdict, applicability, level; exhaustive matching under mypy strict | `NOT_RUN` is not a `bool`; illegal states unrepresentable | None (mypy strict gates domain already) | **Adopt** | quality lane `gates.md` |
| Bidirectional transformations | Round-trip laws between graph and generated views | Edits to generated views flow back | Heavy; belongs to visual and okf lanes | Theory-only here | - |
| Information theory, probabilistic assurance | Rank findings by evidence gain; rule precision as probability | Prioritisation | Needs labelled data that does not exist yet | Theory-only; precision from fixtures becomes MEASUREMENT once collected | - |

## 5. Implications for EIJA

1. **Engine shape (ADR candidates 0089-0092).** Typed `Fact` relations (sorted tuples) feed `Rule` functions `facts -> findings`. Two kinds: *file-local* (one file's hash in, findings out, cached per file) and *graph-global* (declared relation slices in). Cache key = SHA-256 of `(rule fingerprint, sorted input hashes)`; the rule fingerprint covers rule id, version, source hash, config and pinned tool versions (high durability). Early cutoff on output hash. Store in SQLite (stdlib); scratch in `.tmp/`.
2. **Finding model and SARIF profile (0093-0096).** Fields: `rule_id`, `level`, `message_id` plus `args`, primary and related locations as `repo://` URIs (reuse the okf grammar), `witness` list, `fingerprint` (SHA-256 over rule id, logical location and normalised args, versioned `eija/v1`, excluding line numbers so it survives edits), optional `fix`. The writer emits a pinned SARIF subset: sorted results, rules and artifacts; `uriBaseId`; explicit `columnKind`; no GUIDs, times or absolute paths; also `primaryLocationLineHash` for GitHub. Tests validate against the OASIS schema with `jsonschema`; store the schema's hash and vendor only after the owner clears its terms.
3. **NOT_RUN is first-class.** A missing tool yields `executionSuccessful: false` plus a `toolExecutionNotifications` entry, and the verdict lattice makes the aggregate NOT_RUN. This implements AGENTS.md ("missing prerequisites report NOT_RUN") and stops a skipped gate looking green.
4. **Every rule ships with tests (0097-0100).** (a) Annotated fixtures (`ruleid:` / `ok:` / `todo`); (b) golden SARIF with a bless command; (c) `.fixed` goldens; (d) fix idempotence (apply, re-run, zero findings of that rule; apply twice, identical bytes); (e) the Definition 3.1 differential test after random edit sequences (generated with the property lane's Hypothesis); (f) a permutation harness: shuffled input order, several `PYTHONHASHSEED`, `TZ`, `LC_ALL`, working directories, CRLF versus LF checkouts, thread counts and a non-BMP character, requiring byte-identical SARIF on Windows and POSIX. The mutation lane can score the rule tests. A metadata lint requires code, standalone message template, help text, long explanation and applicability for every fix.
5. **Fix proposals, not application (0101-0102).** A fix is byte-range edits plus `applicability` (Rust vocabulary mapped to ruff safe/unsafe) and a `precondition_sha256` per file; applying to a changed file fails closed. Overlapping edits are reported as a conflict (ESLint pushes them to the next pass). This respects "agents and providers never approve or apply": the MCP tool returns proposals, the agent edits in its own sandbox, the checker re-runs and the kernel decides. Python fixes use LibCST; docs and OKF fixes use range edits.
6. **Suppressions and baselines as evidence (0103-0106).** One ledger keyed by fingerprint, using SARIF `suppressions`, with a required justification and an evidence path that must resolve (ProofMap gaps GAP-017, GAP-018, GAP-029: prose-only acceptance failed). A suppression matching nothing is itself a finding (import-linter default). Baselines may shrink, never grow (ArchUnit freezing, quality-lane ratchet). No expiry dates, since wall clock is banned; expire by ADR or commit reference. ProofMap GAP-003 (timestamps caused artefact churn) is the same lesson as the no-clock rule.
7. **Adapters for other lanes (0107-0108).** okf `Finding(check, code, path, message)` and STALE/DRIFT map to rule ids; the hash-method names and CRLF fold come from one shared helper, not a second copy. Ruff SARIF is ingested as is; import-linter and the complexity ratchet get adapters; tla, smt-bmc and property results become findings with a named evidence kind, and a model-level proof is labelled as such, never as code conformance. Visual-lane diagram nodes are logical locations. The metrics lane consumes per-rule precision and fix-acceptance counts.
8. **Delivery views (0109).** SARIF (canonical), rdjson for reviewdog, LSP-shaped JSON for MCP, text for terminals. GitHub upload only via REST with an owner-supplied token; owner decision.
9. **Dependencies and register (0110).** `graph` extra pinned `==`: `rfc8785`, `jsonschema`, `libcst`. Optional processes outside the extra: ast-grep, reviewdog, sarif-sdk, Semgrep (own rules only). Add `docs/oss/REGISTER.md` rows for each, plus a custom-module row (Finding model, SARIF writer, rule cache, suppression ledger, permutation harness) with the OSS-check table from `docs/adr/template.md`.
10. **Benchmark before optimising (0111).** `graph/bench/` records cold and warm runs and hash costs on this repo with platform, Python and tool versions in the file. Keep the cache off by default until the warm-run gain justifies its bug surface. Any number quoted earlier is a PREDICTION.

## 6. Gaps and unverified items

- UNVERIFIED: licences of GNU Make and the LSP spec text; reuse terms of `sarif-schema-2.1.0.json` (OASIS repo says content is governed by OASIS IPR, RF on RAND; the schema's own header not read).
- UNVERIFIED: whether ruff 0.16.9 exposes SARIF on the CLI (emitter is in source, docs page omits it) and whether its result order is stable; Soufflé on Windows; Semgrep and CodeQL footprint on 16 GB shared RAM.
- UNVERIFIED wording: SARIF Appendix F and section numbers came through the summarising fetch tool, not a raw read. Bazel, Buck2, Pants, Salsa, Semgrep, ESLint and Rust doc statements are also summaries. Facts from the two papers, ruff and ESLint source, LICENSE files and the GitHub API were read raw.
- Not read: Adapton abstract, Barik et al. findings, Elm error-message essay, Green et al. theorems, Feldera internals beyond LICENSE and README. No claim here depends on them.
- No study found comparing message wording for LLM agents; that benefit is a PREDICTION.
- Incremental gain on this repo is unmeasured. DBSP's Lean-checked proofs (paper's claim) concern DBSP circuits, not our Python cache; ours rests on the differential test, which shows agreement on tested edit sequences, not a proof. A proof about a rule model is not a proof about the implementation.
- Out of scope, covered by other dossiers: Neo4j and graph databases, OKF spec details, category theory.
