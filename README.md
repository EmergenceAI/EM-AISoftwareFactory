# AI Software Factory

**Autonomous Engineering Operating System** for multi-repository software delivery.

Transform Jira issues into tested, reviewed PRs across multiple repositories with **one command**.

---

## Installation

### Option 1: Private Marketplace (Recommended)

```bash
# In Claude Code
/plugin install em-software-factory@em-plugins
```

Skills are available immediately across all projects.

### Option 2: Relative Path

```bash
# If the factory is in your workspace
claude --plugin-dir ../EM-AISoftwareFactory

# Or with full path
claude --plugin-dir /path/to/EM-AISoftwareFactory
```

---

## Quick Start

### Single Repository

```bash
# 1. Install the plugin (see Installation above)

# 2. Navigate to your repository
cd /path/to/your/repo

# 3. Start Claude Code
claude

# 4. Implement a Jira issue
/autonomous-implement SEMI-1413

# That's it! Creates plan → implements → tests → PR → updates Jira
```

### Multi-Repository with Orchestrator

```bash
# 1. Install the plugin (see Installation above)

# 2. From workspace root
cd /path/to/em-aisoftwarefactory

# 3. Auto-routes to correct repository and injects knowledge
python3 -m orchestrator implement SEMI-1413

# 4. Follow the printed instructions in Claude Code
```

---

## What Is This?

An **Engineering OS** that provides:

- **Single-Command SDLC** - From Jira → tested PR  
- **Multi-Repo Orchestration** - Auto-routes issues to 5 repositories  
- **Knowledge-Driven** - Applies repo-specific patterns automatically  
- **Quality Enforced** - 80% coverage, air-gapped, foundations standards  
- **80% Autonomous** - Strategic checkpoints only (plan, PR)

---

## Documentation

### Core Guides

| Guide | Description |
|-------|-------------|
| **[Quickstart](docs/guides/QUICKSTART.md)** | Get started |
| **[Orchestrator Usage](#orchestrator-usage)** | Single & multi-repo |
| **[Skills Reference](#skills-reference)** | All available skills |
| **[Knowledge System](#knowledge-system)** | Architecture, ADRs, patterns |

### Documentation

| Doc | Purpose |
|-----|---------|
| **[Foundations Standards](knowledge/foundations/standards.md)** | Air-gapped, DoD, engineering principles |
| **[Orchestrator Guide](docs/guides/ORCHESTRATOR_GUIDE.md)** | Complete orchestrator usage |
| **[Complete Docs](docs/README.md)** | Full documentation index |

---

## Orchestrator Usage

The orchestrator provides **workspace-level automation** with repository routing and knowledge injection.

### Single Repository

**Direct skill invocation (no orchestrator):**

```bash
# 1. Navigate to repository
cd /path/to/your/repo

# 2. Start Claude Code (plugin already installed)
claude

# 3. Run autonomous-implement
/autonomous-implement SEMI-1413
```

**What happens:**
- Fetches SEMI-1413 from Jira
- Creates branch from main
- Researches em-semi codebase
- Creates implementation plan
- Generates tests from acceptance criteria
- Implements solution
- Validates with tests
- Creates PR
- Updates Jira

**Limitations:**
- No repository-specific knowledge injection
- No Foundations standards enforcement
- Manual repository selection

---

### Multi-Repository with Orchestrator

**Orchestrator-based (recommended for production):**

```bash
# Step 1: Test routing
python3 -m orchestrator test SEMI-1413

# Output:
#  Routed SEMI-1413 → semi
#  Loaded knowledge: architecture, patterns, conventions

# Step 2: Generate implementation instructions
python3 -m orchestrator implement SEMI-1413

# Output:
#  Knowledge context prepared: /tmp/knowledge_context_xyz.md
#  Repository: /path/to/your/repo
# 
# To execute:
#   cd /path/to/your/repo
#   claude
#   /autonomous-implement SEMI-1413 --context-file /tmp/knowledge_context_xyz.md

# Step 3: Follow the instructions
# (Opens Claude Code and runs the skill with knowledge context)
```

**What the orchestrator adds:**
- **Auto-routing**: SEMI-1413 → em-semi (via Jira component)
- **Knowledge injection**: em-semi architecture/patterns
- **Foundations enforcement**: Air-gapped, 80% coverage, DoD
- **Standards compliance**: Automatic validation

**Routing logic:**
```yaml
# workspace.yaml
jira:
  component_mapping:
    Semi: semi                 # SEMI-* issues → em-semi
    Runtime: runtime           # RT-* issues → em-runtime
    UI: runtime-ui             # UI-* issues → em-runtime-ui
    Talk2Data: talk2data       # T2D-* issues → em-talk2data
    "Data Readiness": data-readiness
```

---

### Batch Multi-Repository

```bash
# Implement multiple issues across repositories
python3 -m orchestrator multi-repo SEMI-1413 T2D-890 RT-567

# Output:
#  SEMI-1413 → em-semi
#  T2D-890 → em-talk2data
#  RT-567 → em-runtime
# 
# Generated 3 instruction sets (see /tmp/orchestrator_instructions_*.sh)
```

---

## Skills Reference

### Autonomous Skills (End-to-End)

|-------|-------------|----------|------|
| **`/autonomous-implement`** | Full SDLC: Jira → PR | 80% (2 checkpoints) | 10 min |
| **`/autonomous-sprint`** | Full sprint automation | 80% (3 checkpoints) | 25 min |
| **`/batch-implement`** | Parallel batch processing | 80% (2 checkpoints) | 15 min |

### Core Development Skills

| Skill | Description | Autonomy |
|-------|-------------|----------|
| **`/create-plan`** | Generate implementation plan from Jira | 100% |
| **`/implement-plan`** | Execute phased implementation | 95% (1 checkpoint) |
| **`/eval-generator`** | Generate tests from acceptance criteria | 100% |
| **`/create-pr`** | Create pull request | 95% (1 checkpoint) |
| **`/code-review`** | Automated code review | 95% (1 checkpoint) |
| **`/commit`** | Smart commit organization | 100% |

### Research & Planning

| Skill | Description |
|-------|-------------|
| **`/research-codebase`** | Semantic code search |
| **`/jira-to-branches`** | Batch branch creation from JQL |
| **`/jira-update`** | Update Jira issue status |

**See [docs/guides/QUICKSTART.md](docs/guides/QUICKSTART.md) for detailed skill usage.**

---

## Knowledge System

The knowledge system extracts and applies repository-specific context automatically.

### What Gets Extracted

```
knowledge/
├── repositories/
│   ├── semi/
│   │   ├── architecture.md      ← em-semi architecture
│   │   ├── patterns.md          ← Coding patterns (context managers, etc.)
│   │   ├── conventions.md       ← Style guide (imports, type hints)
│   │   └── dependencies.md      ← Package management approach
│   ├── talk2data/
│   │   └── ...                  ← talk2data knowledge
│   └── runtime/
│       └── ...                  ← Runtime knowledge
└── foundations/
    ├── standards.md             ← Air-gapped requirements, DoD
    └── overview.md              ← Engineering principles
```

### Automatic Sync

```bash
# Runs automatically before orchestrator
./sync_knowledge.sh

# Or manually
./sync_knowledge.sh

# Only re-extracts if repository changed (git diff check)
```

### Pointing to Specific Knowledge

#### In Code

Knowledge is automatically injected via `--context-file`:

```bash
/autonomous-implement SEMI-1413 --context-file /tmp/knowledge_context.md
```

The context file contains:
```markdown
# Repository Knowledge Context

## Architecture
[Complete em-semi architecture patterns]

## Coding Patterns
[Context managers, async/await, type hints]

## Conventions
[Import style, naming, docstrings]

## Foundations Standards
### Air-Gapped Requirements (CRITICAL)
- NO cloud APIs (AWS, GCP, Azure)
...
```

#### Referencing ADRs

**Option 1: Add to knowledge extraction**

```bash
# Edit knowledge/repositories/semi/architecture.md
# Add section:

## Architecture Decision Records

### ADR-001: Event Sourcing for Workflow State
- Decision: Use event sourcing for all workflow state changes
- Rationale: Enables time-travel debugging and audit trails
- File: docs/adr/001-event-sourcing.md

### ADR-002: DuckDB for Analytics
- Decision: Embed DuckDB for local analytics queries
- Rationale: Air-gapped requirement, zero-dependency
- File: docs/adr/002-duckdb.md
```

**Option 2: Link in workspace.yaml**

```yaml
# workspace.yaml
repositories:
  - name: semi
    path: em-semi
    knowledge:
      adrs:
        - path: docs/adr/001-event-sourcing.md
          title: Event Sourcing for Workflow State
        - path: docs/adr/002-duckdb.md
          title: DuckDB for Analytics
```

**Option 3: Direct reference in prompts**

```bash
/autonomous-implement SEMI-1413

# Then mention in plan approval:
"Ensure this follows ADR-002 (DuckDB for analytics)"
```

---

## Workspace Configuration

### Repository Mapping

```yaml
# workspace.yaml
workspace:
  root: /path/to/your/workspace

repositories:
  - name: semi
    path: em-semi
    jira_component: Semi
    github: EmergenceAI/em-semi
    
  - name: talk2data
    path: em-talk2data
    jira_component: Talk2Data
    github: EmergenceAI/em-talk2data

jira:
  component_mapping:
    Semi: semi                    # Routes SEMI-* → em-semi
    Talk2Data: talk2data          # Routes T2D-* → em-talk2data
    Runtime: runtime
    UI: runtime-ui
    "Data Readiness": data-readiness
```

### Adding a New Repository

```bash
# 1. Add to workspace.yaml
# 2. Extract knowledge
./sync_knowledge.sh

# 3. Test routing
python3 -m orchestrator test YOUR-ISSUE-123

# 4. Verify knowledge loaded
# Should show: "Loaded knowledge for your-repo"
```

---

## Requirements

- **Claude Code** v2.1.81+ (for skills)
- **Python 3.8+** (for orchestrator)
- **Git** (for repositories)
- **Jira MCP** (optional, for real Jira data)

### Jira MCP Setup (Optional)

```bash
# Set environment variables
export JIRA_URL=https://your-company.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your_api_token

# Test connection
/mcp
```

**Without Jira MCP:** Uses mock data (still works for testing)

---

## Common Workflows

### Implement Single Issue

```bash
# Quick (no orchestrator)
cd /path/to/your/repo && /autonomous-implement SEMI-1413

# Full (with knowledge)
python3 -m orchestrator implement SEMI-1413
# Follow instructions
```

### Implement Sprint

```bash
# All issues in sprint
/autonomous-sprint --jql "sprint in openSprints()"

# Specific filter
/autonomous-sprint --jql "filter = 17150"
```

### Research First

```bash
# Understand codebase before implementing
/research-codebase "How does wafer processing work?"

# Then implement
/autonomous-implement SEMI-1413
```

---

## Troubleshooting

### "Can't find repository"

```bash
# Check workspace.yaml
cat workspace.yaml | grep -A 5 "repositories:"

# Verify path exists
ls -la /path/to/your/repo
```

### "No knowledge found"

```bash
# Sync knowledge
./sync_knowledge.sh

# Check extracted
ls -la knowledge/repositories/semi/
```

### "Routing to wrong repository"

```bash
# Test routing
python3 -m orchestrator test SEMI-1413

# Check Jira component mapping
cat workspace.yaml | grep -A 10 "component_mapping:"
```

### "Branch created from wrong base"

Fixed in latest version! All branches now created from main automatically.

See [CRITICAL_FIX_BRANCHING.md](CRITICAL_FIX_BRANCHING.md) for details.

---

## Next Steps

1. **[5 min]** Read [Quickstart Guide](docs/guides/QUICKSTART.md)
2. **[10 min]** Try `/autonomous-implement` on a real issue
3. **[15 min]** Set up orchestrator for your workspace
4. **[Optional]** Configure Jira MCP for real data

---

## Support

- **Documentation:** [docs/README.md](docs/README.md)
- **Issues:** GitHub Issues
- **Internal:** #ai-software-factory Slack

