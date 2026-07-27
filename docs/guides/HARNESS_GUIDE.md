# Harness Guide

**Complete guide to workspace-level orchestration with knowledge injection.**

---

## Table of Contents

- [Quick Start](#quick-start)
- [Single Repository Mode](#single-repository-mode)
- [Multi-Repository Mode](#multi-repository-mode)
- [Knowledge System](#knowledge-system)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)

---

## Quick Start

### TL;DR

```bash
# Test routing
python3 -m harness test SEMI-1413

# Generate instructions
python3 -m harness implement SEMI-1413

# Follow the printed instructions in Claude Code
```

---

## Single Repository Mode

### Without Orchestrator (Direct)

**Use when:** Working in one repository, don't need knowledge injection

```bash
# 1. Navigate to repository
cd ~/Documents/Development/em-semi

# 2. Start Claude Code
claude --plugin-dir ~/Documents/Development/EM-AISoftwareFactory//Users/malamunisamy/Documents/Development/EM-AISoftwareFactory

# 3. Run skill
/autonomous-implement SEMI-1413
```

**Pros:**
- Simple, direct
- Fast (no harness overhead)

**Cons:**
- No automatic knowledge injection
- No Foundations standards enforcement
- You choose repository manually

---

### With Orchestrator (Knowledge-Enhanced)

**Use when:** Want repo-specific patterns and standards enforced

```bash
# From workspace root
python3 -m harness implement SEMI-1413

# Output:
#  Routed SEMI-1413 → semi
#  Knowledge context prepared: /tmp/knowledge_context_xyz.md
# 
# To execute:
#   1. cd ~/Documents/Development/EM-AISoftwareFactory
#   2. claude --plugin-dir /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory
#   3. cd ~/Documents/Development/em-semi
#   4. /autonomous-implement SEMI-1413 --context-file /tmp/knowledge_context_xyz.md

# Follow the instructions
```

**Pros:**
- Auto-routes to correct repository
- Loads repository knowledge
- Enforces Foundations standards
- Applies repo-specific patterns

**Cons:**
- Extra step (copy/paste commands)

---

## Multi-Repository Mode

### Scenario: Issue Affects Multiple Repos

```bash
# Example: ARCH-500 needs changes in runtime AND runtime-ui

# Step 1: Check which repos
python3 -m harness multi-repo ARCH-500

# Output:
#  Routed ARCH-500 to repositories: runtime, runtime-ui
# 
# Implementation order (respects dependencies):
#   1. runtime (base dependency)
#   2. runtime-ui (depends on runtime)
# 
# Instructions generated:
#   /tmp/harness_instructions_ARCH-500-runtime.sh
#   /tmp/harness_instructions_ARCH-500-runtime-ui.sh

# Step 2: Execute in order
# (Follow instructions for runtime first, then runtime-ui)
```

---

### Scenario: Batch Multiple Issues

```bash
# Implement 5 issues across 3 repositories

python3 -m harness multi-repo SEMI-1413 SEMI-1414 T2D-890 RT-567 UI-123

# Output:
#  Routing summary:
#   - semi: SEMI-1413, SEMI-1414
#   - talk2data: T2D-890
#   - runtime: RT-567
#   - runtime-ui: UI-123
# 
# Generated 5 instruction sets
# 
# Suggested execution order (considering dependencies):
#   1. runtime (RT-567)
#   2. Parallel: semi (SEMI-1413, SEMI-1414) + talk2data (T2D-890)
#   3. runtime-ui (UI-123)
```

---

## Knowledge System

### What Gets Injected

When you use `--context-file`, the skill receives:

```markdown
# Repository Knowledge Context

## Repository: semi
**Language:** python
**Build System:** docker
**Test Framework:** pytest

---

## Architecture

### Wafer Processing Pipeline
The wafer processing pipeline consists of...

### Memory Pool Management
All batch jobs use context managers for resource cleanup...

### Event Sourcing Pattern
Workflow state changes are event-sourced...

---

## Coding Patterns

- Use context managers for all resource cleanup
- Async/await for I/O operations
- Type hints on all public APIs
- Google-style docstrings

---

## Conventions

- Imports: absolute only (no relative imports)
- File naming: snake_case.py
- Test naming: test_*.py
- Max line length: 100 chars

---

## Foundations Standards

### Air-Gapped Requirements (CRITICAL)
- NO cloud-specific APIs (AWS, GCP, Azure)
- NO cloud IAM dependencies
- Helm charts must deploy without cloud provider
- Use Crossplane for infrastructure abstraction

### Definition of Done
1. 80% test coverage minimum
2. gitleaks passes (no secrets)
3. Pacto contract valid
4. Documentation updated
5. Air-gapped compatible
```

### How It's Used

The AI reads this context and:

1. **Follows architecture patterns**
   ```python
   # AI uses context manager (from patterns)
   with WaferProcessor() as processor:
       processor.run_batch()
   ```

2. **Applies conventions**
   ```python
   # AI adds type hints (from conventions)
   def process_wafer(wafer_id: str, config: Dict[str, Any]) -> ProcessResult:
       ...
   ```

3. **Enforces Foundations**
   ```python
   # AI avoids cloud APIs (from standards)
   #  DON'T:
   # import boto3
   # s3 = boto3.client('s3')
   
   #  DO:
   from storage import ObjectStore  # Abstracted
   store = ObjectStore.from_config()
   ```

4. **Ensures coverage**
   ```python
   # AI creates enough tests to hit 80% coverage
   # (from Definition of Done)
   ```

---

### Sync Knowledge

```bash
# Manual sync
./sync_knowledge.sh

# Automatic sync
# Runs before harness implement/multi-repo commands

# Check what was extracted
ls -la knowledge/repositories/semi/
# architecture.md
# patterns.md      - 291 bytes
# conventions.md   - 249 bytes
# dependencies.md  - 230 bytes
```

---

### Adding Custom Knowledge

#### Method 1: Edit Knowledge Files Directly

```bash
# Edit extracted knowledge
vim knowledge/repositories/semi/architecture.md

# Add your ADRs, patterns, etc.
```

#### Method 2: Update Source Docs

```bash
# Edit source documentation
cd ~/Documents/Development/em-semi
vim docs/architecture.md

# Re-sync
cd ~/Documents/Development/EM-AISoftwareFactory
./sync_knowledge.sh
```

#### Method 3: Add ADR References

```yaml
# workspace.yaml
repositories:
  - name: semi
    path: em-semi
    knowledge:
      adrs:
        - file: docs/adr/001-event-sourcing.md
          summary: Use event sourcing for workflow state
        - file: docs/adr/002-duckdb.md
          summary: DuckDB for air-gapped analytics
```

Then re-extract:
```bash
./sync_knowledge.sh
```

---

## Configuration

### workspace.yaml Structure

```yaml
# Workspace root directory
workspace:
  root: /Users/username/Documents/Development

# Repository definitions
repositories:
  - name: semi                          # Internal name
    display_name: EM Semi              # Human-readable
    path: em-semi                       # Relative to workspace.root
    github: EmergenceAI/em-semi        # GitHub repo
    jira_component: Semi               # Jira component name
    primary_language: python
    build_system: docker
    test_framework: pytest

  - name: talk2data
    display_name: EM Talk2Data
    path: em-talk2data
    github: EmergenceAI/em-talk2data
    jira_component: Talk2Data
    primary_language: python
    build_system: poetry
    test_framework: pytest

# Jira integration
jira:
  url: https://your-company.atlassian.net
  project_key: ABI
  
  # Component → Repository mapping
  component_mapping:
    Semi: semi                         # SEMI-* → em-semi
    Talk2Data: talk2data               # T2D-* → em-talk2data
    Runtime: runtime                   # RT-* → em-runtime
    UI: runtime-ui                     # UI-* → em-runtime-ui
    "Data Readiness": data-readiness   # DR-* → em-data-readiness

# Repository dependencies (for multi-repo ordering)
dependencies:
  - source: runtime
    target: runtime-ui
    reason: UI depends on Runtime API

  - source: runtime
    target: talk2data
    reason: Talk2Data integrates with Runtime
```

---

### Routing Strategies

The router uses **3 strategies** in order:

#### 1. Component Mapping (Primary)

```python
# Jira issue with component "Semi"
SEMI-1413
  Component: Semi
  ↓
  component_mapping["Semi"] = "semi"
  ↓
  Routes to: em-semi repository
```

#### 2. Description Analysis (Fallback)

```python
# No component set, searches description
Issue description: "Fix memory leak in semi wafer processing"
  ↓
  Contains "semi" → routes to: em-semi
```

#### 3. Label Prefix (Fallback)

```python
# Has label "repo:semi"
Labels: ["repo:semi", "bug"]
  ↓
  Routes to: em-semi
```

#### 4. Default (Last Resort)

```python
# Nothing matches
  ↓
  Routes to: runtime (default)
```

---

### Adding a New Repository

```bash
# 1. Add to workspace.yaml
vim workspace.yaml

# Add under repositories:
  - name: new-repo
    display_name: EM New Repo
    path: em-new-repo
    github: EmergenceAI/em-new-repo
    jira_component: NewRepo
    primary_language: python
    build_system: poetry
    test_framework: pytest

# Add to component_mapping:
jira:
  component_mapping:
    NewRepo: new-repo

# 2. Extract knowledge
./sync_knowledge.sh

# 3. Test routing
python3 -m harness test NEWREPO-123

# Should output:
#  Routed NEWREPO-123 → new-repo
#  Loaded knowledge for new-repo: XXX chars
```

---

## Advanced Usage

### Custom Knowledge Context

```bash
# Create custom context file
cat > /tmp/my_context.md << 'EOF'
# Custom Knowledge

## Special Requirements
- Use PostgreSQL for all data storage
- Follow GDPR guidelines for PII
- Implement circuit breakers for external APIs

## Patterns
- Repository pattern for data access
- CQRS for read/write separation
EOF

# Use with skill
/autonomous-implement SEMI-1413 --context-file /tmp/my_context.md
```

---

### Pointing to Specific ADRs

```bash
# In implementation plan approval
/autonomous-implement SEMI-1413

# When plan is shown:
"Approve, but ensure this follows:
- ADR-002: Use DuckDB for analytics (air-gapped requirement)
- ADR-005: Event sourcing for state changes"
```

Or add to knowledge extraction:

```bash
# knowledge/repositories/semi/architecture.md

## Architecture Decision Records

### ADR-002: DuckDB for Air-Gapped Analytics
**Decision:** Embed DuckDB for all local analytics queries
**Rationale:** Air-gapped deployment requirement
**File:** docs/adr/002-duckdb.md
**Status:** Active

When implementing analytics features:
- Use DuckDB, not cloud data warehouses
- Embed database file in container
- No external dependencies
```

---

### Override Repository Selection

```bash
# Normally routes based on Jira component
python3 -m harness implement SEMI-1413
# Routes to: semi

# Force different repository (future enhancement)
python3 -m harness implement SEMI-1413 --repo runtime
# Routes to: runtime (override)
```

---

### Check Knowledge Content

```bash
# View loaded knowledge for a repository
cat knowledge/repositories/semi/architecture.md | head -50

# Check knowledge size
wc -c knowledge/repositories/semi/*.md

# Search for specific pattern
grep -r "event sourcing" knowledge/repositories/semi/
```

---

### Debug Routing

```bash
# Test routing without implementation
python3 -m harness test SEMI-1413

# Verbose output
python3 -m harness test SEMI-1413 --verbose

# Test multiple
python3 -m harness test SEMI-1413 T2D-890 RT-567

# Output shows routing decision for each
```

---

## Troubleshooting

### "Routed to wrong repository"

```bash
# Check Jira component
# Go to Jira issue → Components field
# Should match workspace.yaml component_mapping

# Update component_mapping if needed
vim workspace.yaml
# Add: YourComponent: your-repo

# Test
python3 -m harness test YOUR-123
```

### "No knowledge found"

```bash
# Sync knowledge
./sync_knowledge.sh

# Check extracted files
ls -la knowledge/repositories/your-repo/

# If empty, check source docs exist
ls -la ~/Documents/Development/em-your-repo/docs/
ls -la ~/Documents/Development/em-your-repo/README.md
```

### "Context file not found"

```bash
# The context file is temporary
# Run the harness implement command again
python3 -m harness implement SEMI-1413

# It will create a new context file
# Use it immediately (files may be cleaned up)
```

### "Repository path doesn't exist"

```bash
# Check workspace.yaml paths
cat workspace.yaml | grep -A 3 "path:"

# Verify actual directories
ls -la ~/Documents/Development/

# Update workspace.yaml if paths changed
```

---

## Summary

### When to Use What

| Scenario | Command | Knowledge | Routing |
|----------|---------|-----------|---------|
| **Quick single-repo** | `cd repo && /autonomous-implement` |  No | Manual (you cd) |
| **Single-repo + knowledge** | `harness implement` |  Yes | Auto |
| **Multi-repo** | `harness multi-repo` |  Yes | Auto |
| **Batch** | `harness multi-repo ISSUE1 ISSUE2...` |  Yes | Auto |

### Knowledge Injection

| Method | Effort | Flexibility | When to Use |
|--------|--------|-------------|-------------|
| **Auto-extracted** | Low | Medium | Default, works for most cases |
| **Custom file** | Medium | High | Specific requirements per issue |
| **Edit knowledge/** | Medium | Medium | Permanent additions (ADRs, etc.) |
| **Update source docs** | High | Low | Keep source of truth in repos |

---

**The harness transforms "which repo?" and "what patterns?" into "just implement it correctly."** 
