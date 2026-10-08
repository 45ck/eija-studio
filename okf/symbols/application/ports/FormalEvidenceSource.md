---
type: Class
title: application.ports.FormalEvidenceSource
description: Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
resource: repo://src/eija_studio/application/ports.py#FormalEvidenceSource
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#FormalEvidenceSource
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: f3cabd15fddf7ea206490a37fee0d42a3e2819bea3c9becaefce15858c72670a
notes_baseline: aaf47111cf21be6b9afe11b279e0450ee879005b46e3f0e73027b145b161c2c3
---

# application.ports.FormalEvidenceSource

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class FormalEvidenceSource(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#FormalEvidenceSource` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).

A missing prerequisite is returned as a NOT_RUN artifact, never omitted and never a pass.
~~~

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def collect(self, baseline: Workflow, candidate: Workflow) -> list[FormalArtifact]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.FormalArtifact](/symbols/domain/formal/FormalArtifact.md) - One raw formal artifact from a tool report.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
