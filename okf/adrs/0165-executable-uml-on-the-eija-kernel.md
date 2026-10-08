---
type: Architecture Decision Record
title: 'ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check'
description: PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a running app checked against the kernel (ADR-0150).
resource: repo://docs/adr/0165-executable-uml-on-the-eija-kernel.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0165-executable-uml-on-the-eija-kernel.md
  title: 0165-executable-uml-on-the-eija-kernel.md
  hash_method: lf-sha256-v1
  sha256: 5412173a0b0391f9d3d920626d226dd454d682871d390172d3cc85fbe6deddf9
notes_baseline: cfcf056b504e04537a8c691f37bbd89a5e3291cfedfb4ef74e19c794beb887bd
---

# ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for the state-machine slice |
| Date | 2026-10-08 |
| Lane | executable UML (owner direction, 8 October 2026: "how UML is executable and then runnable, with EIJA as the system underneath") |
| Source | `repo://docs/adr/0165-executable-uml-on-the-eija-kernel.md` |

## Decision outcome (verbatim)

> Chosen option: **D**, because it keeps one interpreter and one source per fact, makes the meaning of the state diagram checkable against a W3C standard by code EIJA did not write, and grows expressiveness one typed operator at a time rather than through a general action language.
>
> 1. **Each UML view has one of three standings** (table in the architecture doc): *executable* (the kernel runs it: states, transitions, guards, effects, the record class's attributes), *checked design* (the kernel or a design check refuses it when it disagrees with the executable part: screens and use cases), or *derived* (generated from the executable model or a run and never edited as a source: sequence diagrams from the commit algorithm and from Simulate traces, component diagrams from the generated code).
> 2. **The action vocabulary is closed and typed.** Guards are the `Guard` literals, effects are declared `audit` or `notification` effects with typed adapters, and changes are the `domain.transactions` kinds. There is no action language. A new construct enters only with executable semantics, a missing-resolver refusal, projection rules, identity effects, a negative oracle and an evidence policy (repository rule). A test (`tests/test_executable_uml_profile.py`) fails if a guard or transaction kind is added without a row in the semantics table.
> 3. **AI is the author, not the interpreter.** Chat plan mode (ADR-0156) and drawn edits (ADR-0157) produce typed transactions; the policy refuses what breaks a law; the person accepts. The expressiveness gap that stalled MDA was the cost of writing precise models by hand. AI lowers that cost while the vocabulary stays small enough to check.
> 4. **SCXML export.** `eija scxml --pack P [--workflow F] [--out F]` (`application/scxml.py`, pure) writes the state machine as a W3C SCXML statechart: atomic states, one event per action, a `cond` holding the actor and version checks, and executable content that bumps `version` and appends each effect in order. The actor is resolved by the sender, as the kernel's `UnitOfWork.actor` port does. A model the policy blocks is not exported (`POLICY_BLOCKED`). Committed charts for every pack live in `verification/scxml/generated/` and the `scxml_drift` gate (fast, full) keeps them fresh.
> 5. **Differential check.** `python -m verification.scxml.differential` runs every app-oracle case (`appgen.oracle_cases`: state x action x fixture actor x expected version, plus an undeclared action and an unknown actor) on python-statemachine 3.2.1 and compares state, version and effects with the kernel's answer. Measured 2026-10-08 on linux, Python 3.13: 960 cases over three packs (360, 240, 360), 18 commits, 0 disagreements. Nine negative controls each break the chart one way (drop the role, assignment or version check; retarget a transition; drop, reorder or skip effects; move the initial state; add a transition) and each must produce a disagreement. The `scxml_differential` gate (full, release) reports NOT_RUN without the engine, never PASS.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_executable_uml_profile.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
* [ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects](/adrs/0156-chat-plan-mode-proposes-typed-steps.md) - The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or…
* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".

## Referenced by

* [ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE](/adrs/0166-laws-proved-over-every-run-for-any-pack.md) - Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned…
<!-- okf:generated:end links -->
