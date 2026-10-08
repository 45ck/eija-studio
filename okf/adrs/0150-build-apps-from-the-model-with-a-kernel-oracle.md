---
type: Architecture Decision Record
title: 'ADR-0150: Build runnable apps from the model, checked against the kernel as oracle'
description: The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
resource: repo://docs/adr/0150-build-apps-from-the-model-with-a-kernel-oracle.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0150-build-apps-from-the-model-with-a-kernel-oracle.md
  title: 0150-build-apps-from-the-model-with-a-kernel-oracle.md
  hash_method: lf-sha256-v1
  sha256: da2e47aac84acdad3f801de76dfb75f34318c17839e07266ef7ada81f1fc3376
notes_baseline: 9459574f530cf4e899d4c7789af25743ea0e1c0fc0de00893b9b2009c529703f
---

# ADR-0150: Build runnable apps from the model, checked against the kernel as oracle

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted for the local workflow-app slice |
| Date | 2026-10-08 |
| Lane | app generation (owner direction, 8 October 2026) |
| Source | `repo://docs/adr/0150-build-apps-from-the-model-with-a-kernel-oracle.md` |

## Decision outcome (verbatim)

> Chosen option: a fixed runtime template plus generated spec and oracle.
>
> `eija build --pack P [--workflow F] --out DIR` writes these files:
>
> * `app/spec.py`: the model as plain Python literals, readable next to the diagram.
> * `app/service.py`, `app/server.py`, `app/web/*`, `run.py`: the fixed runtime. It runs the same checks in the same order as the kernel: record, action, actor, authority, replay, version, state, then the declared effects in one SQLite transaction.
> * `tests/oracle.json`: for every state, every action (plus one undeclared action), every fixture actor (plus one unknown actor) and expected versions 0 and 1, the kernel's own answer. Committed cases also record the answer to an exact replay.
> * `tests/test_conformance.py`: replays every oracle case against the generated service, and checks that each committed effect is written exactly once.
> * `BUILD.json`: pack and model identity, the oracle hash and case count, the hash of every file, the conformance result (`PASS`, `FAIL` or `NOT_RUN` with `--no-test`), and whether the kernel source matches the owner-stamped fixture (`kernel_source_review`).
>
> The build runs the generated tests in a separate process, the way a user of the app would, and exits 2 on `FAIL`. Negative controls in `tests/test_appgen.py` mutate five rules in a generated app and require the conformance run to fail for each. The rules are the assignment guard, the role check, the version check, an effect write and a role in the spec.
>
> The generator is pure (`application/appgen.py`). Writing files, reading templates and running the tests live in `interfaces/app_build.py`. A non-empty output directory is written only if it holds a previous build's `BUILD.json`. A rebuild replaces only the files that build listed, so `data/` survives.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_appgen.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
