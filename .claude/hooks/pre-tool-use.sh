#!/bin/sh
# noslop Claude Code hook (PreToolUse, Bash): block quality-bypass attempts. Exit code 2 blocks the tool call.
# Works without jq: it inspects the raw JSON payload, but only inside a single `git ... commit|push ...`
# command segment (segments end at ; & |), so a command that merely MENTIONS a bypass flag in text (a PR
# comment, a document) is not blocked. Ordinary force operations that are not history rewrites
# (`git worktree remove --force`, `pip --force-reinstall`) are allowed; force-pushes are denied in
# .claude/settings.json.
INPUT=$(cat)

GIT='(^|[^[:alnum:]_-])git[[:space:]][^;&|]*(commit|push)[^;&|]*'
if printf '%s' "$INPUT" | grep -qE "${GIT}--no-verify"; then
  echo "noslop: --no-verify bypasses the pre-commit/pre-push gates (nox -t fast / nox -t full)." >&2
  exit 2
fi
if printf '%s' "$INPUT" | grep -qiE "(^|[^[:alnum:]_-])git[[:space:]][^;&|]*commit[^;&|]*(SKIP_CI|\[skip ci\])"; then
  echo "noslop: CI-skip patterns in a commit are not allowed." >&2
  exit 2
fi
exit 0
