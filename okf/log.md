# Update log

## 2026-09-29
* **Integration sync**: regenerated the bundle from the integrated tree (`python -m quality.okf sync`): pages for the ADRs added by the lanes, refreshed source hashes, and `modules/adapters/providers.md` marked deprecated because `adapters/providers.py` became the `adapters/providers/` package. ADR pages now rewrite relative links in the Lane row like the decision outcome, so `../weave/...` no longer breaks the links gate. Curated Notes on 25 pages are still NOTES_STALE until they are re-read (`python -m quality.okf review`).
* **Review fixes**: `sync` no longer clears curated Notes (NOTES_STALE until `review`); `verified` entries are bound to prose and source hashes; symbol pages hash same-module private helpers (`ast-v2`); planned techniques and NOT_RUN criteria are labelled in descriptions; ADR-0045 and ADR-0046 are `proposed`.

## 2026-09-28
* **Creation**: Established the OKF v0.2 knowledge base for EIJA Studio, generated from code by `python -m quality.okf sync`. Pages are linked to code by `repo://` resources and content hashes; see [Knowledge base](/index.md).
