---
type: Quality Gate
title: nox -s okf
description: OKF v0.2 conformance, links, code-link hashes (STALE, NOTES_STALE), coverage and generator drift.
resource: repo://quality/sessions/okf.py#okf
tags:
- gate
- fast
- full
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/okf.py#okf
  title: okf.py
  hash_method: ast-v2
  sha256: c5d6d45e8ae01164f1e784e85c3bf89636acedc395aecec8af3161e3f91a4273
notes_baseline: c9b3cb428306837ce1baace99873f5bfeaaa7af3d988b31f15dff548cd76ed4b
verified:
- by: process:deeper-test-pass
  at: '2026-11-17T01:30:00Z'
  notes_sha256: 34e38738ead699a87dec889f1c5bc16804d71221212ba6b43bf4f26b86816ac2
  sources_sha256: c9b3cb428306837ce1baace99873f5bfeaaa7af3d988b31f15dff548cd76ed4b
---

# nox -s okf

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s okf` |
| Tiers | `fast`, `full`, `release` |
| Session module | `repo://quality/sessions/okf.py` |
| Code | `repo://quality/sessions/okf.py#okf` |

## Docstring

~~~text
OKF v0.2 conformance, links, code-link hashes (STALE, NOTES_STALE), coverage and generator drift.

Integration gate: it is red for anyone whose change moved a linked source until `python -m quality.okf sync`
is run and the pages listed as STALE / NOTES_STALE are re-read and `review`ed (AGENTS.md, Capability lanes).
A PASS establishes that the wiki is well-formed and baselined against today's code, and that hand-written Notes
were re-read since their source last changed; it does not establish that any page's prose is correct. Missing
tooling reports NOT_RUN (a skipped session), never PASS.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

Same findings without the pytest step: `python -m quality.okf check`. How the checks work and which are stricter than the specification: `repo://docs/knowledge-base.md`.

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
