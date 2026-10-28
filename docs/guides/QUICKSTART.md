# Quick Start Guide

Get started with AI Software Factory quickly.

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

## Prerequisites

- **Claude Code** v2.1.81+
- **Git** repository
- **Python 3.8+** (for harness)

---

## Option 1: Single Repository (Fastest)

### 1. Install Plugin

Use one of the installation methods above.

### 2. Navigate to Repository

```bash
cd /path/to/your/repo
```

### 3. Start Claude Code

```bash
claude
```

### 4. Implement an Issue

```bash
/autonomous-implement SEMI-1413
```

That's it! The skill will:
1. Fetch the Jira issue
2. Create a branch from main
3. Research the codebase
4. Create an implementation plan (you approve)
5. Generate tests
6. Implement the solution
7. Validate with tests
8. Create a PR
9. Update Jira

---

## Option 2: Multi-Repository with Orchestrator

### 1. Test Routing

```bash
cd ~/Documents/Development/EM-AISoftwareFactory
python3 -m harness test SEMI-1413
```

Output shows which repository the issue routes to and knowledge loaded.

### 2. Generate Instructions

```bash
python3 -m harness implement SEMI-1413
```

### 3. Follow the Instructions

The harness prints exact commands to run in Claude Code with knowledge context.

**Benefits:**
- Auto-routes to correct repository
- Loads repository knowledge
- Enforces Foundations standards
- Applies repo-specific patterns

---

## Available Skills

### End-to-End

- **`/autonomous-implement`** - Complete SDLC for one issue
- **`/autonomous-sprint`** - Implement full sprint
- **`/batch-implement`** - Parallel batch processing

### Core Development

- **`/create-plan`** - Generate implementation plan
- **`/implement-plan`** - Execute plan
- **`/eval-generator`** - Generate tests from acceptance criteria
- **`/create-pr`** - Create pull request
- **`/code-review`** - Automated code review
- **`/commit`** - Smart commit organization

### Research

- **`/research-codebase`** - Semantic code search
- **`/jira-to-branches`** - Batch branch creation
- **`/jira-update`** - Update Jira status

---

## Common Workflows

### Implement One Issue

```bash
/autonomous-implement SEMI-1413
```

### Implement Sprint

```bash
/autonomous-sprint --jql "sprint in openSprints()"
```

### Research Before Implementing

```bash
/research-codebase "How does wafer processing work?"
# Then:
/autonomous-implement SEMI-1413
```

### Batch Multiple Issues

```bash
/batch-implement SEMI-1413 SEMI-1414 SEMI-1415
```

---

## Checkpoints

The system has **2 checkpoints** for strategic decisions:

### 1. Plan Approval

After research, you review and approve the implementation plan.

**Why:** Ensures approach aligns with your architecture

### 2. PR Review

After implementation, you review the PR before merge.

**Why:** Final quality check and learning opportunity

---

## What Gets Automated

- Branch creation from main
- Codebase research
- Implementation planning
- Test generation
- Code implementation
- Test execution
- PR creation
- Code review
- Jira updates

**You decide:** Plan approval, PR merge

---

## Quality Guarantees

Every implementation includes:

- **80% test coverage minimum**
- **Air-gapped compliance** (no cloud APIs)
- **Pattern compliance** (repo-specific)
- **Security scanning** (gitleaks)
- **Automated code review**

---

## Troubleshooting

### "Skill not found"

```bash
# Verify plugin loaded
ls -la .claude/plugins/em-software-factory

# Restart Claude Code with plugin
claude --plugin-dir ~/Documents/Development/EM-AISoftwareFactory/.claude/plugins/em-software-factory
```

### "Branch created from wrong base"

This was fixed in the latest version. All branches now automatically created from main.

### "Can't find Jira issue"

The system uses mock data if Jira MCP is not configured. Issue keys must match pattern: `PROJECT-NUMBER` (e.g., `SEMI-1413`)

---

## Next Steps

1. Try `/autonomous-implement` on a real issue
2. Read [Harness Guide](HARNESS_GUIDE.md)
3. Set up Jira MCP for real data (optional)

---

## Learn More

- **Full README:** [../../README.md](../../README.md)
- **Harness Guide:** [HARNESS_GUIDE.md](HARNESS_GUIDE.md)
- **Engineering Standards:** [../../knowledge/foundations/standards.md](../../knowledge/foundations/standards.md) 
