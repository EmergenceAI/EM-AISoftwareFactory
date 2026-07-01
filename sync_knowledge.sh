#!/bin/bash

# Sync all knowledge packs from repositories
# Only re-extracts if source docs have changed

set -e

SYNC_STATE=".sync_state.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Syncing knowledge packs from repositories..."
echo ""

# Repository definitions (name:path)
REPOS=(
    "runtime:$HOME/Documents/Development/em-runtime"
    "runtime-ui:$HOME/Documents/Development/em-runtime-ui"
    "talk2data:$HOME/Documents/Development/em-talk2data"
    "connectors:$HOME/Documents/Development/em-connectors"
    "sdk:$HOME/Documents/Development/em-sdk"
    "data-readiness:$HOME/Documents/Development/em-data-readiness"
    "semi:$HOME/Documents/Development/em-semi"
)

# Load sync state
if [ -f "$SYNC_STATE" ]; then
    SYNC_DATA=$(cat "$SYNC_STATE")
else
    SYNC_DATA="{}"
fi

SYNCED_COUNT=0
SKIPPED_COUNT=0
SYNCED_REPOS=()

for repo_entry in "${REPOS[@]}"; do
    repo="${repo_entry%%:*}"
    repo_path="${repo_entry#*:}"

    if [ ! -d "$repo_path" ]; then
        echo "⚠️  $repo: Repository not found at $repo_path, skipping"
        continue
    fi

    # Get current hash of docs
    cd "$repo_path"
    CURRENT_HASH=$(git log -1 --format=%H -- README.md docs/ 2>/dev/null || echo "unknown")
    cd "$SCRIPT_DIR"

    # Get last known hash
    LAST_HASH=$(echo "$SYNC_DATA" | grep -o "\"$repo\":\"[^\"]*\"" | cut -d'"' -f4)

    if [ "$CURRENT_HASH" != "$LAST_HASH" ] || [ -z "$LAST_HASH" ]; then
        echo "📚 $repo: Docs changed, extracting knowledge..."
        ./extract_knowledge.sh "$repo_path" "$repo"

        # Update sync state
        if [ "$SYNC_DATA" = "{}" ]; then
            SYNC_DATA="{\"$repo\":\"$CURRENT_HASH\"}"
        else
            # Remove existing entry for this repo if exists
            SYNC_DATA=$(echo "$SYNC_DATA" | sed "s/\"$repo\":\"[^\"]*\",\?//g" | sed 's/,,/,/g' | sed 's/,}/}/g')
            # Add new entry
            SYNC_DATA=$(echo "$SYNC_DATA" | sed "s/}/,\"$repo\":\"$CURRENT_HASH\"}/")
        fi

        SYNCED_COUNT=$((SYNCED_COUNT + 1))
        SYNCED_REPOS+=("$repo")
    else
        echo "✅ $repo: Up to date"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    fi
done

# Save sync state
echo "$SYNC_DATA" > "$SYNC_STATE"

echo ""
if [ $SYNCED_COUNT -gt 0 ]; then
    echo "✅ Synced $SYNCED_COUNT repos: ${SYNCED_REPOS[*]}"
else
    echo "✅ All knowledge packs up to date"
fi

if [ $SKIPPED_COUNT -gt 0 ]; then
    echo "⏭️  Skipped $SKIPPED_COUNT repos (no changes)"
fi
