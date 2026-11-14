---
type: Architecture Decision Record
title: 'ADR-0245: A partial UML read keeps what it could not read, and a save names its system'
description: A Fagan-style inspection of everything that keeps or moves a model (undo and redo, browser autosave, Save and the systems home, UML import and export) found ten defects.
resource: repo://docs/adr/0245-partial-reads-keep-and-saves-name-their-system.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0245-partial-reads-keep-and-saves-name-their-system.md
  title: 0245-partial-reads-keep-and-saves-name-their-system.md
  hash_method: lf-sha256-v1
  sha256: 799c321a4d0a6bc73fae0efa99da4f17ac25b70f99927b69fdab57808b4dc020
notes_baseline: 1fd84440a1bf113d86f49d096fceb32d605c87099d08b49c0ffa5b712876da18
---

# ADR-0245: A partial UML read keeps what it could not read, and a save names its system

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-13 |
| Lane | PlayIDE saving and UML interchange (inspection of 2026-11-13) |
| Source | `repo://docs/adr/0245-partial-reads-keep-and-saves-name-their-system.md` |

## Decision outcome (verbatim)

> * `Parsed.unread_part` records a transition or region that was drawn but not read, and `Parsed.pseudostate` a
>   pseudostate. `Parsed.settle()` runs after every reader: an arrow to or from a pseudostate becomes an unread part, and
>   a pseudostate is never a state. The import's partial count adds these, so it removes nothing.
> * PlantUML arrows read the style before or after the direction (`-left[#red]->`) and backward arrows (`B <-- A`). A
>   line that still looks like an arrow and is not read counts as unread.
> * `ImportReport.unread` holds each attribute (class, name) and association (source, target, role) the file has but
>   could not be read. The current model's own element with that key is kept in its place and listed under "Kept or
>   filled in". `changes` also lists associations added, removed and changed, and a new record class.
> * Save and "Clear saved work" send `pack`, the system the page opened on. The server refuses another with
>   `SYSTEM_CHANGED` (409), and the page shows the message. Without `pack` (older pages, the CLI) nothing changes.
> * In the page: a browser draft written on an earlier model moves to `<draft key>:earlier` before anything can
>   overwrite it, and is offered again on later loads until it is reopened. Undo and redo reload the model's own screens
>   after the restore ends, so an edit made while they load is kept in the history and in the browser. When storage
>   cannot hold even the current snapshot, the older draft under the key moves aside as an earlier draft, so a reload
>   does not bring it back as the latest work.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0185: Start, open and save your own system in PlayIDE](/adrs/0185-start-open-and-save-your-own-system.md) - PlayIDE could only show the pack the server was started with (`eija serve --pack …`), and every pack was one that ships with EIJA.
* [ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel](/adrs/0190-uml-import-and-export-through-the-kernel.md) - PlayIDE's users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code;…
* [ADR-0198: Undo, redo and autosave of the edited document in PlayIDE](/adrs/0198-undo-redo-and-autosave-of-the-edited-document.md) - PlayIDE is meant to be more robust than the UML tools engineers already use, and every one of those has undo.

## Referenced by

* [ADR-0250: An import matches renamed and respaced names, and two tabs keep each other's work](/adrs/0250-imports-match-names-and-tabs-keep-each-others-work.md) - A second, deeper inspection of saving and UML interchange followed ADR-0245.
<!-- okf:generated:end links -->
