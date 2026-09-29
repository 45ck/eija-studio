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
  sha256: 16c957765057ed96b1e45be580deb54b1cd5ddd49f204a8b8d63e61291fd56f2
notes_baseline: eafa3ac00d85a32e824f98c89de8eafdd1fcd68328a6b67c4b3f361978b0e37a
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
> Hooks are committed but not enabled by this change. The enable step is `git config core.hooksPath .githooks` (see `docs/quality/gates.md`). `noslop doctor` reports that single check as failed until then.

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
