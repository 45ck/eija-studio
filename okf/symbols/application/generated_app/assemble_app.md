---
type: Function
title: application.generated_app.assemble_app
description: One generator and snapshot identity for previews and approved artifacts.
resource: repo://src/eija_studio/application/generated_app.py#assemble_app
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/generated_app.py#assemble_app
  title: application/generated_app.py
  hash_method: ast-v2
  sha256: 8ea63111885ec7b325431231f24e541f8b6c5d9b3a2bf611879ad08e4f3c6560
notes_baseline: 0d3776cbaefe815d857d2e3ea26cdb9857695a360fd8ca64f793a20457a0dc54
---

# application.generated_app.assemble_app

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/generated_app`](/modules/application/generated_app.md) |
| Signature | `def assemble_app(pack: Pack, model: Workflow, data: DataModel \| None, screens: Screens, static: dict[str, str], implementation: str) -> tuple[dict[str, str], dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/generated_app.py#assemble_app` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One generator and snapshot identity for previews and approved artifacts.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.build_subject.SUBJECT_FILE](/symbols/application/build_subject/SUBJECT_FILE.md) - Constant `SUBJECT_FILE` in `application/build_subject`.
* [application.build_subject.build_subject](/symbols/application/build_subject/build_subject.md) - Bind model, contracts, template bytes and measured implementation to one payload.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.

## Referenced by

* [application.generated_app.review_snapshot](/symbols/application/generated_app/review_snapshot.md) - Derive canonical contracts and the review binding through the shared pure assembler.
<!-- okf:generated:end links -->
