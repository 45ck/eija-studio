---
type: Quality Gate
title: nox -s demos_dry
description: Every non-blocked scenario still works against the real Studio (no video).
resource: repo://quality/sessions/demos.py#demos_dry
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/demos.py#demos_dry
  title: demos.py
  hash_method: ast-v2
  sha256: f893b81771c1c2976d140f880d63b9e32dd9f8536bf2848b6b578f4189ad654b
notes_baseline: dd052355dbb2a4aed486070ad59352d548a5830f6efef06ef1f79ee45e6a9ad4
---

# nox -s demos_dry

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s demos_dry` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/demos.py` |
| Code | `repo://quality/sessions/demos.py#demos_dry` |

## Docstring

~~~text
Every non-blocked scenario still works against the real Studio (no video).

Reports NOT_RUN (the session is skipped, never passed) when Playwright is missing or the system
Chrome cannot be launched (`python -m demos` exits 3). A scenario failing while it runs is a failure.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
