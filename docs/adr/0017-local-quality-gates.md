# ADR-0017: Local quality gates with nox sessions and noslop enforcement

* Status: accepted
* Date: 2026-09-28

## Context and problem statement

Hosted CI is not currently available for this repository. Agents and humans still need one command that reproduces every gate, and hooks that stop gate bypasses.

## Considered options

* nox sessions, plus noslop hooks and agent guardrails (chosen)
* tox, or a Makefile/justfile
* A custom Python gate runner (rejected: it would reinvent nox)

## Decision outcome

`noxfile.py` loads one module per gate family from `quality/sessions/`, tagged `fast`, `full` or `release`. [noslop](https://github.com/45ck/noslop) installs git hooks and agent guardrails that run those tiers and block `--no-verify`. Heavy sessions run serially. The GitHub workflow is kept, but it runs only on manual `workflow_dispatch` until hosted CI is enabled.

### Consequences

* Plugin modules let parallel lanes add gates without merge conflicts.
* Gate results are local evidence, not remote attestation. Reports record which machine and platform produced them.
