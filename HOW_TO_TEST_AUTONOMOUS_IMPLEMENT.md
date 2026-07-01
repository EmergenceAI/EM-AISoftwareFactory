# How to Test /autonomous-implement with SEMI-1413

## **Question: How does it determine which repo to make changes?**

### **Answer: Two Methods**

---

## **Method 1: Manual Routing (Direct Skill)**

**You manually cd to the repository:**

```bash
# Step 1: Navigate to em-semi repository
cd ~/Documents/Development/em-semi

# Step 2: Invoke skill
/autonomous-implement SEMI-1413

# The skill works in em-semi because that's where you are!
```

**How it works:**
- ❌ No routing logic
- ✅ Works in current directory
- ✅ Simple and direct

---

## **Method 2: Automatic Routing (Orchestrator)**

**Orchestrator determines repository automatically:**

```bash
# From ANYWHERE (even AI Software Factory root)
python3 -m orchestrator implement SEMI-1413

# Orchestrator:
# 1. Fetches SEMI-1413 from Jira
# 2. Checks Jira component → "Semi"
# 3. Maps "Semi" → em-semi repository (from workspace.yaml)
# 4. cd ~/Documents/Development/em-semi
# 5. Loads em-semi knowledge
# 6. Invokes: /autonomous-implement SEMI-1413 --context-file /tmp/context.md
```

**How it works:**
- ✅ Automatic routing via Jira component
- ✅ Loads em-semi specific knowledge
- ✅ Enforces Foundations standards

---

## **How Routing Works (workspace.yaml)**

### **Component Mapping**

```yaml
# workspace.yaml (line 126-133)
jira:
  component_mapping:
    Runtime: runtime
    UI: runtime-ui
    Talk2Data: talk2data
    Connectors: connectors
    SDK: sdk
    "Data Readiness": data-readiness
    Semi: semi                    ← SEMI-1413 maps here!
```

### **Repository Configuration**

```yaml
# workspace.yaml (line 78-87)
repositories:
  - name: semi
    display_name: EM Semi
    path: em-semi                 ← cd to this path
    github: EmergenceAI/em-semi
    primary_language: python
    build_system: docker
    test_framework: pytest
    jira_component: Semi          ← Matches this component
```

### **Routing Logic**

```python
# orchestrator/router.py
def route_issue(jira_issue):
    # Strategy 1: Component mapping (PRIMARY)
    if issue.components contains "Semi":
        return "semi"  # → em-semi repository
    
    # Strategy 2: Description analysis
    if issue.description contains "semi" or "semiconductor":
        return "semi"
    
    # Strategy 3: Labels
    if issue.labels contains "repo:semi":
        return "semi"
    
    # Default
    return "runtime"
```

---

## **Testing SEMI-1413: Step-by-Step**

### **Prerequisites**

1. **Jira Environment Variables** (for real Jira data):
   ```bash
   export JIRA_URL=https://your-company.atlassian.net
   export JIRA_EMAIL=your-email@company.com
   export JIRA_API_TOKEN=your_token
   ```

2. **Or use mock data** (no env vars needed)

---

### **Test 1: Direct Skill Invocation**

```bash
# Navigate to em-semi
cd ~/Documents/Development/em-semi

# Verify you're in the right place
pwd
# Output: /Users/malamunisamy/Documents/Development/em-semi

# Invoke skill
/autonomous-implement SEMI-1413

# Expected flow:
# ✅ 1. Fetch SEMI-1413 from Jira
# ✅ 2. Research em-semi codebase
# ✅ 3. Create plan in specs/features/SEMI-1413.md
# ✅ 4. Generate evals in tests/evals/SEMI-1413/
# ✅ 5. Implement changes in em-semi
# ✅ 6. Run pytest tests/evals/SEMI-1413/
# ✅ 7. Create PR in em-semi repository
# ✅ 8. Code review
# ✅ 9. Update SEMI-1413 in Jira
```

---

### **Test 2: Orchestrator (Automatic Routing)**

```bash
# From AI Software Factory root (or anywhere)
cd ~/Documents/Development/EM-AISoftwareFactory

# Test routing first
python3 -m orchestrator test SEMI-1413

# Expected output:
# ============================================================
# Orchestrator Component Test
# ============================================================
# 
# Testing Router...
#   ✅ Routed SEMI-1413 → semi
# 
# Testing Knowledge Engine...
#   ✅ Loaded knowledge for semi:
#      - architecture: 1234 chars
#      - patterns: 567 chars
#      - conventions: 890 chars
# 
# ✅ All component tests passed!
```

**If routing works, then implement:**

```bash
# Implement with orchestrator
python3 -m orchestrator implement SEMI-1413

# Expected flow:
# ✅ 1. Fetch SEMI-1413 from Jira (via MCP or mock)
# ✅ 2. Route to "semi" repository (via component mapping)
# ✅ 3. Load knowledge/repositories/semi/*.md
# ✅ 4. Load knowledge/foundations/standards.md
# ✅ 5. Create /tmp/knowledge_context_xyz.md
# ✅ 6. cd ~/Documents/Development/em-semi
# ✅ 7. Invoke: /autonomous-implement SEMI-1413 \
#              --context-file /tmp/knowledge_context_xyz.md
# ✅ 8. Skill reads context and applies em-semi patterns
# ✅ 9. Implementation proceeds with em-semi knowledge
```

---

## **What Makes Routing Work for SEMI-1413**

### **Option A: Jira Component is "Semi"**

If SEMI-1413 has component "Semi":
```
SEMI-1413
  Component: Semi    ← Router checks this
  ↓
  component_mapping["Semi"] = "semi"
  ↓
  Routes to: em-semi repository
```

### **Option B: Issue Key Prefix**

The router is smart - it sees "SEMI-" prefix:
```python
# orchestrator/router.py - description analysis
if "semi" in description.lower():
    return "semi"
```

### **Option C: Manual Label**

Add label `repo:semi` to issue:
```
SEMI-1413
  Labels: ["repo:semi"]    ← Router checks this
  ↓
  Routes to: em-semi repository
```

---

## **Verifying Repository Routing**

### **Check Current Component Mapping**

```bash
# View component mapping
grep -A 10 "component_mapping:" workspace.yaml

# Output:
#   component_mapping:
#     Runtime: runtime
#     UI: runtime-ui
#     Talk2Data: talk2data
#     Connectors: connectors
#     SDK: sdk
#     "Data Readiness": data-readiness
#     Semi: semi              ← SEMI-1413 routes here
```

### **Test Routing Logic**

```bash
# Test orchestrator routing
python3 -m orchestrator test SEMI-1413

# Should output:
#   ✅ Routed SEMI-1413 → semi
```

---

## **Complete Test Example**

### **Scenario: Implement SEMI-1413 in em-semi**

**Step 1: Check Jira Issue**
```bash
# If Jira MCP configured, real data
# Otherwise, mock data used

# Mock data would be:
# {
#   "key": "SEMI-1413",
#   "summary": "[MOCK] Implement feature for SEMI-1413",
#   "components": ["Semi"],  ← Routes to em-semi!
#   "labels": []
# }
```

**Step 2: Test Routing**
```bash
python3 -m orchestrator test SEMI-1413

# Verify output shows:
#   ✅ Routed SEMI-1413 → semi
```

**Step 3: Implement**

**Option A - Direct (manual routing):**
```bash
cd ~/Documents/Development/em-semi
/autonomous-implement SEMI-1413
```

**Option B - Orchestrator (automatic routing):**
```bash
python3 -m orchestrator implement SEMI-1413
```

**Step 4: Verify Results**
```bash
# Check em-semi repository for changes
cd ~/Documents/Development/em-semi

# View created files
ls specs/features/SEMI-1413.md
ls tests/evals/SEMI-1413/

# Check branch
git branch | grep SEMI-1413

# View PR (if created)
gh pr view
```

---

## **Troubleshooting**

### **Issue: Routes to wrong repository**

**Problem:** SEMI-1413 routes to "runtime" instead of "semi"

**Solution 1:** Check Jira component
```bash
# Ensure SEMI-1413 has component "Semi"
# Or add label "repo:semi"
```

**Solution 2:** Use direct invocation
```bash
cd ~/Documents/Development/em-semi
/autonomous-implement SEMI-1413
```

**Solution 3:** Check component mapping
```bash
# Verify workspace.yaml has:
grep "Semi: semi" workspace.yaml
```

---

### **Issue: Can't find em-semi repository**

**Problem:** Orchestrator can't find repository path

**Solution:** Verify workspace.yaml
```yaml
workspace:
  root: /Users/malamunisamy/Documents/Development  ← Correct root?

repositories:
  - name: semi
    path: em-semi  ← Path should be: {root}/{path}
```

**Test path exists:**
```bash
ls -la /Users/malamunisamy/Documents/Development/em-semi
```

---

### **Issue: No knowledge for em-semi**

**Problem:** Orchestrator shows "0 chars" for em-semi knowledge

**Solution:** Sync knowledge
```bash
cd ~/Documents/Development/EM-AISoftwareFactory
./sync_knowledge.sh

# Verify em-semi knowledge exists
ls -la knowledge/repositories/semi/
```

---

## **Summary**

### **How Repository is Determined**

| Method | Routing | Knowledge | When to Use |
|--------|---------|-----------|-------------|
| **Direct Skill** | Manual (you cd) | ❌ None | Quick test in known repo |
| **Orchestrator** | Auto (component) | ✅ Loaded | Production use, multi-repo |

### **For SEMI-1413 Specifically**

**Automatic Routing Works Because:**
1. ✅ Issue key starts with "SEMI-"
2. ✅ Component mapping: "Semi" → "semi"
3. ✅ Repository configured: name="semi", path="em-semi"

**To Test:**
```bash
# Quick test routing
python3 -m orchestrator test SEMI-1413

# Full implementation
python3 -m orchestrator implement SEMI-1413

# Or manual
cd ~/Documents/Development/em-semi
/autonomous-implement SEMI-1413
```

**Result:**
- ✅ Changes made in em-semi repository
- ✅ PR created in EmergenceAI/em-semi
- ✅ em-semi specific patterns applied
- ✅ Semiconductor domain knowledge used

---

**That's it! The routing "just works" based on Jira component mapping!** 🎉
