---
type: Quality Gate
title: nox -s readme_diagram
description: The README's before/after state diagram equals a fresh render of domain.policy.
resource: repo://quality/sessions/oss.py#readme_diagram
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/oss.py#readme_diagram
  title: oss.py
  hash_method: ast-v2
  sha256: d1dc3e94cdcbe85ee8c5039d8ecc39b6cf8f6726dd3be371092391187671d5ec
notes_baseline: 6ad48ba2674918f012729b8bdc4b95ec2de49aa0d8569f605bcdbaaa11e5bd33
---

# nox -s readme_diagram

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s readme_diagram` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/oss.py` |
| Code | `repo://quality/sessions/oss.py#readme_diagram` |

## Docstring

~~~text
The README's before/after state diagram equals a fresh render of domain.policy.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
