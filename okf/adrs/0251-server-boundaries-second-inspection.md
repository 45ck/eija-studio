---
type: Architecture Decision Record
title: 'ADR-0251: Request caps per route, no repository filters, and a server that cleans up after itself'
description: A second, deeper inspection of the `eija` command and the local server (CLI-SERVER-INSPECTION, "Second pass") found eight defects (S1 to S8).
resource: repo://docs/adr/0251-server-boundaries-second-inspection.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0251-server-boundaries-second-inspection.md
  title: 0251-server-boundaries-second-inspection.md
  hash_method: lf-sha256-v1
  sha256: 99affd3f45755fa0705df569ad046d4c5c03f130777cb07c4ab42bc005d5f7f6
notes_baseline: b16011664a85ff7893ec025853c442394eb54b50f81470bc5a818906a5357986
---

# ADR-0251: Request caps per route, no repository filters, and a server that cleans up after itself

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-14 |
| Lane | interfaces / security (second Fagan inspection of the command line and server) |
| Source | `repo://docs/adr/0251-server-boundaries-second-inspection.md` |

## Decision outcome (verbatim)

> All four chosen options above, plus line fixes for S5 to S8 (recorded in the inspection log): the IDE confirms that the server on the built app's port is that build (its `/api/app` names the build subject) before it frames it; a request is pinned to the system it began on (`StudioHandle.pinned`), and a draft is checked and written with no system switch in between; new systems are created one at a time so a double click makes `x` and `x-2`; a backup is a new 0600 file.

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

* [ADR-0190: UML import and export: XMI, PlantUML, Mermaid and draw.io, with every import judged by the kernel](/adrs/0190-uml-import-and-export-through-the-kernel.md) - PlayIDE's users already know UML and already keep UML somewhere else: XMI in Enterprise Architect, Cameo, Papyrus or Visual Paradigm; PlantUML beside the code;…
<!-- okf:generated:end links -->
