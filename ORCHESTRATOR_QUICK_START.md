# Orchestrator Quick Start

**Workspace-level orchestration for multi-repository workflows**

---

## Quick Commands

```bash
# Test orchestrator components
python3 -m orchestrator test ABI-123

# View available repositories
python3 -m orchestrator knowledge --list

# View repository knowledge
python3 -m orchestrator knowledge --repo runtime

# Implement issue (mock data)
python3 -m orchestrator implement ABI-123

# Multi-repo implementation
python3 -m orchestrator multi-repo SDK-456 --repos sdk,runtime,runtime-ui
```

---

## Enable Real Jira (Optional)

```bash
# Set Jira credentials
export JIRA_URL=https://company.atlassian.net
export JIRA_EMAIL=dev@company.com
export JIRA_API_TOKEN=your_api_token

# Now orchestrator uses real Jira data
python3 -m orchestrator implement ABI-123
```

---

## What It Does

1. **Fetches Jira issue** (real or mock)
2. **Routes to repository** (auto-detects from components/labels)
3. **Loads knowledge** (architecture, patterns, Foundations standards)
4. **Invokes `/autonomous-implement`** with knowledge context
5. **Creates PR** with repo-specific patterns applied

---

## How It Enhances Your Skills

### Before (Manual)
```bash
cd ~/Documents/Development/em-runtime
/autonomous-implement ABI-123
# ❌ No repo-specific knowledge
# ❌ Must know which repo
# ❌ Manual Foundations compliance
```

### After (Orchestrated)
```bash
python3 -m orchestrator implement ABI-123
# ✅ Auto-routes to em-runtime
# ✅ Injects runtime architecture/patterns
# ✅ Enforces Foundations standards
```

---

## Your Skills Still Work!

All existing skills work exactly as before:

```bash
cd ~/Documents/Development/em-runtime
/autonomous-implement ABI-123
/autonomous-sprint --jql "sprint in openSprints()"
/research-codebase "How does auth work?"
```

**Orchestrator is optional** - use it when you want workspace-level features!

---

## Help

```bash
# Show all commands
python3 -m orchestrator --help

# Command-specific help
python3 -m orchestrator implement --help
python3 -m orchestrator multi-repo --help
```

---

## Documentation

- **Full guide:** [orchestrator/README.md](orchestrator/README.md)
- **Implementation:** [ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md](ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md)
- **MCP integration:** [ORCHESTRATOR_MCP_INTEGRATION.md](ORCHESTRATOR_MCP_INTEGRATION.md)
- **Complete summary:** [INTEGRATION_COMPLETE_SUMMARY.md](INTEGRATION_COMPLETE_SUMMARY.md)
