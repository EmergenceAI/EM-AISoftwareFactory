"""
Knowledge Engine - Retrieves semantic knowledge for planning and implementation.

The knowledge engine loads architecture, patterns, conventions, and decisions
from centralized knowledge packs and provides them to the harness.
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml


class KnowledgeEngine:
    """Retrieves semantic knowledge for planning and implementation."""

    def __init__(self, knowledge_root: str):
        """
        Initialize knowledge engine.

        Args:
            knowledge_root: Root directory of knowledge packs
        """
        self.knowledge_root = Path(knowledge_root)
        self.cache: Dict[str, Dict] = {}
        self._foundations_cache: Optional[Dict[str, str]] = None

    def get_repository_knowledge(self, repo_name: str) -> Dict[str, str]:
        """
        Load all knowledge for a repository.

        Args:
            repo_name: Repository name (e.g., 'runtime', 'runtime-ui')

        Returns:
            Dictionary with knowledge categories:
            - architecture: System architecture documentation
            - patterns: Coding patterns and best practices
            - conventions: Code style and conventions
            - dependencies: Dependency information
        """
        # Check cache
        if repo_name in self.cache:
            return self.cache[repo_name]

        repo_knowledge_dir = self.knowledge_root / 'repositories' / repo_name

        if not repo_knowledge_dir.exists():
            print(f"Warning: No knowledge pack found for {repo_name}")
            return {
                'architecture': '',
                'patterns': '',
                'conventions': '',
                'dependencies': ''
            }

        knowledge = {
            'architecture': self._load_markdown(repo_knowledge_dir / 'architecture.md'),
            'patterns': self._load_markdown(repo_knowledge_dir / 'patterns.md'),
            'conventions': self._load_markdown(repo_knowledge_dir / 'conventions.md'),
            'dependencies': self._load_markdown(repo_knowledge_dir / 'dependencies.md')
        }

        # Cache it
        self.cache[repo_name] = knowledge
        return knowledge

    def get_coding_standards(self, language: str) -> str:
        """
        Get coding standards for a programming language.

        Args:
            language: Language name (e.g., 'python', 'typescript')

        Returns:
            Coding standards documentation
        """
        standards_file = self.knowledge_root / 'coding-standards' / f'{language}.md'
        return self._load_markdown(standards_file)

    def get_architecture_decisions(self, topic: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get relevant Architecture Decision Records (ADRs).

        Args:
            topic: Optional topic to search for (searches across all ADRs)

        Returns:
            List of ADRs with 'path', 'title', and 'content'
        """
        adr_dir = self.knowledge_root / 'adr'

        if not adr_dir.exists():
            return []

        if topic:
            return self._search_adrs(adr_dir, topic)

        # Return all ADRs
        adrs = []
        for adr_file in sorted(adr_dir.glob('*.md')):
            content = adr_file.read_text()
            # Extract title from first heading
            title = self._extract_title(content)
            adrs.append({
                'path': str(adr_file),
                'title': title,
                'content': content
            })

        return adrs

    def get_integration_patterns(self) -> str:
        """
        Get cross-repository integration patterns.

        Returns:
            Integration patterns documentation
        """
        patterns_file = self.knowledge_root / 'architecture' / 'integration-patterns.md'
        return self._load_markdown(patterns_file)

    def get_system_design(self) -> str:
        """
        Get overall system design documentation.

        Returns:
            System design documentation
        """
        design_file = self.knowledge_root / 'architecture' / 'system-design.md'
        return self._load_markdown(design_file)

    def clear_cache(self):
        """Clear knowledge cache (useful when knowledge packs are updated)."""
        self.cache.clear()

    # Private methods

    def _load_markdown(self, path: Path) -> str:
        """Load markdown file, return empty string if not found."""
        if not path.exists():
            return ""
        return path.read_text()

    def _search_adrs(self, adr_dir: Path, topic: str) -> List[Dict[str, str]]:
        """Search ADRs by topic (case-insensitive substring match)."""
        matching = []
        topic_lower = topic.lower()

        for adr_file in adr_dir.glob('*.md'):
            content = adr_file.read_text()
            if topic_lower in content.lower():
                title = self._extract_title(content)
                matching.append({
                    'path': str(adr_file),
                    'title': title,
                    'content': content
                })

        return matching

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown (first # heading)."""
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"


    def get_foundations_guidance(self, category: str = 'all') -> Dict[str, str]:
        """
        Get Foundations team guidance (standards, principles, constraints).

        Args:
            category: 'all', 'standards', 'overview', or specific category

        Returns:
            Dictionary with guidance documents
        """
        if self._foundations_cache is None:
            self._load_foundations()

        if category == 'all':
            return self._foundations_cache
        elif category in self._foundations_cache:
            return {category: self._foundations_cache[category]}
        else:
            return {}

    def _load_foundations(self):
        """Load Foundations team guidance from knowledge/foundations/."""
        foundations_dir = self.knowledge_root / 'foundations'

        if not foundations_dir.exists():
            self._foundations_cache = {}
            return

        self._foundations_cache = {}

        # Load overview
        overview_file = foundations_dir / 'overview.md'
        if overview_file.exists():
            self._foundations_cache['overview'] = overview_file.read_text()

        # Load standards
        standards_file = foundations_dir / 'standards.md'
        if standards_file.exists():
            self._foundations_cache['standards'] = standards_file.read_text()

    def get_definition_of_done(self) -> str:
        """
        Get Definition of Done checklist from Foundations standards.

        Returns:
            Definition of Done markdown
        """
        if self._foundations_cache is None:
            self._load_foundations()

        standards = self._foundations_cache.get('standards', '')
        if not standards:
            return ""

        # Extract Definition of Done section
        lines = standards.split('\n')
        in_dod = False
        dod_lines = []

        for line in lines:
            if '## Definition of Done' in line:
                in_dod = True
            elif in_dod and line.startswith('## ') and 'Definition of Done' not in line:
                break
            elif in_dod:
                dod_lines.append(line)

        return '\n'.join(dod_lines)

    def get_engineering_principles(self) -> str:
        """
        Get Engineering Principles from Foundations standards.

        Returns:
            Engineering Principles markdown
        """
        if self._foundations_cache is None:
            self._load_foundations()

        standards = self._foundations_cache.get('standards', '')
        if not standards:
            return ""

        # Extract Engineering Principles section
        lines = standards.split('\n')
        in_principles = False
        principles_lines = []

        for line in lines:
            if '## Engineering Principles' in line:
                in_principles = True
            elif in_principles and line.startswith('## ') and 'Engineering Principles' not in line:
                break
            elif in_principles:
                principles_lines.append(line)

        return '\n'.join(principles_lines)

    def get_air_gapped_requirements(self) -> str:
        """
        Get air-gapped deployment requirements.

        Returns:
            Air-gapped requirements summary
        """
        return """# Air-Gapped Requirements (CRITICAL)

From Foundations Engineering Principles:

## Every service MUST work in air-gapped, bare-metal Kubernetes

- Application code CANNOT depend on cloud-specific APIs, IAM or managed services
- Helm charts MUST deploy successfully without cloud provider access
- Cloud-managed services (Cloud SQL, Memorystore) are environment overrides, NOT baseline
- This is NOT aspirational - em-runtime ships to customer environments

## Allowed Infrastructure Dependencies (via Crossplane)

- PostgreSQL (Cloud SQL on GCP, CloudNativePG air-gapped)
- Redis (Memorystore on GCP, Redis operator air-gapped)
- S3-compatible buckets (Cloud Storage on GCP, local PV with obstore air-gapped)
- Secrets (Secret Manager on GCP, Vault air-gapped)

## Everything Else via em-runtime

- Auth: Keycloak
- Authz: OpenFGA
- Assets, governance

## Test Air-Gapped Compatibility

Before merging, verify:
- ✅ No cloud-specific API calls (GCP, AWS, Azure)
- ✅ No hardcoded cloud endpoints
- ✅ Helm chart deploys without cloud provider
- ✅ Uses Crossplane claims for infra, not cloud-specific resources
"""


# Convenience function for quick access
def load_knowledge(workspace_root: Path, repo_name: str) -> Dict[str, str]:
    """
    Convenience function to load knowledge for a repository.

    Args:
        workspace_root: Root of the workspace
        repo_name: Repository name

    Returns:
        Knowledge dictionary
    """
    knowledge_root = workspace_root / 'craft-ai-factory' / 'knowledge'
    engine = KnowledgeEngine(knowledge_root)
    return engine.get_repository_knowledge(repo_name)
