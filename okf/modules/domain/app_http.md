---
type: Module
title: domain.app_http
description: The HTTP status a generated app answers each refusal code with (ADR-0250).
resource: repo://src/eija_studio/domain/app_http.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/app_http.py
  title: domain/app_http.py
  hash_method: ast-api-v1
  sha256: 9acdbe7f5d0a9ccbac6f79287e7eea17f9c4687843999a00daefbd62e8719f64
notes_baseline: 0882d85878c4129249880aef5cf75b10eb93e23e7bded3a5b6a6ad107d1c19e1
---

# domain.app_http

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/app_http.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The HTTP status a generated app answers each refusal code with (ADR-0250).

One table, read by the generated server (app/server.py) when it answers a refusal and by the API contract
(application/api_contract.py) when it documents one, so the two cannot drift apart. Every code the kernel, the data
model's checks or the generated app can refuse with is listed; a code that is not would be answered 409 by default and
documented nowhere, which the tests refuse.

Pure: no I/O.
~~~

## Public symbols

* [`REFUSALS`](/symbols/domain/app_http/REFUSALS.md) (constant) - no docstring
* [`STATUS`](/symbols/domain/app_http/STATUS.md) (constant) - no docstring
* [`status_of`](/symbols/domain/app_http/status_of.md) (function) - The status a refusal with this code is answered with; a code missing from the table is a conflict.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.api_contract](/modules/application/api_contract.md) - The API contract of an app built from a workflow (ADR-0207): an OpenAPI 3.1 document of what the generated server serves, written from the model, the pack and…
* [domain.app_http.REFUSALS](/symbols/domain/app_http/REFUSALS.md) - Constant `REFUSALS` in `domain/app_http`.
* [domain.app_http.STATUS](/symbols/domain/app_http/STATUS.md) - Constant `STATUS` in `domain/app_http`.
* [domain.app_http.status_of](/symbols/domain/app_http/status_of.md) - The status a refusal with this code is answered with; a code missing from the table is a conflict.
<!-- okf:generated:end links -->
