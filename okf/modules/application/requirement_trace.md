---
type: Module
title: application.requirement_trace
description: A bounded declared trace adapter, separate from policy and verification execution.
resource: repo://src/eija_studio/application/requirement_trace.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/requirement_trace.py
  title: application/requirement_trace.py
  hash_method: ast-api-v1
  sha256: 595655a93e2822a4609da999757ed3be92f25f9b83579eaea6aa9a47684dd9a7
notes_baseline: ee62f258498c9257e3e45c35bac764106ba3dd6827ec24f128348711c79677c4
---

# application.requirement_trace

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/requirement_trace.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
A bounded declared trace adapter, separate from policy and verification execution.

Requirement hashes use the same canonical row shape as Weave's csv-row-v1.
No prose is parsed into rules, no source links are inferred, and no evidence is minted.
~~~

## Public symbols

* [`REQUIREMENT_PATH`](/symbols/application/requirement_trace/REQUIREMENT_PATH.md) (constant) - no docstring
* [`compare_requirements`](/symbols/application/requirement_trace/compare_requirements.md) (function) - Compare prose only for existing IDs.
* [`requirement_review`](/symbols/application/requirement_trace/requirement_review.md) (function) - Pinned requirement rows and declared model/law/source/test links with visible gaps.

## Internal imports

* [`application/law_proof`](/modules/application/law_proof.md)
* [`domain/laws`](/modules/domain/laws.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [domain.laws](/modules/domain/laws.md) - Typed law DSL of a domain pack: what a workflow may never do, stated as data (WBS 1.1/1.2).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.play_assurance](/modules/interfaces/play_assurance.md) - Read-only assurance review.
* [application.requirement_trace.REQUIREMENT_PATH](/symbols/application/requirement_trace/REQUIREMENT_PATH.md) - Constant `REQUIREMENT_PATH` in `application/requirement_trace`.
* [application.requirement_trace.compare_requirements](/symbols/application/requirement_trace/compare_requirements.md) - Compare prose only for existing IDs.
* [application.requirement_trace.requirement_review](/symbols/application/requirement_trace/requirement_review.md) - Pinned requirement rows and declared model/law/source/test links with visible gaps.
<!-- okf:generated:end links -->
