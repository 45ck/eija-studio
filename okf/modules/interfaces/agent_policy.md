---
type: Module
title: interfaces.agent_policy
description: 'SDK-free policy data for the agent adapter: which persistence operations an agent adapter must never touch.'
resource: repo://src/eija_studio/interfaces/agent_policy.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/agent_policy.py
  title: interfaces/agent_policy.py
  hash_method: ast-api-v1
  sha256: b211032c164a6f9b5aeafb731be142565a6fb564e08fc7878b0a26179522713d
notes_baseline: 4f79a531c2cfeb0740bd2eb585556d65e01781e6bcfe0c5958e0a45ff837ef4a
---

# interfaces.agent_policy

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/agent_policy.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
SDK-free policy data for the agent adapter: which persistence operations an agent adapter must never touch.

Kept out of ``mcp_server`` so the static lint (tests/test_agent_static.py) can import it without the MCP SDK.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [interfaces.mcp_server](/modules/interfaces/mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
<!-- okf:generated:end links -->
