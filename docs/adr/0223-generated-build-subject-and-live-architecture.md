# ADR-0223: one generated build subject for architecture and runtime observations

* Status: accepted
* Date: 2026-10-11

This decision covers the local preview implementation. Acceptance runs remain separate evidence.

## Context

A workflow semantic hash does not identify its data, screens, generator templates or installed implementation. C4 previously reread the pack's data after generation, and the UI could associate an older running app with a new structural view merely because their workflows matched. A process could also keep running while its generated payload was replaced.

## Decision

Derive `eija.build-subject.v1` from one generated file snapshot. Bind exact workflow content and semantic identity, pack, data, screens, template bytes, installed implementation and generated payload. The subject envelope is excluded from its own payload hash. The generator, C4 projection and generated `/api/app` expose the same subject. Source changes during generation fail closed.

Measure the installed implementation again when a generated server starts. Refuse `BUILD_IMPLEMENTATION_MISMATCH` if it differs from the archived subject; never execute new kernel bytes while reporting the old identity. Include app generator templates in the core implementation manifest used by review evidence and approval, so a template-only change also makes earlier evidence stale. Archived subjects and history remain readable.

Use the same generated identity check before and after conformance tests. The build service independently compares the captured subject, payload inventory and measured implementation at both boundaries before publishing the result. A runner's successful exit cannot produce a passing result when the measured inputs changed during the run.

Read C4 contracts from those generated files. Context, container and component views identify declared structure and source provenance; they do not imply observed deployment or external integration. Reuse the existing component/deployment projections and semantic kernel.

Before replacing a changed generated payload, stop its running process. Identical owned bytes may stay in place and retain the process while conformance is checked again. Unowned output remains refused, and record data is retained under the existing revision refusal policy.

Runtime messages identify the build subject, workflow and recording nonce. The parent also checks the expected frame and origin, typed vocabulary, operation identity and record version. Committed outcomes animate their corresponding edge; refusals show the attempted baseline. Pause and replay use observations already received and never submit application actions.

## Consequences and verification

Same-workflow changes to data, screens, templates or implementation now invalidate the match. Historical observations remain scoped to their recording. Missing, inconsistent and stale subjects disable tracing without preventing ordinary standalone app use. This is local observation integrity, not cryptographic proof or an adversarial same-OS-user boundary.

Tests substitute individual subject inputs, mutate data after generation, change source during generation, tamper with payload bytes and check exact process reuse/replacement. Browser journeys additionally check committed actions, refusal, stale/foreign messages and replay without writes. `SOURCE_REVIEW_REQUIRED` and owner authority remain unchanged; no receipt or trust fixture is restamped.
