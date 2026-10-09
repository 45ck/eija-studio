---
type: Constant
title: domain.data.DATA_FILE
description: Constant `DATA_FILE` in `domain/data`.
resource: repo://src/eija_studio/domain/data.py#DATA_FILE
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#DATA_FILE
  title: domain/data.py
  hash_method: ast-v2
  sha256: bf305d9a8e4bc4ec8a3c2417fa338e3ef8113a1f7f6c5a827355b3c4cacfe56a
notes_baseline: 1dd10da33d208ae6607f2ee39f52f3533fc5c3ca510a2624c61e787fcaef9a2c
---

# domain.data.DATA_FILE

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `DATA_FILE = 'data.json'` |
| Code | `repo://src/eija_studio/domain/data.py#DATA_FILE` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
<!-- okf:generated:end links -->
