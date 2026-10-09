---
type: Architecture Decision Record
title: 'ADR-0210: Actors that are not people: AI agents, timers and external systems in the model'
description: 'Systems people design now have AI agents in them: a support bot that triages tickets and proposes refunds, a scheduled job that escalates what nobody handled, a payment provider that calls back.'
resource: repo://docs/adr/0210-actors-that-are-not-people.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0210-actors-that-are-not-people.md
  title: 0210-actors-that-are-not-people.md
  hash_method: lf-sha256-v1
  sha256: 460698debab8e02e23ed9554d7c25eadb81c412c08ce148d7edb1f3269bd28ad
notes_baseline: 7161c15b18bbd5471859eabf3e6ccc6f5553c3d3f1052ab3a62fc53c277011c1
---

# ADR-0210: Actors that are not people: AI agents, timers and external systems in the model

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE (owner ask, 9 October 2026: many tasks across sectors to refine "how humans and computers and agents and software etc is all designed"; this record covers non-human actors inside the system being designed, not PlayIDE's own chat AI) |
| Source | `repo://docs/adr/0210-actors-that-are-not-people.md` |

## Decision outcome (verbatim)

> Chosen option: a role kind and three kind laws, because they say the thing engineers need to say about agents in the vocabulary they already use, in data the kernel already checks.
>
> * **Role kind.** `Role.kind` in `domain/pack.py`. A person is the default and is not written out when the pack is serialised, so existing packs keep their digests.
> * **`only_kind_holds`** (action, role kinds): every transition performing the action is held by a role of those kinds. "Only a person approves a refund."
> * **`only_kind_enters`** (state, role kinds): every transition entering the state is held by a role of those kinds, whatever the action.
> * **`path_requires_kind`** (state, role kinds): every path from the initial state to the state includes a step by a role of those kinds, the entering step included. "A person acted on every refund that is paid."
> * **Binding.** When a pack loads, each kind law is bound to the pack's roles of its kinds. A role the pack does not declare has no kind, so it never counts: an AI proposing a step for an invented "AutoApprover" role breaks the law. A kind law whose kinds match no declared role is refused when the pack loads (`no declared role is of kind …`).
> * **Where each is judged.** The protected policy judges all three on the table on every edit, so a chat plan or a drawn edit that gives the approval to the agent is refused and names the laws. The law proof (ADR-0166) judges them on every run; for `path_requires_kind` its configurations also record whether a step of the law's kinds has happened yet. The generated SMT encoding covers the two per-transition laws; the path law is listed NOT_RUN with the reason, like `path_requires`.
> * **Diagrams and Simulate.** The use case diagram draws a person as a stick figure and the other kinds as an actor classifier with «agent», «timer» or «system». Simulate reports what each kind of actor tried and what the kernel answered, and the run log names an actor's kind when it is not a person. `/api/play/roles` serves the kinds to the page.
> * **Example.** `packs/refund-desk`: an AI agent triages and proposes, a timer escalates, the payment system confirms or fails a payout, and only a supervisor on shift approves. Its test cases include the agent being refused when it tries to approve, a paused agent (its kill switch: an inactive actor) refused at once, and a supervisor unable to mark a refund paid by hand.

## Sections

* Context and problem statement
* Decision drivers
* What existing tools do
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0166: Laws as the layer above the UML, proved over every run for any pack, with a Laws tab in PlayIDE](/adrs/0166-laws-proved-over-every-run-for-any-pack.md) - Every pack already states its laws as typed data in `pack.json` (`domain/laws.py`, twelve kinds): "only a librarian checks a loan out", "every path to Returned…

## Referenced by

* [ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel](/adrs/0190-uml-import-and-export-through-the-kernel.md) - PlayIDE's users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code;…
<!-- okf:generated:end links -->
