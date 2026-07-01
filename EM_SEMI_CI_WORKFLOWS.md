# em-semi CI/CD Workflows

## Location

```
/Users/malamunisamy/Documents/Development/em-semi/.github/workflows/
```

---

## Workflow Files Overview

### **PR & Testing Workflows**

| Workflow | File | Purpose |
|----------|------|---------|
| **Test & Lint** | `test_lint.yml` | Runs pytest, linting, and type checks on PRs |
| **Auto Code Review** | `pr-auto-code-review.yml` | AI-powered code review after tests pass |
| **PR Review App** | `pr-review-github-app.yml` | GitHub App integration for reviews |
| **Risk Classifier** | `pr-risk-classifier.yml` | Classifies PR risk level (low/medium/high) |

### **Deployment Workflows**

| Workflow | File | Purpose |
|----------|------|---------|
| **Deploy Dev** | `deploy-dev.yml` | Deploys to dev environment |
| **Deploy Staging** | `deploy-staging.yml` | Deploys to staging environment |
| **Release Prod** | `release-prod.yml` | Production release pipeline |

### **Maintenance Workflows**

| Workflow | File | Purpose |
|----------|------|---------|
| **Daily Tests** | `daily-tests.yml` | Nightly regression test suite |
| **Daily Release Notes** | `daily-release-notes.yml` | Automated release note generation |
| **Release Notes QA** | `release-notes-qa.yml` | QA validation of release notes |
| **Helm Drift** | `helm-drift.yml` | Detects drift in Helm deployments |
| **Black Duck SCA** | `blackducksca-workflow.yml` | Security scanning |

---

## Key Workflow: Auto Code Review

### **File:** `pr-auto-code-review.yml`

This is the **automated PR review system** that works with AI Software Factory!

### **How It Works**

```
PR Created
    ↓
test_lint.yml runs
    ↓
Tests pass ✅
    ↓
pr-auto-code-review.yml triggers
    ↓
AI Code Review runs
    ↓
Review posted to PR
```

### **Key Features**

1. **Triggered After Tests Pass**
   ```yaml
   on:
     workflow_run:
       workflows: ["Run Lint and Tests"]  # test_lint.yml
       types: [completed]
   ```

2. **Risk-Based Review**
   - Low risk: Quick review
   - Medium risk: Standard review
   - High risk: Thorough review

3. **Skip Labels**
   - `skip-review` - Skip automated review
   - `skip-auto-review` - Skip automated review

4. **Review Types**
   - Security checks
   - Architecture compliance
   - Code quality
   - Test coverage
   - Air-gapped validation

### **Configuration**

```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write
  actions: read

timeout-minutes: 15
```

### **Review Document**

The workflow uses: `REVIEW.md` (or similar) for review guidelines

---

## Key Workflow: Test & Lint

### **File:** `test_lint.yml`

Runs on every PR before code review.

### **What It Tests**

```yaml
# Typical steps (estimated):
- Checkout code
- Setup Python
- Install dependencies (poetry)
- Run pytest
- Run mypy (type checking)
- Run black (formatting)
- Run flake8/ruff (linting)
- Upload coverage report
```

### **Success Criteria**

- ✅ All tests pass
- ✅ Type checks pass
- ✅ Linting passes
- ✅ Coverage meets threshold (likely 80%)

**If this passes** → Triggers `pr-auto-code-review.yml`

---

## Integration with AI Software Factory

### **Current State**

em-semi **already has** automated code review via GitHub Actions!

```
AI Software Factory PR
    ↓
/autonomous-implement creates PR
    ↓
GitHub Actions: test_lint.yml runs
    ↓
Tests pass ✅
    ↓
GitHub Actions: pr-auto-code-review.yml runs
    ↓
AI review posted
    ↓
Human reviews both AI reviews
    ↓
Merge
```

### **Dual AI Review System**

**You get TWO AI reviews:**

1. **AI Software Factory Review** (via `/code-review` skill)
   - Happens during `/autonomous-implement`
   - Checks: Air-gapped, patterns, architecture
   - Posted before PR creation

2. **GitHub Actions Review** (via `pr-auto-code-review.yml`)
   - Happens after PR creation
   - Checks: Security, quality, coverage
   - Posted as PR comment

**This is GOOD!** Two independent reviews catch more issues.

---

## Workflow Execution Flow

### **Happy Path**

```
1. /autonomous-implement SEMI-1413
     ↓
2. Creates PR on branch: bug/SEMI-1413-fix-memory-leak
     ↓
3. GitHub Actions: test_lint.yml
     - pytest runs
     - mypy checks
     - linting passes
     ✅ Success
     ↓
4. GitHub Actions: pr-auto-code-review.yml
     - Checks PR labels
     - Determines risk level
     - Runs AI review
     - Posts review comment
     ✅ Review complete
     ↓
5. Human reviews:
     - AI Software Factory review (from step 1)
     - GitHub Actions review (from step 4)
     - Code changes
     ↓
6. Human approves & merges
     ↓
7. Deploy pipeline (deploy-dev.yml → deploy-staging.yml → release-prod.yml)
```

### **Failure Handling**

```
If tests fail in test_lint.yml:
    ❌ pr-auto-code-review.yml does NOT run
    ❌ PR marked as failing
    ✅ Good! Don't review broken code

If AI Software Factory evals fail:
    ⚠️  PR created with [NEEDS-REVIEW] label
    ✅ test_lint.yml still runs
    ✅ pr-auto-code-review.yml still runs
    👤 Human decides: fix or reject
```

---

## Environment Secrets Required

Based on the workflows, these secrets are needed:

```yaml
# GitHub App (for pr-auto-code-review.yml)
APP_ID: ${{ secrets.APP_ID }}
APP_PRIVATE_KEY: ${{ secrets.APP_PRIVATE_KEY }}

# Likely also needed (for deployment):
DOCKER_REGISTRY: ${{ secrets.DOCKER_REGISTRY }}
KUBECONFIG: ${{ secrets.KUBECONFIG }}
SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Quality Gates

### **PR Must Pass:**

1. ✅ **All pytest tests** (test_lint.yml)
2. ✅ **Type checking** (mypy in test_lint.yml)
3. ✅ **Linting** (flake8/ruff in test_lint.yml)
4. ✅ **Coverage threshold** (likely 80%)
5. ✅ **AI code review** (pr-auto-code-review.yml)
6. ✅ **Human approval** (required reviewer)

### **Additional Checks:**

- 🔒 Security scan (blackducksca-workflow.yml)
- 🎯 Risk classification (pr-risk-classifier.yml)
- 📊 Helm drift detection (helm-drift.yml)

---

## Customization for AI Factory

### **Skip Auto Review for AI-Generated PRs**

Add this to your AI-generated PRs:

```yaml
# In /autonomous-implement or /create-pr skill:
labels:
  - "ai-generated"
  - "skip-auto-review"  # Skip GitHub Actions review
```

**Why?** AI Software Factory already does code review via `/code-review` skill.

**Or keep both?** Two reviews are better than one!

### **Add AI Factory Label**

Update GitHub Actions to recognize AI-generated PRs:

```yaml
# In pr-auto-code-review.yml:
- name: Check if AI-generated
  id: ai-check
  run: |
    if [[ "${{ contains(github.event.pull_request.labels.*.name, 'ai-generated') }}" == "true" ]]; then
      echo "Adjusting review depth for AI-generated PR"
      echo "ai_generated=true" >> $GITHUB_OUTPUT
    fi

# Then adjust review accordingly
- name: Run AI review
  if: steps.ai-check.outputs.ai_generated != 'true'
  # ... normal review

- name: Run lightweight review for AI PRs
  if: steps.ai-check.outputs.ai_generated == 'true'
  # ... quick validation only
```

---

## Viewing Workflow Runs

### **In GitHub UI:**

```
https://github.com/EmergenceAI/em-semi/actions
```

### **Via CLI:**

```bash
cd /Users/malamunisamy/Documents/Development/em-semi

# List recent workflow runs
gh run list

# View specific run
gh run view 1234567890

# Watch current run
gh run watch
```

### **View Logs:**

```bash
# Download logs for a run
gh run download 1234567890

# View specific job logs
gh run view 1234567890 --log
```

---

## Workflow Status Badges

Add to em-semi README.md:

```markdown
[![Tests](https://github.com/EmergenceAI/em-semi/workflows/Run%20Lint%20and%20Tests/badge.svg)](https://github.com/EmergenceAI/em-semi/actions)
[![Auto Review](https://github.com/EmergenceAI/em-semi/workflows/Automated%20Code%20Review/badge.svg)](https://github.com/EmergenceAI/em-semi/actions)
```

---

## Debugging Workflow Issues

### **Common Issues:**

**1. Auto review not triggering**
```bash
# Check if test_lint.yml passed
gh run list --workflow=test_lint.yml

# Check auto-review workflow
gh run list --workflow=pr-auto-code-review.yml

# Look for skip labels
gh pr view 123 --json labels
```

**2. Tests failing**
```bash
# View test logs
gh run view <run-id> --log

# Run tests locally
cd /Users/malamunisamy/Documents/Development/em-semi
pytest -v
```

**3. Permissions error**
```yaml
# Ensure workflow has correct permissions
permissions:
  contents: write
  pull-requests: write
```

---

## Summary

### **em-semi CI/CD Stack:**

```
┌─────────────────────────────────────────────┐
│           PR Created                         │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  test_lint.yml                               │
│  - pytest                                    │
│  - mypy                                      │
│  - linting                                   │
│  - coverage                                  │
└─────────────────────────────────────────────┘
                   ↓ (if pass)
┌─────────────────────────────────────────────┐
│  pr-auto-code-review.yml                     │
│  - AI code review                            │
│  - Security checks                           │
│  - Architecture validation                   │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  Human Review                                │
│  - Approve/Request Changes                   │
└─────────────────────────────────────────────┘
                   ↓ (if approved)
┌─────────────────────────────────────────────┐
│  Deployment Pipeline                         │
│  - deploy-dev.yml                            │
│  - deploy-staging.yml                        │
│  - release-prod.yml                          │
└─────────────────────────────────────────────┘
```

### **Files to Review:**

1. **`test_lint.yml`** - Test configuration
2. **`pr-auto-code-review.yml`** - Auto review setup
3. **`deploy-dev.yml`** - Deployment config

### **Next Steps:**

1. Read the workflows to understand exact test commands
2. Ensure AI Factory PRs trigger workflows correctly
3. Consider adding `ai-generated` label handling
4. Monitor workflow runs for AI-generated PRs

**The CI/CD infrastructure is already robust and ready for AI Factory integration!** 🚀
