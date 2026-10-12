---
type: Method
title: application.service_views.StudioViews.repository_source
description: Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
resource: repo://src/eija_studio/application/service_views.py#StudioViews.repository_source
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service_views.py#StudioViews.repository_source
  title: application/service_views.py
  hash_method: ast-v2
  sha256: 9b8fcc69e509097d8716810d8434a41931c94af5e0bc87afbb3fc3be4266a978
notes_baseline: 53934a513860c0d8c5c978dd2c4cb9373efc51a92ac50d13c5ce7df447a83888
---

# application.service_views.StudioViews.repository_source

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service_views`](/modules/application/service_views.md) |
| Class | [`StudioViews`](/symbols/application/service_views/StudioViews.md) |
| Signature | `def repository_source(self, reference: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service_views.py#StudioViews.repository_source` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.read_repository_source](/symbols/application/repository/read_repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
<!-- okf:generated:end links -->
