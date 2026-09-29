---
type: Function
title: domain.policy.meaning_options
description: 'The pack''s meanings as the review surface shows them: label, whether supported, consequences.'
resource: repo://src/eija_studio/domain/policy.py#meaning_options
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#meaning_options
  title: domain/policy.py
  hash_method: ast-v2
  sha256: c98a3d534f23b861b2012171e2276a7f0f31f484e090859bc6663d4400720800
notes_baseline: 2ab050b049f9e50ef817948547a65cebbf124b158d468f0dad904c4ea433e444
---

# domain.policy.meaning_options

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def meaning_options(pack: Pack \| None=None) -> dict[str, dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/policy.py#meaning_options` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's meanings as the review surface shows them: label, whether supported, consequences.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
