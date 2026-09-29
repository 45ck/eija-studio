---
type: Class
title: domain.formal.Malformed
description: The artifact does not have the declared typed shape (a structural defect, judged FAIL).
resource: repo://src/eija_studio/domain/formal.py#Malformed
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#Malformed
  title: domain/formal.py
  hash_method: ast-sig-v1
  sha256: 9043891f463befcbebc487c08aa97de3dedad4410aaf9d568f663b37de4f20f3
notes_baseline: 681e8e9ba1f7de490de59f0da9d1e34a17228d23955b1d44e6f7b1e339bae202
---

# domain.formal.Malformed

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `class Malformed(ValueError)` |
| Code | `repo://src/eija_studio/domain/formal.py#Malformed` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
The artifact does not have the declared typed shape (a structural defect, judged FAIL).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.formal.digest](/symbols/domain/formal/digest.md) - `def digest(container: Any, key: str, where: str) -> str` in `domain/formal`.
* [domain.formal.exact_keys](/symbols/domain/formal/exact_keys.md) - `def exact_keys(artifact: dict[str, Any], keys: frozenset[str]) -> None` in `domain/formal`.
* [domain.formal.field](/symbols/domain/formal/field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
* [domain.formal.not_run_reason](/symbols/domain/formal/not_run_reason.md) - A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS.
* [domain.formal.records](/symbols/domain/formal/records.md) - `def records(container: Any, key: str, where: str) -> list[dict[str, Any]]` in `domain/formal`.
* [domain.formal.strings](/symbols/domain/formal/strings.md) - `def strings(container: Any, key: str, where: str, minimum: int=1) -> list[str]` in `domain/formal`.
* [domain.formal.text](/symbols/domain/formal/text.md) - `def text(container: Any, key: str, where: str) -> str` in `domain/formal`.
<!-- okf:generated:end links -->
