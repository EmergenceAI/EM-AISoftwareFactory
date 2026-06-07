# Phased Approach: Single-Repo → Multi-Repo

## Philosophy: Start Simple, Expand Later

**Phase 1 (MVP):** Single-repo automation  
**Phase 2 (Future):** Multi-repo orchestration

---

## Phase 1: Single-Repo MVP (Build This First)

### How It Works

**Run from within a specific repository:**

```bash
# Work in em-talk2data
cd ~/Documents/Development/em-talk2data

# Launch Claude with plugin
claude --plugin-dir .claude/plugins/em-software-factory

# Process issues for THIS repo only
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Talk2Data'"
```

**Or:**

```bash
# Work in em-data-readiness
cd ~/Documents/Development/em-data-readiness

# Launch Claude with plugin
claude --plugin-dir .claude/plugins/em-software-factory

# Process issues for THIS repo only
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Data Readiness'"
```

### Key Simplifications

✅ **No orchestrator repo needed** - Run from the actual repo  
✅ **No "Repository" custom field needed** - Use Components or Labels  
✅ **No multi-repo routing** - Just filter JQL by component  
✅ **Simpler mental model** - One repo at a time  

### Jira Setup (Simple)

**Option A: Use Components**
- Create components in Jira: `Talk2Data`, `Data Readiness`, `AI Factory`
- Assign issues to components
- JQL filter: `component = 'Talk2Data'`

**Option B: Use Labels**
- Add labels: `talk2data`, `data-readiness`
- JQL filter: `labels = 'talk2data'`

**Option C: Manual filtering**
- Just run with specific issue keys
- JQL: `key IN (ABI-123, ABI-124, ABI-125)`

### Installation (Simple)

**Install plugin in each repo independently:**

```bash
# In em-talk2data
cd ~/Documents/Development/em-talk2data
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# In em-data-readiness
cd ~/Documents/Development/em-data-readiness
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory
```

**That's it!** No orchestrator needed.

---

## Phase 1 Workflow Examples

### Example 1: Process Talk2Data Sprint Issues

```bash
cd ~/Documents/Development/em-talk2data
claude --plugin-dir .claude/plugins/em-software-factory

# In Claude:
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Talk2Data'"
```

**What happens:**
1. Query Jira for Talk2Data issues in Sprint 23
2. Create branches in `em-talk2data` repo (current directory)
3. Spawn agents in worktrees within `em-talk2data`
4. Each agent implements its issue
5. Create PRs in `em-talk2data` repo

### Example 2: Process Data Readiness Sprint Issues

```bash
cd ~/Documents/Development/em-data-readiness
claude --plugin-dir .claude/plugins/em-software-factory

# In Claude:
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Data Readiness'"
```

**What happens:**
1. Query Jira for Data Readiness issues in Sprint 23
2. Create branches in `em-data-readiness` repo (current directory)
3. Spawn agents in worktrees within `em-data-readiness`
4. Each agent implements its issue
5. Create PRs in `em-data-readiness` repo

### Example 3: Process Specific Issues

```bash
cd ~/Documents/Development/em-talk2data
claude --plugin-dir .claude/plugins/em-software-factory

# In Claude - just work on these specific issues
/autonomous-sprint --jql "key IN (ABI-123, ABI-124, ABI-125)"
```

---

## Phase 1: What We Build

### Skills (All Single-Repo)

**`/jira-to-branches`**
- Query Jira with JQL
- Create branches in **current repo**
- No repo routing needed

**`/autonomous-implement`**
- Work in **current repo's worktree**
- No multi-repo logic

**`/autonomous-sprint`** (workflow)
- Orchestrate agents in **current repo only**
- Simple and focused

### Simplified Architecture

```
Current Repo (e.g., em-talk2data/)
├── .claude/
│   └── plugins/em-software-factory/
├── .claude/worktrees/               ← Agents work here
│   ├── ABI-123/                     ← Agent 1
│   ├── ABI-124/                     ← Agent 2
│   └── ABI-125/                     ← Agent 3
└── src/                             ← Production code
```

**No orchestrator, no routing, just:**
1. Run from repo
2. Filter Jira by component
3. All work happens in that repo

---

## Phase 2: Multi-Repo (Future Enhancement)

**When you're ready to scale, add:**

1. **Orchestrator repo** (optional)
2. **Repository custom field** in Jira
3. **Multi-repo routing logic** in skills
4. **Cross-repo dependency handling**

But **NOT in MVP!**

---

## Recommended Workflow (Phase 1)

### Sprint Planning

**Jira Components:**
- Component: `Talk2Data` → Issues for em-talk2data repo
- Component: `Data Readiness` → Issues for em-data-readiness repo
- Component: `AI Factory` → Issues for EM-AISoftwareFactory repo

### Sprint Execution

**Monday - em-talk2data issues:**
```bash
cd em-talk2data
claude --plugin-dir .claude/plugins/em-software-factory
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Talk2Data'"
```

**Tuesday - em-data-readiness issues:**
```bash
cd em-data-readiness
claude --plugin-dir .claude/plugins/em-software-factory
/autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Data Readiness'"
```

**Or run both in parallel in separate terminals!**

Terminal 1:
```bash
cd em-talk2data
claude --plugin-dir .claude/plugins/em-software-factory
/autonomous-sprint --jql "component = 'Talk2Data' AND sprint = 'Sprint 23'"
```

Terminal 2:
```bash
cd em-data-readiness
claude --plugin-dir .claude/plugins/em-software-factory
/autonomous-sprint --jql "component = 'Data Readiness' AND sprint = 'Sprint 23'"
```

---

## Installation Steps (Phase 1 - Simple)

### Step 1: Install Plugin in Each Repo

```bash
# em-talk2data
cd ~/Documents/Development/em-talk2data
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory
git commit -m "Add EM Software Factory plugin"

# em-data-readiness
cd ~/Documents/Development/em-data-readiness
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory
git commit -m "Add EM Software Factory plugin"
```

### Step 2: Configure Jira Components (Optional)

**In Jira Project Settings:**
1. Go to Project Settings → Components
2. Create components:
   - `Talk2Data`
   - `Data Readiness`
   - `AI Factory`

### Step 3: Tag Issues

**When creating issues:**
- Set Component field to appropriate repo
- Or just use JQL to filter manually

### Step 4: Run!

```bash
cd ~/Documents/Development/em-talk2data
claude --plugin-dir .claude/plugins/em-software-factory

# Process this repo's issues
/autonomous-sprint --jql "project = ABI AND component = 'Talk2Data' AND sprint = 'Sprint 23'"
```

---

## Migration to Phase 2 (Later)

**When ready for multi-repo orchestration:**

1. Create `em-orchestrator` repo
2. Add `.claude/repos.json` configuration
3. Add "Repository" custom field in Jira
4. Update skills to support multi-repo routing
5. Run from orchestrator instead of individual repos

But for now, **Phase 1 is simpler and works great!**

---

## Summary

### Phase 1 (MVP - Build Now)
- ✅ Install plugin in each repo
- ✅ Run from specific repo
- ✅ Use JQL to filter by component/labels
- ✅ All work happens in that repo
- ✅ Simple, focused, easy to understand

### Phase 2 (Future - When Needed)
- ⏳ Orchestrator repo
- ⏳ Multi-repo routing
- ⏳ Cross-repo dependencies
- ⏳ Centralized management

**Start with Phase 1. It's simpler and solves 90% of use cases!**

---

## Next Steps (Phase 1 Only)

1. Build `/jira-to-branches` skill (single-repo, uses current directory)
2. Build `/autonomous-implement` skill (single-repo)
3. Build `/autonomous-sprint` workflow (single-repo)
4. Test in `em-talk2data` with 2-3 issues
5. Test in `em-data-readiness` with 2-3 issues
6. Production use!

**No orchestrator, no routing, just simple repo-by-repo automation.**

Much simpler! 🎉
