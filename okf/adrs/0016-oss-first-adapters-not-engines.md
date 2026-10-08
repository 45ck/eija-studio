---
type: Architecture Decision Record
title: 'ADR-0016: OSS first: build adapters, not engines'
description: 'EIJA''s value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.'
resource: repo://docs/adr/0016-oss-first-adapters-not-engines.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0016-oss-first-adapters-not-engines.md
  title: 0016-oss-first-adapters-not-engines.md
  hash_method: lf-sha256-v1
  sha256: 76ece21c8e718003b8b3f1da32babb8bca1d9baa4c32fb42600d206cfbc7a7f4
notes_baseline: 29f7b458f671b8da0a1d17e430a1c5d3e5840f24e5eedd6f46358c63b9634cb2
---

# ADR-0016: OSS first: build adapters, not engines

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Source | `repo://docs/adr/0016-oss-first-adapters-not-engines.md` |

## Decision outcome (verbatim)

> Every capability first adopts existing open source (see [docs/oss/REGISTER.md](repo://docs/oss/REGISTER.md)). Custom code is limited to EIJA-specific glue:
>
> * **generators** that project the executable model into a tool's input format,
> * **adapters** that turn the tool's output into typed EIJA evidence, and
> * the **kernel** itself.
>
> This follows the ProofMap Lite doctrine (<https://github.com/45ck/proofmap-lite>). Each custom module records, in the register or its ADR, the OSS it checked, why adapter or dependency use was insufficient, and the path to replace or fork it.

## Sections

* Context and problem statement
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer](/adrs/0023-generated-uml-and-visual-diff.md) - ADR-0019 decided that diagrams are generated projections of the executable model.
* [ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container](/adrs/0025-bend-machine-checked-laws.md) - The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle.
* [ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC](/adrs/0027-tla-plus-specification-and-model-checking.md) - The v0.2 runtime matrix checks one step from each state.
* [ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates](/adrs/0029-z3-policy-soundness-proof.md) - `domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner.
* [ADR-0031: Property-based testing with Hypothesis, in two profiles](/adrs/0031-property-based-testing-with-hypothesis.md) - The kernel's guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to…
* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…
* [ADR-0035: Static analysis, architecture fitness functions and ratcheted budgets](/adrs/0035-static-analysis-and-architecture-fitness-functions.md) - The kernel's central claims (a vendor-free domain, authority checked before replay, computed evidence) hold only while the code keeps its shape.
* [ADR-0037: Measure design, performance and scaling with radon, grimp and coverage.py, and fit models rather than assert them](/adrs/0037-metrics-and-quantitative-models.md) - EIJA Studio claims a clean layered design (domain and application never import adapters), an O(V+E) impact closure and an interactive local UI.
* [ADR-0038: Metric budgets are tests with a stated basis, and timing budgets are advisory in the full gate](/adrs/0038-metric-budgets-as-tests.md) - Metrics that nobody enforces decay into a dashboard.
* [ADR-0039: Apply HCI laws to the Studio UI with Playwright, axe-core and pure formula modules](/adrs/0039-hci-law-instrumentation.md) - The Studio UI is the owner's only instrument for reviewing an AI-proposed change, yet its usability claims are unmeasured.
* [ADR-0041: MCP server as the agent surface: propose and check, never decide](/adrs/0041-mcp-server-agent-surface.md) - People want their own agents (Claude Code, Codex, OpenCode, Gemini CLI) to use EIJA Studio.
* [ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site](/adrs/0043-readme-truthfulness-and-docs-site.md) - EIJA's promise is that what you see matches the code.
* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](/adrs/0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
* [ADR-0047: Hand-authored scripted demo recordings, not demo-machine](/adrs/0047-hardcoded-scripted-demos-not-demo-machine.md) - The owner wants live recordings — real cursor movement, real typing — that show a developer using EIJA Studio end to end: defining ubiquitous language into a D…
* [ADR-0048: Demo scenarios are gated by their real dependencies, never faked](/adrs/0048-scenario-dependency-gating.md) - The owner's full demo narrative (ubiquitous language → DDD tree, drag-and-drop UML kept in sync with the model, in-app image generation, e2e tests/personas/ICP…
* [HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll](/adrs/0058-hci-layout-model.md) - HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll
* [HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio](/adrs/0060-hci-typography.md) - HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio
* [HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture](/adrs/0061-hci-canvas-uml.md) - HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture
* [HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple](/adrs/0062-hci-language-ddd-tree.md) - HCI-ADR-0062: Ubiquitous-language and DDD tree as the navigation spine, with typed edits and a tiered rename ripple
* [HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change](/adrs/0068-hci-design-system-architecture.md) - HCI-ADR-0068: Design system architecture: DTCG tokens with a small generator, layered CSS, native-first components, measured budgets and ADR-gated change
* [ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing](/adrs/0089-weave-metamodel-identity.md) - EIJA Studio wants deterministic, machine-checkable links between code, UI, diagrams, ubiquitous language, requirements, tests, formal results, evidence, ADRs a…
* [ADR-0091: Storage and query: git files are the truth, a disposable SQLite index answers named queries](/adrs/0091-weave-storage-query.md) - Weave ties code, UI, diagrams, language, requirements, tests, proofs, evidence and decisions into one typed graph checked by a compiler-like rule set.
* [ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge](/adrs/0093-weave-consistency-sync.md) - EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.
* [ADR-0095: The weave compiler and lint rules: violation queries over a typed graph, SARIF diagnostics, expiring suppressions](/adrs/0095-weave-lint-compile-rules.md) - EIJA wants deterministic, machine-checkable links between code, tests, requirements, the ubiquitous language, UI, diagrams, formal models, evidence and ADRs, a…
* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay](/adrs/0099-weave-agent-interface.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports f…
* [ADR-0102: Formal verification of the weave: a small trusted kernel, certificates, exhaustive small scope, Alloy for bounded statements, and drift guards](/adrs/0102-weave-formal-verification-of-weave.md) - The weave ties code, tests, requirements, UI, diagrams, the ubiquitous language, formal models and evidence into one typed, hash-anchored graph, and a rule set…
* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…
* [ADR-0151: PlayIDE canvas with Build & run of the live app](/adrs/0151-playide-canvas-and-build-and-run.md) - The owner wants EIJA to feel like "UML you can trust to build apps": a visual, mouse-driven IDE (named PlayIDE) where a UML-literate engineer designs a system…
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE](/adrs/0166-laws-proved-over-every-run-for-any-pack.md) - Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned…
<!-- okf:generated:end links -->
