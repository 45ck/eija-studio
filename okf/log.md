# Update log

## 2026-09-29
* **Integration sync**: regenerated the bundle from the integrated tree (`python -m quality.okf sync`): pages for the ADRs added by the lanes and refreshed source hashes; the orphaned `modules/adapters/providers.md` (now the `adapters/providers/` package) and `gates/metrics/metrics-snapshot-fresh.md` (session dropped when the reviewed metrics lane was restored) were deleted. ADR pages now rewrite relative links in the Lane row like the decision outcome, so `../weave/...` no longer breaks the links gate. The Notes of 25 pages were re-read against the source diffs since the lane baseline; six were out of date and were corrected (compile_case, ProposalProvider, Studio.verify, aggregate_status, assess_receipt, integration-test: formal evidence kinds, CONFLICT, the providers package), the other 19 describe code that changed only in type annotations. All 25 were then recorded with `review` as `process:claude-code-integration-phase0` (a self-declared machine actor, tier `machine-confirmed`).
* **Review fixes**: `sync` no longer clears curated Notes (NOTES_STALE until `review`); `verified` entries are bound to prose and source hashes; symbol pages hash same-module private helpers (`ast-v2`); planned techniques and NOT_RUN criteria are labelled in descriptions; ADR-0045 and ADR-0046 are `proposed`.

## 2026-09-28
* **Creation**: Established the OKF v0.2 knowledge base for EIJA Studio, generated from code by `python -m quality.okf sync`. Pages are linked to code by `repo://` resources and content hashes; see [Knowledge base](/index.md).
