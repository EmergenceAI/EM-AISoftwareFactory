# Engineering OS Quick Start Guide

## Overview

This guide gets you started with the Engineering Operating System architecture in under 30 minutes.

---

## Prerequisites

- Python 3.10+ installed
- All repositories cloned to `~/Documents/Development/`
- Jira and Confluence credentials configured

---

## Step 1: Verify Workspace Configuration (5 min)

### Check Repository Paths

```bash
cd /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory

# Verify all repositories exist
python3 -c "
import yaml
from pathlib import Path

with open('workspace.yaml') as f:
    workspace = yaml.safe_load(f)

root = Path(workspace['workspace']['root'])
print(f'Workspace root: {root}')

for repo in workspace['repositories']:
    repo_path = root / repo['path']
    exists = '✅' if repo_path.exists() else '❌'
    print(f'{exists} {repo[\"name\"]}: {repo_path}')
"
```

**Expected output:**
```
Workspace root: /Users/malamunisamy/Documents/Development
✅ runtime: /Users/malamunisamy/Documents/Development/em-runtime
✅ runtime-ui: /Users/malamunisamy/Documents/Development/em-runtime-ui
✅ talk2data: /Users/malamunisamy/Documents/Development/em-talk2data
✅ connectors: /Users/malamunisamy/Documents/Development/em-connectors
✅ sdk: /Users/malamunisamy/Documents/Development/em-sdk
✅ data-readiness: /Users/malamunisamy/Documents/Development/em-data-readiness
```

If any show ❌, update the `path` in [workspace.yaml](./workspace.yaml).

---

## Step 2: Test Runtime Adapter (10 min)

### Create Test Script

```bash
cat > test_adapter.py << 'EOF'
#!/usr/bin/env python3
"""Quick test of runtime adapter."""

import sys
from pathlib import Path
import yaml

# Add adapters to path
sys.path.insert(0, str(Path(__file__).parent))

from adapters.runtime import RuntimeAdapter

# Load workspace config
with open('workspace.yaml') as f:
    workspace_config = yaml.safe_load(f)

workspace_root = Path(workspace_config['workspace']['root'])

# Find runtime config
runtime_config = next(
    r for r in workspace_config['repositories'] 
    if r['name'] == 'runtime'
)

# Create adapter
adapter = RuntimeAdapter(workspace_root, runtime_config)

# Test metadata
print("=" * 60)
print("RUNTIME ADAPTER TEST")
print("=" * 60)
print()

metadata = adapter.get_metadata()
print(f"Repository: {metadata.display_name}")
print(f"Path: {metadata.path}")
print(f"Language: {metadata.primary_language}")
print(f"Build System: {metadata.build_system}")
print(f"Test Framework: {metadata.test_framework}")
print()

# Test conventions
print("Conventions:")
conventions = adapter.get_conventions()
for key, value in conventions.items():
    print(f"  - {key}: {value}")
print()

# Test branch creation (dry run - we'll just generate the name)
print("Branch naming examples:")
examples = [
    ("ABI-123", "Story", "Add user authentication"),
    ("ABI-456", "Bug", "Fix memory leak in executor"),
    ("ABI-789", "Task", "Update dependencies")
]

for issue_key, issue_type, summary in examples:
    # Don't actually create branch, just show what it would be
    prefix_map = {'Story': 'feature', 'Bug': 'bugfix', 'Task': 'task'}
    prefix = prefix_map.get(issue_type, 'feature')
    slug = summary.lower().replace(' ', '-')[:50].strip('-')
    branch = f"{prefix}/{issue_key}-{slug}"
    print(f"  {issue_key} ({issue_type}): {branch}")

print()
print("=" * 60)
print("✅ Adapter test complete!")
print("=" * 60)
EOF

chmod +x test_adapter.py
```

### Run Test

```bash
python3 test_adapter.py
```

**Expected output:**
```
============================================================
RUNTIME ADAPTER TEST
============================================================

Repository: EM Runtime
Path: /Users/malamunisamy/Documents/Development/em-runtime
Language: python
Build System: poetry
Test Framework: pytest

Conventions:
  - imports: absolute
  - typing: strict (mypy)
  - docstrings: google style
  - test_naming: test_* for functions, Test* for classes
  - error_handling: explicit exceptions, no bare except
  - async: asyncio for I/O, avoid threading

Branch naming examples:
  ABI-123 (Story): feature/ABI-123-add-user-authentication
  ABI-456 (Bug): bugfix/ABI-456-fix-memory-leak-in-executor
  ABI-789 (Task): task/ABI-789-update-dependencies

============================================================
✅ Adapter test complete!
============================================================
```

---

## Step 3: Create First Knowledge Pack (15 min)

### Runtime Knowledge Pack

```bash
# Create directory
mkdir -p knowledge/repositories/runtime

# Create architecture.md
cat > knowledge/repositories/runtime/architecture.md << 'EOF'
# EM Runtime Architecture

## Overview
EM Runtime is a Python-based workflow orchestration and execution engine for AI agents.

## System Components

### 1. Executor (`src/runtime/executor/`)
Core execution engine that runs agent workflows.

**Key Files:**
- `engine.py` - Main execution loop
- `state.py` - Workflow state management
- `context.py` - Execution context

**Responsibilities:**
- Execute agent workflows
- Manage workflow lifecycle
- Handle state persistence
- Coordinate distributed execution

### 2. API (`src/runtime/api/`)
HTTP API for runtime control and monitoring.

**Key Files:**
- `server.py` - FastAPI application
- `routes/` - API endpoints
- `middleware/` - Request/response middleware

**Responsibilities:**
- REST API for workflow management
- Webhook endpoints for events
- Health checks and metrics

### 3. Message Bus (`src/runtime/bus/`)
Event-driven communication layer.

**Key Files:**
- `broker.py` - Message broker
- `events.py` - Event definitions
- `handlers.py` - Event handlers

**Responsibilities:**
- Pub/sub messaging
- Event routing
- Cross-component communication

### 4. Plugin System (`src/runtime/plugins/`)
Extensible tooling framework.

**Key Files:**
- `manager.py` - Plugin lifecycle
- `loader.py` - Dynamic plugin loading
- `registry.py` - Plugin registry

**Responsibilities:**
- Load plugins dynamically
- Manage plugin dependencies
- Expose plugin APIs

## Architecture Patterns

### Repository Pattern
All data access goes through repository interfaces:
- `WorkflowRepository` - Workflow storage
- `StateRepository` - State persistence
- `EventRepository` - Event log

### Factory Pattern
Object creation via factories:
- `AgentFactory` - Create agent instances
- `ToolFactory` - Create tool instances
- `ConnectorFactory` - Create connector instances

### Observer Pattern
Event-driven architecture:
- Components subscribe to events
- Event bus dispatches events
- Handlers react to events

## Data Flow

```
Client → API → Executor → Agent → Tools → Connectors → External Systems
                    ↓
                State Store
                    ↓
                Event Bus → Event Handlers
```

## Entry Points

1. **CLI**: `src/runtime/main.py`
   - Command-line interface
   - Workflow execution
   - Admin commands

2. **API Server**: `src/runtime/api/server.py`
   - HTTP API
   - Port 8000 by default

3. **Library**: `src/runtime/__init__.py`
   - Import as library
   - Embed in other applications

## Dependencies

### Core Dependencies
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Redis** - Caching and pub/sub
- **Celery** - Task queue

### Internal Dependencies
- **em-sdk** - Core SDK and shared libraries
- **em-connectors** - Data connectors

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Test individual components
- Mock external dependencies
- Fast execution

### Integration Tests (`tests/integration/`)
- Test component interactions
- Real database/Redis
- Moderate execution time

### E2E Tests (`tests/e2e/`)
- Test full workflows
- Real external systems
- Slow execution

## Build and Deployment

### Local Development
```bash
poetry install
poetry run pytest
poetry run python -m runtime.main
```

### Docker
```bash
docker build -t em-runtime .
docker run -p 8000:8000 em-runtime
```

### Production
- Deployed to Kubernetes
- Auto-scaling enabled
- Redis cluster for state
EOF

# Create patterns.md
cat > knowledge/repositories/runtime/patterns.md << 'EOF'
# EM Runtime Coding Patterns

## Common Patterns

### 1. Async/Await for I/O
All I/O operations use asyncio:

```python
async def execute_workflow(workflow_id: str) -> WorkflowResult:
    """Execute workflow asynchronously."""
    state = await state_repo.get(workflow_id)
    result = await executor.run(state)
    await state_repo.save(result)
    return result
```

### 2. Repository Pattern for Data Access
Never access database directly - use repositories:

```python
class WorkflowRepository:
    async def get(self, workflow_id: str) -> Workflow:
        """Get workflow by ID."""
        pass
    
    async def save(self, workflow: Workflow) -> None:
        """Save workflow."""
        pass
```

### 3. Dependency Injection
Components receive dependencies via constructor:

```python
class Executor:
    def __init__(
        self,
        state_repo: StateRepository,
        event_bus: EventBus,
        logger: Logger
    ):
        self.state_repo = state_repo
        self.event_bus = event_bus
        self.logger = logger
```

### 4. Error Handling
Explicit exception hierarchy:

```python
class RuntimeError(Exception):
    """Base exception for runtime errors."""
    pass

class WorkflowExecutionError(RuntimeError):
    """Workflow execution failed."""
    pass

# Usage
try:
    result = await executor.run(workflow)
except WorkflowExecutionError as e:
    logger.error(f"Workflow failed: {e}")
    await rollback(workflow)
```

### 5. Event-Driven Communication
Publish events for cross-component communication:

```python
# Publisher
await event_bus.publish(
    WorkflowStartedEvent(workflow_id=workflow_id)
)

# Subscriber
@event_bus.subscribe(WorkflowStartedEvent)
async def on_workflow_started(event: WorkflowStartedEvent):
    logger.info(f"Workflow {event.workflow_id} started")
```

## Anti-Patterns to Avoid

### ❌ Synchronous I/O
```python
# Bad
def get_workflow(workflow_id: str):
    return db.query(Workflow).filter_by(id=workflow_id).first()

# Good
async def get_workflow(workflow_id: str):
    return await db.query(Workflow).filter_by(id=workflow_id).first()
```

### ❌ Circular Imports
```python
# Bad - circular dependency
from runtime.executor import Executor
from runtime.state import StateManager  # StateManager imports Executor

# Good - use protocols or dependency injection
from typing import Protocol

class ExecutorProtocol(Protocol):
    async def run(self, workflow: Workflow) -> Result: ...
```

### ❌ Bare Except
```python
# Bad
try:
    result = await execute()
except:  # Never catch all exceptions
    pass

# Good
try:
    result = await execute()
except (WorkflowError, ValidationError) as e:
    logger.error(f"Known error: {e}")
    raise
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise RuntimeError("Unexpected failure") from e
```

## Best Practices

1. **Type Hints Everywhere**
   - Use strict typing
   - Run mypy in CI
   - No `Any` unless absolutely necessary

2. **Docstrings**
   - Google style
   - Include Args, Returns, Raises
   - Examples for complex functions

3. **Testing**
   - Unit tests for logic
   - Integration tests for I/O
   - Mock external dependencies

4. **Logging**
   - Structured logging (JSON)
   - Include correlation IDs
   - Log at appropriate levels

5. **Configuration**
   - Environment variables for config
   - Pydantic for validation
   - Fail fast on invalid config
EOF

# Create conventions.md
cat > knowledge/repositories/runtime/conventions.md << 'EOF'
# EM Runtime Coding Conventions

## Code Style

### Python Style
- **PEP 8** compliance
- **Line length**: 100 characters
- **Quotes**: Double quotes for strings
- **Imports**: Absolute imports only

### Linting
- **Tool**: ruff
- **Config**: `pyproject.toml`
- **Run**: `poetry run ruff check .`

### Formatting
- **Tool**: black
- **Config**: `pyproject.toml`
- **Run**: `poetry run black .`

## Naming Conventions

### Files and Directories
- **Modules**: lowercase with underscores (`workflow_executor.py`)
- **Packages**: lowercase, no underscores (`runtime`, not `run_time`)
- **Test files**: `test_*.py`

### Classes and Functions
- **Classes**: PascalCase (`WorkflowExecutor`)
- **Functions**: snake_case (`execute_workflow`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- **Private**: Leading underscore (`_internal_method`)

### Variables
- **Local**: snake_case (`workflow_id`)
- **Instance**: snake_case (`self.executor`)
- **Class**: UPPER_SNAKE_CASE (`WorkflowExecutor.DEFAULT_TIMEOUT`)

## Project Structure

```
em-runtime/
├── src/
│   └── runtime/
│       ├── __init__.py
│       ├── main.py
│       ├── executor/
│       ├── api/
│       ├── bus/
│       └── plugins/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── pyproject.toml
└── README.md
```

## Testing Conventions

### Test Naming
- **Test files**: `test_*.py`
- **Test functions**: `test_<what>_<condition>_<expected>()`
- **Test classes**: `Test<ClassName>`

### Test Structure
```python
def test_execute_workflow_with_valid_input_returns_result():
    # Arrange
    workflow = create_test_workflow()
    executor = WorkflowExecutor()
    
    # Act
    result = await executor.execute(workflow)
    
    # Assert
    assert result.status == "completed"
    assert result.output is not None
```

### Fixtures
```python
import pytest

@pytest.fixture
async def executor():
    """Create executor instance for tests."""
    return WorkflowExecutor()

@pytest.fixture
async def sample_workflow():
    """Create sample workflow for tests."""
    return Workflow(id="test-123", steps=[...])
```

## Documentation

### Docstrings
```python
async def execute_workflow(
    workflow_id: str,
    timeout: Optional[int] = None
) -> WorkflowResult:
    """
    Execute a workflow by ID.
    
    Args:
        workflow_id: Unique workflow identifier
        timeout: Optional timeout in seconds (default: 300)
    
    Returns:
        WorkflowResult containing execution status and output
    
    Raises:
        WorkflowNotFoundError: If workflow ID doesn't exist
        WorkflowExecutionError: If execution fails
        TimeoutError: If execution exceeds timeout
    
    Example:
        >>> result = await execute_workflow("wf-123", timeout=60)
        >>> print(result.status)
        'completed'
    """
    pass
```

## Git Conventions

### Branch Naming
- **Features**: `feature/ABI-123-short-description`
- **Bugs**: `bugfix/ABI-456-short-description`
- **Tasks**: `task/ABI-789-short-description`

### Commit Messages
```
type(scope): Short description

Longer explanation if needed.

Closes ABI-123
```

**Types**: feat, fix, docs, style, refactor, test, chore

### PR Description
- Link to Jira ticket
- Summary of changes
- Testing done
- Screenshots (if UI)
EOF

echo "✅ Runtime knowledge pack created!"
echo ""
echo "Files created:"
echo "  - knowledge/repositories/runtime/architecture.md"
echo "  - knowledge/repositories/runtime/patterns.md"  
echo "  - knowledge/repositories/runtime/conventions.md"
```

---

## Step 4: Next Steps

### Immediate (Today)
1. ✅ Review architecture documentation
2. ✅ Verify adapter works
3. [ ] Create UI adapter (`adapters/ui.py`)
4. [ ] Create UI knowledge pack

### This Week
1. [ ] Implement knowledge engine (`orchestrator/knowledge.py`)
2. [ ] Test knowledge retrieval
3. [ ] Create first ADR
4. [ ] Begin orchestrator planner

### Next Week
1. [ ] Complete Phase 1 (Foundation)
2. [ ] Start Phase 2 (Knowledge Layer)
3. [ ] Extract remaining knowledge packs
4. [ ] Test task graph generation

---

## Troubleshooting

### Issue: Repository path not found
**Solution:** Update `workspace.yaml` with correct paths

### Issue: Import error for adapters
**Solution:** Ensure you're running from factory root directory

### Issue: Poetry/pnpm not found
**Solution:** Install build tools for your repositories

---

## Resources

- [ENGINEERING_OS_ARCHITECTURE.md](./ENGINEERING_OS_ARCHITECTURE.md) - Full architecture
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Detailed roadmap
- [workspace.yaml](./workspace.yaml) - Workspace configuration

---

## Questions?

Review the architecture docs or start implementing Phase 1!

The foundation is in place. Now build the orchestrator that makes it all work together.
