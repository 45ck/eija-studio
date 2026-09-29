---
type: Module
title: interfaces.agent_config
description: Copy-paste MCP client configuration for `eija mcp --print-config <client>`.
resource: repo://src/eija_studio/interfaces/agent_config.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/agent_config.py
  title: interfaces/agent_config.py
  hash_method: ast-api-v1
  sha256: 7929fadde2747a62cc4c818058c0a88de6c1ad57e81f4282c00e245b3001755e
notes_baseline: ab10bae8ab3a8d14d09c76ac4d75b742be9e49345f7bf5dd82becc3a008e7ff5
---

# interfaces.agent_config

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/agent_config.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Copy-paste MCP client configuration for `eija mcp --print-config <client>`.

Pure text generation: no MCP SDK import, so it works before the `agents` extra is installed. Each
snippet follows the client's documented syntax (sources are listed in docs/agents/quickstart.md).
It does NOT install or verify anything in the client; the owner pastes it.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.mcp_server](/modules/interfaces/mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
<!-- okf:generated:end links -->
