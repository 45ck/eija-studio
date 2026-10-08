---
type: Architecture Decision Record
title: 'ADR-0191: PlayIDE at the kernel''s limits: measured, and the kernel''s repeated questions memoised'
description: The packs PlayIDE was built and demonstrated on have five or six states.
resource: repo://docs/adr/0191-playide-at-the-kernel-limits.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0191-playide-at-the-kernel-limits.md
  title: 0191-playide-at-the-kernel-limits.md
  hash_method: lf-sha256-v1
  sha256: a2f4e680cf9211ef6f4999807492646a4bc458a8f27e487da773a3ac941129c5
notes_baseline: 9ddf6c968e81e178394f8b5797b78709cac228df6b185a89f8b9e6f341cbba89
---

# ADR-0191: PlayIDE at the kernel's limits: measured, and the kernel's repeated questions memoised

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-10-08 |
| Lane | PlayIDE (owner direction, 8 October 2026: stay fast on large models) |
| Source | `repo://docs/adr/0191-playide-at-the-kernel-limits.md` |

## Decision outcome (verbatim)

> * **Where the time went.** Profiling (cProfile) showed that building the app's oracle and proving the laws each run the kernel tens of thousands of times on one unchanged model, and every run checked the whole model against the policy again (`ensure_policy`) and hashed it again (`Workflow.semantic_hash`). Those two were over 95 % of the time.
> * **`application/memo.py`** keeps the answers in front of the kernel, not inside it: `runtime.execute` asks `ensure_conforms(model, pack, ensure_policy)` and `model_hash(model)` instead of calling the policy check and the hash directly, and the oracle and proof sessions use `model_hash` too. An `IdentityMemo` keeps the last 128 answers, keyed by the objects' identity. A `Workflow` and a `Pack` are frozen after validation, so the same objects always get the same answer; the memo holds the objects themselves, so an id cannot be reused for another object while its entry exists. A copy or an edit is a new object and is asked afresh. Only a pass is remembered: a model the policy refuses is refused by `ensure_policy` itself every time, with its own codes and refs, and the check is part of the key, so a test that replaces it is asked afresh. The protected domain files (`domain/models.py`, `domain/policy.py`) and the SMT snapshot bound to their source are unchanged. `tests/test_kernel_memo.py` checks the answers against the kernel's own.
> * **The app is built once per version.** `interfaces/app_build.app_files` keeps the last eight builds by pack, exact model content (order included), data model digest and screens digest. The ripple builds the model in force beside the candidate on every edit, and the component diagram and Build & run build the candidate again; now each version is generated once. Callers get their own copies.
> * **The class diagram.** Every vertex is placed at a fixed size, so the page tells maxGraph not to measure each shape and attribute row with `getBBox` (`lean()` in `play.js`).

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_kernel_memo.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
