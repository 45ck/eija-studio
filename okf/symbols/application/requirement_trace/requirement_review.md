---
type: Function
title: application.requirement_trace.requirement_review
description: Pinned requirement rows and declared model/law/source/test links with visible gaps.
resource: repo://src/eija_studio/application/requirement_trace.py#requirement_review
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/requirement_trace.py#requirement_review
  title: application/requirement_trace.py
  hash_method: ast-v2
  sha256: 8b19584c8838b0f6e86afbfc87cf205538f91a51a7310ea3c5cc84f60f475c4b
notes_baseline: 86efa48f6e3427078edd2e8b0d86df2f91312b5cfdb72d775dc7553f382da46f
---

# application.requirement_trace.requirement_review

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/requirement_trace`](/modules/application/requirement_trace.md) |
| Signature | `def requirement_review(pack: Pack, model: Workflow, snapshot: dict[str, Any], *, connection: dict[str, Any] \| None=None, drafts: Mapping[str, str] \| None=None, candidate_pack: Pack \| None=None, baseline: Workflow \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/requirement_trace.py#requirement_review` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Pinned requirement rows and declared model/law/source/test links with visible gaps.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.law_proof.compare_laws](/symbols/application/law_proof/compare_laws.md) - Which laws a draft adds, removes or changes.
* [application.requirement_trace.compare_requirements](/symbols/application/requirement_trace/compare_requirements.md) - Compare prose only for existing IDs.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
