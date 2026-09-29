---
type: Architecture Decision Record
title: 'ADR-0041: MCP server as the agent surface: propose and check, never decide'
description: People want their own agents (Claude Code, Codex, OpenCode, Gemini CLI) to use EIJA Studio.
resource: repo://docs/adr/0041-mcp-server-agent-surface.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0041-mcp-server-agent-surface.md
  title: 0041-mcp-server-agent-surface.md
  hash_method: lf-sha256-v1
  sha256: c3c330c15494a0fac33cfc6e1d41e166912a78b6fd90030f613292a5f7fed5eb
notes_baseline: 948e1a43fb3c8fecd932c946110ea47bc8570dd0dc065e49e9226585f4c9db4c
---

# ADR-0041: MCP server as the agent surface: propose and check, never decide

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | agents |
| Source | `repo://docs/adr/0041-mcp-server-agent-surface.md` |

## Decision outcome (verbatim)

> Chosen option: an `eija mcp --workspace PATH` stdio server in `interfaces/mcp_server.py` built on the official SDK, with exactly seven tools (`list_cases`, `create_case`, `propose`, `view_case`, `impact`, `verify`, `render`) and resources for the ubiquitous language, the ADR index/records and the agent contract.
>
> * **Absence, tested.** `select`, `edit`, `approve`, `apply` (and layout, discard, save, preview, execute, export) are not registered; `AgentSurface` receives an `AgentPort` (list/create/propose/verify/view), never the `Studio`, and only `StudioAgentPort` holds one; a best-effort AST lint (`tests/test_agent_static.py`, with negative controls that mutate the source) rejects owner-operation names on any receiver, store writes, `OWNER`, `getattr`-style dynamic access and aliasing of `Studio`. The lint is not a proof: the registry assertion and the narrow port are the guarantee, and the lint catches regressions. There is no principal object in the adapter to enforce anything, the audit log does not attribute agent actions (`Studio.create`/`propose`/`verify` take no principal; kernel follow-up), and the kernel's `AUTHORITY_REQUIRED` guard is never reached from an agent tool because no tool leads to it (the kernel's own tests cover that guard). Kernel domain errors that a permitted tool can hit (`MEANING_REQUIRED`, `STALE_VERSION`, ...) are surfaced as tool errors `CODE: message`; any unexpected exception is returned only as a generic `INTERNAL_ERROR` (details to stderr, never to the agent).
> * **Consent is the owner's, and it is standing.** `propose` has no consent argument. A networked provider requires `--allow-network --egress-consent` at startup or the command refuses to start. `--egress-consent` is not per-request consent: it is set once and covers EVERY `propose` call for the life of the server process, and the agent may call `propose` repeatedly. Passing it means the owner accepts that the agent can send case request text to the provider (and spend against a paid one) without asking again. `--ask-key` is refused (stdin is the protocol channel).
> * **Spend guard.** A session may make at most `--max-provider-calls` networked provider calls (default 3; `0` forbids them). Attempts are counted before the call is made because a started request may bill even if it fails, and this includes attempts the kernel then refuses (for example a case whose meaning is already selected). Beyond the cap `propose` returns `PROVIDER_CALL_LIMIT`; only the owner can raise it, by restarting the server with a higher value. The cap is per server process, not per day or per key: restarting resets it, and it does not replace a spend limit on the provider account. Offline providers are not counted.
> * **Startup errors go to stderr.** In `mcp` mode stdout is the JSON-RPC channel, so configuration and missing-extra errors are written to stderr; a raw-subprocess test asserts every stdout line is a JSON-RPC message.
> * **Redaction.** Question text is shown without expected answers; the decision is summarised (present, by, scope) without its seal; receipts appear as applicability, not raw seals. A test scans every tool's output after approval (with a negative control). Redaction is hygiene, not secrecy: the answers are derivable from `projections`, which the agent may read.
> * **`verify` is refused after owner approval** (`VERIFY_WOULD_INVALIDATE_DECISION`): `Studio.verify` clears an existing decision, and an agent must not be able to revoke the owner's approval. This is an interface guard, not a kernel change. Re-verifying an unapproved case bumps its version, so an owner review in flight goes stale (`STALE_VERSION`); that is documented, not prevented. `expected_version` is optional on `propose`/`verify`: omitted, the tool acts on the current version (no compare-and-swap); pass it to get `STALE_VERSION` protection.
> * **Diagrams are not generated here.** `render` serves projections (`json`, `text`); `mermaid|plantuml|svg` call an injected `DiagramRenderer` (extension point for the visual lane, ADR-0019) and otherwise return `DIAGRAMS_NOT_AVAILABLE`.
> * **SDK version.** Pinned `mcp==2.2.0` (and `anyio==4.15.1`, which the adapter imports directly) in the `agents` extra; the rest of the measured transitive closure is pinned in `requirements-agents-tested.txt` for use as `pip -c` constraints (it is not folded into the extra because deptry would report pins the code does not import). In the 2.x line `FastMCP` was renamed `MCPServer` (`mcp.server.mcpserver`); the design is the same. If a client cannot negotiate with a 2.x server, pin `mcp<2` and swap the import; the adapter is one file.
> * **Config snippets** are generated by `eija mcp --print-config <client>` (pure text, no SDK needed) and parse-tested; syntax sources are cited in `docs/agents/quickstart.md`.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/agents/quickstart.md`
* `repo://tests/test_agent_static.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0016: OSS first: build adapters, not engines](/adrs/0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0019: Diagrams are generated projections of the executable model](/adrs/0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.

## Referenced by

* [ADR-0097: Impact, ranking and evidence-status mathematics: fixed points, integer relevance, greedy selection, count vectors, and no confidence percentage](/adrs/0097-weave-impact-ranking-math.md) - The weave graph must answer six questions about a change: what does it affect, what should an agent or a person read, which tests give the cheapest useful re-c…
* [ADR-0099: Agent interface: typed read tools, deterministic context packs, pure dry runs, a small link checker and hash-chained replay](/adrs/0099-weave-agent-interface.md) - The weave graph will hold typed, hash-anchored links over code, UI, diagrams, language, requirements, tests, proofs and evidence, with a checker that reports f…
* [Agent integration (MCP server, skills)](/lanes/0041-agent-integration.md) - Capability lane with ADR numbers 0041–0042 reserved.
<!-- okf:generated:end links -->
