# Harness - Workspace-Level Orchestration

**Thin orchestration layer that enhances existing skills with repository knowledge and multi-repo coordination.**

---

## What It Does

The harness **delegates** to existing `/autonomous-implement` skill while providing:

1. **Repository Routing** - Auto-routes Jira issues to correct repository
2. **Knowledge Injection** - Provides repo-specific architecture/patterns to skills
3. **Multi-Repo Coordination** - Handles issues that span multiple repositories
4. **Foundations Standards** - Enforces air-gapped requirements, DoD, etc.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User: "Implement ABI-123"                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (Thin Layer)                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Router   │→ │Knowledge │→ │ Executor │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  cd em-runtime/                                              │
│  /autonomous-implement ABI-123                              │
│     (with knowledge context injected)                       │
│                                                              │
│   research → plan → evals → implement → test → PR         │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** The harness does NOT reimplement the SDLC workflow. It enhances existing skills with knowledge context.

---

## Components

### Router ([router.py](router.py))
Routes Jira issues to repositories using:
- Jira component mapping (primary)
- Description analysis (fallback)
- Label prefixes like `repo:runtime`

### Knowledge Engine ([knowledge.py](knowledge.py))
Loads repository-specific knowledge:
- Architecture documentation
- Coding patterns
- Conventions
- Foundations standards (air-gapped, DoD)

### Executor ([executor.py](executor.py))
Invokes `/autonomous-implement` with enriched context:
- Creates temporary knowledge context file
- Injects into skill prompt
- Handles multi-repo coordination

---

## Usage

### Command-Line

```bash
# Implement single issue (auto-route)
python -m harness implement ABI-123

# Implement in specific repository
python -m harness implement ABI-123 --repo runtime

# Multi-repository implementation
python -m harness multi-repo SDK-456 --repos sdk,runtime,runtime-ui

# View repository knowledge
python -m harness knowledge --repo runtime
python -m harness knowledge --list

# Test harness components
python -m harness test ABI-123
```

### Programmatic API

```python
from harness import Executor, Router, KnowledgeEngine
from pathlib import Path
import yaml

# Load configuration
with open('workspace.yaml') as f:
    config = yaml.safe_load(f)

# Execute single issue
executor = Executor(Path('.'), config)
result = executor.execute_single_repo(
    issue_key='ABI-123',
    repository='runtime'
)

print(f"Success: {result.success}")
print(f"PR: {result.pr_url}")

# Multi-repo execution
result = executor.execute_multi_repo(
    issue_key='SDK-456',
    repositories=['sdk', 'runtime', 'runtime-ui']
)

print(result.summary())
```

---

## How It Works

### Single Repository Flow

```python
# 1. Router determines repository
router = Router(workspace_config)
repo = router.route_issue(jira_issue)  # → "runtime"

# 2. Knowledge Engine loads repo knowledge
knowledge = KnowledgeEngine('knowledge/')
repo_knowledge = knowledge.get_repository_knowledge('runtime')
# Returns:
# {
#   'architecture': '...3-tier architecture...',
#   'patterns': '...repository pattern...',
#   'conventions': '...absolute imports, strict typing...',
#   'dependencies': '...poetry, FastAPI...'
# }

# 3. Executor creates knowledge context file
context_file = create_context_file(
    knowledge=repo_knowledge,
    foundations=knowledge.get_foundations_guidance()
)

# 4. Invoke /autonomous-implement with context
message = f"""
Review knowledge context at: {context_file}

Then: /autonomous-implement ABI-123
"""

# Skill gets repo-specific patterns and standards!
```

### Multi-Repository Flow

```python
# Issue affects: sdk, runtime, runtime-ui
router.get_affected_repositories(issue)  
# → ['sdk', 'runtime', 'runtime-ui']

# Execute in parallel (or sequential with dependencies)
for repo in repositories:
    knowledge = knowledge_engine.get_repository_knowledge(repo)
    
    # Invoke /autonomous-implement in each repo
    # with repo-specific knowledge context
    result = execute_in_repo(
        repo=repo,
        issue_key=f"{issue_key}-{repo}",
        knowledge=knowledge
    )

# Link PRs together across repositories
link_cross_repo_prs(results)
```

---

## Knowledge Injection Mechanism

The harness creates a temporary knowledge context file:

```markdown
# Repository Knowledge Context

## Repository: runtime
**Language:** Python
**Build System:** poetry

---

## Architecture

3-tier architecture:
- API Layer (FastAPI)
- Business Logic (Domain Services)
- Data Layer (Repository Pattern)

---

## Coding Patterns

Use repository pattern for data access:
- All database queries through repositories
- Business logic in service layer
- API endpoints thin, delegate to services

---

## Conventions

- Imports: absolute only
- Type hints: strict, all public APIs
- Docstrings: Google style

---

## Foundations Standards

### Air-Gapped Requirements (CRITICAL)
- NO cloud-specific APIs (GCP, AWS, Azure)
- Helm charts must deploy without cloud provider
- Use Crossplane for infrastructure dependencies

### Definition of Done
1. 80% test coverage
2. gitleaks passes
3. Pacto contract valid
...
```

Skills receive this context and use it during implementation!

---

## What Orchestrator Does NOT Do

** Does NOT reimplement skills**
- The skills (`/autonomous-implement`, `/research-codebase`, etc.) already work
- Orchestrator enhances them, doesn't replace them

** Does NOT replace adapters**
- Adapters provide repository-specific commands (build, test, lint)
- Orchestrator uses adapters to get metadata

** Does NOT store state**
- All orchestration is stateless
- State lives in Jira, Git, PRs

---

## Integration with Existing Skills

### Current Skills (Work Today)

```bash
# In any repository:
cd ~/em-runtime
/autonomous-implement ABI-123

# Multi-issue sprint:
/autonomous-sprint --jql "sprint in openSprints()"
```

### Enhanced with Orchestrator

```bash
# From workspace root (any directory):
python -m harness implement ABI-123
#  Auto-routes to em-runtime
#  Injects runtime architecture/patterns
#  Enforces Foundations standards

# Multi-repo issue:
python -m harness multi-repo SDK-456
#  Detects affected repos: sdk, runtime, runtime-ui
#  Executes in parallel with repo-specific knowledge
#  Links PRs together
```

---

## Configuration

### workspace.yaml

```yaml
workspace:
  name: emergence-platform
  root: ~/Documents/Development

repositories:
  - name: runtime
    display_name: EM Runtime
    path: em-runtime
    language: python
    build_system: poetry
    test_framework: pytest
    jira_component: Runtime

  - name: runtime-ui
    display_name: EM Runtime UI
    path: em-runtime-ui
    language: typescript
    build_system: pnpm
    test_framework: vitest
    jira_component: UI

jira:
  component_mapping:
    Runtime: runtime
    UI: runtime-ui
    Talk2Data: talk2data
```

---

## Development Status

### Implemented
- Router (issue → repository mapping)
- Knowledge Engine (load repo knowledge + Foundations)
- Executor (delegate to /autonomous-implement)
- CLI (command-line interface)
- Knowledge context injection

### 🚧 In Progress
- Multi-repo dependency ordering
- PR cross-linking
- Jira MCP integration (currently mocked)

### Planned
- Workflow orchestration (/autonomous-sprint integration)
- Reporter (aggregate results across repos)
- Knowledge sync automation

---

## Testing

```bash
# Test harness components
python -m harness test ABI-123

# Output:
# Testing Router...
#    Routed ABI-123 → runtime
#
# Testing Knowledge Engine...
#    Loaded knowledge for runtime:
#      - architecture
#      - patterns
#      - conventions
#
# Testing Foundations Standards...
#    Loaded foundations standards
```

---

## Examples

### Example 1: Single Repository

```bash
$ python -m harness implement ABI-123

============================================================
AI Software Factory - Workspace Harness
============================================================

 Fetching issue: ABI-123
   Summary: Add rate limiting to API endpoints

 Repository: runtime (auto-routed)

============================================================
Executing ABI-123 in runtime
============================================================

 Loading knowledge context...
    Architecture
    Patterns
    Conventions
    Foundations

 Invoking /autonomous-implement with knowledge context...

[Skill execution output...]

============================================================
Execution Summary: ABI-123
============================================================
Overall:  SUCCESS
Duration: 245.3s
Repositories: 1

 runtime: ABI-123
   PR: https://github.com/EmergenceAI/em-runtime/pull/789
   Branch: feature/ABI-123-rate-limiting
============================================================
```

### Example 2: Multi-Repository

```bash
$ python -m harness multi-repo SDK-456

============================================================
AI Software Factory - Multi-Repo Harness
============================================================

 Fetching issue: SDK-456
   Summary: Add new authentication method

 Repositories: sdk, runtime, runtime-ui (auto-detected)

Executing SDK-456-sdk in sdk...
    PR: https://github.com/EmergenceAI/em-sdk/pull/123

Executing SDK-456-runtime in runtime...
    PR: https://github.com/EmergenceAI/em-runtime/pull/790

Executing SDK-456-ui in runtime-ui...
    PR: https://github.com/EmergenceAI/em-runtime-ui/pull/456

============================================================
Execution Summary: SDK-456
============================================================
Overall:  SUCCESS
Duration: 678.9s
Repositories: 3

 sdk: SDK-456-sdk
   PR: https://github.com/EmergenceAI/em-sdk/pull/123
 runtime: SDK-456-runtime
   PR: https://github.com/EmergenceAI/em-runtime/pull/790
 runtime-ui: SDK-456-ui
   PR: https://github.com/EmergenceAI/em-runtime-ui/pull/456
============================================================
```

---

## Why This Approach?

### Advantages

1. **Reuses existing skills** - No duplicate implementation
2. **Thin layer** - ~500 lines vs ~5000 for full reimplementation
3. **Knowledge-enhanced** - Skills get repo-specific context
4. **Multi-repo aware** - Handles cross-repository coordination
5. **Standards enforcement** - Foundations requirements built-in

### Use Cases

- **Single developer, multi-repo workspace** - Navigate between repos easily
- **Onboarding** - New devs don't need to know which repo
- **Cross-cutting changes** - SDK updates that affect all repos
- **Standards enforcement** - Air-gapped requirements automatically checked

---

## See Also

- [Engineering OS Architecture](../docs/architecture/ENGINEERING_OS_ARCHITECTURE.md)
- [Foundations Knowledge](../docs/architecture/FOUNDATIONS_KNOWLEDGE_COMPLETE.md)
- [Autonomous Skills](../skills/)
- [Knowledge System](../knowledge/)
