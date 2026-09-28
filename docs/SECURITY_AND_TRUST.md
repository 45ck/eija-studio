# Security, trust and privacy boundary

## Deployment assumption

**One trusted OS user, one local EIJA server, synthetic data.** Do not expose this server on a network, put it behind a reverse proxy, use it for production student records, or treat its local owner as an institutional approver. A process running with the same OS permissions can modify the DB, obtain the session capability, read `receipt.key`, change source or invoke Python APIs with a fabricated Principal. The POC does not provide an adversarial OS-user boundary.

## Assets and controls

| Threat | Implemented control | Residual limitation |
|---|---|---|
| Remote page attempts a local mutation | Loopback bind, exact Host allowlist, ephemeral bearer capability, exact Origin on writes, JSON requirement, body cap, no CORS | Not protection from local malware, malicious browser extensions or stolen capability |
| Provider output contains HTML/scripts or claims approval | DOM textContent, restrictive contracts, server-owned interpretation labels, no provider authority port | Prompt can still cause a misleading but typed explanation; owner must choose meaning |
| Provider emits malformed/truncated/tool output | Bounded response bytes, strict local validation, no tools, no silent fallback | Model/provider compatibility and real failure rates need live tests |
| Credential disclosure | Key stays in process or caller-managed environment; non-echoing prompt; no key browser field; no raw provider errors exported | Environment/process memory remains accessible to trusted OS user; terminal/OS hygiene is external |
| Saved ChatGPT login misused as API token | Codex owns authentication; EIJA does not read auth.json; forced ChatGPT method; sanitized subprocess environment | Codex itself and its effective system/managed policy must be trusted and tested |
| Agent accesses local workspace | Empty temporary Codex working directory; ignored user config; read-only mode; explicit disabled shell/unified-exec/apps/search; no approval/apply tool schema | Configuration is not a formally verified sandbox; tool/CLI evolution and inherited managed settings need target validation |
| Replayed success bypasses revocation | Current trusted actor check before operation lookup; full operation binding | Synthetic directory does not integrate with real SSO or assignment feeds |
| Partial state or duplicate effects | One SQLite UOW, CAS versions, unique operation/outbox IDs, process-crash tests | Hardware power loss and real external delivery untested; local enqueue only |
| Forged green report | Recompute claim/kind/subject/observations/coverage; HMAC; immutable retained receipts | HMAC key owner can forge; oracle same-author; no external evidence trust root |
| Modified core looks like ordinary edit | Source fixture mismatch blocks verify/apply eligibility | Fixture manifest itself is self-authored; independent review/signing absent |
| Lost/stale provider response incurs cost | Start-attempt audit, failed publication record, one-process single-flight, no retry | No distributed deduplication, hard money cap or provider-side cancellation guarantee |
| Sensitive request sent out | Startup network flag plus per-call consent; synthetic fixture default; no automatic background inference | The application cannot know whether free text secretly contains personal data |

## Egress and retention

Offline mode performs no model calls. The live proposal payload contains the requested text and the synthetic baseline model. It excludes runtime actors, database contents, local receipt key, session token, stored traces, whole repository and generated evidence. Requests, interpretations, provider usage metadata and audit events are persisted locally. Output errors are sanitized; do not enable verbose provider debugging that prints secrets.

The OpenRouter endpoint is fixed HTTPS with redirects disabled. Proxy environment variables are not inherited by its HTTP transport. No retry is performed. The response cap and `max_tokens` limit output, not total money; reasoning/pricing behaviours and timeouts can still incur charges. Configure a provider-side spend limit yourself before live testing.

The Codex adapter delegates login and token storage to Codex, uses a temporary directory and structured final output, and removes API-key environment variables from the subprocess. Doctor is a non-inference preflight. Read-only sandboxing alone is not sufficient for connectors, so app/search/shell-related features are explicitly disabled as well. If the installed CLI lacks required flags, the adapter refuses instead of silently weakening configuration. Managed policy can impose additional restrictions; do not bypass it.

No secret-bearing workspace or database is included in the public package. Demonstration exports contain only generated synthetic IDs, results and local seals whose disposable workspace key is not distributed.

## Integrity does not mean truth

`SHA256` identifies contents. A correct hash can identify false claims. HMAC identifies integrity relative to a local secret. It does not identify an independent reviewer, validate the policy or measure human comprehension. The runtime verifier and expected-outcome oracle are separately expressed but share authorship. The implementation fixture check means “these are the release bytes,” not “these bytes are formally correct.”

## What must change before production

Use an authenticated institutional identity/assignment adapter with per-resource authority; separate approver credentials from agent execution; isolate agents in restricted processes/containers; introduce independently protected signing/attestation keys; implement rate/spend quotas and egress policies; perform secret/dependency/security reviews; validate target OS permissions and cancellation; define encrypted backups, retention/deletion and incident response; test independent mutations and real operational workflows. Those are new engineering changes, not configuration flags that this release already supports.
