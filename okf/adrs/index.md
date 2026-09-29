# Architecture decision records

# Sections

* [poc](poc/) - The fourteen POC decisions ADR-001 to ADR-014 from the decision log

# Architecture Decision Records

* [ADR-0000: v0.2 proof-of-concept decision log (ADR-001 … ADR-014)](0000-poc-decision-log.md) - These fourteen decisions shipped with EIJA Studio 0.2.0 and are kept verbatim as one log.
* [ADR-0015: Publish EIJA Studio as open source under Apache-2.0](0015-open-source-under-apache-2.md) - The v0.2 package left the distribution licence undecided (NOTICE.md).
* [ADR-0016: OSS first: build adapters, not engines](0016-oss-first-adapters-not-engines.md) - EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority.
* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](0017-local-quality-gates.md) - Hosted CI is not currently available for this repository.
* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
* [ADR-0019: Diagrams are generated projections of the executable model](0019-diagrams-generated-from-executable-model.md) - Reviewers need to see what a change, usually an agent's change, does: state machines, sequences, classes, journeys and ripple effects.
* [ADR-0020: Proposal providers for Codex, Claude Code, OpenCode, Gemini CLI and OpenRouter](0020-multi-provider-agent-adapters.md) - People use different agent CLIs, often with subscription logins rather than API keys.
* [ADR-0045: An OKF v0.2 knowledge base deterministically linked to code](0045-okf-knowledge-base-linked-to-code.md) - Humans and agents need a place to start reading EIJA that is smaller than the repository and does not go stale.
* [ADR-0046: Code-link hash methods and STALE semantics](0046-code-link-hash-methods-and-stale-semantics.md) - ADR-0045 links wiki pages to code with content hashes.
