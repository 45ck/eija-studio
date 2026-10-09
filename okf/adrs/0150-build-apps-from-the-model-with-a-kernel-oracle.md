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
  sha256: a53ece1770935ac2ef86ae93394c6076d85f7fc153d4208cec3622092fdbcfd4
notes_baseline: f2d816c4e5565bab466cd95d6f9ec6432d250da292ad294537320c41a8e61b88
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

> Chosen option: a fixed storage template that calls the kernel, plus the canonical model, pack and oracle.
>
> `eija build --pack P [--workflow F] --out DIR` writes these files:
>
> * `app/model.json` and `app/pack.json`: the canonical workflow model and pack the app was built from.
> * `app/service.py`: a SQLite unit of work implementing the kernel's session port. `create` calls `runtime.initialise` and `act` calls `runtime.execute`, each in one `BEGIN IMMEDIATE` transaction. The app holds no rules of its own.
> * `app/server.py`, `app/web/*`, `run.py`: a local HTTP API and page over that service.
> * `tests/oracle.json`: for every state, every action (plus one undeclared action), every fixture actor (plus one unknown actor) and expected versions 0 and 1, the kernel's own answer. Committed cases also record the answer to an exact replay.
> * `tests/test_conformance.py`: replays every oracle case against the generated service, and checks that each committed effect is written exactly once.
> * `BUILD.json`: pack and model identity, the oracle hash and case count, the hash of every file, the conformance result (`PASS`, `FAIL` or `NOT_RUN` with `--no-test`), and whether the kernel source matches the owner-stamped fixture (`kernel_source_review`).
>
> The build runs the generated tests in a separate process, the way a user of the app would, and exits 2 on `FAIL`. Negative controls in `tests/test_appgen.py` break a generated app five ways and require the conformance run to fail for each: operations not recorded (so replays are not idempotent), audit effects not written, notifications not queued, an approval role changed in `app/model.json`, and an unassigned actor marked assigned in `app/pack.json`. The `appgen` nox session (tags full and release) builds all three packs and fails if any build fails.
>
> The generator is pure (`application/appgen.py`). It refuses a `--workflow` whose id differs from the pack's (`WORKFLOW_PACK_MISMATCH`), and the oracle's negative sentinels are chosen so they never collide with a declared action or actor. Writing files, reading templates and running the tests live in `interfaces/app_build.py`. A non-empty output directory is written only if it holds a previous build's `BUILD.json` of this format and every file present is one that build listed (`data/` and `__pycache__/` aside). A rebuild replaces only those files, so `data/` survives.

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
## Referenced by

* [ADR-0151: PlayIDE canvas with Build & run of the live app](/adrs/0151-playide-canvas-and-build-and-run.md) - The owner wants EIJA to feel like "UML you can trust to build apps": a visual, mouse-driven IDE (named PlayIDE) where a UML-literate engineer designs a system…
* [ADR-0153: Data models as UML class diagrams, checked in the built app](/adrs/0153-data-models-as-uml-class-diagrams.md) - Until now, records in a built app (ADR-0150) carried only a title, because the model had no data.
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0205: The class diagram says what is drawn and what is built](/adrs/0205-the-class-diagram-says-what-is-drawn-and-what-is-built.md) - The built app stores records of the record class only (ADR-0150, ADR-0153).
* [ADR-0207: Each built app's API contract, written from the model](/adrs/0207-each-built-apps-api-contract-written-from-the-model.md) - The System lens (ADR-0203) draws each workflow's provided interface as its actions.
<!-- okf:generated:end links -->
