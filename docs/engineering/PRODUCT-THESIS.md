# Product thesis: abstractions, domain and language

Status: owner's thesis recorded 2026-09-29; audience and first acceptance target clarified 2026-10-02. In the owner's words: *everything is abstraction, especially in software; the domain and its language are the most important thing; this product lets people see that better and see what agents do.* This document turns that into design and engineering consequences. It is a thesis to be tested, not a proven claim.

The [project mission](MISSION.md) turns this thesis into two delivery outcomes: a complete, polished, source-connected IDE across the supported workflow, demonstrated through a WOW walkthrough and showcase content; and a GitHub package demonstrating both proof of concept and reproducible proof of feasibility. The usable product must precede its recording. Finish coherent non-linear navigation, editors, source, agent changes, review, evidence, history and safe recovery; an isolated demo path is insufficient. Human benefit remains a separate validation result. These are development goals; current availability and acceptance are recorded in the self-dogfood contract.

## The claims

1. **Software is a stack of abstractions.** The hard part is choosing the right ones and naming them (the domain and its language), not typing code.
2. **The abstractions that matter are the domain's**: concepts, rules, invariants and vocabulary. Not AI-tooling abstractions (agent frameworks, prompt formats, tool protocols), which change every few months while the domain model outlives them.
3. **Agents write code faster than people can read it, but they do not hold the team's model of the domain.** The characteristic failure is silent drift: names, boundaries and rules change a little in every generated diff until code, UI, diagrams, tests and documents no longer describe the same thing.
4. **So people need to see the abstractions, and to see what an agent did to them.** Not the diff first; the change to the model first.

## What follows for EIJA

The following tables define intended product behavior, not current published capabilities. Availability and acceptance are recorded in the [self-dogfood contract](SELF-DOGFOOD-ACCEPTANCE.md).

| Consequence | Testable form |
|---|---|
| The primary object is the **domain model and ubiquitous language** (contexts, aggregates, terms, rules, invariants). Change cases and agent activity are views of *changes to that model*. | The language/DDD tree is a navigation root, not a settings page. Every screen names the abstractions it is about. |
| An agent's change is shown **as a change to abstractions** (terms, rules, relations added, renamed, split, merged) before it is shown as a code diff. | The review screen leads with a semantic diff of the model; the code diff is one click deeper. |
| Renaming, merging and splitting a concept is a **first-class, checked operation** with a computed ripple. | A rename produces the list of affected code symbols, UI labels, diagram elements, tests, requirements and evidence, deterministically. |
| **Drift is a lint error.** | Language-versus-code, language-versus-UI and model-versus-diagram mismatches are diagnostics from the compiler over the linked graph (the weave lane). |
| Evidence attaches to **abstractions and their invariants**, and says what it does not cover. | Each invariant shows its checks (test, property, model check, proof) and their status, with UNKNOWN visible. |

## Form factor: a modern IDE, not a wizard

The owner's clarification (2026-09-29): the Studio is essentially **a modern IDE**, in the family of Visual Studio, IntelliJ and VS Code, whose subject is the domain model and its language instead of only source files. It is not a wizard.

A wizard is linear (step 1, 2, 3, 4), modal and forgetful. An IDE is a **workbench**: many things visible and editable at once, navigated freely, with undo and history. What that means here:

| IDE concept | EIJA meaning |
|---|---|
| Explorer / project tree | the ubiquitous-language and DDD tree (contexts, aggregates, terms, rules), plus requirements, tests, ADRs, diagrams |
| Editor tabs and splits | diagram editor, rule/DSL text editor, semantic diff, term/concept editor, counterexample trace stepper, side by side |
| Language service and squiggles | the linked-graph compiler; drift and broken links are **diagnostics** |
| Problems panel | diagnostics from the compiler, with severity, provenance and quick fixes (deterministic codemods) |
| Go to definition / find references | term to code to UI to test to proof and back; **ripple is find-references** |
| Rename / refactor with preview | renaming, merging or splitting a concept is a typed semantic transaction with a computed ripple and a preview |
| Source-control changes view | an agent's work as a **changeset of abstractions**, not only of lines |
| Run / debug / test panel | evidence: proofs, model checks, property tests, mutation, with UNKNOWN visible |
| Command palette, quick open, keybindings | keyboard-first operation; every action has a name and a shortcut |
| Status bar | model hash, evidence status, agent activity, staleness |
| Worktrees and agent sessions | **Planned first-class views** of agent sessions, changesets, ownership and dependencies. Reuse worktrees; create another only for a concrete isolation need and handoff plan. A visible worktree does not imply safe parallel landing. |
| Conflict prediction | before anything lands, predict overlap between parallel changesets by **file, symbol and abstraction** (two agents renaming or splitting the same concept is a semantic conflict git cannot see) |
| Landing queue (merge queue) | review, merge main in, run the gates on the **merge result** (not just the branch), then merge; generated files and shared registries have merge rules so they stop conflicting |

Two things stay deliberately *unlike* a typical IDE: approving and applying a change is a structurally isolated, owner-only action (the kernel decides who may, not the UI), and UNKNOWN is a first-class state that the workbench never hides.

## Current delivery decisions: 2 October 2026

| Question | Decision and acceptance boundary |
|---|---|
| Primary audience | **Engineers who understand UML, domain models and software design, including those who increasingly build by prompting coding agents.** Prompting and modeling are complementary workflows. Support for people without that background is a later validation question. |
| Release outcomes | **WOW demo plus GitHub POC/POF.** A clear end-to-end demonstration establishes the concept; reproducible setup and scoped replay establish feasibility. Publish the complete supported IDE experience, evidence-derived walkthrough/clips and explicit limits together. Neither goal is complete merely because the UI or README exists. See [readiness](MISSION.md#prototype-readiness). |
| Engineering approach | **OSS first, one coordinated integration path.** Prefer maintained frameworks/compiler/indexer/prover tooling; add EIJA contracts, adapters and generators. Record an adoption/gap decision before implementing a replacement engine. Named file ownership, a dependency-ordered milestone ledger and retained evidence keep delivery reviewable. |
| First connected project | **EIJA itself first.** Exercise the real integration checkout, model/kernel, Python symbols and annotated UI in one read-only connection. External applications and held-out repositories follow a passing self-dogfood milestone; no external project is selected by this document. |
| What the agent must show | The proposed change to concepts/rules, its actual source links, affected known dependents, refusals and evidence scope. Source facts, explicit bindings, runtime observations and AI hypotheses must remain distinguishable. |
| Deterministic responsibilities | Parse supported structure, preserve stable identities, calculate known-edge impact, check typed model edits, and bind evidence to its subject. AI may propose domain meaning; it cannot turn an unsupported inference into a verified fact. |
| Any-codebase ambition | **Graded support:** intake, structural extraction, selected behavior bindings, checked properties and supported change application. An accepted repository may have unsupported languages or unbound behavior. Language-neutral contracts do not imply universal extraction or proof. |
| Current source-edit boundary | The first repository connection is read-only. Editing the model changes the supported EIJA candidate through the existing kernel; it does not rewrite the connected codebase. General two-way code/model edits remain a design target requiring adapters and conformance evidence. |
| Evidence of benefit | No superiority, novelty or comprehension claim follows from feature count. First prove the local flow; then compare correctness, critical misses, comprehension and total effort using the [V&V protocol](../research/2026-10-02-vv-protocol.md). Live model and human-study results are NOT_RUN. |

Audience research, 8 October 2026 (reference only): the [market gaps and ideal customer profile](../research/2026-10-08-market-gaps-and-icp.md) review suggested dropping prior UML knowledge as an entry requirement. The owner kept the current audience on 8 October 2026: engineers who already know UML. The review stays as background on market gaps, not an adopted direction.

[Self-dogfood acceptance](SELF-DOGFOOD-ACCEPTANCE.md) is the current bounded delivery contract. The [current-alternatives review](../research/2026-10-02-current-alternatives.md) records substantial overlap with existing products and research. The IDE and model operations described in this thesis are design requirements. The wider capabilities below are not a claim that they are implemented.

## Design decisions retained from 29 September 2026

| Question | Decision |
|---|---|
| Source of truth | **Hybrid, two-way.** Code and model are both real; an edit on either side becomes a typed, checked change. |
| First minutes | **Prompt-first is the default** and must be as fast as vibe coding: the owner prompts, agents build, and the IDE *extracts* the language, DDD tree and UML for the owner to confirm (the model crystallizes). **Model-first is also supported** for people who want to define language and domains up front. |
| Code editor | **None built in.** Code is written by agents or in the developer's own editor; the IDE shows code read-only with model-aware navigation (go to definition, find references, ripple). The model editors are the editors. |
| Centre of gravity | **UML, modelling and flow diagrams.** Abstractions are seen as a **tree and as a graph**; **design patterns are shown visually** (recognised in the model and code, applied as checked refactorings). It must **feel good** to use, and speed is a requirement. |
| Flagship demonstrations | (1) side by side with a vibe-coding tool: the same feature evolved repeatedly, showing observed drift or preservation in both conditions without predetermining failure; (2) an agent's change as a semantic diff with ripple and evidence; (3) drag-and-drop UML that updates the software (a typed change, generated code and affected tests, or a rule blocks it with a reason); (4) parallel agents landing safely (semantic conflict prediction, gated landing queue); plus visualisations "under the hood" and UI/UX viewing. |

## Non-goals

EIJA does not invent AI abstractions, and it does not claim to make abstractions *correct*. It makes them visible, linked, checked against the code, and reviewable, and it keeps the human decision with the human.

## Reading list (leads to verify; do not cite from this file without opening the source)

Brooks, "No Silver Bullet" (essential versus accidental complexity); Naur, "Programming as Theory Building" (1985: a program embodies a theory held by its programmers); Evans, *Domain-Driven Design* (ubiquitous language, bounded contexts); Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules" (1972); Dijkstra, "The Humble Programmer" (1972); Ousterhout, *A Philosophy of Software Design* (deep modules); Abelson and Sussman, *Structure and Interpretation of Computer Programs* (building abstractions).

## Open questions (owned by the eval work)

Does an explicit, linked domain model measurably improve agent success and human review accuracy? The evaluation design must compare agents with and without the language/graph context, and reviewers with and without the semantic diff, using pass^k and pre-registered tasks. Until that is measured this remains a hypothesis we are building the tool to test.
