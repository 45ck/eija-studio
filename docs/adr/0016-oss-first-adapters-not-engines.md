# ADR-0016: OSS first: build adapters, not engines

* Status: accepted
* Date: 2026-09-28

## Context and problem statement

EIJA's value is the assurance kernel: meaning selection, typed semantic transactions, subject-bound evidence and separated human authority. Rebuilding diagram renderers, model checkers, proof checkers, property-test engines, mutation testers, linters or tracing tools would dilute that value and be less trustworthy than mature open source.

## Decision outcome

Every capability first adopts existing open source (see [docs/oss/REGISTER.md](../oss/REGISTER.md)). Custom code is limited to EIJA-specific glue:

* **generators** that project the executable model into a tool's input format,
* **adapters** that turn the tool's output into typed EIJA evidence, and
* the **kernel** itself.

This follows the ProofMap Lite doctrine (<https://github.com/45ck/proofmap-lite>). Each custom module records, in the register or its ADR, the OSS it checked, why adapter or dependency use was insufficient, and the path to replace or fork it.

### Consequences

* Good: less code to trust, and mature tools that carry their own V&V history.
* Bad: more external prerequisites (Java for TLC, Docker or WSL for Bend, Chromium for HCI probes). Each gate states its prerequisite, and a missing one reports `NOT_RUN`, never `PASS`.
