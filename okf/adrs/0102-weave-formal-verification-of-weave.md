---
type: Architecture Decision Record
title: 'ADR-0102: Formal verification of the weave: a small trusted kernel, certificates, exhaustive small scope, Alloy for bounded statements, and drift guards'
description: The weave ties code, tests, requirements, UI, diagrams, the ubiquitous language, formal models and evidence into one typed, hash-anchored graph, and a rule set (the compiler and linters) reports on it.
resource: repo://docs/adr/0102-weave-formal-verification-of-weave.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0102-weave-formal-verification-of-weave.md
  title: 0102-weave-formal-verification-of-weave.md
  hash_method: lf-sha256-v1
  sha256: a596c83f804df2f02c7a4d384884b962a50a8f2037159c50e927a7fb3c29e8b2
notes_baseline: af7d69cae0d95f05192668f80f3f1ccfb83804dd00fd1c3865b731b88d06f4a2
---

# ADR-0102: Formal verification of the weave: a small trusted kernel, certificates, exhaustive small scope, Alloy for bounded statements, and drift guards

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | weave (aspect formal-verification-of-weave). Design and evidence: [docs/weave/design/formal-verification-of-weave.md](repo://docs/weave/design/formal-verification-of-weave.md). Obligation list: [graph/formal/OBLIGATIONS.md](repo://graph/formal/OBLIGATIONS.md). |
| Source | `repo://docs/adr/0102-weave-formal-verification-of-weave.md` |

## Decision outcome (verbatim)

> Chosen option: **D**, because each rung was exercised on the actual artefacts and found real things (five items on sibling lanes, section 11 of the design), because the trusted kernel that results is about 200 statement lines on the reference, and because it adds no solver to the trust path.
>
> 1. **Ladder.** For every property use the cheapest rung that closes it: SCHEMA, ENUM (exhaustive, stated domain, with a finite reduction argued where a size-independent claim is wanted), CERT (certificate plus checker), PAPER (a short proof in the design document, hypotheses stated, not machine-checked), ALLOY (bounded, labelled CHECKED_BOUNDED), PROP (Hypothesis, derandomised), DIFF (two independent implementations). Machine-checked proofs only past a trigger.
> 2. **Trusted kernel.** The reader, the canonical writer and framing, the hash-method registry (okf lane), `link_status` with the lift and the ledger check, the status fold, the closure and order checkers, and rule evaluation with its second evaluator. One package, stdlib only, no `eijagraph` extractor or storage import, under a line budget enforced as a ratchet (interface to the quality and metrics lanes). Reference sizes measured: 205 statement lines for six components.
> 3. **Certificates.** Closure (a path, or a forward-closed set for absence), SCC partition, topological order; the checker reads the original input itself. Rule results are cross-checked by two evaluators on the release tier. Extractor fidelity is not certifiable and stays TESTED.
> 4. **Alloy 6.2.0** as an external, pinned, optional process (`graph/formal/TOOLS.lock`: sha256 `6b8c1cb5...`, 21,062,377 bytes, Java 17; solver Glucose by default, SAT4J on the release tier as a second backend). `run_alloy.py` accepts an answer only on exit code 0, a receipt that lists exactly the commands in the model, and every command's outcome equal to its `expect` clause; a missing or mismatching jar, a missing Java or a timeout is NOT_RUN. Wall-clock fields in Alloy's receipt are never copied into an artefact.
> 5. **Z3 is not used for weave-internal properties in phase 1.** clingo 5.8.2 is a test-time bridge for rule fixtures (MIT); TLA+ is reserved for a multi-writer cache. No solver is in the path of a verdict.
> 6. **Independent references** in `graph/formal/eijaref` (stdlib, no import of `eijagraph` or the kernel) with implementation-agnostic law suites, each run on the reference, on at least one wrong implementation (which it must fail) and, when the module exists, on the production function named in `graph/formal/binding.json` (NOT_RUN until then).
> 7. **Stage-0 self-check** (`graph/formal/selfcheck.py`) reports through its own channel and fails a suite that accepts a wrong implementation.
> 8. **Drift guards** for every model: regeneration byte-compare for generated models; named-condition parity between hand-written Alloy and Python; differential runs on exhaustive small scope; digest-pinned `conforms_to` and `proves` links in the weave (statement pinned by `law-block-v1`); bilateral mutation controls. Model links are labelled PROVED_IN_MODEL or CHECKED_BOUNDED, and the link to code CONFORMS_BOUNDED with the bound printed.
> 9. **The list of obligations** is `graph/formal/OBLIGATIONS.md`: 47 rows in seven groups (determinism, graph, status, metamodel and rules, lenses, trust, drift), each with its technique, scope, label and status. Adding a rule, a link type, a hash method or a model adds or updates a row in the same change.
> 10. **Findings forwarded, not fixed.** This lane changes no sibling file and nothing under `src/`. The five findings in the design (an environment-variable NOT_RUN acceptance, a tuple-accepting writer, a hash method that crashes on a lone-surrogate literal, two status-join differences, key-domain differences) go to their owners; the kernel change requests (JCS, `aggregate_status` composition) need their own ADRs.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* Interfaces and dependencies
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/weave/ARCHITECTURE.md`
* `repo://graph/bench/formal_checks.py`
* `repo://graph/formal/OBLIGATIONS.md`
* `repo://graph/formal/binding.json`
* `repo://graph/formal/run_alloy.py`
* `repo://graph/formal/selfcheck.py`
* `repo://quality/sessions/graph.py`
* `repo://quality/tools/adr_index.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.

## Referenced by

* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
