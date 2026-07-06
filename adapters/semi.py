"""
EM Semi Repository Adapter

Handles Docker-based microservices architecture.
"""

from pathlib import Path
from typing import Dict, List, Optional
from .base import RepositoryAdapter


class SemiAdapter(RepositoryAdapter):
    """Adapter for EM Semi - Docker microservices platform."""

    def __init__(self, repo_path: str):
        super().__init__(repo_path)
        self.repo_type = "docker-microservices"

    def get_metadata(self) -> Dict:
        """Get repository metadata."""
        return {
            'name': 'semi',
            'display_name': 'EM Semi',
            'type': self.repo_type,
            'language': 'python',
            'build_system': 'docker',
            'test_framework': 'pytest',
            'description': 'Semiconductor fabrication platform with AI-assisted analysis',
            'has_docker': True,
            'has_docker_compose': True,
            'architecture': 'microservices'
        }

    def build(self) -> bool:
        """
        Build the Docker containers.

        Returns:
            True if build succeeded
        """
        result = self.run_command(['docker-compose', 'build'])
        return result.returncode == 0

    def test(self) -> bool:
        """
        Run tests in Docker containers.

        Returns:
            True if all tests passed
        """
        # Run tests in test container
        result = self.run_command([
            'docker-compose',
            'run',
            '--rm',
            'backend',
            'pytest',
            'tests/',
            '-v'
        ])
        return result.returncode == 0

    def lint(self) -> bool:
        """
        Run linting checks.

        Returns:
            True if linting passed
        """
        # Run ruff in Docker
        ruff_result = self.run_command([
            'docker-compose',
            'run',
            '--rm',
            'backend',
            'ruff',
            'check',
            '.'
        ])

        # Run mypy in Docker
        mypy_result = self.run_command([
            'docker-compose',
            'run',
            '--rm',
            'backend',
            'mypy',
            '.'
        ])

        return ruff_result.returncode == 0 and mypy_result.returncode == 0

    def format(self) -> bool:
        """
        Format code.

        Returns:
            True if formatting succeeded
        """
        result = self.run_command([
            'docker-compose',
            'run',
            '--rm',
            'backend',
            'ruff',
            'format',
            '.'
        ])
        return result.returncode == 0

    def get_architecture(self) -> str:
        """Get architecture documentation."""
        arch_file = self.repo_path / 'docs' / 'architecture.md'
        if arch_file.exists():
            return arch_file.read_text()

        # Fallback to README
        readme = self.repo_path / 'README.md'
        if readme.exists():
            return readme.read_text()

        return "No architecture documentation found"

    def get_patterns(self) -> str:
        """Get coding patterns documentation."""
        patterns_file = self.repo_path / 'docs' / 'patterns.md'
        if patterns_file.exists():
            return patterns_file.read_text()

        return """# EM Semi Patterns

## Microservices Patterns

### Service Structure
- Each service in its own directory
- Shared library for common code
- MCP servers for AI integration

### Docker Compose
- Development: docker-compose.yml
- Production: docker-compose.prod.yml
- Override files for local dev

### API Patterns
- FastAPI for REST endpoints
- Pydantic models for validation
- OpenAPI/Swagger docs auto-generated

### Database Patterns
- Supabase for PostgreSQL
- Shared library for DB access
- Migrations in alembic

### AI Integration
- MCP servers for tool exposure
- A2A protocol for agent communication
- Prefect for workflow orchestration
"""

    def get_conventions(self) -> str:
        """Get coding conventions."""
        return """# EM Semi Conventions

## Code Style
- Python: PEP 8, Ruff for linting and formatting
- TypeScript: ESLint + Prettier
- Line length: 100 characters

## Directory Structure
```
em-semi/
├── backend/         # FastAPI backend service
├── frontend/        # React dashboard
├── shared/          # Shared Python library
├── mcp-server/      # MCP server for AI tools
├── prefect/         # Workflow definitions
└── docker-compose.yml
```

## Testing
- pytest for backend tests
- Test coverage target: 80%
- Integration tests with Docker
- E2E tests with Playwright

## Docker
- Development mode: Run external deps in Docker, code locally
- Production mode: Everything in Docker
- Use docker-compose for orchestration

## Git Conventions
- Branch: feature/{issue-key}-{description}
- Commit: Conventional commits format
- PR: Auto-review enabled for low/medium risk
"""

    def get_dependencies(self) -> List[str]:
        """Get list of dependencies."""
        deps = []

        # Check for Python dependencies (multiple services)
        for service in ['backend', 'shared', 'mcp-server']:
            pyproject = self.repo_path / service / 'pyproject.toml'
            if pyproject.exists():
                deps.append(f"# {service}")
                deps.append(pyproject.read_text())

        # Check for frontend dependencies
        package_json = self.repo_path / 'frontend' / 'package.json'
        if package_json.exists():
            deps.append("# frontend")
            deps.append(package_json.read_text())

        return deps

    def create_branch(self, branch_name: str) -> bool:
        """Create a new git branch."""
        result = self.run_command(['git', 'checkout', '-b', branch_name])
        return result.returncode == 0

    def start_services(self) -> bool:
        """
        Start Docker services for development.

        Returns:
            True if services started successfully
        """
        result = self.run_command(['docker-compose', 'up', '-d'])
        return result.returncode == 0

    def stop_services(self) -> bool:
        """
        Stop Docker services.

        Returns:
            True if services stopped successfully
        """
        result = self.run_command(['docker-compose', 'down'])
        return result.returncode == 0

    def get_service_logs(self, service_name: Optional[str] = None) -> str:
        """
        Get logs from Docker services.

        Args:
            service_name: Specific service, or None for all

        Returns:
            Service logs
        """
        cmd = ['docker-compose', 'logs', '--tail=100']
        if service_name:
            cmd.append(service_name)

        result = self.run_command(cmd)
        return result.stdout
