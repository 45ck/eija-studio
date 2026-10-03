# Knowledge base

Status as of 2026-09-29: **open PR #16, not on `main`.** ADR block 0045-0046.

Goal: an [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) wiki of the project's concepts, decisions and evidence, deterministically linked to code by content hash so that a stale page is a failing check rather than a silent lie.

The ubiquitous language in [Architecture](../architecture/ARCHITECTURE.md) is the seed vocabulary. Until the lane lands, [ADRs](../adr/README.md) and the [OSS register](../oss/REGISTER.md) are the project's decision memory, and the [roadmap](../ROADMAP.md) is its status memory.

Ground rules: generated pages are deterministic and drift-checked; a link from a page to code names the content it was generated from; no page claims more than its source establishes.
