# Interfaces: the eija CLI and the FastAPI HTTP app

# Modules

* [interfaces.agent_config](agent_config.md) - Copy-paste MCP client configuration for `eija mcp --print-config <client>`.
* [interfaces.agent_policy](agent_policy.md) - SDK-free policy data for the agent adapter: which persistence operations an agent adapter must never touch.
* [interfaces.app_build](app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [interfaces.cli](cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.http](http.md) - Loopback-only local adapter.
* [interfaces.mcp_server](mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
* [interfaces.play](play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step the kernel decides (ADR-0152), the screen designer's check a…
* [interfaces.play_interop](play_interop.md) - PlayIDE routes for UML interchange (ADR-0190): export the model on screen, and read a UML file as a report.
* [interfaces.play_systems](play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
* [interfaces.render_html](render_html.md) - Self-contained HTML for `eija render --format html`: generated Mermaid text plus the vendored renderer.
* [interfaces.uml_interop](uml_interop.md) - `eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).
