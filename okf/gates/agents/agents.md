---
type: Quality Gate
title: nox -s agents
description: MCP tools/resources via the SDK's in-memory session and stdio start-up, plus the SDK-free static checks.
resource: repo://quality/sessions/agents.py#agents
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/agents.py#agents
  title: agents.py
  hash_method: ast-v2
  sha256: 8d3e462aef5a63d19a983aee0b842bce8f01746c0a3f2aeedef7e844be549c35
notes_baseline: eb00fa2d3b1e0fa3a65896d5bdc543e28f96ad3cb88a536ccb9c83d14435064b
---

# nox -s agents

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s agents` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/agents.py` |
| Code | `repo://quality/sessions/agents.py#agents` |

## Docstring

~~~text
MCP tools/resources via the SDK's in-memory session and stdio start-up, plus the SDK-free static checks.

The SDK-free checks (owner-operation lint, config snippets, docs and skills drift) always run. The SDK tests
need the `agents` extra; without it they report NOT_RUN in the log (the session still exits 0, so read it).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
