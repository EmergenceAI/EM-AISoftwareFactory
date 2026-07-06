#!/bin/bash

# Extract knowledge from repository to knowledge pack structure
# Usage: ./extract_knowledge.sh <repo_path> <repo_name>

set -e

REPO_PATH=$1
REPO_NAME=$2
KNOWLEDGE_DIR="knowledge/repositories/$REPO_NAME"

if [ -z "$REPO_PATH" ] || [ -z "$REPO_NAME" ]; then
    echo "Usage: ./extract_knowledge.sh <repo_path> <repo_name>"
    echo "Example: ./extract_knowledge.sh ~/Documents/Development/em-runtime-ui runtime-ui"
    exit 1
fi

if [ ! -d "$REPO_PATH" ]; then
    echo "Error: Repository path does not exist: $REPO_PATH"
    exit 1
fi

echo "Extracting knowledge from $REPO_PATH to $KNOWLEDGE_DIR"

mkdir -p "$KNOWLEDGE_DIR"

# Get current git hash for tracking
cd "$REPO_PATH"
CURRENT_HASH=$(git log -1 --format=%H -- README.md docs/ 2>/dev/null || echo "unknown")
SYNC_DATE=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# ═══════════════════════════════════════════════════════
# ARCHITECTURE - Extract from README and docs/
# ═══════════════════════════════════════════════════════

cat > "$OLDPWD/$KNOWLEDGE_DIR/architecture.md" << EOF
<!--
AUTO-GENERATED from $REPO_NAME
Last sync: $SYNC_DATE
Source commit: $CURRENT_HASH
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# $REPO_NAME Architecture

## Overview

EOF

# Extract from README.md
if [ -f "README.md" ]; then
    echo "  Extracting from README.md..."

    # Try to extract Architecture section
    if grep -q "^## Architecture" README.md; then
        sed -n '/^## Architecture/,/^## /p' README.md | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
    # Try Overview section
    elif grep -q "^## Overview" README.md; then
        sed -n '/^## Overview/,/^## /p' README.md | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
    # Try Description section
    elif grep -q "^## Description" README.md; then
        sed -n '/^## Description/,/^## /p' README.md | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
    else
        # Just grab the first few paragraphs after title
        sed -n '/^## /,/^## /p' README.md | head -20 >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
    fi
fi

# Extract from docs/architecture.md if exists
if [ -f "docs/architecture.md" ]; then
    echo "  Extracting from docs/architecture.md..."
    echo -e "\n## Detailed Architecture\n" >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
    cat "docs/architecture.md" >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
fi

# Extract from docs/ARCHITECTURE.md if exists
if [ -f "docs/ARCHITECTURE.md" ]; then
    echo "  Extracting from docs/ARCHITECTURE.md..."
    echo -e "\n## Detailed Architecture\n" >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
    cat "docs/ARCHITECTURE.md" >> "$OLDPWD/$KNOWLEDGE_DIR/architecture.md"
fi

# ═══════════════════════════════════════════════════════
# PATTERNS - Extract from docs/ or analyze code
# ═══════════════════════════════════════════════════════

cat > "$OLDPWD/$KNOWLEDGE_DIR/patterns.md" << EOF
<!--
AUTO-GENERATED from $REPO_NAME
Last sync: $SYNC_DATE
Source commit: $CURRENT_HASH
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# $REPO_NAME Coding Patterns

EOF

# Check for existing patterns docs
if [ -f "docs/patterns.md" ]; then
    echo "  Extracting from docs/patterns.md..."
    cat "docs/patterns.md" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
elif [ -f "docs/coding-patterns.md" ]; then
    echo "  Extracting from docs/coding-patterns.md..."
    cat "docs/coding-patterns.md" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
elif [ -f "docs/development.md" ]; then
    echo "  Extracting patterns from docs/development.md..."
    cat "docs/development.md" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
else
    # Auto-detect based on file types
    echo "  Auto-detecting patterns from codebase..."
    echo "## Common Patterns" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
    echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"

    if [ -f "package.json" ]; then
        echo "TypeScript/JavaScript repository - patterns need manual curation" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
    elif [ -f "pyproject.toml" ]; then
        echo "Python repository - patterns need manual curation" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
    fi

    echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
    echo "[NEEDS CURATION: Review codebase and document common patterns]" >> "$OLDPWD/$KNOWLEDGE_DIR/patterns.md"
fi

# ═══════════════════════════════════════════════════════
# CONVENTIONS - Extract from configs
# ═══════════════════════════════════════════════════════

cat > "$OLDPWD/$KNOWLEDGE_DIR/conventions.md" << EOF
<!--
AUTO-GENERATED from $REPO_NAME
Last sync: $SYNC_DATE
Source commit: $CURRENT_HASH
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# $REPO_NAME Coding Conventions

## Code Style

EOF

# Extract from pyproject.toml (Python)
if [ -f "pyproject.toml" ]; then
    echo "  Extracting Python conventions..."
    echo "### Python (from pyproject.toml)" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo '```toml' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"

    # Extract tool configurations
    sed -n '/\[tool\.black\]/,/^\[/p' pyproject.toml | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md" 2>/dev/null || true
    sed -n '/\[tool\.ruff\]/,/^\[/p' pyproject.toml | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md" 2>/dev/null || true
    sed -n '/\[tool\.mypy\]/,/^\[/p' pyproject.toml | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md" 2>/dev/null || true
    sed -n '/\[tool\.pytest\]/,/^\[/p' pyproject.toml | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md" 2>/dev/null || true

    echo '```' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
fi

# Extract from package.json (TypeScript/JavaScript)
if [ -f "package.json" ]; then
    echo "  Extracting TypeScript/JavaScript conventions..."
    echo "### TypeScript/JavaScript (from package.json)" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo '```json' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"

    if command -v jq &> /dev/null; then
        jq '{scripts, eslintConfig, prettier}' package.json 2>/dev/null >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md" || true
    else
        echo "// jq not available - showing full package.json" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    fi

    echo '```' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
fi

# Extract from .eslintrc or .prettierrc
if [ -f ".eslintrc.json" ]; then
    echo "  Extracting ESLint config..."
    echo "### ESLint Config" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo '```json' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    cat .eslintrc.json >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo '```' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
fi

if [ -f ".prettierrc" ]; then
    echo "  Extracting Prettier config..."
    echo "### Prettier Config" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo '```json' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    cat .prettierrc >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo '```' >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
fi

# Extract testing conventions
echo "## Testing Conventions" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"

if [ -f "pyproject.toml" ]; then
    echo "- Test framework: pytest" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    echo "- Test files: \`tests/test_*.py\`" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
elif [ -f "package.json" ]; then
    if grep -q "vitest" package.json; then
        echo "- Test framework: vitest" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    elif grep -q "jest" package.json; then
        echo "- Test framework: jest" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
    fi
    echo "- Test files: \`**/*.test.ts\` or \`**/*.spec.ts\`" >> "$OLDPWD/$KNOWLEDGE_DIR/conventions.md"
fi

# ═══════════════════════════════════════════════════════
# DEPENDENCIES - Extract from package files
# ═══════════════════════════════════════════════════════

cat > "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md" << EOF
<!--
AUTO-GENERATED from $REPO_NAME
Last sync: $SYNC_DATE
Source commit: $CURRENT_HASH
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# $REPO_NAME Dependencies

## External Dependencies

EOF

# Extract from pyproject.toml
if [ -f "pyproject.toml" ]; then
    echo "  Extracting Python dependencies..."
    echo "### Python (from pyproject.toml)" >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"
    echo '```toml' >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"
    sed -n '/\[tool\.poetry\.dependencies\]/,/^\[/p' pyproject.toml | sed '$d' >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md" 2>/dev/null || true
    echo '```' >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"
    echo "" >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"
fi

# Extract from package.json
if [ -f "package.json" ]; then
    echo "  Extracting JavaScript/TypeScript dependencies..."
    echo "### JavaScript/TypeScript (from package.json)" >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"
    echo '```json' >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"

    if command -v jq &> /dev/null; then
        jq '{dependencies, devDependencies}' package.json 2>/dev/null >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md" || true
    else
        echo "// jq not available" >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"
    fi

    echo '```' >> "$OLDPWD/$KNOWLEDGE_DIR/dependencies.md"
fi

cd "$OLDPWD"
echo "✓ Knowledge pack created at $KNOWLEDGE_DIR"
