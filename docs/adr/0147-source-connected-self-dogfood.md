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

### Snapshot consistency in linked views

Source and impact reads can pin the exact `sha256:` identity returned with a
repository snapshot. The capture used for comparison is also used for indexing
and the returned excerpt, so a separate freshness check cannot race the read.
The authenticated GET freshness endpoint accepts that small identity rather than
a file manifest; the existing request-size limit stays unchanged. Manifest-based
adapter checks can still identify changed paths; a single hash cannot.

The browser pins linked reads, rejects mismatched responses and cancels obsolete
requests after case/revision, selection or connection changes. Refresh updates
the connection without resetting unsent model fields, historical previews or
runtime state. Previously displayed source remains explicitly labelled while
reopening its reference; source/impact failures provide a refresh action.
External repository identity remains distinct from the evidence packet's subject.
No receipt, conformance claim or approval is created by a freshness match.

## Validation

### Immutable code changes

A separate application-owned read-only port compares explicit local commit pairs.
Git owns object identity, inventory and the line diff; the adapter never checks out
or executes the target. Historical excerpts retain exact blob/text/range identities
and never fall back to the current source reader. Captured changed-file hashes are
distinct from a complete live repository capture and from model receipt subjects.

Reuse Python AST/Weave and optional pinned Tree-sitter JavaScript packages for
bounded syntax facts. JavaScript native imports run only in a fixed bounded worker;
missing packages, crashes and timeouts become NOT_RUN. Current coverage is partial:
class/dynamic syntax and uncaptured dependency edges cannot be presented as proven
absence. No owner capability or second workflow interpreter is introduced.

The Code changes view uses the exact Git diff and historical sides, with a separate
selection and task navigator. See [scope and reproduction](../engineering/IMMUTABLE-CODE-REVIEW.md).

### Required observations

Tests must distinguish extraction determinism from semantic correctness; include missing
and changed bindings, excluded paths, pack collisions, stale versions, rejected edits,
and absent owner capabilities on MCP. Run the same workbench against multiple packs,
including the self reference journey. Record the real browser result and exact gate
outcomes in the dated self-dogfood run report. Human comprehension and competitor
superiority remain unmeasured until a comparative study is performed.
