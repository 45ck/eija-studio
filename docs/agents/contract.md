# Agent contract

What an AI agent (Claude Code, Codex, OpenCode, Gemini CLI, or your own) may and may not do with EIJA Studio. It restates [AGENTS.md](../../AGENTS.md) for the MCP surface ([ADR-0041](../adr/0041-mcp-server-agent-surface.md)); if the two ever disagree, AGENTS.md and the kernel win.

The model in one line: **AI proposes. The kernel checks. The local owner decides.**

## What an agent may do

Through the MCP server (`eija mcp`). Its guarantee is that owner operations are not registered as tools at all; it is not a role check:

| Tool | What it does | What it does NOT establish |
|---|---|---|
| `list_cases` | Lists cases (id, version, stage, request head) | Nothing about correctness |
| `pack` | Reads pack declarations, active model, source-review status and the optional repository connection | Extracted facts and declared model semantics have different coverage; no proof of equivalence |
| `affordances` | Reads checked edit choices for a selected case | No edit is selected or applied |
| `edit_check` | Checks an untrusted typed transaction and returns violations and references | Dry-run only: not persisted, applied, approved or evidence |
| `repository_impact` | Traverses declared links from a repository term | Covers supported extraction and declared bindings only; does not edit source |
| `repository_source` | Reads a bounded, hash-bound excerpt from a captured source node or declared binding | Read-only; arbitrary, excluded, untracked and unresolved references are refused |
| `repository_change` | Compares two full local Git commit IDs; reports captured changed files, syntax changes and explicit gaps | No target execution, agent-authorship assertion, behavior proof or model receipt |
| `repository_change_file` | Reads the exact historical diff and bounded source for a permitted changed file or extracted definition | Never falls back to current source; known impact excludes uncaptured/unmodified dependencies |
| `create_case` | Creates a case from a synthetic request | Not a chosen meaning |
| `propose` | Asks the configured provider for an UNTRUSTED interpretation | Not a decision, not evidence. The default provider is an offline fixture, not a model |
| `view_case` | Reads stage, proposal, review-packet summary, projections, meaning-check questions (no answers), UNKNOWNs | Not human understanding |
| `impact` | Reads modelled impact closure (needs an owner-selected meaning) | Covers the explicit model mapping only |
| `verify` | Runs the bounded technical runtime matrix and attaches a receipt | Same-author oracle: not approval, not a proof, not a human study. Refused once the owner has approved |
| `render` | Derived views (`rules`, `states`, `journeys`) as `json`/`text`; the built-in renderer also supplies `mermaid`/`plantuml`/`dot`. SVG needs a separately supplied renderer | Generated from the executable model; never edit it |

Resources: `eija://agent/contract` (this file), `eija://language` (the ubiquitous language), `eija://adr` and `eija://adr/{number}`.

Meaning-check answers and the decision seal are not returned, but that is hygiene, not secrecy: the answers are derivable from the projections you can read. Do not derive them to answer on the owner's behalf. `verify` on a case that is not yet approved bumps its version, so an owner review in flight goes stale; prefer passing `expected_version` (the version you last saw) to `propose` and `verify`.

Agents should also: report `UNKNOWN`, `NOT_RUN` and limitations verbatim; explain to the user what the owner must do next (`owner_next` in tool output); keep requests synthetic.

When following repository links from `pack`, pass its exact `connection.source_hash`
as optional `expected_source_hash` to `repository_source` and `repository_impact`.
The value includes the `sha256:` prefix. The adapter compares that identity to the
same captured bytes used for the answer. Changed bytes produce
`SOURCE_SNAPSHOT_STALE`; fetch `pack` again and reconsider the links before retrying.
Without the optional hash, each read describes its own fresh capture and must not
be assumed to match an earlier view. This observes byte identity at read time;
it does not prove behavior, continuous freshness or source/model conformance.

Historical comparison uses full lowercase 40- or 64-character local commit IDs.
Keep `comparison_id`, both commit/tree identities and `changed_source_hash` values
together when selecting a file or definition. Each changed-source digest covers
only captured changed files and is distinct from live `connection.source_hash`.
Report excluded counts, PARTIAL extraction and NOT_RUN behavior explicitly.
See the [code-review boundary](../engineering/IMMUTABLE-CODE-REVIEW.md).

## What an agent may not do

These operations do not exist on the MCP server, and a test proves it. Do not try to reach them by another route (HTTP API, SQLite file, CLI scripts):

* `select`: choosing the meaning of a request. Only the local owner selects.
* `edit`: changing the model or layout after selection.
* `approve`: acknowledging an exact review subject.
* `apply`: changing the active baseline.
* Grant egress consent for a networked provider. The owner does that at server start with `--allow-network --egress-consent`; no tool argument carries consent. That flag is standing consent for the whole session: the agent may call `propose` repeatedly, bounded only by the owner's `--max-provider-calls` cap (default 3, refusal `PROVIDER_CALL_LIMIT`). Do not try to work around the cap, and do not call `propose` speculatively when a live provider is configured.
* Mint or alter receipts, read `receipt.key`, read the browser launch token, run `scripts/stamp_release.py`, or edit `src/eija_studio/resources/trusted_build.json`.
* Fabricate answers to the meaning-check questions, or present a model proposal, a mocked result or a synthetic test as a live result, a code proof or a human study.
* Weaken kernel guards or protected policy to make a check pass.

## Honest reporting

* Missing prerequisite (Docker, Java, browser, CLI login, network): report `NOT_RUN`, never a pass.
* `human_understanding` is `UNKNOWN` unless a human study exists; say so.
* A local HMAC seal is an integrity check, not an external attestation.

## Limits of this contract

The server narrows what an agent can do through this interface. It is not a sandbox: an agent with the owner's OS permissions could still read the workspace or call the HTTP API if it obtained the launch token. Treat that as a violation of the contract, not as a capability.
