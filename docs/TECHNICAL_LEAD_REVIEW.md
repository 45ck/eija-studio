# Technical lead review — EIJA Studio 0.2.0

**Decision:** deliver one local modular application with two surfaces and one assurance kernel. Keep external language-model inference replaceable. Keep authorisation, execution and evidence deterministic within the declared grammar.

**Readiness:** executable local POC, with reproducible automated checks. Not production-ready; not a universally applicable compiler; no independently established safety or human-productivity claim. This review is authored with the implementation, not an independent principal-engineer sign-off.

## What was actually engineered

The v0.1 consolidation was a definition plus source audit. This release adds a working Python package, browser application, CLI/compiler, typed domain contracts, SQLite unit of work, computed evidence gate, provider adapters and adversarial tests. It does not simply wrap six historical engines or inherit their historical test totals.

The old A3 runtime supplied useful concepts but also contained gaps in executable guard checking and replay authorisation. The new kernel was reworked rather than copied intact: current actor checks precede replay; state, operation records, audit events and outbox entries share one transaction; evidence status is derived from authenticated raw observations and complete declared matrix coverage rather than trusted green flags. The fixed-point impact traversal has no silent default depth cap.

The genuinely integrated proposition is **request → explicit meaning → typed candidate → derived views → executed observations → exact-subject decision → local apply**. An attractive interface, signed receipt or large test count alone does not establish that proposition outside this fixture.

## Product boundaries

| Layer | Responsibility | Not responsible for |
|---|---|---|
| Studio | Present interpretations, rule/state views, runnable preview, evidence and decision | Invent missing requirements or disguise unsupported meaning |
| Semantic compiler | Normalize supported meaning, validate policy, generate projections and impact/evidence obligations | Compile arbitrary source code or prove all software correct |
| Runtime | Execute a supported transition against trusted fixture state atomically | Decide business intent or supply human authority |
| Provider adapters | Suggest typed interpretations with bounded external calls | Write source, mint receipts, approve or apply |
| Evidence gate | Check subject identity, observation shape/coverage, compatibility and local integrity | Claim field validity, independent review or human comprehension |
| Local owner | Select meaning and acknowledge the exact local revision | Stand in for institutional SSO or separation of duties |

## Domain-driven design decisions

The model is not a generic `AgentManager` carrying dictionaries between vendors. The vocabulary is explicit: **Change Case, Meaning Selection, Semantic Transaction, Workflow Definition, Preview Instance, Evidence Receipt, Review Packet, Local Decision, Effect Intent**. Each has a different lifecycle and trust meaning. The central aggregate is the Change Case; workflow instances own their own optimistic versions and committed operations. An active baseline pointer supplies a separate compare-and-swap boundary across cases.

The strategic boundaries are Authoring, Execution, Assurance, Governance and Provider Integration. They are modules in one process, not five network services. The provider port is an anti-corruption boundary: vendor response envelopes, tokens and process details stop in the adapters. SQLite and HTTP types do not enter the domain/application layers. A structural test enforces that dependency direction. The application-owned UnitOfWork port names both authoring and execution operations so their required atomicity is visible.

Some persisted event/artifact payloads remain JSON dictionaries; this is not a claim of exhaustive static typing. Pydantic forbids extra input fields and validates declared domain contracts. Static type checking, lint-tool automation and a complete dependency vulnerability audit were not run. Add them before a production release rather than implying test success substitutes for them.

## Essential invariants

A proposal has no selected meaning until the local owner makes a supported selection. Provider wording never changes canonical authority labels. Unknown guards/effects are rejected, not ignored. A teacher cannot approve. Recommendation requires an active currently assigned actor. Current authority is checked before replaying an earlier success. An operation identifier is bound to actor, target, command and model. A stale aggregate or baseline cannot be silently overwritten.

The displayed runtime result comes from the committed database operation. A failed transaction leaves no partial accepted state, audit or notification intent. Local notifications are queued synthetic effects, never sent. Claims are explicitly separated from decisions: the technical gate can be eligible while human understanding remains UNKNOWN. The exact reviewed subject binds semantics, presentation, implementation, policy, environment and harness. An edit cannot carry a prior approval forward without checking that subject again.

## The hard trade-offs

**Narrow semantics versus apparent flexibility.** The hard-coded excursion policy is intentional. It permits a falsifiable demonstration of coherent behaviour, rather than a generic editor that accepts meanings it cannot execute or validate. Adding another domain requires a new reviewed policy/oracle/fixture boundary; it is not just supplying a clever prompt.

**Single process versus services.** One process reduces deployment and consistency complexity for a local one-owner POC. SQLite serializes writes. It is not designed for multi-tenant throughput or multiple UI servers against one workspace. A provider single-flight lock is process-local, not distributed deduplication.

**Local integrity versus external attestation.** HMAC seals detect tampering relative to a workspace key. A hash identifies bytes; neither establishes that the implementer, oracle or review was correct. An adversarial process with the same OS-user permissions can alter source, read secrets and impersonate the owner. This is an explicit trusted-host assumption, not a solved security problem.

**Synthetic coverage versus empirical validation.** The candidate matrix covers the defined five actors × five states × five actions. It does not enumerate arbitrary event sequences, every timing interleaving or real human behaviour. The runtime and oracle have shared authorship. Independent holdout tests and a counterbalanced human study remain unrun.

**Helpful AI versus unverifiable autonomy.** The current AI role is constrained interpretation, not an autonomous full-stack coding agent. This makes the authority boundary demonstrable. Future repository editing needs a separate process/container capability boundary, independent verifier credentials, provenance of generated code, explicit spend limits and separate human authority—not simply more permissions on this adapter.

## Readiness gates, in order

1. **Live connector gate:** on the target machine, execute one synthetic OpenRouter call and one saved-ChatGPT Codex call; record model/CLI version, refusal behaviour, schema support, timeout and usage observations. Do not mark ready from configuration alone.
2. **Target platform and browser gate:** run the supplied actual browser-network test on Mac/Windows, including session launch and download. Validate file permissions, Codex process cancellation and restart behaviour there.
3. **Independent assurance gate:** assign a different author a hidden mutation set, schema/receipt adversarial inputs, crash/replay races and a source/credential-boundary review. No “overall safety score” may offset a failing authority test.
4. **Human-value gate:** counterbalance equivalent review tasks against a code/test baseline; measure correctness, critical omissions, elapsed time, supervision/rework and delayed understanding. Predefine stop criteria and keep raw anonymised observations.
5. **Expansion gate:** only then introduce a second bounded domain and evaluate whether the same abstractions still fit. Institutional authentication, repository automation, formal proof backends and multi-user collaboration are separate changes with new threat models.

No release claim requires pretending these gates have already passed. The immediate handoff is a functioning, inspectable testbed on which to run them.
