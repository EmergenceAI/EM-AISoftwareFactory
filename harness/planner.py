"""
Planner - Converts Jira issues into executable task graphs with knowledge injection.

The planner:
1. Analyzes Jira issues to determine affected repositories
2. Retrieves knowledge packs for each repository
3. Generates task graphs with phases and steps
4. Analyzes cross-repository dependencies
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from .knowledge import KnowledgeEngine
from .router import Router


@dataclass
class Step:
    """A single step in a task."""
    phase: str              # research, plan, implement, test, review
    prompt_template: str    # prompts/backend.md
    inputs: Dict            # Data passed to step
    expected_output: str    # What we expect back


@dataclass
class Task:
    """A task for a single repository."""
    repository: str
    adapter_class: str      # 'adapters.runtime.RuntimeAdapter'
    knowledge: Dict[str, str]
    steps: List[Step]
    issue_key: str
    issue_type: str
    summary: str
    description: str


@dataclass
class Dependency:
    """Cross-repository dependency."""
    before: str             # Repository that must complete first
    after: str              # Repository that depends on 'before'
    reason: str             # Why this dependency exists


@dataclass
class TaskGraph:
    """Complete task graph for an issue."""
    issue_key: str
    tasks: List[Task]
    dependencies: List[Dependency]


class Planner:
    """Converts specifications into executable task graphs."""

    def __init__(
        self,
        knowledge_engine: KnowledgeEngine,
        router: Router,
        workspace_config: Dict
    ):
        """
        Initialize planner.

        Args:
            knowledge_engine: Knowledge retrieval engine
            router: Repository router
            workspace_config: Loaded workspace.yaml
        """
        self.knowledge = knowledge_engine
        self.router = router
        self.workspace_config = workspace_config
        self.adapters = self._build_adapter_map()

    def create_task_graph(self, jira_issue: Dict) -> TaskGraph:
        """
        Convert Jira issue into executable task graph.

        Args:
            jira_issue: Jira issue dict with:
                - key: Issue key (e.g., 'ABI-123')
                - type: Issue type (Story, Bug, Task)
                - summary: Title
                - description: Full description
                - components: Components
                - acceptanceCriteria: Acceptance criteria (optional)

        Returns:
            TaskGraph with tasks per repository and dependencies
        """
        issue_key = jira_issue['key']
        issue_type = jira_issue.get('type', 'Task')

        # Determine affected repositories
        affected_repos = self.router.get_affected_repositories(jira_issue)

        # Build tasks for each repository
        tasks = []
        for repo_name in affected_repos:
            task = self._create_task_for_repo(repo_name, jira_issue)
            tasks.append(task)

        # Analyze dependencies between tasks
        dependencies = self._analyze_dependencies(tasks)

        return TaskGraph(
            issue_key=issue_key,
            tasks=tasks,
            dependencies=dependencies
        )

    def create_task_graphs_batch(self, jira_issues: List[Dict]) -> List[TaskGraph]:
        """
        Create task graphs for multiple issues.

        Args:
            jira_issues: List of Jira issues

        Returns:
            List of task graphs
        """
        return [self.create_task_graph(issue) for issue in jira_issues]

    # Private methods

    def _create_task_for_repo(self, repo_name: str, jira_issue: Dict) -> Task:
        """Create a task for a specific repository."""
        # Load knowledge pack for repository
        repo_knowledge = self.knowledge.get_repository_knowledge(repo_name)

        # Get repository config
        repo_config = next(
            (r for r in self.workspace_config['repositories'] if r['name'] == repo_name),
            None
        )

        if not repo_config:
            raise ValueError(f"Repository {repo_name} not found in workspace config")

        # Determine adapter class
        adapter_class = repo_config.get('adapter', f'adapters.{repo_name}.{repo_name.title()}Adapter')

        # Generate steps based on issue type
        steps = self._generate_steps(jira_issue, repo_knowledge, repo_config)

        return Task(
            repository=repo_name,
            adapter_class=adapter_class,
            knowledge=repo_knowledge,
            steps=steps,
            issue_key=jira_issue['key'],
            issue_type=jira_issue.get('type', 'Task'),
            summary=jira_issue.get('summary', ''),
            description=jira_issue.get('description', '')
        )

    def _generate_steps(
        self,
        jira_issue: Dict,
        repo_knowledge: Dict[str, str],
        repo_config: Dict
    ) -> List[Step]:
        """
        Generate implementation steps based on issue type and repository.

        Args:
            jira_issue: Jira issue
            repo_knowledge: Knowledge pack for repository
            repo_config: Repository configuration

        Returns:
            List of steps to execute
        """
        issue_type = jira_issue.get('type', 'Task')
        primary_language = repo_config.get('primary_language', 'python')

        # Determine prompt template based on language/repo type
        if 'ui' in repo_config['name']:
            implementation_prompt = 'prompts/ui.md'
        else:
            implementation_prompt = 'prompts/backend.md'

        # Base steps for all issues
        steps = []

        if issue_type == 'Story':
            # Story workflow: research → plan → implement → test → review
            steps = [
                Step(
                    phase='research',
                    prompt_template='prompts/architect.md',
                    inputs={
                        'issue': jira_issue,
                        'architecture': repo_knowledge['architecture']
                    },
                    expected_output='Architecture analysis and design decisions'
                ),
                Step(
                    phase='plan',
                    prompt_template='prompts/planner.md',
                    inputs={
                        'issue': jira_issue,
                        'architecture': repo_knowledge['architecture'],
                        'patterns': repo_knowledge['patterns']
                    },
                    expected_output='Implementation plan with file changes'
                ),
                Step(
                    phase='implement',
                    prompt_template=implementation_prompt,
                    inputs={
                        'issue': jira_issue,
                        'architecture': repo_knowledge['architecture'],
                        'patterns': repo_knowledge['patterns'],
                        'conventions': repo_knowledge['conventions']
                    },
                    expected_output='Code implementation'
                ),
                Step(
                    phase='test',
                    prompt_template='prompts/evaluator.md',
                    inputs={
                        'issue': jira_issue,
                        'acceptance_criteria': jira_issue.get('acceptanceCriteria', ''),
                        'conventions': repo_knowledge['conventions']
                    },
                    expected_output='Test suite and eval results'
                ),
                Step(
                    phase='review',
                    prompt_template='prompts/reviewer.md',
                    inputs={
                        'issue': jira_issue,
                        'patterns': repo_knowledge['patterns'],
                        'conventions': repo_knowledge['conventions']
                    },
                    expected_output='Code review feedback'
                )
            ]

        elif issue_type == 'Bug':
            # Bug workflow: diagnose → fix → test → verify
            steps = [
                Step(
                    phase='diagnose',
                    prompt_template='prompts/reviewer.md',
                    inputs={
                        'issue': jira_issue,
                        'architecture': repo_knowledge['architecture'],
                        'patterns': repo_knowledge['patterns']
                    },
                    expected_output='Root cause analysis'
                ),
                Step(
                    phase='fix',
                    prompt_template=implementation_prompt,
                    inputs={
                        'issue': jira_issue,
                        'patterns': repo_knowledge['patterns'],
                        'conventions': repo_knowledge['conventions']
                    },
                    expected_output='Bug fix implementation'
                ),
                Step(
                    phase='test',
                    prompt_template='prompts/evaluator.md',
                    inputs={
                        'issue': jira_issue,
                        'conventions': repo_knowledge['conventions']
                    },
                    expected_output='Regression tests'
                )
            ]

        else:  # Task, Epic, etc.
            # Simple workflow: plan → implement → test
            steps = [
                Step(
                    phase='plan',
                    prompt_template='prompts/planner.md',
                    inputs={
                        'issue': jira_issue,
                        'architecture': repo_knowledge['architecture']
                    },
                    expected_output='Implementation plan'
                ),
                Step(
                    phase='implement',
                    prompt_template=implementation_prompt,
                    inputs={
                        'issue': jira_issue,
                        'architecture': repo_knowledge['architecture'],
                        'patterns': repo_knowledge['patterns'],
                        'conventions': repo_knowledge['conventions']
                    },
                    expected_output='Implementation'
                ),
                Step(
                    phase='test',
                    prompt_template='prompts/evaluator.md',
                    inputs={
                        'issue': jira_issue,
                        'conventions': repo_knowledge['conventions']
                    },
                    expected_output='Tests'
                )
            ]

        return steps

    def _analyze_dependencies(self, tasks: List[Task]) -> List[Dependency]:
        """
        Analyze cross-repository dependencies.

        Rules:
        - SDK changes must complete before anything else
        - Runtime changes must complete before UI changes
        - Connectors changes before Talk2Data changes

        Args:
            tasks: List of tasks

        Returns:
            List of dependencies
        """
        dependencies = []
        task_repos = [t.repository for t in tasks]

        # SDK → Runtime dependency
        if 'sdk' in task_repos and 'runtime' in task_repos:
            dependencies.append(Dependency(
                before='sdk',
                after='runtime',
                reason='Runtime depends on SDK changes'
            ))

        # SDK → Connectors dependency
        if 'sdk' in task_repos and 'connectors' in task_repos:
            dependencies.append(Dependency(
                before='sdk',
                after='connectors',
                reason='Connectors use SDK interfaces'
            ))

        # Runtime → Runtime-UI dependency
        if 'runtime' in task_repos and 'runtime-ui' in task_repos:
            dependencies.append(Dependency(
                before='runtime',
                after='runtime-ui',
                reason='UI depends on Runtime API changes'
            ))

        # Connectors → Talk2Data dependency
        if 'connectors' in task_repos and 'talk2data' in task_repos:
            dependencies.append(Dependency(
                before='connectors',
                after='talk2data',
                reason='Talk2Data uses connector framework'
            ))

        # Runtime → Talk2Data dependency
        if 'runtime' in task_repos and 'talk2data' in task_repos:
            dependencies.append(Dependency(
                before='runtime',
                after='talk2data',
                reason='Talk2Data integrates with Runtime'
            ))

        return dependencies

    def _build_adapter_map(self) -> Dict[str, str]:
        """Build repository name → adapter class mapping."""
        adapter_map = {}

        for repo in self.workspace_config['repositories']:
            repo_name = repo['name']
            adapter_class = repo.get('adapter', f'adapters.{repo_name}')
            adapter_map[repo_name] = adapter_class

        return adapter_map
