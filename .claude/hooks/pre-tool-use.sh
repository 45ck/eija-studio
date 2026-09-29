#!/bin/sh
# noslop Claude Code hook (PreToolUse, Bash): block quality-bypass attempts. Exit code 2 blocks the tool call.
# Works without jq: it inspects the raw JSON payload, but only inside a single `git ... commit|push ...`
# command segment (segments end at ; & |), so a command that merely MENTIONS a bypass flag in text (a PR
# comment, a document) is not blocked. Ordinary force operations that are not history rewrites
# (`git worktree remove --force`, `pip --force-reinstall`) are allowed; force-pushes are denied in
# .claude/settings.json. A best-effort tripwire, not a security control: an agent with shell access can always
# evade a text match, so the real control is review of any diff that touches .githooks/ or .claude/.
INPUT=$(cat)
# The payload with quoted spans (escaped double quotes in the JSON, and single quotes) removed, so the checks
# below that look at flags and config see the command itself and not text inside a commit message or a comment.
UNQUOTED=$(printf '%s' "$INPUT" | sed -E -e 's/\\"([^\]|\\[^"])*\\"//g' -e "s/'[^']*'//g")

GIT='(^|[^[:alnum:]_-])git[[:space:]][^;&|]*(commit|push)[^;&|]*'
if printf '%s' "$INPUT" | grep -qE "${GIT}--no-verify"; then
  echo "noslop: --no-verify bypasses the pre-commit/pre-push gates (nox -t fast / nox -t full)." >&2
  exit 2
fi
if printf '%s' "$INPUT" | grep -qiE "(^|[^[:alnum:]_-])git[[:space:]][^;&|]*commit[^;&|]*(SKIP_CI|\[skip ci\])"; then
  echo "noslop: CI-skip patterns in a commit are not allowed." >&2
  exit 2
fi
# `git commit -n` (and clusters such as -nm, -anm) is the short form of the no-verify flag.
if printf '%s' "$UNQUOTED" | grep -qE "(^|[^[:alnum:]_-])git[[:space:]][^;&|]*commit[^;&|]*[[:space:]]-[a-zA-Z]*n[a-zA-Z]*([[:space:]\"]|$)"; then
  echo "noslop: git commit -n skips the commit hooks (short form of the no-verify flag)." >&2
  exit 2
fi
# Pointing git at another hooks directory disables the repository hooks.
if printf '%s' "$UNQUOTED" | grep -qE "(^|[^[:alnum:]_-])git[[:space:]][^;&|]*core\.hooksPath"; then
  echo "noslop: overriding core.hooksPath disables the repository hooks." >&2
  exit 2
fi
# Hook-skip environment variables, as a shell assignment (HUSKY=0 git commit, export SKIP=...).
if printf '%s' "$UNQUOTED" | grep -qE "(^|[[:space:]\"&;|])(HUSKY|SKIP|SKIP_CI)(_[A-Z_]+)?="; then
  echo "noslop: hook-skip environment variables are not allowed." >&2
  exit 2
fi
exit 0
