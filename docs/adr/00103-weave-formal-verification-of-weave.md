# ADR-00103: Formal verification of the weave: a small trusted kernel, certificates, exhaustive small scope, Alloy for bounded statements, and drift guards

* Status: proposed
* Date: 2026-09-29
* Lane: weave (aspect formal-verification-of-weave). Design and evidence: [docs/weave/design/formal-verification-of-weave.md](../weave/design/formal-verification-of-weave.md). Obligation list: [graph/formal/OBLIGATIONS.md](../../graph/formal/OBLIGATIONS.md).

Numbering note for the integrator. The brief gave this record the file name `00103`, as it gave `00101` to the human-views record (five digits, unlike the four-digit records above). `docs/weave/ARCHITECTURE.md` section 11 allocates 0103 to statement pinning and assumption ledgers; the statement-pinning content is a dependency of this record (section "Interfaces"), not part of it. Nothing in the decision depends on the number.

## Context and problem statement

The weave ties code, tests, requirements, UI, diagrams, the ubiquitous language, formal models and evidence into one typed, hash-anchored graph, and a rule set (the compiler and linters) reports on it. Its value is that people and agents can trust a green result. That trust has one dangerous failure: a false PASS. The weave must therefore be verified itself, and the verification must be honest about what a proof of a model says about code (nothing by itself), about what an exhaustive run covers (a stated domain), and about what must be trusted (a kernel, small enough to review).

Three questions need one decision. Which properties of the weave are verified, by which technique, with what scope. Where the trusted-kernel boundary lies and how untrusted producers (extractors, agents, the SQL engine, external tools) are held to it. How a formal model is kept from drifting away from the Python it describes. The kernel already shows the approach in miniature: `assess_receipt` recomputes evidence from raw observations and ignores any supplied status; the formal lanes (tla, bend, smt-bmc) pin their tools by digest and accept an answer only on an exact sentinel plus exit code.

## Decision drivers

* False PASS is the only error that matters for a gate; NOT_RUN absorbs PASS, so missing prerequisites cannot cause it.
* A proof about a model is not a proof about the code; conformance is its own claim, bounded and labelled (AGENTS.md, ADR-0018).
* The determinism doctrine (D-01 to D-24): byte-identical output independent of order, clock, locale, seed and platform.
* Untrusted producers, a small trusted checker, the owner decides; agents and providers never approve or apply.
* ADR-0016: adopt open source first; write only EIJA-specific glue and justify it.
* Cheap enough for a shared 16 GB Windows PC on a slow disk: one heavy process at a time, temp files in `.tmp/`.
* Every claim carries an evidence label; no benefit to agents or humans is claimed until measured.

## Considered options

* **A. Tests only** (the status quo for the kernel). Cheap; a passing test says nothing about the inputs nobody thought of, and no negative control shows that a test can fail.
* **B. Machine-checked proofs of the kernel** in Lean 4, Coq, Isabelle or Bend. The strongest rung. Toolchains are heavy (Lean's and Bend's sizes were not measured here), the proofs cover a model or a translation and not the Python interpreter, and the theorems needed (an induction on rank, a cycle argument) are short enough to review on paper. Deferred behind a trigger.
* **C. SMT first (Z3)** as the smt-bmc lane did for the policy. Right for arithmetic and bit-vectors. The weave's properties are finite tables and graph reachability: the domains are enumerable or relational, Z3 would add a solver to the trusted base without a gain, and reachability needs bounded unrolling or a fixed-point engine (UNVERIFIED, not tried).
* **D. A ladder: schema, exhaustive enumeration, certificate plus small checker, Alloy for bounded relational statements, property tests and differential runs, with a second-source rule and negative controls** (chosen).
* **E. A TLA+ model of the whole weave.** Right for interleavings; the weave's verdict path is a pure function of a git tree, and the one temporal risk (a multi-writer incremental cache) does not exist yet.
* **F. Verify the Python directly** with CrossHair, Dafny or Nagini (assurance dossier: bounded search, a .NET or Viper stack, Python-version limits). Optional processes for a few pure functions; none is a dependency.
* **G. Trust the SQL engine for verdicts** and verify only the rules. Rejected: SQLite's behaviour with a LIMIT inside a recursive select is silent truncation (measured), and an absence finding over a truncated closure would be a false PASS.

## Decision outcome

Chosen option: **D**, because each rung was exercised on the actual artefacts and found real things (five items on sibling lanes, section 11 of the design), because the trusted kernel that results is about 200 statement lines on the reference, and because it adds no solver to the trust path.

1. **Ladder.** For every property use the cheapest rung that closes it: SCHEMA, ENUM (exhaustive, stated domain, with a finite reduction argued where a size-independent claim is wanted), CERT (certificate plus checker), PAPER (a short proof in the design document, hypotheses stated, not machine-checked), ALLOY (bounded, labelled CHECKED_BOUNDED), PROP (Hypothesis, derandomised), DIFF (two independent implementations). Machine-checked proofs only past a trigger.
2. **Trusted kernel.** The reader, the canonical writer and framing, the hash-method registry (okf lane), `link_status` with the lift and the ledger check, the status fold, the closure and order checkers, and rule evaluation with its second evaluator. One package, stdlib only, no `eijagraph` extractor or storage import, under a line budget enforced as a ratchet (interface to the quality and metrics lanes). Reference sizes measured: 205 statement lines for six components.
3. **Certificates.** Closure (a path, or a forward-closed set for absence), SCC partition, topological order; the checker reads the original input itself. Rule results are cross-checked by two evaluators on the release tier. Extractor fidelity is not certifiable and stays TESTED.
4. **Alloy 6.2.0** as an external, pinned, optional process (`graph/formal/TOOLS.lock`: sha256 `6b8c1cb5...`, 21,062,377 bytes, Java 17; solver Glucose by default, SAT4J on the release tier as a second backend). `run_alloy.py` accepts an answer only on exit code 0, a receipt that lists exactly the commands in the model, and every command's outcome equal to its `expect` clause; a missing or mismatching jar, a missing Java or a timeout is NOT_RUN. Wall-clock fields in Alloy's receipt are never copied into an artefact.
5. **Z3 is not used for weave-internal properties in phase 1.** clingo 5.8.2 is a test-time bridge for rule fixtures (MIT); TLA+ is reserved for a multi-writer cache. No solver is in the path of a verdict.
6. **Independent references** in `graph/formal/eijaref` (stdlib, no import of `eijagraph` or the kernel) with implementation-agnostic law suites, each run on the reference, on at least one wrong implementation (which it must fail) and, when the module exists, on the production function named in `graph/formal/binding.json` (NOT_RUN until then).
7. **Stage-0 self-check** (`graph/formal/selfcheck.py`) reports through its own channel and fails a suite that accepts a wrong implementation.
8. **Drift guards** for every model: regeneration byte-compare for generated models; named-condition parity between hand-written Alloy and Python; differential runs on exhaustive small scope; digest-pinned `conforms_to` and `proves` links in the weave (statement pinned by `law-block-v1`); bilateral mutation controls. Model links are labelled PROVED_IN_MODEL or CHECKED_BOUNDED, and the link to code CONFORMS_BOUNDED with the bound printed.
9. **The list of obligations** is `graph/formal/OBLIGATIONS.md`: 47 rows in seven groups (determinism, graph, status, metamodel and rules, lenses, trust, drift), each with its technique, scope, label and status. Adding a rule, a link type, a hash method or a model adds or updates a row in the same change.
10. **Findings forwarded, not fixed.** This lane changes no sibling file and nothing under `src/`. The five findings in the design (an environment-variable NOT_RUN acceptance, a tuple-accepting writer, a hash method that crashes on a lone-surrogate literal, two status-join differences, key-domain differences) go to their owners; the kernel change requests (JCS, `aggregate_status` composition) need their own ADRs.

### Consequences

* Good: the kernel is small enough to read in an afternoon, and the gate predicate is proved independent of the owner's open choice of where NOT_RUN sits in the chain (120 of 120 chains).
* Good: a sample became a result in three places by a stated finite reduction (status join over lists of any length; `merge3` laws over any alphabet and key count; the gate predicate over any chain), and the reduction is itself tested.
* Good: every check has a negative control; the determinism harness was shown able to fail (8 distinct outputs against 1).
* Good: Alloy caught nothing wrong but confirmed that each of the seven checker conditions is necessary within scope, and the mutants in Alloy and Python are tied by name parity.
* Good: no solver, no GPL component and no server enters the trust path; the jar is a separate process that is never redistributed.
* Bad: everything is about references and data files today. The production code does not exist, so eight bindings report NOT_RUN and the obligations are "MEASURED on a reference", never "discharged for the product".
* Bad: Alloy results are bounded (7 nodes for closure, 6 for SCC); the size-independent claims rest on paper proofs that no machine has checked.
* Bad: two independent readings of one specification can share a misreading (a differential agreement is evidence against slips only).
* Bad: the Alloy jar is 21 MB with bundled SAT solvers whose licences were not read; the LICENSE file's first line says the Apache text is "NOT VALID YET" and the code is MIT. The jar is fetched by the user, never vendored or redistributed.
* Bad: the exhaustive benchmarks take 75 s and Alloy 16 to 24 s (Glucose) or about 4 minutes (SAT4J) on the reference PC; the full tier pays 46 to 76 s for the test suite.
* Bad: POSIX byte identity is NOT_RUN, and so are the three nox sessions added to `quality/sessions/graph.py` (nox is not installed on the reference PC; their commands were run by hand).
* Revisit when: (a) `eijagraph` exists (bind and run all eight suites; a red one blocks); (b) a metamodel demand chain reaches depth 3, or a minimum obligation can exceed a maximum, or obligations become disjunctive (add Alloy or clingo metamodel satisfiability); (c) the rules aspect moves to an IR, or more than about 30 rules need recursion with negation (generate the model and the SQL from one IR); (d) a certificate kind arises whose soundness proof is not a short induction, or the owner asks for a machine-checked proof (Lean via `leanchecker`, or Bend through the bend lane); (e) a multi-writer incremental cache is built (TLA+); (f) a POSIX run disagrees with Windows; (g) an Alloy release changes verdicts on the pinned models (the pin protects, the trigger re-baselines).

## Interfaces and dependencies

Stated as contracts in the design document, section 13. Summary: metamodel aspect (structured obligation scope, table lemmas as part of `check_metamodel`); storage aspect (LIMIT + 1 rule); consistency aspect (per-view suites through the lens checker); rules aspect (NOT_RUN acceptance as a ledger entry, an optional IR, witness checkers); impact aspect (kernel-exact join in production); agent aspect (non-interference test); human-views aspect (stable `check_certificate` and `check_unreachable` signatures); okf lane (a fail-closed hash wrapper); tla, bend and smt-bmc lanes (`TOOLS.lock` and sentinel pattern); quality lane (kernel import contract, tags); property lane (Hypothesis profile); assurance aspect (statement pinning and assumption ledgers, the ARCHITECTURE 0103 content). Kernel: nothing changes in `src/`.

## OSS check (required for any custom module)

Custom modules introduced by this decision: `graph/formal/eijaref` (references, certificate checkers, law suites, rule IR with a stratifier and evaluator, metamodel and catalogue checkers, an optional clingo bridge), `graph/formal/run_alloy.py`, `graph/formal/selfcheck.py`, `graph/bench/formal_checks.py`, the Alloy models, and `tests/graph/formal`.

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Alloy 6.2.0 (MIT per the LICENSE header; separate process) | Adopted unchanged for bounded relational statements; only the models, the runner and the sentinel rule are custom, because Alloy's receipt has wall-clock fields and an `expect` mismatch is a process exit that must map to FAIL, a missing jar to NOT_RUN | Any Alloy 6 release by re-pinning; a second SAT backend already runs on the release tier |
| Z3 5.1.0.0 (MIT, smt-bmc lane pin) | Not needed: finite tables and reachability; would add a solver to the trusted base for no gain | Use it for arithmetic or bit-vector obligations if one appears |
| clingo 5.8.2 (MIT) | Adopted as a test-time evaluator and fixture synthesiser; only the IR-to-ASP text and the replay harness are custom | Alloy for the same fixtures (the pilot exists) |
| TLA+ and TLC (MIT, tla lane pin) | Reserved for interleavings; nothing in the verdict path is concurrent yet | Reuse the tla lane's `TOOLS.lock` and trace-validation idiom |
| Lean 4 with `leanchecker`, Bend `--verdict`, Dafny `audit`, cvc5 Alethe with Carcara (assurance dossier) | Second checkers and proof assistants for proof links; no theorem here needs them yet | Bend through the bend lane for the two certificate theorems if a trigger fires; Lean as an optional process |
| CrossHair, Dafny, Nagini (assurance dossier) | Bounded search or a .NET or Viper stack; Python-version limits; not needed for pure functions of this size | Optional processes for a few kernel functions |
| Hypothesis 6.168.3 (MPL-2.0, property lane pin) | Adopted unchanged as a test dependency with a derandomised profile | none needed |
| `rfc8785` 0.1.4 (Apache-2.0) | Adopted as an independent oracle for conformance on the subset; the production writer is custom because the kernel's `canonical()` is not JCS and the subset must refuse floats, tuples and non-string keys | The library as the production writer if a subset check is put in front of it |
| networkx 3.5 (BSD-3-Clause) | Test oracle only; its SCC labels are insertion-order dependent (5 labellings over 60 orders) | none needed |
| import-linter 2.15 (quality lane) | Adopted for the kernel import contract; it knows imports only | none needed |
| Neo4j Community (GPL-3.0), OKF pages | Never in the trust path; Neo4j is at most a differential closure check run by a person as a separate process, OKF is a get-only projection | none needed |
| EIJA-specific: the certificate checkers, the reference rule stratifier and evaluator, the partial-lens law checker, the metamodel and catalogue checkers, the Alloy runner | No OSS tool checks impact closures, SCC labels, status folds or a typed weave metamodel against an independent reference with negative controls and NOT_RUN semantics | Each part is small (the largest reference module is 250 lines) and replaceable behind the suite interfaces |
