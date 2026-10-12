---
type: Method
title: application.service.Studio.propose_edit
description: Read-only offline proposal; capture and recheck the case revision without granting owner authority.
resource: repo://src/eija_studio/application/service.py#Studio.propose_edit
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.propose_edit
  title: application/service.py
  hash_method: ast-v2
  sha256: d397b12bf76061ef2ae1c8ecbe61e32828654a6cdac27f1cd2c851c521752919
notes_baseline: 6ee688ee4e2ebe73134a5fe096dd10df8c505cf419ff137e8048061fde892c1a
verified:
- by: process:codex-packaging-integration
  at: '2026-10-03T03:27:08Z'
  notes_sha256: 9d258fe3d227cc4e4eaec720c29d66a59452e5947ac0ec21d70b0d6db702cf89
  sources_sha256: abc9539ecd2451158023cc04e7f201d62088fbcbc203b4dc93603a31dcaa53fc
- by: process:playide-exact-app
  at: '2026-10-11T09:17:31Z'
  notes_sha256: 9d258fe3d227cc4e4eaec720c29d66a59452e5947ac0ec21d70b0d6db702cf89
  sources_sha256: 6ee688ee4e2ebe73134a5fe096dd10df8c505cf419ff137e8048061fde892c1a
---

# application.service.Studio.propose_edit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def propose_edit(self, case_id: str, expected: int, request: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.propose_edit` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Read-only offline proposal; capture and recheck the case revision without granting owner authority.
~~~
<!-- okf:generated:end facts -->

## Notes

The service captures an editable case at the expected version, delegates proposal
availability and validation to `application.edit_proposal.propose_edit`, then rechecks
the same expected version. The optional-port check moved into that helper without
adding persistence, evidence or owner authority. A later owner edit still repeats
its own version and capability checks.

<!-- okf:generated:begin links -->
## Depends on

* [application.edit_proposal.propose_edit](/symbols/application/edit_proposal/propose_edit.md) - No persistence or evidence: resolve one request, then use the existing policy-checked projection.
<!-- okf:generated:end links -->
