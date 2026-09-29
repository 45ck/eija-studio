# POC status

The live checklist for the POC (see [POC-DEFINITION.md](POC-DEFINITION.md)). The landing queue updates it after each
merge. The same checklist is mirrored in the body of the "POC progress tracker" pull request.

## Landing queue

Landings run one at a time, in this order. Each goes through independent review, then fixes, then main merged in,
then every gate on the merge result, then a GIF and a description to the [PR standard](PR-STANDARD.md), then merge.

| # | Item | PR | State |
|---|---|---|---|
| 1 | PR media tooling (`python -m demos pr-gif`) | TBD | queued |
| 2 | smt-bmc review fixes | #25 | queued |
| 3 | agents review fixes | #23 | queued |
| 4 | Evidence kinds: formal proofs admissible in the review packet (ADR 0145–0146) | TBD | queued |
| 5 | Property-based and stateful model-based tests | #24 | queued |
| 6 | TLA+/TLC specification and trace conformance | #22 | queued |
| 7 | Metrics and quantitative models | #12 | queued |
| 8 | OKF v0.2 knowledge base linked to code | #16 | queued |
| 9 | End-to-end test of the whole chain, plus a clean-clone install check | TBD | queued |
| 10 | README, quickstart and hero GIF | #14 | queued |

## After the queue

- Re-record the demo on the redesigned IDE workbench (depends on the UX lane).
- Owner restamps the release fixture at the release checkpoint (owner-only).
