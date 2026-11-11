---
type: Architecture Decision Record
title: 'ADR-0233: Separation of duties'
description: 'Issue #149.'
resource: repo://docs/adr/0233-separation-of-duties.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0233-separation-of-duties.md
  title: 0233-separation-of-duties.md
  hash_method: lf-sha256-v1
  sha256: 8a2e89bcf4a962d97a6f6c05082a312860a79a3c3cbae3695db3334d23b6c87b
notes_baseline: ec9b461ad6f807713e639e60b0cedae18af624485a01e45b4808f51850a46f3f
---

# ADR-0233: Separation of duties

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-11 |
| Lane | kernel / laws |
| Source | `repo://docs/adr/0233-separation-of-duties.md` |

## Decision outcome (verbatim)

> **The law.** `{"kind": "distinct_actors", "actions": [two to eight actions]}`: on one record, no single actor takes two different actions of the list. The same action repeated (a resubmission) is allowed. Its references are checked like every other law's. The table cannot break it, so `check_policy` never reports it.
>
> **The runtime.** After the state check, `runtime.execute` looks up the separation laws in force that name the action. Only when there is one does it read the record's act log (`UnitOfWork.acts`) and refuse an actor who already took another listed action with `SEPARATION_DENIED`, naming the law's code and `law:<id>` in the details. On commit it appends `(action, actor)` to the log (`record_act`) in the same unit of work. Packs without the law never touch the log. A replay is still answered from the operation record. The SQLite store and the generated app each gain an additive `acts` table; no schema version changes.
>
> **The proof.** The law proof's actor classes cannot tell two actors of a role apart, so `distinct_actors` is judged by asking the kernel: wherever one listed action directly follows another on a reachable record, one actor takes the first, is given the role of the second and tries it, and must be refused; a different actor must not be refused for separation. No such place is reported as VACUOUS. `evaluate_run` also judges runs whose steps record their actor. The SMT encoding lists it as not encoded.
>
> **The generated app.** The oracle gains `separation_cases` (only when the pack has the law, so other oracles keep their bytes): a fixture actor takes one listed action, then the next, and the kernel's answer. The conformance template checks them, so it now runs eight tests. The app's action options use the same check, so a refused action shows as not allowed.

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
