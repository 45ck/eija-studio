# ADR-0224: approve the exact generated application

* Status: accepted for supported workflow activation
* Date: 2026-10-11

## Context

The exact workflow transfer preserved typed edits, but an owner decision did not identify the complete generated app. A matching workflow could still have different fields, screens, templates or runtime bytes. Generated conformance and owner review described different subjects.

## Decision

An optional `eija.generated-app-review.v1` binding extends existing cases. Its subject is the generated build envelope from ADR-0223: workflow, pack, data, screens, templates, implementation and exact emitted payload. The binding also names the conformance checker, Python/platform, arguments, timeout, environment and subprocess isolation policy. The owner-plan request carries the expected build digest; the server independently assembles the candidate and refuses a mismatch.

Freeze that generated bundle for the review case. Remeasure its bytes and the implementation at verification, owner decision, application and subsequent build. A separate sealed conformance observation records the actual subprocess outcome against the binding. Kernel/model checks cannot substitute for generated-app execution, and a submitted `PASS` label cannot override failed or missing execution.

Run the checker with isolated Python, a fresh bytecode cache prefix and a minimal measured environment. Ignoring `.pyc` in source measurement does not make existing bytecode safe to execute. The supported generated entrypoint also isolates its import cache before importing the app.

Bind signed decisions to the case, baseline version, decision kind, scope and subject. Commit the model revision, applied case and generated-app association in the same SQLite transaction with the existing version checks. A duplicate application cannot advance the baseline again. A later generated build receives `ACTIVE_APPROVED` only when it matches the stored association and valid applied case. Missing or corrupt provenance is unavailable evidence.

Historical cases without this binding remain workflow-only. Do not rewrite their receipts or display an exact-app approval badge. Initially, activation still accepts workflow edits under unchanged pack identity; edited laws, schemas, vocabulary and screens remain drafts.

## Consequences

The interface can explain which application is being reviewed and whether its evidence is current. Approval remains separate from activation. A recorded failure followed by a successful rerun is conflicting evidence; recovery requires a new case until an explicit supersession contract exists.

The bound digest establishes identity, not correctness. Conformance covers the existing bounded kernel oracle; browser usability, accessibility, real integrations and production authority require their own evidence. `SOURCE_REVIEW_REQUIRED` remains enforced. Disposable synthetic owner fixtures exercise the implementation but never authorize the normal checkout.

## Verification

Require mismatched expected builds, changed payload/source/templates/data/screens, missing or failed execution, stale evidence, cross-case decisions and concurrent baseline changes to refuse without activation. Observe atomic application, duplicate refusal and a fresh-process reopen of the exact generated app. Independent unsafe implementation controls must be caught by behavioral assertions. Retain normal source-gate evidence separately from the synthetic owner journey.
