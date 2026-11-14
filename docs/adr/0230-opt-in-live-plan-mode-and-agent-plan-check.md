# ADR-0230: Opt-in live plan mode, and a plan check for coding agents

* Status: accepted
* Date: 2026-11-11
* Lane: providers / agents / PlayIDE chat

## Context and problem statement

On 2026-10-08 the owner kept PlayIDE's chat offline and synthetic: a phrase reader plus the pack's proposal rules, never a model. On 2026-11-11 the owner chose to allow live AI as an opt-in, with offline staying the default and the demo staying offline. The offline reader misses plain paraphrases (5 of 6 in the intent eval, ADR-0229), which is exactly where a model helps. Separately, coding agents (Claude Code, Codex and others over MCP) had `edit_check` for one edit on a selected case, but no way to ask "would the kernel accept this whole change?" before writing code.

## Decision drivers

* The model reads; it never writes steps, selects a meaning for the owner, approves or applies.
* Consent per request, on top of `--allow-network` at startup, as for every other networked call (AGENTS.md).
* Offline stays the default and is unchanged when no networked provider is configured.
* Exact phrases never leave the machine.

## Considered options

* A live plan proposer that maps a request to one of the pack's meanings and plans that meaning's own transactions (chosen).
* Letting the model write typed steps directly: more general, but the steps become model-authored and the attack surface grows; revisit with evals that measure step quality.
* Leaving the chat offline (the 2026-10-08 position): superseded by the owner's 2026-11-11 decision.

## Decision outcome

**Live plan mode.** `adapters/live_plan_proposals.py` wraps the configured proposal provider. A request whose clauses are all exact phrases is planned offline and never sent. Otherwise the provider's first alternative must be a pack meaning with transactions; those transactions become the plan, and the kernel checks it as usual. An unsafe meaning is planned as asked and refused by its law (issue #152). A meaning with nothing to plan is refused with the model's explanation.

It is wired only when the Studio's provider is networked. `/api/status` reports `live_plan` (true only with `--allow-network`), and `/api/play/plan` takes a strict boolean `consent`; consent without a live proposer or without network is refused with `EGRESS_CONSENT_REQUIRED`. The chat shows an "Ask <provider> for this request" box only when `live_plan` is true, and the box unticks after every send.

**Plan check for agents.** The MCP tool `plan_check(steps)` dry-runs a plan of typed steps (the chat's step vocabulary) on the model in force, in order, and returns the same preview the chat shows: legal or not, each step's status, refusal codes and the laws they name. No case is needed; nothing is stored. It is read-only and listed in `AGENT_TOOLS`, the agent contract and both skill files.

### Consequences

* Good: a person can ask in their own words and still get a kernel-checked plan; an agent can learn which law a change breaks before it writes code.
* Good: nothing changes for an offline Studio, the demo recordings, or the existing tests.
* Bad: the live path can plan only what the pack already models. A request for a genuinely new change still needs exact phrases.
* Bad: no live provider has been run through this path yet; its quality is measured by the intent eval, not assumed.
* Revisit when: the intent eval shows a provider reliably above the offline baseline on paraphrases, or model-written steps are wanted.

### Amendment, 2026-11-13 (Fagan inspection)

* A request that is partly exact phrases and partly prose is refused with `PLAN_REQUEST_MIXED` before anything is sent: the model plans one meaning, so the clauses the phrase reader read would otherwise be dropped from the plan.
* One live plan call runs at a time; a second while one is in flight is refused with `PROVIDER_BUSY` and never sent.
* A request shaped like an exact phrase but naming something the model lacks gets the phrase reader's `PLAN_UNKNOWN_NAME` and is not sent (owner's call, 2026-11-13).
* Every live plan call that leaves the machine is audited, as `Studio.propose` is: `PlanProviderCallStarted`, then `PlanProposalReceived` or `PlanProviderCallNotAccepted`, with a request hash and never the request.
* `plan_check` on a system started in PlayIDE (`eija mcp --systems`, default `~/PlayIDE`) declares new actions and roles as the chat does, and says `grows`.
* See `docs/quality/inspections/2026-11-13-ai-chat-plan-mode.md` for the defects logged and not yet fixed.
