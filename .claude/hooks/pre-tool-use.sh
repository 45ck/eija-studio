#!/bin/sh
# noslop Claude Code hook (PreToolUse, Bash): a best-effort TRIPWIRE for quality-bypass attempts. Exit code 2 blocks
# the tool call. It is not a security control: an agent with shell access can always evade a text match (aliases,
# scripts, editing files with a redirect). The real control is review of any diff that touches .githooks/ or .claude/.
# Works without jq: it greps the raw JSON payload, which is conservative (it may over-block a command that merely
# mentions a bypass in text; the patterns below are the ones known to skip the pre-commit/pre-push gates).
INPUT=$(cat)

block() { echo "noslop: $1" >&2; exit 2; }
has() { printf '%s' "$INPUT" | grep -qiE -- "$1"; }

has 'no-verify' && block "the no-verify flag bypasses the pre-commit/pre-push gates (nox -t fast / nox -t full)."
# `git commit -n` and clusters such as `-nm`/`-anm` are the short form of the same bypass.
has 'git[^|;&"]* commit[^|;&"]* -[a-zA-Z]*n[a-zA-Z]*( |"|$)' && block "git commit -n skips the commit hooks."
has 'core\.hooksPath' && block "overriding core.hooksPath disables the repository hooks."
has '(^|[ "])(HUSKY|SKIP|SKIP_CI)=' && block "hook-skip environment variables are not allowed."
has 'SKIP_CI|\[skip ci\]' && block "CI-skip patterns are not allowed."
exit 0
