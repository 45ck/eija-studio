---
type: Constant
title: domain.models.LINK
description: Constant `LINK` in `domain/models`.
resource: repo://src/eija_studio/domain/models.py#LINK
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#LINK
  title: domain/models.py
  hash_method: ast-v2
  sha256: 4f0087c0f7eea2caf88e07422bf6f0cc0adbf8912c0687e165fc201a7f77d391
notes_baseline: 873673bda2dd40ac7e7b5491a5b3523faac739617cd5e64fae7b7f1edcfc7101
---

# domain.models.LINK

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `LINK = '^[a-z][a-zA-Z0-9_]{0,39}$'` |
| Code | `repo://src/eija_studio/domain/models.py#LINK` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.models.LinkedObject](/symbols/domain/models/LinkedObject.md) - The lifecycle of the object a record links to through a reference field, such as a deploy request's `target` service (issue #93 item 4, ADR-0241): a small stat…
* [domain.models.LinkedStep](/symbols/domain/models/LinkedStep.md) - What a transition does to an object the record links to, written ``target.lock`` (issue #93 item 4, ADR-0241): the object named by the record's `link` field ta…
<!-- okf:generated:end links -->
