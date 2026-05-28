#!/usr/bin/env bash
# Post-Write/Edit hook: lint the changed file based on its extension
# Called with $1 = file path that was written/edited

set -euo pipefail

FILE="$1"

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
