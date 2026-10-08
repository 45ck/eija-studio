---
type: Module
title: application.repository
description: Read-only repository evidence port; this does not grant project execution or approval.
resource: repo://src/eija_studio/application/repository.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py
  title: application/repository.py
  hash_method: ast-api-v1
  sha256: 15413f2b526cc49c643e636b322530936ee6fd9dd2dff6c378a7f96e8d57df10
notes_baseline: 01486c74f540138ddfa373422a79f17b78282f9d1106d4d564a0d97f385af0ee
verified:
- by: process:codex-query-cohesion
  at: '2026-10-03T10:00:00+11:00'
  notes_sha256: d3029bdffc47221bf39c0e157dbd4d9a3c63767ddf9622ccfb6a333f34e309d7
  sources_sha256: 01486c74f540138ddfa373422a79f17b78282f9d1106d4d564a0d97f385af0ee
- by: process:codex-query-cohesion
  at: '2026-10-02T20:26:56.4586414+00:00'
  notes_sha256: d3029bdffc47221bf39c0e157dbd4d9a3c63767ddf9622ccfb6a333f34e309d7
  sources_sha256: 01486c74f540138ddfa373422a79f17b78282f9d1106d4d564a0d97f385af0ee
---

# application.repository

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/repository.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Read-only repository evidence port; this does not grant project execution or approval.
~~~

## Public symbols

* [`COMMIT_OID_PATTERN`](/symbols/application/repository/COMMIT_OID_PATTERN.md) (constant) - no docstring
* [`RepositoryChangeSource`](/symbols/application/repository/RepositoryChangeSource.md) (class) - Immutable, read-only facts for an explicit pair in one configured repository.
* [`RepositorySource`](/symbols/application/repository/RepositorySource.md) (class) - Evidence about one explicitly configured checkout and its declared domain bindings.
* [`compare_repository_changes`](/symbols/application/repository/compare_repository_changes.md) (function) - Validate an immutable comparison request before dispatch to its read-only port.
* [`read_repository_change_file`](/symbols/application/repository/read_repository_change_file.md) (function) - Bound the historical selection before dispatch; absence never bypasses validation.
* [`read_repository_freshness`](/symbols/application/repository/read_repository_freshness.md) (function) - Observe captured byte identity; this grants no source conformance, evidence or owner authority.
* [`read_repository_impact`](/symbols/application/repository/read_repository_impact.md) (function) - Known repository links only.
* [`read_repository_source`](/symbols/application/repository/read_repository_source.md) (function) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
* [`unconfigured_repository`](/symbols/application/repository/unconfigured_repository.md) (function) - An absent connection is visible, never an empty successful extraction.
* [`unconfigured_repository_changes`](/symbols/application/repository/unconfigured_repository_changes.md) (function) - No comparison connection is not a successful empty code change.
* [`validate_change_revisions`](/symbols/application/repository/validate_change_revisions.md) (function) - Validate full object IDs before calling any configured repository port.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

Studio delegates its optional impact, source and freshness reads here, passing the
current injected repository port on each request. These helpers retain the
unconfigured response, captured source hash and underlying adapter refusals;
they do not access the Change Case store or infer behavior from source structure.
Replacing or removing the connection therefore affects the next query.

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
* [interfaces.mcp_server](/modules/interfaces/mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
* [application.repository.COMMIT_OID_PATTERN](/symbols/application/repository/COMMIT_OID_PATTERN.md) - Constant `COMMIT_OID_PATTERN` in `application/repository`.
* [application.repository.RepositoryChangeSource](/symbols/application/repository/RepositoryChangeSource.md) - Immutable, read-only facts for an explicit pair in one configured repository.
* [application.repository.RepositorySource](/symbols/application/repository/RepositorySource.md) - Evidence about one explicitly configured checkout and its declared domain bindings.
* [application.repository.compare_repository_changes](/symbols/application/repository/compare_repository_changes.md) - Validate an immutable comparison request before dispatch to its read-only port.
* [application.repository.read_repository_change_file](/symbols/application/repository/read_repository_change_file.md) - Bound the historical selection before dispatch; absence never bypasses validation.
* [application.repository.read_repository_freshness](/symbols/application/repository/read_repository_freshness.md) - Observe captured byte identity; this grants no source conformance, evidence or owner authority.
* [application.repository.read_repository_impact](/symbols/application/repository/read_repository_impact.md) - Known repository links only.
* [application.repository.read_repository_source](/symbols/application/repository/read_repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
* [application.repository.unconfigured_repository](/symbols/application/repository/unconfigured_repository.md) - An absent connection is visible, never an empty successful extraction.
* [application.repository.unconfigured_repository_changes](/symbols/application/repository/unconfigured_repository_changes.md) - No comparison connection is not a successful empty code change.
* [application.repository.validate_change_revisions](/symbols/application/repository/validate_change_revisions.md) - Validate full object IDs before calling any configured repository port.
<!-- okf:generated:end links -->
