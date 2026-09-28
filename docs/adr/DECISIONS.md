# Architecture decision records

All decisions below are accepted **for the local POC**, not endorsements for production.

| ID | Decision and rationale | Rejected shortcut | Consequence / revisit trigger |
|---|---|---|---|
| ADR-001 | One modular monolith with browser and CLI over the same kernel. | Six engines behind one menu; premature microservices. | Shared semantics and simpler local deployment; revisit for measured multi-user needs. |
| ADR-002 | Rework the narrow A3-inspired kernel instead of inheriting its unchecked preconditions and replay order. | Claim the old 326 passing executions validate the new integration. | Explicit new tests and source lineage; broad historical features are not ported. |
| ADR-003 | Freeze the supported excursion vocabulary and effect policy. | Arbitrary executable expressions, permissive unknown operators. | Reject unsupported semantics; second domain requires deliberate policy and oracle work. |
| ADR-004 | AI is a proposal port only; canonical meaning labels are server-owned. | Grant an LLM write/approve/apply powers because it is signed in. | No autonomous implementation agent; authority remains outside inference. |
| ADR-005 | Use supported Codex noninteractive authentication delegation. | Extract browser/session tokens, unofficial OAuth, subscription-as-API-key. | CLI version/authentication become explicit external prerequisites; live test required. |
| ADR-006 | OpenRouter structured output plus local validation; no silent fallback/retry. | Treat schema support as universal or retry without spend consent. | Certain provider/model pairs will fail closed; timeout billing can remain unknown. |
| ADR-007 | SQLite transaction owns state/operation/audit/outbox; reauthorise before replay. | In-memory effects, post-response writes, cached success as ongoing authority. | Durable local semantics tested; no external dispatcher or multi-server guarantee. |
| ADR-008 | Separate semantic identity, exact review subject, evidence applicability and decision. | One undifferentiated hash or manually asserted PASS. | Layout can retain domain evidence while invalidating exact-presentation approval. |
| ADR-009 | Compute evidence from sealed raw observations with required matrix coverage. | Trust supplied claim/status/admissible fields or incomplete empty observations. | Strict known evidence kind only; HMAC is local integrity, not external attestation. |
| ADR-010 | Keep technical eligibility distinct from human evidence and field authority. | Call synthetic personas/tests a measured human benefit. | Human UNKNOWN is visible and field-use blocked. |
| ADR-011 | Single local owner via ephemeral loopback capability; synthetic actors only. | Pretend role drop-downs constitute institutional authentication. | Same OS user/process is trusted; multi-user operation forbidden for this POC. |
| ADR-012 | Preserve original receipts and audit decisions; no silent rebase. | Rewrite historical reports to current or merge stale approvals. | More retained data; local workspace size is bounded operationally, not yet auto-pruned. |
| ADR-013 | Browser has no build-time framework dependency; render untrusted text through DOM text nodes. | Evaluate provider HTML or require a second frontend deployment. | Small inspectable client; no claim of formal accessibility/usability certification. |
| ADR-014 | One source release plus generated wheel and evidence; no copied historical media archives. | “All-in-one” by nesting the six old packs again. | Small active package with provenance; originals remain separate archival material. |
