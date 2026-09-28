# ADR-0015: Publish EIJA Studio as open source under Apache-2.0

* Status: accepted
* Date: 2026-09-28

## Context and problem statement

The v0.2 package left the distribution licence undecided (NOTICE.md). The owner decided to publish EIJA Studio as open source so that other people and their agents can use and extend it.

## Considered options

* Apache-2.0: permissive, with an explicit patent grant and a NOTICE mechanism; common for developer tooling.
* MIT: permissive and shorter, but with no explicit patent grant.
* AGPL-3.0: strong copyleft; would discourage embedding the kernel in agent toolchains.

## Decision outcome

Apache-2.0. The explicit patent grant and NOTICE file suit an assurance tool that organisations may embed in their agent pipelines. It also matches Bend (Apache-2.0), which the formal-proof lane uses.

### Consequences

* Contributions are accepted under Apache-2.0 (inbound = outbound).
* The original research packs are not relicensed. Only the files in this repository are covered.
