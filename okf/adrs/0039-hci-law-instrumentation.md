---
type: Architecture Decision Record
title: 'ADR-0039: Apply HCI laws to the Studio UI with Playwright, axe-core and pure formula modules'
description: The Studio UI is the owner's only instrument for reviewing an AI-proposed change, yet its usability claims are unmeasured.
resource: repo://docs/adr/0039-hci-law-instrumentation.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0039-hci-law-instrumentation.md
  title: 0039-hci-law-instrumentation.md
  hash_method: lf-sha256-v1
  sha256: c9c830f144e1e82fc69870b50212a3940db13a23617d2358afd72ed4fc8ee8a3
notes_baseline: dbf10692617e659e117ca5d652c296ff94fb5479008662d21dc6ac39bb84e4de
---

# ADR-0039: Apply HCI laws to the Studio UI with Playwright, axe-core and pure formula modules

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | hci |
| Source | `repo://docs/adr/0039-hci-law-instrumentation.md` |

## Decision outcome (verbatim)

> Chosen option: Playwright + axe-playwright-python, because both are mature, permissively licensed, cross-platform, drive real Chrome via `channel="chrome"` without a browser download, and the injection of the observer as a CDP init script leaves the Studio's CSP intact.
>
> * `quality/hci/laws.py` and `wcag.py` are pure, cited, configurable formulas (no I/O).
> * `quality/hci/probe.js` only observes (geometry, choice counts, focus, click -> DOM-update timing); a unit test forbids mutating calls in it.
> * `quality/hci/journey.py` holds the canonical owner journey as data plus one driver for pointer and keyboard-only runs. The pointer moves to and clicks the exact landing point that Fitts's D is computed from, after verifying nothing covers it.
> * `analysis.py`, `recommend.py`, `report.py` turn traces into metrics, deterministic ranked recommendations, a canonical `report.json` and a `REPORT.md` that is a pure function of that JSON.
> * Fitts constants are MacKenzie & Buxton (1992) mouse, smaller-of, Shannon (`230 + 166 * ID` ms), checked against the paper's text. Hick `b = 0.150 s/bit` and the KLM operator times are attributed to Card, Moran & Newell but were taken from secondary sources and NOT re-checked against the primary text. All are labelled population averages.
> * Fitts's `D` lands at the centre of the effective box (overstating D for wide targets); a nearest-edge variant is reported so flagged-move counts are a range. Doherty "first feedback" is the first DOM mutation (a JavaScript-task latency excluding paint), labelled as such.
> * Recommendations state only what the metrics show; any guess about the UI code or the server goes in an explicitly UNVERIFIED `likely_cause`, and a saving that is an upper bound is labelled so and never breaks ranking ties.
> * The working-memory figure is explicitly a visibility proxy, not a memory measurement.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://quality/hci/journey.py`
* `repo://quality/hci/laws.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.

## Referenced by

* [HCI laws and usability instrumentation](/lanes/0039-hci-laws-and-usability-instrumentation.md) - Capability lane with ADR numbers 0039–0040 reserved.
<!-- okf:generated:end links -->
