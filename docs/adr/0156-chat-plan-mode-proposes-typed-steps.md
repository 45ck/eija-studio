# ADR-0156: Chat plan mode proposes typed steps the person accepts or rejects

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026)

## Context and problem statement

The owner's roadmap asks for an AI chat sidebar "like T3 Code, with plan mode prominent", in which the AI proposes changes to the UML and the person accepts or rejects them. The repository's rules say AI proposals are untrusted: they cannot choose meaning, mint receipts, approve, apply or change protected policy. A chat that edited the model directly would break that. A chat that only talked would not help.

## Decision drivers

* The AI proposes; the kernel and policy decide. A plan must be expressed in the existing typed transaction vocabulary, never in a new one.
* The person sees each step on the diagram before anything changes, and can reject any of them.
* Nothing in plan mode persists or applies. Making a change real still goes through a change case and the review workbench.
* No network, spend or keys without the owner's explicit permission. The default proposer must be offline and say so.

## Considered options

* Plan mode over typed transactions, re-checked by the application, previewed as a candidate model (chosen).
* Let the chat call the owner's edit routes (`/edit`, `/select`, `/apply`). Rejected: those are owner-only, and an AI must not approve or apply.
* Save every chat plan as a change case. Rejected for now: a change case needs a selected supported meaning, and a free-form plan has none. Plans that come from a modelled meaning can become a change case; the rest is an owner decision (GitHub issue).
* Use an LLM through the existing OpenRouter or Codex adapters by default. Rejected: live inference needs the owner's permission for egress and spend. The port allows a live proposer later.

## Decision outcome

Chosen option: an application-owned `PlanProposer` port, `application/plan.py`, and an offline proposer.

* `PlanProposer.propose(request, model, pack)` returns a document of steps, each a transaction and a reason. The offline proposer (`adapters/plan_proposals.py`, `offline-plan-fixture-v1`, `live: false`) reads a bounded phrase grammar using exact model names ("add state Lost after Overdue then add Renew from Overdue to Lost for Librarian"), or matches the pack's own proposal rules to a supported meaning with transactions. Anything else is refused with the phrases it understands. It is a fixture, not an AI, and the UI labels it.
* `propose_plan` treats the document as untrusted: it re-parses every step with `parse_transaction`, bounds the plan to 12 steps and the request to 2,000 characters, and keeps a meaning only if the pack has it.
* `preview_plan(model, pack, transactions, accepted)` checks each accepted step after the accepted steps before it, so a step that needs a rejected one says `PLAN_STEP_DOES_NOT_APPLY`. The accepted steps are then applied together through `apply_transactions`, the same policy as an owner's edit, so a protected-authority change is refused with the policy's codes. A legal preview returns the candidate model, its semantic hash and the diff.
* `POST /api/play/plan` and `POST /api/play/plan/preview` expose them. `BuildRequest.plan` lets **Build & run**, **Simulate**, **Screens** and **Components** run on the candidate: the server recomputes it from the steps, never trusting a model the browser sends.
* The chat panel sits at the top of PlayIDE's sidebar with a "Plan mode" label. Each step has a checkbox; **Preview on the diagram** redraws every tab from the candidate, highlights what changed and shows a banner with **Back to the model**. A plan from a modelled meaning offers **Make it a change case**, which opens a case from the request; its meaning is still chosen in the review workbench.

### Consequences

* Good: the AI cannot change anything the person has not seen, and cannot change anything at all outside a preview. The policy decides legality exactly as for an owner's edit.
* Good: the try-it loop (plan, preview, build, simulate) works on a candidate without touching the store.
* Bad: the offline grammar is narrow and wants exact names. A live proposer behind the same port fixes that once the owner allows network use.
* Bad: a free-form plan cannot yet be saved. That needs an owner decision on how a plan without a modelled meaning becomes a change case.
* Revisit when: the owner allows a live proposer, or decides how free-form plans are saved.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| T3 Code plan mode (MIT) | A pattern, not a library: plan first, then act on approval. Adopted as the interaction pattern | — |
| LangChain, LlamaIndex agents | Would let the model call tools directly; here the model may only propose typed steps | A live `PlanProposer` adapter may use a client SDK |
| Existing OpenRouter and Codex adapters | Need network and spend permission | Wrap behind `PlanProposer` once allowed |
| Pydantic transaction contracts | Adopted (existing) | — |
