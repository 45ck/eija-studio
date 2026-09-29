---
type: Method
title: application.service.Studio.formal_view
description: 'Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.'
resource: repo://src/eija_studio/application/service.py#Studio.formal_view
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.formal_view
  title: application/service.py
  hash_method: ast-v2
  sha256: 87789f9e0eb22f4de843785bbb1be798eadb7a5ccd3ab3e23096c87444e78474
notes_baseline: 7e46cbdaad52d681a7f0ae0a47c76cb81764cfad310a5f4f0eb35a8abf90847e
---

# application.service.Studio.formal_view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def formal_view(self, model: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.formal_view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.compiler.subject_for](/symbols/application/compiler/subject_for.md) - `def subject_for(model: Workflow, layout: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]` in `application/compiler`.
* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack's declared verifiers, so a ki…
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
<!-- okf:generated:end links -->
