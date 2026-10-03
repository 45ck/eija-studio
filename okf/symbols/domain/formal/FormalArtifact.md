---
type: Class
title: domain.formal.FormalArtifact
description: One raw formal artifact from a tool report.
resource: repo://src/eija_studio/domain/formal.py#FormalArtifact
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#FormalArtifact
  title: domain/formal.py
  hash_method: ast-sig-v1
  sha256: 3d85f3c700d865c24c6c13976cbd16562b5cda1dc2c39504db61ab6a524170f3
notes_baseline: 9eae750ffa6f9727cb08d68d74d3da1bb93463f8e790a587039f4eedf872f1c4
---

# domain.formal.FormalArtifact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `class FormalArtifact` |
| Code | `repo://src/eija_studio/domain/formal.py#FormalArtifact` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One raw formal artifact from a tool report. ``artifact`` is hashed; ``measurements`` (platform, timings)
are recorded beside it and never hashed. The adapter copies what the tool said and computes no verdict.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `str` |  |
| `artifact` | `dict[str, Any]` |  |
| `measurements` | `dict[str, Any]` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.formal.for_pack](/symbols/application/formal/for_pack.md) - Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
<!-- okf:generated:end links -->
