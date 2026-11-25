#!/usr/bin/env bash
# Post-Write/Edit hook: lint the changed file based on its extension.
# Claude Code passes hook input as JSON on stdin; Edit/Write put the edited
# file's path in .tool_input.file_path. A path passed as $1 (manual runs)
# still works.

set -euo pipefail

FILE="${1:-}"
if [ -z "$FILE" ] && [ ! -t 0 ]; then
  FILE="$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
fi

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  exit 0
fi

EXT="${FILE##*.}"

case "$EXT" in
  py)
    # Python: use ruff if available
    if command -v uvx &>/dev/null; then
      uvx ruff check --fix "$FILE" 2>/dev/null || true
      uvx ruff format "$FILE" 2>/dev/null || true
    elif command -v ruff &>/dev/null; then
      ruff check --fix "$FILE" 2>/dev/null || true
      ruff format "$FILE" 2>/dev/null || true
    fi
    ;;
  ts|tsx|js|jsx|mjs|cjs)
    # JS/TS: use eslint if available, then prettier
    if command -v npx &>/dev/null; then
      npx --no-install eslint --fix "$FILE" 2>/dev/null || true
      npx --no-install prettier --write "$FILE" 2>/dev/null || true
    fi
    ;;
  css|scss|json|md|yaml|yml)
    # Prettier-compatible formats
    if command -v npx &>/dev/null; then
      npx --no-install prettier --write "$FILE" 2>/dev/null || true
    fi
    ;;
esac

exit 0
