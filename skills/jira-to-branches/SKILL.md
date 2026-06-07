---
name: jira-to-branches
description: Query Jira issues with JQL and create GitHub branches in the current repository
---

# Jira to Branches

Query Jira issues using JQL and automatically create standardized GitHub branches for each issue in the current repository.

## When to Use This Skill

Use this skill to:
- Set up branches for all sprint issues at once
- Create branches from JQL query results
- Prepare repository for autonomous implementation
- Standardize branch naming across the team

## Usage

```bash
# Using JQL query
/jira-to-branches --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Talk2Data'"

# Simplified project + sprint syntax
/jira-to-branches --project ABI --sprint "Sprint 23" --component "Talk2Data"

# Specific issues
/jira-to-branches --jql "key IN (ABI-123, ABI-124, ABI-125)"
```

## Branch Naming Convention

Branches are created using this standardized format:

```
{issue-type}/{issue-key}-{slug}
```

**Examples:**
- Story: `story/ABI-123-api-rate-limiting`
- Bug: `bug/ABI-124-fix-auth-timeout`
- Epic: `epic/ABI-125-multi-agent-system`
- Task: `task/ABI-126-update-readme`

**Issue Type Mapping:**
- `Story` → `story/`
- `Bug` → `bug/`
- `Epic` → `epic/`
- `Task` → `task/`
- `Sub-task` → `subtask/`
- Default → `feature/`

## Process

### Step 1: Parse Arguments

If user provides `--jql`, use it directly.

If user provides `--project` and `--sprint` (and optionally `--component`), construct JQL:

```sql
project = {project} AND sprint = '{sprint}' AND status IN ('To Do', 'In Progress')
```

If `--component` provided:
```sql
project = {project} AND sprint = '{sprint}' AND component = '{component}' AND status IN ('To Do', 'In Progress')
```

### Step 2: Query Jira

Use MCP Atlassian to search issues:

```javascript
const issues = await mcp__atlassian__jira_search_issues({
  jql: jqlQuery,
  maxResults: 50,
  fields: ['key', 'summary', 'issuetype', 'status', 'description', 'customfield_*']
})
```

Extract for each issue:
- `key` (e.g., "ABI-123")
- `summary` (e.g., "Add API rate limiting")
- `issuetype.name` (e.g., "Story", "Bug")
- `status.name` (e.g., "To Do", "In Progress")
- `description` (issue details)
- Acceptance criteria (if in custom field or description)

### Step 3: Generate Branch Names

For each issue:

1. **Get issue type:**
   ```javascript
   const typeMap = {
     'Story': 'story',
     'Bug': 'bug',
     'Epic': 'epic',
     'Task': 'task',
     'Sub-task': 'subtask'
   }
   const branchPrefix = typeMap[issue.issuetype.name] || 'feature'
   ```

2. **Create slug from summary:**
   ```javascript
   const slug = issue.summary
     .toLowerCase()
     .replace(/[^a-z0-9]+/g, '-')
     .replace(/^-|-$/g, '')
     .substring(0, 50)
   ```

3. **Combine:**
   ```javascript
   const branchName = `${branchPrefix}/${issue.key}-${slug}`
   ```

### Step 4: Check Existing Branches

Before creating, check if branch already exists:

```bash
git fetch origin
git branch -r | grep "origin/${branchName}"
```

If exists:
- Skip creation
- Note in output: "Branch already exists"

### Step 5: Create Branches

For each issue without existing branch:

```bash
# Ensure we're on main/master
git checkout main

# Create and push new branch
git checkout -b ${branchName}
git push -u origin ${branchName}

# Return to main
git checkout main
```

### Step 6: Update Jira Issues

For each issue with newly created branch:

Add comment to Jira issue:

```markdown
Branch created: `{branchName}`

GitHub: [{repo}/tree/{branchName}](https://github.com/{org}/{repo}/tree/{branchName})
```

Use MCP tool:
```javascript
await mcp__atlassian__jira_add_comment({
  issueKey: issue.key,
  comment: `Branch created: \`${branchName}\`\n\nGitHub: [${repoName}/tree/${branchName}](https://github.com/${org}/${repo}/tree/${branchName})`
})
```

### Step 7: Output Summary

Return structured summary:

```markdown
Created {count} branches for {totalIssues} issues:

✓ ABI-123: story/ABI-123-api-rate-limiting
✓ ABI-124: bug/ABI-124-fix-auth-timeout
○ ABI-125: Branch already exists (epic/ABI-125-multi-agent-system)

Next steps:
- Run /autonomous-sprint to implement all issues
- Or work on individual issues with /autonomous-implement {issue-key}
```

## Output Schema

Return JSON with issue details and branch names:

```json
{
  "issues": [
    {
      "key": "ABI-123",
      "summary": "Add API rate limiting",
      "type": "Story",
      "status": "To Do",
      "branch": "story/ABI-123-api-rate-limiting",
      "created": true,
      "url": "https://github.com/org/repo/tree/story/ABI-123-api-rate-limiting"
    },
    {
      "key": "ABI-124",
      "summary": "Fix authentication timeout",
      "type": "Bug",
      "status": "In Progress",
      "branch": "bug/ABI-124-fix-auth-timeout",
      "created": true,
      "url": "https://github.com/org/repo/tree/bug/ABI-124-fix-auth-timeout"
    },
    {
      "key": "ABI-125",
      "summary": "Multi-agent autonomous system",
      "type": "Epic",
      "status": "In Progress",
      "branch": "epic/ABI-125-multi-agent-system",
      "created": false,
      "reason": "Branch already exists"
    }
  ],
  "summary": {
    "total": 3,
    "created": 2,
    "skipped": 1
  }
}
```

## GitHub Repository Detection

Detect current GitHub repository automatically:

```bash
# Get remote URL
git remote get-url origin
# Example: https://github.com/EmergenceAI/em-talk2data.git
# Or: git@github.com:EmergenceAI/em-talk2data.git

# Parse org and repo
# org = EmergenceAI
# repo = em-talk2data
```

## Error Handling

**No issues found:**
```
No issues found matching JQL: {jql}

Try adjusting your query or check:
- Project key is correct
- Sprint name is exact match
- Status filter includes your issues
```

**Git errors:**
```
Failed to create branch {branchName}: {error}

This might happen if:
- Not in a git repository
- No write access to remote
- Branch name conflicts
```

**Jira API errors:**
```
Failed to query Jira: {error}

Check:
- JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN are set
- JQL syntax is valid
- You have access to the project
```

## Configuration

**Required environment variables:**
```bash
JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=xxx
```

**Git configuration:**
- Must be run from within a Git repository
- Repository must have `origin` remote configured
- User must have push permissions

## Examples

### Example 1: Sprint Setup

```bash
/jira-to-branches --project ABI --sprint "Sprint 23" --component "Talk2Data"
```

**Output:**
```
Created 8 branches for 8 issues:

✓ ABI-123: story/ABI-123-api-rate-limiting
✓ ABI-124: bug/ABI-124-fix-auth-timeout
✓ ABI-125: epic/ABI-125-multi-agent-system
✓ ABI-126: task/ABI-126-update-documentation
✓ ABI-127: story/ABI-127-semantic-search
✓ ABI-128: bug/ABI-128-memory-leak
✓ ABI-129: story/ABI-129-eval-framework
✓ ABI-130: task/ABI-130-refactor-tests

All branches created and pushed to origin.
Jira issues updated with branch links.
```

### Example 2: Specific Issues

```bash
/jira-to-branches --jql "key IN (ABI-123, ABI-124, ABI-125)"
```

**Output:**
```
Created 3 branches for 3 issues:

✓ ABI-123: story/ABI-123-api-rate-limiting
✓ ABI-124: bug/ABI-124-fix-auth-timeout
✓ ABI-125: epic/ABI-125-multi-agent-system
```

### Example 3: Advanced JQL

```bash
/jira-to-branches --jql "project = ABI AND labels = M1 AND status = 'To Do' AND assignee = currentUser()"
```

**Output:**
```
Created 5 branches for 5 issues assigned to you with M1 label.
```

## Integration with Other Skills

```bash
# 1. Create branches for sprint
/jira-to-branches --project ABI --sprint "Sprint 23"

# 2. Implement all issues autonomously
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23'"

# Or implement individual issues
/autonomous-implement ABI-123
/autonomous-implement ABI-124
```

## Success Criteria

- [x] Parses JQL or constructs from project/sprint/component
- [x] Queries Jira via MCP Atlassian
- [x] Generates standardized branch names
- [x] Checks for existing branches before creating
- [x] Creates and pushes branches to GitHub
- [x] Updates Jira issues with branch links
- [x] Returns structured JSON output
- [x] Handles errors gracefully with clear messages

## Notes

**Branch naming:**
- Maximum branch name length: 100 characters
- Slug truncated to 50 characters if needed
- Special characters replaced with hyphens
- Consistent with team conventions

**GitHub permissions:**
- User must have write access to repository
- Branches pushed to `origin` remote
- Uses current git credentials

**Jira updates:**
- Comment added to each issue with branch link
- Does not change issue status
- Links to GitHub branch for easy access

**Performance:**
- Processes up to 50 issues per query (adjustable)
- Branches created sequentially (not parallel)
- Typical speed: ~2-3 seconds per branch
