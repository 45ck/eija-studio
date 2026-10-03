# Traceability and requirements graphs: what keeps links true

Lane: weave. Dossier: traceability. Access date for every URL: 2026-09-29. Status: research input for ADR block 0089-0112, not a decision.

## Decisions first

| # | Decision | Confidence | Evidence |
|---|---|---|---|
| 1 | Anchor every machine-checked link to a **method-versioned digest of the target slice** (the okf lane's `repo://path#fragment` plus a hash method). Do not use timestamps, hand-bumped revision numbers or line numbers as the primary anchor. | High | Sections 3 and 4 |
| 2 | Pick the hash **granularity by measurement**. A whole-file digest is stale on essentially every commit that touches the file; a Python symbol AST digest was stale on about 7-9% of changes and a signature digest on about 1.5-1.8% (2 repositories, section 4). | Medium (2 Python repos, sensitivity only) | MEASUREMENT, section 4 |
| 3 | A changed digest means "the target changed since baseline", never "the link is now false". Report it as `SUSPECT`. Only a **human** clears it, by recording a new baseline digest and a reason. Agents may propose, never clear. | High | Doorstop, OpenFastTrace, doctrine |
| 4 | Reuse the OpenFastTrace defect vocabulary (covered, outdated, predated, ambiguous, orphaned, unwanted) and its direct-versus-transitive split for link states. Do not invent a new one. | High | Section 3.2 |
| 5 | Links recovered by IR or LLMs are **proposals**, never coverage. The best F1 in the 2025 LLM study is about 0.8, and human vetting is analyst-dependent. | High | Section 5 |
| 6 | Do not adopt a requirements manager as the source of truth. EIJA's typed graph is. Use tools only as export targets or separate processes (OpenFastTrace, StrictDoc/ReqIF). | High | ADR-0016, section 3 |
| 7 | No study measures semantic trace-link decay between requirements and code. URL-rot studies exist and are a different failure. Our two measurements are the only internal-link numbers here, and they are limited. | High that the gap exists | Sections 4 and 8 |

## 1. Scope and method

- **Method.** Primary papers (arXiv abstracts, OpenAlex records), official specs and docs, repository files. Licence, release and activity come from `gh api repos/<r>` and the LICENSE text (where the API said `NOASSERTION` I read the file).
- **Search limitation.** The web-search budget was exhausted (200 of 200) before this dossier started, so every source was opened by direct URL and coverage is limited to what I knew to look for (section 8).
- **Extraction limitation.** Web pages were read through a summarising fetch tool; numbers marked "(fetch summary)" were not cross-checked. Repository files were read directly.
- **Inaccessible.** IBM DOORS suspect-link docs (empty page), ISO 26262 and DO-178C text (paywalled), the ISO/IEC 18670 page and the FAA advisory circular (HTTP 403). ProofMap Lite is private; read with the owner's `gh` login.
- **Measurements run locally.** Hash sensitivity by granularity (section 4); canonical-JSON divergence from RFC 8785 (section 6).

## 2. The failure to design against

Two different things are called "link rot", and only the second one hurts EIJA.

1. **Unavailability.** The target is gone. Studies exist (section 5). A content-addressed link cannot rot this way inside a repository, because the check is "does this content exist here".
2. **Drift.** The target exists and no longer means what the link claims. Hata et al. found that link targets in comments "frequently change" while developers rarely edit the links themselves (fetch summary of the ICSE 2019 abstract). Only a change-detecting anchor catches drift.

How a link is anchored decides what can go wrong:

| Anchor | Detects target change | False stale | False fresh | Who decides "meaningful" | Example |
|---|---|---|---|---|---|
| Line or character position | Only by luck | High | High | Nobody | W3C `TextPositionSelector`, "very brittle" |
| Hand-bumped revision integer | Yes, if the author remembers | None | High (forgotten bump) | The author | OpenFastTrace `req~x~2` |
| Timestamp or TTL | No (age only) | High | High | Clock | OKF `stale_after` |
| Digest of raw bytes | Yes | High (formatting, comments) | Low | Nobody | `git hash-object`, SWHID `cnt` |
| Digest of a **normalised** slice | Yes | Tunable | Low, but nonzero outside the slice | The chosen normaliser | okf lane `ast-v1`, Doorstop stamp of item text |
| Recovered by IR or ML | Probabilistically | Both | Both | A model | T-BERT |

"False fresh" for a normalised digest means a change the normaliser ignores (a comment stating an invariant, a behaviour change in a callee). Hence each hash method carries a version and the method choice is a recorded decision.

## 3. Tools and standards

### 3.1 Summary of options

| Name | Licence | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| OpenFastTrace (OFT) | GPL-3.0 (LICENSE.txt) | Active. 4.10.0 released 2026-09-20; pushed 2026-09-28; Java 17+ | **optional process** | Best-defined coverage-state vocabulary. GPL and Java rule out linking; run as a separate CLI, import its report as evidence, `NOT_RUN` without Java. | [repo](https://github.com/itsallcode/openfasttrace), [states](https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide/use_cases/understanding_and_fixing_broken_requirement_branches.md) |
| Doorstop | LGPL-3.0 (LICENSE.md) | Active. v3.2 2026-07-10; pushed 2026-09-28 | **inspiration**; optional import adapter | YAML item per file in git; fingerprint stored in each link (suspect links). Its digest has a serialisation flaw (3.2). | [repo](https://github.com/doorstop-dev/doorstop), [validation](https://github.com/doorstop-dev/doorstop/blob/develop/docs/cli/validation.md) |
| OKF v0.2 (Google Cloud knowledge-catalog) | Apache-2.0 (GitHub API for the repo; the spec file states no separate licence) | Repo pushed 2026-09-21 | **format adopted by the okf lane** | File-based knowledge with `sources`, `verified`, `stale_after`. Time-based, not hash-based (3.3). | [SPEC](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) |
| StrictDoc | Apache-2.0 | Active. 0.30.1 2026-09-16; pushed 2026-09-25 | **export target**; possible dependency | `@relation` markers in source, machine identifiers (MID), ReqIF import/export. No suspect or stale concept found in its user guide. | [repo](https://github.com/strictdoc-project/strictdoc), [guide](https://github.com/strictdoc-project/strictdoc/blob/main/docs/strictdoc_01_user_guide.sdoc) |
| Sphinx-needs | MIT | Active. 8.5.0 2026-09-03 | **inspiration** | Typed fields validated by JSON Schema; `needs.json` export. Code search for "suspect" in its repo returned 0 hits (index may lag). | [repo](https://github.com/useblocks/sphinx-needs), [schema docs](https://github.com/useblocks/sphinx-needs/blob/master/packages/sphinx-needs/docs/schema/index.rst) |
| TRLC (BMW) | GPL-3.0 | Active. 3.0.1 2026-08-07 | **inspiration** | Typed requirements DSL with a linter and user check rules; pure Python; GPL. | [repo](https://github.com/bmw-software-engineering/trlc) |
| LOBSTER (BMW) | AGPL-3.0 | Active. 1.0.6 2026-07-30 | **reject as dependency** | Traceability evidence report for ISO 26262; AGPL. Its JSON trace schemas are worth reading. | [repo](https://github.com/bmw-software-engineering/lobster), [schemas](https://github.com/bmw-software-engineering/lobster/blob/main/documentation/schemas.md) |
| reqstool | MIT | Active. 0.12.2 2026-08-23; needs Python 3.13+ | **inspiration** | Requirements, verification cases and manual results; CI status check; ships an MCP server and LSP. Python 3.13+ floor is above EIJA's 3.11; overlaps the agents lane. | [repo](https://github.com/reqstool/reqstool-client) |
| Reqflow | GPL-2.0-or-later (COPYING) | Last release v1.6.0 in 2019; repo pushed 2025-11-23 | **reject** | Regex tracing across PDF and Word documents. Wrong artefact model, GPL, low release activity. | [repo](https://github.com/goeb/reqflow) |
| OSLC (Core 3.0, RM 2.1, Config 1.0) | CC BY 4.0 with parts Apache-2.0 (Core) | OASIS Standards: Core 2021-08-26, RM 2021-06-21, Config 2023-07-23 | **inspiration**; possible export target later | Linked-data links over HTTP and RDF. Config Management defines baselines and link resolution in a configuration context. RM does not address suspect links or content hashes. Lyo SDK: EPL-2.0, Java, v6.0.1.Final 2026-08-24. | [Core](https://docs.oasis-open-projects.org/oslc-op/core/v3.0/oslc-core.html), [Config](https://docs.oasis-open-projects.org/oslc-op/config/v1.0/config-resources.html), [RM](https://docs.oasis-open-projects.org/oslc-op/rm/v2.1/os/requirements-management-spec.html), [Lyo](https://github.com/eclipse/lyo) |
| ReqIF 1.2 (OMG) | RF-Limited (spec page) | Current version July 2016 | **export target** (via StrictDoc) | Interchange with DOORS-class tools. Exact terms not read in full. | [OMG](https://www.omg.org/spec/ReqIF/) |
| SWHID v1.2 | Spec: Community Specification License 1.0 (LICENSE.md); reference library `swh-model` GPL-3.0 | Spec release 2025-11-07. Foreword: basis of ISO/IEC 18670 (ISO page unreadable, so status UNVERIFIED) | **adopt as an alias** for file and directory anchors; do not depend on `swh-model` | Intrinsic, registry-free ids from a Merkle DAG (3.4). | [spec](https://github.com/swhid/specification), [paper](https://arxiv.org/abs/2001.08647) |
| W3C Web Annotation selectors | W3C document licence | Recommendation 2017-02-23 | **inspiration** | Layered anchors: exact text with prefix and suffix, position, fragment, plus time state. Model for relocation suggestions. | [W3C](https://www.w3.org/TR/annotation-model/) |
| SCIP (Sourcegraph) | Apache-2.0 | Active. v0.10.0 2026-09-03 | **optional adapter** | Language-agnostic symbol identity for non-Python anchors. Another lane may own it. | [repo](https://github.com/sourcegraph/scip) |
| `rfc8785` (Trail of Bits) | Apache-2.0 | Release 0.1.4 (2024-09); repo pushed 2026-09-28 | **dependency** for the graph package's hashed payloads | Pure-Python JCS. Section 6. | [PyPI](https://pypi.org/project/rfc8785/), [repo](https://github.com/trailofbits/rfc8785.py) |
| IBM DOORS | Proprietary (terms UNVERIFIED) | Docs unreadable | **reject** (as dependency) | The suspect-link idea is documented through Doorstop instead. | n/a |

### 3.2 What each gives EIJA

**OpenFastTrace.** Items are `req~name~revision`. Code carries tags such as `// [impl->dsn~validate-authentication-request~1]`. Gherkin `Scenario` blocks import with `Covers` and `Needs` comments. Coverage states are: Covers (fine), **Predated** (covers a newer revision), **Outdated** (covers an older revision), **Ambiguous** (same id defined twice), **Unwanted** (covers something that does not need it) and **Orphaned** (covers a non-existent item). The report distinguishes direct from transitive defects. The revision "is intended to obsolete existing coverage links in case the content ... semantically changed", and the docs say adding a period does not need a bump. A human judges "semantic", and a forgotten bump is silent. EIJA's digest removes the silence; OFT's vocabulary is the right output language. Cost of running it: a JVM and a GPL process boundary. ProofMap Lite's GAP-008 records `oft` missing from PATH and a broken Java shim on Windows, fixed with a repo-local jar and Java discovery.

**Doorstop.** Each link stores the parent's fingerprint. When the parent changes, validation warns "suspect link". `doorstop clear` records the new fingerprint. Its `Stamp.digest` is `sha256` over `str(value)` for uid, text, ref (and links) with **no separator**. I reproduced the algorithm and confirmed `("REQ001","ab","c")` and `("REQ001","a","bc")` give the same digest. Low practical risk, but a clear example of why hashed payloads need canonical, length-safe serialisation. Doorstop's model (link plus parent digest plus explicit clear) is what EIJA should copy, with a method-versioned normalised digest and a ledgered clear.

**StrictDoc, Sphinx-needs, TRLC, reqstool.** All keep requirements as text in git and check structure; none has a content-digest link with a normaliser over code. StrictDoc's `@relation(REQ-1, scope=function)` markers in docstrings are the closest code-to-requirement tag. reqstool's split of automated verification cases from manual verification results is useful vocabulary for evidence kinds.

**OSLC.** Its useful idea is the configuration context: a link is only meaningful in a baseline, which is what "digest at baseline" means for EIJA. An OSLC server is out of scope (ADR-0016).

### 3.3 The OKF v0.2 fields are not hash anchors

OKF v0.2 defines `sources[].resource` (a URI or scope descriptor), `verified` (a list of `{by, at}` events; tier derived: none = unverified, non-human only = machine-confirmed, a `human:` actor = human-reviewed) and `stale_after` ("A concept is stale when `now >= stale_after`"). A text search of the whole spec found no digest, hash or content-revision field, and `verified` is "independent of `generated.at`: content can change without re-confirmation". So plain OKF staleness is **time-based and attestation-based**; the okf lane's `repo://` URI plus hash method fills the hole. Consequences: (a) OKF staleness reads the wall clock, so an EIJA verdict must take `now` as an explicit recorded input and digest staleness must not read it; (b) OKF's `attester` (a deterministic check, no LLM) is the natural place to hang the graph check.

### 3.4 Software Heritage identifiers (SWHID)

A core identifier is `swh:1:<type>:<hex>` with types `cnt`, `dir`, `rev`, `rel`, `snp`. For `cnt` it is SHA-1 of `"blob" SP length NUL bytes`, no file name. I computed it for `LICENSE` here and it equals `git hash-object` (MEASUREMENT: `d645695673349e3947e8e5ae42332d0ac3164cd7` both ways). Directory ids sort entries by byte order and hash child ids, so a change bubbles to the root (a Merkle DAG). Qualifiers add `lines=`/`bytes=` fragments and `origin`, `visit`, `path`, `anchor` context. Limits: SHA-1 (a collision was demonstrated, [Stevens et al. 2017](https://doi.org/10.1007/978-3-319-63688-7_19)) and raw bytes or ranges only, so it cannot say "this function, ignoring formatting". Use: an optional **alias** on file-level anchors, so a bundle can name a source snapshot externally. The spec says attribution "is not required for implementations"; a `cnt` alias is about ten lines of Python, so do not depend on the GPL library.

## 4. What keeps links true: measurement on real history

**Question.** If a link stores a digest of its target, how often does the digest stop matching, by what is hashed?

**Method.** `graph/bench/traceability_staleness.py` replays first-parent git history. For every Python function or method and every commit touching its file, it compares five digests (raw file bytes with CRLF folded, whole-file AST, symbol AST with and without docstring, symbol signature), and asks whether a digest baselined at a commit still matches H commits later. Deterministic, no clock; Python 3.12.10, Windows. Raw results: `graph/bench/results/traceability-staleness-*.json`.

| Repo (licence) | Window | Files | Symbol baselines at H=100 |
|---|---|---|---|
| Doorstop `789792eb` (LGPL-3.0) | 600 first-parent commits, 2013-07-16 to 2026-09-28 | 81 | 15,756 |
| StrictDoc `abf7be7d` (Apache-2.0) | 600 first-parent commits, 2025-07-27 to 2026-09-21 | 186 | 13,015 |

**Per change** (share of file-touching commits after which a link to a symbol in that file would flag stale):

| Digest | Doorstop | StrictDoc |
|---|---|---|
| Raw file bytes | 99.9% | 100% |
| Whole-file AST | 88.7% | 98.3% |
| Symbol AST with docstring | 9.4% | 7.4% |
| Symbol AST without docstring | 8.1% | 7.2% |
| Symbol signature only | 1.5% | 1.8% |

**Survival** (share of links whose digest no longer matches after H commits, among links whose symbol still exists; the last row is links whose symbol is gone):

| H (commits) | Doorstop: file / symbol AST / signature | StrictDoc: file / symbol AST / signature |
|---|---|---|
| 10 | 80.4% / 14.6% / 3.0% | 39.1% / 3.5% / 0.8% |
| 50 | 94.5% / 36.4% / 9.8% | 75.2% / 8.7% / 2.2% |
| 100 | 100% / 62.2% / 23.1% | 84.8% / 13.9% / 3.8% |
| 300 | 100% / 89.6% / 40.2% | 94.2% / 24.0% / 8.2% |
| symbol missing at 100 | 20.6% | 3.3% |

**Reading.**
- A file-level digest carries almost no information: after 100 commits nearly every link is stale. Symbol-level normalisation makes staleness usable.
- Formatting or comment-only file edits (bytes changed, whole-file AST identical) were 164 of 1,177 file versions in Doorstop (13.9%) and 11 of 956 in StrictDoc (1.2%): noise depends on formatter discipline.
- Signature-only digests are about 3 to 6 times quieter than symbol AST digests. Whether a body change should stale a *requirement* link is a **semantic question no hash answers**; it is a per-link-kind policy.
- Renames and moves break anchors whatever is hashed (20.6% missing at H=100 in Doorstop, 3.3% in StrictDoc). Digests make these loud `ORPHANED` states, which is correct, but relocation suggestions are needed to keep clearing manageable.

**Limits.** Two Python repositories. Sensitivity only: a mismatch is not a false link, and there is no ground truth for "the requirement is still satisfied". Horizons are in commits; Doorstop's 600 commits span 13 years, so its horizons are not comparable in time. Baselines are sampled at commits touching the file; only paths present at HEAD are followed; only functions and one level of methods are anchors. Treat the numbers as an order-of-magnitude argument for section 7, bullet 2, not a constant.

## 5. Link rot and link recovery in the literature

| Study | What was measured | Result | Source |
|---|---|---|---|
| Klein et al., PLOS ONE 2014 | Web references in over 3.5M scholarly articles | "one out of five STM articles suffering from reference rot"; URI rot about 3.5% to 5% for 2012 articles, far higher for 1997 (fetch summary) | [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0115253) |
| Hata et al., ICSE 2019 | About 9.6M links in source-code comments | "Almost 10%" dead; targets change more than links are edited | [arXiv:1901.07440](https://arxiv.org/abs/1901.07440) |
| Xiao et al. 2023 | 18.2M links in commit messages, 23,110 repos | "70% of the distinct links suffer from decay"; "14% of links that are prone to evolve become unavailable" | [arXiv:2305.16591](https://arxiv.org/abs/2305.16591) |
| Rath et al. 2018 | Issue tags in commits, 6 OSS projects | Only about 60% of commits linked to an issue; classifier 96% recall at 33% precision for missing tags, and 89%+ precision at 50% recall when augmenting existing links | [arXiv:1804.02433](https://arxiv.org/abs/1804.02433) |
| Nath et al., CASCON 2025 | Release notes to PRs, commits, issues | 47% of release artefacts lack links, 12% contain broken links; Precision@1 0.73 with Gemini 1.5 Pro | [arXiv:2511.18187](https://arxiv.org/abs/2511.18187) |
| Wohlrab et al., RE Journal 2018 | 24 interviews, 15 industrial projects | Practitioners struggle with cross-tool collaboration, conveying benefit, and **traceability maintenance** | [DOI](https://doi.org/10.1007/s00766-018-0306-1) |
| Rempel and Mäder, TSE 2017 | 24 OSS projects, Poisson regression | Traceability completeness for three of four studied activities significantly affects defect rate | [DOI](https://doi.org/10.1109/TSE.2016.2622264) |

Findings that matter to EIJA:

- **Availability decay is measured; semantic decay is not.** I found no study of how fast requirement-to-code links go semantically stale. Mäder and Gotel ([JSS 2012](https://doi.org/10.1016/j.jss.2011.10.023)) aim "to prevent their decay" by event-driven update of UML trace links; the abstract gives no rate. Hence section 4.
- **Completeness is a bigger practical problem than rot.** About 60% of commits carry issue links (Rath), 47% of release artefacts have none (Nath). A coverage gate that only checks existing links misses the missing ones.
- **Recovery accuracy is not good enough to be authoritative.** T-BERT reports mean-average-precision gains of 60.31% over vector-space baselines ([arXiv:2102.04411](https://arxiv.org/abs/2102.04411)). A 2025 evaluation of Claude 3.5 Sonnet, GPT-4o and o3-mini on documentation-to-code links found best F1 of 79.4% and 80.4% on two datasets, and "fully correct" explanations only 42.9% to 71.1% ([arXiv:2506.16440](https://arxiv.org/abs/2506.16440)). Rath's 33% precision at 96% recall shows the recall-precision trade-off.
- **Vetting helps but is analyst-dependent.** In a 26-participant study, analysts "tend to move their candidate RTM toward the line that represents recall = precision"; those given low-recall, low-precision matrices "drastically improved both" ([Cuddeback et al., RE 2010](https://doi.org/10.1109/RE.2010.35)). A vetted link is a recorded human decision, not a proof.
- Gotel and Finkelstein ([1994](https://doi.org/10.1109/ICRE.1994.292398), over 100 practitioners) found most traceability problems come from inadequate pre-requirements-specification traceability. EIJA's links start after intent capture; the earlier "who wanted what and why" chain stays a human record.

**Safety-critical practice.** Guo et al. state that "in most safety-critical domains the need for traceability is prescribed by certifying bodies" ([ICSE 2017](https://doi.org/10.1109/ICSE.2017.9)). Secondary sources say DO-178C requires documented bidirectional traces between requirements, code, tests and results with rigor varying by software level, and ISO 26262 part 8 calls for "traceability between dependent work products" via configuration management plus confidence in software tools ([Wikipedia DO-178C](https://en.wikipedia.org/wiki/DO-178C), [Wikipedia ISO 26262](https://en.wikipedia.org/wiki/ISO_26262)). The normative texts are paywalled, so **the exact objectives are UNVERIFIED**. For EIJA: bidirectional queries are table stakes, and EIJA claims neither tool qualification nor certification credit; it reports NOT_RUN or UNKNOWN where it cannot compute.

## 6. Mechanisms from mathematics and computer science

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Content addressing, Merkle DAG | Link stores `digest(normalise(target))`; verification is recompute-and-compare; directory-level digests aggregate children | Staleness is a pure function of bytes; no trust in timestamps or authors; a change bubbles to any covering directory | Detects change, not truth; hash choice matters (SHA-1 collides) | **adopt** (SHA-256 internal, optional SWHID alias) | [SWHID spec](https://github.com/swhid/specification/blob/main/Chapters/5.Core_identifiers.md) |
| Canonical forms | Normalise before hashing (AST without positions, LF-folded text); version the method (`ast-v1`) | Measured drop from about 100% to about 7% stale per change (section 4) | Normaliser can hide a change that mattered; AST dumps differ across Python versions | **adopt**, already in the okf lane | section 4 |
| Canonical JSON | RFC 8785 JCS for hashed payloads | Byte-identical across languages and platforms | Rejects NaN and Infinity; needs I-JSON numbers | **adopt for graph payloads** (see below) | [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) |
| Build systems: verifying traces and early cutoff | Record `key -> hash(value)`; if a recomputed intermediate is unchanged, stop propagating | A comment-only edit does not make downstream links suspect; work scales with real change | Needs a dependency graph with stable keys | **adapt**: apply to link status propagation | [Mokhov et al. 2018](https://doi.org/10.1145/3236774), Fig. 3 and section 4.2 |
| Order theory, fixed points | Link status as a small ordered set with a monotone "worst of" join; propagate to a least fixed point (the kernel's `closure()`); a monotone function on a finite lattice reaches its fixed point in at most as many rounds as the lattice height (textbook, not opened this session) | Deterministic aggregation; termination without a depth cap; direct and transitive defects fall out | Design work to fix the status order | **adopt** (design proposal, not a citation) | `src/eija_studio/domain/impact.py` |
| Provenance semirings | Annotate each derived fact ("requirement R is covered") with the links and evidence that support it. Why-provenance is the set of supporting witnesses; the full semiring framework also covers confidence, cost and clearance | "Why is this covered?" and "what breaks if I remove this link?" as queries with exact answers | Full polynomial provenance needs a Datalog-style engine | **adapt**: record witness sets only; full framework theory-only | [Green and Tannen 2017](https://doi.org/10.1145/3034786.3056125) |
| IR and ML metrics | Precision, recall, F2 against a gold set for recovered links; report per project | Honest confidence; recall-weighted for safety use | Needs a labelled gold set (the ledgered human decisions become one) | **adopt** as measurement for proposals | section 5 |
| Structural diff and layered anchors | AST matching (GumTree family) and W3C-style layered selectors (exact text plus prefix and suffix, then position) to *suggest* where a renamed or moved target went | Cuts orphan clearing (3-21% missing at H=100, section 4) | Heuristic and fuzzy; a suggestion is not a link; GumTree licence UNVERIFIED | **adapt**: suggestion only, human accepts | [Falleri and Martínez 2024](https://doi.org/10.1145/3597503.3639148), [W3C](https://www.w3.org/TR/annotation-model/) |
| Category theory, information theory | No implementable benefit for links found in this dossier | none shown | | **theory-only** | n/a |

**Canonical JSON divergence (MEASUREMENT, Python 3.12.10 versus Node 22).** The kernel's `canonical()` in `src/eija_studio/domain/models.py` uses `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)`. That differs from RFC 8785 in three cases: floats (`1e-07` versus `1e-7`, `100.0` versus `100`), key order for astral characters (Python sorts U+FFFF before U+10000; UTF-16 code-unit order, which RFC 8785 requires, puts U+10000 first), and integers beyond 2^53 (outside I-JSON). It matches for ASCII keys, strings, booleans and small integers. So the kernel is JCS-compatible on its current payloads only by convention. Do not change the kernel (needs an ADR and would change every fingerprint). In the graph package, either forbid floats and non-BMP keys in hashed payloads or serialise through `rfc8785` (Apache-2.0).

## 7. Implications for EIJA

1. **Link record.** `{id, kind, from, to: repo://path#fragment, method, digest, baseline_decision}`, where `baseline_decision` is the ledger sequence number and actor that accepted the digest. No wall-clock field in the graph artefact (the receipt holds the timestamp). Any `stale_after`-style expiry takes `now` as an explicit, recorded input.
2. **Method per link kind, chosen by measurement.** Requirement to symbol: signature or symbol AST. Requirement to test: test-function AST. Term to code: public-API digest. Whole-file digests only where the file is the artefact (schema, contract). The benchmark ships so the choice can be re-measured on EIJA's own history (too short today).
3. **Pure status function.** `(link, current digest, ledger) -> {COVERED, SUSPECT, ORPHANED, AMBIGUOUS, UNWANTED, UNRESOLVED}`, OFT's names. `UNRESOLVED` is `NOT_RUN` when a parser or resolver is missing, never `PASS`. Aggregate with a fixed status order and the existing `closure()`, reporting **direct** and **transitive** defects.
4. **Early cutoff.** Propagate suspicion from a link only if its target's *normalised* digest changed. A comment edit stops at the first hop.
5. **Clearing is a ledgered human act.** `ack LINK --reason` stores the new digest and actor. Agents propose (with a diff summary) and never clear: Doorstop's `clear` with an audit trail.
6. **Proposals versus links.** Recovered or LLM-suggested links form a separate `proposed` class, excluded from coverage numerators, with tool, version, model and confidence. Report precision and recall against ledgered human decisions. A mocked recovery is never called live.
7. **Completeness gate.** Report requirements with **zero** links and symbols with zero requirements as well as stale links (Rath: about 60% linked; Nath: 47% missing). A green stale check with low completeness is not assurance.
8. **Interfaces to other lanes.** okf: call its `digest(root, ref, method)` and `repo://` grammar; define a `Protocol` now and a fixture test that both sides agree on. agents: expose `link_status`, `impact`, `explain` as read-only queries; no second MCP server. quality: status diagnostics use the linter output format.
9. **Interchange, last.** Export StrictDoc/ReqIF or OFT markdown only on demand; import an OFT report as `tool-report` evidence. GPL and AGPL tools stay separate processes or reading material.
10. **ProofMap Lite lessons.** Freshness by sha256 snapshot, not mtime (GAP-015, GAP-025). A docs-only edit must not clear a code-change warning (GAP-027). A drift warning closes only through a referenced artefact, not prose (GAP-029). Keep unchanged timestamps to avoid diff churn (GAP-003). Keep inferred and canonical evidence apart.

## 8. Gaps and unverified items

- **UNVERIFIED:** DOORS suspect-link mechanics; DO-178C and ISO 26262 normative objectives (Wikipedia only); ISO/IEC 18670 status; GumTree licence; ReqIF terms beyond the "RF-Limited" label; Lyo capabilities beyond licence and release.
- **Weak absence claims.** "No suspect concept in Sphinx-needs and StrictDoc" rests on a GitHub code search (0 hits for sphinx-needs; none relevant for StrictDoc) and a text search of the StrictDoc guide. Search indexes lag.
- **Not read in full:** Klein et al. (abstract and fetch summary), Green and Tannen (survey abstract, not the 2007 original), Hata and Xiao (abstracts; decay definitions differ, so percentages are not comparable), Cleland-Huang et al. 2014 (fetch failed).
- **Not covered:** newer spec-driven tools (for example OpenSpec, named in the reqstool README), Graphify (ProofMap Lite's inferred code-graph evidence), Eclipse Capra (repo not found under the name I tried), Jama and Polarion, Datalog trace queries (graph lane).
- **Measurement limits:** section 4. Nothing measures how often a *body* change makes a requirement link false; that needs labelled data, which the ledgered `ack` decisions will supply.
- **Open ADR questions:** the status order; whether `UNWANTED` applies (which items require coverage); rename survival (suggestion versus alias table); one shared hash-method registry with the okf lane.
