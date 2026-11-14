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
  sha256: 5621c17aa13e9b3bcbc8539d8bd057dfb39c6a7639abf1e03ee3291b081a8b0f
notes_baseline: ad6b6e768338596262b293fa112c53ae4f69927f5a73ae556073b5217d20f969
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
