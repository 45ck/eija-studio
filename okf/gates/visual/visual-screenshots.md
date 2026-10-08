---
type: Quality Gate
title: nox -s visual_screenshots
description: Drive the real Studio in Chrome to the Visual view, assert no CSP violation, refresh docs/assets/*.png.
resource: repo://quality/sessions/visual.py#visual_screenshots
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/visual.py#visual_screenshots
  title: visual.py
  hash_method: ast-v2
  sha256: 6dbc3dbf3685c9da1c6525284cf55cd037543ed9f0a96510b2d6cea7f601f86e
notes_baseline: c0a3144542c7289c8b7fa1f9d087ffee75aac640e924612a411b0ddf1556fd4e
---

# nox -s visual_screenshots

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s visual_screenshots` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/visual.py` |
| Code | `repo://quality/sessions/visual.py#visual_screenshots` |

## Docstring

~~~text
Drive the real Studio in Chrome to the Visual view, assert no CSP violation, refresh docs/assets/*.png.
Exit code 3 means NOT_RUN (Chrome or Playwright missing): the session fails unless EIJA_ALLOW_NOT_RUN=1.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
