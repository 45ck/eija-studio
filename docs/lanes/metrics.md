# Metrics

Status as of 2026-09-29: **open PR #12, not on `main`.** ADR block 0037-0038.

Goal: quantitative models of the kernel and its use, reported with their assumptions. Planned scope: package structure and coupling metrics from existing OSS collectors (radon, grimp), latency measurements, fitted scaling models and a dashboard.

Ground rules that apply from the start:

* One collector per metric. The metrics lane owns collection; quality gates consume its output; nothing else re-measures it.
* A prediction is labelled a prediction and a measurement is labelled a measurement, with the platform that produced it.
* Committed snapshots are deterministic and have a drift check.
* No metric is presented as a measure of correctness or of human benefit.

Until this lane lands, the only measured results are in [Verification](../verification/VERIFICATION.md).
