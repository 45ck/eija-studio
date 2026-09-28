# Provenance and official integration references

## Continuity from the combined packs

`source-inputs.json` records exact hashes for the delivered v0.1 specification/audit/archive and the inspected A3 v0.9 model/runtime sources restored from that archive. The v0.2 implementation is a reworked narrow kernel informed by those sources. No claim is made that every old feature, rendered document, old test suite or bug fix has been ported. The earlier 326 historical test executions are not counted as v0.2 verification.

The release uses the Semantic Model Studio separation of preview/save/apply; Change Once See Everything's propagation concern; Accept the Meaning's authority/evidence distinction; All In One's executable workflow/subject vocabulary; and Make Software Explain Itself's runtime-trace demonstration. Those are conceptual contributions, not six live engines. Old ambiguous `ACC` expansions are not adopted in active code. The active records are Change Case, Semantic Transaction, Evidence Receipt and Review Packet.

The earlier assignment/replay, silently shallow impact and relabelled evidence issues motivated explicit v0.2 regression tests. This release further rejects malformed authenticated matrix artifacts with missing/duplicate/empty cells and invalid observation types. It does not infer whole-system correctness from closing those examples.

## Primary integration references

Reviewed 2026-09-27. These are official provider documentation; consult current versions before a live setup. They describe provider interfaces, not evidence that the supplied adapters completed live calls.

| ID | Official source | Used for |
|---|---|---|
| OAI-AUTH | https://developers.openai.com/codex/auth/ (redirects to official ChatGPT Learn authentication documentation) | ChatGPT login versus API key, saved authentication, ownership by Codex |
| OAI-NI | https://developers.openai.com/codex/noninteractive/ | `codex exec`, reuse of saved login, structured final outputs |
| OAI-CLI | https://developers.openai.com/codex/cli/reference/ | Flags: ignored user config, ephemeral execution, schema/output files, working directory, read-only mode |
| OAI-CONFIG | https://learn.chatgpt.com/docs/config-file/config-reference | Forced ChatGPT login method, shell/unified-exec/apps/search/history configuration |
| OR-STRUCT | https://openrouter.ai/docs/guides/features/structured-outputs | JSON-schema response format and required-parameter routing |
| OR-API | https://openrouter.ai/docs/api/reference/overview | Chat completion endpoint, bearer credential, model and normalized response fields |

No availability, model-price, unlimited-subscription-use or universal schema-support claim is taken from memory. The user selects a currently available OpenRouter model. Codex must pass local preflight, then a real synthetic call must be performed before its live adapter is marked validated.

## Evidence authorship

The implementation, protected domain policy, expected-outcome oracle, tests, release fixture and this review share authorship. There is no independent sign-off, blinded holdout evaluation or human participant dataset. Browser screenshots depict the real application DOM under a documented component-test transport bridge; they are not evidence of ordinary browser navigation or successful provider login.
