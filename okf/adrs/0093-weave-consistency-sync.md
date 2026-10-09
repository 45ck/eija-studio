---
type: Architecture Decision Record
title: 'ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge'
description: 'EIJA keeps many views of one system: code, workflow model, diagrams, OKF pages, term registry, UI sidecar, requirements, links, ledger, exports.'
resource: repo://docs/adr/0093-weave-consistency-sync.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0093-weave-consistency-sync.md
  title: 0093-weave-consistency-sync.md
  hash_method: lf-sha256-v1
  sha256: 251cc13ac5c38732e282b16dba496f2e1e8b14d1f66e341071a94620b7b5ef5b
notes_baseline: c335c1ae6a8aa4fd0e32c2a635f5844d87722a4c6a3dac4a3e8cacb8773ceb8d
---

# ADR-0093: Consistency and synchronisation between views: one source per fact, one-way generation, keyed merge

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-29 |
| Lane | weave (aspect consistency-sync). Design: [docs/weave/design/consistency-and-sync.md](repo://docs/weave/design/consistency-and-sync.md). Contracts and laws: [graph/schema/transformations.md](repo://graph/schema/transformations.md). |
| Source | `repo://docs/adr/0093-weave-consistency-sync.md` |

## Decision outcome (verbatim)

> Chosen option: **B**, because it is the only option that keeps the trust path small (a pure generator, a digest comparison, a keyed merge and a compiler that recomputes), keeps every write in git, and reuses existing mechanisms (the kernel's typed transactions and optimistic concurrency, the okf lane's hash methods, git itself).
>
> 1. **Sources and derived artefacts.** A fact has one authoring home. Y is derived from X iff Y is the output of a fixed, versioned generator that reads only X and declares its inputs (a bare "some deterministic function exists" is vacuous: the constant function qualifies); a derived artefact is a function of authored sources only. Authored sources: workflow model, code and tests, requirements, term registry, declared links, ledger, ADRs and prose, formal models, UI sidecar and markup, intended architecture. Derived, get-only: diagrams, SysML text, exports, generated checks, the graph index, findings. Mixed: an OKF page (generated blocks plus human notes) is a lens with a complement. Proposals, never truth: canvas edits, imported diagrams, agent suggestions, inferred edges.
> 2. **Default is one-way.** Sync is exactly three operations: regenerate (deterministic), propose (a value; nothing applies), ack, merge or commit (a human). A hand edit of a generated region is a finding (CS-02), never merged.
> 3. **Bidirectionality in four places only:** OKF pages (exists; complement laws C1 to C4), a canvas edit translator (proposal only, deferred until the owner wants to author by drawing), explicit renames (one intent, many sources), and the human ack (subject-bound to a digest). The lens laws are executable tests, not a library: GetPut, PutGet modulo layout and declared amendments, conditional PutPut, layout independence, order (dependency-sorted batches), totality, purity, applicability, identity by id.
> 4. **Eleven transformation contracts** (model to diagram, diagram edit to transaction, model to SysML text, model to code obligations and checks with create-once stubs, model to UI projection and UI checks, graph to OKF, code to facts and reflexion, rename, merge, ack, exports) in `graph/schema/transformations.md`, each with class, pins, laws, failure codes, tests and status.
> 5. **Merge.** Authored graph files are canonical, sorted, one record per line. `merge3(base, ours, theirs)` is a keyed three-way merge over whole records: for a fixed base it is the join in a flat lattice per key (proved; symmetric, idempotent, associative where defined). After any merge the compiler runs on the merged tree, and the findings absent from both parents are reported as semantic conflicts. The merge is exposed as a command that reads the git index stages; a custom git driver is an optional convenience only, because driver definitions live in `.git/config` and are per clone.
> 6. **Ledger and evidence are grow-only sets of content-addressed entries**, with `prev[]` sorted before hashing. Layout: either one sorted file merged with git's built-in `union` driver followed by canonicalisation (hosted-merge behaviour of `merge=union` is UNVERIFIED), or, preferred, one file per entry named by `entry_id`; both guarded by an append-only gate. Acks are bound to the digest the reviewer saw, so an ack on one branch cannot hide a code change on another. The link record's `ledger_seq` is replaced by `entry_id` (requested of the link-record and ledger owner).
> 7. **No CRDT library.** A CRDT is warranted only if all four hold: concurrent writers without a review point, interactive latency, merge-safe invariants (or a coordinated commit), and acceptance of convergence without human conflict review. None holds today; the criterion and the triggers are recorded.
> 8. **Renames are explicit records**; removal is deprecation first, delete only when the compiler shows no inbound links; no inference of moves.
> 9. **Tolerant drafts, enforced boundaries**: the working tree may be inconsistent; the fast tier (commit), full tier and release tier enforce. A draft is a proposal value, never evidence.
> 10. **Committed derived files** (diagrams, okf bundle, generated tests) resolve merge conflicts by regeneration. The graph manifest keeps pins; the root hash moves to the release receipt and gate output (recommended, needs the ARCHITECTURE owner).

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* Interfaces and dependencies on other lanes and aspects
* OSS check (required for any custom module)
* Verification and evidence

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/weave/ARCHITECTURE.md`
* `repo://graph/bench/consistency_checks.py`
* `repo://graph/schema/transformations.md`
* `repo://pyproject.toml`
* `repo://tests/graph/test_consistency_checks.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0089: Weave metamodel and identity: a closed typed metamodel, canonical ids, an RFC 8785 subset and sorted-record hashing](/adrs/0089-weave-metamodel-identity.md) - EIJA Studio wants deterministic, machine-checkable links between code, UI, diagrams, ubiquitous language, requirements, tests, formal results, evidence, ADRs a…
* [ADR-0095: The weave compiler and lint rules: violation queries over a typed graph, SARIF diagnostics, expiring suppressions](/adrs/0095-weave-lint-compile-rules.md) - EIJA wants deterministic, machine-checkable links between code, tests, requirements, the ubiquitous language, UI, diagrams, formal models, evidence and ADRs, a…
* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…

## Referenced by

* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay](/adrs/0099-weave-agent-interface.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports f…
* [ADR-0105: Human views: eight task-driven, budgeted, deterministic projections of the weave graph, with counts that compose and no whole-graph picture](/adrs/0105-weave-human-views.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, and a checker will produce fi…
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0203: A system landscape of the workflows that share classes](/adrs/0203-system-landscape-of-workflows-that-share-classes.md) - PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.
* [ADR-0206: A deployment view read from the built app's files](/adrs/0206-a-deployment-view-read-from-the-built-apps-files.md) - PlayIDE had no deployment view.
* [Weave: deterministic linked graph, compiler and linter (`weave`)](/lanes/0089-weave-deterministic-linked-graph.md) - Capability lane with ADR numbers 0089–0112 reserved.
<!-- okf:generated:end links -->
