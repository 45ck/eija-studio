---
type: Class
title: domain.formal.Findings
description: Collects reasons by severity.
resource: repo://src/eija_studio/domain/formal.py#Findings
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#Findings
  title: domain/formal.py
  hash_method: ast-sig-v1
  sha256: c767476f4508671a3b3f1134a08c179660536240547c318d8996bdc5cce340f9
notes_baseline: a71181aecfc3d4a72f56f73a1f9c86f120b60214f53c5cdb3023cd59d2262a17
---

# domain.formal.Findings

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `class Findings` |
| Code | `repo://src/eija_studio/domain/formal.py#Findings` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Collects reasons by severity. Priority: STALE (about another subject), FAIL, UNKNOWN, else PASS.
~~~

## Methods

* [`fail`](/symbols/domain/formal/Findings.fail.md) - `def fail(self, why: str) -> None`
* [`result`](/symbols/domain/formal/Findings.result.md) - `def result(self) -> Assessment`
* [`stale`](/symbols/domain/formal/Findings.stale.md) - `def stale(self, why: str) -> None`
* [`unknown`](/symbols/domain/formal/Findings.unknown.md) - `def unknown(self, why: str) -> None`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Assessment](/symbols/domain/formal/Assessment.md) - `class Assessment` in `domain/formal`.

## Referenced by

* [domain.formal.Findings.fail](/symbols/domain/formal/Findings.fail.md) - `def fail(self, why: str) -> None` in `domain/formal`.
* [domain.formal.Findings.result](/symbols/domain/formal/Findings.result.md) - `def result(self) -> Assessment` in `domain/formal`.
* [domain.formal.Findings.stale](/symbols/domain/formal/Findings.stale.md) - `def stale(self, why: str) -> None` in `domain/formal`.
* [domain.formal.Findings.unknown](/symbols/domain/formal/Findings.unknown.md) - `def unknown(self, why: str) -> None` in `domain/formal`.
* [domain.formal.reported_labels](/symbols/domain/formal/reported_labels.md) - The tool's own verdict and check labels may LOWER the status, never raise it.
* [domain.formal.source_binding](/symbols/domain/formal/source_binding.md) - Producer sources named by the tool's report versus the bytes the adapter observes now.
* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
