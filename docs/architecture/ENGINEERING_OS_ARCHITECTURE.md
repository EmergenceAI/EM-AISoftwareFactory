# Engineering Operating System Architecture

## Executive Summary

Transform `EM-AISoftwareFactory` from a Claude Code plugin into an **Engineering Operating System** — a semantic-aware orchestration layer that treats repositories as plugins, separates knowledge from prompts, and enables cross-repo software delivery at scale.

---

## Current State Analysis

### What You Have Today

```
EM-AISoftwareFactory/
├── skills/                    # 22 Claude Code skills (SDLC automation)
├── workflows/                 # Multi-agent orchestration (autonomous-sprint.js)
├── templates/                 # PR/bug templates
├── hooks/                     # Pre/post execution hooks
├── .mcp.json                  # Atlassian integration
└── .claude-plugin/            # Plugin manifest
```

**Strengths:**
- ✅ Working multi-agent system with eval-based validation
- ✅ Jira/Confluence integration via MCP
- ✅ Autonomous implementation pipeline (research → plan → implement → eval → PR)
- ✅ Skills distributed as Claude Code plugin

**Limitations:**
- ⚠️ Skills are tightly coupled to execution (Claude Code wrappers)
- ⚠️ Repository knowledge is implicit (buried in prompts)
- ⚠️ No workspace-level orchestration
- ⚠️ Semantic knowledge lives in skills, not a dedicated layer

---

## Vision: Engineering Operating System

```
                    AI Software Factory
                            │
            ┌───────────────┴────────────────┐
            │                                │
    Specification Engine          Knowledge Engine
            │                                │
            └───────────────┬────────────────┘
                            │
                      Orchestrator
                            │
         ┌─────────┬────────┼────────┬─────────┐
         │         │        │        │         │
      Runtime     UI    Talk2Data  Connectors  SDK
                            │
                    Git / CI / PRs
```

### Core Principles

1. **Factory ≠ Product** — The factory builds software; it doesn't ship to customers
2. **Repositories as Plugins** — Treat repos as adapters with standardized interfaces
3. **Separation of Concerns** — Prompts ≠ Orchestration ≠ Knowledge
4. **Execution Engine Agnostic** — Claude Code is one execution engine, not the only one

---

## Proposed Architecture

### Directory Structure

```
craft-ai-factory/                      # Renamed from EM-AISoftwareFactory
│
├── orchestrator/                      # Core orchestration engine
│   ├── planner.py                     # Breaks specs into task graphs
│   ├── router.py                      # Routes tasks to repositories
│   ├── executor.py                    # Spawns agents, manages lifecycle
│   └── reporter.py                    # Aggregates results, generates reports
│
├── prompts/                           # Model-agnostic prompt templates
│   ├── planner.md                     # Specification → Implementation plan
│   ├── architect.md                   # Architecture design
│   ├── backend.md                     # Backend implementation
│   ├── ui.md                          # Frontend implementation
│   ├── reviewer.md                    # Code review
│   └── evaluator.md                   # Eval generation & validation
│
├── knowledge/                         # Semantic knowledge layer
│   ├── workspace.yaml                 # Workspace definition
│   ├── repositories/                  # Per-repo knowledge packs
│   │   ├── runtime/
│   │   │   ├── architecture.md
│   │   │   ├── patterns.md
│   │   │   ├── conventions.md
│   │   │   └── dependencies.md
│   │   ├── runtime-ui/
│   │   ├── talk2data/
│   │   ├── connectors/
│   │   └── sdk/
│   ├── architecture/                  # Cross-cutting concerns
│   │   ├── system-design.md
│   │   ├── integration-patterns.md
│   │   └── data-flow.md
│   ├── coding-standards/
│   │   ├── typescript.md
│   │   ├── python.md
│   │   ├── testing.md
│   │   └── security.md
│   └── adr/                          # Architecture Decision Records
│       ├── 001-monorepo-strategy.md
│       ├── 002-mcp-integration.md
│       └── ...
│
├── adapters/                          # Repository adapters
│   ├── base.py                        # Abstract adapter interface
│   ├── runtime.py                     # em-runtime adapter
│   ├── ui.py                          # em-runtime-ui adapter
│   ├── talk2data.py                   # em-talk2data adapter
│   ├── connectors.py                  # em-connectors adapter
│   └── sdk.py                         # em-sdk adapter
│
├── evals/                             # Evaluation framework
│   ├── generators/                    # Eval generators per domain
│   │   ├── backend.py
│   │   ├── ui.py
│   │   └── integration.py
│   ├── runners/                       # Eval execution
│   └── validators/                    # Result validation
│
├── specs/                             # Specification storage
│   ├── features/                      # Feature specs
│   ├── epics/                         # Epic breakdowns
│   └── bugs/                          # Bug specifications
│
├── reports/                           # Generated reports
│   ├── sprint-reports/
│   ├── code-reviews/
│   └── eval-results/
│
├── workspace/                         # Workspace management
│   ├── config.yaml                    # Workspace configuration
│   └── state/                         # Workspace state tracking
│
└── claude-code/                       # Claude Code integration layer
    ├── plugin.json                    # Plugin manifest
    ├── skills/                        # Skills delegating to orchestrator
    │   ├── autonomous-sprint/
    │   ├── create-plan/
    │   └── ...
    └── workflows/                     # Workflow wrappers
```

---

## Key Components

### 1. Workspace Configuration (`workspace.yaml`)

```yaml
workspace:
  name: emergence-platform
  root: /Users/malamunisamy/Documents/Development

repositories:
  - name: runtime
    path: em-runtime
    github: EmergenceAI/em-runtime
    adapter: adapters.runtime
    primary_language: python
    build_system: poetry
    test_framework: pytest
    
  - name: runtime-ui
    path: em-runtime-ui
    github: EmergenceAI/em-runtime-ui
    adapter: adapters.ui
    primary_language: typescript
    build_system: pnpm
    test_framework: vitest
    
  - name: talk2data
    path: em-talk2data
    github: EmergenceAI/em-talk2data
    adapter: adapters.talk2data
    primary_language: python
    build_system: poetry
    
  - name: connectors
    path: em-connectors
    github: EmergenceAI/em-connectors
    adapter: adapters.connectors
    
  - name: sdk
    path: em-sdk
    github: EmergenceAI/em-sdk
    adapter: adapters.sdk

jira:
  project_key: ABI
  custom_fields:
    repository: customfield_10042
    epic_link: customfield_10014
    
confluence:
  space_key: TECH
  documentation_parent: 123456789
```

### 2. Repository Adapter Interface

```python
# adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RepositoryMetadata:
    name: str
    path: str
    github_url: str
    primary_language: str
    build_system: str
    test_framework: str
    conventions: Dict[str, str]

class RepositoryAdapter(ABC):
    """Abstract interface for repository operations"""
    
    @abstractmethod
    def get_metadata(self) -> RepositoryMetadata:
        """Return repository metadata"""
        pass
    
    @abstractmethod
    def build(self, target: Optional[str] = None) -> bool:
        """Run build command"""
        pass
    
    @abstractmethod
    def test(self, test_path: Optional[str] = None) -> bool:
        """Run test command"""
        pass
    
    @abstractmethod
    def lint(self, files: Optional[List[str]] = None) -> bool:
        """Run linter"""
        pass
    
    @abstractmethod
    def get_architecture(self) -> str:
        """Return architecture documentation path"""
        pass
    
    @abstractmethod
    def get_patterns(self) -> str:
        """Return coding patterns documentation path"""
        pass
    
    @abstractmethod
    def get_conventions(self) -> Dict[str, str]:
        """Return coding conventions"""
        pass
    
    @abstractmethod
    def create_branch(self, issue_key: str, issue_type: str, summary: str) -> str:
        """Create standardized branch"""
        pass
```

### 3. Example Adapter Implementation

```python
# adapters/runtime.py
from .base import RepositoryAdapter, RepositoryMetadata
from pathlib import Path
import subprocess

class RuntimeAdapter(RepositoryAdapter):
    def __init__(self, workspace_root: Path, config: dict):
        self.workspace_root = workspace_root
        self.config = config
        self.repo_path = workspace_root / config['path']
    
    def get_metadata(self) -> RepositoryMetadata:
        return RepositoryMetadata(
            name='runtime',
            path=str(self.repo_path),
            github_url='https://github.com/EmergenceAI/em-runtime',
            primary_language='python',
            build_system='poetry',
            test_framework='pytest',
            conventions={
                'branch_prefix': 'feature/',
                'commit_format': 'conventional',
                'pr_template': '.github/pull_request_template.md'
            }
        )
    
    def build(self, target: Optional[str] = None) -> bool:
        """Run poetry build"""
        cmd = ['poetry', 'build']
        if target:
            cmd.extend(['--format', target])
        result = subprocess.run(cmd, cwd=self.repo_path)
        return result.returncode == 0
    
    def test(self, test_path: Optional[str] = None) -> bool:
        """Run pytest"""
        cmd = ['poetry', 'run', 'pytest']
        if test_path:
            cmd.append(test_path)
        result = subprocess.run(cmd, cwd=self.repo_path)
        return result.returncode == 0
    
    def lint(self, files: Optional[List[str]] = None) -> bool:
        """Run ruff"""
        cmd = ['poetry', 'run', 'ruff', 'check']
        if files:
            cmd.extend(files)
        else:
            cmd.append('.')
        result = subprocess.run(cmd, cwd=self.repo_path)
        return result.returncode == 0
    
    def get_architecture(self) -> str:
        return str(self.repo_path / 'docs' / 'architecture.md')
    
    def get_patterns(self) -> str:
        return str(self.repo_path / 'docs' / 'patterns.md')
    
    def get_conventions(self) -> Dict[str, str]:
        return {
            'imports': 'absolute',
            'typing': 'strict',
            'docstrings': 'google',
            'test_naming': 'test_*'
        }
    
    def create_branch(self, issue_key: str, issue_type: str, summary: str) -> str:
        # Runtime-specific branch naming
        prefix = 'feature' if issue_type == 'Story' else 'bugfix'
        branch_name = f"{prefix}/{issue_key}-{summary.lower().replace(' ', '-')}"
        
        subprocess.run(['git', 'checkout', '-b', branch_name], cwd=self.repo_path)
        return branch_name
```

### 4. Knowledge Engine

```python
# orchestrator/knowledge.py
from pathlib import Path
from typing import Dict, List, Optional
import yaml

class KnowledgeEngine:
    """Retrieves semantic knowledge for planning and implementation"""
    
    def __init__(self, knowledge_root: Path):
        self.knowledge_root = knowledge_root
        self.cache = {}
    
    def get_repository_knowledge(self, repo_name: str) -> Dict:
        """Load all knowledge for a repository"""
        repo_knowledge_dir = self.knowledge_root / 'repositories' / repo_name
        
        return {
            'architecture': self._load_markdown(repo_knowledge_dir / 'architecture.md'),
            'patterns': self._load_markdown(repo_knowledge_dir / 'patterns.md'),
            'conventions': self._load_markdown(repo_knowledge_dir / 'conventions.md'),
            'dependencies': self._load_markdown(repo_knowledge_dir / 'dependencies.md')
        }
    
    def get_coding_standards(self, language: str) -> str:
        """Get coding standards for a language"""
        standards_file = self.knowledge_root / 'coding-standards' / f'{language}.md'
        return self._load_markdown(standards_file)
    
    def get_architecture_decisions(self, topic: Optional[str] = None) -> List[str]:
        """Get relevant ADRs"""
        adr_dir = self.knowledge_root / 'adr'
        
        if topic:
            # Search ADRs by topic
            return self._search_adrs(adr_dir, topic)
        
        return [str(f) for f in adr_dir.glob('*.md')]
    
    def get_integration_patterns(self) -> str:
        """Get cross-repo integration patterns"""
        return self._load_markdown(
            self.knowledge_root / 'architecture' / 'integration-patterns.md'
        )
    
    def _load_markdown(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text()
    
    def _search_adrs(self, adr_dir: Path, topic: str) -> List[str]:
        # Simple grep-like search across ADRs
        matching = []
        for adr_file in adr_dir.glob('*.md'):
            content = adr_file.read_text()
            if topic.lower() in content.lower():
                matching.append(str(adr_file))
        return matching
```

### 5. Orchestrator

```python
# orchestrator/planner.py
from typing import List, Dict
from .knowledge import KnowledgeEngine
from adapters.base import RepositoryAdapter

class Planner:
    """Converts specifications into executable task graphs"""
    
    def __init__(self, knowledge: KnowledgeEngine, adapters: Dict[str, RepositoryAdapter]):
        self.knowledge = knowledge
        self.adapters = adapters
    
    def create_task_graph(self, jira_issue: Dict) -> Dict:
        """
        Input: Jira issue
        Output: Task graph with repository routing
        """
        # Determine affected repositories
        affected_repos = self._analyze_affected_repos(jira_issue)
        
        # Build task graph
        tasks = []
        for repo_name in affected_repos:
            adapter = self.adapters[repo_name]
            repo_knowledge = self.knowledge.get_repository_knowledge(repo_name)
            
            tasks.append({
                'repository': repo_name,
                'adapter': adapter,
                'knowledge': repo_knowledge,
                'steps': self._generate_steps(jira_issue, repo_knowledge)
            })
        
        return {
            'issue_key': jira_issue['key'],
            'tasks': tasks,
            'dependencies': self._analyze_dependencies(tasks)
        }
    
    def _analyze_affected_repos(self, jira_issue: Dict) -> List[str]:
        """Determine which repositories are affected by this issue"""
        # Option 1: Jira custom field
        if 'customFields' in jira_issue and 'repository' in jira_issue['customFields']:
            return [jira_issue['customFields']['repository']]
        
        # Option 2: Component mapping
        components = jira_issue.get('components', [])
        repo_map = {
            'Runtime': ['runtime'],
            'UI': ['runtime-ui'],
            'Talk2Data': ['talk2data'],
            'Connectors': ['connectors'],
            'SDK': ['sdk']
        }
        
        repos = []
        for component in components:
            if component in repo_map:
                repos.extend(repo_map[component])
        
        return repos or ['runtime']  # Default
    
    def _generate_steps(self, jira_issue: Dict, repo_knowledge: Dict) -> List[Dict]:
        """Generate implementation steps based on issue type and repo knowledge"""
        issue_type = jira_issue.get('type', 'Task')
        
        if issue_type == 'Story':
            return [
                {'phase': 'research', 'prompt': 'prompts/architect.md'},
                {'phase': 'plan', 'prompt': 'prompts/planner.md'},
                {'phase': 'implement', 'prompt': 'prompts/backend.md'},  # Or ui.md
                {'phase': 'test', 'prompt': 'prompts/evaluator.md'},
                {'phase': 'review', 'prompt': 'prompts/reviewer.md'}
            ]
        elif issue_type == 'Bug':
            return [
                {'phase': 'diagnose', 'prompt': 'prompts/reviewer.md'},
                {'phase': 'fix', 'prompt': 'prompts/backend.md'},
                {'phase': 'test', 'prompt': 'prompts/evaluator.md'}
            ]
        
        return []
    
    def _analyze_dependencies(self, tasks: List[Dict]) -> List[Dict]:
        """Analyze cross-repo dependencies"""
        # If task touches SDK, do it first
        # If task touches UI + Runtime, do Runtime first
        # etc.
        dependencies = []
        
        task_repos = [t['repository'] for t in tasks]
        
        if 'sdk' in task_repos and 'runtime' in task_repos:
            dependencies.append({
                'before': 'sdk',
                'after': 'runtime',
                'reason': 'Runtime depends on SDK changes'
            })
        
        if 'runtime' in task_repos and 'runtime-ui' in task_repos:
            dependencies.append({
                'before': 'runtime',
                'after': 'runtime-ui',
                'reason': 'UI depends on Runtime API changes'
            })
        
        return dependencies
```

### 6. Executor

```python
# orchestrator/executor.py
from typing import Dict, List
import asyncio
from pathlib import Path

class Executor:
    """Spawns and manages agent execution"""
    
    def __init__(self, factory_root: Path, execution_engine: str = 'claude-code'):
        self.factory_root = factory_root
        self.execution_engine = execution_engine
    
    async def execute_task_graph(self, task_graph: Dict) -> Dict:
        """Execute task graph with dependency awareness"""
        tasks = task_graph['tasks']
        dependencies = task_graph['dependencies']
        
        # Topologically sort tasks based on dependencies
        sorted_tasks = self._topological_sort(tasks, dependencies)
        
        results = []
        for task in sorted_tasks:
            result = await self._execute_task(task)
            results.append(result)
        
        return {
            'issue_key': task_graph['issue_key'],
            'results': results
        }
    
    async def _execute_task(self, task: Dict) -> Dict:
        """Execute a single task using configured execution engine"""
        repo_name = task['repository']
        adapter = task['adapter']
        knowledge = task['knowledge']
        steps = task['steps']
        
        if self.execution_engine == 'claude-code':
            return await self._execute_via_claude_code(repo_name, adapter, knowledge, steps)
        elif self.execution_engine == 'openai':
            return await self._execute_via_openai(repo_name, adapter, knowledge, steps)
        else:
            raise ValueError(f"Unsupported execution engine: {self.execution_engine}")
    
    async def _execute_via_claude_code(
        self, 
        repo_name: str,
        adapter,
        knowledge: Dict,
        steps: List[Dict]
    ) -> Dict:
        """Execute via Claude Code workflow"""
        # Call Claude Code workflow with injected knowledge
        workflow_path = self.factory_root / 'claude-code' / 'workflows' / 'implement.js'
        
        # Build context for agent
        context = {
            'repository': repo_name,
            'architecture': knowledge['architecture'],
            'patterns': knowledge['patterns'],
            'conventions': knowledge['conventions'],
            'build_command': adapter.get_metadata().build_system,
            'test_command': adapter.get_metadata().test_framework
        }
        
        # Execute workflow (simplified - actual implementation would use subprocess/API)
        # result = await self._run_workflow(workflow_path, context, steps)
        
        return {
            'repository': repo_name,
            'status': 'success',
            'pr_url': 'https://github.com/...'
        }
    
    def _topological_sort(self, tasks: List[Dict], dependencies: List[Dict]) -> List[Dict]:
        """Sort tasks based on dependencies"""
        # Simple topological sort implementation
        # In production, use a proper graph library
        
        # For now, just honor SDK → Runtime → UI ordering
        priority_order = ['sdk', 'connectors', 'runtime', 'talk2data', 'runtime-ui']
        
        return sorted(
            tasks,
            key=lambda t: priority_order.index(t['repository']) 
                if t['repository'] in priority_order else 999
        )
```

---

## Integration with Claude Code

The Claude Code plugin layer becomes a **thin wrapper** that delegates to the orchestrator:

```javascript
// claude-code/workflows/autonomous-sprint.js
export const meta = {
  name: 'autonomous-sprint',
  description: 'Autonomous sprint implementation via Engineering OS'
}

// Delegate to orchestrator
const result = await agent(
  `Execute autonomous sprint via Engineering OS:
  
  1. Call orchestrator/planner.py with JQL: ${args.jql}
  2. Planner will:
     - Query Jira
     - Analyze affected repositories
     - Build task graphs with knowledge injection
  3. Call orchestrator/executor.py to run task graph
  4. Executor spawns agents with repository-specific context
  
  Return aggregated results.`,
  {
    schema: SPRINT_RESULTS_SCHEMA
  }
)

return result
```

**Skills become delegators:**

```markdown
# skills/create-plan/SKILL.md

## Instructions

1. Call `orchestrator/planner.py` with Jira issue key
2. Planner retrieves:
   - Issue details from Jira
   - Affected repositories
   - Knowledge packs per repository
   - Coding standards
   - Relevant ADRs
3. Use `prompts/planner.md` to generate plan
4. Save plan to `specs/features/{issue-key}.md`
5. Return plan summary
```

---

## Knowledge Pack Example

```markdown
# knowledge/repositories/runtime/architecture.md

# EM Runtime Architecture

## Overview
Python-based workflow orchestration engine.

## Components
- **Executor**: Runs agent workflows
- **State Manager**: Persists workflow state
- **Message Bus**: Event-driven communication
- **Plugin System**: Extensible tooling

## Key Patterns
- Repository pattern for data access
- Factory pattern for agent creation
- Observer pattern for event handling

## Entry Points
- `src/runtime/main.py` - CLI entry point
- `src/runtime/api/server.py` - HTTP API
- `src/runtime/executor/engine.py` - Core execution

## Dependencies
- `em-sdk` - Core SDK
- `em-connectors` - Data connectors
- FastAPI - Web framework
- SQLAlchemy - ORM

## Testing
- Unit: `tests/unit/`
- Integration: `tests/integration/`
- E2E: `tests/e2e/`

## Build
```bash
poetry install
poetry run pytest
```
```

---

## Migration Plan

### Phase 1: Foundation (Week 1-2)
1. ✅ Create `workspace.yaml`
2. ✅ Implement base adapter interface
3. ✅ Create 1-2 repository adapters (runtime, runtime-ui)
4. ✅ Scaffold knowledge packs for each repo

### Phase 2: Knowledge Layer (Week 3-4)
1. ✅ Extract architecture docs into knowledge packs
2. ✅ Document coding standards per language
3. ✅ Create initial ADRs
4. ✅ Implement knowledge engine

### Phase 3: Orchestrator (Week 5-6)
1. ✅ Implement planner with repository routing
2. ✅ Implement executor with adapter integration
3. ✅ Test task graph generation

### Phase 4: Claude Code Integration (Week 7-8)
1. ✅ Refactor skills to delegate to orchestrator
2. ✅ Update workflows to use adapters
3. ✅ Test end-to-end with multi-repo sprint

### Phase 5: Production (Week 9-10)
1. ✅ Complete all repository adapters
2. ✅ Full knowledge pack coverage
3. ✅ Documentation and training
4. ✅ Dogfood on real sprint

---

## Benefits

### Separation of Concerns
- **Prompts** are model-agnostic templates
- **Knowledge** is centralized and versioned
- **Adapters** encapsulate repository details
- **Orchestrator** manages workflow logic

### Repository as Plugin
```python
# Adding a new repository is just configuration
# No code changes needed in orchestrator

# workspace.yaml
repositories:
  - name: new-service
    path: em-new-service
    adapter: adapters.new_service  # Implement this adapter
```

### Execution Engine Agnostic
```python
# Switch from Claude Code to OpenAI in one place
executor = Executor(
    factory_root=factory_root,
    execution_engine='openai'  # or 'claude-code', 'anthropic', 'custom'
)
```

### Knowledge Reuse
```python
# Planner automatically injects relevant knowledge
task_graph = planner.create_task_graph(jira_issue)

# Agent receives:
# - Repository architecture
# - Coding patterns
# - Conventions
# - Relevant ADRs
# - Cross-repo integration patterns
```

### Scalability
```
Today: 5 repositories
Tomorrow: 50 repositories

Same orchestrator, just add:
- adapter implementation
- knowledge pack
- workspace.yaml entry
```

---

## Next Steps

1. **Immediate:**
   - Create `workspace.yaml` with your 6 repositories
   - Implement `RuntimeAdapter` and `UIAdapter`
   - Extract architecture docs into knowledge packs

2. **Short-term (Next Sprint):**
   - Implement orchestrator planner
   - Test repository routing
   - Run first multi-repo sprint via orchestrator

3. **Long-term:**
   - Add remaining adapters
   - Build comprehensive knowledge base
   - Implement execution engine switching
   - Scale to 10+ repositories

---

## Questions to Resolve

1. **Jira Repository Field:** Add custom field or use components?
2. **Execution Engine:** Start with Claude Code only, or plan for multi-engine?
3. **Knowledge Format:** Markdown + YAML, or structured JSON?
4. **Adapter Complexity:** How much should adapters know vs orchestrator?
5. **Prompt Management:** Version prompts separately or embed in orchestrator?

---

## Conclusion

This architecture transforms your plugin into an **Engineering Operating System**:

- **Specification** → **Planning** → **Discovery** → **Knowledge Retrieval** → **Task Graph** → **Execution** → **Evaluation** → **Reporting**

Claude Code becomes the **execution engine**, not the orchestration layer.

The **factory** builds software. The **orchestrator** manages how. The **knowledge engine** informs decisions. The **adapters** abstract repositories.

This is the foundation for scaling your AI-driven SDLC across 10, 50, or 100 repositories.
