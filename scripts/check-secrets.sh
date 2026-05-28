#!/usr/bin/env bash
# Pre-commit hook: scan staged files for potential secrets
# Blocks commit if secrets are detected

set -euo pipefail

# Patterns that indicate secrets/credentials
SECRET_PATTERNS=(
  'AKIA[0-9A-Z]{16}'                          # AWS Access Key ID
  '[0-9a-zA-Z/+]{40}'                         # AWS Secret Key (40-char base64)
  'sk-[a-zA-Z0-9]{48}'                        # OpenAI API Key
  'sk-ant-[a-zA-Z0-9-]{95}'                   # Anthropic API Key
  'ghp_[a-zA-Z0-9]{36}'                       # GitHub Personal Access Token
  'gho_[a-zA-Z0-9]{36}'                       # GitHub OAuth Token
  'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}' # GitHub Fine-Grained PAT
  'xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}' # Slack Bot Token
  'xoxp-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}' # Slack User Token
  'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}' # JWT Token
  'password\s*[:=]\s*["\x27][^"\x27]{8,}'     # Hardcoded passwords
  'api[_-]?key\s*[:=]\s*["\x27][^"\x27]{16,}' # API keys
  'secret\s*[:=]\s*["\x27][^"\x27]{16,}'      # Generic secrets
)

# Files to always skip
SKIP_PATTERNS='\.lock$|node_modules|\.min\.|dist/|build/|\.claude/cache/'

FOUND_SECRETS=0

# Check staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

for FILE in $STAGED_FILES; do
  # Skip binary files, lock files, and build artifacts
  if echo "$FILE" | grep -qE "$SKIP_PATTERNS"; then
    continue
  fi

  if [ ! -f "$FILE" ]; then
    continue
  fi

  for PATTERN in "${SECRET_PATTERNS[@]}"; do
    if grep -qEn "$PATTERN" "$FILE" 2>/dev/null; then
      if [ $FOUND_SECRETS -eq 0 ]; then
        echo "SECRET DETECTION: Potential secrets found in staged files:"
        echo ""
      fi
      echo "  $FILE:"
      grep -nE "$PATTERN" "$FILE" 2>/dev/null | head -3 | while read -r line; do
        echo "    $line"
      done
      FOUND_SECRETS=1
    fi
  done
done

if [ $FOUND_SECRETS -eq 1 ]; then
  echo ""
  echo "Please remove secrets before committing."
  echo "Use environment variables instead of hardcoded credentials."
  exit 1
fi

exit 0
