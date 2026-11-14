---
type: Architecture Decision Record
title: 'ADR-0244: The built app gets no secrets, and `eija serve` binds its port before it prints a link'
description: A Fagan inspection of the `eija` command and the local server (CLI-SERVER-INSPECTION) found two boundary defects.
resource: repo://docs/adr/0244-built-app-environment-and-bind-before-links.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0244-built-app-environment-and-bind-before-links.md
  title: 0244-built-app-environment-and-bind-before-links.md
  hash_method: lf-sha256-v1
  sha256: ee9640ad9c727297af2bae35724020c2c3f56388cd632d94a52fba521b3c9998
notes_baseline: 31a0abd8538c47b02de59888aebb8f76c97dc5ec083943e21d12f376e53117a2
---

# ADR-0244: The built app gets no secrets, and `eija serve` binds its port before it prints a link

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-13 |
| Lane | interfaces / security (Fagan inspection of the command line and server) |
| Source | `repo://docs/adr/0244-built-app-environment-and-bind-before-links.md` |

## Decision outcome (verbatim)

> Chosen options: the allowlist (`interfaces.play.APP_ENVIRONMENT`: `PATH`, the Windows system variables, home, locale, time zone, temp folders and `VIRTUAL_ENV`, plus `PORT`), and bind-then-print. `eija serve` validates the port and binds `127.0.0.1:<port>` before it builds the studio, so a bad or busy port (`CONFIGURATION`, `PORT_IN_USE`) leaves no workspace behind and prints no link. The socket is already listening when the browser opens, so the old "refresh if necessary" race is gone too.

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

* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
* [ADR-0229: Kernel-graded intent evals, and an OpenAI Responses API provider](/adrs/0229-kernel-graded-intent-evals-and-openai-provider.md) - PlayIDE's pitch is that AI may propose a change and the kernel decides what it means.
* [ADR-0236: Hostile input at PlayIDE's edges, and the cost of a plan at the model's limits](/adrs/0236-hostile-input-and-plan-cost.md) - Robustness is PlayIDE's stated edge over other UML tools.
<!-- okf:generated:end links -->
