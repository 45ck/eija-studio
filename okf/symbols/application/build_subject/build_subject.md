---
type: Function
title: application.build_subject.build_subject
description: Bind model, contracts, template bytes and measured implementation to one payload.
resource: repo://src/eija_studio/application/build_subject.py#build_subject
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/build_subject.py#build_subject
  title: application/build_subject.py
  hash_method: ast-v2
  sha256: cc0b8949fd778665453f1245c02665820616cd918ec7b77b00490fedc52c3ad8
notes_baseline: 6662bcc13ca971afc38110bc3d5d767538e970ba2eac6b2f8f37bcf3d018a806
---

# application.build_subject.build_subject

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/build_subject`](/modules/application/build_subject.md) |
| Signature | `def build_subject(files: dict[str, str], *, implementation_digest: str, template_paths: Iterable[str]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/build_subject.py#build_subject` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Bind model, contracts, template bytes and measured implementation to one payload.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.build_subject.FORMAT](/symbols/application/build_subject/FORMAT.md) - Constant `FORMAT` in `application/build_subject`.
* [application.build_subject.SUBJECT_FILE](/symbols/application/build_subject/SUBJECT_FILE.md) - Constant `SUBJECT_FILE` in `application/build_subject`.
* [application.build_subject.snapshot_contracts](/symbols/application/build_subject/snapshot_contracts.md) - Parse the very contracts the generated application will load.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [application.build_subject.checked_build_subject](/symbols/application/build_subject/checked_build_subject.md) - Check archived identity, optionally binding it to the installed runtime and prior snapshot.
<!-- okf:generated:end links -->
