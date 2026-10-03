---
type: Module
title: adapters.repository_changes
description: Read-only, bounded comparison of two local Git commits.
resource: repo://src/eija_studio/adapters/repository_changes.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository_changes.py
  title: adapters/repository_changes.py
  hash_method: ast-api-v1
  sha256: 3a24140d5a5dfb9a686dddf23bb1e403caca7076eaef4c8138a1684d9bff94c1
notes_baseline: 94754f81c3290efd123de132d4c76cc8d9f118131289a6b36f63af784d7097e8
verified:
- by: process:codex-immutable-code-review
  at: '2026-10-02T13:58:00Z'
  notes_sha256: 9a52c81660d3fc1e7519e5699445baaf25ed1bff48e86beed3c7add5546a2d64
  sources_sha256: 80bc47c7c66fbfc877beddd9ad7dc72bdd6f6da1f59e9891a03e0bc415c9e966
- by: process:codex-immutable-code-review
  at: '2026-10-02T13:59:50Z'
  notes_sha256: 9a52c81660d3fc1e7519e5699445baaf25ed1bff48e86beed3c7add5546a2d64
  sources_sha256: 80bc47c7c66fbfc877beddd9ad7dc72bdd6f6da1f59e9891a03e0bc415c9e966
- by: process:codex-comparison-cohesion
  at: '2026-10-02T15:11:05Z'
  notes_sha256: 74be488c29d0a2f309aa878d205e7109ba204b60261ae14883735dfde0a47a05
  sources_sha256: 94754f81c3290efd123de132d4c76cc8d9f118131289a6b36f63af784d7097e8
---

# adapters.repository_changes

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository_changes.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Read-only, bounded comparison of two local Git commits.

This adapter coordinates capture, revalidation and optional retention. Captured
syntax/impact, snapshot projection and cache eligibility have separate owners.
Git supplies immutable blobs and the diff; compared code is never executed.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/repository_analysis`](/modules/adapters/repository_analysis.md)
* [`adapters/repository_capture`](/modules/adapters/repository_capture.md)
* [`adapters/repository_change_cache`](/modules/adapters/repository_change_cache.md)
* [`adapters/repository_change_snapshot`](/modules/adapters/repository_change_snapshot.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

Comparison and file detail are separate read-only operations over exact local commits. Git supplies the diff; Python AST/Weave and the isolated optional JavaScript worker supply bounded syntax facts. Changed-source identity is not the live checkout source identity or a model evidence subject.

This module owns Git capture, policy revalidation and concurrent request ordering. `repository_analysis` adapts captured bytes to the existing Weave parsers and partial impact; `repository_change_snapshot` owns projections and bounded excerpts; `repository_change_cache` owns retention eligibility and prerequisite identity. Python reuses the existing parser and closure digests without a temporary-file extraction pass. These boundaries do not add a second semantic interpreter or change comparison authority.

Explicit comparison recaptures. Detail requests may reuse one byte-bounded defensive copy only after current repository, full changed-path ignore policy and extractor prerequisites are rechecked, including before return. Retention does not establish behavior or atomically lock external policy changes. Literal pathspecs prevent a filename from selecting neighboring diffs. Duplicate definitions and over-limit inventories cannot become guessed unique source selections; excerpts retain physical line endings and exact byte-derived identities.

<!-- okf:generated:begin links -->
## Imports

* [adapters.repository_analysis](/modules/adapters/repository_analysis.md) - Captured-byte syntax and partial impact adapted to existing Weave primitives.
* [adapters.repository_capture](/modules/adapters/repository_capture.md) - Bounded repository reads adapted to the existing deterministic Weave engine.
* [adapters.repository_change_cache](/modules/adapters/repository_change_cache.md) - Bounded retention eligibility and installed extractor prerequisite identity.
* [adapters.repository_change_snapshot](/modules/adapters/repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
