"""
Knowledge Pack Sync Module

Automatically syncs knowledge packs from repositories before orchestrator runs.
Only re-extracts if source documentation has changed.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List

SYNC_STATE_FILE = Path(".sync_state.json")
SCRIPT_DIR = Path(__file__).parent.parent

# Repository paths
REPOSITORIES = {
    'runtime': Path.home() / 'Documents/Development/em-runtime',
    'runtime-ui': Path.home() / 'Documents/Development/em-runtime-ui',
    'talk2data': Path.home() / 'Documents/Development/em-talk2data',
    'connectors': Path.home() / 'Documents/Development/em-connectors',
    'sdk': Path.home() / 'Documents/Development/em-sdk',
    'data-readiness': Path.home() / 'Documents/Development/em-data-readiness',
    'semi': Path.home() / 'Documents/Development/em-semi',
}


def get_docs_hash(repo_path: Path) -> str:
    """
    Get git hash of last commit that touched README.md or docs/.

    Args:
        repo_path: Path to repository

    Returns:
        Git commit hash, or 'unknown' if not a git repo
    """
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H', '--', 'README.md', 'docs/'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip() or 'unknown'
    except Exception:
        return 'unknown'


def load_sync_state() -> Dict[str, str]:
    """Load last sync state from file."""
    if SYNC_STATE_FILE.exists():
        try:
            return json.loads(SYNC_STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_sync_state(state: Dict[str, str]) -> None:
    """Save sync state to file."""
    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2))


def extract_knowledge(repo_path: Path, repo_name: str) -> bool:
    """
    Run extraction script for a repository.

    Args:
        repo_path: Path to repository
        repo_name: Name of repository (for knowledge pack)

    Returns:
        True if extraction succeeded
    """
    extract_script = SCRIPT_DIR / 'extract_knowledge.sh'

    try:
        subprocess.run(
            [str(extract_script), str(repo_path), repo_name],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to extract {repo_name}: {e.stderr}")
        return False


def sync_knowledge_if_needed(verbose: bool = True) -> List[str]:
    """
    Sync knowledge packs from repositories if docs have changed.

    Args:
        verbose: Print status messages

    Returns:
        List of repository names that were synced
    """
    if verbose:
        print("🔄 Checking knowledge pack freshness...")

    sync_state = load_sync_state()
    synced_repos = []
    skipped_count = 0

    for repo_name, repo_path in REPOSITORIES.items():
        if not repo_path.exists():
            if verbose:
                print(f"⚠️  {repo_name}: Not found at {repo_path}, skipping")
            continue

        # Get current docs hash
        current_hash = get_docs_hash(repo_path)
        last_hash = sync_state.get(repo_name)

        # Check if extraction needed
        if current_hash != last_hash:
            if verbose:
                print(f"📚 {repo_name}: Docs changed, extracting knowledge...")

            if extract_knowledge(repo_path, repo_name):
                sync_state[repo_name] = current_hash
                synced_repos.append(repo_name)
            else:
                if verbose:
                    print(f"❌ {repo_name}: Extraction failed")
        else:
            if verbose:
                print(f"✅ {repo_name}: Up to date")
            skipped_count += 1

    # Save updated sync state
    if synced_repos:
        save_sync_state(sync_state)

    if verbose:
        if synced_repos:
            print(f"\n✅ Synced {len(synced_repos)} repos: {', '.join(synced_repos)}")
        else:
            print(f"\n✅ All knowledge packs up to date")

        if skipped_count > 0:
            print(f"⏭️  Skipped {skipped_count} repos (no changes)")

    return synced_repos


def force_sync_all(verbose: bool = True) -> List[str]:
    """
    Force sync all repositories regardless of whether docs changed.

    Args:
        verbose: Print status messages

    Returns:
        List of repository names that were synced
    """
    if verbose:
        print("🔄 Force syncing all knowledge packs...")

    synced_repos = []
    sync_state = {}

    for repo_name, repo_path in REPOSITORIES.items():
        if not repo_path.exists():
            if verbose:
                print(f"⚠️  {repo_name}: Not found at {repo_path}, skipping")
            continue

        if verbose:
            print(f"📚 {repo_name}: Extracting knowledge...")

        if extract_knowledge(repo_path, repo_name):
            current_hash = get_docs_hash(repo_path)
            sync_state[repo_name] = current_hash
            synced_repos.append(repo_name)
        else:
            if verbose:
                print(f"❌ {repo_name}: Extraction failed")

    # Save sync state
    if synced_repos:
        save_sync_state(sync_state)

    if verbose:
        print(f"\n✅ Synced {len(synced_repos)} repos")

    return synced_repos


if __name__ == '__main__':
    # Allow running as standalone script
    import sys

    if '--force' in sys.argv:
        force_sync_all()
    else:
        sync_knowledge_if_needed()
