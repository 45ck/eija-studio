# HCI

Status as of 2026-09-29: **open PR #7, not on `main`.** ADR block 0039-0040.

Goal: measured usability budgets for the running Studio, from established laws and standards: Fitts' law, Hick-Hyman, KLM-GOMS, WCAG 2.2 and Doherty response-time thresholds. Instrumentation uses a real browser (Playwright) and axe-core; a missing browser reports `NOT_RUN`.

What it will and will not claim:

* Predictions from a model (for example KLM-GOMS) are predictions, not observations of people.
* An automated accessibility scan finds some WCAG failures. It does not establish conformance.
* A synthetic test is never a human study. Human comprehension stays `UNKNOWN` until a real study exists.

See also the [visual lane](visual.md), whose UI this lane measures, and the [roadmap](../ROADMAP.md).
