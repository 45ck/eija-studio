---
type: Quality Gate
title: nox -s browser_suite
description: Every `slow` or `browser` test outside tests/metrics, with EIJA_BROWSER_TESTS=1.
resource: repo://quality/sessions/browser.py#browser_suite
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/browser.py#browser_suite
  title: browser.py
  hash_method: ast-v2
  sha256: e1df2d300f0fe5df805190e1d7f8f3515121578e1b308755d1a60c1de2d40468
notes_baseline: 048fb9144891326245475e733e682508465508b02f4a344dd33566bec33ce558
---

# nox -s browser_suite

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s browser_suite` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/browser.py` |
| Code | `repo://quality/sessions/browser.py#browser_suite` |

## Docstring

~~~text
Every `slow` or `browser` test outside tests/metrics, with EIJA_BROWSER_TESTS=1.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
