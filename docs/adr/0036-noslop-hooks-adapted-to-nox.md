# ADR-0036: noslop guardrails adapted to run nox tiers; hook enablement is an explicit step

* Status: accepted
* Date: 2026-09-28
* Lane: quality

## Context and problem statement

[noslop](https://github.com/45ck/noslop) installs git hooks and agent guardrails, but `noslop init` writes a generic Python pack: `black`, `ruff select=ALL`, `typos`, `mypy .`, plain `pytest`. Run in this repository it also replaced `pyproject.toml` and `AGENTS.md` wholesale. The repository already defines its gates as nox tiers (ADR-0017), and git's `core.hooksPath` is repository configuration shared by every worktree while many lanes are mid-flight.

## Decision drivers

* One definition of "the gates": the nox tiers, not a second list inside a hook.
* Hooks must work from Git Bash on Windows and from POSIX shells, in any worktree, without `jq`.
* Enabling a hook must never silently pass when its tools are missing (NOT_RUN, not PASS), and must not block other lanes without warning.
* Hosted CI is unavailable, so generated workflows must be manual-only.

## Considered options

* Use `noslop check` as generated (rejected: enforces a different gate set than nox and fails on the existing tree)
* Adapt noslop's hooks to call `nox -t fast` on pre-commit and `nox -t full` on pre-push; keep its commit-msg and Claude guardrails (chosen)
* Run `git config core.hooksPath .githooks` as part of the lane (rejected: shared repository config that would start enforcing in other worktrees as soon as they merge main, before their venvs have the lint extra)

## Decision outcome

Chosen option: the second. The generated files were kept where sound and changed where not:

* `.githooks/pre-commit` and `pre-push` delegate to `.githooks/run-nox`, which locates the venv interpreter for Windows or POSIX, keeps temp files inside the checkout, and fails with an install instruction if nox is absent.
* `commit-msg` keeps the Conventional Commits check but allows git-generated merge and revert subjects and validates only the subject line.
* `.claude/hooks/pre-tool-use.sh` blocks bypass flags with exit code 2 and no longer refuses every command when `jq` is missing (the generated version did). It is registered in `.claude/settings.json`, which the generated file did not do.
* The generated workflows are `workflow_dispatch` only. The label-gating guardrail workflow takes a PR number input.
* `.github/workflows/**` is not in the deny list of agent edits, because docs and release lanes legitimately edit workflows; hook and agent-settings edits stay denied.

The **git hooks** in `.githooks/` are committed but not enabled by this change. The enable step is `git config core.hooksPath .githooks` (see `docs/quality/gates.md`). `noslop doctor` passes 5 of 6 checks and fails that one until then (PARTIAL, expected).

The **Claude Code files in `.claude/` are not gated on that step**: Claude Code loads `.claude/settings.json` automatically, so its deny rules and PreToolUse hook are live in every clone and worktree as soon as this merges. The deny list was narrowed to force-pushes so ordinary worktree removal and `--force-with-lease` keep working. The hook matches known bypass forms (long flag, `git commit -n`, `core.hooksPath`, `HUSKY=`/`SKIP=`); it is a tripwire, not a security control, and review of diffs to `.githooks/` and `.claude/` is the control.

### Consequences

* Good: hooks and manual runs execute the same gates; nothing in the hooks can drift from `nox -t`.
* Good: no repository-wide behaviour change happens as a side effect of merging this lane.
* Bad: until someone runs the enable line, the git hooks protect nothing. The gap is stated in the PR and in `docs/quality/gates.md`.
* Bad: the agent guardrail can be evaded by anyone with a shell; it stops the common accidental forms only.
* Bad: `noslop update` would regenerate and overwrite these adaptations; do not run it without diffing.
* Revisit when: every lane has merged and installed the `lint` extra (then enable hooksPath for all clones), or noslop gains a configurable command per tier.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| noslop 0.1.0 | Its Python pack is not configurable to delegate to nox and its installer overwrites shared files | Delete `.githooks/run-nox` and pass the tier command to noslop if it gains that option |
| pre-commit (framework) | Adds a second gate runner beside nox and needs its own hook environments | none needed |
