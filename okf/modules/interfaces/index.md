# Interfaces: the eija CLI and the FastAPI HTTP app

# Modules

* [interfaces.agent_config](agent_config.md) - Copy-paste MCP client configuration for `eija mcp --print-config <client>`.
* [interfaces.agent_policy](agent_policy.md) - SDK-free policy data for the agent adapter: which persistence operations an agent adapter must never touch.
* [interfaces.app_build](app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [interfaces.cli](cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.http](http.md) - Loopback-only local adapter.
* [interfaces.mcp_server](mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
* [interfaces.render_html](render_html.md) - Self-contained HTML for `eija render --format html`: generated Mermaid text plus the vendored renderer.
