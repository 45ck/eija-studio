# ADR-0147: Source-connected self-dogfooding with explicit coverage

* Status: accepted for the local development slice
* Date: 2026-10-02
* Lane: integration

## Context

The product thesis calls for a model workbench that helps engineers inspect AI changes.
The owner selected EIJA itself as the first real repository; external projects follow
the first working flow. The previous browser and MCP views did not expose the existing
Weave source connections consistently. An id-only pack cache and workspace binding
could also confuse different contents carrying the same pack name.

## Decision

Reuse the existing typed transactions, policy, Weave extraction and official MCP SDK.
An application-owned repository port exposes a read-only snapshot and linked impact.
Bootstrap supplies the adapter. Git-tracked files form the bounded source inventory;
private, ignored, vendor and unsafe paths are excluded. Target code is never executed
by extraction. Missing bindings and unsupported language constructs remain visible.
The architecture order explicitly places Weave below adapters and above application;
domain and application remain free of vendor, database and network imports.

The browser renders the active model, domain tree and review evidence from server
data. A gesture proposes an existing typed transaction. The server checks it; an
explicit owner edit uses the observed case version. A rejected or stale edit must not
move the authoritative graph. MCP gains read-only model context, edit affordances,
dry-run checks and source impact. It gains no owner operations.

Pack content, not its display id alone, identifies the workspace's semantics. A
workspace whose old identity cannot be established requires explicit migration or a
fresh workspace. Reading an already open valid SQLite workspace must still support
the browser and MCP concurrently; normal SQLite lock sidecars are not semantic writes.

Self-dogfooding uses three separately labelled views: extracted Python facts, a declared
reference journey and direct implementation conformance tests. The workflow schema
cannot fully represent the Studio lifecycle's evidence and authority predicates.
The reference pack therefore does not certify EIJA's implementation. Each bound public
dependency needs its own link; a symbol hash does not transitively prove its callees.

## Alternatives and consequences

An LLM-generated graph alone cannot provide reproducible source facts. A second
interpreter in JavaScript would create another authority, so it is rejected. A new
graph engine is unnecessary: the small SVG view draws the existing model and delegates
semantic decisions to the server. Compiler-backed indexes can extend extraction later.

The connection does not yet compile arbitrary semantic edits into target-source patches.
An applied pack edit changes the local model runtime, not the connected Git checkout.
Full two-way application editing and parallel landing remain separate acceptance items.
No new live-provider calls, source stamping or migration are implied by this decision.

## Validation

Tests must distinguish extraction determinism from semantic correctness; include missing
and changed bindings, excluded paths, pack collisions, stale versions, rejected edits,
and absent owner capabilities on MCP. Run the same workbench against multiple packs,
including the self reference journey. Record the real browser result and exact gate
outcomes in the dated self-dogfood run report. Human comprehension and competitor
superiority remain unmeasured until a comparative study is performed.
