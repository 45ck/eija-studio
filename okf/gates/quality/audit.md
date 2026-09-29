---
type: Quality Gate
title: nox -s audit
description: pip-audit of the measured runtime pins (requirements-tested.txt) against the PyPI advisory database.
resource: repo://quality/sessions/quality.py#audit
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#audit
  title: quality.py
  hash_method: ast-v2
  sha256: 4b2092c36f0468ba381dde52836aaa38e86635380d2408faa21ff4c0129f0db3
notes_baseline: 12fec04b7d47c52f0e023076f34ed6f465008362a6246680367472ee99ffd386
---

# nox -s audit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s audit` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#audit` |

## Docstring

~~~text
pip-audit of the measured runtime pins (requirements-tested.txt) against the PyPI advisory database.

Needs network. Without it the session reports NOT_RUN, never PASS: an unchecked tree is not a clean one.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
