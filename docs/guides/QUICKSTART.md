# Quick Start Guide

Get started with AI Software Factory in **5 minutes**.

---

## Prerequisites

- **Claude Code** v2.1.81+
- **Git** repository
- **Python 3.8+** (for orchestrator)

---

## Option 1: Single Repository (Fastest)

### 1. Navigate to Repository

```bash
cd ~/Documents/Development/em-semi
```

### 2. Start Claude Code

```bash
claude --plugin-dir ~/Documents/Development/EM-AISoftwareFactory/.claude/plugins/em-software-factory
```

### 3. Implement an Issue

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

**Time:** ~10 minutes from Jira to PR

---

## Option 2: Multi-Repository with Orchestrator

### 1. Test Routing

```bash
cd ~/Documents/Development/EM-AISoftwareFactory
python3 -m orchestrator test SEMI-1413
```

Output shows which repository the issue routes to and knowledge loaded.

### 2. Generate Instructions

```bash
python3 -m orchestrator implement SEMI-1413
```

### 3. Follow the Instructions

The orchestrator prints exact commands to run in Claude Code with knowledge context.

**Benefits:**
- ✅ Auto-routes to correct repository
- ✅ Loads 45KB+ of repository knowledge
- ✅ Enforces Foundations standards
- ✅ Applies repo-specific patterns

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

- ✅ Branch creation from main
- ✅ Codebase research
- ✅ Implementation planning
- ✅ Test generation
- ✅ Code implementation
- ✅ Test execution
- ✅ PR creation
- ✅ Code review
- ✅ Jira updates

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

1. **[10 min]** Try `/autonomous-implement` on a real issue
2. **[15 min]** Read [Orchestrator Guide](ORCHESTRATOR_GUIDE.md)
3. **[Optional]** Set up Jira MCP for real data

---

## Learn More

- **Full README:** [../../README.md](../../README.md)
- **Orchestrator Guide:** [ORCHESTRATOR_GUIDE.md](ORCHESTRATOR_GUIDE.md)
- **Architecture:** [../architecture/ENGINEERING_OS_ARCHITECTURE.md](../architecture/ENGINEERING_OS_ARCHITECTURE.md)

---

**Get implementing in 5 minutes. Get proficient in 30 minutes.** 🚀
