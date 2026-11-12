---
type: Function
title: application.appgen.signal_cases
description: Each signal the model receives, delivered with valid record values, and the kernel's answer (a record started in the initial state), then the first one under a name it does not receive and from a sender it does not hear…
resource: repo://src/eija_studio/application/appgen.py#signal_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#signal_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: c93f581cbede4388b6dfd1431e53e9b527ac02d4e187ab197116ffe5b1aa05f7
notes_baseline: 18d0ea4e116ccab71302b1931b88bbac8ef3de4c592331ff6f90055a56118110
---

# application.appgen.signal_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def signal_cases(pack: Pack, model: Workflow, data: DataModel \| None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/appgen.py#signal_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Each signal the model receives, delivered with valid record values, and the kernel's answer (a record started in
the initial state), then the first one under a name it does not receive and from a sender it does not hear: both
refused (ADR-0242). Empty when the model receives none, so other oracles keep their exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_record`'s answer for each: a valid record, then each required value missing, each value of the wrong type, each text o…
* [application.oracle_session.absent](/symbols/application/oracle_session/absent.md) - A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one.
* [application.runtime.receive](/symbols/application/runtime/receive.md) - Start a record because another workflow of the system sent `signal` (issue #93 item 5, ADR-0242).
* [application.simulation.MemorySession](/symbols/application/simulation/MemorySession.md) - The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
