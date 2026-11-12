---
type: Architecture Decision Record
title: 'ADR-0236: Hostile input at PlayIDE''s edges, and the cost of a plan at the model''s limits'
description: Robustness is PlayIDE's stated edge over other UML tools.
resource: repo://docs/adr/0236-hostile-input-and-plan-cost.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0236-hostile-input-and-plan-cost.md
  title: 0236-hostile-input-and-plan-cost.md
  hash_method: lf-sha256-v1
  sha256: 5c03eaef47a04f3485ef8ba2dbc3e7e798e7e715d613ecaf574cda5cf47ae33d
notes_baseline: c6da107d2b359ef32544a852ef0de0ca5b93415ed6be0bb3888d0329e4cf1d24
---

# ADR-0236: Hostile input at PlayIDE's edges, and the cost of a plan at the model's limits

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | robustness (UML interchange, command line, autosave, plan mode) |
| Source | `repo://docs/adr/0236-hostile-input-and-plan-cost.md` |

## Decision outcome (verbatim)

> **UML readers.** An escape that names no character is kept as written. A count of more than 18 digits is read as
> 10^18, which every limit refuses as it would the number itself. An XMI bound must be ASCII digits. A draw.io
> position that is unreadable or infinite counts as 0: it only orders what was drawn. `interop.model` holds the
> helpers (`whole`, `is_count`, `character`).
>
> **Command line.** `failure_report` names what is wrong: `FILE_NOT_FOUND` and `NOT_A_FILE` (with the path the person
> gave), `PERMISSION_DENIED`, `NOT_UTF8` (with the byte offset), `INVALID_JSON` (with line and column),
> `SCHEMA_INVALID` (with each field and problem, never the value) and `INPUT_TOO_DEEP`. `check-export` refuses a file
> that is not a JSON object.
>
> **Autosave.** The page reopens a browser draft only when its shape is the one it writes. Any other draft is moved to
> `<key>:unreadable` and the page opens on the model in force, with a note. If a draft passes the shape check and still
> fails to reopen, the page sets it aside and opens anyway. On disk, `GET /api/play/draft` checks `draft.json` against
> `SavedWork`; one in another shape is moved to `draft.unreadable.json` and the page says so.
>
> **Plan check.** `_statuses` keeps the model after the steps that applied so far (`plan._Applied`), so each step is
> applied once. A 64-step plan at the limits now takes about 70 ms. The verdicts match a replay of every earlier step
> on 400 seeded random plans in the fast tests (8,000 in the fuzzing pass), and a test counts the applications.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
