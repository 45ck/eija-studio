# ADR-0041: MCP server as the agent surface: propose and check, never decide

* Status: accepted
* Date: 2026-09-28
* Lane: agents

## Context and problem statement

People want their own agents (Claude Code, Codex, OpenCode, Gemini CLI) to use EIJA Studio. All four speak the Model Context Protocol (MCP). The kernel's rule is "AI proposes, the kernel checks, the local owner decides", and AGENTS.md forbids agents from selecting meaning, approving or applying. How do we make connecting an agent a one-minute task without giving it owner authority?

## Decision drivers

* Owner operations must not exist on the agent surface, not merely be denied: the guarantee is the absence of the tool and of any call to the owner-only `Studio` methods. (The adapter holds no principal and passes none to `Studio`; it never reaches a check that a principal could pass or fail.)
* Network egress and spend stay the owner's decision, taken at startup, never a tool argument, and bounded so an agent cannot loop on a paid provider.
* Sealed material (decision seal) and the meaning-check answers must not reach an agent.
* OSS first (ADR-0016): use the official SDK; write only the EIJA-specific adapter.
* Onboarding must be copy-paste for four clients whose config syntax differs and changes.

## Considered options

* Official MCP Python SDK (`mcp`), stdio server, agent-only tool surface (chosen).
* Hand-written JSON-RPC over stdio: rejected, protocol details (initialisation, versions, schema generation) are exactly what the SDK maintains.
* Expose every Studio operation over MCP and rely on `Principal.require`: rejected, the kernel would refuse, but the agent would be offered owner tools and could be prompt-injected into trying them; absence is a stronger and testable guarantee.
* Skill files only (CLI instructions), no server: rejected, no typed tools, no resources, no enforceable surface.
* Streamable-HTTP transport: deferred. Loopback stdio launched by the client needs no listening port or token handling; revisit for remote agents.

## Decision outcome

Chosen option: an `eija mcp --workspace PATH` stdio server in `interfaces/mcp_server.py` built on the official SDK, with exactly seven tools (`list_cases`, `create_case`, `propose`, `view_case`, `impact`, `verify`, `render`) and resources for the ubiquitous language, the ADR index/records and the agent contract.

* **Absence, tested.** `select`, `edit`, `approve`, `apply` (and layout, discard, save, preview, execute, export) are not registered; `AgentSurface` receives an `AgentPort` (list/create/propose/verify/view), never the `Studio`. The `Studio` lives only in the closure of the `StudioAgentPort` factory, so the port object has no attribute that leads to it: a test walks every non-dunder attribute path from the surface and calls `attrgetter`/`methodcaller`/dotted paths for every owner name (all `AttributeError`). Dunder or introspection access (`__closure__`, `__globals__`, `operator`, `importlib`) is not prevented at runtime; a best-effort AST lint (`tests/test_agent_static.py`) rejects it, owner-operation and store-write names on any receiver (the store names are derived from the persistence ports, not typed by hand), `OWNER`, `getattr`-style dynamic access, and the `Studio` class or instance used outside the port factory. Each lint rule has a negative control that only it catches (a test enforces that), so deleting a rule fails a test. The lint is not a proof and the adapter is not a sandbox: the registry assertion and the narrow port are the narrowing, and the lint catches regressions in the common spellings. There is no principal object in the adapter to enforce anything, the audit log does not attribute agent actions (`Studio.create`/`propose`/`verify` take no principal; kernel follow-up), and the kernel's `AUTHORITY_REQUIRED` guard is never reached from an agent tool because no tool leads to it (the kernel's own tests cover that guard). Kernel domain errors that a permitted tool can hit (`MEANING_REQUIRED`, `STALE_VERSION`, ...) are surfaced as tool errors `CODE: message`; any unexpected exception is returned only as a generic `INTERNAL_ERROR` (details to stderr, never to the agent).
* **Consent is the owner's, and it is standing.** `propose` has no consent argument. A networked provider requires `--allow-network --egress-consent` at startup or the command refuses to start. `--egress-consent` is not per-request consent: it is set once and covers EVERY `propose` call for the life of the server process, and the agent may call `propose` repeatedly. Passing it means the owner accepts that the agent can send case request text to the provider (and spend against a paid one) without asking again. `--ask-key` is refused (stdin is the protocol channel).
* **Spend guard.** A session may make at most `--max-provider-calls` networked provider calls (default 3; `0` forbids them). Attempts are counted before the call is made because a started request may bill even if it fails, and this includes attempts the kernel then refuses (for example a case whose meaning is already selected). Beyond the cap `propose` returns `PROVIDER_CALL_LIMIT`; only the owner can raise it, by restarting the server with a higher value. The cap is per server process, not per day or per key: restarting resets it, and it does not replace a spend limit on the provider account. Offline providers are not counted.
* **Startup errors go to stderr.** In `mcp` mode stdout is the JSON-RPC channel, so configuration and missing-extra errors are written to stderr; a raw-subprocess test asserts every stdout line is a JSON-RPC message.
* **Redaction.** Question text is shown without expected answers; the decision is summarised (present, by, scope) without its seal; receipts appear as applicability, not raw seals. A test scans every tool's output after approval (with a negative control). Redaction is hygiene, not secrecy: the answers are derivable from `projections`, which the agent may read.
* **`verify` is refused after owner approval** (`VERIFY_WOULD_INVALIDATE_DECISION`): `Studio.verify` clears an existing decision, and an agent must not be able to revoke the owner's approval. This is an interface guard, not a kernel change. Re-verifying an unapproved case bumps its version, so an owner review in flight goes stale (`STALE_VERSION`); that is documented, not prevented. `expected_version` is optional on `propose`/`verify`: omitted, the tool acts on the current version (no compare-and-swap); pass it to get `STALE_VERSION` protection.
* **Diagrams are not generated here.** `render` serves projections (`json`, `text`); `mermaid|plantuml|svg` call an injected `DiagramRenderer` (extension point for the visual lane, ADR-0019) and otherwise return `DIAGRAMS_NOT_AVAILABLE`.
* **SDK version.** Pinned `mcp==2.2.0` (and `anyio==4.15.1`, which the adapter imports directly) in the `agents` extra; the rest of the measured transitive closure is pinned in `requirements-agents-tested.txt` for use as `pip -c` constraints (it is not folded into the extra because deptry would report pins the code does not import). In the 2.x line `FastMCP` was renamed `MCPServer` (`mcp.server.mcpserver`); the design is the same. If a client cannot negotiate with a 2.x server, pin `mcp<2` and swap the import; the adapter is one file.
* **Config snippets** are generated by `eija mcp --print-config <client>` (pure text, no SDK needed) and parse-tested; syntax sources are cited in `docs/agents/quickstart.md`.

### Consequences

* Good: one-minute onboarding; the agent's power is what the contract says, and tests fail if it grows; the SDK carries protocol maintenance.
* Bad: a new optional dependency tree (SDK, starlette, pywin32 on Windows); the MCP 2.x API is young and may move; docs/resources need a checkout (they are not packaged in a wheel, and the server says so).
* Noise note: on a memory-starved Windows PC the first `platform.system()` call (a WMI query) can raise `E_OUTOFMEMORY` inside CPython, which then falls back; pytest's faulthandler prints `Windows fatal exception: code 0x8007000e` although the test passes. It is warmed once in `create_server` at start-up instead of on the first tool call's worker thread; the dump is harmless and may still appear once.
* Not established: this narrows an interface, it is not a sandbox. An agent with the owner's OS permissions can still reach the workspace directly (see AGENTS.md and SECURITY_AND_TRUST.md).
* Observed kernel gap (recorded, not changed by this lane; FOLLOW-UP for the kernel owner): `Studio.verify` and `Studio.save` clear `decision` without recording a `DecisionInvalidated` audit event, unlike `edit` and `layout`. The interface guard above prevents an agent from triggering it through `verify`, but the missing audit event remains a kernel finding.
* Not established by the spend cap: it limits calls per session, not money; agent-authored request text is data the owner sees in Studio and is rendered as text (no HTML injection path was found), but Studio does not label a case as agent-created.
* Revisit when: a remote (HTTP) transport is needed; the diagrams module lands (wire `render`); the SDK 2.x API stabilises or a required client cannot connect.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| MCP Python SDK (`mcp`) | Adopted as-is; only the tool surface, redaction and consent policy are custom | Replace the one file `interfaces/mcp_server.py`; the `AgentSurface` class is SDK-independent |
