#!/bin/sh
# noslop Claude Code hook (PreToolUse, Bash): block quality-bypass attempts. Exit code 2 blocks the tool call.
# Works without jq: it greps the raw JSON payload, which is conservative (it may over-block a command that merely
# mentions a bypass flag in text; it never under-blocks one that contains it).
INPUT=$(cat)

if printf '%s' "$INPUT" | grep -qF -- '--no-verify'; then
  echo "noslop: --no-verify bypasses the pre-commit/pre-push gates (nox -t fast / nox -t full)." >&2
  exit 2
fi
if printf '%s' "$INPUT" | grep -qiE 'SKIP_CI|\[skip ci\]'; then
  echo "noslop: CI-skip patterns are not allowed." >&2
  exit 2
fi
exit 0
