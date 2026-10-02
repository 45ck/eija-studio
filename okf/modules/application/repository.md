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
  sha256: ab346ef51f20a4d20e18a86afff0301521c2f7bf087b06f57539eaadeb89d73f
notes_baseline: 50e6cbba8402c9b23c1a4790b2b5fcd091505d6bdc34cf70883700eceb4cdd89
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
* [`unconfigured_repository`](/symbols/application/repository/unconfigured_repository.md) (function) - An absent connection is visible, never an empty successful extraction.
* [`unconfigured_repository_changes`](/symbols/application/repository/unconfigured_repository_changes.md) (function) - No comparison connection is not a successful empty code change.
* [`validate_change_revisions`](/symbols/application/repository/validate_change_revisions.md) (function) - Validate full object IDs before calling any configured repository port.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

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
* [application.repository.unconfigured_repository](/symbols/application/repository/unconfigured_repository.md) - An absent connection is visible, never an empty successful extraction.
* [application.repository.unconfigured_repository_changes](/symbols/application/repository/unconfigured_repository_changes.md) - No comparison connection is not a successful empty code change.
* [application.repository.validate_change_revisions](/symbols/application/repository/validate_change_revisions.md) - Validate full object IDs before calling any configured repository port.
<!-- okf:generated:end links -->
