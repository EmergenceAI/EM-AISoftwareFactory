# Documentation

Complete documentation for AI Software Factory.

---

## Getting Started

| Doc | Description |
|-----|-------------|
| **[Quick Start](guides/QUICKSTART.md)** | Get started quickly |
| **[Harness Guide](guides/HARNESS_GUIDE.md)** | Complete harness usage |
| **[Main README](../README.md)** | Overview and installation |

---

## Documentation by Category

### Setup

The system is pre-configured and ready to use:

```bash
# Knowledge extraction happens automatically
./sync_knowledge.sh

# Skills work autonomously - just use them!
/autonomous-implement ABI-123
```

**For advanced configuration:**
- `.claude/settings.json` - Factory defaults (80/20 autonomous mode)
- `.claude/settings.local.json` - Personal overrides (optional)
- `workspace.yaml` - Repository routing and configuration

---

### Standards

Platform engineering standards and requirements:

- **[Definition of Done](../knowledge/foundations/standards.md#definition-of-done-per-pr-checklist)** - Required for every PR
- **[Engineering Principles](../knowledge/foundations/standards.md#engineering-principles)** - Core principles
- **[Air-Gapped Requirements](../knowledge/foundations/standards.md#air-gapped--bare-metal)** - CRITICAL deployment constraints
- **[Platform Overview](../knowledge/foundations/overview.md)** - Architecture and ADRs

---

### User Guides

How to use the factory effectively:

- **[Quickstart](guides/QUICKSTART.md)** - Get started
- **[Harness Guide](guides/HARNESS_GUIDE.md)** - Complete harness usage
- **[Testing Guide](guides/TESTING_GUIDE.md)** - Multi-agent system testing

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

## Documentation Structure

```
docs/
├── README.md                                    # This file
└── guides/                                      # User guides
    ├── QUICKSTART.md                            # Quick start
    ├── HARNESS_GUIDE.md                    # Harness usage
    └── TESTING_GUIDE.md                         # Testing multi-agent

knowledge/foundations/
├── standards.md                                 # Engineering standards
└── overview.md                                  # Platform overview

.claude/
├── SETTINGS_README.md                           # Configuration guide
├── settings.json                                # Factory defaults (80/20 mode)
└── settings.local.json.template                 # Personal overrides template
```

---

## Key Features

### 1. Automated Knowledge Management

Knowledge automatically extracted from repositories:
- Syncs from README.md and docs/
- Tracks git changes (only re-extracts if changed)
- Zero maintenance (read-only generated artifacts)

```bash
# Automatic sync before harness runs
ensure_knowledge_fresh()

# Manual sync anytime
./sync_knowledge.sh
```

### 2. 80/20 Autonomous Mode

Skills run with minimal prompts:
- 100% autonomous: 9 skills (research, plan, commit, etc.)
- 95% autonomous: 3 skills (1 checkpoint)
- 80% autonomous: 3 skills (2-3 strategic checkpoints)

**Average: ~85% autonomous across all skills**

### 3. Multi-Repository Support

Orchestrator handles 7 repositories:
- runtime, runtime-ui, talk2data
- data-readiness, semi
- connectors, sdk (paths TBD)

### 4. Foundations Standards Enforcement

Platform standards automatically enforced:
- Air-gapped compatibility checks
- 80% test coverage requirement
- Pacto contract validation
- gitleaks secret detection

---

## Repository Knowledge

Knowledge has been extracted from all repositories.

| Repository | Status |
|------------|--------|
| talk2data | Complete |
| semi | Complete |
| em-foundations | Complete |
| data-readiness | Complete |
| runtime | Complete |
| runtime-ui | Complete |

---

## Skills Reference

### Fully Autonomous (0 checkpoints)
- `/research-codebase` - Search and understand codebase
- `/create-plan` - Generate implementation plan
- `/eval-generator` - Create evaluation tests
- `/commit` - Create conventional commits
- `/jira-to-branches` - Create branches from Jira

### Mostly Autonomous (1 checkpoint)
- `/implement-plan` - Implement from plan ( before commit)
- `/create-pr` - Create pull request ( before PR)
- `/code-review` - Automated review ( if critical)

### High-Value Autonomous (2-3 checkpoints)
- `/autonomous-implement` - End-to-end implementation ( plan, evals, PR)
- `/batch-implement` - Parallel batch implementation ( plans, tests)
- `/autonomous-sprint` - Full sprint automation ( audit, failures, summary)

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

---

## Common Workflows

### Single Issue Implementation
```bash
/autonomous-implement ABI-123
# Prompts: 3 (plan, evals, PR)
```

### Batch Implementation
```bash
/batch-implement SEMI-1 SEMI-2 SEMI-3
# Prompts: 2 (plans, test failures)
```

### Sprint Automation
```bash
/autonomous-sprint --jql "sprint in openSprints()"
# Prompts: 3 (audit, failures, summary)
# Parallelization: concurrent agents
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
- NO cloud-specific APIs (GCP, AWS, Azure)
- NO cloud IAM dependencies
- NO managed services in code
- Helm charts deploy without cloud provider

**Allowed infrastructure (via Crossplane only):**
- PostgreSQL, Redis, S3 buckets, Secrets

### Definition of Done

Every PR must have:
1. 80% test coverage
2. Pacto contract valid
3. No secrets in code (gitleaks passes)
4. Documentation updated
5. Air-gapped compatible
6. Deploys via standard pipeline

See [Engineering Standards](../knowledge/foundations/standards.md) for complete requirements.

---

## Support

### Documentation Issues

Found outdated or incorrect documentation?
1. Check if newer version exists in this docs/ folder
2. Open issue or submit PR

### Getting Help

- **Usage questions:** See [User Guides](guides/)
- **Standards:** See [Engineering Standards](../knowledge/foundations/standards.md)
- **Skills:** Run `/help` or check [skills/](../skills/) directory

---

## What's Next?

1. **Read:** [Quickstart Guide](guides/QUICKSTART.md)
2. **Try:** Run `/autonomous-implement` on a real issue
3. **Customize:** Create `.claude/settings.local.json` if needed

---

## Contributing

Found an issue or want to improve the documentation?

1. All documentation is in `docs/`
2. Follow the existing structure
3. Update this README if adding new docs
4. Keep docs current - remove outdated content
