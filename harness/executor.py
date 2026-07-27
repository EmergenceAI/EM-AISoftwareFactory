"""
Executor - Orchestrates task execution by delegating to existing skills.

The executor:
1. Routes issues to repositories
2. Loads repository-specific knowledge
3. Invokes /autonomous-implement skill with knowledge context
4. Coordinates multi-repository changes
5. Aggregates and reports results

This is a THIN orchestration layer - it delegates to existing skills
rather than reimplementing the SDLC workflow.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import time


@dataclass
class TaskResult:
    """Result of executing a task in a repository."""
    repository: str
    issue_key: str
    success: bool
    pr_url: Optional[str] = None
    branch_name: Optional[str] = None
    output: str = ""
    error: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class ExecutionResult:
    """Result of executing across one or more repositories."""
    issue_key: str
    tasks: List[TaskResult]
    overall_success: bool
    total_duration_seconds: float

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"\n{'='*60}",
            f"Execution Summary: {self.issue_key}",
            f"{'='*60}",
            f"Overall: {'✅ SUCCESS' if self.overall_success else '❌ FAILED'}",
            f"Duration: {self.total_duration_seconds:.1f}s",
            f"Repositories: {len(self.tasks)}",
            ""
        ]

        for task in self.tasks:
            status = "✅" if task.success else "❌"
            lines.append(f"{status} {task.repository}: {task.issue_key}")
            if task.pr_url:
                lines.append(f"   PR: {task.pr_url}")
            if task.branch_name:
                lines.append(f"   Branch: {task.branch_name}")
            if task.error:
                lines.append(f"   Error: {task.error}")

        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


class Executor:
    """
    Executes tasks by delegating to existing /autonomous-implement skill.

    This is NOT a reimplementation of the SDLC workflow. Instead, it:
    - Routes issues to the correct repository
    - Loads repository-specific knowledge
    - Invokes /autonomous-implement with enriched context
    - Handles multi-repository coordination
    """

    def __init__(self, factory_root: Path, workspace_config: Dict, knowledge_engine=None):
        """
        Initialize executor.

        Args:
            factory_root: Root directory of AI factory
            workspace_config: Loaded workspace.yaml
            knowledge_engine: Optional KnowledgeEngine instance
        """
        self.factory_root = Path(factory_root)
        self.workspace_config = workspace_config
        self.workspace_root = Path(workspace_config['workspace']['root'])

        # Import knowledge engine if not provided
        if knowledge_engine is None:
            from .knowledge import KnowledgeEngine
            knowledge_root = self.factory_root / 'knowledge'
            self.knowledge_engine = KnowledgeEngine(str(knowledge_root))
        else:
            self.knowledge_engine = knowledge_engine

    def execute_single_repo(
        self,
        issue_key: str,
        repository: str,
        knowledge_context: Optional[Dict[str, str]] = None
    ) -> TaskResult:
        """
        Execute issue implementation in a single repository.

        Delegates to /autonomous-implement skill with knowledge context.

        Args:
            issue_key: Jira issue key (e.g., 'ABI-123')
            repository: Repository name (e.g., 'runtime')
            knowledge_context: Optional pre-loaded knowledge (for efficiency)

        Returns:
            TaskResult with execution outcome
        """
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"Executing {issue_key} in {repository}")
        print(f"{'='*60}\n")

        try:
            # Load knowledge if not provided
            if knowledge_context is None:
                knowledge_context = self.knowledge_engine.get_repository_knowledge(repository)

            # Load foundations standards
            foundations = self.knowledge_engine.get_foundations_guidance('standards')

            # Get repository config
            repo_config = self._get_repo_config(repository)
            repo_path = self.workspace_root / repo_config['path']

            # Validate repository exists
            if not repo_path.exists():
                raise FileNotFoundError(
                    f"Repository directory not found: {repo_path}\n"
                    f"Expected location for '{repository}' repository.\n"
                    f"GitHub: {repo_config.get('github', 'unknown')}\n"
                    f"Please clone the repository or update workspace.yaml"
                )

            # Invoke /autonomous-implement skill with knowledge context
            result = self._invoke_autonomous_implement(
                issue_key=issue_key,
                repo_path=repo_path,
                knowledge_context=knowledge_context,
                foundations_standards=foundations.get('standards', ''),
                repo_config=repo_config
            )

            duration = time.time() - start_time

            return TaskResult(
                repository=repository,
                issue_key=issue_key,
                success=result['success'],
                pr_url=result.get('pr_url'),
                branch_name=result.get('branch_name'),
                output=result.get('output', ''),
                error=result.get('error'),
                duration_seconds=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return TaskResult(
                repository=repository,
                issue_key=issue_key,
                success=False,
                error=str(e),
                duration_seconds=duration
            )

    def execute_multi_repo(
        self,
        issue_key: str,
        repositories: List[str]
    ) -> ExecutionResult:
        """
        Execute issue implementation across multiple repositories.

        Coordinates parallel or sequential execution depending on dependencies.

        Args:
            issue_key: Jira issue key
            repositories: List of repository names to execute in

        Returns:
            ExecutionResult with all task results
        """
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"Multi-Repo Execution: {issue_key}")
        print(f"Repositories: {', '.join(repositories)}")
        print(f"{'='*60}\n")

        # Pre-load knowledge for all repos (parallel knowledge loading)
        knowledge_contexts = {}
        for repo in repositories:
            knowledge_contexts[repo] = self.knowledge_engine.get_repository_knowledge(repo)

        # Execute in each repository
        # TODO: Add dependency-aware ordering (e.g., sdk before runtime)
        task_results = []
        for repo in repositories:
            result = self.execute_single_repo(
                issue_key=f"{issue_key}-{repo}",  # Create repo-specific sub-issues
                repository=repo,
                knowledge_context=knowledge_contexts[repo]
            )
            task_results.append(result)

            # Stop on first failure (can be configured)
            if not result.success:
                print(f"⚠️  Task failed in {repo}, stopping multi-repo execution")
                break

        total_duration = time.time() - start_time
        overall_success = all(r.success for r in task_results)

        return ExecutionResult(
            issue_key=issue_key,
            tasks=task_results,
            overall_success=overall_success,
            total_duration_seconds=total_duration
        )

    # Private methods

    def _invoke_autonomous_implement(
        self,
        issue_key: str,
        repo_path: Path,
        knowledge_context: Dict[str, str],
        foundations_standards: str,
        repo_config: Dict
    ) -> Dict:
        """
        Invoke /autonomous-implement skill with knowledge context.

        Uses knowledge injection mechanism to provide repo-specific context.

        Args:
            issue_key: Jira issue key
            repo_path: Path to repository
            knowledge_context: Repository knowledge (architecture, patterns, etc.)
            foundations_standards: Foundations team standards
            repo_config: Repository configuration

        Returns:
            Dictionary with execution results
        """
        # Create knowledge context file inside repo_path so subprocess claude can read it
        context_file = self._create_knowledge_context_file(
            knowledge_context=knowledge_context,
            foundations_standards=foundations_standards,
            repo_config=repo_config,
            repo_path=repo_path,
        )

        return self._invoke_skill_via_subprocess(issue_key, context_file, repo_path)

    def _create_knowledge_context_file(
        self,
        knowledge_context: Dict[str, str],
        foundations_standards: str,
        repo_config: Dict,
        repo_path: Path,
    ) -> Path:
        """
        Create knowledge context file inside the target repo directory.

        Placing it inside repo_path ensures the subprocess claude session can
        read it without an out-of-allowed-directory permission prompt.

        Args:
            knowledge_context: Repository knowledge
            foundations_standards: Foundations standards
            repo_config: Repository configuration

        Returns:
            Path to temporary context file
        """
        context = f"""# Repository Knowledge Context
# This context is automatically injected by the harness

## Repository: {repo_config['name']}
**Display Name:** {repo_config.get('display_name', repo_config['name'])}
**Language:** {repo_config.get('language', 'unknown')}
**Build System:** {repo_config.get('build_system', 'unknown')}

---

## Architecture

{knowledge_context.get('architecture', 'No architecture documentation available.')}

---

## Coding Patterns

{knowledge_context.get('patterns', 'No coding patterns documented.')}

---

## Conventions

{knowledge_context.get('conventions', 'No conventions documented.')}

---

## Dependencies

{knowledge_context.get('dependencies', 'No dependency information available.')}

---

## Foundations Standards

{foundations_standards}

---

## Instructions for Implementation

When implementing this issue:
1. Follow the architecture patterns described above
2. Use the coding patterns and conventions for this repository
3. Ensure air-gapped compatibility (critical requirement)
4. Meet Definition of Done checklist
5. Achieve 80% test coverage minimum
6. Run gitleaks to ensure no secrets
"""

        # Write into the repo dir so the subprocess claude session can read it
        # without hitting an out-of-allowed-directory permission prompt.
        # _invoke_skill_via_subprocess deletes it after claude exits.
        context_file = repo_path / f'.knowledge_context_{repo_config["name"]}.md'
        context_file.write_text(context)
        return context_file

    def _invoke_skill_via_subprocess(
        self,
        issue_key: str,
        context_file: Path,
        repo_path: Path
    ) -> Dict:
        """
        Invoke /autonomous-implement skill by shelling out to the claude CLI.

        Runs claude headlessly (-p) with the factory plugin dir so all skills
        are available, then passes the skill invocation as the initial prompt.

        Args:
            issue_key: Jira issue key
            context_file: Path to knowledge context file (persists until skill completes)
            repo_path: Repository path (used as cwd for the claude process)

        Returns:
            Execution result dictionary
        """
        prompt = f"/autonomous-implement {issue_key} --context-file {context_file}"

        cmd = [
            'claude',
            '--plugin-dir', str(self.factory_root),
            '--dangerously-skip-permissions',
            '-p', prompt,
        ]

        print(f"\n🚀 Launching claude to implement {issue_key} in {repo_path.name}...")
        print(f"   Plugin: {self.factory_root}")
        print(f"   Context: {context_file}\n")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(repo_path),
                text=True,
                timeout=3600,  # 1-hour ceiling for large issues
            )

            success = result.returncode == 0

            if not success:
                return {
                    'success': False,
                    'error': f'claude exited with code {result.returncode}',
                    'pr_url': None,
                    'branch_name': None,
                    'output': '',
                }

            return {
                'success': True,
                'output': 'autonomous-implement completed',
                'pr_url': None,
                'branch_name': None,
                'error': None,
            }

        except FileNotFoundError:
            return {
                'success': False,
                'error': 'claude CLI not found — ensure it is on PATH (brew install claude-code)',
                'pr_url': None,
                'branch_name': None,
                'output': '',
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'claude timed out after 1 hour',
                'pr_url': None,
                'branch_name': None,
                'output': '',
            }
        finally:
            # Clean up context file now that claude has finished
            if context_file.exists():
                context_file.unlink()

    def _get_repo_config(self, repository: str) -> Dict:
        """Get repository configuration from workspace config."""
        repos = self.workspace_config.get('repositories', [])
        for repo in repos:
            if repo['name'] == repository:
                return repo
        raise ValueError(f"Repository '{repository}' not found in workspace.yaml")


# Convenience functions

def execute_issue(
    factory_root: Path,
    workspace_config: Dict,
    issue_key: str,
    repository: str
) -> TaskResult:
    """
    Convenience function to execute a single issue.

    Args:
        factory_root: Factory root directory
        workspace_config: Loaded workspace.yaml
        issue_key: Jira issue key
        repository: Repository name

    Returns:
        TaskResult
    """
    executor = Executor(factory_root, workspace_config)
    return executor.execute_single_repo(issue_key, repository)
