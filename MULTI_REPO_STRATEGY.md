# Multi-Repository Strategy for Multi-Agent System

## The Challenge

You have multiple repositories:
- `em-talk2data`
- `em-data-readiness`
- `em-aisoftwarefactory`
- Others...

Each Jira issue might target a different repository. How does the multi-agent system handle this?

---

## Solution Options

### Option 1: Plugin as Git Submodule (Recommended)

**Install plugin in each repository:**

```bash
# In em-talk2data
cd /path/to/em-talk2data
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# In em-data-readiness
cd /path/to/em-data-readiness
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# In other repos...
```

**Advantages:**
- ✅ Each repo has the plugin available
- ✅ Plugin updates sync via `git submodule update`
- ✅ Works with existing workflows
- ✅ Agents can run independently in each repo

**How it works with multi-agent:**
1. Run orchestrator from any repo (or dedicated "control" repo)
2. Orchestrator reads Jira issues
3. For each issue, determine target repo (via custom field or labels)
4. Spawn agent in target repo's directory
5. Agent uses plugin from that repo's `.claude/plugins/`

---

### Option 2: Central Plugin with Multi-Repo Support

**Install plugin once in a central "control" repository:**

```bash
# Create control repo
mkdir ~/em-orchestrator
cd ~/em-orchestrator
git init

# Install plugin
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# Configure managed repos
cat > .claude/repos.json << EOF
{
  "repositories": [
    {
      "name": "em-talk2data",
      "path": "/Users/malamunisamy/Documents/Development/em-talk2data",
      "github": "EmergenceAI/em-talk2data"
    },
    {
      "name": "em-data-readiness",
      "path": "/Users/malamunisamy/Documents/Development/em-data-readiness",
      "github": "EmergenceAI/em-data-readiness"
    }
  ]
}
EOF
```

**Orchestrator workflow:**
```javascript
// Read repo configuration
const repos = JSON.parse(await read('.claude/repos.json'))

// For each issue, route to correct repo
const results = await pipeline(
  issues,
  issue => {
    // Determine target repo from Jira
    const repoName = issue.customFields.repository || 'em-talk2data'
    const repo = repos.find(r => r.name === repoName)
    
    // Spawn agent in target repo directory
    return agent(`Implement ${issue.key}`, {
      label: `implement-${issue.key}`,
      cwd: repo.path,  // Run in specific repo
      isolation: 'worktree'
    })
  }
)
```

**Advantages:**
- ✅ Single plugin installation
- ✅ Centralized orchestration
- ✅ Easy to manage multiple repos
- ✅ Clear separation of orchestration vs implementation

**Disadvantages:**
- ⚠️ Requires custom field in Jira to specify target repo
- ⚠️ More complex setup

---

### Option 3: Hybrid (Recommended for Your Use Case)

**Combine both approaches:**

1. **Install plugin in each repo** (for individual use)
2. **Create orchestrator repo** (for multi-repo automation)

**Structure:**
```
~/Documents/Development/
├── em-talk2data/
│   └── .claude/plugins/em-software-factory/
├── em-data-readiness/
│   └── .claude/plugins/em-software-factory/
├── EM-AISoftwareFactory/           # Plugin source
└── em-orchestrator/                # NEW: Control repo
    ├── .claude/
    │   ├── plugins/em-software-factory/
    │   └── repos.json              # Repo configuration
    └── workflows/
        └── multi-repo-sprint.js    # Multi-repo orchestrator
```

**Benefits:**
- ✅ Developers can use plugin in individual repos
- ✅ Orchestrator can manage all repos
- ✅ Best of both worlds

---

## Implementation: Multi-Repo Support in Skills

### Update `/jira-to-branches` for Multi-Repo

**Add repo detection:**

```markdown
## Process

1. **Query Jira issues**
2. **For each issue, determine target repository:**
   - Option A: Custom field "Repository" in Jira
   - Option B: Label convention (e.g., `repo:em-talk2data`)
   - Option C: Component field in Jira
   - Option D: Parse from description

3. **Group issues by repository:**
   ```json
   {
     "em-talk2data": [
       {"key": "ABI-123", "branch": "..."},
       {"key": "ABI-124", "branch": "..."}
     ],
     "em-data-readiness": [
       {"key": "ABI-125", "branch": "..."}
     ]
   }
   ```

4. **Create branches in each repository:**
   ```bash
   cd /path/to/em-talk2data
   git checkout -b story/ABI-123-feature
   git push -u origin story/ABI-123-feature
   
   cd /path/to/em-data-readiness
   git checkout -b story/ABI-125-feature
   git push -u origin story/ABI-125-feature
   ```
```

### Update `/autonomous-sprint` Workflow for Multi-Repo

```javascript
export const meta = {
  name: 'autonomous-sprint-multi-repo',
  description: 'Autonomous sprint implementation across multiple repositories'
}

// Load repo configuration
const repoConfig = JSON.parse(await read('.claude/repos.json'))

// Phase 1: Query Jira and create branches
phase('Setup')
const issuesByRepo = await agent('Run /jira-to-branches with multi-repo support', {
  schema: ISSUES_BY_REPO_SCHEMA
})

// Phase 2: Parallel implementation across repos
phase('Implement')
const results = await parallel(
  Object.entries(issuesByRepo).map(([repoName, issues]) => () => {
    const repo = repoConfig.repositories.find(r => r.name === repoName)
    
    // Process all issues for this repo in parallel
    return pipeline(
      issues,
      issue => agent(`Implement ${issue.key} in ${repoName}`, {
        label: `${repoName}-${issue.key}`,
        cwd: repo.path,        // Change to repo directory
        isolation: 'worktree'
      })
    )
  })
)

return { results: results.flat() }
```

---

## Jira Configuration for Multi-Repo

### Option A: Custom Field "Repository"

**In Jira:**
1. Create custom field: "Repository" (Select List)
2. Options: `em-talk2data`, `em-data-readiness`, etc.
3. Issues specify which repo they target

**JQL Example:**
```sql
project = ABI AND sprint = 'Sprint 23' AND Repository = 'em-talk2data'
```

### Option B: Labels Convention

**In Jira:**
- Add labels: `repo:em-talk2data`, `repo:em-data-readiness`

**JQL Example:**
```sql
project = ABI AND sprint = 'Sprint 23' AND labels = 'repo:em-talk2data'
```

### Option C: Component Field

**In Jira:**
- Create components matching repo names
- Each issue assigned to a component

**JQL Example:**
```sql
project = ABI AND sprint = 'Sprint 23' AND component = 'em-talk2data'
```

---

## Recommended Approach for Your Setup

### Step 1: Install Plugin in Each Repo

```bash
# em-talk2data
cd ~/Documents/Development/em-talk2data
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# em-data-readiness  
cd ~/Documents/Development/em-data-readiness
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory
```

### Step 2: Create Orchestrator Repo

```bash
# Create orchestrator
mkdir ~/Documents/Development/em-orchestrator
cd ~/Documents/Development/em-orchestrator
git init

# Install plugin
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# Create repo config
cat > .claude/repos.json << 'EOF'
{
  "repositories": [
    {
      "name": "em-talk2data",
      "path": "/Users/malamunisamy/Documents/Development/em-talk2data",
      "github": "EmergenceAI/em-talk2data",
      "defaultBranch": "main"
    },
    {
      "name": "em-data-readiness",
      "path": "/Users/malamunisamy/Documents/Development/em-data-readiness",
      "github": "EmergenceAI/em-data-readiness",
      "defaultBranch": "main"
    },
    {
      "name": "em-aisoftwarefactory",
      "path": "/Users/malamunisamy/Documents/Development/EM-AISoftwareFactory",
      "github": "EmergenceAI/EM-AISoftwareFactory",
      "defaultBranch": "main"
    }
  ]
}
EOF
```

### Step 3: Configure Jira

**Add custom field "Repository":**
1. Go to Jira Admin → Custom Fields
2. Create "Repository" (Select List - Single choice)
3. Add options: `em-talk2data`, `em-data-readiness`, `em-aisoftwarefactory`
4. Associate with your project (ABI)

**When creating issues:**
- Set "Repository" field to target repo
- JQL can filter by repo

### Step 4: Run Multi-Repo Sprint

```bash
cd ~/Documents/Development/em-orchestrator

# Launch Claude with plugin
claude --plugin-dir .claude/plugins/em-software-factory

# Run multi-repo sprint
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23'"

# Or filter by repo
/autonomous-sprint --jql "project = ABI AND Repository = 'em-talk2data' AND sprint = 'Sprint 23'"
```

---

## Single-Repo Usage (Individual Developers)

Developers can still work in individual repos:

```bash
# In em-talk2data
cd ~/Documents/Development/em-talk2data
claude --plugin-dir .claude/plugins/em-software-factory

# Work on single issue
/autonomous-implement ABI-123

# Or local sprint
/autonomous-sprint --jql "project = ABI AND Repository = 'em-talk2data' AND assignee = currentUser()"
```

---

## Summary

**For your multi-repo setup:**

1. ✅ **Install plugin in each repo** (via git submodule)
2. ✅ **Create orchestrator repo** for multi-repo automation
3. ✅ **Add "Repository" custom field in Jira**
4. ✅ **Skills detect and route to correct repo**

**Benefits:**
- Individual repos: Use plugin normally
- Orchestrator: Manages all repos from one place
- Jira: Clear indication which repo each issue targets
- Flexible: Run single-repo or multi-repo sprints

**Plugin Update Process:**
```bash
# Update plugin in all repos at once
for repo in em-talk2data em-data-readiness em-orchestrator; do
  cd ~/Documents/Development/$repo
  git submodule update --remote .claude/plugins/em-software-factory
  git add .claude/plugins/em-software-factory
  git commit -m "Update EM Software Factory plugin"
done
```

This gives you the best of both worlds: plugin available in each repo + centralized orchestration!
