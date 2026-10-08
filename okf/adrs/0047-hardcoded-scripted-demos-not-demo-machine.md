---
type: Architecture Decision Record
title: 'ADR-0047: Hand-authored scripted demo recordings, not demo-machine'
description: 'The owner wants live recordings — real cursor movement, real typing — that show a developer using EIJA Studio end to end: defining ubiquitous language into a DDD tree, drag-and-drop UML editing kept in sync with the exe…'
resource: repo://docs/adr/0047-hardcoded-scripted-demos-not-demo-machine.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0047-hardcoded-scripted-demos-not-demo-machine.md
  title: 0047-hardcoded-scripted-demos-not-demo-machine.md
  hash_method: lf-sha256-v1
  sha256: cdc0f6bc5629319411428c0f8bd139ecc4a0f71e7829fbd37d0639901e6f4e0b
notes_baseline: 72526f01b191002df073d6f84df878aa65049ac00f3ecc6f95ec6734d18a0fd7
---

# ADR-0047: Hand-authored scripted demo recordings, not demo-machine

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | demos |
| Source | `repo://docs/adr/0047-hardcoded-scripted-demos-not-demo-machine.md` |

## Decision outcome (verbatim)

> A hand-authored scripted recorder. It is still engineered with the same rigor as every other lane: typed, tested (a scenario can run "dry": the same real clicks, form input and assertions with video, overlay and delays skipped, so a gate can check a scenario still works as the UI changes), reviewed, and documented — not a one-off script kept outside version control. Cursor motion is a smoothstep-eased loop of Playwright `mouse.move` steps that also moves a synthetic on-page cursor (Chromium does not render the OS pointer into recorded video); typing is `locator.press_sequentially` one character at a time with a seeded random pause between characters (`time.sleep`; the seed fixes only the typing cadence, so recordings are not otherwise repeatable). Video is Playwright's built-in capture, run against the **installed system Google Chrome** (`channel="chrome"`), so no browser is downloaded. Playwright is **not** a dependency of the kernel and was not declared anywhere on `main` before this lane (`scripts/browser_*smoke.py` import it lazily when present); this lane adds `playwright==1.63.0` to the new optional `demos` extra. When Playwright is not installed or Chrome cannot be launched, the CLI reports `NOT_RUN` (exit 3), never a pass.

## Sections

* Context and problem statement
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.

## Referenced by

* [Demos: scripted live recordings, scenario dependency gating](/lanes/0047-demos-scripted-live-recordings-scenario.md) - Capability lane with ADR numbers 0047–0048 reserved.
<!-- okf:generated:end links -->
