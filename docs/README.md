# AI Software Factory - Documentation

Complete documentation for the Engineering Operating System.

---

## Quick Start

**New to the factory?** Start here:

1. [Quickstart Guide](guides/QUICKSTART.md) - Get up and running in 5 minutes
2. [Architecture Overview](architecture/ENGINEERING_OS_ARCHITECTURE.md) - Understand how it works
3. [Testing Guide](guides/TESTING_GUIDE.md) - Run your first autonomous workflow

---

## Documentation by Category

### 🚀 Setup Guides

Complete setup documentation for all components:

- **[Knowledge Setup](setup/KNOWLEDGE_SETUP_COMPLETE.md)** - Automated knowledge extraction from repositories
- **[Silent Mode Setup](setup/SILENT_MODE_COMPLETE.md)** - 80/20 autonomous configuration
- **[EM-Semi Integration](setup/EM_SEMI_INTEGRATION.md)** - Semiconductor platform integration
- **[Orchestrator Implementation](setup/ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md)** - Workspace-level orchestration
- **[MCP Integration](setup/ORCHESTRATOR_MCP_INTEGRATION.md)** - Jira MCP and knowledge context
- **[Integration Summary](setup/INTEGRATION_COMPLETE_SUMMARY.md)** - Complete integration overview

**Quick setup:**
```bash
# Knowledge extraction happens automatically
./sync_knowledge.sh

# Silent mode is pre-configured
# Just run skills - they work autonomously!
/autonomous-implement ABI-123
```

---

### 🏗️ Architecture

System design and architectural decisions:

- **[Engineering OS Architecture](architecture/ENGINEERING_OS_ARCHITECTURE.md)** - Complete system design
  - Orchestrator pattern (Router → Planner → Executor → Reporter)
  - Knowledge Engine (automated extraction & sync)
  - Repository Adapters (standardized interface)
  - Multi-agent workflows

- **[Foundations Knowledge](architecture/FOUNDATIONS_KNOWLEDGE_COMPLETE.md)** - Platform standards
  - Air-gapped requirements (CRITICAL)
  - Definition of Done (per-PR checklist)
  - Engineering Principles (13 core principles)
  - ADRs and constraints

**Key Concepts:**
- **Orchestrator** routes issues to repositories automatically
- **Knowledge** syncs from README/docs before each run
- **Adapters** provide uniform interface (build/test/lint/deploy)
- **Workflows** parallelize work across agents

---

### 📖 User Guides

How to use the factory effectively:

- **[Quickstart](guides/QUICKSTART.md)** - 5-minute introduction
- **[Testing Guide](guides/TESTING_GUIDE.md)** - Multi-agent system testing
- **[Silent Mode Strategy](guides/SILENT_MODE_STRATEGY.md)** - Understanding 80/20 autonomous mode

**Common Tasks:**
```bash
# Implement a single issue
/autonomous-implement ABI-123

# Batch implement multiple issues
/batch-implement SEMI-1 SEMI-2 SEMI-3

# Implement entire sprint (parallel)
/autonomous-sprint --jql "filter = 17150"

# Research codebase
/research-codebase "How does authentication work?"
```

---

### 📚 Reference

Detailed reference documentation:

- **[Multi-Agent Workflows](reference/MULTI_AGENT_COMPLETE.md)** - Complete workflow documentation
  - Workflow API and patterns
  - Agent orchestration
  - Parallel execution strategies
  - Error handling and recovery

- **[SDLC Metrics](reference/SDLC_METRICS_COMPLETE_GUIDE.md)** - Metrics and reporting
  - Sprint metrics
  - PR analysis
  - Velocity tracking
  - Quality metrics

**Example Workflow:**
```javascript
// Parallel implementation with eval validation
const results = await pipeline(
  issues,
  issue => agent(`/autonomous-implement ${issue.key}`, {
    isolation: 'worktree',
    schema: IMPLEMENTATION_SCHEMA
  })
)
```

---

## Documentation Structure

```
docs/
├── README.md                                    # This file
│
├── setup/                                       # Setup guides
│   ├── KNOWLEDGE_SETUP_COMPLETE.md              # Knowledge extraction
│   ├── SILENT_MODE_COMPLETE.md                  # Autonomous configuration
│   ├── EM_SEMI_INTEGRATION.md                   # EM-Semi integration
│   ├── ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md  # Orchestrator setup
│   ├── ORCHESTRATOR_MCP_INTEGRATION.md          # MCP & context integration
│   └── INTEGRATION_COMPLETE_SUMMARY.md          # Complete integration summary
│
├── architecture/                                # System design
│   ├── ENGINEERING_OS_ARCHITECTURE.md           # Complete architecture
│   └── FOUNDATIONS_KNOWLEDGE_COMPLETE.md        # Platform standards
│
├── guides/                                      # User guides
│   ├── QUICKSTART.md                            # 5-minute start
│   ├── TESTING_GUIDE.md                         # Testing multi-agent
│   └── SILENT_MODE_STRATEGY.md                  # 80/20 autonomous mode
│
└── reference/                                   # Detailed reference
    ├── MULTI_AGENT_COMPLETE.md                  # Workflow API
    └── SDLC_METRICS_COMPLETE_GUIDE.md           # Metrics reference
```

---

## Key Features

### 1. Automated Knowledge Management

Knowledge automatically extracted from repositories:
- ✅ Syncs from README.md and docs/
- ✅ Tracks git changes (only re-extracts if changed)
- ✅ Zero maintenance (read-only generated artifacts)

```bash
# Automatic sync before orchestrator runs
ensure_knowledge_fresh()

# Manual sync anytime
./sync_knowledge.sh
```

### 2. 80/20 Autonomous Mode

Skills run with minimal prompts:
- ✅ 100% autonomous: 9 skills (research, plan, commit, etc.)
- ✅ 95% autonomous: 3 skills (1 checkpoint)
- ✅ 80% autonomous: 3 skills (2-3 strategic checkpoints)

**Average: ~85% autonomous across all skills**

### 3. Multi-Repository Support

Orchestrator handles 7 repositories:
- runtime, runtime-ui, talk2data
- data-readiness, semi
- connectors, sdk (paths TBD)

### 4. Foundations Standards Enforcement

Platform standards automatically enforced:
- ✅ Air-gapped compatibility checks
- ✅ 80% test coverage requirement
- ✅ Pacto contract validation
- ✅ gitleaks secret detection

---

## Repository Knowledge

Total knowledge extracted: **3,818 lines**

| Repository | Architecture | Status |
|------------|-------------|--------|
| talk2data | 2,093 lines | ✅ |
| semi | 789 lines | ✅ |
| em-foundations | 850 lines | ✅ |
| data-readiness | 32 lines | ✅ |
| runtime | 31 lines | ✅ |
| runtime-ui | 23 lines | ✅ |

---

## Skills Reference

### Fully Autonomous (0 checkpoints)
- `/research-codebase` - Search and understand codebase
- `/create-plan` - Generate implementation plan
- `/eval-generator` - Create evaluation tests
- `/commit` - Create conventional commits
- `/jira-to-branches` - Create branches from Jira

### Mostly Autonomous (1 checkpoint)
- `/implement-plan` - Implement from plan (⏸️ before commit)
- `/create-pr` - Create pull request (⏸️ before PR)
- `/code-review` - Automated review (⏸️ if critical)

### High-Value Autonomous (2-3 checkpoints)
- `/autonomous-implement` - End-to-end implementation (⏸️ plan, evals, PR)
- `/batch-implement` - Parallel batch implementation (⏸️ plans, tests)
- `/autonomous-sprint` - Full sprint automation (⏸️ audit, failures, summary)

---

## Configuration

### Default Settings

**Everyone gets 80/20 mode:**
- `.claude/settings.json` - Factory defaults (in git)
- Auto-approves safe operations
- Strategic checkpoints only

### Personal Customization

**Override defaults:**
```bash
# Copy template
cp .claude/settings.local.json.template .claude/settings.local.json

# Edit preferences
vim .claude/settings.local.json

# Your overrides are git-ignored
```

See [Silent Mode Setup](setup/SILENT_MODE_COMPLETE.md) for details.

---

## Common Workflows

### Single Issue Implementation
```bash
/autonomous-implement ABI-123
# Prompts: 3 (plan, evals, PR)
# Time: 4-8 minutes
```

### Batch Implementation
```bash
/batch-implement SEMI-1 SEMI-2 SEMI-3
# Prompts: 2 (plans, test failures)
# Time: 10-15 minutes for 10 issues
```

### Sprint Automation
```bash
/autonomous-sprint --jql "sprint in openSprints()"
# Prompts: 3 (audit, failures, summary)
# Time: 12-28 minutes for 32 issues
# Parallelization: 8 concurrent agents
```

### Research & Planning
```bash
# Research (0 prompts)
/research-codebase "How does authentication work?"

# Plan (0 prompts)
/create-plan ABI-123

# Evals (0 prompts)
/eval-generator ABI-123
```

---

## Platform Standards

### Air-Gapped Requirements (CRITICAL)

**Every service MUST work air-gapped:**
- ❌ NO cloud-specific APIs (GCP, AWS, Azure)
- ❌ NO cloud IAM dependencies
- ❌ NO managed services in code
- ✅ Helm charts deploy without cloud provider

**Allowed infrastructure (via Crossplane only):**
- PostgreSQL, Redis, S3 buckets, Secrets

### Definition of Done

Every PR must have:
1. ✅ 80% test coverage
2. ✅ Pacto contract valid
3. ✅ No secrets in code (gitleaks passes)
4. ✅ Documentation updated
5. ✅ Air-gapped compatible
6. ✅ Deploys via standard pipeline

See [Foundations Knowledge](architecture/FOUNDATIONS_KNOWLEDGE_COMPLETE.md) for complete standards.

---

## Support

### Documentation Issues

Found outdated or incorrect documentation?
1. Check if newer version exists in this docs/ folder
2. Check [archive/](archive/) for historical context
3. Open issue or submit PR

### Getting Help

- **Architecture questions:** See [Engineering OS Architecture](architecture/ENGINEERING_OS_ARCHITECTURE.md)
- **Setup issues:** See [Setup Guides](setup/)
- **Usage questions:** See [User Guides](guides/)
- **Workflow API:** See [Multi-Agent Reference](reference/MULTI_AGENT_COMPLETE.md)

---

## What's Next?

1. **Read:** [Quickstart Guide](guides/QUICKSTART.md) - 5 minutes
2. **Understand:** [Architecture Overview](architecture/ENGINEERING_OS_ARCHITECTURE.md) - 15 minutes
3. **Try:** Run `/autonomous-implement` on a real issue - 5 minutes
4. **Customize:** Create `.claude/settings.local.json` if needed - Optional

**Total time to productivity: ~25 minutes**

---

## Contributing

Found an issue or want to improve the documentation?

1. All documentation is in `docs/`
2. Follow the existing structure
3. Update this README if adding new docs
4. Keep docs current - remove outdated content
