---
type: Architecture Decision Record
title: 'ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel'
description: 'PlayIDE''s users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code; Mermaid in a README; draw.io in Confluence.'
resource: repo://docs/adr/0190-uml-import-and-export-through-the-kernel.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0190-uml-import-and-export-through-the-kernel.md
  title: 0190-uml-import-and-export-through-the-kernel.md
  hash_method: lf-sha256-v1
  sha256: 60863bd39154176248666ce84ff524797cd0492df65e392c726fb48478517d98
notes_baseline: 4abb9e6ff29851f1189adb5cd23fb53ffd4d924a937cd0864c8f757dddcf8689
---

# ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for state machines and class models |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026: "what else, spawn threads") |
| Source | `repo://docs/adr/0190-uml-import-and-export-through-the-kernel.md` |

## Sections

* Context and problem statement
* Decision drivers
* Order of the formats
* Considered options
* Decision
* Evidence
* Consequences

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_uml_actor_kinds.py`
* `repo://tests/test_uml_new_system.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0185: Start, open and save your own system in PlayIDE](/adrs/0185-start-open-and-save-your-own-system.md) - PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.
* [ADR-0210: Actors that are not people: AI agents, timers and external systems in the model](/adrs/0210-actors-that-are-not-people.md) - Systems people design now have AI agents in them: a support bot that triages tickets and proposes refunds, a scheduled job that escalates what nobody handled,…

## Referenced by

* [ADR-0201: Build a new system in chat, round after round](/adrs/0201-build-a-new-system-in-chat-round-after-round.md) - The showcase changes a pack that already exists (Library loan).
* [ADR-0216: Describe your app, and what's missing](/adrs/0216-describe-your-app-and-whats-missing.md) - Until now a new system started from three sketch lines, a template or a UML file (ADR-0185, ADR-0190), and then grew in chat (ADR-0201, ADR-0202).
<!-- okf:generated:end links -->
