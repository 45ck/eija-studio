# Assurance and proof linking: how a model-to-code link carries evidence

Lane: weave. Dossier: assurance-proof-linking. Written 2026-09-29; every URL below was opened on 2026-09-29 (how, in section 9). Labels: **MEASUREMENT** = run here, **PREDICTION** = reasoning, not measured, **DESIGN** = a proposal of this dossier, not a fact about the world. `[S#]` are sources in section 7.

## 0. Decisions (read this first)

1. **A link is a certificate plus a checker, never a status.** The untrusted producer (agent, generator, solver, human) supplies a witness; a small trusted checker recomputes acceptance from the witness and pinned inputs. This is the certifying-algorithm pattern [S2], the proof-carrying-code and verified-validator pattern [S1], and the shape OKF v0.2 already has (executor returns a receipt, a deterministic no-LLM attester returns a verdict) [S25]. It is also what `application/verifier.py` and `domain/evidence.py` already do for runtime receipts: `assess_receipt` ignores the supplied `status`. DESIGN: generalise that function to `assess_link`.
2. **The trusted computing base (TCB) is per claim kind, not global.** The kernel core (canonical JSON, SHA-256, link validator, checker registry, status fold) is the floor; each link kind adds exactly the external checker it names (section 2.2). A PASS states which TCB it stands on.
3. **Pin the statement, not just the proof.** Agents attack the statement (weaken a postcondition to `true`, `assume(false)`, `sorry`) [S23]. The owner-approved statement digest is part of the link; a proof of a different statement is FAIL.
4. **Every proof link carries a deterministic assumption ledger** (axioms, `sorry`, `@unsafe`, `{:axiom}`, solver `hole` steps, `{:extern}` postconditions) diffed against a committed ledger, as `dafny audit --compare-report` does [S17].
5. **Two-check rule for proofs:** producer toolchain, then an independent small kernel (Bend `--verdict` [S10], Lean `leanchecker` [S7]). A missing second checker reports NOT_RUN, never PASS.
6. **Conformance (code versus model) is its own link kind and is always bounded and labelled.** A proof about a model is not a proof about the code [S1, S13].
7. **The assurance case is a derived view with lint rules, not a source of truth.** Adopt the Assurance 2.0 structural rules and defeater semantics as linters [S14]; export GSN YAML to a renderer [S16]; keep probabilities as PREDICTION and never gate on them.

## 1. Scope and method

Central question: how does a model-to-code link carry evidence that a small trusted checker verifies whatever produced it, and what is the smallest TCB?

**Queries.** The WebSearch tool's budget (200 of 200 calls) was already spent when this task started, so no engine search was possible. Discovery instead used direct URLs, the GitHub API (`gh api`, `gh search repos`) for status, licence and file contents, the Crossref API (bibliographic metadata and DOI existence), the arXiv API and downloaded PDFs read with `pdftotext`, plus reads of the sibling worktrees (read-only). Status = default-branch `pushed_at`, `archived` flag and latest release, read 2026-09-29.

**Inaccessible or partial.** ACM DL (403), ScienceDirect (403), dblp (bot wall), Springer PDFs (bot wall; Pnueli-Siegel-Singerman 1998, Tretmans 1996, Necula 1997 only reached as metadata), Elsevier for the Leucker-Schallhart runtime-verification survey, `event-b.org` (self-signed certificate; `wiki.event-b.org` used). GSN standard PDF not opened (landing page only). Papers reached only through Crossref are marked **metadata only**. Fetched pages were treated as data; no fetched code was run.

## 2. The answer: smallest TCB and the shape of a link

### 2.1 Pattern (evidence)

- Certifying algorithm: output y plus witness w; a checker verifies "w proves y correct for x"; "the user can be sure without having to trust the algorithm". The checker must be simple *and* easy to understand; correctness of the checker is the crucial issue. LEDA example: matching module 280 LoC, its checker 26 LoC [S2].
- Leroy: a verified validator (`Validate(S,C)=true` implies semantic preservation) with an untrusted compiler is "as strong as" a verified compiler, provided the validator is smaller and simpler; validators are necessarily incomplete and must answer false when unsure. In PCC "the only part of the infrastructure that needs to be trusted is the client-side checker". CompCert's own residual TCB: the C/assembly semantics, the (then) unverified parser, assembler, linker, and Coq's extraction and OCaml toolchain [S1; the paper is the 2009 version, the current TCB may differ].
- Independent kernels catch kernel bugs: Lean4Lean is an external Lean checker, and its authors report one soundness bug spotted and fixed as a result of the verification work [S6]; `leanchecker` is now built into Lean toolchains from v4.28.0 and replays declarations [S7]. Metamath Zero is a formally specified verifier that aims to be a root of trust [S9]. SAT solver proofs are checked by a verified checker (cake_lpr) [S4]; cvc5 can emit Alethe proofs that Carcara (Apache-2.0) checks [S11].

### 2.2 Claim-relative TCB (DESIGN)

| Link kind | Untrusted producer and witness | Trusted checker for this kind | Residual trust (stated on the PASS) | Label |
|---|---|---|---|---|
| generated | generator; model digest, generator pin, output digest | kernel re-runs the pinned generator, byte-compares | generator is deterministic; what the mapping means | GENERATED |
| model-proof | agent; proof file | independent kernel (`bend --verdict`, `leanchecker`) plus statement digest plus assumption ledger | kernel soundness; Bend's translation to BendTT has no proof [S10]; statement fidelity (human) | PROVED_IN_MODEL |
| model-check | agent-authored spec; cfg | pinned TLC jar re-run (sha256 in `TOOLS.lock`) | TLC, the bounds, the abstraction | CHECKED_BOUNDED |
| solver-unsat | agent; SMT-LIB file, optional Alethe proof | Carcara with cvc5 proof; Z3-only is "solver-trusted" | solver or checker; `hole` steps [S11] | PROVED_MODULO_SOLVER or SOLVER_TRUSTED |
| conformance | agent code; recorded observation table or traces | kernel re-executes the real runtime, compares with the model step through the abstraction (alpha) | sampled cells or traces; abstraction losses; oracle authorship | CONFORMS_BOUNDED |
| contract / property | agent; contracts, tests, seed | pytest / Hypothesis re-run with recorded seed | test adequacy | TESTED |
| human decision | human; sealed decision receipt | existing HMAC seal check | local key holder, not institutional identity | DECIDED |

**Kernel floor** (what every row shares): Python, stdlib `json` and `hashlib`, pydantic (already in the kernel), `assess_link`, the checker registry (id, version, sha256), a subprocess runner that accepts an external tool's answer only on an exact sentinel plus exit code (as `bend_runner.classify` does), and a status fold. PREDICTION: this floor fits in one small module; no size was measured.

**Status set** reuses the kernel's PASS, FAIL, STALE, UNKNOWN, CONFLICT and adds NOT_RUN. STALE follows `assess_receipt`: any of the five subject dimensions (semantic, implementation, policy, environment, harness) differing.

### 2.3 Link certificate fields (DESIGN)

`statement` {kind, digest, approved_by_receipt}; `subject` {code digest, model digest, five dimensions}; `relation` (one of the kinds above); `witness` {path, digest, producer id}; `checker` {id, pin}; `ledger` {digest}; `bounds`; `limitations`. Canonical JSON, SHA-256 identity. No wall clock, no supplied verdict.

### 2.4 Attacks and guards

| Threat | Evidence it happens | Deterministic guard |
|---|---|---|
| Weakened or swapped statement | LLMs turn postconditions into `ensures true`, use `assume(false)`/`sorry`, comment-block tricks were anticipated; in a manual sample of successful outputs about 9% of specs were too weak and 15% poorly translated [S23] | `statement.digest` equals the owner-approved digest over raw bytes |
| Proof escape hatches | Lean `sorryAx` "can be used to prove anything" [S8]; Dafny `{:axiom}`, `{:verify false}`, `{:extern}` with ensures [S17]; Bend `@unsafe`, `?TODO`, foreign code [S10]; cvc5 `hole` steps [S11] | extract the ledger, diff against committed; unlisted item is FAIL, listed item makes the PASS say "with assumptions" |
| Elaborator versus kernel gap | Bend `--verdict` re-checks with a Lean-proved kernel; the `.bendtt` translation "has no proof, so read it to confirm a law" [S10] | second check plus record the `.bendtt` digest; NOT_RUN if absent |
| Vacuous or too-weak model | vericoding: trivial solutions on weak specs [S23]; bend lane already runs negative controls | every model link needs a negative control (a seeded-unsafe model must FAIL) and a reachability witness |
| Trace accepted on incomplete data | TLA+ trace validation "might incorrectly accept a trace if the trace provides incomplete information" [S13] | trace must cover all abstracted variables or the link is marked partial |
| Self-reported green | in-toto `test-result` carries producer-reported `result` [S24] | never read it as authority; recompute |
| Staleness | ProofMap: freshness gates proved visibility, not correctness; mtime compares [S27] | content digests only |

## 3. Per tool and school

**Assurance cases.** *GSN*: community standard maintained by SCSC's GSN_SWG, page content CC BY 4.0; current version not stated on the page I opened [S15]. *SACM* (OMG): version 2.4 beta listed Sept 2026, formal 2.3 Oct 2023, IPR mode "Non-Assert" [S15]. *CAE* and *Assurance 2.0* (Bloomfield and Rushby): steps should be deductive ("as deductive as possible and inductive only as strictly necessary"), five CAE blocks (evidence incorporation, calculation, decomposition, substitution, concretion), explicit defeaters; a case has structural rules ("claims cannot link directly to claims", non-circular) that "are easily checked" [S14]. Confidence: soundness is a yes/no logical valuation; probabilistic valuation is applied only to sound cases; evidence incorporation "documents a human assessment" [S14]. Gives EIJA: the linter rules and the honest split of a leaf into machine-checked link plus human-signed fidelity. Cost: a claim-graph schema. Tools: Clarissa/asce is the authors' prototype; I found no open release. `gsn2x` (MIT, Rust, pushed 2026-08-23) renders GSN YAML to SVG and has `--check`, `--evidence` and `--dump-yaml` [S16]. Verdict: adapt the rules; export to gsn2x; SACM export deferred.

**PCC, certifying algorithms, translation validation, verified compilers.** Sections 2.1 and 2.2. CompCert (INRIA non-commercial licence; commercial use needs AbsInt terms) is not usable as a dependency of an Apache-2.0 project [S1L]. CakeML (BSD-3-Clause, pushed 2026-09-28) shows verified compilation and a verified checker [S4]. Alive2 (MIT) is bounded translation validation for LLVM: loops unrolled to a bound "means there are circumstances in which it misses bugs", designed to avoid false alarms, 47 bugs found, 28 fixed [S3]. Lesson for EIJA: bounded validators are useful if the bound is printed on the verdict. Verified model transformations: survey by Rahim and Whittle, metadata only [S30]; the practical route here is regenerate-and-compare (translation validation with the generator as the untrusted party).

**Small kernels and independent checkers.** Lean 4 (Apache-2.0, v4.34.1 on 2026-09-24): `#print axioms` lists transitive axioms [S8]; `leanchecker` [S7] (the standalone `lean4checker` repository is archived and deprecated in its favour). Lean4Lean (Apache-2.0) is an external checker in Lean [S6]. Bend (Apache-2.0, v2.0.32 on 2026-09-27): see section 4. Metamath Zero (CC0) is inspiration [S9]; `metamath-exe` is GPL-2.0, so not a dependency. Verdict: Lean is an optional process only if a lane needs it; the pattern is adopted regardless.

**Refinement.** Abadi and Lamport: a refinement mapping reduces "arbitrary behaviors" to single-transition obligations; a completeness theorem holds under three hypotheses (implementation spec machine closed; specification with finite invisible nondeterminism; internally continuous), after adding history and prophecy variables, and covers safety, not liveness [S12]. That is exactly the tla lane's alpha/gamma abstraction plus per-step comparison. Event-B/Rodin: refinement between abstraction levels with proof to verify consistency [S28]; Rodin is Eclipse/Java, dual CPL 1.0 and EPL (SourceForge), 3.10 announced on the wiki; ProB (EPL 1.0, 1.16.1 dated 2026-08-27) animates and model-checks B, Event-B, TLA+ and others [S28]. Cost is a second formalism. Verdict: inspiration (Rodin), optional cross-check process (ProB); adapt the refinement-mapping check.

**Design by contract and verifiers.** Dafny (MIT text read; verifier powered by Boogie and Z3; targets include Python; last stable release v4.11.0 on 2025-08-25, commits continue to 2026-09-20): `dafny audit` reports `{:axiom}`, `{:verify false}` and `{:extern}` contracts, has `--compare-report`, and is marked "under development" [S17]. icontract (MIT, v2.7.3 on 2026-01-29) and deal (MIT, 4.24.6 on 2025-11-30) give runtime contracts in Python [S19]. CrossHair (MIT with Apache and PSF parts, active): symbolic execution with an SMT solver; "the absence of a counterexample does not guarantee that the property holds"; cannot analyse nondeterminism [S18]. Nagini (MPL-2.0, v1.3.1 on 2026-07-06) verifies statically typed Python via Viper; its README lists Python 3.12 to 3.14 and Java 11+, while EIJA targets 3.11+ [S29]. OpenJML is GPL-2.0 (Java) and out. Verdict: contracts are a TESTED-level link; Dafny and Nagini are optional processes for a few pure kernel functions; none is a dependency of the kernel.

**Runtime verification and trace validation.** TLA+ trace validation reduces "does this execution match the spec" to constrained model checking with TLC; traces record only updates to spec variables; discrepancies were found in every case study [S13]. CCF applied it in CI ("checks that every observed implementation trace matches a behavior of the high-level specification") [S13]. Gives EIJA: the conformance link. Limits: bound, instrumentation, incomplete traces. The tla lane already implements this; weave defines the certificate around it.

**Conformance testing and MBT.** ioco (Tretmans) is "the de-facto standard compliance relation" for labelled transition systems with inputs and outputs, with quiescence treated as an output; iocos is a related relation with better worst-case complexity that supports stepwise refinement [S22]. GraphWalker (MIT, Java, pushed 2026-05-24) and TorXakis (BSD-3) are MBT tools; AltWalker is GPL-3.0. Hypothesis (MPL-2.0, 6.168.3 on 2026-09-28) `RuleBasedStateMachine` generates action sequences with invariants after every step and prints a short reproducing program [S20]. Verdict: EIJA's kernel is a deterministic state machine, so conformance reduces to output equality through an abstraction (already done); use Hypothesis stateful; ioco stays theory until asynchronous or nondeterministic adapters (the outbox) matter.

**LLM-produced verified code.** Clover: consistency checks among code, docstring and annotation, up to 87% acceptance of correct instances and no false positives on its adversarial set, on a small hand-made Dafny dataset [S23]. Vericoding benchmark: 27% Lean, 44% Verus, 82% Dafny with off-the-shelf models [S23]. Both support "AI proposes, checker decides" and both show the weak-specification failure.

**Attestation formats and OKF.** in-toto Statement v1: `subject` with mandatory digest, `predicateType`, `predicate`; subjects are matched by digest only; Apache-2.0 notice [S24]. OKF v0.2 (Apache-2.0 repo): concept files with `sources`, `generated`, `verified`, `stale_after`; Attested Computation (section 10): agent may supply only declared parameter values, executor returns a receipt, the attester (deterministic, no LLM) compares the compiled artifact [S25]. Two mismatches with EIJA: OKF timestamps (`at`, `stale_after`) are wall-clock, and the spec has no hash field (grep for hash, sha, digest found nothing); `verified: human:` is advisory, not authenticated [S25].

**ProofMap Lite lessons (owner repo).** Sidecar, "not a blind deterministic installer"; freshness gates prove visibility, not semantics; a docs-only edit must not clear a code-change warning (executable evidence required); warnings closed with prose only were rejected in favour of Change Bundles; sha256 evidence snapshots replaced mtime; timestamps caused churn; OpenFastTrace (GPL-3.0) runs as a separate JVM tool [S27, S32].

## 4. How Bend LAWS/PROOF links laws to code

- **Mechanism.** `LAWS.bend` imports the code and states each law as an open claim; `PROOF.bend` imports `LAWS.bend` and proves `law sorted` with `def Laws.sorted`; the gate is `bend PROOF.bend`, and Bend refuses a `PROOF.bend` beside a `LAWS.bend` without importing it [S10]. So the link is a name convention plus imports, checked by type-checking.
- **Second check.** `--verdict` re-checks every def with BendTT, "a small kernel that has a proof in Lean"; `bendtt.lean` is 180085 bytes and contains no `sorry` or `axiom` token (MEASUREMENT, grep; I did not compile it) [S10]. Its header says the kernel is `Type : Type` and argues no live term inhabits Empty; I did not verify that argument.
- **Trust statements from Bend itself:** "The compiler (not kernel) is 99% AI-written and not yet fully audited"; "The checker has no proof and may have bugs; `--verdict` uses a proven kernel"; "F32 is axiomatic"; recursion must terminate unless `@unsafe`; a proof counts only with no `@unsafe` and no user foreign code, imports included; no Windows (WSL works) [S10].
- **What the link is not.** The proof is about Bend code, or in EIJA a Bend model generated from the Python workflow; agreement with `application.runtime.execute` is a separate differential test, which the bend lane already labels as evidence, not proof.
- **Gaps EIJA must close.** "The human writes LAWS.bend, the AI does not touch it" is convention; I found no enforcement in what I read. Statement pinning (decision 3) makes it a check. The CLI churns (v2.0.32 renamed `--safe` to `--verdict` two days before this dossier), so pin the version and digest.

## 5. Options table

Licence source: "text" = LICENSE file opened; "SPDX" = GitHub-detected only.

| Name | Licence (source) | Status (2026-09-29) | Verdict | Why | Source |
|---|---|---|---|---|---|
| Bend | Apache-2.0 (text header) | active, v2.0.32 | optional process | second-check kernel; bend lane owns it; young, flags churn | S10 |
| Lean 4 + leanchecker | Apache-2.0 (text) | active, v4.34.1 | optional process | independent kernel replay; heavy toolchain (size not measured) | S7, S8 |
| Lean4Lean | Apache-2.0 (text) | pushed 2026-08-29 | inspiration | independent external checker; authors report a soundness bug found | S6 |
| Metamath Zero | CC0 (SPDX) | active | inspiration | tiny verifier as root of trust | S9 |
| metamath-exe | GPL-2.0 (SPDX) | active | reject | copyleft; not needed | S9 |
| Dafny | MIT (text) | commits to 2026-09-20; stable v4.11.0 2025-08 | optional process | `audit --compare-report` is the ledger model; .NET, Z3 | S17 |
| Z3 | MIT (text) | active | optional process | solver (smt-bmc lane); no certificate | S31 |
| cvc5 | modified BSD (text); optional GPL libs off by default | v1.4.1 2026-09-25 | optional process | Alethe proofs; docs read are for 1.3.0 | S11 |
| Carcara | Apache-2.0 (text) | pushed 2026-09-24 | optional process | checks Alethe proofs; Rust | S11 |
| CakeML / cake_lpr | BSD-3 (text) | active | inspiration | verified checker, untrusted producer | S4 |
| CompCert | INRIA non-commercial or AbsInt terms (text) | active | reject | non-free licence, cannot be a dependency of an Apache-2.0 project; its papers remain the TV reference | S1, S1L |
| Alive2 | MIT (SPDX) | active | inspiration | LLVM-only bounded TV | S3 |
| TLC / TLA+ tools | MIT (text) | v1.7.4 2024-08 | optional process | tla lane; pinned by sha256 | S13 |
| ProB | EPL-1.0 (vendor page) | 1.16.1 2026-08-27 | optional process | second model checker for cross-check; low priority | S28 |
| Rodin / Event-B | CPL-1.0 + EPL (SourceForge) | 3.10 | inspiration | refinement proof; second formalism cost | S28 |
| icontract | MIT (text) | v2.7.3 2026-01 | dependency (optional extra) | runtime contracts, TESTED level | S19 |
| deal | MIT (text) | 4.24.6 2025-11 | inspiration | overlaps icontract | S19 |
| CrossHair | MIT + Apache + PSF (text) | active | optional process | counterexample search; never a proof | S18 |
| Nagini | MPL-2.0 (text) | v1.3.1 2026-07 | optional process (experimental) | Python verifier; Python 3.12-3.14, Java | S29 |
| OpenJML | GPL-2.0 (repo description) | active | reject | Java, copyleft | S30 |
| Hypothesis | MPL-2.0 (text) | 6.168.3 | dependency (test extra) | property lane pins it; file-level copyleft, unmodified use (my reading, not legal advice) | S20 |
| GraphWalker | MIT (text) | pushed 2026-05 | optional process | Java; low priority beside Hypothesis | S21 |
| TorXakis | BSD-3 (text) | pushed 2026-09 | inspiration | ioco-based MBT tool | S21 |
| AltWalker | GPL-3.0 (text) | pushed 2025-10 | reject | GPL | S21 |
| gsn2x | MIT (text) | pushed 2026-08 | export target | GSN YAML to SVG, `--check` | S16 |
| GSN standard | CC BY 4.0 (page) | maintained | export target | notation, attribution required | S15 |
| SACM (OMG) | OMG Non-Assert IPR | 2.4 beta | export target (deferred) | XMI metamodel | S15 |
| Clarissa/asce | none found | unknown | inspiration | no open release found | S14 |
| Isabelle-SACM, OntoGSN, AssureNote, D-Case | none/CC-BY/BSD/EPL (SPDX) | stale or niche | inspiration / reject (AssureNote, D-Case unmaintained since 2015) | not adoptable | S30 |
| in-toto attestation | Apache-2.0 notice (text) | active | export target | Statement shape; never authority | S24 |
| OKF v0.2 | Apache-2.0 (SPDX) | active | export target | okf lane; Attested Computation maps to link kinds | S25 |
| OpenFastTrace | GPL-3.0 (text) | v4.10.0 2026-09-20 | optional process | separate JVM only; never linked | S32 |
| RFC 8785 (JCS) | IETF, Informational | 2020 | dependency (spec) | canonical form for certificates | S26 |

## 6. Mechanisms table

| School | Mechanism | Benefit | Cost | Verdict | Source |
|---|---|---|---|---|---|
| Certifying algorithms | witness plus checker per link kind | producers become untrusted; checker small | one checker per kind; witness must be checkable in near-linear time | adopt | S2 |
| Translation validation | validate each run; sound but incomplete, false when unsure | no need to verify generators | validator can reject correct output | adopt (regenerate-and-compare) | S1 |
| Proof-carrying code | small client-side checker | trust reduces to checker | code-level proofs are costly; here only model-level | adapt | S1 |
| De Bruijn / independent kernels | second, independent check of every proof | catches elaborator and kernel bugs | second toolchain, run time | adopt | S6, S7, S10 |
| Refinement mappings | per-step check function alpha; history/prophecy variables when needed | arbitrary behaviours reduced to single transitions | safety only; three hypotheses; mapping must be written | adapt | S12 |
| Trace validation | replay recorded traces against spec via TLC | ties code to spec in CI | bounded; instrumentation; incomplete traces | adapt (labelled bounded) | S13 |
| Assumption ledger | list of axioms, holes, unsafe, extern; diff vs committed | stops silent trust growth | per-tool extractors | adopt | S17, S8, S10, S11 |
| Vacuity and negative controls | seeded-unsafe model must FAIL; reachability witness | catches vacuous proofs | extra fixtures per link kind | adapt | S23; bend lane; vacuity papers metadata only [S30] |
| Assurance 2.0 soundness | leaves are premises; interior steps deductive; unresolved defeater blocks | boolean, deterministic case status | authoring discipline | adopt (as lint) | S14 |
| Probabilistic valuation, confirmation measure | subjective probabilities aggregated over sound cases | prioritisation | subjective inputs | theory-only; PREDICTION label | S14 |
| Order theory | claim status as monotone fold over an acyclic case | deterministic status; the kernel's status set already folds | none on a DAG; fixed point needed only for impact (existing `impact.py`) | adopt (topological fold) | local code |
| Merkle / content addressing | statement, witness, ledger, subject digests in one certificate | STALE by construction; no mtime | canonicalisation care | adopt | S26 |
| ioco / MBT | quiescence, conformance relation | needed for nondeterministic systems | theory heavy | theory-only for now | S22 |

## 7. Implications for EIJA (DESIGN)

1. **Add a link-certificate schema and `assess_link` in `graph/`** (`graph/schema/link-certificate.schema.json`), mirroring `assess_receipt`: same five subject dimensions, same statuses plus NOT_RUN, never trusts `status`. Kernel changes stay a separate ADR (0089 proposed: link certificates and claim-relative TCB).
2. **A checker registry** (`graph/schema/checkers.json`): id, pinned version, sha256, licence, kind, sentinel. Modelled on the tla lane's `TOOLS.lock` (jar sha256, release, licence).
3. **Statement pinning** (ADR-0090 proposed): the owner-approved digest lives in protected policy; agents add witnesses only. For Bend hash each `law` block; for TLA+ hash the property definitions and cfg.
4. **Assumption ledger extractors** per tool (Bend, Lean, Dafny, Alethe, TLA+ `ASSUME`), diff vs committed report, exit code as in `dafny audit --compare-report`.
5. **Witness adapters, not duplicated engines.** Each lane (bend, tla, smt-bmc, property, mutation) emits `{kind, subject digests, artefact, tool pin, raw observations}`; weave supplies the schema and the fold. The bend runner's `ALL PROOFS CHECK` plus exit 0 rule and its negative controls are the model; the smt-bmc lane should try cvc5 Alethe plus Carcara (for the theories the cvc5 docs list: equality with uninterpreted functions, linear arithmetic, bit-vectors, parts of strings) before calling any unsat "proved", and reject proofs containing `hole` steps or list them in the ledger.
6. **Conformance links re-execute** the real runtime and compare through alpha; they print bounds and abstraction losses, and are never worded as proof.
7. **Claim graph with lint rules** (ADR-0091 proposed): no claim-to-claim edge, acyclic, every leaf is a link certificate or a human decision receipt, defeaters recorded, an unresolved defeater blocks its parent. Export GSN YAML for `gsn2x`; project each claim to an OKF concept.
8. **OKF adapter:** map Attested Computation onto link kinds (`executor.receipt` = witness, `attester` = registry checker id), add namespaced hash fields, and ignore `at` and `stale_after` when computing verdicts (freshness comes from digests).
9. **Canonical form for certificates.** MEASUREMENT (Python 3.12.10): the kernel's `canonical()` (sorted keys, `ensure_ascii=False`) orders keys by code point, so U+FFFF sorts before U+10000, while RFC 8785 sorts by UTF-16 code units; it also prints `1.0` where JCS prints `1`. Certificates therefore use a restricted subset (no floats, integers within IEEE 754 safe range) with a JCS implementation tested against the RFC vectors, and a test proving equality with `canonical()` on that subset.
10. **Human dashboards show, per link:** kind, TCB line, bounds, ledger, negative-control status. UNKNOWN and NOT_RUN stay visible.

## 8. Gaps and unverified

- Original texts not opened: Necula (PCC), Pnueli-Siegel-Singerman, Tretmans (ioco), Leucker-Schallhart, Rahim-Whittle, Kupferman-Vardi and Beer et al. (vacuity). Claims about them rest on Leroy's account or on metadata. UNVERIFIED beyond that.
- GSN current version unknown; SACM 2.4 beta detail from the OMG page only, PDF unread.
- BendTT: consistency argument and the Lean file not checked by me; `BendTT.pdf` unread. Windows support of Bend not tested.
- `dafny audit` is "under development"; `gsn2x --extended-check` contents unspecified in its docs.
- cvc5 Alethe docs read are for 1.3.0, current release is 1.4.1.
- CompCert's current TCB may differ from the 2009 paper.
- Not surveyed: Frama-C, Why3, Atelier B, Isabelle, Rocq, JTorX, Verus, Kani.
- No experiments beyond two greps and one canonicalisation check. All costs are qualitative except the LEDA line counts [S2]. PREDICTION: the kernel floor is small; unmeasured.

## 9. Sources (opened 2026-09-29)

| ID | URL | How |
|---|---|---|
| S1 | https://xavierleroy.org/publi/compcert-CACM.pdf | PDF, pdftotext |
| S1L | https://github.com/AbsInt/CompCert/blob/master/LICENSE | API, text |
| S2 | https://www.mpi-inf.mpg.de/~mehlhorn/ftp/CertifyingAlgorithms.pdf | PDF |
| S3 | https://web.ist.utl.pt/nuno.lopes/pubs/alive2-pldi21.pdf | PDF |
| S4 | https://cakeml.org/tacas21.pdf ; https://github.com/cakeml/cakeml | PDF; API |
| S6 | https://arxiv.org/abs/2403.14064 | PDF |
| S7 | https://github.com/leanprover/lean4checker | README |
| S8 | https://lean-lang.org/doc/reference/latest/Axioms/ | page |
| S9 | https://arxiv.org/abs/1910.10703 ; https://github.com/digama0/mm0 | PDF; API |
| S10 | https://github.com/bendlang/bend (README.md, guide/GUIDE.md, CHANGELOG.md, WONTFIX.txt, bend2/bendtt.lean) | API contents |
| S11 | https://github.com/ufmg-smite/carcara ; https://cvc5.github.io/docs/cvc5-1.3.0/proofs/output_alethe.html ; https://github.com/cvc5/cvc5 | README; page; API |
| S12 | https://lamport.azurewebsites.net/pubs/abadi-existence.pdf (DEC SRC report, 1988; TCS 1991, doi 10.1016/0304-3975(91)90224-P) | PDF; Crossref |
| S13 | https://arxiv.org/abs/2404.16075 ; https://arxiv.org/abs/2406.17455 ; https://github.com/tlaplus/tlaplus | PDF; API |
| S14 | https://arxiv.org/abs/2004.10474 ; https://arxiv.org/abs/2205.04522 | PDF |
| S15 | https://scsc.uk/gsn ; https://www.omg.org/spec/SACM/ ; https://claimsargumentsevidence.org/ | pages |
| S16 | https://github.com/jonasthewolf/gsn2x ; https://jonasthewolf.github.io/gsn2x/ | README; docs |
| S17 | https://dafny.org/latest/DafnyRef/DafnyRef ; https://github.com/dafny-lang/dafny | HTML, grep; API |
| S18 | https://github.com/pschanely/CrossHair ; https://crosshair.readthedocs.io/en/latest/limitations.html | README; page |
| S19 | https://github.com/Parquery/icontract ; https://github.com/life4/deal | API |
| S20 | https://hypothesis.readthedocs.io/en/latest/stateful.html ; https://github.com/HypothesisWorks/hypothesis | page; API |
| S21 | https://github.com/GraphWalker/graphwalker-project ; https://github.com/TorXakis/TorXakis ; https://github.com/altwalker/altwalker | API |
| S22 | https://arxiv.org/abs/2402.00973 | PDF |
| S23 | https://arxiv.org/abs/2509.22908 ; https://arxiv.org/abs/2310.17807 | PDF |
| S24 | https://github.com/in-toto/attestation (spec/v1/statement.md, spec/predicates/test-result.md) | API |
| S25 | https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md | API |
| S26 | https://www.rfc-editor.org/rfc/rfc8785 | page |
| S27 | https://github.com/45ck/proofmap-lite (README.md, docs/gap-audit.md) | API |
| S28 | https://prob.hhu.de/w/index.php/Main_Page ; https://wiki.event-b.org/index.php/Main_Page ; https://sourceforge.net/projects/rodin-b-sharp/ | pages |
| S29 | https://github.com/marcoeilers/nagini | README |
| S30 | Crossref API metadata (DOI existence only): 10.1145/263699.263712, 10.1007/BFb0054170, 10.1007/3-540-61042-1_42, 10.1007/978-3-540-78917-8_1, 10.1016/j.jlap.2008.08.004, 10.1007/s10270-013-0358-0, 10.1007/s100090100062, 10.1007/3-540-63166-6_28; GitHub API for OpenJML, AssureNote, D-Case, Isabelle-SACM, OntoGSN | API |
| S31 | https://github.com/Z3Prover/z3 | API, LICENSE text |
| S32 | https://github.com/itsallcode/openfasttrace | API, LICENSE text |
| local | `src/eija_studio/domain/impact.py`, `domain/models.py`, `domain/evidence.py`, `application/verifier.py`, `docs/SECURITY_AND_TRUST.md`; read-only `eija-wt/bend/verification/bend/*`, `eija-wt/tla/verification/tla/*` | files |
