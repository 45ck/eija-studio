---
type: Function
title: application.diagrams.commit_sequence
description: 'The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is checked BEFORE any replay lookup, then replay/operation binding, CAS on the instance version, state guard, state write,…'
resource: repo://src/eija_studio/application/diagrams.py#commit_sequence
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#commit_sequence
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: 34f72d79857af8b71e72309710601c415d813b5d83f2f98808f9875ec4265a77
notes_baseline: 72b09598f710adba09838022f9d680092be2425115d15d92995d51080530430a
---

# application.diagrams.commit_sequence

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def commit_sequence(workflow: Workflow, action: str) -> Sequence` |
| Code | `repo://src/eija_studio/application/diagrams.py#commit_sequence` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The commit protocol of one action, in the order `application.runtime.execute` runs it: authority is
checked BEFORE any replay lookup, then replay/operation binding, CAS on the instance version, state
guard, state write, audit and outbox effects, operation record, single commit.

Guards and effects come from the transition. The ORDER is hand-encoded here, not read from the runtime:
tests/test_diagrams.py replays the real `execute` through a recording unit of work and compares the call
order, so a reordering in the runtime fails that test, but the runtime source is never parsed. Effects are
listed audit first, then outbox, each sorted: their order inside the one transaction is non-semantic
(see `Workflow.semantic_hash`).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagrams.Sequence](/symbols/application/diagrams/Sequence.md) - `class Sequence` in `application/diagrams`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
