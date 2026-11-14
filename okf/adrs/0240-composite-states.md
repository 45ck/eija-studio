---
type: Architecture Decision Record
title: 'ADR-0240: Composite states'
description: 'Issue #93, item 3.'
resource: repo://docs/adr/0240-composite-states.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0240-composite-states.md
  title: 0240-composite-states.md
  hash_method: lf-sha256-v1
  sha256: 090508c89f0407eb1a8a20f76982374e48328792df02ade5af7b362af51fb669
notes_baseline: 4663a675bac49d394beb7a7e28fea00213d9f2b2809555672f2c49f722a50daa
---

# ADR-0240: Composite states

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | kernel / executable UML |
| Source | `repo://docs/adr/0240-composite-states.md` |

## Decision outcome (verbatim)

> **The model.** A workflow may carry `composites`, up to 16 of `{name, states, initial}`. `states` are its children, which are plain states or other composites, and `initial` is the child a transition into it enters first. They must form a tree: names are unique and differ from every state, each child is known and has one parent, each composite's initial is one of its children, and no composite holds itself. When there are none, the field is left out of every dump, so flat models keep their bytes and semantic hash. The semantic hash sorts composites and their children, because they are sets.
>
> `Workflow.parent`, `ancestors`, `leaves` and `entry` answer the questions a view needs: which composite holds a state, which plain states a composite holds, and which plain state a transition into a composite enters.
>
> **The kernel.** It runs the flat machine. A composite never changes which step commits, so the law proof, Simulate, the oracle and the built app are unchanged, and a test shows the law proof finds the same runs with and without the grouping.
>
> **SCXML.** A composite becomes a compound `<state>` with its `initial`, holding its children. Where one action leaves every state inside a composite (ADR-0232 makes those transitions alike but for their source), the chart carries that transition once, on the composite, so the engine's own hierarchy decides it. The outermost composite that fits wins. The differential runs every oracle case on the nested chart and requires the kernel's answer. As a negative control, a chart that carries such an action on an inner composite only disagrees.
>
> **Diagrams.** Mermaid and PlantUML write `state X { ... }` blocks, and DOT nests clusters. PlayIDE draws a box around each composite's states, and its layout keeps them together (dagre's compound graphs, MIT). A flat model is laid out exactly as before. The diff reports composites added, removed or regrouped.
>
> **Edits.** Renaming a state renames it in its composite. Removing a state takes it out of its composite, but a state that is a composite's initial child or its only child is still in use.
>
> **Interchange.** The UML exports list composites as not carried, as they do for value guards and time events.
>
> **The example.** The refund desk groups `AwaitingApproval` and `WithSupervisor` as `Deciding`, and `Approved` and `PayoutFailed` as `PayingOut`.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.

## Referenced by

* [ADR-0250: An import matches renamed and respaced names, and two tabs keep each other's work](/adrs/0250-imports-match-names-and-tabs-keep-each-others-work.md) - A second, deeper inspection of saving and UML interchange followed ADR-0245.
<!-- okf:generated:end links -->
