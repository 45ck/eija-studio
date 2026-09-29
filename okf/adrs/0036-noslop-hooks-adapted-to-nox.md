---
type: Architecture Decision Record
title: 'ADR-0036: noslop guardrails adapted to run nox tiers; hook enablement is an explicit step'
description: 'noslop installs git hooks and agent guardrails, but `noslop init` writes a generic Python pack: `black`, `ruff select=ALL`, `typos`, `mypy .`, plain `pytest`.'
resource: repo://docs/adr/0036-noslop-hooks-adapted-to-nox.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0036-noslop-hooks-adapted-to-nox.md
  title: 0036-noslop-hooks-adapted-to-nox.md
  hash_method: lf-sha256-v1
  sha256: 46f989262de4cdcca589bb568a7b0fb42e1388594662afa640878e2b48372b09
notes_baseline: ac7dd92c33bd7b8566e5bcade5379ba597be408016030f08e040a0870b4ed3d3
---

# ADR-0036: noslop guardrails adapted to run nox tiers; hook enablement is an explicit step

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-28 |
| Lane | quality |
| Source | `repo://docs/adr/0036-noslop-hooks-adapted-to-nox.md` |

## Decision outcome (verbatim)

> Chosen option: the second. The generated files were kept where sound and changed where not:
>
> * `.githooks/pre-commit` and `pre-push` delegate to `.githooks/run-nox`, which locates the venv interpreter for Windows or POSIX, keeps temp files inside the checkout, and fails with an install instruction if nox is absent.
> * `commit-msg` keeps the Conventional Commits check but allows git-generated merge and revert subjects and validates only the subject line.
> * `.claude/hooks/pre-tool-use.sh` blocks bypass flags with exit code 2 and no longer refuses every command when `jq` is missing (the generated version did). It is registered in `.claude/settings.json`, which the generated file did not do. **Claude Code reads `.claude/settings.json` automatically, so unlike the git hooks this is repo-wide behaviour for agents, not opt-in.** The first version denied `Bash(*--force*)` and grepped the whole payload, which also blocked `git worktree remove --force`, `--force-reinstall` and any text that merely mentioned a flag. It now denies only force-pushes and `--no-verify` on `git commit`/`git push`, matches the flag only inside those commands, and locates itself through `$CLAUDE_PROJECT_DIR` (a relative path failed open from any other working directory). Covered by `tests/tools/test_claude_hook.py`.
> * The generated workflows are `workflow_dispatch` only. The label-gating guardrail workflow takes a PR number input.
> * `.github/workflows/**` is not in the deny list of agent edits, because docs and release lanes legitimately edit workflows; hook and agent-settings edits stay denied.
>
> The **git hooks** in `.githooks/` are committed but not enabled by this change. The enable step is `git config core.hooksPath .githooks` (see `docs/quality/gates.md`). `noslop doctor` passes 5 of 6 checks and fails that one until then (PARTIAL, expected).
>
> The **Claude Code files in `.claude/` are not gated on that step**: Claude Code loads `.claude/settings.json` automatically, so its deny rules and PreToolUse hook are live in every clone and worktree as soon as this merges. The deny list was narrowed to force-pushes so ordinary worktree removal and `pip --force-reinstall` keep working (`--force-with-lease` pushes are denied too). The hook matches inside a single `git ... commit|push` command segment, so a command that only mentions a flag in quoted text is not blocked. The hook matches known bypass forms (long flag, `git commit -n`, `core.hooksPath`, `HUSKY=`/`SKIP=`); it is a tripwire, not a security control, and review of diffs to `.githooks/` and `.claude/` is the control.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://.claude/settings.json`
* `repo://AGENTS.md`
* `repo://docs/quality/gates.md`
* `repo://pyproject.toml`
* `repo://tests/tools/test_claude_hook.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0017: Local quality gates with nox sessions and noslop enforcement](/adrs/0017-local-quality-gates.md) - Hosted CI is not currently available for this repository.

## Referenced by

* [Quality gates, architecture fitness functions and static analysis](/lanes/0035-quality-gates-architecture-fitness.md) - Capability lane with ADR numbers 0035–0036 reserved.
<!-- okf:generated:end links -->
