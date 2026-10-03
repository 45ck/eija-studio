# Adapters: SQLite, providers, receipts and identity behind application ports

# Modules

* [adapters.edit_proposals](edit_proposals.md) - Bounded offline request fixture: exact model names and complete phrases, never an LLM.
* [adapters.identity](identity.md) - Measured release identity, not a proof of correctness or author authenticity.
* [adapters.receipts](receipts.md) - Local integrity seal.
* [adapters.repository](repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.repository_analysis](repository_analysis.md) - Captured-byte syntax and partial impact adapted to existing Weave primitives.
* [adapters.repository_capture](repository_capture.md) - Bounded repository reads adapted to the existing deterministic Weave engine.
* [adapters.repository_change_cache](repository_change_cache.md) - Bounded retention eligibility and installed extractor prerequisite identity.
* [adapters.repository_change_snapshot](repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.
* [adapters.repository_changes](repository_changes.md) - Read-only, bounded comparison of two local Git commits.
* [adapters.repository_javascript](repository_javascript.md) - Crash-isolated JavaScript syntax extraction; reuse the bounded process runner.
* [adapters.self_facts](self_facts.md) - Syntactic facts about EIJA's own review implementation, never a conformance proof.
* [adapters.sqlite_store](sqlite_store.md) - Durable local unit of work.
