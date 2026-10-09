---
type: Architecture Decision Record
title: 'ADR-0208: Moments for real checks, and the run as traffic on the diagram'
description: ADR-0157 gave PlayIDE a checks ring and points that reward checking, never producing.
resource: repo://docs/adr/0208-check-moments-and-traffic.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0208-check-moments-and-traffic.md
  title: 0208-check-moments-and-traffic.md
  hash_method: lf-sha256-v1
  sha256: d805ebc68328ade059d4b1b1f92b68e18dceca5a1c98c64fa5e82488542721a6
notes_baseline: 24a13ee273c34f76671968d6f755ad6284498a58a78e6dd7782157c1237faa6b
---

# ADR-0208: Moments for real checks, and the run as traffic on the diagram

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-09 |
| Lane | PlayIDE (owner direction, 9 October 2026: PlayIDE should be "fun/gamified" while doing everything it needs to; the product vision is "City Skylines for software engineers") |
| Source | `repo://docs/adr/0208-check-moments-and-traffic.md` |

## Decision outcome (verbatim)

> Chosen option. `play.js` sends `playide:checks` (each check with a stable id: `ai`, `screens`, `conformance`, `ripple`, `simulated`), `playide:earn` (with a `caught` kind for a step the policy caught), `playide:simulated` and, during Replay, `playide:step`. The run bar sends `playide:step` for each single step forward; a jump straight to the next stop draws no traffic for the steps it skips. `play-game.js` listens:
>
> * **A check passes.** Its ring part pops, and a note rises under the ring: "✓ Conformance. PASS: 373 cases checked against the kernel".
> * **Every check passes on the view.** The ring turns green with one pulse, and the note says "Every check passes on this model" (or "on this change"). This happens once for each view, and never on page load.
> * **A change makes a build or simulation stale.** The ring flashes amber, and the note says "Changed since the last build and simulation: run them again". **Build & run** and **Simulate** glow until they are run. A button glows only for a check that passed earlier in this page, so a fresh page does not nag.
> * **The next check.** The checks panel opens with "Next:" and names the first failing check, with the page's own button where there is one ("Build & run", "Simulate", "Open Screens"). Once every check passes, it says "Ready."
> * **Caught it.** When unticking an AI step turns a refused plan into one the policy allows (+3, ADR-0157), the note is larger and amber with a shield, and the plan's card pulses.
> * **Traffic.** For each step the kernel decided in the run bar or in Replay, a dot travels along the drawn transition, green when the step went through and blue when a record is created. A refused step stops halfway with a red cross. A try from a state the transition does not leave flashes that state in red. After Simulate, the run's first 120 steps go by in about four seconds as overlapping traffic, and the summary counts count up. The traffic stops if the simulation is cleared or the view changes, so a dot is never drawn on a model it was not run on. These are the real log, sped up.

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

* [ADR-0157: Drawn edits join the plan, and a checks ring rewards checking](/adrs/0157-drawn-edits-and-checks-ring.md) - The owner wants PlayIDE to be visual and mouse-driven ("drag and drop, design then test in place") and to feel rewarding, "tied to real checks".
<!-- okf:generated:end links -->
